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
        # TODO: This is freshening every expired overide in every package,
        # but it should actually be executing a diff to determine what files
        # are actually unmodified and then freshening those instead.
        view = self.view_target(self.view, **kwargs)
        pkg_list = view.settings().get("override_audit_expired_pkgs", [])
        freshen_override(view, pkg_list, [None] * len(pkg_list))

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
            return len(view.settings().get("override_audit_expired_pkgs", [])) > 0

        return False


###----------------------------------------------------------------------------
