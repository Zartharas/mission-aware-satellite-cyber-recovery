#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
FREEZE=ROOT/"study6x/S6X_CANONICAL_RESULT_FREEZE_004.json"
STATUS=ROOT/"publication/Paper_2_Studies_3_4_6/Post_Rejection_Rebuild/S6X_CANONICAL_RESULT_FREEZE_004_STATUS.json"
WORKFLOW=ROOT/".github/workflows/validate-research-configs.yml"

EXPECTED={
"study6x/S6X_CANONICAL_RUNTIME_AUTH_004.json":"d5a329be6c0803c5345845746c66844db8cfb552",
"study6x/validation/run_local_canonical_execution_004.sh":"99088f34886c50d38efaabf1c0aca4679fe07342",
"study6x/S6X_BUILD_EXECUTION_PROTOCOL_CORRECTION_004.json":"2146de81c09a6c8b240e257fed09618baa1aa33f",
"study6x/S6X_EXECUTION_ATTEMPT_001_FAILURE_FREEZE.json":"d381cc8ac4faf1d9ae465bbf76bed85f3353732b",
"study6x/S6X_EXECUTION_ATTEMPT_002_FAILURE_FREEZE.json":"7608fb45151850e4d07709a26a5daa1f70b00ccc",
"study6x/S6X_EXECUTION_ATTEMPT_003_FAILURE_FREEZE.json":"44059848fe984b2de0e06a61b8416575266fab72",
"study6x/S6X_CANONICAL_RESULT_FREEZE_004.json":"2e6b213b994062fd108e4b8435d9c0c36d93fdc0",
"publication/Paper_2_Studies_3_4_6/Post_Rejection_Rebuild/S6X_CANONICAL_RESULT_FREEZE_004_STATUS.json":"1d86adf7d02c8573a8b791b9c9a68ac3077da020"
}

def fail(message):
    print(f"[FAIL] {message}",file=sys.stderr)
    raise SystemExit(1)

def req(condition,message):
    if not condition:
        fail(message)

def blob(rel):
    return subprocess.check_output(["git","hash-object",rel],cwd=ROOT,text=True).strip()

for rel,sha in EXPECTED.items():
    p=ROOT/rel
    req(p.is_file(),f"missing {rel}")
    req(blob(rel)==sha,f"bound drift: {rel}")

f=json.loads(FREEZE.read_text())
req(f["freeze_id"]=="S6X-CANONICAL-RESULT-FREEZE-004","freeze id drift")
req(f["campaign_id"]=="S6X_CANONICAL_EXECUTION_004","campaign id drift")
req(f["status"]=="PREPARED_ON_FEATURE_BRANCH__NOT_EFFECTIVE_UNTIL_APPROVED_MERGE","freeze preparation status drift")
req(f["designation_after_effectivity"]=="CANONICAL_SUCCESSFUL_S6X_EXECUTION","canonical designation drift")
req(f["claim_scope"]=="SEPARATE_EXECUTABLE_STRESS_TEST_OF_STUDY6_OBSERVABILITY_MECHANISM__NOT_EXTERNAL_REPLICATION","claim-scope drift")

a=f["execution_authority"]
req(a["authoritative_main"]=="dcd917f0f8703d571d7527b5a7fd10c3b8692439","execution authority main drift")
req(a["runtime_authorization_id"]=="S6X-CANONICAL-RUNTIME-AUTH-004","runtime authorization id drift")
req(a["runtime_authorization_blob"]=="d5a329be6c0803c5345845746c66844db8cfb552","runtime authorization blob drift")
req(a["runner_blob"]=="99088f34886c50d38efaabf1c0aca4679fe07342","runner blob drift")
req(a["protocol_correction_blob"]=="2146de81c09a6c8b240e257fed09618baa1aa33f","correction blob drift")
req(a["post_merge_ci_run_number"]==1312 and a["post_merge_ci_run_id"]==36762057242 and a["post_merge_ci_conclusion"]=="success","post-merge CI binding drift")
req(a["explicit_author_execution_gate"]=="APPROVED","execution gate binding drift")

t=f["terminal_execution_evidence"]
req(t["runner_exit_code"]==0 and t["runner_terminal_pass"] is True,"Campaign 004 terminal runner status drift")
req(t["terminal_banner"]=="S6X_CANONICAL_SCIENTIFIC_EXECUTION_004=PASS","terminal banner drift")
req(t["console_log_sha256"]=="e45bd9c912d34a9d56c9a7368b2b5714e491eee45dd8640c25412d963d0f5c3c","console hash drift")
req(t["final_repository_main"]=="dcd917f0f8703d571d7527b5a7fd10c3b8692439","final main binding drift")
req(t["tracked_repository_mutation"] is False,"tracked mutation evidence drift")

