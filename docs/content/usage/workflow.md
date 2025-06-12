---
title: Workflow
description: Workflows in OverrideAudit
---

# OverrideAudit Workflows

At its core, OverrideAudit helps automate the actions you would normally take
to allow you to keep track of and work with your
[overrides](../terminology/overrides.md) more easily. Although what it can do
is easy to understand, you may find yourself wondering how or why you would
actually use it in the real world.

This page outlines some of the tasks that you might carry out with
OverrideAudit and what your workflow might be while performing those tasks.


## Using OverrideAudit

OverrideAudit strives to integrate with your normal Sublime workflow as much as
possible, unobtrusively sitting in the background waiting for you to call on
its services. In order to stay out of the way, many of the commands and tasks
available are context sensitive in nature, appearing only in the situations
where they are needed.

Commands for creating [Reports](../reports/index.md) are always available from
within the Command Palette or the Main Menu. Additional commands become
available in the Command Palette as well as the context menu of views that
pertain to overrides (reports, while editing an override, etc) as needed.

In most places, the context menu is specific not only to the editor pane you
are using, but also to the location within the pane that you open the menu. For
example, package names in Reports have a different set of context sensitive
items than the names of overrides do.


## Reports

Most of the ways into the OverrideAudit workflow are by first generating a
report of some kind in order to gather information about how best to proceed.
In most cases that will be an automatically generated report that informs you
of potential problems.

[Reports](../reports/index.md) tell you things such as what packages you have
installed as well as the overrides that exist inside of them. From these
reports, you can use the available context sensitive commands to get at the
information you need to keep Sublime running in tip top shape.


### Automatic Reports

