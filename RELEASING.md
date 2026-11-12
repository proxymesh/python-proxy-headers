# Releasing

## Cut a release

1. On `main`, write the notes under `## Unreleased` in `CHANGELOG.md` and merge them.
2. Actions → **Prepare release** → **Run workflow** on `main`.
3. Set **version** to `X.Y.Z`, or to `patch`, `minor`, or `major`. The next release is a minor, `0.3.0`, because `main` no longer supports Python 3.8 or 3.9.
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

### Publish

A push to `main` looks up the pull request for that commit. When the pull request came from `release/X.Y.Z`, the **publish** job builds the package and uploads it to PyPI with trusted publishing (OIDC) in the GitHub environment `release`. A version that is already on PyPI fails the upload. The **github-release** job then runs `gh release view vX.Y.Z` or creates that release. The notes are the changelog section.

## One-time owner setup

Do this before the next `release/*` merge. This change does not edit repository or PyPI settings.

1. Create a GitHub environment named `release` (Settings → Environments). Optional: required reviewers. Allow deployments from `main`.
2. On PyPI, add a trusted publisher for [python-proxy-headers](https://pypi.org/manage/project/python-proxy-headers/settings/publishing/):
   - Owner: `proxymesh`
   - Repository: `python-proxy-headers`
   - Workflow: `publish.yml`
   - Environment: `release`
3. Publishing already uses OIDC with the GitHub environment `pypi`. After one release succeeds with `release`, remove the trusted publisher whose environment is `pypi`, then delete the `pypi` environment if nothing else uses it.
4. The workflows have no PyPI API token. Delete a `PYPI_API_TOKEN` secret if one is stored on the repository or the `pypi` environment.
5. Settings → Actions → General → Workflow permissions: allow GitHub Actions to create pull requests. Dependabot auto-merge already needs that.

## Tags

Tags are `vX.Y.Z`. Existing tags `v0.1.0` through `v0.2.4` already use that form and stay as they are.
