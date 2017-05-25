import sublime
import sublime_plugin

from ..core import ContextHelper


###----------------------------------------------------------------------------


# TODO: The is_visible and is_enabled in this command need some work because
# they're probably triggering when they should not, going forward.
class OverrideAuditToggleOverrideCommand(ContextHelper,sublime_plugin.TextCommand):
    """
    Swap between editing an override or diffing it based on the current state.
    This only applies to open views as it requires state information to know
    what to do.
    """
    def run(self, edit, **kwargs):
        target = self.view_target(self.view, **kwargs)
        ctx = self.view_context(target, False, **kwargs)

        args = {"package": ctx.package, "override": ctx.override}
        if ctx.is_diff is not None:
            args["is_diff"] = ctx.is_diff

        if ctx.is_diff:
            target.run_command("override_audit_edit_override", args)
        else:
            target.run_command("override_audit_diff_override", args)

    def description(self, **kwargs):
        ctx = self.view_context(None, False, **kwargs)

        return "OverrideAudit: Toggle Override '%s'" % ctx.override

    def is_visible(self, **kwargs):
        ctx = self.view_context(None, False, **kwargs)

        if ctx.has_target():
            return ctx.has_diff()

        return False

    def is_enabled(self, **kwargs):
        return self.view_context(None, False, **kwargs).has_target()


###----------------------------------------------------------------------------
