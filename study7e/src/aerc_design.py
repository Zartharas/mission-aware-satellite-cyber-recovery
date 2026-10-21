from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from itertools import product
from typing import Iterable, Mapping

EXPERIMENT_ID = "S7E-AERC-001"

TRUST_DOMAINS = ("source", "key", "execution", "transport", "authority")
PATHS = ("primary", "corroborator")

TOPOLOGY_SEPARATION: dict[str, frozenset[str]] = {
    "T0_SHARED_ALL": frozenset(),
    "T1_SEPARATE_SOURCE_EXEC": frozenset({"source", "execution"}),
    "T2_SEPARATE_SOURCE_KEY_EXEC": frozenset({"source", "key", "execution"}),
    "T3_SEPARATE_THROUGH_TRANSPORT": frozenset({"source", "key", "execution", "transport"}),
    "T4_SEPARATE_ALL": frozenset(TRUST_DOMAINS),
}

BASE_FEATURES = (
    "primary_signature_valid",
    "primary_source_trusted",
    "primary_fresh",
    "primary_epoch_valid",
    "primary_noncontradictory",
    "primary_complete",
    "primary_authorization",
    "health_ready",
    "security_signal",
)

CORR_FEATURES = (
    "corr_signature_valid",
    "corr_source_trusted",
    "corr_fresh",
    "corr_epoch_valid",
    "corr_noncontradictory",
    "corr_complete",
    "corr_authorization",
)

EXTENDED_FEATURES = BASE_FEATURES + CORR_FEATURES

PRIVILEGED_FIELDS = frozenset(
    {
        "true_authorization",
        "true_health_ready",
        "objective_action",
        "fault_profile",
        "topology",
        "domain_alias_map",
    }
)

FAULT_PROFILES: dict[str, dict[str, object]] = {
    "F0": {"name": "NOMINAL", "path": None, "domain": None, "propagation": "none"},
    "F1": {"name": "PRIMARY_SOURCE_FALSE", "path": "primary", "domain": "source", "propagation": "domain_alias"},
    "F2": {"name": "CORR_SOURCE_FALSE", "path": "corroborator", "domain": "source", "propagation": "domain_alias"},
    "F3": {"name": "PRIMARY_KEY_COMPROMISE", "path": "primary", "domain": "key", "propagation": "domain_alias"},
    "F4": {"name": "CORR_KEY_COMPROMISE", "path": "corroborator", "domain": "key", "propagation": "domain_alias"},
    "F5": {"name": "PRIMARY_FRESHNESS_DELAY", "path": "primary", "domain": None, "propagation": "message_local"},
    "F6": {"name": "CORR_FRESHNESS_DELAY", "path": "corroborator", "domain": None, "propagation": "message_local"},
    "F7": {"name": "PRIMARY_MESSAGE_LOSS", "path": "primary", "domain": None, "propagation": "message_local"},
    "F8": {"name": "CORR_MESSAGE_LOSS", "path": "corroborator", "domain": None, "propagation": "message_local"},
    "F9": {"name": "PRIMARY_TRANSPORT_COMPROMISE", "path": "primary", "domain": "transport", "propagation": "domain_alias"},
    "F10": {"name": "PRIMARY_AUTHORITY_COMPROMISE", "path": "primary", "domain": "authority", "propagation": "domain_alias"},
    "F11": {
        "name": "COMPOUND_AUTHORITY_TRANSPORT",
        "path": "primary",
        "domains": ("authority", "transport"),
        "propagation": "union_domain_alias",
    },
    "F12": {
        "name": "PRIMARY_EXECUTION_COMPROMISE",
        "path": "primary",
        "domain": "execution",
        "propagation": "domain_alias",
    },
}


@dataclass(frozen=True, slots=True)
class Scenario:
    scenario_id: str
    block: str
    true_authorization: int
    true_health_ready: int
    security_signal: int
    topology: str
    fault_profile: str

    def __post_init__(self) -> None:
        for name, value in (
            ("true_authorization", self.true_authorization),
            ("true_health_ready", self.true_health_ready),
            ("security_signal", self.security_signal),
        ):
            if value not in (0, 1):
                raise ValueError(f"{name} must be 0 or 1")
        if self.topology not in TOPOLOGY_SEPARATION:
            raise ValueError(f"unknown topology: {self.topology}")
        if self.fault_profile not in FAULT_PROFILES:
            raise ValueError(f"unknown fault profile: {self.fault_profile}")


