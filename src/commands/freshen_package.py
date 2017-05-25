import sublime
import sublime_plugin

from ..core import ContextHelper, freshen_override


###----------------------------------------------------------------------------


class OverrideAuditFreshenPackageCommand(ContextHelper,sublime_plugin.TextCommand):
    """
    Freshen the given package on disk so it is no longer considered expired.
    This will touch all expired overrides and also remove their expiration
    remark (if invoked from within an override report).
    """
    def run(self, edit, **kwargs):
        ctx = self.view_context(None, False, **kwargs)

        freshen_override(self.view, ctx.package)

    def description(self, **kwargs):
        ctx = self.view_context(None, False, **kwargs)

        return "OverrideAudit: Freshen Expired Overrides in '%s'" % ctx.package

    def is_visible(self, **kwargs):
        ctx = self.view_context(None, False, **kwargs)

        if ctx.package is None or ctx.override is not None:
            return False

        return self._pkg_contains_expired(ctx.package, **kwargs)

    def is_enabled(self, **kwargs):
        ctx = self.view_context(None, False, **kwargs)

        return ctx.package is not None


###----------------------------------------------------------------------------
