import sublime
import sublime_plugin

from ..core import ContextHelper, freshen_override


###----------------------------------------------------------------------------


class OverrideAuditFreshenOverrideCommand(ContextHelper,sublime_plugin.TextCommand):
    """
    Freshen the given override on disk so it is no longer considered expired.
    """
    def run(self, edit, **kwargs):
        target = self.view_target(self.view, **kwargs)
        ctx = self.view_context(target, True, **kwargs)

        freshen_override(target, ctx.package, ctx.override)

    def description(self, **kwargs):
        stub = "Freshen Override"
        ctx = self.view_context(None, True, **kwargs)
        if ctx.has_target():
            return self.caption("%s '%s'" % (stub, ctx.override), **kwargs)
        else:
            return self.caption(stub, **kwargs)

    def is_visible(self, **kwargs):
        if self.always_visible(**kwargs):
            return True

        return self.view_context(None, True, **kwargs).has_target()

    def is_enabled(self, **kwargs):
        ctx = self.view_context(None, True, **kwargs)
        return self.override_exists(ctx)


###----------------------------------------------------------------------------
