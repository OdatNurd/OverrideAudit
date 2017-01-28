OverrideAudit
=============

OverrideAudit is a plugin that helps you detect and work with overrides you
have created for installed packages, allowing you to determine when your
override is out of date and needs to be updated.

Additional tools are provided to allow you to perform other tasks, such as to
detect what overrides you have in place, compare your override to the
underlying package file, temporarily enable and disable your override and more.

---

**NOTE:** This package is still under development and not at all ready for
prime time, including not being suitable for any particular purpose.

---

<!--
Installation
============

Package Control
---------------

The best way to install the plugin is via PackageControl, as this will take
care of ensuring that the plugin is kept up to date without your having to do
anything at all.

To install via Package Control, open the Command Palette and select the command
`Package Control: Install Package` and search for `OverrideAudit`.

Manual Installation
-------------------

In order to manually install the package, clone the repository into your
Sublime Text `Packages` directory. You can locate this directory by choosing
`Preferences > Browse Packages...` from the menu.

Manual installation is not recommended for most users, as in this case you are
responsible for manually keeping everything up to date.
-->

Terminology
-----------

The following terms are used throughout the remainder of this document:

### Packed Package ###

This refers to a package which has been distributed as a `sublime-package` file
(a `zip` file with a different extension). The packages that ship with Sublime
Text to provide core functionality are distributed in this format, and this is
the format that PackageControl usually uses to install a package.

### Unpacked Package ###

This refers to a directory which exists inside of the Sublime Text `Packages`
directory that contains the contents of the package. As some packages contain
files which cannot be used while packed inside of a `sublime-package` file
(e.g. a shared library of some sort), PackageControl may sometimes install a
package in this manner.

Packages that you manually installed via a source control operation such as
`git` are also unpacked files.

### Shipped Package ###

A shipped package is a package that is distributed with Sublime Text directly
and which provides the core functionality of the application. These packages
are installed as Packed packages and are stored in an OS specific location that
is not directly exposed to you.

### Installed Package ###

For the purposes of OverrideAudit, an Installed Package is any installed
package that is contained inside of a `sublime-package` file that is **not** a
Shipped Package.

This means that either PackageControl installed the package for you (and did
not unpack it), or you manually installed the package yourself as a
`sublime-package` file.

Installed Packages are stored in a folder named `InstalledPackages` that is one
directory level above the `Packages` directory, and can be reached by selecting
`Preferences > Browse Packages...` from the menu and going up a level in the
directory hierarchy.

<!--
Usage
-----

All of the functionality of OverrideAudit is exposed via commands in the
Command Palette. It is also possible to configure OverrideAudit to run some
checks for you automatically as a "set it and forget it" mechanism to help you
keep up to date (see Configuration below).

### OverrideAudit: Check expired overrides ###

This command will run a check to see if you have any expired overrides, and
warn you with a dialog popup if you do.

An expired override is an override either on a single file within a package or
on a package as a whole in which the file/package you are overriding is newer
than your override file.

This is an indication that the underlying package has changed and your override
is now out of date. Although this is technically safe, an override of this type
is potentially masking fixes or augmentations to the underlying package that
you will not see. -->

Configuration
-------------

The following configuration options are available for OverrideAudit:

### `reuse_views`: *true/false ###

OverrideAudit generally creates an output view to show you the results of
operations. When this option is enabled (the default), OA will try to find the
view created last time and reuse it for the new command. When disabled, a new
view is created every time.

### `clear_existing`: *true/False ###

WHen `reuse_views` is enabled (the default), this controls whether a reused
view is cleared of its contents prior to executing the command or if the new
output is appended to the end of the existing view.

Some OverrideAudit commands may ignore this setting.

<!--
#### `oa_startup_check`: *true/false ###

When enabled (the default), OverrideAudit will perform a check for out of date
overrides whenever Sublime text starts.

#### `oa_scheduled_check`: true/*false ###

When enabled, OverrideAudit will perform a check for out of date overrides once
per hour while Sublime Text is running. This is handy if you often have a long
running Sublime Text session.

This option is disabled by default.

#### `os_upgrade_check`: *true/false ###

When enabled (the default), OverrideAudit will perform a check for out of date
overrides whenever Sublime Text starts after an upgrade/downgrade (the build
number of sublime text changes).

This operates as `oa_startup_check` does, except that even if that option is
disabled, the check will still be performed.

This allows you to ensure that no matter what, you are notified of out of date
overrides after an upgrade to Sublime Text. -->
