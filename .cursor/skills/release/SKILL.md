---
name: release
description: >-
  Cuts a release with the Prepare release workflow. That workflow opens a
  release/VERSION pull request for a person to merge. Merging publishes to
  PyPI and tags vVERSION. Use when the user invokes /release, /release VERSION,
  asks for a release PR, version bump, or release automation.
---

# Release

Follow `RELEASING.md` at the repository root. Leave the pull request for a person to merge.

## Version

Read `[project].version` in `pyproject.toml`. `/release` with no version means `patch`. `/release X.Y.Z` uses that version. The value is `X.Y.Z`, `patch`, `minor`, or `major`.

## Preconditions

- `## Unreleased` in `CHANGELOG.md` on `main` already contains the release notes.
- `gh` CLI authenticated.
- Prepare release is on `main` (`.github/workflows/prepare-release.yml`).

## Steps

1. Run Prepare release from `main`:

   ```bash
   gh workflow run "Prepare release" --ref main -f version=VERSION
   ```

2. The workflow runs the version, changelog, and package checks, then opens `Release X.Y.Z` from `release/X.Y.Z`. A pull request it opens does not start `pull_request` workflows.
3. Merging publishes to PyPI, tags `vX.Y.Z`, and creates the GitHub Release.

If Prepare release is not on `main` yet, make the same edits by hand: set `pyproject.toml` `version` and `docs/conf.py` `release`, move `## Unreleased` to `## X.Y.Z - YYYY-MM-DD`, push `release/X.Y.Z`, and open the pull request with that changelog section as the body.

Git identity for those hand edits: `cursor@proxymesh.com` / `Cursor`.
