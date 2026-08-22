from __future__ import annotations

import unittest

from src.mission_recovery.wp9b3_readiness import (
    CELL_IDS,
    ENDPOINT_SOURCES,
    build_readiness_matrix,
    validate_readiness,
)
from src.mission_recovery.wp9_static_contracts import (
    build_static_matrix,
    build_wp9_run_schema,
)


class WP9B3ReadinessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = validate_readiness()
        cls.rows = {row["cell_id"]: row for row in cls.result["rows"]}

    def test_all_24_frozen_cells_are_present_once(self) -> None:
        self.assertEqual(self.result["cell_ids"], list(CELL_IDS))
        self.assertEqual(self.result["cell_count"], 24)
        self.assertEqual(set(self.rows), set(CELL_IDS))

    def test_runtime_family_counts_match_frozen_design(self) -> None:
        self.assertEqual(
            self.result["runtime_family_counts"],
            {"command": 9, "recovery": 9, "replay": 3, "observability": 3},
        )

    def test_every_cell_retains_static_effective_policy_identity(self) -> None:
        for row in self.result["rows"]:
            self.assertEqual(
                row["actual_effective_policy_id_static"],
                row["expected_effective_policy_id_for_acceptance_only"],
            )
            self.assertTrue(row["effective_policy_observation_required"])
            self.assertEqual(
                row["effective_policy_observation_source"],
                "retained_runtime_execution_metadata",
            )
            self.assertFalse(row["expected_effective_policy_used_as_metric_input"])

    def test_analysis_endpoints_have_observed_data_sources(self) -> None:
        self.assertTrue(
            self.result["all_analysis_endpoints_have_observed_data_sources"]
        )
        self.assertEqual(
            ENDPOINT_SOURCES["effective_policy_id"],
            "execution_metadata.effective_policy_id",
        )
        for endpoint in (
            "unauthorized_effect_completed",
            "time_to_containment_s",
            "time_to_verified_recovery_s",
            "evidence_completeness_ratio",
            "residual_unauthorized_state_count",
        ):
            self.assertIn(endpoint, ENDPOINT_SOURCES)

    def test_all_cells_are_wp9_run_schema_compatible(self) -> None:
        self.assertTrue(self.result["all_cells_wp9_run_schema_compatible"])
        schema = build_wp9_run_schema()
        self.assertIn("P6", schema["properties"]["policy_id"]["enum"])
        self.assertIn(
            "ground_authorization",
            schema["properties"]["raw_metric_evidence"]["properties"],
        )

    def test_p6_cells_preserve_contact_specific_authorization_semantics(self) -> None:
        static_rows = {
            row["cell_id"]: row for row in build_static_matrix()["rows"]
        }
        for cell_id, available, missed in (
            ("A16", True, 0),
            ("A17", False, 1),
        ):
            contract = static_rows[cell_id]["p6_handoff_contract"][
                "authorization_contract"
            ]
            self.assertEqual(contract["available_at_response_boundary"], available)
            self.assertEqual(
                contract["missed_contact_windows_before_authorization"], missed
            )
            self.assertTrue(contract["runtime_observation_required"])
            self.assertFalse(
                contract["expected_contact_condition_used_as_observed_timestamp"]
            )

    def test_a18_autonomous_contact_delay_composes_to_p5(self) -> None:
        row = self.rows["A18"]
        self.assertEqual(row["event_id"], "E3")
        self.assertEqual(row["contact_condition_id"], "C1")
        self.assertEqual(row["requested_policy_id"], "P7")
        self.assertEqual(row["actual_effective_policy_id_static"], "P5")
        self.assertEqual(row["runtime_variant"], "e3_trusted_recovery_contact_delay")

    def test_e2_and_e4_sentinels_remain_fixed_p0(self) -> None:
        for cell_id in ("A19", "A22"):
            row = self.rows[cell_id]
            self.assertEqual(row["requested_policy_id"], "P0")
            self.assertEqual(row["actual_effective_policy_id_static"], "P0")

    def test_a24_adaptive_e4_composes_to_modeled_p4(self) -> None:
        row = self.rows["A24"]
        self.assertEqual(row["requested_policy_id"], "P7")
        self.assertEqual(row["actual_effective_policy_id_static"], "P4")
        self.assertEqual(row["runtime_family"], "observability")
        self.assertEqual(row["runtime_variant"], "e4_observability")

    def test_runtime_prerequisites_and_isolation_cleanup_sources_exist(self) -> None:
        self.assertTrue(self.result["all_runtime_prerequisites_present"])
        self.assertTrue(self.result["all_isolation_cleanup_sources_present"])
        for row in self.result["rows"]:
            self.assertTrue(row["runtime_prerequisite_sources"])
            self.assertTrue(row["isolation_cleanup_source"].startswith("scripts/"))
            self.assertTrue(row["raw_metric_schema_compatible"])
        for cell_id in ("A16", "A17"):
            self.assertEqual(
                self.rows[cell_id]["isolation_cleanup_source"],
                "scripts/run_wp9b2_p6_development.sh",
            )

    def test_b3_never_crosses_campaign_or_repetition_boundary(self) -> None:
        for key in (
            "runtime_execution_performed",
            "campaign_seed_consumed",
            "campaign_data_generated",
            "repetition_count_frozen",
            "campaign_execution_authorized",
        ):
            self.assertFalse(self.result[key], key)
        for row in self.result["rows"]:
            self.assertFalse(row["campaign_execution_authorized"])
            self.assertFalse(row["campaign_seed_consumed"])
            self.assertFalse(row["campaign_data_generated"])
            self.assertFalse(row["ground_truth_policy_oracle_allowed"])

    def test_matrix_build_is_deterministic_and_execution_free(self) -> None:
        again = build_readiness_matrix()
        self.assertEqual(self.result, again)
        self.assertEqual(self.result["static_seed"], 0)
        self.assertEqual(
            self.result["static_seed_role"],
            "semantic_materialization_only_not_execution",
        )


if __name__ == "__main__":
    unittest.main()