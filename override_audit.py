import sublime
import sublime_plugin

from bisect import bisect
import threading
import os

import sys
from imp import reload


# If our submodules have previously been loaded, reload them now before we
# proceed to ensure everything is up to date.
modules = ["OverrideAudit.lib.packages", "OverrideAudit.lib.output_view"]
for module in modules:
    if module in sys.modules:
        reload(sys.modules[module])


from .lib.packages import PackageInfo, PackageList, PackageFileSet
from .lib.output_view import output_to_view


###----------------------------------------------------------------------------


def plugin_loaded():
    """
    Initialize plugin state.
    """
    PackageInfo.init()
    AutoReportTrigger()


def plugin_unloaded():
    """
    Clean up state before unloading.
    """
    AutoReportTrigger.unregister()


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


def _pkg_display_name(pkg_info):
    """
    Return the name to be used to display a package in reports, which is the
    base package name potentially modified to include the visual distinctions
    that indicate if it is disabled or a dependency.
    """
    if pkg_info.is_disabled:
        return "[%s]" % pkg_info.name
    elif pkg_info.is_dependency:
        return "<%s>" % pkg_info.name
    else:
        return pkg_info.name


def _decorate_package_name(pkg_info):
    """
    Decorate the name of the provided package with a prefix that describes its
    status and optionally also a suffix if it is a complete override or is
    expired.
    """
    suffix = ""

    if pkg_info.has_possible_overrides(simple=False):
        suffix += " <Complete Override>"

    if bool(pkg_info.expired_override_files(simple=False)):
        suffix += " [EXPIRED]"

    return "[{}{}{}] {}{}".format(
               "S" if pkg_info.shipped_path is not None else " ",
               "I" if pkg_info.installed_path is not None else " ",
               "U" if pkg_info.unpacked_path is not None else " ",
               _pkg_display_name(pkg_info),
               suffix)


def _apply_override_settings(view, pkg_name, override, is_diff):
    """
    Apply view settings marking the view as an override view.
    """
    view.settings().set("override_audit_package", pkg_name)
    view.settings().set("override_audit_override", override)
    view.settings().set("override_audit_diff", is_diff)


def _remove_override_settings(view):
    """
    Remove view settings marking the view as an override view.
    """
    view.settings().erase("override_audit_package")
    view.settings().erase("override_audit_override")
    view.settings().erase("override_audit_diff")


def _apply_report_settings(view, report_type):
    """
    Apply view settings marking the view as a report view.
    """
    view.settings().set("override_audit_report", True)
    view.settings().set("override_audit_report_type", report_type)


def _open_override_file(window, pkg_name, override):
    """
    Open the provided override from the given package name.
    """
    filename = os.path.join(sublime.packages_path(), pkg_name, override)
    window.open_file(filename)


def _delete_override_file(window, pkg_name, override):
    """
    Delete the provided override from the given package name.
    """
    # Import send2trash on demand; see Default/side_bar.py.
    import Default.send2trash as send2trash

    settings = sublime.load_settings("OverrideAudit.sublime-settings")
    confirm = settings.get("confirm_deletion", True)

    relative_name = os.path.join(pkg_name, override)
    full_name = os.path.join(sublime.packages_path(), relative_name)
    if os.path.isfile(full_name):
        if confirm:
            msg = "Confirm deletion:\n\n{}".format(relative_name)

        if (confirm is False or
                sublime.yes_no_cancel_dialog(msg) == sublime.DIALOG_YES):
            send2trash.send2trash(full_name)
            window.status_message("Deleted {}".format(relative_name))


