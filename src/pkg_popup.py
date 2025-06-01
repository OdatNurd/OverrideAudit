import sublime

from .core import oa_setting


###----------------------------------------------------------------------------


# Help information available in popups via [?] links; the help is stored based
# on the link name associated with it.
#
# Each topic may contain {pkg} to reference the name of the package being
# displayed in the popup.
_help = {
    # Description for complete overrides; linked from the popup caption for
    # complete overrides.
    "complete_override":
    """
    <h1>{pkg}</h1>
    <div class="help_text">
        <p>
            This package exists as a <b>sublime-package</b> file in both the
            <em>Shipped</em> packages folder as well as the <em>Installed
            Packages</em> folder.
        </p><p>
            As a result, the version of the package in the <em>Installed
            Packages</em> folder is the one that is being used to provide the
            base for this package and the <em>Shipped</em> version of the
            package is <span class="complete">Completely</span> ignored.
        </p><p>
            When the header of the popup also mentions that the package is
            <span class="expired">Expired</span>, the underlying
            <em>Shipped</em> package has been updated; in this case the
            override may be masking new features or bug fixes from the
            <em>Shipped</em> version of the package.
        </p>
    </div>
    <a href="pkg:{pkg}">Back</a>
    """,

    # Description of why it's not possible for a package to contain any
    # overrides.
    "no_override":
    """
    <h1>{pkg}</h1>
    <div class="help_text">
        <p>
            In order for a package to support overridden resources, it must be
            represented by both a <b>sublime-package</b> file (either
            <em>Shipped</em> with Sublime or in the <em>Installed Packages</em>
            folder) as well as being represented in the unpacked
            <em>Packages</em> folder.
        </p><p>
            This package does not fit into that category, and thus is it not
            possible for this package to contain any overridden package
            resource files currently.
        </p>
    </div>
    <a href="pkg:{pkg}">Back</a>
    """
}


