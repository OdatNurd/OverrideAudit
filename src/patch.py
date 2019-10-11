import sublime
import sublime_plugin

import os
import difflib

from .core import oa_setting


###----------------------------------------------------------------------------


def default_patch_base():
    """
    Determine what the default location to store new patch files is. This is
    calculated based on the setting provided by the user, but also takes
    fallback into account when the setting is not set or the path that it
    represents is not accessible.
    """
    home = os.path.expanduser("~")
    base = oa_setting("default_patch_path")

    if not base:
        base = os.path.join(home, "Desktop")

    if os.path.isdir(base):
        return base

    return home


def default_patch_name(pkg_info, patch_contents, pkg_only):
    """
    Determine what the default filename for a patch using the given criteria
    should be. This always includes the path name, but in cases where the patch
    is for only a single resource, the resource name is used also.

    The return name contains no path or extension information; the path should
    come from default_patch_base() and the extension depends on what part of
    the patch is being created.
    """
    base = pkg_info.name
    if not pkg_only and len(patch_contents) > 0:
        res_name = os.path.basename(patch_contents[0])
        base = base + "_" + os.path.splitext(res_name)[0]

    return base


###----------------------------------------------------------------------------