def _thr_diff_override(window, pkg_info, override,
                       diff_only=False, force_reuse=False):
    """
    Generate a diff for the given package and override in a background thread,
    """
    settings = sublime.load_settings("OverrideAudit.sublime-settings")
    context_lines = settings.get("diff_context_lines", 3)

    action = "diff" if diff_only else settings.get("diff_unchanged", "diff")

    if force_reuse:
        reuse, clear = True, True
    else:
        reuse = settings.get("reuse_views", True)
        clear = settings.get("clear_existing", True)

    def _process_diff(thread):
        diff_info = thread.diff
        if diff_info is None:
            return

        if diff_info == "":
            sublime.status_message("No changes detected in override")

            if action == "open":
                return _open_override_file(window, pkg_info.name, override)

            elif action == "ignore":
                return

        title = "Override of %s" % os.path.join(pkg_info.name, override)
        content = "No differences found" if diff_info == "" else diff_info
        view = output_to_view(window, title, content, reuse, clear,
                              "Packages/Diff/Diff.sublime-syntax")

        _apply_override_settings(view, pkg_info.name, override, True)

    callback = lambda thread: _process_diff(thread)
    OverrideDiffThread(window, "Diffing Override", callback,
                       pkg_info=pkg_info, override=override).start()


###----------------------------------------------------------------------------


class AutoReportTrigger():
    """
    A simple singleton class for running an automated expired updates report
    whenever a package is removed from the ignored packages list or at startup
    when the build number of Sublime has changed.
    """
    instance = None

    def __init__(self):
        if AutoReportTrigger.instance is not None:
            return

        AutoReportTrigger.instance = self

        self.settings = sublime.load_settings("Preferences.sublime-settings")
        ignored = self.settings.get("ignored_packages", [])

        self.cached_ignored = PackageFileSet(ignored)
        self.removed = PackageFileSet()

        self.settings.add_on_change("_oa_sw", lambda: self.__settings_change())

        self.__load_status()

    @classmethod
    def unregister(cls):
        if AutoReportTrigger.instance is not None:
            AutoReportTrigger.instance.settings.clear_on_change("_oa_sw")
            AutoReportTrigger.instance = None

    def __load_status(self):
        self.last_build = "0"
        self.force_report = False
        self.status_file = os.path.join(sublime.packages_path(), "User",
                                        "OverrideAudit.status")

        if os.path.isfile(self.status_file):
            with open(self.status_file) as file:
                line = file.readline().split(",")
                try:
                    self.last_build = line[0]
                    self.force_report = line[1] == "True"
                except IndexError:
                    pass

        if self.last_build == sublime.version() and self.force_report == False:
            print("Sublime version is unchanged; skipping automatic report")
            return

        if self.last_build != sublime.version():
            if self.last_build == "0":
                reason = "Initial plugin installation"
            else:
                reason = "Sublime version has changed"
        elif self.force_report:
            reason = "Sublime restarted during a package upgrade"

        print(reason + "; generating automatic report")
        sublime.set_timeout(lambda: self.__execute_auto_report(), 1000)

    def __save_status(self, force):
        with open(self.status_file, "w") as file:
            file.write("%s,%s" % (sublime.version(), force))

    def __execute_auto_report(self):
        self.__save_status(False)
        self.removed = PackageFileSet()

        window = sublime.active_window()
        window.run_command("override_audit_override_report",
            {"only_expired": True, "ignore_empty": True})

    def __check_removed(self, removed_set):
        if removed_set != self.removed:
            return

        self.__execute_auto_report()

    def __settings_change(self):
        new_list = PackageFileSet(self.settings.get("ignored_packages", []))
        if new_list == self.cached_ignored:
            return

        removed = self.cached_ignored - new_list
        added = new_list - self.cached_ignored
        self.cached_ignored = new_list

        oa_settings = sublime.load_settings("OverrideAudit.sublime-settings")
        timeout = oa_settings.get("report_on_unignore", 0) * 1000

        if timeout <= 0:
            return

        self.removed |= removed
        self.removed -= added

        if len(self.removed) != 0:
            self.__save_status(True)

            # Send a copy of the list so we can detect if the list changes
            # in the interim.
            current = PackageFileSet(self.removed)
            sublime.set_timeout(lambda: self.__check_removed(current), timeout)
        else:
            self.__save_status(False)


###----------------------------------------------------------------------------


