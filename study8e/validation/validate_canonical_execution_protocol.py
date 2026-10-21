#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
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


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()
    root = args.root

    protocol = load(root / "study8e/CANONICAL_EXECUTION_PROTOCOL_001.json")
    original_auth = load(root / "study8e/CANONICAL_EXECUTION_AUTHORIZATION_20260920.json")
    auth_correction = load(root / "study8e/CANONICAL_EXECUTION_AUTHORIZATION_CORRECTION_20260920.json")
    population = load(root / "study8e/SATNOGS_POPULATION_FREEZE_002.json")
    trace = load(root / "study8e/SATNOGS_TRACE_ARTIFACT_FREEZE_002.json")
    implementation = load(root / "study8e/IMPLEMENTATION_FREEZE_001.json")
    retirement = load(root / "study8e/CANONICAL_TRIGGER_RETIREMENT_001.json")
    runner = load(root / "study8e/CANONICAL_RUNNER_FREEZE_004.json")
    bound_defect = load(root / "study8e/CANONICAL_BOUND_DEFECT_001.json")
    result_invalidation = load(root / "study8e/CANONICAL_RESULTS_001_INVALIDATION.json")
    go_live_001 = load(root / "study8e/CANONICAL_EXECUTION_GO_LIVE.json")
    go_live_001_closeout = load(root / "study8e/CANONICAL_EXECUTION_GO_LIVE_001_CLOSEOUT.json")
    activation_001 = load(root / "study8e/CANONICAL_EXECUTION_ACTIVATION_001.json")

    require(protocol["experiment_id"] == "S8E-ECTV-001", "protocol experiment drift")
    require(protocol["protocol_id"] == "S8E-CANON-EXEC-001", "protocol id drift")
    require(protocol["frozen_inputs"]["population_freeze"] == population["freeze_id"] == "S8E-SATNOGS-POP-002", "population mismatch")
    require(protocol["frozen_inputs"]["trace_freeze"] == trace["freeze_id"] == "S8E-SATNOGS-TRACE-002", "trace mismatch")
    require(protocol["frozen_inputs"]["implementation_freeze"] == implementation["freeze_id"] == "S8E-IMPLFREEZE-001", "implementation mismatch")
    require(protocol["frozen_inputs"]["trace_records"] == trace["corpus"]["records"] == 476, "trace record drift")
    require(protocol["frozen_inputs"]["trace_pairs"] == trace["corpus"]["pairs"] == 20, "trace pair drift")
    require(protocol["frozen_inputs"]["trace_jsonl_sha256"] == trace["corpus"]["canonical_jsonl"]["sha256"], "trace JSONL hash drift")
    require(protocol["runner_freeze"] == runner["freeze_id"] == "S8E-CANON-RUNNER-004", "runner freeze mismatch")

    grid = protocol["factor_grid"]
    expected = (
        len(grid["horizons_hours"])
        * len(grid["profiles"])
        * len(grid["policies"])
        * len(grid["disruptions"])
    )
    require(grid["horizons_hours"] == [6, 12, 24], "horizon grid drift")
    require(expected == grid["cases_per_anchor"] == 144, "case grid drift")

    bound = protocol["minimum_rate_endpoint"]["sufficient_upper_bound"]
    require("floor(8 * B / d_min) + 1" in bound["formula"], "strict upper-bound formula drift")
    require("strictly greater than 8B/d_min" in bound["rationale"], "strict-bound rationale drift")
    require("not a physical link capacity" in bound["interpretation_guard"], "bound interpretation guard missing")
    postconditions = protocol["minimum_rate_endpoint"]["postconditions"]
    require(any("independently reimplemented strict sufficient upper bounds" in item for item in postconditions), "independent bound postcondition missing")
    require(protocol["minimum_rate_endpoint"]["no_arbitrary_fixed_rate_cap"] is True, "arbitrary fixed cap introduced")

    require(bound_defect["defect_id"] == "S8E-CANON-BOUND-DEFECT-001", "bound defect record drift")
    require(bound_defect["status"] == "SCIENTIFIC_PROTOCOL_DEFECT_DETECTED_AFTER_EXECUTION_BEFORE_RESULT_FREEZE", "bound defect status drift")
    require(bound_defect["post_run_audit"]["nonfinite_recovery_deadline_exceeded_at_bound"] == 24, "known affected case count drift")
    require(bound_defect["exact_regression_example"]["prior_bound_bps"] == 23968, "old regression bound drift")
    require(bound_defect["exact_regression_example"]["corrected_bound_bps"] == 23969, "corrected regression bound drift")

    require(result_invalidation["record_id"] == "S8E-CANON-RESULTS-001-INVALIDATION", "result invalidation id drift")
    require(result_invalidation["status"] == "INVALIDATED_BEFORE_RESULT_FREEZE", "result invalidation status drift")
    require(result_invalidation["canonical_run"]["workflow_run"] == 35529423881, "invalidated workflow run drift")
    require(result_invalidation["canonical_run"]["artifact_id"] == 10610543345, "invalidated artifact id drift")
    require(result_invalidation["canonical_run"]["artifact_zip_sha256"] == "18fd00a0370cb49395af6d1df0b84c02ed9e905cf66ad58d7b2da3579df7d04c", "invalidated artifact hash drift")
    require(result_invalidation["known_scientific_effect"]["known_misclassified_nonfinite_case_count"] == 24, "misclassified case count drift")
    require(result_invalidation["known_scientific_effect"]["result_freeze_permitted"] is False, "invalidated result freeze enabled")

    require(go_live_001["authorization_id"] == "S8E-CANON-GOLIVE-001", "historical go-live 001 drift")
    require(go_live_001_closeout["record_id"] == "S8E-CANON-GOLIVE-001-CLOSEOUT", "go-live 001 closeout drift")
    require(go_live_001_closeout["status"] == "CONSUMED__EXECUTION_COMPLETED__RESULT_INVALIDATED_BEFORE_FREEZE", "go-live 001 closeout status drift")
    require(go_live_001_closeout["canonical_workflow_run"] == 35529423881, "go-live 001 run drift")
    require(go_live_001_closeout["reusable_for_reexecution"] is False, "go-live 001 improperly reusable")
    require(go_live_001_closeout["new_go_live_required_for_reexecution"] is True, "new go-live requirement missing")
    require(activation_001["activation_id"] == "S8E-CANON-ACTIVATE-001", "historical activation drift")
    require(activation_001["authorization_id"] == "S8E-CANON-GOLIVE-001", "historical activation authorization drift")

    require(retirement["record_id"] == "S8E-CANON-TRIGGER-RETIREMENT-001", "retirement record drift")
    require(not (root / ".github/workflows/study8e-canonical-dispatch-bridge.yml").exists(), "stale dispatch bridge returned")
    require(not (root / "study8e/CANONICAL_EXECUTION_TRIGGER_001.json").exists(), "stale trigger returned")

    require(original_auth["authorized"]["canonical_execution_after_protocol_merge"] is False, "historical auth correction lost")
    require(auth_correction["status"] == "AUTHORIZATION_SCOPE_CORRECTED_BEFORE_CANONICAL_EXECUTION", "auth correction drift")

    runner_files = runner["files"]
    for rel_path, meta in runner_files.items():
        require(git_blob_sha1(root / rel_path) == meta["git_blob_sha1"], f"runner blob drift: {rel_path}")
    require(runner["defect_record"] == "S8E-CANON-BOUND-DEFECT-001", "runner defect binding drift")
    require(runner["execution_gate"]["required_go_live_file"] == "study8e/CANONICAL_EXECUTION_GO_LIVE_002.json", "runner go-live path drift")
    require(runner["execution_gate"]["expected_authorization_id"] == "S8E-CANON-GOLIVE-002", "runner authorization id drift")
    require(runner["execution_gate"]["reexecution_authorized_now"] is False, "runner prematurely authorizes reexecution")

    workflow_text = (root / ".github/workflows/study8e-canonical-execution.yml").read_text(encoding="utf-8")
    require("CANONICAL_EXECUTION_GO_LIVE_002.json" in workflow_text, "workflow go-live 002 gate missing")
    require("S8E-CANON-RUNNER-004" in workflow_text, "workflow runner 004 gate missing")
    require("study8e-canonical-results-002" in workflow_text, "workflow results-002 artifact name missing")
    require("independent_canonical_bound.py" in workflow_text, "workflow independent bound compile missing")

    current_go_live_path = root / "study8e/CANONICAL_EXECUTION_GO_LIVE_002.json"
    current_activation_path = root / "study8e/CANONICAL_EXECUTION_ACTIVATION_002.json"
    current_go_live = None
    if current_go_live_path.exists():
        current_go_live = load(current_go_live_path)
        require(current_go_live["authorization_id"] == "S8E-CANON-GOLIVE-002", "go-live 002 id drift")
        require(current_go_live["status"] == "AUTHORIZED", "go-live 002 status drift")
        require(current_go_live["canonical_execution_authorized"] is True, "go-live 002 missing execution authorization")
        require(current_go_live["protocol_id"] == protocol["protocol_id"], "go-live 002 protocol drift")
        require(current_go_live["runner_freeze"] == runner["freeze_id"], "go-live 002 runner drift")
    else:
        require(not current_activation_path.exists(), "activation 002 exists before go-live 002")

    prohibited_results = [
        root / "study8e/results/CANONICAL_CASE_RESULTS.csv",
        root / "study8e/results/CANONICAL_FINDINGS.json",
        root / "study8e/results/INDEPENDENT_AUDIT.json",
        root / "study8e/results/RESULTS_HASH_MANIFEST.json",
    ]
    require(not any(path.exists() for path in prohibited_results), "canonical result file committed before result freeze")

    require(protocol["execution_authorization_gate"]["merged_go_live_authorization_artifact_required"] == "study8e/CANONICAL_EXECUTION_GO_LIVE_002.json", "protocol current go-live path drift")
    require(protocol["execution_authorization_gate"]["real_trace_execution_allowed_by_current_authorization"] is False, "protocol prematurely authorizes reexecution")
    require(protocol["execution_authorization_gate"]["scientific_endpoint_computation_before_go_live"] == "PROHIBITED", "pre-go-live endpoint guard drift")

    print("Study 8E canonical strict-bound repair governance validation: PASS")
    print("protocol_id=S8E-CANON-EXEC-001")
    print("runner_freeze=S8E-CANON-RUNNER-004")
    print("invalidated_results=S8E-CANON-RESULTS-001")
    print("known_bound_misclassifications=24")
    print("current_go_live_002_present=" + ("true" if current_go_live is not None else "false"))
    print("real_trace_reexecution_authorized=" + ("true" if current_go_live is not None else "false"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
