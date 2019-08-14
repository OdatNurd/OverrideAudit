import sublime
from collections import defaultdict


###----------------------------------------------------------------------------


# This metadata is used for any dependency that doesn't contain it's own
# dependency information, which covers any locally installed dependencies that
# are currently under development (i.e. they only contain a .sublime-dependency
# file).
_default_dep_metadata = {
    "version": "Unknown",
    "sublime_text": "*",
    "description": "No description provided",
    "platforms": ["*"],
}

# This metadata is used for any unrecognized package that's not a shipped
# package covered in the table below.
_default_pkg_metadata = {
    "version": "Unknown",
    "sublime_text": "*",
    "description": "No description provided",
    "platforms": ["*"],
    "dependencies": []
}

# This list contains definitions for metadata in packages that ship with
# Sublime directly, which otherwise have no metadata information attached to
# them.
_shipped_metadata = {
    # "Special" packages; these packages have a purpose other than to provide
    # support for a particular language.
    "Default": {
        "description": "Provides core Sublime Text functionality"
    },
    "Theme - Default": {
        "description": "Provides the Default and Adaptive application themes for Sublime Text 3"
    },
    "Color Scheme - Default": {
        "description": "Default color schemes that ship with Sublime Text 3"
    },
    "Color Scheme - Legacy": {
        "description": "Legacy color schemes; these used to ship with older versions of Sublime Text but have been officially deprecated"
    },
    "Language - English": {
        "description": "Provides spell checking dictionaries for the English language"
    },

    # This package is "special" but does not directly ship with Sublime and
    # instead is automatically created at first startup.
    "User": {
        "description": "Your User-specific key bindings, preferences and plugins"
    },


    # These packages ship with Sublime and provide language support (syntax,
    # completions, etc) for core languages and file types.
    "ActionScript": {
        "description": "Default language support for ActionScript"
    },
    "AppleScript": {
        "description": "Default language support for AppleScript"
    },
    "ASP": {
        "description": "Default language support for ASP"
    },
    "Batch File": {
        "description": "Default language support for Batch Files"
    },
    "C#": {
        "description": "Default language support for C#"
    },
    "C++": {
        "description": "Default language support for C++"
    },
    "Clojure": {
        "description": "Default language support for Clojure"
    },
    "CSS": {
        "description": "Default language support for CSS"
    },
    "D": {
        "description": "Default language support for D"
    },
    "Diff": {
        "description": "Default language support for Diff"
    },
    "Erlang": {
        "description": "Default language support for Erlang"
    },
    "Git Formats": {
        "description": "Default language support for <em><b>git</b></em> files and output (commit messages, logs, etc)"
    },
    "Go": {
        "description": "Default language support for Go"
    },
    "Graphviz": {
        "description": "Default language support for Graphviz"
    },
    "Groovy": {
        "description": "Default language support for Groovy"
    },
    "Haskell": {
        "description": "Default language support for Haskell"
    },
    "HTML": {
        "description": "Default language support for HTML"
    },
    "Java": {
        "description": "Default language support for Java"
    },
    "JavaScript": {
        "description": "Default language support for JavaScript"
    },
    "LaTeX": {
        "description": "Default language support for LaTeX"
    },
    "Lisp": {
        "description": "Default language support for Lisp"
    },
    "Lua": {
        "description": "Default language support for Lua"
    },
    "Makefile": {
        "description": "Default language support for Makefile"
    },
    "Markdown": {
        "description": "Default language support for Markdown"
    },
    "Matlab": {
        "description": "Default language support for Matlab"
    },
    "Objective-C": {
        "description": "Default language support for Objective-C"
    },
    "OCaml": {
        "description": "Default language support for OCaml"
    },
    "Pascal": {
        "description": "Default language support for Pascal"
    },
    "Perl": {
        "description": "Default language support for Perl"
    },
    "PHP": {
        "description": "Default language support for PHP"
    },
    "Python": {
        "description": "Default language support for Python"
    },
    "R": {
        "description": "Default language support for R"
    },
    "Rails": {
        "description": "Default language support for Rails"
    },
    "Regular Expressions": {
        "description": "Syntax highlighting support for <em><b>PCRE</b></em> regular expressions for use in some languages and Sublime Text find panels"
    },
    "RestructuredText": {
        "description": "Default language support for RestructuredText"
    },
    "Ruby": {
        "description": "Default language support for Ruby"
    },
    "Rust": {
        "description": "Default language support for Rust"
    },
    "Scala": {
        "description": "Default language support for Scala"
    },
    "ShellScript": {
        "description": "Default language support for ShellScript"
    },
    "SQL": {
        "description": "Default language support for SQL"
    },
    "TCL": {
        "description": "Default language support for TCL"
    },
    "Text": {
        "description": "Default language support for Plain Text files"
    },
    "Textile": {
        "description": "Default language support for Textile"
    },
    "Vintage": {
        "description": "<b><em>vi</em></b> mode editing package for Sublime Text 3",
        "url": "https://github.com/sublimehq/Vintage"
    },
    "XML": {
        "description": "Default language support for XML"
    },
    "YAML": {
        "description": "Default language support for YAML"
    }
}

# These represent packages we ship metadata for, but these packages are not
# available online and thus they should not have an implicit URL attached to
# them.
_closed_default_packages = [
    "Default",
    "Color Scheme - Default",
    "Color Scheme - Legacy",
    "Language - English",
    "Theme - Default",
    "Vintage",
    "User"
]


###----------------------------------------------------------------------------


def default_metadata(pkg_info):
    """
    Given a PackageInfo instances for a package, return back appropriate meta
    information for that package to be used as a default in case there is not
    a version on disk.
    """
    if pkg_info.is_dependency:
        return dict(_default_dep_metadata)

    if pkg_info.name in _shipped_metadata:
        metadata = dict(_default_pkg_metadata)
        metadata.update(_shipped_metadata.get(pkg_info.name))

        if not pkg_info.has_possible_overrides(simple=False):
            metadata["version"] = "Sublime %s" % sublime.version()

        if pkg_info.name == "User":
            metadata["version"] = "Unversioned"

        if pkg_info.name not in _closed_default_packages:
            metadata["url"] = "https://github.com/sublimehq/Packages"

        return metadata

    return dict(_default_pkg_metadata)


###----------------------------------------------------------------------------
