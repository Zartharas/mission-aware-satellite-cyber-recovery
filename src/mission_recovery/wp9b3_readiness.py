from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

from .wp9_static_contracts import (
    build_static_matrix,
    build_wp9_run_schema,
    load_campaign_design,
    validate_wp9_static_contract,
)

ROOT = Path(__file__).resolve().parents[2]
CELL_IDS = tuple(f"A{i:02d}" for i in range(1, 25))

ENDPOINT_SOURCES = {
    "effective_policy_id": "execution_metadata.effective_policy_id",
    "unauthorized_effect_completed": "outcomes.unauthorized_effect_completed",
    "mission_objective_completion_ratio": "outcomes.mission_objective_completion_ratio",
    "safety_invariant_violation_count": "raw_metric_evidence.invariant_violation_intervals",
    "legitimate_command_rejection_rate": "outcomes.legitimate_command_rejection_rate",
    "time_to_containment_s": "timing.containment_s+raw_metric_evidence.containment",
    "time_to_verified_recovery_s": "timing.verified_recovery_s+raw_metric_evidence.trusted_recovery",
    "ground_spacecraft_state_divergence_s": "outcomes.ground_spacecraft_state_divergence_s",
    "recovery_terminal_state": "terminal_state",
    "evidence_completeness_ratio": "outcomes.evidence_completeness_ratio",
    "residual_unauthorized_state_count": "outcomes.residual_unauthorized_state_count",
}

ROUTE_SOURCES = {
    "e1_command_gateway": (
        "scripts/run_wp8_command_stage1_development.sh",
        "src/mission_recovery/wp8_command_runtime_executor.py",
        "tests/test_wp8_command_runtime_executor.py",
    ),
    "e3_command_gateway": (
        "scripts/run_wp9b2_e3_fixed_development.sh",
        "src/mission_recovery/wp9b2_e3_fixed_development.py",
        "tests/test_wp9b2_e3_fixed_development.py",
    ),
    "e3_trusted_recovery": (
        "scripts/run_wp8_recovery_binding_preflight.sh",
        "src/mission_recovery/wp8_recovery_runtime_executor.py",
        "tests/test_wp8_recovery_runtime_executor.py",
    ),
    "e3_trusted_recovery_reduced_evidence": (
        "scripts/run_wp9b2_e3_fixed_development.sh",
        "src/mission_recovery/wp9b2_e3_fixed_development.py",
        "tests/test_wp9b2_e3_fixed_development.py",
    ),
    "e3_ground_authorized_recovery": (
        "scripts/run_wp9b2_p6_development.sh",
        "src/mission_recovery/wp9b2_p6_development.py",
        "tests/test_wp9b2_p6_development.py",
    ),
    "e3_trusted_recovery_contact_delay": (
        "scripts/run_wp8_recovery_binding_preflight.sh",
        "src/mission_recovery/wp9_static_contracts.py",
        "tests/test_wp8_stage1_runtime_wiring.py",
    ),
    "e2_replay_effect": (
        "scripts/run_wp9b2_e2_development.sh",
        "src/mission_recovery/wp9b2_development.py",
        "tests/test_wp9b2_development.py",
    ),
    "e4_observability": (
        "scripts/run_wp9b2_e4_fixed_development.sh",
        "scripts/run_wp8_observability_stage1_development.sh",
        "src/mission_recovery/wp9b2_e4_fixed_development.py",
        "tests/test_wp9b2_e4_fixed_development.py",
    ),
}

ISOLATION_RUNNER = {
    "e1_command_gateway": "scripts/run_wp8_command_stage1_development.sh",
    "e3_command_gateway": "scripts/run_wp9b2_e3_fixed_development.sh",
    "e3_trusted_recovery": "scripts/run_wp8_recovery_binding_preflight.sh",
    "e3_trusted_recovery_reduced_evidence": "scripts/run_wp9b2_e3_fixed_development.sh",
    "e3_ground_authorized_recovery": "scripts/run_wp9b2_p6_development.sh",
    "e3_trusted_recovery_contact_delay": "scripts/run_wp8_recovery_binding_preflight.sh",
    "e2_replay_effect": "scripts/run_wp9b2_e2_development.sh",
    "e4_observability": "scripts/run_wp9b2_e4_fixed_development.sh",
}

EXPECTED_FAMILY_BY_EVENT = {
    "E1": "command",
    "E2": "replay",
    "E3": "recovery",
    "E4": "observability",
}

