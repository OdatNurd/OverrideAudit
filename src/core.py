import sublime
import sublime_plugin

from collections import OrderedDict
from operator import itemgetter
from datetime import datetime
from time import time
from bisect import bisect
from zipfile import ZipFile
from tempfile import mkstemp
import stat
import os
import threading
import subprocess
import sys
import re


from ..lib.packages import PackageInfo, PackageList, PackageFileSet
from ..lib.packages import override_display, check_potential_override
from ..lib.packages import find_zip_entry
from ..lib.output_view import output_to_view
from ..lib.threads import BackgroundWorkerThread
from ..lib.utils import SettingsGroup


###----------------------------------------------------------------------------


# A group of view settings that indicate that a view is either an override or a
# diff of one. The settings indicate what package and override the contents of
# the buffer represents.
override_group = SettingsGroup("override_audit_package",
                               "override_audit_override",
                               "override_audit_diff")


###----------------------------------------------------------------------------


def loaded():
    """
    Initialize plugin state.
    """
    log("Initializing")
    oa_setting.obj = sublime.load_settings("OverrideAudit.sublime-settings")
    oa_setting.default = {
        "reuse_views": True,
        "clear_existing": True,
        "ignore_overrides_in": [],
        "diff_unchanged": "diff",
        "diff_context_lines": 3,
        "diff_empty_hdr": False,
        "save_on_diff": False,
        "confirm_deletion": True,
        "confirm_freshen": True,
        "confirm_revert": True,
        "report_on_unignore": True,
        "external_diff": False,
        "ignore_unknown_overrides": [
            "^\\.git/",
            "^\\.svn/",
            "^\\.hg/"
        ],

        # Inherits from user preferences
        "binary_file_patterns": None
    }

    PackageInfo.init()
    AutoReportTrigger()


def unloaded():
    """
    Clean up state before unloading.
    """
    log("Shutting down")
    AutoReportTrigger.unregister()


def log(message, *args, status=False, dialog=False):
    """
    Simple logging method; writes to the console and optionally also the status
    message as well.
    """
    message = message % args
    print("OverrideAudit:", message)
    if status:
        sublime.status_message(message)
    if dialog:
        sublime.message_dialog(message)


def oa_syntax(file):
    """
    Return the full name of an Override Audit syntax based on the short name.
    """
    return "Packages/OverrideAudit/resources/syntax/%s.sublime-syntax" % file


def oa_setting(key):
    """
    Get an OverrideAudit setting from a cached settings object.
    """
    default = oa_setting.default.get(key, None)
    return oa_setting.obj.get(key, default)


def oa_can_diff_externally():
    """
    Determine if the external diff functionality should be enabled. This is
    based on an introspection of the external_diff setting.
    """
    spec = oa_setting("external_diff")
    if not spec:
        return False

    if isinstance(spec, bool):
        return False

    if isinstance(spec, dict):
        return True

    if isinstance(spec, str):
        if spec == "sublimerge":
            # Both Sublimerge Pro and Sublimerge 3 include a top level resource
            # by this name that contains their version.
            for res in sublime.find_resources("version"):
                if res.split("/")[1] in ("Sublimerge 3", "Sublimerge Pro"):
                    return True

        return False

    return False


def get_ignore_unknown_patterns():
    """
    Fetch the value of the setting that tells us what unknown overrides we
    should ignore in reports. The regular expressions from the settings file
    (if any) are compiled in the returned list.

    When the setting is a boolean, the result is either an empty list or a list
    with a regular expression that will match everything, depending on the
    state of the boolean.
    """
    pattern_list = oa_setting("ignore_unknown_overrides")

    # Only be case sensitive on Linux where the file system is case sensitive
    re_opts = 0 if sublime.platform() == "linux" else re.IGNORECASE
    patterns = []

    if isinstance(pattern_list, bool):
        return [re.compile(r'.')] if pattern_list else []

    # Invalid regex patterns are ignored with a warning
    for regex in pattern_list:
        try:
            patterns.append(re.compile(regex, re_opts))
        except Exception as e:
            log("Invalid ignore_unknown_overrides regex '%s': %s",
                regex, str(e), status=True)

    return patterns