# Help information associated with hover popups that provide more information
# on things in reports, such as the [X] expired override marker and the like.
_info = {
    "[SIU]":
    """
    <h1>Package Type Specifier</h1>
    <div class="help_text">
        <p>
            This field provides a shorthand for letting you know the different
            states in which this package might exist; A package is always in at
            least one of these states, but it could be in two or even all three
            of them at once. The different states are:
        </p>
        <p>
            <ul>
                <li><strong>S</strong> marks packages that ships with Sublime
                Text itself. Packages of this type are not installed in the
                <a href="browse_data_dir">data directory</a>, and are instead
                stored in the location where Sublime Text is installed.</li><br />

                <li><strong>I</strong> marks user installed packages, installed
                into the <code>Installed Packages</code> folder in a
                <code>sublime-package</code> file. This includes package files
                you install manually as well as those installed by Package
                Control.</li><br/>

                <li><strong>U</strong> marks packages that appears as named
                folders in the <code>Packages</code> folder.</li>
            </ul>
        </p>
    </div>
    """,

    "[X]":
    """
    <h1>Expired Override</h1>
    <div class="help_text">
        <p>
            This override is <strong><em>expired</em></strong>.
        </p>
        <p>
            An override is considered to be expired if the underlying package
            that contains it has been updated since the override was created.
            This could mean that the override is now out of date; it might
            need to be changed or it may no longer be needed at all.
        </p>
        <p>
            You can use the <a href="diff_report:{pkg}">Diff report</a>
            to determine if you need to make any changes or incorporate new
            fixes. While expired, your override may block new bug fixes and
            features in the source package, since overriden resources are
            always used if they exist, even if they're out of date.
        </p>
    </div>
    """,

    "[?]":
    """
    <h1>Unknown Override</h1>
    <div class="help_text">
        <p>
            This override is <strong><em>unknown</em></strong>.
        </p>
        <p>
            An override is considered to be <code>unknown</code> when there is
            no file in the underlying <code>sublime-package</code> file that
            shares it's name and location within the package.
        </p>
        <p>
            In a technical sense this is not actually an override and is just a
            regular package resource, though they could still be an issue. For
            example files like this may be old overrides that are no longer
            needed because the underlying file was removed.
        </p>
    </div>
    """,

    "[S]":
    """
    <h1>Package Type Specifier</h1>
    <div class="help_text">
        <p>
            This is a package that ships with Sublime Text itself and is common
            for all users of Sublime. Packages of this type provide much of the
            core functionality that you get "out of the box".
        </p>
        <p>
            Shipped packages are stored in a folder inside of the Sublime
            installation folder; don't be alarmed if you can't find them
            anywhere.
        </p>
        <p>
            You should <strong><em>NEVER</em></strong> directly modify a shipped
            package; rather, if you want or need to change default behaviour, you
            should <a href="override:{pkg}">create an override</a> instead.
        </p>
    </div>
    """,

    "[I]":
    """
    <h1>Package Type Specifier</h1>
    <div class="help_text">
        <p>
            This is a package that is installed as a <code>sublime-package</code>
            file inside of the <code>Installed Packages</code> folder; normally
            this would be done by Package Control, but you can also install
            packages in this format manually as well.
        </p>
        <p>
            You should <strong><em>NEVER</em></strong> directly modify a
            package installed in this manner unless you manually put it there;
            on a future upgrade your changes <strong><em>WILL</em></strong> be
            discarded.
        </p>
        <p>
            If you want or need to modify the behaviour of the package, you
            should <a href="override:{pkg}">create an override</a> instead.
        </p>
    </div>
    """,

    "[U]":
    """
    <h1>Package Type Specifier</h1>
    <div class="help_text">
        <p>
            This is a package that appears as a named folder in the
            <code>Packages</code> folder; the contents of the folder represent
            the contents of the package.
        </p>
        <p>
            If a package is installed in the <code>Installed Packages</code>
            folder or shipped with Sublime and also appears in the
            <code>Packages</code> folder, any files in the folder will
            <strong>override</strong> similarly named files in the underlying
            package.
        </p>
    </div>
    """,

    "<Complete Override>":
    """
    <h1>Complete Package Override</h1>
    <div class="help_text">
        <p>
            A <code>Complete Override</code> is an override that replaces the
            entire contents of a package that ships with Sublime Text with a
            new package, such as a version from a different build of Sublime,
            or one in which package resources are removed (e.g. snippets that
            are no longer desired).
        </p>
        <p>
            To be a complete override, a <code>sublime-package</code> file for
            a package needs to exist in the <code>Installed Packages</code>
            folder as well as having the name of one of the packages that ship
            with Sublime Text.
        </p>
        <p>
            For a complete override, Sublime will ignore it's own version of
            such a package in favor of the one that is user installed. This
            type of override is powerful, but uncommon.
        </p>
    </div>
    """,

    "[EXPIRED]":
    """
    <h1>Expired Complete Package Override</h1>
    <div class="help_text">
        <p>
            This override is an <strong><em>expired, complete override</em></strong>.
        </p>
        <p>
            Similar to a regular override, a complete override is considered to
            be expired if the shipped package that it is overriding has been
            updated (via an update to Sublime Text) since the override was
            created.
        </p>
        <p>
            This could mean that the override is now out of date; it
            might contain files that no longer exist or be missing new files
            and bug fixes/features.
        </p>
    </div>
    """,
}

###----------------------------------------------------------------------------


# The overall style sheet used for the package popups. The colors defined here
# all come from the current color scheme by using the var() syntax to pull the
# closest color available.
_css = """
    body {
        font-family: system;
        margin: 0.5rem 1rem;
        width: 40em;
    }

    a {
        text-decoration: none;
        color: var(--greenish);
    }

    .hidden {
        display: none;
    }

    h1 {
        width: 33em;
        font-size: 1.2rem;
        font-weight: bold;
        margin: 0;
        padding: 0;
        border-bottom: 2px solid var(--orangish);
        color: var(--orangish);
    }

    .code {
        font-family: monospace;
        color: var(--bluish);
    }

    h1 span {
        font-size: 0.80rem;
        position: relative;
        left: 0;
    }

    .complete {
        color: var(--cyanish);
    }

    .expired {
        color: var(--redish);
    }

    .dependency {
        color: var(--redish);
        font-size: 0.75rem;
        line-height: 0.75rem;
        position: relative;
    }

    .disabled {
        color: color(var(--foreground) alpha(0.50));
        font-size: 0.75rem;
        line-height: 0.75rem;
        position: relative;
    }

    .version {
        font-size: 0.8rem;
        line-height: 0.8rem;
        margin-top: -0.8rem;
    }

    .python {
        font-size: 0.8rem;
        line-height: 0.8rem;
        margin-top: -0.8rem;
    }

    .url {
        font-size: 0.8rem;
        line-height: 0.8rem;
        margin-top: -0.8rem;
    }

    .metadata {
        font-size: 0.8rem;
        margin-bottom: 1rem;
        margin-left: 2em;
        margin-right: 2em;
    }

    .depends, .description {
        margin-top: 0.5rem;
    }

    .help {
        font-size: 0.8rem;
    }

    .overrides {
        font-size: 0.9rem;
        margin-bottom: 1rem;
    }

    .links {
        font-size: 0.9rem;
        margin-bottom: 1rem;
    }

    .help_text {
        font-size: 0.9rem;
    }

    .status {
        color: var(--cyanish);
    }
"""