class Spinner():
    """
    A simple spinner that follows the active view in the provided window which
    self terminates when the provided thread is no longer running.
    """
    spin_text = "|/-\\"

    def __init__(self, window, thread, prefix):
        self.window = window
        self.thread = thread
        self.prefix = prefix
        self.tick_view = None

        sublime.set_timeout(lambda: self.tick(0), 250)

    def tick(self, position):
        current_view = self.window.active_view()

        if self.tick_view is not None and current_view != self.tick_view:
            self.tick_view.erase_status("oa_spinner")
            self.tick_view = None

        if not self.thread.is_alive():
            current_view.erase_status("oa_spinner")
            return

        text = "%s [%s]" % (self.prefix, self.spin_text[position])
        position = (position + 1) % len(self.spin_text)

        current_view.set_status("oa_spinner", text)
        if self.tick_view is None:
            self.tick_view = current_view

        sublime.set_timeout(lambda: self.tick(position), 250)


###----------------------------------------------------------------------------


class BackgroundWorkerThread(threading.Thread):
    """
    A thread for performing a task in the background, optionally executing a
    callback in the main thread when processing has completed.

    If given, the callback is invoked in the main thread after processing has
    completed, with the thread instance as a parameter so that results can be
    collected.
    """
    def __init__(self, window, spinner_text, callback, **kwargs):
        super().__init__()

        self.window = window
        self.spinner_text = spinner_text
        self.callback = callback
        self.args = kwargs

    def _check_result(self):
        if self.is_alive():
            sublime.set_timeout(lambda: self._check_result(), 100)
            return

        if self.callback is not None:
            self.callback(self)

    def _process(self):
        pass

    def run(self):
        Spinner(self.window, self, self.spinner_text)
        sublime.set_timeout(lambda: self._check_result(), 10)

        self._process()


###----------------------------------------------------------------------------


class PackageListCollectionThread(BackgroundWorkerThread):
    """
    Collect the list of packages (and optionally also overrides) in the
    background.
    """
    def _process(self):
        self.pkg_list = PackageList()
        if self.args.get("get_overrides", False) is True:
            _packages_with_overrides(self.pkg_list)


###----------------------------------------------------------------------------


class OverrideDiffThread(BackgroundWorkerThread):
    """
    Diff a specific package override in a background thread.
    """
    def _process(self):
        settings = sublime.load_settings("OverrideAudit.sublime-settings")
        context_lines = settings.get("diff_context_lines", 3)

        pkg_info = self.args.get("pkg_info", None)
        override = self.args.get("override", None)

        if not pkg_info or not override:
            self.diff = None
            print("diff thread not given a package or override to diff")
            return

        self.diff = pkg_info.override_diff(override, context_lines,
                                           binary_result="<File is binary>")


###----------------------------------------------------------------------------


class ReportGenerationThread(threading.Thread):
    """
    Helper base class for generating a report in a background thread.
    """
    def __init__(self, window, prefix, **kwargs):
        super().__init__()

        self.window = window
        self.args = kwargs
        Spinner(self.window, self, prefix)

    def _display_report(self):
        settings = sublime.load_settings("OverrideAudit.sublime-settings")
        force_reuse = self.args.get("force_reuse", False)

        reuse = True if force_reuse else settings.get("reuse_views", True)
        clear = True if force_reuse else settings.get("clear_existing", True)

        view = output_to_view(self.window, self.caption, self.content,
                              reuse, clear, self.syntax)
        _apply_report_settings(view, self.report_type)

    def _set_content(self, caption, content, report_type, syntax):
        self.caption = caption
        self.content = content
        self.report_type = report_type
        self.syntax = syntax

        sublime.set_timeout(self._display_report(), 10)

###----------------------------------------------------------------------------


