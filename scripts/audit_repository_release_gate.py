#!/usr/bin/env python3
"""Fail-closed repository sanity audit for the final journal-submission gate.

This audit is deliberately current-state aware. Historical work-package configs and
closeout documents may contain stage-local statuses such as AUTHORIZED_NOT_STARTED;
those records are provenance, not today's execution authorization. Current status is
governed by the active tracker/manuscript/submission files checked here.

The audit never starts NOS3/cFS, executes a campaign trial, consumes a campaign seed,
or mutates scientific evidence.
"""

from __future__ import annotations

import csv
import json
import re
import subprocess
import sys
import tomllib
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
ERRORS: list[str] = []
CHECKS: list[str] = []

VERSION_DOI = "10.5281/zenodo.22181540"
CONCEPT_DOI = "10.5281/zenodo.22181539"
MEMBERSHIP_SHA = "a2bf0c8f352f4386e74a500d97ea8f73e0c39d03bfe10ac0ebcf02470af9f70e"
LEDGER_SHA = "92893a2fd8746f410bffd4dca5101bc3f533ada2ff82f98681788cf0c24ce6fd"
CAMPAIGN_TREE_SHA = "ad1e127b4431b6b334955129fcba82f76b18e5b43585395ac8c37300cac087b1"
REPRO_COMMIT = "99892bd9bb0828bdb3d0a28caf40dbc18fcbc4dc"

PROVENANCE_COMMITS = (
    "aae2239753119c92e7633db3b6c73aee94c7b6dd",
    "97074d0cdc4261de02bc6f618e891a88f45f9cfc",
    "7ed85d5cbeca8f903b3468bc6ccc1c56e29c2446",
    "18596ea32c696b65bbdaf5676b1157d633ed59b5",
    REPRO_COMMIT,
)

ACTIVE_MARKDOWN = (
    "README.md",
    "publication/README.md",
    "scripts/README.md",
    "docs/REPRODUCIBILITY_GUIDE.md",
    "publication/manuscript/MANUSCRIPT-ASSEMBLY.md",
    "publication/submission/computers-and-security/README.md",
    "publication/submission/computers-and-security/submission-checklist.md",
    "publication/submission/computers-and-security/title-page.md",
    "publication/submission/computers-and-security/ai-declaration.md",
    "publication/submission/computers-and-security/cover-letter.md",
)

RECOMMENDED_SCRIPTS = (
    "verify_environment.sh",
    "validate_experiment_schema.py",
    "audit_repository_release_gate.py",
    "prepare_nos3_candidate.sh",
    "prepare_42_candidate.sh",
    "build_nominal_nos3.sh",
    "run_nominal_runtime_preflight.sh",
    "cleanup_nominal_runtime.sh",
    "verify_nos3_source_lock.sh",
    "verify_testbed_runtime.sh",
)


def ok(message: str) -> None:
    CHECKS.append(message)
    print(f"[OK] {message}")


def fail(message: str) -> None:
    ERRORS.append(message)
    print(f"[FAIL] {message}", file=sys.stderr)


def read(rel: str) -> str:
    path = ROOT / rel
    if not path.is_file():
        fail(f"required file missing: {rel}")
        return ""
    return path.read_text(encoding="utf-8")


def require_text(rel: str, required: tuple[str, ...] = (), forbidden: tuple[str, ...] = ()) -> None:
    text = read(rel)
    if not text:
        return
    for token in required:
        if token not in text:
            fail(f"{rel}: required current-state text missing: {token!r}")
    for token in forbidden:
        if token in text:
            fail(f"{rel}: stale/current-state text still present: {token!r}")
    ok(f"current-state wording checked: {rel}")


def validate_json() -> None:
    files = sorted(p for p in ROOT.rglob("*.json") if ".git" not in p.parts)
    for path in files:
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001 - audit must report any parser failure
            fail(f"invalid JSON syntax: {path.relative_to(ROOT)}: {exc}")
    if not ERRORS:
        ok(f"JSON syntax parsed for {len(files)} tracked files")


def validate_toml() -> None:
    files = sorted(p for p in ROOT.rglob("*.toml") if ".git" not in p.parts)
    for path in files:
        try:
            tomllib.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001
            fail(f"invalid TOML syntax: {path.relative_to(ROOT)}: {exc}")
    ok(f"TOML syntax parsed for {len(files)} tracked files")


def validate_csv() -> None:
    files = sorted(p for p in ROOT.rglob("*.csv") if ".git" not in p.parts)
    for path in files:
        try:
            with path.open("r", encoding="utf-8-sig", newline="") as handle:
                rows = list(csv.reader(handle))
        except Exception as exc:  # noqa: BLE001
            fail(f"CSV parse failure: {path.relative_to(ROOT)}: {exc}")
            continue
        if not rows:
            fail(f"empty CSV: {path.relative_to(ROOT)}")
            continue
        width = len(rows[0])
        if width == 0:
            fail(f"CSV has empty header: {path.relative_to(ROOT)}")
            continue
        for idx, row in enumerate(rows[1:], start=2):
            if len(row) != width:
                fail(
                    f"ragged CSV: {path.relative_to(ROOT)} line {idx}: "
                    f"expected {width} fields, found {len(row)}"
                )
    ok(f"CSV structure checked for {len(files)} tracked files")


