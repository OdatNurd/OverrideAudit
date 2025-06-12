from datetime import datetime
import re


###----------------------------------------------------------------------------


def on_config(config, **kwargs):
    """
    This is a configuration hook that is triggered directly by mkdocs when it
    sets up the configuration.

    We want the copyright message in the footer to always be generated with the
    current year, but the macros package we use can't touch that part because
    it is only triggered to expand page content, not layout content.

    So here we find the template string (if any) that was used in the config
    and expand it ourselves.
    """
    config.copyright = re.sub(r'{{\s*current_year\s*}}',
                              str(datetime.now().year),
                              config.copyright)


###----------------------------------------------------------------------------
