import sublime
import sublime_plugin

from datetime import datetime
from bisect import bisect
import os

import sys
from imp import reload


# If our submodules have previously been loaded, reload them now before we
# proceed to ensure everything is up to date.
prefix = "OverrideAudit.lib."
sub_modules = ["packages", "output_view", "threads", "utils"]
for module in sub_modules:
    module = prefix + module
    if module in sys.modules:
        reload(sys.modules[module])


from .lib.packages import PackageInfo, PackageList, PackageFileSet
from .lib.output_view import output_to_view
from .lib.threads import BackgroundWorkerThread
from .lib.utils import SettingsGroup


###----------------------------------------------------------------------------


# A group of view settings that indicate that a view is either an override or a
# diff of one. The settings indicate what package and override the contents of
# the buffer represents.
override_group = SettingsGroup("override_audit_package",
                               "override_audit_override",
                               "override_audit_diff")


###----------------------------------------------------------------------------


def plugin_loaded():
    """
    Initialize plugin state.
    """
    _oa_setting.obj = sublime.load_settings("OverrideAudit.sublime-settings")
    _oa_setting.default = {
        "reuse_views": True,
        "clear_existing": True,
        "ignore_overrides_in": [],
        "diff_unchanged": "diff",
        "diff_context_lines": 3,
        "diff_empty_hdr": False,
        "save_on_diff": False,
        "confirm_deletion": True,
        "confirm_freshen": True,
        "report_on_unignore": True,

        # Inherits from user preferences
        "binary_file_patterns": None
    }

    PackageInfo.init()
    AutoReportTrigger()


def plugin_unloaded():
    """
    Clean up state before unloading.
    """
    AutoReportTrigger.unregister()


def _log(message, *args, status=False, dialog=False):
    """
    Simple logging method; writes to the console and optionally also the status
    message as well.
    """
    message = message % args
    print("OverrideAudit:", message)
    if status:
        sublime.status_message(message)
    if dialog:
        sublime.message_dialog(message)


def _oa_syntax(file):
    """
    Return the full name of an Override Audit syntax based on the short name.
    """
    return "Packages/OverrideAudit/syntax/%s.sublime-syntax" % file


def _oa_setting(key):
    """
    Get an OverrideAudit setting from a cached settings object.
    """
    default = _oa_setting.default.get(key, None)
    return _oa_setting.obj.get(key, default)


def _packages_with_overrides(pkg_list, name_list=None):
    """
    Collect a list of package names from the given package list for which there
    is at least a single (simple) override file and which is not in the list of
    packages to ignore overrides in.

    Optionally, if name_list is provided, the list of package names will be
    filtered to only include packages whose name also exists in the name list.
    """
    ignored = _oa_setting("ignore_overrides_in")
    items = [name for name, pkg in pkg_list if len(pkg.override_files()) > 0
                                               and name not in ignored]

    if name_list is not None:
        items = list(filter(lambda name: name in name_list, items))

    return items


def _decorate_pkg_name(pkg_info, name_only=False):
    """
    Decorate the name of the provided package with a prefix that describes its
    status and optionally also a suffix if it is a complete override or is
    expired.
    """
    suffix = ""
    pkg_name = pkg_info.name

    if pkg_info.is_disabled:
        pkg_name = "[%s]" % pkg_name
    elif pkg_info.is_dependency:
        pkg_name = "<%s>" % pkg_name

    if name_only:
        return pkg_name

    if pkg_info.has_possible_overrides(simple=False):
        suffix += " <Complete Override>"

    if bool(pkg_info.expired_override_files(simple=False)):
        suffix += " [EXPIRED]"

    return "[{}{}{}] {}{}".format(
               "S" if pkg_info.shipped_path is not None else " ",
               "I" if pkg_info.installed_path is not None else " ",
               "U" if pkg_info.unpacked_path is not None else " ",
               pkg_name,
               suffix)


def _open_override(window, pkg_name, override):
    """
    Open the provided override from the given package name.
    """
    filename = os.path.join(sublime.packages_path(), pkg_name, override)
    window.open_file(filename)


