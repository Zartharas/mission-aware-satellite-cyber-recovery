from __future__ import annotations

import unittest

from study2_security.trial_manifest import materialize_trial_manifest, trial_manifest_sha256


class TrialManifestTests(unittest.TestCase):
    def test_exact_frozen_membership_and_hash(self) -> None:
        manifest = materialize_trial_manifest()
        self.assertEqual(manifest["position_count"], 3872)
        self.assertEqual(trial_manifest_sha256(manifest), "190612473717b7768ceccb4596a20d90cd7d532bf7581330ce94d609cb752e67")
        self.assertEqual(manifest["positions"][0]["trial_id"], "S2-AEATR-001:A01:2100001")
        self.assertEqual(manifest["positions"][-1]["trial_id"], "S2-AEATR-001:E09:2500032")

    def test_trial_id_and_order_are_unique(self) -> None:
        positions = materialize_trial_manifest()["positions"]
        self.assertEqual([row["global_order_index"] for row in positions], list(range(1, 3873)))
        self.assertEqual(len({row["trial_id"] for row in positions}), len(positions))


if __name__ == "__main__":
    unittest.main()
