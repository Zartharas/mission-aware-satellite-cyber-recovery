from __future__ import annotations

import json
import unittest
from pathlib import Path

from src.mission_recovery.primary_metrics import RECOVERY_CRITERIA

ROOT = Path(__file__).resolve().parents[1]
RUNNER = (
    ROOT / "scripts" / "run_wp8_command_binding_preflight.sh"
).read_text(encoding="utf-8")
PILOT = json.loads(
    (ROOT / "configs" / "wp8_pilot_design.json").read_text(
        encoding="utf-8"
    )
)


class WP8CommandPreflightContractTests(unittest.TestCase):
    def test_policy_selection_is_not_gated_on_ground_truth_success(self) -> None:
        event_send = RUNNER.index(
            "python3 -m src.mission_recovery.nos3_e1_adapter"
        )
        policy = RUNNER.index('PHASE="POLICY_SELECTION"')
        enforcement = RUNNER.index('PHASE="POLICY_ENFORCEMENT"')
        truth_wait = RUNNER.index('PHASE="EVENT_SUCCESS_CONFIRMATION"')

        self.assertLess(event_send, policy)
        self.assertLess(policy, enforcement)
        self.assertLess(enforcement, truth_wait)
        self.assertIn(
            "policy_trigger_uses_ground_truth=false",
            RUNNER,
        )

    def test_command_authority_divergence_is_behavioral_proxy(self) -> None:
        contract = PILOT["runtime_measurement_contract"]
        rule = contract[
            "command_authority_divergence_operationalization"
        ]
        self.assertEqual(rule["measurement_role"], "behavioral_proxy")
        self.assertIn(
            "not_a_direct_measurement_of_an_onboard_authorization",
            rule["claim_boundary"],
        )
        self.assertIn(
            '"end_ns": numbers["authority_convergence_ns"]',
            RUNNER,
        )

    def test_command_m08_applicability_is_predeclared(self) -> None:
        contract = PILOT["runtime_measurement_contract"]
        rule = contract[
            "family_recovery_criteria_applicability"
        ]["command"]

        self.assertEqual(
            set(rule["applicable"]) | set(rule["excluded"]),
            set(RECOVERY_CRITERIA),
        )
        self.assertFalse(
            set(rule["applicable"]) & set(rule["excluded"])
        )
        self.assertEqual(
            set(rule["applicable"]),
            {
                "authorization_valid",
                "authorized_command_path_restored",
                "ground_spacecraft_state_agreed",
                "health_checks_passed",
                "recovery_manifest_complete",
            },
        )
        self.assertIn(
            "no_residual_unauthorized_state",
            rule["excluded"],
        )

    def test_command_preflight_is_explicitly_nonpilot(self) -> None:
        self.assertIn("SEED=9101", RUNNER)
        self.assertIn("pilot_seed_consumed=false", RUNNER)
        self.assertIn('"development_preflight": True', RUNNER)
        self.assertIn('"pilot_data": False', RUNNER)


if __name__ == "__main__":
    unittest.main()
