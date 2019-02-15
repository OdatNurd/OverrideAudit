OverrideAudit ChangeLog
=======================

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