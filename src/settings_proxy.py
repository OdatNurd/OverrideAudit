import sublime
import sublime_plugin


###----------------------------------------------------------------------------


st_version = int(sublime.version())


###----------------------------------------------------------------------------


class OverrideAuditOpenFileCommand(sublime_plugin.WindowCommand):
    """
    A proxy for the default open_file command that will hide itself from the
    menu/command palette in newer versions of Sublime Text.
    """
    def run(self, **kwargs):
        self.window.run_command("open_file", kwargs)

    def is_visible(self, file, contents=None):
        return st_version < 3124


###----------------------------------------------------------------------------


class OverrideAuditEditSettingsCommand(sublime_plugin.WindowCommand):
    """
    A proxy for the default edit_settings command that will hide itself from
    the menu/command palette in older versions of Sublime Text.
    """
    def run(self, **kwargs):
        self.window.run_command("edit_settings", kwargs)

    def is_visible(self, **kwargs):
        return st_version >= 3124


###----------------------------------------------------------------------------
