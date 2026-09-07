#!/bin/bash
set -euo pipefail

DIR="publication/Paper_2_Studies_3_4_6/IEEE_Transactions_on_Aerospace_and_Electronic_Systems"

if [[ "$(git branch --show-current)" != "paper2/taes-10-page-compression" ]]; then
  echo "ERROR: wrong branch: $(git branch --show-current)"
  exit 1
fi

if [[ -x "/Library/TeX/texbin/latexmk" ]]; then
  export PATH="/Library/TeX/texbin:$PATH"
fi
hash -r 2>/dev/null || true

for CMD in pandoc latexmk pdflatex pdfinfo pdffonts pdftotext shasum; do
  if ! command -v "$CMD" >/dev/null 2>&1; then
    echo "ERROR: required command missing: $CMD"
    exit 1
  fi
done

echo "TAES_SUPPLEMENT_R9_CORRECTED_FINAL_GATE=START"
echo "branch=$(git branch --show-current)"
echo "head=$(git rev-parse HEAD)"

echo "=== APPLY AUTHORIZED CROSS-REFERENCE CORRECTION ==="
python3 "$DIR/TAES_APPLY_SUPPLEMENT_R9_CROSSREF_FIX.py"

echo "=== BUILD CORRECTED SUPPLEMENT R9 ==="
python3 "$DIR/TAES_BUILD_10P_SUPPLEMENT_R9.py"

PDF="$DIR/TAES_10P_R3_SUPPLEMENTARY_MATERIAL_R9_DEV.pdf"
TEX="$DIR/TAES_10P_R3_SUPPLEMENTARY_MATERIAL_R9_DEV.tex"
LOG="$DIR/TAES_10P_R3_SUPPLEMENTARY_MATERIAL_R9_DEV.log"
AUDIT="$DIR/TAES_10P_R3_SUPPLEMENTARY_R9_BUILD_AUDIT.txt"
PATCH_AUDIT="$DIR/TAES_10P_R3_SUPPLEMENTARY_R9_CROSSREF_FIX_AUDIT.txt"
SCIENCE_AUDIT="$DIR/TAES_10P_R3_SHORT_TRACK_SCIENCE_PRESERVATION_R1_AUDIT.txt"
SOURCE="$DIR/TAES_10P_R3_SUPPLEMENTARY_MATERIAL.md"
README="$DIR/TAES_10P_R3_SUPPLEMENTARY_README.txt"
MAIN="$DIR/TAES_10P_R3_MANUSCRIPT_IEEETRAN_R8_DEV.pdf"
R9="$DIR/TAES_MANUSCRIPT.pdf"
FIG="$DIR/TAES_FIGURE1_RESIDUAL_BOUNDARIES.png"

for FILE in "$PDF" "$TEX" "$LOG" "$AUDIT" "$PATCH_AUDIT" "$SOURCE" "$README" "$MAIN" "$R9" "$FIG"; do
  if [[ ! -f "$FILE" ]]; then
    echo "ERROR: expected file missing: $FILE"
    exit 1
  fi
done

echo "=== CORRECTED CROSS-REFERENCE VISIBLE TEXT ==="
pdftotext "$PDF" - | grep -nE 'Table S1 values are logical model time|Table S2 gives the complete frozen map|Table S3 reports the canonical gate summary|denominators in Table S3 are finite model populations' || true

if pdftotext "$PDF" - | grep -Eq 'Table II values are logical model time|Table III gives the complete frozen map|Table IV reports the canonical gate summary|denominators in Table IV are finite model populations'; then
  echo "ERROR: stale R9 table cross-reference remains in corrected supplement PDF"
  exit 1
fi

echo "=== PDF INFO ==="
pdfinfo "$PDF" | grep -E 'Pages:|Page size:|PDF version:'

echo "=== BUILD AUDIT ==="
cat "$AUDIT"

echo "=== FONT EMBEDDING ==="
pdffonts "$PDF"

echo "=== SHA256 ==="
shasum -a 256 "$SOURCE" "$README" "$FIG" "$MAIN" "$R9" "$TEX" "$PDF" "$LOG" "$AUDIT" "$PATCH_AUDIT"

echo "=== BUILD GATE ASSERTIONS ==="
grep -Fx 'TAES_10P_R3_SUPPLEMENTARY_BUILD=PASS_COMPILED_DEVELOPMENT_ONLY' "$AUDIT"
grep -Fx 'supplement_build_revision=9' "$AUDIT"
grep -Fx 'table_cross_reference_gate=PASS_S1_S2_S3_NO_LEGACY_II_III_IV' "$AUDIT"
grep -Fx 'overfull_hbox_count=0' "$AUDIT"
grep -Fx 'latex_warning_count=0' "$AUDIT"
grep -Fx 'font_embedding_all_yes=PASS' "$AUDIT"
grep -Fx 'supplement_content_changed=YES_EDITORIAL_CROSSREF_ONLY' "$AUDIT"
grep -Fx 'supplement_table_values_changed=NO' "$AUDIT"
grep -Fx 'experimental_results_changed=NO' "$AUDIT"
grep -Fx 'science_files_changed=NONE' "$AUDIT"
grep -Fx 'study_rerun=NO' "$AUDIT"

echo "=== READ-ONLY SCIENCE-PRESERVATION AUDIT ==="
python3 "$DIR/TAES_AUDIT_SHORT_TRACK_SCIENCE_PRESERVATION_R1.py"

if [[ ! -f "$SCIENCE_AUDIT" ]]; then
  echo "ERROR: science-preservation audit file missing"
  exit 1
fi

grep -Fx 'TAES_SHORT_TRACK_SCIENCE_PRESERVATION=PASS' "$SCIENCE_AUDIT"
grep -Fx 'study3_population_and_key_results=PASS_PRESERVED' "$SCIENCE_AUDIT"
grep -Fx 'study4_complete_18_rule_map=PASS_PRESERVED_IN_SUPPLEMENT' "$SCIENCE_AUDIT"
grep -Fx 'study6_complete_gate_frontier=PASS_PRESERVED' "$SCIENCE_AUDIT"
grep -Fx 'tracked_changes_outside_paper2_taes_directory=NONE' "$SCIENCE_AUDIT"
grep -Fx 'experimental_results_changed=NO' "$SCIENCE_AUDIT"
grep -Fx 'frozen_study_sources_changed=NO' "$SCIENCE_AUDIT"
grep -Fx 'study_rerun=NO' "$SCIENCE_AUDIT"
grep -Fx 'pooled_population_introduced=NO' "$SCIENCE_AUDIT"

echo "=== SCIENCE-PRESERVATION AUDIT ==="
cat "$SCIENCE_AUDIT"

echo "TAES_SUPPLEMENT_R9_CORRECTED_FINAL_GATE=PASS"
echo "corrected_supplement_pdf=$PDF"
echo "corrected_supplement_pdf_sha256=$(shasum -a 256 "$PDF" | awk '{print $1}')"
echo "corrected_supplement_source_sha256=$(shasum -a 256 "$SOURCE" | awk '{print $1}')"
echo "science_preservation_audit_sha256=$(shasum -a 256 "$SCIENCE_AUDIT" | awk '{print $1}')"
