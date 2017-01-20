import sublime
import sublime_plugin

from .lib.packages import *

###-----------------------------------------------------------------------------

class oa_impl_list_plugins(sublime_plugin.TextCommand):
    def insert_title(self, pkg_list):
        caption = "Total Packages Installed: %d" % len (pkg_list)
        self.result.extend ([
            caption,
            "-" * len (caption),
            "\n"
            ])

    def insert_header(self, pkg_list):
        header = "| {:3} | {:3} | {:3} | {:<40} |".format ("Shp", "Ins", "Unp", "Package")
        hLen = len (header)
        self.result.extend ([
            "-" * hLen,
            header,
            "-" * hLen,
            ])
        return hLen

    def insert_record(self, pkg_info):
        self.result.append (
            "| [{:1}] | [{:1}] | [{:1}] | {:<40} |".format (
            "X" if pkg_info.shipped_path is not None else " ",
            "X" if pkg_info.installed_path is not None else " ",
            "X" if pkg_info.unpacked_path is not None else " ",
            pkg_info.name)
            )

    def insert_footer(self, pkg_list, length):
        self.result.append ("-" * length)

    def generate_list(self, pkg_list):
        self.insert_title (pkg_list)
        l = self.insert_header (pkg_list)
        for name, info in pkg_list:
            self.insert_record(info)
        self.insert_footer (pkg_list, l)

    def run(self, edit):
        self.result = []
        self.generate_list (PackageList ())
        self.view.erase (edit, sublime.Region (0, self.view.size ()))
        self.view.run_command ("insert", {"characters": "\n".join (self.result)})

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
            if self.window.active_view () != view:
                self.window.focus_view (view)

        return view

    def run(self):
        title = "OverrideAudit: Package List"
        syntax = "Packages/OverrideAudit/OverrideAudit-table.sublime-syntax"
        view = self.get_view (title, syntax)
        view.run_command ("oa_impl_list_plugins")
        view.set_read_only (True)

###-----------------------------------------------------------------------------
