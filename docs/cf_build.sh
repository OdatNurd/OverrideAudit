#!/bin/bash -e

### ----------------------------------------------------------------------------
### This script triggers the documentation build for Cloudflare Pages.
###
### Cloudflare does a shallow, head-only clone, but we want to have a full clone
### since one of our plugins uses the git history to determine the date on which
### each help file was last modified.
###
### Further, we want the whole of the build and all of the configuration for it
### to appear solely within the documentation folder, but by setting the build
### root to that folder, Cloudflare will not set up the required libraries
### automatically, and the build can no longer see the git repository due to
### (presumably) the chroot used.
###
### This script ensures that the current directory is the directory in which it
### exists, and then un-shallows the repository and installs the library before
### continuing.
### ----------------------------------------------------------------------------


echo "== [ Changing to the documentation directory ] =="
cd $(dirname $0)

echo "== [ Unshallowing the git clone ] =="
# If for any reason Cloudflare didn't have a shallow clone, the unshallow will
# fail; in that case, just use a regular fetch
git fetch --unshallow || git fetch --all

echo "== [ Installing Python libraries ] =="
pip install -r requirements.txt

echo "== [ Building documentation ] =="
mkdocs build
