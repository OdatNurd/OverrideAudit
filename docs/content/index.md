---
title: About
description: Easily Manage Your Sublime Text Package Overrides
---

# About OverrideAudit

A common practice amongst Sublime Text users is the creation of a
[package override](terminology/overrides.md); a file that is used to modify or
augment the behavior of an existing package to tweak how it works, allowing you
to make Sublime Text truly your own. Overrides allow you to easily "patch" a
package to your liking without having to modify the contents of the package
itself. Power users use overrides for a variety of reasons, and even newer
Sublime Text users sometimes create overrides without being aware that they're
doing it.

While powerful, overrides do have a drawback that can often catch you unaware.
When an override is present, Sublime Text uses it unconditionally, ignoring the
original package file completely. If the author of the package updates it,
you're not told. This could make you miss out on important new features or bug
fixes, or worse.

OverrideAudit was designed to help protect you from these problems. Behind the
scenes, a check is done every time Sublime or one of your packages is updated
to ensure that your overrides are still relevant. With OverrideAudit you can
take a hands on approach to working with your overrides, or just let the
automated checks help keep you abreast of potential problems.

Whether you are a Sublime Text power user with a ton of overrides or even just
a casual user who wants the peace of mind of knowing that you're not missing
out on any package changes, OverrideAudit has you covered.


## License

OverrideAudit is licensed under the MIT License, is fully open source and
freely available. It is available for all platforms supported by Sublime Text,
and operates identically regardless of platform.

```
The MIT License (MIT)

Copyright 2017-2025 Terence Martin

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

```

## Credits

OverrideAudit is primarily developed by
[Terence Martin](https://github.com/OdatNurd){: target="_blank" class="external-link" },
but would not be possible without inspiration, creative input, and extensive
design help from
[Keith Hall](https://github.com/keith-hall){: target="_blank" class="external-link" },
whose assistance and direction are greatly appreciated.

A debt of gratitude is also owed to
[Guillermo López-Anglada](https://github.com/guillermooo){: target="_blank" class="external-link" }
and
[FichteFoll](https://github.com/FichteFoll){: target="_blank" class="external-link" },
whose work on the
[Sublime Text Unofficial Documentation](https://docs.sublimetext.io/){: target="_blank" class="external-link" }
provide invaluable information about Sublime Text and its inner workings.

This documentation uses
[Material for MkDocs](https://squidfunk.github.io/mkdocs-material/){: target="_blank" class="external-link" }.
