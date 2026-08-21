from __future__ import annotations

import json
import unittest
from datetime import datetime, timezone
from pathlib import Path

from src.mission_recovery.wp8_stage2_pilot import (
    allocate_stage2_run_id,
    new_stage2_ledger,
    record_stage2_attempt,
    stage2_execution_plan,
    stage2_order_for_seed,
    stage2_progress,
    validate_stage2_run_id,
)

ROOT = Path(__file__).resolve().parents[1]
PILOT = json.loads(
    (ROOT / "configs" / "wp8_pilot_design.json").read_text(
        encoding="utf-8"
    )
)


def complete_stage1_ledger() -> dict:
    attempts = []
    for index, cell_id in enumerate(
        PILOT["stage_1_control_validity"]["cell_ids"],
        start=1,
    ):
        attempts.append(
            {
                "attempt_index": index,
                "cell_id": cell_id,
                "seed": 101,
                "run_id": f"synthetic-stage1-{cell_id.lower()}",
                "status": "VALID",
                "retained_evidence_ref": f"synthetic/{cell_id}",
                "schema_valid": True,
                "raw_metric_inputs_complete": True,
                "expected_policy_semantics_met": True,
            }
        )
    return {
        "schema": 1,
        "decision_id": "R-028",
        "stage": "stage_1_control_validity",
        "seed": 101,
        "attempts": attempts,
    }


class WP8Stage2PilotTests(unittest.TestCase):
    def test_frozen_seed_block_orders(self) -> None:
        expected = {
            202: ["R02", "C06", "C03", "C02", "C05", "O01", "R03"],
            303: ["R02", "C03", "C02", "C05", "R03", "C06", "O01"],
            404: ["C02", "R02", "C03", "C06", "R03", "O01", "C05"],
            505: ["C06", "O01", "R03", "C05", "C02", "R02", "C03"],
        }
        for seed, order in expected.items():
            self.assertEqual(stage2_order_for_seed(PILOT, seed), order)

    def test_execution_plan_is_28_and_seed_blocked(self) -> None:
        plan = stage2_execution_plan(PILOT)
        self.assertEqual(len(plan), 28)
        self.assertEqual([row["seed"] for row in plan[:7]], [202] * 7)
        self.assertEqual([row["seed"] for row in plan[7:14]], [303] * 7)
        self.assertEqual([row["seed"] for row in plan[14:21]], [404] * 7)
        self.assertEqual([row["seed"] for row in plan[21:]], [505] * 7)
        self.assertNotIn(
            "recovery_generic",
            {row["runtime_path"] for row in plan},
        )

    def test_empty_stage2_starts_at_r02_seed202(self) -> None:
        ledger = new_stage2_ledger(PILOT)
        progress = stage2_progress(
            PILOT,
            complete_stage1_ledger(),
            ledger,
        )
        self.assertFalse(progress["progression_blocked_for_review"])
        self.assertEqual(progress["valid_repetition_count"], 0)
        self.assertEqual(progress["remaining_valid_repetitions"], 28)
        self.assertEqual(
            progress["next_repetition"]["cell_id"],
            "R02",
        )
        self.assertEqual(progress["next_repetition"]["seed"], 202)

    def test_valid_attempt_advances_exactly_one_repetition(self) -> None:
        ledger = new_stage2_ledger(PILOT)
        run_id = allocate_stage2_run_id(
            cell_id="R02",
            seed=202,
            now=datetime(2026, 8, 21, tzinfo=timezone.utc),
            token_factory=lambda: "a" * 32,
        )
        record_stage2_attempt(
            pilot=PILOT,
            ledger=ledger,
            cell_id="R02",
            seed=202,
            run_id=run_id,
            status="VALID",
            retained_evidence_ref="synthetic/r02",
            schema_valid=True,
            raw_metric_inputs_complete=True,
            expected_policy_semantics_met=True,
        )
        progress = stage2_progress(
            PILOT,
            complete_stage1_ledger(),
            ledger,
        )
        self.assertEqual(progress["valid_repetition_count"], 1)
        self.assertEqual(progress["remaining_valid_repetitions"], 27)
        self.assertEqual(progress["next_repetition"]["cell_id"], "C06")
        self.assertEqual(progress["next_repetition"]["seed"], 202)

    def test_any_invalid_attempt_blocks_automatic_progression(self) -> None:
        ledger = new_stage2_ledger(PILOT)
        run_id = allocate_stage2_run_id(
            cell_id="R02",
            seed=202,
            now=datetime(2026, 8, 21, tzinfo=timezone.utc),
            token_factory=lambda: "b" * 32,
        )
        record_stage2_attempt(
            pilot=PILOT,
            ledger=ledger,
            cell_id="R02",
            seed=202,
            run_id=run_id,
            status="RUN_INVALID",
            retained_evidence_ref="synthetic/r02-invalid",
            invalid_class="infrastructure",
            invalid_cause="nominal_runtime",
        )
        progress = stage2_progress(
            PILOT,
            complete_stage1_ledger(),
            ledger,
        )
        self.assertTrue(progress["progression_blocked_for_review"])
        self.assertIsNone(progress["next_repetition"])
        self.assertFalse(progress["stage_2_complete"])

    def test_reviewed_invalid_allows_deliberate_replacement_only(self) -> None:
        ledger = new_stage2_ledger(PILOT)
        run_id = allocate_stage2_run_id(
            cell_id="R02",
            seed=202,
            now=datetime(2026, 8, 21, tzinfo=timezone.utc),
            token_factory=lambda: "f" * 32,
        )
        record_stage2_attempt(
            pilot=PILOT,
            ledger=ledger,
            cell_id="R02",
            seed=202,
            run_id=run_id,
            status="RUN_INVALID",
            retained_evidence_ref="synthetic/r02-invalid-reviewed",
            invalid_class="non_infrastructure",
            invalid_cause="post_recovery_verification",
        )
        blocked = stage2_progress(
            PILOT,
            complete_stage1_ledger(),
            ledger,
        )
        self.assertTrue(blocked["progression_blocked_for_review"])

        reviewed = stage2_progress(
            PILOT,
            complete_stage1_ledger(),
            ledger,
            reviewed_invalid_run_ids={run_id},
        )
        self.assertFalse(reviewed["progression_blocked_for_review"])
        self.assertEqual(
            reviewed["next_repetition"]["cell_id"],
            "R02",
        )
        self.assertEqual(reviewed["next_repetition"]["seed"], 202)
        self.assertEqual(reviewed["reviewed_invalid_attempt_count"], 1)
        self.assertEqual(reviewed["unreviewed_invalid_attempt_count"], 0)

    def test_stage2_run_id_binds_cell_and_seed(self) -> None:
        run_id = allocate_stage2_run_id(
            cell_id="C03",
            seed=303,
            now=datetime(2026, 8, 21, tzinfo=timezone.utc),
            token_factory=lambda: "c" * 32,
        )
        self.assertEqual(
            run_id,
            "20260821T000000.000000Z-wp8-stage2-c03-s303-"
            + "c" * 32,
        )
        validate_stage2_run_id(
            pilot=PILOT,
            cell_id="C03",
            seed=303,
            run_id=run_id,
        )
        with self.assertRaises(ValueError):
            validate_stage2_run_id(
                pilot=PILOT,
                cell_id="C03",
                seed=404,
                run_id=run_id,
            )


if __name__ == "__main__":
    unittest.main()