def _delete_override(window, pkg_name, override):
    """
    Delete the provided override from the given package name.
    """
    # Import send2trash on demand; see Default/side_bar.py.
    import Default.send2trash as send2trash

    confirm = _oa_setting("confirm_deletion")

    relative_name = os.path.join(pkg_name, override)
    full_name = os.path.join(sublime.packages_path(), relative_name)
    if os.path.isfile(full_name):
        if confirm:
            msg = "Confirm deletion:\n\n{}".format(
                PackageInfo.override_display(relative_name))

        if (confirm is False or
                sublime.yes_no_cancel_dialog(msg) == sublime.DIALOG_YES):
            send2trash.send2trash(full_name)
            _log("Deleted %s", relative_name, status=True)


def _thr_freshen_override(view, pkg_name, override=None):
    """
    Touch either the explicitly specified override in the provided package or
    all expired overrides in the package.
    """
    if _oa_setting("confirm_freshen"):
        target = "Expired overrides in '%s'" % pkg_name
        if override is not None:
            relative_name = os.path.join(pkg_name, override)
            target = PackageInfo.override_display(relative_name)

        msg = "Confirm freshen:\n\n{}".format(target)
        if sublime.yes_no_cancel_dialog(msg) != sublime.DIALOG_YES:
            return

    callback = lambda thread: _log(thread.result, status=True)
    OverrideFreshenThread(view.window(), "Freshening Files", callback,
                       pkg_name=pkg_name, override=override, view=view).start()


def _thr_diff_override(window, pkg_info, override,
                       diff_only=False, force_reuse=False):
    """
    Generate a diff for the given package and override in a background thread,
    """
    context_lines = _oa_setting("diff_context_lines")
    action = "diff" if diff_only else _oa_setting("diff_unchanged")
    empty_diff_hdr = _oa_setting("diff_empty_hdr")

    if force_reuse:
        reuse, clear = True, True
    else:
        reuse = _oa_setting("reuse_views")
        clear = _oa_setting("clear_existing")

    def _process_diff(thread):
        diff = thread.diff
        if diff is None:
            return _log("Unable to diff %s/%s\n\n"
                        "Error loading file contents of one or both files.\n"
                        "Check the console for more information",
                        pkg_info.name, override, dialog=True)

        if diff.is_empty:
            _log("No changes detected in %s/%s", pkg_info.name, override,
                 status=True)

            if action == "open":
                return _open_override(window, pkg_info.name, override)

            elif action == "ignore":
                return

        title = "Diff of %s" % PackageInfo.override_display(
            os.path.join(pkg_info.name, override))

        result = diff.result
        prefix = diff.hdr if diff.is_empty and empty_diff_hdr else ""
        content = prefix + "No differences found" if result == "" else result

        view = output_to_view(window, title, content, reuse, clear,
                              "Packages/Diff/Diff.tmLanguage")

        override_group.apply(view, pkg_info.name, override, True)

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
            _log("Sublime version is unchanged; skipping automatic report")
            return

        if self.last_build != sublime.version():
            if self.last_build == "0":
                reason = "Initial plugin installation"
            else:
                reason = "Sublime version has changed"
        elif self.force_report:
            reason = "Sublime restarted during a package upgrade"

        _log(reason + "; generating automatic report")
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

        if not _oa_setting("report_on_unignore"):
            return

        self.removed |= removed
        self.removed -= added

        if len(self.removed) != 0:
            self.__save_status(True)

            # Send a copy of the list so we can detect if the list changes
            # in the interim.
            current = PackageFileSet(self.removed)
            sublime.set_timeout(lambda: self.__check_removed(current), 1000)
        else:
            self.__save_status(False)


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
        context_lines = _oa_setting("diff_context_lines")

        pkg_info = self.args.get("pkg_info", None)
        override = self.args.get("override", None)

        if not pkg_info or not override:
            self.diff = None
            return _log("diff thread not given a package or override to diff")

        # Only need to do this if the user has a specific setting
        binary_patterns = _oa_setting("binary_file_patterns")
        if binary_patterns is not None:
            pkg_info.set_binary_pattern(binary_patterns)

        self.diff = pkg_info.override_diff(override, context_lines,
                                           binary_result="<File is binary>")


