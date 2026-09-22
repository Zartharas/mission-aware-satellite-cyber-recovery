#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from study7e.src.aerc_design import (
    FAULT_PROFILES,
    TOPOLOGY_SEPARATION,
    build_scenario_manifest,
    manifest_counts,
)


class ValidationError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationError(message)


def load_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(value, dict), f"{path} must contain a JSON object")
    return value


def main() -> int:
    protocol = load_json(ROOT / "study7e/PROTOCOL_DRAFT.json")
    state = load_json(ROOT / "study7e/IMPLEMENTATION_STATE.json")
    topologies = load_json(ROOT / "study7e/configs/topologies.json")
    faults = load_json(ROOT / "study7e/configs/fault_profiles.json")
    policy = load_json(ROOT / "study7e/configs/policy_contracts.json")
    env = load_json(ROOT / "study7e/configs/candidate_environment.json")

    require(protocol["experiment_id"] == "S7E-AERC-001", "protocol experiment id drift")
    require("NOT_FROZEN" in protocol["state"], "draft protocol unexpectedly frozen")
    require(protocol["execution_gate"]["canonical_execution_authorized"] is False, "protocol prematurely authorizes execution")
    require(state["canonical_scientific_execution_authorized"] is False, "implementation state prematurely authorizes execution")
    require(state["canonical_results_generated"] is False, "implementation state claims canonical results")
    require(state["production_models_frozen"] is False, "production models prematurely frozen")

    auth = ROOT / "study7e/CANONICAL_EXECUTION_AUTHORIZATION.json"
    require(not auth.exists(), "canonical execution authorization file must not exist in implementation phase")

    canonical_workflow = ROOT / ".github/workflows/study7e-canonical-execution.yml"
    require(not canonical_workflow.exists(), "canonical execution workflow must not exist in implementation phase")

    results_dir = ROOT / "study7e/results"
    if results_dir.exists():
        require(not any(results_dir.rglob("*")), "canonical results directory must be absent or empty")

    require(set(topologies["topologies"]) == set(TOPOLOGY_SEPARATION), "topology config/code drift")
    require(set(faults["profiles"]) == set(FAULT_PROFILES), "fault config/code drift")

    counts = manifest_counts(build_scenario_manifest())
    expected = protocol["expected_counts"]
    require(counts["TOTAL"] == expected["total_manifest_scenarios"] == 260, "manifest total drift")
    require(counts["TR"] == expected["training_scenarios"] == 72, "training count drift")
    require(counts["CANONICAL_EVAL_SCENARIOS"] == expected["canonical_evaluation_scenarios"] == 188, "evaluation count drift")
    require(counts["CANONICAL_EVAL_POLICY_DECISIONS"] == expected["canonical_evaluation_policy_decisions"] == 752, "decision count drift")

    require(len(policy["base_features"]) == 9, "base feature count drift")
    require(len(policy["corroborated_additional_features"]) == 7, "corroborated feature count drift")
    require(env["cfs"]["tag_commit"] == "088b2fa828db9ff7e00733f1908e0eeb59f66ce3", "cFS candidate commit drift")
    require(env["nos3"]["tag_commit"] == "5a3bdee6be9a2c67fdf994ae6db56d5c60395302", "NOS3 candidate commit drift")
    require(env["state"] == "CANDIDATE_BASELINES__NOT_CANONICAL_FREEZE", "environment candidate state drift")

    print("Study 7E pre-canonical implementation validation: PASS")
    print("experiment_id=S7E-AERC-001")
    print("manifest_total=260")
    print("training_scenarios=72")
    print("canonical_evaluation_scenarios=188")
    print("planned_evaluation_decisions=752")
    print("canonical_execution_authorized=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
