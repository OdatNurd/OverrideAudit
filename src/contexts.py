import sublime
import sublime_plugin

from .core import override_group


###----------------------------------------------------------------------------


class OverrideAuditContextListener(sublime_plugin.EventListener):
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
