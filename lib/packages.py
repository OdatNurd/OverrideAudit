import sublime
import io
import os
import zipfile
import codecs
from datetime import datetime
import difflib
from collections import MutableSet, OrderedDict
import fnmatch

###----------------------------------------------------------------------------

# TODO: The PackageInfo() class should take an extra parameter that lets you
# give it the name of a package and it will try to find its paths. This is a
# little complicated by the fact that packages can be installed in sub folders
# of the InstalledPackages path.
#
# Probably a little refactoring of the code here might be nice? I'm not sure at
# the moment what the nicest way to go about that would be, but it seems like
# for some upcoming commands you might want to just create a PackageInfo() for
# a named package and see what happens rather than always grab the list.
#
# TODO: The PackageFileSet() class assumes that Linux is case sensitive for
# filenames and MacOS and Windows are not. In theory sublime or the user folder
# may conceivably be placed on a case-insensitive file system, or a Mac user
# could enable case sensitivity on their file system. For completeness this
# would need to detect if the file system at each of the three package
# locations is case sensitive or not.
#
# That has issues of it's own; creating files requiring appropriate permissions
# in each folder and what to do if some but not all such locations are case
# sensitive being just two of them. Probably the best option is to proceed as
# the code now stands and provide a configuration option to alter the default
# assumptions so users have the final say.

###----------------------------------------------------------------------------

# This assumes that Linux is always using a case sensitive file system and
# MacOS is not (by default, HFS is case-insensitive). In order to detect this
# with certainty, a file would have to be created inside of each potential
# package location to check.
_wrap = (lambda value: value) if sublime.platform() == "linux" else (lambda value: value.lower())

# Paths inside of a zip file always use a Unix path separator, which causes
# problems under Windows because the partial filenames from the sublime-package
# file do not match what is detected locally. This can be fixed by using
# normpath on the zip entry, but in that case we can't find the file in the
# zip any longer.
#
# As an expedient workaround, the code that collects local override files will
# manually swap the path separator character to a Unix style under windows.
#
# This is hacky and could/should probably be fixed in a better way.
_fixPath = (lambda value: value.replace("\\", "/")) if sublime.platform() == "windows" else (lambda value: value)


###----------------------------------------------------------------------------

class PackageFileSet(MutableSet):
    """
    This is an implementation of a set that is meant to store the names of
    the contents of package files. The values in the set are case insensitive
    if the platform itself is case insensitive.

    The insertion order of the data in the set is maintained so that as long as
    files are added in package order, they will be iterated in package order.
    """
    def __init__(self, iterable=None):
        self._content = OrderedDict()
        if iterable is not None:
            self |= iterable

    def __repr__(self):
        return '{}'.format(list(self._content.values()))

    def __contains__(self, value):
        return _wrap(value) in self._content

    def __iter__(self):
        return iter(self._content.values())

    def __len__(self):
        return len(self._content)

    def add(self, value):
        if value not in self:
            self._content[_wrap(value)] = value

    def discard(self, value):
        try:
            del self._content[_wrap(value)]
        except KeyError:
            pass

###----------------------------------------------------------------------------