def filter_unknown_package_content(pkg_files, unknown_overrides, patterns):
    """
    Given a list of the entire unpacked contents of a package and a list of
    overrides that are known to be unknown, return back a filtered copy of the
    package contents in which the unknown overrides that match the patterns
    provided are removed from the file list.
    """
    if pkg_files is None or unknown_overrides is None:
        return pkg_files

    # use re.match to do an implicit anchor at the start of the file name
    filtered = {r for r in unknown_overrides
                 if any(p.match(r) for p in patterns)}

    return pkg_files - filtered


def packages_with_overrides(pkg_list, name_list=None):
    """
    Collect a list of package names from the given package list for which there
    is at least a single (simple) override file and which is not in the list of
    packages to ignore overrides in.

    Optionally, if name_list is provided, the list of package names will be
    filtered to only include packages whose name also exists in the name list.
    """
    ignored = oa_setting("ignore_overrides_in")
    items = [name for name, pkg in pkg_list if len(pkg.override_files()) > 0
                                               and name not in ignored]

    if name_list is not None:
        items = list(filter(lambda name: name in name_list, items))

    return items


def decorate_pkg_name(pkg_info, name_only=False):
    """
    Decorate the name of the provided package with a prefix that describes its
    status and optionally also a suffix if it is a complete override or is
    expired.
    """
    suffix = ""
    pkg_name = pkg_info.name

    if pkg_info.is_disabled:
        pkg_name = "[%s]" % pkg_name
    elif pkg_info.is_dependency:
        pkg_name = "<%s>" % pkg_name

    if name_only:
        return pkg_name

    if pkg_info.has_possible_overrides(simple=False):
        suffix += " <Complete Override>"

    if bool(pkg_info.expired_override_files(simple=False)):
        suffix += " [EXPIRED]"

    return "[{}{}{}] {}{}".format(
               "S" if pkg_info.shipped_path is not None else " ",
               "I" if pkg_info.installed_path is not None else " ",
               "U" if pkg_info.unpacked_path is not None else " ",
               pkg_name,
               suffix)


def open_override(window, pkg_name, override):
    """
    Open the provided override from the given package name.
    """
    filename = os.path.join(sublime.packages_path(), pkg_name, override)
    window.open_file(filename)


def delete_override(window, pkg_name, override):
    """
    Delete the provided override from the given package name.
    """
    # Import send2trash on demand; see Default/side_bar.py.
    import Default.send2trash as send2trash

    confirm = oa_setting("confirm_deletion")

    relative_name = os.path.join(pkg_name, override)
    full_name = os.path.join(sublime.packages_path(), relative_name)
    if os.path.isfile(full_name):
        if confirm:
            msg = "Confirm deletion:\n\n{}".format(
                override_display(relative_name))

        if (confirm is False or
                sublime.yes_no_cancel_dialog(msg) == sublime.DIALOG_YES):
            send2trash.send2trash(full_name)
            log("Deleted %s", relative_name, status=True)


def freshen_override(view, package, override=None):
    """
    Touch either the explicitly specified override in the provided package or
    all expired overrides in the package.
    """
    if oa_setting("confirm_freshen"):
        target = "Expired overrides in '%s'" % package
        if override is not None:
            relative_name = os.path.join(package, override)
            target = override_display(relative_name)

        msg = "Confirm freshen:\n\n{}".format(target)
        if sublime.yes_no_cancel_dialog(msg) != sublime.DIALOG_YES:
            return

    callback = lambda thread: log(thread.result, status=True)
    OverrideFreshenThread(view.window(), "Freshening Files", callback,
                       package=package, override=override, view=view).start()


