#!/usr/bin/env bash
# install.sh - one-prompt AGI runtime installer (macOS / Linux)
#
#   curl -fsSL https://github.com/Megasolid/AGI/releases/download/dna-GCACGAGGCTGT/install.sh | bash
#
# Downloads the runtime from a *pinned release*, verifies it against the released SHA256SUMS before
# extracting, seeds the fresh state, cold-boots, then opens the login screen. No sudo, nothing
# written outside $DEST.
#
# Manual, safer form (review first):
#   curl -fsSL .../install.sh -o install.sh && bash install.sh
set -eu

VERSION="${AGI_VERSION:-dna-GCACGAGGCTGT}"
DEST="${AGI_DEST:-$HOME/AGI}"
BASE_URL="${AGI_BASE_URL:-https://github.com/Megasolid/AGI/releases/download/$VERSION}"
NO_BOOT="${AGI_NO_BOOT:-0}"
NO_LAUNCH="${AGI_NO_LAUNCH:-0}"
RESUME="${AGI_RESUME:-0}"
ZIP="agi-runtime-$VERSION.zip"

say() { printf '%s\n' "$*"; }

# ---- prerequisites -------------------------------------------------------------
PY="${AGI_PYTHON:-}"
for cand in python3 python; do
  [ -n "$PY" ] && break
  if command -v "$cand" >/dev/null 2>&1; then
    if "$cand" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)' 2>/dev/null; then
      PY="$cand"; break
    fi
  fi
done
[ -n "$PY" ] || { say "Python 3.11+ is required. Install it and re-run."; exit 1; }
say "AGI install: $VERSION -> $DEST (python: $PY)"

RESUMING=0
if [ -d "$DEST" ] && [ -n "$(ls -A "$DEST" 2>/dev/null || true)" ]; then
  if [ "$RESUME" = "1" ] && [ -f "$DEST/.agi-runtime-manifest.json" ]; then
    RESUMING=1; say "resuming an extracted runtime at $DEST (download/extract skipped)"
  else
    say "Destination '$DEST' exists and is not empty. Set AGI_RESUME=1 to continue an interrupted install,"
    say "or set AGI_DEST to a new path / remove it."; exit 1
  fi
fi

# ---- download + verify --------------------------------------------------------
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
if [ "$RESUMING" = "1" ]; then
  EXPECTED=""; ACTUAL=""
else
fetch() {  # $1 url  $2 output - retries, because a single transient failure must not abort an install
  i=1
  while [ "$i" -le 4 ]; do
    if command -v curl >/dev/null 2>&1; then
      curl -fsSL --retry 2 "$1" -o "$2" && return 0
    elif command -v wget >/dev/null 2>&1; then
      wget -qO "$2" "$1" && return 0
    else
      say "need curl or wget"; exit 1
    fi
    sleep $((i * 2)); i=$((i + 1))
  done
  say "download failed after 4 attempts: $1"; exit 1
}
# GitHub serves extensionless asset names inconsistently; the release publishes SHA256SUMS.txt
if ! fetch "$BASE_URL/SHA256SUMS.txt" "$TMP/SHA256SUMS" 2>/dev/null; then
  fetch "$BASE_URL/SHA256SUMS" "$TMP/SHA256SUMS"
fi
fetch "$BASE_URL/$ZIP" "$TMP/$ZIP"
EXPECTED="$(awk -v f="$ZIP" '$2 == f {print $1}' "$TMP/SHA256SUMS" | head -n1)"
[ -n "$EXPECTED" ] || { say "SHA256SUMS does not list $ZIP - refusing to install"; exit 1; }
if command -v sha256sum >/dev/null 2>&1; then ACTUAL="$(sha256sum "$TMP/$ZIP" | awk '{print $1}')"
else ACTUAL="$(shasum -a 256 "$TMP/$ZIP" | awk '{print $1}')"; fi
[ "$EXPECTED" = "$ACTUAL" ] || { say "checksum mismatch (expected $EXPECTED, got $ACTUAL) - refusing"; exit 1; }
say "checksum: OK ($ACTUAL)"

fi
mkdir -p "$DEST"
if [ "$RESUMING" != "1" ]; then
  mkdir -p "$TMP/agi"
  ( cd "$TMP/agi" && "$PY" -m zipfile -e "$TMP/$ZIP" . )
  ( cd "$TMP/agi" && cp -a . "$DEST/" )
fi

# ---- dependency: cryptography (private venv if missing; never the system python) ---
if ! "$PY" -c 'import cryptography' 2>/dev/null; then
  say "cryptography missing: creating a private venv inside the install (no system change)"
  [ -d "$DEST/.venv" ] || "$PY" -m venv "$DEST/.venv" || { say "could not create a venv: $DEST/.venv"; exit 1; }
  if ! "$DEST/.venv/bin/python" -m pip install --quiet --disable-pip-version-check cryptography; then
    say "could not install cryptography. Check the network/proxy, or run:"
    say "  $DEST/.venv/bin/python -m pip install cryptography"
    exit 1
  fi
  PY="$DEST/.venv/bin/python"
  say "venv python: $PY"
fi

# ---- seed + cold boot ---------------------------------------------------------
cd "$DEST"
if [ "$NO_BOOT" != "1" ]; then
  say "bootstrapping state..."
  "$PY" memory/scripts/bootstrap.py run >/dev/null
  say "cold boot..."
  AGI_RAM_ROOT="${AGI_RAM_ROOT:-$HOME/.agi/ram}" "$PY" memory/scripts/bios.py
fi

# ---- open the login screen ----------------------------------------------------
if [ "$NO_LAUNCH" != "1" ]; then
  "$PY" memory/scripts/app.py launch --login || true
else
  say ""
  say "Next:  cd \"$DEST\"; $PY memory/scripts/app.py launch --login"
fi
say "AGI installed at $DEST"
