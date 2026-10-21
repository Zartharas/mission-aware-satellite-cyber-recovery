#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
AUTH_RECORD="${1:-}"
OUT="${2:-}"
INTERVAL_CSV="$REPO_ROOT/study3x/local_freeze_work/phase6_run1/S3X_P99_X10_TIMESTAMP_INTERVALS_001.csv"

EXPECTED_INPUT_SHA="cfa4fa3d88cb525237cbfe347fabe8485021351f3b639bdb58f79c575d8a51bc"
RUNTIME="$REPO_ROOT/study3x/runtime/run_phase7_replay_v2.py"
VALIDATOR="$REPO_ROOT/study3x/audit/validate_phase7_replay_v2.py"

if [ -z "$AUTH_RECORD" ] || [ -z "$OUT" ]; then
  echo "ERROR: usage: $0 <authorization-record.json> <output-dir>" >&2
  exit 2
fi

if [ "$(git branch --show-current)" != "main" ]; then
  echo "ERROR: authorized Phase-7 replay must run from main." >&2
  exit 2
fi

if ! git diff --quiet || ! git diff --cached --quiet; then
  echo "ERROR: authorized Phase-7 replay requires a clean tracked worktree." >&2
  exit 2
fi

AUTH_RECORD="$(cd "$(dirname "$AUTH_RECORD")" && pwd)/$(basename "$AUTH_RECORD")"
case "$AUTH_RECORD" in
  "$REPO_ROOT"/study3x/config/S3X_PHASE7_RUNTIME_AUTH_*.json) ;;
  *)
    echo "ERROR: authorization record must be a versioned Phase-7 record under study3x/config/." >&2
    exit 2
    ;;
esac

AUTH_RELATIVE="${AUTH_RECORD#"$REPO_ROOT"/}"
if ! git ls-files --error-unmatch "$AUTH_RELATIVE" >/dev/null 2>&1; then
  echo "ERROR: authorization record must be tracked by Git." >&2
  exit 2
fi
if ! git diff --quiet -- "$AUTH_RELATIVE" || ! git diff --cached --quiet -- "$AUTH_RELATIVE"; then
  echo "ERROR: authorization record has uncommitted changes." >&2
  exit 2
fi

if [ ! -f "$INTERVAL_CSV" ]; then
  echo "ERROR: frozen Phase-6 interval artifact not found: $INTERVAL_CSV" >&2
  exit 2
fi

OUT="$(python3 - "$OUT" <<'PY'
from pathlib import Path
import sys
print(Path(sys.argv[1]).expanduser().resolve())
PY
)"

case "$OUT" in
  "$REPO_ROOT"/study3x/local_freeze_work/phase7_authorized_run1_001|  "$REPO_ROOT"/study3x/local_freeze_work/phase7_authorized_run2_001) ;;
  *)
    echo "ERROR: output must be one of the two canonical authorized Phase-7 run directories." >&2
    exit 2
    ;;
esac

if [ -e "$OUT" ] && [ -n "$(find "$OUT" -mindepth 1 -maxdepth 1 -print -quit 2>/dev/null)" ]; then
  echo "ERROR: Phase-7 output directory must be empty before execution: $OUT" >&2
  exit 2
fi

python3 - "$AUTH_RECORD" "$INTERVAL_CSV" <<'PY'
from pathlib import Path
import hashlib
import json
import sys

auth_path = Path(sys.argv[1])
interval_path = Path(sys.argv[2])

auth = json.loads(auth_path.read_text(encoding="utf-8"))
if auth.get("authorization_id") != "S3X-PHASE7-RUNTIME-AUTH-002":
    raise SystemExit("ERROR: unexpected Phase-7 authorization id")

scope = auth.get("authorization_scope", {})
for key in (
    "real_frozen_interval_artifact_read_authorized",
    "real_1919_interval_expansion_authorized",
    "recovery_policy_execution_authorized",
    "scientific_execution_authorized",
    "independent_reference_validation_authorized",
    "deterministic_repeat_execution_authorized",
):
    if scope.get(key) is not True:
        raise SystemExit(f"ERROR: runtime authorization not effective for {key}")

for key in (
    "result_freeze_authorized",
    "manuscript_claim_use_authorized",
    "p99_x10_retuning_authorized",
    "interval_membership_retuning_authorized",
    "study3_modification_authorized",
    "study3_s3x_pooling_authorized",
):
    if scope.get(key) is not False:
        raise SystemExit(f"ERROR: prohibited scope unexpectedly opened: {key}")

