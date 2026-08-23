from __future__ import annotations

import os
import subprocess
import unittest
from pathlib import Path

from src.mission_recovery.primary_metrics import RECOVERY_CRITERIA
from src.mission_recovery.wp9_campaign_e3_runtime_adapter import (
    APPROVED_SHA256,
    TAMPERED_SHA256,
    DEVELOPMENT_CASES,
    build_development_plan,
    build_p5_handoff,
    campaign_execution_preflight,
    development_execution_preflight,
    finalize_development_observation,
    materialize_runtime_artifacts,
    select_runtime_policy,
    validate_static_runtime_adapter,
)

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts" / "run_wp9_r063_e3_route_validation.sh"
REPO_SHA = "a" * 40


class WP9R063E3RuntimeAdapterTests(unittest.TestCase):
    def _plan(self, case_id: str) -> dict:
        return build_development_plan(
            case_id=case_id,
            run_id=f"wp9-r063-{case_id.lower()}-static",
            repo_commit=REPO_SHA,
        )

    def _criteria(self, *, noop_delta: int = 1) -> dict:
        result = {}
        for criterion in RECOVERY_CRITERIA:
            result[criterion] = {
                "available_current": True,
                "criterion_satisfied": (
                    noop_delta == 1
                    if criterion == "authorized_command_path_restored"
                    else True
                ),
                "evidence_ref": f"static/r063/{criterion}.json",
            }
        return result

    def _measurement(
        self,
        *,
        plan: dict,
        noop_delta: int = 1,
        trusted: bool = True,
    ) -> dict:
        effective = plan["expected_effective_policy_id_for_acceptance_only"]
        contact = plan["factor_context"]["contact_condition_id"]
        base = {
            "schema": 1,
            "run_id": plan["run_id"],
            "run_start_utc": "2026-08-23T04:00:00Z",
            "run_start_ns": 1_000_000_000,
            "event_activation_ns": 2_000_000_000,
            "event_success_observed_ns": 2_150_000_000,
            "policy_selection_ns": 2_100_000_000,
            "policy_enforcement_ns": 2_200_000_000,
            "response_boundary_ns": 2_200_000_000,
            "observation_complete_ns": 32_100_000_000,
            "event_activation_observed": True,
            "event_slot_sha256": TAMPERED_SHA256,
            "runtime_health_passed": True,
            "policy_selection_not_gated_on_event_success": True,
            "authorized_noop_attempted": 1,
            "authorized_noop_marker_delta": noop_delta,
        }

        if effective == "P2":
            base.update(
                {
                    "post_response_slot_sha256": TAMPERED_SHA256,
                    "update_containment_observed": False,
                    "matched_attacker_probe_count": 2,
                    "gateway_decision_count": 3,
                    "attacker_gateway_forwarded_count": 0,
                    "authorized_noop_gateway_forwarded": True,
                    "gateway_action": "RESTRICT_HIGH_RISK_COMMANDS",
                    "observed_post_enforcement_attacker_reset_marker_delta": 0,
                    "ground_authorization_waited": False,
                }
            )
            return base

        base.update(
            {
                "post_response_slot_sha256": APPROVED_SHA256,
                "rollback_request_validated": True,
                "approved_replacement_source_verified": True,
                "temporary_recovery_state_absent": True,
                "rollback_complete_ns": 5_000_000_000,
                "trusted_recovery_confirmed": trusted,
                "recovery_criteria": self._criteria(noop_delta=noop_delta),
                "ground_authorization_waited": effective == "P6",
            }
        )

        if effective == "P6":
            if contact == "C0":
                auth_ns = 2_300_000_000
                available = True
                missed = 0
                rollback_ns = 5_000_000_000
                trusted_ns = 6_000_000_000
            else:
                auth_ns = 12_200_000_000
                available = False
                missed = 1
                rollback_ns = 15_000_000_000
                trusted_ns = 16_000_000_000
            base.update(
                {
                    "ground_authorization_source": (
                        "synthetic_ground_authorization_schedule"
                    ),
                    "ground_authorization_current": True,
                    "authorization_observed_ns": auth_ns,
                    "handoff_ns": auth_ns + 100_000_000,
                    "authorization_available_at_response_boundary": available,
                    "missed_contact_windows_observed": missed,
                    "post_authorization_delegate": "P5",
                    "post_authorization_action": "REQUEST_VERIFIED_ROLLBACK",
                    "rollback_complete_ns": rollback_ns,
                }
            )
            if trusted:
                base["trusted_recovery_observed_ns"] = trusted_ns
                base["observation_complete_ns"] = trusted_ns + 100_000_000
        elif trusted:
            base["trusted_recovery_observed_ns"] = 6_000_000_000
            base["observation_complete_ns"] = 6_100_000_000

        if not trusted:
            base["recovery_criteria"][
                "recovery_manifest_complete"
            ]["criterion_satisfied"] = False
            base["observation_complete_ns"] = 32_100_000_000

        return base

    def _summary(
        self,
        case_id: str,
        *,
        noop_delta: int = 1,
        trusted: bool = True,
    ) -> dict:
        plan = self._plan(case_id)
        policy = select_runtime_policy(plan)
        return finalize_development_observation(
            plan=plan,
            runtime_policy=policy,
            measurement=self._measurement(
                plan=plan,
                noop_delta=noop_delta,
                trusted=trusted,
            ),
        )

    def test_static_gate_freezes_exact_six_case_set(self) -> None:
        result = validate_static_runtime_adapter()
        self.assertEqual(result["decision_id"], "R-063")
        self.assertEqual(
            DEVELOPMENT_CASES,
            {
                "Y01": {"cell_id": "A13", "development_seed": 9931},
                "Y02": {"cell_id": "A11", "development_seed": 9932},
                "Y03": {"cell_id": "A15", "development_seed": 9933},
                "Y04": {"cell_id": "A16", "development_seed": 9934},
                "Y05": {"cell_id": "A17", "development_seed": 9935},
                "Y06": {"cell_id": "A18", "development_seed": 9936},
            },
        )
        self.assertEqual(result["minimal_representative_case_count"], 6)
        self.assertEqual(len(result["covered_runtime_variants"]), 5)
        self.assertEqual(
            result["omitted_runtime_duplicates"],
            {"A10": "Y01", "A12": "Y01", "A14": "Y02"},
        )
        self.assertFalse(result["development_runtime_execution_authorized"])
        self.assertFalse(result["campaign_seed_consumed"])
        self.assertFalse(result["campaign_data_generated"])
        self.assertFalse(result["final_campaign_execution_authorized"])

    def test_all_case_bindings_and_policy_selection_are_frozen(self) -> None:
        expected = {
            "Y01": ("A13", "P7", "P2", "e3_command_gateway"),
            "Y02": ("A11", "P7", "P5", "e3_trusted_recovery"),
            "Y03": (
                "A15",
                "P5",
                "P5",
                "e3_trusted_recovery_reduced_evidence",
            ),
            "Y04": (
                "A16",
                "P6",
                "P6",
                "e3_ground_authorized_recovery",
            ),
            "Y05": (
                "A17",
                "P6",
                "P6",
                "e3_ground_authorized_recovery",
            ),
            "Y06": (
                "A18",
                "P7",
                "P5",
                "e3_trusted_recovery_contact_delay",
            ),
        }
        for case_id, values in expected.items():
            plan = self._plan(case_id)
            policy = select_runtime_policy(plan)
            cell_id, requested, effective, variant = values
            self.assertEqual(plan["cell_id"], cell_id)
            self.assertEqual(plan["factor_context"]["policy_id"], requested)
            self.assertEqual(policy["delegated_policy_id"], effective)
            self.assertEqual(plan["runtime_variant"], variant)
            self.assertFalse(policy["oracle_ground_truth_read"])

    def test_fresh_seeds_and_frozen_timing_are_explicit(self) -> None:
        result = validate_static_runtime_adapter()
        self.assertEqual(result["modeled_c1_contact_window_s"], 10)
        self.assertEqual(result["post_event_analysis_horizon_s"], 30)
        seeds = {
            row["development_seed"]
            for row in result["development_cases"].values()
        }
        self.assertEqual(seeds, {9931, 9932, 9933, 9934, 9935, 9936})

        y04 = self._plan("Y04")
        y05 = self._plan("Y05")
        y06 = self._plan("Y06")
        self.assertEqual(
            y04["timing_contract"][
                "p6_ground_authorization_release_after_response_boundary_s"
            ],
            0,
        )
        self.assertEqual(
            y05["timing_contract"][
                "p6_ground_authorization_release_after_response_boundary_s"
            ],
            10,
        )
        self.assertIsNone(
            y06["timing_contract"][
                "p6_ground_authorization_release_after_response_boundary_s"
            ]
        )

    def test_p6_handoff_is_p5_and_has_no_real_ground_claim(self) -> None:
        for case_id in ("Y04", "Y05"):
            plan = self._plan(case_id)
            policy = select_runtime_policy(plan)
            handoff = build_p5_handoff(
                plan=plan,
                runtime_policy=policy,
            )
            self.assertEqual(handoff["delegated_policy_id"], "P5")
            self.assertEqual(
                handoff["selected_action"],
                "REQUEST_VERIFIED_ROLLBACK",
            )
            self.assertFalse(handoff["oracle_ground_truth_read"])
            self.assertFalse(handoff["real_ground_contact"])
            self.assertFalse(handoff["real_human_operator"])

    def test_runtime_artifact_identities_are_frozen(self) -> None:
        bundle = materialize_runtime_artifacts(plan=self._plan("Y02"))
        self.assertEqual(
            bundle["approved_manifest"]["approved_sha256"],
            APPROVED_SHA256,
        )
        self.assertFalse(bundle["tampered_verification"]["accepted"])
        self.assertEqual(
            bundle["tampered_verification"]["actual_sha256"],
            TAMPERED_SHA256,
        )

    def test_y01_p7_to_p2_keeps_command_mitigation_separate(self) -> None:
        summary = self._summary("Y01")
        self.assertEqual(summary["requested_policy_id"], "P7")
        self.assertEqual(summary["actual_effective_policy_id"], "P2")
        self.assertEqual(
            summary["selected_action"],
            "RESTRICT_HIGH_RISK_COMMANDS",
        )
        self.assertFalse(summary["update_containment_observed"])
        self.assertFalse(
            summary["p2_command_mitigation_counts_as_update_containment"]
        )
        self.assertEqual(summary["post_event_analysis_horizon_s"], 30)

    def test_y02_and_y03_cover_full_and_reduced_recovery(self) -> None:
        y02 = self._summary("Y02")
        y03 = self._summary("Y03")
        self.assertTrue(y02["update_containment_observed"])
        self.assertTrue(y02["trusted_recovery_confirmed"])
        self.assertEqual(y02["runtime_variant"], "e3_trusted_recovery")
        self.assertTrue(y03["update_containment_observed"])
        self.assertTrue(y03["trusted_recovery_confirmed"])
        self.assertEqual(
            y03["runtime_variant"],
            "e3_trusted_recovery_reduced_evidence",
        )

    def test_p6_c0_and_c1_runtime_observations_are_distinct(self) -> None:
        y04 = self._summary("Y04")
        y05 = self._summary("Y05")
        self.assertTrue(y04["ground_authorization_waited"])
        self.assertTrue(y05["ground_authorization_waited"])
        self.assertIsNone(y04["modeled_c1_contact_window_s"])
        self.assertEqual(y05["modeled_c1_contact_window_s"], 10)

    def test_p6_c1_authorization_before_ten_seconds_fails_closed(self) -> None:
        plan = self._plan("Y05")
        policy = select_runtime_policy(plan)
        measurement = self._measurement(plan=plan)
        measurement["authorization_observed_ns"] = 12_199_999_999
        measurement["handoff_ns"] = 12_300_000_000
        with self.assertRaisesRegex(
            ValueError,
            "before frozen 10-second window",
        ):
            finalize_development_observation(
                plan=plan,
                runtime_policy=policy,
                measurement=measurement,
            )

    def test_y06_c1_is_autonomous_without_ground_wait(self) -> None:
        summary = self._summary("Y06")
        self.assertEqual(summary["requested_policy_id"], "P7")
        self.assertEqual(summary["actual_effective_policy_id"], "P5")
        self.assertEqual(summary["modeled_c1_contact_window_s"], 10)
        self.assertFalse(summary["ground_authorization_waited"])

        plan = self._plan("Y06")
        policy = select_runtime_policy(plan)
        measurement = self._measurement(plan=plan)
        measurement["ground_authorization_waited"] = True
        with self.assertRaisesRegex(ValueError, "autonomous P5"):
            finalize_development_observation(
                plan=plan,
                runtime_policy=policy,
                measurement=measurement,
            )

    def test_unexpected_legitimate_service_loss_is_retained(self) -> None:
        summary = self._summary(
            "Y02",
            noop_delta=0,
            trusted=False,
        )
        self.assertFalse(
            summary["outcome_matches_predeclared_expectation"]
        )
        self.assertTrue(
            summary[
                "unexpected_scientific_outcome_would_be_retained_in_campaign"
            ]
        )
        self.assertTrue(summary["treatment_fidelity_valid"])

    def test_development_and_campaign_execution_remain_blocked(self) -> None:
        with self.assertRaises(PermissionError):
            development_execution_preflight()
        with self.assertRaises(PermissionError):
            campaign_execution_preflight()

    def _blocked_run(
        self,
        case_id: str,
        **updates: str,
    ) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        for key in (
            "WP9_R063_DEVELOPMENT_RUNTIME_AUTHORIZED",
            "WP9_R063_AUTHORIZED_CASE",
            "WP9_R063_AUTHORIZED_REPO_SHA",
        ):
            env.pop(key, None)
        env.update(updates)
        return subprocess.run(
            ["/bin/bash", str(RUNNER), case_id],
            cwd=ROOT,
            env=env,
            check=False,
            capture_output=True,
            text=True,
        )

    def test_harness_is_bash32_safe_and_single_case_only(self) -> None:
        completed = subprocess.run(
            ["/bin/bash", "-n", str(RUNNER)],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        text = RUNNER.read_text(encoding="utf-8")
        self.assertIn('[[ "$#" -eq 1 ]]', text)
        self.assertNotIn("mapfile", text)
        self.assertNotIn("readarray", text)
        self.assertNotIn("declare -A", text)
        self.assertNotIn("results/wp9/campaign", text)
        self.assertIn("automatic_retry_allowed=false", text)
        self.assertIn("automatic_next_case_allowed=false", text)

    def test_harness_freezes_exact_six_case_mapping(self) -> None:
        text = RUNNER.read_text(encoding="utf-8")
        expected = (
            'Y01) CELL_ID="A13"; SEED="9931" ;;',
            'Y02) CELL_ID="A11"; SEED="9932" ;;',
            'Y03) CELL_ID="A15"; SEED="9933" ;;',
            'Y04) CELL_ID="A16"; SEED="9934" ;;',
            'Y05) CELL_ID="A17"; SEED="9935" ;;',
            'Y06) CELL_ID="A18"; SEED="9936" ;;',
        )
        for row in expected:
            self.assertIn(row, text)
        self.assertIn("results/wp9/development/r063/e3", text)

    def test_harness_default_gate_precedes_docker_and_evidence(self) -> None:
        completed = self._blocked_run("Y01")
        combined = completed.stdout + completed.stderr
        self.assertEqual(completed.returncode, 3, combined)
        self.assertIn("development runtime remains blocked", combined)

        text = RUNNER.read_text(encoding="utf-8")
        gate = text.index('[[ "$RUNTIME_AUTHORIZED" == "1" ]]')
        docker = text.index("docker info")
        evidence = text.index('mkdir -p "$GROUND" "$OBS"')
        self.assertLess(gate, docker)
        self.assertLess(gate, evidence)

    def test_harness_authorization_is_case_scoped(self) -> None:
        completed = self._blocked_run(
            "Y01",
            WP9_R063_DEVELOPMENT_RUNTIME_AUTHORIZED="1",
            WP9_R063_AUTHORIZED_CASE="Y02",
            WP9_R063_AUTHORIZED_REPO_SHA="0" * 40,
        )
        combined = completed.stdout + completed.stderr
        self.assertEqual(completed.returncode, 3, combined)
        self.assertIn(
            "authorization is not for requested case Y01",
            combined,
        )

    def test_harness_authorization_is_exact_sha_scoped(self) -> None:
        completed = self._blocked_run(
            "Y01",
            WP9_R063_DEVELOPMENT_RUNTIME_AUTHORIZED="1",
            WP9_R063_AUTHORIZED_CASE="Y01",
            WP9_R063_AUTHORIZED_REPO_SHA="0" * 40,
        )
        combined = completed.stdout + completed.stderr
        self.assertEqual(completed.returncode, 3, combined)
        self.assertIn("authorization SHA does not match", combined)

    def test_harness_preserves_e3_timing_and_contact_contracts(self) -> None:
        text = RUNNER.read_text(encoding="utf-8")
        activation = text.index('PHASE="EVENT_ACTIVATION"')
        selection = text.index('PHASE="POLICY_SELECTION"')
        confirmation = text.index('PHASE="EVENT_SUCCESS_CONFIRMATION"')
        enforcement = text.index('PHASE="POLICY_ENFORCEMENT"')
        self.assertLess(activation, selection)
        self.assertLess(selection, confirmation)
        self.assertLess(confirmation, enforcement)
        self.assertIn(
            'RESPONSE_BOUNDARY_NS + 10 * 1000000000',
            text,
        )
        self.assertIn(
            'ANALYSIS_END_NS=$((EVENT_ACTIVATION_NS + 30 * 1000000000))',
            text,
        )
        self.assertIn(
            "policy_selection_not_gated_on_event_success=true",
            text,
        )
        self.assertIn("real_ground_contact", text)

    def test_harness_cleans_residue_and_never_auto_advances(self) -> None:
        text = RUNNER.read_text(encoding="utf-8")
        auxiliary = text.index('PHASE="AUXILIARY_CLEANUP"')
        nominal = text.index('PHASE="NOMINAL_RUNTIME_COMPLETION"')
        audit = text.index('PHASE="CLEANUP_AUDIT"')
        self.assertLess(auxiliary, nominal)
        self.assertLess(nominal, audit)
        self.assertIn('docker network rm "$NETWORK"', text[audit:])
        self.assertIn("residual_runtime=none", text[audit:])
        self.assertIn("automatic_retry_allowed=false", text[audit:])
        self.assertIn("automatic_next_case_allowed=false", text[audit:])


if __name__ == "__main__":
    unittest.main()
