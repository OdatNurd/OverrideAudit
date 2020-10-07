OverrideAudit ChangeLog
=======================

Version 2.2.2 (????-??-??)
--------------------------
  * Previously, when creating or refreshing a report, the cursor
    would be left at the bottom of the view, which can cause some
    unwanted scroll on cursor move.

    Report creation and refreshing now puts the cursor at the top
    of the buffer, similar to the behaviour of opening a file.

  * Fix an issue where attempting to Diff a package that has no
    sublime-package file or no unpacked files might cause an error.

  * Added a new option to Override reports to allow for
    skipping overrides that are unchanged from appearing
    in reports.

  * Added in a new option to Package Diff reports to allow for
    skipping overrides that are unchanged from appearing in
    reports.

  * Fix the context menu in tabs potentially displaying errors in
    the console if the tab prior to an override tab was an image or
    HTML sheet, which throws off the view index calculation.


Version 2.2.1 (2020-02-26)
--------------------------
  * The `Open Resource` command was incorrectly hiding
    packages that are not represented by a `sublime-package`
    file.

    This made it impossible to open a package resource from
    a purely unpacked package (such as the `User` package).
    This is now resolved.

Version 2.2.0 (2020-01-21)
--------------------------
  * Include a new command to open a resource for viewing, which
    works the same as the PackageResourceViewer command of the
    same name. This is functionally somewhat similar to the built
    in `View Package File` command, but prompts you for the file
    in a different manner; overrides are also annotated in the
    list.

  * For packages that contain plugins, the hover popup on reports
    now indicates what version of Python the plugins in that
    package are running in. This provides an indication of that
    package containing a plugin while also allowing for the
    inclusion of newer versions of Python being supported in
    Sublime in the future.

  * Fix a problem where some commands did not reload on package
    update properly. This is not a particularly big deal (and
    restarting Sublime would resolve the issue anyway).

Version 2.1.1 (2019-11-05)
--------------------------
  * Fix an issue with the new `mini_diff_underlying` setting in
    which if an override was open when you quit Sublime, on
    restart the incremental diff indicators would not properly
    track the underlying package file.

Version 2.1.0 (2019-09-15)
--------------------------
  * New command to create an override or promote a view opened
    by `View Package File` to a potential new override. Both are
    available from the main menu and the command palette as
    appropriate, as well as package name context menus.

  * New setting `mini_diff_underlying` (default: `true`) that
    sets the mini diff functionality in override edit views to
    diff against the underlying package file instead of the file
    on disk. Requires `mini_diff` to be enabled in your user
    preferences.

  * New command to revert an existing override. This replaces
    the file with a freshly unpacked version of the underlying
    file. The new setting `confirm_revert` controls whether the
    user gets asked to confirm this action before it is carried
    out.

  * Loose files in an unpacked package that don't correspond to
    any files in an associated `sublime-package` file are now
    shown in override reports and bulk diffs annotated with `[?]`
    to indicate that their status is unknown. The new setting
    `ignore_unknown_overrides` controls if this feature is enabled
    or not and can be used to filter the list of unknown overrides
    as needed.

  * Include hover popups for packages in reports. The popup gives
    more detailed package information, displays some help
    information on click, and can trigger some commands as well.
    This is currently a work in progress.

  * Fix a bug in bulk diff context menu items in reports; they
    would appear disabled instead of hiding themselves. They're
    now also smarter about when they enable themselves.

  * Fix a bug in which a package was only considered a dependency
    if it was an unpacked package. The package control bootstrap
    package 0_package_control_loader is an example of a dependency
    that is packed, so detection has been altered to check if any
    package is a dependency instead.

  * Fix an issue where the temporary files created when an external
    diff is performed might have different line endings than the
    source file originally had.

