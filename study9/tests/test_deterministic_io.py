from __future__ import annotations

import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
for path in (ROOT / "study9" / "src", ROOT / "study2" / "src"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from study9_semantic.deterministic_io import (
    DeterministicOutputError,
    build_output_sha256_manifest,
    canonical_json_bytes,
    canonical_json_sha256,
    integer_fraction,
)


class DeterministicIoTests(unittest.TestCase):
    def test_canonical_json_is_sorted_utf8_compact_and_newline_terminated(self):
        first = canonical_json_bytes({"z": 1, "a": {"β": 2, "x": [3, 4]}})
        second = canonical_json_bytes({"a": {"x": [3, 4], "β": 2}, "z": 1})
        self.assertEqual(first, second)
        self.assertTrue(first.endswith(b"\n"))
        self.assertEqual(first.decode("utf-8"), '{"a":{"x":[3,4],"β":2},"z":1}\n')
        self.assertEqual(canonical_json_sha256({"z": 1, "a": 2}), canonical_json_sha256({"a": 2, "z": 1}))

    def test_integer_fraction_requires_exact_valid_integer_counts(self):
        self.assertEqual(integer_fraction(3, 10), {"numerator": 3, "denominator": 10})
        for args in ((-1, 10), (11, 10), (1, 0), (1.0, 10)):
            with self.subTest(args=args):
                with self.assertRaises(DeterministicOutputError):
                    integer_fraction(*args)

    def test_output_manifest_is_stable_and_sorted(self):
        artifacts_a = {"b.json": b"B\n", "a.json": b"A\n"}
        artifacts_b = {"a.json": b"A\n", "b.json": b"B\n"}
        manifest_a = build_output_sha256_manifest(artifacts_a)
        manifest_b = build_output_sha256_manifest(artifacts_b)
        self.assertEqual(manifest_a, manifest_b)
        self.assertEqual(
            [row["path"] for row in manifest_a["artifacts"]],
            ["a.json", "b.json"],
        )
        self.assertTrue(all(type(row["size_bytes"]) is int for row in manifest_a["artifacts"]))

    def test_nonfinite_json_is_rejected(self):
        with self.assertRaises(DeterministicOutputError):
            canonical_json_bytes({"bad": float("nan")})


if __name__ == "__main__":
    unittest.main()
