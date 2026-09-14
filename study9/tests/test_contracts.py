from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
for path in (ROOT / "study9" / "src", ROOT / "study2" / "src"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import copy
import unittest

from study9_semantic.contracts import (
    ContractViolation,
    EXCLUDED_ABLATION_VALUES,
    FROZEN_DATASET_IDS,
    FULL_POLICY_ENUM_VALUES,
    PRIMARY_POLICY_VALUES,
    REQUIRED_VARIABLES,
    load_frozen_contracts,
    validate_contracts,
)


class ContractTests(unittest.TestCase):
    def test_repository_contracts_fail_closed_and_load(self):
        contracts = load_frozen_contracts(ROOT)
        self.assertEqual(tuple(contracts.protocol["primary_population_freeze"]["members"]), FROZEN_DATASET_IDS)
        self.assertEqual(tuple(contracts.semantic["target_semantics"]), REQUIRED_VARIABLES)
        self.assertTrue(all(row["schema_locked"] for row in contracts.manifest["datasets"]))
        self.assertEqual(contracts.semantic["permitted_deterministic_derivation_rules"], [])
        self.assertFalse(contracts.protocol["authorization"]["row_level_analysis_authorized"])

    def test_tampered_contract_is_rejected(self):
        contracts = load_frozen_contracts(ROOT)
        tampered = copy.deepcopy(contracts)
        tampered.protocol["authorization"]["row_level_analysis_authorized"] = True
        with self.assertRaises(ContractViolation):
            validate_contracts(tampered)

    def test_primary_policy_scope_is_exact_and_ablations_are_excluded(self):
        contracts = load_frozen_contracts(ROOT)
        self.assertEqual(tuple(contracts.policy_scope["primary_policies"]), PRIMARY_POLICY_VALUES)
        self.assertEqual(
            tuple(contracts.policy_scope["excluded_mechanistic_ablations"]),
            EXCLUDED_ABLATION_VALUES,
        )
        self.assertEqual(
            tuple(contracts.policy_scope["study2_policy_enum_order"]),
            FULL_POLICY_ENUM_VALUES,
        )
        self.assertEqual(
            set(contracts.policy_scope["primary_policies"]).intersection(
                contracts.policy_scope["excluded_mechanistic_ablations"]
            ),
            set(),
        )
        self.assertEqual(
            contracts.policy_scope["primary_stratification"]["dataset_policy_stratum_count"],
            12,
        )
        self.assertIsNone(
            contracts.policy_scope["primary_analysis_rule"]["canonical_default_policy"]
        )

    def test_primary_policy_scope_rejects_admitted_ablation(self):
        contracts = load_frozen_contracts(ROOT)
        tampered = copy.deepcopy(contracts)
        tampered.policy_scope["primary_policies"][3] = EXCLUDED_ABLATION_VALUES[0]
        with self.assertRaises(ContractViolation):
            validate_contracts(tampered)

    def test_primary_policy_scope_rejects_reordering(self):
        contracts = load_frozen_contracts(ROOT)
        tampered = copy.deepcopy(contracts)
        policies = tampered.policy_scope["primary_policies"]
        policies[0], policies[1] = policies[1], policies[0]
        with self.assertRaises(ContractViolation):
            validate_contracts(tampered)


if __name__ == "__main__":
    unittest.main()
