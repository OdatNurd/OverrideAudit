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
        ctx = self.view_context(target, False, **kwargs)

        # Defer save of the buffer until the command finishes executing
        sView = None
        if oa_setting("save_on_diff") and ctx.is_diff is not None and not ctx.is_diff:
            sView = target

        callback = lambda thread: self._loaded(thread, target.window(), sView,
                                               ctx.package, ctx.override)
        PackageListCollectionThread(target.window(), "Collecting Package List",
                                    callback, name_list=ctx.package).start()

    def _loaded(self, thread, window, save_view, package, override):
        if save_view is not None:
            if save_view.is_dirty() and isfile(save_view.file_name()):
                save_view.run_command("save")

        pkg_list = thread.pkg_list
        diff_override(window, pkg_list[package], override,
                      diff_only=True, force_reuse=True)

    def description(self, **kwargs):
        ctx = self.view_context(None, False, **kwargs)
        if ctx.source == "settings":
            return self.caption("Diff this Override", **kwargs)

        stub = "Diff Override"
        if ctx.has_target():
            return self.caption("%s '%s'" % (stub, ctx.override), **kwargs)
        else:
            return self.caption(stub, **kwargs)

    def is_visible(self, **kwargs):
        if self.always_visible(**kwargs):
            return True

        view = self.view_target(self.view, **kwargs)
        ctx = self.view_context(view, False, **kwargs)

        if ctx.has_target() and not self.override_unknown(view, ctx):
            return not ctx.is_diff if ctx.has_diff() else True

        return False

    def is_enabled(self, **kwargs):
        view = self.view_target(self.view, **kwargs)
        ctx = self.view_context(view, False, **kwargs)
        if not self.override_unknown(view, ctx) and self.override_exists(ctx):
            return not ctx.is_diff if ctx.has_diff() else True

        return False


###----------------------------------------------------------------------------
