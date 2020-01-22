import sublime
import sublime_plugin

import os

from ..core import diff_override, packages_with_overrides, log
from ..core import setup_new_override_view, PackageListCollectionThread
from ..browse import ResourceType, PackageResourceBrowser


###----------------------------------------------------------------------------


class OverrideAuditCreateOverrideCommand(sublime_plugin.WindowCommand):
    """
    Attempt to create an override for the provided file, which should be in
    the form Packages/PackageName/ResourceName. This will open the file for
    editing if it exists or create a buffer and set up so that saving will
    create an override on save.
    """
    def run(self, package=None, file=None, include_existing=False):
        # If a packge or file name is missing, prompt for the given item and
        # reinvoke ourselves. When given a file but no package, the file is
        # ignored and the user will be prompted to pick the file.
        if package is None or file is None:
            if include_existing:
                res_type = ResourceType.ALL
                annotate = True
            else:
                res_type = ResourceType.NONOVERRIDE
                annotate = False

            return PackageResourceBrowser(package, file, self.window,
                res_type, unknown=False, annotate_overrides=annotate,
                p_filter=lambda p: bool(p.package_file()) and not p.is_disabled,
                on_done=lambda p,r: self.pick(p, r)).browse()

        # Open normally if an unpacked copy exists; fallback for manual calls
        unpacked = os.path.join(sublime.packages_path(), package, file)
        if os.path.exists(unpacked):
            return self.window.open_file(unpacked)

        # No unpacked file; verify the package contains the resource
        res = '/'.join([package, file])
        if "Packages/" + res not in sublime.find_resources(res.split('/')[-1]):
            return log("'{0}' not found; cannot create override".format(
                       file), dialog=True)

        self.window.run_command("open_file", {"file": "${packages}/" + res})

        # Get the active view and set it up as a potential new override.
        view = self.window.active_view()
        setup_new_override_view(view)

    def pick(self, pkg_info, resource):
        if pkg_info is not None:
            self.window.run_command("override_audit_create_override", {
                "package": pkg_info.name,
                "file": resource
            })


###----------------------------------------------------------------------------
