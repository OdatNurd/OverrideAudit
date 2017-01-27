import sublime
import sublime_plugin

from .lib.packages import *
from .lib.output_view import output_to_view

###-----------------------------------------------------------------------------

class OverrideAuditListPackagesCommand(sublime_plugin.WindowCommand):
    def run(self):
        pkg_list = PackageList()
        pkg_counts = pkg_list.package_counts()

        settings = sublime.load_settings("OverrideAudit.sublime-settings")

        title = "Packages: {} ({} dependencies)".format(len(pkg_list), pkg_counts[4])
        t_sep = "=" * len(title)

        stats = ("Shipped:   {:<6} (Shipped with Sublime)\n"
                 "Installed: {:<6} (Installed as sublime-package files)\n"
                 "Unpacked:  {:<6} (Unpacked in Packages\\ directory)\n"
                 "Disabled:  {:<6} (Currently in ignored_packages)\n").format(*pkg_counts)

        row = "| {:3} | {:3} | {:3} | {:<40} |".format("", "", "", "")
        r_sep = "-" * len(row)

        result = [title, t_sep, "", stats, r_sep]
        for pkg_name, pkg_info in pkg_list:
            if pkg_info.disabled:
                pkg_name = "[{}]".format (pkg_name)
            elif pkg_info.is_dependency:
                pkg_name = "<{}>".format (pkg_name)
            result.append (
                "| [{:1}] | [{:1}] | [{:1}] | {:<40} |".format(
                "S" if pkg_info.shipped_path is not None else " ",
                "I" if pkg_info.installed_path is not None else " ",
                "U" if pkg_info.unpacked_path is not None else " ",
                pkg_name))
        result.extend([r_sep, ""])

        output_to_view(self.window,
                       "OverrideAudit: Package List",
                       result,
                       reuse=settings.get("reuse_views", True),
                       clear=settings.get("clear_existing", True),
                       syntax="Packages/OverrideAudit/syntax/OverrideAudit-table.sublime-syntax")

###-----------------------------------------------------------------------------
