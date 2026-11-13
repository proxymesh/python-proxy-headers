#!/usr/bin/env bash
# Install pinned lint tools into ~/.local/bin.
# Cloud agent Builds and CI both run: bash scripts/install-lint-tools.sh

set -euo pipefail

readonly ACTIONLINT_VERSION="1.7.12"
readonly SHELLCHECK_VERSION="0.11.0"
readonly SHFMT_VERSION="3.14.1"
readonly RUFF_VERSION="0.17.5"
readonly ZIZMOR_VERSION="1.32.0"
readonly BIN_DIR="${HOME}/.local/bin"
readonly GITHUB="https://github.com"

# sha256 of the pinned linux release binaries (amd64, then arm64).
readonly SHELLCHECK_SHA_AMD64="\
b7af85e41cc99489dcc21d66c6d5f3685138f06d34651e6d34b42ec6d54fe6f6"
readonly SHELLCHECK_SHA_ARM64="\
68a8133197a50beb8803f8d42f9908d1af1c5540d4bb05fdfca8c1fa47decefc"
readonly SHFMT_SHA_AMD64="\
76e77641faa025814b77f153b29796b8e6fa2fca03e0c76a691608b86c7ea7bf"
readonly SHFMT_SHA_ARM64="\
5f2db09dae91fca848f7adbdd014632e921a383863a2ad7e0450ad3aba0c6489"

TMP_DIR=""
ARCH_KEY=""

# Print a message to stderr.
err() {
  echo "$*" >&2
}

# Delete the temporary download directory.
cleanup() {
  if [[ -n "${TMP_DIR}" ]]; then
    rm -rf "${TMP_DIR}"
  fi
}

# Choose the release arch tag for this machine.
detect_arch() {
  case "$(uname -m)" in
    x86_64)
      ARCH_KEY="amd64"
      ;;
    aarch64 | arm64)
      ARCH_KEY="arm64"
      ;;
    *)
      err "unsupported architecture: $(uname -m)"
      exit 1
      ;;
  esac
}

# Return 0 when the tool already prints the pinned version.
have_version() {
  local bin="$1"
  local version="$2"
  local out=""
  if ! command -v "$bin" >/dev/null 2>&1; then
    return 1
  fi
  out="$("$bin" --version 2>/dev/null || true)"
  if [[ "$out" != *"$version"* ]]; then
    out="$("$bin" -version 2>/dev/null || true)"
  fi
  [[ "$out" == *"$version"* ]]
}

# Create the download directory on first use.
ensure_tmp() {
  if [[ -z "${TMP_DIR}" ]]; then
    TMP_DIR="$(mktemp -d)"
  fi
}

# Download a URL to a file.
fetch() {
  local url="$1"
  local dest="$2"
  curl -fsSL --retry 3 --retry-delay 2 -o "$dest" "$url"
}

# Fail unless the file has this sha256.
verify_sha256() {
  local file="$1"
  local want="$2"
  local got
  got="$(sha256sum "$file" | awk '{print $1}')"
  if [[ "$got" != "$want" ]]; then
    err "checksum mismatch for $(basename "$file")"
    err "expected ${want}"
    err "got      ${got}"
    return 1
  fi
}

# Install actionlint and verify the release checksums file.
install_actionlint() {
  if have_version actionlint "$ACTIONLINT_VERSION"; then
    echo "actionlint ${ACTIONLINT_VERSION} already installed"
    return 0
  fi
  ensure_tmp
  local name="actionlint_${ACTIONLINT_VERSION}_linux_${ARCH_KEY}.tar.gz"
  local sums="actionlint_${ACTIONLINT_VERSION}_checksums.txt"
  local base="${GITHUB}/rhysd/actionlint/releases/download"
  local line
  base="${base}/v${ACTIONLINT_VERSION}"
  fetch "${base}/${sums}" "${TMP_DIR}/${sums}"
  fetch "${base}/${name}" "${TMP_DIR}/${name}"
  line="$(awk -v n="$name" '$2 == n {print}' "${TMP_DIR}/${sums}")"
  if [[ -z "$line" ]]; then
    err "no checksum for ${name}"
    return 1
  fi
  printf '%s\n' "$line" | (cd "$TMP_DIR" && sha256sum -c -)
  tar -xzf "${TMP_DIR}/${name}" -C "$TMP_DIR" actionlint
  install -m 755 "${TMP_DIR}/actionlint" "${BIN_DIR}/actionlint"
  echo "installed actionlint ${ACTIONLINT_VERSION}"
}

