#!/usr/bin/env python3
"""Authorized read-only binding of the preserved P2X v2f manifest.

This tool reads the exact preserved manifest, computes SHA-256, and invokes the
independent v2f verifier. It does not launch Docker, start runtime components,
modify evidence, or authorize nominal runtime execution.
"""
import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GATE = ROOT / "paper2x" / "phase_a" / "V2F_NOMINAL_RUNTIME_QUALIFICATION_GATE_2026-10-07.json"
VERIFIER = ROOT / "scripts" / "verify_paper2x_phase_a_v2f.py"

EVIDENCE_ID = "p2xa-nos3-v2f-build-20261007T185149Z-a61cae46f1"
RELATIVE_MANIFEST = (
    "artifacts/runtime/" + EVIDENCE_ID + "/p2x-v2f-build-manifest.json"
)
EXPECTED_PARENT_HEAD = "8f5faef3830646eae065e8210216a2ed4301316c"
EXPECTED_DESCRIPTOR_SHA = "08ea45ca09c9a82b5456bea1f93cf325c1a61a8ae4332c5a8dea1b7d4dfbb736"


def hold(reason: str) -> None:
    raise SystemExit("P2X_V2F_MANIFEST_READBACK_HOLD=" + reason)


def require(ok: bool, reason: str) -> None:
    if not ok:
        hold(reason)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fd:
        for chunk in iter(lambda: fd.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def validate_gate() -> dict:
    gate = json.loads(GATE.read_text(encoding="utf-8"))
    require(gate["record_id"] ==
            "P2X-PHASE-A-V2F-NOMINAL-RUNTIME-QUALIFICATION-GATE-2026-10-07",
            "wrong_gate")
    require(gate["decision"] ==
            "AUTHOR_EXPLICITLY_APPROVED_V2F_READ_ONLY_MANIFEST_BINDING",
            "read_only_binding_not_authorized")
    require(gate.get("read_only_manifest_binding_authorized") is True,
            "read_only_binding_flag_closed")
    require(gate["execution_authorized"] is False,
            "runtime_execution_open")
    scope = gate["authorization_scope"]
    require(scope["read_only_manifest_hash_readback"] is True and
            scope["nominal_runtime_execution"] is False and
            scope["benign_internal_cfs_noop"] is False and
            scope["cosmos"] is False and
            scope["faults"] is False and
            scope["scientific_observations"] is False and
            scope["final_environment_acceptance"] is False and
            scope["merge_pr215"] is False,
            "scope_firewall")
    require(gate["parent_v2f_executed_head"] == EXPECTED_PARENT_HEAD and
            gate["parent_v2f_evidence_id"] == EVIDENCE_ID and
            gate["parent_v2f_manifest_relative_path"] == RELATIVE_MANIFEST and
            gate["parent_v2f_descriptor_map_sha256"] == EXPECTED_DESCRIPTOR_SHA and
            gate["parent_v2f_raw_artifact_identity"] == "9_OF_9" and
            gate["parent_v2f_independent_readback"] == "PASS",
            "parent_binding_drift")
    require(gate["parent_v2f_manifest_sha256"] is None and
            gate["parent_v2f_manifest_sha256_status"] ==
            "PENDING_AUTHORIZED_READ_ONLY_HOST_READBACK",
            "manifest_hash_already_bound_or_state_drift")
    require(gate["runtime_execution_result"] == "NOT_RUN" and
            gate["environment_final_acceptance"] is False,
            "false_runtime_state")
    return gate


def self_test() -> None:
    gate = validate_gate()
    require(gate["read_only_manifest_binding_parent_workflow_run"] == 1412,
            "authorization_parent_workflow_drift")
    require(gate["read_only_manifest_binding_parent_head"] ==
            "21cac2c161a16fdddd5f541ceb5ff8df5b7f8d19",
            "authorization_parent_head_drift")
    print("P2X_V2F_MANIFEST_READBACK_SELF_TEST=PASS")
    print("P2X_V2F_MANIFEST_READBACK_EXECUTION_SCOPE=READ_ONLY")
    print("P2X_V2F_RUNTIME_EXECUTION=NOT_AUTHORIZED")


def readback() -> None:
    validate_gate()
    manifest = (ROOT / RELATIVE_MANIFEST).resolve()
    root_resolved = ROOT.resolve()
    require(str(manifest).startswith(str(root_resolved) + "/"),
            "manifest_outside_repository")
    require(manifest.is_file(), "manifest_missing:" + str(manifest))

    digest = sha256_file(manifest)

    p = subprocess.run(
        [sys.executable, str(VERIFIER), str(manifest)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    output = (p.stdout or "") + (p.stderr or "")
    require(p.returncode == 0, "independent_verifier_failed")
    require("P2X_V2F_INDEPENDENT_NINE_RAW_SHA256_READBACK=PASS" in output,
            "nine_raw_readback_missing")
    require("P2X_V2F_DEPENDENCY_DESCRIPTOR_MAP_READBACK=PASS" in output,
            "descriptor_readback_missing")
    require("P2X_V2F_TWO_NEW_CANDIDATES=9_OF_9_BYTE_IDENTICAL" in output,
            "nine_of_nine_missing")
    require("P2X_V2F_RUNTIME=NOT_TESTED" in output,
            "runtime_boundary_missing")

    print("P2X_V2F_MANIFEST_READBACK=PASS")
    print("P2X_V2F_MANIFEST_PATH=" + str(manifest))
    print("P2X_V2F_MANIFEST_SHA256=" + digest)
    print("P2X_V2F_EVIDENCE_ID=" + EVIDENCE_ID)
    print("P2X_V2F_PARENT_EXECUTED_HEAD=" + EXPECTED_PARENT_HEAD)
    print("P2X_V2F_DESCRIPTOR_MAP_SHA256=" + EXPECTED_DESCRIPTOR_SHA)
    print("P2X_V2F_RAW_ARTIFACT_IDENTITY=9_OF_9")
    print("P2X_V2F_RUNTIME_EXECUTED=NO")
    print("P2X_V2F_COSMOS_EXECUTED=NO")
    print("P2X_V2F_FAULT_CAMPAIGN_EXECUTED=NO")
    print("P2X_V2F_FINAL_ENVIRONMENT_ACCEPTANCE=NO")


def main() -> None:
    p = argparse.ArgumentParser()
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--self-test", action="store_true")
    g.add_argument("--readback", action="store_true")
    args = p.parse_args()
    if args.self_test:
        self_test()
    else:
        readback()


if __name__ == "__main__":
    main()
