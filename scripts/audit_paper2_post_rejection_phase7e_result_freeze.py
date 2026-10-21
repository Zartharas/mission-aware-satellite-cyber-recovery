#!/usr/bin/env python3
"""Fail-closed audit for Paper-2 Phase-7E corrected result-freeze preparation."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
S3X = ROOT / "study3x"
REBUILD = ROOT / "publication/Paper_2_Studies_3_4_6/Post_Rejection_Rebuild"

FREEZE = S3X / "config/S3X_PHASE7_RESULT_FREEZE_001.json"
STATUS = REBUILD / "PAPER2_PHASE7E_RESULT_FREEZE_STATUS.json"
NOTE = REBUILD / "PHASE7E_RESULT_FREEZE_GATE_R1_2026-09-28.md"
WORKFLOW = ROOT / ".github/workflows/validate-research-configs.yml"
GITIGNORE = ROOT / ".gitignore"

EXPECTED_MAIN = "3d31316ba4b3a0a3e04229a62e776cbeaae8680d"
EXPECTED_INTERVAL_SHA = "cfa4fa3d88cb525237cbfe347fabe8485021351f3b639bdb58f79c575d8a51bc"
EXPECTED_BLOBS = {
    "study3x/config/S3X_PHASE6_TRACE_POPULATION_FREEZE_001.json":
        "ed0bdcec443b7f0c3ee80d441e1122f32e499d3e",
    "study3x/config/S3X_PHASE7_RECOVERY_REPLAY_PROTOCOL_001.json":
        "f42fe8c0c58ee3b9152e629f5673bd5c71ffede4",
    "study3x/config/S3X_PHASE7_IMPLEMENTATION_FREEZE_CANDIDATE_002.json":
        "d7ee15c6a2bfe818ee016eadba0893ef74aa8f18",
    "study3x/config/S3X_PHASE7_RUNTIME_AUTH_002.json":
        "bb7978052cf03bdfaa628a44d7d268d73e9c005a",
    "study3x/validation/run_local_phase7_replay_v2.sh":
        "95cb497cd0465a34e1e8e17609c4e5f781ba8aaf",
}
EXPECTED_RESULTS = {
    "S3X_PHASE7_CASE_RESULTS_001.csv":
        "948cc1def0032ba0c20d0f4fcbb0d67c34130b5c42a136bbe480d7a09e49cb37",
    "S3X_PHASE7_MATCHED_COMPARISONS_001.csv":
        "7ad0e0e901b72f92ac53c3a0e1e48213dba7191ee22904f39720f5cd98a759ef",
    "S3X_PHASE7_SUMMARY_001.json":
        "d93c5e5e2389de3d88f0d9b3d68fc82c97c84925b58529caddd7227d3f65690a",
    "S3X_PHASE7_INDEPENDENT_VALIDATION_001.json":
        "93eeaa0ad23aff53ee9f259737472ed95b740850f60fde7bf20ef08385dea778",
    "S3X_PHASE7_RESULTS_HASH_MANIFEST_001.json":
        "1a07b116edada84db4daadd072aad7b6d567a634f0bf191f4221970f8e504610",
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
    for path in (FREEZE, STATUS, NOTE, WORKFLOW, GITIGNORE):
        require(path.is_file(), f"missing Phase-7E dependency: {path.relative_to(ROOT)}")

    for rel, expected in EXPECTED_BLOBS.items():
        require((ROOT / rel).is_file(), f"missing bound upstream file: {rel}")
        require(git_blob(rel) == expected, f"bound upstream blob drift: {rel}")

    record = read_json(FREEZE)
    require(record.get("schema") == 1, "freeze schema drift")
    require(record.get("freeze_id") == "S3X-PHASE7-RESULT-FREEZE-001", "freeze id drift")
    require(record.get("experiment_id") == "S3X-ETA-001", "experiment id drift")
    require(record.get("paper_id") == "PAPER2_STUDIES_3_4_6", "paper id drift")
    require(record.get("status") == "PREPARED_ON_FEATURE_BRANCH__NOT_EFFECTIVE", "pre-merge status drift")
    require(record.get("authorized_main_commit") == EXPECTED_MAIN, "authorized main binding drift")

    authz = record["authorization_basis"]
    require(authz["author_result_freeze_approval_recorded"] is True, "author freeze approval not recorded")
    require(authz["approved_scope"] == "RESULT_FREEZE_AND_PROVENANCE_CLOSEOUT_ONLY", "authorized scope drift")
    require(authz["manuscript_claim_use_authorized"] is False, "manuscript claim use opened")
    require(authz["manuscript_rewrite_authorized"] is False, "manuscript rewrite opened")

    upstream = record["upstream"]
    require(
        upstream["trace_population_freeze"]["frozen_interval_csv_sha256"] == EXPECTED_INTERVAL_SHA,
        "frozen interval SHA drift",
    )
    require(upstream["trace_population_freeze"]["intervals"] == 1919, "frozen interval count drift")
    require(upstream["phase7d_merge"]["pr"] == 192, "Phase-7D PR binding drift")
    require(upstream["phase7d_merge"]["post_merge_ci_run_number"] == 1262, "Phase-7D CI drift")
    require(upstream["phase7d_merge"]["post_merge_ci_conclusion"] == "success", "Phase-7D CI not successful")
    require(upstream["execution_authority"]["main_commit"] == EXPECTED_MAIN, "execution main drift")
    require(upstream["execution_authority"]["post_handoff_ci_run_number"] == 1264, "execution CI drift")
    require(upstream["execution_authority"]["post_handoff_ci_conclusion"] == "success", "execution CI not successful")

    execution = record["validated_local_execution"]
    for key in (
        "run1_primary_runtime",
        "run1_independent_validation",
        "run2_primary_runtime",
        "run2_independent_validation",
        "summary_validation_both_runs",
        "manifest_integrity_both_runs",
    ):
        require(execution[key] == "PASS", f"execution evidence not PASS: {key}")
    require(execution["frozen_intervals_each_run"] == 1919, "execution interval count drift")
    require(execution["case_rows_each_run"] == 34542, "case count drift")
    require(execution["matched_comparison_rows_each_run"] == 30704, "comparison count drift")
    require(execution["reference_cases_recomputed_each_run"] == 34542, "reference case count drift")
    require(execution["case_level_mismatches_each_run"] == 0, "case mismatches present")
    require(execution["matched_comparison_mismatches_each_run"] == 0, "comparison mismatches present")
    require(execution["tracked_repository_drift_after_each_run"] == 0, "tracked drift recorded")
    require(execution["all_five_canonical_outputs_byte_identical"] is True, "repeatability not verified")
    require(
        execution["validation_characterization"]
        == "SEPARATELY_IMPLEMENTED_REPOSITORY_REFERENCE_EVALUATOR__NOT_INDEPENDENT_HUMAN_OR_EXTERNAL_REPLICATION",
        "validation characterization drift",
    )

    results = record["canonical_result_identity"]
    require(set(results) == set(EXPECTED_RESULTS), "canonical result artifact set drift")
    for name, expected_hash in EXPECTED_RESULTS.items():
        require(results[name]["sha256"] == expected_hash, f"result hash drift: {name}")
        require(results[name]["byte_identical_across_two_clean_runs"] is True, f"repeatability flag missing: {name}")
    require(results["S3X_PHASE7_CASE_RESULTS_001.csv"]["rows"] == 34542, "case artifact row count drift")
    require(results["S3X_PHASE7_MATCHED_COMPARISONS_001.csv"]["rows"] == 30704, "comparison artifact row count drift")
    require(results["S3X_PHASE7_INDEPENDENT_VALIDATION_001.json"]["case_level_mismatches"] == 0, "validation case mismatch drift")
    require(results["S3X_PHASE7_INDEPENDENT_VALIDATION_001.json"]["matched_comparison_mismatches"] == 0, "validation comparison mismatch drift")
    require(results["S3X_PHASE7_RESULTS_HASH_MANIFEST_001.json"]["manifest_integrity"] == "PASS", "manifest integrity drift")

    effectivity = record["effectivity"]
    require(effectivity["creation_state"] == "PREPARED_ON_FEATURE_BRANCH", "creation state drift")
    require(effectivity["result_freeze_effective_at_record_creation"] is False, "freeze effective too early")
    require(effectivity["freeze_effective_only_when_record_tracked_on_main"] is True, "main effectivity control missing")
    require(effectivity["merge_requires_separate_author_review"] is True, "separate author merge review missing")
    require(effectivity["post_merge_ci_required_before_downstream_claim_use"] is True, "post-merge CI gate missing")

    scope = record["scope_after_effective_freeze"]
    require(scope["canonical_result_hashes_locked"] is True, "hash lock missing")
    require(scope["validated_result_population_locked"] is True, "population lock missing")
    for key in (
        "scientific_reexecution_authorized",
        "result_mutation_authorized",
        "canonical_output_bytes_commit_authorized",
        "manuscript_claim_use_authorized",
        "manuscript_rewrite_authorized",
        "p99_x10_retuning_authorized",
        "interval_membership_retuning_authorized",
        "study3_modification_authorized",
        "study3_s3x_pooling_authorized",
    ):
        require(scope[key] is False, f"closed downstream scope opened: {key}")

    storage = record["repository_storage_policy"]
    require(storage["canonical_outputs_remain_local_ignored"] is True, "local output policy drift")
    require(storage["canonical_output_bytes_committed"] is False, "output bytes unexpectedly committed")
    require(storage["tracked_freeze_record_contains_hashes_counts_and_invariants_only"] is True, "freeze-record policy drift")

    status = read_json(STATUS)
    require(
        status["status"] == "RESULT_FREEZE_RECORD_PREPARED__NOT_EFFECTIVE__MANUSCRIPT_USE_CLOSED",
        "Phase-7E status drift",
    )
    require(status["branch_base_commit"] == EXPECTED_MAIN, "Phase-7E base binding drift")
    require(status["freeze_record"]["result_freeze_active_now"] is False, "status activates freeze before merge")
    require(status["authorized_scope"]["canonical_output_bytes_commit"] is False, "status authorizes output commit")
    require(status["authorized_scope"]["manuscript_claim_use"] is False, "status authorizes manuscript use")
    require(status["authorized_scope"]["manuscript_rewrite"] is False, "status authorizes rewrite")

    tracked = subprocess.check_output(["git", "ls-files"], cwd=ROOT, text=True).splitlines()
    forbidden = set(EXPECTED_RESULTS)
    require(
        not any(Path(path).name in forbidden for path in tracked),
        "canonical Phase-7 output bytes were committed",
    )
    require(
        not any(path.startswith("study3x/local_freeze_work/") for path in tracked),
        "local freeze workspace unexpectedly tracked",
    )
    require("study3x/local_freeze_work/" in GITIGNORE.read_text(encoding="utf-8"), "local freeze workspace is not ignored")

    workflow = WORKFLOW.read_text(encoding="utf-8")
    require(
        "python scripts/audit_paper2_post_rejection_phase7e_result_freeze.py" in workflow,
        "Phase-7E audit is not wired into CI",
    )

    print("paper2_phase7e_result_freeze_audit=PASS")
    print("result_freeze_record_prepared=YES")
    print("result_freeze_effective=NO")
    print("frozen_intervals=1919")
    print("cases_each_run=34542")
    print("matched_comparison_rows_each_run=30704")
    print("case_level_mismatches=0")
    print("matched_comparison_mismatches=0")
    print("all_five_canonical_outputs_byte_identical=PASS")
    print("canonical_output_bytes_committed=NO")
    print("manuscript_claim_use=NO")
    print("manuscript_rewrite=NO")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
