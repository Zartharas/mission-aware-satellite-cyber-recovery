from __future__ import annotations

import copy
import unittest
from pathlib import Path

from src.mission_recovery.wp9_r065_bounded_runtime_integration import (
    AUTHORIZATION_CLASSIFICATION,
    INTEGRATION_CASES,
    build_authorization_request,
    build_integration_plan,
)
from src.mission_recovery.wp9_r065_production_integration_executor import (
    MECHANISM_BINDINGS,
    build_execution_request,
    execute_request,
    validate_execution_request,
    validate_static_executor,
)

REPO_SHA = "a" * 40
ROOT = Path(__file__).resolve().parents[1]


def _plan(case_id: str) -> dict:
    return build_integration_plan(
        case_id=case_id,
        run_id=f"r065-production-{case_id.lower()}",
        repo_commit=REPO_SHA,
    )


def _authorization(plan: dict, *, granted: bool = True) -> dict:
    authorization = build_authorization_request(plan)
    authorization["classification"] = AUTHORIZATION_CLASSIFICATION
    authorization["development_runtime_authorized"] = granted
    return authorization


def _request(case_id: str) -> dict:
    plan = _plan(case_id)
    return build_execution_request(
        plan=plan,
        authorization=_authorization(plan),
        current_repo_sha=REPO_SHA,
    )


def _driver_result(request: dict, **overrides) -> dict:
    result = {
        "case_id": request["case_id"],
        "run_id": request["run_id"],
        "cell_id": request["cell_id"],
        "development_seed": request["development_seed"],
        "event_id": request["event_id"],
        "runtime_variant": request["runtime_variant"],
        "runtime_execution_performed": True,
        "treatment_fidelity_valid": True,
        "outcome_matches_predeclared_expectation": True,
        "campaign_seed_consumed": False,
        "campaign_data_generated": False,
        "final_campaign_execution_authorized": False,
        "automatic_retry_performed": False,
        "automatic_next_case_performed": False,
    }
    result.update(overrides)
    return result


