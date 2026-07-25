#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
NOS3_DIR="$ROOT_DIR/external/nos3"
NOS3_LOCK="$ROOT_DIR/artifacts/nos3-submodule-lock.txt"
FORTYTWO_LOCK="$ROOT_DIR/artifacts/fortytwo-lock.txt"
BUILD_LOCK="$ROOT_DIR/artifacts/nominal-build-lock.txt"
LOG_DIR="$ROOT_DIR/logs/wp4"
EXPECTED_NOS3_COMMIT="5a3bdee6be9a2c67fdf994ae6db56d5c60395302"
PINNED_IMAGE="ivvitc/nos3-64@sha256:06aa945988a7770b759022c2e1f6f2531818c087fe41a4739d3a3a7f2a9dcce2"

mkdir -p "$ROOT_DIR/artifacts" "$LOG_DIR"

for required in "$NOS3_LOCK" "$FORTYTWO_LOCK"; do
  if [[ ! -f "$required" ]]; then
    echo "[ERROR] Required lock file is missing: $required" >&2
    exit 1
  fi
done

if [[ ! -d "$NOS3_DIR/.git" ]]; then
  echo "[ERROR] NOS3 checkout is missing: $NOS3_DIR" >&2
  exit 1
fi

if ! docker info >/dev/null 2>&1; then
  echo "[ERROR] Docker daemon is not reachable." >&2
  exit 1
fi

if ! docker image inspect "$PINNED_IMAGE" >/dev/null 2>&1; then
  echo "[ERROR] Pinned NOS3 image digest is not present locally: $PINNED_IMAGE" >&2
  exit 1
fi

ACTUAL_NOS3_COMMIT="$(git -C "$NOS3_DIR" rev-parse HEAD)"
if [[ "$ACTUAL_NOS3_COMMIT" != "$EXPECTED_NOS3_COMMIT" ]]; then
  echo "[ERROR] NOS3 checkout mismatch." >&2
  echo "Expected: $EXPECTED_NOS3_COMMIT" >&2
  echo "Actual:   $ACTUAL_NOS3_COMMIT" >&2
  exit 1
fi

if [[ -n "$(git -C "$NOS3_DIR" status --short)" ]]; then
  echo "[ERROR] NOS3 checkout is not clean before build." >&2
  git -C "$NOS3_DIR" status --short >&2
  exit 1
fi

SUBMODULE_DRIFT="$(git -C "$NOS3_DIR" submodule status --recursive | grep -E '^[+-]' || true)"
if [[ -n "$SUBMODULE_DRIFT" ]]; then
  echo "[ERROR] NOS3 submodule drift or uninitialized submodule detected." >&2
  echo "$SUBMODULE_DRIFT" >&2
  exit 1
fi

LOCKED_DIGEST="$(awk -F= '$1=="resolved_image_digests" {print $2}' "$NOS3_LOCK" | tail -n 1)"
if [[ "$LOCKED_DIGEST" != "$PINNED_IMAGE" ]]; then
  echo "[ERROR] Container digest does not match the committed NOS3 lock." >&2
  echo "Lock:     $LOCKED_DIGEST" >&2
  echo "Expected: $PINNED_IMAGE" >&2
  exit 1
fi

STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
LOG_FILE="$LOG_DIR/nominal-build-$STAMP.log"

echo "WP4 nominal NOS3 build"
echo "======================="
echo "NOS3 commit: $ACTUAL_NOS3_COMMIT"
echo "Builder image: $PINNED_IMAGE"
echo "Network mode: none"
echo ""

docker run --rm \
  --platform linux/amd64 \
  --network none \
  --user "$(id -u):$(id -g)" \
  -e HOME=/tmp \
  -v "$NOS3_DIR:$NOS3_DIR" \
  -w "$NOS3_DIR" \
  "$PINNED_IMAGE" \
  bash -lc '
    set -euo pipefail
    rm -rf cfg/build fsw/build sims/build gsw/build
    ./scripts/cfg/config.sh
    make build-fsw
    make build-sim
    make build-cryptolib
  ' 2>&1 | tee "$LOG_FILE"

REQUIRED_ARTIFACTS=(
  "$NOS3_DIR/cfg/build/launch.sh"
  "$NOS3_DIR/fsw/build/exe/cpu1/core-cpu1"
  "$NOS3_DIR/sims/build/bin/nos3-single-simulator"
  "$NOS3_DIR/sims/build/bin/nos3-sim-cmdbus-bridge"
  "$NOS3_DIR/gsw/build/support/standalone"
)

for artifact in "${REQUIRED_ARTIFACTS[@]}"; do
  if [[ ! -f "$artifact" ]]; then
    echo "[ERROR] Expected build artifact is missing: $artifact" >&2
    exit 1
  fi
done

CFE_COMMIT="$(git -C "$NOS3_DIR/fsw/cfe" rev-parse HEAD)"
OSAL_COMMIT="$(git -C "$NOS3_DIR/fsw/osal" rev-parse HEAD)"
PSP_COMMIT="$(git -C "$NOS3_DIR/fsw/psp" rev-parse HEAD)"
FORTYTWO_COMMIT="$(awk -F= '$1=="fortytwo_commit" {print $2}' "$FORTYTWO_LOCK" | tail -n 1)"
FORTYTWO_BINARY_SHA256="$(awk -F= '$1=="fortytwo_binary_sha256" {print $2}' "$FORTYTWO_LOCK" | tail -n 1)"
IMAGE_ID="$(docker image inspect "$PINNED_IMAGE" --format '{{.Id}}')"

cat > "$BUILD_LOCK" <<EOF
recorded_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)
build_status=PASS
network_mode=none
nos3_commit=$ACTUAL_NOS3_COMMIT
cfe_commit=$CFE_COMMIT
osal_commit=$OSAL_COMMIT
psp_commit=$PSP_COMMIT
fortytwo_commit=$FORTYTWO_COMMIT
fortytwo_binary_sha256=$FORTYTWO_BINARY_SHA256
builder_image=$PINNED_IMAGE
builder_image_id=$IMAGE_ID
build_log=$LOG_FILE
artifact_sha256_begin
$(for artifact in "${REQUIRED_ARTIFACTS[@]}"; do shasum -a 256 "$artifact"; done)
artifact_sha256_end
EOF

echo ""
echo "[OK] Deterministic network-disabled build completed."
echo "[OK] Build lock written to: $BUILD_LOCK"
echo "NOMINAL_BUILD_STATUS=PASS"
