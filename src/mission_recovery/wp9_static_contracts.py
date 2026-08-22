from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from .events import materialize_event
from .policies import evaluate_policy
from .policy_gateway import build_sample_noargs_packet, decide_forward


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CAMPAIGN = ROOT / "configs" / "wp9_campaign_design.json"
DEFAULT_MODEL = ROOT / "configs" / "wp9_experiment_model.json"
DEFAULT_P6_EXTENSION = ROOT / "configs" / "wp9_policy_extension.json"
DEFAULT_SCHEMA_EXTENSION = ROOT / "configs" / "wp9_run_schema_extension.json"
DEFAULT_STATIC_CONTRACT = ROOT / "configs" / "wp9b_static_contract.json"
DEFAULT_BASE_SCHEMA = ROOT / "configs" / "experiment_run.schema.json"

DECISION_ID = "R-045"
STATIC_SEED = 0
WP9_POLICY_IDS = {"P0", "P1", "P2", "P4", "P5", "P6", "P7"}


def _load(path: Path | str) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(
            value,
            ensure_ascii=True,
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
    ).encode("utf-8")


def _sha256_record(value: dict[str, Any]) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def load_campaign_design(path: Path | str = DEFAULT_CAMPAIGN) -> dict[str, Any]:
    return _load(path)


def load_wp9_model(path: Path | str = DEFAULT_MODEL) -> dict[str, Any]:
    return _load(path)


def load_p6_extension(path: Path | str = DEFAULT_P6_EXTENSION) -> dict[str, Any]:
    return _load(path)


def load_schema_extension(
    path: Path | str = DEFAULT_SCHEMA_EXTENSION,
) -> dict[str, Any]:
    return _load(path)


def load_static_contract(
    path: Path | str = DEFAULT_STATIC_CONTRACT,
) -> dict[str, Any]:
    return _load(path)


def campaign_cells(
    design: dict[str, Any] | None = None,
) -> dict[str, dict[str, Any]]:
    design = design or load_campaign_design()
    cells = {row["cell_id"]: deepcopy(row) for row in design["cells"]}
    if len(cells) != len(design["cells"]):
        raise ValueError("duplicate WP9 campaign cell_id")
    if set(cells) != {f"A{i:02d}" for i in range(1, 25)}:
        raise ValueError("WP9 campaign cells must be exactly A01-A24")
    return cells


def validate_wp9_model(model: dict[str, Any] | None = None) -> None:
    model = model or load_wp9_model()
    if model["model_version"] != "0.4.0":
        raise ValueError("WP9 campaign model must be version 0.4.0")
    if model["base_model_version"] != "0.3.0":
        raise ValueError("WP9 campaign model must extend frozen WP8 model 0.3.0")
    policy_ids = {row["id"] for row in model["response_policies"]}
    if policy_ids != WP9_POLICY_IDS:
        raise ValueError("WP9 campaign model policy set changed")
    p6 = next(row for row in model["response_policies"] if row["id"] == "P6")
    if p6["name"] != "wait_for_ground_authorization":
        raise ValueError("WP9 P6 name changed")
    if p6["autonomy_level"] != "ground_dependent":
        raise ValueError("WP9 P6 autonomy classification changed")
    boundary = model["scientific_boundary"]
    if boundary["wp8_model_mutated"] is not False:
        raise ValueError("WP9 model cannot claim mutation of the frozen WP8 model")
    if boundary["runtime_execution_performed"] is not False:
        raise ValueError("WP9-B1 model cannot execute runtime")
    if boundary["campaign_seed_consumed"] is not False:
        raise ValueError("WP9-B1 model cannot consume campaign seeds")
    if boundary["campaign_data_generated"] is not False:
        raise ValueError("WP9-B1 model cannot generate campaign data")
    if boundary["campaign_execution_authorized"] is not False:
        raise ValueError("WP9-B1 model cannot authorize campaign execution")


