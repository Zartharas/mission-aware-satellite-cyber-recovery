#!/usr/bin/env python3
"""Study 10 G4 rights-only inventory of six ESA outer ZIP central directories.

NO payload extraction, telemetry parsing, nested ZIP decompression, upload, or
rights clearance is performed. A missing marker NEVER proves unrestricted use.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import zipfile

from g4_local_integrity_check import expected_entries, verify_local_manifest

KEYWORDS = ("LICENSE", "LICENCE", "COPYING", "NOTICE", "COPYRIGHT",
            "THIRD-PARTY", "THIRD_PARTY", "AUTHORS", "TERMS")
EXPECTED_FROZEN_G2 = "8ed6a2b16233b86bf91672f6f15605dcf906c5eb"
MAX_OUTER_ENTRIES = 10000


class LicenseInventoryError(Exception):
    pass


def marker_basename(name: str) -> str | None:
    """Return only a short rights-document basename, never telemetry paths."""
    base = PurePosixPath(name.replace("\\", "/")).name
    if not base or len(base) > 128:
        return None
    upper = base.upper()
    if any(upper == key or upper.startswith(key + ".") or
           upper.startswith(key + "_") or upper.startswith(key + "-")
           for key in KEYWORDS):
        return base
    return None


def scan_outer_directory(path: Path, expected_name: str) -> dict:
    """Only read ZIP directory metadata. Explicitly do not read ZipExtFile."""
    if path.name != expected_name or path.is_symlink():
        raise LicenseInventoryError("BAD_FILE_NAME_OR_SYMLINK")
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        fd = os.open(path, flags)
    except FileNotFoundError:
        raise LicenseInventoryError("SOURCE_FILE_NOT_FOUND")
    try:
        with os.fdopen(fd, "rb", closefd=True) as file:
            if not stat.S_ISREG(os.fstat(file.fileno()).st_mode):
                raise LicenseInventoryError("NOT_REGULAR_FILE")
            with zipfile.ZipFile(file, "r") as archive:
                infos = archive.infolist()
                if len(infos) > MAX_OUTER_ENTRIES:
                    raise LicenseInventoryError("OUTER_MEMBER_COUNT_LIMIT")
                candidates = Counter()
                nested = 0
                for info in infos:
                    if info.filename.lower().endswith(".zip") and not info.is_dir():
                        nested += 1
                    marker = marker_basename(info.filename)
                    if marker is not None and not info.is_dir():
                        candidates[marker] += 1
                return {
                    "archive_basename": expected_name,
                    "outer_directory_entries": len(infos),
                    "nested_archives_detected_by_filename": nested,
                    "outer_rights_marker_basenames_and_counts": dict(sorted(candidates.items())),
                    "inner_zip_rights_files_examined": 0,
                    "payload_member_data_read": False,
                    "file_level_exception_status": "NOT_PROVEN_CLEAR",
                }
    except (OSError, zipfile.BadZipFile, RuntimeError) as e:
        if isinstance(e, LicenseInventoryError):
            raise
        raise LicenseInventoryError(type(e).__name__) from e


def run(root: Path, esa_dir: Path) -> tuple[dict, int]:
    frozen = verify_local_manifest(root)
    expected = [r for r in expected_entries(frozen, esa_dir, esa_dir)
                if r["family"] == "ESA_ADB"]
    if len(expected) != 6:
        raise LicenseInventoryError("FROZEN_ESA_SIX_SOURCE_CONTRACT_MISMATCH")
    results = []
    for item in expected:
        try:
            entry = scan_outer_directory(item["path"], item["basename"])
            entry.update({
                "source_id": item["id"],
                "source_version": item["id"].split("_")[-1],
                "published_md5_expected_from_frozen_manifest": item["md5"],
                "data_sha256_expected_from_author_prior_integrity_report": item["sha256"],
                "whole_archive_digest_recomputed_in_this_inventory": False,
            })
            results.append(entry)
        except LicenseInventoryError as e:
            results.append({
                "archive_basename": item["basename"],
                "source_id": item["id"],
                "failure_code": str(e),
                "status": "UNABLE_TO_READ_OUTER_ZIP_METADATA",
                "file_level_exception_status": "NOT_PROVEN_CLEAR",
            })
    errors = sum("failure_code" in x for x in results)
    out = {
        "schema_version": 1,
        "study_id": "S10-RSEI-001",
        "record_type": "G4_LOCAL_LICENSE_FILENAME_INVENTORY_ONLY",
        "recorded_utc": datetime.now(timezone.utc).isoformat(),
        "frozen_G2_payload": EXPECTED_FROZEN_G2,
        "source_archives_expected": 6,
        "source_archives_outer_metadata_reviewed": len(results) - errors,
        "source_archives_with_errors": errors,
        "status": "INCOMPLETE_SOURCE_ARCHIVES" if errors else
                  "TOP_LEVEL_LICENSE_FILENAMES_INVENTORIED_NESTED_RIGHTS_UNASSESSED",
        "file_specific_license_clearance": False,
        "author_G4_06_execution_authorized": False,
        "PR_merge_authorized": False,
        "original_telemetry_content_read": False,
        "nested_archives_decompressed": 0,
        "archive_file_paths_exported": False,
        "original_dataset_bytes_uploaded": False,
        "audit_scope_note": (
            "ZIP central-directory metadata only. Marker names are hints, "
            "not licensing grants. Third-party rights may appear in nested ZIPs, "
            "data fields, or materials not flagged by filenames. "
            "No clean-license conclusion is permitted."
        ),
        "archives": results,
    }
    return out, 0 if errors == 0 else 3


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--esa-dir", type=Path, required=True)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    try:
        result, code = run(args.repo, args.esa_dir)
    except (LicenseInventoryError, OSError, ValueError, AssertionError) as exc:
        result, code = ({
            "study_id": "S10-RSEI-001", "stage": "G4_LICENSE_METADATA_ONLY",
            "status": "ERROR_INVENTORY_NOT_CLEARED",
            "failure_code": str(exc) if isinstance(exc, LicenseInventoryError) else type(exc).__name__,
            "file_specific_license_clearance": False,
            "author_G4_06_execution_authorized": False,
        }, 2)
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.report:
        if args.report.is_symlink():
            raise SystemExit("Refusing symlink report destination")
        args.report.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
