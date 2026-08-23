from __future__ import annotations

import copy
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.mission_recovery.wp9_r065_bounded_runtime_integration import (
    AUTHORIZATION_CLASSIFICATION,
    build_authorization_request,
    build_integration_plan,
)
from src.mission_recovery.wp9_r065_production_integration_executor import (
    build_execution_request,
)
from src.mission_recovery.wp9_r065_runtime_mechanism_driver import (
    BASIS_R061_E1_GIT_BLOB_SHA,
    CONCRETE_CASES,
    build_mechanism_invocation,
    build_z01_authorized_request,
    finalize_z01_measurement,
    validate_static_mechanism_driver,
)

ROOT = Path(__file__).resolve().parents[1]
REPO_SHA = "6a5b2c986d60c93cf87b75ad5e89d1c5687a357e"


def _z01_plan(run_id: str = "r065-z01-static-test") -> dict:
    return build_integration_plan(
        case_id="Z01",
        run_id=run_id,
        repo_commit=REPO_SHA,
    )


def _z01_request(run_id: str = "r065-z01-static-test") -> dict:
    plan = _z01_plan(run_id)
    authorization = build_authorization_request(plan)
    authorization["classification"] = AUTHORIZATION_CLASSIFICATION
    authorization["development_runtime_authorized"] = True
    return build_execution_request(
        plan=plan,
        authorization=authorization,
        current_repo_sha=REPO_SHA,
    )


def _measurement(run_id: str, *, attacker_delta: int = 0) -> dict:
    start = 10_000_000_000
    activation = start + 1_000_000_000
    return {
        "schema": 1,
        "run_id": run_id,
        "run_start_utc": "2026-08-23T22:00:00Z",
        "run_start_ns": start,
        "event_activation_ns": activation,
        "event_success_observed_ns": activation + 100_000_000,
        "policy_selection_ns": activation + 200_000_000,
        "policy_enforcement_ns": activation + 300_000_000,
        "second_attacker_probe_observed_ns": activation + 1_000_000_000,
        "authorized_noop_probe_observed_ns": activation + 2_000_000_000,
        "observation_complete_ns": activation + 30_000_000_000,
        "event_activation_reset_marker_delta": 1,
        "post_enforcement_attacker_probe_count": 2,
        "post_enforcement_attacker_reset_marker_delta": attacker_delta,
        "legitimate_commands_attempted": 1,
        "authorized_noop_marker_delta": 1,
        "gateway_decision_count": 3,
        "attacker_gateway_forwarded_count": 0,
        "authorized_noop_gateway_forwarded": True,
        "runtime_health_passed": True,
        "policy_selection_not_gated_on_event_success": True,
        "attacker_gateway_action": "RESTRICT_HIGH_RISK_COMMANDS",
        "authorized_noop_gateway_action": "RESTRICT_HIGH_RISK_COMMANDS",
    }


