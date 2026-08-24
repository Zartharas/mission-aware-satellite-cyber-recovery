from __future__ import annotations

import copy
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from src.mission_recovery.wp9_campaign_trial_controller import build_trial_plan
from src.mission_recovery.wp9_final_campaign_bridge import (
    AUTHORIZATION_CLASSIFICATION,
    build_authorization_request,
    frozen_campaign_sequence,
)
from src.mission_recovery.wp9_r064_attempt_history import (
    validate_attempt_history,
)
from src.mission_recovery.wp9_r066_campaign_runtime_executor import (
    _READINESS_MARKER,
    _shim_text,
    derive_runtime_harness_text,
    execute_request,
    mark_seed_consumed,
    run_campaign_source_harness,
    shim_plan,
    shim_select_policy,
    validate_static_executor,
)
from src.mission_recovery.wp9_r066_final_campaign_runtime_binding import (
    CELL_HARNESS_BINDINGS,
    build_campaign_runtime_request,
    execute_campaign_runtime_request,
    source_harness_blob_sha,
)

ROOT = Path(__file__).resolve().parents[1]
REPO_SHA = "b" * 40


def _plan(cell_id: str, seed: int, run_id: str) -> dict:
    return build_trial_plan(
        campaign_seed=seed,
        cell_id=cell_id,
        run_id=run_id,
        repo_commit=REPO_SHA,
    )


def _granted(plan: dict) -> dict:
    auth = build_authorization_request(plan)
    auth["classification"] = AUTHORIZATION_CLASSIFICATION
    auth["single_trial_runtime_authorized"] = True
    return auth


def _request(cell_id: str = "A19", seed: int = 10001, run_id: str = "r066-test") -> dict:
    plan = _plan(cell_id, seed, run_id)
    return build_campaign_runtime_request(
        plan=plan,
        authorization=_granted(plan),
        attempt_history=[],
        current_repo_sha=REPO_SHA,
    )


