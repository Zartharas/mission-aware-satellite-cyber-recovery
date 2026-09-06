#!/usr/bin/env bash
set -euo pipefail

REPO_EXPECTED="Zartharas/mission-aware-satellite-cyber-recovery"
RELATIVE_PACKAGE="publication/Paper_2_Studies_3_4_6/IEEE_Transactions_on_Aerospace_and_Electronic_Systems"

printf '%s\n' "============================================================"
printf '%s\n' "TAES PAPER 2 REPOSITORY SYNC AND VERIFY"
printf '%s\n' "============================================================"

if ! REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)"; then
  echo "ERROR: Run this script from inside the mission-aware-satellite-cyber-recovery Git clone."
  exit 1
fi

cd "$REPO_ROOT"

ORIGIN_URL="$(git remote get-url origin 2>/dev/null || true)"
echo "repo_root=$REPO_ROOT"
echo "origin=$ORIGIN_URL"
echo "expected_repo=$REPO_EXPECTED"

if [[ -n "$(git status --porcelain)" ]]; then
  echo "ERROR: Local repository has uncommitted changes."
  echo "Commit, stash, or otherwise resolve them before syncing."
  git status --short
  exit 2
fi

git fetch origin main
git switch main
git pull --ff-only origin main

PACKAGE="$REPO_ROOT/$RELATIVE_PACKAGE"

if [[ ! -d "$PACKAGE" ]]; then
  echo "ERROR: Canonical TAES package folder is missing after pull:"
  echo "$PACKAGE"
  exit 3
fi

if [[ -n "$(git status --porcelain -- "$RELATIVE_PACKAGE")" ]]; then
  echo "ERROR: Canonical TAES package is not clean after pull."
  git status --short -- "$RELATIVE_PACKAGE"
  exit 4
fi

echo
echo "canonical_package=$PACKAGE"
echo "storage_rule=ONE_CANONICAL_COPY_IN_REPOSITORY_ONLY"
echo
echo "Tracked TAES package status:"
git status --short -- "$RELATIVE_PACKAGE"

echo
echo "Publisher-facing files currently present in canonical package:"
for name in \
  TAES_MANUSCRIPT.pdf \
  TAES_SUPPLEMENTARY_MATERIAL.zip \
  TAES_SUPPLEMENTARY_README.pdf \
  TAES_SUPPLEMENTARY_README.txt \
  TAES_COVER_LETTER.pdf \
  TAES_COVER_LETTER.docx; do
  if [[ -f "$PACKAGE/$name" ]]; then
    printf '%s\n' "$PACKAGE/$name"
  fi
done

echo
echo "SYNC_RESULT=PASS"
echo "NOTE: Do not create a Downloads mirror or separate portal-staging copy."
echo "NOTE: When submission files are frozen, upload them directly from the canonical package folder above."