def validate_markdown_links() -> None:
    pattern = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
    checked = 0
    for rel in ACTIVE_MARKDOWN:
        text = read(rel)
        if not text:
            continue
        base = (ROOT / rel).parent
        for raw_target in pattern.findall(text):
            target = raw_target.strip()
            if not target or target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            if target.startswith("<") and target.endswith(">"):
                target = target[1:-1]
            # Markdown titles are not used in the active files; trim a simple quoted title if present.
            target = re.sub(r'\s+["\'].*["\']$', "", target)
            target = unquote(target.split("#", 1)[0])
            if not target:
                continue
            candidate = (base / target).resolve()
            try:
                candidate.relative_to(ROOT.resolve())
            except ValueError:
                fail(f"markdown link escapes repository: {rel}: {raw_target}")
                continue
            checked += 1
            if not candidate.exists():
                fail(f"broken local markdown link: {rel}: {raw_target}")
    ok(f"active-document local links checked: {checked}")


def validate_script_guide() -> None:
    for name in RECOMMENDED_SCRIPTS:
        if not (ROOT / "scripts" / name).is_file():
            fail(f"scripts/README.md recommended entry point missing: scripts/{name}")
    ok(f"recommended script entry points exist: {len(RECOMMENDED_SCRIPTS)}")


def validate_submission_inputs() -> None:
    path = ROOT / "publication/manuscript/submission-inputs.csv"
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = {row["input_id"]: row for row in csv.DictReader(handle)}
    expected = {
        "S05": "RESOLVED",
        "S06": "RESOLVED",
        "S09": "AUTHOR_APPROVED_POLICY_RECHECK_REQUIRED",
        "S13": "RESOLVED",
        "S14": "RESOLVED",
    }
    for key, status in expected.items():
        actual = rows.get(key, {}).get("status")
        if actual != status:
            fail(f"submission-inputs.csv {key}: expected {status}, found {actual}")
    s12 = rows.get("S12", {})
    if s12.get("status") != "USER_OR_INSTITUTION_INPUT_IF_REQUIRED":
        fail("S12 IRB/HRPP field must remain conditional; do not invent a determination identifier")
    ok("author attestations and conditional IRB/HRPP state checked")


def validate_frozen_identities() -> None:
    declarations = read("publication/manuscript/07-declarations-and-availability.md")
    tracker = read("tracker/RESEARCH_TRACKER.md")
    for token, label in (
        (VERSION_DOI, "Zenodo version DOI"),
        (CONCEPT_DOI, "Zenodo concept DOI"),
        (MEMBERSHIP_SHA, "720-membership SHA-256"),
        (LEDGER_SHA, "attempt-history ledger SHA-256"),
        (CAMPAIGN_TREE_SHA, "campaign-tree SHA-256"),
    ):
        if token not in declarations:
            fail(f"declarations missing {label}: {token}")
        if token not in tracker:
            fail(f"research tracker missing {label}: {token}")
    if REPRO_COMMIT not in declarations:
        fail("Code Availability no longer points to the intentionally frozen reproducibility-hardened snapshot")
    ok("frozen DOI/hash/code-snapshot identities cross-checked")


def validate_git_provenance() -> None:
    for sha in PROVENANCE_COMMITS:
        result = subprocess.run(
            ["git", "cat-file", "-e", f"{sha}^{{commit}}"],
            cwd=ROOT,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
        if result.returncode != 0:
            fail(f"historical provenance commit not resolvable from full checkout: {sha}")
    ok(f"historical provenance commits resolve: {len(PROVENANCE_COMMITS)}")


def validate_no_unresolved_markers() -> None:
    # Source-level TODO/FIXME/XXX/HACK markers are not allowed in the submission baseline.
    files = [
        p
        for p in ROOT.rglob("*")
        if p.is_file()
        and ".git" not in p.parts
        and p.suffix.lower() in {".py", ".sh"}
    ]
    marker = re.compile(r"\b(TODO|FIXME|XXX|HACK)\b", re.IGNORECASE)
    for path in files:
        for lineno, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), start=1):
            if marker.search(line):
                fail(f"unresolved source marker {path.relative_to(ROOT)}:{lineno}: {line.strip()}")
    ok(f"source comment markers checked across {len(files)} Python/shell files")


def validate_current_state() -> None:
    require_text(
        "README.md",
        required=("final submission-export gate",),
        forbidden=("journal-specific submission preparation is next",),
    )
    require_text(
        "publication/README.md",
        required=("author-attestation gate is complete", "final submission-export gate"),
        forbidden=("author declarations, conflict-of-interest language",),
    )
    require_text(
        "publication/manuscript/MANUSCRIPT-ASSEMBLY.md",
        required=("Author-attestation gate: PASS", "final submission-export gate"),
        forbidden=("The following items require factual author attestation",),
    )
    require_text(
        "tracker/RESEARCH_TRACKER.md",
        required=("Last updated: 2026-08-31", "final submission-export gate"),
        forbidden=("finalize author/declaration metadata",),
    )
    require_text(
        "tracker/work_packages.csv",
        required=("author attestations closed", "final submission export"),
        forbidden=("remaining work is journal-specific formatting/declarations/submission metadata",),
    )
    require_text(
        "publication/submission/computers-and-security/submission-checklist.md",
        required=("Author-attestation gate: PASS", "final submission-export gate"),
    )
    require_text(
        "release/UPLOAD_CHECKLIST.md",
        required=("historical procedural checklist", "Zenodo v1.0.0"),
    )
    require_text(
        "data/README.md",
        required=("screening/rights register", "not part of the frozen 720-observation statistical population"),
    )


def main() -> int:
    print("=== FINAL SUBMISSION REPOSITORY RELEASE-GATE AUDIT ===")
    validate_json()
    validate_toml()
    validate_csv()
    validate_markdown_links()
    validate_script_guide()
    validate_submission_inputs()
    validate_frozen_identities()
    validate_git_provenance()
    validate_no_unresolved_markers()
    validate_current_state()

    print(f"checks_completed={len(CHECKS)}")
    print(f"errors={len(ERRORS)}")
    if ERRORS:
        print("repository_release_gate=FAIL", file=sys.stderr)
        return 1
    print("repository_release_gate=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
