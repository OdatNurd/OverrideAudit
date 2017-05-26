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
        ctx = self.view_context(target, False, **kwargs)

        args = {"package": ctx.package, "override": ctx.override}
        if ctx.is_diff is not None:
            args["is_diff"] = ctx.is_diff

        if ctx.is_diff:
            target.run_command("override_audit_edit_override", args)
        else:
            target.run_command("override_audit_diff_override", args)

    def description(self, **kwargs):
        return "OverrideAudit: Swap Diff/Edit of Current Override"

    def is_visible(self, **kwargs):
        if self.always_visible(**kwargs):
            return True

        ctx = self.view_context(None, False, **kwargs)
        return true if ctx.has_target() and ctx.has_diff() else False

    def is_enabled(self, **kwargs):
        ctx = self.view_context(None, False, **kwargs)
        return ctx.has_diff() and self.override_exists(ctx)


###----------------------------------------------------------------------------
