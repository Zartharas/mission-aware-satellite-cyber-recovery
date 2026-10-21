#!/usr/bin/env python3
"""Fail-closed audit for Paper-2 Rebuild R1 detailed editorial/reference audit."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
REBUILD = ROOT / "publication/Paper_2_Studies_3_4_6/Post_Rejection_Rebuild"

MANUSCRIPT = REBUILD / "PAPER2_REBUILD_MANUSCRIPT_R1_2026-09-28.md"
REPORT = REBUILD / "PAPER2_REBUILD_R1_DETAILED_EDITORIAL_CLAIM_REFERENCE_AUDIT_2026-09-28.md"
REFRESH = REBUILD / "PAPER2_REBUILD_R1_REFERENCE_REFRESH_CANDIDATES_2026-09-28.md"
STATUS = REBUILD / "PAPER2_REBUILD_R1_AUDIT_STATUS.json"
WORKFLOW = ROOT / ".github/workflows/validate-research-configs.yml"

EXPECTED_MAIN = "0e94e5eee412645c5a039a5295f88db01fdd6d68"
EXPECTED_BLOBS = {
    "publication/Paper_2_Studies_3_4_6/Post_Rejection_Rebuild/PAPER2_REBUILD_MANUSCRIPT_R1_2026-09-28.md":
        "822aa4257f15b76f16fed35c1131b2063923b0c8",
    "publication/Paper_2_Studies_3_4_6/IEEE_Transactions_on_Aerospace_and_Electronic_Systems/TAES_SECTION_IV_STUDY3.md":
        "5f2d1d3e0fede6800f5944a1c0990bdf94648307",
    "publication/Paper_2_Studies_3_4_6/IEEE_Transactions_on_Aerospace_and_Electronic_Systems/TAES_SECTION_V_STUDY4.md":
        "42b2a4d1cd38e9f095ddbc89bce90833151a06e6",
    "publication/Paper_2_Studies_3_4_6/IEEE_Transactions_on_Aerospace_and_Electronic_Systems/TAES_SECTION_VI_STUDY6.md":
        "0f88ab212b44be92e520368abaee657ccd0d39d2",
    "study3x/config/S3X_PHASE7_INTERPRETATION_CLAIM_USE_001.json":
        "6010381918774c6f9d5d85cc25c200fd1d5e1022",
}

REQUIRED_DOIS = (
    "10.1109/AERO66936.2026.11519913",
    "10.1109/COMST.2024.3408277",
    "10.3390/aerospace13030249",
    "10.6028/NIST.IR.8270",
    "10.5281/zenodo.15237121",
)


def fail(message: str) -> None:
    print(f"[FAIL] {message}", file=sys.stderr)
    raise SystemExit(1)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def git_blob(rel: str) -> str:
    return subprocess.check_output(["git", "hash-object", rel], cwd=ROOT, text=True).strip()


def main() -> int:
    for p in (MANUSCRIPT, REPORT, REFRESH, STATUS, WORKFLOW):
        require(p.is_file(), f"missing detailed-audit artifact: {p.relative_to(ROOT)}")

    for rel, expected in EXPECTED_BLOBS.items():
        require((ROOT / rel).is_file(), f"missing bound source: {rel}")
        require(git_blob(rel) == expected, f"bound source/manuscript drift: {rel}")

    status = json.loads(STATUS.read_text(encoding="utf-8"))
    require(status["schema"] == 1, "status schema drift")
    require(status["record_id"] == "PAPER2-REBUILD-R1-DETAILED-AUDIT-001", "status id drift")
    require(status["authorized_main_commit"] == EXPECTED_MAIN, "authorized main drift")
    require(
        status["status"] == "DETAILED_AUDIT_PREPARED__MANUSCRIPT_UNCHANGED__NOT_EFFECTIVE_UNTIL_APPROVED_MERGE",
        "status state drift",
    )
    require(
        status["verdict"] == "PASS_SCIENTIFIC_INTEGRITY__EDITORIAL_AND_REFERENCE_CORRECTIONS_REQUIRED_BEFORE_VENUE_LOCK",
        "verdict drift",
    )
    require(status["authoritative_manuscript"]["mutation_authorized"] is False, "R1 mutation opened")

    q = status["quantitative_audit"]
    require(all(v == "PASS_NO_NUMERICAL_CORRECTION" for v in q.values()), "quantitative audit not all-pass")

    closed = status["prohibited_or_closed"]
    for key, value in closed.items():
        require(value is False, f"closed authority unexpectedly opened: {key}")

    report = REPORT.read_text(encoding="utf-8")
    required_report = (
        "title overbreadth",
        "P99_X10 selection wording",
        "Silent Subversion",
        "restore a compact temporal result display",
        "update the approved qualitative figure",
        "ESA dataset",
        "PASS_SCIENTIFIC_INTEGRITY__EDITORIAL_AND_REFERENCE_CORRECTIONS_REQUIRED_BEFORE_VENUE_LOCK",
    )
    for needle in required_report:
        require(needle.lower() in report.lower(), f"required audit finding missing: {needle}")

    refresh = REFRESH.read_text(encoding="utf-8")
    for doi in REQUIRED_DOIS:
        require(doi in refresh, f"required reference-refresh DOI missing: {doi}")
    require("G. De Canio" in refresh, "corrected ESA author metadata missing")
    require("CM0044 Cyber-safe Mode" in refresh, "specific SPARTA refinement missing")

    manuscript = MANUSCRIPT.read_text(encoding="utf-8")
    require(
        "# Residual Trust Boundaries in Satellite Cyber Recovery:" in manuscript,
        "authoritative R1 title unexpectedly changed during audit",
    )
    require(
        "A prespecified cadence-sensitivity process selected the P99_X10 rule" in manuscript,
        "R1 selection wording unexpectedly changed during audit",
    )

    workflow = WORKFLOW.read_text(encoding="utf-8")
    require(
        "python scripts/audit_paper2_rebuild_r1_detailed_audit.py" in workflow,
        "detailed audit is not wired into CI",
    )

    print("paper2_rebuild_r1_detailed_audit=PASS")
    print("authoritative_manuscript_mutation=NO")
    print("frozen_science_mutation=NO")
    print("quantitative_claim_corrections_required=NO")
    print("editorial_reference_corrections_required=YES")
    print("venue_lock=NO")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
