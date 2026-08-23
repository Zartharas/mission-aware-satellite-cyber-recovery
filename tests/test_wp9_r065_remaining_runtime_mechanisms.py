from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import patch

from src.mission_recovery.primary_metrics import RECOVERY_CRITERIA
from src.mission_recovery.wp9_r065_bounded_runtime_integration import (
    AUTHORIZATION_CLASSIFICATION,
    INTEGRATION_CASES,
    build_authorization_request,
    build_integration_plan,
)
from src.mission_recovery.wp9_r065_production_integration_executor import (
    build_execution_request,
)
from src.mission_recovery.wp9_r065_remaining_runtime_mechanism_driver import (
    BASIS_SCRIPT_BLOBS,
    CONCRETE_CASES,
    build_authorized_request,
    build_mechanism_invocation,
    finalize_case_measurement,
    validate_static_remaining_mechanisms,
)

ROOT = Path(__file__).resolve().parents[1]
REPO_SHA = "d" * 40


def _request(case_id: str) -> dict:
    plan = build_integration_plan(
        case_id=case_id,
        run_id=f"r065-{case_id.lower()}-test",
        repo_commit=REPO_SHA,
    )
    auth = build_authorization_request(plan)
    auth["classification"] = AUTHORIZATION_CLASSIFICATION
    auth["development_runtime_authorized"] = True
    return build_execution_request(
        plan=plan,
        authorization=auth,
        current_repo_sha=REPO_SHA,
    )


def _e2_measurement(run_id: str) -> dict:
    activation = 2_000_000_000
    return {
        "schema": 1,
        "run_id": run_id,
        "run_start_utc": "2026-08-23T23:00:00Z",
        "run_start_ns": 1_000_000_000,
        "event_activation_ns": activation,
        "policy_enforcement_ns": activation + 100_000_000,
        "replay_gateway_decision_ns": activation + 200_000_000,
        "replay_effect_observed_ns": None,
        "authorized_noop_probe_observed_ns": activation + 300_000_000,
        "observation_complete_ns": activation + 30_000_000_000,
        "setup_reset_marker_delta": 1,
        "intervening_authorized_noop_marker_delta": 1,
        "post_replay_reset_marker_delta": 0,
        "post_response_authorized_noop_attempted": 1,
        "post_response_authorized_noop_marker_delta": 1,
        "gateway_decision_count": 2,
        "replayed_packet_byte_identical": True,
        "runtime_health_passed": True,
        "replay_gateway_action": "ISOLATE_MODELED_SOURCE",
        "replay_gateway_forwarded": False,
        "authorized_noop_gateway_action": "ISOLATE_MODELED_SOURCE",
        "authorized_noop_gateway_forwarded": True,
    }


def _e4_measurement(run_id: str) -> dict:
    activation = 2_000_000_000
    return {
        "schema": 1,
        "run_id": run_id,
        "run_start_utc": "2026-08-23T23:00:00Z",
        "run_start_ns": 1_000_000_000,
        "event_activation_ns": activation,
        "policy_selection_ns": activation + 100_000_000,
        "policy_enforcement_ns": activation + 200_000_000,
        "event_success_observed_ns": activation + 3_000_000_000,
        "post_response_probe_observed_ns": activation + 6_000_000_000,
        "authorized_noop_probe_observed_ns": activation + 7_000_000_000,
        "observation_complete_ns": activation + 30_000_000_000,
        "event_truth_high_value_delta": 1,
        "event_policy_visible_high_value_delta": 0,
        "post_response_truth_high_value_delta": 1,
        "post_response_policy_visible_high_value_delta": 0,
        "post_response_authorized_noop_attempted": 1,
        "post_response_authorized_noop_marker_delta": 0,
        "gateway_decision_count": 1,
        "immutable_truth_separate": True,
        "runtime_health_passed": True,
        "gateway_action": "ENTER_SAFE_MODE",
        "authorized_noop_gateway_forwarded": False,
    }


def _criteria() -> dict:
    return {
        criterion: {
            "available_current": True,
            "criterion_satisfied": True,
            "evidence_ref": f"test/{criterion}.json",
            "observed_ns": 2_500_000_000,
        }
        for criterion in RECOVERY_CRITERIA
    }


