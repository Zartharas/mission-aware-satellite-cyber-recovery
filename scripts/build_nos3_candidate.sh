#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
NOS3_DIR="$ROOT_DIR/external/nos3"
IMAGE_REF="ivvitc/nos3-64@sha256:06aa945988a7770b759022c2e1f6f2531818c087fe41a4739d3a3a7f2a9dcce2"
RUN_ID="$(date -u +%Y%m%dT%H%M%SZ)"
LOG_DIR="$ROOT_DIR/artifacts/runtime/wp4-build-$RUN_ID"
LOG_FILE="$LOG_DIR/build.log"

mkdir -p "$LOG_DIR"
bash "$ROOT_DIR/scripts/verify_nos3_source_lock.sh"

set +e
docker run --rm \
  --platform linux/amd64 \
  --network none \
  -e HOME=/tmp/nos3-home \
  --mount "type=bind,source=$NOS3_DIR,target=/nos3" \
  --workdir /nos3 \
  "$IMAGE_REF" \
  bash -lc '
    set -e
    mkdir -p "$HOME"
    rm -rf cfg/build fsw/build sims/build gsw/build
    make config
    make build-fsw
    make build-sim
    test -x fsw/build/exe/cpu1/core-cpu1
    test -x sims/build/bin/nos3-single-simulator
    test -x sims/build/bin/nos3-sim-cmdbus-bridge
  ' 2>&1 | tee "$LOG_FILE"
status=${PIPESTATUS[0]}
set -e

if [[ "$status" -ne 0 ]]; then
  echo "NOS3_BUILD_STATUS=FAIL" | tee -a "$LOG_FILE"
  exit "$status"
fi

{
  echo "recorded_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "research_commit=$(git -C "$ROOT_DIR" rev-parse HEAD)"
  echo "nos3_commit=$(git -C "$NOS3_DIR" rev-parse HEAD)"
  echo "container_reference=$IMAGE_REF"
  shasum -a 256 "$NOS3_DIR/fsw/build/exe/cpu1/core-cpu1"
  shasum -a 256 "$NOS3_DIR/sims/build/bin/nos3-single-simulator"
  shasum -a 256 "$NOS3_DIR/sims/build/bin/nos3-sim-cmdbus-bridge"
} > "$LOG_DIR/build-manifest.txt"

cat "$LOG_DIR/build-manifest.txt"
echo "NOS3_BUILD_STATUS=PASS"
echo "NOS3_BUILD_RUNTIME_DIR=$LOG_DIR"
