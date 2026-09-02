from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Iterable

EXPERIMENT_ID = "S3-K4E-001"
EPOCH_S = 5
HORIZON_S = 240
EVIDENCE_TTL_S = 5
ONSET_PHASES = tuple(range(10, 240, 5))
CONTACT_WINDOWS = {
    "K0": ((0, 240),),
    "K4": ((25, 35), (75, 90), (145, 165), (220, 240)),
}
POLICIES = (
    "S2_B0_FAIL_CLOSED",
    "S2_B2_RISK_THRESHOLD",
    "S2_S1_EVIDENCE_AWARE",
)
EVIDENCE = ("V0", "V4", "V5")
PERSISTENCE = {"V0": ("NONE",), "V4": ("ONE_SHOT", "PERSISTENT"), "V5": ("ONE_SHOT", "PERSISTENT")}
PERMISSIVE_ACTIONS = frozenset({"PRESERVE_LIMITED_OPERATION", "PROCEED_TO_RECOVERY_GATE"})
PROTECTIVE_ACTIONS = frozenset({"HOLD_AND_REQUIRE_EVIDENCE", "RESTRICT_AND_REQUEST_AUTHORIZATION"})


@dataclass(frozen=True)
class Cell:
    contact: str
    evidence: str
    persistence: str
    policy: str

    @property
    def cell_id(self) -> str:
        return f"{self.contact}_{self.evidence}_{self.persistence}_{self.policy}"


@dataclass(frozen=True)
class EvidenceRecord:
    received_at_s: int
    claim_authorization_valid: bool
    signature_valid: bool
    treatment_affected: bool


@dataclass(frozen=True)
class EpochRecord:
    experiment_id: str
    trajectory_id: str
    cell_id: str
    contact: str
    evidence: str
    persistence: str
    policy: str
    onset_s: int
    t_s: int
    contact_available: bool
    hidden_authorization_valid: bool
    security_signal: bool
    record_present: bool
    record_age_s: int | None
    record_fresh: bool
    signature_valid: bool
    claim_authorization_valid: bool | None
    treatment_affected: bool
    evidence_qualified: bool
    action: str
    gate_qualified: bool
    unsafe_permissive: bool
    unsafe_qualified: bool
    protective: bool


@dataclass(frozen=True)
class TrajectorySummary:
    experiment_id: str
    trajectory_id: str
    cell_id: str
    contact: str
    evidence: str
    persistence: str
    policy: str
    onset_s: int
    post_onset_epochs: int
    affected_received_records: int
    unsafe_permissive_epochs: int
    unsafe_permissive_epoch_rate: float
    unsafe_qualified_epochs: int
    unsafe_qualified_epoch_rate: float
    unsafe_qualified_exposure_s: int
    unsafe_qualified_episode_count: int
    protective_epochs: int
    protective_epoch_rate: float
    action_transition_count: int


def contact_available(regime: str, t_s: int) -> bool:
    return any(start <= t_s <= end for start, end in CONTACT_WINDOWS[regime])


def cells() -> tuple[Cell, ...]:
    rows: list[Cell] = []
    for contact in CONTACT_WINDOWS:
        for evidence in EVIDENCE:
            for persistence in PERSISTENCE[evidence]:
                for policy in POLICIES:
                    rows.append(Cell(contact, evidence, persistence, policy))
    output = tuple(rows)
    if len(output) != 30 or len({row.cell_id for row in output}) != 30:
        raise AssertionError("Study-3 cell matrix must contain exactly 30 unique cells")
    return output


def trajectory_specs() -> tuple[tuple[Cell, int], ...]:
    rows = tuple((cell, onset) for cell in cells() for onset in ONSET_PHASES)
    if len(rows) != 1380:
        raise AssertionError("Study-3 finite population must contain exactly 1,380 trajectories")
    return rows


def select_action(policy: str, *, evidence_qualified: bool, security_signal: bool, contact: bool) -> str:
    if policy == "S2_B0_FAIL_CLOSED":
        return "PROCEED_TO_RECOVERY_GATE" if evidence_qualified else "RESTRICT_AND_REQUEST_AUTHORIZATION"
    if policy == "S2_B2_RISK_THRESHOLD":
        if not evidence_qualified:
            return "HOLD_AND_REQUIRE_EVIDENCE"
        return "RESTRICT_AND_REQUEST_AUTHORIZATION" if security_signal else "PRESERVE_LIMITED_OPERATION"
    if policy == "S2_S1_EVIDENCE_AWARE":
        if not evidence_qualified:
            return "HOLD_AND_REQUIRE_EVIDENCE"
        if security_signal and not contact:
            return "RESTRICT_AND_REQUEST_AUTHORIZATION"
        return "PROCEED_TO_RECOVERY_GATE"
    raise ValueError(f"unknown policy: {policy}")


def _new_record(cell: Cell, *, t_s: int, onset_s: int, affected_already: bool) -> EvidenceRecord:
    post_onset = t_s >= onset_s
    truthful_value = not post_onset
    affected = False
    if post_onset and cell.evidence in {"V4", "V5"}:
        affected = cell.persistence == "PERSISTENT" or not affected_already
    if not affected:
        return EvidenceRecord(t_s, truthful_value, True, False)
    if cell.evidence == "V4":
        return EvidenceRecord(t_s, True, False, True)
    if cell.evidence == "V5":
        return EvidenceRecord(t_s, True, True, True)
    raise AssertionError("unhandled treatment")


