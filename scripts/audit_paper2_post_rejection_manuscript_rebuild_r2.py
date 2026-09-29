#!/usr/bin/env python3
"""Fail-closed audit for Paper-2 post-rejection Rebuild R2."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
REBUILD = ROOT / "publication/Paper_2_Studies_3_4_6/Post_Rejection_Rebuild"
R1 = REBUILD / "PAPER2_REBUILD_MANUSCRIPT_R1_2026-09-28.md"
R2 = REBUILD / "PAPER2_REBUILD_MANUSCRIPT_R2_2026-09-28.md"
LEDGER = REBUILD / "PAPER2_REBUILD_R2_REFERENCE_INTEGRATION_LEDGER_2026-09-28.md"
DISPLAY = REBUILD / "PAPER2_REBUILD_R2_DISPLAY_INTEGRATION_PLAN_2026-09-28.md"
STATUS = REBUILD / "PAPER2_REBUILD_R2_STATUS.json"
WORKFLOW = ROOT / ".github/workflows/validate-research-configs.yml"

EXPECTED_MAIN = "21dc6444045a8d7668cb5b44b6e39a259567807b"
EXPECTED_R1_BLOB = "822aa4257f15b76f16fed35c1131b2063923b0c8"
EXPECTED_AUDIT_BLOB = "0a0edfc621041b35e7b0a31c1c9bb223fc847ca1"
EXPECTED_REFRESH_BLOB = "70086ae516c53e1966f4e6539880c0955c81f5ec"


def fail(message: str) -> None:
    print(f"[FAIL] {message}", file=sys.stderr)
    raise SystemExit(1)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def git_blob(rel: str) -> str:
    return subprocess.check_output(["git", "hash-object", rel], cwd=ROOT, text=True).strip()


def main() -> int:
    for p in (R1, R2, LEDGER, DISPLAY, STATUS, WORKFLOW):
        require(p.is_file(), f"missing R2 artifact: {p.relative_to(ROOT)}")

    require(git_blob(str(R1.relative_to(ROOT))) == EXPECTED_R1_BLOB, "R1 manuscript drift")
    require(
        git_blob("publication/Paper_2_Studies_3_4_6/Post_Rejection_Rebuild/PAPER2_REBUILD_R1_DETAILED_EDITORIAL_CLAIM_REFERENCE_AUDIT_2026-09-28.md")
        == EXPECTED_AUDIT_BLOB,
        "authoritative R1 audit drift",
    )
    require(
        git_blob("publication/Paper_2_Studies_3_4_6/Post_Rejection_Rebuild/PAPER2_REBUILD_R1_REFERENCE_REFRESH_CANDIDATES_2026-09-28.md")
        == EXPECTED_REFRESH_BLOB,
        "reference-refresh authority drift",
    )

    status = json.loads(STATUS.read_text(encoding="utf-8"))
    require(status["schema"] == 1, "R2 status schema drift")
    require(status["record_id"] == "PAPER2-POST-REJECTION-MANUSCRIPT-REBUILD-R2-001", "R2 status id drift")
    require(status["authorized_main_commit"] == EXPECTED_MAIN, "R2 authorized main drift")
    require(status["immutable_prior_manuscript"]["mutation_authorized"] is False, "R1 mutation opened")
    require(status["authoritative_audit"]["post_merge_ci_run_number"] == 1275, "audit CI binding drift")
    require(status["authoritative_audit"]["post_merge_ci_conclusion"] == "success", "audit post-merge CI not successful")
    require(status["publication_controls"]["venue_lock"] is False, "venue lock opened")
    require(status["publication_controls"]["figure_generation_authorized"] is False, "figure generation opened")
    for key, value in status["science_controls"].items():
        require(value is False, f"science control unexpectedly opened: {key}")

    text = R2.read_text(encoding="utf-8")
    required = (
        "Residual Trust Boundaries in Satellite Cyber-Recovery Qualification",
        "Across separately evaluated temporal, producer-composition, and artifact-assurance layers",
        "A prespecified eight-rule cadence-sensitivity analysis was performed",
        "selected after that analysis and then frozen before timestamp-trace extraction and recovery replay",
        "Silent Subversion",
        "10.1109/AERO66936.2026.11519913",
        "10.1109/COMST.2024.3408277",
        "10.3390/aerospace13030249",
        "10.6028/NIST.IR.8270",
        "10.5220/0013103200003899",
        "G. De Canio",
        "Cyber-safe Mode (CM0044)",
        "Table II. RQ1 temporal qualification results with study-specific units",
        "5,757/5,757",
        "11,514",
        "7,676/7,676",
        "3,838/3,838",
        "Study-3 logical seconds and S3X cadence units are distinct analysis units and are not converted or pooled.",
        "S3X is not an external empirical replication of Study 3.",
        "does not identify a globally best policy",
    )
    for item in required:
        require(item in text, f"required R2 content missing: {item}")

    forbidden = (
        "independently sourced telemetry interval population",
        "strengthens the portability test",
        "S3X Finding 2: V4 Remains Integrity-Detectable",
        "Which trust failures remain invisible to a satellite cyber-recovery decision when it relies on fresh evidence",
    )
    for item in forbidden:
        require(item not in text, f"superseded R1 wording remains in R2: {item}")

    require("### Table III. Study-4 exact first/systematic failure map" in text, "Study-4 table renumbering missing")
    require("### Table IV. Study-6 residual incorrect-state and benign-loss counts" in text, "Study-6 table renumbering missing")

    word_count = len(text.split())
    require(5500 <= word_count <= 8500, f"unexpected R2 word count: {word_count}")
    require(status["r2_metrics"]["word_count"] == word_count, "R2 word count status drift")

    ledger = LEDGER.read_text(encoding="utf-8")
    for doi in (
        "10.1109/AERO66936.2026.11519913",
        "10.1109/COMST.2024.3408277",
        "10.3390/aerospace13030249",
        "10.6028/NIST.IR.8270",
        "10.5220/0013103200003899",
        "10.5281/zenodo.15237121",
    ):
        require(doi in ledger or doi in text, f"reference DOI absent from R2 package: {doi}")

    display = DISPLAY.read_text(encoding="utf-8")
    require("S3X external-source timing stress-test inset" in display, "Figure-1 S3X inset specification missing")
    require("not generated in this phase" in display, "figure-generation boundary missing")

    workflow = WORKFLOW.read_text(encoding="utf-8")
    require(
        "python scripts/audit_paper2_post_rejection_manuscript_rebuild_r2.py" in workflow,
        "R2 audit is not wired into CI",
    )

    print("paper2_post_rejection_manuscript_rebuild_r2_audit=PASS")
    print(f"r2_word_count={word_count}")
    print("r1_manuscript_unchanged=YES")
    print("frozen_science_mutation=NO")
    print("scientific_reexecution=NO")
    print("study3_s3x_pooling=NO")
    print("venue_lock=NO")
    print("figure_generation=NO")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
