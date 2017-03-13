import sublime
import sublime_plugin

from bisect import bisect
import os

from .lib.packages import PackageInfo, PackageList
from .lib.output_view import output_to_view

###----------------------------------------------------------------------------

def _packages_with_overrides(pkg_list, name_list=None):
    """
    Collect a list of package names from the given package list for which there
    is at least a single (simple) override file and which is not in the list of
    packages to ignore overrides in.

    Optionally, if name_list is provided, the list of package names will be
    filtered to only include packages whose name also exists in the name list.
    """
    settings = sublime.load_settings("OverrideAudit.sublime-settings")
    ignored = settings.get("ignore_overrides_in", [])

    items = [name for name, pkg in pkg_list if len(pkg.override_files()) > 0
                                               and name not in ignored]

    if name_list is not None:
        items = list(filter(lambda name: name in name_list, items))

    return items


def _decorate_package_name(pkg_info, status=False):
    """
    Decorate the name of the provided package with a prefix that describes its
    status and optionally also a suffix if it is a complete override.
    """
    suffix = ""
    if status and pkg_info.has_possible_overrides(simple=False):
        suffix = " <Complete Override>"

    return "[{}{}{}] {}{}".format(
               "S" if pkg_info.shipped_path is not None else " ",
               "I" if pkg_info.installed_path is not None else " ",
               "U" if pkg_info.unpacked_path is not None else " ",
               pkg_info.name,
               suffix)


def _apply_context_settings(view, pkg_name, override, is_diff):
    """
    Apply to a view settings so context menus know what options to allow.
    """
    view.settings().set("override_audit_package", pkg_name)
    view.settings().set("override_audit_override", override)
    view.settings().set("override_audit_diff", is_diff)


def _remove_context_settings(view):
    """
    Remove the view settings tso context menus know to not operate on the view.
    """
    view.settings().erase("override_audit_package")
    view.settings().erase("override_audit_override")
    view.settings().erase("override_audit_diff")


def _open_override_file(window, pkg_name, override):
    """
    Open the provided override from the given package name.
    """
    filename = os.path.join(sublime.packages_path(), pkg_name, override)
    window.open_file(filename)


def _diff_override_file(window, pkg_info, override,
                        diff_only=False, force_reuse=False):
    """
    Generate a diff for the given package and override.
    """
    settings = sublime.load_settings("OverrideAudit.sublime-settings")
    context_lines = settings.get("diff_context_lines", 3)

    action = "diff" if diff_only else settings.get("diff_unchanged", "diff")

    if force_reuse:
        reuse, clear = True, True
    else:
        reuse = settings.get("reuse_views", True)
        clear = settings.get("clear_existing", True)

    diff_info = pkg_info.override_diff(override, context_lines)

    if diff_info is None:
        return

    if diff_info == "":
        sublime.status_message("No changes detected in override")

        if action == "open":
            return _open_override_file(window, pkg_info.name, override)
        elif action == "ignore":
            return

    view = output_to_view(window,
                   "Override of %s" % os.path.join(pkg_info.name, override),
                   "No differences found" if diff_info == "" else diff_info,
                   reuse=reuse,
                   clear=clear,
                   syntax="Packages/Diff/Diff.sublime-syntax")

    _apply_context_settings(view, pkg_info.name, override, True)


###----------------------------------------------------------------------------

class OverrideAuditDiffPackage(sublime_plugin.WindowCommand):
    """
    Perform a bulk diff of all overrides in either all packages or a single
    package, depending on the argument provided.

    This is invoked from OverrideAuditDiffOverride when you invoke that command
    with the bulk argument set to true.
    """
    def _perform_diff(self, pkg_info, context_lines, result):
        for file in pkg_info.override_files():
            result.append("    {}".format(file))

            diff = pkg_info.override_diff(file, context_lines,
                                          empty_result="No differences found",
                                          indent=8)
            if diff is None:
                diff = "Error diffing override; please check the console"
            result.extend([diff, ""])

        result.append("")

    def _diff_packages(self, names, pkg_list, single_package):
        settings = sublime.load_settings("OverrideAudit.sublime-settings")
        context_lines = settings.get("diff_context_lines", 3)

        result = []
        title = "Override Diff Report: "
        if len(names) == 1 and single_package:
            title += names[0]
            result.append("Diffing overrides for {}\n".format(names[0]))
        else:
            title += "All Packages"
            result.append("Diffing overrides for {} packages\n".format(
                          len(names)))

        for name in names:
            pkg_info = pkg_list[name]
            result.append(_decorate_package_name(pkg_info, status=True))

            self._perform_diff(pkg_info, context_lines, result)

        output_to_view(self.window,
                       title,
                       result,
                       reuse=settings.get("reuse_views", True),
                       clear=settings.get("clear_existing", True),
                       syntax="Packages/OverrideAudit/syntax/OverrideAudit-diff.sublime-syntax")

    def run(self, package=None):
        pkg_list = PackageList()

        name_list = None if package is None else [package]
        items = _packages_with_overrides(pkg_list, name_list)

        self._diff_packages(items, pkg_list, package is not None)

