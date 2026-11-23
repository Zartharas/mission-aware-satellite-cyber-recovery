"""Study 10 G3 synthetic-only, independent Study 2 policy oracle.

Deliberately uses no study2 imports. This independently authored logic is
compared *against* the exact hash-pinned production selector by the harness.
No ESA, OPS-SAT, or other real-flight source files are accepted.
"""
from __future__ import annotations

from collections.abc import Mapping

FIELDS = (
    "signature_valid", "source_trusted", "fresh", "epoch_valid",
    "contradictory", "minimum_evidence_complete", "security_signal",
    "authorization_available",
)
POLICIES = (
    "S2_B0_FAIL_CLOSED", "S2_B1_FAIL_OPERATIONAL",
    "S2_B2_RISK_THRESHOLD", "S2_S1_EVIDENCE_AWARE",
)
ACTIONS = {
    "P": "PROCEED_TO_RECOVERY_GATE",
    "L": "PRESERVE_LIMITED_OPERATION",
    "R": "RESTRICT_AND_REQUEST_AUTHORIZATION",
    "H": "HOLD_AND_REQUIRE_EVIDENCE",
}


class IncompleteObservation(ValueError):
    """An UNKNOWN or invalid state is never a Study 2 Boolean observation."""


def oracle_action(policy: str, observed: Mapping[str, object]) -> str:
    """Independently evaluate the four frozen policies, using a decision table.

    Only exact bool is accepted: Python's bool(UNKNOWN), bool(None) and
    bool(0/1) are *not* an acceptable evidence-completion procedure.
    """
    if policy not in POLICIES:
        raise ValueError("POLICY_NOT_ONE_OF_FOUR_FROZEN_PRIMARY_POLICIES")
    if set(observed) != set(FIELDS) or any(type(observed[k]) is not bool for k in FIELDS):
        raise IncompleteObservation("UNKNOWN_OR_NON_BOOLEAN_RECOVERY_STATE")

    # Independent readiness relation, not a call to the production selector.
    evidence_ready = (
        all(observed[k] for k in FIELDS[:4])
        and observed["minimum_evidence_complete"]
        and observed["contradictory"] is False
    )
    danger = observed["security_signal"]
    reachable_auth = observed["authorization_available"]

    # Rows: evidence_ready False, evidence_ready True with danger False,
    # evidence_ready True with danger True and auth unavailable/available.
    row = (0 if not evidence_ready else 1 if not danger else 2 if not reachable_auth else 3)
    policy_table = {
        POLICIES[0]: ("R", "P", "P", "P"),
        POLICIES[1]: ("L", "L", "R", "R"),
        POLICIES[2]: ("H", "L", "R", "R"),
        POLICIES[3]: ("H", "P", "R", "P"),
    }
    return ACTIONS[policy_table[policy][row]]
