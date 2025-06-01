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

        window = self.view.window()
        if window is not None:
            window.run_command("override_audit_diff_report",
                               {"package": ctx.package})

    def description(self, **kwargs):
        stub = "Bulk Diff Package"
        ctx = self.view_context(None, False, **kwargs)
        if ctx.package_only():
            return self.caption("%s '%s'" % (stub, ctx.package), **kwargs)
        else:
            return self.caption(stub, **kwargs)

    def is_visible(self, **kwargs):
        if self.always_visible(**kwargs):
            return True

        return self.is_enabled(**kwargs)

    def is_enabled(self, **kwargs):
        target = self.view_target(self.view, **kwargs)
        ctx = self.view_context(target, False, **kwargs)
        report_type = self._report_type(**kwargs)

        return (report_type != ctx.package and
                self.package_overrides_possible(target, ctx) and
                self.package_exists(ctx))


###----------------------------------------------------------------------------
