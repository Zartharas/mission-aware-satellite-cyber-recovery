from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from temporal_model import Cell, ONSET_PHASES, cells, run_population, run_trajectory, trajectory_specs  # noqa: E402


class Study3TemporalModelTests(unittest.TestCase):
    def test_exact_matrix_and_population(self) -> None:
        self.assertEqual(len(cells()), 30)
        self.assertEqual(len(trajectory_specs()), 1380)
        self.assertEqual(len(ONSET_PHASES), 46)

    def test_v0_never_false_qualifies_after_onset(self) -> None:
        _, summaries = run_population()
        for row in summaries:
            if row.evidence == "V0":
                self.assertEqual(row.unsafe_qualified_epochs, 0, row.trajectory_id)

    def test_v4_never_false_qualifies_after_onset(self) -> None:
        _, summaries = run_population()
        for row in summaries:
            if row.evidence == "V4":
                self.assertEqual(row.unsafe_qualified_epochs, 0, row.trajectory_id)

    def test_v5_persistent_exposes_false_qualification_for_gate_entering_policies(self) -> None:
        _, summaries = run_population()
        selected = [
            row for row in summaries
            if row.evidence == "V5"
            and row.persistence == "PERSISTENT"
            and row.policy in {"S2_B0_FAIL_CLOSED", "S2_S1_EVIDENCE_AWARE"}
        ]
        self.assertTrue(selected)
        self.assertTrue(any(row.unsafe_qualified_epochs > 0 for row in selected))

    def test_one_shot_affects_exactly_one_received_post_onset_record(self) -> None:
        _, summaries = run_population()
        for row in summaries:
            if row.persistence == "ONE_SHOT":
                self.assertEqual(row.affected_received_records, 1, row.trajectory_id)

    def test_no_false_qualification_before_onset(self) -> None:
        epochs, _ = run_population()
        for row in epochs:
            if row.t_s < row.onset_s:
                self.assertFalse(row.unsafe_qualified, row.trajectory_id)
                self.assertFalse(row.unsafe_permissive, row.trajectory_id)

    def test_k4_never_has_contact_outside_frozen_windows(self) -> None:
        epochs, _ = run_trajectory(
            Cell("K4", "V5", "PERSISTENT", "S2_S1_EVIDENCE_AWARE"),
            10,
        )
        for row in epochs:
            expected = (
                25 <= row.t_s <= 35
                or 75 <= row.t_s <= 90
                or 145 <= row.t_s <= 165
                or 220 <= row.t_s <= 240
            )
            self.assertEqual(row.contact_available, expected)

    def test_b2_is_protective_after_security_signal_when_evidence_is_qualified(self) -> None:
        epochs, _ = run_trajectory(
            Cell("K0", "V5", "PERSISTENT", "S2_B2_RISK_THRESHOLD"),
            10,
        )
        for row in epochs:
            if row.t_s >= 10 and row.evidence_qualified:
                self.assertEqual(row.action, "RESTRICT_AND_REQUEST_AUTHORIZATION")
                self.assertFalse(row.unsafe_qualified)


if __name__ == "__main__":
    unittest.main()
