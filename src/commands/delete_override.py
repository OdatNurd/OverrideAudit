import sublime
import sublime_plugin

from ..core import ContextHelper, delete_override


###----------------------------------------------------------------------------


class OverrideAuditDeleteOverrideCommand(ContextHelper,sublime_plugin.TextCommand):
    """
    Delete the provided override file from disk.
    """
    def run(self, edit, **kwargs):
        target = self.view_target(self.view, **kwargs)
        ctx = self.view_context(target, False, **kwargs)
        delete_override(target.window(), ctx.package, ctx.override)

    def description(self, **kwargs):
        ctx = self.view_context(None, False, **kwargs)

        return "OverrideAudit: Delete Override '%s'" % ctx.override

    # TODO this should only trigger if the file that's going to be potentially
    # deleted actually exists on disk right now. Currently delete_override()
    # will do nothing, so this should not offer it.
    def is_visible(self, **kwargs):
        return self.view_context(None, False, **kwargs).has_target()

    def is_enabled(self, **kwargs):
        return self.view_context(None, False, **kwargs).has_target()


###----------------------------------------------------------------------------