def diff_override(window, pkg_info, override,
                  diff_only=False, force_reuse=False):
    """
    Generate a diff for the given package and override in a background thread,
    """
    context_lines = oa_setting("diff_context_lines")
    action = "diff" if diff_only else oa_setting("diff_unchanged")
    empty_diff_hdr = oa_setting("diff_empty_hdr")

    if force_reuse:
        reuse, clear = True, True
    else:
        reuse = oa_setting("reuse_views")
        clear = oa_setting("clear_existing")

    def _process_diff(thread):
        diff = thread.diff
        if diff is None:
            return log("Unable to diff %s/%s\n\n"
                        "Error loading file contents of one or both files.\n"
                        "Check the console for more information",
                        pkg_info.name, override, dialog=True)

        if diff.is_empty:
            log("No changes detected in %s/%s", pkg_info.name, override,
                 status=True)

            if action == "open":
                return open_override(window, pkg_info.name, override)

            elif action == "ignore":
                return

        title = "Diff of %s" % override_display(
            os.path.join(pkg_info.name, override))

        result = diff.result
        prefix = diff.hdr if diff.is_empty and empty_diff_hdr else ""
        content = prefix + "No differences found" if result == "" else result

        view = output_to_view(window, title, content, reuse, clear,
                              "Packages/Diff/Diff.tmLanguage")

        override_group.apply(view, pkg_info.name, override, True)

    callback = lambda thread: _process_diff(thread)
    OverrideDiffThread(window, "Diffing Override", callback,
                       pkg_info=pkg_info, override=override).start()


def diff_externally(window, pkg_info, override):
    """
    Launch the configured external diff tool to diff the override from the
    given package info. The task is launched in a background thread.
    """
    base_file = None
    override_file = None

    if pkg_info.exists():
        base_file = extract_packed_override(pkg_info, override)
        override_file = os.path.join(pkg_info.unpacked_path, override)
        diff_args = oa_setting("external_diff")

    if None in (base_file, override_file):
        return log("Unable to externally diff %s/%s\n\n"
                    "Error loading file contents of one or both files.\n"
                    "Check the console for more information",
                    pkg_info.name, override, dialog=True)

    if diff_args == "sublimerge":
        diff_with_sublimerge(base_file, override_file)
    else:
        callback = lambda thread: log(thread.result, status=True)
        DiffExternallyThread(window, "Launching external diff", callback,
                             diff_args=diff_args,
                             base=base_file, override=override_file).start()


def diff_with_sublimerge(base_file, override_file):
    """
    Use Sublimerge 3 or Sublimerge Pro to diff the override against its base
    file. This assumes that one of those packages is installed and enabled
    (the command is not visible otherwise).
    """
    sublime.run_command("new_window")
    window = sublime.active_window()

    window.open_file(base_file).settings().set("_oa_ext_diff_base", base_file)
    window.open_file(override_file)

    window.run_command("sublimerge_diff_views", {
        "left_read_only": True,
        "right_read_only": False,
        })


def revert_override(window, pkg_info, override):
    if oa_setting("confirm_revert"):
        target = override_display(os.path.join(pkg_info.name, override))
        msg = "Confirm revert:\n\n{}".format(target)

        if sublime.yes_no_cancel_dialog(msg) != sublime.DIALOG_YES:
            return

    callback = lambda thread: log(thread.result, status=True)
    OverrideRevertThread(window, "Reverting File", callback,
                       pkg_info=pkg_info, override=override).start()


def find_override(view, pkg_name, override):
    """
    Given a report view, return the bounds of the override belonging to the
    given package. Returns None if the position cannot be located.
    """
    if not view.match_selector(0, "text.override-audit"):
        return None

    bounds = None
    packages = view.find_by_selector("entity.name.package")
    for index, pkg_pos in enumerate(packages):
        if view.substr(pkg_pos) == pkg_name:
            end_pos = view.size()
            if index + 1 < len(packages):
                end_pos = packages[index + 1].begin() - 1

            bounds = sublime.Region(pkg_pos.end() + 1, end_pos)
            break

    if bounds is None:
        return

    overrides = view.find_by_selector("entity.name.filename.override")
    for file_pos in overrides:
        if bounds.contains(file_pos) and view.substr(file_pos) == override:
            return file_pos

    return None


