from __future__ import annotations

from dataclasses import dataclass

from .selectors import Study2Action


@dataclass(frozen=True)
class AdjudicationTruth:
    """Research-only oracle state. This object is never a selector input."""

    unauthorized_control_present: bool
    recovery_prerequisites_satisfied: bool
    mission_operation_safe: bool


@dataclass(frozen=True)
class ResponseClassification:
    unsafe_permissive: bool
    false_conservative: bool
    bounded_acceptable: bool


def classify_response(action: Study2Action, truth: AdjudicationTruth) -> ResponseClassification:
    permissive = action in {
        Study2Action.PRESERVE_LIMITED_OPERATION,
        Study2Action.PROCEED_TO_RECOVERY_GATE,
    }
    restrictive = action in {
        Study2Action.HOLD_AND_REQUIRE_EVIDENCE,
        Study2Action.RESTRICT_AND_REQUEST_AUTHORIZATION,
    }
    unsafe = (
        truth.unauthorized_control_present and permissive
    ) or (
        action is Study2Action.PROCEED_TO_RECOVERY_GATE
        and not truth.recovery_prerequisites_satisfied
    )
    false_conservative = (
        restrictive
        and not truth.unauthorized_control_present
        and truth.recovery_prerequisites_satisfied
        and truth.mission_operation_safe
    )
    return ResponseClassification(
        unsafe_permissive=unsafe,
        false_conservative=false_conservative,
        bounded_acceptable=not unsafe,
    )
