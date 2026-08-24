from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from src.mission_recovery.wp9_r069_campaign_one_position_operator import (
    append_attempt_result_atomic,
    audit_unledgered_campaign_artifacts,
    inspect_runtime_request,
    prepare_next_attempt,
    validate_static_operator,
)


CURRENT_SHA = "72e3a9d81d70b2b993bf28228f3b7b0af24c9908"
POSITION1_RUN = "r069-test-position1"
POSITION2_INVALID_RUN = "r069-test-position2-invalid"
POSITION2_RETRY_RUN = "r069-test-position2-retry"


def retained_valid_position1() -> dict:
    return {
        "schema": 1,
        "decision_id": "R-066",
        "classification": "WP9_R066_FINAL_CAMPAIGN_VALID_TRIAL_RESULT",
        "run_id": POSITION1_RUN,
        "campaign_seed": 10001,
        "cell_id": "A19",
        "attempt_status": "VALID",
        "runtime_execution_performed": True,
        "campaign_seed_consumed": True,
        "campaign_data_generated": True,
        "source_harness_invocation_count": 1,
        "automatic_retry_performed": False,
        "automatic_next_case_performed": False,
        "treatment_fidelity_valid": True,
        "raw_metric_inputs_complete": True,
        "run_record": {
            "environment": {"snapshot_id": "repo-" + CURRENT_SHA},
        },
    }


def retained_invalid_position2() -> dict:
    return {
        "schema": 1,
        "decision_id": "R-066",
        "classification": "WP9_R066_FINAL_CAMPAIGN_INVALID_TRIAL_RESULT",
        "run_id": POSITION2_INVALID_RUN,
        "campaign_seed": 10001,
        "cell_id": "A13",
        "attempt_status": "INVALID",
        "runtime_execution_performed": True,
        "campaign_seed_consumed": True,
        "campaign_data_generated": True,
        "source_harness_invocation_count": 1,
        "source_harness_return_code": 1,
        "invalid_attempt_retained": True,
        "automatic_retry_performed": False,
        "automatic_next_case_performed": False,
        "run_record": {
            "environment": {"snapshot_id": "repo-" + CURRENT_SHA},
        },
    }


