OverrideAudit ChangeLog
=======================

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