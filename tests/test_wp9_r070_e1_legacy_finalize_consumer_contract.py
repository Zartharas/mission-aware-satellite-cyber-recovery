from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.mission_recovery import wp9_r066_campaign_runtime_executor as executor


class WP9R070E1LegacyFinalizeConsumerContractTests(unittest.TestCase):
    def _exercise(self) -> tuple[dict, dict]:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            evidence = root / "campaign" / "E1" / "run-1"
            marker = (
                evidence
                / "immutable-ground"
                / "campaign-seed-consumption.json"
            )
            marker.parent.mkdir(parents=True)
            marker.write_text(
                json.dumps(
                    {
                        "campaign_seed": 10001,
                        "cell_id": "A08",
                    }
                )
                + "\n",
                encoding="utf-8",
            )

            plan = {
                "run_id": "run-1",
                "campaign_seed": 10001,
                "cell_id": "A08",
                "factor_context": {"event_id": "E1"},
            }
            canonical = {
                "schema": 1,
                "classification": (
                    "WP9_R066_FINAL_CAMPAIGN_VALID_TRIAL_RESULT"
                ),
                "run_id": "run-1",
                "campaign_seed": 10001,
                "cell_id": "A08",
                "treatment_fidelity_valid": True,
                "raw_metric_inputs_complete": True,
                "outcome_matches_predeclared_expectation": True,
                "unexpected_scientific_outcome_retained": False,
                "campaign_seed_consumed": True,
                "campaign_data_generated": True,
                "campaign_wide_execution_authorized": False,
            }
            measurement = root / "measurement.json"
            measurement.write_text("{}\n", encoding="utf-8")
            summary = root / "development-summary.json"

            with (
                patch.object(
                    executor,
                    "_campaign_context",
                    return_value=(
                        plan,
                        evidence,
                        "results/wp9/campaign/seed-10001/A08/run-1",
                    ),
                ),
                patch.object(
                    executor.binding,
                    "_runtime_bundle",
                    return_value=canonical,
                ),
            ):
                executor.shim_finalize(
                    family="E1",
                    measurement_json=measurement,
                    output_json=summary,
                )

            compatibility = json.loads(
                summary.read_text(encoding="utf-8")
            )
            campaign_result = json.loads(
                (evidence / "campaign-trial-result.json").read_text(
                    encoding="utf-8"
                )
            )
            return compatibility, campaign_result

    def test_e1_summary_satisfies_exact_r061_post_finalize_assertions(self) -> None:
        summary, _ = self._exercise()

        # Exact fields read by the unchanged R-061 source harness after
        # finalize-development.  This is the compatibility contract.
        self.assertEqual(summary["acceptance_status"], "PASS")
        self.assertIs(summary["treatment_fidelity_valid"], True)
        self.assertIs(summary["raw_metric_inputs_complete"], True)
        self.assertIs(summary["campaign_seed_consumed"], False)
        self.assertIs(summary["campaign_data_generated"], False)
        self.assertIs(
            summary["final_campaign_execution_authorized"],
            False,
        )
        self.assertIs(
            summary["outcome_matches_predeclared_expectation"],
            True,
        )
        self.assertIs(
            summary[
                "unexpected_scientific_outcome_would_be_retained_in_campaign"
            ],
            False,
        )

    def test_legacy_alias_does_not_rewrite_canonical_campaign_semantics(self) -> None:
        summary, campaign_result = self._exercise()

        self.assertIs(summary["campaign_seed_consumed"], False)
        self.assertIs(summary["campaign_data_generated"], False)

        self.assertIs(campaign_result["campaign_seed_consumed"], True)
        self.assertIs(campaign_result["campaign_data_generated"], True)
        self.assertNotIn("acceptance_status", campaign_result)
        self.assertNotIn(
            "final_campaign_execution_authorized",
            campaign_result,
        )
        self.assertNotIn(
            "unexpected_scientific_outcome_would_be_retained_in_campaign",
            campaign_result,
        )


if __name__ == "__main__":
    unittest.main()