def extract_packed_override(pkg_info, override):
    """
    Given a package information structure for a package and an override inside
    of that packages, this determines the package file that the base file is
    contained in and extracts it to a temporary file, whose name is returned.
    """
    override_type, contents = pkg_info.packed_override_contents(override, as_list=False)
    if override_type is None:
        return log("Unable to extract %s/%s; unable to locate base file",
                    pkg_info.name, override)

    name,ext = os.path.splitext(override)
    prefix = "{pre}_{pkg}_{name}_".format(
        pre=override_type,
        pkg=pkg_info.name,
        name=name.replace("/", "_")
        )

    try:
        fd, base_name = mkstemp(prefix=prefix, suffix=ext)
        os.chmod(base_name, stat.S_IREAD)
        os.write(fd, contents.encode("utf-8"))

        os.close(fd)

        return base_name

    except Exception as err:
        return log("Error creating temporary file for %s/%s: %s",
                   pkg_info.name, override, str(err))


def delete_packed_override(filename):
    """
    Attempt to delete the given named file, which should be a file returned
    from extract_packed_override().
    """
    try:
        if os.path.exists(filename):
            os.chmod(filename, stat.S_IREAD | stat.S_IWRITE)
            os.remove(filename)
        log("Deleted temporary file '%s'", filename)
    except:
        log("Error deleting '%s'", filename)


###----------------------------------------------------------------------------


class AutoReportTrigger():
    """
    A simple singleton class for running an automated expired updates report
    whenever a package is removed from the ignored packages list or at startup
    when the build number of Sublime has changed.
    """
    instance = None

    def __init__(self):
        if AutoReportTrigger.instance is not None:
            return

        AutoReportTrigger.instance = self

        self.settings = sublime.load_settings("Preferences.sublime-settings")
        ignored = self.settings.get("ignored_packages", [])

        self.cached_ignored = PackageFileSet(ignored)
        self.removed = PackageFileSet()

        self.settings.add_on_change("_oa_sw", lambda: self.__settings_change())

        self.__load_status()

    @classmethod
    def unregister(cls):
        if AutoReportTrigger.instance is not None:
            AutoReportTrigger.instance.settings.clear_on_change("_oa_sw")
            AutoReportTrigger.instance = None

    def __load_status(self):
        self.last_build = "0"
        self.force_report = False
        self.status_file = os.path.join(sublime.packages_path(), "User",
                                        "OverrideAudit.status")

        if os.path.isfile(self.status_file):
            with open(self.status_file) as file:
                line = file.readline().split(",")
                try:
                    self.last_build = line[0]
                    self.force_report = line[1] == "True"
                except IndexError:
                    pass

        if self.last_build == sublime.version() and self.force_report == False:
            log("Sublime version is unchanged; skipping automatic report")
            return

        if self.last_build != sublime.version():
            if self.last_build == "0":
                reason = "Initial plugin installation"
            else:
                reason = "Sublime version has changed"
        elif self.force_report:
            reason = "Sublime restarted during a package upgrade"

        log(reason + "; generating automatic report")
        sublime.set_timeout(lambda: self.__execute_auto_report(), 1000)

    def __save_status(self, force):
        with open(self.status_file, "w") as file:
            file.write("%s,%s" % (sublime.version(), force))

    def __execute_auto_report(self):
        self.__save_status(False)
        self.removed = PackageFileSet()

        window = sublime.active_window()
        window.run_command("override_audit_override_report",
            {"only_expired": True, "ignore_empty": True})

    def __check_removed(self, removed_set):
        if removed_set != self.removed:
            return

        self.__execute_auto_report()

    def __settings_change(self):
        new_list = PackageFileSet(self.settings.get("ignored_packages", []))
        if new_list == self.cached_ignored:
            return

        removed = self.cached_ignored - new_list
        added = new_list - self.cached_ignored
        self.cached_ignored = new_list

        if not oa_setting("report_on_unignore"):
            return

        self.removed |= removed
        self.removed -= added

        if len(self.removed) != 0:
            self.__save_status(True)

            # Send a copy of the list so we can detect if the list changes
            # in the interim.
            current = PackageFileSet(self.removed)
            sublime.set_timeout(lambda: self.__check_removed(current), 1000)
        else:
            self.__save_status(False)