def evaluate_wp9_policy(
    policy_id: str,
    event_instance: dict[str, Any],
    *,
    p6_extension_path: Path | str = DEFAULT_P6_EXTENSION,
) -> dict[str, Any]:
    if policy_id != "P6":
        return evaluate_policy(policy_id, event_instance)

    extension = load_p6_extension(p6_extension_path)
    policy = extension["policy"]
    if event_instance["event_id"] not in policy["allowed_event_ids"]:
        raise ValueError("P6 is only admitted for the frozen E3 recovery contrast")
    if event_instance["mission_state"] not in policy["allowed_mission_state_ids"]:
        raise ValueError("P6 is only admitted for the frozen M4 recovery contrast")
    if event_instance["evidence_condition"] not in policy[
        "allowed_evidence_condition_ids"
    ]:
        raise ValueError("P6 is only admitted for the frozen T0 recovery contrast")
    if event_instance["contact_condition"] not in policy[
        "allowed_contact_condition_ids"
    ]:
        raise ValueError("P6 contact condition is outside the frozen contrast")

    decision: dict[str, Any] = {
        "requested_policy_id": "P6",
        "delegated_policy_id": "P6",
        "selected_action": policy["action"],
        "autonomy_level": policy["autonomy_level"],
        "decision_basis": "fixed_wp9_ground_authorization_gate",
        "evidence_insufficient": False,
        "evidence_failures": [],
        "event_id": event_instance["event_id"],
        "mission_state": event_instance["mission_state"],
        "contact_condition": event_instance["contact_condition"],
        "evidence_condition": event_instance["evidence_condition"],
        "oracle_ground_truth_read": False,
        "trusted_recovery_verification_deferred_to_wp7": False,
        "ground_authorization_required": True,
    }
    decision["decision_sha256"] = _sha256_record(decision)
    return decision


def build_p6_authorization_contract(
    event_instance: dict[str, Any],
    *,
    p6_extension_path: Path | str = DEFAULT_P6_EXTENSION,
) -> dict[str, Any]:
    decision = evaluate_wp9_policy(
        "P6",
        event_instance,
        p6_extension_path=p6_extension_path,
    )
    extension = load_p6_extension(p6_extension_path)
    contact = event_instance["contact_condition"]
    schedule = extension["synthetic_authorization_schedule"][contact]

    return {
        "schema": 1,
        "decision_id": DECISION_ID,
        "event_id": "E3",
        "mission_state_id": "M4",
        "contact_condition_id": contact,
        "evidence_condition_id": "T0",
        "requested_policy_id": "P6",
        "pre_authorization_action": decision["selected_action"],
        "authorization_source": extension["synthetic_authorization_schedule"][
            "source"
        ],
        "available_at_response_boundary": schedule[
            "available_at_response_boundary"
        ],
        "missed_contact_windows_before_authorization": schedule[
            "missed_contact_windows_before_authorization"
        ],
        "release_rule": schedule["release_rule"],
        "runtime_authorization_timestamp_s": None,
        "runtime_observation_required": True,
        "expected_contact_condition_used_as_observed_timestamp": False,
        "real_human_operator_required": False,
        "real_world_ground_contact_required": False,
        "oracle_ground_truth_read": False,
        "runtime_execution_performed": False,
        "campaign_seed_consumed": False,
        "campaign_data_generated": False,
    }


def build_p6_handoff_contract(
    event_instance: dict[str, Any],
    *,
    p6_extension_path: Path | str = DEFAULT_P6_EXTENSION,
) -> dict[str, Any]:
    authorization = build_p6_authorization_contract(
        event_instance,
        p6_extension_path=p6_extension_path,
    )
    extension = load_p6_extension(p6_extension_path)
    transition = extension["post_authorization_transition"]
    return {
        "schema": 1,
        "decision_id": DECISION_ID,
        "authorization_contract": authorization,
        "handoff_precondition": "runtime_observed_authorization_current",
        "post_authorization_requested_policy_id": "P6",
        "post_authorization_delegated_policy_id": transition[
            "delegated_policy_id"
        ],
        "post_authorization_action": transition["selected_action"],
        "rollback_request_builder": transition["rollback_request_builder"],
        "trusted_recovery_validation": transition[
            "trusted_recovery_validation"
        ],
        "authorization_observation_required_before_handoff": transition[
            "authorization_observation_required_before_handoff"
        ],
        "runtime_execution_performed": False,
        "campaign_seed_consumed": False,
        "campaign_data_generated": False,
    }


