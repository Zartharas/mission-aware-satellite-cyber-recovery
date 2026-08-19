import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PILOT = json.loads(
    (ROOT / "configs/wp8_pilot_design.json").read_text(
        encoding="utf-8"
    )
)

RUNNER = (
    ROOT
    / "scripts"
    / "run_wp8_observability_stage1_development.sh"
)


class ObservabilityRuntimeExecutorTests(unittest.TestCase):
    def test_static_contract_and_pilot_gate(self) -> None:
        contract = PILOT["stage_1_runner_contract"][
            "observability_runtime_executor_contract"
        ]
        status = PILOT["instrumentation_gate"][
            "component_status"
        ]

        self.assertEqual(
            PILOT["status"],
            "STAGE1_OBSERVABILITY_RUNTIME_EXECUTOR_STATIC_"
            "VALIDATED_RUNTIME_PENDING",
        )
        self.assertEqual(
            contract["implementation_id"],
            "WP8-O01-GENERIC-V1",
        )
        self.assertEqual(
            contract["supported_cell_ids"],
            ["O01"],
        )
        self.assertTrue(
            contract["development_seed_parameterized"]
        )
        self.assertTrue(
            contract["pilot_seed_collision_rejected"]
        )
        self.assertTrue(
            contract["static_validation_complete"]
        )
        self.assertFalse(
            contract["runtime_validation_complete"]
        )
        self.assertFalse(
            contract["pilot_executor_ready"]
        )
        self.assertTrue(
            status[
                "stage_1_observability_runtime_executor_static"
            ]
        )
        self.assertFalse(
            status[
                "stage_1_observability_runtime_executor_runtime_validated"
            ]
        )
        self.assertFalse(
            PILOT["instrumentation_gate"][
                "pilot_execution_authorized"
            ]
        )

    def test_o01_frozen_factor_tuple(self) -> None:
        cell = next(
            row
            for row in PILOT["cells"]
            if row["cell_id"] == "O01"
        )
        self.assertEqual(
            (
                cell["event_id"],
                cell["mission_state_id"],
                cell["contact_condition_id"],
                cell["evidence_condition_id"],
                cell["policy_id"],
                cell["expected_effective_policy_id"],
            ),
            ("E4", "M2", "C0", "T0", "P7", "P4"),
        )

    def test_runner_preserves_accepted_mechanism(self) -> None:
        text = RUNNER.read_text(encoding="utf-8")
        self.assertIn('CELL_ID="$1"', text)
        self.assertIn('DEVELOPMENT_SEED="$2"', text)
        self.assertIn(
            'if [[ "$CELL_ID" != "O01" ]]',
            text,
        )
        self.assertIn(
            "development seed collides with frozen pilot seed",
            text,
        )
        self.assertIn(
            'VISIBILITY_DEADLINE_NS=3000000000',
            text,
        )
        self.assertIn('--mode degraded', text)
        self.assertIn(
            'decision = evaluate_policy("P7", event)',
            text,
        )
        self.assertIn(
            'assert decision["delegated_policy_id"] == "P4"',
            text,
        )
        self.assertIn(
            'echo "p4_native_safe_mode_claim=false"',
            text,
        )
        self.assertIn(
            '"containment_observed": False',
            text,
        )
        self.assertIn(
            'python3 -m src.mission_recovery.wp8_runtime_binding',
            text,
        )
        self.assertIn(
            'python3 -m src.mission_recovery.wp8_observability_evidence validate',
            text,
        )

    def test_runner_is_self_identifying_and_not_seed_9301_hardcoded(
        self,
    ) -> None:
        text = RUNNER.read_text(encoding="utf-8")
        self.assertNotIn("SEED=9301", text)
        self.assertNotIn(
            'echo "development_seed=9301"',
            text,
        )
        self.assertIn(
            'run_wp8_observability_stage1_development.sh"',
            text,
        )
        self.assertIn(
            "observability-executor-development",
            text,
        )

    def test_dispatch_names_development_runner(self) -> None:
        dispatch = PILOT["stage_1_runner_contract"][
            "dispatch_by_event_id"
        ]["E4"]
        self.assertEqual(
            dispatch["development_executor"],
            "scripts/run_wp8_observability_stage1_development.sh",
        )
        self.assertFalse(dispatch["pilot_executor_ready"])


if __name__ == "__main__":
    unittest.main()
