#!/usr/bin/env python3
"""Audit a WP11 local release candidate before any archive upload.

The audit verifies release checksums, safe archive paths/types, expected package
structure, and high-confidence credential/private-key indicators. It never
modifies the source campaign or the immutable release-candidate directory and
does not upload or publish anything.
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

EXPECTED_RELEASE_FILES = {
    *EXPECTED_ARCHIVES,
    "RELEASE_MANIFEST.json",
    "README_RELEASE.txt",
    "RELEASE_CHECKSUMS.sha256",
}

EXPECTED_CHECKSUM_TARGETS = (
    EXPECTED_RELEASE_FILES - {"RELEASE_CHECKSUMS.sha256"}
)
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
EXPECTED_FREEZE_BUNDLE_CHECKSUM_FILE_SHA256 = (
    "696bc615c1f227320aced30c1c88f4664f62def0cfbb454209e6068785e2d819"
)
ZENODO_MAX_FILES = 100
ZENODO_DEFAULT_MAX_BYTES = 50_000_000_000

SENSITIVE_SUFFIXES = {
    ".pem",
    ".key",
    ".p12",
    ".pfx",
    ".kdbx",
}
SENSITIVE_BASENAMES = {
    ".env",
    "credentials",
    "credentials.json",
    "secrets",
    "secrets.json",
}

SENSITIVE_PATH_COMPONENTS = {
    "credentials",
    "secrets",
}

SECRET_PATTERNS = {
    "PRIVATE_KEY_MARKER": re.compile(rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "AWS_ACCESS_KEY": re.compile(rb"\bAKIA[0-9A-Z]{16}\b"),
    "GITHUB_TOKEN": re.compile(rb"\bgh[pousr]_[A-Za-z0-9]{30,}\b"),
    "SLACK_TOKEN": re.compile(rb"\bxox[baprs]-[A-Za-z0-9-]{20,}\b"),
}

TEXT_SCAN_SUFFIXES = {
    ".txt", ".md", ".json", ".jsonl", ".csv", ".tsv", ".yaml", ".yml",
    ".ini", ".cfg", ".conf", ".toml", ".xml", ".log", ".sh", ".py", ".key",
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


def sha256_stream(handle) -> str:
    h = hashlib.sha256()
    for block in iter(lambda: handle.read(1024 * 1024), b""):
        h.update(block)
    return h.hexdigest()


def recompute_campaign_archive_identity(path: Path) -> dict:
    expected_prefix = "results/wp9/campaign/"
    expected_ledger = expected_prefix + "attempt-history.json"

    tree = hashlib.sha256()
    ledger_sha256 = None

    with tarfile.open(path, mode="r:gz") as tf:
        members = [member for member in tf if member.isfile()]

        names = [member.name for member in members]
        if len(names) != len(set(names)):
            raise RuntimeError(
                "Campaign archive contains duplicate regular-file names"
            )

        unexpected = [
            name
            for name in names
            if not name.startswith(expected_prefix)
        ]
        if unexpected:
            raise RuntimeError(
                "Campaign archive contains paths outside frozen campaign root: "
                + repr(unexpected[:10])
            )

        for member in sorted(members, key=lambda item: item.name):
            extracted = tf.extractfile(member)
            if extracted is None:
                raise RuntimeError(
                    f"Unable to read campaign archive member: {member.name}"
                )

            digest = sha256_stream(extracted)

            tree.update(member.name.encode("utf-8"))
            tree.update(b"\0")
            tree.update(digest.encode("ascii"))
            tree.update(b"\n")

            if member.name == expected_ledger:
                ledger_sha256 = digest

    if ledger_sha256 is None:
        raise RuntimeError(
            f"Campaign archive is missing authoritative ledger: {expected_ledger}"
        )

    return {
        "campaign_tree_sha256": tree.hexdigest(),
        "ledger_sha256": ledger_sha256,
        "regular_file_count": len(members),
    }


def verify_freeze_archive(path: Path) -> dict:
    expected_prefix = "wp9-integrity-freeze/"
    expected_checksum_name = (
        expected_prefix + "BUNDLE_CHECKSUMS.sha256"
    )

    with tarfile.open(path, mode="r:gz") as tf:
        members = list(tf)

        unsafe_members = [
            member.name
            for member in members
            if (
                not safe_member_name(member.name)
                or not member.isfile()
            )
        ]

        if unsafe_members:
            raise RuntimeError(
                "Integrity-freeze archive contains unsafe or "
                f"non-regular members: {unsafe_members[:25]}"
            )

        names = [
            member.name
            for member in members
        ]

        if len(names) != len(set(names)):
            duplicates = sorted(
                {
                    name
                    for name in names
                    if names.count(name) > 1
                }
            )
            raise RuntimeError(
                "Integrity-freeze archive contains duplicate "
                f"member names: {duplicates[:25]}"
            )

        outside_prefix = [
            name
            for name in names
            if not name.startswith(expected_prefix)
        ]

        if outside_prefix:
            raise RuntimeError(
                "Integrity-freeze archive contains members "
                "outside expected prefix: "
                f"{outside_prefix[:25]}"
            )

        regular_members = {
            member.name: member
            for member in members
        }

        if expected_checksum_name not in regular_members:
            raise RuntimeError(
                "Integrity-freeze archive is missing exact "
                f"checksum member {expected_checksum_name}"
            )

        checksum_member = regular_members[
            expected_checksum_name
        ]

        checksum_handle = tf.extractfile(
            checksum_member
        )

        if checksum_handle is None:
            raise RuntimeError(
                "Unable to read integrity-freeze checksum file"
            )

        checksum_payload = checksum_handle.read()

        checksum_sha256 = hashlib.sha256(
            checksum_payload
        ).hexdigest()

        if (
            checksum_sha256
            != EXPECTED_FREEZE_BUNDLE_CHECKSUM_FILE_SHA256
        ):
            raise RuntimeError(
                "Integrity-freeze BUNDLE_CHECKSUMS.sha256 "
                "identity mismatch: "
                f"expected "
                f"{EXPECTED_FREEZE_BUNDLE_CHECKSUM_FILE_SHA256}, "
                f"observed {checksum_sha256}"
            )

        base = PurePosixPath(
            expected_checksum_name
        ).parent

        parsed_targets = []

        for lineno, raw in enumerate(
            checksum_payload.decode(
                "utf-8"
            ).splitlines(),
            1,
        ):
            if not raw.strip():
                continue

            parts = raw.split(maxsplit=1)

            if (
                len(parts) != 2
                or len(parts[0]) != 64
            ):
                raise RuntimeError(
                    "Malformed integrity-freeze checksum "
                    f"line {lineno}: {raw!r}"
                )

            expected_digest = parts[0].lower()
            relative_name = parts[1].lstrip("* ")

            relative_path = PurePosixPath(
                relative_name
            )

            if (
                relative_path.is_absolute()
                or not relative_path.parts
                or ".." in relative_path.parts
                or "" in relative_path.parts
            ):
                raise RuntimeError(
                    "Unsafe integrity-freeze checksum "
                    f"target: {relative_name!r}"
                )

            target_name = (
                base / relative_path
            ).as_posix()

            if not safe_member_name(target_name):
                raise RuntimeError(
                    "Unsafe resolved integrity-freeze "
                    f"checksum target: {target_name!r}"
                )

            if not target_name.startswith(
                expected_prefix
            ):
                raise RuntimeError(
                    "Integrity-freeze checksum target "
                    "escapes expected archive prefix: "
                    f"{target_name}"
                )

            parsed_targets.append(
                (
                    expected_digest,
                    target_name,
                )
            )

        target_names = [
            name
            for _, name in parsed_targets
        ]

        if len(target_names) != len(
            set(target_names)
        ):
            raise RuntimeError(
                "Integrity-freeze checksum file contains "
                "duplicate target names"
            )

        if expected_checksum_name in set(
            target_names
        ):
            raise RuntimeError(
                "Integrity-freeze checksum manifest "
                "must not checksum itself"
            )

        expected_target_set = (
            set(names)
            - {expected_checksum_name}
        )

        actual_target_set = set(
            target_names
        )

        if actual_target_set != expected_target_set:
            missing_targets = sorted(
                actual_target_set
                - expected_target_set
            )

            unchecksummed_members = sorted(
                expected_target_set
                - actual_target_set
            )

            raise RuntimeError(
                "Integrity-freeze archive checksum "
                "coverage mismatch: "
                f"missing_targets={missing_targets}, "
                f"unchecksummed_members="
                f"{unchecksummed_members}"
            )

        verified = 0

        for expected_digest, target_name in (
            parsed_targets
        ):
            target_member = regular_members.get(
                target_name
            )

            if target_member is None:
                raise RuntimeError(
                    "Integrity-freeze checksum target "
                    "missing from archive: "
                    f"{target_name}"
                )

            target_handle = tf.extractfile(
                target_member
            )

            if target_handle is None:
                raise RuntimeError(
                    "Unable to read integrity-freeze "
                    f"member: {target_name}"
                )

            observed_digest = sha256_stream(
                target_handle
            )

            if observed_digest != expected_digest:
                raise RuntimeError(
                    "Integrity-freeze checksum mismatch "
                    f"for {target_name}: expected "
                    f"{expected_digest}, observed "
                    f"{observed_digest}"
                )

            verified += 1

    if verified != len(expected_target_set):
        raise RuntimeError(
            "Integrity-freeze archive verified-target "
            f"count mismatch: expected "
            f"{len(expected_target_set)}, "
            f"observed {verified}"
        )

    return {
        "bundle_checksum_file":
            expected_checksum_name,
        "bundle_checksum_file_sha256":
            checksum_sha256,
        "regular_file_count":
            len(names),
        "checksum_target_count":
            len(actual_target_set),
        "verified_entries":
            verified,
        "complete_checksum_coverage":
            True,
    }


def sensitive_member_name(
    posix: PurePosixPath,
) -> bool:
    base_lower = posix.name.lower()
    suffix_lower = posix.suffix.lower()
    parent_parts_lower = {
        part.lower()
        for part in posix.parts[:-1]
    }

    return (
        suffix_lower in SENSITIVE_SUFFIXES
        or base_lower in SENSITIVE_BASENAMES
        or base_lower.startswith(".env.")
        or bool(
            parent_parts_lower
            & SENSITIVE_PATH_COMPONENTS
        )
    )


def scan_archive(path: Path) -> dict:
    member_count = 0
    regular_count = 0
    unsafe_members = []
    duplicate_members = []
    seen_member_names = set()
    sensitive_name_candidates = []
    secret_candidates = []

    with tarfile.open(path, mode="r:gz") as tf:
        for member in tf:
            member_count += 1

            if member.name in seen_member_names:
                duplicate_members.append(member.name)
            else:
                seen_member_names.add(member.name)

            if not safe_member_name(member.name):
                unsafe_members.append(member.name)
                continue

            if not member.isfile():
                # Deterministic packager should emit regular files only.
                unsafe_members.append(f"{member.name} [type={member.type!r}]")
                continue

            regular_count += 1
            posix = PurePosixPath(member.name)
            suffix_lower = posix.suffix.lower()
            sensitive_name = sensitive_member_name(
                posix
            )

            if sensitive_name:
                sensitive_name_candidates.append(
                    member.name
                )

            should_scan = (
                member.size
                <= MAX_SCAN_MEMBER_BYTES
                and (
                    suffix_lower
                    in TEXT_SCAN_SUFFIXES
                    or sensitive_name
                )
            )

            if should_scan:
                extracted = tf.extractfile(member)
                if extracted is None:
                    continue
                payload = extracted.read()
                for label, pattern in SECRET_PATTERNS.items():
                    if pattern.search(payload):
                        secret_candidates.append(
                            {
                                "member": member.name,
                                "pattern": label,
                            }
                        )

    return {
        "member_count": member_count,
        "regular_file_count": regular_count,
        "unsafe_members": unsafe_members,
        "duplicate_members": sorted(set(duplicate_members)),
        "sensitive_filename_candidates": sensitive_name_candidates,
        "high_confidence_secret_candidates": secret_candidates,
    }



def verify_manifest_archive_metadata(
    manifest: dict,
    release_dir: Path,
    reports: dict,
    checksum_by_name: dict[str, str],
) -> dict:
    entries = manifest.get("archives")

    if not isinstance(entries, list):
        raise RuntimeError(
            "Manifest archives field must be a list"
        )

    if len(entries) != len(EXPECTED_ARCHIVES):
        raise RuntimeError(
            "Manifest archive-entry count mismatch: "
            f"expected {len(EXPECTED_ARCHIVES)}, "
            f"observed {len(entries)}"
        )

    if not all(
        isinstance(item, dict)
        for item in entries
    ):
        raise RuntimeError(
            "Manifest archives field contains non-object entries"
        )

    names = [
        item.get("name")
        for item in entries
    ]

    if not all(
        isinstance(name, str)
        for name in names
    ):
        raise RuntimeError(
            "Manifest archive entry has missing/non-string name"
        )

    if len(names) != len(set(names)):
        raise RuntimeError(
            "Manifest contains duplicate archive names"
        )

    if set(names) != EXPECTED_ARCHIVES:
        raise RuntimeError(
            "Unexpected archive set in manifest: "
            f"expected {sorted(EXPECTED_ARCHIVES)}, "
            f"observed {sorted(names)}"
        )

    by_name = {
        item["name"]: item
        for item in entries
    }

    verified = {}

    for name in sorted(EXPECTED_ARCHIVES):
        item = by_name[name]
        archive_path = release_dir / name

        if not archive_path.is_file():
            raise RuntimeError(
                f"Manifest archive object missing: {name}"
            )

        observed_sha256 = sha256_file(
            archive_path
        )
        observed_bytes = archive_path.stat().st_size
        observed_file_count = reports[
            name
        ]["regular_file_count"]

        manifest_sha256 = item.get("sha256")
        manifest_bytes = item.get("bytes")
        manifest_file_count = item.get(
            "archived_file_count"
        )

        if (
            not isinstance(manifest_sha256, str)
            or len(manifest_sha256) != 64
        ):
            raise RuntimeError(
                "Manifest archive SHA-256 field is malformed "
                f"for {name}: {manifest_sha256!r}"
            )

        if type(manifest_bytes) is not int:
            raise RuntimeError(
                "Manifest archive byte-count field is not "
                f"an integer for {name}: {manifest_bytes!r}"
            )

        if type(manifest_file_count) is not int:
            raise RuntimeError(
                "Manifest archive file-count field is not "
                f"an integer for {name}: "
                f"{manifest_file_count!r}"
            )

        if manifest_sha256 != observed_sha256:
            raise RuntimeError(
                "Manifest/archive SHA-256 mismatch for "
                f"{name}: manifest={manifest_sha256}, "
                f"observed={observed_sha256}"
            )

        checksum_sha256 = checksum_by_name.get(
            name
        )

        if checksum_sha256 != observed_sha256:
            raise RuntimeError(
                "Manifest/archive/release-checksum identity "
                f"mismatch for {name}: "
                f"release_checksum={checksum_sha256!r}, "
                f"observed={observed_sha256}"
            )

        if manifest_bytes != observed_bytes:
            raise RuntimeError(
                "Manifest/archive byte-count mismatch for "
                f"{name}: manifest={manifest_bytes}, "
                f"observed={observed_bytes}"
            )

        if (
            manifest_file_count
            != observed_file_count
        ):
            raise RuntimeError(
                "Manifest/archive file-count mismatch for "
                f"{name}: manifest={manifest_file_count}, "
                f"observed={observed_file_count}"
            )

        verified[name] = {
            "sha256": observed_sha256,
            "bytes": observed_bytes,
            "archived_file_count":
                observed_file_count,
        }

    return {
        "verified_archive_count":
            len(verified),
        "archives":
            verified,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("release_dir")
    parser.add_argument(
        "--audit-report",
        help=(
            "Output path for audit JSON. Defaults beside the candidate as "
            "<candidate>.LOCAL_AUDIT_REPORT.json; never written inside candidate."
        ),
    )
    args = parser.parse_args()

    release_dir = Path(args.release_dir).expanduser().resolve()
    if not release_dir.is_dir():
        raise RuntimeError(f"Release directory not found: {release_dir}")

    candidate_entries = list(release_dir.iterdir())

    candidate_symlinks = sorted(
        entry.name
        for entry in candidate_entries
        if entry.is_symlink()
    )
    if candidate_symlinks:
        raise RuntimeError(
            "Release candidate contains symbolic-link objects: "
            f"{candidate_symlinks}"
        )

    non_files = sorted(
        entry.name
        for entry in candidate_entries
        if not entry.is_file()
    )
    if non_files:
        raise RuntimeError(
            "Release candidate contains non-file entries: "
            f"{non_files}"
        )

    release_names = {
        entry.name
        for entry in candidate_entries
        if entry.is_file()
    }
    if release_names != EXPECTED_RELEASE_FILES:
        raise RuntimeError(
            "Release candidate object-set mismatch: "
            f"expected {sorted(EXPECTED_RELEASE_FILES)}, "
            f"observed {sorted(release_names)}"
        )

    checksum_path = release_dir / "RELEASE_CHECKSUMS.sha256"
    manifest_path = release_dir / "RELEASE_MANIFEST.json"

    checksum_entries = parse_checksums(checksum_path)
    checksum_names = {name for _, name in checksum_entries}

    if len(checksum_names) != len(checksum_entries):
        raise RuntimeError(
            "RELEASE_CHECKSUMS.sha256 contains duplicate target names"
        )

    if checksum_names != EXPECTED_CHECKSUM_TARGETS:
        raise RuntimeError(
            "Release checksum target-set mismatch: "
            f"expected {sorted(EXPECTED_CHECKSUM_TARGETS)}, "
            f"observed {sorted(checksum_names)}"
        )

    checksum_by_name = {
        name: digest
        for digest, name in checksum_entries
    }

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
        "freeze_bundle_checksum_file_sha256":
            EXPECTED_FREEZE_BUNDLE_CHECKSUM_FILE_SHA256,
    }
    for key, expected in expected_identity.items():
        if identity.get(key) != expected:
            raise RuntimeError(
                f"Manifest source identity mismatch for {key}: "
                f"expected {expected}, observed {identity.get(key)!r}"
            )

    reports = {}
    for name in sorted(EXPECTED_ARCHIVES):
        path = release_dir / name
        if name not in checksum_names:
            raise RuntimeError(f"Archive is not covered by RELEASE_CHECKSUMS.sha256: {name}")
        reports[name] = scan_archive(path)

    for archive_name, report in reports.items():
        if report["unsafe_members"]:
            raise RuntimeError(
                "Archive contains unsafe or non-regular members: "
                f"{archive_name}: {report['unsafe_members'][:25]}"
            )

        if report["duplicate_members"]:
            raise RuntimeError(
                "Archive contains duplicate member names: "
                f"{archive_name}: {report['duplicate_members'][:25]}"
            )

    manifest_archive_verification = (
        verify_manifest_archive_metadata(
            manifest,
            release_dir,
            reports,
            checksum_by_name,
        )
    )

    campaign_report = reports["01-wp9-campaign-raw.tar.gz"]
    if campaign_report["regular_file_count"] != EXPECTED_CAMPAIGN_FILE_COUNT:
        raise RuntimeError(
            "Campaign archive member-count mismatch: "
            f"expected {EXPECTED_CAMPAIGN_FILE_COUNT}, "
            f"observed {campaign_report['regular_file_count']}"
        )

    campaign_identity = recompute_campaign_archive_identity(
        release_dir / "01-wp9-campaign-raw.tar.gz"
    )

    if (
        campaign_identity["regular_file_count"]
        != EXPECTED_CAMPAIGN_FILE_COUNT
    ):
        raise RuntimeError(
            "Recomputed campaign archive member-count mismatch: "
            f"expected {EXPECTED_CAMPAIGN_FILE_COUNT}, "
            f"observed {campaign_identity['regular_file_count']}"
        )

    if campaign_identity["ledger_sha256"] != EXPECTED_LEDGER_SHA256:
        raise RuntimeError(
            "Campaign archive ledger identity mismatch: "
            f"expected {EXPECTED_LEDGER_SHA256}, "
            f"observed {campaign_identity['ledger_sha256']}"
        )

    if (
        campaign_identity["campaign_tree_sha256"]
        != EXPECTED_TREE_SHA256
    ):
        raise RuntimeError(
            "Campaign archive tree identity mismatch: "
            f"expected {EXPECTED_TREE_SHA256}, "
            f"observed {campaign_identity['campaign_tree_sha256']}"
        )

    freeze_identity = verify_freeze_archive(
        release_dir / "02-wp9-integrity-freeze.tar.gz"
    )

    # Publication bundle must not contain raw campaign data or runtime/source implementation.
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

    if forbidden_publication:
        raise RuntimeError(
            "Publication/provenance archive contains "
            "forbidden release paths: "
            f"{forbidden_publication[:25]}"
        )

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

    # The candidate directory is immutable after preparation; count/size it before
    # writing the audit report outside that directory.
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
        "release_candidate_unchanged_by_audit": True,
        "release_file_count": file_count,
        "release_total_bytes": total_bytes,
        "checksum_entries_verified": len(checksum_entries),
        "archives": reports,
        "manifest_archive_metadata_verification":
            manifest_archive_verification,
        "recomputed_campaign_archive_identity": campaign_identity,
        "verified_integrity_freeze_archive": freeze_identity,
        "forbidden_publication_bundle_paths": forbidden_publication,
        "zenodo_default_file_count_gate": file_count <= ZENODO_MAX_FILES,
        "zenodo_default_size_gate": total_bytes <= ZENODO_DEFAULT_MAX_BYTES,
        "upload_performed": False,
        "publication_performed": False,
        "doi_assigned": False,
    }

    audit_path = (
        Path(args.audit_report).expanduser().resolve()
        if args.audit_report
        else release_dir.parent / f"{release_dir.name}.LOCAL_AUDIT_REPORT.json"
    )
    try:
        audit_path.relative_to(release_dir)
    except ValueError:
        pass
    else:
        raise RuntimeError(
            "Audit report must be outside the immutable release-candidate directory"
        )
    if audit_path.exists():
        raise RuntimeError(f"Refusing to overwrite existing audit report: {audit_path}")
    audit_path.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print("============================================================")
    print("WP11 LOCAL RELEASE AUDIT")
    print("============================================================")
    print(f"release_dir={release_dir}")
    print(f"audit_report={audit_path}")
    print(f"release_file_count={file_count}")
    print(f"release_total_bytes={total_bytes}")
    print(f"checksum_entries_verified={len(checksum_entries)}")
    for name in sorted(reports):
        report = reports[name]
        print(
            f"archive={name} members={report['regular_file_count']} "
            f"unsafe={len(report['unsafe_members'])} "
            f"duplicates={len(report['duplicate_members'])} "
            f"sensitive_names={len(report['sensitive_filename_candidates'])} "
            f"secret_candidates={len(report['high_confidence_secret_candidates'])}"
        )
    print(
        "recomputed_campaign_tree_sha256="
        + campaign_identity["campaign_tree_sha256"]
    )
    print(
        "recomputed_campaign_ledger_sha256="
        + campaign_identity["ledger_sha256"]
    )
    print(
        "freeze_bundle_checksum_file_sha256="
        + freeze_identity["bundle_checksum_file_sha256"]
    )
    print(
        "freeze_bundle_verified_entries="
        + str(freeze_identity["verified_entries"])
    )
    print(f"forbidden_publication_bundle_paths={len(forbidden_publication)}")
    print("exact_release_object_set=PASS")
    print("release_checksum_target_set=PASS")
    print(
        "manifest_archive_metadata_verified="
        + str(
            manifest_archive_verification[
                "verified_archive_count"
            ]
        )
    )
    print("manifest_archive_metadata_identity=PASS")
    print("campaign_archive_identity=PASS")
    print("integrity_freeze_archive_identity=PASS")
    print("release_candidate_unchanged_by_audit=true")
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
