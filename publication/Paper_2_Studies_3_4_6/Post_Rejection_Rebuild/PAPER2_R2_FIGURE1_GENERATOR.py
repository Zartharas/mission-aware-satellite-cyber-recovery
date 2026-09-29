#!/usr/bin/env python3
"""Generate deterministic PDF/PNG renders from the tracked Paper-2 R2 Figure-1 SVG source."""

from __future__ import annotations

import hashlib
import os
from pathlib import Path

import cairosvg

ROOT = Path(__file__).resolve().parent
FIG = ROOT / "figures"
SVG = FIG / "PAPER2_R2_FIGURE1_RESIDUAL_BOUNDARIES.svg"
PDF = FIG / "PAPER2_R2_FIGURE1_RESIDUAL_BOUNDARIES.pdf"
PNG = FIG / "PAPER2_R2_FIGURE1_RESIDUAL_BOUNDARIES.png"

SOURCE_DATE_EPOCH = "1790553600"
PDF_WIDTH_PT = 515.52
PDF_HEIGHT_PT = 417.60
PNG_WIDTH_PX = 2148
PNG_HEIGHT_PX = 1740


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    if not SVG.is_file():
        raise SystemExit(f"missing tracked SVG source: {SVG}")

    os.environ["SOURCE_DATE_EPOCH"] = SOURCE_DATE_EPOCH
    source = SVG.read_bytes()

    cairosvg.svg2pdf(
        bytestring=source,
        write_to=str(PDF),
        output_width=PDF_WIDTH_PT,
        output_height=PDF_HEIGHT_PT,
    )
    cairosvg.svg2png(
        bytestring=source,
        write_to=str(PNG),
        output_width=PNG_WIDTH_PX,
        output_height=PNG_HEIGHT_PX,
    )

    print("PAPER2_R2_FIGURE1_GENERATION=PASS")
    print("layout_revision=3")
    print(f"svg_sha256={sha256(SVG)}")
    print(f"pdf_sha256={sha256(PDF)}")
    print(f"png_sha256={sha256(PNG)}")
    print("figure_width_in=7.16")
    print("figure_height_in=5.80")
    print("png_width_px=2148")
    print("png_height_px=1740")
    print("figure_claim_scope=QUALITATIVE_SYNTHESIS_ONLY")
    print("integrated_experiment_implied=NO")
    print("study3_k4_contact_scope=SYNTHETIC_ONLY")
    print("s3x_contact_loss_interpretation=PROHIBITED")


if __name__ == "__main__":
    main()
