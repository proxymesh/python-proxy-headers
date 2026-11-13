#!/usr/bin/env bash
# Stop hook: lint the diff against origin/main.
# Cursor passes a JSON event on stdin. Prints a follow-up message
# when lint fails and loop_count is below 2, otherwise {}.
# Usage: .cursor/hooks/lint-on-stop.sh

set -euo pipefail

readonly MAX_LOOP=2

# Print a message to stderr.
err() {
  echo "$*" >&2
}

# Move to the repository root.
cd_repo_root() {
  local root
  root="$(git rev-parse --show-toplevel)"
  cd "$root" || exit 1
}

# Read loop_count from the hook event JSON.
read_loop_count() {
  local input="$1"
  printf '%s' "$input" | python3 -c '
import json
import sys
data = json.load(sys.stdin)
value = data.get("loop_count") or 0
print(int(value))
'
}

# Print the stop-hook response as JSON.
emit_response() {
  local lint_status="$1"
  local loop_count="$2"
  local output="$3"
  if [[ "$lint_status" -eq 0 || "$loop_count" -ge "$MAX_LOOP" ]]; then
    printf '%s\n' '{}'
    return 0
  fi
  printf '%s' "$output" | python3 -c '
import json
import sys
text = sys.stdin.read()[-4000:]
msg = "scripts/lint.sh --changed failed:\n" + text
print(json.dumps({"followup_message": msg}))
'
}

# Lint the diff and print the hook response.
main() {
  local input loop_count output
  local status=0
  input="$(cat)"
  loop_count="$(read_loop_count "$input")"
  cd_repo_root
  output="$(scripts/lint.sh --changed 2>&1 </dev/null)" || status=$?
  emit_response "$status" "$loop_count" "$output"
}

main "$@"