###----------------------------------------------------------------------------


class PackageListCollectionThread(BackgroundWorkerThread):
    """
    Collect the list of packages in a background thread. The collection can
    optionally filter the list returned to only a set of names given and can
    also optionally pre-fetch the list of overrides in found packages.
    """
    def _process(self):
        self.pkg_list = PackageList(self.args.get("name_list", None))
        if self.args.get("get_overrides", False) is True:
            packages_with_overrides(self.pkg_list)


###----------------------------------------------------------------------------


class OverrideDiffThread(BackgroundWorkerThread):
    """
    Diff a specific package override in a background thread.
    """
    def _process(self):
        context_lines = oa_setting("diff_context_lines")

        pkg_info = self.args.get("pkg_info", None)
        override = self.args.get("override", None)

        if not pkg_info or not override:
            self.diff = None
            return log("diff thread not given a package or override to diff")

        # Only need to do this if the user has a specific setting
        binary_patterns = oa_setting("binary_file_patterns")
        if binary_patterns is not None:
            pkg_info.set_binary_pattern(binary_patterns)

        self.diff = pkg_info.override_diff(override, context_lines,
                                           binary_result="<File is binary>")


###----------------------------------------------------------------------------


# TODO Maybe this shouldn't freshen things that are not currently expired?
# Currently it will if you explicitly tell it to.
class OverrideFreshenThread(BackgroundWorkerThread):
    """
    Touch either the explicitly specified override in the provided package or
    all expired overrides in the package.
    """
    def _touch_override(self, view, zFile, pkg_name, override):
        new_mtime = None
        now = time()
        fname = os.path.join(sublime.packages_path(), pkg_name, override)

        try:
            entry = find_zip_entry(zFile, override)
            zTime = datetime(*entry.date_time).timestamp()

            if zTime > now:
                log("Warning: The packaged '%s/%s' file is from the future" ,
                     pkg_name, override)
                new_mtime = (now, zTime + 1)

            with os.fdopen(os.open(fname, os.O_RDONLY)) as f:
                os.utime(f.fileno() if os.utime in os.supports_fd else fname,
                         new_mtime)

            # TODO: This command could take a list of overrides in the package
            # and handle them all at once.
            view.run_command("override_audit_modify_mark", {
                "package": pkg_name,
                "override": override
            })

            return True
        except:
            return False

    def _msg(self, pkg_name, override, success):
        prefix = "Freshened" if success else "Unable to freshen"
        return "%s '%s/%s'" % (prefix, pkg_name, override)

    def _clean_package(self, view, pkg_name):
        pkg_list = view.settings().get("override_audit_expired_pkgs", [])
        if pkg_name in pkg_list:
            pkg_list.remove(pkg_name)
            view.settings().set("override_audit_expired_pkgs", pkg_list)

    def _single(self, view, zFile, pkg_info, override):
        result = self._touch_override(view, zFile, pkg_info.name, override)
        if result and not pkg_info.expired_override_files(simple=True):
            self._clean_package(view, pkg_info.name)
        return self._msg(pkg_info.name, override, result)

    def _pkg(self, view, zFile, pkg_info):
        count = 0
        pkg_name = pkg_info.name
        expired_list = pkg_info.expired_override_files(simple=True)

        for expired_name in expired_list:
            result = self._touch_override(view, zFile, pkg_name, expired_name)
            log(self._msg(pkg_name, expired_name, result))
            if result:
                count += 1

        if count == len(expired_list):
            prefix = "All"
            self._clean_package(view, pkg_name)
        else:
            prefix = "%d of %d" % (count, len(expired_list))

        return "%s expired overrides freshened in '%s'" % (prefix, pkg_name)

    def _process(self):
        view = self.args.get("view", None)
        package = self.args.get("package", None)
        override = self.args.get("override", None)

        if not view or not package:
            self.result = "Nothing done; missing parameters"
            return log("freshen thread not given a view or package")

        pkg_info = PackageInfo(package)
        if not pkg_info.exists():
            self.result = "Unable to freshen '%s'; no such package" % package
            return

        if not pkg_info.package_file():
            self.result = "Unable to freshen '%s'; no overrides" % package
            return

        try:
            with ZipFile(pkg_info.package_file()) as zFile:
                if override is not None:
                    self.result = self._single(view, zFile, pkg_info, override)
                else:
                    self.result = self._pkg(view, zFile, pkg_info)
        except Exception as e:
            self.result = "Error while freshening: %s" % str(e)


