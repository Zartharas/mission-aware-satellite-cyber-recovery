"""Independent frozen truth-table oracle for S6X-EAP-001.

This module does not call cFS/LC code and is not a qualification-gate input.
It represents the prospectively frozen research-only correctness adjudicator
for the signed GT/GE equality-boundary fixture.
"""

from __future__ import annotations

FROZEN_CASES = {
    ("GT", -1, 0): False,
    ("GT", 0, 0): False,
    ("GT", 1, 0): True,
    ("GE", -1, 0): False,
    ("GE", 0, 0): True,
    ("GE", 1, 0): True,
}


def adjudicate(operator: str, wp_value: int, compare_value: int) -> bool:
    key = (operator, wp_value, compare_value)
    if key not in FROZEN_CASES:
        raise ValueError(f"case not in frozen S6X invariant: {key!r}")
    return FROZEN_CASES[key]


def expected_cases() -> dict[tuple[str, int, int], bool]:
    return dict(FROZEN_CASES)
