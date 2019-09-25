import sublime
import sublime_plugin

from ..core import ContextHelper


###----------------------------------------------------------------------------


class OverrideAuditContextCreatePatchCommand(ContextHelper,sublime_plugin.TextCommand):
    """
    Based on context, determine if the information at the cursor or for the
    current file tab is something that can have a patch created for it. This
    includes the names of packages and overrides in reports as well as inside
    of overrides and their diffs (although a diff is pretty much a patch
    anyway).
    """
    def run(self, edit, **kwargs):
        ctx, r_type, is_pkg_diff = self._get_context(**kwargs)

        self.view.window().run_command("override_audit_create_patch",
            {
                "package": r_type if is_pkg_diff else ctx.package,
                "override": ctx.override,
                "pkg_only": not ctx.has_target()
            })

    def _get_context(self, **kwargs):
        """
        Get all of the context information we need to work; the actual context
        of the command, the report type (if any) and whether or not the
        current view is a package diff or not (diff report for a single
        package).
        """
        ctx = self.view_context(None, False, **kwargs)

        # Get the report type; we want to know if it's a single bulk diff
        r_type = self._report_type(**kwargs) or ":not_set"
        is_pkg_diff = True if not r_type.startswith(":") else False

        return ctx, r_type, is_pkg_diff, self.view_target(self.view, **kwargs)

    def description(self, **kwargs):
        stub = "OverrideAudit: Create Patch"
        ctx, r_type, is_pkg_diff, _ = self._get_context(**kwargs)

        if ctx.has_target() or ctx.package_only() or is_pkg_diff:
            return "%s for '%s'" % (stub,
                ctx.override if ctx.has_target() else ctx.package or r_type)
        else:
            return stub

    def is_visible(self, **kwargs):
        if self.always_visible(**kwargs):
            return True

        return self.is_enabled(**kwargs)

    # TODO: Use the report settings in a report to know if a file has an
    # unpacked folder, and disable if it doesn't.
    def is_enabled(self, **kwargs):
        ctx, r_type, is_pkg_diff, view = self._get_context(**kwargs)

        # Enabled if this view represents an override
        if ctx.has_target():
            return True

        # Enabled for a package if it's possible for it to contain overrides
        if ctx.package_only() or is_pkg_diff:
            pkg_name = ctx.package or r_type
            packages = view.settings().get("override_audit_report_packages", {})
            pkg_info = packages.get(pkg_name, None)
            if pkg_info is not None:
                return ((pkg_info["is_shipped"] or pkg_info["is_installed"]) and
                        pkg_info["is_unpacked"])

        return False


###----------------------------------------------------------------------------
