import sublime
import sublime_plugin

import os


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
        if ctx.source == "settings":
            return "OverrideAudit: Delete this Override"

        stub = "OverrideAudit: Delete Override"
        if ctx.has_target():
            return "%s '%s'" % (stub, ctx.override)
        else:
            return stub

    def is_visible(self, **kwargs):
        if self.always_visible(**kwargs):
            return True

        return self.view_context(None, False, **kwargs).has_target()

    def is_enabled(self, **kwargs):
        return self.override_exists(self.view_context(None, False, **kwargs))


###----------------------------------------------------------------------------
