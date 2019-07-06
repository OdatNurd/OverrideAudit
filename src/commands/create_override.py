import sublime
import sublime_plugin

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
                on_done=lambda p,r: self.pick(p, r)).browse()

        # If an unpacked version already exists, just open it normally.
        unpacked = os.path.join(sublime.packages_path(), package, file)
        if os.path.exists(unpacked):
            return self.window.open_file(unpacked)

        # Convert the filename to a resource; see if it exists in that package
        # or not.
        resource = '/'.join(["Packages", package, file])
        if resource not in sublime.find_resources(resource.split('/')[-1]):
            return log("'{0}' not found; cannot create override".format(
                       file), dialog=True)

        # Convert the filename to a package resource and open it
        resource = '/'.join(["${packages}", package, file])
        self.window.run_command("open_file", {"file": resource})

        # Mark the view as a potential new override and set it up.
        view = self.window.active_view()
        view.settings().set("_oa_is_new_override", True)
        sublime.set_timeout(lambda: self.setup_view(view), 0)

    def pick(self, pkg_info, resource):
        if pkg_info is not None:
            self.window.run_command("create_override", {
                "package": pkg_info.name,
                "file": resource
            })

    def setup_view(self, view):
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
