#!/usr/bin/env python3
"""Current repository release gate after four submitted publication lines.

This gate preserves the legacy structural/frozen-study checks that remain authoritative,
while validating live publication state against the current 2026-09-13 authority
hierarchy. Historical audit scripts remain unchanged as provenance.

The checker never starts scientific runtime, reruns a frozen campaign, modifies evidence,
or changes publisher-facing artifacts.
"""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import yaml

import audit_repository_release_gate_core as legacy

ROOT = Path(__file__).resolve().parents[1]

S1_VERSION_DOI = "10.5281/zenodo.22181540"
S1_CONCEPT_DOI = "10.5281/zenodo.22181539"
S1_MEMBERSHIP_SHA = "a2bf0c8f352f4386e74a500d97ea8f73e0c39d03bfe10ac0ebcf02470af9f70e"
S1_LEDGER_SHA = "92893a2fd8746f410bffd4dca5101bc3f533ada2ff82f98681788cf0c24ce6fd"
S1_CAMPAIGN_TREE_SHA = "ad1e127b4431b6b334955129fcba82f76b18e5b43585395ac8c37300cac087b1"
S1_REPRO_COMMIT = "99892bd9bb0828bdb3d0a28caf40dbc18fcbc4dc"

S2_EXPERIMENT_ID = "S2-AEATR-001"
S2_STATUS = "PRESPECIFIED_ANALYSIS_RESULTS_FROZEN_CANONICAL"
S2_PHASE6_ZIP_SHA = "195860bd44b38ccf170f02cb1cb392583217296d08640c99b18b52286403e133"
S2_OBSERVATIONS_SHA = "8dcc850c561d7e3c0bf7478263b534cae83cbbb55183c313e879dd7d61127854"
S2_TRIAL_MANIFEST_SHA = "190612473717b7768ceccb4596a20d90cd7d532bf7581330ce94d609cb752e67"
S2_RESULT_ZIP_SHA = "0136123a53d150437fefc8ace342af63b11d980cf8cab32ef7a4f03b78267417"
S2_ANALYZER_SHA = "351039f0d6d79eb605c7dc027a5427da862b0f544815f862a85bc997df56c8bd"
S2_AUDITOR_SHA = "3e738e2c27d621073a8c1bba49044df3fc83d099abdd244894537f4c4b22142d"
S2_RESULTS_MERGE = "49c62cbed3fb8fc318e44d696faba1854ed6c21a"
S2_VERSION_DOI = "10.5281/zenodo.22289114"
S2_CONCEPT_DOI = "10.5281/zenodo.22289113"
S2_RESULT_ARCHIVE = (
    "study2/evidence/phase7/archive/"
    "study2-phase7-results-60f64327c45efda24cbb5b342f9d0eac908e1934.zip"
)

S8_EXPERIMENT_ID = "S8-PQC-ICR-001"
S8_STATUS = "TECHNICALLY_CLOSED_PUBLICATION_INTEGRATION_NOT_STARTED"
S8_ROWS = 3456
S8_CANONICAL_SHA = "cfc65b6663be4e9f17a00ed102730f8642efcbbd844045acce032ff09a0bcabf"
S8_FINDINGS_SHA = "26a8ac4d1039917323e75a294775dd14a2b563adb12a5d2fcdb47ce8f15c992e"
S8_INTERPRETATION_SHA = "620827f83fb566ff6ceae1b66c8f51f61ef8e5bbdabbb1c4b5a48b5187a82413"
S8_SCIENCE_MERGE = "63106778559c3127a7d6e8765d52939b73a3f35b"
S8_POST_MERGE_CI = 33761681328

PAPER1_ID = "2026-09-I012066"
PAPER2_ID = "cd1dfa89-4a24-4451-bdd4-af31ce3367f4"
PAPER3_ID = "6db04a31-8223-4aaf-af02-e4bafe06ef89"
PAPER4_ID = "AA-D-26-02872"

ERRORS: list[str] = []
CHECKS: list[str] = []


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


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def require_text(rel: str, required: tuple[str, ...], forbidden: tuple[str, ...] = ()) -> None:
    text = read(rel)
    if not text:
        return
    before = len(ERRORS)
    for token in required:
        if token not in text:
            fail(f"{rel}: required current-state text missing: {token!r}")
    for token in forbidden:
        if token in text:
            fail(f"{rel}: stale current-state text still present: {token!r}")
    if len(ERRORS) == before:
        ok(f"current-state wording checked: {rel}")


def validate_legacy_structural_checks() -> None:
    legacy.ERRORS.clear()
    legacy.CHECKS.clear()
    checks = (
        legacy.validate_json,
        legacy.validate_yaml,
        legacy.validate_toml,
        legacy.validate_csv,
        legacy.validate_xml_svg,
        legacy.validate_markdown_links,
        legacy.validate_script_guide,
        legacy.validate_publication_displays,
        legacy.validate_bibliography_and_citations,
        legacy.validate_submission_inputs,
        legacy.validate_git_provenance,
        legacy.validate_no_unresolved_markers,
    )
    for check in checks:
        check()
    if legacy.ERRORS:
        for message in legacy.ERRORS:
            fail(f"legacy structural check: {message}")
    else:
        ok(f"legacy structural/provenance checks preserved: {len(legacy.CHECKS)} checks")