class PackageInfo():
    """
    Holds meta information on an installed Sublime Text Package

    A package can exist in one or more of these three states:
       * Shipped if it is a sublime-package that ships with Sublime Text
       * Installed if it is a sublime-package installed in InstalledPackages
       * Unpacked if there is a directory inside "Packages\" with that name

    Stored paths are fully qualified names of either the sublime-package file
    or the directory where the unpacked package resides.

    If there is a sublime-package file in InstalledPackages that is the same
    name as a shipped package, Sublime will ignore the shipped package in favor
    of the installed version.
    """

    # The location of packages that ship with sublime live; this is set up at
    # the time the plugin is fully loaded.
    shipped_packages_path = None

    @classmethod
    def init(cls):
        exe_path = os.path.dirname(sublime.executable_path())
        cls.shipped_packages_path = os.path.join(exe_path, "Packages")

    @classmethod
    def _deep_scan(cls, path, filename):
        """
        Scan the entire folder under the given path for the provided file
        """
        # See PackageList.__get_package_list
        for (path, dirs, files) in os.walk(path, followlinks=True):
            if filename in files:
                return True

        return False

    @classmethod
    def check_potential_override(cls, filename):
        """
        Given a filename path, check and see if this could conceivably be a
        reference to an override; i.e. that there is a shipped package with the
        name given in the filename. Note: No check is done that the shipped
        package actually HAS such a member.

        The filename provided must be either absolute(and point to the packages
        path) or relative (in which case it is assumed to point there).

        Returns None if not a potential override or a tuple of the package name
        and the override name (relative to the package).
        """
        if os.path.basename(filename) == "":
            return None

        if os.path.isabs(filename):
            if not filename.startswith(sublime.packages_path()):
                return None
            filename = os.path.relpath(filename, sublime.packages_path())

        # Get only the first path component, which will be a package name.
        parts = filename.split(os.path.sep)
        pkg_name = parts[0]
        pkg_file = pkg_name + ".sublime-package"

        if (os.path.isfile(os.path.join(cls.shipped_packages_path, pkg_file)) or
            cls._deep_scan(sublime.installed_packages_path(), pkg_file)):

            # Always use Unix path separator even on windows; this is how the
            # sublime-package would represent the override path.
            override = "/".join(parts[1:])
            return (pkg_name, override)

        return None

    def __init__(self, name):
        settings = sublime.load_settings("Preferences.sublime-settings")
        ignored_list = settings.get("ignored_packages", [])

        self.name = name

        self.is_dependency = False
        self.is_disabled = True if name in ignored_list else False

        self.shipped_path = None
        self.shipped_mtime = None
        self.installed_path = None
        self.installed_mtime = None
        self.unpacked_path = None

        self.content = dict()
        self.overrides = dict()
        self.expired = dict()

        self.binary_patterns = None

    def __repr__(self):
        return "[name={0}, shipped={1}, installed={2}, unpacked={3}]".format(
            self.name,
            self.shipped_path,
            self.installed_path,
            self.unpacked_path)

    def __get_sublime_pkg_contents(self, pkg_filename):
        if not zipfile.is_zipfile(pkg_filename):
            raise zipfile.BadZipFile("Invalid sublime-package file '{}'".format(pkg_filename))

        with zipfile.ZipFile(pkg_filename) as zFile:
            return PackageFileSet([entry.filename for entry in zFile.infolist()])

    def __get_pkg_dir_contents(self, pkg_path):
        results = PackageFileSet()
        for (path, dirs, files) in os.walk(pkg_path, followlinks=True):
            rPath = os.path.relpath(path, pkg_path) if path != pkg_path else ""
            for name in files:
                results.add(_fixPath(os.path.join(rPath, name)))

        return results

    def __get_pkg_contents(self, filename):
        result = None
        if filename is not None:
            if filename in self.content:
                return self.content[filename]

            if os.path.isdir(filename):
                result = self.__get_pkg_dir_contents(filename)
            else:
                result = self.__get_sublime_pkg_contents(filename)

            self.content[filename] = result

        return result

    def _get_packed_pkg_file_contents(self, override_file):
        try:
            with zipfile.ZipFile(self.package_file()) as zip:
                info = zip.getinfo(override_file)
                handle = codecs.EncodedFile(zip.open(info, mode="rU"), "utf-8")
                content = io.TextIOWrapper(handle, encoding="utf-8").readlines()

                source = "Installed Packages" if self.installed_path is not None else "Shipped Packages"
                source = os.path.join(source, self.name, override_file)

                return (content, source, datetime(*info.date_time).strftime("%Y-%m-%d %H:%M:%S.%f %z"))
        except (KeyError, UnicodeDecodeError, FileNotFoundError):
            return None

    def _get_unpacked_override_contents(self, override_file):
        name = os.path.join(self.unpacked_path, override_file)
        try:
            with open(name, "r", encoding="utf-8") as handle:
                content = handle.readlines()

            mtime = datetime.fromtimestamp(os.stat(name).st_mtime)
            source = os.path.join("Packages", self.name, override_file)

            return (content, source, mtime.strftime("%Y-%m-%d %H:%M:%S.%f %z"))
        except (UnicodeDecodeError, FileNotFoundError):
            return None

    def _override_is_binary(self, override_file):
        if self.binary_patterns is None:
            settings = sublime.load_settings("OverrideAudit.sublime-settings")
            if not settings.has("binary_file_patterns"):
                settings = sublime.load_settings("Preferences.sublime-settings")

            self.binary_patterns = settings.get("binary_file_patterns", [])

        for pattern in self.binary_patterns:
            if fnmatch.fnmatch(override_file, pattern):
                return True
        return False

    def package_file(self):
        return self.installed_path or self.shipped_path

    def is_unpacked(self):
        return True if self.unpacked_path is not None else False

    def package_contents(self):
        return self.__get_pkg_contents(self.package_file())

    def shipped_contents(self):
        return self.__get_pkg_contents(self.shipped_path)

    def installed_contents(self):
        return self.__get_pkg_contents(self.installed_path)

    def unpacked_contents(self):
        return self.__get_pkg_contents(self.unpacked_path)

    def has_possible_overrides(self, simple=True):
        """
        Does simple tests to determine if this package may **possibly** have
        overrides or not. It may return false positives since it does not
        actually check if overrides exist or not.

        simple overrides are unpacked files overriding files in a packed
        package, while non-simple overrides are when an installed
        sublime-package is doing a complete override on a shipped package of
        the same name
        """
        if simple:
            return bool(self.package_file() and self.is_unpacked())
        return bool(self.installed_path and self.shipped_path)

    def override_files(self, simple=True):
        """
        Get the list of overridden files for this package and the given
        override type; the list may be empty.
        """
        if not self.has_possible_overrides(simple):
            return PackageFileSet()

        if simple in self.overrides:
            return self.overrides[simple]

        if not simple:
            base_list = self.installed_contents()
            over_list = self.shipped_contents()
        else:
            base_list = self.package_contents()
            over_list = self.unpacked_contents()

        self.overrides[simple] = over_list & base_list
        return self.overrides[simple]

    def expired_override_files(self, simple=True):
        """
        Get a list of all overriden files for this package which are older than
        the sublime-package file that is currently being used by sublime; the
        list of files may be empty.

        Note that this currently compares timestamps using the timestamp of the
        sublime-package as a whole and not with the timestamp of the files as
        contained within it.
        """
        if not self.has_possible_overrides(simple):
            return PackageFileSet()

        if simple in self.expired:
            return self.expired[simple]

        result = PackageFileSet()
        if not simple:
            if self.shipped_mtime > self.installed_mtime:
                result = PackageFileSet(self.override_files(simple))

        else:
            base_time = self.installed_mtime or self.shipped_mtime
            overrides = self.override_files(simple)

            base_path = os.path.join(sublime.packages_path(), self.name)
            for name in overrides:
                if base_time > os.path.getmtime(os.path.join(base_path, name)):
                    result.add(name)

        self.expired[simple] = result
        return self.expired[simple]

    def override_diff(self, override_file, context_lines, empty_result=None,
                      binary_result=None, indent=None):
        """
        Calculate and return a unified diff of the override file provided. In
        the diff, the first file is the packed version of the file being used
        by sublime and the second is the unpacked override file
        """
        indent = "" if indent is None else " " * indent

        if self._override_is_binary(override_file):
            return "" if binary_result is None else indent + binary_result

        packed = self._get_packed_pkg_file_contents(override_file)
        unpacked = self._get_unpacked_override_contents(override_file)

        if packed is None:
            print("NOPACK: ", override_file)

        if not packed or not unpacked:
            return None


        diff = difflib.unified_diff(packed[0], unpacked[0],
                                    packed[1], unpacked[1],
                                    packed[2], unpacked[2],
                                    context_lines)

        result = u"".join(indent + line for line in diff)
        if empty_result is not None and result == "":
            result = indent + empty_result

        return result

