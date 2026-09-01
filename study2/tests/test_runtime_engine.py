from __future__ import annotations

import unittest

from study2_security.runtime_engine import development_fixture_report, run_trial
from study2_security.runtime_freeze import RuntimeMode


class RuntimeEngineTests(unittest.TestCase):
    def test_all_85_cell_types_execute_with_development_only_seeds(self) -> None:
        report = development_fixture_report()
        self.assertTrue(report["development_only"])
        self.assertFalse(report["campaign_seed_consumed"])
        self.assertFalse(report["campaign_observations_generated"])
        self.assertEqual(report["cell_types_exercised"], 85)
        self.assertTrue(report["all_valid"])

    def test_execution_is_deterministic_for_same_cell_seed_and_run_id(self) -> None:
        first = run_trial(cell_id="A18", seed=2_900_001, run_id="DEV-DETERMINISM")
        second = run_trial(cell_id="A18", seed=2_900_001, run_id="DEV-DETERMINISM")
        self.assertEqual(first, second)

    def test_campaign_seed_is_rejected_in_development_mode(self) -> None:
        with self.assertRaises(ValueError):
            run_trial(cell_id="A01", seed=2_100_001, run_id="SHOULD-FAIL", mode=RuntimeMode.DEVELOPMENT)

    def test_campaign_mode_requires_hash_bound_authorization(self) -> None:
        with self.assertRaises(ValueError):
            run_trial(cell_id="A01", seed=2_100_001, run_id="SHOULD-FAIL", mode=RuntimeMode.CAMPAIGN)

    def test_v5_can_create_authenticated_unsafe_recovery_while_v0_blocks(self) -> None:
        v0 = run_trial(cell_id="A03", seed=2_900_002, run_id="DEV-A03")
        v5 = run_trial(cell_id="A18", seed=2_900_002, run_id="DEV-A18")
        self.assertFalse(v0["evidence_qualified_trusted_recovery"])
        self.assertTrue(v5["evidence_qualified_trusted_recovery"])
        self.assertTrue(v5["adjudication_only"]["unsafe_trusted_recovery"])

    def test_post_signature_manipulation_is_rejected(self) -> None:
        result = run_trial(cell_id="A15", seed=2_900_003, run_id="DEV-A15")
        self.assertFalse(result["visible_runtime"]["signature_valid"])
        self.assertFalse(result["evidence_qualified_trusted_recovery"])

    def test_a3_partial_compromise_can_hide_residual_state(self) -> None:
        result = run_trial(cell_id="E09", seed=2_900_004, run_id="DEV-E09")
        self.assertTrue(result["adjudication_only"]["residual_unauthorized_state"])
        self.assertTrue(result["adjudication_only"]["unsafe_trusted_recovery"])

    def test_a2_contact_unavailability_blocks_immediate_unsafe_recovery(self) -> None:
        result = run_trial(cell_id="E06", seed=2_900_005, run_id="DEV-E06")
        self.assertFalse(result["visible_runtime"]["authorization_available"])
        self.assertFalse(result["evidence_qualified_trusted_recovery"])

    def test_contact_followup_uses_frozen_logical_schedule(self) -> None:
        result = run_trial(cell_id="B16", seed=2_900_006, run_id="DEV-B16")
        self.assertTrue(result["evidence_qualified_trusted_recovery"])
        self.assertEqual(result["time_to_evidence_qualified_trusted_recovery_s"], 185.0)

    def test_ambiguity_pair_has_identical_policy_visible_runtime(self) -> None:
        benign = run_trial(cell_id="C01", seed=2_900_007, run_id="DEV-C01")
        adversarial = run_trial(cell_id="C04", seed=2_900_007, run_id="DEV-C04")
        self.assertEqual(benign["visible_runtime"], adversarial["visible_runtime"])
        self.assertEqual(benign["adjudication_only"]["cause"], "BENIGN")
        self.assertEqual(adversarial["adjudication_only"]["cause"], "ADVERSARIAL")


if __name__ == "__main__":
    unittest.main()
