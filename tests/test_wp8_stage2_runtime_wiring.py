from __future__ import annotations

import json
import unittest
from pathlib import Path

from src.mission_recovery.wp8_stage2_runtime_wiring import (
    _select_policy,
    command_plan,
)

ROOT = Path(__file__).resolve().parents[1]
PILOT = json.loads(
    (ROOT / "configs" / "wp8_pilot_design.json").read_text(
        encoding="utf-8"
    )
)
COMMAND_RUNNER = (
    ROOT / "scripts" / "run_wp8_command_stage1_development.sh"
).read_text(encoding="utf-8")
RECOVERY_RUNNER = (
    ROOT / "scripts" / "run_wp8_recovery_binding_preflight.sh"
).read_text(encoding="utf-8")
OBSERVABILITY_RUNNER = (
    ROOT / "scripts" / "run_wp8_observability_stage1_development.sh"
).read_text(encoding="utf-8")
CONTROLLER = (
    ROOT / "scripts" / "run_wp8_stage2_pilot.sh"
).read_text(encoding="utf-8")


class WP8Stage2RuntimeWiringTests(unittest.TestCase):
    def test_command_plan_uses_stage2_seed_and_frozen_factors(self) -> None:
        run_id = (
            "20260821T000000.000000Z-wp8-stage2-c03-s202-"
            + "d" * 32
        )
        plan = command_plan(
            PILOT,
            cell_id="C03",
            seed=202,
            run_id=run_id,
        )
        factor = plan["factor_context"]
        event = plan["event_instance"]
        self.assertEqual(factor["seed"], 202)
        self.assertEqual(event["seed"], 202)
        self.assertEqual(factor["policy_id"], "P7")
        self.assertEqual(factor["mission_state_id"], "M0")
        self.assertFalse(plan["development_preflight"])
        self.assertTrue(plan["pilot_data"])

        decision = _select_policy(
            PILOT,
            cell_id="C03",
            event=event,
        )
        self.assertEqual(decision["delegated_policy_id"], "P1")
        self.assertFalse(decision["oracle_ground_truth_read"])

    def test_non_anchor_command_cell_is_rejected(self) -> None:
        run_id = (
            "20260821T000000.000000Z-wp8-stage2-c01-s202-"
            + "e" * 32
        )
        with self.assertRaises(ValueError):
            command_plan(
                PILOT,
                cell_id="C01",
                seed=202,
                run_id=run_id,
            )

    def test_three_family_runners_have_explicit_stage2_mode(self) -> None:
        for source in (
            COMMAND_RUNNER,
            RECOVERY_RUNNER,
            OBSERVABILITY_RUNNER,
        ):
            self.assertIn("WP8_STAGE2_PILOT", source)
            self.assertIn("WP8_STAGE2_CONTROLLER", source)
            self.assertIn("WP8_PILOT_SEED", source)
            self.assertIn(
                "src.mission_recovery.wp8_stage2_runtime_wiring",
                source,
            )
            self.assertIn('PILOT_STAGE="stage2"', source)
            self.assertIn(
                'EVIDENCE="$ROOT/results/wp8/pilot/$PILOT_STAGE/$RUN_ID"',
                source,
            )
            self.assertIn("stage2-acceptance.json", source)

    def test_stage1_mode_is_preserved(self) -> None:
        for source in (
            COMMAND_RUNNER,
            RECOVERY_RUNNER,
            OBSERVABILITY_RUNNER,
        ):
            self.assertIn("WP8_STAGE1_PILOT", source)
            self.assertIn("WP8_STAGE1_CONTROLLER", source)
            self.assertIn(
                "src.mission_recovery.wp8_stage1_runtime_wiring",
                source,
            )

    def test_controller_is_one_repetition_and_ci_guarded(self) -> None:
        self.assertIn("WP8_STAGE2_VALIDATED_COMMIT", CONTROLLER)
        self.assertIn("WP8_STAGE2_VALIDATED_CI_RUN_ID", CONTROLLER)
        self.assertIn("WP8_CONFIRM_STAGE2_NEXT", CONTROLLER)
        self.assertIn("WP8_STAGE2_REVIEWED_INVALID_RUN_IDS", CONTROLLER)
        self.assertIn("automatic_next_repetition_invoked=false", CONTROLLER)
        self.assertIn("DO_NOT_RERUN_WITHOUT_REVIEW=true", CONTROLLER)
        self.assertEqual(CONTROLLER.count('"${COMMAND[@]}"'), 1)
        self.assertNotIn("for seed in 202 303 404 505", CONTROLLER)
        self.assertNotIn("while true", CONTROLLER)


if __name__ == "__main__":
    unittest.main()
