import sublime
import os
import string

###-----------------------------------------------------------------------------

class PackageInfo():
    def __init__(self, name):
        self.name = name
        self.shipped_path = None
        self.installed_path = None
        self.unpacked_path = None

    def __repr__(self):
        return "[name={0}, shipped={1}, installed={2}, unpacked={3}]".format (
            self.name ,
            self.shipped_path,
            self.installed_path,
            self.unpacked_path)

###-----------------------------------------------------------------------------

class PackageList():
    def __init__(self):
        self.list = dict ()

        exec_dir = os.path.dirname (sublime.executable_path ())
        self.__get_package_list (os.path.join (exec_dir, "Packages"), shipped=True)
        self.__get_package_list (sublime.installed_packages_path ())
        self.__get_package_list (sublime.packages_path (), packed=False)

    def __len__(self):
        return len (self.list)

    def __getitem__(self, key):
        return self.list[key]

    def __contains__(self, item):
        return item in self.list

    def __iter__(self):
        yield "Default", self.list["Default"]
        for pkg in sorted (self.list):
            if pkg in ["User", "Default"]:
                continue
            yield pkg, self.list[pkg]
        if "User" in self.list:
            yield "User", self.list["User"]

    def __get_pkg(self, name):
        if name not in self.list:
            self.list[name] = PackageInfo (name)

        return self.list[name]

    def __packed_package (self, path, name, shipped):
        package_path = os.path.join (path, name)
        pkg = self.__get_pkg (os.path.splitext(name)[0])
        if shipped:
            pkg.shipped_path = package_path
        else:
            pkg.installed_path = package_path

    def __unpacked_package (self, path, name, shipped):
        pkg = self.__get_pkg (name)
        pkg.unpacked_path = os.path.join (path, name)

    def __get_package_list (self, location, packed=True, shipped=False):
        # Follow symlinks since we're stopping after one level anyway
        for (path, dirs, files) in os.walk (location, followlinks=True):
            if packed:
                for name in [f for f in files if f.endswith (".sublime-package")]:
                    self.__packed_package (path, name, shipped)
            else:
                for name in dirs:
                    self.__unpacked_package (path, name, shipped)
            break

###-----------------------------------------------------------------------------