###----------------------------------------------------------------------------


class OverrideFreshenThread(BackgroundWorkerThread):
    """
    Touch either the explicitly specified override in the provided package or
    all expired overrides in the package.
    """
    def _touch_override(self, pkg_name, override):
        fname = os.path.join(sublime.packages_path(), pkg_name, override)
        try:
            with os.fdopen(os.open(fname, os.O_RDONLY)) as f:
                os.utime(f.fileno() if os.utime in os.supports_fd else fname)
            return True
        except:
            return False

    def _msg(self, pkg_name, override, success):
        prefix = "Freshened" if success else "Unable to freshen"
        return "%s '%s/%s'" % (prefix, pkg_name, override)

    def _handle_single(self, pkg_name, override):
        result = self._touch_override(pkg_name, override)
        return self._msg(pkg_name, override, result)

    def _handle_pkg(self, view, pkg_name):
        pkg_list = PackageList()
        if pkg_name not in pkg_list:
            return "Unable to freshen '%s'; no such package" % pkg_name

        count = 0
        expired_list = pkg_list[pkg_name].expired_override_files(simple=True)

        for expired_name in expired_list:
            result = self._touch_override(pkg_name, expired_name)
            _log(self._msg(pkg_name, expired_name, result))
            if result:
                count += 1

        if count == len(expired_list):
            prefix = "All"

            # None left; remove from the view setting now
            pkg_list = view.settings().get("override_audit_expired_pkgs", [])
            pkg_list.remove(pkg_name)
            view.settings().set("override_audit_expired_pkgs", pkg_list)
        else:
            prefix = "%d of %d" % (count, len(expired_list))

        return "%s expired overrides freshened in '%s'" % (prefix, pkg_name)

    def _process(self):
        view = self.args.get("view", None)
        pkg_name = self.args.get("pkg_name", None)
        override = self.args.get("override", None)
        if not view or not pkg_name:
            self.result = "Nothing done; missing parameters"
            return _log("freshen thread not given a view or package")

        if override is not None:
            self.result = self._handle_single(pkg_name, override)
        else:
            self.result = self._handle_pkg(view, pkg_name)


###----------------------------------------------------------------------------


class ReportGenerationThread(BackgroundWorkerThread):
    """
    Helper base class for generating a report in a background thread.
    """
    def __init__(self, window, spinner_text, current_view, **kwargs):
        super().__init__(window, spinner_text,
                         lambda thread: self._display_report(thread),
                         **kwargs)
        self.current_view = current_view

    def _generation_time(self):
        return datetime.now().strftime("Report Generated: %Y-%m-%d %H:%M:%S\n")

    def _display_report(self, thread):
        # Some reports don't call _set_content if they are empty
        if not hasattr(self, "content"):
            return

        force_reuse = self.args.get("force_reuse", False)

        reuse = True if force_reuse else _oa_setting("reuse_views")
        clear = True if force_reuse else _oa_setting("clear_existing")

        view = output_to_view(self.window, self.caption, self.content,
                              reuse, clear, self.syntax,
                              current_view=self.current_view)
        view.settings().set("override_audit_report_type", self.report_type)

        if self.settings is not None:
            for setting in self.settings:
                view.settings().set(setting, self.settings[setting])

    def _set_content(self, caption, content, report_type, syntax,
                     settings=None):
        self.caption = caption
        self.content = content
        self.report_type = report_type
        self.syntax = syntax
        self.settings = settings


###----------------------------------------------------------------------------


class PackageReportThread(ReportGenerationThread):
    """
    Generate a tabular report of all installed packages and their state.
    """
    def _process(self):
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

        result = [title, t_sep, "", self._generation_time(), stats, r_sep]
        for pkg_name, pkg_info in pkg_list:
            result.append(
                "| {:<40} | [{:1}] | [{:1}] | [{:1}] |".format(
                    _decorate_pkg_name(pkg_info, name_only=True),
                    "S" if pkg_info.shipped_path is not None else " ",
                    "I" if pkg_info.installed_path is not None else " ",
                    "U" if pkg_info.unpacked_path is not None else " "))
        result.extend([r_sep, ""])

        self._set_content("OverrideAudit: Package Report", result, ":packages",
                          _oa_syntax("OA-PkgReport"))