# Install shellcheck from the pinned release tarball.
install_shellcheck() {
  local arch want name base
  if have_version shellcheck "$SHELLCHECK_VERSION"; then
    echo "shellcheck ${SHELLCHECK_VERSION} already installed"
    return 0
  fi
  ensure_tmp
  case "$ARCH_KEY" in
    amd64)
      arch="x86_64"
      want="$SHELLCHECK_SHA_AMD64"
      ;;
    arm64)
      arch="aarch64"
      want="$SHELLCHECK_SHA_ARM64"
      ;;
    *)
      err "unsupported architecture: ${ARCH_KEY}"
      return 1
      ;;
  esac
  name="shellcheck-v${SHELLCHECK_VERSION}.linux.${arch}.tar.gz"
  base="${GITHUB}/koalaman/shellcheck/releases/download"
  base="${base}/v${SHELLCHECK_VERSION}"
  fetch "${base}/${name}" "${TMP_DIR}/${name}"
  verify_sha256 "${TMP_DIR}/${name}" "$want"
  tar -xzf "${TMP_DIR}/${name}" -C "$TMP_DIR"
  install -m 755 \
    "${TMP_DIR}/shellcheck-v${SHELLCHECK_VERSION}/shellcheck" \
    "${BIN_DIR}/shellcheck"
  echo "installed shellcheck ${SHELLCHECK_VERSION}"
}

# Install the shfmt binary after a sha256 check.
install_shfmt() {
  local want name base
  if have_version shfmt "$SHFMT_VERSION"; then
    echo "shfmt ${SHFMT_VERSION} already installed"
    return 0
  fi
  ensure_tmp
  case "$ARCH_KEY" in
    amd64) want="$SHFMT_SHA_AMD64" ;;
    arm64) want="$SHFMT_SHA_ARM64" ;;
    *)
      err "unsupported architecture: ${ARCH_KEY}"
      return 1
      ;;
  esac
  name="shfmt_v${SHFMT_VERSION}_linux_${ARCH_KEY}"
  base="${GITHUB}/mvdan/sh/releases/download/v${SHFMT_VERSION}"
  fetch "${base}/${name}" "${TMP_DIR}/${name}"
  verify_sha256 "${TMP_DIR}/${name}" "$want"
  install -m 755 "${TMP_DIR}/${name}" "${BIN_DIR}/shfmt"
  echo "installed shfmt ${SHFMT_VERSION}"
}

# Install pinned ruff and zizmor with pip.
install_python_tools() {
  if have_version ruff "$RUFF_VERSION" &&
    have_version zizmor "$ZIZMOR_VERSION"; then
    echo "ruff ${RUFF_VERSION} and zizmor ${ZIZMOR_VERSION} already installed"
    return 0
  fi
  if ! python3 -c \
    'import sys; raise SystemExit(sys.version_info < (3, 11))'; then
    err "Python 3.11+ is required to install zizmor"
    exit 1
  fi
  python3 -m pip install \
    --user \
    --disable-pip-version-check \
    --break-system-packages \
    "ruff==${RUFF_VERSION}" \
    "zizmor==${ZIZMOR_VERSION}"
  echo "installed ruff ${RUFF_VERSION} and zizmor ${ZIZMOR_VERSION}"
}

# Install every pinned tool.
main() {
  trap cleanup EXIT
  mkdir -p "$BIN_DIR"
  export PATH="${BIN_DIR}:${PATH}"
  detect_arch
  install_actionlint
  install_shellcheck
  install_shfmt
  install_python_tools
}

main "$@"