class PackageReportThread(ReportGenerationThread):
    """
    Generate a tabular report of all installed packages and their state.
    """
    def run(self):
        pkg_list = PackageList()
        pkg_counts = pkg_list.package_counts()

        title = "{} Total Packages".format(len(pkg_list))
        t_sep = "=" * len(title)

        fmt = '{{:>{}}}'.format(len(str(max(pkg_counts))))
        stats = ("{0} [S]hipped with Sublime\n"
                 "{0} [I]nstalled (user) sublime-package files\n"
                 "{0} [U]npacked in Packages\\ directory\n"
                 "{0} Currently in ignored_packages\n"
                 "{0} Installed Dependencies\n").format(fmt).format(*pkg_counts)

        row = "| {:<40} | {:3} | {:3} | {:<3} |".format("", "", "", "")
        r_sep = "-" * len(row)

        result = [title, t_sep, "", stats, r_sep]
        for pkg_name, pkg_info in pkg_list:
            result.append(
                "| {:<40} | [{:1}] | [{:1}] | [{:1}] |".format(
                    _pkg_display_name(pkg_info),
                    "S" if pkg_info.shipped_path is not None else " ",
                    "I" if pkg_info.installed_path is not None else " ",
                    "U" if pkg_info.unpacked_path is not None else " "))
        result.extend([r_sep, ""])

        self._set_content("OverrideAudit: Package Report", result, ":packages",
                          "Packages/OverrideAudit/syntax/OverrideAudit-pkgList.sublime-syntax")


###----------------------------------------------------------------------------


class OverrideReportThread(ReportGenerationThread):
    """
    Generate a report on all packages which have overrides and what they are,
    if any. The report always includes expired packages and overrides, but the
    optional paramter filters to only show expired results.
    """
    def run(self):
        pkg_list = PackageList()

        settings = sublime.load_settings("OverrideAudit.sublime-settings")
        ignored = settings.get("ignore_overrides_in", [])

        only_expired = self.args["only_expired"]
        ignore_empty = self.args["ignore_empty"]

        if only_expired:
            title = "OverrideAudit: Expired Override Report"
            report_type = ":overrides_expired"
        else:
            title = "OverrideAudit: Override Report"
            report_type = ":overrides"

        result = []
        if only_expired:
            result.append("WARNING: Showing only expired overrides!\n"
                          "WARNING: Non-expired overrides may exist!\n")

        displayed = 0
        for pkg_name, pkg_info in pkg_list:
            if pkg_name not in ignored:
                if self._output_package(result, pkg_info, only_expired):
                    displayed += 1

        if displayed == 0:
            if ignore_empty:
                return sublime.set_timeout(self._notify_empty(), 10)

            result.append(self._empty_msg())

        self._set_content(title, result, report_type,
                          "Packages/OverrideAudit/syntax/OverrideAudit-overrideList.sublime-syntax")

    def _output_package(self, result, pkg_info, only_expired):
        shipped_override = pkg_info.has_possible_overrides(simple=False)
        normal_overrides = pkg_info.override_files(simple=True)

        expired_overrides = pkg_info.expired_override_files(simple=True)
        expired_pkg = bool(pkg_info.expired_override_files(simple=False))

        # No need to do anything if there are no overrides at all
        if not normal_overrides and not shipped_override:
            return False

        if only_expired and not expired_overrides and not expired_pkg:
            return False

        result.append(_decorate_package_name(pkg_info))

        self._output_overrides(result, normal_overrides,
                               expired_overrides, only_expired)
        result.append("")

        return True

    def _output_overrides(self, result, overrides, expired, only_expired):
        if not overrides:
            return result.append("    [No simple overrides found]")

        # Must be overrides, if none are expired use a different message.
        if only_expired and not expired:
            return result.append("    [No expired simple overrides found]")

        for item in (expired if only_expired else overrides):
            fmt = "  `- {}" if item not in expired else "  `- [X] {}"
            result.append(fmt.format(item))

    def _empty_msg(self):
        return "No packages with %soverrides found" % (
                "expired " if self.args["only_expired"] else "")

    def _notify_empty(self):
        msg = self._empty_msg()

        print(msg)
        sublime.status_message(msg)

###----------------------------------------------------------------------------


