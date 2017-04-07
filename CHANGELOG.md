OverrideAudit ChangeLog
=======================

Changes in the next release
---------------------------

  * Fix mixed path separators in diff output, delete confirmations and diff tab
    headers so they are always forward slashes (unix-style) to visually conform
    with how Sublime represents package path fragments internally (#14).
  * The package report, Override report and and bulk diff reports now have word
    wrap turned off by default.
  * Enhanced the checks performed at file load and save so to more correctly
    determine if a file is actually an override or not

Version 1.0.0 (2017-04-03)
--------------------------

  * Initial release