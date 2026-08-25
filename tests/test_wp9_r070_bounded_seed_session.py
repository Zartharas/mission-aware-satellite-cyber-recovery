from __future__ import annotations

import copy
import unittest

from src.mission_recovery.wp9_final_campaign_bridge import frozen_campaign_sequence
from src.mission_recovery.wp9_r070_bounded_seed_session import (
    build_seed_session_plan,
    validate_child_progression,
    validate_static_seed_session,
)


def valid_history(count: int) -> list[dict[str, object]]:
    sequence = frozen_campaign_sequence()
    rows: list[dict[str, object]] = []
    for index, position in enumerate(sequence[:count], start=1):
        rows.append(
            {
                "campaign_seed": int(position["campaign_seed"]),
                "cell_order_index": int(position["cell_order_index"]),
                "cell_id": str(position["cell_id"]),
                "run_id": f"test-valid-{index:04d}",
                "attempt_status": "VALID",
            }
        )
    return rows


class TestR070BoundedSeedSession(unittest.TestCase):
    def test_empty_history_plans_exact_first_seed_block(self) -> None:
        plan = build_seed_session_plan([])
        self.assertEqual(plan["campaign_seed"], 10001)
        self.assertEqual(plan["start_global_order_index"], 1)
        self.assertEqual(plan["end_global_order_index"], 24)
        self.assertEqual(plan["planned_valid_position_count"], 24)
        self.assertEqual(plan["positions"][0]["cell_id"], "A19")
        self.assertEqual(plan["positions"][-1]["cell_id"], "A17")

    def test_after_ten_valid_positions_plans_only_remaining_same_seed(self) -> None:
        plan = build_seed_session_plan(valid_history(10))
        self.assertEqual(plan["campaign_seed"], 10001)
        self.assertEqual(plan["start_global_order_index"], 11)
        self.assertEqual(plan["end_global_order_index"], 24)
        self.assertEqual(plan["planned_valid_position_count"], 14)
        self.assertEqual(plan["positions"][0]["cell_id"], "A08")
        self.assertEqual(plan["positions"][-1]["cell_id"], "A17")

    def test_invalid_attempt_does_not_advance_session_start(self) -> None:
        history = valid_history(10)
        position = frozen_campaign_sequence()[10]
        history.append(
            {
                "campaign_seed": int(position["campaign_seed"]),
                "cell_order_index": int(position["cell_order_index"]),
                "cell_id": str(position["cell_id"]),
                "run_id": "test-invalid-0011",
                "attempt_status": "INVALID",
            }
        )
        plan = build_seed_session_plan(history)
        self.assertEqual(plan["start_global_order_index"], 11)
        self.assertEqual(plan["positions"][0]["cell_id"], "A08")
        self.assertEqual(plan["prior_invalid_attempt_count"], 1)

    def test_seed_boundary_never_crossed(self) -> None:
        plan = build_seed_session_plan(valid_history(24))
        self.assertEqual(plan["campaign_seed"], 10002)
        self.assertEqual(plan["start_global_order_index"], 25)
        self.assertEqual(plan["planned_valid_position_count"], 24)
        self.assertTrue(
            all(int(row["campaign_seed"]) == 10002 for row in plan["positions"])
        )

    def test_valid_child_append_allows_only_frozen_same_seed_progression(self) -> None:
        before = valid_history(10)
        after = copy.deepcopy(before)
        position = frozen_campaign_sequence()[10]
        after.append(
            {
                "campaign_seed": int(position["campaign_seed"]),
                "cell_order_index": int(position["cell_order_index"]),
                "cell_id": str(position["cell_id"]),
                "run_id": "test-valid-0011",
                "attempt_status": "VALID",
            }
        )
        result = validate_child_progression(
            before_history=before,
            after_history=after,
            session_seed=10001,
        )
        self.assertTrue(result["child_attempt_valid"])
        self.assertFalse(result["stop_required"])
        self.assertEqual(result["next_global_order_index"], 12)
        self.assertEqual(result["next_campaign_seed"], 10001)

    def test_invalid_child_append_requires_hard_stop_without_retry(self) -> None:
        before = valid_history(10)
        after = copy.deepcopy(before)
        position = frozen_campaign_sequence()[10]
        after.append(
            {
                "campaign_seed": int(position["campaign_seed"]),
                "cell_order_index": int(position["cell_order_index"]),
                "cell_id": str(position["cell_id"]),
                "run_id": "test-invalid-0011",
                "attempt_status": "INVALID",
            }
        )
        result = validate_child_progression(
            before_history=before,
            after_history=after,
            session_seed=10001,
        )
        self.assertFalse(result["child_attempt_valid"])
        self.assertTrue(result["stop_required"])
        self.assertEqual(result["stop_reason"], "INVALID_ATTEMPT_REQUIRES_REVIEW")
        self.assertFalse(result["automatic_retry_allowed"])

    def test_multiple_appends_are_rejected(self) -> None:
        before = valid_history(10)
        after = valid_history(12)
        with self.assertRaisesRegex(ValueError, "exactly one attempt"):
            validate_child_progression(
                before_history=before,
                after_history=after,
                session_seed=10001,
            )

    def test_static_contract_preserves_trial_integrity(self) -> None:
        row = validate_static_seed_session()
        self.assertEqual(row["session_max_valid_positions"], 24)
        self.assertTrue(row["single_runtime_trial_per_child_invocation"])
        self.assertFalse(row["child_automatic_retry_allowed"])
        self.assertFalse(row["child_automatic_next_case_allowed"])
        self.assertFalse(row["session_automatic_retry_allowed"])
        self.assertTrue(row["session_stops_on_invalid_attempt"])
        self.assertTrue(row["session_stops_on_nonzero_return"])
        self.assertTrue(row["session_stops_at_seed_boundary"])
        self.assertTrue(row["session_frozen_order_enforced"])
        self.assertFalse(row["scientific_outcome_used_to_control_progression"])
        self.assertTrue(row["unexpected_valid_scientific_outcome_retained"])
        self.assertFalse(row["concurrent_session_allowed"])
        self.assertFalse(row["campaign_wide_execution_authorized"])


if __name__ == "__main__":
    unittest.main()
