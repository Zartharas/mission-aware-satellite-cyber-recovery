from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNNER = (
    ROOT / "scripts" / "run_wp8_observability_binding_preflight.sh"
).read_text(encoding="utf-8")
EVIDENCE_MODULE = (
    ROOT / "src" / "mission_recovery" / "wp8_observability_evidence.py"
).read_text(encoding="utf-8")
PILOT = json.loads(
    (ROOT / "configs" / "wp8_pilot_design.json").read_text(
        encoding="utf-8"
    )
)


class WP8ObservabilityPreflightContractTests(unittest.TestCase):
    def test_o01_factors_and_development_seed(self) -> None:
        self.assertIn("SEED=9301", RUNNER)
        self.assertIn('study_cell=O01', RUNNER)
        self.assertIn('"event_id": "E4"', RUNNER)
        self.assertIn('"mission_state_id": "M2"', RUNNER)
        self.assertIn('"policy_id": "P7"', RUNNER)
        self.assertIn('"development_preflight": True', EVIDENCE_MODULE)
        self.assertIn('"pilot_data": False', EVIDENCE_MODULE)
        self.assertIn(
            "wp8_observability_evidence materialize",
            RUNNER,
        )

    def test_event_policy_order_is_nonoracle(self) -> None:
        t0 = RUNNER.index('EVENT_ACTIVATION_NS="$(mono_ns)"')
        send = RUNNER.index(
            'run_e4_adapter "$(basename "$EVENT_SEND_JSON")" send-data-types'
        )
        select = RUNNER.index('PHASE="POLICY_SELECTION"')
        enforce = RUNNER.index('PHASE="POLICY_ENFORCEMENT"')
        success = RUNNER.index('PHASE="EVENT_SUCCESS_OBSERVATION"')

        self.assertLess(t0, send)
        self.assertLess(send, select)
        self.assertLess(select, enforce)
        self.assertLess(enforce, success)

        self.assertIn(
            "policy_trigger_uses_ground_truth=false",
            RUNNER,
        )
        self.assertIn(
            "policy_selection_not_gated_on_event_success=true",
            RUNNER,
        )
        self.assertIn(
            "policy_enforcement_not_gated_on_event_success=true",
            RUNNER,
        )

    def test_e4_deadline_and_containment_are_distinct(self) -> None:
        operational = PILOT["runtime_measurement_contract"][
            "observability_runtime_operationalization"
        ]

        self.assertEqual(operational["decision_id"], "R-022")
        self.assertEqual(
            operational["visibility_deadline_s"],
            3.0,
        )
        self.assertFalse(
            operational["p4_effect"][
                "telemetry_restoration_claim"
            ]
        )
        self.assertEqual(
            operational["containment_rule"],
            (
                "required_high_value_telemetry_policy_visible_and_"
                "confirmed_by_matched_post_enforcement_sample"
            ),
        )
        self.assertIn(
            "p4_selection_is_not_observability_containment=true",
            RUNNER,
        )

    def test_uncontained_valid_run_is_right_censored(self) -> None:
        operational = PILOT["runtime_measurement_contract"][
            "observability_runtime_operationalization"
        ]
        terminal = operational["terminal_taxonomy"]

        self.assertEqual(
            terminal["persistent_e4_after_bounded_response"],
            "RECOVERY_FAILED",
        )
        self.assertTrue(
            terminal["containment_time_right_censored"]
        )
        self.assertTrue(
            terminal["verified_recovery_time_right_censored"]
        )
        self.assertFalse(
            terminal["spacecraft_failure_claim"]
        )

        self.assertIn('"containment_ns": None', EVIDENCE_MODULE)
        self.assertIn('"trusted_recovery_ns": None', EVIDENCE_MODULE)
        self.assertIn('"recovery_failed": True', EVIDENCE_MODULE)
        self.assertIn('"contained": False', EVIDENCE_MODULE)
        self.assertIn(
            "wp8_observability_evidence validate",
            RUNNER,
        )

    def test_observability_metric_semantics_are_frozen(self) -> None:
        operational = PILOT["runtime_measurement_contract"][
            "observability_runtime_operationalization"
        ]

        self.assertEqual(
            operational["development_seed"],
            9301,
        )
        self.assertEqual(
            operational["expected_valid_uncontained_metrics"][
                "mission_objective_completion_ratio"
            ],
            0.5,
        )
        self.assertEqual(
            operational["expected_valid_uncontained_metrics"][
                "legitimate_command_rejection_rate"
            ],
            1.0,
        )
        self.assertEqual(
            operational["expected_valid_uncontained_metrics"][
                "evidence_completeness_ratio"
            ],
            2 / 3,
        )
        self.assertIsNone(
            operational["expected_valid_uncontained_metrics"][
                "time_to_containment_s"
            ]
        )
        self.assertIsNone(
            operational["expected_valid_uncontained_metrics"][
                "time_to_verified_recovery_s"
            ]
        )

    def test_applicability_and_claim_boundaries(self) -> None:
        contract = PILOT["runtime_measurement_contract"]
        applicability = contract[
            "family_recovery_criteria_applicability"
        ]["observability"]

        self.assertEqual(
            set(applicability["applicable"]),
            {
                "required_telemetry_restored",
                "health_checks_passed",
                "recovery_manifest_complete",
            },
        )
        self.assertEqual(len(applicability["excluded"]), 7)

        operational = contract[
            "observability_runtime_operationalization"
        ]

        self.assertIn(
            "not_native_spacecraft_safe_mode",
            operational["claim_boundary"],
        )
        self.assertIn(
            "not_spacecraft_failure",
            operational["terminal_taxonomy"]["claim_boundary"],
        )


if __name__ == "__main__":
    unittest.main()
