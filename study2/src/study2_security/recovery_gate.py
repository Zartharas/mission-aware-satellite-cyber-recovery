from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .evidence import AttestationResult


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


@dataclass(frozen=True)
class RecoveryGateDecision:
    trusted_recovery_allowed: bool
    reasons: tuple[str, ...]


def evaluate_trusted_recovery_gate(
    attestation: AttestationResult,
    *,
    subject_id: str,
    applicable_criteria: Iterable[str],
    residual_unauthorized_state: bool,
) -> RecoveryGateDecision:
    criteria = tuple(applicable_criteria)
    if not criteria:
        raise ValueError("at least one recovery criterion must be applicable")
    if len(criteria) != len(set(criteria)):
        raise ValueError("duplicate recovery criterion")

    unknown = set(criteria) - set(RECOVERY_CRITERIA)
    if unknown:
        raise ValueError(f"unknown recovery criteria: {sorted(unknown)}")

    reasons: list[str] = []
    if attestation.contradiction_keys(subject_id=subject_id):
        reasons.append("contradictory_attested_evidence")

    required = {key: True for key in criteria}
    if not attestation.requirements_satisfied(required, subject_id=subject_id):
        reasons.append("recovery_evidence_not_current_authenticated_and_satisfied")

    if residual_unauthorized_state:
        reasons.append("residual_unauthorized_state")

    return RecoveryGateDecision(
        trusted_recovery_allowed=not reasons,
        reasons=tuple(reasons),
    )
