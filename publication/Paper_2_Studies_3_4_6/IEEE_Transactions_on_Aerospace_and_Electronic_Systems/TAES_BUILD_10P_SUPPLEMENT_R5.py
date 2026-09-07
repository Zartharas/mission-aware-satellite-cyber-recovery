#!/usr/bin/env python3
"""Revision-5 supplementary-PDF builder for the TAES Paper-2 short track.

R4 reached pdflatex with the bound supplementary content but stopped because the
installed Pandoc emits captionless longtables with ``\\def\\LTcaptype{none}``.
TeX Live 2026 longtable interprets a nonempty LTcaptype as a counter name and no
counter named ``none`` exists.

R5 preserves the exact R4 source/conversion/preamble pipeline and changes only
that generated-LaTeX compatibility wrapper for the three supplementary tables:

    \\def\\LTcaptype{none}  ->  \\def\\LTcaptype{}

An empty LTcaptype is supported by the current longtable implementation and
preserves the intended captionless/no-table-counter semantics. No Markdown,
visible table content, figure asset, manuscript text, frozen result, reference,
science file, or publisher-facing artifact is changed.
"""

from __future__ import annotations

from pathlib import Path

import TAES_BUILD_10P_SUPPLEMENT_R1 as r1
import TAES_BUILD_10P_SUPPLEMENT_R3 as r3
import TAES_BUILD_10P_SUPPLEMENT_R4 as r4

ROOT = Path(__file__).resolve().parent

OUT_TEX = ROOT / "TAES_10P_R3_SUPPLEMENTARY_MATERIAL_R5_DEV.tex"
OUT_PDF = ROOT / "TAES_10P_R3_SUPPLEMENTARY_MATERIAL_R5_DEV.pdf"
OUT_LOG = ROOT / "TAES_10P_R3_SUPPLEMENTARY_MATERIAL_R5_DEV.log"
OUT_AUDIT = ROOT / "TAES_10P_R3_SUPPLEMENTARY_R5_BUILD_AUDIT.txt"

EXPECTED_SUPPLEMENTARY_TABLES = 3


def build_tex_r5(source: str) -> tuple[str, int]:
    """Run exact R4 conversion, then normalize Pandoc captionless LTcaptype."""
    tex, break_count = r4.build_tex_r4(source)

    bad_token = r"\def\LTcaptype{none}"
    good_token = r"\def\LTcaptype{}"
    longtable_token = r"\begin{longtable}"

    bad_hits = tex.count(bad_token)
    longtable_hits = tex.count(longtable_token)

    if longtable_hits != EXPECTED_SUPPLEMENTARY_TABLES:
        raise SystemExit(
            "ERROR: R5 expected exactly three supplementary longtables; "
            f"found {longtable_hits}"
        )
    if bad_hits != longtable_hits:
        raise SystemExit(
            "ERROR: R5 expected each captionless longtable to have one Pandoc "
            f"LTcaptype=none wrapper; wrappers={bad_hits} longtables={longtable_hits}"
        )

    tex = tex.replace(bad_token, good_token)

    if bad_token in tex:
        raise SystemExit("ERROR: R5 LTcaptype=none wrapper survived normalization")
    if tex.count(good_token) != EXPECTED_SUPPLEMENTARY_TABLES:
        raise SystemExit(
            "ERROR: R5 expected exactly three empty LTcaptype wrappers after "
            f"normalization; found {tex.count(good_token)}"
        )

    # Visible supplement content and table structures must remain intact.
    required_visible_markers = [
        "Table S1",
        "Table S2",
        "Table S3",
        "S3-K4E-001",
        "S4-MPQ-001",
        "S6-SCTR-001",
    ]
    normalized = tex.replace(r"\allowbreak{}", "")
    missing = [marker for marker in required_visible_markers if marker not in normalized]
    if missing:
        raise SystemExit(
            "ERROR: R5 longtable compatibility normalization lost protected marker(s): "
            + ", ".join(missing)
        )

    if r"\sloppy" in tex:
        raise SystemExit("ERROR: R5 supplement TeX unexpectedly contains \\sloppy")

    return tex, break_count


def main() -> None:
    # Preserve all R1/R3/R4 scientific, source-hash, figure, main-article, and
    # frozen-R9 bindings while isolating R5 development outputs.
    r1.OUT_TEX = OUT_TEX
    r1.OUT_PDF = OUT_PDF
    r1.OUT_LOG = OUT_LOG
    r1.OUT_AUDIT = OUT_AUDIT
    r1.pandoc_body = r3.pandoc_body_r3_prebreak
    r1.build_tex = build_tex_r5

    print("TAES_10P_R3_SUPPLEMENTARY_BUILD_REVISION=5")
    print("r5_change=PANDOC_CAPTIONLESS_LONGTABLE_LTCAPTYPE_NORMALIZATION_ONLY")
    print("pandoc_reader=gfm")
    print("raw_tex_reader_extension=NOT_USED")
    print("figure_raw_tex_reinjected_after_pandoc=YES")
    print("semantic_marker_stage=PRE_BREAK_GENERATED_LATEX")
    print("breakable_identifier_stage=POST_MARKER_DOCUMENT_LATEX")
    print("texlive_basic_compatibility=ENABLED")
    print("removed_optional_packages=enumitem,caption,xurl,float")
    print("captionless_longtable_count=3")
    print("ltcaptype_before=none")
    print("ltcaptype_after=EMPTY")
    print("supplement_source_changed=NO")
    print("supplement_visible_content_changed=NO")

    r1.main()

    if not OUT_AUDIT.is_file():
        raise SystemExit("ERROR: R5 expected build audit missing after successful pipeline")
    with OUT_AUDIT.open("a", encoding="utf-8") as handle:
        handle.write("supplement_build_revision=5\n")
        handle.write("r5_change=PANDOC_CAPTIONLESS_LONGTABLE_LTCAPTYPE_NORMALIZATION_ONLY\n")
        handle.write("pandoc_reader=gfm\n")
        handle.write("raw_tex_reader_extension=NOT_USED\n")
        handle.write("figure_raw_tex_reinjected_after_pandoc=YES\n")
        handle.write("semantic_marker_stage=PRE_BREAK_GENERATED_LATEX\n")
        handle.write("breakable_identifier_stage=POST_MARKER_DOCUMENT_LATEX\n")
        handle.write("texlive_basic_compatibility=ENABLED\n")
        handle.write("removed_optional_packages=enumitem,caption,xurl,float\n")
        handle.write("captionless_longtable_count=3\n")
        handle.write("ltcaptype_before=none\n")
        handle.write("ltcaptype_after=EMPTY\n")
        handle.write("supplement_source_changed=NO\n")
        handle.write("supplement_visible_content_changed=NO\n")


if __name__ == "__main__":
    main()
