#!/usr/bin/env python3
"""Fail-closed audit for Paper-2 Phase-7F interpretation and claim-use preparation."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
S3X = ROOT / "study3x"
REBUILD = ROOT / "publication/Paper_2_Studies_3_4_6/Post_Rejection_Rebuild"
WORKFLOW = ROOT / ".github/workflows/validate-research-configs.yml"

RECORD = S3X / "config/S3X_PHASE7_INTERPRETATION_CLAIM_USE_001.json"
STATUS = REBUILD / "PAPER2_PHASE7F_INTERPRETATION_CLAIM_USE_STATUS.json"
REPORT = REBUILD / "PHASE7F_RESULT_INTERPRETATION_AND_CLAIM_USE_R1_2026-09-28.md"
INSERTS = REBUILD / "PAPER2_REBUILD_PHASE7F_MANUSCRIPT_INSERTS_R1_2026-09-28.md"
FREEZE = S3X / "config/S3X_PHASE7_RESULT_FREEZE_001.json"

EXPECTED_MAIN = "74c124290fce0f46f1687f277edeff28d4d82dc1"
EXPECTED_BLOBS = {
    "study3x/config/S3X_PHASE7_RESULT_FREEZE_001.json":
        "d25b70639b4e32696e47b5630387ef9820f83740",
    "study3x/config/S3X_PHASE7_RECOVERY_REPLAY_PROTOCOL_001.json":
        "f42fe8c0c58ee3b9152e629f5673bd5c71ffede4",
    "study3/src/temporal_model.py":
        "b13e62456c144db0e12808bf700586c1c844c33d",
    "study3x/src/recovery_replay_v2.py":
        "40e3bd0406f1f0bedecbac9cb1386699a8619318",
    "study3x/audit/reference_replay_v2.py":
        "26444d206f18bededa656b1de56d9ba0948c6ef3",
    "study3x/audit/validate_phase7_replay_v2.py":
        "15796f7b8e2da3f92e941021839b387ad365394e",
}


def fail(message: str) -> None:
    print(f"[FAIL] {message}", file=sys.stderr)
    raise SystemExit(1)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def git_blob(rel: str) -> str:
    return subprocess.check_output(
        ["git", "hash-object", rel],
        cwd=ROOT,
        text=True,
    ).strip()


def main() -> int:
    for path in (RECORD, STATUS, REPORT, INSERTS, FREEZE, WORKFLOW):
        require(path.is_file(), f"missing Phase-7F dependency: {path.relative_to(ROOT)}")

    for rel, expected in EXPECTED_BLOBS.items():
        require((ROOT / rel).is_file(), f"missing bound file: {rel}")
        require(git_blob(rel) == expected, f"bound blob drift: {rel}")

    freeze = read_json(FREEZE)
    require(freeze["freeze_id"] == "S3X-PHASE7-RESULT-FREEZE-001", "freeze id drift")
    require(freeze["canonical_result_identity"]["S3X_PHASE7_CASE_RESULTS_001.csv"]["rows"] == 34542, "frozen case count drift")
    require(freeze["canonical_result_identity"]["S3X_PHASE7_MATCHED_COMPARISONS_001.csv"]["rows"] == 30704, "frozen comparison count drift")
    require(freeze["validated_local_execution"]["case_level_mismatches_each_run"] == 0, "frozen case mismatches present")
    require(freeze["validated_local_execution"]["matched_comparison_mismatches_each_run"] == 0, "frozen comparison mismatches present")
    require(freeze["validated_local_execution"]["all_five_canonical_outputs_byte_identical"] is True, "frozen repeatability missing")

    record = read_json(RECORD)
    require(record["schema"] == 1, "claim-use schema drift")
    require(record["record_id"] == "S3X-PHASE7-INTERPRETATION-CLAIM-USE-001", "claim-use id drift")
    require(record["authorized_main_commit"] == EXPECTED_MAIN, "authorized main drift")
    require(record["authorization_basis"]["interpretation_authorized"] is True, "interpretation authorization missing")
    require(record["authorization_basis"]["rebuild_manuscript_claim_use_authorized"] is True, "rebuild claim-use authorization missing")
    require(record["authorization_basis"]["historical_taes_submission_mutation_authorized"] is False, "historical R10 mutation opened")
    require(record["authorization_basis"]["scientific_reexecution_authorized"] is False, "scientific rerun opened")
    require(record["authorization_basis"]["result_mutation_authorized"] is False, "result mutation opened")

    authority = record["frozen_result_authority"]
    require(authority["freeze_id"] == "S3X-PHASE7-RESULT-FREEZE-001", "result freeze binding drift")
    require(authority["effective_main_commit"] == EXPECTED_MAIN, "effective freeze commit drift")
    require(authority["post_merge_ci_run_number"] == 1266, "post-merge CI number drift")
    require(authority["post_merge_ci_run_id"] == 36431944810, "post-merge CI id drift")
    require(authority["post_merge_ci_conclusion"] == "success", "post-merge CI not successful")
    require(authority["canonical_case_rows"] == 34542, "claim-use case count drift")
    require(authority["canonical_matched_comparison_rows"] == 30704, "claim-use comparison count drift")
    require(authority["case_level_mismatches"] == 0, "claim-use case mismatch drift")
    require(authority["matched_comparison_mismatches"] == 0, "claim-use comparison mismatch drift")

    counts = record["exact_structural_counts"]
    expected_counts = {
        "frozen_intervals": 1919,
        "cases": 1919 * 3 * 3 * 2,
        "b0_vs_s1_gap_cache_comparisons": 1919 * 3,
        "v4_first_refresh_cases": 1919 * 3 * 2,
        "v5_b0_or_s1_first_refresh_cases": 1919 * 2 * 2,
        "v5_b2_first_refresh_cases": 1919 * 1 * 2,
        "v5_gap_vs_control_gate_classification_comparisons": 1919 * 3,
        "b0_or_s1_vs_b2_v5_resumption_comparisons": 1919 * 2 * 2,
    }
    require(counts == expected_counts, "structural count derivation drift")

    claims = {row["claim_id"]: row for row in record["manuscript_eligible_claims"]}
    expected_ids = {
        "S3X-C1-HIATUS-CACHE-BOUNDARY",
        "S3X-C2-V4-SIGNATURE-BOUNDARY",
        "S3X-C3-V5-FIRST-REFRESH-BOUNDARY",
        "S3X-C4-TIMING-CLASSIFICATION-INVARIANCE",
        "S3X-C5-V5-DELAY-IDENTITY",
        "S3X-C6-RQ1-SYNTHESIS",
    }
    require(set(claims) == expected_ids, "eligible claim set drift")
    require(all(row["eligible"] is True for row in claims.values()), "eligible claim disabled")

    withheld = "\n".join(record["prohibited_or_withheld_claims"])
    for required in (
        "RF contact loss",
        "cyberattack truth",
        "external empirical replication",
        "globally superior",
        "Study 3 form a pooled population",
        "minimum, median, maximum, mean, percentile",
    ):
        require(required in withheld, f"missing claim firewall: {required}")

    scope = record["manuscript_use_scope"]
    require(scope["post_rejection_rebuild_only"] is True, "claim use not rebuild-only")
    require(scope["historical_submitted_r10_immutable"] is True, "historical R10 immutability missing")
    require(scope["claim_use_effective_only_after_record_merge_and_successful_post_merge_ci"] is True, "claim effectivity gate missing")

    status = read_json(STATUS)
    require(
        status["status"] == "INTERPRETATION_AND_CLAIM_USE_PACKAGE_PREPARED__NOT_EFFECTIVE_UNTIL_APPROVED_MERGE",
        "Phase-7F status drift",
    )
    require(status["result_freeze"]["effective"] is True, "status does not recognize effective result freeze")
    require(status["authorized_now"]["scientific_reexecution"] is False, "status opens rerun")
    require(status["authorized_now"]["result_mutation"] is False, "status opens result mutation")
    require(status["claim_scope"]["output_distribution_claims_not_directly_inspected"] == "WITHHELD", "distributional claim firewall drift")

    report = REPORT.read_text(encoding="utf-8")
    inserts = INSERTS.read_text(encoding="utf-8")
    for text, label in ((report, "report"), (inserts, "inserts")):
        require("1,919" in text, f"{label} missing frozen interval count")
        require("34,542" in text, f"{label} missing case count")
        require("7,676" in text, f"{label} missing B0/S1 V5 count")
        require("3,838" in text, f"{label} missing B2 V5 count")
        require("not an external empirical replication" in text or "not an external empirical replication of Study 3" in text, f"{label} missing replication firewall")
    require("5,757" in inserts, "manuscript inserts missing cache comparison count")
    require("historical TAES R10" in inserts, "manuscript inserts do not preserve historical submission")

    workflow = WORKFLOW.read_text(encoding="utf-8")
    require(
        "python scripts/audit_paper2_post_rejection_phase7f_interpretation_claim_use.py"
        in workflow,
        "Phase-7F audit is not wired into CI",
    )

    print("paper2_phase7f_interpretation_claim_use_audit=PASS")
    print("effective_result_freeze_verified=YES")
    print("structural_claims_prepared=6")
    print("rebuild_manuscript_claim_use_prepared=YES")
    print("distributional_output_claims_withheld=YES")
    print("scientific_reexecution=NO")
    print("result_mutation=NO")
    print("historical_r10_mutation=NO")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
