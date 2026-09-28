#!/usr/bin/env python3
"""Fail-closed audit for Paper-2 post-rejection manuscript rebuild R1."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
REBUILD = ROOT / "publication/Paper_2_Studies_3_4_6/Post_Rejection_Rebuild"
MANUSCRIPT = REBUILD / "PAPER2_REBUILD_MANUSCRIPT_R1_2026-09-28.md"
MAP = REBUILD / "PAPER2_REBUILD_CLAIM_SOURCE_MAP_R1_2026-09-28.md"
STATUS = REBUILD / "PAPER2_REBUILD_MANUSCRIPT_INTEGRATION_STATUS.json"
WORKFLOW = ROOT / ".github/workflows/validate-research-configs.yml"

EXPECTED_BASE = "c69160b26f0a06578446e24ba490aac374502b47"
EXPECTED_BLOBS = {
    "publication/Paper_2_Studies_3_4_6/Post_Rejection_Rebuild/R10_EDITORIAL_DIAGNOSIS_2026-09-26.md":
        "8f19657a97f7c8569671ceeeae2058ea01099c72",
    "publication/Paper_2_Studies_3_4_6/IEEE_Transactions_on_Aerospace_and_Electronic_Systems/TAES_SECTION_IV_STUDY3.md":
        "5f2d1d3e0fede6800f5944a1c0990bdf94648307",
    "publication/Paper_2_Studies_3_4_6/IEEE_Transactions_on_Aerospace_and_Electronic_Systems/TAES_SECTION_V_STUDY4.md":
        "42b2a4d1cd38e9f095ddbc89bce90833151a06e6",
    "publication/Paper_2_Studies_3_4_6/IEEE_Transactions_on_Aerospace_and_Electronic_Systems/TAES_SECTION_VI_STUDY6.md":
        "0f88ab212b44be92e520368abaee657ccd0d39d2",
    "publication/Paper_2_Studies_3_4_6/IEEE_Transactions_on_Aerospace_and_Electronic_Systems/TAES_SECTION_VII_SYNTHESIS.md":
        "5e46c441ce985ceb2de6f16d2a8d1a6d3fedcbe1",
    "publication/Paper_2_Studies_3_4_6/IEEE_Transactions_on_Aerospace_and_Electronic_Systems/TAES_SECTION_VIII_VALIDITY.md":
        "8215d553112c32c548185e1dc240dd21785e879d",
    "study3x/config/S3X_PHASE7_INTERPRETATION_CLAIM_USE_001.json":
        "6010381918774c6f9d5d85cc25c200fd1d5e1022",
    "publication/Paper_2_Studies_3_4_6/Post_Rejection_Rebuild/PAPER2_REBUILD_PHASE7F_MANUSCRIPT_INSERTS_R1_2026-09-28.md":
        "581edbc13ea1fc78ef944011f992c731da9227b5",
}


def fail(message: str) -> None:
    print(f"[FAIL] {message}", file=sys.stderr)
    raise SystemExit(1)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def git_blob(rel: str) -> str:
    return subprocess.check_output(["git", "hash-object", rel], cwd=ROOT, text=True).strip()


def main() -> int:
    for path in (MANUSCRIPT, MAP, STATUS, WORKFLOW):
        require(path.is_file(), f"missing rebuild artifact: {path.relative_to(ROOT)}")

    for rel, expected in EXPECTED_BLOBS.items():
        require((ROOT / rel).is_file(), f"missing bound source: {rel}")
        require(git_blob(rel) == expected, f"bound source blob drift: {rel}")

    status = json.loads(STATUS.read_text(encoding="utf-8"))
    require(status["schema"] == 1, "status schema drift")
    require(status["record_id"] == "PAPER2-POST-REJECTION-MANUSCRIPT-REBUILD-R1-001", "status id drift")
    require(status["authorized_main_commit"] == EXPECTED_BASE, "authorized base drift")
    require(status["authorized_scope"]["new_rebuild_manuscript_editing"] is True, "rebuild editing not authorized")
    require(status["authorized_scope"]["historical_taes_r10_mutation"] is False, "historical R10 mutation opened")
    require(status["authorized_scope"]["scientific_reexecution"] is False, "scientific rerun opened")
    require(status["authorized_scope"]["result_mutation"] is False, "result mutation opened")
    require(status["authorized_scope"]["new_venue_lock"] is False, "venue lock opened")
    require(status["scientific_foundation"]["s3x"]["pooled_with_study3"] is False, "S3X pooling opened")
    require(status["scientific_foundation"]["s3x"]["external_empirical_replication"] is False, "external replication opened")
    require(status["bound_authority"]["phase7f_post_merge_ci_run_number"] == 1270, "Phase-7F CI binding drift")
    require(status["bound_authority"]["phase7f_post_merge_ci_conclusion"] == "success", "Phase-7F CI not successful")

    text = MANUSCRIPT.read_text(encoding="utf-8")

    required = [
        "Which trust failures remain invisible to a satellite cyber-recovery decision",
        "Study 3, S3-K4E-001",
        "Study 4, S4-MPQ-001",
        "Study 6, S6-SCTR-001",
        "S3X-ETA-001",
        "1,919",
        "34,542",
        "30,704",
        "5,757",
        "11,514",
        "7,676",
        "3,838",
        "4,608",
        "420",
        "APPROVED_BAD_SOURCE",
        "S3X is not an external empirical replication of Study 3",
        "No pooled N",
        "venue-neutral manuscript draft",
        "10.5281/zenodo.15237121",
    ]
    for item in required:
        require(item in text, f"required manuscript content missing: {item}")

    require("four studies" not in text.lower(), "S3X incorrectly framed as a fourth pooled study")
    require("globally best policy" not in text.lower(), "global policy-ranking language present")
    require("RF contact-loss observations" in text, "S3X RF/contact firewall missing")
    require("not a measurement of physical cache duration in flight" in text, "cache-duration firewall missing")
    require("not operational outage probabilities" in text, "Study-6 availability firewall missing")

    refs = text.split("## References", 1)
    require(len(refs) == 2, "references section missing")
    require("[14] European Space Agency" in refs[1], "ESA dataset reference missing")

    mapping = MAP.read_text(encoding="utf-8")
    require("No file in publication/Paper_2_Studies_3_4_6/IEEE_Transactions_on_Aerospace_and_Electronic_Systems/ is modified" in mapping, "historical package boundary missing")
    require("Phase-7F claim-use record" in mapping, "Phase-7F authority missing from source map")

    workflow = WORKFLOW.read_text(encoding="utf-8")
    require(
        "python scripts/audit_paper2_post_rejection_manuscript_rebuild_r1.py" in workflow,
        "rebuild audit is not wired into CI",
    )

    word_count = len(text.split())
    require(4500 <= word_count <= 9000, f"unexpected rebuild manuscript word count: {word_count}")

    print("paper2_post_rejection_manuscript_rebuild_r1_audit=PASS")
    print(f"manuscript_word_count={word_count}")
    print("historical_taes_r10_mutation=NO")
    print("scientific_reexecution=NO")
    print("result_mutation=NO")
    print("s3x_study3_pooling=NO")
    print("venue_lock=NO")
    print("rebuild_r1_prepared=YES")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