# The overal HTML layout of the minihtml that makes up the popup. This will be
# filled out with generated data based on the current package.
_pkg_popup = """
    <body id="overrideaudit-package-popup">
        <style>
        {css}
        </style>
        {body}
    </body>
"""


###----------------------------------------------------------------------------


# Pick a CSS class based on the value provided; the default value for a False
# value is autoselected for clarity but can be specified as desired.
_class = lambda v, avail, missing="hidden": avail if v else missing

# Choose between a singular and a plural based on the value provided; for the
# ultimate in pedantism. The most common values default.
_p = lambda v, one="resource", many="resources": one if v == 1 else many


###----------------------------------------------------------------------------


def _get_dependant_packages(view, details):
    """
    Given the status details of a dependency, return back the list of packages
    that declare a dependency on that package. This information is gathered
    from the cached package metadata in the provided view and is cached there
    after first access.

    Since this depends on data from the given view, this will only perform as
    expected for views that contain all package information (e.g. a Package
    Report). This is generally the only report which can contain a dependency.
    """
    if "dependants" in details:
        return details["dependants"]

    name = details["name"]
    dependants = []

    packages = view.settings().get("override_audit_report_packages", {})
    for pkg, info in packages.items():
        pkg_deps = info.get("metadata", {}).get("dependencies", [])
        if name in pkg_deps:
            dependants.append(pkg)

    packages[name]["dependants"] = dependants
    view.settings().set("override_audit_report_packages", packages)
    return dependants


def _popup_header(details):
    """
    Given the status details of a package, return back the header for the
    popup that describes this package. This contains the name of the package
    and it's general state, including:
        - If it is a complete override and, if so, if it is expired
        - Whether it is a dependency
        - Whether it is disabled or not
        - The version from the metadata (if any)
    """
    metadata = details.get("metadata", {})
    version = metadata.get("version", "")
    url = metadata.get("url", "")
    python_version = (details.get("python_version", "")
                      or "package has no plugins")

    if version == "" and not details.get("is_shipped", False):
        version = "unknown version"

    name = details.get("name", "Unknown")
    is_disabled = details.get("is_disabled", False)
    is_dependency = details.get("is_dependency", False)
    is_complete = details.get("is_complete_override", False)
    is_expired = details.get("is_complete_override_expired", False)

    return """
        <h1>
            {name}
            <span class="{is_complete}">Overrides Shipped Package
            <span class="{is_complete_expired}">[Expired]</span>
            <span class="help">[<a href="help:complete_override:{name}">?</a>]</span>
            </span>
        </h1>
        <div class="{is_disabled}">This package is currently disabled</div>
        <div class="{is_dependency}">This package is a dependency library</div>
        <div class="{has_version}">Version: {version}</div>
        <div class="{has_url}"><a href="{url}">{url}</a></div>
        <div class="python">Python: {python_version}</div>
    """.format(
        name=name,
        is_complete=_class(is_complete, "complete"),
        is_complete_expired=_class(is_expired, "expired"),
        is_disabled=_class(is_disabled, "disabled"),
        is_dependency=_class(is_dependency, "dependency"),
        has_version=_class(version != '', "version"),
        version=version,
        python_version=python_version,
        has_url=_class(url != '', "url"),
        url=url
    )


