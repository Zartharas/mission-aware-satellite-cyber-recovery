#!/usr/bin/env python3
"""Revision-6 supplementary-PDF builder for the TAES Paper-2 short track.

R5 normalizes Pandoc's captionless longtable LTcaptype wrapper for TeX Live 2026.
A proactive local layout audit then showed that Pandoc's natural-width table
columns would materially overflow for Tables S1 and S3 even after that compile
compatibility fix.

R6 preserves the exact R5 source/conversion pipeline and changes only generated
LaTeX table layout for the three supplementary tables. It applies fixed-width
p-columns, local small font, and local tabcolsep while preserving every visible
cell value, label, order, and identifier.

No supplementary Markdown, figure asset, manuscript text, frozen result,
reference, science file, or publisher-facing artifact is changed.
"""

from __future__ import annotations

from pathlib import Path

import TAES_BUILD_10P_SUPPLEMENT_R1 as r1
import TAES_BUILD_10P_SUPPLEMENT_R3 as r3
import TAES_BUILD_10P_SUPPLEMENT_R5 as r5

ROOT = Path(__file__).resolve().parent

OUT_TEX = ROOT / "TAES_10P_R3_SUPPLEMENTARY_MATERIAL_R6_DEV.tex"
OUT_PDF = ROOT / "TAES_10P_R3_SUPPLEMENTARY_MATERIAL_R6_DEV.pdf"
OUT_LOG = ROOT / "TAES_10P_R3_SUPPLEMENTARY_MATERIAL_R6_DEV.log"
OUT_AUDIT = ROOT / "TAES_10P_R3_SUPPLEMENTARY_R6_BUILD_AUDIT.txt"

TABLE_REWRITES = (
    (
        r"\begin{longtable}[]{@{}lrrl@{}}",
        r"\small\setlength{\tabcolsep}{4pt}"
        r"\begin{longtable}[]{@{}"
        r">{\raggedright\arraybackslash}p{0.25\textwidth}"
        r">{\centering\arraybackslash}p{0.14\textwidth}"
        r">{\centering\arraybackslash}p{0.18\textwidth}"
        r">{\raggedright\arraybackslash}p{0.32\textwidth}@{}}",
        "S1",
    ),
    (
        r"\begin{longtable}[]{@{}lrr@{}}",
        r"\small\setlength{\tabcolsep}{4pt}"
        r"\begin{longtable}[]{@{}"
        r">{\raggedright\arraybackslash}p{0.14\textwidth}"
        r">{\centering\arraybackslash}p{0.36\textwidth}"
        r">{\centering\arraybackslash}p{0.40\textwidth}@{}}",
        "S2",
    ),
    (
        r"\begin{longtable}[]{@{}lrlrr@{}}",
        r"\small\setlength{\tabcolsep}{4pt}"
        r"\begin{longtable}[]{@{}"
        r">{\raggedright\arraybackslash}p{0.23\textwidth}"
        r">{\centering\arraybackslash}p{0.10\textwidth}"
        r">{\raggedright\arraybackslash}p{0.35\textwidth}"
        r">{\centering\arraybackslash}p{0.08\textwidth}"
        r">{\centering\arraybackslash}p{0.10\textwidth}@{}}",
        "S3",
    ),
)


