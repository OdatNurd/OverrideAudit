---
title: Installation
description: Installing the OverrideAudit package for Sublime Text
---

# Installing OverrideAudit

OverrideAudit supports Sublime Text on Windows, MacOS and Linux. The only
requirement is Sublime Text with a build number of `4126` or higher; no other
external software or packages are required.

!!! NOTE

    Version 1.x of OverrideAudit supports builds of Sublime Text 3 prior to
    build 3197 while version 2.x supports Sublime Text builds through to 4136.

    These versions are no longer actively supported. Package Control will
    automatically install one of those versions if you're using an older build
    of Sublime Text, but upgrading to the latest version is recommended.


## Package Control

The fastest and easiest way to install OverrideAudit is via
[Package Control](https://packagecontrol.io){: target="_blank" }, the de-facto
package manager for Sublime Text. Package Control not only installs your
packages for you, it also ensures that they are kept up to date to make sure
that you always have the benefit of the latest bug fixes and features for all
of your installed packages.

To install OverrideAudit using this method, open the command palette in Sublime
(++shift+ctrl+p++ on Windows/Linux or ++shift+cmd+p++ on MacOS) and select the
`Package Control: Install Package` command, then select `OverrideAudit` from the
packages.

If you are new to Sublime Text and don't have Package Control installed yet,
you'll have to do that first. More recent builds of Sublime Text 3 have an
option in the `Tools` menu named `Install Package Control...` that will install
Package Control for you, while older versions require you to follow the
installation instructions
[here](https://packagecontrol.io/installation){: target="_blank" }.

!!! NOTE

    Although only newer builds of Sublime Text include a menu option to install
    Package Control, it is hidden if Package Control is already installed.


## Manual Installation

If you're unable to use Package Control to install OverrideAudit, it's also
possible to perform a manual installation by cloning the package source from
its [GitHub repository](https://github.com/OdatNurd/OverrideAudit) into your
local `Packages` directory, which you can locate by selecting the
`Browse Packages` command from the command palette or from the `Preferences`
menu.

This method of installation is more complicated and requires that you have a
knowledge of `git` and how to use it in order to install the package.

!!! WARNING

    If you install OverrideAudit manually, it will be up to you to ensure that
    you check for and install any upgrades that may exist to ensure that your
    version of the package is up to date.

    For this reason, it is highly recommended that you **not** install manually
    unless you have a compelling reason or need to do so.


## After Installation

The first thing that OverrideAudit does when it is installed is perform a
background scan to see if you have any [expired overrides](garbage) that you
might need to worry about. A similar check is done every time Sublime Text is
updated and when Package Control updates or installs a package.

If any expired overrides are found, a [report](garbage) will be created to tell
you what they are so that you can take the [appropriate action](garbage). This
might involve making changes to your override, deleting it or just indicating
that it is OK as it is.

For many users, these automated checks and the tools that OverrideAudit
provides to help you deal with them may be all that you need.


!!! WARNING

    OverrideAudit does not perform an automatic search for any package upgrades
    you perform manually or while Sublime Text is not running. In these cases,
    you may want to run the check manually. See the [Report Page](garbage) for
    more information.
