# Changelog

## 0.2.4 - 2026-11-09

### Security

- Restrict the pycurl high-level API to HTTP and HTTPS. `file://` and other non-HTTP schemes are rejected, and libcurl protocols are pinned to HTTP(S), so those fetches cannot bypass the proxy (#36).
- Reject CR, LF, and NUL in origin header names and values, and require the HTTP method to be a single token, so caller-controlled input cannot inject extra request lines (#36).

### Dependencies and CI

- Group weekly Dependabot updates for pip and GitHub Actions, pin `dependabot/fetch-metadata` to a commit SHA, and auto-merge Dependabot version updates (including majors) after checks pass (#29, #31).
- Pin GitHub Actions jobs to `ubuntu-24.04` (#33).
- Bump `actions/upload-artifact` to 7.0.2 and `actions/download-artifact` to 8.0.2 (#32).
- Bump `actions/setup-python` to 7.1.0 and `pypa/gh-action-pypi-publish` to 1.14.3 (#35).