def _metadata(view, details):
    """
    Given the status details of a package, return back the metasdata
    information for the package, which contains the list of dependencies or
    dependant packages as well as the package description.
    """
    is_dep = details.get("is_dependency", False)
    metadata = details.get("metadata", {})

    if is_dep:
        title = "Dependants"
        dep_list = _get_dependant_packages(view, details)
    else:
        title = "Dependencies"
        dep_list = metadata.get("dependencies", [])

    dep_list = ['<a href="pkg:{pkg}">{pkg}</a>'.format(pkg=dep) for dep in dep_list]
    dependencies = ", ".join(dep_list) if dep_list else "none"

    return """
    <div class="metadata">
        <div class="{has_deps}">{title}: {dependencies}</div>
        <div class="description">{description}</div>
    </div>
    """.format(
        description=metadata.get("description", "No description provided"),
        has_deps=_class(is_dep or dep_list, "depends"),
        title=title,
        dependencies=dependencies
        )


def _can_have_overrides(details):
    """
    For non-detailed hover popups, this returns an indication of whether or not
    the package in the details can possibly contain overrides or not.
    """
    if details["overrides"]:
        return """
        <div class="overrides">
        This package may contain overridden package resources; to check, view
        the <a href="override_report">override report</a>.
        </div>
        """
    else:
        return """
        <div class="overrides">
        This package currently does not contain overridden package resources.
        <span class="help">[<a href="help:no_override:{pkg}">?</a>]</span>
        </div>
        """.format(pkg=details["name"])


def _override_details(details):
    """
    For detailed hover popups, this returns information on the count of
    overrides and their various types.
    """
    has_overrides = details["overrides"] > 0
    has_expired = details["expired_overrides"] > 0
    has_unknown = details["unknown_overrides"] > 0
    has_filtered = details["unknowns_filtered"] > 0

    # Possible overrides controls the second section, for when we know there
    # might be overrides, but we don't know how many there are; so only flag
    # it when we know there are some but don't know how many there are.
    possible_overrides = details["has_possible_overrides"] and details["overrides"] < 0

    return """
        <div class="{has_overrides_class}">
            {overrides} overridden package {o_desc}
            <span class="{expired_class}">({expired} expired)</span>
            <br>
            <span class="{unknown_class}"> {unknown} unpacked {u_desc} not present in the source package
                <span class={filtered_class}> ({filtered} being filtered)</span>
            </span>
        </div>
        <div class="{possible_overrides_class}">
            This package may contain overrides; use <span class="code">View Diferences</span> to perform a scan.
        </div>
        """.format(
            pkg=details["name"],
            has_overrides_class=_class(has_overrides, "overrides"),
            overrides=details["overrides"],
            o_desc=_p(details["overrides"]),

            expired_class=_class(has_expired, "has_expired"),
            expired=details["expired_overrides"],

            unknown_class=_class(has_unknown, "overrides"),
            unknown=details["unknown_overrides"],
            u_desc=_p(details["unknown_overrides"]),

            possible_overrides_class=_class(possible_overrides, "overrides"),

            filtered_class=_class(has_filtered, "filtered"),
            filtered=details["unknowns_filtered"])


def _popup_footer(details):
    """
    Generate a footer for the package popup that indicates how the package is
    installed.
    """
    return """
        {shipped} <span class="status">Ships with Sublime</span> &nbsp; &nbsp;
        {installed} <span class="status">In Installed Packages Folder</span> &nbsp; &nbsp;
        {unpacked} <span class="status">In Packages Folder</span>
        """.format(
            shipped="\u2611" if details["is_shipped"] else "\u2610",
            installed="\u2611" if details["is_installed"] else "\u2610",
            unpacked="\u2611" if details["is_unpacked"] else "\u2610")

