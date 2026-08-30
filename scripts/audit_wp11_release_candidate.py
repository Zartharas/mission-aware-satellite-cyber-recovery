#!/usr/bin/env python3
"""Audit a WP11 local release candidate before any archive upload.

The audit verifies release checksums, safe archive paths/types, expected package
structure, and high-confidence credential/private-key indicators. It never
modifies the source campaign and does not upload or publish anything.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import sys
import tarfile

EXPECTED_SCHEMA = "WP11_RELEASE_CANDIDATE_V1"
EXPECTED_ARCHIVES = {
    "01-wp9-campaign-raw.tar.gz",
    "02-wp9-integrity-freeze.tar.gz",
    "03-publication-and-provenance.tar.gz",
}
EXPECTED_CAMPAIGN_FILE_COUNT = 17182
EXPECTED_LEDGER_SHA256 = (
    "92893a2fd8746f410bffd4dca5101bc3f533ada2ff82f98681788cf0c24ce6fd"
)
EXPECTED_TREE_SHA256 = (
    "ad1e127b4431b6b334955129fcba82f76b18e5b43585395ac8c37300cac087b1"
)
EXPECTED_MEMBERSHIP_SHA256 = (
    "a2bf0c8f352f4386e74a500d97ea8f73e0c39d03bfe10ac0ebcf02470af9f70e"
)
ZENODO_MAX_FILES = 100
ZENODO_DEFAULT_MAX_BYTES = 50_000_000_000

SENSITIVE_SUFFIXES = {
    ".pem",
    ".p12",
    ".pfx",
    ".kdbx",
}
SENSITIVE_BASENAMES = {
    ".env",
    "credentials",
    "credentials.json",
    "secrets.json",
}

SECRET_PATTERNS = {
    "PRIVATE_KEY_MARKER": re.compile(rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "AWS_ACCESS_KEY": re.compile(rb"\bAKIA[0-9A-Z]{16}\b"),
    "GITHUB_TOKEN": re.compile(rb"\bgh[pousr]_[A-Za-z0-9]{30,}\b"),
    "SLACK_TOKEN": re.compile(rb"\bxox[baprs]-[A-Za-z0-9-]{20,}\b"),
}

TEXT_SCAN_SUFFIXES = {
    ".txt", ".md", ".json", ".jsonl", ".csv", ".tsv", ".yaml", ".yml",
    ".ini", ".cfg", ".conf", ".toml", ".xml", ".log", ".sh", ".py",
}
MAX_SCAN_MEMBER_BYTES = 10 * 1024 * 1024


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def parse_checksums(path: Path) -> list[tuple[str, str]]:
    entries = []
    for lineno, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip():
            continue
        parts = raw.split(maxsplit=1)
        if len(parts) != 2 or len(parts[0]) != 64:
            raise RuntimeError(f"Malformed checksum line {lineno}: {raw!r}")
        entries.append((parts[0].lower(), parts[1].lstrip("* ")))
    return entries


def safe_member_name(name: str) -> bool:
    p = PurePosixPath(name)
    if p.is_absolute():
        return False
    return all(part not in {"..", ""} for part in p.parts)


def scan_archive(path: Path) -> dict:
    member_count = 0
    regular_count = 0
    unsafe_members = []
    sensitive_name_candidates = []
    secret_candidates = []

    with tarfile.open(path, mode="r:gz") as tf:
        for member in tf:
            member_count += 1
            if not safe_member_name(member.name):
                unsafe_members.append(member.name)
                continue

            if not member.isfile():
                # Deterministic packager should emit regular files only.
                unsafe_members.append(f"{member.name} [type={member.type!r}]")
                continue

            regular_count += 1
            posix = PurePosixPath(member.name)
            base_lower = posix.name.lower()
            suffix_lower = posix.suffix.lower()

            if suffix_lower in SENSITIVE_SUFFIXES or base_lower in SENSITIVE_BASENAMES:
                sensitive_name_candidates.append(member.name)

            if member.size <= MAX_SCAN_MEMBER_BYTES and suffix_lower in TEXT_SCAN_SUFFIXES:
                extracted = tf.extractfile(member)
                if extracted is None:
                    continue
                payload = extracted.read()
                for label, pattern in SECRET_PATTERNS.items():
                    if pattern.search(payload):
                        secret_candidates.append({"member": member.name, "pattern": label})

    return {
        "member_count": member_count,
        "regular_file_count": regular_count,
        "unsafe_members": unsafe_members,
        "sensitive_filename_candidates": sensitive_name_candidates,
        "high_confidence_secret_candidates": secret_candidates,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("release_dir")
    args = parser.parse_args()

    release_dir = Path(args.release_dir).expanduser().resolve()
    if not release_dir.is_dir():
        raise RuntimeError(f"Release directory not found: {release_dir}")

    checksum_path = release_dir / "RELEASE_CHECKSUMS.sha256"
    manifest_path = release_dir / "RELEASE_MANIFEST.json"
    if not checksum_path.is_file() or not manifest_path.is_file():
        raise RuntimeError("Missing RELEASE_CHECKSUMS.sha256 or RELEASE_MANIFEST.json")

    checksum_entries = parse_checksums(checksum_path)
    checksum_names = {name for _, name in checksum_entries}
    for expected, name in checksum_entries:
        target = release_dir / name
        if not target.is_file():
            raise RuntimeError(f"Missing checksummed release object: {name}")
        observed = sha256_file(target)
        if observed != expected:
            raise RuntimeError(
                f"Release checksum mismatch for {name}: expected {expected}, observed {observed}"
            )

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("schema") != EXPECTED_SCHEMA:
        raise RuntimeError(f"Unexpected release schema: {manifest.get('schema')!r}")
    if manifest.get("status") != "LOCAL_RELEASE_CANDIDATE_NOT_UPLOADED_NOT_PUBLISHED":
        raise RuntimeError(f"Unexpected release status: {manifest.get('status')!r}")

    identity = manifest.get("source_identity", {})
    expected_identity = {
        "ledger_sha256": EXPECTED_LEDGER_SHA256,
        "campaign_tree_sha256": EXPECTED_TREE_SHA256,
        "analysis_membership_sha256": EXPECTED_MEMBERSHIP_SHA256,
    }
    for key, expected in expected_identity.items():
        if identity.get(key) != expected:
            raise RuntimeError(
                f"Manifest source identity mismatch for {key}: "
                f"expected {expected}, observed {identity.get(key)!r}"
            )

    archive_names = {item.get("name") for item in manifest.get("archives", [])}
    if archive_names != EXPECTED_ARCHIVES:
        raise RuntimeError(
            f"Unexpected archive set: expected {sorted(EXPECTED_ARCHIVES)}, "
            f"observed {sorted(archive_names)}"
        )

    reports = {}
    for name in sorted(EXPECTED_ARCHIVES):
        path = release_dir / name
        if name not in checksum_names:
            raise RuntimeError(f"Archive is not covered by RELEASE_CHECKSUMS.sha256: {name}")
        reports[name] = scan_archive(path)

    campaign_report = reports["01-wp9-campaign-raw.tar.gz"]
    if campaign_report["regular_file_count"] != EXPECTED_CAMPAIGN_FILE_COUNT:
        raise RuntimeError(
            "Campaign archive member-count mismatch: "
            f"expected {EXPECTED_CAMPAIGN_FILE_COUNT}, "
            f"observed {campaign_report['regular_file_count']}"
        )

    # Publication bundle must not contain raw campaign data or runtime/source implementation.
    publication_report = reports["03-publication-and-provenance.tar.gz"]
    with tarfile.open(release_dir / "03-publication-and-provenance.tar.gz", "r:gz") as tf:
        publication_names = [m.name for m in tf if m.isfile()]
    forbidden_publication_prefixes = (
        "results/wp9/campaign/",
        "src/",
        "tests/",
        "configs/",
        "artifacts/runtime/",
    )
    forbidden_publication = [
        name for name in publication_names
        if name.startswith(forbidden_publication_prefixes)
    ]

    all_unsafe = [
        {"archive": name, "members": report["unsafe_members"]}
        for name, report in reports.items()
        if report["unsafe_members"]
    ]
    sensitive_names = [
        {"archive": name, "members": report["sensitive_filename_candidates"]}
        for name, report in reports.items()
        if report["sensitive_filename_candidates"]
    ]
    secrets = [
        {"archive": name, "candidates": report["high_confidence_secret_candidates"]}
        for name, report in reports.items()
        if report["high_confidence_secret_candidates"]
    ]

    release_files = [p for p in release_dir.iterdir() if p.is_file()]
    total_bytes = sum(p.stat().st_size for p in release_files)
    file_count = len(release_files)

    if file_count > ZENODO_MAX_FILES:
        raise RuntimeError(f"Release object count {file_count} exceeds {ZENODO_MAX_FILES}")
    if total_bytes > ZENODO_DEFAULT_MAX_BYTES:
        raise RuntimeError(
            f"Release bytes {total_bytes} exceed default quota {ZENODO_DEFAULT_MAX_BYTES}"
        )

    status = "PASS"
    review_reasons = []
    if all_unsafe:
        status = "REVIEW_REQUIRED"
        review_reasons.append("unsafe_or_nonregular_archive_members")
    if sensitive_names:
        status = "REVIEW_REQUIRED"
        review_reasons.append("sensitive_filename_candidates")
    if secrets:
        status = "REVIEW_REQUIRED"
        review_reasons.append("high_confidence_secret_candidates")
    if forbidden_publication:
        status = "REVIEW_REQUIRED"
        review_reasons.append("forbidden_publication_bundle_paths")

    audit = {
        "schema": "WP11_LOCAL_RELEASE_AUDIT_V1",
        "status": status,
        "review_reasons": review_reasons,
        "release_dir": str(release_dir),
        "release_file_count": file_count,
        "release_total_bytes": total_bytes,
        "checksum_entries_verified": len(checksum_entries),
        "archives": reports,
        "forbidden_publication_bundle_paths": forbidden_publication,
        "zenodo_default_file_count_gate": file_count <= ZENODO_MAX_FILES,
        "zenodo_default_size_gate": total_bytes <= ZENODO_DEFAULT_MAX_BYTES,
        "upload_performed": False,
        "publication_performed": False,
        "doi_assigned": False,
    }

    audit_path = release_dir / "LOCAL_AUDIT_REPORT.json"
    if audit_path.exists():
        raise RuntimeError(f"Refusing to overwrite existing audit report: {audit_path}")
    audit_path.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print("============================================================")
    print("WP11 LOCAL RELEASE AUDIT")
    print("============================================================")
    print(f"release_dir={release_dir}")
    print(f"release_file_count_before_audit_report={file_count}")
    print(f"release_total_bytes_before_audit_report={total_bytes}")
    print(f"checksum_entries_verified={len(checksum_entries)}")
    for name in sorted(reports):
        report = reports[name]
        print(
            f"archive={name} members={report['regular_file_count']} "
            f"unsafe={len(report['unsafe_members'])} "
            f"sensitive_names={len(report['sensitive_filename_candidates'])} "
            f"secret_candidates={len(report['high_confidence_secret_candidates'])}"
        )
    print(f"forbidden_publication_bundle_paths={len(forbidden_publication)}")
    print(f"zenodo_default_file_count_gate={'PASS' if file_count <= ZENODO_MAX_FILES else 'FAIL'}")
    print(f"zenodo_default_size_gate={'PASS' if total_bytes <= ZENODO_DEFAULT_MAX_BYTES else 'FAIL'}")
    print(f"wp11_local_release_audit={status}")
    print("zenodo_upload_performed=false")
    print("zenodo_publication_performed=false")
    print("doi_assigned=false")

    return 0 if status == "PASS" else 2


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"WP11_LOCAL_RELEASE_AUDIT_ERROR={exc}", file=sys.stderr)
        raise SystemExit(1)
