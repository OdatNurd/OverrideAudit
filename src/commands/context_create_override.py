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
        setup_new_override_view(target, reposition=False)

    def description(self, **kwargs):
        return "OverrideAudit: Override this resource"

    def is_visible(self, **kwargs):
        if self.always_visible(**kwargs):
            return True

        return self.is_enabled(**kwargs)

    def is_enabled(self, **kwargs):
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
