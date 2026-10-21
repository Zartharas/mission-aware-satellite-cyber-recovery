from __future__ import annotations

import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
FREEZE = ROOT / "study3x/config/S3X_PHASE6_TRACE_POPULATION_FREEZE_001.json"


class Phase6CTracePopulationFreezeTests(unittest.TestCase):
    def setUp(self):
        self.record = json.loads(FREEZE.read_text(encoding="utf-8"))

    def test_exact_population_is_bound(self):
        population = self.record["frozen_population_identity"]
        self.assertEqual(population["channels"], 176)
        self.assertEqual(population["total_intervals"], 1919)
        self.assertEqual(population["channels_with_intervals"], 171)
        self.assertEqual(population["channels_with_zero_intervals"], 5)
        self.assertEqual(
            population["canonical_channel_projection_sha256"],
            "f15338f1790f60d83d2c849542f6d6e3b21a8c49f7d413cdc5098e35952294d1",
        )

    def test_all_four_artifact_hashes_are_locked(self):
        expected = {
            "S3X_P99_X10_TIMESTAMP_INTERVALS_001.csv":
                "cfa4fa3d88cb525237cbfe347fabe8485021351f3b639bdb58f79c575d8a51bc",
            "S3X_P99_X10_TIMESTAMP_INTERVALS_SUMMARY_001.json":
                "9d7bcafac252cb39023c86e84db37bdb6ab6c674b2360622e4c43486d41756c5",
            "S3X_P99_X10_TIMESTAMP_INTERVALS_MANIFEST_001.json":
                "9be6db23bb7229da0aae17f0c4073a04c314d5079e595ab69c00aa0ee7a29983",
            "S3X_P99_X10_TIMESTAMP_INTERVALS_VALIDATION_001.json":
                "a1116119d56465f0a7aa990ad379441d0f373848c25b99c3369348228facf647",
        }
        artifacts = self.record["frozen_population_identity"]["canonical_artifacts"]
        self.assertEqual(set(artifacts), set(expected))
        for name, digest in expected.items():
            self.assertEqual(artifacts[name]["sha256"], digest)
            self.assertTrue(artifacts[name]["byte_identical_across_two_clean_runs"])

    def test_freeze_is_not_effective_before_merge(self):
        effectivity = self.record["effectivity"]
        self.assertEqual(effectivity["creation_state"], "PREPARED_ON_FEATURE_BRANCH")
        self.assertFalse(effectivity["trace_population_frozen_at_record_creation"])
        self.assertTrue(effectivity["freeze_effective_only_when_record_tracked_on_main"])
        self.assertTrue(effectivity["merge_requires_separate_author_review"])

    def test_downstream_execution_stays_closed(self):
        scope = self.record["scope_after_effective_freeze"]
        self.assertFalse(scope["interval_membership_retuning_allowed"])
        self.assertFalse(scope["gap_rule_retuning_allowed"])
        self.assertFalse(scope["recovery_policy_execution_authorized"])
        self.assertFalse(scope["scientific_execution_authorized"])
        self.assertFalse(scope["manuscript_claim_use_authorized"])
        self.assertFalse(scope["frozen_study_modification_authorized"])


if __name__ == "__main__":
    unittest.main()
