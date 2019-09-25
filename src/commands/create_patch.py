import sublime
import sublime_plugin

from ..core import packages_with_overrides, log
from ..core import PackageListCollectionThread
from ..browse import ResourceType, PackageBrowser, PackageResourceBrowser


###----------------------------------------------------------------------------


class OverrideAuditCreatePatchCommand(sublime_plugin.WindowCommand):
    """
    Selectively create a patch file for either a single override or all of the
    overrides in a package. The result of this is a file created that is a
    unified diff file of all overrides, potentially also including a sidecar
    file for binary files.
    """
    def _create_patch(self, pkg_info, override=None):
        if override is None:
            file_list = list(
                pkg_info.unknown_override_files() |
                pkg_info.override_files(simple=True)
            )
        else:
            file_list = [override]

        log("Patching in %s:\n\n%s", pkg_info.name, "\n".join(file_list), dialog=True)

    def _loaded(self, thread, package, override, pkg_only):
        pkg_list = thread.pkg_list

        if package is not None and package not in pkg_list:
            return log("Unable to create patch; no package '%s'" % package,
                       status=True, dialog=True)

        if pkg_only and package is not None:
            return self._create_patch(pkg_list[package])
        elif not pkg_only and None not in (package, override):
            return self._create_patch(pkg_list[package], override)

        candidates = packages_with_overrides(pkg_list)
        p_filter = lambda p: p.name in candidates and not p.is_disabled

        if pkg_only:
            PackageBrowser(self.window, p_filter=p_filter).browse(pkg_list,
                on_done=lambda pkg: self._create_patch(pkg_list[pkg]))
        else:
            PackageResourceBrowser(package, override, self.window,
                ResourceType.OVERRIDE, unknown=True, p_filter=p_filter,
                pkg_list=pkg_list,
                on_done=lambda pkg,res: self._create_patch(pkg, res)).browse()


    def run(self, package=None, override=None, pkg_only=False):
        callback = lambda thr: self._loaded(thr, package, override, pkg_only)
        PackageListCollectionThread(self.window, "Collecting Package List",
                                    callback, name_list=package,
                                    get_overrides=True).start()


###----------------------------------------------------------------------------
