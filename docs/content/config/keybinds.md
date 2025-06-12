---
title: Key Bindings
description: Controlling OverrideAudit with custom key buindings
---

## Opening Key Bindings

In order to view the key bindings that ship directly with OverrideAudit, you can
use the `Preferences > Settings > OverrideAudit > Key Bindings` menu item or
the `Preferences: OverrideAudit Key Bindings` command from the Command Palette.

!!! NOTE "Differences in Menu layout on MacOS"

    On MacOS, the `Preferences` menu is under `Sublime Text` in the main menu
    bar.

In the window that this command opens, the left hand pane contains the default
key bindings that ship with OverrideAudit. If you would like to adjust any of
them, copy the binding that you would like to change into the right hand pane
and modify the key as appropriate.

!!! WARNING "Maintain the format of the keymap file!"

    `sublime-keymap` files are `JSON` files which allow for comments of the `//`
    and `/* */` variety; they are also not sensitive to trailing commas in
    places that normally cause problems in strict `JSON` files.

    When copying a key binding to your custom key binding file, remember to
    keep the structure of your file as you see on the left; individual bindings
    should be separated from each other via commas and be within the `[` and `]`
    characters that start and end the file.


## Default Key Bindings

As shipped, OverrideAudit contains two key bindings, both of which have a
[context](https://www.sublimetext.com/docs/key_bindings.html#context-key){: target="_blank" class="external-link" }
applied to ensure that they are only active in the correct place so that they
do not get in the way of any other key bindings you might already be using.


### Toggle Override/Diff View

- *Command:* [Swap Diff/Edit View](../usage/commands.md#swap-diffedit-view)
- ++alt+o++ (Windows/Linux)
- ++command+alt+up++ (MacOS)

While viewing an [override](../terminology/overrides.md), jump to a tab showing
a `diff` of the current override against the underlying file, opening such a
tab if it does not already exist, and refreshing its content if modifications
have been made to the file.

The {{ setting("save_on_diff") }} setting (which is disabled by default) can
use used to automatically save any changes in your override before switching to
the diff.

This command also works in the opposite direction; while viewing an override
diff, this will jump to the tab that contains the override whose diff you're
looking at, opening the file if it is not already open.


### Refresh Report

- *Command:* [Refresh Report](../usage/commands.md#refresh-report)
- ++f5++ (All Platforms)

While viewing any [report](../reports/index.md), cause the report to refresh; all
information being displayed in the report will be recalculated.
