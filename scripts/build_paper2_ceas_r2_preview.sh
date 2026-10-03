#!/usr/bin/env bash
# Editable reviewer proof only. No publisher submission.
set -euo pipefail
ROOT="$(git rev-parse --show-toplevel)"
OUT="$ROOT/.paper2_ceas_r2_preview"
if [ "$#" -ge 1 ]; then OUT="$1"; fi
mkdir -p "$OUT"
OUT="$(cd "$OUT" && pwd)"
M="$ROOT/publication/Paper_2_Studies_3_4_6/CEAS_Space_Journal/MANUSCRIPT_CEAS_R2_2026-10-02.md"
F="$ROOT/publication/Paper_2_Studies_3_4_6/Post_Rejection_Rebuild/figures/PAPER2_R2_FIGURE1_RESIDUAL_BOUNDARIES.svg"
DOC="$OUT/PAPER2_CEAS_R2_REVIEW_PROOF.docx"
PDF="$OUT/PAPER2_CEAS_R2_REVIEW_PROOF.pdf"
for c in pandoc libreoffice inkscape pdfinfo pdftotext pdftoppm; do
  command -v "$c" >/dev/null || { echo "MISSING_TOOL_$c"; exit 2; }
done
test -s "$M"
test -s "$F"
cp "$F" "$OUT/Fig1_original.svg"
inkscape "$F" --export-filename="$OUT/Fig1.eps" >/dev/null 2>&1
test -s "$OUT/Fig1.eps"
pandoc "$M" -f markdown+pipe_tables -t docx \
 --resource-path="$ROOT/publication/Paper_2_Studies_3_4_6/CEAS_Space_Journal:$ROOT/publication/Paper_2_Studies_3_4_6/Post_Rejection_Rebuild" \
 --metadata="lang:en-US" -o "$DOC"
test -s "$DOC"
P="$(mktemp -d)"
trap 'rm -rf "$P"' EXIT
libreoffice -env:UserInstallation="file://$P" --headless --convert-to pdf --outdir "$OUT" "$DOC" >/dev/null
test -s "$PDF"
pdfinfo "$PDF" | grep -E 'Pages:|Page size:'
pdftotext -layout "$PDF" "$OUT/PAPER2_CEAS_R2_REVIEW_PROOF.txt"
for phrase in "Residual Trust Boundaries" "Study 3" "Study 4" "Study 6" "Table 1" "Table 2" "Table 3" "Table 4" "Table 5" "References"; do
 grep -Fq "$phrase" "$OUT/PAPER2_CEAS_R2_REVIEW_PROOF.txt" || { echo "MISSING_PDF_PHRASE_$phrase"; exit 3; }
done
/usr/bin/python3 - "$DOC" <<'PY'
from docx import Document
import zipfile,sys
doc=sys.argv[1]
d=Document(doc)
assert len(d.tables)==5,('tables',len(d.tables))
assert len(d.inline_shapes)>=1,('embedded_figure',len(d.inline_shapes))
with zipfile.ZipFile(doc) as z:
    assert any(n.startswith('word/media/') for n in z.namelist())
print('DOCX_FIVE_TABLES_AND_ONE_EMBEDDED_GRAPHIC=PASS')
PY
pdftoppm -f 1 -l 1 -scale-to 1400 -png -singlefile "$PDF" "$OUT/PAGE1_SAMPLE" >/dev/null 2>&1
test -s "$OUT/PAGE1_SAMPLE.png"
printf '%s\n' "CEAS_R2_REVIEW_PROOF_BUILT=YES" "AUTHOR_CONTACT_AND_DATA_ACCESS_CONFIRMATION_PENDING=YES" "PUBLISHER_SUBMISSION=NO" > "$OUT/REVIEW_STATUS.txt"
echo "CEAS_R2_PREVIEW_BUILD=PASS"
