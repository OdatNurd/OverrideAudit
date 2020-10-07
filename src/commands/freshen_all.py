import sublime
import sublime_plugin

from ...lib.packages import PackageInfo
from ..core import log, ContextHelper, freshen_override
from ..core import filter_unmodified_overrides


###----------------------------------------------------------------------------


# TODO: This should be threaded since it gathers package information when it
# runs (and it should create a PackageList object and not a bunch of singles).
class OverrideAuditFreshenAllCommand(ContextHelper,sublime_plugin.TextCommand):
    """
    Freshen all of the expired overrides in all packages represented in the
    current report so that it's no longer considered expired. This does what
    the override_audit_freshen_package command does, but for all packages and
    not just the one under the cursor.
    """
    def run(self, edit, **kwargs):
        view = self.view_target(self.view, **kwargs)
        only_unchanged = kwargs.get("only_unchanged", True)

        packages = view.settings().get("override_audit_expired_pkgs", [])

        # Freshen every override in every package?
        if not only_unchanged:
            pkg_list = packages
            overrides = [None] * len(pkg_list)
        else:
            pkg_list = []
            overrides = []
            for pkg in packages:
                pkg_info = PackageInfo(pkg)
                expired = pkg_info.expired_override_files(simple=True)
                unchanged = expired - filter_unmodified_overrides(pkg_info, expired)

                for override in unchanged:
                    pkg_list.append(pkg_info.name)
                    overrides.append(override)

        if len(pkg_list) == 0:
            msg = "There are no unchanged expired overrides to freshen"
            if not only_unchanged:
                msg = "No files need to be freshened"
            return log(msg, status=True, dialog=True)

        freshen_override(view, pkg_list, overrides)

    def description(self, **kwargs):
        only_unchanged = kwargs.get("only_unchanged", True)
        text = "Freshen All Expired %sOverrides" % (
                    "(Unchanged) " if only_unchanged else ""
                )
        return self.caption(text, **kwargs)

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
