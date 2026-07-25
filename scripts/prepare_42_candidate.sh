#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FORTYTWO_DIR="$ROOT_DIR/external/fortytwo"
LOCK_FILE="$ROOT_DIR/artifacts/fortytwo-lock.txt"
LOG_DIR="$ROOT_DIR/logs/wp4"
FORTYTWO_REPOSITORY="https://github.com/nasa-itc/42.git"
FORTYTWO_REF="${FORTYTWO_REF:-dev_20260403}"
PINNED_IMAGE="ivvitc/nos3-64@sha256:06aa945988a7770b759022c2e1f6f2531818c087fe41a4739d3a3a7f2a9dcce2"

mkdir -p "$ROOT_DIR/external" "$ROOT_DIR/artifacts" "$LOG_DIR"

if ! docker info >/dev/null 2>&1; then
  echo "[ERROR] Docker daemon is not reachable." >&2
  exit 1
fi

if ! docker image inspect "$PINNED_IMAGE" >/dev/null 2>&1; then
  echo "[ERROR] Pinned NOS3 image digest is not present locally: $PINNED_IMAGE" >&2
  exit 1
fi

if [[ ! -d "$FORTYTWO_DIR/.git" ]]; then
  echo "Cloning 42 into ignored external directory..."
  git clone "$FORTYTWO_REPOSITORY" "$FORTYTWO_DIR"
fi

TARGET="${FORTYTWO_COMMIT:-}"
if [[ -z "$TARGET" && -f "$LOCK_FILE" ]]; then
  TARGET="$(awk -F= '$1=="fortytwo_commit" {print $2}' "$LOCK_FILE" | tail -n 1)"
fi

if [[ -n "$TARGET" ]]; then
  echo "Using previously resolved 42 commit: $TARGET"
  if ! git -C "$FORTYTWO_DIR" cat-file -e "$TARGET^{commit}" 2>/dev/null; then
    git -C "$FORTYTWO_DIR" fetch origin "$TARGET"
  fi
else
  echo "Resolving 42 reference: $FORTYTWO_REF"
  git -C "$FORTYTWO_DIR" fetch origin "$FORTYTWO_REF"
  TARGET="$(git -C "$FORTYTWO_DIR" rev-parse FETCH_HEAD)"
fi

git -C "$FORTYTWO_DIR" checkout --detach "$TARGET"
git -C "$FORTYTWO_DIR" submodule sync --recursive
git -C "$FORTYTWO_DIR" submodule update --init --recursive

if [[ -n "$(git -C "$FORTYTWO_DIR" status --short)" ]]; then
  echo "[ERROR] 42 checkout is not clean before build." >&2
  git -C "$FORTYTWO_DIR" status --short >&2
  exit 1
fi

FORTYTWO_COMMIT_RESOLVED="$(git -C "$FORTYTWO_DIR" rev-parse HEAD)"
FORTYTWO_DESCRIBE="$(git -C "$FORTYTWO_DIR" describe --always --dirty --tags 2>/dev/null || git -C "$FORTYTWO_DIR" rev-parse --short HEAD)"
IMAGE_ID="$(docker image inspect "$PINNED_IMAGE" --format '{{.Id}}')"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
LOG_FILE="$LOG_DIR/fortytwo-build-$STAMP.log"

cat > "$LOCK_FILE" <<EOF
recorded_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)
fortytwo_repository=$FORTYTWO_REPOSITORY
fortytwo_requested_ref=$FORTYTWO_REF
fortytwo_commit=$FORTYTWO_COMMIT_RESOLVED
fortytwo_describe=$FORTYTWO_DESCRIBE
fortytwo_worktree_status_begin
$(git -C "$FORTYTWO_DIR" status --short)
fortytwo_worktree_status_end
fortytwo_build_status=PENDING
builder_image=$PINNED_IMAGE
builder_image_id=$IMAGE_ID
build_log=$LOG_FILE
EOF

echo "[OK] Exact 42 commit frozen before build: $FORTYTWO_COMMIT_RESOLVED"
echo "Building 42 with the pinned NOS3 image and no network access..."

docker run --rm \
  --platform linux/amd64 \
  --network none \
  --user "$(id -u):$(id -g)" \
  -e HOME=/tmp \
  -v "$FORTYTWO_DIR:$FORTYTWO_DIR" \
  -w "$FORTYTWO_DIR" \
  "$PINNED_IMAGE" \
  bash -lc 'set -euo pipefail; make clean >/dev/null 2>&1 || true; make -j"$(nproc)"' \
  2>&1 | tee "$LOG_FILE"

if [[ ! -x "$FORTYTWO_DIR/42" ]]; then
  echo "[ERROR] Expected 42 executable was not produced." >&2
  exit 1
fi

FORTYTWO_SHA256="$(shasum -a 256 "$FORTYTWO_DIR/42" | awk '{print $1}')"

cat > "$LOCK_FILE" <<EOF
recorded_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)
fortytwo_repository=$FORTYTWO_REPOSITORY
fortytwo_requested_ref=$FORTYTWO_REF
fortytwo_commit=$FORTYTWO_COMMIT_RESOLVED
fortytwo_describe=$FORTYTWO_DESCRIBE
fortytwo_worktree_status_begin
$(git -C "$FORTYTWO_DIR" status --short)
fortytwo_worktree_status_end
fortytwo_build_status=PASS
fortytwo_binary_sha256=$FORTYTWO_SHA256
builder_image=$PINNED_IMAGE
builder_image_id=$IMAGE_ID
build_log=$LOG_FILE
EOF

echo ""
echo "[OK] 42 prepared at: $FORTYTWO_DIR"
echo "[OK] Exact commit: $FORTYTWO_COMMIT_RESOLVED"
echo "[OK] Binary SHA-256: $FORTYTWO_SHA256"
echo "[OK] Lock written to: $LOCK_FILE"
echo "FORTYTWO_PREPARATION_STATUS=PASS"
