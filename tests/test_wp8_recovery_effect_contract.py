import json
import unittest
from pathlib import Path

from src.mission_recovery.wp8_recovery_effect_contract import (
    RECOVERY_CELL_IDS,
    build_recovery_cell_effect_contract,
    build_recovery_effect_matrix,
    derive_observed_recovery_effect,
    recovery_cells,
    require_recovery_effect_acceptance,
)

ROOT = Path(__file__).resolve().parents[1]
PILOT = json.loads(
    (ROOT / "configs/wp8_pilot_design.json").read_text(
        encoding="utf-8"
    )
)

EXPECTED = {
    "R01": (
        "P0",
        "P0",
        "OBSERVE_ONLY",
        "observe_only",
        False,
    ),
    "R02": (
        "P5",
        "P5",
        "REQUEST_VERIFIED_ROLLBACK",
        "rollback_request",
        True,
    ),
    "R03": (
        "P7",
        "P5",
        "REQUEST_VERIFIED_ROLLBACK",
        "rollback_request",
        True,
    ),
    "R04": (
        "P7",
        "P2",
        "RESTRICT_HIGH_RISK_COMMANDS",
        "command_gateway",
        False,
    ),
}


def valid_observation(cell_id: str) -> dict:
    contract = build_recovery_cell_effect_contract(
        PILOT,
        cell_id,
    )
    policy = contract["policy_evaluation"]
    artifacts = contract["event_artifacts"]
    family = contract["effect_dispatch"]["effect_family"]

    row = {
        "actual_effective_policy_id": (
            policy["actual_effective_policy_id"]
        ),
        "selected_action": policy["selected_action"],
        "event_slot_sha256": artifacts["tampered_sha256"],
        "post_response_slot_sha256": artifacts[
            "tampered_sha256"
        ],
        "rejected_sha256_absent": False,
        "temporary_recovery_state_absent": True,
        "rollback_request_emitted": False,
        "rollback_request_validated": False,
        "replacement_source_verified": False,
    }

    if family == "rollback_request":
        row.update(
            {
                "post_response_slot_sha256": artifacts[
                    "approved_sha256"
                ],
                "rejected_sha256_absent": True,
                "rollback_request_emitted": True,
                "rollback_request_validated": True,
                "replacement_source_verified": True,
            }
        )
    elif family == "command_gateway":
        row["command_gateway_observation"] = {
            "matched_attacker_probe_count": 2,
            "attacker_reset_marker_delta": 0,
            "authorized_noop_attempt_count": 1,
            "authorized_noop_marker_delta": 1,
        }

    return row


