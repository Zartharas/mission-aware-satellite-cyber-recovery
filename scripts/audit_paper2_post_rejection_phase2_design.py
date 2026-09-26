#!/usr/bin/env python3
"""Fail-closed audit for Paper-2 post-rejection Phase-2 design state.

This checker validates design-only state for S3X and S6X. It does not download
external data, build cFS, mutate source, or execute a scientific campaign.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REBUILD = ROOT / "publication/Paper_2_Studies_3_4_6/Post_Rejection_Rebuild"


def fail(message: str) -> None:
    print(f"[FAIL] {message}", file=sys.stderr)
    raise SystemExit(1)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def load_json(path: Path) -> dict:
    if not path.is_file():
        fail(f"missing JSON: {path.relative_to(ROOT)}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        fail(f"invalid JSON {path.relative_to(ROOT)}: {exc}")


def check_phase2_status() -> None:
    status = load_json(REBUILD / "PAPER2_PHASE2_DESIGN_STATUS.json")
    require(status.get("phase") == "POST_REJECTION_REBUILD_PHASE2_DESIGN", "Phase-2 phase drift")
    require(
        status.get("status") == "AUTHORIZED_SOURCE_METADATA_AND_INVARIANT_FIXTURE_DESIGN_COMPLETE__NO_EXECUTION",
        "Phase-2 status drift",
    )
    require(status.get("branch_base_commit") == "db744891dc9a726ad51b25543c5f3ee90c0ce4e7", "Phase-2 base drift")

    prior = status.get("prior_merge", {})
    require(prior.get("pull_request") == 172, "prior PR identity drift")
    require(prior.get("merge_commit") == "db744891dc9a726ad51b25543c5f3ee90c0ce4e7", "prior merge commit drift")
    ci = prior.get("post_merge_ci", {})
    require(ci.get("run_id") == 36267400739, "post-merge CI run identity drift")
    require(ci.get("conclusion") == "success", "post-merge CI conclusion drift")

    s3x = status.get("s3x", {})
    require(s3x.get("source_freeze_authorized") is False, "S3X source freeze unexpectedly authorized")
    require(s3x.get("trace_extraction_authorized") is False, "S3X trace extraction unexpectedly authorized")
    require(s3x.get("recovery_policy_execution_authorized") is False, "S3X recovery execution unexpectedly authorized")

    s4x = status.get("s4x", {})
    require(s4x.get("state") == "HOLD__NOT_CURRENTLY_JUSTIFIED__EXECUTION_NOT_AUTHORIZED", "S4X hold drift")

    s6x = status.get("s6x", {})
    for key in ("implementation_authorized", "build_authorized", "artifact_mutation_authorized", "scientific_execution_authorized"):
        require(s6x.get(key) is False, f"S6X gate unexpectedly open: {key}")

    manuscript = status.get("manuscript", {})
    for key in ("rewrite_authorized", "venue_lock_authorized", "publisher_submission_authorized"):
        require(manuscript.get(key) is False, f"Paper-2 publication gate unexpectedly open: {key}")


def check_s3x_candidate() -> None:
    candidate = load_json(REBUILD / "S3X_SOURCE_FREEZE_CANDIDATE_R1.json")
    require(candidate.get("experiment_id") == "S3X-ETA-001", "S3X experiment identity drift")
    require(candidate.get("status") == "SOURCE_FREEZE_CANDIDATE__NOT_FROZEN__NO_SCIENTIFIC_EXECUTION", "S3X candidate status drift")

    source = candidate.get("candidate_source", {})
    require(source.get("version") == "v2", "S3X dataset version drift")
    require(source.get("doi") == "10.5281/zenodo.15237121", "S3X DOI drift")
    require(source.get("license_from_official_repository") == "CC BY 3.0 IGO", "S3X license drift")

    scope = candidate.get("selected_scope", {})
    require(scope.get("missions") == ["ESA-Mission1", "ESA-Mission2"], "S3X selected mission scope drift")
    require(scope.get("excluded_missions") == ["ESA-Mission3"], "S3X excluded mission scope drift")

    archives = {row["name"]: row for row in candidate.get("outer_archives", [])}
    expected = {
        "ESA-Mission1.zip": "9770ad12ed730238f37c42d5c27ab436",
        "ESA-Mission2.zip": "bfc72012691427d9327eb41f726ce45e",
    }
    require(set(archives) == set(expected), "S3X outer archive set drift")
    for name, md5 in expected.items():
        require(archives[name].get("zenodo_md5") == md5, f"S3X Zenodo MD5 drift: {name}")
        require(archives[name].get("local_sha256") is None, f"S3X local SHA unexpectedly populated: {name}")
        require(archives[name].get("verified_local") is False, f"S3X local verification unexpectedly true: {name}")

    require(candidate.get("source_freeze_authorized") is False, "S3X source freeze unexpectedly authorized")
    require(candidate.get("source_freeze_ready") is False, "S3X source freeze unexpectedly ready")
    require(candidate.get("recovery_policy_execution_authorized") is False, "S3X recovery execution unexpectedly authorized")

    require((ROOT / "scripts/inspect_s3x_esa_schema.py").is_file(), "S3X schema inspector missing")
    require((REBUILD / "S3X_METADATA_SCHEMA_INSPECTION_R2_2026-09-26.md").is_file(), "S3X metadata/schema record missing")


def check_s6x_candidate() -> None:
    candidate = load_json(REBUILD / "S6X_SOURCE_PIN_CANDIDATE_R1.json")
    require(candidate.get("experiment_id") == "S6X-EAP-001", "S6X experiment identity drift")
    require(candidate.get("status") == "SOURCE_PIN_CANDIDATE__DESIGN_ONLY__NO_CHECKOUT_OR_BUILD_AUTHORIZED", "S6X candidate status drift")

    cfs = candidate.get("cfs", {})
    require(cfs.get("tag") == "v7.0.1", "S6X cFS tag drift")
    require(cfs.get("prerelease") is False, "S6X cFS release-class drift")

    lc = candidate.get("limit_checker", {})
    require(lc.get("pinned_commit_candidate") == "a1c3a47ea1fa5c0d7751d6ff88848dc9bd8a6c7a", "S6X LC commit drift")
    require(lc.get("function") == "LC_SignedCompare", "S6X LC function drift")
    require(lc.get("requirement_ids") == ["LC2003", "LC2003.1"], "S6X requirement binding drift")

    invariant = candidate.get("primary_invariant", {})
    expected_cases = [
        {"operator": "GT", "wp_value": -1, "expected": "FALSE"},
        {"operator": "GT", "wp_value": 0, "expected": "FALSE"},
        {"operator": "GT", "wp_value": 1, "expected": "TRUE"},
        {"operator": "GE", "wp_value": -1, "expected": "FALSE"},
        {"operator": "GE", "wp_value": 0, "expected": "TRUE"},
        {"operator": "GE", "wp_value": 1, "expected": "TRUE"},
    ]
    require(invariant.get("cases") == expected_cases, "S6X invariant truth table drift")
    require(invariant.get("objective_adjudicator_gate_visible") is False, "S6X adjudicator leaked into gate")

    fixture = candidate.get("primary_fixture", {})
    require(fixture.get("fixture_id") == "S6X_FIXTURE_GT_EQ_BOUNDARY_001", "S6X fixture identity drift")
    require(fixture.get("baseline_expression") == "WPValue > CompareValue", "S6X baseline semantics drift")
    require(fixture.get("controlled_incorrect_expression") == "WPValue >= CompareValue", "S6X fixture semantics drift")
    require(fixture.get("implemented") is False, "S6X fixture unexpectedly implemented")

    for key in ("implementation_authorized", "build_authorized", "artifact_mutation_authorized", "scientific_execution_authorized"):
        require(candidate.get(key) is False, f"S6X candidate gate unexpectedly open: {key}")

    require((REBUILD / "S6X_INVARIANT_FIXTURE_DESIGN_R2_2026-09-26.md").is_file(), "S6X invariant design record missing")


def check_no_extension_workspaces() -> None:
    for rel in ("study3x", "study6x", "s3x", "s6x"):
        require(not (ROOT / rel).exists(), f"unauthorized extension workspace exists: {rel}")


def main() -> int:
    check_phase2_status()
    check_s3x_candidate()
    check_s6x_candidate()
    check_no_extension_workspaces()
    require((REBUILD / "PHASE2_DESIGN_GATE_R1_2026-09-26.md").is_file(), "Phase-2 design gate record missing")
    print("paper2_post_rejection_phase2_design_audit=PASS")
    print("s3x_source_freeze_authorized=NO")
    print("s3x_recovery_execution_authorized=NO")
    print("s6x_implementation_authorized=NO")
    print("s6x_build_authorized=NO")
    print("s6x_scientific_execution_authorized=NO")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
