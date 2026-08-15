from __future__ import annotations

from typing import Any


_EFFECT_FAMILIES = {
    "P1": "command_gateway",
    "P2": "command_gateway",
    "P4": "command_gateway",
    "P5": "rollback_request",
}


def build_p7_effect_plan(decision: dict[str, Any]) -> dict[str, Any]:
    if decision["requested_policy_id"] != "P7":
        raise ValueError("effect plan requires requested policy P7")

    if decision["oracle_ground_truth_read"] is not False:
        raise ValueError("P7 decision violates oracle boundary")

    delegated = decision["delegated_policy_id"]
    if delegated not in _EFFECT_FAMILIES:
        raise ValueError(f"unsupported P7 delegate: {delegated}")

    return {
        "requested_policy_id": "P7",
        "delegated_policy_id": delegated,
        "selected_action": decision["selected_action"],
        "effect_family": _EFFECT_FAMILIES[delegated],
        "decision_basis": decision["decision_basis"],
        "evidence_insufficient": decision["evidence_insufficient"],
        "oracle_ground_truth_read": False,
        "trusted_recovery_verification_deferred_to_wp7": (
            decision["trusted_recovery_verification_deferred_to_wp7"]
        ),
    }
