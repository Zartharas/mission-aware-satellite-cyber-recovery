from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_RULES = ROOT / "configs" / "wp6_policy_rules.json"

ALLOWED_POLICIES = {"P0", "P1", "P2", "P4", "P5", "P7"}
ALLOWED_MISSION_STATES = {"M0", "M2", "M4"}
ALLOWED_CONTACT_CONDITIONS = {"C0", "C1"}
ALLOWED_EVIDENCE_CONDITIONS = {"T0", "T1"}


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


def load_policy_rules(path: Path | str = DEFAULT_RULES) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _policy_input(event_instance: dict[str, Any]) -> dict[str, Any]:
    payload = {
        "event_id": event_instance["event_id"],
        "mission_state": event_instance["mission_state"],
        "contact_condition": event_instance["contact_condition"],
        "evidence_condition": event_instance["evidence_condition"],
        "policy_visible_evidence": dict(
            event_instance["policy_visible_evidence"]
        ),
    }

    if payload["mission_state"] not in ALLOWED_MISSION_STATES:
        raise ValueError("unsupported mission state")
    if payload["contact_condition"] not in ALLOWED_CONTACT_CONDITIONS:
        raise ValueError("unsupported contact condition")
    if payload["evidence_condition"] not in ALLOWED_EVIDENCE_CONDITIONS:
        raise ValueError("unsupported evidence condition")

    return payload


def assess_minimum_evidence(
    event_instance: dict[str, Any],
    *,
    rules_path: Path | str = DEFAULT_RULES,
) -> dict[str, Any]:
    rules = load_policy_rules(rules_path)
    policy_input = _policy_input(event_instance)
    evidence = policy_input["policy_visible_evidence"]
    requirements = rules["minimum_policy_evidence"][policy_input["event_id"]]

    failures: list[str] = []
    for requirement in requirements:
        key = requirement["key"]
        rule = requirement["rule"]

        if rule == "present":
            if key not in evidence:
                failures.append(f"{key}:missing")
        elif rule == "true":
            if evidence.get(key) is not True:
                failures.append(f"{key}:not_true")
        else:
            raise ValueError(f"unsupported evidence rule: {rule}")

    return {
        "sufficient": not failures,
        "failures": failures,
    }


def _fixed_decision(
    policy_id: str,
    policy_input: dict[str, Any],
    rules: dict[str, Any],
) -> dict[str, Any]:
    policy = rules["fixed_policies"][policy_id]
    return {
        "requested_policy_id": policy_id,
        "delegated_policy_id": policy_id,
        "selected_action": policy["action"],
        "autonomy_level": policy["autonomy_level"],
        "decision_basis": "fixed_policy",
        "evidence_insufficient": False,
        "evidence_failures": [],
        "event_id": policy_input["event_id"],
        "mission_state": policy_input["mission_state"],
        "contact_condition": policy_input["contact_condition"],
        "evidence_condition": policy_input["evidence_condition"],
        "oracle_ground_truth_read": False,
        "trusted_recovery_verification_deferred_to_wp7": policy_id == "P5",
    }


def _mission_aware_decision(
    policy_input: dict[str, Any],
    evidence_assessment: dict[str, Any],
    rules: dict[str, Any],
) -> dict[str, Any]:
    state = policy_input["mission_state"]
    contact = policy_input["contact_condition"]
    event_id = policy_input["event_id"]

    if not evidence_assessment["sufficient"]:
        delegated = (
            rules["mission_aware_policy"]["rules"]["evidence_insufficient"]
            [state][contact]
        )
        basis = "evidence_insufficient"
    else:
        delegated = (
            rules["mission_aware_policy"]["rules"]["evidence_sufficient"]
            [event_id][state][contact]
        )
        basis = "event_state_contact"

    fixed = rules["fixed_policies"][delegated]

    return {
        "requested_policy_id": "P7",
        "delegated_policy_id": delegated,
        "selected_action": fixed["action"],
        "autonomy_level": "adaptive",
        "decision_basis": basis,
        "evidence_insufficient": not evidence_assessment["sufficient"],
        "evidence_failures": list(evidence_assessment["failures"]),
        "event_id": event_id,
        "mission_state": state,
        "contact_condition": contact,
        "evidence_condition": policy_input["evidence_condition"],
        "oracle_ground_truth_read": False,
        "trusted_recovery_verification_deferred_to_wp7": delegated == "P5",
    }


def evaluate_policy(
    policy_id: str,
    event_instance: dict[str, Any],
    *,
    rules_path: Path | str = DEFAULT_RULES,
) -> dict[str, Any]:
    if policy_id not in ALLOWED_POLICIES:
        raise ValueError(f"unsupported policy_id: {policy_id}")

    rules = load_policy_rules(rules_path)
    policy_input = _policy_input(event_instance)

    if policy_id == "P7":
        evidence_assessment = assess_minimum_evidence(
            event_instance,
            rules_path=rules_path,
        )
        decision = _mission_aware_decision(
            policy_input,
            evidence_assessment,
            rules,
        )
    else:
        decision = _fixed_decision(policy_id, policy_input, rules)

    decision["decision_sha256"] = hashlib.sha256(
        _canonical_bytes(decision)
    ).hexdigest()
    return decision
