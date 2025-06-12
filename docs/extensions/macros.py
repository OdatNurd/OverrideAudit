# In this file, the functions are macros to be expanded out in the docs, so the
# linter can't tell that they're actually used, just not here.
#
# pyright: reportUnusedFunction=false

from datetime import datetime
from mkdocs_macros.plugin import MacrosPlugin


###----------------------------------------------------------------------------


def _rel_segment(env: MacrosPlugin) -> str:
    """
    Given an env that contains information on the source path of a particular
    file that a macro is being expanded into, return back an appropriate
    string that can be used in a link to get from this page back to the root
    of the site.

    The source path of all files are relative to the document root, so this
    returns one "../" for every "/" that appears in the source path.
    """
    sep_count = env.page.file.src_uri.count('/')
    return '../' * sep_count


###----------------------------------------------------------------------------


def define_env(env: MacrosPlugin):
    """
    This function is invoked by mkdocs to populate a series of macros and other
    enhancements to mkdocs page generation.
    """

    # Custom variable that expands to the current year at the point where the
    # documentation is generated.
    #
    # NOTE: Despite what it looks like, this variable *DOES NOT* expand in the
    #       page footer; see the code in hooks.py for how that one is handled.
    env.variables['current_year'] = str(datetime.now().year)


    @env.macro
    def setting(setting: str) -> str:
        """
        Takes as an argument the name of a setting and returns back the
        Markdown for a link to that specific setting. The text of the link
        will be the name of the setting itself.

        Links in mkdocs need to always be relative so that the site can be
        mounted on a sub path and still work. As such this uses the path of
        the current page to determine how to generate the relative link.
        """
        return f"[{setting}]({_rel_segment(env)}config/settings.md#{setting})"


###----------------------------------------------------------------------------
