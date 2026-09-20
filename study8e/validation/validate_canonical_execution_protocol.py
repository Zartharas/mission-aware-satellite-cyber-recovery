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
    runner = load(root / "study8e/CANONICAL_RUNNER_FREEZE_003.json")
    retirement = load(root / "study8e/CANONICAL_TRIGGER_RETIREMENT_001.json")

    require(protocol["protocol_id"] == "S8E-CANON-EXEC-001", "protocol id drift")
    require(protocol["frozen_inputs"]["population_freeze"] == population["freeze_id"], "population mismatch")
    require(protocol["frozen_inputs"]["trace_freeze"] == trace["freeze_id"], "trace mismatch")
    require(protocol["frozen_inputs"]["implementation_freeze"] == impl["freeze_id"], "implementation mismatch")
    require(protocol["runner_freeze"] == runner["freeze_id"] == "S8E-CANON-RUNNER-003", "runner freeze mismatch")
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

    require(runner["defect_record"] == "S8E-CANON-RUNNER-DEFECT-001", "runner defect record drift")
    require("Syntax-only repair" in runner["repair_scope"], "runner repair scope drift")
    require(runner["files"]["study8e/analysis/run_canonical_execution.py"]["git_blob_sha1"] == "4d31d3eab64b96711f59024f458ab5236078b0b1", "canonical runner blob drift")
    require(runner["files"]["study8e/tests/test_canonical_execution_runner.py"]["git_blob_sha1"] == "d7e3f841b7ff1270656d022eb3910b77c17c1305", "canonical runner test blob drift")
    require(runner["files"][".github/workflows/study8e-canonical-execution.yml"]["git_blob_sha1"] == "8d08b8818df1cabec24ef4055ad64f67e703916e", "canonical workflow blob drift")
    require(runner["execution_state"]["canonical_workflow_dispatch_runs_before_freeze"] == 0, "runner freeze dispatch state drift")
    require(runner["execution_state"]["real_trace_scientific_endpoints_computed"] is False, "runner freeze endpoint state drift")
    require(runner["execution_state"]["current_authorization_allows_execution"] is False, "runner freeze improperly authorizes dispatch")

    workflow = (root / ".github/workflows/study8e-canonical-execution.yml").read_text(encoding="utf-8")
    require("authorization_id:" in workflow, "workflow authorization_id input missing")
    require("CANONICAL_EXECUTION_GO_LIVE.json" in workflow, "workflow go-live gate missing")
    require("canonical_execution_authorized" in workflow, "workflow go-live boolean check missing")

    require(retirement["status"] == "STALE_ONE_TIME_DISPATCH_PATH_RETIRED_BEFORE_CANONICAL_SCIENTIFIC_EXECUTION", "stale trigger retirement status drift")
    require(retirement["historical_dispatch"]["workflow_run"] == 35525450194, "historical dispatch run drift")
    require(retirement["historical_dispatch"]["conclusion"] == "failure", "historical dispatch conclusion drift")
    require(retirement["historical_dispatch"]["canonical_runner_compile_status"] == "FAIL", "historical dispatch compile state drift")
    require(retirement["historical_dispatch"]["scientific_endpoint_computed"] is False, "historical dispatch scientific endpoint state drift")
    require(retirement["current_authoritative_execution_path"]["runner_freeze"] == "S8E-CANON-RUNNER-003", "retirement runner authority drift")
    require(retirement["current_authoritative_execution_path"]["canonical_execution_currently_authorized"] is False, "retirement improperly authorizes execution")

    stale_bridge = root / ".github/workflows/study8e-canonical-dispatch-bridge.yml"
    stale_trigger = root / "study8e/CANONICAL_EXECUTION_TRIGGER_001.json"
    require(not stale_bridge.exists(), "stale canonical dispatch bridge still present")
    require(not stale_trigger.exists(), "stale canonical execution trigger still present")

    go_live_path = root / "study8e/CANONICAL_EXECUTION_GO_LIVE.json"
    go_live = None
    if go_live_path.exists():
        go_live = load(go_live_path)
        require(go_live["schema"] == 1, "go-live schema drift")
        require(go_live["experiment_id"] == "S8E-ECTV-001", "go-live experiment drift")
        require(go_live["authorization_id"] == "S8E-CANON-GOLIVE-001", "go-live authorization id drift")
        require(go_live["status"] == "AUTHORIZED", "go-live status drift")
        require(go_live["canonical_execution_authorized"] is True, "go-live execution authorization missing")
        require(go_live["authorized_pre_go_live_main"] == "a19a2d1dbfd5735a3053da46c822e7a1438f752b", "go-live pre-authorization main drift")
        require(go_live["protocol_id"] == protocol["protocol_id"], "go-live protocol mismatch")
        require(go_live["runner_freeze"] == runner["freeze_id"], "go-live runner mismatch")
        require(go_live["population_freeze"] == population["freeze_id"], "go-live population mismatch")
        require(go_live["trace_freeze"] == trace["freeze_id"], "go-live trace mismatch")
        require(go_live["implementation_freeze"] == impl["freeze_id"], "go-live implementation mismatch")
        frozen = go_live["frozen_input_identity"]
        require(frozen["trace_artifact_workflow_run"] == protocol["frozen_inputs"]["trace_artifact_workflow_run"], "go-live trace workflow mismatch")
        require(frozen["trace_artifact_id"] == protocol["frozen_inputs"]["trace_artifact_id"], "go-live trace artifact mismatch")
        require(frozen["trace_artifact_zip_sha256"] == protocol["frozen_inputs"]["trace_artifact_zip_sha256"], "go-live trace ZIP mismatch")
        require(frozen["trace_manifest_sha256"] == protocol["frozen_inputs"]["trace_manifest_sha256"], "go-live manifest mismatch")
        require(frozen["trace_jsonl_sha256"] == protocol["frozen_inputs"]["trace_jsonl_sha256"], "go-live JSONL mismatch")
        require(frozen["trace_records"] == protocol["frozen_inputs"]["trace_records"] == 476, "go-live trace record mismatch")
        require(frozen["trace_pairs"] == protocol["frozen_inputs"]["trace_pairs"] == 20, "go-live trace pair mismatch")
        require(frozen["canonical_runner_git_blob_sha1"] == runner["files"]["study8e/analysis/run_canonical_execution.py"]["git_blob_sha1"], "go-live runner blob mismatch")
        require(frozen["canonical_runner_test_git_blob_sha1"] == runner["files"]["study8e/tests/test_canonical_execution_runner.py"]["git_blob_sha1"], "go-live runner test blob mismatch")
        require(frozen["canonical_workflow_git_blob_sha1"] == runner["files"][".github/workflows/study8e-canonical-execution.yml"]["git_blob_sha1"], "go-live workflow blob mismatch")
        require(frozen["study8e_primary_model_git_blob_sha1"] == protocol["frozen_inputs"]["implementation_primary_git_blob_sha1"], "go-live primary model blob mismatch")
        require(frozen["study8e_independent_reference_git_blob_sha1"] == protocol["frozen_inputs"]["implementation_reference_git_blob_sha1"], "go-live reference model blob mismatch")
        require(go_live["authorized_scope"]["real_TRACE002_timing_endpoint_computation"] is True, "go-live timing endpoint scope missing")
        require(go_live["authorized_scope"]["minimum_rate_threshold_computation"] is True, "go-live minimum-rate scope missing")
        require(go_live["authorized_scope"]["independent_case_level_audit"] is True, "go-live independent audit scope missing")
        require(go_live["authorized_scope"]["deterministic_second_execution"] is True, "go-live deterministic repeat scope missing")
        require(go_live["authorized_scope"]["canonical_result_artifact_upload"] is True, "go-live artifact-upload scope missing")
        require(go_live["still_not_authorized"]["source_api_requery_or_rematerialization"] is True, "go-live source re-query guard missing")
        require(go_live["still_not_authorized"]["modify_TRACE002_rows"] is True, "go-live TRACE-002 mutation guard missing")
        require(go_live["still_not_authorized"]["modify_frozen_Study8"] is True, "go-live Study 8 mutation guard missing")
        require(go_live["still_not_authorized"]["alter_runner_or_model_during_execution"] is True, "go-live runner mutation guard missing")
        require(go_live["result_merge_authorization"] is False, "go-live improperly authorizes result merge")
        require(go_live["manuscript_integration_authorization"] is False, "go-live improperly authorizes manuscript integration")
        require(go_live["publisher_submission_authorization"] is False, "go-live improperly authorizes publisher submission")

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
    print("runner_freeze=S8E-CANON-RUNNER-003")
    print("cases_per_anchor=144")
    print("historical_failed_canonical_dispatch_run=35525450194")
    print("historical_failed_dispatch_scientific_endpoint_computed=false")
    print("real_trace_execution_authorized=" + ("true" if go_live is not None else "false"))
    print("go_live_artifact_present=" + ("true" if go_live is not None else "false"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
