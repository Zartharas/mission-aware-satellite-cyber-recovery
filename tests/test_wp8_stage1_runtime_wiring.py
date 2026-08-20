from __future__ import annotations

import json
import subprocess
import sys
import unittest
from copy import deepcopy
from pathlib import Path

from src.mission_recovery.events import materialize_event

from src.mission_recovery.wp8_stage1_runtime_wiring import (
    PILOT_RUNTIME_PATH_BY_CELL,
    _factor,
    _select_policy,
    _semantic_contract_view,
    require_active_pilot,
    validate_runtime_wiring_contract,
)

ROOT = Path(__file__).resolve().parents[1]
PILOT = json.loads(
    (ROOT / "configs/wp8_pilot_design.json").read_text(encoding="utf-8")
)


class Stage1RuntimeWiringTests(unittest.TestCase):
    def test_r042_dispatch_activated_pilot_authorization_pending(self):
        validate_runtime_wiring_contract(PILOT)
        dispatch = PILOT["stage_1_runner_contract"][
            "family_runtime_dispatch_adapter_contract"
        ]
        r039 = dispatch["pilot_mode_contract"]
        r040 = dispatch["runtime_wiring_contract"]
        ci = r040["exact_sha_ci_validation"]
        activation = r040["dispatch_activation"]
        self.assertTrue(r039["runtime_wiring_complete"])
        self.assertEqual(ci["decision_id"], "R-041")
        self.assertEqual(ci["status"], "PASS")
        self.assertEqual(
            ci["validated_implementation_commit"],
            "ba26b39b295e45932f4adf834f458ccc8dd9863e",
        )
        self.assertEqual(ci["workflow_run_id"], 32319312294)
        self.assertEqual(ci["conclusion"], "success")
        self.assertFalse(ci["dispatch_activation_performed"])
        self.assertEqual(activation["decision_id"], "R-042")
        self.assertEqual(activation["status"], "PASS")
        self.assertEqual(
            activation["activation_basis_commit"],
            "4322a2a80edfa0a24ad0ab9fa66e0a0046c3b698",
        )
        self.assertEqual(
            activation["activation_basis_workflow_run_id"],
            32328740879,
        )
        self.assertTrue(activation["activation_performed"])
        self.assertFalse(r040["authorization_pending"])
        self.assertFalse(r040["runtime_execution_performed"])
        self.assertFalse(r040["pilot_seed_consumed"])
        self.assertFalse(r040["pilot_data_generated"])
        self.assertTrue(
            PILOT["instrumentation_gate"]["component_status"][
                "stage_1_family_runtime_dispatch_adapters"
            ]
        )
        for row in PILOT["stage_1_runner_contract"][
            "dispatch_by_event_id"
        ].values():
            self.assertTrue(row["pilot_executor_ready"])
        self.assertFalse(
            PILOT["instrumentation_gate"]["pilot_execution_authorized"]
        )

    def test_r040_runtime_paths_are_exact(self):
        self.assertEqual(
            PILOT_RUNTIME_PATH_BY_CELL,
            {
                "C01": "command_generic",
                "C02": "command_generic",
                "C03": "command_generic",
                "C04": "command_generic",
                "C05": "command_generic",
                "C06": "command_generic",
                "C07": "command_generic",
                "R01": "recovery_generic",
                "R02": "recovery_full_trusted",
                "R03": "recovery_full_trusted",
                "R04": "recovery_generic",
                "O01": "observability_generic",
            },
        )

    def test_r042_current_configuration_cannot_execute_pilot(self):
        with self.assertRaisesRegex(
            PermissionError,
            "pilot execution is not authorized",
        ):
            require_active_pilot(PILOT, cell_id="C05")

    def test_historical_semantic_view_changes_only_lifecycle(self):
        view = _semantic_contract_view(PILOT)
        self.assertEqual(view["cells"], PILOT["cells"])
        self.assertEqual(
            view["runtime_measurement_contract"],
            PILOT["runtime_measurement_contract"],
        )
        self.assertEqual(
            view["stage_1_control_validity"],
            PILOT["stage_1_control_validity"],
        )
        self.assertFalse(
            view["instrumentation_gate"]["pilot_execution_authorized"]
        )
        self.assertFalse(
            view["instrumentation_gate"]["component_status"]
            ["stage_1_family_runtime_dispatch_adapters"]
        )

    def _future_authorized_pilot(self):
        pilot = deepcopy(PILOT)
        pilot["instrumentation_gate"][
            "component_status"
        ]["stage_1_family_runtime_dispatch_adapters"] = True
        pilot["instrumentation_gate"][
            "pilot_execution_authorized"
        ] = True
        for row in pilot["stage_1_runner_contract"][
            "dispatch_by_event_id"
        ].values():
            row["pilot_executor_ready"] = True
        return pilot

    def test_policy_selector_rejects_factor_mismatch(self):
        pilot = self._future_authorized_pilot()
        event = materialize_event(
            "E1",
            mission_state="M2",
            contact_condition="C0",
            evidence_condition="T0",
            seed=101,
        )
        event["mission_state"] = "M0"
        with self.assertRaisesRegex(
            ValueError,
            "mission_state",
        ):
            _select_policy(
                pilot,
                cell_id="C05",
                event=event,
            )

    def test_runtime_wiring_cli_subcommand_handshake(self):
        subcommands = (
            "check-gate",
            "command-plan",
            "command-select-policy",
            "command-finalize-observation",
            "command-bind-pilot",
            "recovery-plan",
            "recovery-select-policy",
            "recovery-prepare-rollback",
            "recovery-finalize-observation",
            "recovery-bind-pilot",
            "full-recovery-validate-factor",
            "full-recovery-bind-existing",
            "observability-bind-existing",
        )
        for command in subcommands:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "src.mission_recovery."
                    "wp8_stage1_runtime_wiring",
                    command,
                    "--help",
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
            self.assertEqual(
                result.returncode,
                0,
                msg=(
                    command
                    + "\nstdout:\n"
                    + result.stdout
                    + "\nstderr:\n"
                    + result.stderr
                ),
            )

    def test_pilot_scope_and_controller_audit_retention(self):
        recovery = (
            ROOT
            / "scripts"
            / "run_wp8_recovery_stage1_development.sh"
        ).read_text(encoding="utf-8")
        controller = (
            ROOT / "scripts/run_wp8_stage1_pilot.sh"
        ).read_text(encoding="utf-8")
        wiring = (
            ROOT
            / "src"
            / "mission_recovery"
            / "wp8_stage1_runtime_wiring.py"
        ).read_text(encoding="utf-8")

        self.assertIn(
            'SCOPE_JSON="$GROUND/pilot-evidence-scope.json"',
            recovery,
        )
        self.assertIn(
            "immutable-ground/pilot-evidence-scope.json",
            wiring,
        )
        self.assertIn(
            "controller_post_runner_audit_failure",
            controller,
        )
        self.assertIn(
            '"experiment_failure_claimed": False',
            controller,
        )
        self.assertNotIn(
            "experiment_failure_claimed=True",
            controller,
        )
        self.assertIn(
            "controller-attempt-status.txt",
            controller,
        )

    def test_pilot_controller_and_family_hooks_exist(self):
        controller = (ROOT / "scripts/run_wp8_stage1_pilot.sh").read_text(
            encoding="utf-8"
        )
        self.assertNotIn("--all", controller)
        self.assertIn("deterministic_stage1_cell_ids", controller)
        self.assertIn("record_attempt", controller)
        self.assertIn("stage1_progress", controller)
        self.assertIn("WP8_STAGE1_PILOT=1", controller)
        self.assertIn("WP8_STAGE1_CONTROLLER=1", controller)
        self.assertLess(
            controller.index("check-gate"),
            controller.index("docker info"),
        )
        self.assertLess(
            controller.index("check-gate"),
            controller.index('mkdir -p "$LEDGER_DIR"'),
        )
        self.assertIn('CONTROLLER_LOG="$EVIDENCE/controller.log"', controller)
        command = (ROOT / "scripts/run_wp8_command_stage1_development.sh").read_text(encoding="utf-8")
        self.assertIn("command_pilot_measurement_provenance=PASS", command)
        for script in (
            "run_wp8_command_stage1_development.sh",
            "run_wp8_recovery_stage1_development.sh",
            "run_wp8_recovery_binding_preflight.sh",
            "run_wp8_observability_stage1_development.sh",
        ):
            text = (ROOT / "scripts" / script).read_text(encoding="utf-8")
            self.assertIn("WP8_STAGE1_PILOT", text)
            self.assertIn("WP8_STAGE1_CONTROLLER", text)
            self.assertIn("--run-id", text)
            self.assertIn("wp8_stage1_runtime_wiring", text)

    def test_controller_run_id_contract_is_exact(self):
        pilot = self._future_authorized_pilot()
        valid = (
            "20260819T123456.123456Z-wp8-stage1-c05-s101-"
            + ("a" * 32)
        )
        factor = _factor(
            pilot,
            cell_id="C05",
            run_id=valid,
        )
        self.assertEqual(factor["seed"], 101)

        with self.assertRaisesRegex(
            ValueError,
            "controller-allocated",
        ):
            _factor(
                pilot,
                cell_id="C05",
                run_id="20260819T123456Z-wp8-stage1-c05-s101",
            )

        with self.assertRaisesRegex(
            ValueError,
            "cell differs",
        ):
            _factor(
                pilot,
                cell_id="C06",
                run_id=valid,
            )

    def test_expected_policy_is_not_used_pre_enforcement(self):
        pilot = self._future_authorized_pilot()
        for row in pilot["cells"]:
            if row["cell_id"] == "C05":
                row["expected_effective_policy_id"] = "P4"
                break

        event = materialize_event(
            "E1",
            mission_state="M2",
            contact_condition="C0",
            evidence_condition="T0",
            seed=101,
        )
        selected = _select_policy(
            pilot,
            cell_id="C05",
            event=event,
        )
        self.assertEqual(
            selected["delegated_policy_id"],
            "P2",
        )

    def test_no_ungated_runtime_sender_or_factor_rewrite_cli(self):
        wiring = (
            ROOT
            / "src"
            / "mission_recovery"
            / "wp8_stage1_runtime_wiring.py"
        ).read_text(encoding="utf-8")

        self.assertNotIn("sendto(", wiring)
        self.assertNotIn(
            "recovery-send-authorized-noop",
            wiring,
        )
        self.assertNotIn(
            "full-recovery-normalize-factor",
            wiring,
        )
        self.assertIn(
            "full-recovery-validate-factor",
            wiring,
        )


if __name__ == "__main__":
    unittest.main()
