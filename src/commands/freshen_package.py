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
        target = self.view_target(self.view, **kwargs)
        package, _o, _d = self.view_context(target, False, **kwargs)

        freshen_override(self.view, package)

    def description(self, **kwargs):
        target = self.view_target(self.view, **kwargs)
        package, _o, _d = self.view_context(target, False, **kwargs)

        return "OverrideAudit: Freshen Expired Overrides in '%s'" % package

    def is_visible(self, **kwargs):
        target = self.view_target(self.view, **kwargs)
        package, override, _ = self.view_context(target, False, **kwargs)

        if package is None or override is not None:
            return False

        return self._pkg_contains_expired(package, **kwargs)

    def is_enabled(self, **kwargs):
        target = self.view_target(self.view, **kwargs)
        package, _o, _d = self.view_context(target, False, **kwargs)

        return package is not None

###----------------------------------------------------------------------------
