from __future__ import annotations

import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
AUTH = ROOT / "study3x/config/S3X_PHASE7_RUNTIME_AUTH_001.json"


class Phase7CRuntimeAuthorizationTests(unittest.TestCase):
    def setUp(self):
        self.auth = json.loads(AUTH.read_text(encoding="utf-8"))

    def test_population_and_repeatability_are_exact(self):
        constraints = self.auth["runtime_constraints"]
        self.assertEqual(constraints["frozen_interval_count"], 1919)
        self.assertEqual(constraints["cases_per_interval"], 18)
        self.assertEqual(constraints["expected_case_count"], 34542)
        self.assertEqual(constraints["expected_matched_comparison_rows"], 30704)
        repeat = self.auth["deterministic_repeatability"]
        self.assertTrue(repeat["two_clean_output_directories_required"])
        self.assertTrue(repeat["byte_identical_sha256_required"])
        self.assertEqual(repeat["accepted_primary_reference_case_mismatches"], 0)
        self.assertEqual(repeat["accepted_matched_comparison_mismatches"], 0)

    def test_result_freeze_and_manuscript_use_remain_closed(self):
        scope = self.auth["authorization_scope"]
        self.assertFalse(scope["result_freeze_authorized"])
        self.assertFalse(scope["manuscript_claim_use_authorized"])
        boundary = self.auth["result_freeze_boundary"]
        self.assertFalse(boundary["result_freeze_authorized_now"])
        self.assertFalse(boundary["manuscript_claim_use_authorized_now"])

    def test_authorization_is_not_effective_on_feature_branch(self):
        self.assertEqual(
            self.auth["status"],
            "PREPARED_ON_FEATURE_BRANCH__NOT_EFFECTIVE",
        )
        effectivity = self.auth["effectivity"]
        self.assertTrue(effectivity["record_effective_only_when_tracked_on_main"])
        self.assertTrue(effectivity["record_merge_requires_separate_author_review"])
        self.assertTrue(
            effectivity["actual_runtime_execution_requires_explicit_post_merge_author_instruction"]
        )

    def test_no_execution_is_recorded_at_creation(self):
        state = self.auth["execution_state_at_record_creation"]
        self.assertTrue(all(value is False for value in state.values()))


if __name__ == "__main__":
    unittest.main()
