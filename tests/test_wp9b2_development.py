import json
import subprocess
import unittest
from pathlib import Path

from src.mission_recovery.wp9b2_development import (
    build_case_plan,
    case_registry,
    finalize_e2_observation,
    validate_development_cases,
)

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts" / "run_wp9b2_e2_development.sh"


class WP9B2DevelopmentTests(unittest.TestCase):
    def test_bounded_case_registry_is_exact_and_development_only(self):
        validate_development_cases()
        rows = case_registry()
        self.assertEqual(sorted(rows), [f"D{i:02d}" for i in range(1, 11)])
        self.assertEqual(
            [rows[f"D{i:02d}"]["development_seed"] for i in range(1, 11)],
            list(range(9601, 9611)),
        )
        self.assertEqual(
            {case_id for case_id, row in rows.items() if row["executor_ready"]},
            {"D03", "D04", "D05"},
        )

    def test_e2_case_plans_match_frozen_cells_and_delegates(self):
        expected = {
            "D03": ("A19", "P0", "P0", "OBSERVE_ONLY", 1),
            "D04": ("A20", "P1", "P1", "ISOLATE_MODELED_SOURCE", 0),
            "D05": ("A21", "P7", "P1", "ISOLATE_MODELED_SOURCE", 0),
        }
        for case_id, values in expected.items():
            with self.subTest(case_id=case_id):
                plan = build_case_plan(
                    case_id=case_id,
                    run_id=f"wp9b2-{case_id.lower()}-test",
                    repo_commit="1234567890abcdef",
                )
                cell, requested, effective, action, delta = values
                self.assertEqual(plan["campaign_cell_id"], cell)
                self.assertEqual(plan["factor_context"]["policy_id"], requested)
                self.assertEqual(
                    plan["runtime_policy_decision"]["delegated_policy_id"], effective
                )
                self.assertEqual(plan["runtime_policy_decision"]["selected_action"], action)
                self.assertEqual(
                    plan["e2_replay_effect_contract"]["m01_effect_observation"]
                    ["expected_delta_for_acceptance_only"],
                    delta,
                )
                self.assertFalse(plan["campaign_seed_consumed"])
                self.assertFalse(plan["campaign_data"])
                self.assertFalse(plan["automatic_next_case"])

    def test_nonready_family_cannot_build_runtime_plan(self):
        with self.assertRaises(PermissionError):
            build_case_plan(
                case_id="D01",
                run_id="wp9b2-d01-test",
                repo_commit="1234567890abcdef",
            )

    @staticmethod
    def _observations(plan, expected_delta):
        packet = plan["e2_replay_effect_contract"]["setup"]["packet_sha256"]
        packet_hex = plan["e2_replay_effect_contract"]["replay"]["packet_hex"]
        setup = {
            "role": "previously_accepted_authorized_command_before_treatment",
            "packet_sha256": packet,
            "packet_hex": packet_hex,
        }
        intervening = {"command_class": "sample_noop"}
        replay = {
            "role": "byte_identical_stale_replay_after_treatment",
            "packet_sha256": packet,
            "packet_hex": packet_hex,
        }
        decision = {
            "source_id": "modeled_attacker",
            "command_class": "sample_reset_counters",
            "packet_sha256": packet,
            "action": plan["runtime_policy_decision"]["selected_action"],
            "forwarded": bool(expected_delta),
        }
        return setup, intervening, replay, [decision]

    def test_e2_finalizer_accepts_observed_effect_for_each_ready_case(self):
        expected = {"D03": 1, "D04": 0, "D05": 0}
        for case_id, delta in expected.items():
            with self.subTest(case_id=case_id):
                plan = build_case_plan(
                    case_id=case_id,
                    run_id=f"wp9b2-{case_id.lower()}-finalize",
                    repo_commit="1234567890abcdef",
                )
                setup, intervening, replay, decisions = self._observations(plan, delta)
                summary = finalize_e2_observation(
                    plan=plan,
                    setup=setup,
                    intervening=intervening,
                    replay=replay,
                    gateway_decisions=decisions,
                    reset_before_setup=10,
                    reset_after_setup=11,
                    reset_before_replay=11,
                    reset_after_replay=11 + delta,
                    noop_before=20,
                    noop_after=21,
                )
                self.assertEqual(summary["post_replay_reset_marker_delta"], delta)
                self.assertEqual(summary["unauthorized_effect_completed_observed"], delta == 1)
                self.assertFalse(summary["packet_send_success_used_as_m01"])
                self.assertFalse(summary["noop_receipt_used_as_m01"])
                self.assertFalse(summary["campaign_seed_consumed"])
                self.assertFalse(summary["campaign_data"])

    def test_e2_finalizer_rejects_wrong_observed_effect(self):
        plan = build_case_plan(
            case_id="D04",
            run_id="wp9b2-d04-wrong-effect",
            repo_commit="1234567890abcdef",
        )
        setup, intervening, replay, decisions = self._observations(plan, 0)
        with self.assertRaises(ValueError):
            finalize_e2_observation(
                plan=plan,
                setup=setup,
                intervening=intervening,
                replay=replay,
                gateway_decisions=decisions,
                reset_before_setup=1,
                reset_after_setup=2,
                reset_before_replay=2,
                reset_after_replay=3,
                noop_before=1,
                noop_after=2,
            )

    def test_e2_finalizer_rejects_nonidentical_replay(self):
        plan = build_case_plan(
            case_id="D03",
            run_id="wp9b2-d03-nonidentical",
            repo_commit="1234567890abcdef",
        )
        setup, intervening, replay, decisions = self._observations(plan, 1)
        replay["packet_hex"] = "00"
        with self.assertRaises(ValueError):
            finalize_e2_observation(
                plan=plan,
                setup=setup,
                intervening=intervening,
                replay=replay,
                gateway_decisions=decisions,
                reset_before_setup=1,
                reset_after_setup=2,
                reset_before_replay=2,
                reset_after_replay=3,
                noop_before=1,
                noop_after=2,
            )

    def test_runner_is_bash_syntax_valid_and_one_case_only(self):
        completed = subprocess.run(
            ["/bin/bash", "-n", str(RUNNER)],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        text = RUNNER.read_text(encoding="utf-8")
        self.assertIn('OBSERVATION_WINDOW_SECONDS=3', text)
        self.assertIn('case "$CASE_ID" in', text)
        self.assertIn('D03|D04|D05)', text)
        self.assertIn('automatic_next_case=false', text)
        self.assertNotIn('D03 D04 D05', text)
        self.assertNotIn('for CASE_ID', text)

    def test_runner_measurement_window_is_fixed_before_acceptance(self):
        text = RUNNER.read_text(encoding="utf-8")
        sleep_pos = text.index('sleep "$OBSERVATION_WINDOW_SECONDS"')
        finalize_pos = text.index('finalize-e2')
        self.assertLess(sleep_pos, finalize_pos)
        self.assertIn('RESET_AFTER_REPLAY="$(count_reset_marker)"', text)
        self.assertNotIn('expected_delta', text)


if __name__ == "__main__":
    unittest.main()
