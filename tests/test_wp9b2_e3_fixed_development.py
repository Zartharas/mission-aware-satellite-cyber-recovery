import subprocess
import unittest
from pathlib import Path

from src.mission_recovery.wp9b2_e3_fixed_development import (
    build_plan,
    build_runtime_rollback,
    finalize_p2,
    finalize_p5,
    observe_runtime_policy,
    validate_gate,
)

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts" / "run_wp9b2_e3_fixed_development.sh"


class WP9B2E3FixedDevelopmentTests(unittest.TestCase):
    def _plan(self, case_id):
        return build_plan(
            case_id=case_id,
            run_id=f"wp9b2-{case_id.lower()}-unit",
            repo_commit="1234567890abcdef",
        )

    def test_r048_gate_preserves_r046_and_campaign_identity(self):
        validate_gate()
        expected = {
            "D06": ("A10", 9606, "P2", "T0"),
            "D07": ("A12", 9607, "P2", "T1"),
            "D08": ("A15", 9608, "P5", "T1"),
        }
        for case_id, values in expected.items():
            plan = self._plan(case_id)
            cell, seed, policy, evidence = values
            self.assertEqual(plan["campaign_cell_id"], cell)
            self.assertEqual(plan["factor_context"]["seed"], seed)
            self.assertEqual(plan["factor_context"]["policy_id"], policy)
            self.assertEqual(plan["factor_context"]["evidence_condition_id"], evidence)
            self.assertFalse(plan["campaign_seed_consumed"])
            self.assertFalse(plan["campaign_data"])
            self.assertFalse(plan["automatic_next_case"])

    def test_d06_d07_runtime_policy_is_fixed_p2(self):
        for case_id in ("D06", "D07"):
            plan = self._plan(case_id)
            policy = observe_runtime_policy(plan)
            self.assertEqual(policy["delegated_policy_id"], "P2")
            self.assertEqual(policy["selected_action"], "RESTRICT_HIGH_RISK_COMMANDS")
            self.assertFalse(policy["oracle_ground_truth_read"])

    def test_d07_t1_omits_approved_version_at_policy_time_only(self):
        plan = self._plan("D07")
        event = plan["event_instance"]
        self.assertEqual(event["evidence_condition"], "T1")
        self.assertIn("approved_version", event["policy_evidence_omitted"])
        self.assertNotIn("approved_version", event["policy_visible_evidence"])
        self.assertFalse(plan["policy_time_visibility_used_as_classification_evidence"])

    @staticmethod
    def _p2_decisions():
        return [
            {
                "action": "RESTRICT_HIGH_RISK_COMMANDS",
                "source_id": "modeled_attacker",
                "command_class": "sample_reset_counters",
                "forwarded": False,
            },
            {
                "action": "RESTRICT_HIGH_RISK_COMMANDS",
                "source_id": "modeled_attacker",
                "command_class": "sample_reset_counters",
                "forwarded": False,
            },
            {
                "action": "RESTRICT_HIGH_RISK_COMMANDS",
                "source_id": "authorized_ground",
                "command_class": "sample_noop",
                "forwarded": True,
            },
        ]

    def test_p2_finalizer_accepts_d06_d07_without_calling_mitigation_containment(self):
        for case_id in ("D06", "D07"):
            plan = self._plan(case_id)
            policy = observe_runtime_policy(plan)
            tampered = plan["artifact_identities"]["tampered_sha256"]
            result = finalize_p2(
                plan=plan,
                runtime_policy=policy,
                gateway_decisions=self._p2_decisions(),
                event_slot_sha256=tampered,
                post_response_slot_sha256=tampered,
                reset_before=4,
                reset_after=4,
                noop_before=7,
                noop_after=8,
            )
            self.assertTrue(result["command_path_mitigation_observed"])
            self.assertFalse(result["command_path_mitigation_counts_as_update_containment"])
            self.assertFalse(result["update_containment_observed"])
            self.assertTrue(result["containment_right_censored_at_run_end"])
            self.assertFalse(result["trusted_recovery_observed"])
            self.assertTrue(result["trusted_recovery_right_censored_at_run_end"])

    def test_p2_finalizer_rejects_update_slot_mutation(self):
        plan = self._plan("D06")
        policy = observe_runtime_policy(plan)
        with self.assertRaisesRegex(ValueError, "must not mutate"):
            finalize_p2(
                plan=plan,
                runtime_policy=policy,
                gateway_decisions=self._p2_decisions(),
                event_slot_sha256=plan["artifact_identities"]["tampered_sha256"],
                post_response_slot_sha256=plan["artifact_identities"]["approved_sha256"],
                reset_before=1,
                reset_after=1,
                noop_before=1,
                noop_after=2,
            )

    def test_p2_finalizer_rejects_forwarded_attacker_probe(self):
        plan = self._plan("D06")
        policy = observe_runtime_policy(plan)
        rows = self._p2_decisions()
        rows[0]["forwarded"] = True
        with self.assertRaisesRegex(ValueError, "not both blocked"):
            finalize_p2(
                plan=plan,
                runtime_policy=policy,
                gateway_decisions=rows,
                event_slot_sha256=plan["artifact_identities"]["tampered_sha256"],
                post_response_slot_sha256=plan["artifact_identities"]["tampered_sha256"],
                reset_before=1,
                reset_after=1,
                noop_before=1,
                noop_after=2,
            )

    def test_d08_rollback_mechanism_is_valid_but_bounded_scope_is_not_trusted_recovery(self):
        plan = self._plan("D08")
        policy = observe_runtime_policy(plan)
        self.assertEqual(policy["delegated_policy_id"], "P5")
        self.assertEqual(policy["selected_action"], "REQUEST_VERIFIED_ROLLBACK")
        bundle = build_runtime_rollback(plan=plan, runtime_policy=policy)
        self.assertTrue(bundle["request_validation"]["accepted"])
        self.assertTrue(bundle["replacement_verification"]["accepted"])
        result = finalize_p5(
            plan=plan,
            runtime_policy=policy,
            rollback_bundle=bundle,
            event_slot_sha256=plan["artifact_identities"]["tampered_sha256"],
            post_response_slot_sha256=plan["artifact_identities"]["approved_sha256"],
            authorized_noop_delta=1,
        )
        self.assertTrue(result["modeled_rollback_execution_performed"])
        self.assertTrue(result["update_containment_observed"])
        self.assertFalse(result["complete_ten_criterion_manifest_emitted"])
        self.assertFalse(result["trusted_recovery_observed"])
        self.assertTrue(result["trusted_recovery_right_censored_at_run_end"])
        self.assertFalse(result["t1_causal_recovery_failure_claim"])

    def test_d08_does_not_treat_policy_time_t1_as_classification_evidence(self):
        plan = self._plan("D08")
        event = plan["event_instance"]
        self.assertIn("approved_version", event["policy_evidence_omitted"])
        self.assertFalse(plan["policy_time_visibility_used_as_classification_evidence"])
        scope = plan["d08_bounded_scope"]
        self.assertFalse(scope["complete_ten_criterion_manifest_emitted"])
        self.assertFalse(scope["trusted_recovery_confirmation_allowed"])
        self.assertFalse(scope["nonconfirmation_causal_t1_claim_allowed"])

    def test_runner_is_bash3_compatible_single_case_and_fail_closed(self):
        completed = subprocess.run(
            ["/bin/bash", "-n", str(RUNNER)],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        text = RUNNER.read_text(encoding="utf-8")
        self.assertIn('case "$CASE_ID" in D06|D07|D08)', text)
        self.assertIn('EXPECTED_CONFIRM="EXECUTE-$CASE_ID"', text)
        self.assertIn('automatic_next_case=false', text)
        self.assertNotIn('${CASE_ID,,}', text)
        self.assertNotIn('mapfile', text)
        self.assertNotIn('readarray', text)
        self.assertNotIn('declare -A', text)
        self.assertNotIn('for CASE_ID', text)

    def test_runner_cleans_gateway_before_residue_check(self):
        text = RUNNER.read_text(encoding="utf-8")
        nominal = text.index('echo "nominal_runtime_completion=PASS"')
        cleanup = text.index('docker rm -f "$GATEWAY"', nominal)
        residue = text.index('PHASE="RESIDUE_CHECK"')
        self.assertLess(nominal, cleanup)
        self.assertLess(cleanup, residue)

    def test_runner_observation_window_precedes_acceptance(self):
        text = RUNNER.read_text(encoding="utf-8")
        self.assertIn('OBSERVATION_WINDOW_SECONDS=2', text)
        p2_sleep = text.index('sleep "$OBSERVATION_WINDOW_SECONDS"')
        p2_finalize = text.index('finalize-p2')
        self.assertLess(p2_sleep, p2_finalize)
        self.assertIn('finalize-p5', text)


if __name__ == "__main__":
    unittest.main()
