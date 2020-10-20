import sublime
import io
import os
import re
import zipfile
import codecs
from datetime import datetime
import difflib
from collections import MutableSet, OrderedDict
import glob
import fnmatch

from .metadata import default_metadata


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


def _shipped_packages_path():
    """
    Get the location for shipped packages in Sublime; this lazy-loads the path
    on first call, and requires that the plugin host be set up completely
    before being called.
    """
    if not hasattr(_shipped_packages_path, "pkg_path"):
        exe_path = os.path.dirname(sublime.executable_path())
        _shipped_packages_path.pkg_path = os.path.join(exe_path, "Packages")

    return _shipped_packages_path.pkg_path


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


def _is_compatible_version(version_range):
    """
    This code is taken from Package Control and is used to match a version
    selector like '>3200', '<3000' or '3100-3200' against the current build of
    Sublime to see if it is compatible or not.
    """
    min_version = float("-inf")
    max_version = float("inf")

    if version_range == '*':
        return True

    gt_match = re.match(r'>(\d+)$', version_range)
    ge_match = re.match(r'>=(\d+)$', version_range)
    lt_match = re.match(r'<(\d+)$', version_range)
    le_match = re.match(r'<=(\d+)$', version_range)
    range_match = re.match(r'(\d+) - (\d+)$', version_range)

    if gt_match:
        min_version = int(gt_match.group(1)) + 1
    elif ge_match:
        min_version = int(ge_match.group(1))
    elif lt_match:
        max_version = int(lt_match.group(1)) - 1
    elif le_match:
        max_version = int(le_match.group(1))
    elif range_match:
        min_version = int(range_match.group(1))
        max_version = int(range_match.group(2))
    else:
        return None

    if min_version > int(sublime.version()):
        return False
    if max_version < int(sublime.version()):
        return False

    return True


def find_zip_entry(zFile, override_file):
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


