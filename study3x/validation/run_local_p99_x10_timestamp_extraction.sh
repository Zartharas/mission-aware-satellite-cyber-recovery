#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
LOCAL_ROOT="${2:-$REPO_ROOT/study3x/local_source/esa_v2}"
OUT="${3:-$REPO_ROOT/study3x/local_freeze_work/phase6}"
AUTH_RECORD="${1:-}"

if [ -z "$AUTH_RECORD" ]; then
  echo "ERROR: a separately versioned Phase-6 runtime authorization record is required." >&2
  echo "usage: $0 <authorization-record.json> [local-source-root] [output-dir]" >&2
  exit 2
fi

if [ ! -f "$AUTH_RECORD" ]; then
  echo "ERROR: authorization record not found: $AUTH_RECORD" >&2
  exit 2
fi

if [ "$(git branch --show-current)" != "main" ]; then
  echo "ERROR: authorized Phase-6 extraction must run from main." >&2
  exit 2
fi

if ! git diff --quiet || ! git diff --cached --quiet; then
  echo "ERROR: authorized Phase-6 extraction requires a clean tracked worktree." >&2
  exit 2
fi

AUTH_RECORD="$(cd "$(dirname "$AUTH_RECORD")" && pwd)/$(basename "$AUTH_RECORD")"
case "$AUTH_RECORD" in
  "$REPO_ROOT"/study3x/config/S3X_PHASE6_TIMESTAMP_EXTRACTION_AUTH_*.json)
    ;;
  *)
    echo "ERROR: authorization record must be a versioned study3x/config Phase-6 authorization record." >&2
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

M1_ARCHIVE="$LOCAL_ROOT/downloads/ESA-Mission1.zip"
M2_ARCHIVE="$LOCAL_ROOT/downloads/ESA-Mission2.zip"
M1_DIR="$LOCAL_ROOT/extracted/mission1"
M2_DIR="$LOCAL_ROOT/extracted/mission2"
SOURCE_FREEZE="$REPO_ROOT/study3x/local_freeze_work/S3X_SOURCE_FREEZE_001.json"
GAP_FREEZE="$REPO_ROOT/study3x/config/S3X_GAP_RULE_FREEZE_001.json"
PROTOCOL="$REPO_ROOT/study3x/config/S3X_TIMESTAMP_TRACE_EXTRACTION_PROTOCOL_001.json"
EXTRACTOR="$REPO_ROOT/study3x/validation/extract_p99_x10_timestamp_intervals.py"
VALIDATOR="$REPO_ROOT/study3x/validation/validate_p99_x10_timestamp_intervals.py"

for cmd in python3; do
  command -v "$cmd" >/dev/null 2>&1 || {
    echo "ERROR: required command not found: $cmd" >&2
    exit 1
  }
done

OUT="$(python3 - "$OUT" <<'PY'
from pathlib import Path
import sys
print(Path(sys.argv[1]).expanduser().resolve())
PY
)"

case "$OUT" in
  "$REPO_ROOT"/study3x/local_freeze_work/*)
    ;;
  *)
    echo "ERROR: Phase-6 output must remain under study3x/local_freeze_work/." >&2
    exit 2
    ;;
esac

if [ -e "$OUT" ] && [ -n "$(find "$OUT" -mindepth 1 -maxdepth 1 -print -quit 2>/dev/null)" ]; then
  echo "ERROR: Phase-6 output directory must be empty before execution: $OUT" >&2
  exit 2
fi

python3 - <<'PY'
try:
    import pandas  # noqa: F401
except Exception as exc:
    raise SystemExit(
        "ERROR: pandas is required for authorized Phase-6 local execution. "
        f"Original import error: {exc}"
    )
PY

mkdir -p "$OUT"

echo "===== S3X PHASE 6 CANDIDATE TIMESTAMP INTERVAL EXTRACTION ====="
echo "trace_population_freeze=NO"
echo "recovery_policy_execution=NO"
echo "scientific_execution=NO"

python3 "$EXTRACTOR"   --mission1-archive "$M1_ARCHIVE"   --mission2-archive "$M2_ARCHIVE"   --mission1-dir "$M1_DIR"   --mission2-dir "$M2_DIR"   --source-freeze "$SOURCE_FREEZE"   --gap-rule-freeze "$GAP_FREEZE"   --protocol "$PROTOCOL"   --authorization-record "$AUTH_RECORD"   --output-dir "$OUT"

python3 "$VALIDATOR"   --mission1-archive "$M1_ARCHIVE"   --mission2-archive "$M2_ARCHIVE"   --mission1-dir "$M1_DIR"   --mission2-dir "$M2_DIR"   --source-freeze "$SOURCE_FREEZE"   --gap-rule-freeze "$GAP_FREEZE"   --protocol "$PROTOCOL"   --authorization-record "$AUTH_RECORD"   --interval-csv "$OUT/S3X_P99_X10_TIMESTAMP_INTERVALS_001.csv"   --summary-json "$OUT/S3X_P99_X10_TIMESTAMP_INTERVALS_SUMMARY_001.json"   --manifest-json "$OUT/S3X_P99_X10_TIMESTAMP_INTERVALS_MANIFEST_001.json"   --output-json "$OUT/S3X_P99_X10_TIMESTAMP_INTERVALS_VALIDATION_001.json"

echo
echo "===== PHASE 6 LOCAL OUTPUT HASHES ====="
python3 - "$OUT" <<'PY'
import hashlib
from pathlib import Path
import sys

root = Path(sys.argv[1])
for name in (
    "S3X_P99_X10_TIMESTAMP_INTERVALS_001.csv",
    "S3X_P99_X10_TIMESTAMP_INTERVALS_SUMMARY_001.json",
    "S3X_P99_X10_TIMESTAMP_INTERVALS_MANIFEST_001.json",
    "S3X_P99_X10_TIMESTAMP_INTERVALS_VALIDATION_001.json",
):
    path = root / name
    h = hashlib.sha256(path.read_bytes()).hexdigest()
    print(f"{h}  {path}")
PY

echo
echo "S3X_PHASE6_LOCAL_CANDIDATE_EXTRACTION_AND_VALIDATION=PASS"
echo "trace_population_frozen=NO"
echo "recovery_policy_execution=NO"
echo "scientific_execution=NO"
