import sublime
import sublime_plugin

from ..core import packages_with_overrides, log
from ..core import PackageListCollectionThread
from ..browse import ResourceType, PackageBrowser, PackageResourceBrowser
from ..patch import default_patch_base, default_patch_name, create_patch_file


###----------------------------------------------------------------------------


class OverrideAuditCreatePatchCommand(sublime_plugin.WindowCommand):
    """
    Selectively create a patch file for either a single override or all of the
    overrides in a package. A textual patch will be created into a view ready
    for saving; the patch_path provided sets where the save location will
    prompt by default, and will default to the appropriate setting value if
    not given.
    """
    def run(self, package=None, override=None, pkg_only=False, patch_path=None):
        callback = lambda thr: self._loaded(thr, package, override, pkg_only, patch_path)
        PackageListCollectionThread(self.window, "Collecting Package List",
                                    callback, name_list=package,
                                    get_overrides=True).start()

    def _loaded(self, thread, package, override, pkg_only, patch_path):
        pkg_list = thread.pkg_list

        if package is not None and package not in pkg_list:
            return log("Unable to create patch; no package '%s'" % package,
                       status=True, dialog=True)

        if pkg_only and package is not None:
            return self._make_patch(patch_path, pkg_list[package])
        elif not pkg_only and None not in (package, override):
            return self._make_patch(patch_path, pkg_list[package], override)

        candidates = packages_with_overrides(pkg_list)
        p_filter = lambda p: p.name in candidates and not p.is_disabled

        if pkg_only:
            PackageBrowser(self.window, p_filter=p_filter).browse(pkg_list,
                on_done=lambda pkg: self._make_patch(patch_path, pkg))
        else:
            PackageResourceBrowser(package, override, self.window,
                ResourceType.OVERRIDE, unknown=True, p_filter=p_filter,
                pkg_list=pkg_list,
                on_done=lambda pkg,res: self._make_patch(patch_path, pkg, res)).browse()

    def _make_patch(self, patch_path, pkg_info, override=None):
        # We get called with a pkg_info of None if the user cancels the browse.
        if pkg_info is None:
            return

        if override is None:
            file_list = list(
                pkg_info.unknown_override_files() |
                pkg_info.override_files(simple=True)
            )
        else:
            file_list = [override]

        create_patch_file(self.window, pkg_info, file_list, override is None,
                          patch_path)


###----------------------------------------------------------------------------
