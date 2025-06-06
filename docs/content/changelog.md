---
title: Release History
description: The release history for OverrideAudit
---


## Version 3

This is the latest version of Override, targeting Sublime Text builds of 4200
and newer (Sublime Text 4).

### 3.0.0 (????-??-??)

  - Updated the minimum required version of Sublime Text to be `4200` going
    forward, to take advantage of new features in Sublime and provide a
    cleaner cut for when the next dev release cycle alters the plugin host
    structure.

  - Update OverrideAudit to officially use the Python 3.8 plugin host rather
    than the legacy plugin host.

  - Fix some minor edge case bugs that could trigger in obscure cases and cause
    console errors.

  - Fix an issue with the package hover popup for some reports displaying an
    incorrect count of overrides.

  - Update handling of the Python version that displays in the hover popup so
    that it always displays even if there are no plugins, and make the reported
    version more correct based on upcoming changes to the Python version used
    by Sublime.

  - If a package declares an invalid Python version, mention in the hover popup
    that plugins are ignored in that package as a result (Sublime displays a
    message to this effect in the console when the package loads).

  - Update the metadata that's used to provide information for packages that
    ship with Sublime directly to include new packages that have been added to
    the standard Sublime distribution.

  - Mark the dependencies that display in the package report as "legacy-style"
    dependencies, since with PC 4+, all most all dependencies are installed as
    actual libraries outside of the Packages folder.


## Version 2

This is an updated version of OverrideAudit, targeting Sublime Text 3.2+
(builds 3197 and later).


### 2.2.7 (2024-02-21)

  - Update the documentation link that is present in the command palette,
    which was missed as a part of the prior release.


### 2.2.6 (2023-09-15)

  - Update documentation links to point to the new domain at which the
    documentation is hosted, as well as some support locations as well; these
    were not out of date per se, but were brought up to date with current link
    formats.

  - This release was made for ST3 and ST4 so that older versions can still
    access the documentation as they might expect.


### 2.2.5 (2022-06-06)

  - Update the hover popup that displays package information to make it clearer
    that the commands that are implemented in the Default package are available
    in all plugin hosts and not just the one that it natively runs in.

  - Include extra hover popups on different parts of the various reports that
    are available to help explain what is being seen, such as the different
    package types and the text that marks different types of overrides.

  - **This is the last version of OverrideAudit that is targeted towards Sublime
    Text 3; all future versions will require Sublime Text 4 version 4126 or
    better.**


### 2.2.4 (2021-10-12)

  - Fix an issue with the command that allows you to open any resource, which
    was not properly allowing for opening all resources. In particular, any
    override classified as `Unknown` (a file in a package with no corresponding
    file in the `sublime-package` file) was filtered from the list, making
    opening them impossible.


### 2.2.3 (2021-07-13)

  - Fix the version of Python displayed for the `User` package in builds of
    Sublime Text 4, where plugins in that package run in the new plugin host.

  - Fix commands in tab context menus generating errors because they were
    getting an `event` in situations they did not expect them in.


### 2.2.2 (2020-10-20)

  - When refreshing a report, put the cursor back at the top of the file so that
    moving doesn't cause the scroll to jump.

  - Fix an issue with diffing packages that aren't represented with a
    `sublime-package` file.

  - All reports now use a custom context menu so that the commands that only
    commands relevant to the report are displayed.

  - Reports can now optionally skip displaying overrides on files if they're
    overrides that are unchanged from the base file (such as when temporarily
    reverting overrides).

  - Fix a bug with context menu commands in windows where there was an HTML or
    Image sheet in place, which would make the commands choose the wrong tab and
    potentially generate errors.


### 2.2.1 (2020-02-26)

  - This fixes a bug in the new `Open Resource` command that would cause it to
    hide any packages that are not backed by a `sublime-package` file (such as
    the `User` package).


### 2.2.0 (2020-01-21)

  - Include a new `Open Resource` command that will allow you to browse for and
    open any package resource you like. This works like the
    `PackageResourceViewer` command of the same name, except that any resources
    that are represented by overrides are annotated in the panel.

  - The hover popup that appears on packages in OverrideAudit has an additional
    field for packages that contains plugins in the form of the version of
    Python that's used to execute the plugins in that package.

  - Fix an issue where some OverrideAudit commands would not reload themselves
    if the package was update without restarting Sublime.


### 2.1.1 (2019-11-05)

  - Fix an issue with the new `mini_diff_underlying` setting in which if an
    override was open when you quit Sublime and then you restart, the
    incremental diff indicators would not be set up correctly.


### 2.1.0 (2019-9-15)

  - Added new commands to create an override and promote a view opened by
    `View Package File` to an override. Both set up the tab so that saving the
    file for the first time will create the override; closing the tab before
    saving will abort.

  - Added a new command to revert an override back to the original file content;
    the new `confirm_revert` setting controls if you are asked to confirm the
    revert or not. Unlike deleting an override, the override content is
    irrevocably lost if you don't back it up first (e.g. in `git`).

  - Added a new setting `mini_diff_underlying` to have OverrideAudit set up the
    incremental diff functionality of Sublime while editing an override to
    track the unpacked version of the file instead of the version on disk.


  - Loose files in unpacked packages that don't correspond to files in their
    packed package equivalent can be displayed in the Override and Bulk Diff
    reports via the `ignore_unknown_overrides` setting.


  - Hovering the mouse over a package name in a report will display a package
    popup with information on that package, such as it's version and
    description and a click-able URL (for packages that define them). The popup
    also includes information on overrides in that package as well as some
    commands. This is still a `WIP`, so the layout and available commands are
    not fully fleshed out yet.

  - Fixed an issue where the temporary files created for external diffing might
    have a different line ending than the source file originally had.

  - Fixed an issue with the `Bulk Diff Package` context command in reports,
    which was not hiding itself when disabled. It is now also smarter about when
    it does enable itself.

  - Fix a bug in dependency package detection that caused it to only detect
    unpacked packages as a dependencies.