b=f["build_and_test_evidence"]
req(b["repetitions"]==2 and b["builds_per_repetition"]==4 and b["total_builds"]==8,"build/repetition count drift")
req(b["artifact_path"]=="build-native_std/exe/cpu1/cf/lc.so","artifact path drift")
req(b["clean_artifact_sha256"]=="7311d8d1b89ffe2ca0e43ca1e2f6430db28d2f9532ebf426c4870ab5847f1670","clean artifact drift")
req(b["approved_bad_source_artifact_sha256"]=="275ae69dc92dd60f023d203664ab5fda021b46100a58d1f670a8546dd57f031c","bad artifact drift")
for run in ("run1","run2"):
    r=b[run]
    req(r["clean_primary_sha256"]==r["clean_rebuild_sha256"]=="7311d8d1b89ffe2ca0e43ca1e2f6430db28d2f9532ebf426c4870ab5847f1670",f"{run} clean reproducibility drift")
    req(r["bad_primary_sha256"]==r["bad_rebuild_sha256"]=="275ae69dc92dd60f023d203664ab5fda021b46100a58d1f670a8546dd57f031c",f"{run} bad reproducibility drift")
    req(r["clean_primary_runtest_rc"]==0 and r["clean_rebuild_runtest_rc"]==0,f"{run} clean RC drift")
    req(r["bad_primary_runtest_rc"]==2 and r["bad_rebuild_runtest_rc"]==2,f"{run} bad RC drift")
    req(r["clean_primary_rebuild_match"] is True and r["bad_primary_rebuild_match"] is True and r["clean_bad_artifact_distinct"] is True,f"{run} acceptance drift")
req(b["repeated_build_hashes_and_test_outcomes_match"] is True,"repeated build/test record drift")

p=f["scientific_population_evidence"]
req(p["observations_per_repetition"]==396 and p["block_a_rows_per_repetition"]==12 and p["block_b_rows_per_repetition"]==384,"population contract drift")
req(p["run1_primary_reference_gate_mismatches"]==0 and p["run2_primary_reference_gate_mismatches"]==0,"gate mismatch drift")
req(p["run1_independent_validation"]=="PASS" and p["run2_independent_validation"]=="PASS","independent validation drift")
req(p["scientific_population_validation"]=="PASS","population validation drift")

expected_results={
"S6X_GATE_OBSERVATIONS_004.csv":"cb840a8d89267b313be79280d2909e708327cb5ca333e23dbfc7e50b9e37dc63",
"S6X_SUMMARY_004.json":"965c14ebe7b888c955a21b8d676ccb577b37bd78ff549f319011e699ffb76d92",
"S6X_EVIDENCE_RECORDS_004.json":"3feae27e2359d1ec385efb1e38209c72445444d9a03d20afac520efe74cd1a35",
"S6X_INDEPENDENT_VALIDATION_004.json":"6918268bf53a7a9356bb0e42c88b3f4626274364855ab62e83c2b1a4857acf89",
"S6X_RESULTS_HASH_MANIFEST_004.json":"5ee9beae2c81945abdc6169621f764cbdd55f0521c781dbab1527b84ae6529be"
}
r=f["deterministic_repeat_result_hashes"]
req({k:r[k] for k in expected_results}==expected_results,"canonical result hash bindings drift")
req(r["repeat_identity"]=="PASS","deterministic repeat designation drift")

sig=f["signature_evidence"]
req(sig["governed_signature_count"]==4,"signature count drift")
req(sig["run1_clean_signature_sha256"]==sig["run2_clean_signature_sha256"]=="e085a4746d138573932a8d7c9992fa62cc40bb876c9bc59965aac224f81fa16c","clean signature binding drift")
req(sig["run1_bad_signature_sha256"]==sig["run2_bad_signature_sha256"]=="68ba20e6f6250d9089ad21f959f73d7ad3faf21c7dd998ac9d3c778a8bbe7f8a","bad signature binding drift")
req(sig["clean_signature_repeat_match"] is True and sig["bad_signature_repeat_match"] is True,"signature repeat drift")

hist=f["historical_attempts_preserved"]
req(len(hist)==3,"historical attempt count drift")
expected_hist=[
("S6X-EXEC-ATTEMPT-001","d381cc8ac4faf1d9ae465bbf76bed85f3353732b","FAILED_CLOSED_PRE_SCIENTIFIC_OBSERVATION_GENERATION__TOOLING_ONLY"),
("S6X-EXEC-ATTEMPT-002","7608fb45151850e4d07709a26a5daa1f70b00ccc","FAILED_CLOSED_PRE_SCIENTIFIC_OBSERVATION_GENERATION__RUNNER_STDOUT_HASH_CAPTURE_CONTROL_DEFECT"),
("S6X-EXEC-ATTEMPT-003","44059848fe984b2de0e06a61b8416575266fab72","FAILED_CLOSED_AFTER_COMPLETE_SCIENTIFIC_EXECUTION_AND_VALIDATION__POST_EXECUTION_RESULT_HASH_REPORTING_VARIABLE_EXPANSION_CONTROL_DEFECT")
]
for item,(aid,bsha,status) in zip(hist,expected_hist):
    req(item["attempt_id"]==aid and item["freeze_blob"]==bsha and item["status"]==status,f"historical freeze binding drift: {aid}")

