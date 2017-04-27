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


def _pkg_scan(path, filename, recurse=False):
    """
    Scan the given path for a filename with the name provided. If found, the
    full path to the file is returned.

    recurse controls if the search will also scan subfolders of the provided
    path.
    """
    for (path, dirs, files) in os.walk(path, followlinks=True):
        for name in files:
            if _wrap(name) == _wrap(filename):
                return os.path.join(path, name)

        if not recurse:
            break

    return None


def _find_zip_entry(zFile, override_file):
    """
    Implement ZipFile.getinfo() as case insensitive for systems with a case
    insensitive file system so that looking up overrides will work the same
    as it does in the Sublime core.
    """
    try:
        return zFile.getinfo(override_file)

    except KeyError:
        if _wrap("ABC") == _wrap("abc"):
            override_file = _wrap(override_file)
            entry_list = zFile.infolist()
            for entry in entry_list:
                if _wrap(entry.filename) == override_file:
                    return entry

        raise


def override_display(override_file, pkg_name=None):
    """
    Format an override name for display, optionally prefixing it with a
    package name.

    Ensures that all overrides displayed use the forward slash style of path
    separator that Sublime uses internally.
    """
    if pkg_name is not None:
        override_file = "%s/%s" % (pkg_name, override_file)
    return _fixPath(override_file)


def check_potential_override(filename, deep=False):
    """
    Given a filename path, check and see if this could conceivably be a
    reference to an override; i.e. that there is a shipped or installed
    package with the name given in the filename.

    When deep is False, this only checks that the file could potentially be
    an override. Set deep to True to actually look inside of the package
    itself to see if this really represents an override or not.

    The filename provided must be either absolute(and point to the Packages
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

    shipped = os.path.join(PackageInfo.shipped_packages_path, pkg_file)
    installed = _pkg_scan(sublime.installed_packages_path(), pkg_file, True)

    if os.path.isfile(shipped) or installed is not None:
        # Always use Unix path separator even on windows; this is how the
        # sublime-package would represent the override path internally.
        override = "/".join(parts[1:])
        if not deep:
            return (pkg_name, override)

        try:
            with zipfile.ZipFile(installed or shipped) as zFile:
                info = _find_zip_entry(zFile, override)
                return (pkg_name, info.filename)
        except:
            pass

    return None


###----------------------------------------------------------------------------


class PackageFileSet(MutableSet):
    """
    This is an implementation of a set that is meant to store the names and
    contents of package files. The values in the set are case insensitive
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


class OverrideDiffResult():
    """
    Wraps the results of an override diff operation.

    For a binary diff, result is the message to use to indicate the diff is
    binary, or None to return an empty string. Otherwise the result is the
    result of the diff, which may be replaced with empty_msg if given and the
    diff result is None.

    The optional indent value will be used to indent all values.
    """
    def __init__(self, packed, unpacked, result, is_binary=False,
                 empty_msg=None, indent=None):
        if packed is not None and unpacked is not None:
            self.hdr =  indent + "--- %s    %s\n" % (packed[1], packed[2])
            self.hdr += indent + "+++ %s    %s\n" % (unpacked[1], unpacked[2])
        else:
            self.hdr = ""

        self.is_binary = is_binary
        if is_binary:
            self.is_empty = True
            self.result = "" if result is None else indent + result

        else:
            self.result = result
            self.is_empty = (result == "")
            if empty_msg is not None and result == "":
                self.result = indent + empty_msg


###----------------------------------------------------------------------------


