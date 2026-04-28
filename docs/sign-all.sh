#!/usr/bin/env bash
#
# sign-all.sh — sign every .shortcut in raw/ and drop the result in signed/.
#
# RUN THIS ON YOUR MAC. macOS only — Linux/Windows don't have `shortcuts`.
#
# Usage:
#   bash docs/sign-all.sh             # sign everything in raw/
#   bash docs/sign-all.sh hello-world # sign only one (no extension)
#
# Output goes to signed/<slug>.shortcut.

set -euo pipefail

# Find the repo root (parent of the docs/ dir this script lives in)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

RAW_DIR="$REPO_ROOT/raw"
SIGNED_DIR="$REPO_ROOT/signed"

# Sanity checks
if [[ "$(uname -s)" != "Darwin" ]]; then
    echo "ERROR: sign-all.sh requires macOS (the 'shortcuts' CLI). You're on $(uname -s)." >&2
    exit 1
fi

if ! command -v shortcuts >/dev/null 2>&1; then
    echo "ERROR: 'shortcuts' CLI not found. It ships with macOS 12+; check your PATH." >&2
    exit 1
fi

if [[ ! -d "$RAW_DIR" ]]; then
    echo "ERROR: raw/ folder not found at $RAW_DIR" >&2
    exit 1
fi

mkdir -p "$SIGNED_DIR"

# Build the list of files to process
shopt -s nullglob
if [[ $# -gt 0 ]]; then
    # Specific slug(s) given on the command line
    files=()
    for slug in "$@"; do
        f="$RAW_DIR/$slug.shortcut"
        if [[ ! -f "$f" ]]; then
            echo "WARN: $f does not exist, skipping" >&2
            continue
        fi
        files+=("$f")
    done
else
    # All shortcuts in raw/
    files=("$RAW_DIR"/*.shortcut)
fi

if [[ ${#files[@]} -eq 0 ]]; then
    echo "Nothing to sign in $RAW_DIR"
    exit 0
fi

ok=0
fail=0
for input in "${files[@]}"; do
    name="$(basename "$input" .shortcut)"
    output="$SIGNED_DIR/$name.shortcut"

    echo "→ $name"

    # Validate first
    if ! plutil -lint "$input" >/dev/null 2>&1; then
        echo "  ✗ plutil -lint failed; skipping"
        fail=$((fail + 1))
        continue
    fi

    # Sign with mode=anyone (no contact embedding)
    if shortcuts sign --mode anyone --input "$input" --output "$output" 2>/dev/null; then
        echo "  ✓ signed → signed/$name.shortcut"
        ok=$((ok + 1))
    else
        echo "  ✗ shortcuts sign failed"
        fail=$((fail + 1))
    fi
done

echo
echo "Done: $ok signed, $fail failed."
echo
if [[ $ok -gt 0 ]]; then
    echo "To import into the Shortcuts app, open one with:"
    echo "  open signed/<name>.shortcut"
    echo
    echo "Or to import all of them:"
    echo "  for f in signed/*.shortcut; do open \"\$f\"; done"
fi

[[ $fail -eq 0 ]]
