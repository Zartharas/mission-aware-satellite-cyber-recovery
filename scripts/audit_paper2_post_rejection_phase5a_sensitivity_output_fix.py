#!/usr/bin/env python3
"""Fail-closed audit for Paper-2 Phase-5A S3X sensitivity output correction."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
S3X = ROOT / "study3x"
REBUILD = ROOT / "publication/Paper_2_Studies_3_4_6/Post_Rejection_Rebuild"

EXPECTED_R1_HASHES = {
    "sensitivity_csv": "033912eedd7ab1398d07e396c671b95912924f554b35e9eedbc6813eedbc68c5",
    "delta_frequency_csv": "1399dde74c0cad144e4be4b5c0af201030eaf9ae70621c8b5b70ff9a52b78349",
    "summary_json": "7d752002b4d91f8789d58c97a79dd7e0a9bcda9f296e3d96816d9cf7fc24ee51",
}


def fail(message: str) -> None:
    print(f"[FAIL] {message}", file=sys.stderr)
    raise SystemExit(1)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def main() -> int:
    status_path = REBUILD / "PAPER2_PHASE5A_SENSITIVITY_OUTPUT_FIX_STATUS.json"
    gate_path = REBUILD / "PHASE5A_SENSITIVITY_OUTPUT_FIX_GATE_R1_2026-09-26.md"
    analyzer_r2 = S3X / "validation/analyze_cadence_gap_sensitivity.py"
    analyzer_r1 = S3X / "validation/analyze_cadence_gap_sensitivity_r1.py"
    runner_r2 = S3X / "validation/run_local_gap_sensitivity_r2.sh"
    runner_r1 = S3X / "validation/run_local_gap_sensitivity.sh"
    tests = ROOT / "tests/test_s3x_gap_sensitivity.py"

    for file_path in (
        status_path,
        gate_path,
        analyzer_r2,
        analyzer_r1,
        runner_r2,
        runner_r1,
        tests,
    ):
        require(
            file_path.is_file(),
            f"required Phase-5A file missing: {file_path.relative_to(ROOT)}",
        )

    status = json.loads(status_path.read_text(encoding="utf-8"))
    require(
        status.get("status")
        == "AUTHORIZED_OUTPUT_SCHEMA_CORRECTION__AWAITING_CI_AND_LOCAL_RERUN",
        "unexpected Phase-5A status",
    )

    local = status["predecessor"]["local_phase5_execution"]
    require(local.get("status") == "PASS", "Phase-5 local predecessor not PASS")
    require(local.get("channels_analyzed") == 176, "unexpected predecessor channel count")
    require(local.get("sensitivity_rows") == 1408, "unexpected predecessor sensitivity-row count")
    for key, expected in EXPECTED_R1_HASHES.items():
        require(
            local["outputs"][key]["sha256"] == expected,
            f"R1 evidence hash drift: {key}",
        )
    require(local.get("worktree_clean_after_run") is True, "R1 post-run worktree was not clean")

    defect = status.get("defect", {})
    require(
        defect.get("class") == "OUTPUT_SCHEMA_FIELD_NAME_COLLISION",
        "unexpected Phase-5A defect class",
    )
    require(
        defect.get("scientific_calculation_invalidated") is False,
        "Phase-5A must not mark scientific calculation invalidated",
    )
    require(
        defect.get("threshold_formula_recalculation_mismatches") == 0,
        "threshold recalculation mismatch count changed",
    )
    require(defect.get("sensitivity_rows_checked") == 1408, "reviewed-row count changed")

    prohibited = status.get("prohibited", {})
    for key in (
        "gap_rule_selection",
        "gap_rule_freeze",
        "timestamp_level_gap_trace_emission",
        "trace_population_freeze",
        "recovery_policy_execution",
        "scientific_execution",
        "scientific_claim_change",
        "manuscript_claim_use",
    ):
        require(prohibited.get(key) is True, f"closed Phase-5A gate not recorded: {key}")

    analyzer = analyzer_r2.read_text(encoding="utf-8")
    required_analyzer_markers = (
        'OUTPUT_SCHEMA_VERSION = 2',
        'AUDIT_ID = "S3X-GAP-SENSITIVITY-002"',
        'SENSITIVITY_OUTPUT = "S3X_GAP_SENSITIVITY_002.csv"',
        'FREQUENCY_OUTPUT = "S3X_DELTA_FREQUENCIES_002.csv"',
        'SUMMARY_OUTPUT = "S3X_GAP_SENSITIVITY_SUMMARY_002.json"',
        '"cadence_median_seconds"',
        '"cadence_p99_seconds"',
        '"exceedance_median_seconds"',
        '"exceedance_p99_seconds"',
        '"legacy_metric_name_collision_present": False',
        '"sensitivity_csv": output_file_record(sensitivity_path)',
        '"delta_frequency_csv": output_file_record(frequency_path)',
        '"gap_rule_selected": False',
        '"gap_rule_frozen": False',
        '"timestamp_level_gap_traces_emitted": False',
        '"recovery_policy_execution_performed": False',
        '"scientific_results_generated": False',
    )
    for marker in required_analyzer_markers:
        require(marker in analyzer, f"R2 analyzer missing marker: {marker}")

    tests_text = tests.read_text(encoding="utf-8")
    for marker in (
        "test_sensitivity_row_separates_cadence_and_exceedance_metrics",
        "test_output_file_record_binds_exact_sha256",
        'self.assertNotIn("median_seconds", row)',
        'self.assertNotIn("p99_seconds", row)',
    ):
        require(marker in tests_text, f"Phase-5A regression test missing marker: {marker}")

    r1_text = runner_r1.read_text(encoding="utf-8")
    require(
        "analyze_cadence_gap_sensitivity_r1.py" in r1_text,
        "historical R1 runner is not bound to preserved R1 analyzer",
    )
    require("S3X_GAP_SENSITIVITY_001.csv" in r1_text, "historical R1 output name drift")

    r2_text = runner_r2.read_text(encoding="utf-8")
    require(
        "analyze_cadence_gap_sensitivity.py" in r2_text,
        "R2 runner is not bound to corrected analyzer",
    )
    for marker in (
        "S3X_GAP_SENSITIVITY_002.csv",
        "S3X_DELTA_FREQUENCIES_002.csv",
        "S3X_GAP_SENSITIVITY_SUMMARY_002.json",
        "gap_rule_selection=NO",
        "trace_extraction=NO",
        "recovery_policy_execution=NO",
        "scientific_execution=NO",
    ):
        require(marker in r2_text, f"R2 runner missing marker: {marker}")

    for runner in (runner_r1, runner_r2):
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
            f"shell syntax invalid for {runner.name}: {shell_check.stderr.strip()}",
        )

    for forbidden in (
        S3X / "results",
        S3X / "canonical",
        S3X / "traces",
    ):
        require(
            not forbidden.exists(),
            f"forbidden S3X scientific path exists: {forbidden.relative_to(ROOT)}",
        )

    print("paper2_phase5a_sensitivity_output_fix_audit=PASS")
    print("r1_evidence_bound=YES")
    print("output_schema_collision_fixed=YES")
    print("csv_sha256_binding_required=YES")
    print("gap_rule_selection=NO")
    print("gap_rule_freeze=NO")
    print("trace_extraction=NO")
    print("recovery_policy_execution=NO")
    print("scientific_execution=NO")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
