#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
S3X = ROOT / "study3x"
REBUILD = ROOT / "publication/Paper_2_Studies_3_4_6/Post_Rejection_Rebuild"

AUTH = S3X / "config/S3X_PHASE7_RUNTIME_AUTH_001.json"
STATUS = REBUILD / "PAPER2_PHASE7C_RUNTIME_AUTHORIZATION_STATUS.json"
WORKFLOW = ROOT / ".github/workflows/validate-research-configs.yml"

EXPECTED = {
    "study3x/config/S3X_PHASE7_RECOVERY_REPLAY_PROTOCOL_001.json":
        "f42fe8c0c58ee3b9152e629f5673bd5c71ffede4",
    "study3x/config/S3X_PHASE6_TRACE_POPULATION_FREEZE_001.json":
        "ed0bdcec443b7f0c3ee80d441e1122f32e499d3e",
    "study3x/config/S3X_PHASE7_IMPLEMENTATION_FREEZE_CANDIDATE_001.json":
        "6fb62e9a6d3187485d4f1591a063dd56f5ed2aa9",
    "study3x/src/recovery_replay.py":
        "09a1c887f8861a6e5dba6059cab2ab906befbbcd",
    "study3x/audit/reference_replay.py":
        "9e13446323be67115950374cb5debfaa7532a17e",
    "study3x/runtime/run_phase7_replay.py":
        "1aefa814d8f619dcd5ac9c0848950965660b5c90",
    "study3x/audit/validate_phase7_replay.py":
        "df9faa48a92d0cccd32d77365a163518f8574d5b",
    "study3x/validation/run_local_phase7_replay.sh":
        "e5b8ead787a1811070a953ff7803c948defea95d",
}

EXPECTED_INPUT_SHA = "cfa4fa3d88cb525237cbfe347fabe8485021351f3b639bdb58f79c575d8a51bc"


def require(condition: bool, message: str) -> None:
    if not condition:
        print(f"[FAIL] {message}", file=sys.stderr)
        raise SystemExit(1)


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def git_blob(rel: str) -> str:
    return subprocess.check_output(
        ["git", "hash-object", rel],
        cwd=ROOT,
        text=True,
    ).strip()


