import sublime_plugin

from ..core import oa_syntax, decorate_pkg_name
from ..core import ReportGenerationThread
from ...lib.packages import PackageList

###----------------------------------------------------------------------------


class PackageReportThread(ReportGenerationThread):
    """
    Generate a tabular report of all installed packages and their state.
    """
    def _process(self):
        pkg_list = PackageList()
        pkg_counts = pkg_list.package_counts()

        title = f"{len(pkg_list)} Total Packages"
        t_sep = "=" * len(title)

        fmt = '{{:>{}}}'.format(len(str(max(pkg_counts))))
        stats = ("{0} [S]hipped with Sublime\n"
                 "{0} [I]nstalled (user) sublime-package files\n"
                 "{0} [U]npacked in Packages\\ directory\n"
                 "{0} Currently in ignored_packages\n"
                 "{0} Installed Legacy-style Dependencies\n").format(fmt).format(*pkg_counts)

        r_sep = "+------------------------------------------+-----+-----+-----+"

        packages = {}
        result = [title, t_sep, "", self._generation_time(), stats, r_sep]
        for pkg_name, pkg_info in pkg_list:
            packages[pkg_name] = pkg_info.status(detailed=False)

            result.append(
                "| {:<40} | [{:1}] | [{:1}] | [{:1}] |".format(
                    decorate_pkg_name(pkg_info, name_only=True),
                    "S" if pkg_info.shipped_path is not None else " ",
                    "I" if pkg_info.installed_path is not None else " ",
                    "U" if pkg_info.unpacked_path is not None else " "))
        result.extend([r_sep, ""])

        self._set_content("OverrideAudit: Package Report", result, ":packages",
                          oa_syntax("OA-PkgReport"), {
                            "override_audit_report_packages": packages,
                            "context_menu": "OverrideAuditReport.sublime-menu"
                         })


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
#