import sublime
import sublime_plugin

from .lib.packages import *

###-----------------------------------------------------------------------------

class OverrideAuditListPluginsCommand(sublime_plugin.WindowCommand):
    def get_view(self, title, syntax):
        view = None
        for tmpView in self.window.views ():
            if tmpView.name () == title:
                view = tmpView
                break

        if view is None:
            view = self.window.new_file ()
            view.set_scratch (True)
            view.set_name (title)
            view.assign_syntax (syntax)
        else:
            view.set_read_only (False)

            view.sel ().clear ()
            view.sel ().add (sublime.Region (0, view.size ()))
            view.run_command ("left_delete")

            if self.window.active_view () != view:
                self.window.focus_view (view)

        return view

    def generate(self, view):
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
        result.append (h_sep)

        view.run_command ("insert", {"characters": "\n".join (result)})
        view.run_command ("move_to", {"to": "bof", "extend": False})
        view.set_read_only (True)

    def run(self):
        title = "OverrideAudit: Package List"
        syntax = "Packages/OverrideAudit/OverrideAudit-table.sublime-syntax"
        view = self.get_view (title, syntax)

        self.generate(view)

###-----------------------------------------------------------------------------
