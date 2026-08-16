from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNNER = (ROOT / "scripts" / "run_nominal_runtime_preflight.sh").read_text(encoding="utf-8")


class NominalRuntimeStartupContractTests(unittest.TestCase):
    def test_fortytwo_listeners_precede_truth_consumer(self) -> None:
        start_42 = RUNNER.index("start fortytwo fortytwo")
        wait_9999 = RUNNER.index(
            'wait_for_tcp_listener "$PREFIX-fortytwo" 9999 75 '
            "fortytwo_tcp_9999_listener"
        )
        wait_4286 = RUNNER.index(
            'wait_for_tcp_listener "$PREFIX-fortytwo" 4286 75 '
            "fortytwo_tcp_4286_listener"
        )
        truth_start = RUNNER.index("start truth-sink truth-sink")
        self.assertLess(start_42, wait_9999)
        self.assertLess(wait_9999, wait_4286)
        self.assertLess(wait_4286, truth_start)

    def test_truth_sink_connects_before_hardware_sims(self) -> None:
        truth_start = RUNNER.index("start truth-sink truth-sink")
        truth_ready = RUNNER.index(
            'wait_for_log_marker "$PREFIX-truth-sink" '
            "TRUTH_SINK_CONNECTED 30 truth_sink_connection"
        )
        hardware = RUNNER.index('for sim in "${HARDWARE_SIMS[@]}"')
        self.assertLess(truth_start, truth_ready)
        self.assertLess(truth_ready, hardware)

    def test_radio_readiness_still_follows_hardware_launch(self) -> None:
        hardware = RUNNER.index('for sim in "${HARDWARE_SIMS[@]}"')
        radio_ready = RUNNER.index(
            'wait_for_tcp_listener "$PREFIX-generic-radio-sim" '
            "8010 45 radio_tcp_8010_listener"
        )
        self.assertLess(hardware, radio_ready)

    def test_truth_sink_readiness_has_single_gate(self) -> None:
        marker = 'wait_for_log_marker "$PREFIX-truth-sink" TRUTH_SINK_CONNECTED'
        self.assertEqual(RUNNER.count(marker), 1)


if __name__ == "__main__":
    unittest.main()
