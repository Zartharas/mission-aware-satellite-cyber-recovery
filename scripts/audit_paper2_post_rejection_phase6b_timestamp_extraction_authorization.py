#!/usr/bin/env python3
"""Fail-closed audit for Paper-2 Phase-6B runtime authorization preparation."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
S3X = ROOT / "study3x"
REBUILD = ROOT / "publication/Paper_2_Studies_3_4_6/Post_Rejection_Rebuild"

AUTH_PATH = S3X / "config/S3X_PHASE6_TIMESTAMP_EXTRACTION_AUTH_001.json"
PROTOCOL_PATH = S3X / "config/S3X_TIMESTAMP_TRACE_EXTRACTION_PROTOCOL_001.json"
STATUS_PATH = REBUILD / "PAPER2_PHASE6B_TIMESTAMP_EXTRACTION_AUTHORIZATION_STATUS.json"
GATE_PATH = REBUILD / "PHASE6B_TIMESTAMP_EXTRACTION_AUTHORIZATION_GATE_R1_2026-09-27.md"

EXPECTED_PROTOCOL_SHA256 = "f6957393a864090d484e29f16067807bf52cacf0688fc48af32164ef9f7eb5a4"
EXPECTED_DESIGN_MERGE = "92534c45c85ee36c148acfe92dce1ec61ad49c24"
EXPECTED_PROJECTION = "f15338f1790f60d83d2c849542f6d6e3b21a8c49f7d413cdc5098e35952294d1"
EXPECTED_ZERO = {
    "ESA-Mission2/channel_66.zip",
    "ESA-Mission2/channel_67.zip",
    "ESA-Mission2/channel_68.zip",
    "ESA-Mission2/channel_69.zip",
    "ESA-Mission2/channel_100.zip",
}


def fail(message: str) -> None:
    print(f"[FAIL] {message}", file=sys.stderr)
    raise SystemExit(1)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    for path in (AUTH_PATH, PROTOCOL_PATH, STATUS_PATH, GATE_PATH):
        require(path.is_file(), f"missing Phase-6B artifact: {path.relative_to(ROOT)}")

    require(sha256(PROTOCOL_PATH) == EXPECTED_PROTOCOL_SHA256, "merged protocol SHA-256 drift")

    auth = read_json(AUTH_PATH)
    require(auth.get("schema") == 1, "authorization schema drift")
    require(
        auth.get("authorization_id") == "S3X-PHASE6-TIMESTAMP-EXTRACTION-AUTH-001",
        "authorization id drift",
    )
    require(auth.get("experiment_id") == "S3X-ETA-001", "experiment id drift")
    require(
        auth.get("protocol_id") == "S3X-PHASE6-TIMESTAMP-TRACE-EXTRACTION-PROTOCOL-001",
        "protocol id drift",
    )
    require(auth.get("protocol_sha256") == EXPECTED_PROTOCOL_SHA256, "authorization protocol hash drift")

    evidence = auth.get("design_evidence", {})
    require(evidence.get("design_pr") == 186, "design PR binding drift")
    require(evidence.get("design_merge_commit") == EXPECTED_DESIGN_MERGE, "design merge binding drift")
    require(evidence.get("design_post_merge_ci_run_number") == 1244, "post-merge CI run number drift")
    require(evidence.get("design_post_merge_ci_run_id") == 36334882085, "post-merge CI run id drift")
    require(evidence.get("design_post_merge_ci_head_sha") == EXPECTED_DESIGN_MERGE, "post-merge CI head drift")
    require(evidence.get("design_post_merge_ci_conclusion") == "success", "post-merge CI conclusion drift")

    require(auth.get("design_merge_verified") is True, "design merge not verified")
    require(auth.get("design_post_merge_ci_success") is True, "design post-merge CI not verified")
    require(auth.get("author_execution_approval_recorded") is True, "author execution approval not recorded")
    require(auth.get("timestamp_level_extraction_authorized") is True, "timestamp extraction not authorized")
    require(auth.get("trace_population_freeze_authorized") is False, "trace population freeze unexpectedly authorized")
    require(auth.get("recovery_policy_execution_authorized") is False, "recovery execution unexpectedly authorized")
    require(auth.get("scientific_execution_authorized") is False, "scientific execution unexpectedly authorized")

    scope = auth.get("authorization_scope", {})
    for key in (
        "timestamp_level_extraction_authorized",
        "independent_validation_authorized",
        "deterministic_repeat_execution_authorized",
    ):
        require(scope.get(key) is True, f"authorized scope missing: {key}")
    for key in (
        "trace_population_freeze_authorized",
        "recovery_policy_execution_authorized",
        "scientific_execution_authorized",
        "manuscript_claim_use_authorized",
        "gap_rule_retuning_authorized",
        "frozen_study_modification_authorized",
    ):
        require(scope.get(key) is False, f"closed authorization scope opened: {key}")

    constraints = auth.get("execution_constraints", {})
    require(constraints.get("required_branch") == "main", "runtime branch constraint drift")
    require(constraints.get("authorization_record_must_be_tracked") is True, "tracked record requirement missing")
    require(constraints.get("clean_tracked_worktree_required") is True, "clean-worktree requirement missing")
    require(constraints.get("output_root") == "study3x/local_freeze_work/", "output root drift")
    require(constraints.get("output_directory_must_be_empty") is True, "empty-output requirement missing")
    require(constraints.get("source_integrity_verification_required") is True, "source verification requirement missing")
    require(constraints.get("gap_rule") == "P99_X10", "runtime gap rule drift")
    require(constraints.get("comparison_operator") == ">", "runtime comparison drift")
    require(constraints.get("runtime_threshold_override_allowed") is False, "threshold override opened")
    require(constraints.get("runtime_multiplier_override_allowed") is False, "multiplier override opened")

    repeat = auth.get("deterministic_repeatability", {})
    require(repeat.get("two_clean_output_directories_required") is True, "two-run repeatability missing")
    require(repeat.get("byte_identical_sha256_required") is True, "byte-identical repeatability missing")
    require(repeat.get("required_before_trace_population_freeze_review") is True, "repeatability gate before freeze missing")
    require(len(repeat.get("required_matching_artifacts", [])) == 4, "repeatability artifact set drift")

    invariants = auth.get("expected_validation_invariants", {})
    require(invariants.get("channels") == 176, "channel invariant drift")
    require(invariants.get("total_intervals") == 1919, "interval invariant drift")
    require(invariants.get("channels_with_intervals") == 171, "nonzero-channel invariant drift")
    require(invariants.get("channels_with_zero_intervals") == 5, "zero-channel invariant drift")
    require(set(invariants.get("zero_interval_channels", [])) == EXPECTED_ZERO, "zero-channel set drift")
    require(invariants.get("canonical_channel_projection_sha256") == EXPECTED_PROJECTION, "projection hash drift")
    require(invariants.get("invariants_are_validation_constraints_not_retuning_targets") is True, "retuning firewall missing")

    state = auth.get("execution_state_at_authorization_record_creation", {})
    for key in (
        "timestamp_level_extraction_performed",
        "deterministic_repeat_execution_performed",
        "independent_validation_performed",
        "trace_population_frozen",
        "recovery_policy_execution_performed",
        "scientific_results_generated",
        "manuscript_claim_use",
    ):
        require(state.get(key) is False, f"execution state unexpectedly true: {key}")

    effectivity = auth.get("effectivity", {})
    require(effectivity.get("record_effective_only_when_tracked_on_main") is True, "main-effectivity gate missing")
    require(effectivity.get("creation_state") == "PREPARED_ON_FEATURE_BRANCH", "authorization creation-state marker missing")
    require(
        effectivity.get("effective_runner_condition") == "record is tracked and unmodified on clean main",
        "authorization runner-effectivity rule drift",
    )
    require(effectivity.get("record_merge_requires_separate_author_review") is True, "separate merge review gate missing")

    status = read_json(STATUS_PATH)
    require(
        status.get("status") == "AUTHORIZATION_RECORD_PREPARED__NO_EXTRACTION_PERFORMED",
        "Phase-6B status drift",
    )
    require(status.get("branch_base_commit") == EXPECTED_DESIGN_MERGE, "Phase-6B base commit drift")
    auth_status = status.get("authorization_record", {})
    require(auth_status.get("creation_state") == "PREPARED_ON_FEATURE_BRANCH", "authorization creation-state drift")
    require(
        auth_status.get("effective_runner_condition") == "tracked and unmodified on clean main",
        "authorization effectivity condition drift",
    )

    for forbidden in (
        S3X / "results",
        S3X / "canonical",
        S3X / "traces",
    ):
        require(not forbidden.exists(), f"forbidden scientific path exists: {forbidden.relative_to(ROOT)}")

    print("paper2_phase6b_timestamp_extraction_authorization_audit=PASS")
    print(f"protocol_sha256={EXPECTED_PROTOCOL_SHA256}")
    print("timestamp_level_extraction_authorized_by_author=YES")
    print("authorization_record_effectivity=CONDITIONAL_ON_TRACKED_CLEAN_MAIN")
    print("timestamp_level_extraction_performed=NO")
    print("trace_population_frozen=NO")
    print("recovery_policy_execution=NO")
    print("scientific_execution=NO")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
