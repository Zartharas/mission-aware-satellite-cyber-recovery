#!/usr/bin/env python3
"""Prepare a deterministic WP11 release candidate without mutating raw evidence.

This tool is intentionally packaging-only. It verifies the frozen WP9 campaign
and integrity-freeze identities, creates a small set of normalized tar.gz
objects outside the repository, writes checksums/manifest metadata, and then
re-verifies that the source campaign and Git worktree are unchanged.

It does NOT upload to Zenodo, publish a DOI, modify results/wp9/campaign, stage
Git files, commit, push, or remove/quarantine evidence.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
import tarfile
from typing import Iterable

EXPECTED_REPO_NAME = "mission-aware-satellite-cyber-recovery"
MINIMUM_MANUSCRIPT_COMMIT = "81fd0e5a5c56d7c0d8a7bc398c5bddb65988c442"

EXPECTED_LEDGER_SHA256 = (
    "92893a2fd8746f410bffd4dca5101bc3f533ada2ff82f98681788cf0c24ce6fd"
)
EXPECTED_CAMPAIGN_TREE_SHA256 = (
    "ad1e127b4431b6b334955129fcba82f76b18e5b43585395ac8c37300cac087b1"
)
EXPECTED_ANALYSIS_MEMBERSHIP_SHA256 = (
    "a2bf0c8f352f4386e74a500d97ea8f73e0c39d03bfe10ac0ebcf02470af9f70e"
)
EXPECTED_CAMPAIGN_FILE_COUNT = 17182
EXPECTED_LEDGER_RECORDS = 729
EXPECTED_VALID = 720
EXPECTED_INVALID = 9
EXPECTED_FREEZE_BUNDLE_CHECKSUM_FILE_SHA256 = (
    "696bc615c1f227320aced30c1c88f4664f62def0cfbb454209e6068785e2d819"
)

ZENODO_MAX_FILES = 100
ZENODO_DEFAULT_MAX_BYTES = 50_000_000_000


def run_git(repo: Path, *args: str) -> str:
    proc = subprocess.run(
        ["git", *args],
        cwd=repo,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(
            f"git {' '.join(args)} failed ({proc.returncode}): {proc.stderr.strip()}"
        )
    return proc.stdout.strip()


def verify_git_identity_unchanged(
    repo: Path,
    expected_branch: str,
    expected_head: str,
    expected_status: str,
) -> dict:
    observed_branch = run_git(
        repo,
        "branch",
        "--show-current",
    )
    observed_head = run_git(
        repo,
        "rev-parse",
        "HEAD",
    )
    observed_status = run_git(
        repo,
        "status",
        "--porcelain",
    )

    if observed_branch != expected_branch:
        raise RuntimeError(
            "Repository branch changed during packaging: "
            f"expected {expected_branch!r}, "
            f"observed {observed_branch!r}"
        )

    if observed_head != expected_head:
        raise RuntimeError(
            "Repository HEAD changed during packaging: "
            f"expected {expected_head}, "
            f"observed {observed_head}"
        )

    if observed_status != expected_status:
        raise RuntimeError(
            "Git worktree changed during packaging"
        )

    return {
        "branch": observed_branch,
        "head": observed_head,
        "status": observed_status,
    }


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def all_regular_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*"):
        if path.is_symlink():
            raise RuntimeError(f"Symlink not permitted in frozen release source: {path}")
        if path.is_file():
            files.append(path)
    return sorted(files, key=lambda p: p.as_posix())


def campaign_tree_identity(repo: Path, campaign_root: Path) -> tuple[str, int]:
    files = all_regular_files(campaign_root)
    h = hashlib.sha256()
    for path in files:
        relative = path.relative_to(repo).as_posix()
        digest = sha256_file(path)
        h.update(relative.encode("utf-8"))
        h.update(b"\0")
        h.update(digest.encode("ascii"))
        h.update(b"\n")
    return h.hexdigest(), len(files)


def parse_ledger(path: Path) -> list[dict]:
    obj = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(obj, list):
        records = obj
    elif isinstance(obj, dict):
        for key in ("attempts", "records", "history"):
            value = obj.get(key)
            if isinstance(value, list):
                records = value
                break
        else:
            raise RuntimeError("Unable to locate ledger record array")
    else:
        raise RuntimeError("Unexpected ledger JSON structure")

    if not all(isinstance(row, dict) for row in records):
        raise RuntimeError("Ledger contains non-object records")
    return records


def verify_ledger(path: Path) -> dict:
    digest = sha256_file(path)
    if digest != EXPECTED_LEDGER_SHA256:
        raise RuntimeError(
            f"ledger SHA mismatch: expected {EXPECTED_LEDGER_SHA256}, observed {digest}"
        )

    records = parse_ledger(path)
    valid = sum(row.get("attempt_status") == "VALID" for row in records)
    invalid = sum(row.get("attempt_status") == "INVALID" for row in records)

    if (len(records), valid, invalid) != (
        EXPECTED_LEDGER_RECORDS,
        EXPECTED_VALID,
        EXPECTED_INVALID,
    ):
        raise RuntimeError(
            "ledger count mismatch: "
            f"records={len(records)} valid={valid} invalid={invalid}"
        )

    return {
        "sha256": digest,
        "records": len(records),
        "valid": valid,
        "invalid": invalid,
    }


def parse_sha256_manifest(path: Path) -> list[tuple[str, str]]:
    entries: list[tuple[str, str]] = []
    for lineno, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.strip()
        if not line:
            continue
        parts = line.split(maxsplit=1)
        if len(parts) != 2 or len(parts[0]) != 64:
            raise RuntimeError(f"Malformed checksum line {path}:{lineno}: {raw!r}")
        digest, name = parts
        name = name.lstrip("* ")
        entries.append((digest.lower(), name))
    return entries


def verify_freeze_bundle(freeze_dir: Path) -> dict:
    root = freeze_dir.resolve()

    paths = sorted(
        root.rglob("*"),
        key=lambda path: path.as_posix(),
    )

    symlinks = [
        path.relative_to(root).as_posix()
        for path in paths
        if path.is_symlink()
    ]
    if symlinks:
        raise RuntimeError(
            "Symlinks are not permitted in frozen integrity bundle: "
            f"{symlinks}"
        )

    special_entries = [
        path.relative_to(root).as_posix()
        for path in paths
        if (
            not path.is_symlink()
            and not path.is_file()
            and not path.is_dir()
        )
    ]
    if special_entries:
        raise RuntimeError(
            "Special filesystem entries are not permitted in "
            f"frozen integrity bundle: {special_entries}"
        )

    regular_files = [
        path
        for path in paths
        if path.is_file()
    ]

    candidates = [
        path
        for path in regular_files
        if path.name == "BUNDLE_CHECKSUMS.sha256"
    ]

    if len(candidates) != 1:
        raise RuntimeError(
            "Expected exactly one BUNDLE_CHECKSUMS.sha256 under "
            f"{freeze_dir}; found {len(candidates)}"
        )

    manifest = candidates[0]

    if manifest.parent.resolve() != root:
        raise RuntimeError(
            "BUNDLE_CHECKSUMS.sha256 must be at the freeze "
            f"directory root; observed {manifest}"
        )

    manifest_sha = sha256_file(manifest)

    if (
        manifest_sha
        != EXPECTED_FREEZE_BUNDLE_CHECKSUM_FILE_SHA256
    ):
        raise RuntimeError(
            "freeze bundle checksum-file SHA mismatch: "
            f"expected "
            f"{EXPECTED_FREEZE_BUNDLE_CHECKSUM_FILE_SHA256}, "
            f"observed {manifest_sha}"
        )

    entries = parse_sha256_manifest(manifest)

    normalized_entries: list[tuple[str, str]] = []

    for expected, raw_name in entries:
        posix = PurePosixPath(raw_name)

        if (
            posix.is_absolute()
            or not posix.parts
            or ".." in posix.parts
            or "" in posix.parts
        ):
            raise RuntimeError(
                "Unsafe checksum entry in frozen integrity bundle: "
                f"{raw_name!r}"
            )

        normalized_entries.append(
            (
                expected,
                posix.as_posix(),
            )
        )

    target_names = [
        name
        for _, name in normalized_entries
    ]

    if len(target_names) != len(set(target_names)):
        raise RuntimeError(
            "Duplicate checksum target in frozen integrity bundle"
        )

    manifest_relative = (
        manifest.relative_to(root).as_posix()
    )

    if manifest_relative in set(target_names):
        raise RuntimeError(
            "BUNDLE_CHECKSUMS.sha256 must not checksum itself"
        )

    expected_target_set = {
        path.relative_to(root).as_posix()
        for path in regular_files
        if path != manifest
    }

    actual_target_set = set(target_names)

    if actual_target_set != expected_target_set:
        missing_files = sorted(
            actual_target_set - expected_target_set
        )
        unchecksummed_files = sorted(
            expected_target_set - actual_target_set
        )

        raise RuntimeError(
            "Frozen integrity-bundle checksum coverage mismatch: "
            f"missing_targets={missing_files}, "
            f"unchecksummed_files={unchecksummed_files}"
        )

    verified = 0

    for expected, name in normalized_entries:
        target = (root / name).resolve()

        try:
            target.relative_to(root)
        except ValueError as exc:
            raise RuntimeError(
                f"Checksum entry escapes freeze directory: {name}"
            ) from exc

        if not target.is_file():
            raise RuntimeError(
                f"Missing freeze-bundle file: {target}"
            )

        observed = sha256_file(target)

        if observed != expected:
            raise RuntimeError(
                f"Freeze checksum mismatch for {name}: "
                f"expected {expected}, observed {observed}"
            )

        verified += 1

    if verified != len(expected_target_set):
        raise RuntimeError(
            "Frozen integrity-bundle verified-target count "
            f"mismatch: expected {len(expected_target_set)}, "
            f"observed {verified}"
        )

    return {
        "bundle_checksum_file": str(manifest),
        "bundle_checksum_file_sha256": manifest_sha,
        "freeze_regular_file_count": len(regular_files),
        "checksum_target_count": len(actual_target_set),
        "verified_entries": verified,
        "complete_checksum_coverage": True,
    }


def normalized_tar_gz(
    output: Path,
    members: Iterable[tuple[Path, str]],
) -> dict:
    members = list(members)
    if output.exists():
        raise RuntimeError(f"Refusing to overwrite archive: {output}")

    with output.open("wb") as raw_out:
        with gzip.GzipFile(
            filename="",
            mode="wb",
            fileobj=raw_out,
            mtime=0,
            compresslevel=9,
        ) as gz:
            with tarfile.open(
                fileobj=gz,
                mode="w",
                format=tarfile.GNU_FORMAT,
            ) as tf:
                for source, arcname in sorted(members, key=lambda x: x[1]):
                    if source.is_symlink() or not source.is_file():
                        raise RuntimeError(f"Only regular files may be archived: {source}")

                    stat = source.stat()
                    info = tarfile.TarInfo(name=arcname)
                    info.size = stat.st_size
                    info.mtime = 0
                    info.uid = 0
                    info.gid = 0
                    info.uname = ""
                    info.gname = ""
                    info.mode = 0o644
                    info.type = tarfile.REGTYPE

                    with source.open("rb") as handle:
                        tf.addfile(info, handle)

    return {
        "path": output,
        "sha256": sha256_file(output),
        "bytes": output.stat().st_size,
        "archived_file_count": len(members),
    }


def tracked_publication_files(repo: Path) -> list[Path]:
    pathspecs = [
        "docs",
        "publication",
        "references",
        "results/README.md",
        "tracker/RESEARCH_TRACKER.md",
        "tracker/work_packages.csv",
        "README.md",
        "LICENSE",
        "CITATION.cff",
    ]
    proc = subprocess.run(
        ["git", "ls-files", "-z", "--", *pathspecs],
        cwd=repo,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.decode("utf-8", errors="replace"))

    names = [x for x in proc.stdout.split(b"\0") if x]
    files: list[Path] = []
    for raw in names:
        rel = raw.decode("utf-8")
        path = repo / rel
        if path.is_symlink() or not path.is_file():
            raise RuntimeError(f"Unexpected tracked publication path: {path}")
        files.append(path)
    return sorted(files, key=lambda p: p.relative_to(repo).as_posix())


def detect_freeze_dir(explicit: str | None) -> Path:
    if explicit:
        path = Path(explicit).expanduser().resolve()
        if not path.is_dir():
            raise RuntimeError(f"Freeze directory does not exist: {path}")
        return path

    candidates = sorted(
        p.resolve()
        for p in (Path.home() / "Downloads").glob("WP9_R069_INTEGRITY_FREEZE_20260829_*")
        if p.is_dir()
    )
    if len(candidates) != 1:
        raise RuntimeError(
            "Provide --freeze-dir because automatic discovery did not find exactly one "
            f"WP9_R069_INTEGRITY_FREEZE_20260829_* directory; found {len(candidates)}"
        )
    return candidates[0]


def path_is_within(
    path: Path,
    root: Path,
) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def validate_output_location(
    out: Path,
    repo: Path,
    campaign_root: Path,
    freeze_dir: Path,
) -> None:
    resolved_out = out.resolve()

    protected_roots = (
        ("campaign", campaign_root.resolve()),
        ("integrity-freeze", freeze_dir.resolve()),
        ("repository", repo.resolve()),
    )

    for label, root in protected_roots:
        if path_is_within(
            resolved_out,
            root,
        ):
            raise RuntimeError(
                "Release-candidate output must be outside "
                f"protected {label} tree: "
                f"output={resolved_out}, protected={root}"
            )


def write_json(path: Path, obj: object) -> None:
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=".")
    parser.add_argument("--freeze-dir")
    parser.add_argument("--out")
    args = parser.parse_args()

    repo = Path(args.repo).expanduser().resolve()
    repo = Path(run_git(repo, "rev-parse", "--show-toplevel")).resolve()

    if repo.name != EXPECTED_REPO_NAME:
        raise RuntimeError(f"Wrong repository: {repo}")

    branch = run_git(repo, "branch", "--show-current")
    head = run_git(repo, "rev-parse", "HEAD")
    status_before = run_git(repo, "status", "--porcelain")

    if branch != "main":
        raise RuntimeError(f"Release preparation requires local main; observed branch={branch!r}")
    if status_before:
        raise RuntimeError("Release preparation requires a clean tracked/untracked Git worktree")

    ancestor = subprocess.run(
        ["git", "merge-base", "--is-ancestor", MINIMUM_MANUSCRIPT_COMMIT, head],
        cwd=repo,
        check=False,
    ).returncode
    if ancestor != 0:
        raise RuntimeError(
            f"HEAD {head} does not contain minimum audited manuscript commit "
            f"{MINIMUM_MANUSCRIPT_COMMIT}"
        )

    campaign_root = repo / "results/wp9/campaign"
    ledger_path = campaign_root / "attempt-history.json"
    if not campaign_root.is_dir() or not ledger_path.is_file():
        raise RuntimeError(
            "Local raw campaign is required at results/wp9/campaign; it is intentionally "
            "not stored in GitHub"
        )

    freeze_dir = detect_freeze_dir(args.freeze_dir)

    out = (
        Path(args.out).expanduser().resolve()
        if args.out
        else (Path.home() / "Downloads" / f"WP11_RELEASE_CANDIDATE_{head[:7]}").resolve()
    )

    validate_output_location(
        out,
        repo,
        campaign_root,
        freeze_dir,
    )

    if out.exists():
        raise RuntimeError(f"Refusing to reuse existing release-candidate directory: {out}")
    out.mkdir(parents=True)

    print("============================================================")
    print("WP11 RELEASE CANDIDATE — READ-ONLY SOURCE VERIFICATION")
    print("============================================================")
    print(f"repository={repo}")
    print(f"repository_head={head}")
    print(f"freeze_dir={freeze_dir}")
    print(f"output_dir={out}")

    ledger = verify_ledger(ledger_path)
    tree_sha_before, campaign_file_count = campaign_tree_identity(repo, campaign_root)
    if tree_sha_before != EXPECTED_CAMPAIGN_TREE_SHA256:
        raise RuntimeError(
            f"campaign-tree SHA mismatch: expected {EXPECTED_CAMPAIGN_TREE_SHA256}, "
            f"observed {tree_sha_before}"
        )
    if campaign_file_count != EXPECTED_CAMPAIGN_FILE_COUNT:
        raise RuntimeError(
            f"campaign file-count mismatch: expected {EXPECTED_CAMPAIGN_FILE_COUNT}, "
            f"observed {campaign_file_count}"
        )

    freeze = verify_freeze_bundle(freeze_dir)

    print(f"ledger_sha256={ledger['sha256']}")
    print(f"ledger_records={ledger['records']}")
    print(f"valid_records={ledger['valid']}")
    print(f"invalid_records={ledger['invalid']}")
    print(f"campaign_file_count={campaign_file_count}")
    print(f"campaign_tree_sha256={tree_sha_before}")
    print(f"freeze_bundle_verified_entries={freeze['verified_entries']}")
    print("source_preflight=PASS")

    campaign_members = [
        (path, path.relative_to(repo).as_posix())
        for path in all_regular_files(campaign_root)
    ]
    freeze_members = [
        (path, f"wp9-integrity-freeze/{path.relative_to(freeze_dir).as_posix()}")
        for path in all_regular_files(freeze_dir)
    ]
    publication_files = tracked_publication_files(repo)
    publication_members = [
        (path, path.relative_to(repo).as_posix())
        for path in publication_files
    ]

    archives = []
    archives.append(
        normalized_tar_gz(
            out / "01-wp9-campaign-raw.tar.gz",
            campaign_members,
        )
    )
    archives.append(
        normalized_tar_gz(
            out / "02-wp9-integrity-freeze.tar.gz",
            freeze_members,
        )
    )
    archives.append(
        normalized_tar_gz(
            out / "03-publication-and-provenance.tar.gz",
            publication_members,
        )
    )

    source_identity = {
        "repository_head": head,
        "repository_branch": branch,
        "ledger_sha256": EXPECTED_LEDGER_SHA256,
        "campaign_tree_sha256": EXPECTED_CAMPAIGN_TREE_SHA256,
        "campaign_file_count": EXPECTED_CAMPAIGN_FILE_COUNT,
        "analysis_membership_sha256": EXPECTED_ANALYSIS_MEMBERSHIP_SHA256,
        "ledger_records": EXPECTED_LEDGER_RECORDS,
        "valid_records": EXPECTED_VALID,
        "invalid_records": EXPECTED_INVALID,
        "freeze_bundle_checksum_file_sha256": EXPECTED_FREEZE_BUNDLE_CHECKSUM_FILE_SHA256,
    }

    manifest = {
        "schema": "WP11_RELEASE_CANDIDATE_V1",
        "status": "LOCAL_RELEASE_CANDIDATE_NOT_UPLOADED_NOT_PUBLISHED",
        "source_identity": source_identity,
        "archives": [
            {
                "name": item["path"].name,
                "sha256": item["sha256"],
                "bytes": item["bytes"],
                "archived_file_count": item["archived_file_count"],
            }
            for item in archives
        ],
        "zenodo_constraints_checked": {
            "max_files_per_record": ZENODO_MAX_FILES,
            "default_max_total_bytes": ZENODO_DEFAULT_MAX_BYTES,
        },
        "claim_boundary": [
            "controlled NOS3/Fortytwo software-in-the-loop evidence only",
            "no operational spacecraft or ground-station access",
            "no RF transmission/interference claim",
            "no native spacecraft safe-mode claim",
            "C1 timing is synthetic/modelled only",
            "A16/A17 remain P6 before post-authorization rollback delegation",
            "raw expected values were never substituted for observed metrics",
        ],
    }

    manifest_path = out / "RELEASE_MANIFEST.json"
    write_json(manifest_path, manifest)

    readme_path = out / "README_RELEASE.txt"
    readme_path.write_text(
        "Mission-aware satellite cyber response and trusted recovery\n"
        "WP11 local release candidate\n\n"
        "This directory is a local packaging candidate only. It has not been uploaded "
        "or published and has no DOI yet.\n\n"
        "Archive 01 contains the complete frozen local WP9 campaign tree.\n"
        "Archive 02 contains the publication-grade WP9 integrity-freeze bundle.\n"
        "Archive 03 contains tracked publication/provenance/manuscript materials, not "
        "the full source/runtime implementation.\n\n"
        "Verify RELEASE_CHECKSUMS.sha256 and complete the separate WP11 release audit "
        "before any archive upload.\n",
        encoding="utf-8",
    )

    checksum_targets = [
        *(item["path"] for item in archives),
        manifest_path,
        readme_path,
    ]
    checksum_path = out / "RELEASE_CHECKSUMS.sha256"
    checksum_path.write_text(
        "".join(
            f"{sha256_file(path)}  {path.name}\n"
            for path in sorted(checksum_targets, key=lambda p: p.name)
        ),
        encoding="utf-8",
    )

    upload_objects = sorted(out.iterdir(), key=lambda p: p.name)
    total_bytes = sum(path.stat().st_size for path in upload_objects if path.is_file())
    upload_file_count = sum(path.is_file() for path in upload_objects)

    if upload_file_count > ZENODO_MAX_FILES:
        raise RuntimeError(
            f"release candidate has {upload_file_count} files; Zenodo default maximum is "
            f"{ZENODO_MAX_FILES}"
        )
    if total_bytes > ZENODO_DEFAULT_MAX_BYTES:
        raise RuntimeError(
            f"release candidate is {total_bytes} bytes; exceeds default Zenodo "
            f"{ZENODO_DEFAULT_MAX_BYTES}-byte quota"
        )

    # Re-verify raw source after packaging. This is the critical non-mutation proof.
    ledger_after = sha256_file(ledger_path)
    tree_sha_after, file_count_after = campaign_tree_identity(repo, campaign_root)
    freeze_after = verify_freeze_bundle(freeze_dir)

    git_identity_after = (
        verify_git_identity_unchanged(
            repo,
            branch,
            head,
            status_before,
        )
    )

    if ledger_after != EXPECTED_LEDGER_SHA256:
        raise RuntimeError("Ledger changed during packaging")
    if tree_sha_after != tree_sha_before or file_count_after != campaign_file_count:
        raise RuntimeError("Campaign source tree changed during packaging")
    if (
        freeze_after["bundle_checksum_file_sha256"]
        != freeze["bundle_checksum_file_sha256"]
        or freeze_after["checksum_target_count"]
        != freeze["checksum_target_count"]
        or freeze_after["verified_entries"]
        != freeze["verified_entries"]
    ):
        raise RuntimeError(
            "Integrity-freeze bundle changed during packaging"
        )

    print()
    print("============================================================")
    print("WP11 RELEASE CANDIDATE — DECISIVE STATUS")
    print("============================================================")
    for item in archives:
        print(f"archive={item['path'].name}")
        print(f"archive_sha256={item['sha256']}")
        print(f"archive_bytes={item['bytes']}")
        print(f"archive_source_files={item['archived_file_count']}")
    print(f"release_file_count={upload_file_count}")
    print(f"release_total_bytes={total_bytes}")
    print(f"release_checksums_sha256={sha256_file(checksum_path)}")
    print(f"campaign_tree_sha256_after={tree_sha_after}")
    print(f"ledger_sha256_after={ledger_after}")
    print("source_campaign_unchanged=true")
    print("freeze_bundle_unchanged=true")
    print(
        "repository_branch_after="
        + git_identity_after["branch"]
    )
    print(
        "repository_head_after="
        + git_identity_after["head"]
    )
    print("repository_branch_unchanged=true")
    print("repository_head_unchanged=true")
    print("git_worktree_unchanged=true")
    print("zenodo_default_file_count_gate=PASS")
    print("zenodo_default_size_gate=PASS")
    print("zenodo_upload_performed=false")
    print("zenodo_publication_performed=false")
    print("doi_assigned=false")
    print("wp11_local_release_candidate=PASS")

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # fail closed with one decisive error
        print(f"WP11_RELEASE_CANDIDATE_ERROR={exc}", file=sys.stderr)
        raise SystemExit(1)
