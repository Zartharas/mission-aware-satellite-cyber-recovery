from __future__ import annotations

import hashlib
import sys
import tempfile
from pathlib import Path
import unittest
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[2]
for path in (ROOT / "study9" / "src", ROOT / "study2" / "src"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from study9_semantic.input_identity import (
    InputIdentityError,
    InputIdentitySpec,
    iter_verified_rows,
    verify_csv_source,
)


CSV_BYTES = b"a,b\n1,2\n3,4\n"


class InputIdentityTests(unittest.TestCase):
    def _direct_spec(self, path: Path, *, sha: str | None = None, rows: int = 2, columns: int = 2):
        return InputIdentitySpec(
            dataset_id="AEGISSAT_2025",
            source_kind="DIRECT_CSV",
            source_path=path,
            canonical_artifact_path="AegisSat-AD.csv",
            canonical_artifact_sha256=sha or hashlib.sha256(CSV_BYTES).hexdigest(),
            expected_rows=rows,
            expected_columns=columns,
        )

    def _zip_spec(self, path: Path, *, member: str = "Data/Raw/test.csv"):
        return InputIdentitySpec(
            dataset_id="CUCD_ID_V3",
            source_kind="ZIP_CSV_MEMBER",
            source_path=path,
            canonical_artifact_path=member,
            canonical_artifact_sha256=hashlib.sha256(CSV_BYTES).hexdigest(),
            expected_rows=2,
            expected_columns=2,
            outer_container_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
        )

    def test_direct_csv_verifies_and_streams_exact_rows(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "source.csv"
            path.write_bytes(CSV_BYTES)
            spec = self._direct_spec(path)
            verified = verify_csv_source(spec)
            self.assertEqual(verified.header, ("a", "b"))
            self.assertEqual(verified.row_count, 2)
            self.assertEqual(
                list(iter_verified_rows(spec, verified)),
                [{"a": "1", "b": "2"}, {"a": "3", "b": "4"}],
            )

    def test_direct_csv_rejects_hash_mismatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "source.csv"
            path.write_bytes(CSV_BYTES)
            spec = self._direct_spec(path, sha="0" * 64)
            with self.assertRaises(InputIdentityError):
                verify_csv_source(spec)

    def test_zip_member_requires_exact_member_identity_and_hashes(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "source.zip"
            with ZipFile(path, "w") as archive:
                archive.writestr("Data/Raw/test.csv", CSV_BYTES)
            spec = self._zip_spec(path)
            verified = verify_csv_source(spec)
            self.assertEqual(verified.row_count, 2)
            self.assertEqual(len(list(iter_verified_rows(spec, verified))), 2)

            missing = self._zip_spec(path, member="Data/Raw/not-there.csv")
            with self.assertRaises(InputIdentityError):
                verify_csv_source(missing)

    def test_zip_rejects_outer_container_hash_mismatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "source.zip"
            with ZipFile(path, "w") as archive:
                archive.writestr("Data/Raw/test.csv", CSV_BYTES)
            spec = self._zip_spec(path)
            tampered = InputIdentitySpec(
                **{**spec.__dict__, "outer_container_sha256": "f" * 64}
            )
            with self.assertRaises(InputIdentityError):
                verify_csv_source(tampered)

    def test_csv_rejects_row_width_mismatch(self):
        bad = b"a,b\n1,2\n3\n"
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "source.csv"
            path.write_bytes(bad)
            spec = self._direct_spec(path, sha=hashlib.sha256(bad).hexdigest())
            with self.assertRaises(InputIdentityError):
                verify_csv_source(spec)

    def test_csv_rejects_shape_mismatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "source.csv"
            path.write_bytes(CSV_BYTES)
            with self.assertRaises(InputIdentityError):
                verify_csv_source(self._direct_spec(path, rows=3))
            with self.assertRaises(InputIdentityError):
                verify_csv_source(self._direct_spec(path, columns=3))

    def test_csv_rejects_duplicate_headers(self):
        bad = b"a,a\n1,2\n3,4\n"
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "source.csv"
            path.write_bytes(bad)
            spec = self._direct_spec(path, sha=hashlib.sha256(bad).hexdigest())
            with self.assertRaises(InputIdentityError):
                verify_csv_source(spec)


if __name__ == "__main__":
    unittest.main()
