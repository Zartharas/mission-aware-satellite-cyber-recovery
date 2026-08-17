from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNNER = (
    ROOT / "scripts" / "run_wp8_observability_binding_preflight.sh"
).read_text(encoding="utf-8")


class ObservabilityMeasurementContractTests(unittest.TestCase):
    def test_nominal_destination_settles_before_e4_ownership(self) -> None:
        nominal = RUNNER.index(
            "nominal_tolab_destination_settle=PASS"
        )
        enable = RUNNER.index(
            'run_e4_adapter "$(basename "$ENABLE_JSON")" '
            "enable-output --destination e4-proxy"
        )
        ownership = RUNNER.index(
            "e4_tolab_destination_ownership=PASS"
        )
        self.assertLess(nominal, enable)
        self.assertLess(enable, ownership)

    def test_destination_stability_guard_is_present(self) -> None:
        self.assertIn(
            "assert_e4_destination_stable()",
            RUNNER,
        )
        self.assertGreaterEqual(
            RUNNER.count("assert_e4_destination_stable"),
            5,
        )
        self.assertIn(
            "expected_destination=e4-proxy",
            RUNNER,
        )

    def test_post_enforcement_metric_predicate_is_unchanged(self) -> None:
        self.assertIn(
            'test "$POST_TRUTH_AFTER" -eq '
            '$((POST_TRUTH_BEFORE + 1))',
            RUNNER,
        )
        self.assertIn(
            'test "$POST_POLICY_AFTER" -eq '
            '"$POST_POLICY_BEFORE"',
            RUNNER,
        )

    def test_nominal_active_gs_marker_precedes_event(self) -> None:
        settle = RUNNER.index(
            'PHASE="NOMINAL_TOLAB_DESTINATION_SETTLE"'
        )
        event = RUNNER.index(
            'PHASE="EVENT_ACTIVATION"'
        )
        self.assertLess(settle, event)
        self.assertIn(
            "nominal_tolab_destination=active-gs",
            RUNNER,
        )


if __name__ == "__main__":
    unittest.main()
