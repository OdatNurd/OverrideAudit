OverrideAudit
=============

---

**NOTE:** This package is still under active development, so things are still
in a state of flux and not all features are currently present. I endeavor not
to push any breaking changes but it is entirely possible that commands or their
operation may slightly change out from under you.

Suggestions/improvements are also quite welcomed!

---

OverrideAudit is a plugin for Sublime Text 3 which helps you detect and work
with your package overrides. This allows you to easily see a list of files that
you are overriding, see what changes you have made, and provide warnings to you
when the file you are overriding has been changed.

---

## Installation ##

### Package Control ###

The best way to install the plugin is via PackageControl, as this will take
care of ensuring that the plugin is kept up to date without your having to do
anything at all.

OverrideAudit is currently not listed in Package Control because it's not
officially released yet. In order to install via Package Control, open the
Command Palette and select the command `Package Control: Add Repository` and
then paste in the URL to this repository (https://github.com/OdatNurd/OverrideAudit).

Once this is done, you will be able to install the package via the command
palette using the command `Package Control: Install Package` and searching for
`OverrideAudit`.

<!--
To install via Package Control, open the Command Palette and select the command
`Package Control: Install Package` and search for `OverrideAudit`.
-->

### Manual Installation ###

In order to manually install the package, clone the repository into your
Sublime Text `Packages` directory. You can locate this directory by choosing
`Preferences > Browse Packages...` from the menu.

Manual installation is not recommended for most users, as in this case you are
responsible for manually keeping everything up to date. You should only use
manual installation if you have a very compelling reason to do so and are
familiar enough with the process to know how to do it properly.

---

## Usage ##

OverrideAudit commands can be executed via the Command Palette or via the menu,
using options under the `Tools > OverrideAudit` sub-menu. The available commands
are:

### `OverrideAudit: List Installed Packages` ###

This will display a list of all packages currently installed in Sublime Text,
in a table format. The table lists the packages in roughly the order that they
will be loaded by Sublime at startup.

For each package, an indication is made as to whether this package is
`[S]`hipped, `[I]`nstalled or `[U]`npacked. Additionally, a package that is
currently disabled is displayed in `[Square Brackets]` while a package that
represents a dependency for an installed package is displayed in `<Angle
Brackets>`.

### `OverrideAudit: List Package Overrides` ###

This will display a list of all packages that have any overrides, listing all
of the files that are overridden.

The list of overrides prefixes each package with a shorter version of the flags
that indicate it's type (*Shipped*, *Installed* or *Unpacked*) and lists both
*Simple* as well as *Complete* overrides.

### `OverrideAudit: Diff Package Overrides` ###

This will display a quick panel that lists all packages with at least one
*Simple* override, and allows you to compare the differences between the base
file and your override to see what is different between the two.

The diff output is displayed as a Unified Diff.

---

## Configuration ##

The following configuration options are available for OverrideAudit. You can
see the default settings as well as your own custom settings under the
`Preferences > Package Settings > Override Audit` menu entries. On MacOS, the
`Preferences` menu is under `Sublime Text` in the menu.

### `reuse_views`: true/false (Default: true)###

OverrideAudit generally creates an output view to show you the results of
operations. When this option is enabled (the default), OA will try to find the
view created last time and reuse it for the new command. When disabled, a new
view is created every time.

### `clear_existing`: true/false (Default: true) ###

When `reuse_views` is enabled (the default), this controls whether a reused
view is cleared of its contents prior to executing the command or if the new
output is appended to the end of the existing view.

Some OverrideAudit commands may ignore this setting.

### `ignore_overrides_in`: Array (Default: []) ###

This is an optional list of package names which should be excluded from commands
that show/calculate override information. The format of this option is the same
as the `ignored_packages` Sublime setting.

This does not affect packages displayed in the general package list; it only
hides packages from lists that exclusively show packages with overrides.

### `diff_context_lines`: Number (Default: 3) ###

When displaying a diff for an override, this specifies how many unchanged lines
before and after each difference are displayed to provide better context for
the changes.

---

## Terminology ##

The following terms are used in the documentation, and are described here for
those not familiar with how Sublime Text 3 works with and uses packages.

### Packed Package ###

A *Packed* package is a package that is contained in a `sublime-package` file.
This is actually just a `zip` file with a different extension. The name of the
package file provides the name of the package itself.

This is a convenient way to install a package because all of the files and
resources that make up the package are contained in a single file.

> The package file `Python.sublime-package` is a packed package that provides
> the contents of the `Python` package, which provides support for writing
> Python programs in Sublime Text.

### Unpacked Package ###

An *Unpacked* package is a package that is stored as files in a subdirectory of
the the Sublime Text `Packages` directory, which is accessible from within
Sublime by selecting `Preferences > Browse Packages...` from the menu. The name
of the package comes from the name of the directory the package is stored in.

> The contents of the directory `Packages\User` are considered to be the
> contents of a package named `User`

### Shipped Package ###

A *Shipped* Package is a *Packed* package that ships with Sublime Text itself.
These packages provide the core functionality of Sublime Text itself, and are
stored in a special location alongside the Sublime executable.This makes them
common to all users of Sublime on the same computer.

> The shipped package `Default.sublime-package` provides the set of default key
> bindings, settings, menu entries and so on that all other plugins modify.

### Installed Package ###

An *Installed Package* is a *Packed* package that is stored in the `Installed
Packages` directory, which is one directory level above the `Packages`
directory used to store *Unpacked* packages.

Please note that this does not mean that an *Unpacked* package is in some way
***not*** installed; the terminology is purely meant to make a distinction
between packages that are installed in a specific format and location.

> `Package Control` is installed as an **Installed Package**, and many packages
> that it installs are also installed in this manner.

### Override ###

An *Override* is a file or files which override similarly named files contained
in a package. When an override is in effect, Sublime will ignore the original
packaged version of the file and use the override file in its place.

This can be used to modify package behaviour to your liking, but is dangerous in
that if the packaged version of the file is modified by the package author, the
override will continue to mask those changes and improvements.

Detecting when this is happening is one of the core features of OverrideAudit.

### Simple Override ###

A *Simple* override is the most common type of override, in which a package is
partially unpacked and then modified. This means that there is a directory in
the Sublime `Packages` directory named the same as an existing *Shipped* or
*Installed* package which contains files of the same names as those within the
`sublime-package` file.

> The file `Packages\Python\Python.sublime-build` is a simple override which
> causes Sublime to ignore the *Shipped* version of the file from the `Python`
> package, allowing you to modify how Python is built.

### Complete Override ###

A *Complete* override is less common than a *Simple* override. This variety of
override occurs when a *Packed* package with the same name as a *Shipped*
package is installed into the `Installed Packages` folder. When this happens,
Sublime will ignore the shipped version of the package and use the other version
instead, as if it was the package that was shipped with Sublime.

> The File `Installed Packages\Python.sublime-package` is a complete override of
> the *Shipped* `Python` package. As far as Sublime is concerned, this is the
> `Python` package that provides all functionality for this language.

---

## License ##

Copyright 2017 Terence Martin

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
