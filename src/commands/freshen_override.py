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
        package, override, _ = self.view_context(target, True, **kwargs)

        freshen_override(target, package, override)

    def description(self, **kwargs):
        target = self.view_target(self.view, **kwargs)
        package, override, _ = self.view_context(target, True, **kwargs)

        return "OverrideAudit: Freshen Override '%s'" % override

    def is_visible(self, **kwargs):
        target = self.view_target(self.view, **kwargs)
        package, override, _ = self.view_context(target, True, **kwargs)

        return package is not None and override is not None

    def is_enabled(self, **kwargs):
        target = self.view_target(self.view, **kwargs)
        package, override, _ = self.view_context(target, True, **kwargs)

        return package is not None and override is not None


###----------------------------------------------------------------------------