def main() -> int:
    require(AUTH.is_file(), "Phase-7C authorization record missing")
    require(STATUS.is_file(), "Phase-7C status record missing")

    for rel, expected in EXPECTED.items():
        path = ROOT / rel
        require(path.is_file(), f"bound file missing: {rel}")
        require(git_blob(rel) == expected, f"bound blob drift: {rel}")

    auth = read_json(AUTH)
    require(auth["authorization_id"] == "S3X-PHASE7-RUNTIME-AUTH-001", "authorization id drift")
    require(auth["status"] == "PREPARED_ON_FEATURE_BRANCH__NOT_EFFECTIVE", "authorization preparation state drift")
    require(auth["predecessor"]["phase7b_merge_commit"] == "6b890245bee10536b8600161ff5f63e7ebd5cdfa", "Phase-7B merge binding drift")
    require(auth["predecessor"]["phase7b_post_merge_ci_run_number"] == 1256, "Phase-7B CI binding drift")
    require(auth["predecessor"]["phase7b_post_merge_ci_conclusion"] == "success", "Phase-7B CI conclusion drift")

    bindings = auth["frozen_bindings"]
    require(bindings["frozen_interval_csv_sha256"] == EXPECTED_INPUT_SHA, "frozen interval SHA drift")
    require(bindings["protocol_blob"] == EXPECTED["study3x/config/S3X_PHASE7_RECOVERY_REPLAY_PROTOCOL_001.json"], "protocol binding drift")
    require(bindings["trace_freeze_blob"] == EXPECTED["study3x/config/S3X_PHASE6_TRACE_POPULATION_FREEZE_001.json"], "trace freeze binding drift")
    require(bindings["implementation_candidate_blob"] == EXPECTED["study3x/config/S3X_PHASE7_IMPLEMENTATION_FREEZE_CANDIDATE_001.json"], "candidate binding drift")
    require(bindings["primary_blob"] == EXPECTED["study3x/src/recovery_replay.py"], "primary binding drift")
    require(bindings["reference_blob"] == EXPECTED["study3x/audit/reference_replay.py"], "reference binding drift")
    require(bindings["population_runtime_blob"] == EXPECTED["study3x/runtime/run_phase7_replay.py"], "runtime binding drift")
    require(bindings["population_validator_blob"] == EXPECTED["study3x/audit/validate_phase7_replay.py"], "validator binding drift")
    require(bindings["local_runtime_gate"]["git_blob_sha1"] == EXPECTED["study3x/validation/run_local_phase7_replay.sh"], "local gate binding drift")

    scope = auth["authorization_scope"]
    for key in (
        "real_frozen_interval_artifact_read_authorized",
        "real_1919_interval_expansion_authorized",
        "recovery_policy_execution_authorized",
        "scientific_execution_authorized",
        "independent_reference_validation_authorized",
        "deterministic_repeat_execution_authorized",
    ):
        require(scope[key] is True, f"prepared runtime scope not open: {key}")
    for key in (
        "result_freeze_authorized",
        "manuscript_claim_use_authorized",
        "p99_x10_retuning_authorized",
        "interval_membership_retuning_authorized",
        "study3_modification_authorized",
        "study3_s3x_pooling_authorized",
    ):
        require(scope[key] is False, f"prohibited scope opened: {key}")

    constraints = auth["runtime_constraints"]
    require(constraints["required_branch"] == "main", "required branch drift")
    require(constraints["clean_tracked_worktree_required"] is True, "clean-worktree gate missing")
    require(constraints["frozen_interval_count"] == 1919, "interval-count drift")
    require(constraints["cases_per_interval"] == 18, "cases-per-interval drift")
    require(constraints["expected_case_count"] == 34542, "case-count drift")
    require(constraints["expected_matched_comparison_rows"] == 30704, "comparison-count drift")
    require(constraints["canonical_run_directories"] == [
        "study3x/local_freeze_work/phase7_authorized_run1_001",
        "study3x/local_freeze_work/phase7_authorized_run2_001",
    ], "canonical run directories drift")

    repeat = auth["deterministic_repeatability"]
    require(repeat["two_clean_output_directories_required"] is True, "two-run requirement missing")
    require(repeat["byte_identical_sha256_required"] is True, "byte-identity requirement missing")
    require(repeat["accepted_primary_reference_case_mismatches"] == 0, "case mismatch tolerance drift")
    require(repeat["accepted_matched_comparison_mismatches"] == 0, "comparison mismatch tolerance drift")
    require(len(repeat["required_matching_artifacts"]) == 5, "repeatability artifact set drift")

    boundary = auth["result_freeze_boundary"]
    require(boundary["result_freeze_authorized_now"] is False, "result freeze opened too early")
    require(boundary["manuscript_claim_use_authorized_now"] is False, "manuscript use opened too early")
    require(boundary["canonical_output_commit_authorized_now"] is False, "canonical output commit opened too early")
    require(boundary["result_freeze_requires_separate_author_review"] is True, "separate result-freeze review missing")

    created = auth["execution_state_at_record_creation"]
    require(all(value is False for value in created.values()), "execution already recorded at authorization preparation")

    effectivity = auth["effectivity"]
    require(effectivity["record_effective_only_when_tracked_on_main"] is True, "main-only effectivity missing")
    require(effectivity["creation_state"] == "PREPARED_ON_FEATURE_BRANCH", "creation state drift")
    require(effectivity["record_merge_requires_separate_author_review"] is True, "separate merge review missing")
    require(effectivity["actual_runtime_execution_requires_explicit_post_merge_author_instruction"] is True, "post-merge execution instruction gate missing")

    status = read_json(STATUS)
    require(status["status"] == "PHASE7C_RUNTIME_AUTHORIZATION_PREPARED__NOT_EFFECTIVE__NO_REAL_EXECUTION", "status drift")
    require(status["authorization_candidate"]["authorization_effective_now"] is False, "authorization effective before merge")
    require(status["authorization_candidate"]["cases"] == 34542, "status case count drift")
    require(status["authorization_candidate"]["matched_comparison_rows"] == 30704, "status comparison count drift")
    require(all(value is False for value in status["executed_now"].values()), "status records execution before authorization effectivity")

    runner = (S3X / "validation/run_local_phase7_replay.sh").read_text(encoding="utf-8")
    for phrase in (
        'if [ "$(git branch --show-current)" != "main" ]',
        "requires a clean tracked worktree",
        "phase7_authorized_run1_001",
        "phase7_authorized_run2_001",
        "S3X_PHASE7_LOCAL_AUTHORIZED_REPLAY_AND_VALIDATION=PASS",
        "result_freeze=NO",
        "manuscript_claim_use=NO",
    ):
        require(phrase in runner, f"runtime-gate control missing: {phrase}")

    tracked = subprocess.check_output(["git", "ls-files"], cwd=ROOT, text=True).splitlines()
    forbidden_names = {
        "S3X_PHASE7_CASE_RESULTS_001.csv",
        "S3X_PHASE7_MATCHED_COMPARISONS_001.csv",
        "S3X_PHASE7_SUMMARY_001.json",
        "S3X_PHASE7_INDEPENDENT_VALIDATION_001.json",
        "S3X_PHASE7_RESULTS_HASH_MANIFEST_001.json",
    }
    require(
        not any(Path(path).name in forbidden_names for path in tracked),
        "Phase-7 real scientific output is tracked before runtime",
    )

    workflow = WORKFLOW.read_text(encoding="utf-8")
    require(
        "python scripts/audit_paper2_post_rejection_phase7c_runtime_authorization.py"
        in workflow,
        "Phase-7C audit not wired into CI",
    )

    print("paper2_phase7c_runtime_authorization_audit=PASS")
    print("authorization_prepared=YES")
    print("authorization_effective=NO")
    print("real_1919_interval_expansion_performed=NO")
    print("scientific_execution_performed=NO")
    print("result_freeze=NO")
    print("manuscript_claim_use=NO")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
