from __future__ import annotations

from dataclasses import replace

from .selectors import ObservationSummary, Study2Action, Study2Policy, select_action


CONTEXT_ABLATION_SELECTORS = (
    "S2_S1_EVIDENCE_AWARE",
    "PI_NO_MISSION",
    "PI_NO_EVIDENCE",
    "PI_NO_CONTACT",
    "PI_SECURITY_ONLY",
)


def select_context_ablation(selector_id: str, observation: ObservationSummary) -> Study2Action:
    if selector_id not in CONTEXT_ABLATION_SELECTORS:
        raise ValueError(f"unknown context selector: {selector_id}")
    if selector_id == "S2_S1_EVIDENCE_AWARE":
        return select_action(Study2Policy.EVIDENCE_AWARE, observation)
    if selector_id == "PI_NO_MISSION":
        return select_action(Study2Policy.EVIDENCE_AWARE, replace(observation, security_signal=False))
    if selector_id == "PI_NO_EVIDENCE":
        return select_action(Study2Policy.EVIDENCE_AWARE, replace(observation, signature_valid=True, source_trusted=True, fresh=True, epoch_valid=True, contradictory=False, minimum_evidence_complete=True))
    if selector_id == "PI_NO_CONTACT":
        return select_action(Study2Policy.EVIDENCE_AWARE, replace(observation, authorization_available=True))
    return Study2Action.RESTRICT_AND_REQUEST_AUTHORIZATION if observation.security_signal else Study2Action.PRESERVE_LIMITED_OPERATION
