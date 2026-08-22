from __future__ import annotations

import copy
import unittest
from pathlib import Path

from src.mission_recovery.wp9c_repetition_selection import (
    ROOT,
    _extract_record,
    _load,
    conservative_precision_for_candidate,
    empirical_precision_for_candidate,
    extreme_laplace_binary_probability,
    model_stability_for_candidate,
    validate_method_config,
    wilson_half_width,
)


class WP9CRepetitionSelectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = _load(ROOT / "configs/wp9c_repetition_selection.json")
        cls.campaign = _load(ROOT / "configs/wp9_campaign_design.json")

    def _synthetic_anchors(self, *, structural: bool = False):
        anchors = {}
        for anchor_index, cell_id in enumerate(
            self.config["input_contract"]["anchor_cell_ids"]
        ):
            rows = []
            for seed_index, seed in enumerate(
                self.config["input_contract"]["anchor_seed_ids"]
            ):
                offset = 0.0 if structural else 0.01 * seed_index
                rows.append(
                    {
                        "cell_id": cell_id,
                        "seed": seed,
                        "run_id": f"synthetic-{cell_id}-{seed}",
                        "mission_objective_completion_ratio": 0.70 + offset,
                        "evidence_completeness_ratio": 0.80 + offset,
                        "unauthorized_effect_completed": (
                            False if structural else seed_index == 0
                        ),
                        "trusted_recovery_confirmed": (
                            True if structural else seed_index >= 3
                        ),
                        "legitimate_attempted": 1,
                        "legitimate_rejected": (
                            0 if structural else int(seed_index == 4)
                        ),
                        "legitimate_rejection_indicator": (
                            False if structural else seed_index == 4
                        ),
                        "time_to_containment_s": 4.0 + (0.0 if structural else offset),
                        "time_to_verified_recovery_s": 5.0 + (0.0 if structural else offset),
                        "ground_spacecraft_state_divergence_s": (
                            2.0 + (0.0 if structural else offset)
                        ),
                        "containment_observed": True,
                        "trusted_recovery_observed": True,
                        "terminal_state": "TRUSTED_RECOVERY_CONFIRMED",
                    }
                )
            anchors[cell_id] = rows
        return anchors

    def test_method_config_matches_frozen_r044_candidates_and_targets(self) -> None:
        validate_method_config(self.config, self.campaign)
        self.assertEqual(
            self.config["candidate_valid_repetitions_per_cell"],
            [12, 16, 20, 24, 30],
        )
        self.assertEqual(
            self.config["precision_targets"]["model_fit_convergence_rate"],
            0.90,
        )

    def test_method_never_authorizes_campaign_or_freezes_result(self) -> None:
        boundary = self.config["scientific_boundary"]
        self.assertTrue(boundary["read_only_pilot_inputs"])
        for key in (
            "pilot_effects_used_as_final_effect_assumptions",
            "expected_values_used_as_metric_inputs",
            "campaign_runtime_execution_performed",
            "campaign_seed_consumed",
            "campaign_data_generated",
            "final_campaign_execution_authorized",
        ):
            self.assertFalse(boundary[key], key)
        execution = self.config["selection_execution"]
        self.assertFalse(execution["executes_nos3"])
        self.assertFalse(execution["executes_campaign"])

    def test_wilson_sensitivity_width_decreases_with_repetitions(self) -> None:
        p = 6.0 / 7.0
        widths = [wilson_half_width(p, n) for n in (12, 16, 20, 24, 30)]
        self.assertEqual(widths, sorted(widths, reverse=True))
        self.assertGreater(widths[0], 0.18)
        self.assertLess(widths[-1], 0.18)

    def test_structural_binary_anchor_gets_nonzero_laplace_envelope(self) -> None:
        anchors = self._synthetic_anchors(structural=True)
        envelope = extreme_laplace_binary_probability(anchors)
        self.assertAlmostEqual(envelope["extreme_probability"], 6.0 / 7.0)
        self.assertGreater(envelope["extreme_probability"], 0.5)
        self.assertLess(envelope["extreme_probability"], 1.0)

    def test_conservative_structural_metrics_do_not_get_zero_width(self) -> None:
        anchors = self._synthetic_anchors(structural=True)
        result = conservative_precision_for_candidate(
            anchors=anchors,
            config=self.config,
            candidate=30,
        )
        for row in result["rows"]:
            self.assertGreater(row["precision_value"], 0.0)
        self.assertTrue(result["precision_pass"])

    def test_model_stability_is_deterministic_and_improves_with_n(self) -> None:
        p = 6.0 / 7.0
        first = model_stability_for_candidate(
            extreme_probability=p,
            config=self.config,
            candidate=24,
        )
        again = model_stability_for_candidate(
            extreme_probability=p,
            config=self.config,
            candidate=24,
        )
        larger = model_stability_for_candidate(
            extreme_probability=p,
            config=self.config,
            candidate=30,
        )
        self.assertEqual(first, again)
        self.assertLess(
            first["minimum_convergence_rate"],
            larger["minimum_convergence_rate"],
        )
        self.assertFalse(first["convergence_pass"])
        self.assertTrue(larger["convergence_pass"])

    def test_empirical_structural_zero_width_is_deferred_not_sufficient(self) -> None:
        anchors = self._synthetic_anchors(structural=True)
        config = copy.deepcopy(self.config)
        config["empirical_resampling"]["iterations"] = 200
        result = empirical_precision_for_candidate(
            anchors=anchors,
            config=config,
            candidate=12,
        )
        self.assertGreater(result["structural_endpoint_count"], 0)
        self.assertTrue(result["structural_endpoints_require_sensitivity"])
        statuses = {row["status"] for row in result["rows"]}
        self.assertIn("STRUCTURAL_DEGENERATE_REQUIRES_SENSITIVITY", statuses)

    def test_empirical_bootstrap_is_deterministic(self) -> None:
        anchors = self._synthetic_anchors(structural=False)
        config = copy.deepcopy(self.config)
        config["empirical_resampling"]["iterations"] = 200
        first = empirical_precision_for_candidate(
            anchors=anchors,
            config=config,
            candidate=16,
        )
        again = empirical_precision_for_candidate(
            anchors=anchors,
            config=config,
            candidate=16,
        )
        self.assertEqual(first, again)

    def test_extract_record_preserves_right_censoring_at_run_end(self) -> None:
        record = {
            "run_id": "synthetic-censored",
            "terminal_state": "RECOVERY_FAILED",
            "timing": {
                "containment_s": None,
                "verified_recovery_s": None,
            },
            "outcomes": {
                "mission_objective_completion_ratio": 0.5,
                "evidence_completeness_ratio": 0.6,
                "unauthorized_effect_completed": True,
                "ground_spacecraft_state_divergence_s": 7.0,
            },
            "raw_metric_evidence": {
                "run_end_s": 120.0,
                "containment": {"predicate": False, "timestamp_s": None},
                "trusted_recovery": {"predicate": False, "timestamp_s": None},
                "legitimate_commands": {"attempted": 1, "rejected": 0},
            },
        }
        extracted = _extract_record(run_record=record, cell_id="O01", seed=101)
        self.assertEqual(extracted["time_to_containment_s"], 120.0)
        self.assertEqual(extracted["time_to_verified_recovery_s"], 120.0)
        self.assertFalse(extracted["trusted_recovery_confirmed"])

    def test_no_precision_target_is_invented_for_count_or_categorical_metrics(self) -> None:
        no_threshold = set(
            self.config["metric_classes"]["no_numeric_precision_threshold_frozen"]
        )
        self.assertEqual(
            no_threshold,
            {
                "safety_invariant_violation_count",
                "recovery_terminal_state",
                "effective_policy_id",
                "residual_unauthorized_state_count",
            },
        )


if __name__ == "__main__":
    unittest.main()
