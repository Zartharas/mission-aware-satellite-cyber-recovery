from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
AUTH = ROOT / "study3x/config/S3X_PHASE6_TIMESTAMP_EXTRACTION_AUTH_001.json"
PROTOCOL = ROOT / "study3x/config/S3X_TIMESTAMP_TRACE_EXTRACTION_PROTOCOL_001.json"


class Phase6BRuntimeAuthorizationTests(unittest.TestCase):
    def test_authorization_binds_exact_merged_protocol(self):
        auth = json.loads(AUTH.read_text(encoding="utf-8"))
        protocol_sha = hashlib.sha256(PROTOCOL.read_bytes()).hexdigest()
        self.assertEqual(
            protocol_sha,
            "f6957393a864090d484e29f16067807bf52cacf0688fc48af32164ef9f7eb5a4",
        )
        self.assertEqual(auth["protocol_sha256"], protocol_sha)

    def test_authorization_scope_is_bounded(self):
        auth = json.loads(AUTH.read_text(encoding="utf-8"))
        self.assertTrue(auth["timestamp_level_extraction_authorized"])
        self.assertTrue(auth["authorization_scope"]["independent_validation_authorized"])
        self.assertTrue(auth["authorization_scope"]["deterministic_repeat_execution_authorized"])
        self.assertFalse(auth["trace_population_freeze_authorized"])
        self.assertFalse(auth["recovery_policy_execution_authorized"])
        self.assertFalse(auth["scientific_execution_authorized"])
        self.assertFalse(auth["authorization_scope"]["manuscript_claim_use_authorized"])
        self.assertFalse(auth["authorization_scope"]["gap_rule_retuning_authorized"])

    def test_design_merge_and_ci_are_bound(self):
        auth = json.loads(AUTH.read_text(encoding="utf-8"))
        self.assertTrue(auth["design_merge_verified"])
        self.assertTrue(auth["design_post_merge_ci_success"])
        self.assertTrue(auth["author_execution_approval_recorded"])
        self.assertEqual(
            auth["design_evidence"]["design_merge_commit"],
            "92534c45c85ee36c148acfe92dce1ec61ad49c24",
        )
        self.assertEqual(auth["design_evidence"]["design_post_merge_ci_run_number"], 1244)
        self.assertEqual(auth["design_evidence"]["design_post_merge_ci_run_id"], 36334882085)

    def test_execution_state_is_still_empty(self):
        auth = json.loads(AUTH.read_text(encoding="utf-8"))
        self.assertTrue(
            all(
                value is False
                for value in auth["execution_state_at_authorization_record_creation"].values()
            )
        )

    def test_record_is_not_declared_effective_before_merge(self):
        auth = json.loads(AUTH.read_text(encoding="utf-8"))
        effectivity = auth["effectivity"]
        self.assertTrue(effectivity["record_effective_only_when_tracked_on_main"])
        self.assertTrue(effectivity["record_currently_prepared_on_feature_branch"])
        self.assertTrue(effectivity["record_merge_requires_separate_author_review"])


if __name__ == "__main__":
    unittest.main()
