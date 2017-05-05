import sublime
import sublime_plugin
from os.path import isfile

from ..core import oa_setting, diff_override
from ..core import PackageListCollectionThread, ContextHelper


###----------------------------------------------------------------------------


class OverrideAuditDiffOverrideCommand(ContextHelper,sublime_plugin.TextCommand):
    """
    Open a diff of a given override. If the current view represents the
    override, it will be saved before the diff happens.
    """
    def run(self, edit, **kwargs):
        target = self.view_target(self.view, **kwargs)
        pkg_name, override, is_diff = self.view_context(target, False, **kwargs)

        # Defer save of the buffer until the command finishes executing
        sView = None
        if oa_setting("save_on_diff") and is_diff is not None and not is_diff:
            sView = target

        callback = lambda thread: self._loaded(thread, target.window(), sView,
                                               pkg_name, override)
        PackageListCollectionThread(target.window(), "Collecting Package List",
                                    callback, name_list=pkg_name).start()

    def _loaded(self, thread, window, save_view, pkg_name, override):
        if save_view is not None:
            if save_view.is_dirty() and isfile(save_view.file_name()):
                save_view.run_command("save")

        pkg_list = thread.pkg_list
        diff_override(window, pkg_list[pkg_name], override,
                      diff_only=True, force_reuse=True)

    def description(self, **kwargs):
        target = self.view_target(self.view, **kwargs)
        pkg_name, override, _ = self.view_context(target, False, **kwargs)

        return "OverrideAudit: Diff Override '%s'" % override

    def is_visible(self, **kwargs):
        target = self.view_target(self.view, **kwargs)
        pkg_name, override, is_diff = self.view_context(target, False, **kwargs)

        if pkg_name is not None and override is not None:
            return not is_diff

        return False


###----------------------------------------------------------------------------
