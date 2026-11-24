from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Study2Policy(str, Enum):
    FAIL_CLOSED = "S2_B0_FAIL_CLOSED"
    FAIL_OPERATIONAL = "S2_B1_FAIL_OPERATIONAL"
    RISK_THRESHOLD = "S2_B2_RISK_THRESHOLD"
    EVIDENCE_AWARE = "S2_S1_EVIDENCE_AWARE"
    NO_FRESHNESS = "S2_ABL_NO_FRESHNESS"
    NO_CONTRADICTION = "S2_ABL_NO_CONTRADICTION"
    NO_EPOCH = "S2_ABL_NO_EPOCH"
    NO_SIGNATURE_TRUST = "S2_ABL_NO_SIGNATURE_TRUST"


class Study2Action(str, Enum):
    HOLD_AND_REQUIRE_EVIDENCE = "HOLD_AND_REQUIRE_EVIDENCE"
    PRESERVE_LIMITED_OPERATION = "PRESERVE_LIMITED_OPERATION"
    RESTRICT_AND_REQUEST_AUTHORIZATION = "RESTRICT_AND_REQUEST_AUTHORIZATION"
    PROCEED_TO_RECOVERY_GATE = "PROCEED_TO_RECOVERY_GATE"


@dataclass(frozen=True)
class ObservationSummary:
    signature_valid: bool
    source_trusted: bool
    fresh: bool
    epoch_valid: bool
    contradictory: bool
    minimum_evidence_complete: bool
    security_signal: bool
    authorization_available: bool


def select_action(policy: Study2Policy, obs: ObservationSummary) -> Study2Action:
    checks = {
        "signature": obs.signature_valid and obs.source_trusted,
        "freshness": obs.fresh,
        "epoch": obs.epoch_valid,
        "contradiction": not obs.contradictory,
        "complete": obs.minimum_evidence_complete,
    }
    if policy is Study2Policy.NO_SIGNATURE_TRUST:
        checks["signature"] = True
    elif policy is Study2Policy.NO_FRESHNESS:
        checks["freshness"] = True
    elif policy is Study2Policy.NO_EPOCH:
        checks["epoch"] = True
    elif policy is Study2Policy.NO_CONTRADICTION:
        checks["contradiction"] = True

    evidence_qualified = all(checks.values())

    if policy is Study2Policy.FAIL_CLOSED:
        return Study2Action.RESTRICT_AND_REQUEST_AUTHORIZATION if not evidence_qualified else Study2Action.PROCEED_TO_RECOVERY_GATE
    if policy is Study2Policy.FAIL_OPERATIONAL:
        return Study2Action.RESTRICT_AND_REQUEST_AUTHORIZATION if evidence_qualified and obs.security_signal else Study2Action.PRESERVE_LIMITED_OPERATION
    if policy is Study2Policy.RISK_THRESHOLD:
        if not evidence_qualified:
            return Study2Action.HOLD_AND_REQUIRE_EVIDENCE
        return Study2Action.RESTRICT_AND_REQUEST_AUTHORIZATION if obs.security_signal else Study2Action.PRESERVE_LIMITED_OPERATION

    if not evidence_qualified:
        return Study2Action.HOLD_AND_REQUIRE_EVIDENCE
    if obs.security_signal and not obs.authorization_available:
        return Study2Action.RESTRICT_AND_REQUEST_AUTHORIZATION
    return Study2Action.PROCEED_TO_RECOVERY_GATE