class BulkDiffReportThread(ReportGenerationThread):
    """
    Perform a bulk diff of all overrides in either all packages or a single
    package, depending on the argument provided.

    This is invoked from OverrideAuditDiffOverride when you invoke that command
    with the bulk argument set to true.
    """
    def run(self):
        pkg_list = PackageList()

        package = self.args["package"]
        force_reuse = self.args["force_reuse"]

        if package is not None:
            if package not in pkg_list:
                print("Cannot diff package; package not found")
                return

            items = [package]
        else:
            items = _packages_with_overrides(pkg_list)

        self._diff_packages(items, pkg_list, package is not None, force_reuse)

    def _diff_packages(self, names, pkg_list, single_package, force_reuse):
        settings = sublime.load_settings("OverrideAudit.sublime-settings")
        context_lines = settings.get("diff_context_lines", 3)

        result = []
        title = "Override Diff Report: "
        description = "Bulk Diff Report for overrides in"
        report_type = ":bulk_all"

        if len(names) == 1 and single_package:
            title += names[0]
            result.append(description + " {}\n".format(names[0]))
            report_type = names[0]
        else:
            title += "All Packages"
            result.append(description + " {} packages\n".format(len(names)))

        for name in names:
            pkg_info = pkg_list[name]

            result.append(_decorate_package_name(pkg_info))
            self._perform_diff(pkg_info, context_lines, result)

        self._set_content(title, result, report_type,
                          "Packages/OverrideAudit/syntax/OverrideAudit-diff.sublime-syntax")

    def _perform_diff(self, pkg_info, context_lines, result):
        override_list = pkg_info.override_files(simple=True)
        expired_list = pkg_info.expired_override_files(simple=True)

        for file in override_list:
            if file in expired_list:
                result.append("    [X] {}".format(file))
            else:
                result.append("    {}".format(file))

            diff = pkg_info.override_diff(file, context_lines,
                                          empty_result="No differences found",
                                          binary_result="<File is binary>",
                                          indent=8)
            if diff is None:
                diff = (" " * 8) + ("Error opening or decoding file;"
                                    " is it UTF-8 or Binary?")
            result.extend([diff, ""])

        if len(override_list) == 0:
            result.append("    [No simple overrides found]")
        result.append("")


###----------------------------------------------------------------------------


class OverrideAuditPackageReportCommand(sublime_plugin.WindowCommand):
    """
    Generate a tabular report of all installed packages and their state.
    """
    def run(self, force_reuse=False):
        PackageReportThread(self.window, "Generating Package Report",
                            force_reuse=force_reuse).start()


###----------------------------------------------------------------------------


class OverrideAuditOverrideReportCommand(sublime_plugin.WindowCommand):
    """
    Generate a report on all packages which have overrides and what they are,
    if any. The report always includes expired packages and overrides, but the
    optional paramter filters to only show expired results.
    """
    def run(self, force_reuse=False, only_expired=False, ignore_empty=False):
        OverrideReportThread(self.window, "Generating Override Report",
                             force_reuse=force_reuse,
                             only_expired=only_expired,
                             ignore_empty=ignore_empty).start()


###----------------------------------------------------------------------------


class OverrideAuditDiffPackageCommand(sublime_plugin.WindowCommand):
    """
    Perform a bulk diff of all overrides in either all packages or a single
    package, depending on the argument provided.

    This is invoked from OverrideAuditDiffOverride when you invoke that command
    with the bulk argument set to true.
    """
    def run(self, package=None, force_reuse=False):
        BulkDiffReportThread(self.window, "Generating Bulk Diff",
                             package=package, force_reuse=force_reuse).start()


###----------------------------------------------------------------------------


class OverrideAuditDiffOverrideCommand(sublime_plugin.WindowCommand):
    """
    Selective diff of a single override or package based on the provided
    arguments. The user will be prompted via quick panel to select the value of
    any elided arguments (except bulk which controls the output).
    """
    def _file_pick(self, pkg_info, override_list, index):
        if index >= 0:
            _thr_diff_override(self.window, pkg_info, override_list[index])

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

    def _loaded(self, thread, package, file, bulk):
        if thread.is_alive():
            sublime.set_timeout(lambda: self._loaded(thread, package, file, bulk), 100)
            return

        pkg_list = thread.pkg_list

        if package is None:
            self._show_pkg_list(pkg_list, bulk)
        else:
            if package in pkg_list:
                pkg_info = pkg_list[package]
                if file is None:
                    self._show_override_list(pkg_info)
                else:
                    if pkg_info.has_possible_overrides():
                        _thr_diff_override(self.window, pkg_info, file)
                    else:
                        print("Package '%s' has no overrides to diff" % package)
            else:
                print("Unable to diff; no such package '%s'" % package)

    def run(self, package=None, file=None, bulk=False):
        # Shortcut for bulk diffing a single package
        if bulk and package is not None:
            self.window.run_command("override_audit_diff_package",
                                    {"package": package})
            return

        callback = lambda thread: self._loaded(thread, package, file, bulk)
        PackageListCollectionThread(self.window, "Collecting Package List",
                                    callback, get_overrides=True).start()


