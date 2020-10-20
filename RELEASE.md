Release Checklist
=================

This file contains the checklist of steps to take while executing a release,
since many of these changes require modifications to files right at the point
of release that cannot (or should not) be modified ahead of time.

# Documentation Update

These ensure that the web documentation and associated web pages are up to date
for the new release.

 * Update the version banner on the main page
 * Update web ChangeLog
 * Modify web documentation as appropriate


# Code Update

These ensure that package content meant for distribution by Package Control is
up to date for the release.

 * Update README.md to document any new features that have been added
 * Update CHANGELOG.md for all new features and update date
 * New file in messages/ for PackageControl updates
 * Update messages.json to reference new message file
 * Merge branch to `stable`
 * Tag release with -a (message: "Release Version x.x.x")
 * Push tag and new stable branch

# GitHub

The final step is to draft a new release based on the newly pushed tag to keep
the release list on GitHub up to date.