def check_potential_override(filename, deep=False, get_content=False):
    """
    Given a filename path, check and see if this could conceivably be a
    reference to an override; i.e. that there is a shipped or installed
    package with the name given in the filename.

    When deep is False, this only checks that the file could potentially be
    an override. Set deep to True to actually look inside of the package
    itself to see if this really represents an override or not.

    When get_content is True and the filename represents an override, the
    returned tuple will also contain as a third element the unpacked content
    of the override; this requires deep to be set to True.

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

    shipped = os.path.join(_shipped_packages_path(), pkg_file)
    installed = _pkg_scan(sublime.installed_packages_path(), pkg_file, True)

    if os.path.isfile(shipped) or installed is not None:
        # Always use Unix path separator even on windows; this is how the
        # sublime-package would represent the override path internally.
        override = "/".join(parts[1:])
        if not deep:
            return (pkg_name, override, None)

        try:
            with zipfile.ZipFile(installed or shipped) as zFile:
                info = find_zip_entry(zFile, override)

                content = None
                if get_content:
                    # Make a stub PackageInfo with enough members filled out to
                    # fetch the appropriate content.
                    p_info = PackageInfo(pkg_name, scan=False)
                    p_info.shipped_path = shipped
                    p_info.installed_path = installed

                    content = p_info.packed_override_contents(info.filename, as_list=False)[1]

                return (pkg_name, info.filename, content)
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
       * Installed if it is a sublime-package installed in Installed Packages/
       * Unpacked if there is a directory inside "Packages/" with that name

    Stored paths are fully qualified names of either the sublime-package file
    or the directory where the unpacked package resides.

    If there is a sublime-package file in Installed Packages/ that is the same
    name as a shipped package, Sublime will ignore the shipped package in favor
    of the installed version. This is a complete override and methods in this
    class know to look in the package file being used by Sublime in this case
    when looking up overriden file contents.
    """
    def __init__(self, name, scan=True):
        settings = sublime.load_settings("Preferences.sublime-settings")
        ignored_list = settings.get("ignored_packages", [])

        self.name = name
        self.metadata = {}
        self.python_version = ""

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
        self.unknown_overrides = None
        self.unknowns_filtered = 0

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

    def _check_if_depdendency(self):
        """
        See if this package represents a dependency or not; this requires that
        all of the package files and the unpacked package path (if any) have
        been set up first.
        """
        self.is_dependency = (
            self.contains_file("dependency-metadata.json") or
            self.contains_file(".sublime-dependency")
            )

    def _add_path(self, pkg_path):
        if os.path.isdir(pkg_path):
            self.unpacked_path = pkg_path

            if hasattr(self, "verify_name"):
                self.__verify_pkg_name(pkg_path)

    def __scan(self):
        if _wrap("Abc") == _wrap("abc"):
            self.verify_name = True

        pkg_filename = "%s.sublime-package" % self.name
        pkg_path = os.path.join(sublime.packages_path(), self.name)

        # Scan for the shipped package so we can collect the proper case on
        # case insensitive systems.
        self._add_package(_pkg_scan(_shipped_packages_path(), pkg_filename), True)
        self._add_package(_pkg_scan(sublime.installed_packages_path(), pkg_filename, True))
        self._add_path(pkg_path)

        # Now that package data is fully populated, check if we're a dep and
        # then load our metadata.
        self._check_if_depdendency()
        self._load_metadata()

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

    def __select_dependencies(self, dependency_info):
        """
        This is taken from Package Control (and slightly modified). It takes a
        dependency JSON object from dependencies.json and determines which
        entry  (if any) should be used based on sublime version, os and
        architecture. It will return an empty list if there is no match.
        """
        platform_selectors = [
            sublime.platform() + '-' + sublime.arch(),
            sublime.platform(),
            '*'
        ]

        for platform_selector in platform_selectors:
            if platform_selector not in dependency_info:
                continue

            platform_dependency = dependency_info[platform_selector]
            versions = platform_dependency.keys()

            # Sorting reverse will give us >, < then *
            for version_selector in sorted(versions, reverse=True):
                if not _is_compatible_version(version_selector):
                    continue
                return platform_dependency[version_selector]

        # If there were no matches in the info, but there also weren't any
        # errors, then it just means there are not dependencies for this machine
        return []

    def __get_dependencies(self):
        if not self.contains_file("dependencies.json"):
            return self.metadata.get("dependencies", [])

        try:
            data = self.get_file("dependencies.json")
            return self.__select_dependencies(sublime.decode_value(data))

        except:
            return self.metadata.get("dependencies", [])

    def __get_meta_file(self, resource):
        try:
            if self.contains_file(resource):
                return self.get_file(resource)

        except:
            pass

        return None

    def _load_metadata(self):
        res_name = "package-metadata.json"
        if self.is_dependency:
            res_name = "dependency-metadata.json"

        self.metadata = default_metadata(self)

        try:
            data = self.__get_meta_file(res_name)
            if data:
                self.metadata = sublime.decode_value(data)

            if not self.is_dependency:
                self.metadata["dependencies"] = self.__get_dependencies()
        except:
            pass

        if self.contains_plugins():
            self.python_version = "3.3"
            data = self.__get_meta_file(".python-version")
            if data:
                self.python_version = data.strip()

    def _get_packed_pkg_file_contents(self, override_file, as_list=True):
        try:
            with zipfile.ZipFile(self.package_file()) as zFile:
                info = find_zip_entry(zFile, override_file)
                file = codecs.EncodedFile(zFile.open(info, mode="rU"), "utf-8")
                if as_list:
                    content = io.TextIOWrapper(file, encoding="utf-8").readlines()
                else:
                    content = io.TextIOWrapper(file, encoding="utf-8").read()

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

    def _get_file_internal(self, resource, as_binary=True):
        """
        Get file contents either from the packed package that Sublime would use
        or the local folder and return it as either a string or bytes. This
        is the analog of the sublime.load_resource() API call and it's binary
        cousin, implemented here in a way that doesn't utilize the Sublime file
        catalog so that it works with ignored packages.
        """
        if self.unpacked_path:
            name = os.path.join(self.unpacked_path, resource)
            mode, encoding = ("rb", None) if as_binary else ("r", "utf-8")
            try:
                with open(name, mode, encoding=encoding) as handle:
                    return handle.read()

            except PermissionError:
                print("Error loading %s; permission denied" % name)
                return None

            except UnicodeDecodeError:
                print("Error loading %s; unable to decode file contents" % name)
                return None

            except FileNotFoundError:
                pass

        try:
            if self.package_file() is not None:
                with zipfile.ZipFile(self.package_file()) as zFile:
                    info = find_zip_entry(zFile, resource)
                    file = codecs.EncodedFile(zFile.open(info, mode="rU"), "utf-8")
                    if as_binary:
                        return file.read()

                    return io.TextIOWrapper(file, encoding="utf-8").read()

        except (KeyError, FileNotFoundError):
            return None

        except UnicodeDecodeError:
            print("Error loading %s:%s; unable to decode file contents" %
                  (self.package_file(), resource))
            return None

    def _override_is_binary(self, override_file):
        for pattern in self.binary_patterns:
            if fnmatch.fnmatch(override_file, pattern):
                return True
        return False

    def exists(self):
        return bool(self.shipped_path or self.installed_path or self.unpacked_path)

    def package_file(self):
        return self.installed_path or self.shipped_path

    def package_mtime(self):
        return self.installed_mtime if self.installed_path else self.shipped_mtime

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

    def unknown_override_files(self):
        """
        Get the list of files that exist in the unpacked package but not in the
        packed package (if any). This implies that the override type is simple,
        and will return an empty set if there are no such files.
        """
        if not self.has_possible_overrides(True):
            return PackageFileSet()

        if self.unknown_overrides is not None:
            return self.unknown_overrides

        base_list = self.package_contents()
        over_list = self.unpacked_contents()

        self.unknown_overrides = over_list - base_list
        return self.unknown_overrides

    def unpacked_contents_unknown_filtered(self, patterns):
        """
        This performs the same basic operation as unpacked_contents() does, but
        the list of returned files is filtered such that any package contents
        that appear in unknown_override_files() and also match one of the
        patterns in the provided pattern list are removed prior to the return.

        The value of this call is not cached; it also updates the internal
        state on the number of unknown overrides that have been ignored, which
        is reflected in the call to status().
        """
        self.unknowns_filtered = 0
        pkg_files = self.unpacked_contents()
        if pkg_files is None:
            return None

        unknown_overrides = self.unknown_override_files()

        # use re.match to do an implicit anchor at the start of the file name
        filtered = {r for r in unknown_overrides
                     if any(p.match(r) for p in patterns)}

        self.unknowns_filtered = len(filtered)

        return pkg_files - filtered

    def expired_override_files(self, simple=True):
        """
        Get a list of all overridden files for this package which are older
        than the source sublime-package file that is currently being used by
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

    def packed_override_contents(self, override_file, as_list=True):
        """
        Given the name of an override file, return back a tuple that indicates
        if the source package is shipped or installed and the contents of the
        base file for that override as a list of lines.
        """
        content = self._get_packed_pkg_file_contents(override_file, as_list)
        if not content:
            return (None, None)

        return ("Installed" if self.installed_path else "Shipped",
                content[0])

    def unpacked_override_contents(self, override_file):
        """
        Given the name of an override file, return back the contents of the
        override as a list of lines.
        """
        content = self._get_unpacked_override_contents(override_file)
        if not content:
            return None

        return content[0]

    def contains_file(self, resource):
        """
        Checks to see if the resource provided exists in this package or not
        and returns a value as appropriate. This will check both inside of
        package files as well as on the local file system; the return value
        only tells you that this resource exists in the package, not WHERE it
        comes from.
        """
        try:
            if self.package_file() is not None:
                with zipfile.ZipFile(self.package_file()) as zFile:
                    if find_zip_entry(zFile, resource) is not None:
                        return True

        except (KeyError, FileNotFoundError):
            pass

        if self.unpacked_path:
            return os.path.exists(os.path.join(self.unpacked_path, resource))

        return False

    def contains_plugins(self):
        """
        Checks to see if this package contains any plugins or not, which is
        defined as a .py file in the root of the package contents.
        """
        def is_plugin(name):
            if name.endswith(".py") and "/" not in name:
                # Exclude syntax test files in the shipped Python package
                return False if name.startswith("syntax_test") and self.name == "Python" else True

            return False

        try:
            if self.package_file() is not None:
                with zipfile.ZipFile(self.package_file()) as zFile:
                    for info in zFile.infolist():
                        if is_plugin(info.filename):
                            return True

        except (FileNotFoundError):
            pass

        if self.unpacked_path:
            path_len = len(self.unpacked_path) + 1
            res_spec = os.path.join(self.unpacked_path, "*.py")
            try:
                next(f for f in glob.iglob(res_spec) if is_plugin(f[path_len:]))
                return True
            except:
                pass

        return False

    def get_file(self, resource):
        """
        Given a resource specification, get the contents of that resource and
        return it; returns None if the resource is not found. The resource
        loaded is the one that sublime.load_resource() would load.
        """
        return self._get_file_internal(resource, as_binary=False)

    def get_binary_file(self, resource):
        """
        This works as get_file does, but the returned value is a bytes
        instead of a string; thus it works like sublime.load_binary_resource.
        As in get_file(), this returns the resource that API method would load.
        """
        return self._get_file_internal(resource, as_binary=True)

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

        packed = self._get_packed_pkg_file_contents(override_file, as_list=True)
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

    def status(self, detailed=False):
        """
        Return a status dictionary for the status of this package. When
        detailed is True, the resulting dictionary will contain complete
        override details. False provides only information on whether overrides
        are possible or not.

        This detail requires gathering package contents and thus is a more
        heavy-weight call.
        """
        if detailed:
            overrides         = len(self.override_files(simple=True))
            expired_overrides = len(self.expired_override_files(simple=True))
            unknown_overrides = len(self.unknown_override_files())
        else:
            overrides = 1 if self.has_possible_overrides() else 0
            expired_overrides = unknown_overrides = overrides

        return {
            # Core info
            "name": self.name,
            "metadata": self.metadata,
            "python_version": self.python_version,

            # Installation Status
            "is_shipped":   bool(self.shipped_path),
            "is_installed": bool(self.installed_path),
            "is_unpacked":  bool(self.unpacked_path),

            # Extended status
            "is_disabled":   self.is_disabled,
            "is_dependency": self.is_dependency,

            # Is this a complete override?
            "is_complete_override":         self.has_possible_overrides(simple=False),
            "is_complete_override_expired": bool(self.expired_override_files(simple=False)),

            # Override information; may contain false positives if detailed is
            # False
            "overrides":         overrides,
            "expired_overrides": expired_overrides,
            "unknown_overrides": unknown_overrides,
            "unknowns_filtered": self.unknowns_filtered
        }


###----------------------------------------------------------------------------


class PackageList():
    """
    Holds a list of packages and all of their relevant information. This can
    be either a complete list of all known packages, or a sub list of only
    certain packages by name.

    The class implements a dictionary interface for callers and iterates over
    known packages in their Sublime text load order.

    On case insensitive file systems, the names of packages are not case
    sensitive. In the event that different packages provide different cases of
    package name, the first name seen (i.e. either shipped or installed) will
    be the "de facto" case for that package.
    """
    def __init__(self, name_list=None):
        self._list = dict()
        self._disabled = 0
        self._dependencies = 0

        # Maps lower cased package names to listed packages on case insensitive
        # systems.
        self._case_list = dict() if _wrap("ABC") == _wrap("abc") else None

        if name_list is not None:
            if isinstance(name_list, str):
                name_list = [name_list]

            if _wrap("Abc") == _wrap("abc"):
                name_list = [_wrap(name) for name in name_list]

        self._shipped = self.__find_pkgs(_shipped_packages_path(), name_list, shipped=True)
        self._installed = self.__find_pkgs(sublime.installed_packages_path(), name_list)
        self._unpacked = self.__find_pkgs(sublime.packages_path(), name_list, packed=False)

        for pkg in self._list.values():
            # Check if the package is a dependency and then load it's metadata.
            pkg._check_if_depdendency()
            pkg._load_metadata()

            # Count it as a dependency
            if pkg.is_dependency:
                self._dependencies += 1

    def package_counts(self):
        """
        Return a tuple which contains the number of packages that fit certain
        critera: (shipped, installed, unpacked, disabled, dependencies).

        Note that installed packages indicates the number of packages installed
        by the user into the Installed Packages/ folder.
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
            self._list[name] = PackageInfo(name, scan=False)
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

    def __find_pkgs(self, location, name_list, packed=True, shipped=False):
        count = 0
        # Follow symlinks since we're stopping after one level anyway except in
        # the Installed Packages/ folder. Maybe an issue if someone goes crazy
        # in there?
        for (path, dirs, files) in os.walk(location, followlinks=True):
            if packed:
                if name_list:
                    files = [f for f in files if os.path.splitext(_wrap(f))[0] in name_list]

                for name in [f for f in files if f.endswith(".sublime-package")]:
                    self.__packed_package(path, name, shipped)
                    count += 1
            else:
                if name_list:
                    dirs = [d for d in dirs if _wrap(d) in name_list]

                for name in dirs:
                    self.__unpacked_package(path, name, shipped)
                    count += 1

            if shipped or not packed:
                break

        return count


###----------------------------------------------------------------------------
