import unittest

from src.mission_recovery.update_artifacts import (
    build_approved_update,
    build_downgrade_update,
    build_manifest,
    build_tampered_update,
    sha256_hex,
    verify_candidate,
)


class UpdateArtifactTests(unittest.TestCase):
    def test_artifacts_are_deterministic(self):
        self.assertEqual(build_approved_update(), build_approved_update())
        self.assertEqual(build_tampered_update(), build_tampered_update())

    def test_approved_artifact_matches_manifest(self):
        manifest = build_manifest()
        result = verify_candidate(build_approved_update(), manifest)
        self.assertTrue(result["accepted"])
        self.assertEqual(result["reasons"], [])
        self.assertEqual(
            result["actual_sha256"],
            manifest["approved_sha256"],
        )

    def test_tampered_same_version_is_rejected_by_hash(self):
        manifest = build_manifest()
        result = verify_candidate(build_tampered_update(), manifest)
        self.assertFalse(result["accepted"])
        self.assertIn("sha256_mismatch", result["reasons"])
        self.assertEqual(result["version"], "2.0.0")

    def test_downgrade_is_rejected(self):
        manifest = build_manifest()
        result = verify_candidate(build_downgrade_update(), manifest)
        self.assertFalse(result["accepted"])
        self.assertIn("version_not_approved", result["reasons"])
        self.assertIn("version_below_minimum", result["reasons"])

    def test_approved_and_tampered_hashes_differ(self):
        self.assertNotEqual(
            sha256_hex(build_approved_update()),
            sha256_hex(build_tampered_update()),
        )


if __name__ == "__main__":
    unittest.main()