h = hashlib.sha256(interval_path.read_bytes()).hexdigest()
expected = "cfa4fa3d88cb525237cbfe347fabe8485021351f3b639bdb58f79c575d8a51bc"
if h != expected:
    raise SystemExit(f"ERROR: frozen interval SHA mismatch: expected={expected} actual={h}")
print(f"frozen_interval_sha256={h}")
PY

python3 - "$REPO_ROOT" <<'PY'
from pathlib import Path
import subprocess
import sys

root = Path(sys.argv[1])
expected = {
    "study3x/config/S3X_PHASE7_RECOVERY_REPLAY_PROTOCOL_001.json":
        "f42fe8c0c58ee3b9152e629f5673bd5c71ffede4",
    "study3x/config/S3X_PHASE6_TRACE_POPULATION_FREEZE_001.json":
        "ed0bdcec443b7f0c3ee80d441e1122f32e499d3e",
    "study3x/config/S3X_PHASE7_IMPLEMENTATION_FREEZE_CANDIDATE_002.json":
        "d7ee15c6a2bfe818ee016eadba0893ef74aa8f18",
    "study3x/src/recovery_replay_v2.py":
        "40e3bd0406f1f0bedecbac9cb1386699a8619318",
    "study3x/audit/reference_replay_v2.py":
        "26444d206f18bededa656b1de56d9ba0948c6ef3",
    "study3x/runtime/run_phase7_replay_v2.py":
        "f2a789edd24a0e23ff0d256312fc7d2b7e656573",
    "study3x/audit/validate_phase7_replay_v2.py":
        "15796f7b8e2da3f92e941021839b387ad365394e",
}
for rel, wanted in expected.items():
    actual = subprocess.check_output(
        ["git", "hash-object", rel], cwd=root, text=True
    ).strip()
    if actual != wanted:
        raise SystemExit(
            f"ERROR: bound implementation drift: {rel} expected={wanted} actual={actual}"
        )
print("phase7_bound_code_identity=PASS")
PY

mkdir -p "$OUT"

echo "===== S3X PHASE 7 AUTHORIZED RECOVERY REPLAY ====="
echo "result_freeze=NO"
echo "manuscript_claim_use=NO"

python3 "$RUNTIME"   --authorization-record "$AUTH_RECORD"   --interval-csv "$INTERVAL_CSV"   --output-dir "$OUT"

python3 "$VALIDATOR"   --authorization-record "$AUTH_RECORD"   --interval-csv "$INTERVAL_CSV"   --case-results "$OUT/S3X_PHASE7_CASE_RESULTS_001.csv"   --matched-comparisons "$OUT/S3X_PHASE7_MATCHED_COMPARISONS_001.csv"   --summary-json "$OUT/S3X_PHASE7_SUMMARY_001.json"   --output-json "$OUT/S3X_PHASE7_INDEPENDENT_VALIDATION_001.json"

python3 - "$OUT" <<'PY'
from pathlib import Path
import hashlib
import json
import sys

root = Path(sys.argv[1])
names = [
    "S3X_PHASE7_CASE_RESULTS_001.csv",
    "S3X_PHASE7_MATCHED_COMPARISONS_001.csv",
    "S3X_PHASE7_SUMMARY_001.json",
    "S3X_PHASE7_INDEPENDENT_VALIDATION_001.json",
]
hashes = {}
for name in names:
    path = root / name
    hashes[name] = hashlib.sha256(path.read_bytes()).hexdigest()

manifest = {
    "schema": 1,
    "experiment_id": "S3X-ETA-001",
    "authorization_id": "S3X-PHASE7-RUNTIME-AUTH-002",
    "artifacts": hashes,
    "result_freeze_authorized": False,
    "manuscript_claim_use_authorized": False,
}
manifest_path = root / "S3X_PHASE7_RESULTS_HASH_MANIFEST_001.json"
manifest_path.write_text(
    json.dumps(manifest, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)
for name, digest in hashes.items():
    print(f"{name}_sha256={digest}")
print(
    "S3X_PHASE7_RESULTS_HASH_MANIFEST_001.json_sha256="
    + hashlib.sha256(manifest_path.read_bytes()).hexdigest()
)
PY

echo "S3X_PHASE7_LOCAL_AUTHORIZED_REPLAY_V2_AND_VALIDATION=PASS"
echo "result_freeze=NO"
echo "manuscript_claim_use=NO"
