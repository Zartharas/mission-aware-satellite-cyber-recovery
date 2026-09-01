from __future__ import annotations

import unittest

from study2_security.protocol import ContactRegime
from study2_security.runtime_authorization import CampaignAuthorization
from study2_security.runtime_freeze import CONTACT_CALIBRATION, EXPECTED_TRIAL_MANIFEST_SHA256, RuntimeMode, is_campaign_seed, is_development_seed, require_seed_mode, runtime_freeze_sha256


class RuntimeFreezeTests(unittest.TestCase):
    def test_contact_schedule_is_frozen_logical_time(self) -> None:
        self.assertTrue(CONTACT_CALIBRATION[ContactRegime.K0].available_at(10.0))
        self.assertFalse(CONTACT_CALIBRATION[ContactRegime.K1].available_at(10.0))
        self.assertEqual(CONTACT_CALIBRATION[ContactRegime.K1].next_contact_at_or_after(10.0), 20.0)
        self.assertEqual(CONTACT_CALIBRATION[ContactRegime.K2].next_contact_at_or_after(10.0), 60.0)
        self.assertEqual(CONTACT_CALIBRATION[ContactRegime.K3].next_contact_at_or_after(10.0), 180.0)
        self.assertEqual(CONTACT_CALIBRATION[ContactRegime.K4].next_contact_at_or_after(10.0), 25.0)

    def test_seed_namespaces_are_disjoint_and_fail_closed(self) -> None:
        self.assertTrue(is_development_seed(2_900_001))
        self.assertFalse(is_campaign_seed(2_900_001))
        self.assertTrue(is_campaign_seed(2_100_001))
        self.assertFalse(is_development_seed(2_100_001))
        require_seed_mode(2_900_001, RuntimeMode.DEVELOPMENT)
        require_seed_mode(2_100_001, RuntimeMode.CAMPAIGN)
        with self.assertRaises(ValueError):
            require_seed_mode(2_100_001, RuntimeMode.DEVELOPMENT)
        with self.assertRaises(ValueError):
            require_seed_mode(2_900_001, RuntimeMode.CAMPAIGN)

    def test_runtime_freeze_hash_is_stable(self) -> None:
        self.assertEqual(runtime_freeze_sha256(), "f49b6740e70fe95a8182000fbc64052cb180a253a4c3fd7c5c0e75777aab9cdd")
        self.assertEqual(EXPECTED_TRIAL_MANIFEST_SHA256, "190612473717b7768ceccb4596a20d90cd7d532bf7581330ce94d609cb752e67")

    def test_authorization_requires_exact_active_hash_binding(self) -> None:
        expected = {"protocol_sha256": "p", "cell_matrix_sha256": "c", "trial_manifest_sha256": "t", "runtime_freeze_sha256": "r", "container_recipe_sha256": "d"}
        auth = CampaignAuthorization(authorization_id="AUTH-1", experiment_id="S2-AEATR-001", scope="EXACT_FROZEN_STUDY2_CAMPAIGN", authorized_repository_commit="abc", protocol_sha256="p", cell_matrix_sha256="c", trial_manifest_sha256="t", runtime_freeze_sha256="r", container_recipe_sha256="d", active=True, consumed=False)
        auth.validate(current_repository_commit="abc", expected_bindings=expected)
        with self.assertRaises(ValueError):
            auth.validate(current_repository_commit="different", expected_bindings=expected)
        bad = CampaignAuthorization(**{**auth.__dict__, "trial_manifest_sha256": "wrong"})
        with self.assertRaises(ValueError):
            bad.validate(current_repository_commit="abc", expected_bindings=expected)


if __name__ == "__main__":
    unittest.main()