For most users, working with overrides starts with an automatically generated
[Override Report](../reports/override.md), which may happen after an update to
Sublime or one of the packages you have installed. In these cases,
OverrideAudit may detect that one or more of your
[overrides](../terminology/overrides.md) has
[expired](../terminology/index.md#expired-override) and may require attention.

This report allows you to get a quick overview of all of the overrides you
currently have and which ones may require your attention to ensure that you
don't miss out on anything important.


### Manual Reports

OverrideAudit can also generate various [Reports](../reports/index.md) on
demand, including the expired override report that it automatically generates
when needed. These reports can be created either in response to an automatic
report to help diagnose potential problems as well as to gain insight into your
overrides at any time.


## Overrides


Although the various reports help you to see what overrides you have and their
state, their main focus is in helping you to work with your overrides in
general. The reports help you focus in on the overrides that may need your
attention the most.

OverrideAudit adds extra context sensitive functionality to open override
files, allowing you to see how they're different from the files they are
overriding, update them when they need changes, and even to remove them when
you're done with them.


### Finding Overrides

Before you can start working with your overrides, you need to know that they
exist in the first place. The easiest way to do that is via an
[Override Report](../reports/override.md). This report will show you what
overrides exist in each package (if any), as well as providing an indication as
to whether that override is [expired](../terminology/index.md#expired-override)
or not.

Another option is the [Bulk Diff Report](../reports/bulkdiff.md), which
contains the same information as the Override Report and also includes a
unified diff for each override so that you can immediately see how each
override is different from it's underlying file. This report can be generated
either for all packages all at once or for just a single package, depending on
your needs.


### Editing Overrides

When working with OverrideAudit, you may determine that you would like to make
changes to an override that already exists. From any report which is showing
you the name of an override, you can open the context menu over an override and
select the
{{ command('Swap Diff/Edit View', 'OverrideAudit: Edit Override') }}  command
to automatically open the override for editing.

If you have a diff view open for an override, you can open the context menu
anywhere within the file contents or it's editor tab and select the
`OverrideAudit: Edit this Override` command, select the `OverrideAudit: Swap
Diff/Edit View` command from the Command Palette or use the ++alt+o++ or
++command+alt+up++ [keyboard shortcut](../config/keybinds.md) to immediately
swap to an edit view for that override.

It is also possible to open an override manually using the standard Sublime
file operations or via another package such as
[PackageResourceViewer](https://packagecontrol.io/packages/PackageResourceViewer){: target="_blank" class="external-link" }.
Regardless of how you open an override, OverrideAudit will detect that it is an
override and seamlessly integrate with it.


### Diffing Overrides

Once you know you have an override, you often need to know exactly how your
override is different from the underlying file that it is overriding. For this
purpose, OverrideAudit provides the ability to calculate and display a diff of
an override, allowing you to easily see how things are different.

There are a variety of ways to generate a diff for an existing override,
allowing you to quickly get at the information you need with a minimum of
effort.

  - Selecting {{ command('Diff Single Override', 'OverideAudit: Diff Single Override') }}
    from the Command Palette or `Tools > OverrideAudit > Diff Single Override`
    from the menu will prompt you for an override and then show you a diff of
    it.

    This command automatically filters the list of packages and the contents
    of the selected package so that you only see relevant information.

  - From within any report which is showing you the name of an override, you can
    open the context menu over an override and select the
    `OverrideAudit: Diff Override` command to open a diff for that override.

  - While you are editing an override you can open the context menu anywhere
    within the file or it's editor tab and select the
    `OverrideAudit: Diff this Override` command to immediately open a diff.

    This operation is also available as `OverrideAudit: Swap Diff/Edit View` in
    the Command Palette or using the ++alt+o++ or ++command+alt+up++
    [keyboard shortcut](../config/keybinds.md).


!!! NOTE "Using external diff tools"

    For more extensive override changes, or when you have a preference to view
    a diff in a favorite tool, OverrideAudit can be configured to use that tool
    via the {{ setting("external_diff") }} setting. This enables the
    `OverrideAudit: Open Diff Externally` command in the context menu and
    command palette while you are viewing a diff.


!!! NOTE "Taking advantage of Sublime Text's internal Diff function"

    The {{ setting("mini_diff_underlying") }} setting can be used to have
    OverrideAudit set up the Sublime Text
    [incremental diff](https://www.sublimetext.com/docs/incremental_diff.html){: target="_blank" class="external-link" }
    functionality to show file differences based on the unpacked version of the
    file.

    With this option enabled (it is turned on by default), while editing
    overrides you can use the native Sublime Text diff navigation and display
    to see exactly how your override is different from the underlying file.



### Freshening Expired Override

OverrideAudit will warn you when you have any overrides that have
[expired](../terminology/index.md#expired-override); that is, the file that
it is overriding has been updated since you created or last edited your
override. In such a case, you should check to see how the changes impact you
and if you need to take any action (for example, to pick up new bug fixes).

OverrideAudit determines that an override has expired when the underlying file
has a newer modification date than the override itself, which indicates that
the source file has been potentially altered. Making any changes to an override
(or just saving it without making any changes) will update the last
modification time and "freshen" the override.

If you are viewing a [Report](../reports/index.md) that displays the names of
existing overrides, you can also take the following actions:

  - Open the context menu on the name of an expired override and select the
    {{ command('Freshen Expired Overrides', 'OverrideAudit: Freshen Package') }}
    command to freshen that single override.

  - Open the context menu on the name of a package which contains at least one
    expired override and select the
    {{ command('Freshen Expired Overrides', 'OverrideAudit: Freshen Package') }}
    command to freshen all expired overrides within that package all at once.


### Deleting Overrides

Sometimes overrides reach a point where they are no longer useful. This can be
because you have decided that you don't like the change, or possibly the
package author has officially fixed a problem that you were working around.
OverrideAudit allows you to easily delete an override when you no longer need
it.

Like most commands, this operation available in a variety of ways:

  - From within an Edit or Diff of an override, you can select the
    {{ command('Delete Override', 'OverrideAudit: Delete this Override') }}
    command from the context menu or `OverrideAudit: Delete Current Override`
    from the Command Palette.

  - From within a report that displays the names of overrides, you can open the
    context menu over the name of an override and select the
    `OverrideAudit: Delete Override` command.

!!! NOTE

    When OverrideAudit deletes an override, it tries to places it into the
    Recycle Bin/Trash (depending on your operating system) so that you can get
    it back if you need to.

    This is done through the same mechanism that Sublime itself uses to delete
    files.


!!! WARNING

    When you delete an override, Sublime will unload it but will not
    automatically reload the package to pick up the original file.

    For this reason, it is a good idea to restart Sublime after deleting
    overrides to ensure that everything works as you expect it to.


### Reverting Overrides

In some cases, your override may reach a point where you do not want to delete
it outright, but you would like to make a different set of changes, for example
if the underlying file has changed enough that it would be easier to make the
modification again to the new file. OverrideAudit allows you to easily revert
the content of the file back to the base, allowing you to make new edits.

  - From within an Edit or Diff of an override, you can select the
    {{ command('Revert Override', 'OverrideAudit: Revert this Override') }}
    command from the context menu or `OverrideAudit: Revert Current Override`
    from the Command Palette.

  - From within a report that displays the names of overrides, you can open the
    context menu over the name of an override and select the
    `OverrideAudit: Revert Override` command.


!!! NOTE

    Reverting an override leaves the file in place but brings the content back
    in line with the underlying package content. Your override remains in place
    and will be managed just as other overrides are.