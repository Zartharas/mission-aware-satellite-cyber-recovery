#!/usr/bin/env python3
"""Revision-2 supplementary-PDF builder for the TAES Paper-2 short track.

R1 stopped before TeX materialization because the installed Pandoc does not
support the reader specification ``gfm+raw_tex``. R2 preserves the exact bound
supplementary Markdown, GFM parsing, Figure S1 asset, R8 main article, and R9
fallback. It changes only how the generated raw-LaTeX Figure S1 include block
passes through Pandoc:

1. replace exactly one generated Figure S1 raw-LaTeX block with a neutral token;
2. run Pandoc with ``--from=gfm``;
3. replace exactly one token in the generated LaTeX with the exact Figure S1
   LaTeX block;
4. continue with the unchanged R1 build and audit pipeline.

No manuscript content, frozen result, table value, reference, science file, or
publisher-facing artifact is changed.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import TAES_BUILD_10P_SUPPLEMENT_R1 as r1

ROOT = Path(__file__).resolve().parent

OUT_TEX = ROOT / "TAES_10P_R3_SUPPLEMENTARY_MATERIAL_R2_DEV.tex"
OUT_PDF = ROOT / "TAES_10P_R3_SUPPLEMENTARY_MATERIAL_R2_DEV.pdf"
OUT_LOG = ROOT / "TAES_10P_R3_SUPPLEMENTARY_MATERIAL_R2_DEV.log"
OUT_AUDIT = ROOT / "TAES_10P_R3_SUPPLEMENTARY_R2_BUILD_AUDIT.txt"

FIGURE_LATEX_BLOCK = "\\begin{center}\n\\includegraphics[width=0.96\\textwidth]{TAES_FIGURE1_RESIDUAL_BOUNDARIES.png}\n\\end{center}"
FIGURE_PLACEHOLDER = "TAESSUPPFIGURESPLACEHOLDER"


def pandoc_body_r2(markdown_body: str) -> tuple[str, int]:
    figure_hits = markdown_body.count(FIGURE_LATEX_BLOCK)
    if figure_hits != 1:
        raise SystemExit(
            "ERROR: R2 expected exactly one generated Fig. S1 raw-LaTeX block "
            f"before Pandoc; found {figure_hits}"
        )
    if FIGURE_PLACEHOLDER in markdown_body:
        raise SystemExit("ERROR: R2 placeholder token already present in supplement body")

    pandoc_input = markdown_body.replace(FIGURE_LATEX_BLOCK, FIGURE_PLACEHOLDER, 1)

    with tempfile.TemporaryDirectory(prefix="taes_supp_r2_") as tmp:
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
    placeholder_hits = tex.count(FIGURE_PLACEHOLDER)
    if placeholder_hits != 1:
        raise SystemExit(
            "ERROR: R2 expected exactly one Fig. S1 placeholder after Pandoc; "
            f"found {placeholder_hits}"
        )

    tex = tex.replace(FIGURE_PLACEHOLDER, FIGURE_LATEX_BLOCK, 1)
    if tex.count(FIGURE_LATEX_BLOCK) != 1:
        raise SystemExit("ERROR: R2 failed to restore exactly one Fig. S1 LaTeX block")

    tex, break_count = r1.make_breakable_texttt(tex)
    return tex, break_count


def main() -> None:
    # Preserve the R1 scientific/content bindings while isolating R2 outputs.
    r1.OUT_TEX = OUT_TEX
    r1.OUT_PDF = OUT_PDF
    r1.OUT_LOG = OUT_LOG
    r1.OUT_AUDIT = OUT_AUDIT
    r1.pandoc_body = pandoc_body_r2

    print("TAES_10P_R3_SUPPLEMENTARY_BUILD_REVISION=2")
    print("r2_change=GFM_RAW_TEX_FIGURE_PLACEHOLDER_POSTCONVERSION_ONLY")
    print("pandoc_reader=gfm")
    print("raw_tex_reader_extension=NOT_USED")
    print("figure_raw_tex_reinjected_after_pandoc=YES")

    r1.main()

    # Append revision provenance to the R1-format build audit after a successful
    # build. This does not affect any bound source or generated PDF content.
    if not OUT_AUDIT.is_file():
        raise SystemExit("ERROR: R2 expected build audit missing after successful R1 pipeline")
    with OUT_AUDIT.open("a", encoding="utf-8") as handle:
        handle.write("supplement_build_revision=2\n")
        handle.write("r2_change=GFM_RAW_TEX_FIGURE_PLACEHOLDER_POSTCONVERSION_ONLY\n")
        handle.write("pandoc_reader=gfm\n")
        handle.write("raw_tex_reader_extension=NOT_USED\n")
        handle.write("figure_raw_tex_reinjected_after_pandoc=YES\n")


if __name__ == "__main__":
    main()
