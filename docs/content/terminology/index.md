---
title: Terminology
description: Terminology in OverrideAudit
---

This page describes the terms that you will find used throughout the
OverrideAudit documentation.

This is meant to be a high level overview of these terms. If you're not
familiar with what packages and overrides in Sublime Text are, the
[overrides](overrides.md) page contains more detailed information on these topics.

## Packages

---


### Packed Package

A *Packed* package is a package that is contained in a `sublime-package` file.
This is actually just a `zip` file with a different extension. The name of the
package file provides the name of the package itself.

This is a convenient way to install a package because all of the files and
resources that make up the package are contained in a single file.

> The package file `Python.sublime-package` is a packed package that provides
> the contents of the `Python` package, which provides support for writing
> Python programs in Sublime Text.


### Unpacked Package

An *Unpacked* package is a package that is stored as files in a subdirectory of
the the Sublime Text `Packages` directory, which is accessible from within
Sublime by selecting `Preferences > Browse Packages...` from the menu or from
the `Command Palette`. The name of the package comes from the name of the
directory the package is stored in.

> The contents of the directory `Packages\User` are considered to be the
> contents of a package named `User`


### Shipped Package

A *Shipped* Package is a *Packed* package that ships with Sublime Text itself.
These packages provide the core functionality of Sublime Text, and are stored
in a special location alongside the Sublime executable.This makes them common
to all users of Sublime on the same computer.

> The shipped package `Default.sublime-package` provides the set of default key
> bindings, settings, menu entries and so on that all other packages modify.


### Installed Package

An *Installed* Package is a *Packed* package that is stored in the
`Installed Packages` directory, which is one directory level above the
`Packages` directory used to store *Unpacked* packages.

Please note that this does not mean that an *Unpacked* package is in some way
**not** installed; the terminology is purely meant to make a distinction
between packages that are installed in a specific format and location.

> `Package Control` is installed as an **Installed Package**, and many packages
> that it installs are also installed in this manner.


## Overrides

---

### Override

An *Override* is a file or files which override similarly named files contained
in a package. When an override is in effect, Sublime will ignore the original
packaged version of the file and use the override file in its place.

This can be used to modify package behaviour to your liking, but is dangerous
in that if the packaged version of the file is modified by the package author,
the override will continue to mask those changes and improvements.

Detecting when this is happening is one of the core features of OverrideAudit.


### Simple Override

A *Simple* override is the most common type of override, in which a package is
partially unpacked and then modified. This means that there is a directory in
the Sublime `Packages` directory named the same as an existing *Shipped* or
*Installed* package which contains files of the same names as those within the
`sublime-package` file.

> The file `Packages\Python\Python.sublime-build` is a simple override which
> causes Sublime to ignore the *Shipped* version of the file from the `Python`
> package, allowing you to modify how Python is built.


### Complete Override

A *Complete* override is less common than a *Simple* override. This variety of
override occurs when a *Packed* package with the same name as a *Shipped*
package is installed into the `Installed Packages` folder. When this happens,
Sublime will ignore the shipped version of the package and use the other
version instead, as if it was the package that was shipped with Sublime.

> The File `Installed Packages\Python.sublime-package` is a *Complete* override
> of the *Shipped* Python package. As far as Sublime is concerned, this is the
> `Python` package that provides all functionality for this language.


### Expired Override

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


### Unknown Override

This terminology is unique to OverrideAudit, and is used to indicate that there
are files in an *Unpacked* package folder that do not exist in the *Packed*
version of the package.

Such a file is not technically an override (as it is not overriding anything)
but is still considered a part of the package by Sublime Text nonetheless.
Overrides of this type may be the result of adding additional files to the
package or the result of file that were previously overridden being removed
from the Shipped version of the package.

The [Override Report](../reports/override.md) and
[Bulk Diff Report](../reports/bulkdiff.md) can display overrides of this type
in that report via the
[ignore_unknown_overrides](../config/settings.md#ignore_unknown_overrides)
setting (the default is to enable this feature) to give you an indication of
when this is happening. This can act as a reminder that new files have been
added to the package or that overrides exist which may no longer be needed
because the source package has removed the file.