###----------------------------------------------------------------------------


class ContextHelper():
    """
    Helper class to allow context specific commands to seamlessly work in view
    context menu, tab context menus and the command palette.

    Finds the appropriate target view and package/override/diff options based
    on where it is used.
    """
    def _extract(self, scope, event):
        if event is None:
            return None

        point = self.view.window_to_text((event["x"], event["y"]))
        if not self.view.match_selector(point, scope):
            return None

        return self.view.substr(self.view.extract_scope(point))

    def _package_at_point(self, event):
        return self._extract("text.override-audit entity.name.package", event)

    def _override_at_point(self, event):
        return self._extract("text.override-audit entity.name.filename.override", event)

    def _package_for_override_at(self, event):
        if event is not None:
            point = self.view.window_to_text((event["x"], event["y"]))
            packages = self.view.find_by_selector("entity.name.package")

            if packages:
                p_lines = [self.view.rowcol(p.begin())[0] for p in packages]
                pkg_region = packages[bisect(p_lines, self.view.rowcol(point)[0]) - 1]

                return self.view.substr(pkg_region)

        return None

    def _report_type(self, **kwargs):
        target = self.view_target(self.view, **kwargs)
        if target.settings().get("override_audit_report", False) is True:
            return target.settings().get("override_audit_report_type")

        return None

    def view_target(self, view, group=-1, index=-1, **kwargs):
        """
        Get target view specified by group and index, if needed.
        """
        window = view.window()
        return view if group == -1 else window.views_in_group(group)[index]

    def view_context(self, view, event=None, **kwargs):
        """
        Return a tuple of (pkg_name, override_name, is_diff) for the provided
        view and possible event. Some members of the tuple will be None if they
        do not apply or cannot be determined by the current command state.

        If view is none, view_target is invoked to determine it.

        Some/all members of the tuple may be None.
        """
        if view is None:
            view = self.view_target(self.view, **kwargs)

        pkg_name = None
        override = None
        is_diff = None

        # Favor settings if they exist
        settings = view.settings()
        if (settings.has("override_audit_package") and
                settings.has("override_audit_override")):

            pkg_name = view.settings().get("override_audit_package")
            override = view.settings().get("override_audit_override")
            is_diff  = view.settings().get("override_audit_diff", None)

        # Check for context clicks on a package or override name
        elif event is not None:
            pkg_name = self._package_at_point(event)
            if pkg_name is None:
                override = self._override_at_point(event)
                if override is not None:
                    pkg_name = self._package_for_override_at(event)

        return (pkg_name, override, is_diff)

    def want_event(self):
        return True

###----------------------------------------------------------------------------


class OverrideAuditContextOverrideCommand(ContextHelper,sublime_plugin.TextCommand):
    """
    Offer to diff, edit or delete an override via context menu selection.

    Works as a view context menu (on an override), tab context menu or via the
    command palette.
    """
    def run(self, edit, action, **kwargs):
        target = self.view_target(self.view, **kwargs)
        pkg_name, override, is_diff = self.view_context(target, **kwargs)

        if action == "toggle":
            action = "diff" if not is_diff else "edit"

        # TODO: May be a good idea to check around here to see if the settings
        # are defunct and need to be removed if that's not already happening
        # elsewhere.

        if action == "diff":
            self._context_diff(target.window(), pkg_name, override)

        elif action == "edit":
            _open_override_file(target.window(), pkg_name, override)

        elif action == "delete":
            _delete_override_file(target.window(), pkg_name, override)

        else:
            print("Error: unknown action for override context")

    def _context_diff(self, window, package, override):
        callback = lambda thr: self._pkg_loaded(thr, window, package, override)
        PackageListCollectionThread(window, "Collecting Package List",
                                    callback).start()

    def _pkg_loaded(self, thread, window, pkg_name, override):
        pkg_list = thread.pkg_list
        _thr_diff_override(window, pkg_list[pkg_name], override,
                           diff_only=True, force_reuse=True)

    def description(self, action, **kwargs):
        pkg_name, override, is_diff = self.view_context(None, **kwargs)

        if action == "toggle":
            action = "diff" if is_diff is False else "edit"

        return "OverrideAudit: %s Override '%s'" % (action.title(), override)

    def is_visible(self, action, **kwargs):
        pkg_name, override, is_diff = self.view_context(None, **kwargs)

        if action == "toggle":
            return True if is_diff is not None else False

        # Everything else requires package and override to be visible
        if pkg_name is not None and override is not None:
            return True if is_diff is None or action == "delete" else False

        return False


