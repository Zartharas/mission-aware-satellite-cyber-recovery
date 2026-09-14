from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
for path in (ROOT / "study9" / "src", ROOT / "study2" / "src"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import copy
import json
import unittest
from unittest.mock import patch

import study9_semantic.contracts as contracts_module
from study9_semantic.contracts import (
    CANONICAL_EXECUTION_AUTHORIZATION_FLAGS,
    CANONICAL_RUN_CODE_FREEZE_PATH,
    CANONICAL_RUN_TESTED_COMMIT,
    CLOSED_PROTOCOL_STATUS,
    CODE_FREEZE_COMPUTATIONAL_PATHS,
    ContractViolation,
    EXCLUDED_ABLATION_VALUES,
    FROZEN_DATASET_IDS,
    FULL_POLICY_ENUM_VALUES,
    GUARANTEED_SIDECAR_DEFINITION_ID,
    IMPLEMENTATION_EXECUTION_FLAGS,
    OPEN_PROTOCOL_STATUS,
    PRE_REAL_DATA_AUDIT_STATUS,
    PRIMARY_POLICY_VALUES,
    REQUIRED_VARIABLES,
    RUN_IDENTITY_BASE_PATHS,
    STATE_COLLAPSE_RULE_ID,
    load_frozen_contracts,
    sha256_file,
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
        self.assertFalse(contracts.protocol["authorization"]["canonical_execution_authorized"])
        self.assertFalse(contracts.protocol["authorization"]["dataset_ingestion_authorized"])
        self.assertEqual(contracts.protocol["status"], CLOSED_PROTOCOL_STATUS)

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

    def test_execution_design_freeze_is_exact_and_closed(self):
        contracts = load_frozen_contracts(ROOT)
        design = contracts.execution_design
        self.assertEqual(
            design["lossless_state_collapse"]["rule_id"],
            STATE_COLLAPSE_RULE_ID,
        )
        self.assertEqual(
            design["guaranteed_minimal_sidecar"]["definition_id"],
            GUARANTEED_SIDECAR_DEFINITION_ID,
        )
        self.assertFalse(
            design["guaranteed_minimal_sidecar"]["actual_unresolved_values_may_be_substituted"]
        )
        self.assertTrue(
            design["lossless_state_collapse"][
                "sum_of_group_multiplicities_must_equal_verified_dataset_row_count"
            ]
        )
        self.assertFalse(design["execution_boundary"]["real_dataset_rows_opened"])
        self.assertFalse(design["execution_boundary"]["study9_endpoints_computed"])

    def test_execution_design_rejects_actual_missing_value_substitution(self):
        contracts = load_frozen_contracts(ROOT)
        tampered = copy.deepcopy(contracts)
        tampered.execution_design["guaranteed_minimal_sidecar"][
            "actual_unresolved_values_may_be_substituted"
        ] = True
        with self.assertRaises(ContractViolation):
            validate_contracts(tampered)

    def test_execution_design_rejects_state_collapse_drift(self):
        contracts = load_frozen_contracts(ROOT)
        tampered = copy.deepcopy(contracts)
        tampered.execution_design["lossless_state_collapse"]["rule_id"] = "ALTERED_RULE"
        with self.assertRaises(ContractViolation):
            validate_contracts(tampered)

    def test_execution_design_rejects_input_identity_tamper(self):
        contracts = load_frozen_contracts(ROOT)
        tampered = copy.deepcopy(contracts)
        tampered.execution_design["input_identity_contracts"][0][
            "canonical_artifact_sha256"
        ] = "0" * 64
        with self.assertRaises(ContractViolation):
            validate_contracts(tampered)

    def test_pre_real_data_adversarial_audit_is_bound_and_closed(self):
        contracts = load_frozen_contracts(ROOT)
        audit = contracts.pre_real_data_audit
        self.assertEqual(audit["status"], PRE_REAL_DATA_AUDIT_STATUS)
        self.assertEqual(audit["audit_basis_commit"], "f7723ffd7d2e9a6127f260f83d5a0d36cf7ffff1")
        self.assertEqual(audit["actual_clone_validation"]["test_count"], 57)
        self.assertEqual(audit["actual_clone_validation"]["result"], "PASS")
        self.assertFalse(audit["execution_boundary"]["real_dataset_rows_opened"])
        self.assertFalse(audit["execution_boundary"]["study9_endpoints_computed"])
        self.assertTrue(
            contracts.protocol["pre_real_data_adversarial_audit"][
                "independent_raw_row_projection_implemented"
            ]
        )

    def test_pre_real_data_audit_tamper_is_rejected(self):
        contracts = load_frozen_contracts(ROOT)
        tampered = copy.deepcopy(contracts)
        tampered.pre_real_data_audit["required_remediations"]["independent_raw_row_projection"] = False
        with self.assertRaises(ContractViolation):
            validate_contracts(tampered)

    def test_run_manifest_identity_path_set_is_exact(self):
        contracts = load_frozen_contracts(ROOT)
        self.assertEqual(
            tuple(contracts.protocol["implementation_phase"]["run_manifest_reproducibility_identity_paths"]),
            RUN_IDENTITY_BASE_PATHS,
        )
        self.assertIn("study9/PRE_REAL_DATA_ADVERSARIAL_AUDIT.json", RUN_IDENTITY_BASE_PATHS)
        self.assertIn("study9/src/study9_semantic/contracts.py", RUN_IDENTITY_BASE_PATHS)
        self.assertIn("study9/src/study9_semantic/canonical_runner.py", RUN_IDENTITY_BASE_PATHS)
        self.assertIn("study2/src/study2_security/selectors.py", RUN_IDENTITY_BASE_PATHS)

    def test_canonical_run_code_freeze_is_bound_exact_and_closed(self):
        contracts = load_frozen_contracts(ROOT)
        binding = contracts.protocol["canonical_run_code_freeze"]
        self.assertTrue(binding["frozen"])
        self.assertEqual(binding["freeze_record"], CANONICAL_RUN_CODE_FREEZE_PATH)
        self.assertEqual(binding["tested_commit"], CANONICAL_RUN_TESTED_COMMIT)
        self.assertEqual(binding["computational_file_count"], len(CODE_FREEZE_COMPUTATIONAL_PATHS))
        self.assertEqual(binding["actual_clone_full_suite_test_count"], 69)
        self.assertEqual(binding["actual_clone_canonical_runner_test_count"], 6)
        self.assertEqual(binding["actual_clone_result"], "PASS")
        record = json.loads((ROOT / CANONICAL_RUN_CODE_FREEZE_PATH).read_text(encoding="utf-8"))
        self.assertEqual(
            tuple(item["path"] for item in record["computational_identity"]["files"]),
            CODE_FREEZE_COMPUTATIONAL_PATHS,
        )
        self.assertNotIn("study9/src/study9_semantic/contracts.py", CODE_FREEZE_COMPUTATIONAL_PATHS)
        self.assertFalse(record["execution_boundary"]["real_dataset_rows_opened"])
        self.assertFalse(record["execution_boundary"]["study9_endpoints_computed"])
        self.assertFalse(record["execution_boundary"]["results_directory_created"])

    def test_canonical_run_code_freeze_rejects_tested_commit_tamper(self):
        contracts = load_frozen_contracts(ROOT)
        tampered = copy.deepcopy(contracts)
        tampered.protocol["canonical_run_code_freeze"]["tested_commit"] = "0" * 40
        with self.assertRaises(ContractViolation):
            validate_contracts(tampered)

    def test_canonical_run_code_freeze_rejects_runtime_hash_drift(self):
        contracts = load_frozen_contracts(ROOT)
        target = ROOT / CODE_FREEZE_COMPUTATIONAL_PATHS[0]

        def altered_sha(path: Path) -> str:
            if path == target:
                return "0" * 64
            return sha256_file(path)

        with patch.object(contracts_module, "sha256_file", side_effect=altered_sha):
            with self.assertRaises(ContractViolation) as caught:
                validate_contracts(contracts)
        self.assertIn("computational SHA-256 drift", str(caught.exception))

    def test_canonical_run_code_freeze_rejects_recorded_byte_size_tamper(self):
        contracts = load_frozen_contracts(ROOT)
        record_path = ROOT / CANONICAL_RUN_CODE_FREEZE_PATH
        original_load_json = contracts_module._load_json

        def altered_load(path: Path):
            value = original_load_json(path)
            if path == record_path:
                value = copy.deepcopy(value)
                value["computational_identity"]["files"][0]["size_bytes"] += 1
            return value

        with patch.object(contracts_module, "_load_json", side_effect=altered_load):
            with self.assertRaises(ContractViolation) as caught:
                validate_contracts(contracts)
        self.assertIn("byte-size drift", str(caught.exception))

    def test_partial_future_execution_transition_is_rejected(self):
        contracts = load_frozen_contracts(ROOT)
        tampered = copy.deepcopy(contracts)
        tampered.protocol["authorization"][CANONICAL_EXECUTION_AUTHORIZATION_FLAGS[0]] = True
        with self.assertRaises(ContractViolation):
            validate_contracts(tampered)

    def test_coherent_future_open_state_accepts_existing_code_freeze(self):
        contracts = load_frozen_contracts(ROOT)
        future = copy.deepcopy(contracts)
        future.protocol["status"] = OPEN_PROTOCOL_STATUS
        for flag in CANONICAL_EXECUTION_AUTHORIZATION_FLAGS:
            future.protocol["authorization"][flag] = True
        for flag in IMPLEMENTATION_EXECUTION_FLAGS:
            future.protocol["implementation_phase"][flag] = True
        future.protocol["implementation_phase"]["synthetic_only"] = False
        future.protocol["implementation_phase"]["loader_runner_synthetic_test_only"] = False
        validate_contracts(future)


if __name__ == "__main__":
    unittest.main()
