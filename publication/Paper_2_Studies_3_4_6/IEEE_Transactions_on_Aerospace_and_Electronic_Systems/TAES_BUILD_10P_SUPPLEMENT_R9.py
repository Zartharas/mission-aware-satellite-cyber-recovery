#!/usr/bin/env python3
"""Build corrected TAES Paper-2 short-track Supplement R9.

R9 changes visible supplement content only by the four authorized stale table
cross-reference corrections recorded by TAES_APPLY_SUPPLEMENT_R9_CROSSREF_FIX.py.
All numerical results, tables, figure content, study populations, science files,
paired R8 main article, and frozen R9 16-page fallback remain unchanged.
"""
from __future__ import annotations

import re
import shutil
from pathlib import Path

import TAES_BUILD_10P_SUPPLEMENT_R1 as r1
import TAES_BUILD_10P_SUPPLEMENT_R3 as r3
import TAES_BUILD_10P_SUPPLEMENT_R7 as r7

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "TAES_10P_R3_SUPPLEMENTARY_MATERIAL.md"
PATCH_AUDIT = ROOT / "TAES_10P_R3_SUPPLEMENTARY_R9_CROSSREF_FIX_AUDIT.txt"

OUT_TEX = ROOT / "TAES_10P_R3_SUPPLEMENTARY_MATERIAL_R9_DEV.tex"
OUT_PDF = ROOT / "TAES_10P_R3_SUPPLEMENTARY_MATERIAL_R9_DEV.pdf"
OUT_LOG = ROOT / "TAES_10P_R3_SUPPLEMENTARY_MATERIAL_R9_DEV.log"
OUT_AUDIT = ROOT / "TAES_10P_R3_SUPPLEMENTARY_R9_BUILD_AUDIT.txt"

OLD_SOURCE_SHA = "e6313fca178f9de40a6b7c28468be6b20ae1fc7249c2e3c8e30ca5fbf0d7027c"

CROSSREF_NEW = (
    "Table S1 values are logical model time, not spacecraft response time, communication latency, operator latency, or ground-contact duration.",
    "Table S2 gives the complete frozen map as `first/systematic` counts.",
    "Table S3 reports the canonical gate summary.",
    "Again, the denominators in Table S3 are finite model populations.",
)
CROSSREF_OLD = (
    "Table II values are logical model time, not spacecraft response time, communication latency, operator latency, or ground-contact duration.",
    "Table III gives the complete frozen map as `first/systematic` counts.",
    "Table IV reports the canonical gate summary.",
    "Again, the denominators in Table IV are finite model populations.",
)


def corrected_sha_from_audit() -> str:
    if not PATCH_AUDIT.is_file():
        raise SystemExit("ERROR: missing R9 cross-reference correction audit")
    text = PATCH_AUDIT.read_text(encoding="utf-8", errors="strict")
    match = re.search(r"^corrected_supplement_sha256=([0-9a-f]{64})$", text, re.MULTILINE)
    if not match:
        raise SystemExit("ERROR: corrected supplement SHA missing from R9 correction audit")
    return match.group(1)


def crossref_pdf_gate(pdf: Path) -> None:
    text = r1.run(["pdftotext", str(pdf), "-"]).stdout
    compact = re.sub(r"\s+", " ", text.replace("\u00ad", " ")).strip()
    required = (
        "Table S1 values are logical model time",
        "Table S2 gives the complete frozen map as first/systematic counts.",
        "Table S3 reports the canonical gate summary.",
        "denominators in Table S3 are finite model populations.",
    )
    missing = [marker for marker in required if marker not in compact]
    if missing:
        raise SystemExit("ERROR: R9 PDF corrected cross-reference gate missing: " + ", ".join(missing))
    forbidden = (
        "Table II values are logical model time",
        "Table III gives the complete frozen map",
        "Table IV reports the canonical gate summary",
        "denominators in Table IV are finite model populations",
    )
    present = [marker for marker in forbidden if marker in compact]
    if present:
        raise SystemExit("ERROR: R9 PDF stale table cross-reference survived: " + ", ".join(present))