class RecoveryEffectContractTests(unittest.TestCase):
    def test_recovery_cells_are_frozen_r01_r04(self) -> None:
        self.assertEqual(
            tuple(
                row["cell_id"]
                for row in recovery_cells(PILOT)
            ),
            RECOVERY_CELL_IDS,
        )

    def test_recovery_policy_effect_matrix(self) -> None:
        matrix = build_recovery_effect_matrix(PILOT)
        actual = {}
        for row in matrix["rows"]:
            policy = row["policy_evaluation"]
            dispatch = row["effect_dispatch"]
            actual[row["cell_id"]] = (
                policy["requested_policy_id"],
                policy["actual_effective_policy_id"],
                policy["selected_action"],
                dispatch["effect_family"],
                dispatch[
                    "containment_expected_for_acceptance_only"
                ],
            )
        self.assertEqual(actual, EXPECTED)

    def test_recovery_artifact_identities_are_frozen(
        self,
    ) -> None:
        for cell_id in RECOVERY_CELL_IDS:
            row = build_recovery_cell_effect_contract(
                PILOT,
                cell_id,
            )
            artifacts = row["event_artifacts"]
            self.assertEqual(
                artifacts["approved_sha256"],
                (
                    "42945a2622fa351b3a3fdc31e002cbe326cb7a42"
                    "a958ee757f317abea67b6697"
                ),
            )
            self.assertEqual(
                artifacts["tampered_sha256"],
                (
                    "ff96d61205cc2c49b6d7d73fc36b9544c0deea79"
                    "d7a9304cc1fb9f1f8986053d"
                ),
            )
            self.assertFalse(
                artifacts[
                    "tampered_candidate_verification_accepted"
                ]
            )
            self.assertIn(
                "sha256_mismatch",
                artifacts[
                    "tampered_candidate_rejection_reasons"
                ],
            )

    def test_r01_is_observe_only_non_recovery(self) -> None:
        row = build_recovery_cell_effect_contract(
            PILOT,
            "R01",
        )
        self.assertEqual(
            row["effect_dispatch"]["effect_family"],
            "observe_only",
        )
        self.assertFalse(
            row["effect_dispatch"][
                "containment_expected_for_acceptance_only"
            ]
        )
        self.assertFalse(
            row["rollback_request_contract"]["expected"]
        )
        self.assertFalse(
            row["command_gateway_contract"]["required"]
        )

    def test_r02_r03_are_verified_rollback_effects(
        self,
    ) -> None:
        for cell_id in ("R02", "R03"):
            row = build_recovery_cell_effect_contract(
                PILOT,
                cell_id,
            )
            self.assertEqual(
                row["effect_dispatch"]["effect_family"],
                "rollback_request",
            )
            self.assertTrue(
                row["rollback_request_contract"]["expected"]
            )
            self.assertTrue(
                row["rollback_request_contract"][
                    "request_ready_for_acceptance_only"
                ]
            )
            self.assertFalse(
                row["rollback_request_contract"][
                    "recovery_execution_performed_offline"
                ]
            )
            self.assertTrue(
                row["effect_dispatch"][
                    "containment_expected_for_acceptance_only"
                ]
            )

    def test_r03_p7_dispatches_to_rollback_request(
        self,
    ) -> None:
        row = build_recovery_cell_effect_contract(
            PILOT,
            "R03",
        )
        self.assertEqual(
            row["p7_effect_plan"]["effect_family"],
            "rollback_request",
        )
        self.assertFalse(
            row["p7_effect_plan"]["oracle_ground_truth_read"]
        )

    def test_r04_p7_dispatches_to_command_gateway_not_rollback(
        self,
    ) -> None:
        row = build_recovery_cell_effect_contract(
            PILOT,
            "R04",
        )
        self.assertEqual(
            row["p7_effect_plan"]["effect_family"],
            "command_gateway",
        )
        self.assertEqual(
            row["policy_evaluation"]["selected_action"],
            "RESTRICT_HIGH_RISK_COMMANDS",
        )
        self.assertFalse(
            row["rollback_request_contract"]["expected"]
        )
        self.assertTrue(
            row["command_gateway_contract"]["required"]
        )
        self.assertEqual(
            row["command_gateway_contract"][
                "attacker_probe"
            ][
                "expected_cfs_reset_marker_delta_for_acceptance_only"
            ],
            0,
        )
        self.assertEqual(
            row["command_gateway_contract"][
                "authorized_probe"
            ][
                "expected_cfs_noop_marker_delta_for_acceptance_only"
            ],
            1,
        )
        self.assertFalse(
            row["effect_dispatch"][
                "containment_expected_for_acceptance_only"
            ]
        )

    def test_valid_effect_observations_accept_all_four_cells(
        self,
    ) -> None:
        expected_containment = {
            "R01": False,
            "R02": True,
            "R03": True,
            "R04": False,
        }
        for cell_id in RECOVERY_CELL_IDS:
            derived = derive_observed_recovery_effect(
                pilot=PILOT,
                cell_id=cell_id,
                observation=valid_observation(cell_id),
            )
            require_recovery_effect_acceptance(derived)
            self.assertTrue(
                derived["event_success_observed"]
            )
            self.assertEqual(
                derived["containment_predicate_observed"],
                expected_containment[cell_id],
            )
            self.assertTrue(
                derived[
                    "stage1_expected_effect_semantics_met"
                ]
            )
            self.assertFalse(
                derived["recovery_criteria_evaluated"]
            )
            self.assertFalse(
                derived["primary_metrics_emitted"]
            )
            self.assertFalse(
                derived["terminal_state_emitted"]
            )
            self.assertFalse(
                derived["trusted_recovery_evidence_emitted"]
            )

    def test_r01_accidental_rollback_is_rejected(
        self,
    ) -> None:
        row = valid_observation("R01")
        contract = build_recovery_cell_effect_contract(
            PILOT,
            "R01",
        )
        row.update(
            {
                "post_response_slot_sha256": contract[
                    "event_artifacts"
                ]["approved_sha256"],
                "rejected_sha256_absent": True,
                "rollback_request_emitted": True,
                "rollback_request_validated": True,
                "replacement_source_verified": True,
            }
        )
        derived = derive_observed_recovery_effect(
            pilot=PILOT,
            cell_id="R01",
            observation=row,
        )
        with self.assertRaises(ValueError):
            require_recovery_effect_acceptance(derived)

    def test_r04_accidental_rollback_is_rejected(
        self,
    ) -> None:
        row = valid_observation("R04")
        contract = build_recovery_cell_effect_contract(
            PILOT,
            "R04",
        )
        row.update(
            {
                "post_response_slot_sha256": contract[
                    "event_artifacts"
                ]["approved_sha256"],
                "rejected_sha256_absent": True,
                "rollback_request_emitted": True,
                "rollback_request_validated": True,
                "replacement_source_verified": True,
            }
        )
        derived = derive_observed_recovery_effect(
            pilot=PILOT,
            cell_id="R04",
            observation=row,
        )
        with self.assertRaises(ValueError):
            require_recovery_effect_acceptance(derived)

    def test_r02_missing_rollback_effect_is_rejected(
        self,
    ) -> None:
        row = valid_observation("R02")
        contract = build_recovery_cell_effect_contract(
            PILOT,
            "R02",
        )
        row.update(
            {
                "post_response_slot_sha256": contract[
                    "event_artifacts"
                ]["tampered_sha256"],
                "rejected_sha256_absent": False,
                "rollback_request_emitted": False,
                "rollback_request_validated": False,
                "replacement_source_verified": False,
            }
        )
        derived = derive_observed_recovery_effect(
            pilot=PILOT,
            cell_id="R02",
            observation=row,
        )
        with self.assertRaises(ValueError):
            require_recovery_effect_acceptance(derived)

    def test_policy_mismatch_is_rejected(self) -> None:
        row = valid_observation("R03")
        row["actual_effective_policy_id"] = "P2"
        derived = derive_observed_recovery_effect(
            pilot=PILOT,
            cell_id="R03",
            observation=row,
        )
        with self.assertRaises(ValueError):
            require_recovery_effect_acceptance(derived)

    def test_offline_matrix_crosses_no_runtime_or_pilot_boundary(
        self,
    ) -> None:
        matrix = build_recovery_effect_matrix(PILOT)
        self.assertFalse(
            matrix["runtime_execution_authorized"]
        )
        self.assertFalse(matrix["pilot_seed_consumed"])
        self.assertFalse(matrix["pilot_data_generated"])
        self.assertFalse(matrix["primary_metrics_emitted"])
        self.assertFalse(matrix["terminal_states_emitted"])
        self.assertFalse(
            matrix["trusted_recovery_evidence_emitted"]
        )


if __name__ == "__main__":
    unittest.main()
