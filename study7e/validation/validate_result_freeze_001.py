#!/usr/bin/env python3
import base64
import hashlib
import io
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "study7e" / "RESULT_FREEZE_MANIFEST_001.json"
STATE = ROOT / "study7e" / "RESULT_FREEZE_STATE.json"
AUTH = ROOT / "study7e" / "configs" / "result_freeze_authorization_001.json"
CANDIDATE = ROOT / "study7e" / "configs" / "result_freeze_candidate_001.json"
CHECKPOINT = ROOT / "study7e" / "results" / "S7E-AERC-HELDOUT-EXEC-001" / "result_checkpoint.json"
ENDPOINTS = ROOT / "study7e" / "results" / "S7E-AERC-HELDOUT-EXEC-001" / "exact_endpoint_counts.json"
AUDIT = ROOT / "study7e" / "results" / "S7E-AERC-HELDOUT-EXEC-001" / "audit_reconciliation.json"

manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
state = json.loads(STATE.read_text(encoding="utf-8"))
auth = json.loads(AUTH.read_text(encoding="utf-8"))
candidate = json.loads(CANDIDATE.read_text(encoding="utf-8"))
checkpoint = json.loads(CHECKPOINT.read_text(encoding="utf-8"))
endpoints = json.loads(ENDPOINTS.read_text(encoding="utf-8"))
audit = json.loads(AUDIT.read_text(encoding="utf-8"))

assert manifest["freeze_id"] == "S7E-AERC-RESULT-FREEZE-001"
assert manifest["state"] == "ACTIVE_RESULTS_FROZEN__PR_MERGE_NOT_AUTHORIZED__PUBLICATION_NOT_AUTHORIZED"
assert manifest["governance"]["result_freeze_active"] is True
assert manifest["governance"]["held_out_execution_sealed"] is True
assert manifest["governance"]["retry_authorized"] is False
assert manifest["governance"]["model_retraining_or_change_authorized"] is False
assert manifest["governance"]["endpoint_or_population_change_authorized"] is False
assert manifest["governance"]["pr_167_merge_authorized"] is False
assert manifest["governance"]["manuscript_or_publication_result_claims_authorized"] is False

assert auth["authorization_id"] == manifest["authorization_id"]
assert auth["authorized"]["formal_result_freeze_activation"] is True
assert auth["authorized"]["durable_byte_exact_artifact_preservation"] is True
assert auth["prohibited"]["pr_167_merge"] is True
assert auth["prohibited"]["manuscript_or_publication_result_claims"] is True

assert state["result_freeze_active"] is True
assert state["scientific_execution_sealed"] is True
assert state["durable_raw_artifact_preserved"] is True
assert state["prohibited"]["pr_167_merge"] is True
assert state["prohibited"]["manuscript_or_publication_result_claims"] is True

assert candidate["candidate_id"] == "S7E-AERC-RESULT-FREEZE-CANDIDATE-001"
assert candidate["candidate_decision"]["scientific_internal_consistency"] == "PASS"
assert candidate["candidate_decision"]["freeze_activated"] is False

assert checkpoint["checkpoint_id"] == "S7E-AERC-HELDOUT-RESULTS-001"
assert checkpoint["execution_id"] == manifest["execution_id"]
assert checkpoint["validity"]["invalid_scenarios"] == 0
assert checkpoint["validity"]["audit_mismatches"] == 0
assert checkpoint["validity"]["paired_equal_information_hashes_verified"] is True
assert checkpoint["validity"]["complete_population_release_criterion_met"] is True
assert checkpoint["governance"]["one_shot_execution_sealed"] is True
assert checkpoint["governance"]["retry_authorized"] is False
assert checkpoint["governance"]["pr_merge_authorized"] is False
assert checkpoint["governance"]["publication_or_result_claims_authorized"] is False

assert endpoints["population"] == {"decisions": 784, "scenarios": 196}
assert endpoints["overall"] == manifest["frozen_result_summary"]["overall"]
assert audit["policy_decisions"] == 784
assert audit["invalid_scenarios"] == 0
assert audit["audit_matches"] == 784
assert audit["audit_mismatches"] == 0
assert audit["all_actions_reconciled"] is True

expected_h = {
    "H1": "SUPPORTED",
    "H2": "PARTIALLY_SUPPORTED",
    "H3": "PARTIALLY_SUPPORTED",
    "H4": "PARTIALLY_SUPPORTED",
    "H5": "SUPPORTED",
}
assert manifest["frozen_result_summary"]["hypothesis_disposition"] == expected_h
assert state["hypothesis_disposition"] == expected_h
assert {k: v["disposition"] for k, v in candidate["hypothesis_review"].items()} == expected_h

artifact = manifest["durable_raw_artifact"]
chunk_paths = [ROOT / item["path"] for item in artifact["chunks"]]
assert [p.name for p in chunk_paths] == sorted(p.name for p in chunk_paths)
encoded = b"".join(p.read_bytes() for p in chunk_paths)
assert len(encoded) == artifact["encoded_chars_including_terminal_newline"]
archive = base64.b64decode(encoded)
assert len(archive) == artifact["decoded_bytes"]
assert hashlib.sha256(archive).hexdigest() == artifact["decoded_sha256"]
assert artifact["decoded_sha256"] == checkpoint["artifact"]["sha256"]

with zipfile.ZipFile(io.BytesIO(archive), "r") as zf:
    names = sorted(zf.namelist())
    expected_names = sorted(artifact["archive_member_sha256"])
    assert names == expected_names
    for name in names:
        observed = hashlib.sha256(zf.read(name)).hexdigest()
        expected = artifact["archive_member_sha256"][name]
        assert observed == expected, f"{name}: {observed} != {expected}"

print("S7E_AERC_RESULT_FREEZE_001=PASS")
print("result_freeze_active=true")
print("durable_artifact_sha256=" + artifact["decoded_sha256"])
print("scenarios=196")
print("policy_decisions=784")
print("invalid_scenarios=0")
print("audit_mismatches=0")
print("pr_167_merge_authorized=false")
print("publication_or_result_claims_authorized=false")
