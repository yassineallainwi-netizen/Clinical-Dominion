#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PROJECT_DIR="$ROOT_DIR"
RENPY_BIN="${RENPY_BIN:-}"

if [[ -z "$RENPY_BIN" ]]; then
  if command -v renpy >/dev/null 2>&1; then
    RENPY_BIN="$(command -v renpy)"
  fi
fi

if [[ -z "$RENPY_BIN" || ! -x "$RENPY_BIN" ]]; then
  echo "Ren'Py SDK CLI not found."
  echo "Set RENPY_BIN to your SDK launcher, e.g.:"
  echo "  export RENPY_BIN=/path/to/renpy.sh"
  echo "Then run: tools/run_renpy_checks.sh"
  exit 2
fi

echo "Using Ren'Py CLI: $RENPY_BIN"
"$RENPY_BIN" "$PROJECT_DIR" lint
"$RENPY_BIN" "$PROJECT_DIR" compile --compile
"$RENPY_BIN" "$PROJECT_DIR" test

echo "Ren'Py lint/compile/test checks passed."
