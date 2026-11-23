#!/usr/bin/env python3
"""Offline, fail-closed ESA nested-ZIP rights-marker metadata inventory.

Reads outer ZIP members ONLY when those members are ZIP containers. The resulting
nested ZIP is spooled locally to inspect its central directory. Never reads
members inside a nested ZIP, parses telemetry, extracts files, or uploads data.
Rights-marker counts are *hints*, never a license grant or file-level clearance.
"""
from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import tempfile
import time
import zipfile

STUDY = "S10-RSEI-001"
FROZEN_G2 = "8ed6a2b16233b86bf91672f6f15605dcf906c5eb"
PREVIOUS_REPORT_SHA256 = "1b15ca458ce1f85ee4730e1b267dae4f023e60bf90689575b03930cd02fc00b5"
PREVIOUS_REPORT_STATUS = "TOP_LEVEL_LICENSE_FILENAMES_INVENTORIED_NESTED_RIGHTS_UNASSESSED"
EXPECTED_OUTER_ENTRIES = 2124
EXPECTED_NESTED_ZIPS = 2090
MAX_OUTER_ENTRIES = 10000
CHUNK = 1024 * 1024
RIGHTS = ("THIRD_PARTY", "THIRD-PARTY", "COPYRIGHT", "LICENCE", "LICENSE", "COPYING", "NOTICE", "AUTHORS", "TERMS")


class InventoryError(Exception):
    """Fail-closed validation or resource boundary."""


@dataclass(frozen=True)
class Limits:
    max_nested_bytes: int = 512 * 1024 * 1024
    max_total_bytes: int = 32 * 1024 * 1024 * 1024
    max_nested_count: int = 2500
    max_nested_entries: int = 10000
    max_elapsed_seconds: int = 1800


class Budget:
    def __init__(self, limits: Limits) -> None:
        self.limits = limits
        self.begin = time.monotonic()
        self.nested_count = 0
        self.bytes_spooled = 0

    def check_time(self) -> None:
        if time.monotonic() - self.begin > self.limits.max_elapsed_seconds:
            raise InventoryError("TIME_BUDGET_EXCEEDED")

    def start_nested(self, declared_size: int) -> None:
        self.check_time()
        if self.nested_count >= self.limits.max_nested_count:
            raise InventoryError("NESTED_ARCHIVE_COUNT_LIMIT")
        if declared_size < 0 or declared_size > self.limits.max_nested_bytes:
            raise InventoryError("NESTED_ARCHIVE_SIZE_LIMIT")
        self.nested_count += 1

    def account_bytes(self, n: int, within_member: int) -> None:
        self.check_time()
        if within_member > self.limits.max_nested_bytes:
            raise InventoryError("NESTED_ARCHIVE_SIZE_LIMIT")
        if self.bytes_spooled + n > self.limits.max_total_bytes:
            raise InventoryError("TOTAL_SPOOL_BYTES_LIMIT")
        self.bytes_spooled += n


def _rights_category(filename: str) -> str | None:
    # Do not export original names or paths, even for candidate rights files.
    base = filename.replace("\\", "/").rsplit("/", 1)[-1].upper()
    for category in RIGHTS:
        if base == category or base.startswith((category + ".", category + "-", category + "_")):
            return category.replace("-", "_")
    return None


def _metadata(infos: list[zipfile.ZipInfo], limit: int) -> tuple[Counter[str], int]:
    if len(infos) > limit:
        raise InventoryError("ZIP_DIRECTORY_ENTRY_LIMIT")
    markers: Counter[str] = Counter()
    deeper = 0
    names = set()
    for info in infos:
        name = info.filename
        if name in names:
            raise InventoryError("DUPLICATE_ZIP_MEMBER_NAME")
        names.add(name)
        if info.is_dir():
            continue
        if name.casefold().endswith(".zip"):
            deeper += 1
        key = _rights_category(name)
        if key:
            markers[key] += 1
    return markers, deeper


def _open_regular(path: Path, expected_basename: str):
    if path.name != expected_basename or path.is_symlink():
        raise InventoryError("SOURCE_NAME_OR_SYMLINK_REFUSED")
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0)
    try:
        descriptor = os.open(path, flags)
    except FileNotFoundError as exc:
        raise InventoryError("SOURCE_NOT_FOUND") from exc
    if not stat.S_ISREG(os.fstat(descriptor).st_mode):
        os.close(descriptor)
        raise InventoryError("SOURCE_NOT_REGULAR_FILE")
    return os.fdopen(descriptor, "rb")


