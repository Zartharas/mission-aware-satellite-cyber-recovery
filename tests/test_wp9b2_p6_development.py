import json
import subprocess
import unittest
from pathlib import Path

from src.mission_recovery.wp9b2_p6_development import (
    build_p5_handoff,
    build_p6_plan,
    finalize_p6_runtime,
    observe_p6_policy,
    validate_p6_gate,
)

ROOT = Path(__file__).resolve().parents[1]
GATE = ROOT / "configs" / "wp9b2_p6_runtime_gate.json"
R046 = ROOT / "configs" / "wp9b2_development_cases.json"
RUNNER = ROOT / "scripts" / "run_wp9b2_p6_development.sh"


class WP9B2P6DevelopmentTests(unittest.TestCase):
    def test_r047_gate_is_development_only_and_preserves_r046_history(self):
        validate_p6_gate()
        gate = json.loads(GATE.read_text(encoding="utf-8"))
        r046 = json.loads(R046.read_text(encoding="utf-8"))
        rows = {row["case_id"]: row for row in r046["cases"]}

        self.assertEqual(gate["decision_id"], "R-047")
        self.assertEqual(gate["case_ids"], ["D01", "D02"])
        self.assertEqual(gate["development_seeds"], [9601, 9602])
        self.assertFalse(rows["D01"]["executor_ready"])
        self.assertFalse(rows["D02"]["executor_ready"])
        self.assertTrue(gate["scientific_boundary"]["development_only"])
        self.assertFalse(
            gate["scientific_boundary"]["final_campaign_seed_consumption"]
        )
        self.assertFalse(
            gate["scientific_boundary"]["final_campaign_data_generation"]
        )
        self.assertFalse(
            gate["scientific_boundary"]["final_campaign_execution_authorized"]
        )

    def test_development_contact_window_cannot_become_campaign_parameter(self):
        gate = json.loads(GATE.read_text(encoding="utf-8"))
        timing = gate["development_contact_window"]
        self.assertEqual(timing["seconds"], 2)
        self.assertFalse(timing["final_campaign_parameter"])
        self.assertFalse(timing["final_campaign_duration_frozen"])
        self.assertTrue(timing["wp9b3_campaign_duration_freeze_required"])

    def test_d01_d02_plans_match_frozen_p6_cells(self):
        expected = {
            "D01": ("A16", 9601, "C0", True, 0),
            "D02": ("A17", 9602, "C1", False, 1),
        }
        for case_id, values in expected.items():
            with self.subTest(case_id=case_id):
                plan = build_p6_plan(
                    case_id=case_id,
                    run_id=f"wp9b2-{case_id.lower()}-test",
                    repo_commit="1234567890abcdef",
                )
                cell, seed, contact, available, missed = values
                self.assertEqual(plan["campaign_cell_id"], cell)
                self.assertEqual(plan["factor_context"]["seed"], seed)
                self.assertEqual(
                    plan["factor_context"]["contact_condition_id"], contact
                )
                self.assertEqual(plan["factor_context"]["policy_id"], "P6")
                self.assertEqual(
                    plan["pre_authorization_policy_decision"][
                        "selected_action"
                    ],
                    "WAIT_FOR_GROUND_AUTHORIZATION",
                )
                auth = plan["p6_handoff_contract"]["authorization_contract"]
                self.assertEqual(
                    auth["available_at_response_boundary"], available
                )
                self.assertEqual(
                    auth["missed_contact_windows_before_authorization"], missed
                )
                self.assertFalse(plan["campaign_seed_consumed"])
                self.assertFalse(plan["campaign_data"])
                self.assertFalse(plan["trusted_recovery_claim"])
                self.assertFalse(plan["automatic_next_case"])

    @staticmethod
    def _authorization(case_id, boundary_ns, observed_ns):
        d01 = case_id == "D01"
        return {
            "schema": 1,
            "case_id": case_id,
            "source": "synthetic_ground_authorization_schedule",
            "contact_condition_id": "C0" if d01 else "C1",
            "response_boundary_monotonic_ns": boundary_ns,
            "authorization_observed_monotonic_ns": observed_ns,
            "available_at_response_boundary": d01,
            "missed_contact_windows": 0 if d01 else 1,
            "pre_release_probe_performed": not d01,
            "pre_release_authorization_current": False,
            "release_after_modeled_window_count": 0 if d01 else 1,
            "authorization_current": True,
            "rollback_request_exists_before_authorization": False,
            "development_contact_window_seconds": 2,
            "development_contact_window_final_campaign_parameter": False,
            "real_human_operator_used": False,
            "real_world_ground_contact_used": False,
        }

    def test_p6_finalizer_accepts_c0_and_c1_handoff_ordering(self):
        for case_id in ("D01", "D02"):
            with self.subTest(case_id=case_id):
                plan = build_p6_plan(
                    case_id=case_id,
                    run_id=f"wp9b2-{case_id.lower()}-finalize",
                    repo_commit="1234567890abcdef",
                )
                activation_ns = 1_000_000_000
                policy_ns = 1_100_000_000
                boundary_ns = 1_200_000_000
                observed_ns = (
                    1_250_000_000
                    if case_id == "D01"
                    else boundary_ns + 2_000_000_000
                )
                authorization = self._authorization(
                    case_id, boundary_ns, observed_ns
                )
                policy = observe_p6_policy(
                    plan=plan, observed_monotonic_ns=policy_ns
                )
                handoff = build_p5_handoff(
                    plan=plan,
                    authorization=authorization,
                    handoff_monotonic_ns=observed_ns + 1,
                )
                summary = finalize_p6_runtime(
                    plan=plan,
                    event_observation={
                        "event_activation_observed": True,
                        "event_activation_monotonic_ns": activation_ns,
                        "observed_sha256": plan["artifact_evidence"][
                            "tampered_sha256"
                        ],
                    },
                    runtime_policy_observation=policy,
                    authorization=authorization,
                    handoff=handoff,
                    staged_approved_sha256=plan["artifact_evidence"][
                        "approved_sha256"
                    ],
                )
                self.assertEqual(summary["acceptance_status"], "PASS")
                self.assertTrue(summary["handoff_after_authorization_observed"])
                self.assertEqual(summary["post_authorization_delegate"], "P5")
                self.assertTrue(summary["rollback_request_validated"])
                self.assertFalse(summary["actual_recovery_execution_performed"])
                self.assertFalse(summary["trusted_recovery_claim"])
                self.assertFalse(summary["campaign_seed_consumed"])
                self.assertFalse(summary["campaign_data"])

    def test_d02_rejects_authorization_before_one_development_window(self):
        plan = build_p6_plan(
            case_id="D02",
            run_id="wp9b2-d02-early-authorization",
            repo_commit="1234567890abcdef",
        )
        authorization = self._authorization(
            "D02", 1_000_000_000, 2_999_999_999
        )
        with self.assertRaises(ValueError):
            build_p5_handoff(
                plan=plan,
                authorization=authorization,
                handoff_monotonic_ns=3_000_000_000,
            )

    def test_p6_rejects_handoff_before_observed_authorization(self):
        plan = build_p6_plan(
            case_id="D01",
            run_id="wp9b2-d01-early-handoff",
            repo_commit="1234567890abcdef",
        )
        authorization = self._authorization(
            "D01", 1_000_000_000, 1_100_000_000
        )
        with self.assertRaises(ValueError):
            build_p5_handoff(
                plan=plan,
                authorization=authorization,
                handoff_monotonic_ns=1_099_999_999,
            )

    def test_runner_is_bash_syntax_valid_single_case_and_bash3_compatible(self):
        completed = subprocess.run(
            ["/bin/bash", "-n", str(RUNNER)],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        text = RUNNER.read_text(encoding="utf-8")
        self.assertIn("DEVELOPMENT_CONTACT_WINDOW_SECONDS=2", text)
        self.assertIn('D01|D02)', text)
        self.assertIn('EXPECTED_CONFIRM="EXECUTE-$CASE_ID"', text)
        self.assertIn('tr \'[:upper:]\' \'[:lower:]\'', text)
        self.assertNotIn('${CASE_ID,,}', text)
        self.assertNotIn('mapfile', text)
        self.assertNotIn('readarray', text)
        self.assertNotIn('declare -A', text)
        self.assertNotIn('for CASE_ID', text)
        self.assertIn('automatic_next_case=false', text)

    def test_runner_stops_before_actual_recovery_and_trusted_recovery_claim(self):
        text = RUNNER.read_text(encoding="utf-8")
        self.assertIn('actual_recovery_execution_performed=false', text)
        self.assertIn('trusted_recovery_claim=false', text)
        self.assertIn('development_contact_window_final_campaign_parameter=false', text)
        self.assertIn('rollback request exists before D02 authorization release', text)


if __name__ == "__main__":
    unittest.main()
