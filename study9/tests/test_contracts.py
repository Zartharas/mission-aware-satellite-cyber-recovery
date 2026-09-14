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
    FROZEN_DATASET_IDS,
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


if __name__ == "__main__":
    unittest.main()