def _e3_measurement(request: dict) -> dict:
    activation = 2_000_000_000
    selection = activation + 100_000_000
    enforcement = activation + 200_000_000
    response = enforcement
    effective = request["actual_effective_policy_id"]
    row = {
        "schema": 1,
        "run_id": request["run_id"],
        "run_start_utc": "2026-08-23T23:00:00Z",
        "run_start_ns": 1_000_000_000,
        "event_activation_ns": activation,
        "event_success_observed_ns": activation + 150_000_000,
        "policy_selection_ns": selection,
        "policy_enforcement_ns": enforcement,
        "response_boundary_ns": response,
        "observation_complete_ns": activation + 30_000_000_000,
        "event_activation_observed": True,
        "event_slot_sha256": "ff96d61205cc2c49b6d7d73fc36b9544c0deea79d7a9304cc1fb9f1f8986053d",
        "runtime_health_passed": True,
        "policy_selection_not_gated_on_event_success": True,
        "authorized_noop_attempted": 1,
        "authorized_noop_marker_delta": 1,
        "ground_authorization_waited": False,
    }
    if effective == "P2":
        row.update({
            "post_response_slot_sha256": "ff96d61205cc2c49b6d7d73fc36b9544c0deea79d7a9304cc1fb9f1f8986053d",
            "update_containment_observed": False,
            "matched_attacker_probe_count": 2,
            "gateway_decision_count": 3,
            "attacker_gateway_forwarded_count": 0,
            "authorized_noop_gateway_forwarded": True,
            "gateway_action": "RESTRICT_HIGH_RISK_COMMANDS",
            "observed_post_enforcement_attacker_reset_marker_delta": 0,
        })
        return row

    rollback_ns = activation + 1_000_000_000
    if effective == "P6":
        row["ground_authorization_waited"] = True
        if request["factor_context"]["contact_condition_id"] == "C1":
            auth_ns = response + 10_000_000_000
            missed = 1
            available = False
        else:
            auth_ns = response + 10_000_000
            missed = 0
            available = True
        handoff_ns = auth_ns + 10_000_000
        rollback_ns = handoff_ns + 10_000_000
        row.update({
            "ground_authorization_source": "synthetic_ground_authorization_schedule",
            "ground_authorization_current": True,
            "authorization_observed_ns": auth_ns,
            "handoff_ns": handoff_ns,
            "authorization_available_at_response_boundary": available,
            "missed_contact_windows_observed": missed,
            "post_authorization_delegate": "P5",
            "post_authorization_action": "REQUEST_VERIFIED_ROLLBACK",
        })

    row.update({
        "post_response_slot_sha256": "42945a2622fa351b3a3fdc31e002cbe326cb7a42a958ee757f317abea67b6697",
        "rollback_request_validated": True,
        "approved_replacement_source_verified": True,
        "temporary_recovery_state_absent": True,
        "rollback_complete_ns": rollback_ns,
        "trusted_recovery_confirmed": True,
        "trusted_recovery_observed_ns": rollback_ns + 10_000_000,
        "recovery_criteria": _criteria(),
    })
    return row


