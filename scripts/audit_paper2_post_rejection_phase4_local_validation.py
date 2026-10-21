#!/usr/bin/env python3
"""Fail-closed audit for Paper-2 Phase-4 local-validation tooling."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
S3X = ROOT / "study3x"
S6X = ROOT / "study6x"
REBUILD = ROOT / "publication/Paper_2_Studies_3_4_6/Post_Rejection_Rebuild"


def fail(message: str) -> None:
    print(f"[FAIL] {message}", file=sys.stderr)
    raise SystemExit(1)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def main() -> int:
    gate = REBUILD / "PHASE4_LOCAL_VALIDATION_GATE_R1_2026-09-26.md"
    require(gate.is_file(), "Phase-4 gate record missing")

    s3_runner = S3X / "validation/acquire_verify_freeze_esa_v2.sh"
    s6_runner = S6X / "validation/materialize_validate_cfs_v701.sh"
    require(s3_runner.is_file(), "S3X acquisition/source-freeze wrapper missing")
    require(s6_runner.is_file(), "S6X pre-runtime materialization wrapper missing")

    s3 = s3_runner.read_text(encoding="utf-8")
    for marker in (
        "15237121/files/ESA-Mission1.zip?download=1",
        "15237121/files/ESA-Mission2.zip?download=1",
        "3776246073",
        "4098539932",
        "9770ad12ed730238f37c42d5c27ab436",
        "bfc72012691427d9327eb41f726ce45e",
        "run_local_source_freeze.sh",
        "scientific_execution=NO",
    ):
        require(marker in s3, f"S3X wrapper missing marker: {marker}")

    s6 = s6_runner.read_text(encoding="utf-8")
    for marker in (
        "--branch v7.0.1",
        "apps/lc",
        "088b2fa828db9ff7e00733f1908e0eeb59f66ce3",
        "a1c3a47ea1fa5c0d7751d6ff88848dc9bd8a6c7a",
        "test_invariant_oracle",
        "validate_local_cfs_pin.py",
        "fixture_patch_applied=NO",
        "build_executed=NO",
        "scientific_execution=NO",
    ):
        require(marker in s6, f"S6X wrapper missing marker: {marker}")

    for forbidden in (
        S3X / "results",
        S3X / "canonical",
        S6X / "results",
        S6X / "canonical",
        S6X / "build",
    ):
        require(not forbidden.exists(), f"forbidden scientific/pre-build path exists: {forbidden.relative_to(ROOT)}")

    print("paper2_phase4_local_validation_tooling_audit=PASS")
    print("s3x_local_source_freeze_execution_in_repo=NO")
    print("s3x_gap_rule_freeze_authorized=NO")
    print("s6x_build_authorized=NO")
    print("s6x_scientific_execution_authorized=NO")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
