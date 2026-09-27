#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
LOCAL_ROOT="${1:-$REPO_ROOT/study3x/local_source/esa_v2}"
OUT="${2:-$REPO_ROOT/study3x/local_freeze_work}"

M1_ROOT="$LOCAL_ROOT/extracted/mission1"
M2_ROOT="$LOCAL_ROOT/extracted/mission2"
FREEZE="$OUT/S3X_SOURCE_FREEZE_001.json"

for cmd in python3 shasum; do
  command -v "$cmd" >/dev/null 2>&1 || {
    echo "ERROR: required command not found: $cmd" >&2
    exit 1
  }
done

if [ ! -f "$FREEZE" ]; then
  echo "ERROR: source-freeze record not found: $FREEZE" >&2
  exit 1
fi

if [ ! -d "$M1_ROOT" ] || [ ! -d "$M2_ROOT" ]; then
  echo "ERROR: expected extracted Mission-1 and Mission-2 roots under $LOCAL_ROOT/extracted" >&2
  exit 1
fi

echo "===== S3X READ-ONLY CADENCE/GAP SENSITIVITY R2 ====="
echo "gap_rule_selection=NO"
echo "trace_extraction=NO"
echo "recovery_policy_execution=NO"
echo "scientific_execution=NO"

python3 "$REPO_ROOT/study3x/validation/analyze_cadence_gap_sensitivity.py" \
  --mission1-dir "$M1_ROOT" \
  --mission2-dir "$M2_ROOT" \
  --source-freeze "$FREEZE" \
  --output-dir "$OUT"

echo
echo "===== OUTPUT HASHES ====="
shasum -a 256 \
  "$OUT/S3X_GAP_SENSITIVITY_002.csv" \
  "$OUT/S3X_DELTA_FREQUENCIES_002.csv" \
  "$OUT/S3X_GAP_SENSITIVITY_SUMMARY_002.json"

echo
echo "S3X_LOCAL_GAP_SENSITIVITY_WORKFLOW_R2=PASS"
echo "gap_rule_selection=NO"
echo "gap_rule_frozen=NO"
echo "trace_extraction=NO"
echo "recovery_policy_execution=NO"
echo "scientific_execution=NO"
