import sublime
import sublime_plugin

from bisect import bisect
import os

from .pkg_popup import show_pkg_popup
from .core import log
from .core import delete_packed_override
from .core import setup_override_minidiff


###----------------------------------------------------------------------------


class OverrideAuditEventListener(sublime_plugin.EventListener):
    """
    Check on file load and save to see if the new file is potentially an
    override for a package, and set the variables that allow for our context
    menus to let you edit/diff the override.
    """
    def on_post_save_async(self, view):
        # Will remove existing settings if the view is no longer an override
        setup_override_minidiff(view)

    def on_load_async(self, view):
        # Things like PackageResourceViewer trigger on_load before the file
        # actually exists; context items are only allowed once the file is
        # actually saved.
        setup_override_minidiff(view)

    def on_close(self, view):
        tmp_base = view.settings().get("_oa_ext_diff_base", None)
        if tmp_base is not None:
            delete_packed_override(tmp_base)

    def on_hover(self, view, point, hover_zone):
        if hover_zone != sublime.HOVER_TEXT:
            return

        if not view.match_selector(point, "text.override-audit & (entity.name.package, meta.override, meta.package)"):
            return None

        hover_text = view.substr(view.extract_scope(point))
        is_detailed = False

        if view.match_selector(point, "entity.name.package"):
            is_detailed = view.settings().get("override_audit_report_type", "??")
            link = "pkg:%s" % hover_text
        else:
            packages = view.find_by_selector("entity.name.package")
            if packages:
                p_lines = [view.rowcol(p.begin())[0] for p in packages]
                pkg_region = packages[bisect(p_lines, view.rowcol(point)[0]) - 1]

                pkg = view.substr(pkg_region)

            if view.match_selector(point, "meta.package.specifier"):
                hover_text = '[SIU]'

            link = "info:%s:%s" % (hover_text, pkg)

        show_pkg_popup(view, point, link, is_detailed)


###----------------------------------------------------------------------------


class CreateOverrideEventListener(sublime_plugin.ViewEventListener):
    """
    This listener applies only to newly created override views created by the
    override_audit_create_override command. It ensures that the appropriate
    path exists prior to saving a new override, and removes the scratch mark
    from a new override once it has been modified for the first time.
    """
    @classmethod
    def is_applicable(cls, settings):
        return settings.get("_oa_is_new_override", False)

    def on_pre_save(self):
        """
        Before the first save of a new override, try to create the appropriate
        unpacked folder; doing so marked this as no longer a potential new
        override.
        """
        view_filename = self.view.file_name()
        if view_filename is None:
            return

        path = os.path.dirname(view_filename)
        try:
            os.makedirs(path, exist_ok=True)
            self.view.settings().erase("_oa_is_new_override")
        except:
            log("Error creating package directory for new override",
                dialog=True)

    def on_modified(self):
        """
        On first modification to the buffer, turn off the scratch status so the
        user knows they modified the original file.
        """
        if self.view.is_scratch():
            self.view.set_scratch(False)


###----------------------------------------------------------------------------
