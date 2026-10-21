#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
OUT="${1:-$REPO_ROOT/study3x/local_freeze_work}"

SENSITIVITY="$OUT/S3X_GAP_SENSITIVITY_002.csv"
FREQUENCY="$OUT/S3X_DELTA_FREQUENCIES_002.csv"
SUMMARY="$OUT/S3X_GAP_SENSITIVITY_SUMMARY_002.json"
RESULT="$OUT/S3X_P99_X10_PREFREEZE_VALIDATION_001.json"

for cmd in python3 shasum; do
  command -v "$cmd" >/dev/null 2>&1 || {
    echo "ERROR: required command not found: $cmd" >&2
    exit 1
  }
done

for file in "$SENSITIVITY" "$FREQUENCY" "$SUMMARY"; do
  if [ ! -f "$file" ]; then
    echo "ERROR: required Phase-5A R2 artifact not found: $file" >&2
    exit 1
  fi
done

echo "===== S3X P99_X10 PRE-FREEZE VALIDATION ====="
echo "candidate_rule=P99_X10"
echo "gap_rule_selection=NO"
echo "gap_rule_freeze=NO"
echo "trace_extraction=NO"
echo "recovery_policy_execution=NO"
echo "scientific_execution=NO"

python3 "$REPO_ROOT/study3x/validation/validate_p99_x10_prefreeze.py" \
  --sensitivity-csv "$SENSITIVITY" \
  --delta-frequency-csv "$FREQUENCY" \
  --summary-json "$SUMMARY" \
  --output-json "$RESULT"

echo
echo "===== PRE-FREEZE VALIDATION OUTPUT HASH ====="
shasum -a 256 "$RESULT"

echo
echo "S3X_LOCAL_P99_X10_PREFREEZE_WORKFLOW=PASS"
echo "candidate_rule=P99_X10"
echo "gap_rule_selection=NO"
echo "gap_rule_frozen=NO"
echo "trace_extraction=NO"
echo "recovery_policy_execution=NO"
echo "scientific_execution=NO"
