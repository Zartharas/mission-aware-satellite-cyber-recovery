from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

from study7e.src.aerc_design import TRUST_DOMAINS, build_scenario_manifest, domain_map

ROOT = Path(__file__).resolve().parents[2]
CANDIDATE = json.loads((ROOT / "study7e/configs/execution_parameters_candidate_2026-09-23.json").read_text())
FAULTS = json.loads((ROOT / "study7e/configs/fault_transformations_draft.json").read_text())


def opaque_u32(namespace: str, label: str, used: set[int]) -> tuple[int, int]:
    retry = 0
    while True:
        material = f"S7E-AERC-001|{namespace}|{label}|{retry}".encode("utf-8")
        value = int.from_bytes(hashlib.sha256(material).digest()[:4], "big")
        if value != 0 and value not in used:
            return value, retry
        retry += 1


class ExecutionParameterCandidateTests(unittest.TestCase):
    def test_candidate_remains_unfrozen(self) -> None:
        self.assertEqual(
            CANDIDATE["state"],
            "TECHNICAL_CANDIDATE__AUTHOR_APPROVAL_REQUIRED__NOT_FROZEN",
        )
        approvals = CANDIDATE["approvals"]
        self.assertFalse(any(approvals.values()))

    def test_zero_age_freshness_is_deterministic(self) -> None:
        cfg = CANDIDATE["controlled_time"]
        self.assertEqual(cfg["freshness_max_age_ticks"], 0)
        issue = cfg["nominal_issue_tick"]
        nominal = cfg["nominal_evaluation_tick"]
        stale = cfg["stale_fault_evaluation_tick"]
        self.assertEqual(issue, nominal)
        self.assertEqual(stale, nominal + 1)
        self.assertTrue(issue <= nominal and nominal - issue <= 0)
        self.assertFalse(issue <= stale and stale - issue <= 0)
        self.assertFalse(cfg["wall_clock_dependency"])

    def test_epoch_one_and_f9_byte47_are_compatible(self) -> None:
        self.assertEqual(CANDIDATE["evidence_epoch"]["expected_epoch"], 1)
        body = bytearray(64)
        body[40:48] = (1).to_bytes(8, "big")
        self.assertEqual(body[47], 1)
        body[47] ^= 0x01
        self.assertEqual(int.from_bytes(body[40:48], "big"), 0)
        self.assertIn("offset 47", FAULTS["profiles"]["F9"]["transformation"])

    def test_scenario_registry_is_collision_free_for_280_design_rows(self) -> None:
        labels = sorted(row.scenario_id for row in build_scenario_manifest())
        self.assertEqual(len(labels), 280)
        used: set[int] = set()
        retries: list[int] = []
        values: dict[str, int] = {}
        for label in labels:
            value, retry = opaque_u32("scenario", label, used)
            used.add(value)
            retries.append(retry)
            values[label] = value
        self.assertEqual(len(used), 280)
        self.assertNotIn(0, used)
        self.assertEqual(max(retries), 0)
        examples = CANDIDATE["opaque_registry_algorithm"]["scenario_registry"]["examples"]
        for label, expected_hex in examples.items():
            self.assertEqual(values[label], int(expected_hex, 16))

    def test_domain_alias_registries_match_design_and_are_collision_free(self) -> None:
        expected_aliases = {domain: set() for domain in TRUST_DOMAINS}
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
                    expected_aliases[domain].add(mapping[path][domain])

        configured = CANDIDATE["opaque_registry_algorithm"]["domain_registries"]
        for domain in TRUST_DOMAINS:
            self.assertEqual(set(configured[domain]["labels"]), expected_aliases[domain])
            used: set[int] = set()
            values: dict[str, int] = {}
            for label in sorted(expected_aliases[domain]):
                value, retry = opaque_u32(domain, label, used)
                self.assertEqual(retry, 0)
                used.add(value)
                values[label] = value
            self.assertEqual(len(values), 3)
            self.assertNotIn(0, used)
            for label, expected_hex in configured[domain].get("examples", {}).items():
                self.assertEqual(values[label], int(expected_hex, 16))

    def test_test_key_seed_derivation_is_deterministic_distinct_and_host_only(self) -> None:
        cfg = CANDIDATE["deterministic_test_keys"]
        self.assertFalse(cfg["persistent_private_key_files"])
        self.assertTrue(cfg["derive_on_demand_in_host_harness"])
        self.assertTrue(cfg["wipe_seed_and_secret_key_after_signing"])
        self.assertFalse(cfg["cfs_private_key_present"])
        seeds = []
        for alias in cfg["key_domains"]:
            material = f"S7E-AERC-001|ED25519-TEST-SEED-V1|{alias}".encode("utf-8")
            seeds.append(hashlib.sha256(material).digest())
        self.assertEqual(len({seed.hex() for seed in seeds}), 3)
        self.assertTrue(all(len(seed) == 32 for seed in seeds))

    def test_fault_transform_candidate_still_covers_f0_to_f12(self) -> None:
        self.assertEqual(set(FAULTS["profiles"]), {f"F{i}" for i in range(13)})
        self.assertIn("offset 47", FAULTS["profiles"]["F9"]["transformation"])
        self.assertIn("two separately signed", FAULTS["profiles"]["F12"]["transformation"])
        self.assertFalse(FAULTS["approvals"]["byte_transformations_frozen"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
