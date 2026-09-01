"""Independent frozen Study-1 P7 decision baseline for Study-2 conformance checks.

This module intentionally duplicates the finite Study-1 semantics instead of reading the
runtime policy table. That separation lets a conformance check detect silent drift in the
implementation or configuration. It does not redefine Study-1 and is not a Study-2 policy.
"""
from __future__ import annotations

STUDY1_REPRODUCIBILITY_SNAPSHOT = "99892bd9bb0828bdb3d0a28caf40dbc18fcbc4dc"

ACTIONS = {
    "P0": "OBSERVE_ONLY",
    "P1": "ISOLATE_MODELED_SOURCE",
    "P2": "RESTRICT_HIGH_RISK_COMMANDS",
    "P4": "ENTER_SAFE_MODE",
    "P5": "REQUEST_VERIFIED_ROLLBACK",
}

EVIDENCE_SUFFICIENT = {
    ("E1", "T0"): True,
    ("E1", "T1"): False,
    ("E2", "T0"): True,
    ("E2", "T1"): False,
    ("E3", "T0"): True,
    ("E3", "T1"): False,
    ("E4", "T0"): False,
    ("E4", "T1"): False,
}

EVIDENCE_INSUFFICIENT_POLICY = {
    ("M0", "C0"): "P2",
    ("M0", "C1"): "P2",
    ("M2", "C0"): "P4",
    ("M2", "C1"): "P4",
    ("M4", "C0"): "P2",
    ("M4", "C1"): "P4",
}

EVIDENCE_SUFFICIENT_POLICY = {
    ("E1", "M0", "C0"): "P1",
    ("E1", "M0", "C1"): "P2",
    ("E1", "M2", "C0"): "P2",
    ("E1", "M2", "C1"): "P2",
    ("E1", "M4", "C0"): "P2",
    ("E1", "M4", "C1"): "P2",
    ("E2", "M0", "C0"): "P1",
    ("E2", "M0", "C1"): "P2",
    ("E2", "M2", "C0"): "P2",
    ("E2", "M2", "C1"): "P2",
    ("E2", "M4", "C0"): "P2",
    ("E2", "M4", "C1"): "P2",
    ("E3", "M0", "C0"): "P5",
    ("E3", "M0", "C1"): "P5",
    ("E3", "M2", "C0"): "P5",
    ("E3", "M2", "C1"): "P5",
    ("E3", "M4", "C0"): "P5",
    ("E3", "M4", "C1"): "P5",
    ("E4", "M0", "C0"): "P2",
    ("E4", "M0", "C1"): "P2",
    ("E4", "M2", "C0"): "P4",
    ("E4", "M2", "C1"): "P4",
    ("E4", "M4", "C0"): "P2",
    ("E4", "M4", "C1"): "P4",
}


def expected_p7_decision(
    event_id: str,
    mission_state: str,
    contact_condition: str,
    evidence_condition: str,
) -> dict[str, object]:
    sufficient = EVIDENCE_SUFFICIENT[(event_id, evidence_condition)]
    if sufficient:
        delegated = EVIDENCE_SUFFICIENT_POLICY[
            (event_id, mission_state, contact_condition)
        ]
        basis = "event_state_contact"
    else:
        delegated = EVIDENCE_INSUFFICIENT_POLICY[
            (mission_state, contact_condition)
        ]
        basis = "evidence_insufficient"

    return {
        "evidence_sufficient": sufficient,
        "delegated_policy_id": delegated,
        "selected_action": ACTIONS[delegated],
        "decision_basis": basis,
    }
