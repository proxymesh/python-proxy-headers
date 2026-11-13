#!/usr/bin/env bash
# Run the repo lint checks. CI runs this with no arguments.
# Usage: scripts/lint.sh [--changed]
#   --changed  check files that differ from origin/main.

set -euo pipefail

readonly BASE_REF="origin/main"
readonly HOST_RE='[a-z0-9-]+\.proxymesh\.com'

failures=()

# Print a message to stderr.
err() {
  echo "$*" >&2
}

# Stop if the install script has not been run.
require_tools() {
  local tool
  for tool in actionlint zizmor shellcheck shfmt ruff; do
    if ! command -v "$tool" >/dev/null 2>&1; then
      err "missing ${tool}; run scripts/install-lint-tools.sh"
      exit 1
    fi
  done
}

# Print paths that differ from origin/main, including untracked files.
changed_files() {
  git diff --name-only --diff-filter=ACMR "$BASE_REF"
  git ls-files --others --exclude-standard
}

# Print existing paths from stdin whose names end with suffix.
filter_suffix() {
  local suffix="$1"
  local path
  while IFS= read -r path; do
    if [[ -f "$path" && "$path" == *"$suffix" ]]; then
      printf '%s\n' "$path"
    fi
  done
}

# Print workflow files from the argument list.
filter_workflows() {
  local path
  for path in "$@"; do
    if [[ -f "$path" && "$path" == .github/workflows/* ]]; then
      case "$path" in
        *.yml | *.yaml) printf '%s\n' "$path" ;;
      esac
    fi
  done
}

# Run a command and record its name if it fails.
run_check() {
  local name="$1"
  shift
  if ! "$@"; then
    failures+=("$name")
  fi
}

# Lint GitHub Actions workflows.
run_actionlint() {
  local mode="$1"
  shift
  local -a files=()
  if [[ "$mode" == "changed" ]]; then
    mapfile -t files < <(filter_workflows "$@")
    if [[ "${#files[@]}" -eq 0 ]]; then
      return 0
    fi
    run_check "actionlint" actionlint "${files[@]}"
    return 0
  fi
  run_check "actionlint" actionlint
}

# Run zizmor offline on workflows.
run_zizmor() {
  local mode="$1"
  shift
  local -a files=()
  if [[ "$mode" == "changed" ]]; then
    mapfile -t files < <(filter_workflows "$@")
    if [[ "${#files[@]}" -eq 0 ]]; then
      return 0
    fi
    run_check "zizmor" zizmor --offline "${files[@]}"
    return 0
  fi
  run_check "zizmor" zizmor --offline .github/workflows
}

# Run shellcheck and shfmt on shell scripts.
run_shell() {
  local mode="$1"
  shift
  local -a files=()
  if [[ "$mode" == "changed" ]]; then
    mapfile -t files < <(printf '%s\n' "$@" | filter_suffix ".sh")
  else
    mapfile -t files < <(git ls-files | filter_suffix ".sh")
  fi
  if [[ "${#files[@]}" -eq 0 ]]; then
    return 0
  fi
  run_check "shellcheck" shellcheck "${files[@]}"
  run_check "shfmt" shfmt -d -i 2 -ci "${files[@]}"
}

# Return 0 when origin/main's copy of the file also fails format.
format_dirty_on_base() {
  local path="$1"
  if ! git cat-file -e "${BASE_REF}:${path}" 2>/dev/null; then
    return 1
  fi
  if git show "${BASE_REF}:${path}" |
    ruff format --check --stdin-filename "$path" - >/dev/null 2>&1; then
    return 1
  fi
  return 0
}

# Format-check changed Python files.
# Files already unformatted on origin/main belong to the format PR.
check_python_format() {
  local path
  local failed=0
  for path in "$@"; do
    if ruff format --check "$path" >/dev/null 2>&1; then
      continue
    fi
    if format_dirty_on_base "$path"; then
      continue
    fi
    if ! ruff format --check "$path"; then
      failed=1
    fi
  done
  if [[ "$failed" -ne 0 ]]; then
    failures+=("ruff format")
  fi
}

# Language-specific checks. Other repos replace this function.
run_python() {
  local mode="$1"
  shift
  local -a files=()
  if [[ "$mode" == "changed" ]]; then
    mapfile -t files < <(printf '%s\n' "$@" | filter_suffix ".py")
    if [[ "${#files[@]}" -eq 0 ]]; then
      return 0
    fi
    run_check "ruff check" ruff check "${files[@]}"
    check_python_format "${files[@]}"
    return 0
  fi
  run_check "ruff check" ruff check
}

# Return 0 when every proxy host on the line is allowed.
host_allowed() {
  local rest="$1"
  local match label prefix
  while [[ "$rest" =~ ([a-z0-9-]+)\.proxymesh\.com ]]; do
    label="${BASH_REMATCH[1]}"
    match="${label}.proxymesh.com"
    prefix="${rest%%"${match}"*}"
    if [[ "$label" != "docs" && "$label" != "www" ]]; then
      case "$prefix" in
        *@) ;;
        *) return 1 ;;
      esac
    fi
    rest="${rest#*"${match}"}"
  done
  return 0
}

# Fail on real ProxyMesh proxy hostnames.
run_hostnames() {
  local mode="$1"
  shift
  local hits=""
  local line
  local failed=0
  local -a files=()
  if [[ "$mode" == "changed" ]]; then
    local path
    for path in "$@"; do
      if [[ -f "$path" ]]; then
        files+=("$path")
      fi
    done
    if [[ "${#files[@]}" -eq 0 ]]; then
      return 0
    fi
    hits="$(grep -nE -I -H -- "$HOST_RE" "${files[@]}" || true)"
  else
    hits="$(git grep -nE -I -- "$HOST_RE" || true)"
  fi
  while IFS= read -r line; do
    if [[ -z "$line" ]]; then
      continue
    fi
    if host_allowed "$line"; then
      continue
    fi
    err "proxy hostname: ${line}"
    failed=1
  done <<<"$hits"
  if [[ "$failed" -ne 0 ]]; then
    failures+=("proxy hostnames")
  fi
}

# Parse arguments, run every check, then exit 1 if any failed.
main() {
  local mode="all"
  local root
  local -a changed=()
  if [[ "$#" -gt 1 ]]; then
    err "Usage: scripts/lint.sh [--changed]"
    exit 2
  fi
  if [[ "$#" -eq 1 ]]; then
    if [[ "$1" != "--changed" ]]; then
      err "Usage: scripts/lint.sh [--changed]"
      exit 2
    fi
    mode="changed"
  fi
  export PATH="${HOME}/.local/bin:${PATH}"
  export RUFF_CACHE_DIR="${HOME}/.cache/ruff"
  root="$(git rev-parse --show-toplevel)"
  cd "$root" || exit 1
  require_tools
  if [[ "$mode" == "changed" ]]; then
    if ! git rev-parse --verify --quiet "$BASE_REF" >/dev/null; then
      err "missing ${BASE_REF}; fetch it and retry"
      exit 1
    fi
    mapfile -t changed < <(changed_files)
  fi
  run_actionlint "$mode" "${changed[@]}"
  run_zizmor "$mode" "${changed[@]}"
  run_shell "$mode" "${changed[@]}"
  run_python "$mode" "${changed[@]}"
  run_hostnames "$mode" "${changed[@]}"
  if [[ "${#failures[@]}" -gt 0 ]]; then
    err "lint failed: ${failures[*]}"
    exit 1
  fi
}

main "$@"