def validate_study1_frozen_identity() -> None:
    declarations = read("publication/manuscript/07-declarations-and-availability.md")
    before = len(ERRORS)
    for token, label in (
        (S1_VERSION_DOI, "Study-1 Zenodo version DOI"),
        (S1_CONCEPT_DOI, "Study-1 Zenodo concept DOI"),
        (S1_MEMBERSHIP_SHA, "Study-1 720-membership SHA-256"),
        (S1_LEDGER_SHA, "Study-1 attempt-history ledger SHA-256"),
        (S1_CAMPAIGN_TREE_SHA, "Study-1 campaign-tree SHA-256"),
        (S1_REPRO_COMMIT, "Study-1 frozen reproduction snapshot"),
    ):
        if token not in declarations:
            fail(f"declarations missing {label}: {token}")

    citation = yaml.safe_load(read("CITATION.cff"))
    preferred = citation.get("preferred-citation", {}) if isinstance(citation, dict) else {}
    if preferred.get("doi") != S1_VERSION_DOI:
        fail(f"CITATION.cff Study-1 preferred DOI drift: {preferred.get('doi')!r}")
    if preferred.get("version") != "1.0.0":
        fail(f"CITATION.cff preferred version drift: {preferred.get('version')!r}")
    if len(ERRORS) == before:
        ok("Study-1 frozen identities cross-checked at authoritative records")


def validate_study2_frozen_identity() -> None:
    before = len(ERRORS)
    freeze = json.loads(read("study2/PHASE7_RESULTS_FREEZE.json"))
    provenance = json.loads(read("study2/PHASE7_PROVENANCE.json"))
    verification = json.loads(read("study2/release/phase6/ZENODO_PUBLICATION_VERIFICATION.json"))
    declarations = read("publication/manuscript/07-declarations-and-availability.md")

    expected_freeze = {
        "experiment_id": S2_EXPERIMENT_ID,
        "status": S2_STATUS,
        "canonical_merge_commit": S2_RESULTS_MERGE,
        "analysis_entrypoint_sha256": S2_ANALYZER_SHA,
        "phase6_artifact_zip_sha256": S2_PHASE6_ZIP_SHA,
        "phase7_result_artifact_zip_sha256": S2_RESULT_ZIP_SHA,
        "durable_result_archive_sha256": S2_RESULT_ZIP_SHA,
        "valid_observations_analyzed": 3872,
        "invalid_attempts": 0,
        "cells_analyzed": 85,
        "primary_contrast_rows": 162,
        "secondary_contrast_rows": 432,
        "independent_recalculation_mismatches": 0,
        "independent_auditor_sha256": S2_AUDITOR_SHA,
        "new_campaign_execution": False,
        "study1_reanalysis": False,
        "weighted_global_policy_score_computed": False,
        "global_policy_rank_computed": False,
    }
    for key, expected in expected_freeze.items():
        if freeze.get(key) != expected:
            fail(f"Study-2 freeze {key}: expected {expected!r}, found {freeze.get(key)!r}")

    source = provenance.get("source_phase6", {})
    for key, expected in (
        ("artifact_zip_sha256", S2_PHASE6_ZIP_SHA),
        ("observations_sha256", S2_OBSERVATIONS_SHA),
        ("trial_manifest_sha256", S2_TRIAL_MANIFEST_SHA),
        ("valid_observations", 3872),
        ("invalid_attempts", 0),
        ("cell_count", 85),
    ):
        if source.get(key) != expected:
            fail(f"Study-2 provenance source_phase6 {key} drift")

    archive = ROOT / S2_RESULT_ARCHIVE
    if not archive.is_file():
        fail(f"Study-2 durable result ZIP missing: {S2_RESULT_ARCHIVE}")
    elif sha256_file(archive) != S2_RESULT_ZIP_SHA:
        fail("Study-2 durable result ZIP SHA-256 mismatch")

    if verification.get("version_doi") != S2_VERSION_DOI:
        fail("Study-2 public verification version DOI drift")
    if verification.get("concept_doi") != S2_CONCEPT_DOI:
        fail("Study-2 public verification concept DOI drift")
    if verification.get("state") != "PUBLIC_DURABLE_ARCHIVE_PUBLISHED_AND_PUBLIC_BYTES_VERIFIED":
        fail("Study-2 public verification state drift")
    public_file = verification.get("public_file", {})
    if public_file.get("expected_sha256") != S2_PHASE6_ZIP_SHA:
        fail("Study-2 public expected SHA drift")
    if public_file.get("public_download_sha256") != S2_PHASE6_ZIP_SHA:
        fail("Study-2 public download SHA drift")
    if public_file.get("sha256_match") is not True:
        fail("Study-2 public SHA-match flag is not true")

    for token in (
        S2_PHASE6_ZIP_SHA,
        S2_OBSERVATIONS_SHA,
        S2_TRIAL_MANIFEST_SHA,
        S2_RESULT_ZIP_SHA,
        S2_VERSION_DOI,
        S2_CONCEPT_DOI,
    ):
        if token not in declarations:
            fail(f"Study-2 declaration identity missing: {token}")

    if len(ERRORS) == before:
        ok("Study-2 frozen/provenance/public identities cross-checked")