### 2.0.0 (2019-3-14)

  - The code has been refactored to make it easier to extend and add new
    commands. With the exception of the items outlined in the following points,
    everything works as it did before. If you had custom key
    bindings/menus/command palette entries, they may need to be updated.

  - Commands intended for use in context menus now have a customizable
    visibility state to allow for more control in custom menus. Where
    previously they would always hide themselves if they did not apply, now
    they instead disable themselves. The default context menus still hide the
    commands, however.

  - Default command captions for disabled commands are slightly different in
    cases where the contextual information that says what they would do is
    missing. For example, `Diff Override` instead of telling you what override
    might be diffed.

  - Slight visual tweaks to the Package Report to make it more visually
    pleasing.


## Version 1

  - This is the original version of OverrideAudit, targeting Sublime Text 3
    builds 3092 or later.


### 1.2.2 (2019-03-13)

  - This version is functionally identical to version 1.2.1 and exists to be the
    place holder for the last of the 1.x series versions of OverrideAudit. It
    can only be automatically installed by people using builds of Sublime Text
    3 prior to build 3197; newer versions of Sublime will pick up version 2
    instead.


### 1.2.1 (2019-02-15)

  - Support using
    [Sublimerge Pro](https://packagecontrol.io/packages/Sublimerge%20Pro){: target="_blank" class="external-link" }
    or
    [Sublimerge 3](https://packagecontrol.io/packages/Sublimerge%203){: target="_blank" class="external-link" }
    as the external diff tool by setting `external_diff` to `"sublimerge"`.

  - Improve detection of an invalid `external_diff` setting that could lead to
    the command being enabled when it should not be.

  - Log to the console when the temporary files created during an external diff
    are removed.


### 1.2.0 (2019-02-10)

  - Implement the ability to open an override diff in an external diff tool via
    the `external_diff` setting. This command is available from the command
    palette and the context menu of override diff views.


### 1.1.2 (2019-01-21)

  - Fix a bug in the handling of the `save_on_diff` setting in which, in certain
    cases an override buffer tab might visually appear unsaved even though the
    contents were saved to disk properly.


  - Fix a bug introduced in 1.1.0 while fixing
    [#24](https://github.com/OdatNurd/OverrideAudit/issues/24){: target="_blank" class="external-link" }
    in which text in reports telling you that there are no overrides would
    incorrectly be treated as override file names.

  - Improved detection of dependency packages that are under development, which
    use a different metadata file than installed dependencies do.
    ([#25](https://github.com/OdatNurd/OverrideAudit/issues/25){: target="_blank" class="external-link" })

  - Replace the menu item in the preferences menu and the entry in the command
    palette that open the README file with a version that opens this online
    documentation instead.


### 1.1.1 (2017-05-01)

  - Remove a debug print statement that slipped through during some last minute
    code testing prior to the last release.


### 1.1.0 (2017-04-28)

  - Implement the ability to `freshen` a single expired override or all
    within a package
    ([#15](https://github.com/OdatNurd/OverrideAudit/issues/15){: target="_blank" class="external-link" })
    via a context menu option.

  - Implement the ability to show the diff header even if a diff is empty
    ([#18](https://github.com/OdatNurd/OverrideAudit/issues/18){: target="_blank" class="external-link" })
    controlled via `diff_empty_hdr` option

  - Fix a problem with overrides starting with a period not being correctly
    recognized as an override
    ([#24](https://github.com/OdatNurd/OverrideAudit/issues/24){: target="_blank" class="external-link" })

  - Fix a file case issue on Windows/MacOS where opening an override from a
    package folder with an incorrect case would not enable the commands to edit
    or diff the override

  - Performance enhancements for some package operations for users with a large
    number of installed packages


### 1.0.1 (2017-04-10)

  - Fix mixed path separators in diff output, delete confirmations and diff tab
    headers so they are always forward slashes (unix-style) to visually
    conform with how Sublime represents package path fragments internally
    ([#14](https://github.com/OdatNurd/OverrideAudit/issues/14){: target="_blank" class="external-link" })

  - The Package Report, Override Report and Bulk Diff Reports now have word wrap
    turned off by default

  - Enhanced the checks performed at file load and save so to more correctly
    determine if a file is actually an override or not when enabling
    integration with OverrideAudit Edit/Diff functionality

  - Rename the "Swap Diff/Override View" command to "Swap Diff/Edit View" in the
    command palette and change the associated text used in Diff tab titles

  - Add a configuration option `save_on_diff` (defaults to `false`) to control
    if the contents of an edited override should be persisted to disk before
    performing a diff on it.


### 1.0.0 (2017-04-3)

  - Initial release
