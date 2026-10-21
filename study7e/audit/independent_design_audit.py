#!/usr/bin/env python3
from __future__ import annotations

import json
from itertools import product
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class AuditError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AuditError(message)


def load(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(value, dict), f"{path} must be a JSON object")
    return value


def independent_domain_map(topology: dict, domains: tuple[str, ...]) -> dict[str, dict[str, str]]:
    separated = frozenset(topology["separate"])
    require(separated.issubset(domains), "unknown separated trust domain")
    out = {"primary": {}, "corroborator": {}}
    for domain in domains:
        if domain in separated:
            out["primary"][domain] = f"primary:{domain}"
            out["corroborator"][domain] = f"corroborator:{domain}"
        else:
            shared = f"shared:{domain}"
            out["primary"][domain] = shared
            out["corroborator"][domain] = shared
    return out


def independent_affected_paths(
    topology: dict,
    profile: dict,
    domains: tuple[str, ...],
) -> frozenset[str]:
    propagation = profile["propagation"]
    if propagation == "none":
        return frozenset()

    target = profile["path"]
    require(target in {"primary", "corroborator"}, "invalid target path")

    if propagation == "message_local":
        return frozenset({target})

    mapping = independent_domain_map(topology, domains)

    if propagation == "domain_alias":
        domain = profile["domain"]
        require(domain in domains, "fault references unknown domain")
        target_id = mapping[target][domain]
        return frozenset(
            path for path in ("primary", "corroborator")
            if mapping[path][domain] == target_id
        )

    if propagation == "union_domain_alias":
        affected: set[str] = set()
        for domain in profile["domains"]:
            require(domain in domains, "compound fault references unknown domain")
            target_id = mapping[target][domain]
            affected.update(
                path for path in ("primary", "corroborator")
                if mapping[path][domain] == target_id
            )
        return frozenset(affected)

    raise AuditError(f"unknown propagation mode: {propagation}")


def expected_counts(fault_ids: tuple[str, ...]) -> dict[str, int]:
    tr1 = len(tuple(product((0, 1), (0, 1), range(3), range(6))))
    tr0 = len(tuple(product((0, 1), (0, 1), range(3), range(1))))
    unseen_faults = tuple(fid for fid in fault_ids if 6 <= int(fid[1:]) <= 12)
    e1 = len(tuple(product((0, 1), (0, 1), range(3), unseen_faults)))
    e2 = len(tuple(product((0, 1), (0, 1), range(2), fault_ids)))
    c0 = len(tuple(product((0, 1), (0, 1), range(2), range(1))))
    training = tr1 + tr0
    evaluation = e1 + e2 + c0
    return {
        "TR1": tr1,
        "TR0": tr0,
        "TRAINING": training,
        "E1": e1,
        "E2": e2,
        "C0": c0,
        "TOTAL": training + evaluation,
        "EVALUATION": evaluation,
        "POLICY_DECISIONS": evaluation * 4,
    }


def main() -> int:
    topologies_doc = load(ROOT / "study7e/configs/topologies.json")
    faults_doc = load(ROOT / "study7e/configs/fault_profiles.json")
    protocol = load(ROOT / "study7e/PROTOCOL_DRAFT.json")
    training = load(ROOT / "study7e/configs/learner_candidate.json")

    domains = tuple(topologies_doc["trust_domains"])
    require(domains == ("source", "key", "execution", "transport", "authority"), "trust-domain drift")

    topologies = topologies_doc["topologies"]
    faults = faults_doc["profiles"]
    require(tuple(topologies) == (
        "T0_SHARED_ALL",
        "T1_SEPARATE_SOURCE_EXEC",
        "T2_SEPARATE_SOURCE_KEY_EXEC",
        "T3_SEPARATE_THROUGH_TRANSPORT",
        "T4_SEPARATE_ALL",
    ), "topology ordering/identity drift")
    require(tuple(faults) == tuple(f"F{i}" for i in range(13)), "fault identity drift")

    expected_separation = {
        "T0_SHARED_ALL": set(),
        "T1_SEPARATE_SOURCE_EXEC": {"source", "execution"},
        "T2_SEPARATE_SOURCE_KEY_EXEC": {"source", "key", "execution"},
        "T3_SEPARATE_THROUGH_TRANSPORT": {"source", "key", "execution", "transport"},
        "T4_SEPARATE_ALL": set(domains),
    }
    for topology_id, expected in expected_separation.items():
        actual = set(topologies[topology_id]["separate"])
        require(actual == expected, f"{topology_id} separation drift")

    # Independent propagation matrix. This does not import production design code.
    matrix: dict[str, dict[str, list[str]]] = {}
    domain_coverage: set[str] = set()
    for topology_id, topology in topologies.items():
        matrix[topology_id] = {}
        for fault_id, profile in faults.items():
            paths = independent_affected_paths(topology, profile, domains)
            matrix[topology_id][fault_id] = sorted(paths)
            if profile.get("domain"):
                domain_coverage.add(profile["domain"])
            for domain in profile.get("domains", []):
                domain_coverage.add(domain)

    require(domain_coverage == set(domains), f"fault/domain coverage gap: {sorted(set(domains) - domain_coverage)}")
    require(matrix["T0_SHARED_ALL"]["F12"] == ["corroborator", "primary"], "T0 F12 propagation drift")
    require(matrix["T1_SEPARATE_SOURCE_EXEC"]["F12"] == ["primary"], "T1 F12 propagation drift")
    require(matrix["T0_SHARED_ALL"]["F3"] == ["corroborator", "primary"], "T0 key propagation drift")
    require(matrix["T2_SEPARATE_SOURCE_KEY_EXEC"]["F3"] == ["primary"], "T2 key propagation drift")
    require(matrix["T3_SEPARATE_THROUGH_TRANSPORT"]["F10"] == ["corroborator", "primary"], "T3 authority propagation drift")
    require(matrix["T4_SEPARATE_ALL"]["F10"] == ["primary"], "T4 authority propagation drift")

    counts = expected_counts(tuple(faults))
    require(counts == {
        "TR1": 72,
        "TR0": 12,
        "TRAINING": 84,
        "E1": 84,
        "E2": 104,
        "C0": 8,
        "TOTAL": 280,
        "EVALUATION": 196,
        "POLICY_DECISIONS": 784,
    }, f"independent cardinality drift: {counts}")

    expected = protocol["expected_counts"]
    require(expected["total_manifest_scenarios"] == counts["TOTAL"], "protocol total mismatch")
    require(expected["training_scenarios"] == counts["TRAINING"], "protocol training mismatch")
    require(expected["canonical_evaluation_scenarios"] == counts["EVALUATION"], "protocol evaluation mismatch")
    require(expected["canonical_evaluation_policy_decisions"] == counts["POLICY_DECISIONS"], "protocol decision mismatch")

    require(training["training_blocks"] == ["TR0", "TR1"], "learner training-block drift")
    require(training["prohibited_training_blocks"] == ["E1", "E2", "C0"], "learner evaluation-leakage guard drift")
    require(training["training_scenarios"] == 84, "learner training count drift")
    require(training["model_training_performed"] is False, "pre-canonical model training unexpectedly recorded")
    require(training["production_model_freeze_performed"] is False, "pre-canonical model freeze unexpectedly recorded")

    print("Study 7E independent pre-canonical design audit: PASS")
    print("trust_domains_covered=5/5")
    print("fault_profiles=13")
    print("manifest_total=280")
    print("training_scenarios=84")
    print("evaluation_scenarios=196")
    print("planned_policy_decisions=784")
    print("model_training_performed=false")
    print("scientific_results_generated=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