RECOVERY_CRITERIA = (
    "approved_version",
    "integrity_measurement_valid",
    "authorization_valid",
    "measured_state_current",
    "authorized_command_path_restored",
    "ground_spacecraft_state_agreed",
    "required_telemetry_restored",
    "health_checks_passed",
    "no_residual_unauthorized_state",
    "recovery_manifest_complete",
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _require_sources(variant: str) -> tuple[str, ...]:
    if variant not in ROUTE_SOURCES:
        raise ValueError(f"unmapped WP9 runtime variant: {variant}")
    sources = ROUTE_SOURCES[variant]
    for rel in sources:
        path = ROOT / rel
        if not path.is_file():
            raise ValueError(f"runtime prerequisite missing: {rel}")
    return sources


def _validate_isolation_cleanup(variant: str) -> str:
    rel = ISOLATION_RUNNER[variant]
    text = (ROOT / rel).read_text(encoding="utf-8")
    required = (
        "set -Eeuo pipefail",
        "run_nominal_runtime_preflight.sh",
        "--network \"$NETWORK\"",
        "trap cleanup EXIT",
        "docker rm -f",
    )
    missing = [token for token in required if token not in text]
    if missing:
        raise ValueError(f"{variant}: isolation/cleanup tokens missing: {missing}")
    return rel


def _placeholder_record(row: dict[str, Any]) -> dict[str, Any]:
    factor = row["factor_context"]
    record: dict[str, Any] = {
        "run_id": f"wp9b3-readiness-{row['cell_id'].lower()}",
        "model_version": "0.4.0",
        "seed": 0,
        "mission_state_id": factor["mission_state_id"],
        "event_id": factor["event_id"],
        "policy_id": factor["policy_id"],
        "contact_condition_id": factor["contact_condition_id"],
        "evidence_condition_id": factor["evidence_condition_id"],
        "environment": {
            "host_architecture": "static-readiness",
            "simulator": "NOS3",
            "simulator_commit": "0000000",
            "flight_software": "cFS",
            "flight_software_commit": "0000000",
            "snapshot_id": "wp9b3-static-readiness",
            "container_or_vm_digest": None,
        },
        "timing": {
            "run_start_utc": "2026-01-01T00:00:00Z",
            "event_activation_s": 0.1,
            "containment_s": None,
            "verified_recovery_s": None,
            "run_end_utc": "2026-01-01T00:00:01Z",
        },
        "outcomes": {
            "unauthorized_effect_completed": False,
            "mission_objective_completion_ratio": 0.0,
            "safety_invariant_violations": [],
            "legitimate_command_rejection_rate": None,
            "ground_spacecraft_state_divergence_s": 0.0,
            "evidence_completeness_ratio": 0.0,
            "minimum_energy_reserve_ratio": None,
            "time_in_safe_mode_s": None,
            "time_in_degraded_mode_s": None,
            "contact_windows_consumed": 0,
            "residual_unauthorized_state_count": 0,
        },
        "recovery_evidence": {criterion: None for criterion in RECOVERY_CRITERIA},
        "raw_metric_evidence": {
            "event_success": {"predicate": False, "timestamp_s": None},
            "containment": {"predicate": False, "timestamp_s": None},
            "trusted_recovery": {"predicate": False, "timestamp_s": None},
            "objective_instances": [
                {
                    "objective_instance_id": "static-readiness-objective",
                    "weight": 1.0,
                    "scheduled_start_s": 0.0,
                    "scheduled_end_s": 1.0,
                    "completion_predicate": "runtime observation required",
                    "completion_evidence_ref": "runtime/required",
                    "completed": False,
                }
            ],
            "invariant_violation_intervals": [],
            "legitimate_commands": {"attempted": 0, "rejected": 0},
            "ground_spacecraft_divergence_intervals": [],
            "recovery_checklist": [
                {
                    "criterion_id": criterion,
                    "available_current": False,
                    "criterion_satisfied": False,
                    "evidence_ref": f"runtime/{criterion}",
                }
                for criterion in RECOVERY_CRITERIA
            ],
            "recovery_checklist_excluded": [],
            "run_end_s": 1.0,
            "terminal_state_predicates": {
                "run_invalid": False,
                "mission_loss": False,
                "trusted_recovery_confirmed": False,
                "operational_restored": False,
                "recovery_failed": True,
                "contained": False,
            },
        },
        "terminal_state": "RECOVERY_FAILED",
        "invalid_run_reason": None,
        "notes": "WP9-B3 schema-readiness placeholder; not runtime or campaign data.",
    }
    if factor["policy_id"] == "P6":
        c1 = factor["contact_condition_id"] == "C1"
        record["raw_metric_evidence"]["ground_authorization"] = {
            "required": True,
            "source": "synthetic_ground_authorization_schedule",
            "available_at_response_boundary": not c1,
            "available_timestamp_s": 1.0 if c1 else 0.0,
            "missed_contact_windows": 1 if c1 else 0,
            "authorization_current": True,
            "evidence_ref": "runtime/ground-authorization",
        }
    return record


def _validate_schema_compatibility(row: dict[str, Any], schema: dict[str, Any]) -> None:
    record = _placeholder_record(row)
    errors = sorted(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(record),
        key=lambda error: list(error.path),
    )
    if errors:
        detail = "; ".join(error.message for error in errors[:5])
        raise ValueError(f"{row['cell_id']}: WP9 run-schema readiness failed: {detail}")


def _validate_endpoint_sources(design: dict[str, Any]) -> None:
    endpoints = set()
    for contract in design["analysis_contracts"].values():
        endpoints.update(contract["primary_endpoints"])
    missing = sorted(endpoints - set(ENDPOINT_SOURCES))
    if missing:
        raise ValueError(f"analysis endpoints lack observed-data source: {missing}")
    if ENDPOINT_SOURCES["effective_policy_id"] != "execution_metadata.effective_policy_id":
        raise ValueError("effective policy must come from retained execution metadata")


def build_readiness_matrix() -> dict[str, Any]:
    validate_wp9_static_contract()
    design = load_campaign_design()
    _validate_endpoint_sources(design)
    schema = build_wp9_run_schema()
    static = build_static_matrix(design)

    if static["cell_ids"] != list(CELL_IDS):
        raise ValueError("WP9-B3 cell identity/order differs from A01-A24")

    rows = []
    for row in static["rows"]:
        cell_id = row["cell_id"]
        factor = row["factor_context"]
        expected_family = EXPECTED_FAMILY_BY_EVENT[factor["event_id"]]
        if row["runtime_family"] != expected_family:
            raise ValueError(f"{cell_id}: runtime family disagrees with event")
        if row["actual_effective_policy_id"] != row[
            "expected_effective_policy_id_for_acceptance_only"
        ]:
            raise ValueError(f"{cell_id}: effective-policy readiness mismatch")
        if row["oracle_ground_truth_read"] is not False:
            raise ValueError(f"{cell_id}: policy crossed immutable-truth oracle boundary")

        sources = _require_sources(row["runtime_variant"])
        isolation_runner = _validate_isolation_cleanup(row["runtime_variant"])
        _validate_schema_compatibility(row, schema)

        rows.append(
            {
                "cell_id": cell_id,
                "event_id": factor["event_id"],
                "mission_state_id": factor["mission_state_id"],
                "contact_condition_id": factor["contact_condition_id"],
                "evidence_condition_id": factor["evidence_condition_id"],
                "requested_policy_id": row["requested_policy_id"],
                "actual_effective_policy_id_static": row["actual_effective_policy_id"],
                "expected_effective_policy_id_for_acceptance_only": row[
                    "expected_effective_policy_id_for_acceptance_only"
                ],
                "runtime_family": row["runtime_family"],
                "runtime_variant": row["runtime_variant"],
                "runtime_prerequisite_sources": list(sources),
                "isolation_cleanup_source": isolation_runner,
                "raw_metric_schema_compatible": True,
                "effective_policy_observation_required": True,
                "effective_policy_observation_source": (
                    "retained_runtime_execution_metadata"
                ),
                "expected_effective_policy_used_as_metric_input": False,
                "ground_truth_policy_oracle_allowed": False,
                "campaign_execution_authorized": False,
                "campaign_seed_consumed": False,
                "campaign_data_generated": False,
            }
        )

    family_counts = dict(Counter(row["runtime_family"] for row in rows))
    expected_counts = {
        "command": 9,
        "recovery": 9,
        "replay": 3,
        "observability": 3,
    }
    if family_counts != expected_counts:
        raise ValueError(f"WP9-B3 runtime-family counts changed: {family_counts}")

    return {
        "schema": 1,
        "classification": "WP9B3_ALL_24_STATIC_READINESS_PASS",
        "cell_ids": list(CELL_IDS),
        "cell_count": 24,
        "runtime_family_counts": family_counts,
        "rows": rows,
        "all_analysis_endpoints_have_observed_data_sources": True,
        "all_cells_wp9_run_schema_compatible": True,
        "all_runtime_prerequisites_present": True,
        "all_isolation_cleanup_sources_present": True,
        "effective_policy_source": "retained_runtime_execution_metadata",
        "expected_values_role": "acceptance_only_not_metric_inputs",
        "static_seed": 0,
        "static_seed_role": "semantic_materialization_only_not_execution",
        "runtime_execution_performed": False,
        "campaign_seed_consumed": False,
        "campaign_data_generated": False,
        "repetition_count_frozen": False,
        "campaign_execution_authorized": False,
    }


def validate_readiness() -> dict[str, Any]:
    result = build_readiness_matrix()
    if result["cell_count"] != 24:
        raise ValueError("WP9-B3 requires all 24 cells")
    for key in (
        "runtime_execution_performed",
        "campaign_seed_consumed",
        "campaign_data_generated",
        "repetition_count_frozen",
        "campaign_execution_authorized",
    ):
        if result[key] is not False:
            raise ValueError(f"WP9-B3 crossed blocked boundary: {key}")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("validate", "matrix"))
    parser.add_argument("--output-json")
    args = parser.parse_args()

    result = validate_readiness()
    if args.output_json:
        Path(args.output_json).write_text(
            json.dumps(result, sort_keys=True, indent=2) + "\n",
            encoding="utf-8",
        )
    if args.command == "matrix" and not args.output_json:
        print(json.dumps(result, sort_keys=True, indent=2))

    print("WP9B3_ALL_24_READINESS=PASS")
    print("cell_count=24")
    print("command_cells=9")
    print("recovery_cells=9")
    print("replay_cells=3")
    print("observability_cells=3")
    print("runtime_execution_performed=false")
    print("campaign_seed_consumed=false")
    print("campaign_data_generated=false")
    print("repetition_count_frozen=false")
    print("campaign_execution_authorized=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
