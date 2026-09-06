#!/usr/bin/env python3
"""Generate TAES Paper 2 Figure 1 in the canonical publication directory.

Figure 1 is a manuscript-level qualitative synthesis of three separately frozen
experiments. It deliberately uses three parallel panels with no connecting
arrows so that the graphic cannot imply an integrated experimental pipeline.

Outputs:
  TAES_FIGURE1_RESIDUAL_BOUNDARIES.pdf  (primary vector master)
  TAES_FIGURE1_RESIDUAL_BOUNDARIES.png  (300-dpi visual-QA preview)

This script does not read, rerun, or modify any study result.
"""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle
from matplotlib import font_manager

ROOT = Path(__file__).resolve().parent
PDF_OUT = ROOT / "TAES_FIGURE1_RESIDUAL_BOUNDARIES.pdf"
PNG_OUT = ROOT / "TAES_FIGURE1_RESIDUAL_BOUNDARIES.png"

FIG_W = 7.16
FIG_H = 4.65


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def choose_font() -> str:
    available = {f.name for f in font_manager.fontManager.ttflist}
    for name in ("Arial", "Helvetica", "Liberation Sans", "DejaVu Sans"):
        if name in available:
            return name
    return "DejaVu Sans"


def add_wrapped_text(ax, x, y, text, *, size=8.4, weight="normal", va="top"):
    ax.text(
        x,
        y,
        text,
        transform=ax.transAxes,
        ha="left",
        va=va,
        fontsize=size,
        fontweight=weight,
        linespacing=1.18,
        wrap=True,
    )


def draw_panel(ax, title, subtitle, visible, truth, residual, effect):
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    outer = FancyBboxPatch(
        (0.015, 0.02), 0.97, 0.96,
        boxstyle="round,pad=0.012,rounding_size=0.018",
        linewidth=1.15,
        edgecolor="black",
        facecolor="white",
        transform=ax.transAxes,
        clip_on=False,
    )
    ax.add_patch(outer)

    header = Rectangle(
        (0.03, 0.835), 0.94, 0.125,
        linewidth=0,
        facecolor="0.90",
        transform=ax.transAxes,
    )
    ax.add_patch(header)

    add_wrapped_text(ax, 0.055, 0.935, title, size=9.3, weight="bold")
    add_wrapped_text(ax, 0.055, 0.875, subtitle, size=8.3)

    sections = [
        ("Gate-visible evidence", visible),
        ("Research-only truth", truth),
        ("Residual boundary", residual),
        ("Effect of stronger composition", effect),
    ]
    ys = [0.795, 0.575, 0.425, 0.235]
    body_sizes = [7.9, 8.0, 7.9, 7.8]
    for (heading, body), y, body_size in zip(sections, ys, body_sizes):
        add_wrapped_text(ax, 0.055, y, heading, size=8.2, weight="bold")
        add_wrapped_text(ax, 0.055, y - 0.055, body, size=body_size)


def main() -> None:
    font_name = choose_font()
    plt.rcParams.update({
        "font.family": font_name,
        "font.size": 8.5,
        "axes.linewidth": 0.8,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
    })

    fig = plt.figure(figsize=(FIG_W, FIG_H), facecolor="white")

    # Global anti-overclaim banner.
    fig.text(
        0.5, 0.965,
        "Three separately frozen experiments | qualitative synthesis only | no pooled population | no experimental data flow",
        ha="center", va="top", fontsize=9.0, fontweight="bold",
    )

    gs = fig.add_gridspec(
        1, 3,
        left=0.025, right=0.975, bottom=0.105, top=0.91,
        wspace=0.055,
    )

    ax1 = fig.add_subplot(gs[0, 0])
    draw_panel(
        ax1,
        "Study 3",
        "Temporal runtime evidence",
        "Signature validity; freshness; received authorization evidence; contact-dependent record availability; security signal.",
        "Hidden authorization truth.",
        "Fresh, validly signed V5 evidence can remain false; a truthful pre-onset cache can briefly lag a state change.",
        "K4 contact-aware restriction reduces selected modeled exposure, but persistent V5 qualification remains for B0/S1.",
    )

    ax2 = fig.add_subplot(gs[0, 1])
    draw_panel(
        ax2,
        "Study 4",
        "Producer composition",
        "Signed producer claims; vote threshold; synthetic provenance-domain count.",
        "Hidden authorization truth.",
        "Same-size compromised subsets can differ in whether the qualification rule is satisfied.",
        "Provenance can delay systematic unsafe qualification and cause earlier benign rejection for selected subsets; null effects remain.",
    )

    ax3 = fig.add_subplot(gs[0, 2])
    draw_panel(
        ax3,
        "Study 6",
        "Recovery-artifact assurance",
        "Signature; digest; provenance; reproduced-build match; source-review attestation; release approval.",
        "Objective baseline correctness.",
        "APPROVED_BAD_SOURCE remains qualified when all six gate-visible assurance signals are true.",
        "Additional signals close specified modeled states while increasing sensitivity to benign assurance-signal loss.",
    )

    fig.text(
        0.5, 0.038,
        "Parallel panels summarize separate finite models; this is not an integrated recovery architecture, and only Study 3 models contact.",
        ha="center", va="bottom", fontsize=8.3,
    )

    fixed_date = datetime(2026, 9, 6, 0, 0, 0, tzinfo=timezone.utc)
    pdf_meta = {
        "Title": "TAES Paper 2 Figure 1 - Parallel Residual Trust Boundaries",
        "Author": "Aman Kumar Singh",
        "Subject": "Qualitative cross-study synthesis of separately frozen experiments",
        "Keywords": "satellite cyber recovery; residual trust boundary; evidence qualification",
        "Creator": "TAES_GENERATE_FIGURE1.py",
        "Producer": "Matplotlib",
        "CreationDate": fixed_date,
        "ModDate": fixed_date,
    }

    fig.savefig(PDF_OUT, format="pdf", bbox_inches="tight", pad_inches=0.03, metadata=pdf_meta)
    fig.savefig(PNG_OUT, format="png", dpi=300, bbox_inches="tight", pad_inches=0.03)
    plt.close(fig)

    print("TAES_FIGURE1_GENERATION=PASS")
    print(f"font={font_name}")
    print(f"figure_width_in={FIG_W}")
    print(f"figure_height_in={FIG_H}")
    print(f"pdf={PDF_OUT}")
    print(f"pdf_sha256={sha256(PDF_OUT)}")
    print(f"png={PNG_OUT}")
    print(f"png_sha256={sha256(PNG_OUT)}")
    print("figure_claim_scope=QUALITATIVE_SYNTHESIS_ONLY")
    print("integrated_experiment_implied=NO")
    print("contact_model_scope=STUDY3_ONLY")
    print("NOTE: visually inspect the PNG at full two-column width before manuscript insertion.")


if __name__ == "__main__":
    main()
