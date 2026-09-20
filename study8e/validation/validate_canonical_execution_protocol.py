#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


class ValidationError(RuntimeError):
    pass


def load(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValidationError(f"{path} is not a JSON object")
    return value


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationError(message)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()
    root = args.root

    protocol = load(root / "study8e/CANONICAL_EXECUTION_PROTOCOL_001.json")
    auth = load(root / "study8e/CANONICAL_EXECUTION_AUTHORIZATION_20260920.json")
    correction = load(root / "study8e/CANONICAL_EXECUTION_AUTHORIZATION_CORRECTION_20260920.json")
    population = load(root / "study8e/SATNOGS_POPULATION_FREEZE_002.json")
    trace = load(root / "study8e/SATNOGS_TRACE_ARTIFACT_FREEZE_002.json")
    impl = load(root / "study8e/IMPLEMENTATION_FREEZE_001.json")
    runner = load(root / "study8e/CANONICAL_RUNNER_FREEZE_002.json")

    require(protocol["protocol_id"] == "S8E-CANON-EXEC-001", "protocol id drift")
    require(protocol["frozen_inputs"]["population_freeze"] == population["freeze_id"], "population mismatch")
    require(protocol["frozen_inputs"]["trace_freeze"] == trace["freeze_id"], "trace mismatch")
    require(protocol["frozen_inputs"]["implementation_freeze"] == impl["freeze_id"], "implementation mismatch")
    require(protocol["runner_freeze"] == runner["freeze_id"] == "S8E-CANON-RUNNER-002", "runner freeze mismatch")
    require(protocol["frozen_inputs"]["trace_records"] == trace["corpus"]["records"] == 476, "trace record count drift")
    require(protocol["frozen_inputs"]["trace_pairs"] == trace["corpus"]["pairs"] == 20, "trace pair count drift")
    require(
        protocol["frozen_inputs"]["trace_jsonl_sha256"] == trace["corpus"]["canonical_jsonl"]["sha256"],
        "trace JSONL hash drift",
    )

    grid = protocol["factor_grid"]
    expected = (
        len(grid["horizons_hours"])
        * len(grid["profiles"])
        * len(grid["policies"])
        * len(grid["disruptions"])
    )
    require(grid["horizons_hours"] == [6, 12, 24], "horizon grid drift")
    require(expected == grid["cases_per_anchor"] == 144, "case grid must remain 144 per anchor")

    gate = protocol["execution_authorization_gate"]
    require(gate["protocol_and_runner_governance_merge_required"] is True, "merge gate disabled")
    require(gate["post_merge_repository_validation_required"] is True, "post-merge validation gate disabled")
    require(gate["separate_explicit_author_execution_authorization_required"] is True, "separate execution authorization disabled")
    require(gate["real_trace_execution_allowed_by_current_authorization"] is False, "current protocol incorrectly permits execution")
    require(gate["scientific_endpoint_computation_before_go_live"] == "PROHIBITED", "pre-go-live endpoint prohibition drift")
    require(gate["merged_go_live_authorization_artifact_required"] == "study8e/CANONICAL_EXECUTION_GO_LIVE.json", "go-live artifact path drift")

    require(auth["authorized"]["canonical_execution_after_protocol_merge"] is False, "authorization improperly permits execution")
    for key in (
        "real_TRACE002_timing_endpoint_computation",
        "real_TRACE002_minimum_rate_endpoint_computation",
        "policy_profile_disruption_scientific_execution",
        "canonical_result_freeze",
    ):
        require(auth["not_authorized"][key] is True, f"{key} must remain not authorized")

    require(correction["status"] == "AUTHORIZATION_SCOPE_CORRECTED_BEFORE_CANONICAL_EXECUTION", "authorization correction status drift")
    require(correction["execution_state_at_correction"]["canonical_workflow_dispatch_runs"] == 0, "correction no-dispatch evidence drift")
    require(correction["execution_state_at_correction"]["canonical_real_trace_scientific_endpoints_computed"] is False, "correction endpoint state drift")

    require(runner["scientific_runner_unchanged"] is True, "scientific runner unexpectedly changed")
    require(runner["files"]["study8e/analysis/run_canonical_execution.py"]["git_blob_sha1"] == "ae6b24a3573eab9d2e59f6c7b149412a76bf4f6c", "canonical runner blob drift")
    require(runner["files"]["study8e/tests/test_canonical_execution_runner.py"]["git_blob_sha1"] == "d7e3f841b7ff1270656d022eb3910b77c17c1305", "canonical runner test blob drift")
    require(runner["files"][".github/workflows/study8e-canonical-execution.yml"]["git_blob_sha1"] == "6bb59909a6db5a2c497c815efd02afb1e12919ca", "canonical workflow blob drift")
    require(runner["current_execution_state"]["canonical_workflow_dispatch_runs"] == 0, "runner freeze dispatch state drift")
    require(runner["current_execution_state"]["real_trace_scientific_endpoints_computed"] is False, "runner freeze endpoint state drift")
    require(runner["current_execution_state"]["current_authorization_allows_dispatch"] is False, "runner freeze improperly authorizes dispatch")

    workflow = (root / ".github/workflows/study8e-canonical-execution.yml").read_text(encoding="utf-8")
    require("authorization_id:" in workflow, "workflow authorization_id input missing")
    require("CANONICAL_EXECUTION_GO_LIVE.json" in workflow, "workflow go-live gate missing")
    require("canonical_execution_authorized" in workflow, "workflow go-live boolean check missing")

    go_live = root / "study8e/CANONICAL_EXECUTION_GO_LIVE.json"
    require(not go_live.exists(), "go-live artifact must not exist before explicit canonical execution authorization")

    prohibited_results = [
        root / "study8e/results/CANONICAL_CASE_RESULTS.csv",
        root / "study8e/results/CANONICAL_FINDINGS.json",
        root / "study8e/results/INDEPENDENT_AUDIT.json",
        root / "study8e/results/RESULTS_HASH_MANIFEST.json",
    ]
    require(not any(path.exists() for path in prohibited_results), "canonical scientific result artifact exists before authorization")

    coverage = protocol["trace_preparation"]["forward_coverage_proof"]
    require("older" in coverage["implication"], "forward-coverage proof missing older-page property")
    require("not a complete backward history" in coverage["boundary"], "backward-history limitation missing")

    minimum_rate = protocol["minimum_rate_endpoint"]
    require(minimum_rate["lower_bound_bps"] == 1, "threshold lower bound drift")
    require(minimum_rate["no_arbitrary_fixed_rate_cap"] is True, "arbitrary fixed rate cap introduced")
    require("not a physical link capacity" in minimum_rate["sufficient_upper_bound"]["interpretation_guard"], "upper-bound interpretation guard missing")

    print("Study 8E canonical execution governance validation: PASS")
    print("protocol_id=S8E-CANON-EXEC-001")
    print("runner_freeze=S8E-CANON-RUNNER-002")
    print("cases_per_anchor=144")
    print("canonical_workflow_dispatch_runs_recorded=0")
    print("real_trace_execution_authorized=false")
    print("go_live_artifact_present=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
