from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from src.mission_recovery.wp9_r066_campaign_evidence_freshness import (
    validate_fresh_campaign_evidence,
)


def _request(run_id: str = "r066-freshness") -> dict:
    return {
        "schema": 1,
        "decision_id": "R-066",
        "classification": "WP9_R066_FINAL_CAMPAIGN_RUNTIME_REQUEST",
        "run_id": run_id,
        "campaign_seed": 10001,
        "cell_id": "A19",
        "evidence_directory": (
            f"results/wp9/campaign/seed-10001/A19/{run_id}"
        ),
    }


class WP9R066CampaignEvidenceFreshnessTests(unittest.TestCase):
    def test_fresh_exact_namespaces_pass_without_writes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = validate_fresh_campaign_evidence(_request(), root=root)
            self.assertTrue(result["evidence_directory_fresh"])
            self.assertTrue(result["nominal_runtime_evidence_directory_fresh"])
            self.assertTrue(result["parent_symlink_free"])
            self.assertTrue(result["resolved_namespace_confined"])
            self.assertTrue(result["hidden_rerun_blocked"])
            self.assertFalse(result["filesystem_write_performed"])
            self.assertFalse(result["runtime_execution_performed"])
            self.assertFalse(result["campaign_seed_consumed"])
            self.assertFalse(result["campaign_data_generated"])
            self.assertFalse((root / result["evidence_directory"]).exists())
            self.assertFalse(
                (root / result["nominal_runtime_evidence_directory"]).exists()
            )

    def test_existing_campaign_run_directory_is_blocked(self) -> None:
        request = _request("r066-existing")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / request["evidence_directory"]
            target.mkdir(parents=True)
            with self.assertRaisesRegex(ValueError, "hidden rerun blocked"):
                validate_fresh_campaign_evidence(request, root=root)

    def test_existing_campaign_run_symlink_is_blocked(self) -> None:
        request = _request("r066-symlink")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / request["evidence_directory"]
            target.parent.mkdir(parents=True)
            target.symlink_to(root / "missing-target", target_is_directory=True)
            with self.assertRaisesRegex(ValueError, "hidden rerun blocked"):
                validate_fresh_campaign_evidence(request, root=root)

    def test_existing_nominal_runtime_directory_is_blocked(self) -> None:
        request = _request("r066-runtime-existing")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "artifacts" / "runtime" / request["run_id"]
            target.mkdir(parents=True)
            with self.assertRaisesRegex(
                ValueError, "nominal runtime evidence directory already exists"
            ):
                validate_fresh_campaign_evidence(request, root=root)

    def test_nominal_runtime_parent_symlink_is_blocked(self) -> None:
        request = _request("r066-runtime-parent-symlink")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            external = root / "external-runtime"
            external.mkdir()
            runtime_parent = root / "artifacts" / "runtime"
            runtime_parent.parent.mkdir(parents=True)
            runtime_parent.symlink_to(external, target_is_directory=True)
            with self.assertRaisesRegex(ValueError, "parent symlink blocked"):
                validate_fresh_campaign_evidence(request, root=root)

    def test_parent_symlink_cannot_redirect_campaign_namespace(self) -> None:
        request = _request("r066-parent-symlink")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            external = root / "external"
            external.mkdir()
            seed_parent = root / "results" / "wp9" / "campaign" / "seed-10001"
            seed_parent.parent.mkdir(parents=True)
            seed_parent.symlink_to(external, target_is_directory=True)
            with self.assertRaisesRegex(ValueError, "parent symlink blocked"):
                validate_fresh_campaign_evidence(request, root=root)

    def test_run_id_path_traversal_is_blocked(self) -> None:
        request = _request("../escape")
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError, "one relative path component"):
                validate_fresh_campaign_evidence(request, root=Path(tmp))

    def test_noncanonical_campaign_path_is_blocked(self) -> None:
        request = _request()
        request["evidence_directory"] = "results/wp9/campaign/other"
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError, "exact campaign evidence path"):
                validate_fresh_campaign_evidence(request, root=Path(tmp))

    def test_development_namespace_is_blocked(self) -> None:
        request = _request()
        request["evidence_directory"] = "results/wp9/development/r066/test"
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                validate_fresh_campaign_evidence(request, root=Path(tmp))


if __name__ == "__main__":
    unittest.main()
