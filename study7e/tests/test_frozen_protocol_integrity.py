from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = json.loads((ROOT / "study7e/FREEZE_MANIFEST_001.json").read_text())
STATE = json.loads((ROOT / "study7e/FREEZE_CANDIDATE_STATE.json").read_text())
AUTH = json.loads((ROOT / "study7e/configs/freeze_authorization_001.json").read_text())
ENV = json.loads((ROOT / "study7e/configs/frozen_environment_001.json").read_text())
KEYS = json.loads((ROOT / "study7e/configs/frozen_public_key_registry_001.json").read_text())
FAULTS = json.loads((ROOT / "study7e/configs/frozen_fault_transformations_001.json").read_text())
LEARNER = json.loads((ROOT / "study7e/configs/frozen_learner_protocol_001.json").read_text())


class FrozenProtocolIntegrityTests(unittest.TestCase):
    def test_freeze_scope_is_exact(self) -> None:
        self.assertEqual(MANIFEST["freeze_id"], "S7E-AERC-FREEZE-001")
        self.assertEqual(MANIFEST["candidate_id"], "S7E-AERC-FC-001")
        self.assertEqual(
            MANIFEST["state"],
            "FROZEN__MODELS_UNTRAINED__CANONICAL_EXECUTION_PROHIBITED",
        )
        self.assertTrue(all(MANIFEST["frozen_components"].values()))
        self.assertTrue(all(MANIFEST["explicitly_not_authorized"].values()))

    def test_authorization_matches_freeze_scope(self) -> None:
        self.assertEqual(AUTH["state"], "AUTHOR_FREEZE_APPROVED")
        self.assertTrue(all(AUTH["authorized"].values()))
        self.assertTrue(all(AUTH["not_authorized"].values()))

    def test_machine_state_has_only_authorized_freeze_gates(self) -> None:
        for name in (
            "protocol_frozen",
            "environment_frozen",
            "public_key_registry_frozen",
            "fault_transformations_frozen",
            "learner_protocol_frozen",
        ):
            self.assertTrue(STATE[name], name)
        for name in (
            "production_models_trained",
            "production_models_frozen",
            "canonical_execution_authorized",
            "canonical_results_generated",
            "pr_merge_authorized",
            "publication_result_claims_authorized",
        ):
            self.assertFalse(STATE[name], name)

    def test_all_qualified_source_blobs_remain_exact(self) -> None:
        for path, expected in MANIFEST["bound_git_blobs"].items():
            actual = subprocess.check_output(
                ["git", "rev-parse", f"HEAD:{path}"], text=True
            ).strip()
            self.assertEqual(actual, expected, path)
        candidate_blob = subprocess.check_output(
            ["git", "rev-parse", f"HEAD:{MANIFEST['candidate_config']}"], text=True
        ).strip()
        self.assertEqual(candidate_blob, MANIFEST["candidate_config_blob_sha"])

    def test_environment_snapshot_matches_qualified_candidate(self) -> None:
        self.assertEqual(ENV["state"], "FROZEN_ENVIRONMENT")
        self.assertEqual(
            ENV["flight_software"]["commit"],
            "088b2fa828db9ff7e00733f1908e0eeb59f66ce3",
        )
        self.assertEqual(
            ENV["signature_verifier"]["commit"],
            "ab2b16dd619ad5f6979a4fbe69cfa324a6fcc35f",
        )
        self.assertEqual(ENV["learner_runtime"]["python"], "3.11.16")
        self.assertEqual(ENV["learner_runtime"]["scikit_learn"], "1.9.1")
        self.assertFalse(ENV["production_model_training_authorized"])
        self.assertFalse(ENV["canonical_execution_authorized"])

    def test_public_key_registry_is_public_only_and_exact(self) -> None:
        self.assertEqual(KEYS["state"], "FROZEN_PUBLIC_KEY_REGISTRY")
        self.assertEqual(len(KEYS["entries"]), 3)
        self.assertFalse(KEYS["secret_seed_or_private_key_committed"])
        self.assertFalse(KEYS["persistent_private_key_files"])
        self.assertFalse(KEYS["private_key_in_cfs"])
        expected = {
            "corroborator:key": "0x9532BF30",
            "primary:key": "0xC9B0FE66",
            "shared:key": "0x39262168",
        }
        self.assertEqual({x["key_domain"]: x["key_id"] for x in KEYS["entries"]}, expected)

    def test_fault_transforms_are_frozen_by_exact_blob(self) -> None:
        self.assertEqual(FAULTS["state"], "FROZEN_FAULT_TRANSFORMATIONS")
        self.assertEqual(FAULTS["source_blob_sha"], "292db65822a866bce5e4ad50278b98090bf4d24b")
        self.assertEqual(FAULTS["profile_count"], 13)
        self.assertEqual(FAULTS["profiles"], [f"F{i}" for i in range(13)])
        self.assertTrue(FAULTS["amendment_requires_new_freeze_id"])

    def test_learner_protocol_is_frozen_but_models_are_not(self) -> None:
        self.assertEqual(LEARNER["state"], "FROZEN_LEARNER_PROTOCOL__MODELS_UNTRAINED")
        self.assertEqual(LEARNER["training_blocks"], ["TR0", "TR1"])
        self.assertEqual(LEARNER["prohibited_training_blocks"], ["E1", "E2", "C0"])
        self.assertEqual(LEARNER["training_scenarios"], 84)
        self.assertTrue(LEARNER["shared_for_L0_and_L1"])
        self.assertEqual(LEARNER["hyperparameters"]["random_state"], 2571582253)
        self.assertFalse(LEARNER["model_training_performed"])
        self.assertFalse(LEARNER["production_model_freeze_performed"])
        self.assertFalse(LEARNER["training_authorized"])

    def test_canonical_execution_and_model_artifacts_remain_absent(self) -> None:
        self.assertFalse((ROOT / "study7e/CANONICAL_EXECUTION_AUTHORIZATION.json").exists())
        self.assertFalse((ROOT / ".github/workflows/study7e-canonical-execution.yml").exists())
        for path in (
            "study7e/models/frozen_model_manifest.json",
            "study7e/models/L0_BASE.joblib",
            "study7e/models/L1_CORROBORATED.joblib",
            "study7e/models/L0_BASE.pkl",
            "study7e/models/L1_CORROBORATED.pkl",
            "study7e/models/L0_BASE.onnx",
            "study7e/models/L1_CORROBORATED.onnx",
        ):
            self.assertFalse((ROOT / path).exists(), path)


if __name__ == "__main__":
    unittest.main(verbosity=2)
