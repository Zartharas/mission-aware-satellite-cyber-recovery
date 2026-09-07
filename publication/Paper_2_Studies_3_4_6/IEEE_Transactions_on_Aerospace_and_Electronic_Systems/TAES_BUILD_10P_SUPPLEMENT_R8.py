#!/usr/bin/env python3
"""Revision-8 supplementary-PDF builder for the TAES Paper-2 short track.

R8 is the final pre-visual-QA development builder. It preserves R7's source,
conversion, fixed-width tables, table-scope assertion, normalized PDF text gate,
and corrected font-embedding parser. It refines only the final gate policy:

- overfull horizontal boxes remain fatal;
- LaTeX warnings remain fatal;
- non-embedded fonts remain fatal;
- non-Letter output remains fatal;
- overfull vertical boxes are recorded diagnostically and deferred to visual QA.

This avoids rejecting a visually sound PDF solely for output-routine/page-building
vertical-box diagnostics. No visible supplement content or science is changed.
"""

from __future__ import annotations

from pathlib import Path

import TAES_BUILD_10P_SUPPLEMENT_R1 as r1
import TAES_BUILD_10P_SUPPLEMENT_R3 as r3
import TAES_BUILD_10P_SUPPLEMENT_R7 as r7

ROOT = Path(__file__).resolve().parent

OUT_TEX = ROOT / "TAES_10P_R3_SUPPLEMENTARY_MATERIAL_R8_DEV.tex"
OUT_PDF = ROOT / "TAES_10P_R3_SUPPLEMENTARY_MATERIAL_R8_DEV.pdf"
OUT_LOG = ROOT / "TAES_10P_R3_SUPPLEMENTARY_MATERIAL_R8_DEV.log"
OUT_AUDIT = ROOT / "TAES_10P_R3_SUPPLEMENTARY_R8_BUILD_AUDIT.txt"


def main() -> None:
    # Preserve all prior scientific/source/hash bindings while isolating R8 dev outputs.
    r1.OUT_TEX = OUT_TEX
    r1.OUT_PDF = OUT_PDF
    r1.OUT_LOG = OUT_LOG
    r1.OUT_AUDIT = OUT_AUDIT
    r1.pandoc_body = r3.pandoc_body_r3_prebreak
    r1.build_tex = r7.build_tex_r7
    r1.text_gate = r7.text_gate_r7
    r1.font_audit = r7.font_audit_r7

    print("TAES_10P_R3_SUPPLEMENTARY_BUILD_REVISION=8")
    print("r8_change=FINAL_GATE_POLICY_REFINEMENT_ONLY")
    print("pandoc_reader=gfm")
    print("raw_tex_reader_extension=NOT_USED")
    print("figure_raw_tex_reinjected_after_pandoc=YES")
    print("semantic_marker_stage=PRE_BREAK_GENERATED_LATEX")
    print("breakable_identifier_stage=POST_MARKER_DOCUMENT_LATEX")
    print("texlive_basic_compatibility=ENABLED")
    print("captionless_longtable_count=3")
    print("fixed_width_longtable_count=3")
    print("table_local_scope_assertion=ENABLED")
    print("pdf_text_gate=WHITESPACE_INSENSITIVE_VISIBLE_TEXT")
    print("pdffonts_embedding_field=EMB")
    print("overfull_hbox_gate=FATAL_ZERO_REQUIRED")
    print("overfull_vbox_gate=DIAGNOSTIC_VISUAL_QA")
    print("latex_warning_gate=FATAL_ZERO_REQUIRED")
    print("font_embedding_gate=FATAL_ALL_EMBEDDED")
    print("page_size_gate=FATAL_US_LETTER")
    print("supplement_source_changed=NO")
    print("supplement_visible_content_changed=NO")

    r1.main()

    if not OUT_PDF.is_file() or not OUT_LOG.is_file() or not OUT_AUDIT.is_file():
        raise SystemExit("ERROR: R8 expected output artifact missing after successful pipeline")

    log = OUT_LOG.read_text(encoding="utf-8", errors="replace")
    boxes = r1.box_counts(log)

    if boxes["overfull_hbox"] != 0:
        raise SystemExit(
            f"ERROR: R8 final overfull hbox count is {boxes['overfull_hbox']}, expected 0"
        )
    if boxes["latex_warning"] != 0:
        raise SystemExit(
            f"ERROR: R8 final LaTeX warning count is {boxes['latex_warning']}, expected 0"
        )

    font_count, all_embedded = r7.font_audit_r7(OUT_PDF)
    if font_count < 1:
        raise SystemExit("ERROR: R8 supplement PDF contains no reported fonts")
    if not all_embedded:
        raise SystemExit("ERROR: R8 supplement PDF contains a non-embedded font")

    pages, page_size = r1.parse_pdfinfo(OUT_PDF)
    if pages < 1:
        raise SystemExit("ERROR: R8 supplement PDF has no pages")
    if "612 x 792 pts" not in page_size:
        raise SystemExit("ERROR: R8 supplement PDF is not US Letter: " + page_size)

    with OUT_AUDIT.open("a", encoding="utf-8") as handle:
        handle.write("supplement_build_revision=8\n")
        handle.write("r8_change=FINAL_GATE_POLICY_REFINEMENT_ONLY\n")
        handle.write("table_local_scope_assertion=PASS\n")
        handle.write("pdf_text_gate=WHITESPACE_INSENSITIVE_VISIBLE_TEXT\n")
        handle.write("pdffonts_embedding_field=EMB\n")
        handle.write("final_overfull_hbox_gate=PASS_ZERO\n")
        handle.write(f"final_overfull_vbox_count={boxes['overfull_vbox']}\n")
        handle.write("final_overfull_vbox_gate=DIAGNOSTIC_VISUAL_QA\n")
        handle.write("final_latex_warning_gate=PASS_ZERO\n")
        handle.write("final_font_embedding_gate=PASS_ALL_EMBEDDED\n")
        handle.write("final_page_size_gate=PASS_US_LETTER\n")
        handle.write("final_previsual_mechanical_gate=PASS\n")
        handle.write("supplement_source_changed=NO\n")
        handle.write("supplement_visible_content_changed=NO\n")

    print("R8_FINAL_PREVISUAL_MECHANICAL_GATE=PASS")
    print(f"r8_pages={pages}")
    print(f"r8_page_size={page_size}")
    print(f"r8_font_count={font_count}")
    print("r8_font_embedding_all_yes=PASS")
    print("r8_overfull_hbox_count=0")
    print(f"r8_overfull_vbox_count={boxes['overfull_vbox']}")
    print("r8_overfull_vbox_review=DEFER_TO_VISUAL_QA")
    print("r8_latex_warning_count=0")


if __name__ == "__main__":
    main()