def main() -> None:
    for command in r1.REQUIRED_COMMANDS:
        if not shutil.which(command):
            raise SystemExit(f"ERROR: required command missing: {command}")

    corrected_sha = corrected_sha_from_audit()
    if corrected_sha == OLD_SOURCE_SHA:
        raise SystemExit("ERROR: R9 corrected supplement SHA unexpectedly equals R8 source SHA")

    r1.require_file(SOURCE, corrected_sha, "corrected R9 supplementary Markdown")
    r1.require_file(r1.SUPP_README, r1.EXPECTED_README, "R3 supplementary README")
    r1.require_file(r1.FIGURE_PNG, r1.EXPECTED_FIGURE_PNG, "Supplementary Fig. S1 PNG")
    r1.require_file(r1.MAIN_R8_PDF, r1.EXPECTED_MAIN_R8_PDF, "visually approved R8 main PDF")
    r1.require_file(r1.FROZEN_R9_PDF, r1.EXPECTED_FROZEN_R9_PDF, "frozen R9 fallback PDF")

    source = SOURCE.read_text(encoding="utf-8").replace("\r\n", "\n")
    if "—" in source:
        raise SystemExit("ERROR: em dash detected in corrected supplementary source")
    if "6,408" in source:
        raise SystemExit("ERROR: pooled Paper-2 population detected in corrected supplement")
    for old in CROSSREF_OLD:
        if old in source:
            raise SystemExit("ERROR: stale table cross-reference remains in corrected source: " + old)
    for new in CROSSREF_NEW:
        if source.count(new) != 1:
            raise SystemExit("ERROR: corrected table cross-reference count is not exactly one: " + new)

    r1.EXPECTED_SUPP_MD = corrected_sha
    r1.OUT_TEX = OUT_TEX
    r1.OUT_PDF = OUT_PDF
    r1.OUT_LOG = OUT_LOG
    r1.OUT_AUDIT = OUT_AUDIT
    r1.pandoc_body = r3.pandoc_body_r3_prebreak
    r1.build_tex = r7.build_tex_r7
    r1.text_gate = r7.text_gate_r7
    r1.font_audit = r7.font_audit_r7

    tex, break_count = r7.build_tex_r7(source)
    OUT_TEX.write_text(tex, encoding="utf-8")

    r1.run([
        "latexmk",
        "-pdf",
        "-interaction=nonstopmode",
        "-halt-on-error",
        "-file-line-error",
        OUT_TEX.name,
    ], cwd=ROOT)

    if not OUT_PDF.is_file() or not OUT_LOG.is_file():
        raise SystemExit("ERROR: R9 supplement build did not create expected PDF/log")

    pages, page_size = r1.parse_pdfinfo(OUT_PDF)
    log = OUT_LOG.read_text(encoding="utf-8", errors="replace")
    boxes = r1.box_counts(log)
    font_count, all_fonts_embedded = r7.font_audit_r7(OUT_PDF)
    r7.text_gate_r7(OUT_PDF)
    crossref_pdf_gate(OUT_PDF)

    if boxes["overfull_hbox"] != 0:
        raise SystemExit(f"ERROR: R9 final overfull hbox count is {boxes['overfull_hbox']}, expected 0")
    if boxes["latex_warning"] != 0:
        raise SystemExit(f"ERROR: R9 final LaTeX warning count is {boxes['latex_warning']}, expected 0")
    if font_count < 1 or not all_fonts_embedded:
        raise SystemExit("ERROR: R9 supplement font embedding gate failed")
    if "612 x 792 pts" not in page_size:
        raise SystemExit("ERROR: R9 supplement PDF is not US Letter: " + page_size)

    audit_lines = [
        "TAES_10P_R3_SUPPLEMENTARY_BUILD=PASS_COMPILED_DEVELOPMENT_ONLY",
        "supplement_build_revision=9",
        "r9_change=FOUR_STALE_TABLE_CROSS_REFERENCES_CORRECTED_ONLY",
        f"pre_correction_supplement_sha256={OLD_SOURCE_SHA}",
        f"corrected_supplement_sha256={corrected_sha}",
        f"supplement_readme_sha256={r1.EXPECTED_README}",
        f"figure_s1_png_sha256={r1.EXPECTED_FIGURE_PNG}",
        f"paired_main_r8_pdf_sha256={r1.EXPECTED_MAIN_R8_PDF}",
        f"frozen_r9_fallback_pdf_sha256={r1.EXPECTED_FROZEN_R9_PDF}",
        f"tex_sha256={r1.sha256(OUT_TEX)}",
        f"pdf_sha256={r1.sha256(OUT_PDF)}",
        f"log_sha256={r1.sha256(OUT_LOG)}",
        f"pages={pages}",
        f"page_size={page_size}",
        f"overfull_hbox_count={boxes['overfull_hbox']}",
        f"overfull_vbox_count={boxes['overfull_vbox']}",
        f"underfull_hbox_count={boxes['underfull_hbox']}",
        f"underfull_vbox_count={boxes['underfull_vbox']}",
        f"latex_warning_count={boxes['latex_warning']}",
        f"font_count={font_count}",
        f"font_embedding_all_yes={'PASS' if all_fonts_embedded else 'FAIL'}",
        f"breakable_code_insertions={break_count}",
        "figure_s1_embedded=YES",
        "appendices_a_e_text_gate=PASS",
        "tables_s1_s2_s3_text_gate=PASS",
        "table_cross_reference_gate=PASS_S1_S2_S3_NO_LEGACY_II_III_IV",
        "main_article_appended=NO",
        "main_article_page_count_changed=NO",
        "supplement_content_changed=YES_EDITORIAL_CROSSREF_ONLY",
        "supplement_table_values_changed=NO",
        "experimental_results_changed=NO",
        "science_files_changed=NONE",
        "study_rerun=NO",
        "publisher_facing=NO",
        "supplement_visual_qa_required=YES_FOCUSED_CROSSREF_AND_LAYOUT",
        "merge_to_main=NOT_AUTHORIZED_UNTIL_QA_PASS",
    ]
    OUT_AUDIT.write_text("\n".join(audit_lines) + "\n", encoding="utf-8")
    for line in audit_lines:
        print(line)

    print("R9_FINAL_PREVISUAL_MECHANICAL_GATE=PASS")


if __name__ == "__main__":
    main()
