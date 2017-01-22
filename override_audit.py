import sublime
import sublime_plugin

from .lib.packages import *
from .lib.output_view import output_to_view

###-----------------------------------------------------------------------------

class OverrideAuditListPackagesCommand(sublime_plugin.WindowCommand):
    def run(self):
        pkg_list = PackageList ()

        caption = "Total Packages Installed: {}".format (len (pkg_list))
        c_sep = "-" * len (caption)
        header = "| {:3} | {:3} | {:3} | {:<40} |".format ("Shp", "Ins", "Unp", "Package")
        h_sep = "-" * len (header)

        result = [caption, c_sep, "", h_sep, header, h_sep]
        for pkg_name, pkg_info in pkg_list:
            result.append (
                "| [{:1}] | [{:1}] | [{:1}] | {:<40} |".format (
                "X" if pkg_info.shipped_path is not None else " ",
                "X" if pkg_info.installed_path is not None else " ",
                "X" if pkg_info.unpacked_path is not None else " ",
                pkg_name)
                )
        result.extend ([h_sep, ""])

        output_to_view (self.window,
                        "OverrideAudit: Package List",
                        result,
                        syntax="Packages/OverrideAudit/syntax/OverrideAudit-table.sublime-syntax")

###-----------------------------------------------------------------------------
