from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNNER = (
    ROOT / "scripts" / "run_nominal_runtime_preflight.sh"
).read_text(encoding="utf-8")


class NominalRuntimeStartupContractTests(unittest.TestCase):
    def test_blocking_ipc_sequence_is_frozen(self) -> None:
        expected = (
            'EXPECTED_FORTYTWO_BLOCKING_IPC_SEQUENCE='
            '"4278,4277,4378,4377,4478,4477,4279,4280,'
            '4245,4227,4234,9999,4284,4281,4282,4283,4286"'
        )
        self.assertIn(expected, RUNNER)
        self.assertIn(
            "fortytwo_blocking_ipc_sequence_verified true",
            RUNNER,
        )

    def test_reaction_wheel_pairs_progress_in_42_order(self) -> None:
        ordered = [
            'wait_for_tcp_listener "$PREFIX-fortytwo" 4278 30',
            "start_hardware_sim generic-reactionwheel-sim0",
            'wait_for_tcp_listener "$PREFIX-fortytwo" 4378 30',
            "start_hardware_sim generic-reactionwheel-sim1",
            'wait_for_tcp_listener "$PREFIX-fortytwo" 4478 30',
            "start_hardware_sim generic-reactionwheel-sim2",
            'wait_for_tcp_listener "$PREFIX-fortytwo" 4279 30',
        ]
        positions = [RUNNER.index(token) for token in ordered]
        self.assertEqual(positions, sorted(positions))

    def test_truth_sink_satisfies_only_9999_dependency(self) -> None:
        ordered = [
            'wait_for_tcp_listener "$PREFIX-fortytwo" 9999 30',
            "start truth-sink truth-sink",
            'wait_for_log_marker "$PREFIX-truth-sink" '
            "TRUTH_SINK_CONNECTED 30 truth_sink_connection",
            'wait_for_tcp_listener "$PREFIX-fortytwo" 4284 30',
        ]
        positions = [RUNNER.index(token) for token in ordered]
        self.assertEqual(positions, sorted(positions))
        self.assertEqual(
            RUNNER.count(
                'wait_for_log_marker "$PREFIX-truth-sink" '
                "TRUTH_SINK_CONNECTED"
            ),
            1,
        )

    def test_radio_is_last_42_client_and_r023_waits_are_absent(self) -> None:
        ordered = [
            'wait_for_tcp_listener "$PREFIX-fortytwo" 4286 30',
            "start_hardware_sim generic-radio-sim",
            "start_hardware_sim sample-sim",
            'wait_for_tcp_listener "$PREFIX-generic-radio-sim" '
            "8010 45 radio_tcp_8010_listener",
        ]
        positions = [RUNNER.index(token) for token in ordered]
        self.assertEqual(positions, sorted(positions))
        self.assertNotIn(
            'wait_for_tcp_listener "$PREFIX-fortytwo" 9999 75',
            RUNNER,
        )
        self.assertNotIn(
            'wait_for_tcp_listener "$PREFIX-fortytwo" 4286 75',
            RUNNER,
        )


if __name__ == "__main__":
    unittest.main()