def _e2_replay_envelope(packet: bytes) -> dict[str, Any]:
    return {
        "schema": 1,
        "event_id": "E2",
        "probe_variant": "wp9_byte_identical_replay_effect",
        "source_id": "modeled_attacker",
        "command_class": "sample_reset_counters",
        "declared_risk_class": "high_surrogate",
        "packet_hex": packet.hex(),
        "packet_sha256": hashlib.sha256(packet).hexdigest(),
    }


def build_e2_replay_effect_contract(
    cell_id: str,
    *,
    design: dict[str, Any] | None = None,
) -> dict[str, Any]:
    design = design or load_campaign_design()
    cells = campaign_cells(design)
    if cell_id not in {"A19", "A20", "A21"}:
        raise ValueError("E2 replay effect contract is limited to A19-A21")
    cell = cells[cell_id]
    if cell["event_id"] != "E2":
        raise ValueError("WP9 replay cell event changed")

    event = materialize_event(
        "E2",
        mission_state=cell["mission_state_id"],
        contact_condition=cell["contact_condition_id"],
        evidence_condition=cell["evidence_condition_id"],
        seed=STATIC_SEED,
    )
    decision = evaluate_wp9_policy(cell["policy_id"], event)
    if decision["delegated_policy_id"] != cell["expected_effective_policy_id"]:
        raise ValueError("WP9 E2 policy delegate differs from frozen design")

    packet = build_sample_noargs_packet("sample_reset_counters")
    packet_sha = hashlib.sha256(packet).hexdigest()
    envelope = _e2_replay_envelope(packet)
    forwarded = decide_forward(decision["selected_action"], envelope)
    expected_delta = 1 if forwarded else 0

    return {
        "schema": 1,
        "decision_id": DECISION_ID,
        "cell_id": cell_id,
        "factor_context": {
            "event_id": "E2",
            "mission_state_id": cell["mission_state_id"],
            "contact_condition_id": cell["contact_condition_id"],
            "evidence_condition_id": cell["evidence_condition_id"],
            "policy_id": cell["policy_id"],
        },
        "static_seed": STATIC_SEED,
        "static_seed_role": "semantic_materialization_only_not_campaign_execution",
        "requested_policy_id": cell["policy_id"],
        "actual_effective_policy_id": decision["delegated_policy_id"],
        "selected_action": decision["selected_action"],
        "oracle_ground_truth_read": decision["oracle_ground_truth_read"],
        "setup": {
            "role": "previously_accepted_authorized_command_before_treatment",
            "source_id": "authorized_ground",
            "command_class": "sample_reset_counters",
            "packet_sha256": packet_sha,
            "direct_nominal_setup_path": True,
            "excluded_from_m01": True,
        },
        "intervening_state_probe": {
            "source_id": "authorized_ground",
            "command_class": "sample_noop",
            "purpose": "create observable post-setup activity before stale replay",
        },
        "replay": {
            **envelope,
            "role": "byte_identical_stale_replay_after_treatment",
            "byte_identical_to_setup": True,
        },
        "m01_effect_observation": {
            "source": "observed_post_replay_cfs_reset_marker_delta",
            "expected_delta_for_acceptance_only": expected_delta,
            "expected_forwarded_for_acceptance_only": forwarded,
            "setup_marker_excluded": True,
            "packet_send_success_is_not_effect_evidence": True,
            "noop_receipt_alone_is_not_effect_evidence": True,
        },
        "expected_values_role": "post_observation_acceptance_only_not_metric_inputs",
        "runtime_execution_performed": False,
        "campaign_seed_consumed": False,
        "campaign_data_generated": False,
    }


def runtime_route_for_cell(
    cell_id: str,
    *,
    static_contract: dict[str, Any] | None = None,
) -> dict[str, str]:
    static_contract = static_contract or load_static_contract()
    routing = static_contract["runtime_routing"]
    if cell_id not in routing:
        raise ValueError(f"unknown WP9 cell: {cell_id}")
    family, variant = routing[cell_id]
    return {"runtime_family": family, "runtime_variant": variant}


