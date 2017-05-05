import sublime
import sublime_plugin

from ..core import ContextHelper


###----------------------------------------------------------------------------


class OverrideAuditToggleOverrideCommand(ContextHelper,sublime_plugin.TextCommand):
    """
    Swap between editing an override or diffing it based on the current state.
    This only applies to open views as it requires state information to know
    what to do.
    """
    def run(self, edit, **kwargs):
        target = self.view_target(self.view, **kwargs)
        pkg_name, override, is_diff = self.view_context(target, False, **kwargs)

        args = {"pkg_name": pkg_name, "override": override}
        if is_diff is not None:
            args["is_diff"] = is_diff

        if is_diff:
            target.run_command("override_audit_edit_override", args)
        else:
            target.run_command("override_audit_diff_override", args)

    def description(self, **kwargs):
        target = self.view_target(self.view, **kwargs)
        pkg_name, override, _ = self.view_context(target, False, **kwargs)

        return "OverrideAudit: Toggle Override '%s'" % override

    def is_visible(self, **kwargs):
        target = self.view_target(self.view, **kwargs)
        pkg_name, override, is_diff = self.view_context(target, False, **kwargs)

        if pkg_name is not None and override is not None:
            return True if is_diff is not None else False

        return False


###----------------------------------------------------------------------------