class WP9R065ProductionIntegrationExecutorTests(unittest.TestCase):
    def test_static_executor_binds_all_nine_signatures_without_runtime(self):
        result = validate_static_executor()

        self.assertEqual(result["decision_id"], "R-065")
        self.assertEqual(result["integration_case_count"], 9)
        self.assertEqual(result["runtime_variant_count"], 8)
        self.assertEqual(result["integration_signature_count"], 9)
        self.assertEqual(result["event_family_count"], 4)
        self.assertTrue(result["production_integration_executor_bound"])
        self.assertEqual(result["mechanism_binding_count"], 9)
        self.assertEqual(result["driver_invocation_limit"], 1)
        self.assertTrue(result["unexpected_scientific_outcome_retained"])
        self.assertTrue(result["treatment_fidelity_failure_retained"])
        self.assertFalse(result["development_runtime_execution_authorized"])
        self.assertFalse(result["runtime_execution_performed"])
        self.assertFalse(result["campaign_seed_consumed"])
        self.assertFalse(result["campaign_data_generated"])
        self.assertFalse(result["final_campaign_execution_authorized"])
        self.assertFalse(result["automatic_retry_allowed"])
        self.assertFalse(result["automatic_next_case_allowed"])

    def test_exact_mechanism_bindings_cover_validated_route_decisions(self):
        expected = {
            "e1_command_gateway": ("E1", "command", "R-060", "R-061"),
            "e2_replay_effect": ("E2", "replay", "R-056", "R-057"),
            "e4_observability": ("E4", "observability", "R-058", "R-059"),
            "e3_command_gateway": ("E3", "recovery", "R-062", "R-063"),
            "e3_trusted_recovery": ("E3", "recovery", "R-062", "R-063"),
            "e3_trusted_recovery_reduced_evidence": (
                "E3", "recovery", "R-062", "R-063"
            ),
            "e3_ground_authorized_recovery:C0": (
                "E3", "recovery", "R-062", "R-063"
            ),
            "e3_ground_authorized_recovery:C1": (
                "E3", "recovery", "R-062", "R-063"
            ),
            "e3_trusted_recovery_contact_delay": (
                "E3", "recovery", "R-062", "R-063"
            ),
        }
        self.assertEqual(set(MECHANISM_BINDINGS), set(expected))
        for signature, values in expected.items():
            event_id, family, observation, prior_runtime = values
            binding = MECHANISM_BINDINGS[signature]
            self.assertEqual(binding["event_id"], event_id)
            self.assertEqual(binding["runtime_family"], family)
            self.assertEqual(
                binding["campaign_observation_adapter_decision_id"], observation
            )
            self.assertEqual(
                binding["prior_runtime_validation_decision_id"], prior_runtime
            )

    def test_all_z_cases_build_development_only_execution_requests(self):
        for case_id in sorted(INTEGRATION_CASES):
            with self.subTest(case_id=case_id):
                plan = _plan(case_id)
                request = build_execution_request(
                    plan=plan,
                    authorization=_authorization(plan),
                    current_repo_sha=REPO_SHA,
                )
                self.assertEqual(request["case_id"], case_id)
                self.assertEqual(
                    request["development_seed"],
                    INTEGRATION_CASES[case_id]["development_seed"],
                )
                self.assertEqual(
                    request["mechanism_binding"]["runtime_variant"],
                    request["runtime_variant"],
                )
                self.assertEqual(request["event_instance"], plan["event_instance"])
                self.assertEqual(request["factor_context"], plan["factor_context"])
                self.assertTrue(request["single_case_runtime_authorization_validated"])
                self.assertTrue(request["development_validation_only"])
                self.assertNotIn("campaign_seed", request)
                self.assertTrue(
                    request["evidence_directory"].startswith(
                        "results/wp9/development/r065/integration/"
                    )
                )
                self.assertNotIn(
                    "results/wp9/campaign", request["evidence_directory"]
                )
                self.assertFalse(request["runtime_execution_performed"])
                self.assertFalse(request["campaign_seed_consumed"])
                self.assertFalse(request["campaign_data_generated"])
                self.assertFalse(request["final_campaign_execution_authorized"])

    def test_execution_request_requires_exact_granted_runtime_authorization(self):
        plan = _plan("Z01")
        with self.assertRaisesRegex(PermissionError, "not granted"):
            build_execution_request(
                plan=plan,
                authorization=_authorization(plan, granted=False),
                current_repo_sha=REPO_SHA,
            )

        bad_sha = _authorization(plan)
        with self.assertRaisesRegex(ValueError, "current repository"):
            build_execution_request(
                plan=plan,
                authorization=bad_sha,
                current_repo_sha="b" * 40,
            )

    def test_request_validation_fails_closed_on_identity_or_namespace_mutation(self):
        request = _request("Z08")
        mutations = {
            "development_seed": 9949,
            "cell_id": "A18",
            "runtime_variant": "e3_trusted_recovery_contact_delay",
            "driver_invocation_limit": 2,
            "automatic_retry_allowed": True,
            "automatic_next_case_allowed": True,
            "final_campaign_execution_authorized": True,
        }
        for key, value in mutations.items():
            bad = copy.deepcopy(request)
            bad[key] = value
            with self.subTest(key=key):
                with self.assertRaises(ValueError):
                    validate_execution_request(bad)

        bad = copy.deepcopy(request)
        bad["evidence_directory"] = "results/wp9/campaign/seed-10001/A17/run"
        with self.assertRaisesRegex(ValueError, "development evidence namespace"):
            validate_execution_request(bad)

    def test_driver_is_invoked_exactly_once_and_never_advances(self):
        request = _request("Z04")
        calls = []

        def driver(value: dict) -> dict:
            calls.append(copy.deepcopy(value))
            return _driver_result(value)

        result = execute_request(request=request, driver=driver)

        self.assertEqual(len(calls), 1)
        self.assertEqual(result["driver_invocation_count"], 1)
        self.assertTrue(result["runtime_execution_performed"])
        self.assertFalse(result["automatic_retry_performed"])
        self.assertFalse(result["automatic_next_case_performed"])
        self.assertFalse(result["campaign_seed_consumed"])
        self.assertFalse(result["campaign_data_generated"])
        self.assertFalse(result["final_campaign_execution_authorized"])

    def test_driver_result_identity_and_campaign_boundaries_are_fail_closed(self):
        request = _request("Z03")
        bad_results = (
            {"case_id": "Z02"},
            {"development_seed": 9942},
            {"runtime_variant": "e2_replay_effect"},
            {"campaign_seed_consumed": True},
            {"campaign_data_generated": True},
            {"final_campaign_execution_authorized": True},
            {"automatic_retry_performed": True},
            {"automatic_next_case_performed": True},
        )
        for mutation in bad_results:
            with self.subTest(mutation=mutation):
                def driver(value: dict, mutation=mutation) -> dict:
                    return _driver_result(value, **mutation)

                with self.assertRaises(ValueError):
                    execute_request(request=request, driver=driver)

    def test_unexpected_outcome_is_retained_without_retry(self):
        request = _request("Z05")
        calls = []

        def driver(value: dict) -> dict:
            calls.append(value["run_id"])
            return _driver_result(
                value,
                outcome_matches_predeclared_expectation=False,
                scientific_outcome="unexpected_but_valid",
            )

        result = execute_request(request=request, driver=driver)

        self.assertEqual(calls, [request["run_id"]])
        self.assertFalse(
            result["driver_result"]["outcome_matches_predeclared_expectation"]
        )
        self.assertEqual(
            result["driver_result"]["scientific_outcome"],
            "unexpected_but_valid",
        )
        self.assertTrue(result["unexpected_scientific_outcome_retained"])
        self.assertFalse(result["automatic_retry_performed"])
        self.assertFalse(result["automatic_next_case_performed"])

    def test_treatment_fidelity_failure_is_retained_without_hidden_rerun(self):
        request = _request("Z06")
        calls = []

        def driver(value: dict) -> dict:
            calls.append(value["case_id"])
            return _driver_result(
                value,
                treatment_fidelity_valid=False,
                runtime_execution_performed=True,
                invalid_attempt_retained=True,
            )

        result = execute_request(request=request, driver=driver)

        self.assertEqual(calls, ["Z06"])
        self.assertFalse(result["driver_result"]["treatment_fidelity_valid"])
        self.assertTrue(result["driver_result"]["invalid_attempt_retained"])
        self.assertTrue(result["treatment_fidelity_failure_retained"])
        self.assertFalse(result["automatic_retry_performed"])
        self.assertFalse(result["automatic_next_case_performed"])

    def test_static_executor_contains_no_runtime_process_or_docker_invocation(self):
        path = (
            ROOT
            / "src"
            / "mission_recovery"
            / "wp9_r065_production_integration_executor.py"
        )
        source = path.read_text(encoding="utf-8")
        self.assertNotIn("subprocess", source)
        self.assertNotIn("os.system", source)
        self.assertNotIn("docker run", source)
        self.assertNotIn("docker compose", source)
        self.assertNotIn("results/wp9/campaign/", source)


if __name__ == "__main__":
    unittest.main()
