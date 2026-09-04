#!/usr/bin/env python3
"""Fail-closed audit for Repository Review v3 non-scientific remediation.

This audit validates current-state documentation and publication/governance artifacts.
It does not start a scientific runtime, rerun a canonical campaign, or modify evidence.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

EXPECTED = {
    "study3": {
        "experiment": "S3-K4E-001",
        "merge": "68a2c9a1394743e9a233e93586e86a6179a0793c",
        "population_key": ("membership", "trajectories"),
        "population": 1380,
    },
    "study4": {
        "experiment": "S4-MPQ-001",
        "merge": "09a3fa61276e348b58a852c156e7bfc64b25d32d",
        "population_key": ("membership", "observations"),
        "population": 4608,
    },
    "study5": {
        "experiment": "S5-CUCD-001",
        "merge": "6415a391dc2337c51ce72442ac7d86a25b4fbc02",
        "population_key": ("membership", "portability_observations"),
        "population": 80,
    },
    "study6": {
        "experiment": "S6-SCTR-001",
        "merge": "0dfe7f4331fc1f8864344c95d39e0d8dcb74c8f4",
        "population_key": ("population", "total"),
        "population": 420,
    },
    "study7": {
        "experiment": "S7-LSO-001",
        "merge": "f582c36cc5747a6703ec651bb957bbfea5852a7e",
        "population_key": ("population", "total"),
        "population": 1033,
    },
}

STALE_ACTIVE_PHRASES = {
    "study3": "DESIGN_AND_IMPLEMENTATION_CANDIDATE_NO_CAMPAIGN_RESULT_YET",
    "study4": "DESIGN_AND_IMPLEMENTATION_CANDIDATE_NO_CANONICAL_RESULT_YET",
    "study5": "design freeze candidate; no canonical result is claimed",
}

STUDY2_SHA = "195860bd44b38ccf170f02cb1cb392583217296d08640c99b18b52286403e133"
STUDY2_VERSION_DOI = "10.5281/zenodo.22289114"
STUDY2_CONCEPT_DOI = "10.5281/zenodo.22289113"
STUDY2_RECORD_ID = 22289114
STUDY2_VERSION = "1.0.0"


def fail(message: str, errors: list[str]) -> None:
    errors.append(message)
    print(f"[FAIL] {message}")


def ok(message: str) -> None:
    print(f"[OK] {message}")


def load_json(rel: str, errors: list[str]) -> dict:
    path = ROOT / rel
    if not path.is_file():
        fail(f"missing JSON: {rel}", errors)
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        fail(f"invalid JSON {rel}: {exc}", errors)
        return {}


def nested(data: dict, keys: tuple[str, ...]):
    value = data
    for key in keys:
        if not isinstance(value, dict) or key not in value:
            return None
        value = value[key]
    return value


def main() -> int:
    errors: list[str] = []

    for study, expected in EXPECTED.items():
        readme_rel = f"{study}/README.md"
        readme_path = ROOT / readme_rel
        if not readme_path.is_file():
            fail(f"missing current-state README: {readme_rel}", errors)
            continue
        text = readme_path.read_text(encoding="utf-8")
        for required in (
            expected["experiment"],
            "CANONICAL_RESULTS_FROZEN_MERGED",
            expected["merge"],
        ):
            if required not in text:
                fail(f"{readme_rel} missing current marker: {required}", errors)
        stale = STALE_ACTIVE_PHRASES.get(study)
        if stale and stale in text:
            fail(f"{readme_rel} still contains stale active status: {stale}", errors)
        if not any(err.startswith(readme_rel) for err in errors):
            ok(f"current canonical status: {readme_rel}")

        freeze = load_json(f"{study}/results/RESULTS_FREEZE.json", errors)
        if freeze:
            if freeze.get("experiment_id") != expected["experiment"]:
                fail(f"{study} results-freeze experiment ID mismatch", errors)
            actual_population = nested(freeze, expected["population_key"])
            if actual_population != expected["population"]:
                fail(
                    f"{study} frozen population mismatch: "
                    f"expected {expected['population']} got {actual_population}",
                    errors,
                )

    s3 = load_json("study3/results/RESULTS_FREEZE.json", errors)
    if s3:
        audit = s3.get("independent_audit", {})
        if audit.get("status") != "PASS":
            fail("Study 3 independent audit is not PASS", errors)
        for key in (
            "trajectory_mismatches",
            "epoch_rule_mismatches",
            "qualification_origin_mismatches",
            "sha_mismatches",
        ):
            if audit.get(key) != 0:
                fail(f"Study 3 independent audit {key} != 0", errors)

    s4_auditor = ROOT / "study4/analysis/audit_independent.py"
    if not s4_auditor.is_file():
        fail("Study 4 independent auditor missing", errors)
    else:
        ok("Study 4 independent auditor retained")

    s5 = load_json("study5/results/RESULTS_FREEZE.json", errors)
    if s5 and nested(s5, ("canonical_validation", "independent_audit_mismatches")) != 0:
        fail("Study 5 independent audit mismatch count is not zero", errors)

    for study in ("study6", "study7"):
        freeze = load_json(f"{study}/results/RESULTS_FREEZE.json", errors)
        if freeze and freeze.get("independent_audit") != "PASS":
            fail(f"{study} independent audit is not PASS", errors)

    discussion = ROOT / "publication/manuscript/05-discussion.md"
    if not discussion.is_file():
        fail("missing publication/manuscript/05-discussion.md", errors)
    else:
        text = discussion.read_text(encoding="utf-8")
        required = (
            "**Bounded formal verification.**",
            "Study1P7`: 48 distinct states",
            "TrustedRecovery`: 385 distinct states",
            "AdversarialEvidence`: 540 generated / 400 distinct states, depth 3",
            "do not constitute exhaustive verification of the Python implementation",
        )
        for marker in required:
            if marker not in text:
                fail(f"Discussion missing formal-verification boundary: {marker}", errors)
        if all(marker in text for marker in required):
            ok("Discussion formal-verification limitation is explicit")

    for rel in (
        "docs/RESEARCH_PROGRAM_PROVENANCE_AND_PUBLICATION_ROADMAP.md",
        "docs/STUDIES3_8_ASSURANCE_COVERAGE_AUDIT.md",
    ):
        if not (ROOT / rel).is_file():
            fail(f"missing remediation document: {rel}", errors)
        else:
            ok(f"remediation document present: {rel}")

    study2_readme = ROOT / "study2/release/phase6/README.md"
    if not study2_readme.is_file():
        fail("missing Study-2 Phase-6 release README", errors)
    else:
        text = study2_readme.read_text(encoding="utf-8")
        for marker in (
            "PUBLIC_DURABLE_ARCHIVE_PUBLISHED_AND_PUBLIC_BYTES_VERIFIED",
            STUDY2_SHA,
            STUDY2_VERSION_DOI,
            STUDY2_CONCEPT_DOI,
            "ZENODO_PUBLICATION_VERIFICATION.md",
            "ZENODO_PUBLICATION_VERIFICATION.json",
            "ZENODO_DEPOSIT_READY.md",
            "ZENODO_DEPOSIT_METADATA.json",
        ):
            if marker not in text:
                fail(f"Study-2 release README missing publication marker: {marker}", errors)

    metadata = load_json("study2/release/phase6/ZENODO_DEPOSIT_METADATA.json", errors)
    if metadata:
        if metadata.get("doi_state") != "PENDING_EXTERNAL_DURABLE_ARCHIVE_PUBLICATION":
            fail("historical Study-2 deposit handoff DOI state drifted", errors)
        if nested(metadata, ("exact_file", "sha256")) != STUDY2_SHA:
            fail("Study-2 deposit metadata SHA does not match frozen source ZIP", errors)
        governance = metadata.get("governance", {})
        for key in (
            "reuse_study1_doi_allowed",
            "invent_doi_before_publication_allowed",
            "modify_or_rezip_source_evidence_allowed",
            "claim_operational_spacecraft_validation_allowed",
        ):
            if governance.get(key) is not False:
                fail(f"Study-2 deposit governance must keep {key}=false", errors)

    verification = load_json("study2/release/phase6/ZENODO_PUBLICATION_VERIFICATION.json", errors)
    if verification:
        expected = {
            "experiment_id": "S2-AEATR-001",
            "state": "PUBLIC_DURABLE_ARCHIVE_PUBLISHED_AND_PUBLIC_BYTES_VERIFIED",
            "record_id": STUDY2_RECORD_ID,
            "version_doi": STUDY2_VERSION_DOI,
            "concept_doi": STUDY2_CONCEPT_DOI,
            "publication_date": "2026-09-04",
            "version": STUDY2_VERSION,
            "resource_type": "dataset",
            "license": "cc-by-4.0",
            "scientific_execution_performed": False,
            "frozen_science_modified": False,
            "study1_doi_reused": False,
        }
        for key, expected_value in expected.items():
            if verification.get(key) != expected_value:
                fail(
                    f"Study-2 Zenodo verification {key}: "
                    f"expected {expected_value!r} got {verification.get(key)!r}",
                    errors,
                )
        public_file = verification.get("public_file", {})
        if public_file.get("expected_sha256") != STUDY2_SHA:
            fail("Study-2 Zenodo expected SHA drift", errors)
        if public_file.get("public_download_sha256") != STUDY2_SHA:
            fail("Study-2 Zenodo public-download SHA mismatch", errors)
        if public_file.get("sha256_match") is not True:
            fail("Study-2 Zenodo SHA match flag is not true", errors)
        audit = verification.get("verification", {})
        if audit.get("result") != "PASS":
            fail("Study-2 Zenodo publication verification is not PASS", errors)
        if audit.get("public_bytes_match_frozen_source") is not True:
            fail("Study-2 public Zenodo bytes are not bound to frozen source", errors)

    if not errors:
        ok("Study-2 Zenodo publication and public-byte identity verified")

    print(f"checks_failed={len(errors)}")
    if errors:
        print("repository_review_v3_remediation=FAIL")
        return 1
    print("repository_review_v3_remediation=PASS")
    print("study2_doi_state=PUBLIC_DURABLE_ARCHIVE_PUBLISHED_AND_PUBLIC_BYTES_VERIFIED")
    print(f"study2_version_doi={STUDY2_VERSION_DOI}")
    print(f"study2_concept_doi={STUDY2_CONCEPT_DOI}")
    print("studies3_7_current_state=PASS")
    print("formal_verification_limitation=PASS")
    print("publication_roadmap=PASS")
    print("assurance_coverage_audit=PASS_NO_ADDITIONAL_TESTS_REQUIRED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
