---
title: About
description: Easily Manage Your Sublime Text Package Overrides
---

# Introduction

A common practice in Sublime Text is the creation of a [package override](garbage); a file
that is used to modify the behavior of an existing package to work the way that
you want it to work. Overrides allow you to easily "patch" a package to your
liking without having to modify the contents of the package itself. Power users
use overrides for a variety of reasons, and even newer Sublime Text users
sometimes create overrides without being aware that they're doing it.

While powerful, overrides do have a drawback that can often catch you unaware.
When an override is present, Sublime Text uses it unconditionally, ignoring the
original package file completely. If the author of the package updates it,
you're not told. This could make you miss out on important new features or bug
fixes.

OverrideAudit was designed to help protect you from these problems. Behind the
scenes, a check is done every time Sublime or one of your packages is updated.
With OverrideAudit you can take a hands on approach to working with your
overrides, or just let the automated checks help keep you abreast of potential
problems.

Whether you are a Sublime Text power user with a ton of overrides or even just
a casual user who wants the peace of mind of knowing that you're not missing
out on any package changes, OverrideAudit has you covered.


