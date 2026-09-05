#!/usr/bin/env bash
set -euo pipefail

BRANCH="publication/phase1-jais-primary"
SOURCE_DIR="publication/submission/journal-of-aerospace-information-systems"
DEST_DIR="${1:-$HOME/Documents/JAIS_Paper1_Submission_Package}"

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "ERROR: Run this script from inside the mission-aware-satellite-cyber-recovery Git repository." >&2
  exit 2
fi

if [[ -n "$(git status --porcelain)" ]]; then
  echo "ERROR: Working tree is not clean. Commit, stash, or discard local changes before syncing." >&2
  git status --short >&2
  exit 3
fi

git fetch --prune origin

if git show-ref --verify --quiet "refs/heads/$BRANCH"; then
  git switch "$BRANCH"
else
  git switch --track -c "$BRANCH" "origin/$BRANCH"
fi

git pull --ff-only origin "$BRANCH"

if [[ ! -d "$SOURCE_DIR" ]]; then
  echo "ERROR: JAIS package directory not found: $SOURCE_DIR" >&2
  exit 4
fi

mkdir -p "$DEST_DIR"
rsync -a --delete "$SOURCE_DIR/" "$DEST_DIR/"

printf 'JAIS local package synced.\n'
printf 'Branch: %s\n' "$BRANCH"
printf 'Repository commit: %s\n' "$(git rev-parse HEAD)"
printf 'Local package: %s\n' "$DEST_DIR"

if command -v open >/dev/null 2>&1; then
  open "$DEST_DIR"
fi
