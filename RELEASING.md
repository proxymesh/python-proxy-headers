# Releasing

## Cut a release

1. On `main`, write the notes under `## Unreleased` in `CHANGELOG.md` and merge them.
2. Actions → **Prepare release** → **Run workflow** on `main`.
3. Set **version** to `X.Y.Z`, or to `patch`, `minor`, or `major`.
4. The workflow bumps `pyproject.toml` and `docs/conf.py`, moves Unreleased to `## X.Y.Z - YYYY-MM-DD`, runs the release checks, and builds the sdist and wheel. It then opens a pull request titled `Release X.Y.Z` from `release/X.Y.Z`. The body is that changelog section.
5. Merge the pull request into `main`.

A pull request opened with `GITHUB_TOKEN` does not start `pull_request` workflows, so Prepare release runs the checks before it pushes. A release pull request opened by hand uses the same publish path: branch `release/X.Y.Z`, both version manifests, and a dated changelog section. **Release check** runs on that pull request.

## What runs

### Prepare release

`.github/workflows/prepare-release.yml` on `workflow_dispatch`, from `main`, runner `ubuntu-24.04`.

Version manifests:

- `pyproject.toml` field `version`
- `docs/conf.py` field `release`

### Release check

The **Release check** job in `.github/workflows/publish.yml` runs on pull requests to `main`. It checks that the version manifests match, that `CHANGELOG.md` has `## X.Y.Z - YYYY-MM-DD` for that version, and that a `release/*` branch name matches it. It builds the sdist and wheel.

Don't make Release check a required check: release PRs are opened with GITHUB_TOKEN, so it doesn't run on them unless you close and reopen the PR.

### Publish

A push to `main` looks up the pull request for that commit. When the pull request
came from `release/X.Y.Z`, the **publish** job builds the package and uploads it
to PyPI with the existing trusted publisher and the GitHub environment `pypi`
(unchanged). A version that is already on PyPI fails the upload. The
**github-release** job then runs `gh release view vX.Y.Z` or creates that
release. The notes are the changelog section.

## One-time owner setup

1. Settings → Actions → General → Workflow permissions: allow GitHub Actions to
   create pull requests. Dependabot auto-merge already needs that.

## Tags

Tags are `vX.Y.Z`. Existing tags `v0.1.0` through `v0.2.4` already use that form and stay as they are.
