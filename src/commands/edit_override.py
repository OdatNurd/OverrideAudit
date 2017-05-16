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
        package, override, _ = self.view_context(target, False, **kwargs)

        open_override(target.window(), package, override)

    def description(self, **kwargs):
        target = self.view_target(self.view, **kwargs)
        package, override, _ = self.view_context(target, False, **kwargs)

        return "OverrideAudit: Edit Override '%s'" % override

    def is_visible(self, **kwargs):
        target = self.view_target(self.view, **kwargs)
        package, override, is_diff = self.view_context(target, False, **kwargs)

        if package is not None and override is not None:
            return is_diff is None or is_diff

        return False

    def is_enabled(self, **kwargs):
        target = self.view_target(self.view, **kwargs)
        package, override, _ = self.view_context(target, False, **kwargs)

        return package is not None and override is not None


###----------------------------------------------------------------------------