def domain_map(topology: str) -> dict[str, dict[str, str]]:
    if topology not in TOPOLOGY_SEPARATION:
        raise KeyError(topology)
    separated = TOPOLOGY_SEPARATION[topology]
    mapping: dict[str, dict[str, str]] = {"primary": {}, "corroborator": {}}
    for domain in TRUST_DOMAINS:
        if domain in separated:
            mapping["primary"][domain] = f"primary:{domain}"
            mapping["corroborator"][domain] = f"corroborator:{domain}"
        else:
            shared = f"shared:{domain}"
            mapping["primary"][domain] = shared
            mapping["corroborator"][domain] = shared
    return mapping


def affected_paths(topology: str, fault_profile: str) -> frozenset[str]:
    if fault_profile not in FAULT_PROFILES:
        raise KeyError(fault_profile)
    profile = FAULT_PROFILES[fault_profile]
    propagation = str(profile["propagation"])

    if propagation == "none":
        return frozenset()

    target_path = str(profile["path"])
    if target_path not in PATHS:
        raise ValueError(f"invalid target path for {fault_profile}: {target_path}")

    if propagation == "message_local":
        return frozenset({target_path})

    mapping = domain_map(topology)
    if propagation == "domain_alias":
        domain = str(profile["domain"])
        target_domain_id = mapping[target_path][domain]
        return frozenset(path for path in PATHS if mapping[path][domain] == target_domain_id)

    if propagation == "union_domain_alias":
        domains = tuple(str(x) for x in profile["domains"])
        affected: set[str] = set()
        for domain in domains:
            target_domain_id = mapping[target_path][domain]
            affected.update(path for path in PATHS if mapping[path][domain] == target_domain_id)
        return frozenset(affected)

    raise ValueError(f"unknown propagation mode: {propagation}")


def objective_action(scenario: Scenario) -> str:
    if scenario.security_signal and scenario.true_authorization and scenario.true_health_ready:
        return "ENTER_RECOVERY_GATE"
    return "HOLD"


def _scenario_rows(
    block: str,
    topologies: Iterable[str],
    faults: Iterable[str],
    security_signal: int,
) -> list[Scenario]:
    rows: list[Scenario] = []
    counter = 0
    for auth, health, topology, fault in product(
        (0, 1),
        (0, 1),
        tuple(topologies),
        tuple(faults),
    ):
        counter += 1
        rows.append(
            Scenario(
                scenario_id=f"{block}-{counter:03d}",
                block=block,
                true_authorization=auth,
                true_health_ready=health,
                security_signal=security_signal,
                topology=topology,
                fault_profile=fault,
            )
        )
    return rows


def build_scenario_manifest() -> list[Scenario]:
    training_signal = _scenario_rows(
        "TR1",
        ("T0_SHARED_ALL", "T1_SEPARATE_SOURCE_EXEC", "T2_SEPARATE_SOURCE_KEY_EXEC"),
        ("F0", "F1", "F2", "F3", "F4", "F5"),
        1,
    )
    training_no_signal = _scenario_rows(
        "TR0",
        ("T0_SHARED_ALL", "T1_SEPARATE_SOURCE_EXEC", "T2_SEPARATE_SOURCE_KEY_EXEC"),
        ("F0",),
        0,
    )
    e1 = _scenario_rows(
        "E1",
        ("T0_SHARED_ALL", "T1_SEPARATE_SOURCE_EXEC", "T2_SEPARATE_SOURCE_KEY_EXEC"),
        ("F6", "F7", "F8", "F9", "F10", "F11", "F12"),
        1,
    )
    e2 = _scenario_rows(
        "E2",
        ("T3_SEPARATE_THROUGH_TRANSPORT", "T4_SEPARATE_ALL"),
        tuple(FAULT_PROFILES),
        1,
    )
    c0 = _scenario_rows(
        "C0",
        ("T3_SEPARATE_THROUGH_TRANSPORT", "T4_SEPARATE_ALL"),
        ("F0",),
        0,
    )
    return training_signal + training_no_signal + e1 + e2 + c0


