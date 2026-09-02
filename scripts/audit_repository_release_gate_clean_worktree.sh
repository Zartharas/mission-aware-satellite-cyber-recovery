#!/usr/bin/env bash
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || true)"
if [[ -z "$ROOT" || ! -d "$ROOT/.git" ]]; then
  echo "FAIL: run this script from inside the mission-aware-satellite-cyber-recovery Git checkout" >&2
  exit 1
fi

cd "$ROOT"

if [[ -n "$(git status --porcelain --untracked-files=normal)" ]]; then
  echo "FAIL: tracked/untracked working-tree changes are present; clean or preserve them before auditing" >&2
  git status --short >&2
  exit 1
fi

HEAD_SHA="$(git rev-parse HEAD)"
TMP_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/mission-aware-release-gate.XXXXXX")"
WORKTREE="$TMP_ROOT/checkout"
VENV="$TMP_ROOT/venv"

cleanup() {
  set +e
  if [[ -d "$WORKTREE" ]]; then
    git -C "$ROOT" worktree remove --force "$WORKTREE" >/dev/null 2>&1 || true
  fi
  rm -rf "$TMP_ROOT"
}
trap cleanup EXIT INT TERM

echo "============================================================"
echo "MISSION-AWARE REPOSITORY — CLEAN-WORKTREE RELEASE-GATE AUDIT"
echo "============================================================"
echo "source_repo=$ROOT"
echo "source_head=$HEAD_SHA"
echo "audit_worktree=$WORKTREE"

git worktree add --detach "$WORKTREE" "$HEAD_SHA" >/dev/null

python3 -m venv "$VENV"
"$VENV/bin/python" -m pip install --upgrade pip
"$VENV/bin/python" -m pip install -r "$WORKTREE/requirements-dev.txt"

cd "$WORKTREE"
"$VENV/bin/python" scripts/audit_repository_release_gate.py
"$VENV/bin/python" scripts/audit_bibliography_metadata.py

if [[ -n "$(git status --porcelain --untracked-files=normal)" ]]; then
  echo "FAIL: clean-worktree audit produced repository drift" >&2
  git status --short >&2
  exit 1
fi

if [[ "$(git rev-parse HEAD)" != "$HEAD_SHA" ]]; then
  echo "FAIL: audit worktree HEAD drifted" >&2
  exit 1
fi

echo "clean_worktree_release_gate=PASS"
echo "audited_commit=$HEAD_SHA"
