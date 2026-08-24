from __future__ import annotations

import copy
import unittest

from src.mission_recovery.wp9_campaign_trial_controller import build_trial_plan
from src.mission_recovery.wp9_final_campaign_bridge import (
    AUTHORIZATION_CLASSIFICATION,
    build_authorization_request,
    build_execution_descriptor,
    frozen_campaign_sequence,
    next_required_trial_from_attempt_history,
    validate_attempt_history,
)

REPO_SHA = "a" * 40


def _attempt(position: dict, run_id: str, status: str) -> dict:
    return {
        "campaign_seed": position["campaign_seed"],
        "cell_order_index": position["cell_order_index"],
        "cell_id": position["cell_id"],
        "run_id": run_id,
        "attempt_status": status,
    }


def _granted(plan: dict) -> dict:
    authorization = build_authorization_request(plan)
    authorization["classification"] = AUTHORIZATION_CLASSIFICATION
    authorization["single_trial_runtime_authorized"] = True
    return authorization


class WP9R064AttemptHistoryTests(unittest.TestCase):
    def test_invalid_attempt_does_not_advance_and_new_run_id_is_required(self):
        sequence = frozen_campaign_sequence()
        first = sequence[0]
        history = [_attempt(first, "r064-first-invalid", "INVALID")]

        validated = validate_attempt_history(history)
        self.assertEqual(validated["valid_position_count"], 0)
        self.assertEqual(validated["attempt_count"], 1)
        self.assertEqual(
            next_required_trial_from_attempt_history(history),
            first,
        )

        with self.assertRaisesRegex(ValueError, "run_id"):
            validate_attempt_history(
                history + [_attempt(first, "r064-first-invalid", "VALID")]
            )

        accepted = history + [_attempt(first, "r064-first-valid", "VALID")]
        self.assertEqual(
            next_required_trial_from_attempt_history(accepted),
            sequence[1],
        )

    def test_attempt_history_rejects_hidden_rerun_and_out_of_order_attempt(self):
        sequence = frozen_campaign_sequence()
        first, second = sequence[0], sequence[1]

        with self.assertRaisesRegex(ValueError, "next frozen trial"):
            validate_attempt_history([_attempt(second, "wrong-first", "INVALID")])

        with self.assertRaisesRegex(ValueError, "next frozen trial"):
            validate_attempt_history(
                [
                    _attempt(first, "first-valid", "VALID"),
                    _attempt(first, "hidden-rerun", "INVALID"),
                ]
            )

    def test_duplicate_valid_position_cannot_be_counted_twice(self):
        first = frozen_campaign_sequence()[0]
        with self.assertRaisesRegex(ValueError, "next frozen trial"):
            validate_attempt_history(
                [
                    _attempt(first, "first-valid", "VALID"),
                    _attempt(first, "duplicate-valid", "VALID"),
                ]
            )

    def test_attempt_status_is_fail_closed(self):
        first = frozen_campaign_sequence()[0]
        for status in ("PASS", "FAIL", "UNKNOWN", ""):
            with self.subTest(status=status):
                with self.assertRaisesRegex(ValueError, "attempt_status"):
                    validate_attempt_history([_attempt(first, "bad-status", status)])

    def test_execution_descriptor_requires_attempt_history_and_exact_next_position(self):
        sequence = frozen_campaign_sequence()
        first = sequence[0]
        history = [_attempt(first, "first-invalid", "INVALID")]
        plan = build_trial_plan(
            campaign_seed=first["campaign_seed"],
            cell_id=first["cell_id"],
            run_id="first-retry-new-run-id",
            repo_commit=REPO_SHA,
        )
        descriptor = build_execution_descriptor(
            plan=plan,
            authorization=_granted(plan),
            attempt_history=history,
            current_repo_sha=REPO_SHA,
        )
        self.assertEqual(descriptor["global_order_index"], 1)
        self.assertEqual(descriptor["prior_attempt_count"], 1)
        self.assertEqual(descriptor["prior_valid_position_count"], 0)
        self.assertTrue(descriptor["attempt_history_validated"])
        self.assertEqual(descriptor["run_id"], "first-retry-new-run-id")

        reused = copy.deepcopy(plan)
        reused["run_id"] = "first-invalid"
        with self.assertRaisesRegex(ValueError, "run_id"):
            build_execution_descriptor(
                plan=reused,
                authorization=_granted(reused),
                attempt_history=history,
                current_repo_sha=REPO_SHA,
            )


if __name__ == "__main__":
    unittest.main()
