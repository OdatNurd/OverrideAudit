import sublime
import sublime_plugin

from ..core import ContextHelper


###----------------------------------------------------------------------------


class OverrideAuditDiffPackageCommand(ContextHelper,sublime_plugin.TextCommand):
    """
    Bulk diff either a single package or all packages. This can be invoked via
    a context menu to set a package, invoked with a "package" argument to set
    the package, or with no arguments to diff all packages.
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
        package, override, _ = self.view_context(target, False, **kwargs)

        if package is None or override is not None:
            return False

        return not self._report_type(**kwargs) == package


###----------------------------------------------------------------------------
