#!/usr/bin/env python3
"""Fail-closed audit for Paper-2 Phase-5B P99_X10 pre-freeze tooling."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
S3X = ROOT / "study3x"
REBUILD = ROOT / "publication/Paper_2_Studies_3_4_6/Post_Rejection_Rebuild"

EXPECTED_R2_HASHES = {
    "sensitivity_csv": "f690dd230b2897dd74ec880be0de9c207cbb3c975fb4f7740bb18b49df55b88e",
    "delta_frequency_csv": "1399dde74c0cad144e4be4b5c0af201030eaf9ae70621c8b5b70ff9a52b78349",
    "summary_json": "c57fb506c08f03f69f3bed7326355bc97a318f7b6b5015c7745cc3e956865cc6",
}
EXPECTED_PROJECTION_SHA256 = (
    "f15338f1790f60d83d2c849542f6d6e3b21a8c49f7d413cdc5098e35952294d1"
)
EXPECTED_ZERO_CHANNELS = {
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


def main() -> int:
    status_path = REBUILD / "PAPER2_PHASE5B_P99X10_PREFREEZE_STATUS.json"
    gate_path = REBUILD / "PHASE5B_P99X10_PREFREEZE_GATE_R1_2026-09-26.md"
    validator = S3X / "validation/validate_p99_x10_prefreeze.py"
    runner = S3X / "validation/run_local_p99_x10_prefreeze_validation.sh"
    tests = ROOT / "tests/test_s3x_p99_x10_prefreeze.py"

    for path in (status_path, gate_path, validator, runner, tests):
        require(
            path.is_file(),
            f"required Phase-5B file missing: {path.relative_to(ROOT)}",
        )

    status = json.loads(status_path.read_text(encoding="utf-8"))
    require(
        status.get("status")
        == "AUTHORIZED_PREFREEZE_VALIDATION_TOOLING__AWAITING_CI_AND_LOCAL_EXECUTION",
        "unexpected Phase-5B status",
    )

    local = status["predecessor"]["local_r2_execution"]
    require(local.get("status") == "PASS", "Phase-5A R2 predecessor not PASS")
    require(local.get("output_schema_version") == 2, "R2 schema version drift")
    require(local.get("channels_analyzed") == 176, "R2 channel count drift")
    require(local.get("sensitivity_rows") == 1408, "R2 sensitivity-row count drift")
    require(local.get("worktree_clean_after_run") is True, "R2 post-run worktree not clean")
    for key, expected in EXPECTED_R2_HASHES.items():
        require(
            local["outputs"][key]["sha256"] == expected,
            f"R2 evidence hash drift: {key}",
        )

    candidate = status.get("prefreeze_candidate", {})
    require(candidate.get("rule") == "P99_X10", "unexpected pre-freeze candidate")
    require(
        candidate.get("status")
        == "ADVANCED_TO_PREFREEZE_VALIDATION_NOT_SELECTED_NOT_FROZEN",
        "candidate status must remain pre-freeze only",
    )
    require(candidate.get("expected_channels") == 176, "expected channel count drift")
    require(
        candidate.get("expected_total_exceedance_count") == 1919,
        "expected P99_X10 aggregate drift",
    )
    require(
        candidate.get("expected_channels_with_exceedances") == 171,
        "expected nonzero-channel count drift",
    )
    require(
        candidate.get("expected_channels_with_zero_exceedances") == 5,
        "expected zero-channel count drift",
    )
    require(
        set(candidate.get("expected_zero_exceedance_channels", []))
        == EXPECTED_ZERO_CHANNELS,
        "expected zero-exceedance channel set drift",
    )
    require(
        candidate.get("canonical_channel_projection_sha256")
        == EXPECTED_PROJECTION_SHA256,
        "canonical channel projection digest drift",
    )

    prohibited = status.get("prohibited", {})
    for key in (
        "gap_rule_selection",
        "gap_rule_freeze",
        "timestamp_level_gap_trace_emission",
        "trace_population_freeze",
        "recovery_policy_execution",
        "scientific_execution",
        "manuscript_claim_use",
    ):
        require(prohibited.get(key) is True, f"closed Phase-5B gate not recorded: {key}")

    validator_text = validator.read_text(encoding="utf-8")
    for marker in (
        'CANDIDATE_RULE = "P99_X10"',
        '"f690dd230b2897dd74ec880be0de9c207cbb3c975fb4f7740bb18b49df55b88e"',
        '"1399dde74c0cad144e4be4b5c0af201030eaf9ae70621c8b5b70ff9a52b78349"',
        '"c57fb506c08f03f69f3bed7326355bc97a318f7b6b5015c7745cc3e956865cc6"',
        '"f15338f1790f60d83d2c849542f6d6e3b21a8c49f7d413cdc5098e35952294d1"',
        "p99 * 10.0",
        "float(minimum) > threshold",
        '"telemetry_archives_read": False',
        '"gap_rule_selected": False',
        '"gap_rule_frozen": False',
        '"timestamp_level_gap_traces_emitted": False',
        '"recovery_policy_execution_performed": False',
        '"scientific_results_generated": False',
    ):
        require(marker in validator_text, f"validator missing safety marker: {marker}")

    for forbidden in (
        "local_source",
        "pd.read_pickle",
        "pandas",
    ):
        require(
            forbidden not in validator_text,
            f"pre-freeze validator must not read telemetry source: {forbidden}",
        )

    test_text = tests.read_text(encoding="utf-8")
    for marker in (
        "test_valid_candidate_rows_pass_strict_semantics",
        "test_equal_to_threshold_is_rejected_as_non_strict",
        "test_threshold_formula_drift_is_rejected",
        "test_canonical_projection_is_order_independent",
    ):
        require(marker in test_text, f"Phase-5B regression test missing: {marker}")

    shell_check = subprocess.run(
        ["bash", "-n", str(runner)],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    require(
        shell_check.returncode == 0,
        f"Phase-5B runner shell syntax invalid: {shell_check.stderr.strip()}",
    )

    runner_text = runner.read_text(encoding="utf-8")
    for marker in (
        "S3X_GAP_SENSITIVITY_002.csv",
        "S3X_DELTA_FREQUENCIES_002.csv",
        "S3X_GAP_SENSITIVITY_SUMMARY_002.json",
        "S3X_P99_X10_PREFREEZE_VALIDATION_001.json",
        "candidate_rule=P99_X10",
        "gap_rule_selection=NO",
        "gap_rule_freeze=NO",
        "trace_extraction=NO",
        "recovery_policy_execution=NO",
        "scientific_execution=NO",
    ):
        require(marker in runner_text, f"Phase-5B runner missing marker: {marker}")

    for forbidden in (
        S3X / "results",
        S3X / "canonical",
        S3X / "traces",
    ):
        require(
            not forbidden.exists(),
            f"forbidden S3X scientific path exists: {forbidden.relative_to(ROOT)}",
        )

    print("paper2_phase5b_p99x10_prefreeze_tooling_audit=PASS")
    print("candidate_rule=P99_X10")
    print("candidate_selected=NO")
    print("gap_rule_freeze=NO")
    print("trace_extraction=NO")
    print("recovery_policy_execution=NO")
    print("scientific_execution=NO")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
