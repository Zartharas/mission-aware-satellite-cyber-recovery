from __future__ import annotations

import copy
import unittest
from pathlib import Path
from unittest.mock import Mock

from src.mission_recovery.wp9_campaign_trial_controller import build_trial_plan
from src.mission_recovery.wp9_final_campaign_bridge import (
    AUTHORIZATION_CLASSIFICATION,
    build_authorization_request,
)
from src.mission_recovery.wp9_r066_final_campaign_runtime_binding import (
    CELL_HARNESS_BINDINGS,
    build_campaign_runtime_request,
    build_compatibility_plan,
    execute_campaign_runtime_request,
    source_harness_blob_sha,
    validate_static_campaign_runtime_binding,
)

ROOT = Path(__file__).resolve().parents[1]
REPO_SHA = "a" * 40


def _plan(cell_id: str, seed: int = 10001, run_id: str | None = None) -> dict:
    return build_trial_plan(
        campaign_seed=seed,
        cell_id=cell_id,
        run_id=run_id or f"r066-{cell_id.lower()}-{seed}",
        repo_commit=REPO_SHA,
    )


def _granted(plan: dict) -> dict:
    auth = build_authorization_request(plan)
    auth["classification"] = AUTHORIZATION_CLASSIFICATION
    auth["single_trial_runtime_authorized"] = True
    return auth


