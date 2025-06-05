---
title: Commands
description: OverrideAudit Command List
---

This page lists the various commands that you can use while working with
OverrideAudit. These commands are integrated into Sublime Text in a variety of
ways to better suit the different work styles that people have.

Although some commands (such as creating a
[Package Report](../reports/package.md)) are always available, many commands
are only present when the current situation warrants them, so that
OverrideAudit can stay out of your way.

The list below specifies in what situations and locations each command is
presented, along with a description of what the command actually does.

---

### :material-keyboard: Create Override

***Command Palette***

:   `OverrideAudit: Create Report`

***Menu***

:   `Tools > OverrideAudit > Create Override`

***Context Menu***

:   `OverrideAudit: Create Override` (*on a package name in a report*)

This command allows you to create a new override quickly and easily by
prompting you to select the appropriate package and resource to override via a
quick panel. The packages displayed are constrained to only those packages
which can contain overrides, and the list of package resources is constrained
to only those files which are not currently overridden.

In use the command opens up the content of the underlying package file in a new
buffer and (if
[mini_diff_underlying](../config/settings.md#mini_diff_underlying) is enabled)
will also set up the
[incremental diff](https://www.sublimetext.com/docs/incremental_diff.html){: target="_blank" }
functionality in Sublime Text to track changes to the file based on the Packed
version of the file so that you can see what changes you've made.

The override will not be created until you save the file for the first time,
allowing you to change your mind without having to delete the override
afterwards. If you close the file without making any changes, you won't be
prompted to save; if you intend to create an override of the file that is
identical, you must manually save before closing the buffer.

!!! NOTE

    When executed from the context menu of a package name in a report, the
    command infers the package name and only prompts you to select the resource
    you want to override.


---

### :material-keyboard: Open Resource

***Command Palette***

:   `OverrideAudit: Open Resource`

***Menu***

:   `Tools > OverrideAudit > Open Resource`

This command allows you to open any package resource by prompting you to select
the appropriate package and resource via a quick panel in the same way as the
command to create an override would. Unlike that command, all package resources
will be shown, and any that are currently being overridden will be annotated in
the list as well.

This is similar in use to the `View Package File` command that is natively
available in Sublime, though the method for browsing for the package resource
is different.

!!! NOTE

    When opening a resource, the file will be editable (unlike when opened via
    `View Package File`); this facilitates the creation of a new override should
    that be desirable.


---

### :material-keyboard: Override Current Resource

***Command Palette***

:   `OverrideAudit: Override Current Resource`

***Menu***

:   `Tools > OverrideAudit > Override Current Resource`

***Context Menu***

:   `OverrideAudit: Override This Resource` (*while viewing a package resource
    that is not already overridden*)

This command is a shortcut to the [Create Override](#create-override) command,
and can be used to convert an existing file buffer for a package resource into
an override without having to navigate to it in the quick panel.

The command is only enabled while the current file in Sublime is an appropriate
file; when selected it immediately makes the buffer editable and otherwise does
what the Create Override command would do.

To be eligible to create an override, the current file must be read only, have
a path that indicates that it is a package file, and not currently exist on
disk. The easiest way to open such a file is to use the `View Package File`
command from the command palette.


---

### :material-keyboard: Package Report

***Command Palette***

:   `OverrideAudit: Package Report`

***Menu***

:   `Tools > OverrideAudit > Package Report`

This will display a list of all packages currently installed in Sublime Text,
in a table format. The table lists the packages in roughly the order that they
will be loaded by Sublime at startup (top to bottom and left to right).

For each package, an indication is made as to whether this package is
`[S]`hipped, `[I]`nstalled or `[U]`npacked (see the
[terminology](../terminology/index.md) page for more information).

Additionally, a package that is currently disabled is displayed in
`[Square Brackets]` while a package that represents a dependency for an
installed package is displayed in `<Angle Brackets>`.

Each package name supports a context menu item which allows you to open a bulk
diff report for that package, allowing you to quickly get an overview of the
status of any overrides on that package. See the OverrideAudit: Bulk Diff
Single Package command for more information.

!!! NOTE

    As of Package Control 4, many package dependencies are installed as actual
    libraries rather than as special dependency packages. As such, you may not
    see all dependencies in the package report.


---

### :material-keyboard: Override Report

***Command Palette***

:   `OverrideAudit: Override Report`

***Menu***

:   `Tools > OverrideAudit > Override Report`

This will display a list of all packages for which there are overrides of any
type, *simple* or *complete*, with an indication on any package or override
file that is currently expired (see the [terminology](../terminology/index.md)
page for more information on these terms).

For each package displayed, a condensed version of the indicators from the
[Package Report](../reports/package.md) are displayed, indicating whether the
package in question is `[S]`hipped, `[I]`nstalled or `[U]`npacked.

A package which is a *complete* override is indicated by text to this effect
appearing next to it in the output line. If such a package is *expired*, an
additional note to this effect is added to let you know.

All *simple* overrides for a package are displayed below the package name in the
report, and may be prefixed with an `[X]` mark if they are currently *expired*.

As with the `Package Report`, a context menu item is presented on package names
to allow a quick bulk diff of overrides in that package. Additionally, override
filenames include context commands to allow you to quickly edit, diff or delete
that override.


---

### :material-keyboard: Override Report (Only Expired)

***Command Palette***

:   `OverrideAudit: Override Report (Only Expired)`

***Menu***

:   `Tools > OverrideAudit > Override Report (Only Expired)`

This command operates the same as the standard
[Override Report](../reports/override.md) command, but constrains its output to
**only** packages which have some form of expired override (either *simple* or
*complete*).

This allows you to focus solely on those overrides which may require your more
immediate attention.


---

### :material-keyboard: Override Report (Exclude Unchanged)

***Command Palette***

:   `OverrideAudit: Override Report (Exclude Unchanged)`

***Menu***

:   `Tools > OverrideAudit > Override Report (Exclude Unchanged)`

This command operates the same as the standard
[Override Report](../reports/override.md) command, but the list of overrides
displayed is filtered so that any override that is identical to the file it's
overriding is not displayed. If doing this causes a package to contain no
overrides, the entire package is filtered from the list as well.

This allows you to focus solely on overrides that are different, such as if
you are working on changes to a package by overriding it entirely (for example
when working on the
[shipped Sublime packages](../terminology/index.md#shipped-package)).


---

### :material-keyboard: Bulk Diff Report (All Packages)

***Command Palette***

:   `OverrideAudit: Bulk Diff All Packages`

***Menu***

:   `Tools > OverrideAudit > Bulk Diff: All Packages`

This will generate a diff for every *simple* override that exists for all
packages into a single output report, allowing for a quick overview of all
overrides at once.

As for the [Override Report](../reports/override.md) command, each package
listed has a condensed version of the indicators from the Package Report
indicating whether the package in question is `[S]`hipped, `[I]`nstalled or
`[U]`npacked as well as an indication if the package is a *complete* override
or not. Additionally, expired *complete* and *simple* overrides are also
indicated in the bulk diff report.

Each section of the report is progressively indented so that it is possible to
use Sublime code folding to hide away parts of the report as you work.

As in the [Override Report](../reports/override.md), the name of each package
and the filenames of each override support context menus that allows you to
quickly bulk diff, open or diff them in their own distinct view.


---

### :material-keyboard: Bulk Diff Report (Single Package)

***Command Palette***

:   `OverrideAudit: Bulk Diff Single Package`

***Menu***

:   `Tools > OverrideAudit > Bulk Diff: Single Package...`

***Context Menu***

:   `OverrideAudit: Bulk Diff Package` (*on a package name in a report*)

This command operates identically to the
[Bulk Diff All Packages](#bulk-diff-report-all-packages) command, with the
exception that instead of calculating a diff for all overrides in all packages
you are instead prompted via a quick panel for a single package to diff
instead.

You can also access a bulk diff of a single package via a context menu on the
name of a package in a [Package Report](../reports/package.md),
[Override Report](../reports/override.md) or
[Bulk Diff Report](../reports/bulkdiff.md).

In these cases the command is directly applied to the package named without
prompting you first.


---

### :material-keyboard: Refresh Report

***Command Palette***

:   `OverrideAudit: Refresh Report`

***Menu***

:   `Tools > OverrideAudit > Refresh Report`

***Context Menu***

:   `OverrideAudit: Refresh Report` (*anywhere in a report view*)

***Keyboard*** (see [key bindings](../config/keybinds.md)))

:   ++f5++ (*All Platforms*)

This command is available from within all OverrideAudit report views (
[Package Report](../reports/package.md),
[Override Report](../reports/override.md), or
[Bulk Diff Report](../reports/bulkdiff.md)) via the Command Palette, context
menu or main menu, and allows you to quickly re-run the same report.

When a report is refreshed, OverrideAudit ignores the current values of the
[reuse_views](../config/settings.md#reuse_views) and
[clear_existing](../config/settings.md#clear_existing) options and operates as
if they are both set to true so that the existing report will be replaced.

This command is also available as a context menu entry from within a report
view or its associated editor tab and via the keyboard.


---

### :material-keyboard: Diff Single Override

***Command Palette***

:   `OverrideAudit: Diff Single Override`

***Menu***

:   `Tools > OverrideAudit > Diff Single Override...`

***Context Menu***

:   `OverrideAudit: Diff Override` (*on an override name in a report or in an
    override view*)

This will display a quick panel that lists all packages with at least one
*simple* override, and allows you to compare the differences between the base
file and your override to see what is different between the two.

When the content of the file is different, the output is displayed in a Unified
Diff format in a new buffer, allowing you to inspect the changes.

As a shortcut, you can directly diff an override file from the context menu on
any [Override Report](../reports/override.md),
[Bulk Diff Report](../reports/bulkdiff.md) or directly in an override while
you're editing it. In these cases the command is directly applied to the
override file without prompting you first.

The option [diff_unchanged](../config/settings.md#diff_unchanged) allows you to
specify the result of performing a diff when the override is identical to the
underlying file.


---

### :material-keyboard: Swap Diff/Edit View

***Command Palette***

:   `OverrideAudit: Swap Diff/Edit View`


***Context Menu***

:   `OverrideAudit: Diff Override` (*while editing an override or on an override
    name in a report*)

:   `OverrideAudit: Edit Override` (*while viewing an override diff or on an
    override name in a report*)

***Keyboard*** (see [key bindings](../config/keybinds.md)))

:   ++alt+o++ (*Windows/Linux*)
:   ++command+alt+up++ (*MacOS*)

This command is only available while the current file is either an edit session
for an override or a diff of an override or in the context menu on an override
name in a report.

Although this command does not appear in the top level `Tools > OverrideAudit`
menu, it does appear within command palette and in the context menu of an
appropriate file view, as well as on the context menu of an override file from
within an [Override Report](../reports/override.md) or
[Bulk Diff Report](../reports/bulkdiff.md).

In the command palette the command is named as `Swap Diff/Edit View`, while in
context menus it appears with a name that tells you which of the two options
it's going to take.

Additionally, OverrideAudit contains a key binding to the standard Sublime key
for swapping between associated files that operates from within an appropriate
file view; see [key bindings](../config/keybinds.md)).

Regardless of how you trigger the command, any existing edit or diff view for
this override will be switched to directly. In the case of a diff view, the
diff will be recalculated, allowing any saved changes to be immediately
reflected. The configuration option
[save_on_diff](../config/settings.md#save_on_diff) can be enabled to ensure
that unsaved changes in the file are persisted first, if desired.

This command ignores the current values of the
[reuse_views](../config/settings.md#reuse_views),
[clear_existing](../config/settings.md#clear_existing) and
[diff_unchanged](../config/settings.md#diff_unchanged) settings and operates as
if they are set to `true`, `true` and `"diff"` respectively in order to ensure
that you don't end up with a large number of duplicate views.


---

### :material-keyboard: Open Diff Externally

***Command Palette***

:   `OverrideAudit: Open Diff Externally` (*while viewing an override diff*)

***Context Menu***

:   `OverrideAudit: Open Diff Externally` (*while viewing an override diff*)

This command is only available while the current file is a diff of an override
and requires that the [external_diff](../config/settings.md#external_diff)
setting be set as well.

Like other contextual commands, this command does not appear in the top level
`Tools > OverrideAudit` menu but does appear with in the context menu of an
appropriate diff view and in the command palette while a diff view is active.

The command executes the configured external command to perform it's own diff
of this particular override, allowing you to use the power of that tool for
more sophisticated diff operations, such as side by side diffs, ignoring white
space, merging changes and so on.

When invoked, the command extracts a temporary read-only copy of the base file
for the current override for use by the external tool and then deletes that
file once the diff has completed. The file is named based on where the base
override file came from.

By default the file is created in the temporary directory on the system, but
you can set the `TMPDIR`, `TEMP` or `TMP` environment variables to alter the
location where the temporary files are stored.


---

### :material-keyboard: Delete Override

***Command Palette***

:   `OverrideAudit: Delete Override`

***Context Menu***

:   `OverrideAudit: Delete Override` (*while editing an override, viewing an
    override diff, or on an override name in a report*)

This command is only available while the current file is either an edit session
for an override or a diff of an override or in the context menu on an override
name in a report.

Like the [Swap Diff/Override View](#swap-diffedit-view) command, this command does not
appear in the top level `Tools > OverrideAudit` menu but does appear within the
context menu of an appropriate file view and on the context menu of an override
file from within an [Override Report](../reports/override.md) or
[Bulk Diff Report](../reports/bulkdiff.md).

This command will delete the current override after prompting you to verify
that you really mean to delete this file. OverrideAudit attempts to send the
override to the trash using the same internal mechanism that Sublime Text uses
to delete files.

When an override is deleted, any existing edit sessions of the override will
remain open, and Sublime will indicate that they have unsaved changes because
the file is missing.

The configuration setting
[confirm_deletion](../config/settings.md#confirm_deletion) can be set to
`false` if you want to be able to delete overrides without being prompted
first.


---

### :material-keyboard: Revert Override

***Command Palette***

:   `OverrideAudit: Revert Current Override`

***Context Menu***

:   `OverrideAudit: Revert Override` (*while editing an override, viewing an
    override diff, or on an override name in a report*)

This command is only available while the current file is either an edit session
for an override or a diff of an override or in the context menu on an override
name in a report.

Like the [Delete Override](#delete-override) command, this command does not appear in
the top level `Tools > OverrideAudit` menu but does appear within the context
menu of an appropriate file view and on the context menu of an override file
from within an [Override Report](../reports/override.md) or
[Bulk Diff Report](../reports/bulkdiff.md).

This command will revert the content of the current override back to the
original content of the file after prompting you to verify that you really
meant to perform this action.

This has the same general effect of deleting an override in that the content of
the file is put back to the original data, but the override remains on disk
(and is thus still an override, though it has no changes). The original
override will be irrevocably lost when this command is executed, so take a
manual backup if you would like to come back to this override at a future
point.

This command is most useful for package developers that may want to temporarily
put the content of a changed file back to it's release state quickly and
easily, since packages are generally held in source control and the modified
file can be easily put back later as needed.

The configuration setting
[confirm_revert](../config/settings.md#confirm_revert) can be set to `false` if
you want to be able to revert overrides without being prompted first.


---

### :material-keyboard: Freshen Expired Overrides

***Context Menu***

:   `OverrideAudit: Freshen Expired Overrides in Package` (*on a package name in
    a report*)
:   `OverrideAudit: Freshen Override` (*on an override name in a report*)

This command is only available from within the context menu of an
[Override Report](../reports/override.md) or
[Diff Report](../reports/bulkdiff.md) for overrides that are expired or for
packages that contain at least one expired override.

When used, the last modification time stamp of the selected expired overrides
is modified to be more recent than the underlying file after prompting you to
verify that you meant to perform the freshen operation.

This stops OverrideAudit from reporting that override as being expired and also
modifies the report to indicate that the overrides freshened are now no longer
expired.

Freshening a package is a shortcut for freshening all of the expired overrides
that it contains all in one operation, which may be handy in cases where
package files have been updated in the `sublime-package` file without their
content changing.

The configuration setting
[confirm_freshen](../config/settings.md#confirm_freshen) can be set to `false`
if you want to be able to freshen overrides without being prompted first.
