from __future__ import annotations

import copy
import unittest
from pathlib import Path

from src.mission_recovery.wp9_campaign_trial_controller import build_trial_plan
from src.mission_recovery.wp9_final_campaign_bridge import (
    build_authorization_request,
    build_execution_descriptor,
    frozen_campaign_sequence,
    next_required_trial,
    route_trial_plan,
    run_authorized_trial,
    validate_static_bridge,
    validate_trial_authorization,
)


REPO_SHA = "a" * 40
ROOT = Path(__file__).resolve().parents[1]


def _plan(seed: int, cell_id: str, run_id: str) -> dict:
    return build_trial_plan(
        campaign_seed=seed,
        cell_id=cell_id,
        run_id=run_id,
        repo_commit=REPO_SHA,
    )


def _granted_authorization(plan: dict) -> dict:
    request = build_authorization_request(plan)
    granted = copy.deepcopy(request)
    granted["classification"] = (
        "WP9_R064_FINAL_CAMPAIGN_SINGLE_TRIAL_AUTHORIZATION"
    )
    granted["single_trial_runtime_authorized"] = True
    return granted


class WP9R064FinalCampaignBridgeTests(unittest.TestCase):
    def test_static_bridge_covers_all_routes_without_authorizing_runtime(self):
        result = validate_static_bridge()

        self.assertEqual(result["decision_id"], "R-064")
        self.assertEqual(result["campaign_cell_count"], 24)
        self.assertEqual(result["campaign_seed_block_count"], 30)
        self.assertEqual(result["planned_valid_executions"], 720)
        self.assertEqual(result["campaign_route_family_count"], 4)
        self.assertEqual(result["campaign_runtime_variant_count"], 8)
        self.assertTrue(result["campaign_observation_adapters_ready"])
        self.assertTrue(result["validated_runtime_mechanism_evidence_present"])
        self.assertTrue(result["authorization_contract_present"])
        self.assertTrue(result["one_trial_per_invocation"])
        self.assertFalse(result["automatic_retry_allowed"])
        self.assertFalse(result["automatic_next_case_allowed"])
        self.assertFalse(result["runtime_execution_performed"])
        self.assertFalse(result["campaign_seed_consumed"])
        self.assertFalse(result["campaign_data_generated"])
        self.assertFalse(result["final_campaign_execution_authorized"])

    def test_all_24_frozen_cells_route_through_campaign_observation_adapters(self):
        expected_family = {
            **{f"A{i:02d}": "E1" for i in range(1, 10)},
            **{f"A{i:02d}": "E3" for i in range(10, 19)},
            **{f"A{i:02d}": "E2" for i in range(19, 22)},
            **{f"A{i:02d}": "E4" for i in range(22, 25)},
        }
        expected_observation_decision = {
            "E1": "R-060",
            "E2": "R-056",
            "E3": "R-062",
            "E4": "R-058",
        }
        expected_runtime_validation = {
            "E1": "R-061",
            "E2": "R-057",
            "E3": "R-063",
            "E4": "R-059",
        }

        observed = set()
        for cell_id, event_id in expected_family.items():
            plan = _plan(10001, cell_id, f"r064-{cell_id.lower()}")
            route = route_trial_plan(plan)

            self.assertEqual(route["cell_id"], cell_id)
            self.assertEqual(route["event_id"], event_id)
            self.assertEqual(
                route["campaign_observation_adapter_decision_id"],
                expected_observation_decision[event_id],
            )
            self.assertEqual(
                route["development_runtime_validation_decision_id"],
                expected_runtime_validation[event_id],
            )
            self.assertFalse(route["runtime_execution_performed"])
            observed.add(cell_id)

        self.assertEqual(observed, set(expected_family))

    def test_frozen_sequence_is_exact_720_trial_prefix_order(self):
        sequence = frozen_campaign_sequence()

        self.assertEqual(len(sequence), 720)
        self.assertEqual(len({row["global_order_index"] for row in sequence}), 720)
        self.assertEqual(
            sequence[0],
            {
                "global_order_index": 1,
                "block_index": 1,
                "campaign_seed": 10001,
                "cell_order_index": 1,
                "cell_id": "A19",
            },
        )
        self.assertEqual(sequence[23]["campaign_seed"], 10001)
        self.assertEqual(sequence[23]["cell_order_index"], 24)
        self.assertEqual(sequence[23]["cell_id"], "A17")
        self.assertEqual(sequence[24]["campaign_seed"], 10002)
        self.assertEqual(sequence[24]["cell_order_index"], 1)
        self.assertEqual(sequence[24]["cell_id"], "A05")
        self.assertEqual(sequence[-1]["campaign_seed"], 10030)
        self.assertEqual(sequence[-1]["cell_order_index"], 24)
        self.assertEqual(sequence[-1]["cell_id"], "A23")

    def test_next_required_trial_requires_exact_valid_prefix(self):
        sequence = frozen_campaign_sequence()

        self.assertEqual(next_required_trial([]), sequence[0])
        self.assertEqual(next_required_trial(sequence[:7]), sequence[7])
        self.assertIsNone(next_required_trial(sequence))

        with self.assertRaisesRegex(ValueError, "exact frozen prefix"):
            next_required_trial([sequence[1]])

        duplicate = [sequence[0], sequence[0]]
        with self.assertRaisesRegex(ValueError, "exact frozen prefix"):
            next_required_trial(duplicate)

        gap = [sequence[0], sequence[2]]
        with self.assertRaisesRegex(ValueError, "exact frozen prefix"):
            next_required_trial(gap)

    def test_authorization_request_is_fail_closed(self):
        plan = _plan(10001, "A19", "r064-auth-request")
        request = build_authorization_request(plan)

        self.assertEqual(request["decision_id"], "R-064")
        self.assertEqual(
            request["classification"],
            "WP9_R064_FINAL_CAMPAIGN_SINGLE_TRIAL_AUTHORIZATION_REQUEST",
        )
        self.assertEqual(request["authorization_scope"], "single_frozen_trial")
        self.assertEqual(request["authorized_repo_sha"], REPO_SHA)
        self.assertEqual(request["campaign_seed"], 10001)
        self.assertEqual(request["cell_id"], "A19")
        self.assertEqual(request["cell_order_index"], 1)
        self.assertFalse(request["single_trial_runtime_authorized"])
        self.assertFalse(request["campaign_wide_execution_authorized"])
        self.assertFalse(request["automatic_retry_allowed"])
        self.assertFalse(request["automatic_next_case_allowed"])

        with self.assertRaisesRegex(ValueError, "classification"):
            validate_trial_authorization(
                plan=plan,
                authorization=request,
                current_repo_sha=REPO_SHA,
            )

        ungranted = copy.deepcopy(request)
        ungranted["classification"] = (
            "WP9_R064_FINAL_CAMPAIGN_SINGLE_TRIAL_AUTHORIZATION"
        )
        with self.assertRaisesRegex(PermissionError, "not granted"):
            validate_trial_authorization(
                plan=plan,
                authorization=ungranted,
                current_repo_sha=REPO_SHA,
            )

    def test_authorization_must_bind_exact_trial_and_repository(self):
        plan = _plan(10001, "A19", "r064-auth-exact")
        authorization = _granted_authorization(plan)

        validated = validate_trial_authorization(
            plan=plan,
            authorization=authorization,
            current_repo_sha=REPO_SHA,
        )
        self.assertEqual(validated["cell_id"], "A19")

        bad_repo = copy.deepcopy(authorization)
        bad_repo["authorized_repo_sha"] = "b" * 40
        with self.assertRaisesRegex(ValueError, "repository SHA"):
            validate_trial_authorization(
                plan=plan,
                authorization=bad_repo,
                current_repo_sha=REPO_SHA,
            )

        bad_cell = copy.deepcopy(authorization)
        bad_cell["cell_id"] = "A20"
        with self.assertRaisesRegex(ValueError, "cell"):
            validate_trial_authorization(
                plan=plan,
                authorization=bad_cell,
                current_repo_sha=REPO_SHA,
            )

        bad_order = copy.deepcopy(authorization)
        bad_order["cell_order_index"] = 2
        with self.assertRaisesRegex(ValueError, "order"):
            validate_trial_authorization(
                plan=plan,
                authorization=bad_order,
                current_repo_sha=REPO_SHA,
            )

        bad_scope = copy.deepcopy(authorization)
        bad_scope["authorization_scope"] = "campaign_batch"
        with self.assertRaisesRegex(ValueError, "scope"):
            validate_trial_authorization(
                plan=plan,
                authorization=bad_scope,
                current_repo_sha=REPO_SHA,
            )

        bad_retry = copy.deepcopy(authorization)
        bad_retry["automatic_retry_allowed"] = True
        with self.assertRaisesRegex(ValueError, "automatic retry"):
            validate_trial_authorization(
                plan=plan,
                authorization=bad_retry,
                current_repo_sha=REPO_SHA,
            )

        bad_next = copy.deepcopy(authorization)
        bad_next["automatic_next_case_allowed"] = True
        with self.assertRaisesRegex(ValueError, "automatic next"):
            validate_trial_authorization(
                plan=plan,
                authorization=bad_next,
                current_repo_sha=REPO_SHA,
            )

    def test_execution_descriptor_requires_next_frozen_trial(self):
        sequence = frozen_campaign_sequence()
        first = sequence[0]
        plan = _plan(
            first["campaign_seed"],
            first["cell_id"],
            "r064-first-trial",
        )
        authorization = _granted_authorization(plan)

        descriptor = build_execution_descriptor(
            plan=plan,
            authorization=authorization,
            completed_valid_positions=[],
            current_repo_sha=REPO_SHA,
        )

        self.assertEqual(descriptor["global_order_index"], 1)
        self.assertEqual(descriptor["campaign_seed"], 10001)
        self.assertEqual(descriptor["cell_id"], "A19")
        self.assertEqual(
            descriptor["evidence_directory"],
            "results/wp9/campaign/seed-10001/A19/r064-first-trial",
        )
        self.assertFalse(descriptor["runtime_execution_performed"])
        self.assertFalse(descriptor["campaign_seed_consumed"])
        self.assertFalse(descriptor["campaign_data_generated"])

        wrong_plan = _plan(10001, "A13", "r064-wrong-first")
        wrong_auth = _granted_authorization(wrong_plan)
        with self.assertRaisesRegex(ValueError, "next frozen trial"):
            build_execution_descriptor(
                plan=wrong_plan,
                authorization=wrong_auth,
                completed_valid_positions=[],
                current_repo_sha=REPO_SHA,
            )

    def test_runner_invokes_exactly_one_injected_executor_and_never_advances(self):
        plan = _plan(10001, "A19", "r064-one-shot")
        authorization = _granted_authorization(plan)
        calls = []

        def fake_executor(descriptor: dict) -> dict:
            calls.append(copy.deepcopy(descriptor))
            return {
                "classification": "STATIC_TDD_FAKE_EXECUTOR_ONLY",
                "runtime_execution_performed": False,
                "campaign_seed_consumed": False,
                "campaign_data_generated": False,
            }

        result = run_authorized_trial(
            plan=plan,
            authorization=authorization,
            completed_valid_positions=[],
            current_repo_sha=REPO_SHA,
            executor=fake_executor,
        )

        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0]["cell_id"], "A19")
        self.assertFalse(result["automatic_retry_performed"])
        self.assertFalse(result["automatic_next_case_performed"])
        self.assertFalse(result["runtime_execution_performed"])
        self.assertFalse(result["campaign_seed_consumed"])
        self.assertFalse(result["campaign_data_generated"])

    def test_runner_does_not_retry_executor_failure(self):
        plan = _plan(10001, "A19", "r064-failure")
        authorization = _granted_authorization(plan)
        calls = []

        def failing_executor(descriptor: dict) -> dict:
            calls.append(descriptor["run_id"])
            raise RuntimeError("synthetic static/TDD failure")

        with self.assertRaisesRegex(RuntimeError, "synthetic static/TDD failure"):
            run_authorized_trial(
                plan=plan,
                authorization=authorization,
                completed_valid_positions=[],
                current_repo_sha=REPO_SHA,
                executor=failing_executor,
            )

        self.assertEqual(calls, ["r064-failure"])

    def test_a17_and_a18_keep_frozen_c1_semantics(self):
        a17 = _plan(10001, "A17", "r064-a17")
        a18 = _plan(10001, "A18", "r064-a18")

        self.assertEqual(
            a17["timing_contract"]["modeled_c1_contact_window_s"],
            10,
        )
        self.assertEqual(
            a17["timing_contract"][
                "p6_ground_authorization_release_after_event_s"
            ],
            10,
        )
        self.assertEqual(
            a18["timing_contract"]["modeled_c1_contact_window_s"],
            10,
        )
        self.assertIsNone(
            a18["timing_contract"][
                "p6_ground_authorization_release_after_event_s"
            ]
        )

    def test_shell_entry_point_is_static_only_and_has_no_docker_execution(self):
        script = (
            ROOT / "scripts" / "run_wp9_r064_final_campaign_trial.sh"
        ).read_text(encoding="utf-8")

        self.assertIn("validate-static", script)
        self.assertIn("authorization-request", script)
        self.assertIn("execution remains blocked", script)
        self.assertNotIn("docker run", script)
        self.assertNotIn("docker compose", script)
        self.assertNotIn("results/wp9/campaign", script)


if __name__ == "__main__":
    unittest.main()
