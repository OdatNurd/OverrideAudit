import sublime
import sublime_plugin

from ..core import ContextHelper, open_override


###----------------------------------------------------------------------------


class OverrideAuditEditOverrideCommand(ContextHelper,sublime_plugin.TextCommand):
    """
    Open a diff of a given override. If the current view represents the
    override, it will be saved before the diff happens.
    """
    def run(self, edit, **kwargs):
        target = self.view_target(self.view, **kwargs)
        pkg_name, override, _ = self.view_context(target, False, **kwargs)

        open_override(target.window(), pkg_name, override)

    def description(self, **kwargs):
        target = self.view_target(self.view, **kwargs)
        pkg_name, override, _ = self.view_context(target, False, **kwargs)

        return "OverrideAudit: Edit Override '%s'" % override

    def is_visible(self, **kwargs):
        target = self.view_target(self.view, **kwargs)
        pkg_name, override, is_diff = self.view_context(target, False, **kwargs)

        if pkg_name is not None and override is not None:
            return is_diff is None or is_diff

        return False


###----------------------------------------------------------------------------