def validate_study8_frozen_identity() -> None:
    before = len(ERRORS)
    close = json.loads(read("study8/STUDY8_TECHNICAL_CLOSE.json"))
    if close.get("study_id") != S8_EXPERIMENT_ID:
        fail("Study-8 technical-close experiment ID drift")
    if close.get("status") != S8_STATUS:
        fail(f"Study-8 technical-close status drift: {close.get('status')!r}")

    science_merge = close.get("science_merge", {})
    if science_merge.get("main_commit") != S8_SCIENCE_MERGE:
        fail("Study-8 science merge commit drift")
    post_ci = science_merge.get("post_merge_ci", {})
    if post_ci.get("run_id") != S8_POST_MERGE_CI or post_ci.get("conclusion") != "success":
        fail("Study-8 post-merge CI identity/conclusion drift")

    population = close.get("canonical_population", {})
    for key in ("expected_rows", "primary_rows", "independent_rows", "exact_row_matches"):
        if population.get(key) != S8_ROWS:
            fail(f"Study-8 {key} drift: {population.get(key)!r}")
    if population.get("mismatch_count") != 0:
        fail("Study-8 row mismatch count is not zero")

    frozen = close.get("frozen_sha256", {})
    for key, expected in (
        ("canonical_observations_csv", S8_CANONICAL_SHA),
        ("primary_findings_json", S8_FINDINGS_SHA),
        ("independent_findings_json", S8_FINDINGS_SHA),
        ("interpretation_audit_json", S8_INTERPRETATION_SHA),
    ):
        if frozen.get(key) != expected:
            fail(f"Study-8 frozen SHA drift: {key}")

    result = subprocess.run(
        [sys.executable, "study8/scripts/check_study8_technical_close.py"],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
    )
    if result.returncode != 0 or "study8_technical_close=PASS" not in result.stdout:
        fail("Study-8 technical-close checker failed or omitted PASS")

    if len(ERRORS) == before:
        ok("Study-8 frozen technical-close identities cross-checked")


def validate_current_publication_state() -> None:
    common_ids = (PAPER1_ID, PAPER2_ID, PAPER3_ID, PAPER4_ID)
    require_text(
        "docs/CURRENT_PUBLICATION_STATE.md",
        required=(
            "four submitted publication lines",
            *common_ids,
            "SUBMITTED__TECHNICAL_CHECK",
            "read-only candidate audit",
            "No next venue or manuscript package is currently locked",
        ),
        forbidden=(
            "This is the next active publication-development priority.",
            "The next gate is venue-specific submission-package preparation",
        ),
    )
    require_text(
        "README.md",
        required=(
            "four submitted publication lines",
            *common_ids,
            "read-only audit of remaining eligible work",
            "No next venue or manuscript is currently locked",
        ),
        forbidden=(
            "two separately frozen empirical studies",
            "Study-8 companion paper",
        ),
    )
    require_text(
        "publication/README.md",
        required=(
            PAPER1_ID,
            PAPER2_ID,
            PAPER3_ID,
            PAPER4_ID,
        ),
    )
    require_text(
        "docs/PUBLICATION_PHASE_MAP.md",
        required=(PAPER1_ID, PAPER2_ID, PAPER3_ID, PAPER4_ID),
    )

    csv_path = ROOT / "tracker/PUBLICATION_STATE.csv"
    if not csv_path.is_file():
        fail("tracker/PUBLICATION_STATE.csv missing")
    else:
        text = csv_path.read_text(encoding="utf-8-sig")
        before = len(ERRORS)
        for token in common_ids:
            if token not in text:
                fail(f"tracker/PUBLICATION_STATE.csv missing submitted identity: {token}")
        if len(ERRORS) == before:
            ok("machine-readable publication tracker contains all submitted identities")


def main() -> int:
    print("=== REPOSITORY RELEASE GATE V4 / CURRENT FOUR-SUBMISSION STATE ===")
    validate_legacy_structural_checks()
    validate_study1_frozen_identity()
    validate_study2_frozen_identity()
    validate_study8_frozen_identity()
    validate_current_publication_state()

    print(f"checks_completed={len(CHECKS)}")
    print(f"errors={len(ERRORS)}")
    if ERRORS:
        print("repository_release_gate_v4=FAIL", file=sys.stderr)
        return 1
    print("repository_release_gate_v4=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
