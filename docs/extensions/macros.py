# In this file, the functions are macros to be expanded out in the docs, so the
# linter can't tell that they're actually used, just not here.
#
# pyright: reportUnusedFunction=false

from typing import Optional

from datetime import datetime
from mkdocs_macros.plugin import MacrosPlugin

from markdown.extensions.toc import slugify


###----------------------------------------------------------------------------


def _rel_path_to(env: MacrosPlugin, page: str) -> str:
    """
    This function is expected to be invoked from a macro, in which the source
    URI of a page with a macro in it is known.

    Using that source path and the URI of a page elsewhere in the site, this
    will return back the appropriate relative path to get to the destination
    page from the source.
    """
    # Since all links are relative to the root, we need to go back up once for
    # each slash in the source URI.
    sep_count = env.page.file.src_uri.count('/')
    return f"{'../' * sep_count}{page}"


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
    def setting(setting: str, text: Optional[str]=None) -> str:
        """
        Takes as an argument the name of a setting and optionally link text,
        and returns back the Markdown for a link to that specific setting. The
        text of the link will be the name of the setting itself unless specific
        text is provided.

        Links in mkdocs need to always be relative so that the site can be
        mounted on a sub path and still work. As such this uses the path of
        the current page to determine how to generate the relative link.
        """
        text = text or setting
        slug = slugify(setting, '-')
        return f"[{text}]({_rel_path_to(env, 'config/settings.md')}#{slug})"


    @env.macro
    def command(command: str, text: Optional[str]=None) -> str:
        """
        Takes as an argument the name of a command and optionally link text,
        and returns back the Markdown for a link to that command. The text of
        the link will be the name of the setting itself unless specific text
        is provided.

        Links in mkdocs need to always be relative so that the site can be
        mounted on a sub path and still work. As such this uses the path of
        the current page to determine how to generate the relative link.
        """
        text = text or command
        slug = slugify(command, '-')
        return f"[{text}]({_rel_path_to(env, 'usage/commands.md')}#{slug})"


###----------------------------------------------------------------------------
