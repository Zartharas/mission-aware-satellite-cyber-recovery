#!/usr/bin/env python3
"""Pre-runtime validation of a local cFS v7.0.1 checkout for S6X.

This utility performs static source-identity and patch dry-run checks only.
It does not build cFS, apply the fixture, sign artifacts, or execute S6X.
"""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

CFS_COMMIT = "088b2fa828db9ff7e00733f1908e0eeb59f66ce3"
LC_COMMIT = "a1c3a47ea1fa5c0d7751d6ff88848dc9bd8a6c7a"

EXPECTED_BLOBS = {
    "fsw/src/lc_watch.c": "67e8bb9d6270a1c5251343f08fa8e67717b7049f",
    "docs/lc_FunctionalRequirements.csv": "22b5af26c37d7687a620b4997c3bd71a5871142e",
    "unit-test/lc_watch_tests.c": "18a18d6099150146a5a02644aaebb298de261f52",
    "README.md": "4ea5537d4c0965030a14d6aff637820a4331cc89",
}


def run(cwd: Path, *args: str) -> str:
    result = subprocess.run(
        args,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise SystemExit(
            f"command failed in {cwd}: {' '.join(args)}\n{result.stderr.strip()}"
        )
    return result.stdout.strip()


def require_clean_git(path: Path, label: str) -> None:
    dirty = run(path, "git", "status", "--porcelain")
    if dirty:
        raise SystemExit(f"{label} checkout is not clean:\n{dirty}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("cfs_checkout", type=Path)
    parser.add_argument(
        "--fixture-patch",
        type=Path,
        default=Path(__file__).resolve().parents[1]
        / "fixtures"
        / "S6X_FIXTURE_GT_EQ_BOUNDARY_001.patch",
    )
    args = parser.parse_args()

    cfs = args.cfs_checkout.resolve()
    if not (cfs / ".git").exists():
        raise SystemExit(f"not a Git checkout: {cfs}")

    cfs_head = run(cfs, "git", "rev-parse", "HEAD")
    if cfs_head != CFS_COMMIT:
        raise SystemExit(f"cFS HEAD mismatch: expected {CFS_COMMIT}, got {cfs_head}")
    require_clean_git(cfs, "cFS")

    lc = cfs / "apps" / "lc"
    if not lc.is_dir():
        raise SystemExit("apps/lc submodule is not initialized")

    lc_head = run(lc, "git", "rev-parse", "HEAD")
    if lc_head != LC_COMMIT:
        raise SystemExit(f"LC HEAD mismatch: expected {LC_COMMIT}, got {lc_head}")
    require_clean_git(lc, "LC")

    for rel, expected_blob in EXPECTED_BLOBS.items():
        actual = run(lc, "git", "hash-object", rel)
        if actual != expected_blob:
            raise SystemExit(
                f"LC blob mismatch for {rel}: expected {expected_blob}, got {actual}"
            )

    source = (lc / "fsw/src/lc_watch.c").read_text(encoding="utf-8")
    baseline = "EvalResult = (WPValue > CompareValue) ? LC_WATCH_TRUE : LC_WATCH_FALSE;"
    ge = "EvalResult = (WPValue >= CompareValue) ? LC_WATCH_TRUE : LC_WATCH_FALSE;"
    if source.count(baseline) != 1:
        raise SystemExit("baseline GT expression count is not exactly one")
    if source.count(ge) < 1:
        raise SystemExit("expected GE expression not found")

    tests = (lc / "unit-test/lc_watch_tests.c").read_text(encoding="utf-8")
    for test_name in ("LC_SignedCompare_Test_GT", "LC_SignedCompare_Test_GE"):
        if f"void {test_name}(void)" not in tests:
            raise SystemExit(f"expected upstream test missing: {test_name}")

    patch = args.fixture_patch.resolve()
    if not patch.is_file():
        raise SystemExit(f"fixture patch not found: {patch}")
    check = subprocess.run(
        ["git", "apply", "--check", str(patch)],
        cwd=lc,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if check.returncode != 0:
        raise SystemExit(f"fixture patch dry-run failed:\n{check.stderr.strip()}")

    print("S6X_PRE_RUNTIME_SOURCE_VALIDATION=PASS")
    print(f"cfs_commit={cfs_head}")
    print(f"lc_commit={lc_head}")
    print("fixture_patch_applied=NO")
    print("build_executed=NO")
    print("scientific_execution=NO")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
