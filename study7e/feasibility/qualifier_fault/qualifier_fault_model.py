from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Iterable

from study7e.src.aerc_design import PATHS, affected_paths


@dataclass(frozen=True, slots=True)
class Evidence:
    path: str
    scenario_id: int
    producer_role: str
    authorization: int
    source_id: int
    authority_id: int
    key_id: int
    epoch: int
    issued_tick: int
    sequence: int
    signature_valid: int = 1
    structurally_complete: bool = True

    def __post_init__(self) -> None:
        if self.path not in PATHS:
            raise ValueError("invalid path")
        if self.producer_role not in PATHS:
            raise ValueError("invalid producer role")
        if self.authorization not in (0, 1):
            raise ValueError("authorization must be binary")
        if self.signature_valid not in (0, 1):
            raise ValueError("signature_valid must be binary")

    def body_identity(self) -> tuple[object, ...]:
        return (
            self.scenario_id,
            self.producer_role,
            self.authorization,
            self.source_id,
            self.authority_id,
            self.key_id,
            self.epoch,
            self.issued_tick,
            self.sequence,
        )


@dataclass(frozen=True, slots=True)
class QualifierContext:
    expected_scenario_id: int
    expected_epoch: int
    now_tick: int
    freshness_max_age_ticks: int
    trusted_sources: dict[str, frozenset[int]]
    known_keys: dict[str, frozenset[int]]


@dataclass(frozen=True, slots=True)
class PathState:
    last_sequence: int | None = None
    last_body: tuple[object, ...] | None = None
    contradicted: bool = False


ZERO_FEATURES = {
    "signature_valid": 0,
    "source_trusted": 0,
    "fresh": 0,
    "epoch_valid": 0,
    "noncontradictory": 0,
    "complete": 0,
    "authorization": 0,
}


def nominal_evidence(path: str, true_authorization: int, *, scenario_id: int = 0x53374901,
                     epoch: int = 7, issued_tick: int = 100, sequence: int = 1) -> Evidence:
    if path == "primary":
        source_id, authority_id, key_id = 0x1001, 0x3001, 0x2001
    elif path == "corroborator":
        source_id, authority_id, key_id = 0x1002, 0x3002, 0x2002
    else:
        raise ValueError(path)

    return Evidence(
        path=path,
        scenario_id=scenario_id,
        producer_role=path,
        authorization=true_authorization,
        source_id=source_id,
        authority_id=authority_id,
        key_id=key_id,
        epoch=epoch,
        issued_tick=issued_tick,
        sequence=sequence,
    )


def default_context(*, scenario_id: int = 0x53374901, epoch: int = 7,
                    now_tick: int = 100, freshness_max_age_ticks: int = 5) -> QualifierContext:
    return QualifierContext(
        expected_scenario_id=scenario_id,
        expected_epoch=epoch,
        now_tick=now_tick,
        freshness_max_age_ticks=freshness_max_age_ticks,
        trusted_sources={
            "primary": frozenset({0x1001}),
            "corroborator": frozenset({0x1002}),
        },
        known_keys={
            "primary": frozenset({0x2001}),
            "corroborator": frozenset({0x2002}),
        },
    )


def qualify_evidence(evidence: Evidence | None, context: QualifierContext,
                     state: PathState) -> tuple[dict[str, int], PathState]:
    if evidence is None:
        return dict(ZERO_FEATURES), state
    if not evidence.structurally_complete:
        return dict(ZERO_FEATURES), state
    if evidence.scenario_id != context.expected_scenario_id:
        return dict(ZERO_FEATURES), state

    role = evidence.producer_role
    source_trusted = int(evidence.source_id in context.trusted_sources.get(role, frozenset()))
    key_known = evidence.key_id in context.known_keys.get(role, frozenset())
    signature_valid = int(bool(evidence.signature_valid) and key_known)
    epoch_valid = int(evidence.epoch == context.expected_epoch)
    fresh = int(
        evidence.issued_tick <= context.now_tick
        and (context.now_tick - evidence.issued_tick) <= context.freshness_max_age_ticks
    )

    next_state = state
    if signature_valid:
        body = evidence.body_identity()
        if state.last_sequence is None:
            next_state = PathState(evidence.sequence, body, state.contradicted)
        elif evidence.sequence > state.last_sequence:
            next_state = PathState(evidence.sequence, body, state.contradicted)
        elif evidence.sequence == state.last_sequence:
            if body != state.last_body:
                next_state = PathState(state.last_sequence, state.last_body, True)
        else:
            next_state = PathState(state.last_sequence, state.last_body, True)

    features = {
        "signature_valid": signature_valid,
        "source_trusted": source_trusted,
        "fresh": fresh,
        "epoch_valid": epoch_valid,
        "noncontradictory": int(not next_state.contradicted),
        "complete": 1,
        "authorization": evidence.authorization,
    }
    return features, next_state


def qualify_stream(evidence_items: Iterable[Evidence], context: QualifierContext,
                   state: PathState | None = None) -> tuple[dict[str, int], PathState]:
    current_state = state or PathState()
    features = dict(ZERO_FEATURES)
    for evidence in evidence_items:
        features, current_state = qualify_evidence(evidence, context, current_state)
    return features, current_state


def apply_fault(topology: str, fault_profile: str, true_authorization: int,
                *, scenario_id: int = 0x53374901, epoch: int = 7,
                issued_tick: int = 100, freshness_max_age_ticks: int = 5) -> dict[str, list[Evidence]]:
    streams = {
        path: [nominal_evidence(path, true_authorization, scenario_id=scenario_id,
                                epoch=epoch, issued_tick=issued_tick, sequence=1)]
        for path in PATHS
    }

    affected = affected_paths(topology, fault_profile)

    if fault_profile == "F0":
        return streams

    if fault_profile in {"F1", "F2", "F3", "F4", "F10"}:
        for path in affected:
            streams[path] = [replace(streams[path][0], authorization=1 - true_authorization)]
        return streams

    if fault_profile in {"F5", "F6"}:
        for path in affected:
            streams[path] = [
                replace(
                    streams[path][0],
                    issued_tick=issued_tick - freshness_max_age_ticks - 1,
                )
            ]
        return streams

    if fault_profile in {"F7", "F8"}:
        for path in affected:
            streams[path] = []
        return streams

    if fault_profile == "F9":
        for path in affected:
            streams[path] = [
                replace(streams[path][0], epoch=epoch ^ 1, signature_valid=0)
            ]
        return streams

    if fault_profile == "F11":
        for path in affected:
            streams[path] = [
                replace(
                    streams[path][0],
                    authorization=1 - true_authorization,
                    epoch=epoch ^ 1,
                    signature_valid=0,
                )
            ]
        return streams

    if fault_profile == "F12":
        for path in affected:
            first = streams[path][0]
            second = replace(first, authorization=1 - true_authorization)
            streams[path] = [first, second]
        return streams

    raise KeyError(fault_profile)


def changed_paths(streams: dict[str, list[Evidence]], true_authorization: int,
                  *, scenario_id: int = 0x53374901, epoch: int = 7,
                  issued_tick: int = 100) -> frozenset[str]:
    changed: set[str] = set()
    for path in PATHS:
        nominal = [nominal_evidence(path, true_authorization, scenario_id=scenario_id,
                                    epoch=epoch, issued_tick=issued_tick, sequence=1)]
        if streams[path] != nominal:
            changed.add(path)
    return frozenset(changed)