Version 2.0.0 (2019-03-14)
--------------------------
  * Massive internal refactoring has been done to make it easier
    to add in new commands and functionality. The primary target
    of the refactor was in taking a few commands which were
    overloaded and took an "action" parameter to select how they
    worked and splitting them out into distinct commands.

    This change will make it easier to add in new functionality
    but it does mean that many commands have been renamed to
    more descriptive names.

    The full list of changes is:

      override_audit_diff_override
        -> override_audit_diff_single

      override_audit_diff_package
        -> override_audit_diff_report

      override_audit_context_override
        -> override_audit_toggle_override
        -> override_audit_diff_override
        -> override_audit_edit_override
        -> override_audit_delete_override
        -> override_audit_freshen_override

      override_audit_context_package
        -> override_audit_diff_package
        -> override_audit_freshen_package

      override_audit_context_report
        -> override_audit_refresh_report

  * Enhanced all of the commands available via the context menu:

      - Commands are now always visible unless you provide an
        argument telling them to hide themselves when they do
        not apply; this allows you to add these commands to other
        menus and control visibily.

      - Commands will be visible but disabled when the underlying
        package or override they are supposed to work with does
        not exist. For an override this means a file does not
        exist, while for a package it means that the unpacked
        folder is missing.

      - The default captions for disabled commands is slightly
        different when the appropriate context information is not
        available to tell you what exactly they will do (e.g.
        "Diff Override" instead of telling you what override will
        be diffed)

  * The package report table frame was updated, because the lack
    of `+` characters is really hard to unsee once it's pointed
    out.

Version 1.2.2 (2019-03-13)
--------------------------
  * Last public version of OverrideAudit version 1.x. This version is
    functionally identical to the previous version, but is here to point
    out that no further releases in this series are planned.


Version 1.2.1 (2019-02-15)
--------------------------
  * Support using
    [Sublimerge Pro](https://packagecontrol.io/packages/Sublimerge%20Pro) or
    [Sublimerge 3](https://packagecontrol.io/packages/Sublimerge%203)
    as the external diff tool by setting `external_diff` to the
    string `"sublimerge"`.

  * Improve detection of an invalid `external_diff` setting that could
    lead to the command being enabled when it should not be.

  * Log to the console when the tempoary files created during an
    external diff are removed


Version 1.2.0 (2019-02-10)
--------------------------
  * Implement the ability to open an override diff in an external diff
    tool via the `external_diff` setting. This command is available
    from the command palette and the context menu of override diff
    views.


Version 1.1.2 (2019-01-21)
-------------------------
  * Fix a bug in save_on_diff handling whereby the buffer might
    visually appear unsaved in some circumstances even though the file
    was actually saved.

  * Fix a bug introduced in 1.1.0 while fixing #24 which caused text
    in reports telling you that there are no overrides to be treated
    as an override.

  * Improve detection of packages that are dependency packages that
    are still under development so that they appear as appropriate in
    package reports (#25).

  * Include links to the online documentation in the settings menu
    and the command palette instead of opening the README file, since
    they contain the same information but one is hyperlinked and laid
    out better than the other one.


Version 1.1.1 (2017-05-01)
--------------------------
  * Remove a debug print statement that slipped through during some
    last minute code testing prior to the last release.


Version 1.1.0 (2017-04-28)
--------------------------

  * Implement the ability to "freshen" a single expired override or
    all within a package (#15) via a context menu option
  * Implement the ability to show the diff header even if a diff is
    empty (#18) controlled via `diff_empty_hdr` option
  * Fix a problem with overrides starting with a period not being
    correctly recognized as an override (#24).
  * Fix a file case issue on Windows/MacOS where opening an override
    from a package folder with an incorrect case would not enable
    the commands to edit or diff the override.
  * Performance enhancements for some package operations for users
    with a large number of installed packages.


Version 1.0.1 (2017-04-10)
--------------------------

  * Fix mixed path separators in diff output, delete confirmations and
    diff tab headers so they are always forward slashes (unix-style)
    to visually conform with how Sublime represents package path
    fragments internally (#14).

  * The Package Report, Override Report and and Bulk Diff Reports now
    have word wrap turned off by default.

  * Enhanced the checks performed at file load and save so to more
    correctly determine if a file is actually an override or not when
    enabling integration with OverrideAudit Edit/Diff functionality.

  * Rename the "Swap Diff/Override View" command to "Swap Diff/Edit
    View" in the command palette and change the associated text used
    in Diff tab titles.

  * Add a configuration option `save_on_diff` (defaults to false) to
    control if the contents of an edited override should be persisted
    to disk before performing a diff on it.


Version 1.0.0 (2017-04-03)
--------------------------

  * Initial release
