from __future__ import annotations

import unittest
from fractions import Fraction

from study8.src.contact_recovery_model import PROFILE_OBJECTS
from study8e.src.external_contact_recovery_model import (
    ExternalCase,
    Window,
    evaluate_case,
    minimum_integer_rate_bps,
    normalize_windows,
)


class ExternalContactRecoveryModelTests(unittest.TestCase):
    def test_union_overlapping_and_abutting_windows(self) -> None:
        result = normalize_windows(
            [(0, 10), (10, 20), (19, 30), (40, 50)]
        )
        self.assertEqual(
            result,
            (
                Window(Fraction(0), Fraction(30)),
                Window(Fraction(40), Fraction(50)),
            ),
        )

    def test_same_window_chaining_restores_trust(self) -> None:
        case = ExternalCase(
            "PROFILE_512_44",
            "P1_STAGED_CUTOVER",
            "A0_NONE",
            Fraction(20),
            10_000,
        )
        result = evaluate_case(case, [(0, 20)])
        self.assertEqual(result["trusted_recovery_success"], 1)
        self.assertEqual(result["terminal_state"], "TRUST_RESTORED")
        self.assertEqual(result["windows_consumed"], 1)
        self.assertEqual(
            result["cryptographic_bytes_transferred"],
            sum(PROFILE_OBJECTS["PROFILE_512_44"].values()),
        )
        self.assertLess(result["recovery_completion_time_s"], Fraction(20))

    def test_strict_horizon_boundary_is_failure(self) -> None:
        total = sum(PROFILE_OBJECTS["PROFILE_512_44"].values())
        rate = total * 8 // 10
        self.assertEqual(rate, 10_048)
        case = ExternalCase(
            "PROFILE_512_44",
            "P1_STAGED_CUTOVER",
            "A0_NONE",
            Fraction(10),
            rate,
        )
        result = evaluate_case(case, [(0, 10)])
        self.assertEqual(result["recovery_completion_time_s"], Fraction(10))
        self.assertEqual(result["trusted_recovery_success"], 0)
        self.assertEqual(
            result["terminal_state"],
            "RECOVERY_DEADLINE_EXCEEDED",
        )

    def test_a1_drops_first_largest_fragment_then_recovers(self) -> None:
        sizes = PROFILE_OBJECTS["PROFILE_512_44"]
        case = ExternalCase(
            "PROFILE_512_44",
            "P1_STAGED_CUTOVER",
            "A1_DROP_FIRST_LARGEST_OBJECT_FRAGMENT",
            Fraction(30),
            10_000,
        )
        result = evaluate_case(case, [(0, 30)])
        self.assertEqual(result["trusted_recovery_success"], 1)
        self.assertEqual(
            result["cryptographic_bytes_transferred"],
            sum(sizes.values()) + max(sizes.values()),
        )

    def test_a2_consumes_first_proof_opportunity_window(self) -> None:
        case = ExternalCase(
            "PROFILE_512_44",
            "P1_STAGED_CUTOVER",
            "A2_DELAY_FIRST_TRANSITION_PROOF_ONE_CONTACT",
            Fraction(40),
            10_000,
        )
        result = evaluate_case(case, [(0, 10), (20, 40)])
        self.assertEqual(result["trusted_recovery_success"], 1)
        self.assertEqual(result["windows_consumed"], 2)
        self.assertGreaterEqual(
            result["proof_accepted_time_s"],
            Fraction(20),
        )

    def test_a3_consumes_first_commit_opportunity_and_retries(self) -> None:
        case = ExternalCase(
            "PROFILE_512_44",
            "P1_STAGED_CUTOVER",
            "A3_STALE_EPOCH_REPLAY_AT_COMMIT",
            Fraction(40),
            10_000,
        )
        result = evaluate_case(case, [(0, 10), (20, 40)])
        self.assertEqual(result["trusted_recovery_success"], 1)
        self.assertEqual(result["transition_attempts"], 2)
        self.assertGreaterEqual(result["commit_time_s"], Fraction(20))
        self.assertEqual(result["stale_epoch_acceptance"], 0)

    def test_p3_guard_blocks_when_commit_plus_confirmation_cannot_fit(self) -> None:
        windows = [(0, 7)]
        p1 = evaluate_case(
            ExternalCase(
                "PROFILE_512_44",
                "P1_STAGED_CUTOVER",
                "A0_NONE",
                Fraction(7),
                10_000,
            ),
            windows,
        )
        p3 = evaluate_case(
            ExternalCase(
                "PROFILE_512_44",
                "P3_CONTACT_AWARE_STAGED",
                "A0_NONE",
                Fraction(7),
                10_000,
            ),
            windows,
        )
        self.assertEqual(p3["p3_guard_blocked"], 1)
        self.assertEqual(
            p3["terminal_state"],
            "CONTACT_BUDGET_EXHAUSTED",
        )
        self.assertNotEqual(p1["terminal_state"], p3["terminal_state"])
        self.assertEqual(p1["trusted_recovery_success"], 0)
        self.assertEqual(p3["trusted_recovery_success"], 0)

    def test_p1_and_p3_same_success_when_capacity_sufficient(self) -> None:
        windows = [(0, 20)]
        results = []
        for policy in (
            "P1_STAGED_CUTOVER",
            "P3_CONTACT_AWARE_STAGED",
        ):
            results.append(
                evaluate_case(
                    ExternalCase(
                        "PROFILE_512_44",
                        policy,
                        "A0_NONE",
                        Fraction(20),
                        10_000,
                    ),
                    windows,
                )
            )
        self.assertEqual(
            [r["trusted_recovery_success"] for r in results],
            [1, 1],
        )

    def test_minimum_integer_rate_strict_boundary(self) -> None:
        threshold = minimum_integer_rate_bps(
            profile="PROFILE_512_44",
            policy="P1_STAGED_CUTOVER",
            disruption="A0_NONE",
            horizon_s=20,
            windows=[(0, 20)],
            max_rate_bps=20_000,
        )
        self.assertEqual(threshold, 5_025)

    def test_a2_single_window_has_no_finite_threshold_within_bound(self) -> None:
        threshold = minimum_integer_rate_bps(
            profile="PROFILE_512_44",
            policy="P1_STAGED_CUTOVER",
            disruption="A2_DELAY_FIRST_TRANSITION_PROOF_ONE_CONTACT",
            horizon_s=20,
            windows=[(0, 20)],
            max_rate_bps=10_000_000,
        )
        self.assertIsNone(threshold)


if __name__ == "__main__":
    unittest.main()