class WP9R065RemainingRuntimeMechanismTests(unittest.TestCase):
    def test_static_binding_covers_z02_through_z09_with_three_family_harnesses(self):
        result = validate_static_remaining_mechanisms()
        self.assertEqual(CONCRETE_CASES, set(f"Z{i:02d}" for i in range(2, 10)))
        self.assertEqual(result["concrete_case_count"], 8)
        self.assertEqual(result["family_harness_count"], 3)
        self.assertEqual(result["concrete_cases"], [f"Z{i:02d}" for i in range(2, 10)])
        self.assertEqual(result["development_seeds"], list(range(9942, 9950)))
        self.assertTrue(result["one_case_per_invocation"])
        self.assertEqual(result["mechanism_subprocess_invocation_limit"], 1)
        self.assertFalse(result["automatic_retry_allowed"])
        self.assertFalse(result["automatic_next_case_allowed"])
        self.assertFalse(result["runtime_execution_performed"])
        self.assertFalse(result["campaign_seed_consumed"])
        self.assertFalse(result["campaign_data_generated"])
        self.assertFalse(result["final_campaign_execution_authorized"])

    def test_basis_harness_blobs_are_locked(self):
        self.assertEqual(BASIS_SCRIPT_BLOBS, {
            "R-057": "4530cde131dd5a27454411d9e39f99e36c58b211",
            "R-059": "c51e254e1d00f6b59dbd33f6130eda8ff506bae1",
            "R-063": "76193d768ee48bfc5748f5fc6c12675d8057456e",
        })

    def test_exact_authorization_is_bound_for_each_remaining_case(self):
        for case_id in sorted(CONCRETE_CASES):
            seed = INTEGRATION_CASES[case_id]["development_seed"]
            env = {
                "WP9_R065_DEVELOPMENT_RUNTIME_AUTHORIZED": "1",
                "WP9_R065_AUTHORIZED_CASE": case_id,
                "WP9_R065_AUTHORIZED_SEED": str(seed),
                "WP9_R065_AUTHORIZED_REPO_SHA": REPO_SHA,
            }
            with self.subTest(case_id=case_id):
                request = build_authorized_request(
                    case_id=case_id,
                    run_id=f"r065-{case_id.lower()}-auth",
                    current_repo_sha=REPO_SHA,
                    environ=env,
                )
                self.assertEqual(request["case_id"], case_id)
                self.assertEqual(request["development_seed"], seed)
                self.assertEqual(request["repo_commit"], REPO_SHA)

    def test_authorization_rejects_case_seed_or_sha_mismatch(self):
        good = {
            "WP9_R065_DEVELOPMENT_RUNTIME_AUTHORIZED": "1",
            "WP9_R065_AUTHORIZED_CASE": "Z02",
            "WP9_R065_AUTHORIZED_SEED": "9942",
            "WP9_R065_AUTHORIZED_REPO_SHA": REPO_SHA,
        }
        for key, value in (
            ("WP9_R065_AUTHORIZED_CASE", "Z03"),
            ("WP9_R065_AUTHORIZED_SEED", "9943"),
            ("WP9_R065_AUTHORIZED_REPO_SHA", "e" * 40),
            ("WP9_R065_DEVELOPMENT_RUNTIME_AUTHORIZED", "0"),
        ):
            env = dict(good)
            env[key] = value
            with self.subTest(key=key):
                with self.assertRaises((PermissionError, ValueError)):
                    build_authorized_request(
                        case_id="Z02",
                        run_id="r065-z02-negative",
                        current_repo_sha=REPO_SHA,
                        environ=env,
                    )

    def test_invocation_routes_to_exactly_three_family_harnesses(self):
        expected = {
            "Z02": "run_wp9_r065_e2_mechanism.sh",
            "Z03": "run_wp9_r065_e4_mechanism.sh",
            "Z04": "run_wp9_r065_e3_mechanism.sh",
            "Z05": "run_wp9_r065_e3_mechanism.sh",
            "Z06": "run_wp9_r065_e3_mechanism.sh",
            "Z07": "run_wp9_r065_e3_mechanism.sh",
            "Z08": "run_wp9_r065_e3_mechanism.sh",
            "Z09": "run_wp9_r065_e3_mechanism.sh",
        }
        for case_id, script_name in expected.items():
            request = _request(case_id)
            invocation = build_mechanism_invocation(request=request, root=ROOT)
            with self.subTest(case_id=case_id):
                self.assertEqual(invocation["command"][0], "bash")
                self.assertEqual(Path(invocation["command"][1]).name, script_name)
                self.assertEqual(invocation["subprocess_invocation_limit"], 1)
                self.assertIn(
                    f"results/wp9/development/r065/integration/{request['run_id']}",
                    invocation["request_json"].as_posix(),
                )
                self.assertNotIn("results/wp9/campaign", invocation["request_json"].as_posix())

    def test_z02_reuses_e2_measurement_contract(self):
        request = _request("Z02")
        result = finalize_case_measurement(request=request, measurement=_e2_measurement(request["run_id"]))
        self.assertTrue(result["treatment_fidelity_valid"])
        self.assertTrue(result["outcome_matches_predeclared_expectation"])
        self.assertEqual(result["post_replay_reset_marker_delta"], 0)
        self.assertFalse(result["replay_gateway_forwarded"])
        self.assertTrue(result["authorized_noop_gateway_forwarded"])

    def test_z03_reuses_e4_measurement_contract(self):
        request = _request("Z03")
        result = finalize_case_measurement(request=request, measurement=_e4_measurement(request["run_id"]))
        self.assertTrue(result["treatment_fidelity_valid"])
        self.assertTrue(result["outcome_matches_predeclared_expectation"])
        self.assertEqual(result["event_truth_high_value_delta"], 1)
        self.assertEqual(result["event_policy_visible_high_value_delta"], 0)
        self.assertEqual(result["post_response_policy_visible_high_value_delta"], 0)
        self.assertFalse(result["authorized_noop_gateway_forwarded"])

    def test_z04_through_z09_reuse_e3_measurement_contracts(self):
        for case_id in ("Z04", "Z05", "Z06", "Z07", "Z08", "Z09"):
            request = _request(case_id)
            result = finalize_case_measurement(
                request=request,
                measurement=_e3_measurement(request),
            )
            with self.subTest(case_id=case_id):
                self.assertTrue(result["treatment_fidelity_valid"])
                self.assertTrue(result["outcome_matches_predeclared_expectation"])
                self.assertFalse(result["automatic_retry_performed"])
                self.assertFalse(result["automatic_next_case_performed"])
                self.assertFalse(result["campaign_seed_consumed"])
                self.assertFalse(result["campaign_data_generated"])

    def test_family_harnesses_are_development_only_and_campaign_free(self):
        for name in (
            "run_wp9_r065_e2_mechanism.sh",
            "run_wp9_r065_e4_mechanism.sh",
            "run_wp9_r065_e3_mechanism.sh",
        ):
            source = (ROOT / "scripts" / name).read_text(encoding="utf-8")
            with self.subTest(name=name):
                self.assertIn("results/wp9/development/r065/integration", source)
                self.assertNotIn("results/wp9/campaign", source)
                self.assertIn("automatic_retry_allowed=false", source)
                self.assertIn("automatic_next_case_allowed=false", source)
                self.assertIn("campaign_seed_consumed=false", source)
                self.assertIn("campaign_data_generated=false", source)

    def test_static_validation_never_runs_mechanism_subprocess(self):
        with patch("subprocess.run") as run:
            result = validate_static_remaining_mechanisms()
        run.assert_not_called()
        self.assertFalse(result["runtime_execution_performed"])


if __name__ == "__main__":
    unittest.main()