###----------------------------------------------------------------------------


class OverrideRevertThread(BackgroundWorkerThread):
    """
    Revert the explicitly specified override in the provided package back to
    it's initial unpacked state.
    """
    def _process(self):
        pkg_info = self.args.get("pkg_info", None)
        override = self.args.get("override", None)

        if not pkg_info or not override:
            self.result = "Nothing done; missing parameters"
            return log("revert thread not given a package or override")

        if not pkg_info.exists():
            self.result = "Unable to revert '%s'; no such package" % package
            return

        if not pkg_info.package_file():
            self.result = "Unable to revert '%s'; no overrides" % package
            return

        try:
            fname = os.path.join(sublime.packages_path(), pkg_info.name, override)
            o_type, contents = pkg_info.packed_override_contents(override, as_list=False)

            with open(fname, 'wb') as file:
                file.write(contents.encode("utf-8"))

            self.result = "Reverted '%s/%s'" % (pkg_info.name, override)

        except Exception as e:
            self.result = "Error while reverting: %s" % str(e)


###----------------------------------------------------------------------------


class ReportGenerationThread(BackgroundWorkerThread):
    """
    Helper base class for generating a report in a background thread.
    """
    def __init__(self, window, spinner_text, current_view, **kwargs):
        super().__init__(window, spinner_text,
                         lambda thread: self._display_report(thread),
                         **kwargs)
        self.current_view = current_view

    def _generation_time(self):
        return datetime.now().strftime("Report Generated: %Y-%m-%d %H:%M:%S\n")

    def _display_report(self, thread):
        # Some reports don't call _set_content if they are empty
        if not hasattr(self, "content"):
            return

        force_reuse = self.args.get("force_reuse", False)

        reuse = True if force_reuse else oa_setting("reuse_views")
        clear = True if force_reuse else oa_setting("clear_existing")

        view = output_to_view(self.window, self.caption, self.content,
                              reuse, clear, self.syntax,
                              current_view=self.current_view)
        view.settings().set("override_audit_report_type", self.report_type)

        if self.settings is not None:
            for setting,value in self.settings.items():
                view.settings().set(setting, value)

    def _set_content(self, caption, content, report_type, syntax,
                     settings=None):
        self.caption = caption
        self.content = content
        self.report_type = report_type
        self.syntax = syntax
        self.settings = settings


###----------------------------------------------------------------------------


