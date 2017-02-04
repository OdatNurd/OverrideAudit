import sublime
import sublime_plugin

from .lib.packages import *

###-----------------------------------------------------------------------------

# For development only; runs tests for the current development path
class OverideAuditTestCommand(sublime_plugin.WindowCommand):
    """
    For binding a key to the command currently being tested
    """
    def run (self):
        # self.window.run_command ("override_audit_package_list_test")
        # self.window.run_command ("override_audit_list_packages")
        # self.window.run_command ("override_audit_list_package_overrides")
        self.window.run_command ("override_audit_diff_override")

###-----------------------------------------------------------------------------

class OverrideAuditPackageListTestCommand(sublime_plugin.WindowCommand):
    """
    For testing the PackageList class.
    """
    def run(self):
        print ("================================================================")
        p_list = PackageList ()
        print ("Total Packages Installed:", len (p_list))
        print (p_list["Objective-C"])
        if "Objective-D" in p_list:
            print (p_list["Objective-D"])
        for name, info in p_list:
            print (name)

###-----------------------------------------------------------------------------