def _package_links(details):
    """
    Generate a set of links for taking actions with this package. Each of the
    links hides itself when it's not valid, and if none are valid the entire
    section is hidden.
    """
    can_create = details.get("is_shipped", False) or details.get("is_installed", False)

    # Only consider that we have overrides (and thus should allow you to open
    # a diff of them) if it's possible to have overrides and the number is
    # either -1 (did not check) or some number > 0 (there are some). A value of
    # 0 means we looked and there are none.
    has_overrides = details.get("has_possible_overrides", False) and details.get("overrides", -1) != 0

    return """
        <div class="{link_class}">
            <span class="{has_overrides}">[<a href="diff_report:{pkg}">View Differences</a>]</span>
            <span class="{can_create}">[<a href="override:{pkg}">Create new override</a>]</span>
            <br>
        </div>
    """.format(
        link_class=_class(can_create or has_overrides, "links"),
        has_overrides=_class(has_overrides, "overrides"),
        can_create=_class(can_create, "overrides"),
        pkg=details["name"])


def _expand_details(view, details, is_detailed):
    """
    Given the details information for a package and whether or not it should be
    interpreted as being detailed or not, return back the HTML that describes
    the package or dependency.
    """
    result = """
    {header}
    {metadata}
    {overrides}
    {links}
    {footer}
    """.format(
        header=_popup_header(details),
        metadata=_metadata(view, details),
        overrides=_override_details(details) if is_detailed else _can_have_overrides(details),
        links=_package_links(details),
        footer=_popup_footer(details)
        )

    return result


def _render_popup(view, link_name, is_detailed):
    """
    Render the appropraite HTML content for the link provided, getting the
    package information from the given view and detailing the output as
    appropriate.

    The link_name can be pkg:packagename to display the popup for a given
    package or help:topic:packagename to display the help for the provided help
    topic in the popup, rendering a link to come back to the packagename.

    The return value is None if the link is not recognized.
    """
    packages = view.settings().get("override_audit_report_packages", {})

    if link_name.startswith("pkg:"):
        link_name = link_name[len("pkg:"):]

        pkg_details = packages.get(link_name, None)
        return None if pkg_details is None else _expand_details(view, pkg_details, is_detailed)

    if link_name.startswith("help:"):
        link_name = link_name[len("help:"):]
        topic, pkg = link_name.split(':')

        help_text = _help.get(topic, None)
        return None if help_text is None else help_text.format(pkg=pkg)

    if link_name.startswith("info:"):
        link_name = link_name[len("info:"):]
        topic, pkg = link_name.split(':')

        help_text = _info.get(topic, None)
        return None if help_text is None else help_text.format(pkg=pkg)

    return None


def _popup_link(view, point, link_name, is_detailed):
    """
    Respond to a link link in a displayed package popup by examining the link
    and taking the appropriate action, which is either to execute an external
    command or display some HTML content.
    """
    if link_name == "override_report":
        view.window().run_command("override_audit_override_report")
    elif link_name == "browse_data_dir":
        view.window().run_command('open_dir', {"dir": "${packages}/.."})
    elif link_name.startswith("diff_report:"):
        package = link_name[len("diff_report:"):]
        if package != "":
            view.window().run_command("override_audit_diff_report", {"package": package})
        else:
            view.window().run_command("override_audit_diff_report")
    elif link_name.startswith("override:"):
        package = link_name[len("override:"):]
        if package != "":
            view.window().run_command("override_audit_create_override", {"package": package})
        else:
            view.window().run_command("override_audit_create_override")

    elif link_name.startswith("http"):
        view.window().run_command("open_url", {"url": link_name})

    # We could use view.update_popup() instead, but when the content changes
    # size Sublime reads that as a mouse move and hides the popup instead.
    show_pkg_popup(view, point, link_name, is_detailed)


###----------------------------------------------------------------------------


def show_pkg_popup(view, point, link_name, is_detailed):
    """
    Render the package popup at the given point, using the provided link name
    as the initial popup content. The popup may contain links, which will alter
    the content in the popup when they're clicked.
    """
    if not oa_setting("enable_hover_popup"):
        return

    body = _render_popup(view, link_name, is_detailed)
    if body is not None:
        view.show_popup(
            _pkg_popup.format(css=_css, body=body),
            flags=sublime.HIDE_ON_MOUSE_MOVE_AWAY,
            location=point,
            max_width=1024,
            max_height=512,
            on_navigate=lambda href: _popup_link(view, point, href, is_detailed))


###----------------------------------------------------------------------------