###----------------------------------------------------------------------------

class OverrideAuditDiffOverrideCommand(sublime_plugin.WindowCommand):
    """
    Selective diff of a single override or package based on the provided
    arguments. The user will be prompted via quick panel to select the value of
    any elided arguments (except bulk which controls the output).
    """
    def _file_pick(self, pkg_info, override_list, index):
        if index >= 0:
            _diff_override_file(self.window, pkg_info, override_list[index])

    def _show_override_list(self, pkg_info):
        override_list = list(pkg_info.override_files())
        if not override_list:
            print("Package '%s' has no overrides" % pkg_info.name)
        self.window.show_quick_panel(
            items=override_list,
            on_select=lambda i: self._file_pick(pkg_info, override_list, i))

    def _pkg_pick(self, pkg_list, pkg_override_list, index, bulk):
        if index >= 0:
            pkg_info = pkg_list[pkg_override_list[index]]
            if not bulk:
                self._show_override_list(pkg_info)
            else:
                self.window.run_command("override_audit_diff_package",
                                        {"package": pkg_info.name})

    def _show_pkg_list(self, pkg_list, bulk):
        items = _packages_with_overrides(pkg_list)

        if not items:
            print("No unignored packages have overrides")
        self.window.show_quick_panel(
            items=items,
            on_select=lambda i: self._pkg_pick(pkg_list, items, i, bulk))

    def run(self, package=None, file=None, bulk=False):
        pkg_list = PackageList()

        if package is None:
            self._show_pkg_list(pkg_list, bulk)
        else:
            if package in pkg_list:
                pkg_info = pkg_list[package]
                if file is None:
                    self._show_override_list(pkg_info)
                else:
                    if pkg_info.has_possible_overrides():
                        self._perform_diff(pkg_info, file)
                    else:
                        print("Package '%s' has no overrides to diff" % package)
            else:
                print("Unable to diff; no such package '%s'" % package)

###----------------------------------------------------------------------------

class OverrideAuditPackageReportCommand(sublime_plugin.WindowCommand):
    """
    Generate a tabular report of all installed packages and their state.
    """
    def run(self):
        pkg_list = PackageList()
        pkg_counts = pkg_list.package_counts()

        settings = sublime.load_settings("OverrideAudit.sublime-settings")

        title = "{} Total Packages".format(len(pkg_list))
        t_sep = "=" * len(title)

        fmt = '{{:>{}}}'.format(len(str(max(pkg_counts))))
        stats = ("{0} [S]hipped with Sublime\n"
                 "{0} [I]nstalled (user) sublime-package files\n"
                 "{0} [U]npacked in Packages\\ directory\n"
                 "{0} Currently in ignored_packages\n"
                 "{0} Installed dependencies\n").format(fmt).format(*pkg_counts)

        row = "| {:<40} | {:3} | {:3} | {:<3} |".format("", "", "", "")
        r_sep = "-" * len(row)

        result = [title, t_sep, "", stats, r_sep]
        for pkg_name, pkg_info in pkg_list:
            if pkg_info.is_disabled:
                pkg_name = "[{}]".format(pkg_name)
            elif pkg_info.is_dependency:
                pkg_name = "<{}>".format(pkg_name)
            result.append(
                "| {:<40} | [{:1}] | [{:1}] | [{:1}] |".format(
                    pkg_name,
                    "S" if pkg_info.shipped_path is not None else " ",
                    "I" if pkg_info.installed_path is not None else " ",
                    "U" if pkg_info.unpacked_path is not None else " "))
        result.extend([r_sep, ""])

        output_to_view(self.window,
                       "OverrideAudit: Package Report",
                       result,
                       reuse=settings.get("reuse_views", True),
                       clear=settings.get("clear_existing", True),
                       syntax="Packages/OverrideAudit/syntax/OverrideAudit-pkgList.sublime-syntax")

###----------------------------------------------------------------------------

