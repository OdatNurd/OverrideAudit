import sublime
import sublime_plugin

from ..core import diff_override, packages_with_overrides, log
from ..core import PackageListCollectionThread


###----------------------------------------------------------------------------


class OverrideAuditDiffSingleCommand(sublime_plugin.WindowCommand):
    """
    Selective diff of a single override or package based on the provided
    arguments. The user will be prompted via quick panel to select the value of
    any elided arguments (except bulk which controls the output).
    """
    def _file_pick(self, pkg_info, override_list, index):
        if index >= 0:
            diff_override(self.window, pkg_info, override_list[index])

    def _show_override_list(self, pkg_info):
        override_list = list(pkg_info.override_files())
        if not override_list:
            log("Package '%s' has no overrides" % pkg_info.name,
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
                self.window.run_command("override_audit_diff_report",
                                        {"package": pkg_info.name})

    def _show_pkg_list(self, pkg_list, bulk):
        items = packages_with_overrides(pkg_list)

        if not items:
            log("No unignored packages have overrides",
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
                        diff_override(self.window, pkg_info, override)
                    else:
                        log("Package '%s' has no overrides to diff" % package,
                             status=True, dialog=True)
            else:
                log("Unable to diff; no package '%s'" % package,
                     status=True, dialog=True)

    def run(self, package=None, override=None, bulk=False):
        # Shortcut for bulk diffing a single package
        if bulk and package is not None:
            self.window.run_command("override_audit_diff_report",
                                    {"package": package})
            return

        callback = lambda thread: self._loaded(thread, package, override, bulk)
        PackageListCollectionThread(self.window, "Collecting Package List",
                                    callback, get_overrides=True).start()


###----------------------------------------------------------------------------
