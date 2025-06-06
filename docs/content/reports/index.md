---
title: Reports
description: Reports in OverrideAudit
---

OverrideAudit contains several reports that help you to get a handle on what
packages you currently have installed, how they're installed and what overrides
they may contain. Many [workflows](../usage/workflow.md) in OverrideAudit start
from a report.

All reports are always available from the `Tools > OverrideAudit` menu as well
as from the command palette, regardless of the context of the current action
you may be taking in Sublime. Additionally, [Bulk Diff Reports](bulkdiff.md) are
also available as context menu options by opening the menu over a package name
in any report.

All reports share some common functionality:

  - Hovering your mouse over package names and markup like `[S]` or `[X]` will
    display a hover popup describing what that item is

  - The report header tells you the date and time that the report was created,
    so you can tell if the information is still relevant to you or not

  - The contents of the report can be refreshed to bring them up to date if
    things are changing in the background or since the report was first created

  - Package names (and in many cases override names) are displayed in the
    [Symbol List](https://docs.sublimetext.io/guide/usage/file-management/navigation.html#goto-anything){: target="_blank" class="external-link" },
    allowing you to quickly jump to a location by name

  - Package and override names (in reports that contain them) support a context
    menu that provides commands that apply to that package or override
