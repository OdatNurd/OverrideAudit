import sublime
import sublime_plugin

from ..core import ContextHelper, open_override


###----------------------------------------------------------------------------


class OverrideAuditEditOverrideCommand(ContextHelper,sublime_plugin.TextCommand):
    """
    Open a given override for editing.
    """
    def run(self, edit, **kwargs):
        target = self.view_target(self.view, **kwargs)
        ctx = self.view_context(target, False, **kwargs)

        open_override(target.window(), ctx.package, ctx.override)

    def description(self, **kwargs):
        ctx = self.view_context(None, False, **kwargs)
        if ctx.source == "settings":
            return self.caption("Edit this Override", **kwargs)

        stub = "Edit Override"
        if ctx.has_target():
            return self.caption("%s '%s'" % (stub, ctx.override), **kwargs)
        else:
            return self.caption(stub, **kwargs)

    def is_visible(self, **kwargs):
        if self.always_visible(**kwargs):
            return True

        ctx = self.view_context(None, False, **kwargs)
        if ctx.has_target():
            return ctx.is_diff if ctx.has_diff() else True

        return False

    def is_enabled(self, **kwargs):
        ctx = self.view_context(None, False, **kwargs)
        if self.override_exists(ctx):
            return ctx.is_diff if ctx.has_diff() else True

        return False


###----------------------------------------------------------------------------