class PackageInfo():
    """
    Holds meta information on an installed Sublime Text Package

    A package can exist in one or more of these three states:
       * Shipped if it is a sublime-package that ships with Sublime Text
       * Installed if it is a sublime-package installed in Installed Packages\
       * Unpacked if there is a directory inside "Packages\" with that name

    Stored paths are fully qualified names of either the sublime-package file
    or the directory where the unpacked package resides.

    If there is a sublime-package file in Installed Packages\ that is the same
    name as a shipped package, Sublime will ignore the shipped package in favor
    of the installed version. This is a complete override and methods in this
    class know to look in the package file being used by Sublime in this case
    when looking up overriden file contents.
    """

    # The location where packages that ship with sublime live; you must call
    # the init() class method at plugin load time to set this or things will
    # not work.
    shipped_packages_path = None

    @classmethod
    def init(cls):
        exe_path = os.path.dirname(sublime.executable_path())
        cls.shipped_packages_path = os.path.join(exe_path, "Packages")

    def __init__(self, name, scan=False):
        settings = sublime.load_settings("Preferences.sublime-settings")
        ignored_list = settings.get("ignored_packages", [])

        self.name = name

        self.is_dependency = False
        self.is_disabled = True if name in ignored_list else False

        self.shipped_path = None
        self.installed_path = None
        self.unpacked_path = None

        self.shipped_mtime = None
        self.installed_mtime = None

        self.pkg_content = dict()
        self.zip_list = dict()
        self.zip_dict = dict()

        self.overrides = dict()
        self.expired_overrides = dict()

        self.binary_patterns = settings.get("binary_file_patterns", [])

        if scan:
            self.__scan()

    def __repr__(self):
        name = self.name
        if self.is_dependency:
            name = "<%s>" % self.name
        elif self.is_disabled:
            name = "[%s]" % self.name

        return "([{1}{2}{3}] {0})".format(
            name,
            "S" if bool(self.shipped_path) else " ",
            "I" if bool(self.installed_path) else " ",
            "U" if bool(self.unpacked_path) else " ")

    def __verify_pkg_name(self, pathname):
        """
        Verify on case insensitive platforms that the package name follows the
        same case as the files that are used to contain it.
        """
        del self.verify_name

        pathname = os.path.basename(pathname)
        if pathname.endswith(".sublime-package"):
            pathname = os.path.splitext(pathname)[0]

        self.name = pathname

    def _add_package(self, filename, is_shipped=False):
        if filename is not None and os.path.isfile(filename):
            mtime = os.path.getmtime(filename)

            if is_shipped:
                self.shipped_path, self.shipped_mtime = filename, mtime
            else:
                self.installed_path, self.installed_mtime = filename, mtime

            if hasattr(self, "verify_name"):
                self.__verify_pkg_name(filename)

    def _add_path(self, pkg_path):
        if os.path.isdir(pkg_path):
            self.unpacked_path = pkg_path

            metadata = os.path.join(pkg_path, "dependency-metadata.json")
            if os.path.isfile(metadata):
                self.is_dependency = True

            if hasattr(self, "verify_name"):
                self.__verify_pkg_name(pkg_path)

    def __scan(self):
        if _wrap("Abc") == _wrap("abc"):
            self.verify_name = True

        pkg_filename = "%s.sublime-package" % self.name
        pkg_path = os.path.join(sublime.packages_path(), self.name)

        # Scan for the shipped package so we can collect the proper case on
        # case insensitive systems.
        self._add_package(_pkg_scan(self.shipped_packages_path, pkg_filename), True)
        self._add_package(_pkg_scan(sublime.installed_packages_path(), pkg_filename, True))
        self._add_path(pkg_path)

    def __get_sublime_pkg_zip_list(self, pkg_filename):
        if pkg_filename in self.zip_list:
            return self.zip_list[pkg_filename]

        if not zipfile.is_zipfile(pkg_filename):
            raise zipfile.BadZipFile("Invalid sublime-package file '%s'" %
                                     pkg_filename)

        with zipfile.ZipFile(pkg_filename) as zFile:
            self.zip_list[pkg_filename] = zFile.infolist()

        return self.zip_list[pkg_filename]

    def __get_sublime_pkg_zip_dict(self, pkg_filename):
        if pkg_filename in self.zip_dict:
            return self.zip_dict[pkg_filename]

        zip_list = self.__get_sublime_pkg_zip_list(pkg_filename)
        self.zip_dict[pkg_filename] = dict((e.filename, e) for e in zip_list)

        return self.zip_dict[pkg_filename]

    def __get_sublime_pkg_contents(self, pkg_filename):
        zip_list = self.__get_sublime_pkg_zip_list(pkg_filename)
        return PackageFileSet([entry.filename for entry in zip_list])

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
            if filename in self.pkg_content:
                return self.pkg_content[filename]

            if os.path.isdir(filename):
                result = self.__get_pkg_dir_contents(filename)
            else:
                result = self.__get_sublime_pkg_contents(filename)

            self.pkg_content[filename] = result

        return result

    def _get_packed_pkg_file_contents(self, override_file):
        try:
            with zipfile.ZipFile(self.package_file()) as zFile:
                info = _find_zip_entry(zFile, override_file)
                file = codecs.EncodedFile(zFile.open(info, mode="rU"), "utf-8")
                content = io.TextIOWrapper(file, encoding="utf-8").readlines()

                source = "Shipped Packages"
                if self.installed_path is not None:
                    source = "Installed Packages"

                source = os.path.join(source, self.name, override_file)
                mtime = datetime(*info.date_time).strftime("%Y-%m-%d %H:%M:%S")

                return (content, _fixPath(source), mtime)

        except (KeyError, FileNotFoundError):
            print("Error loading %s:%s; cannot find file in sublime-package" %
                  (self.package_file(), override_file))
            return None

        except UnicodeDecodeError:
            print("Error loading %s:%s; unable to decode file contents" %
                  (self.package_file(), override_file))
            return None

    def _get_unpacked_override_contents(self, override_file):
        name = os.path.join(self.unpacked_path, override_file)
        try:
            with open(name, "r", encoding="utf-8") as handle:
                content = handle.readlines()

            mtime = datetime.fromtimestamp(os.stat(name).st_mtime)
            source = os.path.join("Packages", self.name, override_file)

            return (content, _fixPath(source), mtime.strftime("%Y-%m-%d %H:%M:%S"))

        except FileNotFoundError:
            print("Error loading %s; cannot find file" % name)
            return None

        except UnicodeDecodeError:
            print("Error loading %s; unable to decode file contents" % name)
            return None

        except PermissionError:
            print("Error loading %s; permission denied" % name)

        except:
            print("Error loading %s; unknown error" % name)

    def _override_is_binary(self, override_file):
        for pattern in self.binary_patterns:
            if fnmatch.fnmatch(override_file, pattern):
                return True
        return False

    def exists(self):
        return bool(self.shipped_path or self.installed_path or self.unpacked_path)

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
        the same name.
        """
        if simple:
            return bool(self.package_file() and self.is_unpacked())
        return bool(self.installed_path and self.shipped_path)

    def override_file_zipinfo(self, override_file, simple=True):
        """
        Given the name of an override file, return the zipinfo structure from
        the containing package, where the package queried is based on the state
        of the simple flag.

        On case-insensitive file systems, this will attempt to look up the
        override in a case insensitive manner.

        The given override file must be in the zip path format.
        """
        if not self.has_possible_overrides(simple):
            return None

        source_pkg = self.package_file() if simple else self.shipped_path
        zip_dict = self.__get_sublime_pkg_zip_dict(source_pkg)

        zipinfo = zip_dict.get(override_file, None)
        if zipinfo is not None:
            return zipinfo

        if _wrap("AbC") == _wrap("abc"):
            zip_list = self.__get_sublime_pkg_zip_list(source_pkg)
            for entry in zip_list:
                if _wrap(entry.filename) == override_file:
                    return entry

        return None

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
        the source sublime-package file that is currently being used by
        sublime; the list of files may be empty.

        Note that this currently compares timestamps of the two package files
        when simple is False. When simple is True, we compare the local file
        timestamp to the record that comes out of the package file being used
        by Sublime and fall back to the timestamp of the package itself if the
        file entry can't be found.
        """
        if not self.has_possible_overrides(simple):
            return PackageFileSet()

        if simple in self.expired_overrides:
            return self.expired_overrides[simple]

        result = PackageFileSet()
        if not simple:
            if self.shipped_mtime > self.installed_mtime:
                result = PackageFileSet(self.override_files(simple))

        else:
            base_path = os.path.join(sublime.packages_path(), self.name)
            overrides = self.override_files(simple)
            pkg_time = self.installed_mtime or self.shipped_mtime

            for name in overrides:
                zipinfo = self.override_file_zipinfo(name, simple)
                base_time = (pkg_time if zipinfo is None else
                             datetime(*zipinfo.date_time).timestamp())
                file_time = os.path.getmtime(os.path.join(base_path, name))

                if file_time is not None and base_time > file_time:
                    result.add(name)

        self.expired_overrides[simple] = result
        return self.expired_overrides[simple]

    def set_binary_pattern(self, pattern_list):
        """
        Set the list of file patterns that should be considered to be binary
        during a diff. Any file that matches one of these patterns will not be
        diffed.

        The default is to use the "binary_file_patterns" setting from the
        Preferences.sublime-settings file, so you only need to change this if
        you want to alter that default.
        """
        self.binary_patterns = pattern_list

    def override_diff(self, override_file, context_lines, empty_result=None,
                      binary_result=None, indent=None):
        """
        Calculate and return a unified diff of the override file provided. In
        the diff, the first file is the packed version of the file being used
        by sublime and the second is the unpacked override file.
        """
        indent = "" if indent is None else " " * indent

        if self._override_is_binary(override_file):
            return OverrideDiffResult(None, None, binary_result,
                                      is_binary=True, indent=indent)

        packed = self._get_packed_pkg_file_contents(override_file)
        unpacked = self._get_unpacked_override_contents(override_file)

        if not packed or not unpacked:
            return None

        diff = difflib.unified_diff(packed[0], unpacked[0],
                                    packed[1], unpacked[1],
                                    packed[2], unpacked[2],
                                    context_lines)

        result = u"".join(indent + line for line in diff)
        return OverrideDiffResult(packed, unpacked, result,
                                  empty_msg=empty_result, indent=indent)