def build_static_cell_contract(
    cell_id: str,
    *,
    design: dict[str, Any] | None = None,
) -> dict[str, Any]:
    design = design or load_campaign_design()
    cells = campaign_cells(design)
    cell = cells[cell_id]
    event = materialize_event(
        cell["event_id"],
        mission_state=cell["mission_state_id"],
        contact_condition=cell["contact_condition_id"],
        evidence_condition=cell["evidence_condition_id"],
        seed=STATIC_SEED,
    )
    decision = evaluate_wp9_policy(cell["policy_id"], event)
    if decision["delegated_policy_id"] != cell["expected_effective_policy_id"]:
        raise ValueError(
            f"{cell_id}: effective policy {decision['delegated_policy_id']} "
            f"!= frozen {cell['expected_effective_policy_id']}"
        )
    if decision["oracle_ground_truth_read"] is not False:
        raise ValueError("WP9 policy evaluation cannot read immutable ground truth")

    row: dict[str, Any] = {
        "schema": 1,
        "decision_id": DECISION_ID,
        "cell_id": cell_id,
        "factor_context": {
            "model_version": "0.4.0",
            "static_seed": STATIC_SEED,
            "mission_state_id": cell["mission_state_id"],
            "event_id": cell["event_id"],
            "policy_id": cell["policy_id"],
            "contact_condition_id": cell["contact_condition_id"],
            "evidence_condition_id": cell["evidence_condition_id"],
        },
        "event_instance_sha256": event["instance_sha256"],
        "requested_policy_id": cell["policy_id"],
        "actual_effective_policy_id": decision["delegated_policy_id"],
        "expected_effective_policy_id_for_acceptance_only": cell[
            "expected_effective_policy_id"
        ],
        "selected_action": decision["selected_action"],
        "oracle_ground_truth_read": False,
        **runtime_route_for_cell(cell_id),
        "development_preflight": True,
        "campaign_data": False,
        "campaign_seed_consumed": False,
        "runtime_execution_performed": False,
        "expected_values_role": "post_observation_acceptance_only_not_metric_inputs",
    }
    if cell_id in {"A19", "A20", "A21"}:
        row["e2_replay_effect_contract"] = build_e2_replay_effect_contract(
            cell_id,
            design=design,
        )
    if cell["policy_id"] == "P6":
        row["p6_handoff_contract"] = build_p6_handoff_contract(event)
    return row


def build_static_matrix(
    design: dict[str, Any] | None = None,
) -> dict[str, Any]:
    design = design or load_campaign_design()
    rows = [
        build_static_cell_contract(f"A{i:02d}", design=design)
        for i in range(1, 25)
    ]
    return {
        "schema": 1,
        "decision_id": DECISION_ID,
        "classification": "WP9B1_STATIC_CAMPAIGN_MECHANISM_MATRIX",
        "cell_ids": [row["cell_id"] for row in rows],
        "rows": rows,
        "development_preflight": True,
        "runtime_execution_performed": False,
        "development_runtime_data_generated": False,
        "campaign_seed_consumed": False,
        "campaign_data_generated": False,
        "repetition_count_frozen": False,
        "campaign_execution_authorized": False,
    }


