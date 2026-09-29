#!/usr/bin/env python3
"""Fail-closed audit for S6X pre-runtime closeout/build-design preparation."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
S6X = ROOT / "study6x"
REBUILD = ROOT / "publication/Paper_2_Studies_3_4_6/Post_Rejection_Rebuild"

PROTOCOL = S6X / "S6X_BUILD_EXECUTION_PROTOCOL_CANDIDATE_001.json"
SCHEMA = S6X / "S6X_EVIDENCE_SCHEMA_CANDIDATE_001.json"
HARNESS = S6X / "fixtures/S6X_INVARIANT_HARNESS_EQUALITY_001.patch"
DOCKERFILE = S6X / "validation/S6X_BUILD_ENVIRONMENT_001.Dockerfile"
CLOSEOUT = S6X / "validation/closeout_pre_runtime_validation.sh"
ENV_PREP = S6X / "validation/prepare_build_environment_001.sh"
REPORT = REBUILD / "S6X_PRE_RUNTIME_CLOSEOUT_AND_BUILD_EXECUTION_DESIGN_2026-09-28.md"
STATUS = REBUILD / "S6X_PRE_RUNTIME_CLOSEOUT_BUILD_DESIGN_STATUS.json"
WORKFLOW = ROOT / ".github/workflows/validate-research-configs.yml"

EXPECTED_BASE = "3194c939d5c3d9869187d5c794e380690dc31a44"
EXPECTED_BINDINGS = {
    "study6/STUDY6_PROTOCOL.json": "5218a7158cf96465605196ec40eac8b0199aa690",
    "study6x/S6X_SOURCE_PIN.json": "2af7cb503c3cf8715d31341d731df0533fabfa29",
    "study6x/S6X_PREEXECUTION_PROTOCOL.json": "6d93693495c055c07ced71352e29b813cab1477a",
    "study6x/validation/materialize_validate_cfs_v701.sh": "140356b576699827545518f8a4e172749e111fca",
    "study6x/validation/validate_local_cfs_pin.py": "e7176d370a69d2ca9a3ebbc2637b5891e5045cc0",
    "study6x/fixtures/S6X_FIXTURE_GT_EQ_BOUNDARY_001.patch": "e3189e5a06ff47a2cf68bb7d343c563a300dc313",
    "study6x/src/invariant_oracle.py": "70b555cec84cb455c72094c6539df3873662182d",
}


def fail(message: str) -> None:
    print(f"[FAIL] {message}", file=sys.stderr)
    raise SystemExit(1)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def git_blob(rel: str) -> str:
    return subprocess.check_output(["git", "hash-object", rel], cwd=ROOT, text=True).strip()


def main() -> int:
    for p in (PROTOCOL, SCHEMA, HARNESS, DOCKERFILE, CLOSEOUT, ENV_PREP, REPORT, STATUS, WORKFLOW):
        require(p.is_file(), f"missing S6X design artifact: {p.relative_to(ROOT)}")

    for rel, expected in EXPECTED_BINDINGS.items():
        require(git_blob(rel) == expected, f"bound S6X/Study-6 source drift: {rel}")

    protocol = json.loads(PROTOCOL.read_text(encoding="utf-8"))
    require(protocol["experiment_id"] == "S6X-EAP-001", "S6X experiment id drift")
    require(protocol["protocol_id"] == "S6X-BUILD-EXECUTION-PROTOCOL-CANDIDATE-001", "protocol id drift")
    require(protocol["authorized_main_commit"] == EXPECTED_BASE, "authorized base drift")
    require(protocol["pre_runtime_closeout"]["completed"] is False, "pre-runtime closeout falsely marked complete")
    require(protocol["build_environment_candidate"]["environment_frozen"] is False, "build environment falsely frozen")
    require(protocol["canonical_population_candidate"]["planned_total_gate_observations"] == 396, "planned S6X population drift")
    require(protocol["canonical_population_candidate"]["block_a"]["planned_gate_observations"] == 12, "S6X block-A count drift")
    require(protocol["canonical_population_candidate"]["block_b"]["planned_gate_observations"] == 384, "S6X block-B count drift")
    require(protocol["research_only_invariant"]["oracle_gate_visible"] is False, "correctness oracle leaked into gate")
    require(
        protocol["build_environment_candidate"]["base_image"]
        == "amd64/ubuntu:noble-20260911@sha256:496754492fb28b4d3049432f2ca787449331e23fb14f0dd3fffea86bf5a93eb4",
        "build base image drift",
    )
    for key, value in protocol["authorization"].items():
        require(value is False, f"closed S6X authorization unexpectedly open: {key}")

    status = json.loads(STATUS.read_text(encoding="utf-8"))
    require(status["record_id"] == "S6X-PRE-RUNTIME-CLOSEOUT-BUILD-DESIGN-001", "status id drift")
    require(status["authorized_main_commit"] == EXPECTED_BASE, "status base drift")
    require(status["pre_runtime_validation"]["verified_post_fix_local_rerun_available"] is False, "missing local rerun falsely claimed")
    require(status["pre_runtime_validation"]["closeout_completed"] is False, "S6X closeout falsely completed")
    require(status["build_execution_design"]["canonical_population_planned_gate_observations"] == 396, "status population drift")
    require(status["build_execution_design"]["full_study6_external_replication_claim"] is False, "external replication claim opened")
    require(status["build_execution_design"]["protocol_effective_for_scientific_execution"] is False, "scientific protocol activated early")
    for key, value in status["closed_authorities"].items():
        require(value is False, f"closed authority unexpectedly open: {key}")

    harness = HARNESS.read_text(encoding="utf-8")
    require("WPValue      = 0;" in harness, "compiled equality-boundary harness missing")
    require("Result == LC_WATCH_FALSE" in harness, "GT equality expected-false assertion missing")
    require("LC_SignedCompare_Test_GE" in harness, "GE equality harness missing")

    dockerfile = DOCKERFILE.read_text(encoding="utf-8")
    require("FROM --platform=linux/amd64 amd64/ubuntu:noble-20260911@sha256:496754492fb28b4d3049432f2ca787449331e23fb14f0dd3fffea86bf5a93eb4" in dockerfile, "pinned linux/amd64 base missing")
    require("native_std" not in dockerfile, "Dockerfile must prepare environment only, not build cFS")

    for shell in (CLOSEOUT, ENV_PREP):
        cp = subprocess.run(["bash", "-n", str(shell)], cwd=ROOT, check=False)
        require(cp.returncode == 0, f"shell syntax failed: {shell.relative_to(ROOT)}")

    report = REPORT.read_text(encoding="utf-8")
    for phrase in (
        "no verified post-fix local rerun",
        "compiled independent functional invariant",
        "396",
        "not a full external replication",
        "No cFS/LC compilation",
    ):
        require(phrase.lower() in report.lower(), f"design report missing boundary: {phrase}")

    workflow = WORKFLOW.read_text(encoding="utf-8")
    require(
        "python scripts/audit_paper2_s6x_pre_runtime_closeout_build_design.py" in workflow,
        "S6X closeout/build-design audit not wired into CI",
    )

    print("paper2_s6x_pre_runtime_closeout_build_design_audit=PASS")
    print("verified_post_fix_local_rerun=NO")
    print("pre_runtime_closeout=OPEN")
    print("cfs_build_authorized=NO")
    print("scientific_execution_authorized=NO")
    print("planned_s6x_gate_observations=396")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