###----------------------------------------------------------------------------


class PackageList():
    """
    Holds a complete list of all known packages in all known locations.

    For most intents and purposes this is a dictionary object with keys that
    are package names and values that are PackageInfo instances. This includes
    standard dictionary functionality such as iteration and content testing.

    On case insensitive file systems, the names of packages are not case
    sensitive. In the event that different packages provide different cases of
    package name, the first name seen (i.e. either shipped or installed) will
    be the "de facto" case for that package.
    """
    def __init__(self):
        self._list = dict()
        self._disabled = 0
        self._dependencies = 0

        # Maps lower cased package names to listed packages on case insensitive
        # systems.
        self._case_list = dict() if _wrap("ABC") == _wrap("abc") else None

        self._shipped = self.__find_pkgs(PackageInfo.shipped_packages_path, shipped=True)
        self._installed = self.__find_pkgs(sublime.installed_packages_path())
        self._unpacked = self.__find_pkgs(sublime.packages_path(), packed=False)

    def package_counts(self):
        """
        Return a tuple which contains the number of packages that fit certain
        critera: (shipped, installed, unpacked, disabled, dependencies).

        Note that installed packages indicates the number of packages installed
        by the user into the Installed Packages\ folder.
        """
        return (self._shipped, self._installed, self._unpacked,
                self._disabled, self._dependencies)

    def __key(self, key):
        """
        Return the de facto key (package name) for the given key; returns the
        key untouched on case sensitive systems or when the key is not known.
       """
        if self._case_list is not None:
            case_key = key.lower()
            if case_key in self._case_list:
                return self._case_list[case_key]
        return key

    def __len__(self):
        return len(self._list)

    def __getitem__(self, key):
        return self._list[self.__key(key)]

    def __contains__(self, key):
        return self.__key(key) in self._list

    # Iterate packages in (roughly) load order
    def __iter__(self):
        if "Default" in self._list:
            yield "Default", self._list["Default"]

        for pkg in sorted(self._list):
            if pkg in ["User", "Default"]:
                continue
            yield pkg, self._list[pkg]

        if "User" in self._list:
            yield "User", self._list["User"]

    def __get_pkg(self, name):
        """
        Get or create package by name during initial package scan
        """
        name = self.__key(name)
        if name not in self._list:
            self._list[name] = PackageInfo(name)
            if self._case_list is not None:
                self._case_list[name.lower()] = name

            if self._list[name].is_disabled:
                self._disabled += 1

        return self._list[name]

    def __packed_package(self, path, name, shipped):
        pkg_file = os.path.join(path, name)
        pkg = self.__get_pkg(os.path.splitext(name)[0])
        pkg._add_package(pkg_file, shipped)

    def __unpacked_package(self, path, name, shipped):
        pkg_path = os.path.join(path, name)
        pkg = self.__get_pkg(name)
        pkg._add_path(pkg_path)

        if pkg.is_dependency:
            self._dependencies += 1

    def __find_pkgs(self, location, packed=True, shipped=False):
        count = 0
        # Follow symlinks since we're stopping after one level anyway except in
        # the Installed Packages\ folder. Maybe an issue if someone goes crazy
        # in there?
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
