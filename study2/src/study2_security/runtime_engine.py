from __future__ import annotations

import hashlib
import json
from dataclasses import asdict
from typing import Any

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from .adjudication import AdjudicationTruth, classify_response
from .cell_matrix import materialize_cell_matrix
from .context_ablations import select_context_ablation
from .evidence import AttestationResult, EvidenceClaim, EvidenceCondition, SignedEvidence, sign_claim, verify_bundle
from .protocol import AdversaryBudget, AdversaryClass, ContactRegime, ScenarioIdentity
from .recovery_gate import RECOVERY_CRITERIA, evaluate_trusted_recovery_gate
from .runtime_authorization import CampaignAuthorization
from .runtime_freeze import CENSOR_HORIZON_S, CONTACT_CALIBRATION, DECISION_TIME_S, EVIDENCE_ISSUED_AT_S, EVIDENCE_VALID_FOR_S, EXPERIMENT_ID, RECOVERY_PROCESSING_S, RuntimeMode, require_seed_mode
from .selectors import ObservationSummary, Study2Action, Study2Policy, select_action


SUBJECT_ID = "synthetic-spacecraft-1"
PRODUCER_CRITERIA = {
    "ground-auth": ("authorization_valid", "authorized_command_path_restored", "ground_spacecraft_state_agreed", "recovery_manifest_complete"),
    "platform-attest": ("approved_version", "integrity_measurement_valid", "measured_state_current", "no_residual_unauthorized_state"),
    "telemetry-monitor": ("required_telemetry_restored", "health_checks_passed"),
}
ALL_PRODUCERS = (*PRODUCER_CRITERIA.keys(), "independent-monitor")


def _token(*parts: object) -> str:
    return hashlib.sha256("|".join(str(part) for part in parts).encode("utf-8")).hexdigest()


def _private_key(source_id: str) -> Ed25519PrivateKey:
    seed = hashlib.sha256(f"{EXPERIMENT_ID}|synthetic-ed25519|{source_id}".encode("utf-8")).digest()
    return Ed25519PrivateKey.from_private_bytes(seed)


def _private_keys() -> dict[str, Ed25519PrivateKey]:
    return {source: _private_key(source) for source in ALL_PRODUCERS}


def _public_keys() -> dict[str, Any]:
    return {source: key.public_key() for source, key in _private_keys().items()}


def _cell(cell_id: str) -> dict[str, Any]:
    for cell in materialize_cell_matrix()["cells"]:
        if cell["cell_id"] == cell_id:
            return dict(cell)
    raise ValueError(f"unknown frozen cell: {cell_id}")


def _contact_regime(cell: dict[str, Any]) -> ContactRegime:
    return ContactRegime(cell.get("contact", "K0"))


def _initial_truth(cell: dict[str, Any]) -> dict[str, bool]:
    truth = {criterion: True for criterion in RECOVERY_CRITERIA}
    block = cell["block"]
    if block == "A_PRIMARY_EVIDENCE_MECHANISM":
        truth["authorization_valid"] = False
    elif block == "B_CONTACT_AUTHORIZATION":
        truth["authorization_valid"] = CONTACT_CALIBRATION[_contact_regime(cell)].available_at(DECISION_TIME_S)
    elif block == "C_FAULT_ATTACK_AMBIGUITY" and cell["ambiguity_family"] == "contact_or_authorization_loss":
        truth["authorization_valid"] = False
    elif block == "D_CONTEXT_ABLATION" and cell["context"] == "unauthorized_command":
        truth["authorization_valid"] = False
    elif block == "E_ADVERSARY_BUDGET_STRESS":
        truth["authorization_valid"] = False
        if cell["adversary"] == "A3":
            truth["no_residual_unauthorized_state"] = False
    return truth


def _base_evidence(*, seed: int, truth: dict[str, bool], issued_at_s: float = EVIDENCE_ISSUED_AT_S) -> tuple[SignedEvidence, ...]:
    epoch = 1000 + (seed % 997)
    private_keys = _private_keys()
    rows: list[SignedEvidence] = []
    for source_id, criteria in PRODUCER_CRITERIA.items():
        for sequence, criterion in enumerate(criteria, start=1):
            claim = EvidenceClaim(source_id=source_id, subject_id=SUBJECT_ID, key=criterion, value=truth[criterion], epoch=epoch, sequence=sequence, issued_at_s=issued_at_s, valid_for_s=EVIDENCE_VALID_FOR_S, provenance=_token(EXPERIMENT_ID, seed, source_id, criterion, issued_at_s))
            rows.append(sign_claim(claim, private_keys[source_id]))
    return tuple(rows)


