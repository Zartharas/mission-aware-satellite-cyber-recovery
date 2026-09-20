from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PRIMARY_PATH = ROOT / "study8e" / "src" / "external_trace_recovery_model.py"
REFERENCE_PATH = ROOT / "study8e" / "audit" / "independent_external_trace_reference.py"


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


primary = _load("study8e_primary", PRIMARY_PATH)
reference = _load("study8e_reference", REFERENCE_PATH)


def _windows(*pairs: tuple[int, int]):
    return tuple(primary.Window(a, b) for a, b in pairs)


class Study8EImplementationFreezeTests(unittest.TestCase):
    def test_profile_objects_are_loaded_from_frozen_study8_budget(self) -> None:
        self.assertEqual(sum(primary.PROFILE_OBJECTS["PROFILE_512_44"].values()), 12560)
        self.assertEqual(sum(primary.PROFILE_OBJECTS["PROFILE_768_65"].values()), 17460)
        self.assertEqual(sum(primary.PROFILE_OBJECTS["PROFILE_1024_87"].values()), 24236)

    def test_window_union_and_horizon_clipping(self) -> None:
        raw = _windows(
            (0, 100),
            (100, 200),
            (150, 250),
            (400, 600),
            (700, 900),
        )
        self.assertEqual(
            primary.merge_windows(raw),
            (primary.Window(0, 250), primary.Window(400, 600), primary.Window(700, 900)),
        )
        self.assertEqual(
            primary.effective_windows(raw, 500),
            (primary.Window(0, 250), primary.Window(400, 500)),
        )

    def test_zero_capacity_window_is_not_consumed_or_disruption_triggered(self) -> None:
        case = primary.ExternalCase(
            profile="PROFILE_512_44",
            policy="P1_STAGED_CUTOVER",
            disruption="A2_DELAY_FIRST_TRANSITION_PROOF_ONE_CONTACT",
            horizon_us=3_000_000,
            rate_bps=1,
            windows=_windows((0, 1), (1_000_000, 2_000_000)),
        )
        row = primary.evaluate_case(case)
        self.assertEqual(row["observation_opportunities_consumed"], 1)
        self.assertEqual(row["trusted_recovery_success"], 0)

    def test_exact_simple_minimum_rate(self) -> None:
        profile = "PROFILE_512_44"
        total_bytes = sum(primary.PROFILE_OBJECTS[profile].values())
        expected = total_bytes * 8
        result = primary.minimum_success_rate_bps(
            profile=profile,
            policy="P1_STAGED_CUTOVER",
            disruption="A0_NONE",
            horizon_us=2_000_000,
            windows=_windows((0, 1_000_000)),
        )
        self.assertEqual(result["status"], "FINITE_THRESHOLD")
        self.assertEqual(result["minimum_rate_bps"], expected)

        fail = primary.evaluate_case(
            primary.ExternalCase(
                profile=profile,
                policy="P1_STAGED_CUTOVER",
                disruption="A0_NONE",
                horizon_us=2_000_000,
                rate_bps=expected - 1,
                windows=_windows((0, 1_000_000)),
            )
        )
        success = primary.evaluate_case(
            primary.ExternalCase(
                profile=profile,
                policy="P1_STAGED_CUTOVER",
                disruption="A0_NONE",
                horizon_us=2_000_000,
                rate_bps=expected,
                windows=_windows((0, 1_000_000)),
            )
        )
        self.assertEqual(fail["trusted_recovery_success"], 0)
        self.assertEqual(success["trusted_recovery_success"], 1)

    def test_strict_horizon_boundary(self) -> None:
        profile = "PROFILE_512_44"
        total_bits = sum(primary.PROFILE_OBJECTS[profile].values()) * 8
        exact = primary.evaluate_case(
            primary.ExternalCase(
                profile=profile,
                policy="P1_STAGED_CUTOVER",
                disruption="A0_NONE",
                horizon_us=1_000_000,
                rate_bps=total_bits,
                windows=_windows((0, 1_000_000)),
            )
        )
        just_above = primary.evaluate_case(
            primary.ExternalCase(
                profile=profile,
                policy="P1_STAGED_CUTOVER",
                disruption="A0_NONE",
                horizon_us=1_000_000,
                rate_bps=total_bits + 1,
                windows=_windows((0, 1_000_000)),
            )
        )
        self.assertEqual(exact["recovery_completion_us"], 1_000_000)
        self.assertEqual(exact["trusted_recovery_success"], 0)
        self.assertEqual(exact["terminal_state"], "RECOVERY_DEADLINE_EXCEEDED")
        self.assertEqual(just_above["trusted_recovery_success"], 1)

    def test_p3_guard_blocks_when_commit_plus_confirmation_cannot_fit(self) -> None:
        case = primary.ExternalCase(
            profile="PROFILE_512_44",
            policy="P3_CONTACT_AWARE_STAGED",
            disruption="A0_NONE",
            horizon_us=2_000_000,
            rate_bps=64_000,
            windows=_windows((0, 1_000_000)),
        )
        row = primary.evaluate_case(case)
        self.assertEqual(row["p3_guard_blocked"], 1)
        self.assertEqual(row["terminal_state"], "CONTACT_BUDGET_EXHAUSTED")
        self.assertEqual(row["trusted_recovery_success"], 0)

    def test_a2_and_a3_require_later_positive_capacity_opportunity(self) -> None:
        windows = _windows((0, 1_000_000), (2_000_000, 3_000_000))
        for disruption in (
            "A2_DELAY_FIRST_TRANSITION_PROOF_ONE_CONTACT",
            "A3_STALE_EPOCH_REPLAY_AT_COMMIT",
        ):
            row = primary.evaluate_case(
                primary.ExternalCase(
                    profile="PROFILE_512_44",
                    policy="P1_STAGED_CUTOVER",
                    disruption=disruption,
                    horizon_us=4_000_000,
                    rate_bps=1_000_000,
                    windows=windows,
                )
            )
            self.assertEqual(row["trusted_recovery_success"], 1)
            self.assertEqual(row["observation_opportunities_consumed"], 2)

    def test_a1_consumes_bytes_without_delivering_first_largest_fragment(self) -> None:
        sizes = primary.PROFILE_OBJECTS["PROFILE_512_44"]
        total = sum(sizes.values())
        largest = max(sizes.values())
        row = primary.evaluate_case(
            primary.ExternalCase(
                profile="PROFILE_512_44",
                policy="P1_STAGED_CUTOVER",
                disruption="A1_DROP_FIRST_LARGEST_OBJECT_FRAGMENT",
                horizon_us=2_000_000,
                rate_bps=(total + largest) * 8,
                windows=_windows((0, 1_000_000)),
            )
        )
        self.assertEqual(row["trusted_recovery_success"], 1)
        self.assertEqual(row["cryptographic_bytes_transferred"], total + largest)

    def test_primary_and_independent_reference_parity(self) -> None:
        fixtures = [
            (
                "PROFILE_512_44",
                "P0_HARD_CUTOVER",
                "A0_NONE",
                4_000_000,
                250_000,
                ((200_000, 1_000_000), (1_500_000, 2_100_000)),
            ),
            (
                "PROFILE_512_44",
                "P1_STAGED_CUTOVER",
                "A1_DROP_FIRST_LARGEST_OBJECT_FRAGMENT",
                5_000_000,
                300_000,
                ((100_000, 1_100_000), (2_000_000, 3_000_000)),
            ),
            (
                "PROFILE_768_65",
                "P2_HYBRID_OVERLAP",
                "A2_DELAY_FIRST_TRANSITION_PROOF_ONE_CONTACT",
                6_000_000,
                800_000,
                ((0, 1_000_000), (1_500_000, 2_500_000), (4_000_000, 5_000_000)),
            ),
            (
                "PROFILE_1024_87",
                "P3_CONTACT_AWARE_STAGED",
                "A3_STALE_EPOCH_REPLAY_AT_COMMIT",
                8_000_000,
                1_500_000,
                ((250_000, 1_250_000), (2_000_000, 3_000_000), (5_000_000, 6_500_000)),
            ),
            (
                "PROFILE_512_44",
                "P3_CONTACT_AWARE_STAGED",
                "A0_NONE",
                2_000_000,
                64_000,
                ((0, 1_000_000),),
            ),
        ]

        for profile, policy, disruption, horizon, rate, raw in fixtures:
            actual = primary.evaluate_case(
                primary.ExternalCase(
                    profile=profile,
                    policy=policy,
                    disruption=disruption,
                    horizon_us=horizon,
                    rate_bps=rate,
                    windows=tuple(primary.Window(a, b) for a, b in raw),
                )
            )
            expected = reference.independently_evaluate(
                profile=profile,
                policy=policy,
                disruption=disruption,
                horizon_us=horizon,
                rate_bps=rate,
                windows=tuple(raw),
            )
            self.assertEqual(actual, expected)

    def test_minimum_rate_solver_matches_local_bruteforce_neighborhood(self) -> None:
        profile = "PROFILE_512_44"
        total_bits = sum(primary.PROFILE_OBJECTS[profile].values()) * 8
        result = primary.minimum_success_rate_bps(
            profile=profile,
            policy="P1_STAGED_CUTOVER",
            disruption="A0_NONE",
            horizon_us=2_000_000,
            windows=_windows((0, 1_000_000)),
        )
        found = result["minimum_rate_bps"]
        self.assertIsInstance(found, int)
        for rate in range(total_bits - 4, total_bits):
            row = primary.evaluate_case(
                primary.ExternalCase(
                    profile=profile,
                    policy="P1_STAGED_CUTOVER",
                    disruption="A0_NONE",
                    horizon_us=2_000_000,
                    rate_bps=rate,
                    windows=_windows((0, 1_000_000)),
                )
            )
            self.assertEqual(row["trusted_recovery_success"], 0)
        self.assertEqual(found, total_bits)

    def test_direct_entrypoints_refuse_canonical_execution(self) -> None:
        self.assertIn(
            "canonical external-trace execution is not authorized",
            PRIMARY_PATH.read_text(encoding="utf-8"),
        )
        self.assertIn(
            "canonical external-trace audit execution is not authorized",
            REFERENCE_PATH.read_text(encoding="utf-8"),
        )


if __name__ == "__main__":
    unittest.main()
