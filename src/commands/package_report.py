import sublime
import sublime_plugin

from ..override_audit import oa_syntax, decorate_pkg_name
from ..override_audit import ReportGenerationThread
from ...lib.packages import PackageList

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
                    decorate_pkg_name(pkg_info, name_only=True),
                    "S" if pkg_info.shipped_path is not None else " ",
                    "I" if pkg_info.installed_path is not None else " ",
                    "U" if pkg_info.unpacked_path is not None else " "))
        result.extend([r_sep, ""])

        self._set_content("OverrideAudit: Package Report", result, ":packages",
                          oa_syntax("OA-PkgReport"))


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