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
        ctx = self.view_context(None, False, **kwargs)

        self.view.window().run_command("override_audit_diff_report",
                                       {"package": ctx.package})

    def description(self, **kwargs):
        ctx = self.view_context(None, False, **kwargs)

        return "OverrideAudit: Bulk Diff Package '%s'" % ctx.package

    def is_visible(self, **kwargs):
        ctx = self.view_context(None, False, **kwargs)

        if ctx.package is None or ctx.override is not None:
            return False

        return not self._report_type(**kwargs) == ctx.package


###----------------------------------------------------------------------------
