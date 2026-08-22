import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from src.mission_recovery.wp9b2_e4_fixed_development import (
    build_plan,
    finalize,
    observe_policy,
    validate_gate,
)

ROOT = Path(__file__).resolve().parents[1]
GATE = json.loads((ROOT / "configs/wp9b2_e4_fixed_runtime_gate.json").read_text(encoding="utf-8"))
CASES = json.loads((ROOT / "configs/wp9b2_development_cases.json").read_text(encoding="utf-8"))
RUNNER = ROOT / "scripts/run_wp9b2_e4_fixed_development.sh"


class WP9B2E4FixedDevelopmentTests(unittest.TestCase):
    def _plan_policy(self, case_id):
        plan, event = build_plan(case_id=case_id, run_id="unit-run", repo_commit="unit-commit")
        return plan, event, observe_policy(plan=plan, event=event)

    def _finalize(self, case_id, gateway=None, **overrides):
        plan, _, policy = self._plan_policy(case_id)
        kwargs = {
            "plan": plan,
            "policy": policy,
            "event_truth_before": 0,
            "event_truth_after": 1,
            "event_visible_before": 0,
            "event_visible_after": 0,
            "post_truth_before": 1,
            "post_truth_after": 2,
            "post_visible_before": 0,
            "post_visible_after": 0,
            "gateway_decisions_path": gateway,
            "noop_before": 4,
            "noop_after": 4,
        }
        kwargs.update(overrides)
        return finalize(**kwargs)

    def test_r049_gate_is_development_only_and_preserves_r046_identity(self):
        validate_gate()
        self.assertEqual(GATE["decision_id"], "R-049")
        boundary = GATE["scientific_boundary"]
        self.assertTrue(boundary["development_only"])
        self.assertTrue(boundary["single_case_per_invocation"])
        self.assertFalse(boundary["campaign_seed_consumed"])
        self.assertFalse(boundary["campaign_data"])
        self.assertFalse(boundary["final_campaign_execution_authorized"])
        self.assertEqual(CASES["decision_id"], "R-046")

    def test_d09_d10_plans_match_frozen_campaign_cells_and_seeds(self):
        d09, _, _ = self._plan_policy("D09")
        d10, _, _ = self._plan_policy("D10")
        self.assertEqual(
            (d09["campaign_cell_id"], d09["development_seed"], d09["requested_policy_id"]),
            ("A22", 9609, "P0"),
        )
        self.assertEqual(
            (d10["campaign_cell_id"], d10["development_seed"], d10["requested_policy_id"]),
            ("A23", 9610, "P4"),
        )

    def test_both_cases_preserve_degraded_policy_visible_evidence_and_truth_separation(self):
        for case_id in ("D09", "D10"):
            _, event, policy = self._plan_policy(case_id)
            self.assertTrue(event["ground_truth"]["telemetry_truth_available"])
            self.assertEqual(
                event["policy_visible_evidence"],
                {
                    "telemetry_stream_present": True,
                    "high_value_channels_complete": False,
                    "evidence_fresh": False,
                    "state_estimate_complete": False,
                },
            )
            self.assertFalse(policy["oracle_ground_truth_read"])

    def test_d09_is_fixed_p0_observe_only_without_command_gate(self):
        plan, _, policy = self._plan_policy("D09")
        self.assertEqual(policy["requested_policy_id"], "P0")
        self.assertEqual(policy["delegated_policy_id"], "P0")
        self.assertEqual(policy["selected_action"], "OBSERVE_ONLY")
        result = self._finalize("D09")
        self.assertFalse(result["modeled_conservative_command_gate_observed"])
        self.assertFalse(result["containment_observed"])

    def test_d10_is_fixed_p4_modeled_command_gate_not_native_safe_mode(self):
        plan, _, policy = self._plan_policy("D10")
        self.assertEqual(policy["requested_policy_id"], "P4")
        self.assertEqual(policy["delegated_policy_id"], "P4")
        self.assertEqual(policy["selected_action"], "ENTER_SAFE_MODE")
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "gateway.jsonl"
            path.write_text(
                json.dumps({
                    "action": "ENTER_SAFE_MODE",
                    "source_id": "authorized_ground",
                    "command_class": "sample_noop",
                    "forwarded": False,
                }) + "\n",
                encoding="utf-8",
            )
            result = self._finalize("D10", gateway=path)
        self.assertTrue(result["modeled_conservative_command_gate_observed"])
        self.assertEqual(result["legitimate_commands_attempted"], 1)
        self.assertEqual(result["legitimate_commands_rejected"], 1)
        self.assertFalse(result["p4_native_safe_mode_claim"])

    def test_finalizer_requires_truth_visible_split_for_event_and_post_probe(self):
        with self.assertRaisesRegex(ValueError, "event-success"):
            self._finalize("D09", event_visible_after=1)
        with self.assertRaisesRegex(ValueError, "post-response"):
            self._finalize("D09", post_truth_after=1)

    def test_d10_finalizer_rejects_forwarded_authorized_noop(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "gateway.jsonl"
            path.write_text(
                json.dumps({
                    "action": "ENTER_SAFE_MODE",
                    "source_id": "authorized_ground",
                    "command_class": "sample_noop",
                    "forwarded": True,
                }) + "\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "forwarded"):
                self._finalize("D10", gateway=path)

    def test_d10_finalizer_rejects_cfs_noop_marker_increase(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "gateway.jsonl"
            path.write_text(
                json.dumps({
                    "action": "ENTER_SAFE_MODE",
                    "source_id": "authorized_ground",
                    "command_class": "sample_noop",
                    "forwarded": False,
                }) + "\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "unexpectedly reached cFS"):
                self._finalize("D10", gateway=path, noop_after=5)

    def test_runner_is_bash3_compatible_single_case_and_fail_closed(self):
        subprocess.run(["/bin/bash", "-n", str(RUNNER)], check=True)
        text = RUNNER.read_text(encoding="utf-8")
        self.assertIn('D09|D10)', text)
        self.assertIn('EXPECTED_CONFIRM="EXECUTE-$CASE_ID"', text)
        self.assertIn('WP9B2_CONFIRM', text)
        self.assertNotIn('${CASE_ID,,}', text)
        for token in ("mapfile", "readarray", "declare -A"):
            self.assertNotIn(token, text)
        self.assertIn('automatic_next_case=false', text)

    def test_runner_observes_fixed_deadline_and_cleans_before_residue_check(self):
        text = RUNNER.read_text(encoding="utf-8")
        event_wait = text.index('wait_until_ns "$EVENT_DEADLINE_NS"')
        post_wait = text.index('wait_until_ns "$POST_DEADLINE_NS"')
        acceptance = text.index('PHASE="ACCEPTANCE"')
        cleanup = text.index('PHASE="AUXILIARY_CLEANUP"')
        residue = text.index('PHASE="RESIDUE_CHECK"')
        self.assertLess(event_wait, acceptance)
        self.assertLess(post_wait, acceptance)
        self.assertLess(cleanup, residue)
        self.assertIn('p4_native_safe_mode_claim=false', text)
        self.assertIn('p4_telemetry_restoration_claim=false', text)


if __name__ == "__main__":
    unittest.main()
