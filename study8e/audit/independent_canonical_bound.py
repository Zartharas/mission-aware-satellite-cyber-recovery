from __future__ import annotations

from fractions import Fraction
from typing import Sequence

from study8.src.contact_recovery_model import PROFILE_OBJECTS


def independent_strict_sufficient_upper_bound_bps(
    profile: str,
    windows: Sequence[tuple[Fraction, Fraction]],
) -> int | None:
    """Independently compute the strict-before-window sufficient rate bound.

    For B modeled bytes and shortest positive window d_min, return the smallest
    positive integer rate r satisfying r > 8B/d_min. This is
    floor(8B/d_min) + 1, including the exact-divisibility case.
    """
    if not windows:
        return None
    durations = [end - start for start, end in windows]
    if any(duration <= 0 for duration in durations):
        raise ValueError("non-positive future window duration")
    shortest = min(durations)
    sizes = PROFILE_OBJECTS[profile]
    burden_bytes = sum(sizes.values()) + max(sizes.values())
    ratio = Fraction(8 * burden_bytes, 1) / shortest
    return max(1, ratio.numerator // ratio.denominator + 1)
