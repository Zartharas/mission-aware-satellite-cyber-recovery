#!/usr/bin/env python3
"""Generate TAES Paper 2 Figure 1 in the canonical publication directory.

Figure 1 is a manuscript-level qualitative synthesis of three separately frozen
experiments. It deliberately uses three parallel panels with no connecting
arrows so that the graphic cannot imply an integrated experimental pipeline.

Revision 2 replaces Matplotlib's automatic wrapping with explicit line wrapping
and adds a post-layout overflow check. This prevents long text from silently
crossing panel boundaries at two-column width.

Outputs:
  TAES_FIGURE1_RESIDUAL_BOUNDARIES.pdf  (primary vector master)
  TAES_FIGURE1_RESIDUAL_BOUNDARIES.png  (300-dpi visual-QA preview)

This script does not read, rerun, or modify any study result.
"""

from __future__ import annotations

import hashlib
import textwrap
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
FIG_H = 5.15
WRAP_WIDTH = 33


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


def wrap_text(text: str, width: int = WRAP_WIDTH) -> str:
    return "\n".join(
        textwrap.wrap(
            text,
            width=width,
            break_long_words=False,
            break_on_hyphens=False,
        )
    )


def add_text(ax, registry, x, y, text, *, size=7.6, weight="normal", va="top", label=""):
    artist = ax.text(
        x,
        y,
        text,
        transform=ax.transAxes,
        ha="left",
        va=va,
        fontsize=size,
        fontweight=weight,
        linespacing=1.20,
    )
    registry.append((artist, ax, label or text[:40]))
    return artist


def draw_panel(ax, registry, title, subtitle, visible, truth, residual, effect):
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    outer = FancyBboxPatch(
        (0.01, 0.015), 0.98, 0.97,
        boxstyle="round,pad=0.012,rounding_size=0.018",
        linewidth=1.0,
        edgecolor="black",
        facecolor="white",
        transform=ax.transAxes,
        clip_on=False,
    )
    ax.add_patch(outer)

    header = Rectangle(
        (0.03, 0.855), 0.94, 0.105,
        linewidth=0,
        facecolor="0.91",
        transform=ax.transAxes,
    )
    ax.add_patch(header)

    add_text(ax, registry, 0.055, 0.938, title, size=9.2, weight="bold", label=f"{title}:title")
    add_text(ax, registry, 0.055, 0.892, subtitle, size=7.9, label=f"{title}:subtitle")

    sections = [
        ("Gate-visible evidence", wrap_text(visible), 0.805, 7.3),
        ("Research-only truth", wrap_text(truth), 0.615, 7.4),
        ("Residual boundary", wrap_text(residual), 0.455, 7.3),
        ("Effect of stronger composition", wrap_text(effect), 0.255, 7.3),
    ]

    for heading, body, y, body_size in sections:
        add_text(ax, registry, 0.055, y, heading, size=7.8, weight="bold", label=f"{title}:{heading}")
        add_text(ax, registry, 0.055, y - 0.045, body, size=body_size, label=f"{title}:{heading}:body")


def verify_panel_text_bounds(fig, registry) -> None:
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    failures = []

    for artist, ax, label in registry:
        text_box = artist.get_window_extent(renderer=renderer)
        axes_box = ax.get_window_extent(renderer=renderer)
        tolerance = 1.5
        if (
            text_box.x0 < axes_box.x0 - tolerance
            or text_box.x1 > axes_box.x1 + tolerance
            or text_box.y0 < axes_box.y0 - tolerance
            or text_box.y1 > axes_box.y1 + tolerance
        ):
            failures.append(label)

    if failures:
        joined = ", ".join(failures)
        raise SystemExit(f"ERROR: Figure 1 panel text overflow detected: {joined}")


def main() -> None:
    font_name = choose_font()
    plt.rcParams.update({
        "font.family": font_name,
        "font.size": 8.0,
        "axes.linewidth": 0.8,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
    })

    fig = plt.figure(figsize=(FIG_W, FIG_H), facecolor="white")

    fig.text(
        0.5, 0.978,
        "Three separately frozen experiments | qualitative synthesis only",
        ha="center", va="top", fontsize=8.7, fontweight="bold",
    )
    fig.text(
        0.5, 0.948,
        "No pooled population | no experimental data flow between panels",
        ha="center", va="top", fontsize=8.0,
    )

    gs = fig.add_gridspec(
        1, 3,
        left=0.025, right=0.975, bottom=0.09, top=0.90,
        wspace=0.055,
    )

    registry = []

    draw_panel(
        fig.add_subplot(gs[0, 0]),
        registry,
        "Study 3",
        "Temporal runtime evidence",
        "Signature validity; freshness; received authorization evidence; contact-dependent record availability; security signal.",
        "Hidden authorization truth.",
        "Fresh, validly signed V5 evidence can remain false; a truthful pre-onset cache can briefly lag a state change.",
        "K4 restriction reduces selected modeled exposure but does not eliminate persistent V5 qualification for B0/S1.",
    )

    draw_panel(
        fig.add_subplot(gs[0, 1]),
        registry,
        "Study 4",
        "Producer composition",
        "Signed producer claims; vote threshold; synthetic provenance-domain count.",
        "Hidden authorization truth.",
        "Same-size compromised subsets can differ because their provenance-domain composition differs.",
        "Provenance can delay systematic unsafe qualification, cause earlier benign rejection for selected subsets, and have null threshold effects.",
    )

    draw_panel(
        fig.add_subplot(gs[0, 2]),
        registry,
        "Study 6",
        "Recovery-artifact assurance",
        "Signature; digest; provenance; reproduced-build match; source-review attestation; release approval.",
        "Objective baseline correctness.",
        "APPROVED_BAD_SOURCE remains qualified when all six gate-visible assurance signals are true.",
        "Additional signals close specified modeled states while increasing sensitivity to benign assurance-signal loss.",
    )

    fig.text(
        0.5, 0.032,
        "Parallel panels are a qualitative manuscript synthesis, not an integrated recovery architecture. Only Study 3 models contact.",
        ha="center", va="bottom", fontsize=7.7,
    )

    verify_panel_text_bounds(fig, registry)

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
    print("layout_revision=2")
    print(f"font={font_name}")
    print(f"figure_width_in={FIG_W}")
    print(f"figure_height_in={FIG_H}")
    print("panel_text_overflow_check=PASS")
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