class OverrideAuditOverrideReport(sublime_plugin.WindowCommand):
    """
    Generate a report on all packages which have overrides and what they are,
    if any.
    """
    def run(self):
        pkg_list = PackageList()

        settings = sublime.load_settings("OverrideAudit.sublime-settings")
        ignored = settings.get("ignore_overrides_in", [])

        result = []
        for pkg_name, pkg_info in pkg_list:
            normal_overrides = pkg_info.override_files(simple=True)
            shipped_override = pkg_info.has_possible_overrides(simple=False)
            if pkg_name in ignored or (not normal_overrides and not shipped_override):
                continue

            result.append(_decorate_package_name(pkg_info, status=True))

            if normal_overrides:
                result.extend(["  `- {}".format(item) for item in normal_overrides])
            else:
                result.append("    [No simple overrides found]")
            result.append("")

        if len(result) == 0:
            result.append("No packages with overrides found")

        output_to_view(self.window,
                       "OverrideAudit: Override Report",
                       result,
                       reuse=settings.get("reuse_views", True),
                       clear=settings.get("clear_existing", True),
                       syntax="Packages/OverrideAudit/syntax/OverrideAudit-overrideList.sublime-syntax")

###----------------------------------------------------------------------------

class OverrideAuditContextDiffOpenOverride(sublime_plugin.TextCommand):
    """
    Offer to diff or edit an override via context menu selection.

    This handles both the context menu for a view which contains an edit
    session for an override or a diff of one, or the context menu items which
    apply to override names in the override and bulk diff reports.

    When diff is None, the command assumes it is operating on a view and uses
    internal settings on the view to know which of the two menu options to
    provide.

    Otherwise the command presented assumes it is the context menu for an
    override file, and diff indicates if the command is to diff or edit.
    """
    def run(self, edit, event=None, diff=None):
        if diff is None:
            # When not given diff is a toggle for the current state of a view.
            pkg_name = self.view.settings().get("override_audit_package")
            override = self.view.settings().get("override_audit_override")
            diff     = not self.view.settings().get("override_audit_diff")

        else:
            point    = self.view.window_to_text((event["x"], event["y"]))
            pkg_name = self.package_for_override(point)
            override = self.override_at_point(point)

        # TODO: May be a good idea to check around here to see if the settings
        # are defunct and need to be removed if that's not already happening
        # elsewhere.

        if diff:
            pkg_list = PackageList()
            _diff_override_file(self.view.window(), pkg_list[pkg_name], override,
                                diff_only=True, force_reuse=True)
        else:
            _open_override_file(self.view.window(), pkg_name, override)

    def description(self, event=None, diff=None):
        # When not given diff is a toggle for the current state of a view.
        if diff is None:
            diff = not self.view.settings().get("override_audit_diff", False)

        return "Override Audit: %s Override" % ("Diff" if diff else "Edit")

    def override_at_point(self, point):
        if not self.view.match_selector(point, "text.override-audit entity.name.filename"):
            return None
        return self.view.substr(self.view.extract_scope(point))

    def package_for_override(self, point):
        packages = self.view.find_by_selector("entity.package.name")
        if packages:
            p_lines = [self.view.rowcol(p.begin())[0] for p in packages]
            pkg_region = packages[bisect(p_lines, self.view.rowcol(point)[0]) - 1]

            return self.view.substr(pkg_region)

        return None

    def is_visible(self, event=None, diff=None):
        if diff is not None:
            point = self.view.window_to_text((event["x"], event["y"]))
            return self.override_at_point(point) is not None

        settings = self.view.settings()
        return (settings.has("override_audit_package") and
                settings.has("override_audit_override"))

    def want_event(self):
        return True

###----------------------------------------------------------------------------

class OverrideAuditEventListener(sublime_plugin.EventListener):
    """
    Check on file load and save to see if the new file is potentially an
    override for a package, and set the variables that allow for our context
    menus to let you edit/diff the override.
    """
    def _check_for_override(self, view):
        result = PackageInfo.check_potential_override(view.file_name())
        if result is not None:
            _apply_context_settings(view, result[0], result[1], False)
        else:
            _remove_context_settings(view)

    def on_post_save(self, view):
        # Will remove existing settings if the view is no longer an override
        self._check_for_override(view)

    def on_load(self, view):
        # Things like PackageResourceViewer trigger on_load before the file
        # actually exists; only allow the context items once the file is
        # actually saved.
        if os.path.isfile(view.file_name()):
            self._check_for_override(view)
