#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
NOS3_DIR="$ROOT_DIR/external/nos3"
LOCK_FILE="$ROOT_DIR/artifacts/nos3-submodule-lock.txt"

EXPECTED_NOS3="5a3bdee6be9a2c67fdf994ae6db56d5c60395302"
EXPECTED_CFE="87e273743f3d07ed9216462b461e9f398ff96c87"
EXPECTED_OSAL="08a79bb6ac02b9ced8aa555853ecdd96e5ebc1a7"
EXPECTED_PSP="d0a5d6fa4093d473a929fde42a0983e489d89d4a"
EXPECTED_IMAGE_DIGEST="ivvitc/nos3-64@sha256:06aa945988a7770b759022c2e1f6f2531818c087fe41a4739d3a3a7f2a9dcce2"

fail() {
  echo "[FAIL] $*" >&2
  exit 1
}

pass() {
  echo "[OK] $*"
}

command -v git >/dev/null 2>&1 || fail "git is not available"
command -v docker >/dev/null 2>&1 || fail "docker is not available"
[[ -d "$NOS3_DIR/.git" ]] || fail "NOS3 checkout not found at $NOS3_DIR"
[[ -f "$LOCK_FILE" ]] || fail "lock file not found at $LOCK_FILE"

actual_nos3="$(git -C "$NOS3_DIR" rev-parse HEAD)"
[[ "$actual_nos3" == "$EXPECTED_NOS3" ]] || fail "NOS3 commit mismatch: $actual_nos3"
pass "NOS3 commit matches the recorded lock"

[[ -z "$(git -C "$NOS3_DIR" status --short)" ]] || fail "NOS3 worktree is not clean"
pass "NOS3 worktree is clean"

submodule_drift="$(git -C "$NOS3_DIR" submodule status --recursive | grep -E '^[+-U]' || true)"
[[ -z "$submodule_drift" ]] || fail "submodule drift or uninitialized submodule detected: $submodule_drift"
pass "recursive submodules match the NOS3 superproject"

actual_cfe="$(git -C "$NOS3_DIR/fsw/cfe" rev-parse HEAD)"
actual_osal="$(git -C "$NOS3_DIR/fsw/osal" rev-parse HEAD)"
actual_psp="$(git -C "$NOS3_DIR/fsw/psp" rev-parse HEAD)"
[[ "$actual_cfe" == "$EXPECTED_CFE" ]] || fail "cFE commit mismatch: $actual_cfe"
[[ "$actual_osal" == "$EXPECTED_OSAL" ]] || fail "OSAL commit mismatch: $actual_osal"
[[ "$actual_psp" == "$EXPECTED_PSP" ]] || fail "PSP commit mismatch: $actual_psp"
pass "cFE, OSAL, and PSP commits match the recorded lock"

grep -Fqx "nos3_commit=$EXPECTED_NOS3" "$LOCK_FILE" || fail "NOS3 commit missing from lock file"
grep -Fqx "resolved_image_digests=$EXPECTED_IMAGE_DIGEST" "$LOCK_FILE" || fail "image digest missing from lock file"
grep -Fq "$EXPECTED_CFE fsw/cfe" "$LOCK_FILE" || fail "cFE commit missing from lock file"
grep -Fq "$EXPECTED_OSAL fsw/osal" "$LOCK_FILE" || fail "OSAL commit missing from lock file"
grep -Fq "$EXPECTED_PSP fsw/psp" "$LOCK_FILE" || fail "PSP commit missing from lock file"
pass "committed lock artifact contains the required revisions"

resolved_digests="$(docker image inspect ivvitc/nos3-64:20260619 --format '{{join .RepoDigests "\n"}}' 2>/dev/null || true)"
grep -Fqx "$EXPECTED_IMAGE_DIGEST" <<<"$resolved_digests" || fail "pinned NOS3 image digest is not available locally"
pass "local NOS3 image resolves to the committed digest"

echo
printf 'NOS3_SOURCE_LOCK_STATUS=PASS\n'