def scan_outer(path: Path, expected_basename: str, budget: Budget) -> dict:
    """Read nested ZIP containers, then nested *directory metadata only*."""
    with _open_regular(path, expected_basename) as handle:
        try:
            with zipfile.ZipFile(handle, "r") as outer:
                infos = outer.infolist()
                outer_markers, nested_count = _metadata(infos, MAX_OUTER_ENTRIES)
                nested_markers: Counter[str] = Counter()
                deeper_count = 0
                nested_entries = 0
                for info in infos:
                    if info.is_dir() or not info.filename.casefold().endswith(".zip"):
                        continue
                    if info.flag_bits & 1:
                        raise InventoryError("ENCRYPTED_NESTED_CONTAINER_REFUSED")
                    budget.start_nested(info.file_size)
                    # TemporaryFile is unnamed and closed after one nested ZIP.
                    # No nested ZIP member is ever opened or decompressed.
                    with tempfile.TemporaryFile(mode="w+b") as scratch:
                        copied = 0
                        with outer.open(info, "r") as nested_stream:
                            while True:
                                budget.check_time()
                                block = nested_stream.read(CHUNK)
                                if not block:
                                    break
                                copied += len(block)
                                budget.account_bytes(len(block), copied)
                                scratch.write(block)
                        if copied != info.file_size:
                            raise InventoryError("NESTED_CONTAINER_LENGTH_MISMATCH")
                        scratch.seek(0)
                        with zipfile.ZipFile(scratch, "r") as inner:
                            inner_infos = inner.infolist()
                            found, deeper = _metadata(inner_infos, budget.limits.max_nested_entries)
                            nested_markers.update(found)
                            deeper_count += deeper
                            nested_entries += len(inner_infos)
                return {
                    "outer_directory_entries": len(infos),
                    "nested_zip_containers_examined": nested_count,
                    "nested_directory_entries_counted": nested_entries,
                    "outer_rights_marker_categories_and_counts": dict(sorted(outer_markers.items())),
                    "nested_rights_marker_categories_and_counts": dict(sorted(nested_markers.items())),
                    "deeper_zip_containers_not_opened": deeper_count,
                    "original_telemetry_members_read": False,
                    "nested_zip_container_bytes_spooled_locally": True,
                    "file_specific_license_clearance": False,
                }
        except InventoryError:
            raise
        except (OSError, RuntimeError, EOFError, ValueError, NotImplementedError, zipfile.BadZipFile, zipfile.LargeZipFile) as exc:
            # Never report paths, raw member names, or exception text.
            raise InventoryError("NESTED_ZIP_FORMAT_OR_IO_ERROR") from exc


def verify_previous_report(path: Path, expected_sha: str = PREVIOUS_REPORT_SHA256) -> dict:
    if path.is_symlink():
        raise InventoryError("PREVIOUS_REPORT_SYMLINK_REFUSED")
    try:
        with _open_regular(path, path.name) as handle:
            raw = handle.read(1024 * 1024 + 1)
    except (OSError, ValueError) as exc:
        raise InventoryError("PREVIOUS_REPORT_IO_ERROR") from exc
    if len(raw) > 1024 * 1024 or hashlib.sha256(raw).hexdigest() != expected_sha:
        raise InventoryError("PREVIOUS_REPORT_SHA256_MISMATCH")
    try:
        old = json.loads(raw)
    except (ValueError, UnicodeDecodeError) as exc:
        raise InventoryError("PREVIOUS_REPORT_JSON_INVALID") from exc
    if not isinstance(old, dict) or old.get("status") != PREVIOUS_REPORT_STATUS or old.get("study_id") != STUDY:
        raise InventoryError("PREVIOUS_REPORT_STATUS_MISMATCH")
    if old.get("source_archives_outer_metadata_reviewed") != 6 or old.get("source_archives_with_errors") != 0:
        raise InventoryError("PREVIOUS_REPORT_INCOMPLETE")
    entries = old.get("archives")
    if not isinstance(entries, list) or len(entries) != 6:
        raise InventoryError("PREVIOUS_REPORT_SOURCE_COUNT_MISMATCH")
    if sum(x.get("outer_directory_entries", -99999) for x in entries if isinstance(x, dict)) != EXPECTED_OUTER_ENTRIES:
        raise InventoryError("PREVIOUS_REPORT_OUTER_COUNT_MISMATCH")
    if sum(x.get("nested_archives_detected_by_filename", -99999) for x in entries if isinstance(x, dict)) != EXPECTED_NESTED_ZIPS:
        raise InventoryError("PREVIOUS_REPORT_NESTED_COUNT_MISMATCH")
    return old


