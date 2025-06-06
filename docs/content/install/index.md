---
title: Installation
description: Installing the OverrideAudit package for Sublime Text
---

# Installing OverrideAudit

OverrideAudit supports Sublime Text on Windows, MacOS and Linux. The only
requirement is Sublime Text with a build number of `4200` or higher; no other
external software or packages are required.

!!! NOTE "Required builds of Sublime Text"

    Version 1.x of OverrideAudit supports builds of Sublime Text 3 prior to
    build 3197 while version 2.x supports Sublime Text builds through to 4199.

    These versions of OverrideAudit are no longer actively supported. Package
    Control will automatically install one of those versions if you're using an
    older build of Sublime Text, but upgrading to the latest version of Sublime
    is recommended.


## Package Control

The fastest and easiest way to install OverrideAudit is via
[Package Control](https://packagecontrol.io){: target="_blank" class="external-link" }, the de-facto
package manager for Sublime Text. Package Control not only installs your
packages for you, it also ensures that they are kept up to date to make sure
that you always have the benefit of the latest bug fixes and features for all
of your installed packages.

To install OverrideAudit using this method, open the command palette in Sublime
(++shift+ctrl+p++ on Windows/Linux or ++shift+cmd+p++ on MacOS) and select the
`Package Control: Install Package` command, then select `OverrideAudit` from the
list of packages presented.

!!! NOTE "OverrideAudit not in the list of packages to install"

    Don't see OverrideAudit in the list? Package Control will not list packages
    that are already installed. You may want to double check your
    *Package Control.sublime-settings* to see if you have already installed
    OverrideAudit previously, or your *Preferences.sublime-settings* to make
    sure it is not in the list of `ignored_packages`.

If you are new to Sublime Text and don't have Package Control installed yet,
you'll have to do that first. More recent builds of Sublime Text 3 have an
option in the `Tools` menu named `Install Package Control...` that will install
Package Control for you, while older versions require you to follow the
installation instructions
[here](https://packagecontrol.io/installation){: target="_blank" class="external-link" }.

!!! NOTE "Can't see menu entry to install Package Control"

    Although only newer builds of Sublime Text include a menu option to install
    Package Control, it is hidden if Package Control is already installed.

!!! WARNING "MacOS issues with installing Package Control"

    If you are using MacOS and installing Package Control does not work for you,
    you are likely running into a known issue with Package Control version 3 on
    this OS. The resolution is to install Package Control 4, which requires some
    manual steps since Package Control does not work for you. Running the
    following code snippet in the Sublime Text console (`View > Show Console`)
    will download and install the latest version:

    ```{.python .word-wrapped}
    from urllib.request import urlretrieve; urlretrieve(url="https://github.com/wbond/package_control/releases/latest/download/Package.Control.sublime-package", filename=sublime.installed_packages_path() + '/Package Control.sublime-package')
    ```

    Alternatively:

    1. Download the latest Package Control release from the repo mentioned above
    2. Rename the downloaded file to `Package Control.sublime-package` (the file
       you downloaded will have an extra `.` instead of a space in it)
    3. In Sublime, choose `Sublime Text > Preferences > Browse Packages`
    4. In Finder, go up one level and into the `Installed Packages` folder
    5. Move your downloaded and renamed package file into this folder


## Manual Installation

If you're unable to use Package Control to install OverrideAudit, it's also
possible to perform a manual installation by cloning the package source from
its [GitHub repository](https://github.com/OdatNurd/OverrideAudit){: target="_blank" class="external-link" }
into your local `Packages` directory, which you can locate by selecting the
`Browse Packages` command from the command palette or from the `Preferences`
menu.

This method of installation is more complicated and requires that you have a
knowledge of `git` and how to use it in order to install the package.

!!! WARNING "Beware of manual installation"

    If you install OverrideAudit manually, it will be up to you to ensure that
    you check for and install any upgrades that may exist to ensure that your
    version of the package is up to date.

    For this reason, it is highly recommended that you **not** install manually
    unless you have a compelling reason or need to do so.


## First Steps

The first thing that OverrideAudit does when it is installed is perform a
background scan to see if you have any
[expired overrides](../terminology/overrides.md#expired-override) that you might
need to worry about. A similar check is done every time Sublime Text is updated
and when Package Control updates or installs a package.

If any expired overrides are found, a
[report](../reports/override.md) will be created to tell
you what they are so that you can take the
[appropriate action](../usage/workflow.md). This
might involve making changes to your override, deleting it or just indicating
that it is OK as it is.

For many users, these automated checks and the tools that OverrideAudit
provides to help you deal with them may be all that you need.


!!! WARNING "Upgrades OverrideAudit can't track"

    OverrideAudit does not perform this check for any package upgrades you
    perform manually or for upgrades which happen while Sublime Text is not
    running. In these cases, you may want to run the check manually. See the
    [Report Page](../reports/index.md) for more information.