class WP9R065ConcreteRuntimeMechanismDriverTests(unittest.TestCase):
    def test_static_driver_is_z01_only_and_preserves_runtime_boundaries(self):
        result = validate_static_mechanism_driver()

        self.assertEqual(result["decision_id"], "R-065")
        self.assertEqual(result["concrete_case_count"], 1)
        self.assertEqual(result["concrete_cases"], ["Z01"])
        self.assertEqual(result["remaining_cases"], [
            "Z02", "Z03", "Z04", "Z05", "Z06", "Z07", "Z08", "Z09"
        ])
        self.assertEqual(CONCRETE_CASES, {"Z01"})
        self.assertEqual(result["runtime_family"], "command")
        self.assertEqual(result["runtime_variant"], "e1_command_gateway")
        self.assertEqual(result["cell_id"], "A06")
        self.assertEqual(result["development_seed"], 9941)
        self.assertEqual(result["basis_runtime_validation_decision_id"], "R-061")
        self.assertEqual(result["basis_r061_e1_git_blob_sha"], BASIS_R061_E1_GIT_BLOB_SHA)
        self.assertTrue(result["one_case_per_invocation"])
        self.assertEqual(result["mechanism_subprocess_invocation_limit"], 1)
        self.assertFalse(result["development_runtime_execution_authorized"])
        self.assertFalse(result["runtime_execution_performed"])
        self.assertFalse(result["development_seed_consumed"])
        self.assertFalse(result["campaign_seed_consumed"])
        self.assertFalse(result["campaign_data_generated"])
        self.assertFalse(result["automatic_retry_allowed"])
        self.assertFalse(result["automatic_next_case_allowed"])
        self.assertFalse(result["final_campaign_execution_authorized"])

    def test_static_driver_locks_the_validated_r061_e1_harness_blob(self):
        source = (ROOT / "scripts" / "run_wp9_r061_e1_route_validation.sh").read_bytes()
        header = f"blob {len(source)}\0".encode("ascii")
        import hashlib

        observed = hashlib.sha1(header + source).hexdigest()
        self.assertEqual(observed, BASIS_R061_E1_GIT_BLOB_SHA)
        self.assertEqual(observed, "5a4596cfbe5941dbaeb833c802d68258343e7f9a")

    def test_authorized_request_is_exact_z01_a06_seed_9941_sha_bound(self):
        env = {
            "WP9_R065_DEVELOPMENT_RUNTIME_AUTHORIZED": "1",
            "WP9_R065_AUTHORIZED_CASE": "Z01",
            "WP9_R065_AUTHORIZED_SEED": "9941",
            "WP9_R065_AUTHORIZED_REPO_SHA": REPO_SHA,
        }
        request = build_z01_authorized_request(
            run_id="r065-z01-auth-test",
            current_repo_sha=REPO_SHA,
            environ=env,
        )
        self.assertEqual(request["case_id"], "Z01")
        self.assertEqual(request["cell_id"], "A06")
        self.assertEqual(request["development_seed"], 9941)
        self.assertEqual(request["repo_commit"], REPO_SHA)
        self.assertEqual(request["event_id"], "E1")
        self.assertEqual(request["runtime_variant"], "e1_command_gateway")
        self.assertTrue(request["single_case_runtime_authorization_validated"])
        self.assertFalse(request["campaign_seed_consumed"])
        self.assertFalse(request["campaign_data_generated"])
        self.assertFalse(request["final_campaign_execution_authorized"])

    def test_authorization_fails_closed_on_case_seed_or_sha_mismatch(self):
        good = {
            "WP9_R065_DEVELOPMENT_RUNTIME_AUTHORIZED": "1",
            "WP9_R065_AUTHORIZED_CASE": "Z01",
            "WP9_R065_AUTHORIZED_SEED": "9941",
            "WP9_R065_AUTHORIZED_REPO_SHA": REPO_SHA,
        }
        mutations = {
            "WP9_R065_AUTHORIZED_CASE": "Z02",
            "WP9_R065_AUTHORIZED_SEED": "9942",
            "WP9_R065_AUTHORIZED_REPO_SHA": "b" * 40,
            "WP9_R065_DEVELOPMENT_RUNTIME_AUTHORIZED": "0",
        }
        for key, value in mutations.items():
            env = dict(good)
            env[key] = value
            with self.subTest(key=key):
                with self.assertRaises((PermissionError, ValueError)):
                    build_z01_authorized_request(
                        run_id="r065-z01-auth-negative",
                        current_repo_sha=REPO_SHA,
                        environ=env,
                    )

    def test_mechanism_invocation_is_one_bash_process_in_development_namespace(self):
        request = _z01_request("r065-z01-invocation")
        invocation = build_mechanism_invocation(request=request, root=ROOT)

        self.assertEqual(invocation["command"][0], "bash")
        self.assertEqual(
            Path(invocation["command"][1]).name,
            "run_wp9_r065_z01_e1_mechanism.sh",
        )
        self.assertEqual(invocation["command"][2], "--request-json")
        self.assertTrue(
            invocation["request_json"].as_posix().startswith(
                (ROOT / "results/wp9/development/r065/integration").as_posix()
            )
        )
        self.assertNotIn("results/wp9/campaign", invocation["request_json"].as_posix())
        self.assertEqual(invocation["subprocess_invocation_limit"], 1)
        self.assertFalse(invocation["automatic_retry_allowed"])
        self.assertFalse(invocation["automatic_next_case_allowed"])

    def test_non_z01_request_is_rejected_before_mechanism_invocation(self):
        plan = build_integration_plan(
            case_id="Z02",
            run_id="r065-z02-negative",
            repo_commit=REPO_SHA,
        )
        auth = build_authorization_request(plan)
        auth["classification"] = AUTHORIZATION_CLASSIFICATION
        auth["development_runtime_authorized"] = True
        request = build_execution_request(
            plan=plan,
            authorization=auth,
            current_repo_sha=REPO_SHA,
        )
        with self.assertRaisesRegex(PermissionError, "Z01 only"):
            build_mechanism_invocation(request=request, root=ROOT)

    def test_z01_measurement_finalizer_accepts_expected_treatment(self):
        request = _z01_request("r065-z01-finalize-pass")
        result = finalize_z01_measurement(
            request=request,
            measurement=_measurement(request["run_id"]),
        )

        self.assertEqual(result["case_id"], "Z01")
        self.assertEqual(result["cell_id"], "A06")
        self.assertEqual(result["development_seed"], 9941)
        self.assertEqual(result["event_id"], "E1")
        self.assertEqual(result["runtime_variant"], "e1_command_gateway")
        self.assertTrue(result["runtime_execution_performed"])
        self.assertTrue(result["treatment_fidelity_valid"])
        self.assertTrue(result["outcome_matches_predeclared_expectation"])
        self.assertFalse(result["campaign_seed_consumed"])
        self.assertFalse(result["campaign_data_generated"])
        self.assertFalse(result["automatic_retry_performed"])
        self.assertFalse(result["automatic_next_case_performed"])
        self.assertFalse(result["final_campaign_execution_authorized"])

    def test_unexpected_scientific_outcome_is_retained_not_retried(self):
        request = _z01_request("r065-z01-unexpected")
        result = finalize_z01_measurement(
            request=request,
            measurement=_measurement(request["run_id"], attacker_delta=1),
        )
        self.assertFalse(result["outcome_matches_predeclared_expectation"])
        self.assertTrue(result["unexpected_scientific_outcome_retained"])
        self.assertFalse(result["automatic_retry_performed"])
        self.assertFalse(result["automatic_next_case_performed"])

    def test_harness_is_r065_z01_specific_and_retains_e1_mechanism_markers(self):
        harness = ROOT / "scripts" / "run_wp9_r065_z01_e1_mechanism.sh"
        source = harness.read_text(encoding="utf-8")
        required = (
            'CASE_ID="Z01"',
            'CELL_ID="A06"',
            'SEED="9941"',
            'IMAGE="ivvitc/nos3-64@sha256:06aa945988a7770b759022c2e1f6f2531818c087fe41a4739d3a3a7f2a9dcce2"',
            "src.mission_recovery.nos3_e1_adapter",
            "sample_reset_counters",
            "modeled_attacker sample_reset_counters",
            "authorized_ground sample_noop",
            "EVENT_ACTIVATION_NS + 30 * 1000000000",
            "results/wp9/development/r065/integration",
            "automatic_retry_allowed=false",
            "automatic_next_case_allowed=false",
            "campaign_seed_consumed=false",
            "campaign_data_generated=false",
        )
        for marker in required:
            with self.subTest(marker=marker):
                self.assertIn(marker, source)
        self.assertNotIn("results/wp9/campaign", source)
        self.assertNotIn("SEED=\"9924\"", source)
        self.assertNotIn("X04", source)

    def test_static_validation_does_not_execute_subprocess(self):
        with patch("subprocess.run") as run:
            result = validate_static_mechanism_driver()
        run.assert_not_called()
        self.assertFalse(result["runtime_execution_performed"])


if __name__ == "__main__":
    unittest.main()
