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
        if ctx.package_only():
            return "OverrideAudit: Freshen Expired Overrides in '%s'" % ctx.package
        else:
            return "OverrideAudit: Freshen Expired Package"

    def is_visible(self, **kwargs):
        if self.always_visible(**kwargs):
            return True

        ctx = self.view_context(None, False, **kwargs)
        expired = self._pkg_contains_expired(ctx.package, **kwargs)

        return expired and ctx.package_only()

    def is_enabled(self, **kwargs):
        ctx = self.view_context(None, False, **kwargs)
        expired = self._pkg_contains_expired(ctx.package, **kwargs)

        return expired and self.package_exists(ctx)


###----------------------------------------------------------------------------
