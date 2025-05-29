import sublime


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
        "description": """
        Default Sublime Text functionality that is not provided by the
        underlying application core
        """
    },
    "Theme - Default": {
        "description": """
        Default and Adaptive application themes for Sublime Text 3
        """
    },
    "Color Scheme - Default": {
        "description": """
        Default color schemes that ship with Sublime Text 3
        """
    },
    "Color Scheme - Legacy": {
        "description": """
        Legacy color schemes; these used to be in <em><b>Color Scheme -
        Default</b></em> in older versions of Sublime Text but have now been
        officially deprecated. Color schemes in this package may not take
        advantage of new syntax highlighting improvements
        """
    },
    "Language - English": {
        "description": """
        Provides tspell checking dictionaries for the English language
        """
    },

    # This package is "special" but does not directly ship with Sublime and
    # instead is automatically created at first startup.
    "User": {
        "description": """
        Your User-specific key bindings, preferences and plugins are stored
        in this package. Packages you have installed may also store other data
        here as well.
        """
    },


    # These packages ship with Sublime and provide language support (syntax,
    # completions, etc) for core languages and file types.
    "ActionScript": {
        "description": "Support for working with ActionScript"
    },
    "AppleScript": {
        "description": "Support for working with AppleScript"
    },
    "ASP": {
        "description": "Support for working with ASP"
    },
    "Binary": {
        "description": "Support for distinguishing Binary files from Text files"
    },
    "Batch File": {
        "description": "Support for working with Batch Files"
    },
    "C#": {
        "description": "Support for working with C#"
    },
    "C++": {
        "description": "Support for working with C and C++"
    },
    "Clojure": {
        "description": "Support for working with Clojure"
    },
    "CSS": {
        "description": "Support for working with CSS"
    },
    "D": {
        "description": "Support for working with D"
    },
    "Diff": {
        "description": "Support for comparing files via the side bar"
    },
    "Erlang": {
        "description": "Support for working with Erlang"
    },
    "Git Formats": {
        "description": """
        Support for working with <em><b>git</b></em> files and output (commit
        messages, logs, etc)
        """
    },
    "Go": {
        "description": "Support for working with Go"
    },
    "Graphviz": {
        "description": "Support for working with Graphviz"
    },
    "Groovy": {
        "description": "Support for working with Groovy"
    },
    "Haskell": {
        "description": "Support for working with Haskell"
    },
    "HTML": {
        "description": "Support for working with HTML"
    },
    "JSON": {
        "description": "Support for working with JSON"
    },
    "Java": {
        "description": "Support for working with Java"
    },
    "JavaScript": {
        "description": "Support for working with JavaScript"
    },
    "LaTeX": {
        "description": "Support for working with LaTeX"
    },
    "Lisp": {
        "description": "Support for working with Lisp"
    },
    "Lua": {
        "description": "Support for working with Lua"
    },
    "Makefile": {
        "description": """
        Support for working with <em><b>make</b></em> and Makefiles
        """
    },
    "Markdown": {
        "description": "Support for working with Markdown"
    },
    "Matlab": {
        "description": "Support for working with Matlab"
    },
    "Objective-C": {
        "description": "Support for working with Objective-C and Objective-C++"
    },
    "OCaml": {
        "description": "Support for working with OCaml"
    },
    "Pascal": {
        "description": "Support for working with Pascal"
    },
    "Perl": {
        "description": "Support for working with Perl"
    },
    "PHP": {
        "description": "Support for working with PHP"
    },
    "Python": {
        "description": "Support for working with Python"
    },
    "R": {
        "description": "Support for working with R"
    },
    "Rails": {
        "description": "Support for working with Rails"
    },
    "Regular Expressions": {
        "description": """
        Syntax highlighting support for <em><b>PCRE</b></em> regular
        expressions. This is used in Sublime Text find panels as well as in
        some of the language packages that also ship with Sublime.
        """
    },
    "RestructuredText": {
        "description": "Support for working with RestructuredText"
    },
    "Ruby": {
        "description": "Support for working with Ruby"
    },
    "Rust": {
        "description": "Support for working with Rust"
    },
    "Scala": {
        "description": "Support for working with Scala"
    },
    "ShellScript": {
        "description": """
        Support for working with shell scripts (<em><b>generic</b></em> as well
        as <em><b>bash</b></em>)
        """
    },
    "SQL": {
        "description": "Support for working with SQL"
    },
    "TCL": {
        "description": "Support for working with TCL"
    },
    "Text": {
        "description": "Support for working with Plain Text files"
    },
    "Textile": {
        "description": "Support for working with Textile"
    },
    "TOML": {
        "description": "Support for working with TOML files"
    },
    "Vintage": {
        "description": "<b><em>vi</em></b> mode editing package for Sublime Text 3",
        "url": "https://github.com/sublimehq/Vintage"
    },
    "XML": {
        "description": "Support for working with XML"
    },
    "YAML": {
        "description": "Support for working with YAML"
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
        metadata.update(_shipped_metadata.get(pkg_info.name, {}))

        if not pkg_info.has_possible_overrides(simple=False):
            metadata["version"] = "Sublime %s" % sublime.version()

        if pkg_info.name == "User":
            metadata["version"] = "Unversioned"

        if pkg_info.name not in _closed_default_packages:
            metadata["url"] = "https://github.com/sublimehq/Packages"

        return metadata

    return dict(_default_pkg_metadata)


###----------------------------------------------------------------------------
