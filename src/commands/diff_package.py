import sublime
import sublime_plugin

from ..override_audit import ContextHelper


###----------------------------------------------------------------------------


class OverrideAuditDiffPackageCommand(ContextHelper,sublime_plugin.TextCommand):
    """
    Freshen the given package on disk so it is no longer considered expired.
    """
    def run(self, edit, **kwargs):
        target = self.view_target(self.view, **kwargs)
        package, _o, _d = self.view_context(target, False, **kwargs)

        self.view.window().run_command("override_audit_diff_report",
                                       {"package": package})

    def description(self, **kwargs):
        target = self.view_target(self.view, **kwargs)
        package, _o, _d = self.view_context(target, False, **kwargs)

        return "OverrideAudit: Bulk Diff Package '%s'" % package

    def is_visible(self, **kwargs):
        target = self.view_target(self.view, **kwargs)
        package, _o, _d = self.view_context(target, False, **kwargs)

        if package is None:
            return False

        return not self._report_type(**kwargs) == package


###----------------------------------------------------------------------------