def build_tex_r6(source: str) -> tuple[str, int]:
    """Run exact R5 build, then normalize only supplementary table widths."""
    tex, break_count = r5.build_tex_r5(source)

    for old, new, label in TABLE_REWRITES:
        hits = tex.count(old)
        if hits != 1:
            raise SystemExit(
                f"ERROR: R6 expected exactly one Pandoc natural-width Table {label} "
                f"signature; found {hits}"
            )
        tex = tex.replace(old, new, 1)

    if tex.count(r"\begin{longtable}") != 3:
        raise SystemExit(
            "ERROR: R6 expected exactly three longtables after layout normalization"
        )

    # Guard visible table content after layout-only transformation.
    normalized = tex.replace(r"\allowbreak{}", "")
    required = [
        "Table S1",
        "Persistent \\texttt{V5}",
        "46/46",
        "122.500",
        "Table S2",
        r"\texttt{Q3\_D3}",
        "3/6",
        "2/5",
        "Table S3",
        r"\texttt{G5\_COMPOSITE}",
        r"\texttt{APPROVED\_BAD\_SOURCE}",
        "1/5",
        "63/64",
    ]
    missing = [marker for marker in required if marker not in normalized]
    if missing:
        raise SystemExit(
            "ERROR: R6 table-layout normalization lost protected visible marker(s): "
            + ", ".join(missing)
        )

    if r"\sloppy" in tex:
        raise SystemExit("ERROR: R6 supplement TeX unexpectedly contains \\sloppy")

    return tex, break_count


def main() -> None:
    # Preserve all R1/R3/R4/R5 scientific and hash bindings while isolating R6
    # development outputs.
    r1.OUT_TEX = OUT_TEX
    r1.OUT_PDF = OUT_PDF
    r1.OUT_LOG = OUT_LOG
    r1.OUT_AUDIT = OUT_AUDIT
    r1.pandoc_body = r3.pandoc_body_r3_prebreak
    r1.build_tex = build_tex_r6

    print("TAES_10P_R3_SUPPLEMENTARY_BUILD_REVISION=6")
    print("r6_change=FIXED_WIDTH_LONGTABLE_LAYOUT_ONLY")
    print("pandoc_reader=gfm")
    print("raw_tex_reader_extension=NOT_USED")
    print("figure_raw_tex_reinjected_after_pandoc=YES")
    print("semantic_marker_stage=PRE_BREAK_GENERATED_LATEX")
    print("breakable_identifier_stage=POST_MARKER_DOCUMENT_LATEX")
    print("texlive_basic_compatibility=ENABLED")
    print("removed_optional_packages=enumitem,caption,xurl,float")
    print("captionless_longtable_count=3")
    print("ltcaptype_after=EMPTY")
    print("table_s1_fixed_width=YES")
    print("table_s2_fixed_width=YES")
    print("table_s3_fixed_width=YES")
    print("table_local_font=small")
    print("table_local_tabcolsep_pt=4")
    print("supplement_source_changed=NO")
    print("supplement_visible_content_changed=NO")

    r1.main()

    if not OUT_AUDIT.is_file():
        raise SystemExit("ERROR: R6 expected build audit missing after successful pipeline")
    with OUT_AUDIT.open("a", encoding="utf-8") as handle:
        handle.write("supplement_build_revision=6\n")
        handle.write("r6_change=FIXED_WIDTH_LONGTABLE_LAYOUT_ONLY\n")
        handle.write("pandoc_reader=gfm\n")
        handle.write("raw_tex_reader_extension=NOT_USED\n")
        handle.write("figure_raw_tex_reinjected_after_pandoc=YES\n")
        handle.write("semantic_marker_stage=PRE_BREAK_GENERATED_LATEX\n")
        handle.write("breakable_identifier_stage=POST_MARKER_DOCUMENT_LATEX\n")
        handle.write("texlive_basic_compatibility=ENABLED\n")
        handle.write("removed_optional_packages=enumitem,caption,xurl,float\n")
        handle.write("captionless_longtable_count=3\n")
        handle.write("ltcaptype_after=EMPTY\n")
        handle.write("table_s1_fixed_width=YES\n")
        handle.write("table_s2_fixed_width=YES\n")
        handle.write("table_s3_fixed_width=YES\n")
        handle.write("table_local_font=small\n")
        handle.write("table_local_tabcolsep_pt=4\n")
        handle.write("supplement_source_changed=NO\n")
        handle.write("supplement_visible_content_changed=NO\n")


if __name__ == "__main__":
    main()
