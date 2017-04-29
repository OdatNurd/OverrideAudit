OverrideAudit
=============

OverrideAudit is a package for Sublime Text 3 that helps you detect and work
with your package overrides, allowing you to easily see a list of files that
you are overriding, see what changes your override provides, and most
importantly to  provide warnings to you when the file you are overriding has
been changed by its author so you can determine what course of action to take.

If you're new to OverrideAudit, there is an [introductory video](https://www.youtube.com/watch?v=qYeli46frR8)
available which shows some of the key features.

-------------------------------------------------------------------------------


## Installation ##

### Package Control ###

The best way to install the package is via PackageControl, as this will take
care of ensuring that the package is kept up to date without your having to do
anything at all.

To install via Package Control, open the Command Palette and select the command
`Package Control: Install Package` and search for `OverrideAudit`.


### Manual Installation ###

In order to manually install the package, clone the repository into your
Sublime Text `Packages` directory. You can locate this directory by choosing
`Preferences > Browse Packages...` from the menu.

Manual installation is not recommended for most users, as in this case you are
responsible for manually keeping everything up to date. You should only use
manual installation if you have a very compelling reason to do so and are
familiar enough with the process to know how to do it properly.


-------------------------------------------------------------------------------


## Usage ##

OverrideAudit provides a series of commands to help you discover and inspect
the package overrides that you currently have in place, see what is different
between your override and the underlying package file, and most importantly the
ability to detect when the file you are overriding has been updated by its
author.

