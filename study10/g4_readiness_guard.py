"""Fail-closed Study 10 G4 readiness audit.

Reads only committed Study 10 governance documentation and frozen Study 2/9
source files. Never opens external ESA/OPS-SAT/Hack-A-Sat telemetry payloads.
A successful audit means the G4 HOLD is intact, NOT that G4 may execute.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GATE = ROOT / "study10/G4_SOURCE_READINESS_GATE_CANDIDATE_20261122.json"
RECEIPT = ROOT / "study10/G2_PROTOCOL_FREEZE_RECEIPT_20261122.json"
G3 = ROOT / "study10/g3_synthetic_validator.py"
EXPECTED_RECEIPT_BLOB = "38e5da5edc193b358012bc9c2c3180917d7419ac"
EXPECTED_G3_BLOB = "ea940991bbfb784c9a47357daf5925c66883a1cd"
EXPECTED_PAYLOAD_COMMIT = "8ed6a2b16233b86bf91672f6f15605dcf906c5eb"


def git_blob_sha1(data: bytes) -> str:
    return hashlib.sha1(
        b"blob " + str(len(data)).encode("ascii") + b"\0" + data
    ).hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def audit() -> dict:
    gate = load(GATE)
    receipt_bytes = RECEIPT.read_bytes()
    assert git_blob_sha1(receipt_bytes) == EXPECTED_RECEIPT_BLOB
    receipt = json.loads(receipt_bytes)
    assert git_blob_sha1(G3.read_bytes()) == EXPECTED_G3_BLOB
    assert receipt["payload"]["read_only_payload_commit"] == EXPECTED_PAYLOAD_COMMIT
    assert receipt["binding_Option_B_source_rights_policy"]["policy_id"] == (
        "B_FREEZE_DESIGN_WITH_SOURCE_USE_HOLD"
    )
    assert receipt["binding_Option_B_source_rights_policy"]["rights_clearance_for_source_data"] is False
    assert receipt["scientific_controls"]["G4_source_semantic_adjudication"].startswith("BLOCKED")
    assert gate["scope"]["current_work_authorized"] == (
        "READ_ONLY_PUBLIC_SOURCE_METADATA_AND_INTERNAL_G4_PREFLIGHT_DOCUMENTATION"
    )
    assert gate["state"] == "HOLD_SOURCE_RIGHTS_INTEGRITY_AND_EXPLICIT_G4_AUTHORIZATION"
    assert gate["frozen_G2"]["payload_commit"] == EXPECTED_PAYLOAD_COMMIT
    assert gate["G3_evidence"]["tested_commit"] == (
        "5ec1c7d29a001cf0711a9e5b357e1937f69ef512"
    )
    assert gate["G3_evidence"]["synthetic_controls_passed"] == 18
    assert gate["G3_evidence"]["standalone_oracle_comparisons_passed"] == 1024
    assert gate["G3_evidence"]["G3_result_immutable_freeze_performed"] is False

    # Compare only local, source-controlled *research protocol* files.
    # No original external satellite data are accessed.
    protocol_files = receipt["payload"]["files"]
    assert len(protocol_files) == 4
    for item in protocol_files:
        path = ROOT / item["path"]
        assert path.is_file()
        raw = path.read_bytes()
        assert len(raw) == item["bytes"]
        assert hashlib.sha256(raw).hexdigest() == item["sha256"]
        assert git_blob_sha1(raw) == item["git_blob_sha1"]

    frozen_stops = receipt["binding_Option_B_source_rights_policy"][
        "hard_fail_closed_pre_G4_conditions"
    ]
    gates = gate["hard_preG4_gates"]
    assert len(gates) == len(frozen_stops) == 6
    assert [entry["required_condition"] for entry in gates] == frozen_stops
    for entry in gates:
        assert entry["status"] in ("HOLD", "BLOCKED_IF_SECONDARY_SOURCE_USED")
        assert entry["sole_author_signoff"] is False
        assert entry["actual_source_use_cleared"] is False
        assert entry["no_real_data_payload_access_in_this_review"] is True

    scope = gate["scope"]
    for key in (
        "real_telemetry_payload_access_authorized",
        "source_byte_download_or_extraction_performed",
        "native_semantic_mapping_authorized",
        "row_level_action_estimation_authorized",
        "dataset_public_redistribution_authorized",
        "publication_submission_authorized",
        "pr_merge_authorized",
    ):
        assert scope[key] is False
    approvals = gate["approval"]
    assert approvals["G4_source_rights_signoff_recorded"] is False
    assert approvals["G4_scientific_execution_authorization_recorded"] is False
    assert approvals["G4_real_data_source_use_authorization_recorded"] is False

    sources = gate["source_identity_evidence"]
    assert len(sources["esa_adb_archive_ids"]) == 6
    assert all(entry["complete_inner_member_integrity_confirmed"] is False
               for entry in sources["esa_adb_archive_ids"])
    assert len(sources["ops_sat_v2"]["files"]) == 3
    assert sources["hackasat4"]["file_family_rights_cleared"] is False

    return {
        "study_id": "S10-RSEI-001",
        "stage": "G4_READINESS_ONLY",
        "gate": "HOLD",
        "validation": "PASS_FAIL_CLOSED_PRE_G4_AUDIT",
        "frozen_G2_protocol_files_sha256_verified": len(protocol_files),
        "frozen_G2_receipt_git_blob_match": True,
        "G3_validator_git_blob_match": True,
        "hard_preG4_conditions_still_blocked": len(gates),
        "original_telemetry_files_read": 0,
        "G4_source_processing_authorized": False,
        "PR_merge_authorized": False,
        "scientific_claim": "NO_REAL_DATA_OR_NATIVE_SEMANTIC_VALIDATION",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--audit", action="store_true", help="Validate the HOLD state")
    group.add_argument("--require-g4-execution", action="store_true",
                       help="Fail closed; never starts telemetry processing")
    args = parser.parse_args()
    result = audit()
    if args.require_g4_execution:
        result["validation"] = "BLOCKED_NO_AUTHOR_RIGHTS_SIGNOFF_OR_G4_AUTHORIZATION"
        print(json.dumps(result, indent=2, sort_keys=True))
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
