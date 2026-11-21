#!/usr/bin/env python3
"""Fail-closed, read-only Paper 2 CEAS current-state cross-surface audit.

Only editorial/governance text and the current Paper 2 tracker row are read.
No scientific files, publisher artifacts, data, or Git refs are modified.
Dated TAES/rebuild records remain preserved as historical provenance.
"""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PORTAL_ID = "38cc76f5-ab6b-4b8e-b6ba-24727db86b48"
RECEIPT = "issuecomment-6275866467"
STATE = "REJECTED__EDITORIAL_ASSESSMENT__2026-10-22"
DECISION_DATE = "2026-10-22"
DECISION_FILE = "CEAS_EDITORIAL_DECISION_2026-10-22.md"
TRANSFER_STATE = "TRANSFER_NOT_COMPLETED"
DATE = "2026-10-19"
ZIP_SHA = "cd58668c183cbfdf9a14be85159435d2d4224e25d353365a5f608d2c4f6ab64f"

TEXT_SURFACES = {
    "README.md": ("CEAS Space Journal", PORTAL_ID, RECEIPT, STATE, ZIP_SHA, "TAES-2026-4182"),
    "publication/README.md": ("### Latest decision: CEAS Space Journal RevB editorial rejection", PORTAL_ID, RECEIPT, STATE, ZIP_SHA, "### Historical: TAES initial submission and rejection"),
    "docs/CURRENT_PUBLICATION_STATE.md": ("**Current-state date:** 2026-11-21", PORTAL_ID, RECEIPT, STATE, ZIP_SHA, "HISTORICAL: rejected TAES"),
    "docs/PUBLICATION_PHASE_MAP.md": ("**Current-state reference:** 2026-11-21", "PHASE 3S - PAPER 2 LATEST CEAS REV-B EDITORIAL DECISION", PORTAL_ID, RECEIPT, STATE, "Phase 3R - Paper 2 post-rejection rebuild (historical)"),
    "tracker/RESEARCH_TRACKER.md": ("Last updated: 2026-11-21", PORTAL_ID, RECEIPT, STATE, ZIP_SHA, "HISTORICAL: TAES initial submission"),
    "publication/Paper_2_Studies_3_4_6/Post_Rejection_Rebuild/README.md": ("CURRENT CEAS PAPER-2 PUBLISHER STATUS", "Historical phase-by-phase provenance (not current status)", RECEIPT, "PHASE5C_AUTHORIZED"),
    "publication/Paper_2_Studies_3_4_6/Post_Rejection_Rebuild/CEAS_REVB_SUBMISSION_HANDOFF_2026-10-19.md": ("CURRENT DECISION / POST-SUBMISSION ADDENDUM", PORTAL_ID, RECEIPT, ZIP_SHA, "NOT submitted to CEAS"),
    "publication/Paper_2_Studies_3_4_6/CEAS_Space_Journal/CEAS_EDITORIAL_DECISION_2026-10-22.md": (STATE, DECISION_DATE, PORTAL_ID, TRANSFER_STATE, ZIP_SHA, "Wilhelm Kordulla"),
}

FORBIDDEN_ACTIVE = {
    "README.md": (
        "Paper 2 is in a controlled Phase-3 pre-execution rebuild state",
        "No new scientific execution is authorized.",
    ),
    "publication/README.md": (
        "No S3X trace extraction/recovery replay, no S6X build or artifact execution, no manuscript rewrite, no venue lock, and no publisher submission is authorized.",
    ),
    "docs/CURRENT_PUBLICATION_STATE.md": (
        "Manuscript rewrite, venue lock, and publisher submission remain unauthorized.",
        "scientific execution remains closed.",
    ),
    "docs/PUBLICATION_PHASE_MAP.md": (
        "PHASE3_PREEXECUTION__S3X_SOURCE_VERIFICATION__S6X_STATIC_IMPLEMENTATION__NO_SCIENTIFIC_EXECUTION",
        "Current gate: `AUTHOR_REVIEW_AFTER_PHASE3_CI",
    ),
    "tracker/RESEARCH_TRACKER.md": (
        "Phase 3 now authorizes only local S3X source verification",
        "SUBMISSION_RECEIVED__TECHNICAL_CHECK",
    ),
}

def require(condition: bool, detail: str) -> None:
    if not condition:
        raise SystemExit("FAIL: " + detail)

def read(rel: str) -> str:
    file = ROOT / rel
    require(file.is_file() and not file.is_symlink(), "missing/nonregular " + rel)
    return file.read_text(encoding="utf-8")

for rel, markers in TEXT_SURFACES.items():
    content = read(rel)
    for marker in markers:
        require(marker in content, f"{rel}: missing exact authority marker {marker!r}")
    for old in FORBIDDEN_ACTIVE.get(rel, ()):
        require(old not in content, f"{rel}: obsolete current-state claim {old!r}")
    print("CURRENT_STATE_SURFACE=PASS " + rel)

with (ROOT / "tracker/PUBLICATION_STATE.csv").open(encoding="utf-8", newline="") as handle:
    rows = list(csv.DictReader(handle))
p2 = [row for row in rows if row.get("publication_id") == "PAPER_2"]
require(len(p2) == 1, "Paper 2 publication state must be one exact row")
row = p2[0]
require(row["venue"] == "CEAS Space Journal", "Paper 2 CSV venue drift")
require(row["manuscript_or_submission_id"] == PORTAL_ID, "Paper 2 CSV portal tracking ID drift")
require(row["submission_date"] == DATE, "Paper 2 CSV submission date drift")
require(row["current_status"] == STATE, "Paper 2 CSV status drift")
require(row["frozen"].lower() == "true", "Paper 2 frozen guard drift")
require(row["current_authority"].endswith(DECISION_FILE), "Paper 2 CSV authority drift")
require("TAES-2026-4182" in row["next_action"], "historical TAES provenance absent")
require("2026-10-22" in row["next_action"] and "NOT COMPLETED" in row["next_action"], "editorial rejection and transfer status absent")
print("PAPER2_CURRENT_PUBLICATION_STATE_AUDIT=PASS")
print("NO_RESEARCH_EXECUTION=YES")
