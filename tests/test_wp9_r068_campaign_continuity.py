from __future__ import annotations

import unittest

from src.mission_recovery.wp9_r068_campaign_continuity import (
    validate_campaign_continuity,
)


POSITION1_RUN = (
    "20260824T145723Z-wp9-r066-p0001-s10001-a19-"
    "69fe370fe1d249e68ebf05671a630b9d"
)
POSITION1_SHA = "aae2239753119c92e7633db3b6c73aee94c7b6dd"
CURRENT_SHA = "05dcb05bf73d6d2a52c0baf55c3e919d4278b7fe"


def _history() -> list[dict]:
    return [
        {
            "campaign_seed": 10001,
            "cell_order_index": 1,
            "cell_id": "A19",
            "run_id": POSITION1_RUN,
            "attempt_status": "VALID",
        }
    ]


def _result() -> dict:
    return {
        "attempt_status": "VALID",
        "run_id": POSITION1_RUN,
        "campaign_seed": 10001,
        "cell_id": "A19",
        "classification": "WP9_R066_FINAL_CAMPAIGN_VALID_TRIAL_RESULT",
        "runtime_execution_performed": True,
        "campaign_seed_consumed": True,
        "campaign_data_generated": True,
        "source_harness_invocation_count": 1,
        "automatic_retry_performed": False,
        "automatic_next_case_performed": False,
        "treatment_fidelity_valid": True,
        "raw_metric_inputs_complete": True,
        "run_record": {
            "environment": {
                "snapshot_id": f"repo-{POSITION1_SHA}",
            }
        },
    }


class WP9R068CampaignContinuityTests(unittest.TestCase):
    def test_historical_valid_trial_may_precede_current_baseline(self) -> None:
        calls: list[tuple[str, str]] = []

        def is_ancestor(old: str, new: str) -> bool:
            calls.append((old, new))
            return old == POSITION1_SHA and new == CURRENT_SHA

        result = validate_campaign_continuity(
            attempt_history=_history(),
            retained_results={POSITION1_RUN: _result()},
            current_repo_sha=CURRENT_SHA,
            is_ancestor=is_ancestor,
        )

        self.assertEqual(calls, [(POSITION1_SHA, CURRENT_SHA)])
        self.assertEqual(result["valid_position_count"], 1)
        self.assertEqual(result["historical_baseline_count"], 1)
        self.assertEqual(result["next_required_global_order_index"], 2)
        self.assertEqual(result["next_required_campaign_seed"], 10001)
        self.assertEqual(result["next_required_cell_order_index"], 2)
        self.assertEqual(result["next_required_cell_id"], "A13")
        self.assertTrue(result["baseline_transition_valid"])
        self.assertFalse(result["runtime_execution_performed"])
        self.assertFalse(result["campaign_seed_consumed"])
        self.assertFalse(result["campaign_data_generated"])

    def test_historical_baseline_need_not_equal_current_baseline(self) -> None:
        self.assertNotEqual(POSITION1_SHA, CURRENT_SHA)

        result = validate_campaign_continuity(
            attempt_history=_history(),
            retained_results={POSITION1_RUN: _result()},
            current_repo_sha=CURRENT_SHA,
            is_ancestor=lambda old, new: old == POSITION1_SHA and new == CURRENT_SHA,
        )

        self.assertTrue(result["baseline_transition_valid"])
        self.assertEqual(result["retained_execution_repo_shas"], [POSITION1_SHA])

    def test_non_ancestor_retained_baseline_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "ancestor"):
            validate_campaign_continuity(
                attempt_history=_history(),
                retained_results={POSITION1_RUN: _result()},
                current_repo_sha=CURRENT_SHA,
                is_ancestor=lambda _old, _new: False,
            )

    def test_retained_result_identity_must_match_ledger(self) -> None:
        result = _result()
        result["cell_id"] = "A20"

        with self.assertRaisesRegex(ValueError, "identity"):
            validate_campaign_continuity(
                attempt_history=_history(),
                retained_results={POSITION1_RUN: result},
                current_repo_sha=CURRENT_SHA,
                is_ancestor=lambda _old, _new: True,
            )

    def test_valid_result_requires_complete_campaign_science_flags(self) -> None:
        result = _result()
        result["campaign_seed_consumed"] = False

        with self.assertRaisesRegex(ValueError, "VALID retained result"):
            validate_campaign_continuity(
                attempt_history=_history(),
                retained_results={POSITION1_RUN: result},
                current_repo_sha=CURRENT_SHA,
                is_ancestor=lambda _old, _new: True,
            )


if __name__ == "__main__":
    unittest.main()
