import sublime
import sublime_plugin

from .lib.packages import *
from .lib.output_view import output_to_view

###-----------------------------------------------------------------------------

class OverrideAuditListPackagesCommand(sublime_plugin.WindowCommand):
    def run(self):
        pkg_list = PackageList()
        pkg_counts = pkg_list.package_counts()

        settings = sublime.load_settings("OverrideAudit.sublime-settings")

        title = "Packages: {} ({} dependencies)".format(len(pkg_list), pkg_counts[4])
        t_sep = "=" * len(title)

        stats = ("Shipped:   {:<6} (Shipped with Sublime)\n"
                 "Installed: {:<6} (Installed as sublime-package files)\n"
                 "Unpacked:  {:<6} (Unpacked in Packages\\ directory)\n"
                 "Disabled:  {:<6} (Currently in ignored_packages)\n").format(*pkg_counts)

        row = "| {:<40} | {:3} | {:3} | {:<3} |".format("", "", "", "")
        r_sep = "-" * len(row)

        result = [title, t_sep, "", stats, r_sep]
        for pkg_name, pkg_info in pkg_list:
            if pkg_info.is_disabled:
                pkg_name = "[{}]".format (pkg_name)
            elif pkg_info.is_dependency:
                pkg_name = "<{}>".format (pkg_name)
            result.append (
                "| {:<40} | [{:1}] | [{:1}] | [{:1}] |".format(
                pkg_name,
                "S" if pkg_info.shipped_path is not None else " ",
                "I" if pkg_info.installed_path is not None else " ",
                "U" if pkg_info.unpacked_path is not None else " "))
        result.extend([r_sep, ""])

        output_to_view(self.window,
                       "OverrideAudit: Package List",
                       result,
                       reuse=settings.get("reuse_views", True),
                       clear=settings.get("clear_existing", True),
                       syntax="Packages/OverrideAudit/syntax/OverrideAudit-table.sublime-syntax")

###-----------------------------------------------------------------------------

# This is still crude as hell; proof of proof of concept type styff
class OverrideAuditListPackageOverridesCommand(sublime_plugin.WindowCommand):
    def run(self):
        pkg_list = PackageList()
        pkg_counts = pkg_list.package_counts()

        settings = sublime.load_settings("OverrideAudit.sublime-settings")

        result = []
        for pkg_name, pkg_info in pkg_list:

            # Get overrides; leave if none. This is fairly low cost except for a
            # bunch of empty list creations since the override code does not try
            # to collect the package contents if there can't be any possible
            # overide of the type given.
            normal_overrides = pkg_info.override_files(simple=True)
            shipped_overrides = pkg_info.override_files(simple=False)
            if not normal_overrides and not shipped_overrides:
               continue

            # Decorate name; seems like a dependency will never be overridden
            # so probably not needed. Also, possibly add option to ignore
            # disabled packages? Also, there should be an option for packages
            # to exclude from the list too.
            if pkg_info.is_disabled:
                pkg_name = "[{}]".format (pkg_name)
            elif pkg_info.is_dependency:
                pkg_name = "<{}>".format (pkg_name)

            # Truncated package name and info for debug purposes
            result.append (
                "[{}{}{}] {}".format(
                "S" if pkg_info.shipped_path is not None else " ",
                "I" if pkg_info.installed_path is not None else " ",
                "U" if pkg_info.unpacked_path is not None else " ",
                pkg_name))

            if shipped_overrides:
                result.append("  `- Overrides for Installed<->Shipped")
                result.extend(["    `- {}".format(item) for item in shipped_overrides])

            if normal_overrides:
                result.append("  `- Unpacked Overrides")
                result.extend(["    `- {}".format(item) for item in normal_overrides])

        output_to_view(self.window,
                       "OverrideAudit: Package Override List",
                       result,
                       settings={"auto_indent": False},
                       reuse=settings.get("reuse_views", True),
                       clear=settings.get("clear_existing", True))