class WP9R066CampaignRuntimeExecutorTests(unittest.TestCase):
    def test_static_executor_closes_phase9_binding_gap_without_authorizing_runtime(self) -> None:
        result = validate_static_executor()
        self.assertEqual(result["campaign_cell_count"], 24)
        self.assertEqual(result["runtime_family_count"], 4)
        self.assertTrue(result["production_runtime_executor_bound"])
        self.assertTrue(result["source_harness_blob_identity_enforced"])
        self.assertTrue(result["post_readiness_seed_commit_enforced"])
        self.assertTrue(result["pre_readiness_failure_can_remain_seed_unconsumed"])
        self.assertTrue(result["e3_runtime_policy_compatibility_intercepted"])
        self.assertTrue(result["one_source_harness_invocation_per_trial"])
        self.assertFalse(result["automatic_retry_allowed"])
        self.assertFalse(result["automatic_next_case_allowed"])
        self.assertFalse(result["runtime_execution_performed"])
        self.assertFalse(result["campaign_seed_consumed"])
        self.assertFalse(result["campaign_data_generated"])
        self.assertFalse(result["campaign_runtime_authorized"])

    def test_each_derived_harness_has_exact_three_plumbing_edits_and_bash_syntax(self) -> None:
        for cell_id, binding in CELL_HARNESS_BINDINGS.items():
            with self.subTest(cell_id=cell_id):
                request = {
                    "source_harness": copy.deepcopy(binding),
                    "cell_id": cell_id,
                    "campaign_seed": 10001,
                }
                original_path = ROOT / binding["source_path"]
                before_blob = source_harness_blob_sha(original_path)
                text, derivation = derive_runtime_harness_text(request=request)
                self.assertEqual(
                    before_blob,
                    binding["source_blob_sha"],
                )
                self.assertEqual(derivation["root_line_replacement_count"], 1)
                self.assertEqual(derivation["case_mapping_replacement_count"], 1)
                self.assertEqual(
                    derivation["post_readiness_seed_commit_insertion_count"], 1
                )
                self.assertEqual(text.count(_READINESS_MARKER), 1)
                self.assertEqual(text.count("mark-seed"), 1)
                self.assertEqual(text.count("WP9_R066_REPO_ROOT"), 1)
                self.assertEqual(
                    source_harness_blob_sha(original_path),
                    before_blob,
                )
                with tempfile.NamedTemporaryFile(
                    "w", suffix=".sh", delete=False, encoding="utf-8"
                ) as handle:
                    handle.write(text)
                    derived = Path(handle.name)
                try:
                    checked = subprocess.run(
                        ["/bin/bash", "-n", str(derived)],
                        cwd=ROOT,
                        check=False,
                        capture_output=True,
                        text=True,
                    )
                    self.assertEqual(checked.returncode, 0, checked.stderr)
                finally:
                    derived.unlink(missing_ok=True)

    def test_all_source_harnesses_have_one_common_post_isolation_readiness_boundary(self) -> None:
        paths = {row["source_path"] for row in CELL_HARNESS_BINDINGS.values()}
        self.assertEqual(len(paths), 4)
        for path in paths:
            with self.subTest(path=path):
                text = (ROOT / path).read_text(encoding="utf-8")
                self.assertEqual(text.count(_READINESS_MARKER), 1)

    def test_python_shim_intercepts_e3_policy_selection_in_addition_to_plan_and_finalize(self) -> None:
        shim = _shim_text()
        self.assertIn('COMMAND" = "plan-development"', shim)
        self.assertIn('COMMAND" = "select-policy"', shim)
        self.assertIn("shim-select-policy", shim)
        self.assertIn('COMMAND" = "finalize-development"', shim)
        self.assertNotIn("materialize-artifacts", shim)
        self.assertNotIn("build-p5-handoff", shim)

    def test_shim_plan_does_not_mark_seed_before_runtime_readiness(self) -> None:
        plan = _plan("A19", 10001, "r066-plan-no-seed")
        with tempfile.TemporaryDirectory() as tmp:
            evidence = Path(tmp) / "campaign"
            evidence.mkdir(parents=True)
            plan_path = Path(tmp) / "plan.json"
            output = Path(tmp) / "compat.json"
            plan_path.write_text(json.dumps(plan), encoding="utf-8")
            env = {
                "WP9_R066_CAMPAIGN_PLAN_JSON": str(plan_path),
                "WP9_R066_CAMPAIGN_EVIDENCE_DIRECTORY": str(evidence),
                "WP9_R066_CAMPAIGN_EVIDENCE_PREFIX": "results/wp9/campaign/test",
            }
            with patch.dict(os.environ, env, clear=False):
                shim_plan(family="E2", output_json=output)
            self.assertTrue(output.is_file())
            self.assertFalse(
                (evidence / "immutable-ground" / "campaign-seed-consumption.json").exists()
            )

    def test_seed_commit_occurs_once_at_post_readiness_boundary(self) -> None:
        plan = _plan("A19", 10001, "r066-seed-once")
        with tempfile.TemporaryDirectory() as tmp:
            evidence = Path(tmp) / "campaign"
            evidence.mkdir(parents=True)
            plan_path = Path(tmp) / "plan.json"
            plan_path.write_text(json.dumps(plan), encoding="utf-8")
            env = {
                "WP9_R066_CAMPAIGN_PLAN_JSON": str(plan_path),
                "WP9_R066_CAMPAIGN_EVIDENCE_DIRECTORY": str(evidence),
                "WP9_R066_CAMPAIGN_EVIDENCE_PREFIX": "results/wp9/campaign/test",
            }
            with patch.dict(os.environ, env, clear=False):
                marker = mark_seed_consumed()
                self.assertTrue(marker["campaign_seed_consumed"])
                self.assertFalse(marker["campaign_data_generated"])
                with self.assertRaisesRegex(ValueError, "already exists"):
                    mark_seed_consumed()
            retained = json.loads(
                (
                    evidence
                    / "immutable-ground"
                    / "campaign-seed-consumption.json"
                ).read_text(encoding="utf-8")
            )
            self.assertEqual(retained["campaign_seed"], 10001)
            self.assertEqual(retained["cell_id"], "A19")
            self.assertEqual(
                retained["commit_boundary"],
                "after_nominal_runtime_readiness_and_isolation",
            )

    def test_e3_policy_shim_accepts_campaign_cell_not_historical_source_cell(self) -> None:
        for cell_id in ("A10", "A12", "A14", "A16", "A17", "A18"):
            with self.subTest(cell_id=cell_id):
                plan = _plan(cell_id, 10001, f"r066-policy-{cell_id.lower()}")
                from src.mission_recovery.wp9_r066_final_campaign_runtime_binding import (
                    build_compatibility_plan,
                )
                compat = build_compatibility_plan(plan=plan)
                with tempfile.TemporaryDirectory() as tmp:
                    plan_path = Path(tmp) / "compat.json"
                    output = Path(tmp) / "policy.json"
                    plan_path.write_text(json.dumps(compat), encoding="utf-8")
                    shim_select_policy(plan_json=plan_path, output_json=output)
                    policy = json.loads(output.read_text(encoding="utf-8"))
                self.assertEqual(policy["cell_id"], cell_id)
                self.assertEqual(policy["development_seed"], 10001)
                self.assertEqual(policy["campaign_seed"], 10001)
                self.assertFalse(policy["oracle_ground_truth_read"])
                self.assertEqual(
                    policy["delegated_policy_id"],
                    plan["expected_effective_policy_id_for_acceptance_only"],
                )

    def test_authorized_execution_invokes_supplied_runner_once_and_never_advances(self) -> None:
        request = _request()
        env = {
            "WP9_R066_FINAL_CAMPAIGN_RUNTIME_AUTHORIZED": "1",
            "WP9_R066_AUTHORIZED_RUN_ID": request["run_id"],
            "WP9_R066_AUTHORIZED_SEED": str(request["campaign_seed"]),
            "WP9_R066_AUTHORIZED_CELL": request["cell_id"],
            "WP9_R066_AUTHORIZED_REPO_SHA": request["repo_commit"],
        }
        runner = Mock(
            return_value={
                "run_id": request["run_id"],
                "campaign_seed": request["campaign_seed"],
                "cell_id": request["cell_id"],
                "attempt_status": "VALID",
                "runtime_execution_performed": True,
                "campaign_seed_consumed": True,
                "campaign_data_generated": True,
                "automatic_retry_performed": False,
                "automatic_next_case_performed": False,
            }
        )
        result = execute_campaign_runtime_request(
            request=request,
            runner=runner,
            authorization_environment=env,
        )
        self.assertEqual(runner.call_count, 1)
        self.assertEqual(result["source_harness_invocation_count"], 1)
        self.assertFalse(result["automatic_retry_performed"])
        self.assertFalse(result["automatic_next_case_performed"])

    def test_runner_failure_is_not_retried(self) -> None:
        request = _request(run_id="r066-runner-failure")
        env = {
            "WP9_R066_FINAL_CAMPAIGN_RUNTIME_AUTHORIZED": "1",
            "WP9_R066_AUTHORIZED_RUN_ID": request["run_id"],
            "WP9_R066_AUTHORIZED_SEED": str(request["campaign_seed"]),
            "WP9_R066_AUTHORIZED_CELL": request["cell_id"],
            "WP9_R066_AUTHORIZED_REPO_SHA": request["repo_commit"],
        }
        runner = Mock(side_effect=RuntimeError("synthetic runner failure"))
        with self.assertRaisesRegex(RuntimeError, "synthetic runner failure"):
            execute_campaign_runtime_request(
                request=request,
                runner=runner,
                authorization_environment=env,
            )
        self.assertEqual(runner.call_count, 1)

    def test_invalid_history_requires_new_run_id_same_frozen_position(self) -> None:
        first = frozen_campaign_sequence()[0]
        history = [
            {
                "campaign_seed": first["campaign_seed"],
                "cell_order_index": first["cell_order_index"],
                "cell_id": first["cell_id"],
                "run_id": "r066-invalid-first",
                "attempt_status": "INVALID",
            }
        ]
        validated = validate_attempt_history(history)
        self.assertEqual(validated["valid_position_count"], 0)

        retry_plan = _plan("A19", 10001, "r066-valid-second-id")
        request = build_campaign_runtime_request(
            plan=retry_plan,
            authorization=_granted(retry_plan),
            attempt_history=history,
            current_repo_sha=REPO_SHA,
        )
        self.assertEqual(request["global_order_index"], 1)
        self.assertEqual(request["campaign_seed"], 10001)
        self.assertEqual(request["cell_id"], "A19")
        self.assertEqual(request["prior_invalid_attempt_count"], 1)

        duplicate_plan = _plan("A19", 10001, "r066-invalid-first")
        with self.assertRaisesRegex(ValueError, "run_id"):
            build_campaign_runtime_request(
                plan=duplicate_plan,
                authorization=_granted(duplicate_plan),
                attempt_history=history,
                current_repo_sha=REPO_SHA,
            )

    def test_valid_history_advances_exactly_one_position(self) -> None:
        sequence = frozen_campaign_sequence()
        first, second = sequence[0], sequence[1]
        history = [
            {
                "campaign_seed": first["campaign_seed"],
                "cell_order_index": first["cell_order_index"],
                "cell_id": first["cell_id"],
                "run_id": "r066-first-valid",
                "attempt_status": "VALID",
            }
        ]
        plan = _plan(second["cell_id"], second["campaign_seed"], "r066-second")
        request = build_campaign_runtime_request(
            plan=plan,
            authorization=_granted(plan),
            attempt_history=history,
            current_repo_sha=REPO_SHA,
        )
        self.assertEqual(request["global_order_index"], 2)
        self.assertEqual(request["cell_id"], second["cell_id"])
        self.assertEqual(request["campaign_seed"], second["campaign_seed"])

    def test_real_runner_symbol_is_not_called_by_static_validation(self) -> None:
        with patch(
            "src.mission_recovery.wp9_r066_campaign_runtime_executor.run_campaign_source_harness"
        ) as runner:
            validate_static_executor()
            runner.assert_not_called()


if __name__ == "__main__":
    unittest.main()