def manifest_counts(scenarios: Iterable[Scenario]) -> dict[str, int]:
    counts = {"TR1": 0, "TR0": 0, "E1": 0, "E2": 0, "C0": 0}
    for scenario in scenarios:
        counts[scenario.block] += 1
    counts["TRAINING_SCENARIOS"] = counts["TR1"] + counts["TR0"]
    counts["TOTAL"] = counts["TRAINING_SCENARIOS"] + counts["E1"] + counts["E2"] + counts["C0"]
    counts["CANONICAL_EVAL_SCENARIOS"] = counts["E1"] + counts["E2"] + counts["C0"]
    counts["CANONICAL_EVAL_POLICY_DECISIONS"] = counts["CANONICAL_EVAL_SCENARIOS"] * 4
    return counts


def _require_binary_features(snapshot: Mapping[str, object], features: Iterable[str]) -> tuple[int, ...]:
    values: list[int] = []
    for feature in features:
        if feature not in snapshot:
            raise KeyError(f"missing feature: {feature}")
        value = snapshot[feature]
        if value not in (0, 1, False, True):
            raise ValueError(f"{feature} must be binary")
        values.append(int(value))
    return tuple(values)


def project_base(snapshot: Mapping[str, object]) -> tuple[int, ...]:
    if PRIVILEGED_FIELDS.intersection(snapshot.keys()):
        raise ValueError("privileged research-only field present in policy snapshot")
    return _require_binary_features(snapshot, BASE_FEATURES)


def project_corroborated(snapshot: Mapping[str, object]) -> tuple[int, ...]:
    if PRIVILEGED_FIELDS.intersection(snapshot.keys()):
        raise ValueError("privileged research-only field present in policy snapshot")
    return _require_binary_features(snapshot, EXTENDED_FEATURES)


def canonical_policy_input_bytes(policy_id: str, vector: tuple[int, ...]) -> bytes:
    payload = {"schema": 1, "experiment_id": EXPERIMENT_ID, "policy": policy_id, "features": vector}
    return json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")


def paired_input_hashes(snapshot: Mapping[str, object]) -> dict[str, str]:
    base = project_base(snapshot)
    extended = project_corroborated(snapshot)

    # The pair hashes intentionally omit policy identity. The contract is equality of
    # the exact feature bytes supplied to paired policy adapters.
    base_bytes = json.dumps(base, separators=(",", ":")).encode("utf-8")
    corr_bytes = json.dumps(extended, separators=(",", ":")).encode("utf-8")
    return {
        "D0_BASE": hashlib.sha256(base_bytes).hexdigest(),
        "L0_BASE": hashlib.sha256(base_bytes).hexdigest(),
        "D1_CORROBORATED": hashlib.sha256(corr_bytes).hexdigest(),
        "L1_CORROBORATED": hashlib.sha256(corr_bytes).hexdigest(),
    }


def d0_base(vector: tuple[int, ...]) -> str:
    if len(vector) != len(BASE_FEATURES):
        raise ValueError("D0 input length mismatch")
    proceed = all(vector[:6]) and vector[6] == 1 and vector[7] == 1 and vector[8] == 1
    return "ENTER_RECOVERY_GATE" if proceed else "HOLD"


def d1_corroborated(vector: tuple[int, ...]) -> str:
    if len(vector) != len(EXTENDED_FEATURES):
        raise ValueError("D1 input length mismatch")
    base_ok = all(vector[:6]) and vector[6] == 1 and vector[7] == 1 and vector[8] == 1
    corr_offset = len(BASE_FEATURES)
    corr_quality = vector[corr_offset : corr_offset + 6]
    corr_auth = vector[corr_offset + 6]
    proceed = base_ok and all(corr_quality) and corr_auth == 1
    return "ENTER_RECOVERY_GATE" if proceed else "HOLD"
