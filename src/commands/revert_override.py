import sublime
import sublime_plugin
from os.path import isfile

from ..core import oa_setting, revert_override
from ..core import PackageListCollectionThread, ContextHelper


###----------------------------------------------------------------------------


class OverrideAuditRevertOverrideCommand(ContextHelper,sublime_plugin.TextCommand):
    """
    Revert the changes to a given override.
    """
    def run(self, edit, **kwargs):
        target = self.view_target(self.view, **kwargs)
        ctx = self.view_context(target, False, **kwargs)

        callback = lambda thread: self._loaded(thread, target.window(),
                                               ctx.package, ctx.override)
        PackageListCollectionThread(target.window(), "Collecting Package List",
                                    callback, name_list=ctx.package).start()

    def _loaded(self, thread, window, package, override):
        pkg_list = thread.pkg_list
        revert_override(window, pkg_list[package], override)

    def description(self, **kwargs):
        ctx = self.view_context(None, False, **kwargs)
        if ctx.source == "settings":
            return self.caption("Revert this Override", **kwargs)

        stub = "Revert Override"
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
            return True
            # return not ctx.is_diff if ctx.has_diff() else True

        return False

    def is_enabled(self, **kwargs):
        view = self.view_target(self.view, **kwargs)
        ctx = self.view_context(view, False, **kwargs)
        if not self.override_unknown(view, ctx) and self.override_exists(ctx):
            return True
            # return not ctx.is_diff if ctx.has_diff() else True

        return False


###----------------------------------------------------------------------------
