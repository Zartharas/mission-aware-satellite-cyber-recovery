#!/usr/bin/env python3
"""Revision-7 supplementary-PDF builder for the TAES Paper-2 short track.

R6 fixes the three supplementary table widths proactively. R7 preserves that
exact generated content and adds final build-hardening only:

1. assert that each R6 table-local ``\\small``/``\\tabcolsep`` declaration remains
   inside Pandoc's captionless-longtable brace group;
2. make the PDF text gate whitespace-insensitive so discretionary identifier
   line breaks cannot create false failures;
3. parse the actual ``emb`` field from ``pdffonts``;
4. require zero final overfull boxes, zero LaTeX warnings, embedded fonts, and
   US-Letter output before the development build is accepted.

No supplementary Markdown, visible table content, figure asset, manuscript text,
frozen result, reference, science file, or publisher-facing artifact is changed.
"""

from __future__ import annotations

import re
from pathlib import Path

import TAES_BUILD_10P_SUPPLEMENT_R1 as r1
import TAES_BUILD_10P_SUPPLEMENT_R3 as r3
import TAES_BUILD_10P_SUPPLEMENT_R6 as r6

ROOT = Path(__file__).resolve().parent

OUT_TEX = ROOT / "TAES_10P_R3_SUPPLEMENTARY_MATERIAL_R7_DEV.tex"
OUT_PDF = ROOT / "TAES_10P_R3_SUPPLEMENTARY_MATERIAL_R7_DEV.pdf"
OUT_LOG = ROOT / "TAES_10P_R3_SUPPLEMENTARY_MATERIAL_R7_DEV.log"
OUT_AUDIT = ROOT / "TAES_10P_R3_SUPPLEMENTARY_R7_BUILD_AUDIT.txt"


def _compact_visible(value: str) -> str:
    """Remove extraction/layout whitespace without changing visible characters."""
    return re.sub(r"\s+", "", value.replace("\u00ad", ""))


def text_gate_r7(pdf: Path) -> None:
    """Whitespace-insensitive visible-text gate for line-breakable identifiers."""
    text = r1.run(["pdftotext", str(pdf), "-"]).stdout
    compact = _compact_visible(text)
    markers = [
        "Supplementary Material",
        r1.TITLE,
        "Supplementary Figure S1",
        "Fig. S1.",
        "Appendix A",
        "Appendix B",
        "Appendix C",
        "Appendix D",
        "Appendix E",
        "Table S1",
        "Table S2",
        "Table S3",
        "1,380 trajectories",
        "4,608 exact observations",
        "420 exact observations",
        "PRE_ONSET_CACHE",
        "APPROVED_BAD_SOURCE",
    ]
    missing = [marker for marker in markers if _compact_visible(marker) not in compact]
    if missing:
        raise SystemExit(
            "ERROR: R7 supplement PDF normalized text-gate missing: "
            + ", ".join(missing)
        )


def font_audit_r7(pdf: Path) -> tuple[int, bool]:
    """Read the actual pdffonts 'emb' field (fifth token from row end)."""
    out = r1.run(["pdffonts", str(pdf)]).stdout
    lines = [line for line in out.splitlines()[2:] if line.strip()]
    embedded = True
    for line in lines:
        parts = line.split()
        if len(parts) < 5:
            raise SystemExit("ERROR: R7 unable to parse pdffonts row: " + line)
        emb = parts[-5].lower()
        if emb not in {"yes", "no"}:
            raise SystemExit(
                "ERROR: R7 unexpected pdffonts embedding field "
                f"{emb!r} in row: {line}"
            )
        if emb != "yes":
            embedded = False
    return len(lines), embedded


def build_tex_r7(source: str) -> tuple[str, int]:
    """Run exact R6 generated content and assert table-local scoping."""
    tex, break_count = r6.build_tex_r6(source)

    # Pandoc 3.8 wraps each captionless longtable in a brace group containing
    # \def\LTcaptype{...}. R5 normalizes the value to empty. R6's local table
    # declarations must remain inside those existing groups.
    scoped_pattern = re.compile(
        r"\{\\def\\LTcaptype\{\}.*?"
        r"\\small\\setlength\{\\tabcolsep\}\{4pt\}"
        r"\\begin\{longtable\}.*?\\end\{longtable\}\s*\}",
        flags=re.DOTALL,
    )
    scoped = scoped_pattern.findall(tex)
    if len(scoped) != 3:
        raise SystemExit(
            "ERROR: R7 expected all three fixed-width longtables to remain "
            f"inside Pandoc captionless-table groups; found {len(scoped)}"
        )

    if tex.count(r"\small\setlength{\tabcolsep}{4pt}") != 3:
        raise SystemExit("ERROR: R7 expected exactly three table-local size/spacing declarations")
    if tex.count(r"\begin{longtable}") != 3 or tex.count(r"\end{longtable}") != 3:
        raise SystemExit("ERROR: R7 supplementary longtable count changed")
    if r"\sloppy" in tex:
        raise SystemExit("ERROR: R7 supplement TeX unexpectedly contains \\sloppy")

    return tex, break_count


