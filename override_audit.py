import imp
import sys

###----------------------------------------------------------------------------


def reload(prefix, modules=[""]):
    prefix = "OverrideAudit.%s." % prefix

    for module in modules:
        module = (prefix + module).rstrip(".")
        if module in sys.modules:
            imp.reload(sys.modules[module])


###----------------------------------------------------------------------------


reload("lib")
reload("src")

from .lib import *
from .src import *


# ###----------------------------------------------------------------------------


def plugin_loaded():
    core.loaded()


def plugin_unloaded():
    core.unloaded()


###----------------------------------------------------------------------------