def build_wp9_run_schema(
    *,
    base_schema_path: Path | str = DEFAULT_BASE_SCHEMA,
    extension_path: Path | str = DEFAULT_SCHEMA_EXTENSION,
) -> dict[str, Any]:
    schema = deepcopy(_load(base_schema_path))
    extension = load_schema_extension(extension_path)
    schema["$id"] = extension["result_schema_id"]
    schema["title"] = extension["result_title"]

    policy_enum = list(schema["properties"]["policy_id"]["enum"])
    for policy_id in extension["policy_id_additions"]:
        if policy_id not in policy_enum:
            policy_enum.append(policy_id)
    schema["properties"]["policy_id"]["enum"] = policy_enum

    auth = extension["ground_authorization"]
    auth_schema = {
        "type": "object",
        "additionalProperties": False,
        "required": list(auth["required_fields"]),
        "properties": {
            "required": {"const": True},
            "source": {"const": auth["source_const"]},
            "available_at_response_boundary": {"type": "boolean"},
            "available_timestamp_s": {
                "type": ["number", "null"],
                "minimum": 0,
            },
            "missed_contact_windows": {"type": "integer", "minimum": 0},
            "authorization_current": {"type": "boolean"},
            "evidence_ref": {"type": "string", "minLength": 1},
        },
    }
    raw = schema["properties"]["raw_metric_evidence"]
    raw["properties"][auth["property_name"]] = auth_schema

    p6_noninvalid = {
        "properties": {
            "policy_id": {"const": auth["require_for_policy_id"]},
            "terminal_state": {"not": {"const": "RUN_INVALID"}},
        },
        "required": ["policy_id", "terminal_state"],
    }
    schema["allOf"].append(
        {
            "if": p6_noninvalid,
            "then": {
                "properties": {
                    "raw_metric_evidence": {
                        "required": [auth["property_name"]]
                    }
                }
            },
        }
    )

    for contact_id, rule in auth["contact_rules"].items():
        schema["allOf"].append(
            {
                "if": {
                    "properties": {
                        "policy_id": {"const": auth["require_for_policy_id"]},
                        "contact_condition_id": {"const": contact_id},
                        "terminal_state": {"not": {"const": "RUN_INVALID"}},
                    },
                    "required": [
                        "policy_id",
                        "contact_condition_id",
                        "terminal_state",
                    ],
                },
                "then": {
                    "properties": {
                        "raw_metric_evidence": {
                            "properties": {
                                auth["property_name"]: {
                                    "properties": {
                                        "available_at_response_boundary": {
                                            "const": rule[
                                                "available_at_response_boundary"
                                            ]
                                        },
                                        "missed_contact_windows": {
                                            "const": rule[
                                                "missed_contact_windows"
                                            ]
                                        },
                                    }
                                }
                            }
                        }
                    }
                },
            }
        )
    return schema


def validate_wp9_static_contract() -> None:
    validate_wp9_model()
    design = load_campaign_design()
    static = load_static_contract()
    cells = campaign_cells(design)

    if static["decision_id"] != DECISION_ID:
        raise ValueError("WP9-B1 static contract decision changed")
    if static["status"] != (
        "WP9B1_STATIC_IMPLEMENTATION_FROZEN_RUNTIME_VALIDATION_REQUIRED"
    ):
        raise ValueError("WP9-B1 static status changed")
    boundary = static["scientific_boundary"]
    required_false = [
        "wp9b2_runtime_validation_complete",
        "runtime_execution_performed",
        "development_runtime_data_generated",
        "campaign_seed_consumed",
        "campaign_data_generated",
        "repetition_count_frozen",
        "campaign_execution_authorized",
        "wp8_code_or_pilot_design_mutated",
    ]
    for key in required_false:
        if boundary[key] is not False:
            raise ValueError(f"WP9-B1 boundary must remain false: {key}")
    if boundary["wp9b1_static_implementation_complete"] is not True:
        raise ValueError("WP9-B1 static implementation is not marked complete")

    if set(static["runtime_routing"]) != set(cells):
        raise ValueError("WP9-B1 runtime routing does not cover A01-A24")

    matrix = build_static_matrix(design)
    if matrix["cell_ids"] != [f"A{i:02d}" for i in range(1, 25)]:
        raise ValueError("WP9-B1 static matrix ordering changed")
    if matrix["runtime_execution_performed"] is not False:
        raise ValueError("WP9-B1 static matrix cannot execute runtime")
    if matrix["campaign_seed_consumed"] is not False:
        raise ValueError("WP9-B1 static matrix cannot consume campaign seeds")
    if matrix["campaign_data_generated"] is not False:
        raise ValueError("WP9-B1 static matrix cannot generate campaign data")
    if matrix["campaign_execution_authorized"] is not False:
        raise ValueError("WP9-B1 static matrix cannot authorize campaign execution")
