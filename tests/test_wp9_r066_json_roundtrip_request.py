from __future__ import annotations

import json
import unittest
from unittest.mock import Mock

from src.mission_recovery.wp9_campaign_trial_controller import build_trial_plan
from src.mission_recovery.wp9_final_campaign_bridge import (
    AUTHORIZATION_CLASSIFICATION,
    build_authorization_request,
)
from src.mission_recovery.wp9_r066_final_campaign_runtime_binding import (
    build_campaign_runtime_request,
    execute_campaign_runtime_request,
)

REPO_SHA = "a" * 40


class WP9R066JsonRoundTripRequestTests(unittest.TestCase):
    def test_campaign_request_survives_json_round_trip_before_execution(self) -> None:
        plan = build_trial_plan(
            campaign_seed=10001,
            cell_id="A19",
            run_id="r066-json-roundtrip-a19",
            repo_commit=REPO_SHA,
        )
        authorization = build_authorization_request(plan)
        authorization["classification"] = AUTHORIZATION_CLASSIFICATION
        authorization["single_trial_runtime_authorized"] = True

        request = build_campaign_runtime_request(
            plan=plan,
            authorization=authorization,
            attempt_history=[],
            current_repo_sha=REPO_SHA,
        )

        persisted_request = json.loads(json.dumps(request))

        environment = {
            "WP9_R066_FINAL_CAMPAIGN_RUNTIME_AUTHORIZED": "1",
            "WP9_R066_AUTHORIZED_RUN_ID": request["run_id"],
            "WP9_R066_AUTHORIZED_SEED": str(request["campaign_seed"]),
            "WP9_R066_AUTHORIZED_CELL": request["cell_id"],
            "WP9_R066_AUTHORIZED_REPO_SHA": REPO_SHA,
        }
        runner_result = {
            "run_id": request["run_id"],
            "campaign_seed": request["campaign_seed"],
            "cell_id": request["cell_id"],
            "attempt_status": "VALID",
            "runtime_execution_performed": True,
            "campaign_seed_consumed": True,
            "campaign_data_generated": True,
            "automatic_retry_performed": False,
            "automatic_next_case_performed": False,
        }
        runner = Mock(return_value=runner_result)

        result = execute_campaign_runtime_request(
            request=persisted_request,
            runner=runner,
            authorization_environment=environment,
        )

        runner.assert_called_once()
        self.assertEqual(result["run_id"], request["run_id"])
        self.assertEqual(result["campaign_seed"], 10001)
        self.assertEqual(result["cell_id"], "A19")
        self.assertFalse(result["automatic_retry_performed"])
        self.assertFalse(result["automatic_next_case_performed"])


if __name__ == "__main__":
    unittest.main()