class DiffExternallyThread(BackgroundWorkerThread):
    """
    Spawn a diff in an external process, waiting for it to complete and then
    cleaning up any temporary files.
    """
    def _launch(self, base, override, diff_args):
        shell_cmd = diff_args.get("shell_cmd")
        env = diff_args.get("env", {})
        working_dir = diff_args.get("working_dir", "")

        if not shell_cmd:
            raise ValueError("shell_cmd is required")

        if not isinstance(shell_cmd, str):
            raise ValueError("shell_cmd must be a string")

        variables = self.window.extract_variables()
        variables["base"] = base
        variables["override"] = override

        # Don't expand vars in env; we let python do that for us.
        shell_cmd = sublime.expand_variables(shell_cmd, variables)
        working_dir = sublime.expand_variables(working_dir, variables)

        if working_dir == "" and self.window.active_view():
            path = os.path.dirname(self.window.active_view().file_name() or "")
            if os.path.isdir(path):
                working_dir = path

        log("Running %s", shell_cmd)

        # Hide the console window on Windows
        startupinfo = None
        if os.name == "nt":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        process_env = os.environ.copy()
        process_env.update(env)
        for var, value in process_env.items():
            process_env[var] = os.path.expandvars(value)

        # Might not exist, but that is a user error. We checked before auto
        # changing it.
        if working_dir != "":
            os.chdir(working_dir)

        if sys.platform == "win32":
            # Use shell=True on Windows, so shell_cmd is passed through with the correct escaping
            self.proc = subprocess.Popen(
                shell_cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL,
                startupinfo=startupinfo,
                env=process_env,
                shell=True)
        elif sys.platform == "darwin":
            # Use a login shell on OSX, otherwise the users expected env vars won't be setup
            self.proc = subprocess.Popen(
                ["/usr/bin/env", "bash", "-l", "-c", shell_cmd],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL,
                startupinfo=startupinfo,
                env=process_env,
                shell=False)
        elif sys.platform == "linux":
            # Explicitly use /bin/bash on Linux, to keep Linux and OSX as
            # similar as possible. A login shell is explicitly not used for
            # linux, as it's not required
            self.proc = subprocess.Popen(
                ["/usr/bin/env", "bash", "-c", shell_cmd],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL,
                startupinfo=startupinfo,
                env=process_env,
                shell=False)

    def _prepare_args_dict(self, args):
        prepared = args.copy()
        osx = prepared.pop("osx", {})
        linux = prepared.pop("linux", {})
        windows = prepared.pop("windows", {})

        prepared.update({
            "osx": osx,
            "linux": linux,
            "windows": windows
            }[sublime.platform()]
        )

        return prepared

    def _process(self):
        base = self.args.get("base", None)
        override = self.args.get("override", None)
        diff_args = self.args.get("diff_args", None)

        if None in (base, override, diff_args):
            self.result = "Nothing done; missing parameters"
            return log("external diff thread not given files and diff args")

        try:
            diff_args = self._prepare_args_dict(diff_args)

            self._launch(base, override, diff_args)
            result_code = self.proc.wait()
            self.result = "External diff tool has exited"
        except Exception as err:
            result_code = None
            self.result = "External diff failure"
            log("Error while diffing externally: %s", str(err), dialog=True)

        if result_code:
            log("External diff finished with return code %d", result_code)

        delete_packed_override(base)


###----------------------------------------------------------------------------


class CommandContext(tuple):
    """
    This is a custom named tuple that is used by the ContextHelper class to
    describe the context that a command is being executed in.
    """
    __slots__ = ()
    package = property(itemgetter(0))
    override = property(itemgetter(1))
    is_diff = property(itemgetter(2))
    source = property(itemgetter(3))

    def __new__(_cls, package, override, is_diff, source):
        return tuple.__new__(_cls, (package, override, is_diff, source))

    def __repr__(self):
        return self.__class__.__name__ + '(package=%r, override=%r, is_diff=%r, source=%r)' % self

    def has_target(self):
        return None not in (self.package, self.override)

    def is_complete(self):
        return None not in (self.package, self.override, self.is_diff)

    def package_only(self):
        return self.package is not None and self.override is None

    def has_diff(self):
        return self.is_diff is not None


