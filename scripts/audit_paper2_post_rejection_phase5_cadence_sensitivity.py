#!/usr/bin/env python3
"""Fail-closed audit for Paper-2 Phase-5 S3X cadence sensitivity tooling."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
S3X = ROOT / "study3x"
REBUILD = ROOT / "publication/Paper_2_Studies_3_4_6/Post_Rejection_Rebuild"

EXPECTED_RULES = {
    "P99_X1",
    "P99_X2",
    "P99_X3",
    "P99_X5",
    "P99_X10",
    "MAX_P99_MEDIAN_X2",
    "MAX_P99_MEDIAN_X3",
    "MAX_P99_MEDIAN_X5",
}


def fail(message: str) -> None:
    print(f"[FAIL] {message}", file=sys.stderr)
    raise SystemExit(1)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def main() -> int:
    status_path = REBUILD / "PAPER2_PHASE5_CADENCE_SENSITIVITY_STATUS.json"
    gate_path = REBUILD / "PHASE5_CADENCE_SENSITIVITY_GATE_R1_2026-09-26.md"
    analyzer = S3X / "validation/analyze_cadence_gap_sensitivity.py"
    runner = S3X / "validation/run_local_gap_sensitivity.sh"
    regression = ROOT / "tests/test_s3x_gap_sensitivity.py"

    for path in (status_path, gate_path, analyzer, runner, regression):
        require(path.is_file(), f"required Phase-5 file missing: {path.relative_to(ROOT)}")

    status = json.loads(status_path.read_text(encoding="utf-8"))
    require(
        status.get("status")
        == "AUTHORIZED_READ_ONLY_SENSITIVITY_TOOLING__AWAITING_LOCAL_EXECUTION",
        "unexpected Phase-5 status",
    )
    authorized = status.get("authorized", {})
    require(authorized.get("read_only_cadence_analysis") is True, "read-only analysis not authorized")
    require(authorized.get("candidate_threshold_sensitivity") is True, "threshold sensitivity not authorized")

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
        require(prohibited.get(key) is True, f"closed gate not recorded: {key}")

    require(set(status.get("candidate_rules", [])) == EXPECTED_RULES, "candidate-rule set drift")

    analyzer_text = analyzer.read_text(encoding="utf-8")
    for marker in (
        "READ_ONLY_CADENCE_GAP_SENSITIVITY",
        "candidate thresholds are sensitivity diagnostics, not selected gap rules",
        '"gap_rule_selected": False',
        '"gap_rule_frozen": False',
        '"timestamp_level_gap_traces_emitted": False',
        '"recovery_policy_execution_performed": False',
        '"scientific_results_generated": False',
        "SHA-256 mismatch",
    ):
        require(marker in analyzer_text, f"analyzer missing safety marker: {marker}")

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
        f"runner shell syntax invalid: {shell_check.stderr.strip()}",
    )

    runner_text = runner.read_text(encoding="utf-8")
    for marker in (
        "S3X_GAP_SENSITIVITY_001.csv",
        "S3X_DELTA_FREQUENCIES_001.csv",
        "S3X_GAP_SENSITIVITY_SUMMARY_001.json",
        "gap_rule_selection=NO",
        "trace_extraction=NO",
        "recovery_policy_execution=NO",
        "scientific_execution=NO",
    ):
        require(marker in runner_text, f"runner missing safety marker: {marker}")

    for forbidden in (
        S3X / "results",
        S3X / "canonical",
        S3X / "traces",
    ):
        require(
            not forbidden.exists(),
            f"forbidden S3X scientific path exists: {forbidden.relative_to(ROOT)}",
        )

    print("paper2_phase5_cadence_sensitivity_tooling_audit=PASS")
    print("read_only_cadence_analysis=YES")
    print("gap_rule_selection=NO")
    print("gap_rule_freeze=NO")
    print("trace_extraction=NO")
    print("recovery_policy_execution=NO")
    print("scientific_execution=NO")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