def run(repo: Path, esa_dir: Path, previous_report: Path, limits: Limits) -> tuple[dict, int]:
    previous = verify_previous_report(previous_report)
    # Reuse the pinned G2 manifest verifier and explicit six-file identity mapping.
    from g4_local_integrity_check import expected_entries, verify_local_manifest
    frozen = verify_local_manifest(repo)
    entries = [e for e in expected_entries(frozen, esa_dir, esa_dir) if e["family"] == "ESA_ADB"]
    if len(entries) != 6:
        raise InventoryError("G2_ESA_ALLOWLIST_MISMATCH")
    by_id = {x["source_id"]: x for x in previous["archives"]}
    if len(by_id) != 6:
        raise InventoryError("PREVIOUS_REPORT_SOURCE_ID_MISMATCH")
    budget = Budget(limits)
    results = []
    for entry in entries:
        source_id = entry["id"]
        try:
            older = by_id[source_id]
            if older["archive_basename"] != entry["basename"]:
                raise InventoryError("PREVIOUS_REPORT_SOURCE_BASENAME_MISMATCH")
            result = scan_outer(entry["path"], entry["basename"], budget)
            if (result["outer_directory_entries"] != older["outer_directory_entries"] or
                    result["nested_zip_containers_examined"] != older["nested_archives_detected_by_filename"]):
                raise InventoryError("PREVIOUS_OUTER_METADATA_COUNT_MISMATCH")
            results.append({"source_id": source_id, "archive_basename": entry["basename"], "status": "DIRECTORIES_SCANNED_LICENSE_UNRESOLVED", **result})
        except (InventoryError, KeyError) as exc:
            code = str(exc) if isinstance(exc, InventoryError) else "PREVIOUS_REPORT_SOURCE_ID_MISMATCH"
            results.append({"source_id": source_id, "archive_basename": entry["basename"], "status": "INCOMPLETE", "failure_code": code, "file_specific_license_clearance": False})
    failures = sum(x["status"] == "INCOMPLETE" for x in results)
    deeper = sum(x.get("deeper_zip_containers_not_opened", 0) for x in results)
    out = {
        "schema_version": 1,
        "study_id": STUDY,
        "record_type": "G4_LOCAL_NESTED_LICENSE_METADATA_INVENTORY_ONLY",
        "recorded_utc": datetime.now(timezone.utc).isoformat(),
        "frozen_G2_payload": FROZEN_G2,
        "previous_author_report_sha256_expected_and_checked": PREVIOUS_REPORT_SHA256,
        "previous_author_report_original_bytes_published": False,
        "status": "INCOMPLETE_OR_UNSUPPORTED_NESTING" if failures or deeper else "NESTED_DIRECTORY_MARKERS_INVENTORIED_RIGHTS_UNRESOLVED",
        "source_archives_expected": 6,
        "source_archives_scanned": 6 - failures,
        "source_archives_with_errors": failures,
        "deeper_zip_containers_not_opened": deeper,
        "nested_archive_container_bytes_spooled_total": budget.bytes_spooled,
        "nested_archive_count_attempted": budget.nested_count,
        "original_telemetry_members_read": False,
        "original_dataset_bytes_uploaded": False,
        "nested_zip_payload_members_opened": 0,
        "file_specific_license_clearance": False,
        "author_G4_06_execution_authorized": False,
        "PR_merge_authorized": False,
        "interpretation": "Marker categories are hints only. Absence of markers never proves clearance. Inner files, in-band notices, data rights and applicable release terms require separate review.",
        "archives": results,
    }
    return out, 0 if not failures and not deeper else 3


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--esa-dir", type=Path, required=True)
    parser.add_argument("--previous-report", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--max-nested-mib", type=int, default=512)
    parser.add_argument("--max-total-mib", type=int, default=32768)
    parser.add_argument("--max-seconds", type=int, default=1800)
    args = parser.parse_args()
    if not 1 <= args.max_nested_mib <= 1024 or not 1 <= args.max_total_mib <= 65536 or not 1 <= args.max_seconds <= 7200:
        parser.error("Limits must stay within bounded supported ranges")
    try:
        result, code = run(args.repo, args.esa_dir, args.previous_report, Limits(
            max_nested_bytes=args.max_nested_mib * 1024 * 1024,
            max_total_bytes=args.max_total_mib * 1024 * 1024,
            max_elapsed_seconds=args.max_seconds,
        ))
    except (InventoryError, OSError, ValueError, AssertionError) as exc:
        result = {
            "study_id": STUDY,
            "record_type": "G4_LOCAL_NESTED_LICENSE_METADATA_INVENTORY_ONLY",
            "status": "ERROR_FAIL_CLOSED",
            "failure_code": str(exc) if isinstance(exc, InventoryError) else type(exc).__name__,
            "file_specific_license_clearance": False,
            "author_G4_06_execution_authorized": False,
            "PR_merge_authorized": False,
        }
        code = 2
    output = json.dumps(result, indent=2, sort_keys=True) + "\n"
    # Exclusive creation preserves any prior evidence. Refuse symlink paths.
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    try:
        fd = os.open(args.report, flags, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(output)
    except FileExistsError:
        parser.error("Output report already exists; refusing overwrite")
    print(output, end="")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
