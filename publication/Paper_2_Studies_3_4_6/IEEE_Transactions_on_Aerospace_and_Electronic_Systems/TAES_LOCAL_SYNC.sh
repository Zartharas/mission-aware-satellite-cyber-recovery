#!/usr/bin/env bash
set -euo pipefail

REPO_EXPECTED="Zartharas/mission-aware-satellite-cyber-recovery"
RELATIVE_PACKAGE="publication/Paper_2_Studies_3_4_6/IEEE_Transactions_on_Aerospace_and_Electronic_Systems"
DESTINATION="${1:-$HOME/Downloads/TAES_Paper_2_Submission}"

printf '%s\n' "============================================================"
printf '%s\n' "TAES PAPER 2 LOCAL SYNC AND PORTAL-STAGING HELPER"
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
  echo "Commit, stash, or otherwise resolve them before running this sync helper."
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

mkdir -p "$DESTINATION"
rsync -a --delete --exclude 'PORTAL_UPLOAD/' "$PACKAGE/" "$DESTINATION/"

PORTAL_DIR="$DESTINATION/PORTAL_UPLOAD"
mkdir -p "$PORTAL_DIR"
find "$PORTAL_DIR" -mindepth 1 -maxdepth 1 -type f -delete

UPLOAD_CANDIDATES=(
  "TAES_MANUSCRIPT.pdf"
  "TAES_SUPPLEMENTARY_MATERIAL.zip"
  "TAES_SUPPLEMENTARY_README.pdf"
  "TAES_SUPPLEMENTARY_README.txt"
)

for name in "${UPLOAD_CANDIDATES[@]}"; do
  if [[ -f "$PACKAGE/$name" ]]; then
    cp -p "$PACKAGE/$name" "$PORTAL_DIR/$name"
  fi
done

(
  cd "$DESTINATION"
  find . -type f \
    ! -path './PORTAL_UPLOAD/*' \
    ! -name 'LOCAL_SYNC_SHA256.txt' \
    -print0 \
    | sort -z \
    | xargs -0 shasum -a 256 \
    > LOCAL_SYNC_SHA256.txt
)

echo
echo "canonical_package=$PACKAGE"
echo "local_copy=$DESTINATION"
echo "portal_upload_staging=$PORTAL_DIR"
echo
echo "Tracked TAES package status:"
git status --short -- "$RELATIVE_PACKAGE"

echo
echo "Local portal-upload candidates currently present:"
find "$PORTAL_DIR" -maxdepth 1 -type f -print | sort

echo
echo "Local sync SHA-256 manifest:"
echo "$DESTINATION/LOCAL_SYNC_SHA256.txt"

echo
echo "SYNC_RESULT=PASS"
echo "NOTE: PORTAL_UPLOAD may remain empty until final publisher-facing files are created and frozen."
