import sublime
import sublime_plugin
import os

from .override_audit import override_group
from ..lib.packages import check_potential_override


###----------------------------------------------------------------------------


class OverrideAuditEventListener(sublime_plugin.EventListener):
    """
    Check on file load and save to see if the new file is potentially an
    override for a package, and set the variables that allow for our context
    menus to let you edit/diff the override.
    """
    def _check_for_override(self, view):
        filename = view.file_name()
        if filename is None or not os.path.isfile(filename):
            return

        result = check_potential_override(filename, deep=True)
        if result is not None:
            override_group.apply(view, result[0], result[1], False)
        else:
            override_group.remove(view)

    def on_post_save_async(self, view):
        # Will remove existing settings if the view is no longer an override
        self._check_for_override(view)

    def on_load_async(self, view):
        # Things like PackageResourceViewer trigger on_load before the file
        # actually exists; context items are only allowed once the file is
        # actually saved.
        self._check_for_override(view)


###----------------------------------------------------------------------------
