import sublime
from os.path import dirname, basename

from .core import packages_with_overrides, log
from .core import PackageListCollectionThread


###---------------------------------------------------------------------------


class ResourceType():
    """
    This class acts as a simple enumeration of the different styles of
    resources that you can browse using the other classes in this module.
    """
    OVERRIDE = 1
    NONOVERRIDE = 2
    ALL = 3


###---------------------------------------------------------------------------


class PackageBrowser():
    """
    Provide the ability to browse for a package among all known packages. The
    browse can be filtered to show all packages (ALL) or only those packages
    that contain at least one override (OVERRIDE) as desired.

    The NONOVERRIDE option is treated as ALL for the purposes of this class.
    """
    def __init__(self, window=None, file_type=ResourceType.ALL):
        self.window = window or sublime.active_window()
        self.file_type = file_type

    def _get_contents(self, pkg_list):
        if self.file_type == ResourceType.OVERRIDE:
            return packages_with_overrides(pkg_list)
        else:
            return [name for name, pkg in pkg_list]

    def browse(self, pkg_list, on_done):
        """
        Allows the user to select a package from the package list provided,
        filtering the list to the criteria set in the file_type attribute.

        on_done will be called with the name of the package selected, which can
        be None if the panel was cancelled or no packages were found.
        """
        items = self._get_contents(pkg_list)
        if not items:
            log("No packages contain resources of the selected type",
                status=True, dialog=True)
            return on_done(None)

        self.window.show_quick_panel(
            items=items,
            on_select=lambda idx: on_done(items[idx] if idx >= 0 else None))


###---------------------------------------------------------------------------


class ResourceBrowser():
    """
    Provide the ability to browse for a package file among the list of files
    contain in a package. The browse can be filtered to allow for the selection
    of any resource (ALL), only overrides (OVERRIDE) or only files that are not
    overrides (NONOVERRIDE).

    The value of the unknown argument indicates if package files whose status
    is unknown should appear in the list or not. An unknown file is one which
    appears in the unpacked content of the package but doesn't correspond to a
    packed file.

    The browse will use hierarchy if the package content has a structure.
    """

    # These keys in the result dictionary tell us what files and folders exist
    # at this particular nesting level in the resulting output dictionary.
    FILES='files'
    FOLDERS='folders'

    # In addition to the above, while browsing package content this key is
    # added to stack entries to indicate what the current item is at the
    # stack entry chosen.
    CURRENT='current'

    def __init__(self, window=None, file_type=ResourceType.ALL, unknown=True):
        self.window = window or sublime.active_window()
        self.file_type = file_type
        self.unknown = unknown
        self.cache = {}

    def _explode_files(self, files):
        """
        Explode a list of files that represent packge file contents into a dict
        which describes their logical path layout.

        The dict has keys that indicate the files and folders stored at this
        level, with each folder also being represented as a key that points to
        another similar dict for the content at that level.
        """
        def handle_file(file_spec, branch):
            parts = file_spec.split('/', 1)
            if len(parts) == 1:
                return branch[self.FILES].append(parts[0])

            subdir, remaining_path = parts[0] + '/', parts[1]
            if subdir not in branch:
                branch[self.FOLDERS].append(subdir)
                branch[subdir] = {self.FILES: [], self.FOLDERS: []}

            handle_file(remaining_path, branch[subdir])

        retVal = {self.FILES: [], self.FOLDERS: []}
        for file in sorted(files, key=lambda fn: (dirname(fn), basename(fn))):
            handle_file(file, retVal)

        return retVal

    def _get_pkg_content(self, pkg_info):
        """
        Get the browseable contents of the packge given, based on the browse
        type. This caches the result in case the user goes out of a package and
        then comes back in as part of a larger overall browse operation.
        """
        if pkg_info.name not in self.cache:
            # Collect all of the contents of the package; if there is a package
            # file, that is the cannonical content; otherwise get the list of
            # unpacked files.
            if pkg_info.package_file():
                contents = pkg_info.package_contents()
            else:
                contents = pkg_info.unpacked_contents()

            if self.file_type == ResourceType.ALL:
                res_list = contents
            else:
                overrides = pkg_info.override_files(simple=True)
                if self.file_type == ResourceType.OVERRIDE:
                    res_list = overrides
                else:
                    res_list = contents - overrides

            # Include files of unknown status if required.
            if self.unknown:
                res_list |= pkg_info.unknown_override_files()

            self.cache[pkg_info.name] = self._explode_files(res_list)

        return self.cache[pkg_info.name]

    def select_item(self, captions, items, prior_text, stack, index):
        if index >= 0:
            if index == 0 and len(stack) > 0:
                items = stack.pop()
                return self._display_panel(items, prior_text, stack)

            selected = captions[index]
            children = items.get(selected, None)

            if children is not None:
                items[self.CURRENT] = selected
                stack.append(items)
                return self._display_panel(children, prior_text, stack)

            resource = [entry[self.CURRENT] for entry in stack]
            resource.append(selected)

            return self.on_done(''.join(resource))

        return self.on_done(None)

    def _display_panel(self, items, prior_text, stack):
        captions = items[self.FOLDERS] + items[self.FILES]
        if len(stack) > 0 or self.return_to_pkg:
            captions.insert(0, prior_text)

        self.window.show_quick_panel(
            items=captions,
            on_select=lambda index: self.select_item(captions, items, prior_text, stack, index))

    def browse(self, pkg_info, return_to_pkg, on_done):
        """
        Allows the user to select a resource from the contents of the package
        provided, filtering the list to the criteria set in the file_type
        attribute.

        If return_to_pkg is True, the first item in the list will be an item
        that indicates that the user can go up a level; it is up to the caller
        to handle what happens with this item is selected however.

        on_done will be called with the name of the package selected, which can
        be None if the panel was cancelled or no packages were found.
        """
        self.on_done = on_done
        self.return_to_pkg = return_to_pkg

        items = self._get_pkg_content(pkg_info)
        if not items:
            log("Package '%s' has no resources of the selected type" % pkg_name,
                status=True, dialog=True)
            return on_done(None)

        self._display_panel(items, "..", [])


