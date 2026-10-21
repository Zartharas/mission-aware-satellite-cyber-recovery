from __future__ import annotations
import hashlib, json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
C=json.loads((ROOT/"study7e/results/S7E-AERC-HELDOUT-EXEC-001/result_checkpoint.json").read_text())
E=(ROOT/"study7e/results/S7E-AERC-HELDOUT-EXEC-001/exact_endpoint_counts.json").read_bytes()
A=(ROOT/"study7e/results/S7E-AERC-HELDOUT-EXEC-001/audit_reconciliation.json").read_bytes()

def test_result_checkpoint_identity_and_population():
    assert C["execution_id"]=="S7E-AERC-HELDOUT-EXEC-001"
    assert C["workflow"]["run_id"]==35948870036
    assert C["population"]["total_scenarios"]==196
    assert C["population"]["total_policy_decisions"]==784

def test_validity_gate_is_complete():
    assert C["validity"]["invalid_scenarios"]==0
    assert C["validity"]["audit_mismatches"]==0
    assert C["validity"]["audit_matches"]==784
    assert C["independent_post_run_recomputation"]["result"]=="PASS"

def test_repo_endpoint_copy_matches_execution_artifact_hash():
    assert hashlib.sha256(E).hexdigest()==C["artifact_file_sha256"]["exact_endpoint_counts.json"]
    assert hashlib.sha256(A).hexdigest()==C["artifact_file_sha256"]["audit_reconciliation.json"]

def test_governance_remains_closed():
    assert C["governance"]["one_shot_execution_sealed"] is True
    assert C["governance"]["retry_authorized"] is False
    assert C["governance"]["post_hoc_model_change_authorized"] is False
    assert C["governance"]["model_retraining_authorized"] is False
    assert C["governance"]["pr_merge_authorized"] is False
    assert C["governance"]["publication_or_result_claims_authorized"] is False
