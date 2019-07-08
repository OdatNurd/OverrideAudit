import sublime
import sublime_plugin

import os

from ..core import diff_override, packages_with_overrides, log
from ..core import PackageListCollectionThread
from ..browse import ResourceType, PackageResourceBrowser


###----------------------------------------------------------------------------


class OverrideAuditCreateOverrideCommand(sublime_plugin.WindowCommand):
    """
    Attempt to create an override for the provided file, which should be in
    the form Packages/PackageName/ResourceName. This will open the file for
    editing if it exists or create a buffer and set up so that saving will
    create an override on save.
    """
    def run(self, package=None, file=None):
        # If a packge or file name is missing, prompt for the given item and
        # reinvoke ourselves. When given a file but no package, the file is
        # ignored and the user will be prompted to pick the file.
        if package is None or file is None:
            return PackageResourceBrowser(package, file, self.window,
                ResourceType.NONOVERRIDE, unknown=False,
                p_filter=lambda p: bool(p.package_file()),
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

        # Mark the view as a potential new override and set it up.
        view = self.window.active_view()
        view.settings().set("_oa_is_new_override", True)
        self.setup_view(view)

    def pick(self, pkg_info, resource):
        if pkg_info is not None:
            self.window.run_command("override_audit_create_override", {
                "package": pkg_info.name,
                "file": resource
            })

    def setup_view(self, view):
        if view.is_loading():
            return sublime.set_timeout(lambda: self.setup_view(view), 10)

        settings = sublime.load_settings("Preferences.sublime-settings")
        mini_diff = settings.get("mini_diff")

        # File is left as a scratch buffer until the first modification
        view.run_command("move_to", {"to": "bof"})
        view.set_read_only(False)

        # Sublime turns off mini_diff for packed files that it opens.
        if mini_diff:
            view.settings().set("mini_diff", mini_diff)
            reference_doc = view.substr(sublime.Region(0, len(view)))
            view.set_reference_document(reference_doc)


###----------------------------------------------------------------------------
