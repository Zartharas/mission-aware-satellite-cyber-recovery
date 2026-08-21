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

    def test_event_observer_is_prepositioned_without_timing_gate(self) -> None:
        observer = RUNNER.index('PHASE="EVENT_OBSERVER_PREPOSITION"')
        ready = RUNNER.index(
            "immutable_activation_slot_observer_prepositioned=PASS"
        )
        t0 = RUNNER.index('EVENT_ACTIVATION_NS="$(mono_ns)"')
        inject = RUNNER.index(
            'docker cp "$TAMPERED" "$CFS:$STAGE_BACKING"'
        )
        select = RUNNER.index('PHASE="POLICY_SELECTION"')
        enforce_clock = RUNNER.index(
            'POLICY_ENFORCEMENT_NS="$(mono_ns)"'
        )
        strict_boundary = RUNNER.index(
            "prepositioned E3 event-success observer had not completed"
        )
        recovery_effect = RUNNER.index(
            'PHASE="POST_ENFORCEMENT_RECOVERY_EFFECT"'
        )

        self.assertLess(observer, ready)
        self.assertLess(ready, t0)
        self.assertLess(t0, inject)
        self.assertLess(inject, select)
        self.assertLess(select, enforce_clock)
        self.assertLess(enforce_clock, strict_boundary)
        self.assertLess(strict_boundary, recovery_effect)

        operational = PILOT["runtime_measurement_contract"][
            "recovery_runtime_operationalization"
        ]
        event_observer = operational["event_success_observer"]

        self.assertEqual(
            event_observer["revision_id"],
            "R-019",
        )
        self.assertEqual(
            event_observer["implementation"],
            "single_persistent_in_container_sha_observer",
        )
        self.assertTrue(event_observer["preposition_before_t0"])
        self.assertFalse(
            event_observer[
                "observer_completion_can_delay_policy_selection"
            ]
        )
        self.assertFalse(
            event_observer[
                "observer_completion_can_delay_policy_enforcement"
            ]
        )
        self.assertFalse(
            event_observer[
                "observer_completion_can_delay_recovery_effect"
            ]
        )

        self.assertIn(
            "event_success_observed_by_policy_enforcement_boundary=true",
            RUNNER,
        )
        self.assertIn(
            "policy_enforcement_not_gated_on_event_success=true",
            RUNNER,
        )
        self.assertIn(
            "recovery_effect_not_delayed_for_ground_truth_observer=true",
            RUNNER,
        )

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

    def test_recovery_measurement_destination_stabilization(self) -> None:
        settle = RUNNER.index(
            'PHASE="NOMINAL_TOLAB_DESTINATION_SETTLE"'
        )
        nominal_marker = RUNNER.index(
            "TO telemetry output enabled for IP active-gs"
        )
        plane = RUNNER.index(
            'PHASE="MEASUREMENT_PLANE_PREPOSITION"'
        )
        enable = RUNNER.index(
            'enable-output --destination recovery-proxy'
        )
        ownership = RUNNER.index(
            "recovery_tolab_destination_ownership=PASS"
        )
        event = RUNNER.index('PHASE="EVENT_ACTIVATION"')
        post_probe = RUNNER.index(
            'run_e4_adapter "$(basename "$SEND_JSON")" send-data-types'
        )

        self.assertLess(settle, nominal_marker)
        self.assertLess(nominal_marker, plane)
        self.assertLess(plane, enable)
        self.assertLess(enable, ownership)
        self.assertLess(ownership, event)
        self.assertLess(event, post_probe)

        self.assertIn(
            "count_tolab_enable_markers()",
            RUNNER,
        )
        self.assertIn(
            "last_tolab_destination()",
            RUNNER,
        )
        self.assertIn(
            "assert_recovery_destination_stable()",
            RUNNER,
        )
        self.assertIn(
            'test "$RECOVERY_TOLAB_ENABLE_COUNT" -eq '
            '$((NOMINAL_TOLAB_ENABLE_COUNT + 1))',
            RUNNER,
        )
        self.assertIn(
            'test "$RECOVERY_TOLAB_LAST_DESTINATION" = '
            '"recovery-proxy"',
            RUNNER,
        )
        self.assertGreaterEqual(
            RUNNER.count("assert_recovery_destination_stable"),
            4,
        )

    def test_post_recovery_command_and_telemetry_probes(self) -> None:
        operational = PILOT["runtime_measurement_contract"][
            "recovery_runtime_operationalization"
        ]
        command_probe = operational["post_recovery_command_probe"]

        self.assertEqual(
            command_probe["revision_id"],
            "R-020",
        )
        self.assertEqual(
            command_probe["implementation"],
            "direct_internal_sample_noop_health_probe",
        )
        self.assertFalse(
            command_probe["e1_event_adapter_cli_invoked"]
        )
        self.assertFalse(command_probe["study_event"])
        self.assertFalse(command_probe["event_instance_required"])
        self.assertEqual(
            command_probe["expected_packet_sha256"],
            "722b8fe72fb18ee581c970ea92c100f435fa90ccccaf0a05bf3e8bee0c4d13bd",
        )

        self.assertNotIn(
            "python3 -m src.mission_recovery.nos3_e1_adapter",
            RUNNER,
        )
        self.assertIn(
            "build_sample_noop_packet",
            RUNNER,
        )
        self.assertIn(
            '"study_event": False',
            RUNNER,
        )
        self.assertIn(
            '"event_instance_used": False',
            RUNNER,
        )
        self.assertIn(
            "post_recovery_noop_probe_record=PASS",
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

    def test_trusted_recovery_criteria_are_evidence_derived(self) -> None:
        operational = PILOT["runtime_measurement_contract"][
            "recovery_runtime_operationalization"
        ]
        derivation = operational[
            "trusted_recovery_evidence_derivation"
        ]

        self.assertEqual(
            derivation["revision_id"],
            "R-021",
        )
        self.assertTrue(
            derivation["criterion_evidence_refs_required"]
        )
        self.assertTrue(
            derivation[
                "criterion_values_must_all_be_true_for_trusted_recovery"
            ]
        )
        self.assertEqual(
            derivation["literal_unconditional_true_criteria_allowed"],
            ["recovery_manifest_complete"],
        )

        command_probe = operational["post_recovery_command_probe"]
        self.assertEqual(
            command_probe["trusted_recovery_criterion"],
            "authorized_command_path_restored",
        )
        self.assertFalse(
            command_probe["end_to_end_identity_protocol_claim"]
        )

        self.assertIn(
            'criterion_derivation_revision_id": "R-021"',
            RUNNER,
        )
        self.assertIn(
            '"criterion_evidence_refs": criterion_evidence_refs',
            RUNNER,
        )
        self.assertIn(
            "authorization_validation_accepted",
            RUNNER,
        )
        self.assertIn(
            "authorized_command_path_restored = (",
            RUNNER,
        )
        self.assertIn(
            "required_telemetry_restored = (",
            RUNNER,
        )
        self.assertIn(
            "no_residual_unauthorized_state = (",
            RUNNER,
        )
        self.assertIn(
            "trusted_recovery_criteria_derived_from_retained_evidence=PASS",
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
            "no_E1_event_instance_or_E1_adapter_CLI",
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
