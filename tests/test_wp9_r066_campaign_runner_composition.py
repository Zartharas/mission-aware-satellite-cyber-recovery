from __future__ import annotations

import copy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.mission_recovery import wp9_r066_campaign_runtime_executor as executor
from src.mission_recovery import wp9_r066_final_campaign_runtime_binding as binding
from src.mission_recovery.wp9_r066_campaign_evidence_freshness import (
    validate_fresh_campaign_evidence,
)


def _derive_request(cell_id: str = "A19") -> dict:
    return {
        "source_harness": copy.deepcopy(binding.CELL_HARNESS_BINDINGS[cell_id]),
        "cell_id": cell_id,
        "campaign_seed": 10001,
    }


class WP9R066CampaignRunnerCompositionTests(unittest.TestCase):
    def test_campaign_wrapper_composes_without_recursion_and_restores_binding_globals(self) -> None:
        request = _derive_request()
        original_derive = binding.derive_harness_text
        original_shim = binding._shim_text

        def fake_run_source_harness(supplied_request: dict) -> dict:
            text, derivation = binding.derive_harness_text(
                request=supplied_request
            )
            shim = binding._shim_text()
            return {
                "post_readiness_seed_commit_insertion_count": derivation[
                    "post_readiness_seed_commit_insertion_count"
                ],
                "mark_seed_count": text.count("mark-seed"),
                "shim_select_policy_present": "shim-select-policy" in shim,
            }

        with patch.object(
            binding,
            "run_source_harness",
            side_effect=fake_run_source_harness,
        ) as runner:
            result = executor.run_campaign_source_harness(request)

        self.assertEqual(result["post_readiness_seed_commit_insertion_count"], 1)
        self.assertEqual(result["mark_seed_count"], 1)
        self.assertTrue(result["shim_select_policy_present"])
        self.assertEqual(runner.call_count, 1)
        self.assertIs(binding.derive_harness_text, original_derive)
        self.assertIs(binding._shim_text, original_shim)

    def test_composition_failure_stops_before_binding_runner_or_campaign_write(self) -> None:
        request = _derive_request()
        original_derive = binding.derive_harness_text
        original_shim = binding._shim_text

        with patch.object(
            executor,
            "derive_runtime_harness_text",
            side_effect=RuntimeError("synthetic composition failure"),
        ) as deriver, patch.object(binding, "run_source_harness") as runner:
            with self.assertRaisesRegex(
                RuntimeError,
                "synthetic composition failure",
            ):
                executor.run_campaign_source_harness(request)

        deriver.assert_called_once_with(request=request)
        runner.assert_not_called()
        self.assertIs(binding.derive_harness_text, original_derive)
        self.assertIs(binding._shim_text, original_shim)

    def test_retained_unconsumed_pre_runtime_artifact_does_not_block_fresh_run_id(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            prior = (
                root
                / "results"
                / "wp9"
                / "campaign"
                / "seed-10001"
                / "A19"
                / "r066-retained-pre-runtime"
                / "immutable-ground"
            )
            prior.mkdir(parents=True)
            (prior / "campaign-plan.json").write_text("{}\n", encoding="utf-8")
            (prior / "r066-runtime-request.json").write_text("{}\n", encoding="utf-8")
            self.assertFalse((prior / "campaign-seed-consumption.json").exists())

            run_id = "r066-fresh-after-pre-runtime"
            request = {
                "schema": 1,
                "decision_id": "R-066",
                "classification": "WP9_R066_FINAL_CAMPAIGN_RUNTIME_REQUEST",
                "run_id": run_id,
                "campaign_seed": 10001,
                "cell_id": "A19",
                "evidence_directory": (
                    "results/wp9/campaign/seed-10001/A19/" + run_id
                ),
            }
            result = validate_fresh_campaign_evidence(request, root=root)
            self.assertTrue(result["evidence_directory_fresh"])
            self.assertTrue(result["hidden_rerun_blocked"])
            self.assertFalse(result["campaign_seed_consumed"])


if __name__ == "__main__":
    unittest.main()
