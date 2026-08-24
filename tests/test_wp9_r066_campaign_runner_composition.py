from __future__ import annotations

import copy
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.mission_recovery.wp9_campaign_trial_controller import build_trial_plan
from src.mission_recovery.wp9_final_campaign_bridge import (
    AUTHORIZATION_CLASSIFICATION,
    build_authorization_request,
)
from src.mission_recovery import wp9_r066_campaign_runtime_executor as executor
from src.mission_recovery import wp9_r066_final_campaign_runtime_binding as binding
from src.mission_recovery.wp9_r066_campaign_evidence_freshness import (
    validate_fresh_campaign_evidence,
)

REPO_SHA = "d" * 40


def _derive_request(cell_id: str = "A19") -> dict:
    return {
        "source_harness": copy.deepcopy(binding.CELL_HARNESS_BINDINGS[cell_id]),
        "cell_id": cell_id,
        "campaign_seed": 10001,
    }


def _full_request(run_id: str) -> dict:
    plan = build_trial_plan(
        campaign_seed=10001,
        cell_id="A19",
        run_id=run_id,
        repo_commit=REPO_SHA,
    )
    authorization = build_authorization_request(plan)
    authorization["classification"] = AUTHORIZATION_CLASSIFICATION
    authorization["single_trial_runtime_authorized"] = True
    return binding.build_campaign_runtime_request(
        plan=plan,
        authorization=authorization,
        attempt_history=[],
        current_repo_sha=REPO_SHA,
    )


class WP9R066CampaignRunnerCompositionTests(unittest.TestCase):
    def test_campaign_wrapper_injects_runtime_composition_without_mutating_binding_globals(self) -> None:
        request = _derive_request()
        original_derive = binding.derive_harness_text
        original_shim = binding._shim_text

        def fake_run_source_harness(
            supplied_request: dict,
            *,
            derive_harness_text_fn=None,
            shim_text_fn=None,
        ) -> dict:
            self.assertIs(binding.derive_harness_text, original_derive)
            self.assertIs(binding._shim_text, original_shim)
            self.assertIs(derive_harness_text_fn, executor.derive_runtime_harness_text)
            self.assertIs(shim_text_fn, executor._shim_text)
            text, derivation = derive_harness_text_fn(request=supplied_request)
            self.assertEqual(
                derivation["post_readiness_seed_commit_insertion_count"], 1
            )
            self.assertEqual(text.count("mark-seed"), 1)
            self.assertIn("shim-select-policy", shim_text_fn())
            return {"composition": "PASS"}

        with patch.object(
            binding,
            "run_source_harness",
            side_effect=fake_run_source_harness,
        ) as runner:
            result = executor.run_campaign_source_harness(request)

        self.assertEqual(result, {"composition": "PASS"})
        self.assertEqual(runner.call_count, 1)
        self.assertIs(binding.derive_harness_text, original_derive)
        self.assertIs(binding._shim_text, original_shim)

    def test_composition_failure_occurs_before_campaign_evidence_write(self) -> None:
        request = _full_request("r066-pre-runtime-composition-failure")

        def fake_git_run(command, **kwargs):
            if command == ["git", "rev-parse", "HEAD"]:
                return subprocess.CompletedProcess(command, 0, stdout=REPO_SHA + "\n")
            if command == ["git", "status", "--short"]:
                return subprocess.CompletedProcess(command, 0, stdout="")
            raise AssertionError(f"unexpected subprocess before composition: {command}")

        cases = (
            (
                "derive",
                lambda *, request: (_ for _ in ()).throw(
                    RuntimeError("synthetic derive failure")
                ),
                lambda: "#!/bin/bash\n",
                "synthetic derive failure",
            ),
            (
                "shim",
                lambda *, request: ("#!/bin/bash\n", {"schema": 1}),
                lambda: (_ for _ in ()).throw(
                    RuntimeError("synthetic shim failure")
                ),
                "synthetic shim failure",
            ),
        )

        for label, deriver, shim_builder, message in cases:
            with self.subTest(label=label), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                with patch.object(binding, "ROOT", root), patch.object(
                    binding,
                    "source_harness_blob_sha",
                    return_value=request["source_harness"]["source_blob_sha"],
                ), patch.object(binding.subprocess, "run", side_effect=fake_git_run):
                    with self.assertRaisesRegex(RuntimeError, message):
                        binding.run_source_harness(
                            request,
                            derive_harness_text_fn=deriver,
                            shim_text_fn=shim_builder,
                        )

                self.assertFalse((root / request["evidence_directory"]).exists())

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
