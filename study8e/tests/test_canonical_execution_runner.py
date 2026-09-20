from __future__ import annotations

import unittest
from fractions import Fraction

from study8.src.contact_recovery_model import PROFILE_OBJECTS
from study8e.analysis.run_canonical_execution import (
    Anchor,
    MergedWindow,
    RawObservation,
    build_anchors,
    ceil_fraction,
    format_utc_microseconds,
    median_fraction,
    merge_trace_windows,
    parse_utc_microseconds,
    reference_threshold,
    relative_future_windows,
    sufficient_upper_bound_bps,
)
from study8e.src.external_contact_recovery_model import minimum_integer_rate_bps


class CanonicalExecutionRunnerTests(unittest.TestCase):
    def test_utc_microsecond_roundtrip(self) -> None:
        text = "2026-06-15T12:34:56.123456Z"
        value = parse_utc_microseconds(text)
        self.assertEqual(format_utc_microseconds(value), text)

    def test_rejects_more_than_microsecond_precision(self) -> None:
        with self.assertRaises(Exception):
            parse_utc_microseconds("2026-06-15T12:34:56.1234567Z")

    def test_merge_overlapping_and_abutting_windows(self) -> None:
        rows = [
            RawObservation(1, 3, 20, 30, 9, 42),
            RawObservation(1, 1, 0, 10, 9, 42),
            RawObservation(1, 2, 10, 25, 9, 42),
            RawObservation(1, 4, 40, 50, 9, 42),
        ]
        merged = merge_trace_windows(rows)
        self.assertEqual(len(merged), 2)
        self.assertEqual((merged[0].start_us, merged[0].end_us), (0, 30))
        self.assertEqual(merged[0].observation_ids, (1, 2, 3))
        self.assertEqual((merged[1].start_us, merged[1].end_us), (40, 50))

    def test_anchor_requires_complete_24h_source_followup(self) -> None:
        source_end = parse_utc_microseconds("2026-07-01T00:00:00Z")
        day = 24 * 3600 * 1_000_000
        windows = [
            MergedWindow(
                selection_order=1,
                norad_cat_id=42,
                ground_station=9,
                merged_index=1,
                start_us=source_end - 3 * day,
                end_us=source_end - 2 * day,
                observation_ids=(1,),
            ),
            MergedWindow(
                selection_order=1,
                norad_cat_id=42,
                ground_station=9,
                merged_index=2,
                start_us=source_end - day,
                end_us=source_end - day // 2,
                observation_ids=(2,),
            ),
        ]
        anchors = build_anchors({1: windows}, source_end)
        self.assertEqual(len(anchors), 1)
        self.assertEqual(anchors[0].merged_window_index, 1)

    def test_future_windows_exclude_anchor_window(self) -> None:
        anchor = Anchor(1, 42, 9, 1, "TRACE01-A001", 10_000_000, 1)
        windows = [
            MergedWindow(1, 42, 9, 1, 0, 10_000_000, (1,)),
            MergedWindow(1, 42, 9, 2, 20_000_000, 30_000_000, (2,)),
        ]
        future = relative_future_windows(
            anchor=anchor,
            merged_windows=windows,
            horizon_hours=1,
        )
        self.assertEqual(future, [(Fraction(10), Fraction(20))])

    def test_sufficient_bound_carries_a1_byte_burden(self) -> None:
        windows = [(Fraction(0), Fraction(2))]
        bound = sufficient_upper_bound_bps("PROFILE_512_44", windows)
        self.assertIsNotNone(bound)
        sizes = PROFILE_OBJECTS["PROFILE_512_44"]
        burden = sum(sizes.values()) + max(sizes.values())
        self.assertGreaterEqual((bound * 2) // 8, burden)

    def test_reference_and_primary_threshold_agree(self) -> None:
        windows = [(Fraction(0), Fraction(20))]
        profile = "PROFILE_512_44"
        upper = sufficient_upper_bound_bps(profile, windows)
        self.assertIsNotNone(upper)
        primary = minimum_integer_rate_bps(
            profile=profile,
            policy="P1_STAGED_CUTOVER",
            disruption="A0_NONE",
            horizon_s=Fraction(20),
            windows=windows,
            max_rate_bps=upper,
        )
        reference = reference_threshold(
            profile=profile,
            policy="P1_STAGED_CUTOVER",
            disruption="A0_NONE",
            horizon_s=Fraction(20),
            windows=windows,
            upper_bound_bps=upper,
        )
        self.assertEqual(primary, 5025)
        self.assertEqual(reference, primary)

    def test_exact_median(self) -> None:
        self.assertEqual(
            median_fraction([Fraction(1), Fraction(4)]),
            Fraction(5, 2),
        )
        self.assertEqual(
            median_fraction([Fraction(3), Fraction(1), Fraction(2)]),
            Fraction(2),
        )

    def test_ceil_fraction(self) -> None:
        self.assertEqual(ceil_fraction(Fraction(10, 3)), 4)
        self.assertEqual(ceil_fraction(Fraction(9, 3)), 3)


if __name__ == "__main__":
    unittest.main()
