import sublime
import sublime_plugin

from .lib.packages import *

###-----------------------------------------------------------------------------

# For development only; runs tests for the current development path
class OverideAuditTestCommand(sublime_plugin.WindowCommand):
    def run (self):
        self.window.run_command ("plugin_dump")

###-----------------------------------------------------------------------------

class PluginDumpCommand(sublime_plugin.WindowCommand):
    def run(self):
        print ("================================================================")
        p_list = PackageList ()
        print ("Total Packages Installed:", len (p_list))
        print (p_list["Objective-C"])
        if "Objective-Boobs" in p_list:
            print (p_list["Objective-Boobs"])
        for name, info in p_list:
            print (name)

###-----------------------------------------------------------------------------
