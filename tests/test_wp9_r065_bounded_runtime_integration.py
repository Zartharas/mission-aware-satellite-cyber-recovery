from __future__ import annotations

import copy
import unittest
from pathlib import Path

from src.mission_recovery.wp9_r065_bounded_runtime_integration import (
    AUTHORIZATION_CLASSIFICATION,
    INTEGRATION_CASES,
    build_authorization_request,
    build_executor_descriptor,
    build_integration_plan,
    execution_preflight,
    integration_case,
    validate_static_integration,
    validate_runtime_authorization,
)


REPO_SHA = "a" * 40
ROOT = Path(__file__).resolve().parents[1]


def _plan(case_id: str, run_id: str | None = None) -> dict:
    return build_integration_plan(
        case_id=case_id,
        run_id=run_id or f"r065-{case_id.lower()}",
        repo_commit=REPO_SHA,
    )


def _granted(plan: dict) -> dict:
    request = build_authorization_request(plan)
    authorization = copy.deepcopy(request)
    authorization["classification"] = AUTHORIZATION_CLASSIFICATION
    authorization["development_runtime_authorized"] = True
    return authorization


class WP9R065BoundedRuntimeIntegrationTests(unittest.TestCase):
    def test_static_design_is_minimal_and_runtime_blocked(self):
        result = validate_static_integration()

        self.assertEqual(result["decision_id"], "R-065")
        self.assertEqual(result["integration_case_count"], 9)
        self.assertEqual(result["runtime_variant_count"], 8)
        self.assertEqual(result["integration_signature_count"], 9)
        self.assertEqual(result["event_family_count"], 4)
        self.assertTrue(result["minimal_representative_set"])
        self.assertTrue(result["r064_static_bridge_required"])
        self.assertFalse(result["production_runtime_executor_bound"])
        self.assertFalse(result["development_runtime_execution_authorized"])
        self.assertFalse(result["runtime_execution_performed"])
        self.assertFalse(result["campaign_seed_consumed"])
        self.assertFalse(result["campaign_data_generated"])
        self.assertFalse(result["final_campaign_execution_authorized"])
        self.assertFalse(result["automatic_retry_allowed"])
        self.assertFalse(result["automatic_next_case_allowed"])

    def test_cases_cover_eight_variants_plus_distinct_p6_c0_c1_branch(self):
        self.assertEqual(set(INTEGRATION_CASES), {f"Z{i:02d}" for i in range(1, 10)})
        self.assertEqual(
            [INTEGRATION_CASES[f"Z{i:02d}"]["development_seed"] for i in range(1, 10)],
            list(range(9941, 9950)),
        )

        plans = [_plan(f"Z{i:02d}") for i in range(1, 10)]
        variants = {row["runtime_variant"] for row in plans}
        signatures = {row["integration_signature"] for row in plans}
        families = {row["event_id"] for row in plans}

        self.assertEqual(len(variants), 8)
        self.assertEqual(len(signatures), 9)
        self.assertEqual(families, {"E1", "E2", "E3", "E4"})
        self.assertIn("e3_ground_authorized_recovery:C0", signatures)
        self.assertIn("e3_ground_authorized_recovery:C1", signatures)

    def test_case_selection_is_frozen_to_non_campaign_development_seeds(self):
        expected = {
            "Z01": ("A06", 9941, "E1", "e1_command_gateway"),
            "Z02": ("A21", 9942, "E2", "e2_replay_effect"),
            "Z03": ("A24", 9943, "E4", "e4_observability"),
            "Z04": ("A13", 9944, "E3", "e3_command_gateway"),
            "Z05": ("A11", 9945, "E3", "e3_trusted_recovery"),
            "Z06": ("A15", 9946, "E3", "e3_trusted_recovery_reduced_evidence"),
            "Z07": ("A16", 9947, "E3", "e3_ground_authorized_recovery"),
            "Z08": ("A17", 9948, "E3", "e3_ground_authorized_recovery"),
            "Z09": ("A18", 9949, "E3", "e3_trusted_recovery_contact_delay"),
        }

        for case_id, (cell_id, seed, event_id, variant) in expected.items():
            case = integration_case(case_id)
            plan = _plan(case_id)
            self.assertEqual(case["cell_id"], cell_id)
            self.assertEqual(case["development_seed"], seed)
            self.assertEqual(plan["cell_id"], cell_id)
            self.assertEqual(plan["development_seed"], seed)
            self.assertEqual(plan["event_id"], event_id)
            self.assertEqual(plan["runtime_variant"], variant)
            self.assertNotIn("campaign_seed", plan)
            self.assertFalse(plan["campaign_seed_consumed"])
            self.assertFalse(plan["campaign_data_generated"])

    def test_plan_preserves_frozen_cell_semantics_with_development_seed(self):
        for case_id in INTEGRATION_CASES:
            plan = _plan(case_id)
            factor = plan["factor_context"]
            self.assertEqual(factor["seed"], plan["development_seed"])
            self.assertEqual(factor["event_id"], plan["event_id"])
            self.assertEqual(
                plan["actual_effective_policy_id"],
                plan["expected_effective_policy_id_for_acceptance_only"],
            )
            self.assertFalse(plan["oracle_ground_truth_read"])
            self.assertEqual(
                plan["expected_values_role"],
                "post_observation_acceptance_only_not_metric_inputs",
            )
            self.assertTrue(plan["development_validation_only"])
            self.assertFalse(plan["development_runtime_execution_authorized"])
            self.assertFalse(plan["final_campaign_execution_authorized"])

    def test_p6_c0_c1_and_a18_autonomous_timing_remain_distinct(self):
        z07 = _plan("Z07")
        z08 = _plan("Z08")
        z09 = _plan("Z09")

        self.assertEqual(z07["cell_id"], "A16")
        self.assertEqual(z07["contact_condition_id"], "C0")
        self.assertEqual(z07["p6_authorization_release_after_event_s"], 0)

        self.assertEqual(z08["cell_id"], "A17")
        self.assertEqual(z08["contact_condition_id"], "C1")
        self.assertEqual(z08["modeled_c1_contact_window_s"], 10)
        self.assertEqual(z08["p6_authorization_release_after_event_s"], 10)

        self.assertEqual(z09["cell_id"], "A18")
        self.assertEqual(z09["contact_condition_id"], "C1")
        self.assertEqual(z09["modeled_c1_contact_window_s"], 10)
        self.assertIsNone(z09["p6_authorization_release_after_event_s"])
        self.assertFalse(z09["ground_authorization_wait_required"])

    def test_authorization_request_is_fail_closed_and_exact(self):
        plan = _plan("Z01", "r065-auth")
        request = build_authorization_request(plan)

        self.assertEqual(request["decision_id"], "R-065")
        self.assertEqual(request["authorization_scope"], "single_development_integration_case")
        self.assertEqual(request["case_id"], "Z01")
        self.assertEqual(request["development_seed"], 9941)
        self.assertEqual(request["authorized_repo_sha"], REPO_SHA)
        self.assertFalse(request["development_runtime_authorized"])
        self.assertFalse(request["campaign_runtime_authorized"])
        self.assertFalse(request["automatic_retry_allowed"])
        self.assertFalse(request["automatic_next_case_allowed"])

        with self.assertRaisesRegex(ValueError, "classification"):
            validate_runtime_authorization(
                plan=plan,
                authorization=request,
                current_repo_sha=REPO_SHA,
            )

        ungranted = copy.deepcopy(request)
        ungranted["classification"] = AUTHORIZATION_CLASSIFICATION
        with self.assertRaisesRegex(PermissionError, "not granted"):
            validate_runtime_authorization(
                plan=plan,
                authorization=ungranted,
                current_repo_sha=REPO_SHA,
            )

    def test_granted_static_authorization_binds_exact_case_seed_plan_and_repo(self):
        plan = _plan("Z02", "r065-exact")
        authorization = _granted(plan)

        validated = validate_runtime_authorization(
            plan=plan,
            authorization=authorization,
            current_repo_sha=REPO_SHA,
        )
        self.assertEqual(validated["case_id"], "Z02")

        mutations = {
            "case_id": "Z03",
            "development_seed": 9943,
            "authorized_repo_sha": "b" * 40,
            "plan_sha256": "0" * 64,
            "automatic_retry_allowed": True,
            "automatic_next_case_allowed": True,
            "campaign_runtime_authorized": True,
        }
        for key, value in mutations.items():
            bad = copy.deepcopy(authorization)
            bad[key] = value
            with self.subTest(key=key):
                with self.assertRaises((ValueError, PermissionError)):
                    validate_runtime_authorization(
                        plan=plan,
                        authorization=bad,
                        current_repo_sha=REPO_SHA,
                    )

    def test_executor_descriptor_is_development_only_and_never_campaign_namespace(self):
        plan = _plan("Z09", "r065-z09-descriptor")
        descriptor = build_executor_descriptor(
            plan=plan,
            authorization=_granted(plan),
            current_repo_sha=REPO_SHA,
        )

        self.assertEqual(descriptor["case_id"], "Z09")
        self.assertEqual(descriptor["development_seed"], 9949)
        self.assertTrue(
            descriptor["evidence_directory"].startswith(
                "results/wp9/development/r065/integration/"
            )
        )
        self.assertNotIn("results/wp9/campaign", descriptor["evidence_directory"])
        self.assertFalse(descriptor["runtime_execution_performed"])
        self.assertFalse(descriptor["campaign_seed_consumed"])
        self.assertFalse(descriptor["campaign_data_generated"])
        self.assertFalse(descriptor["final_campaign_execution_authorized"])

    def test_execution_preflight_remains_blocked_during_static_tdd_preparation(self):
        plan = _plan("Z01", "r065-blocked")
        descriptor = build_executor_descriptor(
            plan=plan,
            authorization=_granted(plan),
            current_repo_sha=REPO_SHA,
        )

        with self.assertRaisesRegex(PermissionError, "separate runtime authorization"):
            execution_preflight(descriptor=descriptor)

    def test_shell_entry_point_is_static_only(self):
        script_path = ROOT / "scripts" / "run_wp9_r065_bounded_runtime_integration.sh"
        script = script_path.read_text(encoding="utf-8")

        self.assertIn("validate-static", script)
        self.assertIn("plan-case", script)
        self.assertIn("authorization-request", script)
        self.assertIn("execute-case", script)
        self.assertIn("execution remains blocked", script)
        self.assertNotIn("docker run", script)
        self.assertNotIn("docker compose", script)
        self.assertNotIn("results/wp9/campaign", script)


if __name__ == "__main__":
    unittest.main()