###----------------------------------------------------------------------------


class ContextHelper():
    """
    Helper class to allow context specific commands to seamlessly work in view
    context menu, tab context menus and the command palette.

    Finds the appropriate target view and package/override/diff options based
    on where it is used.
    """
    def _extract(self, scope, event):
        if event is None:
            return None

        point = self.view.window_to_text((event["x"], event["y"]))
        scope = "text.override-audit " + scope
        if not self.view.match_selector(point, scope):
            return None

        return self.view.substr(self.view.extract_scope(point))

    def _package_at_point(self, event):
        return self._extract("entity.name.package", event)

    def _override_at_point(self, event, expired=False):
        scope="entity.name.filename.override"
        if expired:
            scope += ".expired"

        return self._extract(scope, event)

    def _package_for_override_at(self, event):
        if event is not None:
            point = self.view.window_to_text((event["x"], event["y"]))
            packages = self.view.find_by_selector("entity.name.package")

            if packages:
                p_lines = [self.view.rowcol(p.begin())[0] for p in packages]
                pkg_region = packages[bisect(p_lines, self.view.rowcol(point)[0]) - 1]

                return self.view.substr(pkg_region)

        return None

    def _report_type(self, **kwargs):
        target = self.view_target(self.view, **kwargs)
        return target.settings().get("override_audit_report_type")

    def _pkg_contains_expired(self, pkg_name, **kwargs):
        target = self.view_target(self.view, **kwargs)
        expired = target.settings().get("override_audit_expired_pkgs", [])
        return pkg_name in expired

    def view_target(self, view, group=-1, index=-1, **kwargs):
        """
        Get target view specified by group and index, if needed.
        """
        window = view.window()
        return view if group == -1 else window.views_in_group(group)[index]

    def view_context(self, view, expired, event=None, **kwargs):
        """
        Return a CommandContext tuple for the provided view and possible event.
        Some members of the tuple will be None if they do not apply or cannot
        be determined by the current command state.

        If view is none, view_target is invoked to determine it. Additionally,
        expired indicates if the override found needs to be expired or not.
        """
        if view is None:
            view = self.view_target(self.view, **kwargs)

        package = None
        override = None
        is_diff = None
        source = None

        # Prioritize explicit arguments when present
        if any(key in kwargs for key in ("pkg_name", "package", "override")):
            package = kwargs.get("pkg_name", kwargs.get("package", None))
            override = kwargs.get("override", None)
            is_diff = kwargs.get("is_diff", None)
            source = "args"

        # Favor settings if they exist (only for non-expired)
        elif override_group.has(view) and expired == False:
            package, override, is_diff = override_group.get(view)
            source = "settings"

        # Check for context clicks on a package or override name as a fallback
        elif event is not None:
            source = "context"
            package = self._package_at_point(event)
            if package is None:
                override = self._override_at_point(event, expired)
                if override is not None:
                    package = self._package_for_override_at(event)

        return CommandContext(package, override, is_diff, source)

    def always_visible(self, **kwargs):
        return kwargs.get("always_visible", True)

    def override_exists(self, ctx):
        if ctx.has_target():
            relative_name = os.path.join(ctx.package, ctx.override)
            full_name = os.path.join(sublime.packages_path(), relative_name)
            return os.path.isfile(full_name)

        return False

    def override_unknown(self, view, ctx):
        if ctx.has_target():
            unknowns = view.settings().get("override_audit_unknown_overrides", {})
            if ctx.package in unknowns:
                if ctx.override in unknowns[ctx.package]:
                    return True

        return False

    def package_exists(self, ctx):
        if ctx.package_only():
            pkg_dir = os.path.join(sublime.packages_path(), ctx.package)
            return os.path.isdir(pkg_dir)

        return False

    def want_event(self):
        return True


###----------------------------------------------------------------------------
