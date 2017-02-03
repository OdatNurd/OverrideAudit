import sublime
import io
import os
import string
import zipfile
import codecs
from datetime import datetime
import time
import difflib
from collections import MutableSet, OrderedDict

###-----------------------------------------------------------------------------

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
# TODO: The PackageInfo.override_files() method does not memoize the list of
# overridden files, so every invocation calculates it again. I don't know how
# important that might be at this juncture, since it seems like the real cost
# savings is in not having to fetch the list of files each time.
#
# TODO: The PackageFileSet() class assumes that Linux is case sensitive for
# filenames and MacOS and Windows are not. In theory sublime or the user folder
# may conceivably be placed on a case-insensitive file system, or a Mac user
# could enable case sensitivity on their file system. For completeness this
# would need to detect if the file system at each of the three package locations
# is case sensitive or not.
#
# That has issues of it's own; creating files requiring appropriate permissions
# in each folder and what to do if some but not all such locations are case
# sensitive being just two of them. Probably the best option is to proceed as
# the code now stands and provide a configuration option to alter the default
# assumptions so users have the final say.

###-----------------------------------------------------------------------------

# This assumes that Linux is always using a case sensitive file system and MacOS
# is not (by default, HFS is case-insensitive). In order to detect this with
# certainty, a file would have to be created inside of each potential package
# location to check.
_wrap = (lambda value: value) if sublime.platform() == "linux" else (lambda value: value.lower())

class PackageFileSet(MutableSet):
    """
    This is an implementation of a set that is meant to store the names of
    the contents of package files. The values in the set are case sensitive if
    the platform itself is case sensitive.

    The insertion order of the data in the set is maintained so that as long as
    files are added in package order, they will be iterated in package order.
    """
    def __init__(self, iterable=None):
        self._content = OrderedDict()
        if iterable is not None:
            self |= iterable

    def __repr__(self):
        return '{}'.format(list(self._content.values()))

    def __contains__(self,value):
        return _wrap(value) in self._content

    def __iter__(self):
        return iter(self._content.values ())

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

###-----------------------------------------------------------------------------

class PackageInfo():
    """
    Holds meta information on an installed Sublime Text Package

    A package can exist in one or more of these three states:
       * Shipped if it is a sublime-package that ships with Sublime Text
       * Installed if it is a sublime-package installed in InstalledPackages
       * Unpacked if there is a directory inside "Packages\" with that name

    Stored paths are fully qualified names of either the sublime-package file or
    the directory where the unpacked package resides.

    If there is a sublime-package file in InstalledPackages that is the same
    name as a shipped package, Sublime will ignore the shipped package in favor
    of the installed version.
    """
    def __init__(self, name):
        settings = sublime.load_settings ("Preferences.sublime-settings")
        ignored_list = settings.get ("ignored_packages", [])

        self.name = name

        self.is_dependency = False
        self.is_disabled = True if name in ignored_list else False

        self.shipped_path = None
        self.shipped_mtime = None
        self.installed_path = None
        self.installed_mtime = None
        self.unpacked_path = None

        self.content = dict()

    def __repr__(self):
        return "[name={0}, shipped={1}, installed={2}, unpacked={3}]".format(
            self.name ,
            self.shipped_path,
            self.installed_path,
            self.unpacked_path)

    def __get_sublime_pkg_contents(self,pkg_filename):
        if not zipfile.is_zipfile(pkg_filename):
            raise zipfile.BadZipFile("Invalid sublime-package file '{}'".format(name))

        pName = os.path.basename(pkg_filename)
        with zipfile.ZipFile(pkg_filename) as zFile:
            return PackageFileSet([entry.filename for entry in zFile.infolist()])

    def __get_pkg_dir_contents(self,pkg_path):
        results=PackageFileSet()
        for (path, dirs, files) in os.walk(pkg_path, followlinks=True):
            rPath = os.path.relpath(path, pkg_path) if path != pkg_path else ""
            for name in files:
                results.add(os.path.join(rPath, name))

        return results

    def __get_pkg_contents(self,filename):
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
                content = io.TextIOWrapper(handle).readlines()

                source = "Installed Packages" if self.installed_path is not None else "Shipped Packages"
                source = os.path.join(source, self.name, override_file)

                return (content, source, datetime(*info.date_time).ctime())
        except (KeyError, UnicodeDecodeError, FileNotFoundError):
            return None

    def _get_unpacked_override_contents(self, override_file):
        name = os.path.join(self.unpacked_path, override_file)
        try:
            with open(name, "r", encoding="utf=8") as handle:
                content = handle.readlines()

            mtime = os.stat(name).st_mtime
            source = os.path.join("Packages", self.name, override_file)

            return (content, source, time.ctime(mtime))
        except (UnicodeDecodeError, FileNotFoundError):
            return None

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
        sublime-package is doing a complete override on a shipped package of the
        same name
        """
        if simple:
            return bool(self.package_file() and self.is_unpacked())
        return bool(self.installed_path and self.shipped_path)

    def override_files(self, simple=True):
        """
        Get the list of overridden files for this package and the given override
        type; the list may be empty.
        """
        if not self.has_possible_overrides(simple):
            return PackageFileSet()

        if not simple:
            base_list = self.installed_contents()
            over_list = self.shipped_contents()
        else:
            base_list = self.package_contents()
            over_list = self.unpacked_contents()

        return base_list & over_list

    def override_diff(self, override_file, context_lines):
        """
        Calculate and return a unified diff of the override file provided. In
        the diff, the first file is the packed version of the file being used
        by sublime and the second is the unpacked override file
        """
        packed = self._get_packed_pkg_file_contents(override_file)
        unpacked = self._get_unpacked_override_contents(override_file)

        if not packed or not unpacked:
            print("Unable to diff %s" % os.path.join(self.name, override_file))
            return None

        diff = difflib.unified_diff(packed[0], unpacked[0],
                                    packed[1], unpacked[1],
                                    packed[2], unpacked[2],
                                    context_lines)

        result = u"".join(line for line in diff)
        return "No differences found" if result == "" else result

###-----------------------------------------------------------------------------

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

        exec_dir = os.path.dirname(sublime.executable_path())
        self._shipped = self.__get_package_list(os.path.join(exec_dir, "Packages"), shipped=True)
        self._installed = self.__get_package_list(sublime.installed_packages_path ())
        self._unpacked = self.__get_package_list(sublime.packages_path (), packed=False)

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
        if os.path.isfile (metadata):
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

###-----------------------------------------------------------------------------
