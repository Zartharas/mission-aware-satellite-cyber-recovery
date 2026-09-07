#!/bin/bash
set -euo pipefail

DIR="publication/Paper_2_Studies_3_4_6/IEEE_Transactions_on_Aerospace_and_Electronic_Systems"

if [[ "$(git branch --show-current)" != "paper2/taes-10-page-compression" ]]; then
  echo "ERROR: wrong branch: $(git branch --show-current)"
  exit 1
fi

SOURCE="$DIR/TAES_10P_R3_SUPPLEMENTARY_MATERIAL.md"
SUPP_PDF="$DIR/TAES_10P_R3_SUPPLEMENTARY_MATERIAL_R9_DEV.pdf"
PATCH_AUDIT="$DIR/TAES_10P_R3_SUPPLEMENTARY_R9_CROSSREF_FIX_AUDIT.txt"
BUILD_AUDIT="$DIR/TAES_10P_R3_SUPPLEMENTARY_R9_BUILD_AUDIT.txt"
MAIN_PDF="$DIR/TAES_10P_R3_MANUSCRIPT_IEEETRAN_R8_DEV.pdf"
R9_PDF="$DIR/TAES_MANUSCRIPT.pdf"
OUT_AUDIT="$DIR/TAES_10P_R3_SHORT_TRACK_SCIENCE_PRESERVATION_R2_AUDIT.txt"

for FILE in "$SOURCE" "$SUPP_PDF" "$PATCH_AUDIT" "$BUILD_AUDIT" "$MAIN_PDF" "$R9_PDF"; do
  if [[ ! -f "$FILE" ]]; then
    echo "ERROR: required existing local artifact missing: $FILE"
    exit 1
  fi
done

EXPECTED_SOURCE="c3496de9644be4e9ee38b97f2cb98faf7c1aac2821c5575eb2b9a96f198ce95f"
EXPECTED_SUPP_PDF="f570dbb7d489e53da74b3942ba08e9cd5008bab4f50e72ddb06e27ba0c1fdabb"
EXPECTED_MAIN_PDF="f34cd280371f73492f6ef746fd52279fb1ab01fa4ce8c38eedb8aa67a74f551b"
EXPECTED_R9_PDF="a7624fa416ebe4ba4d0b9e46da25b5dcb4d85e23e63291f4bdf497d5ba6cb319"

sha() { shasum -a 256 "$1" | awk '{print $1}'; }
assert_sha() {
  local file="$1"
  local expected="$2"
  local actual
  actual="$(sha "$file")"
  if [[ "$actual" != "$expected" ]]; then
    echo "ERROR: SHA mismatch: $file"
    echo "expected=$expected"
    echo "actual=$actual"
    exit 1
  fi
  echo "PASS_SHA $(basename "$file")=$actual"
}

echo "TAES_SHORT_TRACK_SCIENCE_PRESERVATION_R2_FINAL_GATE=START"
echo "branch=$(git branch --show-current)"
echo "head=$(git rev-parse HEAD)"

echo "=== EXISTING CORRECTED ARTIFACT IDENTITIES ==="
assert_sha "$SOURCE" "$EXPECTED_SOURCE"
assert_sha "$SUPP_PDF" "$EXPECTED_SUPP_PDF"
assert_sha "$MAIN_PDF" "$EXPECTED_MAIN_PDF"
assert_sha "$R9_PDF" "$EXPECTED_R9_PDF"

echo "=== PRIOR R9 BUILD CONTROLS ==="
grep -Fx 'TAES_10P_R3_SUPPLEMENTARY_BUILD=PASS_COMPILED_DEVELOPMENT_ONLY' "$BUILD_AUDIT"
grep -Fx 'supplement_build_revision=9' "$BUILD_AUDIT"
grep -Fx 'table_cross_reference_gate=PASS_S1_S2_S3_NO_LEGACY_II_III_IV' "$BUILD_AUDIT"
grep -Fx 'supplement_table_values_changed=NO' "$BUILD_AUDIT"
grep -Fx 'experimental_results_changed=NO' "$BUILD_AUDIT"
grep -Fx 'science_files_changed=NONE' "$BUILD_AUDIT"
grep -Fx 'study_rerun=NO' "$BUILD_AUDIT"

echo "=== READ-ONLY SCIENCE-PRESERVATION R2 ==="
python3 "$DIR/TAES_AUDIT_SHORT_TRACK_SCIENCE_PRESERVATION_R2.py"

if [[ ! -f "$OUT_AUDIT" ]]; then
  echo "ERROR: R2 preservation audit output missing"
  exit 1
fi

echo "=== R2 AUDIT ASSERTIONS ==="
grep -Fx 'TAES_SHORT_TRACK_SCIENCE_PRESERVATION=PASS' "$OUT_AUDIT"
grep -Fx 'study3_population_and_key_results=PASS_PRESERVED' "$OUT_AUDIT"
grep -Fx 'study4_complete_18_rule_map=PASS_PRESERVED_IN_SUPPLEMENT' "$OUT_AUDIT"
grep -Fx 'study6_complete_gate_frontier=PASS_PRESERVED' "$OUT_AUDIT"
grep -Fx 'framework_e_q_t_u_c=PASS_PRESERVED_IN_MAIN' "$OUT_AUDIT"
grep -Fx 'non_pooling_control=PASS_MAIN_AND_SUPPLEMENT' "$OUT_AUDIT"
grep -Fx 'only_study3_contact_control=PASS' "$OUT_AUDIT"
grep -Fx 'qualification_not_recovery_completion_control=PASS' "$OUT_AUDIT"
grep -Fx 'external_replication_claim=PASS_NOT_CLAIMED' "$OUT_AUDIT"
grep -Fx 'references_1_through_13=PASS_MAIN' "$OUT_AUDIT"
grep -Fx 'tuf_v1_0_36=PASS_MAIN' "$OUT_AUDIT"
grep -Fx 'ai_disclosure=PASS_MAIN_AND_RESULTS_BOUNDARY' "$OUT_AUDIT"
grep -Fx 'stale_table_crossrefs=PASS_REMOVED' "$OUT_AUDIT"
grep -Fx 'corrected_table_crossrefs=PASS_S1_S2_S3' "$OUT_AUDIT"
grep -Fx 'experimental_results_changed=NO' "$OUT_AUDIT"
grep -Fx 'frozen_study_sources_changed=NO' "$OUT_AUDIT"
grep -Fx 'study_rerun=NO' "$OUT_AUDIT"
grep -Fx 'pooled_population_introduced=NO' "$OUT_AUDIT"
grep -Fx 'common_effect_introduced=NO' "$OUT_AUDIT"
grep -Fx 'global_policy_rank_introduced=NO' "$OUT_AUDIT"
grep -Fx 'science_preservation_decision=PASS_SHORT_MAIN_PLUS_CORRECTED_SUPPLEMENT_PRESERVES_FROZEN_R9_CLAIM_BOUNDARIES' "$OUT_AUDIT"
grep -Fx 'science_preservation_audit_revision=2' "$OUT_AUDIT"

echo "=== AUDIT SHA256 ==="
shasum -a 256 "$OUT_AUDIT"

echo "TAES_SHORT_TRACK_SCIENCE_PRESERVATION_R2_FINAL_GATE=PASS"
echo "corrected_supplement_pdf=$SUPP_PDF"
echo "corrected_supplement_pdf_sha256=$EXPECTED_SUPP_PDF"
