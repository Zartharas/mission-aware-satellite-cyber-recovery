from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "study3x/config/S3X_PHASE7_RECOVERY_REPLAY_PROTOCOL_001.json"
MODEL_PATH = ROOT / "study3/src/temporal_model.py"


def load_model():
    spec = importlib.util.spec_from_file_location("phase7_parent_model_test", MODEL_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load Study-3 model")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


MODEL = load_model()


class Phase7ARecoveryReplayDesignTests(unittest.TestCase):
    def setUp(self):
        self.protocol = json.loads(PROTOCOL.read_text(encoding="utf-8"))

    def test_case_population_is_exact(self):
        grid = self.protocol["factor_grid"]
        self.assertEqual(grid["expected_cases"], 1919 * 3 * 3 * 2)
        self.assertEqual(grid["expected_cases"], 34542)
        self.assertFalse(grid["persistence_dimension"])

    def test_one_epoch_freshness_ratio_is_preserved_as_normalization(self):
        self.assertEqual(MODEL.EVIDENCE_TTL_S / MODEL.EPOCH_S, 1)
        transition = self.protocol["modeled_state_transition"]
        self.assertEqual(transition["pre_hiatus_cache_fresh_through_units"], 1)
        self.assertFalse(transition["repeated_post_refresh_behavior_modeled"])

    def test_parent_policy_actions_match_phase7_binding(self):
        expected = {
            ("S2_B0_FAIL_CLOSED", True, False): "PROCEED_TO_RECOVERY_GATE",
            ("S2_B0_FAIL_CLOSED", True, True): "PROCEED_TO_RECOVERY_GATE",
            ("S2_B0_FAIL_CLOSED", False, False): "RESTRICT_AND_REQUEST_AUTHORIZATION",
            ("S2_B0_FAIL_CLOSED", False, True): "RESTRICT_AND_REQUEST_AUTHORIZATION",
            ("S2_B2_RISK_THRESHOLD", True, False): "RESTRICT_AND_REQUEST_AUTHORIZATION",
            ("S2_B2_RISK_THRESHOLD", True, True): "RESTRICT_AND_REQUEST_AUTHORIZATION",
            ("S2_B2_RISK_THRESHOLD", False, False): "HOLD_AND_REQUIRE_EVIDENCE",
            ("S2_B2_RISK_THRESHOLD", False, True): "HOLD_AND_REQUIRE_EVIDENCE",
            ("S2_S1_EVIDENCE_AWARE", True, False): "RESTRICT_AND_REQUEST_AUTHORIZATION",
            ("S2_S1_EVIDENCE_AWARE", True, True): "PROCEED_TO_RECOVERY_GATE",
            ("S2_S1_EVIDENCE_AWARE", False, False): "HOLD_AND_REQUIRE_EVIDENCE",
            ("S2_S1_EVIDENCE_AWARE", False, True): "HOLD_AND_REQUIRE_EVIDENCE",
        }
        for (policy, qualified, proxy), action in expected.items():
            self.assertEqual(
                MODEL.select_action(
                    policy,
                    evidence_qualified=qualified,
                    security_signal=True,
                    contact=proxy,
                ),
                action,
            )

    def test_source_timing_claims_stay_closed(self):
        timing = self.protocol["source_timing_abstraction"]
        self.assertFalse(timing["operational_contact_claim"])
        self.assertFalse(timing["rf_outage_claim"])
        self.assertFalse(timing["spacecraft_outage_claim"])
        self.assertFalse(timing["command_availability_claim"])

    def test_execution_remains_closed(self):
        auth = self.protocol["authorization_model"]
        self.assertTrue(auth["phase7a_design_authorized"])
        self.assertFalse(auth["implementation_authorized"])
        self.assertFalse(auth["recovery_policy_execution_authorized"])
        self.assertFalse(auth["scientific_execution_authorized"])
        self.assertFalse(auth["manuscript_claim_use_authorized"])
        self.assertTrue(auth["runtime_requires_separate_versioned_authorization_record"])


if __name__ == "__main__":
    unittest.main()