###----------------------------------------------------------------------------


class OverrideReportThread(ReportGenerationThread):
    """
    Generate a report on all packages which have overrides and what they are,
    if any. The report always includes expired packages and overrides, but the
    optional parameter filters to only show expired results.
    """
    def _process(self):
        pkg_list = PackageList()

        ignored = _oa_setting("ignore_overrides_in")

        only_expired = self.args["only_expired"]
        ignore_empty = self.args["ignore_empty"]

        if only_expired:
            title = "OverrideAudit: Expired Override Report"
            report_type = ":overrides_expired"
        else:
            title = "OverrideAudit: Override Report"
            report_type = ":overrides"

        expired_pkgs = []
        result = []
        if only_expired:
            result.append("WARNING: Showing only expired overrides!\n"
                          "WARNING: Non-expired overrides may exist!\n")
        result.append(self._generation_time())

        displayed = 0
        for pkg_name, pkg_info in pkg_list:
            if pkg_name not in ignored:
                if self._output_package(result, pkg_info, only_expired,
                                        expired_pkgs):
                    displayed += 1

        if displayed == 0:
            if ignore_empty:
                return sublime.set_timeout(self._notify_empty(), 10)

            result.append(self._empty_msg())

        self._set_content(title, result, report_type,
                          _oa_syntax("OA-OverrideReport"),
                          {"override_audit_expired_pkgs": expired_pkgs})

    def _output_package(self, result, pkg_info, only_expired, expired_pkgs):
        shipped_override = pkg_info.has_possible_overrides(simple=False)
        normal_overrides = pkg_info.override_files(simple=True)

        expired_overrides = pkg_info.expired_override_files(simple=True)
        expired_pkg = bool(pkg_info.expired_override_files(simple=False))

        # No need to do anything if there are no overrides at all
        if not normal_overrides and not shipped_override:
            return False

        if only_expired and not expired_overrides and not expired_pkg:
            return False

        if expired_overrides:
            expired_pkgs.append(pkg_info.name)

        result.append(_decorate_pkg_name(pkg_info))

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
        _log(self._empty_msg(), status=True)


###----------------------------------------------------------------------------


class BulkDiffReportThread(ReportGenerationThread):
    """
    Perform a bulk diff of all overrides in either all packages or a single
    package, depending on the argument provided.

    This is invoked from OverrideAuditDiffOverride when you invoke that command
    with the bulk argument set to true.
    """
    def _process(self):
        pkg_list = PackageList()

        package = self.args["package"]
        force_reuse = self.args["force_reuse"]

        if package is not None:
            if package not in pkg_list:
                return _log("Cannot diff package '%s'; not found" % package,
                            status=True, dialog=True)

            items = [package]
        else:
            items = _packages_with_overrides(pkg_list)

        self._diff_packages(items, pkg_list, package is not None, force_reuse)

    def _diff_packages(self, names, pkg_list, single_package, force_reuse):
        context_lines = _oa_setting("diff_context_lines")
        binary_patterns = _oa_setting("binary_file_patterns")

        result = []
        title = "Override Diff Report: "
        description = "Bulk Diff Report for overrides in"
        report_type = ":bulk_all"
        expired_pkgs = []

        if len(names) == 1 and single_package:
            title += names[0]
            result.append(description + " {}\n".format(names[0]))
            report_type = names[0]
        elif len(names) == 0:
            title += "All Packages"
            result.append("No packages with overrides found to diff\n")
        else:
            title += "All Packages"
            result.append(description + " {} packages\n".format(len(names)))

        result.append(self._generation_time())

        for name in names:
            pkg_info = pkg_list[name]
            if binary_patterns is not None:
                pkg_info.set_binary_pattern(binary_patterns)

            result.append(_decorate_pkg_name(pkg_info))
            self._perform_diff(pkg_info, context_lines, result,
                               expired_pkgs)

        self._set_content(title, result, report_type, _oa_syntax("OA-Diff"),
                          {"override_audit_expired_pkgs": expired_pkgs})

    def _perform_diff(self, pkg_info, context_lines, result, expired_pkgs):
        override_list = pkg_info.override_files(simple=True)
        expired_list = pkg_info.expired_override_files(simple=True)
        empty_diff_hdr = _oa_setting("diff_empty_hdr")

        if expired_list:
            expired_pkgs.append(pkg_info.name)

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
                content = (" " * 8) + ("Error opening or decoding file;"
                                       " is it UTF-8 or Binary?")
            else:
                prefix = diff.hdr if diff.is_empty and empty_diff_hdr else ""
                content = prefix + diff.result

            result.extend([content, ""])

        if len(override_list) == 0:
            if pkg_info.has_possible_overrides(simple=True):
                result.append("    [No simple overrides found]")
            else:
                reason = ("no sublime-package" if pkg_info.is_unpacked() else
                          "no unpacked files")
                result.append("    [No overrides possible; %s]" % reason)
        result.append("")