def run_trajectory(cell: Cell, onset_s: int) -> tuple[tuple[EpochRecord, ...], TrajectorySummary]:
    if onset_s not in ONSET_PHASES:
        raise ValueError("onset is outside the frozen phase grid")
    latest: EvidenceRecord | None = None
    affected_received_records = 0
    epochs: list[EpochRecord] = []
    trajectory_id = f"{EXPERIMENT_ID}:{cell.cell_id}:T{onset_s:03d}"

    for t_s in range(0, HORIZON_S + EPOCH_S, EPOCH_S):
        contact = contact_available(cell.contact, t_s)
        if contact:
            latest = _new_record(
                cell,
                t_s=t_s,
                onset_s=onset_s,
                affected_already=affected_received_records > 0,
            )
            if latest.treatment_affected:
                affected_received_records += 1

        age = None if latest is None else t_s - latest.received_at_s
        fresh = latest is not None and 0 <= age <= EVIDENCE_TTL_S
        signature_valid = latest.signature_valid if latest is not None else False
        evidence_qualified = latest is not None and fresh and signature_valid
        claim_value = latest.claim_authorization_valid if latest is not None else None
        security_signal = t_s >= onset_s
        hidden_authorization_valid = t_s < onset_s

        action = select_action(
            cell.policy,
            evidence_qualified=evidence_qualified,
            security_signal=security_signal,
            contact=contact,
        )
        gate_qualified = (
            action == "PROCEED_TO_RECOVERY_GATE"
            and evidence_qualified
            and claim_value is True
        )
        unsafe_permissive = (
            t_s >= onset_s
            and not hidden_authorization_valid
            and action in PERMISSIVE_ACTIONS
        )
        unsafe_qualified = (
            t_s >= onset_s
            and not hidden_authorization_valid
            and gate_qualified
        )
        protective = t_s >= onset_s and action in PROTECTIVE_ACTIONS

        epochs.append(
            EpochRecord(
                experiment_id=EXPERIMENT_ID,
                trajectory_id=trajectory_id,
                cell_id=cell.cell_id,
                contact=cell.contact,
                evidence=cell.evidence,
                persistence=cell.persistence,
                policy=cell.policy,
                onset_s=onset_s,
                t_s=t_s,
                contact_available=contact,
                hidden_authorization_valid=hidden_authorization_valid,
                security_signal=security_signal,
                record_present=latest is not None,
                record_age_s=age,
                record_fresh=fresh,
                signature_valid=signature_valid,
                claim_authorization_valid=claim_value,
                treatment_affected=latest.treatment_affected if latest is not None else False,
                evidence_qualified=evidence_qualified,
                action=action,
                gate_qualified=gate_qualified,
                unsafe_permissive=unsafe_permissive,
                unsafe_qualified=unsafe_qualified,
                protective=protective,
            )
        )

    post = [row for row in epochs if row.t_s >= onset_s]
    unsafe_flags = [row.unsafe_qualified for row in post]
    episodes = sum(flag and (index == 0 or not unsafe_flags[index - 1]) for index, flag in enumerate(unsafe_flags))
    transitions = sum(post[index].action != post[index - 1].action for index in range(1, len(post)))
    unsafe_permissive_epochs = sum(row.unsafe_permissive for row in post)
    unsafe_qualified_epochs = sum(row.unsafe_qualified for row in post)
    protective_epochs = sum(row.protective for row in post)
    denominator = len(post)

    summary = TrajectorySummary(
        experiment_id=EXPERIMENT_ID,
        trajectory_id=trajectory_id,
        cell_id=cell.cell_id,
        contact=cell.contact,
        evidence=cell.evidence,
        persistence=cell.persistence,
        policy=cell.policy,
        onset_s=onset_s,
        post_onset_epochs=denominator,
        affected_received_records=affected_received_records,
        unsafe_permissive_epochs=unsafe_permissive_epochs,
        unsafe_permissive_epoch_rate=unsafe_permissive_epochs / denominator,
        unsafe_qualified_epochs=unsafe_qualified_epochs,
        unsafe_qualified_epoch_rate=unsafe_qualified_epochs / denominator,
        unsafe_qualified_exposure_s=unsafe_qualified_epochs * EPOCH_S,
        unsafe_qualified_episode_count=episodes,
        protective_epochs=protective_epochs,
        protective_epoch_rate=protective_epochs / denominator,
        action_transition_count=transitions,
    )
    return tuple(epochs), summary


def run_population() -> tuple[tuple[EpochRecord, ...], tuple[TrajectorySummary, ...]]:
    all_epochs: list[EpochRecord] = []
    summaries: list[TrajectorySummary] = []
    for cell, onset in trajectory_specs():
        epochs, summary = run_trajectory(cell, onset)
        all_epochs.extend(epochs)
        summaries.append(summary)
    if len(summaries) != 1380:
        raise AssertionError("population membership drift")
    return tuple(all_epochs), tuple(summaries)


def as_rows(values: Iterable[object]) -> list[dict[str, object]]:
    return [asdict(value) for value in values]
