import sublime
import sublime_plugin

import os
import difflib

from datetime import datetime

from .base64 import b85encode, b85decode
from .core import oa_setting, oa_syntax, log
from ..lib.output_view import output_to_view


###----------------------------------------------------------------------------


# Chunk up a long string into fixed width newline separated strings for
# inclusion in the diff output.
_chunk = lambda string, length: (">" + string[0+i:length+i] + "\n" for i in range(0, len(string), length))


###----------------------------------------------------------------------------


def _patch_meta_line(pkg_info, version):
    """
    Generate the line that replicates what command was used to generate the
    diff.
    """
    return "oadiff --pkg=%s --version=%s\n" % (pkg_info.name, version)


def _do_binary_patch(pkg_info, resource, version):
    """
    Do a (potential) patch on a binary resource file. If the user file is
    determined to have the same CRC32 value as the packed version of the file,
    then this will return back an empty list. Otherwise it appends a base85
    encoded version of the file as binary diff hunk.
    """
    packed   = pkg_info._get_packed_bin_file_info(resource, contents=False)
    unpacked = pkg_info._get_unpacked_bin_file_info(resource)

    if packed is None:
        packed = (
            None,
            "%s Packages/%s/%s" % ("Shipped" if pkg_info.shipped_path else "Installed", pkg_info.name, resource),
            datetime.fromtimestamp(0).strftime("%Y-%m-%d %H:%M:%S"),
            None
            )

    # If both files have ths same CRC, consider them identical. This
    # automatically fails when the packed file is missing because it's CRC is
    # None in that case.
    if packed[3] == unpacked[3]:
        return []

    patch = [
        _patch_meta_line(pkg_info, version),
        "--- %s\t%s\n" % (packed[1], packed[2]),
        "+++ %s\t%s\n" % (unpacked[1], unpacked[2]),
        "Binary File: %d %d\n" % (len(unpacked[0]), unpacked[3])
    ]

    patch.extend(_chunk(b85encode(unpacked[0]).decode("utf-8"), 78))
    # b85decode("".join([line [1:] for line in content.splitlines()]))

    return patch


def _do_file_patch(pkg_info, resource, version):
    """
    Do a (potential) patch of a regular file; this will determine the diff (if
    any) for the given resource. If there are differences, the return value is
    appropriate diff output to append to the patch; this will be an empty list
    if there are no differences.
    """
    packed   = pkg_info._get_packed_pkg_file_contents(resource, as_list=True)
    unpacked = pkg_info._get_unpacked_override_contents(resource)

    if packed is None:
        packed = (
            [],
            "%s Packages/%s/%s" % ("Shipped" if pkg_info.shipped_path else "Installed", pkg_info.name, resource),
            datetime.fromtimestamp(0).strftime("%Y-%m-%d %H:%M:%S")
            )

    if None not in (packed, unpacked):
        diff = list(difflib.unified_diff(packed[0], unpacked[0],
                                         packed[1], unpacked[1],
                                         packed[2], unpacked[2]))
        if diff:
            diff.insert(0, _patch_meta_line(pkg_info, version))
            return diff

    return []


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


def create_patch_file(window, pkg_info, patch_contents, pkg_only,
                      patch_path=None):
    """
    Create the appropriate patch file(s) for the content of the patch and the
    package provided; pkg_only is used as an indication if the patch is meant
    to be a full patch or only a single resource.

    This will generate a view that contains textual patch information with a
    name based on the content of the patch and based in the default patch
    location.
    """
    patch_path = patch_path or default_patch_base()
    patch_name = default_patch_name(pkg_info, patch_contents, pkg_only)

    # Only need to do this if the user has a specific setting
    binary_patterns = oa_setting("binary_file_patterns")
    if binary_patterns is not None:
        pkg_info.set_binary_pattern(binary_patterns)

    # Fix up the version numbers for default packages in our shipped metadata
    pkg_version = pkg_info.metadata.get("version", "unknown")
    if " " in pkg_version:
        pkg_version = pkg_version.split(' ')[-1]

    result = []
    for res in patch_contents:
        if pkg_info._override_is_binary(res):
            patch = _do_binary_patch(pkg_info, res, pkg_version)
        else:
            patch = _do_file_patch(pkg_info, res, pkg_version)

        result.extend(patch)

    # If the patch ends up empty, we can leave without doing anything else.
    if not result:
        return log("No changes were found; patch file would be empty",
                   status=True, dialog=True)

    content = "".join(result)

    # Output and temporarily make sure that tabs are not expanded, since
    # append will modify them but they might be important in the diff
    # later.
    view = output_to_view(window, patch_name + ".oapatch", content, False, False,
                          oa_syntax("OA-DiffPatch"),
                          {
                            "translate_tabs_to_spaces": False,
                            "default_dir": patch_path,
                          })
    view.settings().erase("translate_tabs_to_spaces")

    # Our output code assumes the view is a report, so make it editable
    view.set_read_only(False)
    view.set_scratch(False)

    # Put the cursor on the first line.
    view.sel().clear()
    view.sel().add(sublime.Region(0))


###----------------------------------------------------------------------------
