import sublime
import sublime_plugin

from ..core import ContextHelper, freshen_override


###----------------------------------------------------------------------------


class OverrideAuditFreshenAllCommand(ContextHelper,sublime_plugin.TextCommand):
    """
    Freshen all of the expired overrides in all packages represented in the
    current report so that it's no longer considered expired. This does what
    the override_audit_freshen_package command does, but for all packages and
    not just the one under the cursor.
    """
    def run(self, edit, **kwargs):
        print("Refreshing, isn't it")
        # freshen_override(self.view, ctx.package)

    def description(self, **kwargs):
        return "OverrideAudit: Freshen All Expired Overrides"

    def is_visible(self, **kwargs):
        if self.always_visible(**kwargs):
            return True

        return self.is_enabled(**kwargs)

    def is_enabled(self, **kwargs):
        report = self._report_type(**kwargs)
        if report is not None and report != ":packages":
            view = self.view_target(self.view, **kwargs)
            return bool(view.find_by_selector("entity.name.filename.override.expired"))

        return False


###----------------------------------------------------------------------------
