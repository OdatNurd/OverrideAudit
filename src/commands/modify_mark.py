import sublime
import sublime_plugin

from ..core import find_override


###----------------------------------------------------------------------------


class OverrideAuditModifyMarkCommand(sublime_plugin.TextCommand):
    """
    Modify the mark assigned to an override in a report. An override only
    supports a single mark, if any. Passing a mark of None removes any mark.
    """
    def run(self, edit, package, override, mark=None):
        pos = find_override(self.view, package, override)
        if pos is None:
            return

        mark_pos = sublime.Region(pos.begin() - 4, pos.begin())
        current_mark = self.view.substr(mark_pos)

        if mark is None and current_mark[0] == " ":
            return

        new_mark = ""
        if mark is not None:
            new_mark = '[%s] ' % mark[0]
            if current_mark[0] == " ":
                mark_pos = sublime.Region(pos.begin(), pos.begin())

        self.view.set_read_only(False)
        self.view.replace(edit, mark_pos, new_mark)
        self.view.set_read_only(True)

    def is_enabled(self, package, override, mark=None):
        return self.view.settings().has("override_audit_report_type")


###----------------------------------------------------------------------------
