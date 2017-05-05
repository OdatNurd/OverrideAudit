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
        pkg_name, override, _ = self.view_context(target, True, **kwargs)

        freshen_override(target, pkg_name, override)

    def description(self, **kwargs):
        target = self.view_target(self.view, **kwargs)
        pkg_name, override, _ = self.view_context(target, True, **kwargs)

        return "OverrideAudit: Freshen Override '%s'" % override

    def is_visible(self, **kwargs):
        target = self.view_target(self.view, **kwargs)
        pkg_name, override, _ = self.view_context(target, True, **kwargs)

        return pkg_name is not None and override is not None

###----------------------------------------------------------------------------
