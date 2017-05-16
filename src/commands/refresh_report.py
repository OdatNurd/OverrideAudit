import sublime
import sublime_plugin

from ..core import ContextHelper


###----------------------------------------------------------------------------


class OverrideAuditRefreshReportCommand(ContextHelper,sublime_plugin.TextCommand):
    """
    Offer to refresh existing reports after manual changes have been made. This
    can only be invoked when the current view is a report.
    """
    def run(self, edit, **kwargs):
        target_view = self.view_target(self.view, **kwargs)
        window = target_view.window()
        report_type = self._report_type(**kwargs)

        command = {
            ":packages":          "override_audit_package_report",
            ":overrides":         "override_audit_override_report",
            ":overrides_expired": "override_audit_override_report"
        }.get(report_type, "override_audit_diff_report")
        args = {"force_reuse": True}

        if report_type[0] != ":":
            args["package"] = report_type
        elif report_type == ":overrides_expired":
            args["only_expired"] = True

        window.focus_view(target_view)
        window.run_command(command, args)

    def description(self, **kwargs):
        report = self._report_type(**kwargs)
        report = {
            ":packages":          "Package Report",
            ":overrides":         "Override Report",
            ":overrides_expired": "Override Report (Expired only)",
            ":bulk_all":          "Bulk Diff Report"
        }.get(report, "Bulk Diff of '%s'" % report)

        return "OverrideAudit: Refresh %s" % report

    def is_visible(self, **kwargs):
        return self._report_type(**kwargs) is not None

    def is_enabled(self, **kwargs):
        return self._report_type(**kwargs) is not None


###----------------------------------------------------------------------------
