---
title: Overrides
description: Information on Overrides
---

# Introduction

One of the great things about Sublime Text is how customizable it is. Along
with things like customizing your settings and key bindings, you can add almost
any functionality you might want. Using
[Package Control](https://packagecontrol.io){: target="_blank" class="external-link" }
you can find and install a vast array of third party packages to add features
that make Sublime Text uniquely your own.

Sometimes though, a package does not quite meet your needs and a little
tweaking is in order to get things just right. Thankfully, Sublime is open
enough to allow you to easily tinker with installed packages to get things
running the way you like through the use of package overrides.

Although powerful, there are some common pitfalls that you might fall into
while using them. On it's own, Sublime doesn't provide any direct support for
working with your package overrides at all, leaving you to manage them
yourself. Enter OverrideAudit.

OverrideAudit strives to fill in a missing Sublime Text functionality gap by
helping you to manage your overrides. With it you can track the overrides you
have made and see how they're different from the file that they are replacing.
It can help you to edit them when you need to make changes or get rid of them
when you no longer need them.

Most importantly, it can help to keep you informed when there are potential
problems that you should take a look at, to help you from falling into those
nasty pitfalls.


## What are Overrides

In the simplest terms, an `override` is a file or (more rarely) a complete
package that you create to be used as a modification to an existing package.
Instead of manually unpacking, editing and repackaging a package file, Sublime
Text will treat your override file as if it was contained inside of the target
package. This saves you the hassle of editing the contents of the package
directly.

Overrides are an important aspect to package customization because both Sublime
Text and Package Control will replace a package as a whole when performing
updates, thus discarding your changes. You could get around this by disabling
updates, but this leaves you potentially using older, more outdated packages.
Making changes directly to a package file is a recipe for confusion and is thus
not a good idea.


## Creating an Override

In order to override files in a package, that package must be installed as a
`sublime-package` file. This is how all packages that ship with Sublime itself
are installed, as well as most packages installed by Package Control.

As noted below, there are two different styles of overrides that you can create
in Sublime Text, a [simple](index.md#simple-override) override and a
[complete](index.md#complete-override)
override. By far the most common type for most users is a simple override.

The easiest way to create a simple override is by using OverrideAudit's
[Create Override](../usage/commands.md#create-override) command to select the
resource you want to override. If you've used` View Package File` from the
Command Palette, you can use the
[Override Current Resource](../usage/commands.md#override-current-resource)
command instead.


## Common Pitfalls

Sublime loads override files transparently and silently; there is no warning or
message generated that lets you know that part of a package has been
overridden.

Now imagine that behind the scenes, the author of such a package fixes some
bugs and releases a new version. After your copy of the package is updated,
you're left with an override file that is still based on the older version of
the package; your override has [expired](index.md#expired-override), but you
don't know it.

The best case here is that the file you are overriding was not modified at all,
while the worst case is that because your file is too old, the package does not
work any longer, or may not even fully load. These can be very tricky problems
to diagnose if you're not aware of what's going on.

Overrides are very powerful and necessary; many useful customizations that
users want to make to get packages to work to their liking can only be
performed by creating an override. Overrides are safe as long as you know that
they exist and track what's going on.

OverrideAudit is designed to help keep you informed of potential problems,
taking the worry out of customizing Sublime to your heart's content so that
you're free to get on with your work.


## Packages

In Sublime Text, a `Package` is simply a named collection of resource files
that are grouped together to make some kind of modification or extension to
Sublime. There are a number of different types of resource files that a package
can include, ranging from as simple as an additional key bindings all the way
to custom python code for implementing entirely new features.

Most of the functionality that is provided by default in Sublime is provided by
a set of `Default Packages` that ship with Sublime itself, and that list of
packages is augmented by third party packages that you choose to install.

Regardless of their content, packages in Sublime text can be installed in two
different ways, `Packed` and `Unpacked`.


### Packed Packages

A `Packed` package is a collection of files grouped together into a single
archive file, which makes them easier to share and install. This is important
for mechanisms such as [Package Control](https://packagecontrol.io){: target="_blank" class="external-link" },
which help to install new packages and keep them up to date, and is also the
format in which the packages that ship with Sublime (`Shipped Packages`) are
distributed.

A Packed package is actually a `zip` file with the extension changed to
`sublime-package`. This type of package is used by Sublime for the default packages that
it ships with, and is the preferred method for package installation via Package
Control as well.

Since a package upgrade will replace the entire package as a whole, it is
unwise to make modifications to a package by modifying it directly, since your
changes will be lost on package update.

Packages you have installed in this manner are placed inside of the
`Installed Packages` folder, which is stored in a location that is specific to you. You can
find this location by selecting the `Preferences: Browse Packages` command from
the menu or command palette and then going up a level to the parent folder.

`Shipped Packages` are not stored in this location, since a single copy of them
is used as the base for all users on the current computer.


### Unpacked Packages

Occasionally it is not possible for a package to be installed in a packed
format. For example, it may contain platform specific libraries or binaries
that cannot be accessed while they are inside of the packed package file.

For packages such as this, Sublime also supports a package installation method
known as an `Unpacked` package. This style of package is stored as a collection
of files in a folder inside of the `Packages` folder.

As with the `Installed Packages` folder, the location of this folder is specific
to you. You can find this location by selecting the
`Preferences: Browse Packages` command from the command palette or the main
menu.

Most notably, all of your customized settings and key bindings are stored in an
unpacked package named `User` inside of this folder.


## Override Types

There are two main types of overrides in Sublime Text,
[Simple](index.md#simple-override) and
[Complete](index.md#complete-override),
with the Simple override being the most common type of override for most users.
In the [terminology](index.md) of OverrideAudit, there are also
[expired](index.md#expired-override) and
[unknown](index.md#unknown-override) overrides, which are specific cases of
`simple` overrides.

Regardless of the type of an override, it still shares the same set of
pitfalls, in that Sublime uses them unconditionally without telling you that it
is doing so or that you might need to update them.


### Simple Override

A `Simple` override is the most common type of override, and allows you to
override the complete contents of a single file within a `Packed` package
without modifying the package itself. This ensures that your changes will
remain in place even if the package you are overriding is updated by its
author.

To create such an override, create an `Unpacked` folder for the package inside
the `Packages` folder, extract the file you wish to modify from the sublime-
package file into that folder, and change it as desired.

While loading the `sublime-package` file, Sublime will ignore the file from the
package file and use the unpacked file instead. This is transparent to you;
sublime doesn't provide any indication that an override file is being used.

 This works not only for default packages, but also user installed packages and
packages which have been completely overrridden (see below).


### Complete Override

A `Complete` override is less common and allows you to override the entire
contents of one of the packages that ship with Sublime all at once. The most
common use case for this is to update one of the shipped packages with a newer
version, allowing you to pick up bug fixes in the default packages in between
Sublime releases.

To create such an override, you place a `sublime-packag`e file with the same
name as one of the default packed in the `Installed Packages` folder. When
loading packages, when Sublime encounters such a package file, it will
completely ignore the shipped version and use the overridden version instead.

Like a `Simple` override, a complete override is transparent to you.


### Expired Override

As outlined in the different types of overrides above, when an override is in
place Sublime uses it automatically, with no warnings or indications that it is
happening. If the source package is updated, your override will remain in
effect even though it is possible that the underlying file has been modified.

In this specific case, we say that this override has `Expired`; the source file
is newer than the override file itself, and so some changes may have been made
that you should include into your override. Detecting this situation and
helping you deal with it is one of the main reasons that OverrideAudit was
created.

In the case of a `Simple` override, the override is considered to be expired if
the time stamp of the file inside of the `sublime-package` file is newer than
the last modification time of the override file. For a `Complete` override, the
time stamps of the two package files themselves are compared.

!!! WARNING "ZIP file format limitations"

    The format of a `zip` file includes a modification time for each file in the
    archive, but due to technical limitations, this time does not include any
    time zone information.

    For this reason, the detection of an expired `Simple` override is not
    completely foolproof, although it is unlikely to be a problem in most
    cases.


### Unknown Override

A file in an *Unpacked* package is only considered to be an override if an
identically named file also exists in the *Packed* version of that package; that
is, such a file is `overriding` the content of the package.

It's possible for files to appear in the *Unpacked* version of a package without
also existing in the *Packed* version as well. In this case Sublime still treats
that file as if it was a part of the package, but technically speaking it's not
an override because it's not overriding anything.

OverrideAudit refers to files of this type as *Unknown Overrides* to create a
distinction between them and actual override files. This distinction is
important because OverrideAudit has no way to know why such a file might exist.

Potential reasons for these sort of files range from you manually adding extra
package files on purpose (say to extend the functionality of a package) to the
`sublime-package` version of the file being updated to a new version that no
longer has such a file within it.

Although the first case is intentional, the second may not be and could be an
indication that a file that used to be overridden is no longer present, which
could mean that such a file is no longer needed or that its presence will have
unforeseen consequences on the operation of the package.

!!! NOTE

    The {{ setting("ignore_unknown_overrides") }} setting controls whether
    unknown overrides will be displayed by the
    [Override Report](../reports/override.md) and
    [Bulk Diff Report](../reports/bulkdiff.md) or not.

    The default is to display these files as an extra warning to you, but you
    can disable this if desired.