###---------------------------------------------------------------------------


class PackageResourceBrowser():
    """
    Opens a quick panel in the provided window to allow the user to browse for
    a package resource of a given type.

    Depending on the options provided, the user will be able to browse for a
    package or just files within a given package. The list of resources is
    filtered by the resource type provided.

    on_done is invoked when the user makes a selection and given the package
    and resource selected; both will be None if the browse was canceled by the
    user.
    """
    def __init__(self, pkg_name=None, resource=None, window=None,
                 file_type=ResourceType.ALL, pkg_list=None, unknown=True,
                 on_done=None):
        self.pkg_name = pkg_name
        self.resource = resource
        self.window = window or sublime.active_window()
        self.file_type = file_type
        self.pkg_list = pkg_list
        self.on_done = on_done
        self.cache = {}
        self.pkg_browser = PackageBrowser(self.window, self.file_type)
        self.res_browser = ResourceBrowser(self.window, self.file_type, unknown)

    def _on_done(self, pkg_info, resource_name):
        if self.on_done is not None:
            sublime.set_timeout(lambda: self.on_done(pkg_info, resource_name))

    def _res_select(self, pkg_name, file):
        if file == "..":
            return self._start_browse(thread=None)

        pkg_info = self.pkg_list[pkg_name] if file is not None else None
        self._on_done(pkg_info, file)

    def _pkg_select(self, pkg_name, return_to_pkg):
        if pkg_name is not None:
            if self.resource is not None:
                return self._on_done(self.pkg_list[pkg_name], self.resource)

            self.res_browser.browse(self.pkg_list[pkg_name],
                return_to_pkg,
                lambda name: self._res_select(pkg_name, name))
        else:
            self._on_done(None, None)

    def _start_browse(self, thread):
        if thread is not None:
            self.pkg_list = thread.pkg_list

        if self.pkg_name is None:
            return self.pkg_browser.browse(self.pkg_list, lambda name: self._pkg_select(name, True))

        if self.pkg_name in self.pkg_list:
            return self._pkg_select(self.pkg_name, False)

        log("Package '%s' does not exist" % self.pkg_name,
            status=True, dialog=True)

    def browse(self):
        """
        Start a browse operation based on the properties given at construction
        time or set before the call.

        If a package list was pre-supplied, the browse starts immediately;
        otherwise a background thread captures the package information first
        and then implicitly starts the browse.

        The on_done callback will be invoked with the name of the package and
        resource selected; both are None if the browse was cancelled.
        """
        if self.pkg_list is not None:
            return self._start_browse(None)

        PackageListCollectionThread(self.window, "Collecting Package List",
                                    lambda thr: self._start_browse(thr),
                                    name_list=self.pkg_name,
                                    get_overrides=True).start()


###---------------------------------------------------------------------------
