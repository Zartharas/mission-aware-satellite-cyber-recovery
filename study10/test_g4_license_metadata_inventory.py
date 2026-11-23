"""G4 rights inventory synthetic-only tests; no original telemetry fixtures."""
from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
import zipfile

from g4_license_metadata_inventory import (
    LicenseInventoryError, marker_basename, scan_outer_directory,
)


class SyntheticRightsInventoryTests(unittest.TestCase):
    def make_zip(self, root: Path, name: str, files: dict[str, bytes]) -> Path:
        path = root / name
        with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
            for filename, content in files.items():
                z.writestr(filename, content)
        return path

    def test_rights_marker_only_basename(self):
        self.assertEqual(marker_basename("private/telemetry/LICENSE.txt"), "LICENSE.txt")
        self.assertEqual(marker_basename("foo/bar/third_party.md"), "third_party.md")
        self.assertIsNone(marker_basename("mission/private_status.csv"))
        self.assertIsNone(marker_basename("mission/anomaly_labels.csv"))

    def test_outer_license_candidates_and_nested_incomplete(self):
        with TemporaryDirectory() as root:
            p = self.make_zip(Path(root), "ESA-Mission1.zip", {
                "NOTICE.txt": b"synthetic notice",
                "some/private/telemetry.csv": b"synthetic data",
                "data/nested.zip": b"not opened by license inventory",
                "docs/COPYING.md": b"synthetic copyright",
            })
            with patch.object(zipfile.ZipFile, "open", side_effect=AssertionError("payload opened")):
                out = scan_outer_directory(p, "ESA-Mission1.zip")
            self.assertEqual(out["outer_directory_entries"], 4)
            self.assertEqual(out["nested_archives_detected_by_filename"], 1)
            self.assertEqual(out["outer_rights_marker_basenames_and_counts"], {"COPYING.md": 1, "NOTICE.txt": 1})
            self.assertEqual(out["inner_zip_rights_files_examined"], 0)
            self.assertIs(out["payload_member_data_read"], False)
            self.assertEqual(out["file_level_exception_status"], "NOT_PROVEN_CLEAR")

    def test_no_marker_does_not_imply_license_clearance(self):
        with TemporaryDirectory() as root:
            p = self.make_zip(Path(root), "ESA-Mission2.zip", {"payload.csv": b"not analyzed"})
            out = scan_outer_directory(p, "ESA-Mission2.zip")
            self.assertEqual(out["outer_rights_marker_basenames_and_counts"], {})
            self.assertEqual(out["file_level_exception_status"], "NOT_PROVEN_CLEAR")

    def test_symlink_refused(self):
        with TemporaryDirectory() as root:
            dirpath = Path(root)
            real = self.make_zip(dirpath, "ESA-Mission3.zip", {"README.txt": b"synthetic"})
            link = dirpath / "ESA-Mission1.zip"
            link.symlink_to(real)
            with self.assertRaisesRegex(LicenseInventoryError, "BAD_FILE_NAME_OR_SYMLINK"):
                scan_outer_directory(link, "ESA-Mission1.zip")

    def test_wrong_basename_refused(self):
        with TemporaryDirectory() as root:
            p = self.make_zip(Path(root), "unexpected.zip", {"NOTICE.txt": b"synthetic"})
            with self.assertRaisesRegex(LicenseInventoryError, "BAD_FILE_NAME_OR_SYMLINK"):
                scan_outer_directory(p, "ESA-Mission3.zip")

    def test_missing_file_refused(self):
        with TemporaryDirectory() as root:
            with self.assertRaisesRegex(LicenseInventoryError, "SOURCE_FILE_NOT_FOUND"):
                scan_outer_directory(Path(root) / "ESA-Mission1.zip", "ESA-Mission1.zip")

    def test_corrupted_zip_refused(self):
        with TemporaryDirectory() as root:
            p = Path(root) / "ESA-Mission1.zip"
            p.write_bytes(b"not a valid zip")
            with self.assertRaisesRegex(LicenseInventoryError, "BadZipFile"):
                scan_outer_directory(p, "ESA-Mission1.zip")


if __name__ == "__main__":
    unittest.main()
