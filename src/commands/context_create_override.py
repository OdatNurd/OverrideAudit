import sublime
import sublime_plugin
from os.path import isfile

from ..core import oa_setting, setup_new_override_view
from ..core import PackageListCollectionThread, ContextHelper


###----------------------------------------------------------------------------


class OverrideAuditContextCreateOverrideCommand(ContextHelper,sublime_plugin.TextCommand):
    """
    When invoked on a read-only view that represents a package resource that
    does not yet exist on disk (e.g. as opened by 'View Package Resource' in
    the command palette), promote that view to be a potential new override.
    """
    def run(self, edit, **kwargs):
        target = self.view_target(self.view, **kwargs)
        if self.package is not None:
            target.window().run_command("override_audit_create_override", {
                "package": self.package
                })
        else:
            setup_new_override_view(target, reposition=False)

    def description(self, **kwargs):
        if self.package is not None:
            return "OverrideAudit: Create Override in '%s'" % self.package

        return "OverrideAudit: Override this resource"

    def _ctx_package(self, **kwargs):
        """
        Check the context of the command to see if it's being triggered on the
        name of a package (only) which can contain overrides. If so, store the
        name in the tracking variable and return it. Otherwise, reset the
        tracking variable and return None.
        """
        target = self.view_target(self.view, **kwargs)
        ctx = self.view_context(target, False, **kwargs)

        self.package = ctx.package if self.package_overrides_possible(target, ctx) else None
        return self.package


    def is_visible(self, **kwargs):
        if self.always_visible(**kwargs):
            return True

        return self.package is not None or self.is_enabled(**kwargs)

    def is_enabled(self, **kwargs):
        # Always enabled if we're invoked via a context action on a package
        # that can contain overrides.
        if self._ctx_package(**kwargs) is not None:
            return True

        # The current buffers needs to be eligibile to promote to an override.
        spp = sublime.packages_path()
        view = self.view_target(self.view, **kwargs)
        name = view.file_name()

        # Unnamed or editable buffers can't represent new overrides, and neither
        # can files not in the packages folder or files that already exist.
        if (name is None or not view.is_read_only() or
            not name.startswith(spp) or isfile(name)):
            return False

        # We can only enable the command if this file represents a resource
        # that actually exists in the package.
        res = name[len(spp) + 1:].replace("\\", "/")
        if "Packages/" + res not in sublime.find_resources(res.split('/')[-1]):
            return False

        return True


###----------------------------------------------------------------------------
