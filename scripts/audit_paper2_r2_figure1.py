#!/usr/bin/env python3
"""Fail-closed audit for Paper-2 R2 Figure 1 revision-3 source and QA package."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
REBUILD = ROOT / "publication/Paper_2_Studies_3_4_6/Post_Rejection_Rebuild"
R2 = REBUILD / "PAPER2_REBUILD_MANUSCRIPT_R2_2026-09-28.md"
SVG = REBUILD / "figures/PAPER2_R2_FIGURE1_RESIDUAL_BOUNDARIES.svg"
GEN = REBUILD / "PAPER2_R2_FIGURE1_GENERATOR.py"
QA = REBUILD / "PAPER2_R2_FIGURE1_VISUAL_SCIENTIFIC_QA_2026-09-28.md"
STATUS = REBUILD / "PAPER2_R2_FIGURE1_STATUS.json"
WORKFLOW = ROOT / ".github/workflows/validate-research-configs.yml"

EXPECTED_MAIN = "ccef12d6f0c09fe48d795735726c964d8daad561"
EXPECTED_R2_BLOB = "9e3f345a3a16102c39bb978f4e522c261e80cfb4"
EXPECTED_SVG_SHA256 = "adfdfaf833c8624bb405209be22ef6b2f002cdec53f081ce097f67e728eedffc"


def fail(message: str) -> None:
    print(f"[FAIL] {message}", file=sys.stderr)
    raise SystemExit(1)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def git_blob(path: Path) -> str:
    return subprocess.check_output(
        ["git", "hash-object", str(path.relative_to(ROOT))],
        cwd=ROOT,
        text=True,
    ).strip()


def main() -> int:
    for path in (R2, SVG, GEN, QA, STATUS, WORKFLOW):
        require(path.is_file(), f"missing Figure-1 package file: {path.relative_to(ROOT)}")

    require(git_blob(R2) == EXPECTED_R2_BLOB, "authoritative R2 manuscript drift")
    require(sha256(SVG) == EXPECTED_SVG_SHA256, "Figure-1 SVG SHA-256 drift")

    svg = SVG.read_text(encoding="utf-8")
    required_svg = (
        "Three separately evaluated experiments | qualitative synthesis only",
        "No pooled population | no experimental data flow between panels",
        "Study 3",
        "Study 4",
        "Study 6",
        "S3X external-source timing stress test",
        "1,919 P99_X10 timestamp intervals",
        "5,757",
        "V4 affected record: non-qualifying",
        "V5 first refresh: B0/S1 qualify; B2",
        "K4 = synthetic contact modeling",
        "S3X = timing proxy, not observed RF/contact loss",
        "Not external empirical replication of Study 3",
        "APPROVED_BAD_SOURCE",
    )
    for item in required_svg:
        require(item in svg, f"required Figure-1 label missing: {item}")

    for forbidden in ("marker-end=", "<marker", "->", "→"):
        require(forbidden not in svg, f"arrow/pipeline cue present in SVG: {forbidden}")

    status = json.loads(STATUS.read_text(encoding="utf-8"))
    require(status["schema"] == 1, "Figure-1 status schema drift")
    require(status["record_id"] == "PAPER2-R2-FIGURE1-VISUAL-QA-001", "Figure-1 status id drift")
    require(status["authorized_main_commit"] == EXPECTED_MAIN, "Figure-1 authorized main drift")
    require(status["figure"]["revision"] == 3, "Figure-1 revision drift")
    require(status["figure"]["native_png_visual_qa"] == "PASS", "native PNG QA not pass")
    require(status["figure"]["independent_pdf_render_visual_qa"] == "PASS", "PDF render QA not pass")
    require(status["visual_controls"]["parallel_main_panels"] is True, "parallel-panel control missing")
    require(status["visual_controls"]["arrows_or_pipeline_cues"] is False, "pipeline cue opened")
    require(status["visual_controls"]["cross_panel_text_collision"] is False, "text collision remains")
    require(status["visual_controls"]["s3x_subordinate_inset"] is True, "S3X inset hierarchy missing")

    for key, value in status["science_controls"].items():
        require(value is False, f"science control unexpectedly opened: {key}")
    for key, value in status["insertion_controls"].items():
        require(value is False, f"downstream insertion control unexpectedly opened: {key}")

    qa = QA.read_text(encoding="utf-8")
    require("REVISION_1_REJECTED__S3X_INSET_FOOTER_OVERFLOW" in qa, "revision-1 rejection missing")
    require("REVISION_2_REJECTED__STUDY3_TEXT_INSET_OVERLAP" in qa, "revision-2 rejection missing")
    require("PASS_REVISION_3_FIGURE_SOURCE_AND_VISUAL_QA" in qa, "revision-3 pass missing")
    require("MANUSCRIPT_INSERTION_NOT_YET_AUTHORIZED" in qa, "insertion firewall missing")

    generator = GEN.read_text(encoding="utf-8")
    require('SOURCE_DATE_EPOCH = "1790553600"' in generator, "deterministic PDF source-date control missing")
    require("PAPER2_R2_FIGURE1_GENERATION=PASS" in generator, "generator pass marker missing")

    workflow = WORKFLOW.read_text(encoding="utf-8")
    require(
        "python scripts/audit_paper2_r2_figure1.py" in workflow,
        "Figure-1 audit is not wired into CI",
    )

    print("paper2_r2_figure1_audit=PASS")
    print("figure_revision=3")
    print("r2_manuscript_unchanged=YES")
    print("visual_qa=PASS")
    print("scientific_reexecution=NO")
    print("study3_s3x_pooling=NO")
    print("manuscript_insertion=NOT_AUTHORIZED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
