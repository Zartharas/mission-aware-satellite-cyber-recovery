from __future__ import annotations

import hashlib
import json
import subprocess
import unittest
from pathlib import Path

from study7e.src.aerc_design import TRUST_DOMAINS, build_scenario_manifest, domain_map

ROOT = Path(__file__).resolve().parents[2]
FC = json.loads((ROOT / "study7e/configs/protocol_environment_freeze_candidate_001.json").read_text())
EP = json.loads((ROOT / "study7e/configs/execution_parameters_candidate_2026-09-23.json").read_text())
APPROVAL = json.loads((ROOT / "study7e/configs/ep_author_approval_2026-09-23.json").read_text())
STATE = json.loads((ROOT / "study7e/FREEZE_CANDIDATE_STATE.json").read_text())
FREEZE = json.loads((ROOT / "study7e/FREEZE_MANIFEST_001.json").read_text())


def opaque_u32(namespace: str, label: str, used: set[int]) -> int:
    retry = 0
    while True:
        material = f"S7E-AERC-001|{namespace}|{label}|{retry}".encode()
        value = int.from_bytes(hashlib.sha256(material).digest()[:4], "big")
        if value != 0 and value not in used:
            return value
        retry += 1


def canonical_registry() -> dict:
    labels = sorted(row.scenario_id for row in build_scenario_manifest())
    used: set[int] = set()
    scenarios: dict[str, str] = {}
    for label in labels:
        value = opaque_u32("scenario", label, used)
        used.add(value)
        scenarios[label] = f"0x{value:08X}"

    aliases = {domain: set() for domain in TRUST_DOMAINS}
    for topology in (
        "T0_SHARED_ALL",
        "T1_SEPARATE_SOURCE_EXEC",
        "T2_SEPARATE_SOURCE_KEY_EXEC",
        "T3_SEPARATE_THROUGH_TRANSPORT",
        "T4_SEPARATE_ALL",
    ):
        mapping = domain_map(topology)
        for path in ("primary", "corroborator"):
            for domain in TRUST_DOMAINS:
                aliases[domain].add(mapping[path][domain])

    domains: dict[str, dict[str, str]] = {}
    for domain in TRUST_DOMAINS:
        used = set()
        domains[domain] = {}
        for label in sorted(aliases[domain]):
            value = opaque_u32(domain, label, used)
            used.add(value)
            domains[domain][label] = f"0x{value:08X}"

    return {
        "schema": 1,
        "experiment_id": "S7E-AERC-001",
        "algorithm": "sha256_first4_u32_be_retry_v1",
        "scenarios": scenarios,
        "domains": domains,
    }


class FreezeCandidateTests(unittest.TestCase):
    def test_ep_approval_is_narrow_and_complete(self) -> None:
        self.assertEqual(APPROVAL["state"], "EP_1_THROUGH_EP_5_APPROVED_FOR_FREEZE_CANDIDATE_PREPARATION_ONLY")
        self.assertTrue(all(APPROVAL["decisions"].values()))
        self.assertTrue(all(APPROVAL["not_authorized"].values()))

    def test_candidate_artifact_remains_historical_while_authoritative_state_is_frozen(self) -> None:
        self.assertEqual(FC["state"], "PROTOCOL_ENVIRONMENT_FREEZE_CANDIDATE__NOT_FROZEN__AUTHOR_APPROVAL_REQUIRED")
        self.assertFalse(any(FC["freeze_gates"].values()))
        self.assertEqual(FREEZE["state"], "FROZEN__MODELS_UNTRAINED__CANONICAL_EXECUTION_PROHIBITED")
        self.assertTrue(STATE["protocol_frozen"])
        self.assertTrue(STATE["environment_frozen"])
        self.assertTrue(STATE["public_key_registry_frozen"])
        self.assertTrue(STATE["fault_transformations_frozen"])
        self.assertTrue(STATE["learner_protocol_frozen"])
        self.assertFalse(STATE["production_models_trained"])
        self.assertFalse(STATE["production_models_frozen"])
        self.assertFalse(STATE["canonical_execution_authorized"])
        self.assertFalse(STATE["pr_merge_authorized"])

    def test_execution_parameters_match_approved_ep_candidate(self) -> None:
        self.assertEqual(FC["approved_execution_parameters"]["freshness_max_age_ticks"], EP["controlled_time"]["freshness_max_age_ticks"])
        self.assertEqual(FC["approved_execution_parameters"]["evidence_epoch"], EP["evidence_epoch"]["expected_epoch"])
        self.assertFalse(FC["approved_execution_parameters"]["persistent_private_key_files"])
        self.assertFalse(FC["approved_execution_parameters"]["private_key_in_cfs"])

    def test_registry_digest_and_domain_ids(self) -> None:
        registry = canonical_registry()
        encoded = json.dumps(registry, sort_keys=True, separators=(",", ":")).encode()
        self.assertEqual(hashlib.sha256(encoded).hexdigest(), FC["approved_execution_parameters"]["registry_canonical_json_sha256"])
        self.assertEqual(len(registry["scenarios"]), 280)
        for domain in TRUST_DOMAINS:
            self.assertEqual(registry["domains"][domain], FC["opaque_domain_ids"][domain])

    def test_public_key_registry_is_public_only(self) -> None:
        key_registry = FC["test_public_key_registry_candidate"]
        self.assertFalse(key_registry["secret_seed_or_private_key_committed"])
        self.assertEqual(len(key_registry["entries"]), 3)
        for entry in key_registry["entries"]:
            public_key = bytes.fromhex(entry["public_key_hex"])
            self.assertEqual(len(public_key), 32)
            self.assertEqual(hashlib.sha256(public_key).hexdigest(), entry["public_key_sha256"])
            self.assertEqual(entry["key_id"], FC["opaque_domain_ids"]["key"][entry["key_domain"]])

    def test_learner_rule_is_shared_fixed_and_untrained(self) -> None:
        learner = FC["learner_protocol_candidate"]
        self.assertTrue(learner["shared_for_L0_and_L1"])
        self.assertEqual(learner["training_blocks"], ["TR0", "TR1"])
        self.assertEqual(learner["prohibited_training_blocks"], ["E1", "E2", "C0"])
        self.assertFalse(learner["model_training_performed"])
        self.assertFalse(learner["production_model_freeze_performed"])
        expected = int.from_bytes(hashlib.sha256(b"S7E-AERC-001|LEARNER-RANDOM-STATE-V1").digest()[:4], "big")
        self.assertEqual(learner["hyperparameters"]["random_state"], expected)
        self.assertEqual(learner["hyperparameters"]["criterion"], "gini")
        self.assertEqual(learner["hyperparameters"]["splitter"], "best")

    def test_bound_blobs_are_exact_in_qualified_tree(self) -> None:
        for path, expected in FC["bound_git_blobs"].items():
            actual = subprocess.check_output(["git", "rev-parse", f"HEAD:{path}"], text=True).strip()
            self.assertEqual(actual, expected, path)

    def test_scientific_and_merge_gates_remain_closed(self) -> None:
        for name in (
            "production_models_trained",
            "production_models_frozen",
            "canonical_execution_authorized",
            "pr_merge_authorized",
        ):
            self.assertFalse(STATE[name])


if __name__ == "__main__":
    unittest.main(verbosity=2)
