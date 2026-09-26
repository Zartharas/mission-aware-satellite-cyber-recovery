#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
TARGET="${1:-$REPO_ROOT/study6x/external/cFS-v7.0.1}"
OUT="${2:-$REPO_ROOT/study6x/workspace}"
mkdir -p "$(dirname "$TARGET")" "$OUT"

for cmd in git python3; do
  command -v "$cmd" >/dev/null 2>&1 || {
    echo "ERROR: required command not found: $cmd" >&2
    exit 1
  }
done

EXPECTED_CFS="088b2fa828db9ff7e00733f1908e0eeb59f66ce3"
EXPECTED_LC="a1c3a47ea1fa5c0d7751d6ff88848dc9bd8a6c7a"

echo "===== S6X PRE-RUNTIME MATERIALIZATION ====="
echo "build_authorized=NO"
echo "scientific_execution=NO"

if [ ! -d "$TARGET/.git" ]; then
  if [ -e "$TARGET" ]; then
    echo "ERROR: target exists but is not a Git checkout: $TARGET" >&2
    exit 1
  fi
  git clone --depth 1 --branch v7.0.1 \
    https://github.com/nasa/cFS.git "$TARGET"
fi

actual_cfs="$(git -C "$TARGET" rev-parse HEAD)"
if [ "$actual_cfs" != "$EXPECTED_CFS" ]; then
  echo "ERROR: cFS checkout mismatch" >&2
  echo "expected=$EXPECTED_CFS actual=$actual_cfs" >&2
  exit 1
fi

git -C "$TARGET" submodule update --init --depth 1 apps/lc

actual_lc="$(git -C "$TARGET/apps/lc" rev-parse HEAD)"
if [ "$actual_lc" != "$EXPECTED_LC" ]; then
  echo "ERROR: LC submodule mismatch" >&2
  echo "expected=$EXPECTED_LC actual=$actual_lc" >&2
  exit 1
fi

PYTHONPATH="$REPO_ROOT" python3 -m unittest study6x.tests.test_invariant_oracle

python3 "$REPO_ROOT/study6x/validation/validate_local_cfs_pin.py" \
  "$TARGET" \
  --fixture-patch "$REPO_ROOT/study6x/fixtures/S6X_FIXTURE_GT_EQ_BOUNDARY_001.patch" \
  | tee "$OUT/S6X_PRE_RUNTIME_VALIDATION_001.txt"

python3 - "$TARGET" "$REPO_ROOT" "$OUT/S6X_PRE_RUNTIME_VALIDATION_001.json" <<'PY'
import hashlib
import json
import subprocess
import sys
from pathlib import Path

target = Path(sys.argv[1]).resolve()
repo = Path(sys.argv[2]).resolve()
out = Path(sys.argv[3]).resolve()

def git(cwd: Path, *args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=cwd, text=True).strip()

patch = repo / "study6x/fixtures/S6X_FIXTURE_GT_EQ_BOUNDARY_001.patch"
report = {
    "schema": 1,
    "experiment_id": "S6X-EAP-001",
    "validation_id": "S6X-PRE-RUNTIME-VALIDATION-001",
    "mode": "STATIC_PRE_RUNTIME_VALIDATION",
    "cfs_commit": git(target, "rev-parse", "HEAD"),
    "lc_commit": git(target / "apps/lc", "rev-parse", "HEAD"),
    "fixture_patch_sha256": hashlib.sha256(patch.read_bytes()).hexdigest(),
    "fixture_patch_applied": False,
    "build_executed": False,
    "artifact_signing_executed": False,
    "scientific_execution": False,
    "next_gate": "AUTHOR_REVIEW_BEFORE_ANY_BUILD_OR_SCIENTIFIC_EXECUTION",
}
out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
print(f"validation_json={out}")
PY

echo
echo "S6X_PRE_RUNTIME_MATERIALIZATION=PASS"
echo "cfs_commit=$actual_cfs"
echo "lc_commit=$actual_lc"
echo "fixture_patch_applied=NO"
echo "build_executed=NO"
echo "scientific_execution=NO"