def _budget(adversary: AdversaryClass) -> AdversaryBudget:
    compromised = {AdversaryClass.A0: (), AdversaryClass.A1: ("ground-auth",), AdversaryClass.A2: ("ground-auth",), AdversaryClass.A3: ("ground-auth", "platform-attest")}[adversary]
    return AdversaryBudget(adversary_class=adversary, compromised_sources=compromised, independent_trust_anchor="verifier-root")


def _scenario(cell: dict[str, Any], *, seed: int, condition: EvidenceCondition, adversary: AdversaryClass, contact: ContactRegime) -> ScenarioIdentity:
    scenario_id = f"{cell['cell_id']}:{seed}"
    return ScenarioIdentity(experiment_id=EXPERIMENT_ID, scenario_id=scenario_id, seed=seed, treatment_id=f"{cell['cell_id']}:{condition.value}:{cell.get('mechanism', 'runtime')}", evidence_condition=condition, adversary_class=adversary, contact_regime=contact, ground_truth_token=_token(scenario_id, "ground-truth"), provenance_token=_token(scenario_id, "provenance"), analysis_control_token=_token(scenario_id, "analysis"))


def _apply_cell_evidence(cell: dict[str, Any], *, seed: int, truth: dict[str, bool]) -> tuple[SignedEvidence, ...]:
    from .treatments import apply_treatment
    bundle = _base_evidence(seed=seed, truth=truth)
    block = cell["block"]
    private_keys = _private_keys()
    if block in {"A_PRIMARY_EVIDENCE_MECHANISM", "E_ADVERSARY_BUDGET_STRESS"}:
        condition = EvidenceCondition(cell["evidence"])
        adversary = AdversaryClass(cell["adversary"])
        contact = _contact_regime(cell)
        scenario = _scenario(cell, seed=seed, condition=condition, adversary=adversary, contact=contact)
        budget = _budget(adversary)
        kwargs: dict[str, Any] = {}
        if condition is not EvidenceCondition.CURRENT:
            kwargs.update(target_source="ground-auth", target_key="authorization_valid")
        if condition is EvidenceCondition.CONTRADICTORY:
            kwargs["alternate_source"] = "independent-monitor"
        result = apply_treatment(scenario, bundle, budget=budget, private_keys=private_keys, now_s=DECISION_TIME_S, **kwargs)
        bundle = result.evidence
        if block == "E_ADVERSARY_BUDGET_STRESS" and adversary is AdversaryClass.A3:
            bundle = apply_treatment(scenario, bundle, budget=budget, private_keys=private_keys, target_source="platform-attest", target_key="no_residual_unauthorized_state", now_s=DECISION_TIME_S).evidence
        return bundle
    if block == "C_FAULT_ATTACK_AMBIGUITY":
        family = cell["ambiguity_family"]
        if family == "telemetry_loss":
            return tuple(row for row in bundle if row.claim.key != "required_telemetry_restored")
        if family == "state_inconsistency":
            target = next(row for row in bundle if row.claim.key == "ground_spacecraft_state_agreed")
            conflict = EvidenceClaim(source_id="independent-monitor", subject_id=target.claim.subject_id, key=target.claim.key, value=not bool(target.claim.value), epoch=target.claim.epoch, sequence=1, issued_at_s=target.claim.issued_at_s, valid_for_s=target.claim.valid_for_s, provenance=_token(EXPERIMENT_ID, seed, "ambiguity", "state_inconsistency"))
            return (*bundle, sign_claim(conflict, private_keys["independent-monitor"]))
        return bundle
    if block == "D_CONTEXT_ABLATION":
        context = cell["context"]
        if context == "replay":
            target_index = next(index for index, row in enumerate(bundle) if row.claim.key == "authorization_valid")
            target = bundle[target_index]
            replay = EvidenceClaim(source_id=target.claim.source_id, subject_id=target.claim.subject_id, key=target.claim.key, value=target.claim.value, epoch=target.claim.epoch, sequence=0, issued_at_s=target.claim.issued_at_s, valid_for_s=target.claim.valid_for_s, provenance=target.claim.provenance)
            changed = list(bundle)
            changed[target_index] = sign_claim(replay, private_keys[target.claim.source_id])
            return tuple(changed)
        if context == "evidence_loss":
            return tuple(row for row in bundle if row.claim.key != "authorization_valid")
    return bundle


