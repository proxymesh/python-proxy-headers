#!/usr/bin/env bash
# Run every repo lint check. CI, the stop hook and agents all run this.
# Install the tools first with scripts/install-lint-tools.sh.

set -euo pipefail

failed=()

err() {
  echo "$*" >&2
}

# Run a check and remember its name if it fails.
check() {
  local name="$1"
  shift
  "$@" || failed+=("${name}")
}

# Fail on real ProxyMesh proxy hosts; docs. and www. are allowed.
check_hostnames() {
  ! git grep --untracked -nIoE '[a-z0-9-]+\.proxymesh\.com' |
    grep -vE ':(docs|www)\.proxymesh\.com$'
}

main() {
  export PATH="${HOME}/.local/bin:${PATH}"
  cd "$(git rev-parse --show-toplevel)"
  local -a sh_files
  mapfile -t sh_files < <(git ls-files -co --exclude-standard '*.sh')

  check actionlint actionlint
  check zizmor zizmor --quiet --offline .github/workflows
  check shellcheck shellcheck "${sh_files[@]}"
  check shfmt shfmt -d -i 2 -ci "${sh_files[@]}"
  check ruff ruff check
  check hostnames check_hostnames

  if ((${#failed[@]} > 0)); then
    err "lint failed: ${failed[*]}"
    exit 1
  fi
}

main "$@"
