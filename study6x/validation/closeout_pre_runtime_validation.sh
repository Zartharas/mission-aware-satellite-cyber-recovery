#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
TARGET="${1:-$REPO_ROOT/study6x/external/cFS-v7.0.1}"
OUT="${2:-$REPO_ROOT/study6x/workspace}"
mkdir -p "$OUT"

RUNNER="$REPO_ROOT/study6x/validation/materialize_validate_cfs_v701.sh"
HARNESS="$REPO_ROOT/study6x/fixtures/S6X_INVARIANT_HARNESS_EQUALITY_001.patch"
VALIDATION_JSON="$OUT/S6X_PRE_RUNTIME_VALIDATION_001.json"
VALIDATION_TXT="$OUT/S6X_PRE_RUNTIME_VALIDATION_001.txt"
CLOSEOUT_JSON="$OUT/S6X_PRE_RUNTIME_CLOSEOUT_001.json"

echo "===== S6X PRE-RUNTIME CLOSEOUT ====="
echo "build_authorized=NO"
echo "scientific_execution=NO"

bash "$RUNNER" "$TARGET" "$OUT"

test -f "$VALIDATION_JSON"
test -f "$VALIDATION_TXT"

git -C "$TARGET/apps/lc" apply --check "$HARNESS"

python3 - "$REPO_ROOT" "$TARGET" "$VALIDATION_JSON" "$VALIDATION_TXT" "$CLOSEOUT_JSON" <<'PY'
import hashlib
import json
import platform
import subprocess
import sys
from pathlib import Path

repo = Path(sys.argv[1]).resolve()
target = Path(sys.argv[2]).resolve()
validation_json = Path(sys.argv[3]).resolve()
validation_txt = Path(sys.argv[4]).resolve()
out = Path(sys.argv[5]).resolve()

EXPECTED_CFS = "088b2fa828db9ff7e00733f1908e0eeb59f66ce3"
EXPECTED_LC = "a1c3a47ea1fa5c0d7751d6ff88848dc9bd8a6c7a"

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def git(cwd: Path, *args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=cwd, text=True).strip()

record = json.loads(validation_json.read_text(encoding="utf-8"))
if record.get("validation_id") != "S6X-PRE-RUNTIME-VALIDATION-001":
    raise SystemExit("unexpected validation id")
if record.get("cfs_commit") != EXPECTED_CFS:
    raise SystemExit("cFS commit mismatch in validation record")
if record.get("lc_commit") != EXPECTED_LC:
    raise SystemExit("LC commit mismatch in validation record")
for key in ("fixture_patch_applied", "build_executed", "artifact_signing_executed", "scientific_execution"):
    if record.get(key) is not False:
        raise SystemExit(f"closed pre-runtime gate unexpectedly open: {key}")

tracked = [
    "study6x/S6X_SOURCE_PIN.json",
    "study6x/S6X_PREEXECUTION_PROTOCOL.json",
    "study6x/validation/materialize_validate_cfs_v701.sh",
    "study6x/validation/validate_local_cfs_pin.py",
    "study6x/fixtures/S6X_FIXTURE_GT_EQ_BOUNDARY_001.patch",
    "study6x/fixtures/S6X_INVARIANT_HARNESS_EQUALITY_001.patch",
    "study6x/src/invariant_oracle.py",
    "study6x/tests/test_invariant_oracle.py",
    "study6x/tests/test_validate_local_cfs_pin.py",
]

report = {
    "schema": 1,
    "experiment_id": "S6X-EAP-001",
    "closeout_id": "S6X-PRE-RUNTIME-CLOSEOUT-001",
    "status": "LOCAL_PRE_RUNTIME_VALIDATION_PASS__PENDING_AUTHOR_REVIEW",
    "repository_head": git(repo, "rev-parse", "HEAD"),
    "cfs_commit": git(target, "rev-parse", "HEAD"),
    "lc_commit": git(target / "apps/lc", "rev-parse", "HEAD"),
    "validation_json_sha256": sha256(validation_json),
    "validation_text_sha256": sha256(validation_txt),
    "tracked_dependency_sha256": {rel: sha256(repo / rel) for rel in tracked},
    "host_context": {
        "platform": platform.platform(),
        "machine": platform.machine(),
        "python": platform.python_version(),
    },
    "harness_patch_dry_run": "PASS",
    "fixture_patch_applied": False,
    "harness_patch_applied": False,
    "build_executed": False,
    "artifact_signing_executed": False,
    "scientific_execution": False,
    "canonical_results_generated": False,
    "next_gate": "AUTHOR_REVIEW_OF_S6X_PRE_RUNTIME_CLOSEOUT_AND_BUILD_ENVIRONMENT_FREEZE_CANDIDATE_BEFORE_ANY_CFS_BUILD",
}
out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
print(f"closeout_json={out}")
print(f"closeout_json_sha256={sha256(out)}")
PY

echo "S6X_PRE_RUNTIME_CLOSEOUT=PASS"
echo "fixture_patch_applied=NO"
echo "harness_patch_applied=NO"
echo "build_executed=NO"
echo "scientific_execution=NO"
