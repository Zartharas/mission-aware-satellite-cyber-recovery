#!/usr/bin/env python3
"""Revision-3 supplementary-PDF builder for the TAES Paper-2 short track.

R2 successfully kept the GFM Pandoc reader and reinjected the generated raw-LaTeX
Fig. S1 block after conversion, but it inserted discretionary ``\\allowbreak{}``
commands before the R1 semantic marker gate. R1 then searched post-break TeX for
pre-break literals such as ``S3-K4E-001`` and stopped before TeX materialization.

R3 changes validation order only:

1. keep R2's exact GFM figure-placeholder/reinjection strategy;
2. return pre-break generated body LaTeX to the unchanged R1 semantic marker gate;
3. after R1 marker validation and document assembly, insert discretionary breaks
   into ``\\texttt{}`` identifiers;
4. validate that removing only ``\\allowbreak{}`` commands recovers all protected
   Study identifiers.

No supplementary prose, table value, figure asset, manuscript text, frozen
result, reference, science file, or publisher-facing artifact is changed.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import TAES_BUILD_10P_SUPPLEMENT_R1 as r1
import TAES_BUILD_10P_SUPPLEMENT_R2 as r2

ROOT = Path(__file__).resolve().parent

OUT_TEX = ROOT / "TAES_10P_R3_SUPPLEMENTARY_MATERIAL_R3_DEV.tex"
OUT_PDF = ROOT / "TAES_10P_R3_SUPPLEMENTARY_MATERIAL_R3_DEV.pdf"
OUT_LOG = ROOT / "TAES_10P_R3_SUPPLEMENTARY_MATERIAL_R3_DEV.log"
OUT_AUDIT = ROOT / "TAES_10P_R3_SUPPLEMENTARY_R3_BUILD_AUDIT.txt"

_R1_BUILD_TEX = r1.build_tex


def pandoc_body_r3_prebreak(markdown_body: str) -> tuple[str, int]:
    """Run R2's GFM-safe figure reinjection but defer breakable-code insertion."""
    figure_hits = markdown_body.count(r2.FIGURE_LATEX_BLOCK)
    if figure_hits != 1:
        raise SystemExit(
            "ERROR: R3 expected exactly one generated Fig. S1 raw-LaTeX block "
            f"before Pandoc; found {figure_hits}"
        )
    if r2.FIGURE_PLACEHOLDER in markdown_body:
        raise SystemExit("ERROR: R3 placeholder token already present in supplement body")

    pandoc_input = markdown_body.replace(
        r2.FIGURE_LATEX_BLOCK, r2.FIGURE_PLACEHOLDER, 1
    )

    with tempfile.TemporaryDirectory(prefix="taes_supp_r3_") as tmp:
        tmp_path = Path(tmp)
        md_path = tmp_path / "body.md"
        md_path.write_text(pandoc_input, encoding="utf-8")
        proc = r1.run([
            "pandoc",
            str(md_path),
            "--from=gfm",
            "--to=latex",
            "--wrap=none",
        ], cwd=r1.ROOT)

    tex = proc.stdout
    placeholder_hits = tex.count(r2.FIGURE_PLACEHOLDER)
    if placeholder_hits != 1:
        raise SystemExit(
            "ERROR: R3 expected exactly one Fig. S1 placeholder after Pandoc; "
            f"found {placeholder_hits}"
        )

    tex = tex.replace(r2.FIGURE_PLACEHOLDER, r2.FIGURE_LATEX_BLOCK, 1)
    if tex.count(r2.FIGURE_LATEX_BLOCK) != 1:
        raise SystemExit("ERROR: R3 failed to restore exactly one Fig. S1 LaTeX block")

    # Deliberately no discretionary-break insertion here. R1 must first validate
    # semantic literals against the pre-break generated body TeX.
    return tex, 0


def build_tex_r3(source: str) -> tuple[str, int]:
    """Run the unchanged R1 marker gate first, then add breakable identifiers."""
    tex, prebreak_count = _R1_BUILD_TEX(source)
    if prebreak_count != 0:
        raise SystemExit(
            "ERROR: R3 expected zero discretionary breaks before semantic marker gate; "
            f"found {prebreak_count}"
        )

    tex, break_count = r1.make_breakable_texttt(tex)

    if r"\sloppy" in tex:
        raise SystemExit("ERROR: R3 supplement TeX unexpectedly contains \\sloppy")
    if r2.FIGURE_PLACEHOLDER in tex:
        raise SystemExit("ERROR: R3 temporary figure placeholder survived into final TeX")
    if tex.count(r2.FIGURE_LATEX_BLOCK) != 1:
        raise SystemExit("ERROR: R3 final TeX does not contain exactly one Fig. S1 block")

    normalized = tex.replace(r"\allowbreak{}", "")
    protected_ids = ["S3-K4E-001", "S4-MPQ-001", "S6-SCTR-001"]
    missing = [marker for marker in protected_ids if marker not in normalized]
    if missing:
        raise SystemExit(
            "ERROR: R3 post-break normalization failed protected Study identifiers: "
            + ", ".join(missing)
        )

    return tex, break_count


def main() -> None:
    # Preserve all R1 scientific/content/hash bindings while isolating R3 outputs.
    r1.OUT_TEX = OUT_TEX
    r1.OUT_PDF = OUT_PDF
    r1.OUT_LOG = OUT_LOG
    r1.OUT_AUDIT = OUT_AUDIT
    r1.pandoc_body = pandoc_body_r3_prebreak
    r1.build_tex = build_tex_r3

    print("TAES_10P_R3_SUPPLEMENTARY_BUILD_REVISION=3")
    print("r3_change=SEMANTIC_MARKER_GATE_BEFORE_DISCRETIONARY_BREAK_INSERTION")
    print("pandoc_reader=gfm")
    print("raw_tex_reader_extension=NOT_USED")
    print("figure_raw_tex_reinjected_after_pandoc=YES")
    print("semantic_marker_stage=PRE_BREAK_GENERATED_LATEX")
    print("breakable_identifier_stage=POST_MARKER_DOCUMENT_LATEX")

    r1.main()

    if not OUT_AUDIT.is_file():
        raise SystemExit("ERROR: R3 expected build audit missing after successful R1 pipeline")
    with OUT_AUDIT.open("a", encoding="utf-8") as handle:
        handle.write("supplement_build_revision=3\n")
        handle.write("r3_change=SEMANTIC_MARKER_GATE_BEFORE_DISCRETIONARY_BREAK_INSERTION\n")
        handle.write("pandoc_reader=gfm\n")
        handle.write("raw_tex_reader_extension=NOT_USED\n")
        handle.write("figure_raw_tex_reinjected_after_pandoc=YES\n")
        handle.write("semantic_marker_stage=PRE_BREAK_GENERATED_LATEX\n")
        handle.write("breakable_identifier_stage=POST_MARKER_DOCUMENT_LATEX\n")


if __name__ == "__main__":
    main()
