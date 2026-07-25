#!/usr/bin/env bash
set -euo pipefail

echo "System:"
uname -a
echo

echo "Architecture:"
uname -m
echo

echo "macOS:"
sw_vers || true
echo

for cmd in git python3 docker gh; do
  if command -v "$cmd" >/dev/null 2>&1; then
    echo "[OK] $cmd: $("$cmd" --version 2>/dev/null | head -n 1)"
  else
    echo "[MISSING] $cmd"
  fi
done

echo
echo "Disk space:"
df -h .
