---
title: Configuring OverrideAudit
description: Available configuration settings for OverrideAudit
---

## Opening Settings

In order to view OverrideAudit's settings, you can use the `Preferences >
Settings > OverrideAudit >Settings` menu item or the `Preferences:
OverrideAudit Settings` command from the Command Palette.

!!! NOTE

    On MacOS, the `Preferences` menu is under `Sublime Text` in the main menu
    bar.

In the window that this command opens, the left hand pane contains the default
setting that ship with OverrideAudit. If you would like to adjust any of them,
copy the setting (or settings) that you would like to modify into the right
hand pane and adjust as desired.

!!! WARNING

    `sublime-settings` files are `JSON` files which allow for comments of the
    `//` and `/* */` variety; they are also not sensitive to trailing commas in
    places that normally cause problems in strict `JSON` files.

    When copying a setting to your custom settings file, remember to keep the
    structure of your file as you see on the left; each setting should be in
    `"key": value,` format, separated from each other via commas and be within
    the `{` and `}` characters that start and end the file.


## Available Settings

###  :material-cog: **reuse_views**

- **`Boolean`**
- ***Default:*** `true`

OverrideAudit generally creates an output view to show you the results of
operations. When this option is enabled (the default), OA will try to find the
view created last time and reuse it for the new command. When disabled, a new
view is created every time.

Some OverrideAudit commands may ignore this setting.


###  :material-cog: **clear_existing**

- **`Boolean`**
- ***Default:*** `true`

When `reuse_views` is enabled (the default), this controls whether a reused
view is cleared of its contents prior to executing the command or if the new
output is appended to the end of the existing view.

Some OverrideAudit commands may ignore this setting.


###  :material-cog: **ignore_overrides_in**

- **`List`**
- ***Default:*** `[]`

This is an optional list of package names which should be excluded from
commands that show/calculate override information. The format of this option is
the same as the `ignored_packages` Sublime setting.

This does not affect packages displayed in the general package list; it only
hides packages from lists that show packages with overrides, such as the
[Override Report](garbage) or the commands that find and diff overrides.

!!! WARNING

    Any overrides you create in packages in this list will be masked from you,
    so be very careful about what you add to the list.


###  :material-cog: **diff_unchanged**

- **`String`** (`"diff"`, `"ignore"`, `"open"`)
- ***Default:*** `"diff"`

When using the [Diff Single Override](garbage) command, this setting controls
what happens when the selected override has no differences from the underlying
file.

The possible values of this setting are:

- `"diff"` to open a tab with the empty diff in it
- `"ignore"` to ignore the command; the status line will indicate the lack of
  changes
- `"open"` to open the file for editing, allowing you to see its contents or
  make new modifications.


###  :material-cog: **diff_context_lines**

- **`Number`**
- ***Default:*** `3`

When displaying a diff for an override, this specifies how many unchanged lines
before and after each difference are displayed to provide better context for
the changes.


###  :material-cog: **diff_empty_hdr**

- **`Boolean`**
- ***Default:*** `false`

When enabled, this allows you to see the source files and related time stamps
of both files that participated in the diff even when there are no changes to
display.

This applies both to a bulk diff as well as a single file diff, but note that
for a single file diff this option will only have an effect if `diff_unchanged`
is set to `"diff"`, as otherwise no diff is displayed.


###  :material-cog: **save_on_diff**

- **`Boolean`**
- ***Default:*** `false`

This setting controls whether or not OverrideAudit will make sure any unsaved
changes are persisted to disk when switching from an edit of an override to a
diff of it, so that your changes will be reflected in the diff.

This option has no effect for a buffer with unsaved changes that represents a
file that no longer exists on disk (i.e. you have opened the override and then
deleted it) to ensure that you don't accidentally resurrect a deleted file by
saving it again.


###  :material-cog: **confirm_deletion**

- **`Boolean`**
- ***Default:*** `true`

When removing files, this setting controls whether OverrideAudit will prompt
you to confirm the deletion before it happens or not.

OverrideAudit uses the `send2trash` library that ships with Sublime Text to
perform file deletions.


###  :material-cog: **confirm_freshen**

- **`Boolean`**
- ***Default:*** `true`

When freshening expired override files, this setting controls whether
OverrideAudit will prompt you to confirm the operation before it happens or
not.

Although this operation is not destructive, freshening an expired override will
stop OverrideAudit from warning you that it's expired.


