#!/bin/bash
set -u

ROOT="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(git -C "$ROOT" rev-parse --show-toplevel 2>/dev/null || true)"

if [[ -z "$REPO_ROOT" ]]; then
  echo "ERROR: unable to resolve repository root"
  exit 2
fi

if [[ -x "/Library/TeX/texbin/latexmk" ]]; then
  export PATH="/Library/TeX/texbin:$PATH"
fi
hash -r 2>/dev/null || true

required=(python3 pandoc latexmk pdflatex pdfinfo pdffonts pdftotext shasum)
for cmd in "${required[@]}"; do
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "ERROR: required command missing: $cmd"
    exit 2
  fi
done

echo "TAES_SUPPLEMENT_R8_FINAL_PREVISUAL_GATE=START"
echo "branch=$(git -C "$REPO_ROOT" branch --show-current)"
echo "head=$(git -C "$REPO_ROOT" rev-parse HEAD)"
echo "pandoc=$(pandoc --version | head -1)"
echo "latexmk=$(latexmk -v | head -1)"

python3 "$ROOT/TAES_BUILD_10P_SUPPLEMENT_R8.py"
rc=$?
if [[ "$rc" -ne 0 ]]; then
  echo "TAES_SUPPLEMENT_R8_FINAL_PREVISUAL_GATE=FAIL_BUILD"
  exit "$rc"
fi

PDF="$ROOT/TAES_10P_R3_SUPPLEMENTARY_MATERIAL_R8_DEV.pdf"
TEX="$ROOT/TAES_10P_R3_SUPPLEMENTARY_MATERIAL_R8_DEV.tex"
LOG="$ROOT/TAES_10P_R3_SUPPLEMENTARY_MATERIAL_R8_DEV.log"
AUDIT="$ROOT/TAES_10P_R3_SUPPLEMENTARY_R8_BUILD_AUDIT.txt"
MAIN="$ROOT/TAES_10P_R3_MANUSCRIPT_IEEETRAN_R8_DEV.pdf"
R9="$ROOT/TAES_MANUSCRIPT.pdf"
SUPP_MD="$ROOT/TAES_10P_R3_SUPPLEMENTARY_MATERIAL.md"
SUPP_README="$ROOT/TAES_10P_R3_SUPPLEMENTARY_README.txt"
FIG="$ROOT/TAES_FIGURE1_RESIDUAL_BOUNDARIES.png"

for f in "$PDF" "$TEX" "$LOG" "$AUDIT" "$MAIN" "$R9" "$SUPP_MD" "$SUPP_README" "$FIG"; do
  if [[ ! -f "$f" ]]; then
    echo "ERROR: expected gate artifact missing: $f"
    exit 3
  fi
done

echo "=== FINAL PREVISUAL GATE SUMMARY ==="
grep -E '^(TAES_10P_R3_SUPPLEMENTARY_BUILD=|pages=|page_size=|overfull_hbox_count=|overfull_vbox_count=|underfull_hbox_count=|underfull_vbox_count=|latex_warning_count=|font_count=|font_embedding_all_yes=|figure_s1_embedded=|appendices_a_e_text_gate=|tables_s1_s2_s3_text_gate=|main_article_appended=|main_article_page_count_changed=|supplement_content_changed=|science_files_changed=|study_rerun=|supplement_build_revision=|final_overfull_hbox_gate=|final_overfull_vbox_count=|final_overfull_vbox_gate=|final_latex_warning_gate=|final_font_embedding_gate=|final_page_size_gate=|final_previsual_mechanical_gate=)' "$AUDIT" || true

echo "=== PDF INFO ==="
pdfinfo "$PDF" | grep -E 'Pages:|Page size:|PDF version:'

echo "=== FONT EMBEDDING ==="
pdffonts "$PDF"

echo "=== PROTECTED SHA256 ==="
shasum -a 256 "$SUPP_MD" "$SUPP_README" "$FIG" "$MAIN" "$R9" "$PDF" "$TEX" "$LOG" "$AUDIT"

echo "=== OUTPUT ==="
echo "supplement_pdf=$PDF"
echo "supplement_pdf_sha256=$(shasum -a 256 "$PDF" | awk '{print $1}')"
echo "supplement_pages=$(pdfinfo "$PDF" | awk '/^Pages:/ {print $2}')"
echo "main_r8_sha256=$(shasum -a 256 "$MAIN" | awk '{print $1}')"
echo "frozen_r9_sha256=$(shasum -a 256 "$R9" | awk '{print $1}')"

echo "TAES_SUPPLEMENT_R8_FINAL_PREVISUAL_GATE=PASS"
exit 0
