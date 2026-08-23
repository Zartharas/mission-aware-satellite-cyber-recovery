from __future__ import annotations

import unittest

from src.mission_recovery.wp9_r065_bounded_runtime_integration import (
    AUTHORIZATION_CLASSIFICATION,
    build_authorization_request,
    build_integration_plan,
)
from src.mission_recovery.wp9_r065_production_integration_executor import (
    build_execution_request,
    execute_request,
)

REPO_SHA = "a" * 40


def _request() -> dict:
    plan = build_integration_plan(
        case_id="Z01",
        run_id="r065-integration-return-propagation",
        repo_commit=REPO_SHA,
    )
    authorization = build_authorization_request(plan)
    authorization["classification"] = AUTHORIZATION_CLASSIFICATION
    authorization["development_runtime_authorized"] = True
    return build_execution_request(
        plan=plan,
        authorization=authorization,
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
        "unexpected_scientific_outcome_retained": False,
        "campaign_seed_consumed": False,
        "campaign_data_generated": False,
        "final_campaign_execution_authorized": False,
        "automatic_retry_performed": False,
        "automatic_next_case_performed": False,
    }
    result.update(overrides)
    return result


class WP9R065IntegrationReturnPropagationTests(unittest.TestCase):
    def test_expected_valid_outcome_is_not_mislabeled_unexpected_or_fidelity_failure(self):
        request = _request()
        result = execute_request(
            request=request,
            driver=lambda value: _driver_result(value),
        )

        self.assertTrue(result["driver_result"]["outcome_matches_predeclared_expectation"])
        self.assertFalse(result["driver_result"]["unexpected_scientific_outcome_retained"])
        self.assertTrue(result["driver_result"]["treatment_fidelity_valid"])
        self.assertFalse(result["unexpected_scientific_outcome_retained"])
        self.assertFalse(result["treatment_fidelity_failure_retained"])

    def test_unexpected_valid_outcome_propagates_as_retained(self):
        request = _request()
        result = execute_request(
            request=request,
            driver=lambda value: _driver_result(
                value,
                outcome_matches_predeclared_expectation=False,
                unexpected_scientific_outcome_retained=True,
            ),
        )

        self.assertTrue(result["unexpected_scientific_outcome_retained"])
        self.assertFalse(result["treatment_fidelity_failure_retained"])

    def test_retained_fidelity_failure_propagates_without_becoming_unexpected_outcome(self):
        request = _request()
        result = execute_request(
            request=request,
            driver=lambda value: _driver_result(
                value,
                treatment_fidelity_valid=False,
                invalid_attempt_retained=True,
            ),
        )

        self.assertFalse(result["unexpected_scientific_outcome_retained"])
        self.assertTrue(result["treatment_fidelity_failure_retained"])
        self.assertFalse(result["automatic_retry_performed"])
        self.assertFalse(result["automatic_next_case_performed"])


if __name__ == "__main__":
    unittest.main()
