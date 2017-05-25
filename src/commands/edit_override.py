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

        return "OverrideAudit: Edit Override '%s'" % ctx.override

    def is_visible(self, **kwargs):
        ctx = self.view_context(None, False, **kwargs)

        if ctx.has_target():
            return ctx.is_diff is None or ctx.is_diff

        return False

    def is_enabled(self, **kwargs):
        return self.view_context(None, False, **kwargs).has_target()


###----------------------------------------------------------------------------