###----------------------------------------------------------------------------


class OverrideAuditPackageReportCommand(sublime_plugin.WindowCommand):
    """
    Generate a tabular report of all installed packages and their state.
    """
    def run(self, force_reuse=False):
        PackageReportThread(self.window, "Generating Package Report",
                            self.window.active_view(),
                            force_reuse=force_reuse).start()


###----------------------------------------------------------------------------


class OverrideAuditOverrideReportCommand(sublime_plugin.WindowCommand):
    """
    Generate a report on all packages which have overrides and what they are,
    if any. The report always includes expired packages and overrides, but the
    optional parameter filters to only show expired results.
    """
    def run(self, force_reuse=False, only_expired=False, ignore_empty=False):
        OverrideReportThread(self.window, "Generating Override Report",
                             self.window.active_view(),
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
                             self.window.active_view(),
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
            _log("Package '%s' has no overrides" % pkg_info.name,
                 status=True, dialog=True)

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
            _log("No unignored packages have overrides",
                 status=True, dialog=True)

        self.window.show_quick_panel(
            items=items,
            on_select=lambda i: self._pkg_pick(pkg_list, items, i, bulk))

    def _loaded(self, thread, package, override, bulk):
        pkg_list = thread.pkg_list

        if package is None:
            self._show_pkg_list(pkg_list, bulk)
        else:
            if package in pkg_list:
                pkg_info = pkg_list[package]
                if override is None:
                    self._show_override_list(pkg_info)
                else:
                    if pkg_info.has_possible_overrides():
                        _thr_diff_override(self.window, pkg_info, override)
                    else:
                        _log("Package '%s' has no overrides to diff" % package,
                             status=True, dialog=True)
            else:
                _log("Unable to diff; no package '%s'" % package,
                     status=True, dialog=True)

    def run(self, package=None, override=None, bulk=False):
        # Shortcut for bulk diffing a single package
        if bulk and package is not None:
            self.window.run_command("override_audit_diff_package",
                                    {"package": package})
            return

        callback = lambda thread: self._loaded(thread, package, override, bulk)
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
        scope = "text.override-audit " + scope
        if not self.view.match_selector(point, scope):
            return None

        return self.view.substr(self.view.extract_scope(point))

    def _package_at_point(self, event):
        return self._extract("entity.name.package", event)

    def _override_at_point(self, event, expired=False):
        scope="entity.name.filename.override"
        if expired:
            scope += ".expired"

        return self._extract(scope, event)

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
        return target.settings().get("override_audit_report_type")

    def _pkg_contains_expired(self, pkg_name, **kwargs):
        target = self.view_target(self.view, **kwargs)
        expired = target.settings().get("override_audit_expired_pkgs", [])
        return pkg_name in expired

    def view_target(self, view, group=-1, index=-1, **kwargs):
        """
        Get target view specified by group and index, if needed.
        """
        window = view.window()
        return view if group == -1 else window.views_in_group(group)[index]

    def view_context(self, view, expired, event=None, **kwargs):
        """
        Return a tuple of (pkg_name, override_name, is_diff) for the provided
        view and possible event. Some members of the tuple will be None if they
        do not apply or cannot be determined by the current command state.

        If view is none, view_target is invoked to determine it. Additionally,
        expired indicates if the override found needs to be expired or not.
        """
        if view is None:
            view = self.view_target(self.view, **kwargs)

        pkg_name = None
        override = None
        is_diff = None

        # Favor settings if they exist
        if override_group.has(view):
            pkg_name, override, is_diff = override_group.get(view)

        # Check for context clicks on a package or override name
        elif event is not None:
            pkg_name = self._package_at_point(event)
            if pkg_name is None:
                override = self._override_at_point(event, expired)
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
        pkg_name, override, is_diff = self.view_context(target, False, **kwargs)

        if action == "toggle":
            action = "diff" if not is_diff else "edit"

        if action == "diff":
            if (_oa_setting("save_on_diff") and target.is_dirty() and
                    os.path.isfile(target.file_name())):
                target.run_command("save")
            self._context_diff(target.window(), pkg_name, override)

        elif action == "edit":
            _open_override(target.window(), pkg_name, override)

        elif action == "delete":
            _delete_override(target.window(), pkg_name, override)

        else:
            _log("Error: unknown action for override context: %s", action)

    def _context_diff(self, window, package, override):
        callback = lambda thr: self._pkg_loaded(thr, window, package, override)
        PackageListCollectionThread(window, "Collecting Package List",
                                    callback).start()

    def _pkg_loaded(self, thread, window, pkg_name, override):
        pkg_list = thread.pkg_list
        _thr_diff_override(window, pkg_list[pkg_name], override,
                           diff_only=True, force_reuse=True)

    def description(self, action, **kwargs):
        pkg_name, override, is_diff = self.view_context(None, False, **kwargs)

        if action == "toggle":
            action = "diff" if is_diff is False else "edit"

        return "OverrideAudit: %s Override '%s'" % (action.title(), override)

    def is_visible(self, action, **kwargs):
        pkg_name, override, is_diff = self.view_context(None, False, **kwargs)

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
    def run(self, edit, action, event):
        pkg_name = self._package_at_point(event)
        if action == "diff":
            self.view.window().run_command("override_audit_diff_package",
                                           {"package": pkg_name})
        elif action == "freshen":
            _thr_freshen_override(self.view, pkg_name)
        else:
            _log("Error: unknown action for package context: %s", action)

    def description(self, action, event, **kwargs):
        pkg_name = self._package_at_point(event)

        if action == "diff":
            return "OverrideAudit: Bulk Diff Package '%s'" % pkg_name
        elif action == "freshen":
            return "OverrideAudit: Freshen Expired Overrides in '%s'" % pkg_name

    def is_visible(self, action, event, **kwargs):
        pkg_name = self._package_at_point(event)
        if pkg_name is None:
            return False

        if action == "freshen":
            return self._pkg_contains_expired(pkg_name, **kwargs)

        return not self._report_type(**kwargs) == pkg_name


###----------------------------------------------------------------------------


class OverrideAuditContextReportCommand(ContextHelper,sublime_plugin.TextCommand):
    """
    Offer to refresh existing reports after manual changes have been made.
    """
    def run(self, edit, **kwargs):
        target_view = self.view_target(self.view, **kwargs)
        window = target_view.window()
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

        window.focus_view(target_view)
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

        result = PackageInfo.check_potential_override(filename, deep=True)
        if result is not None:
            override_group.apply(view, result[0], result[1], False)
        else:
            override_group.remove(view)

    def on_post_save_async(self, view):
        # Will remove existing settings if the view is no longer an override
        self._check_for_override(view)

    def on_load_async(self, view):
        # Things like PackageResourceViewer trigger on_load before the file
        # actually exists; context items are only allowed once the file is
        # actually saved.
        self._check_for_override(view)

    def on_query_context(self, view, key, operator, operand, match_all):
        if key == "override_audit_override_view":
            lhs = override_group.has(view)
        elif key == "override_audit_report_view":
            lhs = view.settings().has("override_audit_report_type")
        else:
            return None

        rhs = bool(operand)

        if operator == sublime.OP_EQUAL:
            return lhs == rhs
        elif operator == sublime.OP_NOT_EQUAL:
            return lhs != rhs

        return None


###----------------------------------------------------------------------------