class WP9R066FinalCampaignRuntimeBindingTests(unittest.TestCase):
    def test_static_binding_covers_every_frozen_cell_exactly_once(self) -> None:
        result = validate_static_campaign_runtime_binding()
        self.assertEqual(result["campaign_cell_count"], 24)
        self.assertEqual(result["source_harness_count"], 4)
        self.assertEqual(result["runtime_variant_count"], 8)
        self.assertTrue(result["production_runtime_executor_bound"])
        self.assertTrue(result["source_harness_blob_identity_enforced"])
        self.assertTrue(result["campaign_seed_passthrough_enforced"])
        self.assertTrue(result["campaign_evidence_namespace_enforced"])
        self.assertTrue(result["attempt_history_guard_required"])
        self.assertTrue(result["one_trial_per_invocation"])
        self.assertFalse(result["automatic_retry_allowed"])
        self.assertFalse(result["automatic_next_case_allowed"])
        self.assertFalse(result["runtime_execution_performed"])
        self.assertFalse(result["campaign_seed_consumed"])
        self.assertFalse(result["campaign_data_generated"])
        self.assertFalse(result["campaign_runtime_authorized"])

        self.assertEqual(
            set(CELL_HARNESS_BINDINGS),
            {f"A{i:02d}" for i in range(1, 25)},
        )

    def test_source_harnesses_are_exact_runtime_validated_blobs(self) -> None:
        expected = {
            "scripts/run_wp9_r061_e1_route_validation.sh": (
                "5a4596cfbe5941dbaeb833c802d68258343e7f9a"
            ),
            "scripts/run_wp9_r057_e2_route_validation.sh": (
                "4530cde131dd5a27454411d9e39f99e36c58b211"
            ),
            "scripts/run_wp9_r063_e3_route_validation.sh": (
                "76193d768ee48bfc5748f5fc6c12675d8057456e"
            ),
            "scripts/run_wp9_r059_e4_route_validation.sh": (
                "c51e254e1d00f6b59dbd33f6130eda8ff506bae1"
            ),
        }
        for path, blob in expected.items():
            with self.subTest(path=path):
                self.assertEqual(source_harness_blob_sha(ROOT / path), blob)

    def test_every_binding_uses_same_effective_treatment_class_as_source_alias(self) -> None:
        result = validate_static_campaign_runtime_binding()
        self.assertTrue(result["source_alias_treatment_equivalence_validated"])
        for cell_id, binding in CELL_HARNESS_BINDINGS.items():
            with self.subTest(cell_id=cell_id):
                self.assertIn(binding["source_case"], binding["source_supported_cases"])
                self.assertEqual(binding["event_id"], _plan(cell_id)["factor_context"]["event_id"])

    def test_compatibility_plan_uses_campaign_seed_and_campaign_cell(self) -> None:
        samples = (
            ("A01", 10001),
            ("A04", 10002),
            ("A19", 10003),
            ("A10", 10004),
            ("A14", 10005),
            ("A17", 10006),
            ("A18", 10007),
            ("A22", 10008),
            ("A24", 10009),
        )
        for cell_id, seed in samples:
            with self.subTest(cell_id=cell_id, seed=seed):
                plan = _plan(cell_id, seed)
                compat = build_compatibility_plan(plan=plan)
                self.assertEqual(compat["cell_id"], cell_id)
                self.assertEqual(compat["campaign_seed"], seed)
                self.assertEqual(compat["development_seed"], seed)
                self.assertEqual(compat["factor_context"]["seed"], seed)
                self.assertEqual(compat["factor_context"], plan["factor_context"])
                self.assertEqual(compat["runtime_family"], plan["runtime_family"])
                self.assertEqual(compat["runtime_variant"], plan["runtime_variant"])
                self.assertEqual(
                    compat["runtime_policy_decision"]["delegated_policy_id"],
                    plan["expected_effective_policy_id_for_acceptance_only"],
                )
                self.assertFalse(
                    compat["runtime_policy_decision"]["oracle_ground_truth_read"]
                )
                self.assertTrue(compat["campaign_runtime_compatibility_plan"])
                self.assertFalse(compat["campaign_seed_consumed"])
                self.assertFalse(compat["campaign_data_generated"])

    def test_request_requires_exact_attempt_guard_and_campaign_namespace(self) -> None:
        plan = _plan("A19", 10001, "r066-first")
        request = build_campaign_runtime_request(
            plan=plan,
            authorization=_granted(plan),
            attempt_history=[],
            current_repo_sha=REPO_SHA,
        )
        self.assertEqual(request["global_order_index"], 1)
        self.assertEqual(request["campaign_seed"], 10001)
        self.assertEqual(request["cell_id"], "A19")
        self.assertEqual(
            request["evidence_directory"],
            "results/wp9/campaign/seed-10001/A19/r066-first",
        )
        self.assertTrue(request["attempt_history_validated"])
        self.assertTrue(request["source_harness_blob_identity_validated"])
        self.assertFalse(request["automatic_retry_allowed"])
        self.assertFalse(request["automatic_next_case_allowed"])
        self.assertFalse(request["runtime_execution_performed"])
        self.assertFalse(request["campaign_seed_consumed"])
        self.assertFalse(request["campaign_data_generated"])

    def test_out_of_order_campaign_request_is_rejected(self) -> None:
        plan = _plan("A13", 10001, "r066-wrong-first")
        with self.assertRaisesRegex(ValueError, "next frozen trial"):
            build_campaign_runtime_request(
                plan=plan,
                authorization=_granted(plan),
                attempt_history=[],
                current_repo_sha=REPO_SHA,
            )

    def test_runtime_fails_closed_before_runner_without_exact_environment_authorization(self) -> None:
        plan = _plan("A19", 10001, "r066-blocked")
        request = build_campaign_runtime_request(
            plan=plan,
            authorization=_granted(plan),
            attempt_history=[],
            current_repo_sha=REPO_SHA,
        )
        runner = Mock()
        with self.assertRaisesRegex(PermissionError, "campaign runtime authorization"):
            execute_campaign_runtime_request(
                request=request,
                runner=runner,
                authorization_environment={},
            )
        runner.assert_not_called()

    def test_authorization_environment_is_run_seed_cell_and_sha_scoped(self) -> None:
        plan = _plan("A19", 10001, "r066-scoped")
        request = build_campaign_runtime_request(
            plan=plan,
            authorization=_granted(plan),
            attempt_history=[],
            current_repo_sha=REPO_SHA,
        )
        good = {
            "WP9_R066_FINAL_CAMPAIGN_RUNTIME_AUTHORIZED": "1",
            "WP9_R066_AUTHORIZED_RUN_ID": request["run_id"],
            "WP9_R066_AUTHORIZED_SEED": str(request["campaign_seed"]),
            "WP9_R066_AUTHORIZED_CELL": request["cell_id"],
            "WP9_R066_AUTHORIZED_REPO_SHA": REPO_SHA,
        }
        for key in tuple(good):
            bad = copy.deepcopy(good)
            bad[key] = "wrong"
            with self.subTest(key=key):
                runner = Mock()
                with self.assertRaises((PermissionError, ValueError)):
                    execute_campaign_runtime_request(
                        request=request,
                        runner=runner,
                        authorization_environment=bad,
                    )
                runner.assert_not_called()

    def test_static_binding_does_not_mutate_campaign_or_invoke_runtime(self) -> None:
        before = list((ROOT / "results" / "wp9" / "campaign").rglob("*")) if (
            ROOT / "results" / "wp9" / "campaign"
        ).exists() else []
        validate_static_campaign_runtime_binding()
        after = list((ROOT / "results" / "wp9" / "campaign").rglob("*")) if (
            ROOT / "results" / "wp9" / "campaign"
        ).exists() else []
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
