# Agent instructions

Read `.cursorrules` too (git identity, PR footer rule).

## Checks (run before every push)
- `scripts/lint.sh --changed` must pass. CI runs `scripts/lint.sh`.
  The tools are preinstalled by `scripts/install-lint-tools.sh`; never
  download linters yourself.
- Tests: `python test_header_security.py && python test_httpx_guard.py &&
  python test_client_internals.py`.
- Prove it works: paste the command and its output for any behavior you
  claim. CI green alone is not proof.

## Context and CI
- Never print full CI logs or whole large files. Wait for CI with the
  ci-watcher subagent, or `gh pr checks --watch --fail-fast > /dev/null`
  then `gh run view RUN_ID --log-failed | tail -n 80`.
- For the same edit in several places, write and run a small script
  (sed, python) instead of many single edits, and show the script.
- Rewrite a file in one edit when you change most of it.

## Subagents
- After each push: hand CI waiting to `ci-watcher`.
- When `scripts/lint.sh` fails: hand the findings to `lint-fixer`, then read
  its diff before pushing.
- Workflow edits you can fully specify (pins, timeouts, permissions, env):
  `ci-workflow`. Designing a workflow (new jobs, release flow) stays with you.
- Launch subagents only on composer-2.5 (standard speed) or grok-4.7.
  No screenshots or computer use unless the task asks.

## Code standards (the owner rejects PRs that miss these)
- Follow this repo's AGENTS.md / .cursorrules / .cursor/rules and PEP 8, the Google Python Style Guide and the Google Shell Style Guide. Run the repo's linters on changed files and fix everything.
- Imports at the top of the module. No imports inside functions, methods or class bodies. A guarded try/except ImportError at module top is fine where versions truly differ.
- No classes or functions defined inside functions (no class factories) unless there is a concrete reason you state in the PR body.
- Simple, direct code. No defensive scaffolding: no getattr/hasattr fallback chains for names that exist in every supported version, no runtime contract/signature checks, no debug/introspection helpers. Check what the supported versions actually provide and import it directly; tests and CI catch breakage.
- DRY with judgment: reuse existing helpers, no duplicate helpers, no thin wrappers, no single-caller helpers extracted for neatness, no dead code. Grep for unused functions before finishing.
- Match existing patterns and naming in the repo; smallest diff that does the job. Don't reformat or restructure unrelated code.
- Logging: lazy args (logger.info('x %s', y)), never f-strings in log calls. Retries: use the repo's retry library, not hand-rolled loops.
- Tests: cover the behavior change, reuse existing test layout and fixtures, no giant harnesses when a focused test works.
- Use standard linters and tools instead of writing custom checkers, dev servers or check runners.
- Shell scripts follow the Google Shell Style Guide (main function, set -euo pipefail, quoted vars, err to stderr) and pass shellcheck + shfmt -i 2 -ci.
- Workflows: actions pinned to full SHAs with version comments, ubuntu-24.04, read-only default permissions with write only where needed, persist-credentials: false unless pushing, timeouts, no ${{ }} inside run:, dependabot for github-actions; pass actionlint and zizmor.
- CI: extend existing workflows before adding new ones. A new workflow must justify itself in the PR body and stay small: no huge matrices (lowest supported + current stable + latest/master is usually enough), no pre-release runtimes, no duplicated steps or duplicate scheduled jobs.
- Docs/examples: generic placeholders only; never real internal hostnames or credentials.
- One concern per PR, ideally under ~400 changed lines. Say what you'd split if it's bigger.
- Before finishing, re-read your full diff as a strict reviewer and fix anything this list would flag. Report per-file line counts.

Owner rule (all ProxyMesh repos): never use specific ProxyMesh proxy server domains (any *.proxymesh.com proxy host) in code, docs, examples, tests, changelogs or PR bodies. Use a generic placeholder such as proxy.example.com and link https://docs.proxymesh.com/.

## Rules and what enforces them
| Rule | Enforced by |
|---|---|
| Workflows pass actionlint | `scripts/lint.sh` (actionlint), CI lint job |
| No `${{ }}` in `run:`, scoped permissions, no dangerous triggers | zizmor in `scripts/lint.sh` |
| Shell scripts: Google Shell Style, shellcheck clean, shfmt -i 2 -ci | shellcheck + shfmt in `scripts/lint.sh` (style parts: review) |
| No real ProxyMesh proxy hostnames | hostname grep in `scripts/lint.sh` |
| Python passes ruff | `ruff check` in `scripts/lint.sh` |
| Imports at module top, no print | review only for now (ruff PLC0415, T201 planned) |
| Actions SHA-pinned with exact `# vX.Y.Z` | review (actionlint does not check pins) |
| Focused PRs under ~400 lines, no version bumps | review |

When a reviewer corrects the same mistake twice, add a check that fails on
it (lint rule, grep in lint.sh, or test) and add a row here. Docs-only rules
are for judgment calls nothing can check.
