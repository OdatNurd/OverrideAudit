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
        ctx = self.view_context(None, True, **kwargs)

        return "OverrideAudit: Freshen Override '%s'" % ctx.override

    def is_visible(self, **kwargs):
        return self.view_context(None, True, **kwargs).has_target()

    def is_enabled(self, **kwargs):
        return self.view_context(None, True, **kwargs).has_target()


###----------------------------------------------------------------------------
