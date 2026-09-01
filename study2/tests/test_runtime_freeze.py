from __future__ import annotations

import unittest

from study2_security.protocol import ContactRegime
from study2_security.runtime_authorization import (
    AUTHORIZATION_PATH,
    CampaignAuthorization,
    current_runtime_bindings,
)
from study2_security.runtime_freeze import (
    CONTACT_CALIBRATION,
    EXPECTED_TRIAL_MANIFEST_SHA256,
    RuntimeMode,
    is_campaign_seed,
    is_development_seed,
    require_seed_mode,
    runtime_freeze_sha256,
)


class RuntimeFreezeTests(unittest.TestCase):
    def test_contact_schedule_is_frozen_logical_time(self) -> None:
        self.assertTrue(CONTACT_CALIBRATION[ContactRegime.K0].available_at(10.0))
        self.assertFalse(CONTACT_CALIBRATION[ContactRegime.K1].available_at(10.0))
        self.assertEqual(
            CONTACT_CALIBRATION[ContactRegime.K1].next_contact_at_or_after(10.0), 20.0
        )
        self.assertEqual(
            CONTACT_CALIBRATION[ContactRegime.K2].next_contact_at_or_after(10.0), 60.0
        )
        self.assertEqual(
            CONTACT_CALIBRATION[ContactRegime.K3].next_contact_at_or_after(10.0), 180.0
        )
        self.assertEqual(
            CONTACT_CALIBRATION[ContactRegime.K4].next_contact_at_or_after(10.0), 25.0
        )

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
        self.assertEqual(
            runtime_freeze_sha256(),
            "40e38ebc1dccc8b549d36bcbf6c2aca4a52ade7c6ecb87670224ef643d741434",
        )
        self.assertEqual(
            EXPECTED_TRIAL_MANIFEST_SHA256,
            "190612473717b7768ceccb4596a20d90cd7d532bf7581330ce94d609cb752e67",
        )

    def _authorization(self) -> CampaignAuthorization:
        bindings = current_runtime_bindings()
        return CampaignAuthorization(
            authorization_id="AUTH-TEST",
            experiment_id="S2-AEATR-001",
            scope="EXACT_FROZEN_STUDY2_CAMPAIGN",
            phase5_base_commit="a" * 40,
            active=True,
            consumed=False,
            **bindings,
        )

    def test_authorization_uses_self_derived_runtime_bindings(self) -> None:
        auth = self._authorization()
        auth.validate_bindings()
        wrong = CampaignAuthorization(
            **{**auth.__dict__, "trial_manifest_sha256": "0" * 64}
        )
        with self.assertRaises(ValueError):
            wrong.validate_bindings()

    def test_phase5_has_no_repository_backed_campaign_authorization(self) -> None:
        self.assertFalse(AUTHORIZATION_PATH.exists())
        with self.assertRaises(ValueError):
            self._authorization().validate()

    def test_authorization_consumption_is_single_use(self) -> None:
        consumed = self._authorization().consumed_copy()
        self.assertFalse(consumed.active)
        self.assertTrue(consumed.consumed)
        with self.assertRaises(ValueError):
            consumed.validate_bindings()


if __name__ == "__main__":
    unittest.main()
