from __future__ import annotations

import json
import unittest
from pathlib import Path

from src.mission_recovery.primary_metrics import RECOVERY_CRITERIA

ROOT = Path(__file__).resolve().parents[1]
RUNNER = (
    ROOT / "scripts" / "run_wp8_recovery_binding_preflight.sh"
).read_text(encoding="utf-8")
PILOT = json.loads(
    (ROOT / "configs" / "wp8_pilot_design.json").read_text(
        encoding="utf-8"
    )
)


class WP8RecoveryPreflightContractTests(unittest.TestCase):
    def test_development_seed_and_nonpilot_contract(self) -> None:
        self.assertIn("SEED=9201", RUNNER)
        self.assertIn("pilot_seed_consumed=false", RUNNER)
        self.assertIn('"development_preflight": True', RUNNER)
        self.assertIn('"pilot_data": False', RUNNER)

    def test_event_injection_precedes_nonoracle_policy_selection(self) -> None:
        t0 = RUNNER.index('EVENT_ACTIVATION_NS="$(mono_ns)"')
        inject = RUNNER.index('docker cp "$TAMPERED" "$CFS:$STAGE_BACKING"')
        select = RUNNER.index('PHASE="POLICY_SELECTION"')
        enforce = RUNNER.index('PHASE="POLICY_ENFORCEMENT"')

        self.assertLess(t0, inject)
        self.assertLess(inject, select)
        self.assertLess(select, enforce)
        self.assertIn(
            "recovery_policy_trigger_uses_ground_truth=false",
            RUNNER,
        )
        self.assertIn(
            "policy_selection_not_gated_on_event_success=true",
            RUNNER,
        )

    def test_recovery_containment_and_trusted_order(self) -> None:
        enforcement = RUNNER.index('POLICY_ENFORCEMENT_NS="$(mono_ns)"')
        effect = RUNNER.index(
            'PHASE="POST_ENFORCEMENT_RECOVERY_EFFECT"'
        )
        containment = RUNNER.index('CONTAINMENT_NS="$(mono_ns)"')
        verification = RUNNER.index('PHASE="POST_RECOVERY_VERIFICATION"')
        manifest = RUNNER.index('trusted_recovery_evidence_manifest=PASS')
        trusted = RUNNER.index('TRUSTED_RECOVERY_NS="$(mono_ns)"')
        run_end = RUNNER.index('RUN_END_NS="$(mono_ns)"')

        self.assertLess(enforcement, effect)
        self.assertLess(effect, containment)
        self.assertLess(containment, verification)
        self.assertLess(verification, manifest)
        self.assertLess(manifest, trusted)
        self.assertLess(trusted, run_end)

    def test_all_ten_recovery_criteria_and_manifest_contract(self) -> None:
        contract = PILOT["runtime_measurement_contract"]
        recovery_rule = contract[
            "family_recovery_criteria_applicability"
        ]["recovery"]

        self.assertEqual(
            set(recovery_rule["applicable"]),
            set(RECOVERY_CRITERIA),
        )
        self.assertEqual(recovery_rule["excluded"], [])

        operational = contract["recovery_runtime_operationalization"]
        self.assertEqual(
            operational["decision_id"],
            "R-018",
        )
        self.assertTrue(
            operational["trusted_recovery"][
                "all_ten_recovery_criteria_required"
            ]
        )
        self.assertTrue(
            operational["trusted_recovery"][
                "evidence_manifest_must_validate_before_trusted_timestamp"
            ]
        )

    def test_post_recovery_command_and_telemetry_probes(self) -> None:
        self.assertIn(
            "--command-class sample_noop",
            RUNNER,
        )
        self.assertIn(
            "post_recovery_authorized_noop=PASS",
            RUNNER,
        )
        self.assertIn(
            'count_mid "$TRUTH_JSONL" 0x08E9',
            RUNNER,
        )
        self.assertIn(
            'count_mid "$POLICY_JSONL" 0x08E9',
            RUNNER,
        )
        self.assertIn(
            "required_telemetry_restored=true",
            RUNNER,
        )

    def test_claim_boundary_is_modeled_slot_not_firmware_activation(self) -> None:
        operational = PILOT["runtime_measurement_contract"][
            "recovery_runtime_operationalization"
        ]
        self.assertEqual(
            operational["modeled_activation_slot"]["virtual_path"],
            "/cf/mission-aware-e3-candidate.pkg",
        )
        self.assertIn(
            "not_operational_firmware_activation",
            operational["claim_boundary"],
        )
        self.assertIn(
            "probe_mechanism_only_not_study_event",
            operational["probe_adapter_reuse"][
                "nos3_e1_adapter"
            ],
        )
        self.assertIn(
            "probe_mechanism_only_not_study_event",
            operational["probe_adapter_reuse"][
                "nos3_e4_adapter"
            ],
        )


if __name__ == "__main__":
    unittest.main()