###----------------------------------------------------------------------------


class OverrideAuditContextPackageCommand(ContextHelper,sublime_plugin.TextCommand):
    """
    Offer to bulk diff an entire package based on a context menu selection.

    The menu item is visible only in context menus which present a package name
    such as the global package list, override list or existing diff report.
    """
    def run(self, edit, event):
        pkg_name = self._package_at_point(event)

        self.view.window().run_command("override_audit_diff_package",
                                       {"package": pkg_name})

    def description(self, event, **kwargs):
        pkg_name = self._package_at_point(event)

        return "OverrideAudit: Bulk Diff Package '%s'" % pkg_name

    def is_visible(self, event, **kwargs):
        pkg_name = self._package_at_point(event)
        if pkg_name is not None and self._report_type(**kwargs) == pkg_name:
            return False
        return pkg_name is not None


###----------------------------------------------------------------------------


class OverrideAuditContextReportCommand(ContextHelper,sublime_plugin.TextCommand):
    """
    Offer to refresh existing reports after manual changes have been made.
    """
    def run(self, edit, **kwargs):
        window = self.view_target(self.view, **kwargs).window()
        report_type = self._report_type(**kwargs)

        command = {
            ":packages":          "override_audit_package_report",
            ":overrides":         "override_audit_override_report",
            ":overrides_expired": "override_audit_override_report"
        }.get(report_type, "override_audit_diff_package")
        args = {"force_reuse": True}

        if report_type[0] != ":":
            args["package"] = report_type
        elif report_type == ":overrides_expired":
            args["only_expired"] = True

        window.run_command(command, args)

    def description(self, **kwargs):
        report = self._report_type(**kwargs)
        report = {
            ":packages":          "Package Report",
            ":overrides":         "Override Report",
            ":overrides_expired": "Override Report (Expired only)",
            ":bulk_all":          "Bulk Diff Report"
        }.get(report, "Bulk Diff of '%s'" % report)

        return "OverrideAudit: Refresh %s" % report

    def is_visible(self, **kwargs):
        return self._report_type(**kwargs) is not None


###----------------------------------------------------------------------------


class OverrideAuditEventListener(sublime_plugin.EventListener):
    """
    Check on file load and save to see if the new file is potentially an
    override for a package, and set the variables that allow for our context
    menus to let you edit/diff the override.
    """
    def _check_for_override(self, view):
        filename = view.file_name()
        if filename is None or not os.path.isfile(filename):
            return

        result = PackageInfo.check_potential_override(filename)
        if result is not None:
            _apply_override_settings(view, result[0], result[1], False)
        else:
            _remove_override_settings(view)

    def on_post_save_async(self, view):
        # Will remove existing settings if the view is no longer an override
        self._check_for_override(view)

    def on_load_async(self, view):
        # Things like PackageResourceViewer trigger on_load before the file
        # actually exists; context items are only allowed once the file is
        # actually saved.
        self._check_for_override(view)

    def on_query_context(self, view, key, operator, operand, match_all):
        if key != "override_audit_override_view":
            return None

        return (view.settings().has("override_audit_package") and
                view.settings().has("override_audit_override"))


###----------------------------------------------------------------------------
