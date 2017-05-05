import sublime
import sublime_plugin

from ..override_audit import ContextHelper, freshen_override


###----------------------------------------------------------------------------


class OverrideAuditFreshenPackageCommand(ContextHelper,sublime_plugin.TextCommand):
    """
    Freshen the given package on disk so it is no longer considered expired.
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
        package, _o, _d = self.view_context(target, False, **kwargs)

        if package is None:
            return False

        return self._pkg_contains_expired(package, **kwargs)


###----------------------------------------------------------------------------