def _attest(evidence: tuple[SignedEvidence, ...], *, seed: int, now_s: float = DECISION_TIME_S) -> AttestationResult:
    epoch = 1000 + (seed % 997)
    return verify_bundle(evidence, public_keys=_public_keys(), trusted_sources=frozenset(ALL_PRODUCERS), now_s=now_s, expected_epoch_by_subject={SUBJECT_ID: epoch}, minimum_sequence_by_source_epoch={(source_id, epoch): (-1 if source_id == "independent-monitor" else 0) for source_id in ALL_PRODUCERS})


def _security_signal(cell: dict[str, Any]) -> bool:
    if cell["block"] != "D_CONTEXT_ABLATION":
        return True
    return cell["context"] in {"unauthorized_command", "replay"}


def _authorization_available(cell: dict[str, Any]) -> bool:
    block = cell["block"]
    if block in {"A_PRIMARY_EVIDENCE_MECHANISM", "B_CONTACT_AUTHORIZATION", "E_ADVERSARY_BUDGET_STRESS"}:
        return CONTACT_CALIBRATION[_contact_regime(cell)].available_at(DECISION_TIME_S)
    if block == "C_FAULT_ATTACK_AMBIGUITY":
        return cell["ambiguity_family"] != "contact_or_authorization_loss"
    if block == "D_CONTEXT_ABLATION":
        return cell["context"] != "unauthorized_command"
    return True


def _observation(attestation: AttestationResult, cell: dict[str, Any], *, authorization_available: bool | None = None) -> ObservationSummary:
    rows = attestation.verifications
    current = attestation.current_values(subject_id=SUBJECT_ID)
    return ObservationSummary(signature_valid=bool(rows) and all(row.signature_valid for row in rows), source_trusted=bool(rows) and all(row.source_trusted for row in rows), fresh=bool(rows) and all(row.fresh for row in rows), epoch_valid=bool(rows) and all(row.epoch_valid for row in rows), contradictory=bool(attestation.contradictions), minimum_evidence_complete=all(criterion in current for criterion in RECOVERY_CRITERIA), security_signal=_security_signal(cell), authorization_available=_authorization_available(cell) if authorization_available is None else authorization_available)


def _select(cell: dict[str, Any], observation: ObservationSummary) -> Study2Action:
    if cell["block"] == "D_CONTEXT_ABLATION":
        return select_context_ablation(cell["selector"], observation)
    return select_action(Study2Policy(cell["policy"]), observation)


def _gate(action: Study2Action, attestation: AttestationResult) -> tuple[bool, tuple[str, ...]]:
    if action is not Study2Action.PROCEED_TO_RECOVERY_GATE:
        return False, ("selector_did_not_enter_recovery_gate",)
    current = attestation.current_values(subject_id=SUBJECT_ID)
    residual_visible = current.get("no_residual_unauthorized_state") is not True
    decision = evaluate_trusted_recovery_gate(attestation, subject_id=SUBJECT_ID, applicable_criteria=RECOVERY_CRITERIA, residual_unauthorized_state=residual_visible)
    return decision.trusted_recovery_allowed, decision.reasons


def _future_contact_recovery(cell: dict[str, Any], *, seed: int) -> tuple[bool, float | None, str | None]:
    if cell["block"] != "B_CONTACT_AUTHORIZATION":
        return False, None, None
    regime = _contact_regime(cell)
    next_contact = CONTACT_CALIBRATION[regime].next_contact_at_or_after(DECISION_TIME_S)
    if next_contact is None or next_contact <= DECISION_TIME_S:
        return False, None, None
    truth = {criterion: True for criterion in RECOVERY_CRITERIA}
    evidence = _base_evidence(seed=seed, truth=truth, issued_at_s=next_contact)
    attestation = _attest(evidence, seed=seed, now_s=next_contact)
    observation = _observation(attestation, cell, authorization_available=True)
    action = _select(cell, observation)
    trusted, _ = _gate(action, attestation)
    recovery_time = next_contact + RECOVERY_PROCESSING_S
    if trusted and recovery_time <= CENSOR_HORIZON_S:
        return True, recovery_time, action.value
    return False, None, action.value


