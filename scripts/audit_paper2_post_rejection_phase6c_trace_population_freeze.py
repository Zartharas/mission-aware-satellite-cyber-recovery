#!/usr/bin/env python3
"""Fail-closed audit for Paper-2 Phase-6C trace-population freeze preparation."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
S3X = ROOT / "study3x"
REBUILD = ROOT / "publication/Paper_2_Studies_3_4_6/Post_Rejection_Rebuild"

FREEZE = S3X / "config/S3X_PHASE6_TRACE_POPULATION_FREEZE_001.json"
PROTOCOL = S3X / "config/S3X_TIMESTAMP_TRACE_EXTRACTION_PROTOCOL_001.json"
AUTH = S3X / "config/S3X_PHASE6_TIMESTAMP_EXTRACTION_AUTH_001.json"
GAP = S3X / "config/S3X_GAP_RULE_FREEZE_001.json"
STATUS = REBUILD / "PAPER2_PHASE6C_TRACE_POPULATION_FREEZE_STATUS.json"
GATE = REBUILD / "PHASE6C_TRACE_POPULATION_FREEZE_GATE_R1_2026-09-27.md"
WORKFLOW = ROOT / ".github/workflows/validate-research-configs.yml"

EXPECTED_MAIN = "5b835b442b8be5a8556790324b8f234d08943def"
EXPECTED_PROTOCOL_SHA = "f6957393a864090d484e29f16067807bf52cacf0688fc48af32164ef9f7eb5a4"
EXPECTED_SOURCE_FREEZE_SHA = "dd1d71dc074588c12cae24c3718ed758fabd36c41b22755f57ccf98964db9f27"
EXPECTED_PROJECTION = "f15338f1790f60d83d2c849542f6d6e3b21a8c49f7d413cdc5098e35952294d1"
EXPECTED_ZERO = {
    "ESA-Mission2/channel_66.zip",
    "ESA-Mission2/channel_67.zip",
    "ESA-Mission2/channel_68.zip",
    "ESA-Mission2/channel_69.zip",
    "ESA-Mission2/channel_100.zip",
}
EXPECTED_ARTIFACTS = {
    "S3X_P99_X10_TIMESTAMP_INTERVALS_001.csv":
        "cfa4fa3d88cb525237cbfe347fabe8485021351f3b639bdb58f79c575d8a51bc",
    "S3X_P99_X10_TIMESTAMP_INTERVALS_SUMMARY_001.json":
        "9d7bcafac252cb39023c86e84db37bdb6ab6c674b2360622e4c43486d41756c5",
    "S3X_P99_X10_TIMESTAMP_INTERVALS_MANIFEST_001.json":
        "9be6db23bb7229da0aae17f0c4073a04c314d5079e595ab69c00aa0ee7a29983",
    "S3X_P99_X10_TIMESTAMP_INTERVALS_VALIDATION_001.json":
        "a1116119d56465f0a7aa990ad379441d0f373848c25b99c3369348228facf647",
}


def fail(message: str) -> None:
    print(f"[FAIL] {message}", file=sys.stderr)
    raise SystemExit(1)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    for path in (FREEZE, PROTOCOL, AUTH, GAP, STATUS, GATE, WORKFLOW):
        require(path.is_file(), f"missing Phase-6C dependency: {path.relative_to(ROOT)}")

    require(sha256(PROTOCOL) == EXPECTED_PROTOCOL_SHA, "protocol SHA-256 drift")

    record = read_json(FREEZE)
    require(record.get("schema") == 1, "freeze schema drift")
    require(record.get("freeze_id") == "S3X-P99X10-TRACE-POPULATION-FREEZE-001", "freeze id drift")
    require(record.get("experiment_id") == "S3X-ETA-001", "experiment id drift")
    require(record.get("status") == "PREPARED_ON_FEATURE_BRANCH__NOT_EFFECTIVE", "pre-merge status drift")
    require(record.get("authorized_main_commit") == EXPECTED_MAIN, "authorized main binding drift")

    upstream = record.get("upstream", {})
    require(upstream.get("source_freeze", {}).get("sha256") == EXPECTED_SOURCE_FREEZE_SHA, "source freeze drift")
    require(upstream.get("gap_rule_freeze", {}).get("freeze_id") == "S3X-P99X10-GAP-RULE-FREEZE-001", "gap freeze id drift")
    require(upstream.get("gap_rule_freeze", {}).get("rule") == "P99_X10", "gap rule drift")
    require(upstream.get("gap_rule_freeze", {}).get("comparison_operator") == ">", "comparison operator drift")
    require(float(upstream.get("gap_rule_freeze", {}).get("multiplier")) == 10.0, "multiplier drift")
    require(upstream.get("timestamp_trace_protocol", {}).get("sha256") == EXPECTED_PROTOCOL_SHA, "protocol binding drift")
    require(upstream.get("runtime_authorization", {}).get("authorization_id") == "S3X-PHASE6-TIMESTAMP-EXTRACTION-AUTH-001", "authorization id drift")
    require(upstream.get("runtime_authorization", {}).get("phase6b_merge_commit") == EXPECTED_MAIN, "Phase-6B merge binding drift")
    require(upstream.get("runtime_authorization", {}).get("phase6b_post_merge_ci_run_number") == 1249, "Phase-6B post-merge run drift")
    require(upstream.get("runtime_authorization", {}).get("phase6b_post_merge_ci_run_id") == 36338339416, "Phase-6B post-merge run id drift")
    require(upstream.get("runtime_authorization", {}).get("phase6b_post_merge_ci_conclusion") == "success", "Phase-6B CI conclusion drift")

    execution = record.get("validated_local_execution", {})
    for key in (
        "source_identity_verification",
        "run1_extraction_and_validation",
        "run2_extraction_and_validation",
        "deterministic_repeatability",
        "independent_repository_validation_both_runs",
    ):
        require(execution.get(key) == "PASS", f"execution evidence not PASS: {key}")
    require(
        execution.get("validation_characterization")
        == "SEPARATELY_IMPLEMENTED_REPOSITORY_VALIDATOR__NOT_INDEPENDENT_HUMAN_OR_EXTERNAL_REPLICATION",
        "validation characterization drift",
    )

    population = record.get("frozen_population_identity", {})
    require(population.get("channels") == 176, "channel count drift")
    require(population.get("total_intervals") == 1919, "interval count drift")
    require(population.get("channels_with_intervals") == 171, "nonzero-channel count drift")
    require(population.get("channels_with_zero_intervals") == 5, "zero-channel count drift")
    require(set(population.get("zero_interval_channels", [])) == EXPECTED_ZERO, "zero-channel set drift")
    require(population.get("canonical_channel_projection_sha256") == EXPECTED_PROJECTION, "projection hash drift")

    artifacts = population.get("canonical_artifacts", {})
    require(set(artifacts) == set(EXPECTED_ARTIFACTS), "canonical artifact set drift")
    for name, expected_hash in EXPECTED_ARTIFACTS.items():
        require(artifacts[name].get("sha256") == expected_hash, f"artifact hash drift: {name}")
        require(artifacts[name].get("byte_identical_across_two_clean_runs") is True, f"repeatability flag missing: {name}")

    effectivity = record.get("effectivity", {})
    require(effectivity.get("creation_state") == "PREPARED_ON_FEATURE_BRANCH", "creation state drift")
    require(effectivity.get("trace_population_frozen_at_record_creation") is False, "freeze became effective before merge")
    require(effectivity.get("freeze_effective_only_when_record_tracked_on_main") is True, "main effectivity control missing")
    require(effectivity.get("merge_requires_separate_author_review") is True, "separate author merge review missing")
    require(
        effectivity.get("effective_freeze_condition")
        == "record is tracked and unmodified on main after separately authorized merge",
        "freeze effectivity rule drift",
    )

    scope = record.get("scope_after_effective_freeze", {})
    require(scope.get("exact_population_identity_locked") is True, "population identity lock missing")
    require(scope.get("artifact_hashes_locked") is True, "artifact hash lock missing")
    for key in (
        "interval_membership_retuning_allowed",
        "gap_rule_retuning_allowed",
        "recovery_policy_execution_authorized",
        "scientific_execution_authorized",
        "manuscript_claim_use_authorized",
        "frozen_study_modification_authorized",
    ):
        require(scope.get(key) is False, f"closed downstream scope opened: {key}")

    storage = record.get("repository_storage_policy", {})
    require(storage.get("canonical_large_outputs_remain_local_ignored") is True, "local-output policy drift")
    require(storage.get("canonical_output_bytes_committed") is False, "canonical output bytes unexpectedly committed")
    require(storage.get("tracked_freeze_record_contains_hashes_and_invariants_only") is True, "repository-safe record policy drift")

    status = read_json(STATUS)
    require(status.get("status") == "TRACE_POPULATION_FREEZE_RECORD_PREPARED__NOT_EFFECTIVE", "Phase-6C status drift")
    require(status.get("branch_base_commit") == EXPECTED_MAIN, "Phase-6C base binding drift")
    require(status.get("freeze_record", {}).get("trace_population_frozen_now") is False, "status freezes population before merge")

    auth = read_json(AUTH)
    require(auth.get("timestamp_level_extraction_authorized") is True, "Phase-6B extraction authorization missing")
    require(auth.get("trace_population_freeze_authorized") is False, "Phase-6B record retroactively opened trace freeze")
    require(auth.get("recovery_policy_execution_authorized") is False, "recovery execution unexpectedly authorized")
    require(auth.get("scientific_execution_authorized") is False, "scientific execution unexpectedly authorized")

    gap = read_json(GAP)
    require(gap.get("rule", {}).get("name") == "P99_X10", "P99_X10 rule changed")
    require(gap.get("lock_policy", {}).get("retune_after_timestamp_trace_inspection") is False, "P99_X10 retuning lock opened")

    tracked = subprocess.check_output(["git", "ls-files"], text=True).splitlines()
    for name in EXPECTED_ARTIFACTS:
        require(not any(Path(path).name == name for path in tracked), f"local canonical output was committed: {name}")

    for forbidden in (S3X / "results", S3X / "canonical", S3X / "traces"):
        require(not forbidden.exists(), f"forbidden scientific path exists: {forbidden.relative_to(ROOT)}")

    workflow = WORKFLOW.read_text(encoding="utf-8")
    require(
        "python scripts/audit_paper2_post_rejection_phase6c_trace_population_freeze.py"
        in workflow,
        "Phase-6C audit is not wired into CI",
    )

    print("paper2_phase6c_trace_population_freeze_audit=PASS")
    print("candidate_population_validated=YES")
    print("candidate_intervals=1919")
    print("deterministic_repeatability=PASS")
    print("trace_population_freeze_record_prepared=YES")
    print("trace_population_frozen=NO")
    print("recovery_policy_execution=NO")
    print("scientific_execution=NO")
    print("manuscript_claim_use=NO")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
