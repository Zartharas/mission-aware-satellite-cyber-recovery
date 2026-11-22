#!/usr/bin/env python3
"""S10-RSEI-001: offline, integrity-only ESA-ADB / OPS-SAT-AD file audit.

No network, no telemetry parsing, no upload, no archive extraction to a named path.
Original files are read-only. Nested ESA ZIPs are temporarily staged *one at a
 time* to a caller-supplied local scratch directory and deleted automatically.
A PASS is a byte-integrity finding, NEVER G4 scientific-execution permission.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import sys
import tempfile
import time
import zipfile

CHUNK = 1024 * 1024
EXPECTED_FROZEN_G2_MANIFEST_SHA256 = "2eb2cb1ec3a49de3ff61bd7bb1a4d186a45d6fddf7da98ec79d18f0dee9b4210"
EXPECTED_FROZEN_G2_RECEIPT_SHA1 = "38e5da5edc193b358012bc9c2c3180917d7419ac"
DEFAULT_LIMITS = {
    "max_outer_members": 20000,
    "max_nested_members_each": 10000,
    "max_total_uncompressed_per_archive": 16 * (1024 ** 3),
    "max_nested_zip_stage": 5 * (1024 ** 3),
    "max_single_member_uncompressed": 6 * (1024 ** 3),
    "max_compression_ratio": 1000,
}
# Filename/size/directory count from prior author-local intake, independently
# subordinate to the *content-hash-pinned* G2 manifest's frozen MD5/SHA256.
ESA_PRIOR_INTAKE = {
    (1, "v1"): ("ESA-Mission1.zip", 3776246054, 780, 3776362882),
    (1, "v2"): ("ESA-Mission1 (1).zip", 3776246073, 780, 3776363122),
    (2, "v1"): ("ESA-Mission2.zip", 4098539912, 230, 4099243015),
    (2, "v2"): ("ESA-Mission2 (1).zip", 4098539932, 230, 4099243187),
    (3, "v1"): ("ESA-Mission3.zip", 3734403447, 52, 3734582943),
    (3, "v2"): ("ESA-Mission3 (1).zip", 3734403444, 52, 3734582483),
}

class IntegrityError(Exception):
    pass


def git_blob_sha1(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()


def verify_local_manifest(root: Path) -> dict:
    mf = root / "study10/G2_FREEZE_MANIFEST_CANDIDATE_20261121.json"
    receipt = root / "study10/G2_PROTOCOL_FREEZE_RECEIPT_20261122.json"
    if hashlib.sha256(mf.read_bytes()).hexdigest() != EXPECTED_FROZEN_G2_MANIFEST_SHA256:
        raise IntegrityError("FROZEN_G2_MANIFEST_SHA256_MISMATCH")
    if git_blob_sha1(receipt.read_bytes()) != EXPECTED_FROZEN_G2_RECEIPT_SHA1:
        raise IntegrityError("G2_RECEIPT_GIT_BLOB_ID_MISMATCH")
    m, r = json.loads(mf.read_bytes()), json.loads(receipt.read_bytes())
    assert r["payload"]["read_only_payload_commit"] == "8ed6a2b16233b86bf91672f6f15605dcf906c5eb"
    assert r["binding_Option_B_source_rights_policy"]["policy_id"] == "B_FREEZE_DESIGN_WITH_SOURCE_USE_HOLD"
    assert r["binding_Option_B_source_rights_policy"]["rights_clearance_for_source_data"] is False
    assert r["scientific_controls"]["G4_source_semantic_adjudication"].startswith("BLOCKED")
    return m


def expected_entries(m: dict, esa_dir: Path, ops_dir: Path) -> list[dict]:
    records: list[dict] = []
    seen = set()
    for ent in m["dataset_file_identity"]["ESA_ADB_archive_ids"]:
        key = (int(ent["mission"]), str(ent["release"]))
        if key not in ESA_PRIOR_INTAKE or key in seen:
            raise IntegrityError("ESA_FROZEN_IDENTITY_COUNT_OR_KEY_INVALID")
        seen.add(key)
        name, prior_size, prior_count, prior_inflated = ESA_PRIOR_INTAKE[key]
        expected_doi = {"v1": "10.5281/zenodo.12528696", "v2": "10.5281/zenodo.15237121"}[key[1]]
        if ent["doi"] != expected_doi or not re.fullmatch(r"[a-f0-9]{32}", ent["published_md5"]):
            raise IntegrityError("ESA_EXPECTED_DOI_OR_MD5_INVALID")
        records.append({"id": f"ESA_M{key[0]}_{key[1]}", "family": "ESA_ADB",
                        "basename": name, "path": esa_dir / name, "md5": ent["published_md5"],
                        "sha256": ent["sha256_author_reported"], "expected_size": prior_size,
                        "zip_directory_count": prior_count, "zip_uncompressed_bytes": prior_inflated})
    if seen != set(ESA_PRIOR_INTAKE):
        raise IntegrityError("ESA_SIX_ARCHIVE_MANIFEST_INCOMPLETE")
    ops = m["dataset_file_identity"]["OPS_SAT_AD_v2"]
    if ops["doi"] != "10.5281/zenodo.15108715":
        raise IntegrityError("OPS_V2_SOURCE_DOI_INVALID")
    for name, item in (("dataset.csv", ops["dataset_csv"]),
                       ("segments.csv", ops["segments_csv"])):
        records.append({"id": "OPS_V2_" + name, "family": "OPS_SAT_AD_V2",
                        "basename": name, "path": ops_dir / name, "md5": item["md5"],
                        "sha256": item["sha256_author_reported"]})
    records.append({"id": "OPS_V2_LICENSE", "family": "OPS_SAT_AD_V2",
                    "basename": "LICENSE", "path": ops_dir / "LICENSE",
                    "md5": ops["license_file_md5"],
                    "sha256": ops["license_file_sha256_author_reported"]})
    if len(records) != 9 or any(not re.fullmatch(r"[a-f0-9]{64}", x["sha256"]) for x in records):
        raise IntegrityError("EXPECTED_RECORDS_INVALID")
    return records


def safe_member_name(name: str) -> bool:
    if not name or "\x00" in name or name.startswith(("/", "\\")) or "\\" in name:
        return False
    if re.match(r"^[A-Za-z]:", name):
        return False
    p = PurePosixPath(name)
    return not any(x in ("..", "") for x in p.parts) and not p.is_absolute()


def checked_zip_members(z: zipfile.ZipFile, *, max_members: int, limits: dict) -> tuple[list, int]:
    infos = z.infolist()
    if len(infos) > max_members:
        raise IntegrityError("ZIP_MEMBER_COUNT_LIMIT")
    names = set()
    sum_uncompressed = 0
    for info in infos:
        if not safe_member_name(info.filename):
            raise IntegrityError("ZIP_UNSAFE_MEMBER_PATH")
        if info.filename in names:
            raise IntegrityError("ZIP_DUPLICATE_MEMBER_NAME")
        names.add(info.filename)
        mode = (info.external_attr >> 16) & 0o177777
        if stat.S_ISLNK(mode) or (mode and stat.S_IFMT(mode) not in (0, stat.S_IFREG, stat.S_IFDIR)):
            raise IntegrityError("ZIP_SYMLINK_OR_SPECIAL_MEMBER")
        if info.flag_bits & 0x1:
            raise IntegrityError("ZIP_ENCRYPTED_MEMBER")
        if info.file_size > limits["max_single_member_uncompressed"]:
            raise IntegrityError("ZIP_SINGLE_MEMBER_SIZE_LIMIT")
        if info.file_size > 0 and info.file_size / max(1, info.compress_size) > limits["max_compression_ratio"]:
            raise IntegrityError("ZIP_COMPRESSION_RATIO_LIMIT")
        sum_uncompressed += info.file_size
        if sum_uncompressed > limits["max_total_uncompressed_per_archive"]:
            raise IntegrityError("ZIP_TOTAL_UNCOMPRESSED_SIZE_LIMIT")
    return infos, sum_uncompressed


def ensure_runtime(deadline: float | None) -> None:
    if deadline is not None and time.monotonic() > deadline:
        raise IntegrityError("LOCAL_INTEGRITY_RUNTIME_LIMIT_REACHED")


def drain(reader, *, max_bytes: int, deadline: float | None = None) -> int:
    n = 0
    while True:
        ensure_runtime(deadline)
        data = reader.read(CHUNK)
        if not data:
            return n
        n += len(data)
        if n > max_bytes:
            raise IntegrityError("ZIP_MEMBER_STREAM_EXCEEDED_ALLOWED_SIZE")


def inspect_zip(fp, expected: dict, *, outer_only: bool, scratch: Path | None,
                limits: dict, deadline: float | None = None) -> dict:
    out = {"outer_crc": "NOT_RUN", "nested_crc": "NOT_RUN", "outer_members": 0,
           "nested_archives": 0, "nested_members": 0, "outer_uncompressed_bytes": 0,
           "nested_uncompressed_bytes": 0, "temporary_source_bytes_retained": False}
    fp.seek(0)
    with zipfile.ZipFile(fp, "r", allowZip64=True) as outer:
        infos, total = checked_zip_members(outer, max_members=limits["max_outer_members"], limits=limits)
        out["outer_members"] = len(infos)
        out["outer_uncompressed_bytes"] = total
        if (len(infos) != expected["zip_directory_count"] or
                total != expected["zip_uncompressed_bytes"]):
            raise IntegrityError("OUTER_ZIP_DIRECTORY_DIFFERS_FROM_PRIOR_INTAKE")
        nested = [z for z in infos if not z.is_dir() and z.filename.lower().endswith(".zip")]
        out["nested_archives"] = len(nested)
        total_inflated = 0
        for info in infos:
            ensure_runtime(deadline)
            if info.is_dir():
                continue
            # All outer members are fully streamed; ZipExtFile verifies CRC on EOF.
            with outer.open(info, "r") as stream:
                if info in nested and not outer_only:
                    if scratch is None:
                        raise IntegrityError("EXPLICIT_SCRATCH_DIRECTORY_REQUIRED")
                    if info.file_size > limits["max_nested_zip_stage"]:
                        raise IntegrityError("NESTED_ZIP_TEMP_STAGE_LIMIT")
                    free = shutil.disk_usage(scratch).free
                    if free < info.file_size + 128 * 1024 * 1024:
                        raise IntegrityError("INSUFFICIENT_LOCAL_SCRATCH_DISK")
                    # TemporaryFile is deleted automatically; no named extraction.
                    with tempfile.TemporaryFile(mode="w+b", dir=scratch) as stage:
                        n = 0
                        while True:
                            ensure_runtime(deadline)
                            b = stream.read(CHUNK)
                            if not b:
                                break
                            n += len(b)
                            if n > info.file_size or n > limits["max_nested_zip_stage"]:
                                raise IntegrityError("NESTED_ZIP_STREAM_EXCEEDED_LIMIT")
                            stage.write(b)
                        if n != info.file_size:
                            raise IntegrityError("OUTER_MEMBER_SIZE_MISMATCH")
                        stage.seek(0)
                        with zipfile.ZipFile(stage, "r") as inner:
                            nested_infos, nested_uncompressed = checked_zip_members(
                                inner, max_members=limits["max_nested_members_each"], limits=limits)
                            total_inflated += nested_uncompressed
                            if total_inflated + total > limits["max_total_uncompressed_per_archive"]:
                                raise IntegrityError("NESTED_TOTAL_INFLATION_LIMIT")
                            for inner_info in nested_infos:
                                ensure_runtime(deadline)
                                if inner_info.is_dir():
                                    continue
                                if inner_info.filename.lower().endswith(".zip"):
                                    raise IntegrityError("DEEPER_NESTED_ZIP_NOT_VALIDATED")
                                with inner.open(inner_info, "r") as r:
                                    if drain(r, max_bytes=inner_info.file_size, deadline=deadline) != inner_info.file_size:
                                        raise IntegrityError("NESTED_MEMBER_SIZE_MISMATCH")
                            out["nested_members"] += len(nested_infos)
                            out["nested_uncompressed_bytes"] += nested_uncompressed
                else:
                    if drain(stream, max_bytes=info.file_size, deadline=deadline) != info.file_size:
                        raise IntegrityError("OUTER_MEMBER_SIZE_MISMATCH")
        out["outer_crc"] = "PASS"
        out["nested_crc"] = "NOT_CHECKED" if outer_only else "PASS"
    return out


def audit_one(rec: dict, *, outer_only: bool, scratch: Path | None, limits: dict,
              deadline: float | None = None) -> dict:
    out = {"id": rec["id"], "family": rec["family"], "basename": rec["basename"],
           "expected_doi": "10.5281/zenodo.12528696" if rec["id"].endswith("_v1")
           else "10.5281/zenodo.15237121" if rec["family"] == "ESA_ADB"
           else "10.5281/zenodo.15108715",
           "expected_md5": rec["md5"], "expected_sha256_from_prior_author_report": rec["sha256"],
           "status": "NOT_CHECKED"}
    p = rec["path"]
    if deadline is not None and time.monotonic() > deadline:
        out["status"] = "FAIL_INTEGRITY_OR_RESOURCE_LIMIT"
        out["failure_code"] = "LOCAL_INTEGRITY_RUNTIME_LIMIT_REACHED"
        return out
    if p.name != rec["basename"] or p.is_symlink():
        out["status"] = "FAIL_BAD_PATH_OR_SYMLINK"
        return out
    try:
        flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
        fd = os.open(p, flags)
        with os.fdopen(fd, "rb", closefd=True) as f:
            st = os.fstat(f.fileno())
            if not stat.S_ISREG(st.st_mode):
                raise IntegrityError("SOURCE_NOT_REGULAR_FILE")
            size = st.st_size
            out["size_bytes"] = size
            if rec.get("expected_size") is not None and size != rec["expected_size"]:
                raise IntegrityError("FILE_SIZE_DIFFERS_FROM_PRIOR_INTAKE")
            md5 = hashlib.md5(usedforsecurity=False)
            sha256 = hashlib.sha256()
            n = 0
            while True:
                ensure_runtime(deadline)
                b = f.read(CHUNK)
                if not b:
                    break
                md5.update(b)
                sha256.update(b)
                n += len(b)
            out["md5"] = md5.hexdigest()
            out["sha256"] = sha256.hexdigest()
            out["matches_published_md5"] = out["md5"] == rec["md5"]
            out["matches_prior_author_sha256"] = out["sha256"] == rec["sha256"]
            if n != size or not out["matches_published_md5"] or not out["matches_prior_author_sha256"]:
                raise IntegrityError("SOURCE_HASH_OR_SIZE_MISMATCH")
            if rec["family"] == "ESA_ADB":
                out["archive_check"] = inspect_zip(f, rec, outer_only=outer_only,
                                                    scratch=scratch, limits=limits, deadline=deadline)
                out["status"] = "INCOMPLETE_NESTED_NOT_CHECKED" if outer_only else "PASS_FULL_OUTER_AND_NESTED_CRC"
            else:
                out["status"] = "PASS_MD5_SHA256"
    except FileNotFoundError:
        out["status"] = "MISSING_LOCAL_FILE"
    except (IntegrityError, zipfile.BadZipFile, RuntimeError, NotImplementedError, EOFError,
            OSError, ValueError, OverflowError) as e:
        out["status"] = "FAIL_INTEGRITY_OR_RESOURCE_LIMIT"
        out["failure_code"] = str(e) if isinstance(e, IntegrityError) else type(e).__name__
    return out


def run(args: argparse.Namespace) -> tuple[dict, int]:
    manifest = verify_local_manifest(args.repo)
    expected = expected_entries(manifest, args.esa_dir, args.ops_dir)
    if not args.outer_only:
        if args.scratch_dir is None or not args.scratch_dir.is_dir() or args.scratch_dir.is_symlink():
            raise IntegrityError("DEEP_ZIP_AUDIT_REQUIRES_LOCAL_SCRATCH_DIRECTORY")
    if args.max_runtime_seconds <= 0:
        raise IntegrityError("MAX_RUNTIME_MUST_BE_POSITIVE")
    deadline = time.monotonic() + args.max_runtime_seconds
    records = [audit_one(x, outer_only=args.outer_only, scratch=args.scratch_dir,
                         limits=DEFAULT_LIMITS, deadline=deadline) for x in expected]
    full = all(x["status"] in ("PASS_MD5_SHA256", "PASS_FULL_OUTER_AND_NESTED_CRC") for x in records)
    missing = any(x["status"] == "MISSING_LOCAL_FILE" for x in records)
    failed = any(x["status"].startswith("FAIL_") for x in records)
    status = ("PASS_ALL_NINE_LOCAL_IDENTITY_AND_NESTED_INTEGRITY" if full else
              "FAIL_LOCAL_INTEGRITY_OR_RESOURCE_LIMIT" if failed else
              "INCOMPLETE_SOURCE_FILES_NOT_MOUNTED" if missing else
              "INCOMPLETE_NESTED_ZIP_CHECKS")
    out = {"schema": 1, "study_id": "S10-RSEI-001", "stage": "G4_INTEGRITY_ONLY",
           "run_utc": datetime.now(timezone.utc).isoformat(),
           "frozen_G2_payload_commit": "8ed6a2b16233b86bf91672f6f15605dcf906c5eb",
           "status": status, "source_files_expected": 9, "source_files_passed": sum(x["status"].startswith("PASS_") for x in records),
           "source_files_missing": sum(x["status"] == "MISSING_LOCAL_FILE" for x in records),
           "original_telemetry_semantic_rows_inspected": 0, "archive_members_extracted_as_named_files": 0,
           "raw_telemetry_uploaded": False, "G4_scientific_execution_authorized": False,
           "PR_merge_authorized": False,
           "archive_check_scope": "OUTER_AND_ONE_NESTED_ZIP_LEVEL_CRC" if not args.outer_only else "OUTER_CRC_ONLY",
           "files": records}
    return out, 0 if full else 2 if failed else 3


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1],
                   help="Local checkout of exact frozen Study 10 Git documents")
    p.add_argument("--esa-dir", type=Path, required=True, help="Local directory with the SIX v1/v2 ESA-Mission*.zip files")
    p.add_argument("--ops-dir", type=Path, required=True, help="Local directory with dataset.csv, segments.csv, LICENSE (v2)")
    p.add_argument("--scratch-dir", type=Path, help="Local scratch directory for temporary nested-ZIP integrity validation")
    p.add_argument("--outer-only", action="store_true", help="Fast outer ZIP CRC audit only, does NOT satisfy full nested ZIP check")
    p.add_argument("--max-runtime-seconds", type=int, default=21600,
                   help="Local wall-clock safety cap across nine inputs (default: 21600 seconds)")
    p.add_argument("--report", type=Path, help="Optional local output of hash-only report; never original data")
    a = p.parse_args()
    try:
        out, code = run(a)
    except (IntegrityError, OSError, ValueError, KeyError, AssertionError) as e:
        out, code = {"schema": 1, "study_id": "S10-RSEI-001", "stage": "G4_INTEGRITY_ONLY",
                     "status": "FAIL_PRECHECK", "reason": str(e) if isinstance(e, IntegrityError) else type(e).__name__,
                     "G4_scientific_execution_authorized": False}, 2
    s = json.dumps(out, indent=2, sort_keys=True) + "\n"
    if a.report is not None:
        try:
            a.report.write_text(s, encoding="utf-8")
        except OSError:
            print("REPORT_WRITE_FAILED", file=sys.stderr)
            return 2
    print(s)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