def run_trial(*, cell_id: str, seed: int, run_id: str, mode: RuntimeMode = RuntimeMode.DEVELOPMENT, authorization: CampaignAuthorization | None = None, current_repository_commit: str = "", expected_authorization_bindings: dict[str, str] | None = None) -> dict[str, Any]:
    require_seed_mode(seed, mode)
    if mode is RuntimeMode.CAMPAIGN:
        if authorization is None:
            raise ValueError("campaign runtime requires an authorization envelope")
        authorization.validate(current_repository_commit=current_repository_commit, expected_bindings=expected_authorization_bindings or {})
    cell = _cell(cell_id)
    truth_values = _initial_truth(cell)
    evidence = _apply_cell_evidence(cell, seed=seed, truth=truth_values)
    attestation = _attest(evidence, seed=seed)
    observation = _observation(attestation, cell)
    action = _select(cell, observation)
    trusted_now, gate_reasons = _gate(action, attestation)
    trusted_recovery = trusted_now
    recovery_time_s: float | None = DECISION_TIME_S if trusted_now else None
    followup_action: str | None = None
    if not trusted_recovery:
        trusted_future, future_time, followup_action = _future_contact_recovery(cell, seed=seed)
        if trusted_future:
            trusted_recovery = True
            recovery_time_s = future_time
    hidden_prerequisites_satisfied = all(truth_values.values())
    hidden_residual_unauthorized = not truth_values["no_residual_unauthorized_state"]
    adjudication_truth = AdjudicationTruth(unauthorized_control_present=hidden_residual_unauthorized, recovery_prerequisites_satisfied=hidden_prerequisites_satisfied, mission_operation_safe=not hidden_residual_unauthorized)
    classification = classify_response(action, adjudication_truth)
    restrictive = action in {Study2Action.HOLD_AND_REQUIRE_EVIDENCE, Study2Action.RESTRICT_AND_REQUEST_AUTHORIZATION}
    terminal_state = "TRUSTED_RECOVERY" if trusted_recovery else "LIMITED_OPERATION" if action is Study2Action.PRESERVE_LIMITED_OPERATION else "RECOVERY_GATE_BLOCKED" if action is Study2Action.PROCEED_TO_RECOVERY_GATE else "HOLD_OR_RESTRICT"
    visible = {**asdict(observation), "action": action.value, "gate_reasons": list(gate_reasons), "followup_action": followup_action, "accepted_evidence_count": len(attestation.accepted), "rejected_evidence_count": len(attestation.rejected), "contradiction_count": len(attestation.contradictions)}
    adjudication = {**asdict(adjudication_truth), **asdict(classification), "cause": cell.get("cause"), "unsafe_trusted_recovery": trusted_recovery and not hidden_prerequisites_satisfied, "residual_unauthorized_state": hidden_residual_unauthorized, "legitimate_command_rejected": restrictive and hidden_prerequisites_satisfied}
    result = {
        "schema": 1,
        "experiment_id": EXPERIMENT_ID,
        "run_id": run_id,
        "trial_id": f"{EXPERIMENT_ID}:{cell_id}:{seed}",
        "cell_id": cell_id,
        "seed": seed,
        "runtime_mode": mode.value,
        "attempt_status": "VALID",
        "time_basis": "DETERMINISTIC_LOGICAL_SIL_TIME_NOT_WALL_CLOCK",
        "decision_time_s": DECISION_TIME_S,
        "censor_horizon_s": CENSOR_HORIZON_S,
        "visible_runtime": visible,
        "adjudication_only": adjudication,
        "evidence_qualified_trusted_recovery": trusted_recovery,
        "time_to_evidence_qualified_trusted_recovery_s": recovery_time_s,
        "time_to_recovery_right_censored": not trusted_recovery,
        "time_to_containment_s": DECISION_TIME_S if action is not Study2Action.PRESERVE_LIMITED_OPERATION else None,
        "ground_spacecraft_state_divergence": not truth_values["ground_spacecraft_state_agreed"],
        "response_selection_stability": True,
        "recovery_terminal_state": terminal_state,
        "oracle_was_selector_input": False,
        "automatic_retry_allowed": False,
        "automatic_next_trial_allowed": False,
    }
    result["observation_sha256"] = hashlib.sha256((json.dumps(result, ensure_ascii=True, allow_nan=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")).hexdigest()
    return result


def development_fixture_report() -> dict[str, Any]:
    cells = materialize_cell_matrix()["cells"]
    results = []
    for index, cell in enumerate(cells):
        seed = 2_900_001 + (index % 64)
        result = run_trial(cell_id=cell["cell_id"], seed=seed, run_id=f"DEV-P5-{cell['cell_id']}-{seed}", mode=RuntimeMode.DEVELOPMENT)
        results.append({"cell_id": result["cell_id"], "seed": result["seed"], "attempt_status": result["attempt_status"], "observation_sha256": result["observation_sha256"]})
    return {"schema": 1, "classification": "PHASE5_DEVELOPMENT_FIXTURE_REPORT", "development_only": True, "campaign_seed_consumed": False, "campaign_observations_generated": False, "cell_types_exercised": len(results), "all_valid": all(row["attempt_status"] == "VALID" for row in results), "results": results}
