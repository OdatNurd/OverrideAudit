import sublime_plugin

from ..core import oa_can_diff_externally, diff_externally
from ..core import PackageListCollectionThread, ContextHelper


###----------------------------------------------------------------------------


class OverrideAuditDiffExternallyCommand(ContextHelper,sublime_plugin.TextCommand):
    """
    In an existing Override diff, this will use the configured external tool to
    show the diff by extracting a temporary file to represent the packed file.
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
        diff_externally(window, pkg_list[package], override)

    def description(self, **kwargs):
        return self.caption("Open Diff Externally", **kwargs)

    def is_visible(self, **kwargs):
        if self.always_visible(**kwargs):
            return True

        return self.is_enabled(**kwargs)

    def is_enabled(self, **kwargs):
        ctx = self.view_context(None, False, **kwargs)
        return True if (ctx.has_target() and
                        ctx.is_diff and
                        oa_can_diff_externally()) else False


###----------------------------------------------------------------------------