###----------------------------------------------------------------------------

class PackageList():
    """
    Holds a complete list of all known packages in all known locations.

    For most intents and purposes this is a dictionary object with keys that
    are package names and values that are PackageInfo instances. This includes
    standard dictionary functionality such as iteration and content testing.
    """
    def __init__(self):
        self.list = dict()
        self._disabled = 0
        self._dependencies = 0

        self._shipped = self.__get_package_list(PackageInfo.shipped_packages_path, shipped=True)
        self._installed = self.__get_package_list(sublime.installed_packages_path())
        self._unpacked = self.__get_package_list(sublime.packages_path(), packed=False)

    def package_counts(self):
        return (self._shipped, self._installed, self._unpacked,
                self._disabled, self._dependencies)

    def __len__(self):
        return len(self.list)

    def __getitem__(self, key):
        return self.list[key]

    def __contains__(self, item):
        return item in self.list

    # Iterate packages in load order
    def __iter__(self):
        if "Default" in self.list:
            yield "Default", self.list["Default"]

        for pkg in sorted(self.list):
            if pkg in ["User", "Default"]:
                continue
            yield pkg, self.list[pkg]

        if "User" in self.list:
            yield "User", self.list["User"]

    def __get_pkg(self, name):
        if name not in self.list:
            self.list[name] = PackageInfo(name)
            if self.list[name].is_disabled:
                self._disabled += 1

        return self.list[name]

    def __packed_package(self, path, name, shipped):
        package_path = os.path.join(path, name)
        package_mtime = os.path.getmtime(package_path)
        pkg = self.__get_pkg(os.path.splitext(name)[0])
        if shipped:
            pkg.shipped_path = package_path
            pkg.shipped_mtime = package_mtime
        else:
            pkg.installed_path = package_path
            pkg.installed_mtime = package_mtime

    def __unpacked_package(self, path, name, shipped):
        pkg = self.__get_pkg(name)
        pkg.unpacked_path = os.path.join(path, name)

        metadata = os.path.join(pkg.unpacked_path, "dependency-metadata.json")
        if os.path.isfile(metadata):
            pkg.is_dependency = True
            self._dependencies += 1

    def __get_package_list(self, location, packed=True, shipped=False):
        count = 0
        # Follow symlinks since we're stopping after one level anyway. Maybe an
        # issue if someone goes crazy in the installed packages directory?
        for (path, dirs, files) in os.walk(location, followlinks=True):
            if packed:
                for name in [f for f in files if f.endswith(".sublime-package")]:
                    self.__packed_package(path, name, shipped)
                    count += 1
            else:
                for name in dirs:
                    self.__unpacked_package(path, name, shipped)
                    count += 1

            if shipped or not packed:
                break

        return count

###----------------------------------------------------------------------------