class R069OperatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.history = [
            {
                "campaign_seed": 10001,
                "cell_order_index": 1,
                "cell_id": "A19",
                "run_id": POSITION1_RUN,
                "attempt_status": "VALID",
            },
            {
                "campaign_seed": 10001,
                "cell_order_index": 2,
                "cell_id": "A13",
                "run_id": POSITION2_INVALID_RUN,
                "attempt_status": "INVALID",
            },
        ]
        self.retained = {
            POSITION1_RUN: retained_valid_position1(),
            POSITION2_INVALID_RUN: retained_invalid_position2(),
        }

    def test_static_contract_is_one_position_fail_closed(self) -> None:
        row = validate_static_operator()
        self.assertEqual(row["decision_id"], "R-069")
        self.assertTrue(row["schema_aware_request_inspection"])
        self.assertTrue(row["r068_continuity_required"])
        self.assertTrue(row["atomic_attempt_history_append"])
        self.assertTrue(row["one_trial_per_invocation"])
        self.assertFalse(row["automatic_retry_allowed"])
        self.assertFalse(row["automatic_next_case_allowed"])
        self.assertFalse(row["runtime_execution_performed"])
        self.assertFalse(row["campaign_seed_consumed"])
        self.assertFalse(row["campaign_data_generated"])

    def test_prepare_retry_uses_exact_next_position_and_nested_schema(self) -> None:
        prepared = prepare_next_attempt(
            attempt_history=self.history,
            retained_results=self.retained,
            current_repo_sha=CURRENT_SHA,
            run_id=POSITION2_RETRY_RUN,
            is_ancestor=lambda old, new: old == CURRENT_SHA and new == CURRENT_SHA,
        )
        self.assertEqual(prepared["next_trial"]["global_order_index"], 2)
        self.assertEqual(prepared["next_trial"]["campaign_seed"], 10001)
        self.assertEqual(prepared["next_trial"]["cell_order_index"], 2)
        self.assertEqual(prepared["next_trial"]["cell_id"], "A13")
        self.assertEqual(prepared["plan"]["run_id"], POSITION2_RETRY_RUN)
        self.assertEqual(prepared["plan"]["runtime_family"], "recovery")
        self.assertEqual(prepared["plan"]["runtime_variant"], "e3_command_gateway")
        self.assertEqual(prepared["request"]["prior_attempt_count"], 2)
        self.assertEqual(prepared["request"]["prior_valid_position_count"], 1)
        self.assertEqual(prepared["request"]["prior_invalid_attempt_count"], 1)
        self.assertNotIn("runtime_family", prepared["request"])
        summary = inspect_runtime_request(prepared["request"])
        self.assertEqual(summary["runtime_family"], "recovery")
        self.assertEqual(summary["runtime_variant"], "e3_command_gateway")
        self.assertEqual(summary["event_id"], "E3")
        self.assertEqual(summary["source_case"], "Y01")
        self.assertEqual(summary["source_cell"], "A13")
        self.assertEqual(summary["global_order_index"], 2)
        self.assertEqual(summary["campaign_seed"], 10001)
        self.assertEqual(summary["cell_id"], "A13")
        self.assertTrue(summary["request_schema_validated"])
        self.assertFalse(summary["automatic_retry_allowed"])
        self.assertFalse(summary["automatic_next_case_allowed"])
        self.assertFalse(summary["runtime_execution_performed"])
        self.assertFalse(summary["campaign_seed_consumed"])
        self.assertFalse(summary["campaign_data_generated"])

    def test_prepare_retry_rejects_reused_run_id(self) -> None:
        with self.assertRaises(ValueError):
            prepare_next_attempt(
                attempt_history=self.history,
                retained_results=self.retained,
                current_repo_sha=CURRENT_SHA,
                run_id=POSITION2_INVALID_RUN,
                is_ancestor=lambda old, new: True,
            )

    def test_atomic_append_preserves_invalid_then_advances_after_valid_retry(self) -> None:
        retry_result = {
            "attempt_status": "VALID",
            "run_id": POSITION2_RETRY_RUN,
            "campaign_seed": 10001,
            "cell_id": "A13",
            "source_harness_invocation_count": 1,
            "runtime_execution_performed": True,
            "campaign_seed_consumed": True,
            "campaign_data_generated": True,
            "campaign_wide_execution_authorized": False,
            "automatic_retry_performed": False,
            "automatic_next_case_performed": False,
            "runner_result": {
                "attempt_status": "VALID",
                "treatment_fidelity_valid": True,
                "raw_metric_inputs_complete": True,
            },
        }
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "attempt-history.json"
            path.write_text(json.dumps(self.history) + "\n", encoding="utf-8")
            state = append_attempt_result_atomic(
                attempt_history_path=path,
                executor_result=retry_result,
                cell_order_index=2,
            )
            written = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(len(written), 3)
        self.assertEqual(written[1]["attempt_status"], "INVALID")
        self.assertEqual(written[2]["attempt_status"], "VALID")
        self.assertEqual(state["attempt_count"], 3)
        self.assertEqual(state["valid_position_count"], 2)
        self.assertEqual(state["invalid_attempt_count"], 1)
        self.assertEqual(state["next_required_global_order_index"], 3)
        self.assertEqual(state["next_required_campaign_seed"], 10001)
        self.assertEqual(state["next_required_cell_order_index"], 3)
        self.assertNotEqual(state["next_required_cell_id"], "A13")

    def test_atomic_append_rejects_executor_auto_retry_or_wrong_position(self) -> None:
        bad = {
            "attempt_status": "VALID",
            "run_id": POSITION2_RETRY_RUN,
            "campaign_seed": 10001,
            "cell_id": "A13",
            "source_harness_invocation_count": 1,
            "runtime_execution_performed": True,
            "campaign_seed_consumed": True,
            "campaign_data_generated": True,
            "campaign_wide_execution_authorized": False,
            "automatic_retry_performed": True,
            "automatic_next_case_performed": False,
            "runner_result": {},
        }
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "attempt-history.json"
            path.write_text(json.dumps(self.history) + "\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                append_attempt_result_atomic(
                    attempt_history_path=path,
                    executor_result=bad,
                    cell_order_index=2,
                )

    def test_unledgered_pre_runtime_request_plan_is_retained_but_not_science(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            run = root / "seed-10001" / "A13" / "pre-runtime-abort"
            ground = run / "immutable-ground"
            ground.mkdir(parents=True)
            (ground / "campaign-plan.json").write_text("{}\n", encoding="utf-8")
            (ground / "r066-runtime-request.json").write_text("{}\n", encoding="utf-8")
            row = audit_unledgered_campaign_artifacts(
                attempt_history=self.history,
                campaign_root=root,
            )
        self.assertEqual(row["unledgered_pre_runtime_artifact_count"], 1)
        self.assertEqual(row["unledgered_pre_runtime_run_ids"], ["pre-runtime-abort"])
        self.assertFalse(row["unledgered_scientific_artifact_detected"])

    def test_unledgered_seed_commit_or_runtime_evidence_is_fail_closed(self) -> None:
        for relative in (
            "immutable-ground/campaign-seed-consumption.json",
            "campaign-trial-result.json",
            "campaign-trial-invalid.json",
            "source-harness.stderr.log",
            "runtime-observation/measurement.json",
        ):
            with self.subTest(relative=relative), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                run = root / "seed-10001" / "A13" / "unledgered-runtime"
                target = run / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text("{}\n", encoding="utf-8")
                with self.assertRaises(ValueError):
                    audit_unledgered_campaign_artifacts(
                        attempt_history=self.history,
                        campaign_root=root,
                    )


if __name__ == "__main__":
    unittest.main()
