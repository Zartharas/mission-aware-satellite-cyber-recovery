from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.mission_recovery import wp9_r066_campaign_runtime_executor as executor


class WP9R067FinalizeCompatibilityContractTests(unittest.TestCase):
    def _exercise(self, *, family: str, unexpected: bool) -> tuple[dict, dict]:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            evidence = root / "campaign" / family / "run-1"
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
                        "cell_id": "A13" if family == "E3" else "A05",
                    }
                )
                + "\n",
                encoding="utf-8",
            )

            cell_id = "A13" if family == "E3" else "A05"
            plan = {
                "run_id": "run-1",
                "campaign_seed": 10001,
                "cell_id": cell_id,
                "factor_context": {"event_id": family},
            }
            canonical = {
                "schema": 1,
                "classification": "WP9_R066_FINAL_CAMPAIGN_VALID_TRIAL_RESULT",
                "run_id": "run-1",
                "campaign_seed": 10001,
                "cell_id": cell_id,
                "outcome_matches_predeclared_expectation": not unexpected,
                "unexpected_scientific_outcome_retained": unexpected,
            }
            measurement = root / "measurement.json"
            measurement.write_text("{}\n", encoding="utf-8")
            summary = root / "development-summary.json"

            with (
                patch.object(
                    executor,
                    "_campaign_context",
                    return_value=(plan, evidence, "results/wp9/campaign/test"),
                ),
                patch.object(
                    executor.binding,
                    "_runtime_bundle",
                    return_value=canonical,
                ),
            ):
                executor.shim_finalize(
                    family=family,
                    measurement_json=measurement,
                    output_json=summary,
                )

            compatibility = json.loads(summary.read_text(encoding="utf-8"))
            campaign_result = json.loads(
                (evidence / "campaign-trial-result.json").read_text(
                    encoding="utf-8"
                )
            )
            return compatibility, campaign_result

    def test_e1_and_e3_legacy_summary_alias_is_preserved(self) -> None:
        for family in ("E1", "E3"):
            for unexpected in (False, True):
                with self.subTest(family=family, unexpected=unexpected):
                    summary, campaign_result = self._exercise(
                        family=family,
                        unexpected=unexpected,
                    )
                    self.assertEqual(
                        summary[
                            "unexpected_scientific_outcome_would_be_retained_in_campaign"
                        ],
                        unexpected,
                    )
                    self.assertEqual(
                        summary["unexpected_scientific_outcome_retained"],
                        unexpected,
                    )
                    self.assertEqual(
                        campaign_result["unexpected_scientific_outcome_retained"],
                        unexpected,
                    )
                    self.assertNotIn(
                        "unexpected_scientific_outcome_would_be_retained_in_campaign",
                        campaign_result,
                    )

    def test_canonical_campaign_result_schema_is_not_rewritten(self) -> None:
        summary, campaign_result = self._exercise(
            family="E3",
            unexpected=False,
        )
        self.assertEqual(
            summary["outcome_matches_predeclared_expectation"],
            campaign_result["outcome_matches_predeclared_expectation"],
        )
        self.assertEqual(
            campaign_result["classification"],
            "WP9_R066_FINAL_CAMPAIGN_VALID_TRIAL_RESULT",
        )
        self.assertNotIn(
            "unexpected_scientific_outcome_would_be_retained_in_campaign",
            campaign_result,
        )


if __name__ == "__main__":
    unittest.main()