###  :material-cog: **confirm_revert**

- **`Boolean`**
- ***Default:*** `true`

When reverting an override file back to it's original unmodified state, this
setting controls whether OverrideAudit will prompt you to confirm the operation
before it happens or not.

This operation is destructive; the current content of the override will be lost
as a result of this action. Make sure that you have it safely backed up (for
example in a version control system like `git`) if you wish to come back to it
at a later date.


###  :material-cog: **binary_file_patterns**

- **`List`**
- ***Default:*** contents of the global setting in `Preferences.sublime-settings`

This setting is identical to the Sublime Text setting of the same name and
controls what files are considered to be binary for the purposes of performing
a diff operation.

The default value for this operation is taken from your regular Sublime Text
user settings, so you only need to specify a value in the *OverrideAudit*
settings if you want to consider a different set of files binary for the
purposes of diffs.


###  :material-cog: **report_on_unignore**

- **`Boolean`**
- ***Default:*** `true`

OverrideAudit can automatically generate a report to check for *expired*
overrides every time a package is removed from the `ignored_packages` list in
your *Preferences.sublime-settings* file.

As well as happening when you manually decide to re-enable a package you have
been ignoring, this is also an indication that
[Package Control](https://packagecontrol.io){: target="_blank" } has finished
upgrading a package.

When this option is turned off, checks for expired overrides only happen when
Sublime starts or when you manually create an [Override Report](garbage).

When enabled, the report will only be shown if any expired overrides are found.


###  :material-cog: **external_diff**

- **`Boolean`**/**`String`**/**`Dictionary`**
- ***Default:*** `false`

OverrideAudit allows you to open an existing override diff in an external tool
of your choice if so desired. This is often helpful for overrides with complex
diffs, for doing selected reverts or edits based on the original file, and so
on.

The default value for this setting is `false`, which disables the external diff
functionality.

If you use the `Sublimerge Pro` or `Sublimerge 3` package in Sublime Text, you
can set `external_diff` to the string `"sublimerge"` to open the external diff
using that package.

!!! NOTE

    These packages no longer exist as they were redacted by their author; as a
    result, this particular setting is only available to anyone that had already
    installed the package prior to it being removed.

The setting may also be set to a JSON dictionary similar to that used in a
`sublime-build` file. In this dictionary, the keys `shell_cmd`, `env` and
`working_dir` work as they do in a build. The platform keys `linux`, `windows`
and `osx` may also be set as in a build system to provide platform specific
settings, which allows you to use one settings file across all platforms.

The variables that are standard in a `sublime-build` file are also valid here,
as well as the variables `$base` and `$override` which represent the name of
the base file and the override file respectively.


###  :material-cog: **ignore_unknown_overrides**

- **`Boolean`**/**`List`**
- ***Default:*** `["\\.git/", "\\.svn/", "\\.hg/" ]`

When displaying an [Override Report](garbage) or a [Bulk Diff Report](garbage),
OverrideAudit can display files which appear in the Unpacked version of a
package but not in the `sublime-package` file for that package.

These files are known as [unknown overrides](garbage), and are an indication
that a resource has been added to a package by you or that a file that used to
be an override is no longer considered to be one due to a package update.

This setting can be set to `true` to enable this feature or `false` to disable
it. Additionally you can set it to a list of regular expressions for matching
resource file names. This will enable the feature and also use the list of
expressions to hide matching files.

The default is to enable the setting by filtering away the control files that
various version control systems use to be able to track files.

!!! NOTE

    Package resources always use the `posix` (unix-style) path separators, even
    on Windows. Additionally, when using the setting as a list of regular
    expressions, each expression is inherently anchored to the start of the
    resource name


###  :material-cog: **mini_diff_underlying**

- **`Boolean`**
- ***Default:*** `true`

When editing an overridden package resource, OverrideAudit can set up the
`incremental diff` feature of Sublime to track the underlying package file being
overridden. This allows the diff indicators in the gutter to show you changes
as compared to the underlying file as well as being able to use native
functionality to navigate between changes and revert hunks.

When set to `true` (the default), every time you open or save a package override,
the incremental diff will be set to track the packed version of the resource
file you're editing. Setting this setting to `false` disables this feature, in
which case the incremental diff works the same for overrides as for other
files.

For this setting to have any effect, the `mini_diff` setting in your user
preferences must be set to `true`.