def main() -> None:
    # Preserve all R1/R3/R5/R6 source, science, figure, R8-main, and R9 bindings.
    r1.OUT_TEX = OUT_TEX
    r1.OUT_PDF = OUT_PDF
    r1.OUT_LOG = OUT_LOG
    r1.OUT_AUDIT = OUT_AUDIT
    r1.pandoc_body = r3.pandoc_body_r3_prebreak
    r1.build_tex = build_tex_r7
    r1.text_gate = text_gate_r7
    r1.font_audit = font_audit_r7

    print("TAES_10P_R3_SUPPLEMENTARY_BUILD_REVISION=7")
    print("r7_change=FINAL_BUILD_HARDENING_ONLY")
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
    print("final_mechanical_gate=ENABLED")
    print("supplement_source_changed=NO")
    print("supplement_visible_content_changed=NO")

    r1.main()

    if not OUT_PDF.is_file() or not OUT_LOG.is_file() or not OUT_AUDIT.is_file():
        raise SystemExit("ERROR: R7 expected output artifact missing after successful pipeline")

    log = OUT_LOG.read_text(encoding="utf-8", errors="replace")
    boxes = r1.box_counts(log)
    if boxes["overfull_hbox"] != 0:
        raise SystemExit(
            f"ERROR: R7 final overfull hbox count is {boxes['overfull_hbox']}, expected 0"
        )
    if boxes["overfull_vbox"] != 0:
        raise SystemExit(
            f"ERROR: R7 final overfull vbox count is {boxes['overfull_vbox']}, expected 0"
        )
    if boxes["latex_warning"] != 0:
        raise SystemExit(
            f"ERROR: R7 final LaTeX warning count is {boxes['latex_warning']}, expected 0"
        )

    font_count, all_embedded = font_audit_r7(OUT_PDF)
    if font_count < 1:
        raise SystemExit("ERROR: R7 supplement PDF contains no reported fonts")
    if not all_embedded:
        raise SystemExit("ERROR: R7 supplement PDF contains a non-embedded font")

    pages, page_size = r1.parse_pdfinfo(OUT_PDF)
    if pages < 1:
        raise SystemExit("ERROR: R7 supplement PDF has no pages")
    if "612 x 792 pts" not in page_size:
        raise SystemExit("ERROR: R7 supplement PDF is not US Letter: " + page_size)

    with OUT_AUDIT.open("a", encoding="utf-8") as handle:
        handle.write("supplement_build_revision=7\n")
        handle.write("r7_change=FINAL_BUILD_HARDENING_ONLY\n")
        handle.write("table_local_scope_assertion=PASS\n")
        handle.write("pdf_text_gate=WHITESPACE_INSENSITIVE_VISIBLE_TEXT\n")
        handle.write("pdffonts_embedding_field=EMB\n")
        handle.write("final_overfull_hbox_gate=PASS_ZERO\n")
        handle.write("final_overfull_vbox_gate=PASS_ZERO\n")
        handle.write("final_latex_warning_gate=PASS_ZERO\n")
        handle.write("final_font_embedding_gate=PASS_ALL_EMBEDDED\n")
        handle.write("final_page_size_gate=PASS_US_LETTER\n")
        handle.write("final_mechanical_gate=PASS\n")
        handle.write("supplement_source_changed=NO\n")
        handle.write("supplement_visible_content_changed=NO\n")

    print("R7_FINAL_MECHANICAL_GATE=PASS")
    print(f"r7_pages={pages}")
    print(f"r7_page_size={page_size}")
    print(f"r7_font_count={font_count}")
    print("r7_font_embedding_all_yes=PASS")
    print("r7_overfull_hbox_count=0")
    print("r7_overfull_vbox_count=0")
    print("r7_latex_warning_count=0")


if __name__ == "__main__":
    main()
