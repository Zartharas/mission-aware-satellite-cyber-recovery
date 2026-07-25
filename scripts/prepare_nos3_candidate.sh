#!/usr/bin/env bash
set -euo pipefail

NOS3_REPOSITORY="https://github.com/nasa/nos3.git"
NOS3_COMMIT="5a3bdee6be9a2c67fdf994ae6db56d5c60395302"
NOS3_IMAGE="ivvitc/nos3-64:20260619"
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
EXTERNAL_ROOT="$PROJECT_ROOT/external"
NOS3_DIR="$EXTERNAL_ROOT/nos3"
LOCK_FILE="$PROJECT_ROOT/artifacts/nos3-submodule-lock.txt"

mkdir -p "$EXTERNAL_ROOT" "$PROJECT_ROOT/artifacts"

if [[ ! -d "$NOS3_DIR/.git" ]]; then
  echo "Cloning NOS3 into ignored external directory..."
  git clone --no-checkout "$NOS3_REPOSITORY" "$NOS3_DIR"
fi

echo "Fetching selected NOS3 commit..."
git -C "$NOS3_DIR" fetch --prune origin "$NOS3_COMMIT"
git -C "$NOS3_DIR" checkout --detach "$NOS3_COMMIT"

echo "Initializing recursive submodules..."
git -C "$NOS3_DIR" submodule sync --recursive
git -C "$NOS3_DIR" submodule update --init --recursive

{
  echo "recorded_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "nos3_repository=$NOS3_REPOSITORY"
  echo "nos3_commit=$(git -C "$NOS3_DIR" rev-parse HEAD)"
  echo "nos3_describe=$(git -C "$NOS3_DIR" describe --always --dirty 2>/dev/null || true)"
  echo "nos3_worktree_status_begin"
  git -C "$NOS3_DIR" status --short
  echo "nos3_worktree_status_end"
  echo "submodules_begin"
  git -C "$NOS3_DIR" submodule status --recursive
  echo "submodules_end"
  echo "candidate_image=$NOS3_IMAGE"
} > "$LOCK_FILE"

if [[ "${PULL_IMAGE:-0}" == "1" ]]; then
  echo "Pulling candidate NOS3 image..."
  docker pull "$NOS3_IMAGE"
fi

if docker image inspect "$NOS3_IMAGE" >/dev/null 2>&1; then
  digest="$(docker image inspect "$NOS3_IMAGE" --format '{{join .RepoDigests ","}}')"
  echo "resolved_image_digests=$digest" >> "$LOCK_FILE"
else
  echo "resolved_image_digests=not_pulled" >> "$LOCK_FILE"
fi

if [[ -n "$(git -C "$NOS3_DIR" status --porcelain)" ]]; then
  echo "[FAIL] NOS3 checkout is not clean after preparation."
  exit 1
fi

echo
echo "[OK] NOS3 candidate prepared at: $NOS3_DIR"
echo "[OK] Lock inventory written to: $LOCK_FILE"
echo
echo "Review the lock file before committing it."
echo "To pull and resolve the candidate image digest, run:"
echo "  PULL_IMAGE=1 bash scripts/prepare_nos3_candidate.sh"
