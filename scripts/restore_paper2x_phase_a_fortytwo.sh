#!/usr/bin/env bash
# Paper 2 P2X Phase A: restore exact FortyTwo source and reconstruct its executable.
# This does not run NOS3, issue commands, generate trials, or edit historical lock files.
set -Eeuo pipefail
MODE="inspect"
if [ "$#" -gt 0 ]; then MODE="$1"; fi
case "$MODE" in inspect|restore|build) ;; *) echo "usage: bash scripts/restore_paper2x_phase_a_fortytwo.sh [inspect|restore|build]" >&2; exit 2;; esac
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
FT="$ROOT/external/fortytwo"
FT_LOCK="$ROOT/artifacts/fortytwo-lock.txt"
NOS3_LOCK="$ROOT/artifacts/nos3-submodule-lock.txt"
BUILD_LOCK="$ROOT/artifacts/nominal-build-lock.txt"
PIN="eda252bf31f27850e867e698cfdd963e143ead1f"
IMAGE="ivvitc/nos3-64@sha256:06aa945988a7770b759022c2e1f6f2531818c087fe41a4739d3a3a7f2a9dcce2"
OLD_HASH="9c0062d2a447a6340e7c191850ff952d3f8768dd307e3e7fb141e777961e60c7"
fail() { echo "P2X_PHASE_A_FORTYTWO_HOLD=$*" >&2; exit 1; }

test "$(basename "$ROOT")" = "mission-aware-satellite-cyber-recovery" || fail "wrong_project_root"
origin="$(git -C "$ROOT" remote get-url origin 2>/dev/null || true)"
case "$origin" in
  https://github.com/Zartharas/mission-aware-satellite-cyber-recovery|https://github.com/Zartharas/mission-aware-satellite-cyber-recovery.git|git@github.com:Zartharas/mission-aware-satellite-cyber-recovery|git@github.com:Zartharas/mission-aware-satellite-cyber-recovery.git|ssh://git@github.com/Zartharas/mission-aware-satellite-cyber-recovery|ssh://git@github.com/Zartharas/mission-aware-satellite-cyber-recovery.git) ;;
  *) fail "wrong_satellite_repository_origin" ;;
esac
test -z "$(git -C "$ROOT" status --porcelain)" || fail "satellite_repo_worktree_dirty"
for cmd in git docker shasum awk; do command -v "$cmd" >/dev/null 2>&1 || fail "missing_$cmd"; done
for f in "$FT_LOCK" "$NOS3_LOCK" "$BUILD_LOCK"; do test -s "$f" || fail "historical_lock_missing:$f"; done
test "$(awk -F= '$1=="fortytwo_commit"{print $2}' "$FT_LOCK" | tail -n 1)" = "$PIN" || fail "historical_fortytwo_source_pin_drift"
test "$(awk -F= '$1=="fortytwo_binary_sha256"{print $2}' "$FT_LOCK" | tail -n 1)" = "$OLD_HASH" || fail "historical_fortytwo_binary_hash_drift"
test "$(awk -F= '$1=="resolved_image_digests"{print $2}' "$NOS3_LOCK" | tail -n 1)" = "$IMAGE" || fail "nos3_image_lock_drift"
docker info >/dev/null 2>&1 || fail "docker_daemon_unavailable"
docker image inspect "$IMAGE" >/dev/null 2>&1 || fail "pinned_image_missing"
test "$(docker image inspect "$IMAGE" --format '{{.Os}}/{{.Architecture}}')" = "linux/amd64" || fail "wrong_docker_architecture"

if [ "$MODE" = "inspect" ]; then
  if [ -e "$FT" ] || [ -L "$FT" ]; then
    echo "FORTYTWO_DESTINATION=EXISTS"
    if git -C "$FT" rev-parse HEAD >/dev/null 2>&1; then
      echo "fortytwo_head=$(git -C "$FT" rev-parse HEAD)"
    fi
    if [ -f "$FT/42" ]; then shasum -a 256 "$FT/42"; else echo "FORTYTWO_BINARY=MISSING"; fi
  else
    echo "FORTYTWO_DESTINATION=MISSING"
  fi
  echo "P2X_FORTYTWO_INSPECT=PASS"
  echo "FORTYTWO_SOURCE_RESTORE=NOT_RUN"
  echo "FORTYTWO_BUILD=NOT_RUN"
  exit 0
fi