scope=f["freeze_scope"]
req(scope["result_population_freeze_authorized_by_author"] is True,"result-freeze authorization missing")
req(scope["result_freeze_effective_at_record_creation"] is False,"freeze effective before merge")
req(scope["result_freeze_effective_only_when_record_tracked_on_main"] is True,"freeze effectivity boundary weakened")
req(scope["canonical_successful_execution_designation_effective_at_record_creation"] is False,"canonical designation effective early")
for key in ("raw_campaign_workspace_commit_authorized","canonical_output_file_commit_authorized","manuscript_claim_use_authorized","figure_revision_authorized","study6_modification_authorized","study6_s6x_pooling_authorized","venue_lock_authorized"):
    req(scope[key] is False,f"prohibited freeze scope opened: {key}")

eff=f["effectivity"]
req(eff["creation_state"]=="PREPARED_ON_FEATURE_BRANCH__NOT_EFFECTIVE","effectivity creation state drift")
req(eff["approved_merge_required"] is True and eff["record_must_be_tracked_on_main"] is True,"merge/main gate weakened")
req(eff["post_merge_ci_required_before_any_claim_use_review"] is True,"post-merge CI gate weakened")

pres=f["preservation"]
req(pres["preserve_campaign_004_directory"] is True and pres["preserve_campaign_004_console_log"] is True,"Campaign 004 preservation weakened")
req(pres["delete_modify_move_or_rerun_campaign_004"] is False,"Campaign 004 mutation/reuse opened")
req(pres["campaign_005_required"] is False,"unnecessary Campaign 005 introduced")

s=json.loads(STATUS.read_text())
req(s["phase"]=="S6X_CANONICAL_RESULT_FREEZE_004_PREPARATION","status phase drift")
req(s["freeze_candidate"]["id"]=="S6X-CANONICAL-RESULT-FREEZE-004","status freeze id drift")
req(s["freeze_candidate"]["blob"]=="2e6b213b994062fd108e4b8435d9c0c36d93fdc0","status freeze blob drift")
req(s["freeze_candidate"]["result_freeze_effective_at_record_creation"] is False,"status marks freeze effective early")
req(s["freeze_candidate"]["canonical_successful_execution_designation_effective_at_record_creation"] is False,"status marks canonical designation effective early")
req(s["campaign_004"]["runner_exit_code"]==0 and s["campaign_004"]["runner_terminal_pass"] is True,"status loses terminal PASS")
req(s["campaign_004"]["observations_per_repetition"]==396 and s["campaign_004"]["repetitions"]==2 and s["campaign_004"]["total_builds"]==8,"status campaign contract drift")
req(s["campaign_004"]["primary_reference_gate_mismatches"]==0 and s["campaign_004"]["independent_validation"]=="PASS" and s["campaign_004"]["deterministic_repeat_results"]=="PASS","status scientific validation drift")
for key,value in s["publication_boundaries"].items():
    req(value is False,f"publication boundary opened: {key}")

tracked=subprocess.check_output(["git","ls-files"],cwd=ROOT,text=True).splitlines()
for rel in tracked:
    req(not rel.startswith("study6x/workspace/S6X_CANONICAL_EXECUTION_004/"),"raw Campaign 004 workspace tracked")
    req(rel!="study6x/workspace/S6X_CANONICAL_EXECUTION_004_console.log","Campaign 004 console log tracked")
for name in expected_results:
    req(not any(Path(rel).name==name and rel.startswith("study6x/workspace/") for rel in tracked),f"raw canonical output tracked: {name}")

req("python scripts/audit_paper2_s6x_canonical_result_freeze_004.py" in WORKFLOW.read_text(),"CI hook missing")

print("paper2_s6x_canonical_result_freeze_004_audit=PASS")
print("campaign004_terminal_runner_pass=YES")
print("scientific_population_validation=PASS")
print("deterministic_repeat_results=PASS")
print("historical_attempts_001_003_preserved=YES")
print("result_freeze_004_prepared=YES")
print("result_freeze_effective=NO_PENDING_APPROVED_MERGE")
print("raw_campaign_workspace_committed=NO")
print("canonical_output_files_committed=NO")
print("manuscript_claim_use=NO")
print("figure_revision=NO")
print("study6_s6x_pooling=NO")
print("campaign005_required=NO")
