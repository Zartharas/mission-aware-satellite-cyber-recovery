"""Synthetic ZIP-only tests for G4 nested rights metadata; no satellite bytes."""
from __future__ import annotations

from io import BytesIO
import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
import zipfile

from g4_nested_license_metadata_inventory import (
    Budget, InventoryError, Limits, _rights_category, scan_outer,
    verify_previous_report, EXPECTED_OUTER_ENTRIES, EXPECTED_NESTED_ZIPS,
    PREVIOUS_REPORT_STATUS, STUDY,
)


def zip_bytes(contents: dict[str, bytes]) -> bytes:
    memory = BytesIO()
    with zipfile.ZipFile(memory, "w", zipfile.ZIP_DEFLATED) as target:
        for name, data in contents.items():
            target.writestr(name, data)
    return memory.getvalue()


class SyntheticNestedInventory(unittest.TestCase):
    def limits(self, **kwargs) -> Limits:
        return Limits(**kwargs)

    def source(self, root: Path, name: str = "ESA-Mission1.zip", *, nested: bytes | None = None) -> Path:
        if nested is None:
            nested = zip_bytes({"docs/LICENSE.txt": b"synthetic notice", "telemetry.csv": b"nonflight"})
        path = root / name
        path.write_bytes(zip_bytes({"nested/channel.zip": nested, "outer/NOTICE.md": b"synthetic"}))
        return path

    def test_nested_categories_and_path_privacy(self):
        with TemporaryDirectory() as tmp:
            src = self.source(Path(tmp), nested=zip_bytes({
                "private/path/LICENSE.txt": b"synthetic",
                "private/path/THIRD_PARTY.md": b"synthetic",
                "private/path/telemetry.csv": b"synthetic",
            }))
            result = scan_outer(src, src.name, Budget(Limits()))
            self.assertEqual(result["nested_zip_containers_examined"], 1)
            self.assertEqual(result["nested_directory_entries_counted"], 3)
            self.assertEqual(result["nested_rights_marker_categories_and_counts"], {"LICENSE": 1, "THIRD_PARTY": 1})
            self.assertEqual(result["outer_rights_marker_categories_and_counts"], {"NOTICE": 1})
            self.assertNotIn("private", json.dumps(result))
            self.assertNotIn("telemetry.csv", json.dumps(result))
            self.assertFalse(result["file_specific_license_clearance"])
            self.assertFalse(result["original_telemetry_members_read"])

    def test_absent_marker_never_clears_rights(self):
        with TemporaryDirectory() as tmp:
            src = self.source(Path(tmp), nested=zip_bytes({"telemetry.csv": b"synthetic"}))
            result = scan_outer(src, src.name, Budget(Limits()))
            self.assertEqual(result["nested_rights_marker_categories_and_counts"], {})
            self.assertFalse(result["file_specific_license_clearance"])

    def test_deeper_zip_counted_but_not_opened(self):
        with TemporaryDirectory() as tmp:
            deeply = zip_bytes({"LICENSE.md": b"synthetic"})
            src = self.source(Path(tmp), nested=zip_bytes({"deeper.zip": deeply}))
            result = scan_outer(src, src.name, Budget(Limits()))
            self.assertEqual(result["deeper_zip_containers_not_opened"], 1)
            self.assertEqual(result["nested_rights_marker_categories_and_counts"], {})

    def test_refuse_corrupt_inner_zip(self):
        with TemporaryDirectory() as tmp:
            src = self.source(Path(tmp), nested=b"bad zip bytes")
            with self.assertRaisesRegex(InventoryError, "NESTED_ZIP_FORMAT_OR_IO_ERROR"):
                scan_outer(src, src.name, Budget(Limits()))

    def test_refuse_size_limit(self):
        with TemporaryDirectory() as tmp:
            src = self.source(Path(tmp))
            with self.assertRaisesRegex(InventoryError, "NESTED_ARCHIVE_SIZE_LIMIT"):
                scan_outer(src, src.name, Budget(Limits(max_nested_bytes=8)))

    def test_refuse_cumulative_limit(self):
        with TemporaryDirectory() as tmp:
            src = self.source(Path(tmp))
            with self.assertRaisesRegex(InventoryError, "TOTAL_SPOOL_BYTES_LIMIT"):
                scan_outer(src, src.name, Budget(Limits(max_total_bytes=10)))

    def test_refuse_nested_count_limit(self):
        with TemporaryDirectory() as tmp:
            src = self.source(Path(tmp))
            with self.assertRaisesRegex(InventoryError, "NESTED_ARCHIVE_COUNT_LIMIT"):
                scan_outer(src, src.name, Budget(Limits(max_nested_count=0)))

    def test_refuse_elapsed_limit(self):
        with TemporaryDirectory() as tmp:
            src = self.source(Path(tmp))
            budget = Budget(Limits(max_elapsed_seconds=0))
            with self.assertRaisesRegex(InventoryError, "TIME_BUDGET_EXCEEDED"):
                scan_outer(src, src.name, budget)

    def test_refuse_source_symlink(self):
        with TemporaryDirectory() as tmp:
            folder = Path(tmp)
            actual = self.source(folder, name="source.zip")
            link = folder / "ESA-Mission1.zip"
            link.symlink_to(actual)
            with self.assertRaisesRegex(InventoryError, "SOURCE_NAME_OR_SYMLINK_REFUSED"):
                scan_outer(link, link.name, Budget(Limits()))

    def test_refuse_duplicate_inner_filenames(self):
        import warnings
        stream = BytesIO()
        with zipfile.ZipFile(stream, "w") as z:
            z.writestr("LICENSE", b"one")
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", UserWarning)
                z.writestr("LICENSE", b"two")
        with TemporaryDirectory() as tmp:
            src = self.source(Path(tmp), nested=stream.getvalue())
            with self.assertRaisesRegex(InventoryError, "DUPLICATE_ZIP_MEMBER_NAME"):
                scan_outer(src, src.name, Budget(Limits()))

    def test_report_sha256_mismatch(self):
        with TemporaryDirectory() as tmp:
            previous = Path(tmp) / "report.json"
            previous.write_text("{}", encoding="utf-8")
            with self.assertRaisesRegex(InventoryError, "PREVIOUS_REPORT_SHA256_MISMATCH"):
                verify_previous_report(previous)

    def test_report_integrity_and_counts(self):
        entries = [
            {"source_id": f"ESA_M{i}_v1", "archive_basename": f"S{i}.zip",
             "outer_directory_entries": EXPECTED_OUTER_ENTRIES // 6 + (1 if i <= EXPECTED_OUTER_ENTRIES % 6 else 0),
             "nested_archives_detected_by_filename": EXPECTED_NESTED_ZIPS // 6 + (1 if i <= EXPECTED_NESTED_ZIPS % 6 else 0)}
            for i in range(1, 7)
        ]
        old = {"study_id": STUDY, "status": PREVIOUS_REPORT_STATUS,
               "source_archives_outer_metadata_reviewed": 6, "source_archives_with_errors": 0,
               "archives": entries}
        raw = json.dumps(old).encode()
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "old.json"
            path.write_bytes(raw)
            self.assertEqual(verify_previous_report(path, hashlib.sha256(raw).hexdigest())["status"], PREVIOUS_REPORT_STATUS)
            old["archives"][0]["nested_archives_detected_by_filename"] += 1
            raw = json.dumps(old).encode()
            path.write_bytes(raw)
            with self.assertRaisesRegex(InventoryError, "PREVIOUS_REPORT_NESTED_COUNT_MISMATCH"):
                verify_previous_report(path, hashlib.sha256(raw).hexdigest())

    def test_rights_marker_only_category(self):
        self.assertEqual(_rights_category("/private/NOTICE-secret.md"), "NOTICE")
        self.assertEqual(_rights_category("third-party.txt"), "THIRD_PARTY")
        self.assertIsNone(_rights_category("telemetry.csv"))


if __name__ == "__main__":
    unittest.main()