if [ "$MODE" = "restore" ]; then
  if [ -e "$FT" ] || [ -L "$FT" ]; then fail "destination_already_exists_no_overwrite"; fi
  mkdir -p "$ROOT/external"
  git clone --no-checkout https://github.com/nasa-itc/42.git "$FT"
  git -C "$FT" fetch origin "$PIN"
  git -C "$FT" checkout --detach "$PIN"
  test "$(git -C "$FT" rev-parse HEAD)" = "$PIN" || fail "source_checkout_wrong_revision"
  test -z "$(git -C "$FT" status --porcelain)" || fail "new_checkout_not_clean"
  echo "P2X_FORTYTWO_PINNED_SOURCE_RESTORED=PASS"
  echo "FORTYTWO_BINARY_BUILT=NO"
  exit 0
fi

# Build mode: byte-verify rebuilt executable against the immutable July freeze.
test -d "$FT/.git" || fail "pinned_fortytwo_source_missing"
test "$(git -C "$FT" rev-parse --show-toplevel)" = "$FT" || fail "fortytwo_not_checkout_root"
test "$(git -C "$FT" rev-parse HEAD)" = "$PIN" || fail "fortytwo_wrong_revision"
test "$(git -C "$FT" remote get-url origin)" = "https://github.com/nasa-itc/42.git" || fail "fortytwo_wrong_origin"
test -z "$(git -C "$FT" status --porcelain)" || fail "fortytwo_dirty_source"
test ! -e "$FT/42" || fail "fortytwo_binary_already_exists_inspect_instead_of_overwriting"
test ! -L "$FT/42" || fail "fortytwo_binary_symlink"
test -d "$FT/Object" || fail "fortytwo_object_directory_absent"
test -z "$(find "$FT/Object" -maxdepth 1 -name '*.o' -print -quit)" || fail "partial_object_build_present_no_overwrite"

STAMP="$(date -u +%Y%m%dT%H%M%SZ)-$$"
OUT="$ROOT/artifacts/runtime/p2xa-42-build-$STAMP"
mkdir -p "$OUT"
before_ft="$(shasum -a 256 "$FT_LOCK" | awk '{print $1}')"
before_nos3="$(shasum -a 256 "$NOS3_LOCK" | awk '{print $1}')"
before_build="$(shasum -a 256 "$BUILD_LOCK" | awk '{print $1}')"
printf 'experiment_id=P2X-NOS3-RG-001\nphase=A_environment_reconstruction_only\nfortytwo_source_pin=%s\nimage_digest=%s\nimage_network_mode=none\nhistorical_binary_sha256=%s\nstarted_utc=%s\n' \
  "$PIN" "$IMAGE" "$OLD_HASH" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" > "$OUT/rebuild-manifest.txt"
echo "P2X_PHASE_A_FORTYTWO_BUILD_EVIDENCE=$OUT"

# Source Makefile supports GUIFLAG override; original July flags are not present in the lock.
# A hash mismatch is evidence of build variation, not a reason to alter the historical freeze.
docker run --rm \
  --platform linux/amd64 --network none \
  --user "$(id -u):$(id -g)" -e HOME=/tmp \
  --mount "type=bind,source=$FT,target=/work/fortytwo" \
  --workdir /work/fortytwo "$IMAGE" \
  make GUIFLAG= SHADERFLAG= 42 2>&1 | tee "$OUT/fortytwo-build.log"

test -f "$FT/42" || fail "fortytwo_build_did_not_create_binary"
test -z "$(git -C "$FT" status --porcelain)" || fail "fortytwo_source_mutation_during_build"
actual="$(shasum -a 256 "$FT/42" | awk '{print $1}')"
printf 'reconstructed_binary_sha256=%s\nhistorical_binary_match=%s\n' "$actual" \
  "$(if [ "$actual" = "$OLD_HASH" ]; then echo YES; else echo NO; fi)" >> "$OUT/rebuild-manifest.txt"
test "$(shasum -a 256 "$FT_LOCK" | awk '{print $1}')" = "$before_ft" || fail "historical_fortytwo_lock_changed"
test "$(shasum -a 256 "$NOS3_LOCK" | awk '{print $1}')" = "$before_nos3" || fail "historical_nos3_lock_changed"
test "$(shasum -a 256 "$BUILD_LOCK" | awk '{print $1}')" = "$before_build" || fail "historical_nos3_build_lock_changed"
printf 'fortytwo_binary_sha256=%s\nfortytwo_build_evidence=%s\n' "$actual" "$OUT"
test "$actual" = "$OLD_HASH" || fail "fortytwo_binary_differs_from_july_freeze_hold_before_NOS3_build"
echo "P2X_PHASE_A_FORTYTWO_BYTE_IDENTICAL_RECONSTRUCTION=PASS"
echo "RUNTIME_EXECUTED=NO"
echo "SCIENTIFIC_DATA_GENERATED=NO"