In addition to manually executing commands, OverrideAudit tries to keep you
protected from *expired* overrides by
[automatically checking](#automatic-reports-of-expired-overrides) for them
every time you upgrade Sublime Text or a package.

OverrideAudit commands may be executed via the Command Palette as well as via
the menu using options under the `Tools > OverrideAudit` sub-menu. In addition,
some commands are available as context menu items when you open the context
menu over a package name or override name in a report, or over a report in
general.

Some commands, such as the ability to "freshen" an expired override, are only
available via context menu items so that you can directly target them at the
package or override that you are interested in.

The following lists the available commands as seen in the Command Palette; the
menu items are similarly named.


### `OverrideAudit: Package Report` ###

This will display a list of all packages currently installed in Sublime Text,
in a table format. The table lists the packages in roughly the order that they
will be loaded by Sublime at startup.

For each package, an indication is made as to whether this package is
`[S]`hipped, `[I]`nstalled or `[U]`npacked (see the [terminology](#terminology)
section for more information).

Additionally, a package that is currently disabled is displayed in `[Square
Brackets]` while a package that represents a dependency for an installed
package is displayed in `<Angle Brackets>`.

Each package name supports a context menu item which allows you to open a bulk
diff report for that package, allowing you to quickly get an overview of the
status of any overrides on that package. See the `OverrideAudit: Bulk Diff
Single Package` command for more information.


### `OverrideAudit: Override Report` ###

This will display a list of all packages for which there are overrides of any
type, *simple* or *complete*, with an indication on any package or override
file that is currently *expired* (see the [terminology](#terminology) section
for more information on these terms).

For each package displayed, a condensed version of the indicators from the
`Package Report` are displayed, indicating whether the package in question is
`[S]`hipped, `[I]`nstalled or `[U]`npacked.

A package which is a *complete* override is indicated by text to this effect
appearing next to it in the output line. If such a package is *expired*, an
additional note to this effect is added to let you know.

All *simple* overrides for a package are displayed below the package name in
the report, and may be prefixed with a `[X]` mark if they are currently
*expired*.

As with the `Package Report`, a context menu item is presented on package names
to allow a quick bulk diff of overrides in that package. Additionally, override
filenames include context commands to allow you to quickly edit, diff or delete
that override.


### `OverrideAudit: Override Report (Only expired)` ###

This command operates the same as the standard `Override Report` command, but
constrains its output to **only** packages which have some form of expired
override (either *simple* or *complete*).

This allows you to focus solely on those overrides which may require your more
immediate attention.


### `OverrideAudit: Diff Single Override` ###

This will display a quick panel that lists all packages with at least one
*simple* override, and allows you to compare the differences between the base
file and your override to see what is different between the two.

When the content of the file is different, the output is displayed in a Unified
Diff format in a new buffer, allowing you to inspect the changes.

As a shortcut, you can directly diff an override file from any `Override
Report` or existing `Bulk Diff` report.

The option `diff_unchanged` allows you to specify the result of performing a
diff when the override is identical to the underlying file.


### `OverrideAudit: Bulk Diff All Packages` ###

This will generate a diff for every *simple* override that exists for all
packages into a single output report, allowing for a quick overview of all
overrides at once.

As for the *Override Report* command, each package listed has a condensed
version of the indicators from the Package Report indicating whether the
package in question is `[S]`hipped, `[I]`nstalled or `[U]`npacked as well as an
indication if the package is a *complete* override or not. Additionally,
expired *complete* and *simple* overrides are also indicated in the bulk diff
report.

Each section of the report is progressively indented so that it is possible to
use Sublime code folding to hide away parts of the report as you work.

As in the *Override Report*, the name of each package and the filenames of each
override support context menus that allows you to quickly bulk diff, open or
diff them in their own distinct view.


### `OverrideAudit: Bulk Diff Single Package` ###

This command operates identically to the `Bulk Diff All Packages` command, with
the exception that instead of calculating a diff for all overrides in all
packages you are instead prompted via a quick panel for a single package to
diff instead.

You can also access a bulk diff of a single package via a context menu on the
name of a package in a `Package Report`, `Override Report` or a `Bulk Diff`
report.


### `OverrideAudit: Refresh Report` ###

This command is available from within all OverrideAudit report views (`Package
Report`, `Override Report`, or `Bulk Diff`) via the Command Palette, context
menu or main menu, and allows you to quickly re-run the same report.

When a report is refreshed, OverrideAudit ignores the current values of the
`reuse_views` and `clear_existing` options and operates as if they are both set
to `true` so that the existing report will be replaced.

This command is also available as a context menu entry from within a report
view or its associated editor tab and via the <kbd>F5</kbd> key, although you
can change this binding to a key of your liking.


### `OverrideAudit: Swap Diff/Edit View` ###

This command is only available in the Command Palette while the current file is
either an edit session for an override or a diff of an override.

Although this command does not appear in the top level `Tools > OverrideAudit`
menu, it does appear within the context menu of an appropriate file view, as
well as on the context menu of an override file from within an `Override
Report` or `Bulk Diff`.

Additionally, OverrideAudit contains a key binding to the standard Sublime key
for swapping between associated files (<kbd>Alt+O</kbd> on Windows/Linux or
<kbd>&#8984;+Alt+Up</kbd> on MacOS) that operates from within an appropriate
file view.

Regardless of how you trigger the command, any existing edit or diff view for
this override will be switched to directly. In the case of a diff view, the
diff will be recalculated, allowing any *saved* changes to be immediately
reflected. The configuration option `save_on_diff` can be enabled to ensure
that unsaved changes in the file are persisted first, if desired.

This command ignores the current values of the `reuse_view`, `clear_existing`
and `diff_unchanged` settings and operates as if they are set to `true`, `true`
and `diff` respectively in order to ensure that you don't end up with a large
number of duplicate views.


### `OverrideAudit: Delete Override` ###

This command is only available in the Command Palette while the current file is
either an edit session for an override or a diff of an override.

Like the `Swap Diff/Override View` command, this command does not appear in the
top level `Tools > OverrideAudit` menu but does appear within the context menu
of an appropriate file view and on the context menu of an override file from
within an `Override Report` or `Bulk Diff`.

This command will delete the current override after prompting you to verify
that you really mean to delete this file. OverrideAudit attempts to send the
override to the trash using the same internal mechanism that Sublime Text uses
to delete files.

When an override is deleted, any existing edit sessions of the override will
remain open, and Sublime will indicate that they have unsaved changes because
the file is missing.

The configuration setting `confirm_delete` can be set to `false` if you want to
be able to delete overrides without being prompted first.


-------------------------------------------------------------------------------


## Automatic Reports of Expired Overrides ##

Although package overrides are vital to your ability to customize Sublime Text
to your liking, Sublime will not warn you when you are overriding a file that
has been changed since the time you first created the override.

In such a situation, the updated source file is ignored and your override
remains in place, which means that any bug fixes or enhancements that the
original package author has made will be hidden from you and you will never
know it.

In order to help keep you protected from this happening without your realizing
it, OverrideAudit will automatically try to generate a report to tell you if
you have any *expired* overrides when it detects that something has been
updated.

The report generated is an [Override Report](#overrideaudit-override-report)
that contains only information on expired overrides. The report is only
displayed if there are any expired overrides so that OverrideAudit can keep out
of your way if there are no potential problems.

An automated report will be generated in the following circumstances:

 * Whenever you start Sublime Text and the version number has changed from the
   last time you ran it, indicating that you have upgraded Sublime Text to a
   different version.
 * Whenever a package is removed from the list of `ignored_packages` in your
   preferences file. [Package Control](https://packagecontrol.io/) does this
   whenever it is upgrading a package, for example.


-------------------------------------------------------------------------------


## Freshening an Expired Override ##

When an expired override is detected, it's a good idea to check and see what
has changed between the source file and your override, so you can determine if
you need to incorporate any changes into your override or possibly just remove
it entirely if it is no longer needed.

Due to the way that PackageControl updates packages, it is possible for
OverrideAudit to report an override as expired without any actual content
changes being made to the original file.

In these cases, in order to stop the file from being reported as expired, its
time stamp on disk needs to be changed to be more recent than the new package
file. If you're opening your overrides to view their contents, this is as
simple as just re-saving the file.

If you have many overrides, either in a single package or spread across
multiple packages, a better option might be one of the *Bulk Diff* operations,
which  allows you to quickly scan for and see changes and only edit files that
need special attention.

In this case, opening and saving files would quickly become a hassle. For this
reason, OverrideAudit makes available in the context menu a command to
*Freshen* either a single override or all overrides in a package all at once.

By default you are prompted that you want to do this before the command
executes. You can modify the `confirm_freshen` configuration option to stop
this from happening if desired.

The freshen operation updates the last modification time of files to be the
current date so that OverrideAudit knows that everything is up to date.


-------------------------------------------------------------------------------


***NOTE:*** If you upgrade a package manually without adding it to the list of
`ignored_packages` or while Sublime is not running, OverrideAudit will be
unable to detect that anything has changed and will not automatically generate
a report for you.

For this reason, it may be a good idea to manually run this report from the
command palette as a part of your manual package upgrades.


-------------------------------------------------------------------------------


## Configuration ##

The following configuration options are available for OverrideAudit. You can
see the default settings as well as your own custom settings under the
`Preferences > Package Settings > OverrideAudit` menu entries or via the
command palette with `Preferences: OverrideAudit Settings`. On MacOS, the
`Preferences` menu is under `Sublime Text` in the menu.


### `reuse_views`: true/false (Default: true) ###

OverrideAudit generally creates an output view to show you the results of
operations. When this option is enabled (the default), OA will try to find the
view created last time and reuse it for the new command. When disabled, a new
view is created every time.

Some OverrideAudit commands may ignore this setting.


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
hides packages from lists that show packages with overrides, such as the
Override Report or the commands that find and diff overrides.

**NOTE:** Any overrides you create in packages in this list will be masked from
you, so be very careful about what you add to the list.


### `diff_unchanged`: String (Default: "diff") ###

When using the `Diff Single Override` command, this setting controls what
happens when the selected override has no differences from the underlying file.

The possible values of this setting are:

  * `"diff"` to open a tab with the empty diff in it
  * `"ignore"` to ignore the command; the status line will indicate the lack of
    changes
  * `"open"` to open the file for editing, allowing you to see its contents or
    make new modifications.


### `diff_context_lines`: Number (Default: 3) ###

When displaying a diff for an override, this specifies how many unchanged lines
before and after each difference are displayed to provide better context for
the changes.


### `diff_empty_hdr`: Boolean (Default: false) ###

When enabled, this allows you to see the source files and related time stamps
of both files that participated in the diff even when there are no changes to
display.

This applies both to a bulk diff as well as a single file diff, but note that
for a single file diff this option will only have an effect if `diff_unchanged`
is set to `"diff"`, as otherwise no diff is displayed.



### `save_on_diff`: true/false (Default: false) ###

This setting controls whether or not OverrideAudit will make sure any unsaved
changes are persisted to disk when switching from an edit of an override to a
diff of it, so that your changes will be reflected in the diff.

This option has no effect for a buffer with unsaved changes that represents a
file that no longer exists on disk (i.e. you have opened the override and then
deleted it) to ensure that you don't accidentally resurrect a deleted file by
saving it again.


### `confirm_deletion` : true/false (Default: true) ###

When removing files, this setting controls whether OverrideAudit will prompt
you to confirm the deletion before it happens or not.

OverrideAudit uses the `send2trash` library that ships with Sublime Text to
perform file deletions.


### `confirm_freshen` : true/false (Default: true) ###

When freshening expired override files, this setting controls whether
OverrideAUdit will prompt you to confirm the operation before it happens or
not.

Although this operation is not destructive, freshening an expired override will
stop OverrideAudit from warning you that it's expired.


### `binary_file_patterns`: Array (Default: from user settings) ###

This setting is identical to the Sublime Text setting of the same name and
controls what files are considered to be binary for the purposes of performing
a diff operation.

The default value for this operation is taken from your regular Sublime Text
user settings, so you only need to specify a value in the *OverrideAudit*
settings if you want to consider a different set of files binary for the
purposes of diffs.


### `report_on_unignore`: Boolean (Default: true) ###

OverrideAudit can
[automatically generate a report](#automatic-reports-of-expired-overrides) to
check for *expired* overrides every time a package is removed from the
`ignored_packages` list in your *Preferences.sublime-settings* file.

As well as happening when you manually decide to re-enable a package you have
been ignoring, this is also an indication that
[Package Control](https://packagecontrol.io/) has finished upgrading a package.

When enabled, the report will only be shown if any expired overrides are found.


-------------------------------------------------------------------------------


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
> bindings, settings, menu entries and so on that all other packages modify.


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


### Expired Override ###

This terminology is unique to OverrideAudit, and is used to indicate that an
override (either *simple* or *complete*) is overriding a file that has been
updated at the source (e.g. by Sublime text being upgraded or the package
author modifying it).

When this happens Sublime does not warn you on its own, and will continue to
use your overrides, potentially causing you to miss out on important bug fixes
or new features.

The tools in OverrideAudit are designed to help warn you when this is happening
and allow you to easily see what has changed so you can decide how best to
address the situation.


-------------------------------------------------------------------------------


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
