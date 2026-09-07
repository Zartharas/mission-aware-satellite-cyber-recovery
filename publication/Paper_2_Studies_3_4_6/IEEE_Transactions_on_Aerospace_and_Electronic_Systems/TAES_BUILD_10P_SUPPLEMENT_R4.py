#!/usr/bin/env python3
"""Revision-4 supplementary-PDF builder for the TAES Paper-2 short track.

R3 reached pdflatex successfully but TeX Live 2026 Basic stopped on the unused
optional dependency ``enumitem.sty``. The R1 preamble also loads ``caption``,
``xurl``, and ``float`` although this supplement does not use package-specific
commands from those packages.

R4 preserves the exact R3 content/conversion pipeline and removes only those
unused optional package loads from the generated document preamble. The body
LaTeX, Figure S1 block, longtables, lists, hyperlinks, margins, source hashes,
main R8 article, and frozen R9 fallback remain bound and unchanged.

No supplementary prose, table value, figure asset, manuscript text, frozen
result, reference, science file, or publisher-facing artifact is changed.
"""

from __future__ import annotations

from pathlib import Path

import TAES_BUILD_10P_SUPPLEMENT_R1 as r1
import TAES_BUILD_10P_SUPPLEMENT_R3 as r3

ROOT = Path(__file__).resolve().parent

OUT_TEX = ROOT / "TAES_10P_R3_SUPPLEMENTARY_MATERIAL_R4_DEV.tex"
OUT_PDF = ROOT / "TAES_10P_R3_SUPPLEMENTARY_MATERIAL_R4_DEV.pdf"
OUT_LOG = ROOT / "TAES_10P_R3_SUPPLEMENTARY_MATERIAL_R4_DEV.log"
OUT_AUDIT = ROOT / "TAES_10P_R3_SUPPLEMENTARY_R4_BUILD_AUDIT.txt"

_UNUSED_OPTIONAL_PACKAGES = ("enumitem", "caption", "xurl", "float")


def build_tex_r4(source: str) -> tuple[str, int]:
    """Run exact R3 conversion, then remove only unused optional package loads."""
    tex, break_count = r3.build_tex_r3(source)

    removed: list[str] = []
    for package in _UNUSED_OPTIONAL_PACKAGES:
        token = f"\\usepackage{{{package}}}\n"
        hits = tex.count(token)
        if hits != 1:
            raise SystemExit(
                f"ERROR: R4 expected exactly one preamble load for {package}; found {hits}"
            )
        tex = tex.replace(token, "", 1)
        removed.append(package)

    # Guard against accidentally relying on package-specific commands from the
    # removed optional packages. Standard article/longtable \caption and ordinary
    # itemize/enumerate environments are intentionally allowed.
    forbidden_after_removal = [
        r"\setlist",
        r"\newlist",
        r"\captionsetup",
        r"\captionof",
        r"\restylefloat",
        r"\newfloat",
    ]
    present = [marker for marker in forbidden_after_removal if marker in tex]
    if present:
        raise SystemExit(
            "ERROR: R4 removed optional package but generated TeX uses package-specific command(s): "
            + ", ".join(present)
        )

    for package in removed:
        if f"\\usepackage{{{package}}}" in tex:
            raise SystemExit(f"ERROR: R4 optional package load survived: {package}")

    if r"\sloppy" in tex:
        raise SystemExit("ERROR: R4 supplement TeX unexpectedly contains \\sloppy")

    return tex, break_count


def main() -> None:
    # Preserve all R1/R3 scientific, source-hash, figure, main-article, and R9
    # bindings while isolating R4 development outputs.
    r1.OUT_TEX = OUT_TEX
    r1.OUT_PDF = OUT_PDF
    r1.OUT_LOG = OUT_LOG
    r1.OUT_AUDIT = OUT_AUDIT
    r1.pandoc_body = r3.pandoc_body_r3_prebreak
    r1.build_tex = build_tex_r4

    print("TAES_10P_R3_SUPPLEMENTARY_BUILD_REVISION=4")
    print("r4_change=REMOVE_UNUSED_OPTIONAL_TEX_PACKAGES_ONLY")
    print("pandoc_reader=gfm")
    print("raw_tex_reader_extension=NOT_USED")
    print("figure_raw_tex_reinjected_after_pandoc=YES")
    print("semantic_marker_stage=PRE_BREAK_GENERATED_LATEX")
    print("breakable_identifier_stage=POST_MARKER_DOCUMENT_LATEX")
    print("texlive_basic_compatibility=ENABLED")
    print("removed_optional_packages=enumitem,caption,xurl,float")
    print("supplement_body_latex_changed=NO")

    r1.main()

    if not OUT_AUDIT.is_file():
        raise SystemExit("ERROR: R4 expected build audit missing after successful R1 pipeline")
    with OUT_AUDIT.open("a", encoding="utf-8") as handle:
        handle.write("supplement_build_revision=4\n")
        handle.write("r4_change=REMOVE_UNUSED_OPTIONAL_TEX_PACKAGES_ONLY\n")
        handle.write("pandoc_reader=gfm\n")
        handle.write("raw_tex_reader_extension=NOT_USED\n")
        handle.write("figure_raw_tex_reinjected_after_pandoc=YES\n")
        handle.write("semantic_marker_stage=PRE_BREAK_GENERATED_LATEX\n")
        handle.write("breakable_identifier_stage=POST_MARKER_DOCUMENT_LATEX\n")
        handle.write("texlive_basic_compatibility=ENABLED\n")
        handle.write("removed_optional_packages=enumitem,caption,xurl,float\n")
        handle.write("supplement_body_latex_changed=NO\n")


if __name__ == "__main__":
    main()
