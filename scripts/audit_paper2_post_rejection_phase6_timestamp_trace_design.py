#!/usr/bin/env python3
"""Fail-closed repository audit for Paper-2 Phase-6A design state."""

from __future__ import annotations

import ast
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
S3X = ROOT / "study3x"
REBUILD = ROOT / "publication/Paper_2_Studies_3_4_6/Post_Rejection_Rebuild"
WORKFLOWS = ROOT / ".github/workflows"

PROTOCOL_ID = "S3X-PHASE6-TIMESTAMP-TRACE-EXTRACTION-PROTOCOL-001"
SOURCE_FREEZE_ID = "S3X-ESA-V2-SOURCE-FREEZE-001"
GAP_FREEZE_ID = "S3X-P99X10-GAP-RULE-FREEZE-001"
EXPECTED_SOURCE_FREEZE_SHA256 = "dd1d71dc074588c12cae24c3718ed758fabd36c41b22755f57ccf98964db9f27"
EXPECTED_PROJECTION_SHA256 = "f15338f1790f60d83d2c849542f6d6e3b21a8c49f7d413cdc5098e35952294d1"
EXPECTED_TOTAL = 1919
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


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    protocol_path = S3X / "config/S3X_TIMESTAMP_TRACE_EXTRACTION_PROTOCOL_001.json"
    gap_freeze_path = S3X / "config/S3X_GAP_RULE_FREEZE_001.json"
    extractor_path = S3X / "validation/extract_p99_x10_timestamp_intervals.py"
    validator_path = S3X / "validation/validate_p99_x10_timestamp_intervals.py"
    runner_path = S3X / "validation/run_local_p99_x10_timestamp_extraction.sh"
    status_path = REBUILD / "PAPER2_PHASE6_TIMESTAMP_TRACE_EXTRACTION_DESIGN_STATUS.json"
    design_path = REBUILD / "PHASE6_TIMESTAMP_TRACE_EXTRACTION_DESIGN_R1_2026-09-27.md"
    test_path = ROOT / "tests/test_s3x_phase6_timestamp_trace_design.py"
    workflow_path = WORKFLOWS / "validate-research-configs.yml"

    required_paths = (
        protocol_path,
        gap_freeze_path,
        extractor_path,
        validator_path,
        runner_path,
        status_path,
        design_path,
        test_path,
        workflow_path,
    )
    for path in required_paths:
        require(path.is_file(), f"required Phase-6A file missing: {path.relative_to(ROOT)}")

    protocol = read_json(protocol_path)
    require(protocol.get("schema") == 1, "unexpected protocol schema")
    require(protocol.get("protocol_id") == PROTOCOL_ID, "unexpected protocol id")
    require(protocol.get("experiment_id") == "S3X-ETA-001", "unexpected experiment id")
    require(
        protocol.get("status") == "DESIGN_ONLY__NO_TIMESTAMP_EXTRACTION_AUTHORIZED",
        "Phase-6 protocol status drift",
    )

    upstream = protocol.get("upstream", {})
    source = upstream.get("source_freeze", {})
    require(source.get("freeze_id") == SOURCE_FREEZE_ID, "source freeze id drift")
    require(source.get("sha256") == EXPECTED_SOURCE_FREEZE_SHA256, "source freeze hash drift")
    require(source.get("channel_counts", {}).get("total") == 176, "channel count drift")

    rule = upstream.get("gap_rule_freeze", {})
    require(rule.get("freeze_id") == GAP_FREEZE_ID, "gap freeze id drift")
    require(rule.get("rule") == "P99_X10", "gap rule drift")
    require(rule.get("comparison_operator") == ">", "strict comparison drift")
    require(float(rule.get("multiplier")) == 10.0, "multiplier drift")

    prefreeze = upstream.get("prefreeze_validation", {})
    require(prefreeze.get("total_exceedance_count") == EXPECTED_TOTAL, "prefreeze total drift")
    require(
        prefreeze.get("canonical_channel_projection_sha256")
        == EXPECTED_PROJECTION_SHA256,
        "prefreeze projection hash drift",
    )

    invariants = protocol.get("expected_invariants", {})
    require(invariants.get("total_intervals") == EXPECTED_TOTAL, "Phase-6 expected total drift")
    require(invariants.get("channels_with_intervals") == 171, "nonzero-channel count drift")
    require(invariants.get("channels_with_zero_intervals") == 5, "zero-channel count drift")
    require(set(invariants.get("zero_interval_channels", [])) == EXPECTED_ZERO, "zero-channel set drift")
    require(
        invariants.get("canonical_channel_projection_sha256")
        == EXPECTED_PROJECTION_SHA256,
        "Phase-6 projection hash drift",
    )
    require(
        invariants.get("invariants_are_validation_constraints_not_retuning_targets") is True,
        "retuning-target firewall missing",
    )

    determinism = protocol.get("determinism_validation", {})
    require(determinism.get("repeat_execution_required") is True, "repeat execution gate missing")
    require(determinism.get("independent_output_directories_required") is True, "independent repeat directories not required")
    require(determinism.get("byte_identical_sha256_required") is True, "byte-identical repeatability not required")
    require(determinism.get("variable_wall_clock_metadata_allowed_in_canonical_outputs") is False, "variable canonical metadata unexpectedly allowed")
    require(determinism.get("required_before_trace_population_freeze_review") is True, "repeatability not required before population-freeze review")

    numeric = protocol.get("numeric_method", {})
    require(numeric.get("comparison_operator") == ">", "numeric comparison drift")
    require(numeric.get("threshold_runtime_override_allowed") is False, "threshold override opened")
    require(numeric.get("multiplier_runtime_override_allowed") is False, "multiplier override opened")
    require(
        numeric.get("p99_method") == "repository quantile_linear linear interpolation",
        "P99 method drift",
    )

    auth = protocol.get("authorization_model", {})
    require(auth.get("phase6a_design_authorized") is True, "Phase-6A design authorization missing")
    require(auth.get("timestamp_level_extraction_authorized") is False, "runtime extraction opened")
    require(
        auth.get("runtime_requires_separate_versioned_authorization_record") is True,
        "separate runtime authorization control missing",
    )
    require(auth.get("runtime_authorization_record_committed") is False, "runtime authorization record unexpectedly committed")

    for key in (
        "timestamp_level_extraction_authorized",
        "timestamp_level_extraction_performed",
        "trace_population_frozen",
        "recovery_policy_execution_performed",
        "scientific_results_generated",
        "manuscript_claim_use",
    ):
        require(protocol.get("gates", {}).get(key) is False, f"closed protocol gate changed: {key}")

    status = read_json(status_path)
    require(
        status.get("status") == "DESIGN_PREPARED__NO_TIMESTAMP_EXTRACTION_AUTHORIZED",
        "Phase-6A status drift",
    )
    require(
        status.get("branch_base_commit")
        == "1d36b224e46c15653f0c5d76dce6da26f7d9a6e1",
        "Phase-6A branch base drift",
    )
    for key in (
        "timestamp_level_gap_trace_extraction",
        "trace_population_freeze",
        "recovery_policy_execution",
        "scientific_execution",
        "manuscript_claim_use",
        "frozen_study_modification",
        "gap_rule_retuning",
    ):
        require(status.get("prohibited", {}).get(key) is True, f"prohibited status gate changed: {key}")

    gap = read_json(gap_freeze_path)
    require(gap.get("freeze_id") == GAP_FREEZE_ID, "Phase-5C freeze id drift")
    require(gap.get("rule", {}).get("name") == "P99_X10", "Phase-5C rule drift")
    require(gap.get("rule", {}).get("status") == "SELECTED_AND_FROZEN", "Phase-5C rule not frozen")
    require(gap.get("rule", {}).get("comparison_operator") == ">", "Phase-5C comparison drift")
    require(float(gap.get("rule", {}).get("multiplier")) == 10.0, "Phase-5C multiplier drift")
    require(
        gap.get("lock_policy", {}).get("retune_after_timestamp_trace_inspection") is False,
        "Phase-5C retuning lock drift",
    )
    for key in (
        "timestamp_level_gap_trace_extraction",
        "trace_population_frozen",
        "recovery_policy_execution_performed",
        "scientific_results_generated",
        "manuscript_claim_use",
    ):
        require(gap.get("gates", {}).get(key) is False, f"Phase-5C closed gate changed: {key}")

    authorization_records = list(
        (S3X / "config").glob("S3X_PHASE6_TIMESTAMP_EXTRACTION_AUTH_*.json")
    )
    require(len(authorization_records) <= 1, "multiple Phase-6 runtime authorization records exist")
    if authorization_records:
        require(
            authorization_records[0].name == "S3X_PHASE6_TIMESTAMP_EXTRACTION_AUTH_001.json",
            "unexpected Phase-6 runtime authorization record name",
        )
        phase6b_status = (
            REBUILD / "PAPER2_PHASE6B_TIMESTAMP_EXTRACTION_AUTHORIZATION_STATUS.json"
        )
        phase6b_audit = (
            ROOT / "scripts/audit_paper2_post_rejection_phase6b_timestamp_extraction_authorization.py"
        )
        require(phase6b_status.is_file(), "later Phase-6B status missing for authorization record")
        require(phase6b_audit.is_file(), "later Phase-6B audit missing for authorization record")

    for forbidden in (
        S3X / "results",
        S3X / "canonical",
        S3X / "traces",
    ):
        require(not forbidden.exists(), f"forbidden scientific path exists: {forbidden.relative_to(ROOT)}")

    extractor_source = extractor_path.read_text(encoding="utf-8")
    validator_source = validator_path.read_text(encoding="utf-8")
    ast.parse(extractor_source, filename=str(extractor_path))
    ast.parse(validator_source, filename=str(validator_path))
    require("--multiplier" not in extractor_source, "extractor exposes multiplier runtime override")
    require("--threshold" not in extractor_source, "extractor exposes threshold runtime override")
    require("--authorization-record" in extractor_source, "extractor lacks authorization-record gate")
    require("--authorization-record" in validator_source, "validator lacks authorization-record gate")

    runner_source = runner_path.read_text(encoding="utf-8")
    require("AUTH_RECORD" in runner_source, "runner lacks authorization-record requirement")
    require("--authorization-record" in runner_source, "runner does not pass authorization record")
    require('git branch --show-current' in runner_source, "runner does not require main")
    require('git ls-files --error-unmatch' in runner_source, "runner does not require tracked authorization")
    require('git diff --quiet' in runner_source, "runner does not require clean tracked worktree")
    require('study3x/local_freeze_work/' in runner_source, "runner does not confine output to ignored local tree")
    require('output directory must be empty' in runner_source, "runner does not require an empty output directory")
    require('output directory must be empty before extraction' in extractor_source, "extractor does not refuse stale output directories")
    for marker in (
        "design_merge_verified",
        "design_post_merge_ci_success",
        "author_execution_approval_recorded",
    ):
        require(marker in extractor_source, f"extractor missing runtime authorization marker: {marker}")
        require(marker in validator_source, f"validator missing runtime authorization marker: {marker}")
    subprocess.run(["bash", "-n", str(runner_path)], check=True)

    design = design_path.read_text(encoding="utf-8")
    require("DESIGN ONLY" in design, "design-only marker missing")
    require("1,919" in design, "bound interval invariant missing from design")
    require("strict" in design.lower() and "greater-than" in design.lower(), "strict comparison explanation missing")
    require("does not freeze" in design.lower(), "trace-population non-freeze control missing")

    workflow = workflow_path.read_text(encoding="utf-8")
    require(
        "python scripts/audit_paper2_post_rejection_phase6_timestamp_trace_design.py"
        in workflow,
        "Phase-6A audit is not wired into release-gate CI",
    )

    forbidden_workflow_tokens = (
        "run_local_p99_x10_timestamp_extraction.sh",
        "extract_p99_x10_timestamp_intervals.py",
        "validate_p99_x10_timestamp_intervals.py --mission1",
    )
    for path in WORKFLOWS.glob("*.y*ml"):
        text = path.read_text(encoding="utf-8")
        for token in forbidden_workflow_tokens:
            require(token not in text, f"real Phase-6 runtime wired into CI: {path.name}: {token}")

    gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
    require("study3x/local_source/" in gitignore, "local source ignore rule missing")
    require("study3x/local_freeze_work/" in gitignore, "local freeze-work ignore rule missing")

    print("paper2_phase6_timestamp_trace_design_audit=PASS")
    print("phase6_design=YES")
    print("timestamp_level_extraction_authorized=NO")
    print("timestamp_level_extraction_performed=NO")
    print("trace_population_frozen=NO")
    print("recovery_policy_execution=NO")
    print("scientific_execution=NO")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
