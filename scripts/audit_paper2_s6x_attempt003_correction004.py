#!/usr/bin/env python3
from __future__ import annotations
import copy
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
FREEZE=ROOT/"study6x/S6X_EXECUTION_ATTEMPT_003_FAILURE_FREEZE.json"
CORRECTION=ROOT/"study6x/S6X_BUILD_EXECUTION_PROTOCOL_CORRECTION_004.json"
AUTH=ROOT/"study6x/S6X_CANONICAL_RUNTIME_AUTH_004.json"
STATUS=ROOT/"publication/Paper_2_Studies_3_4_6/Post_Rejection_Rebuild/S6X_ATTEMPT003_FAILURE_FREEZE_CORRECTION_004_STATUS.json"
SCHEMA3=ROOT/"study6x/S6X_EVIDENCE_SCHEMA_003.json"
SCHEMA4=ROOT/"study6x/S6X_EVIDENCE_SCHEMA_004.json"
RUNTIME3=ROOT/"study6x/runtime/run_canonical_population_003.py"
RUNTIME4=ROOT/"study6x/runtime/run_canonical_population_004.py"
VALIDATOR3=ROOT/"study6x/audit/validate_canonical_execution_003.py"
VALIDATOR4=ROOT/"study6x/audit/validate_canonical_execution_004.py"
RUNNER3=ROOT/"study6x/validation/run_local_canonical_execution_003.sh"
RUNNER4=ROOT/"study6x/validation/run_local_canonical_execution_004.sh"
WORKFLOW=ROOT/".github/workflows/validate-research-configs.yml"

EXPECTED={
"study6x/S6X_CANONICAL_RUNTIME_AUTH_003.json":"b5399dce4f671733e0637e19965e0a6a6605ee78",
"study6x/S6X_BUILD_EXECUTION_PROTOCOL_CORRECTION_003.json":"35271a7e5aa672e63072c4b228dc321cca6f1826",
"study6x/validation/run_local_canonical_execution_003.sh":"3f3379cedcdbd89b1fd3f2eb793e7522dfbd0283",
"study6x/S6X_EVIDENCE_SCHEMA_003.json":"768298234860a886b919af6449cec026478e7e81",
"study6x/runtime/run_canonical_population_003.py":"aa998b3fd50b76d9f2f9c95db28ca90adced8209",
"study6x/audit/validate_canonical_execution_003.py":"da55bb1d807494addff10759dd99921e3e51ecff",
"study6x/S6X_BUILD_ENVIRONMENT_FREEZE_002.json":"235d7524f254ae3ad0ff6a4f331be59aceb3aaed",
"study6x/S6X_SOURCE_PIN.json":"2af7cb503c3cf8715d31341d731df0533fabfa29",
"study6x/fixtures/S6X_FIXTURE_GT_EQ_BOUNDARY_001.patch":"e3189e5a06ff47a2cf68bb7d343c563a300dc313",
"study6x/fixtures/S6X_INVARIANT_HARNESS_EQUALITY_001.patch":"b3318be396a6c4e5c98f2339846d9ea59bcd5def",
"study6x/src/invariant_oracle.py":"70b555cec84cb455c72094c6539df3873662182d",
"study6x/runtime/gate_evaluator.py":"c6045b249daa6a3ff3b2ff54982b047c299fd04c",
"study6x/audit/reference_gate_evaluator.py":"c3834f478196fe3fd3e9290ff0ecc603a0933247",
"study6x/S6X_EXECUTION_ATTEMPT_003_FAILURE_FREEZE.json":"44059848fe984b2de0e06a61b8416575266fab72",
"study6x/S6X_BUILD_EXECUTION_PROTOCOL_CORRECTION_004.json":"2146de81c09a6c8b240e257fed09618baa1aa33f",
"study6x/S6X_EVIDENCE_SCHEMA_004.json":"af697b5407bf1eda49667109d208aa9e57030494",
"study6x/runtime/run_canonical_population_004.py":"965fde110b7dc754553efe08b1530beeba752908",
"study6x/audit/validate_canonical_execution_004.py":"b4c7a81ae74e118d820ae2ada107d9e15e40ed2e",
"study6x/validation/run_local_canonical_execution_004.sh":"99088f34886c50d38efaabf1c0aca4679fe07342",
"study6x/S6X_CANONICAL_RUNTIME_AUTH_004.json":"d5a329be6c0803c5345845746c66844db8cfb552",
"publication/Paper_2_Studies_3_4_6/Post_Rejection_Rebuild/S6X_ATTEMPT003_FAILURE_FREEZE_CORRECTION_004_STATUS.json":"e227378a285b1e0884e345e257aa3834bfc45338"
}

def fail(message):
    print(f"[FAIL] {message}",file=sys.stderr)
    raise SystemExit(1)

def req(condition,message):
    if not condition:
        fail(message)

def blob(rel):
    return subprocess.check_output(["git","hash-object",rel],cwd=ROOT,text=True).strip()

for path in (FREEZE,CORRECTION,AUTH,STATUS,SCHEMA3,SCHEMA4,RUNTIME3,RUNTIME4,VALIDATOR3,VALIDATOR4,RUNNER3,RUNNER4,WORKFLOW):
    req(path.is_file(),f"missing {path.relative_to(ROOT)}")

for rel,sha in EXPECTED.items():
    req(blob(rel)==sha,f"bound drift: {rel}")

f=json.loads(FREEZE.read_text())
req(f["attempt_id"]=="S6X-EXEC-ATTEMPT-003","attempt id drift")
req(f["status"]=="FAILED_CLOSED_AFTER_COMPLETE_SCIENTIFIC_EXECUTION_AND_VALIDATION__POST_EXECUTION_RESULT_HASH_REPORTING_VARIABLE_EXPANSION_CONTROL_DEFECT","Attempt 003 status drift")
e=f["author_supplied_preserved_evidence"]
req(e["console_log_sha256"]=="222f16141add494887397fad40d98ef497cd09f07c9b0e832f5716181f645684","console binding drift")
req(e["governed_build_roots"]==8 and e["repetitions_completed"]==2 and e["total_builds_completed"]==8,"build/repetition evidence drift")
req(e["clean_artifact_sha256"]=="7311d8d1b89ffe2ca0e43ca1e2f6430db28d2f9532ebf426c4870ab5847f1670","clean artifact binding drift")
req(e["bad_artifact_sha256"]=="275ae69dc92dd60f023d203664ab5fda021b46100a58d1f670a8546dd57f031c","bad artifact binding drift")
req(e["clean_runtest_rc_run1"]==0 and e["clean_runtest_rc_run2"]==0,"clean RC drift")
req(e["bad_runtest_rc_run1"]==2 and e["bad_runtest_rc_run2"]==2,"bad RC drift")
req(e["observations_per_repetition"]==396 and e["block_a_rows_per_repetition"]==12 and e["block_b_rows_per_repetition"]==384,"population evidence drift")
req(e["primary_reference_gate_mismatches_run1"]==0 and e["primary_reference_gate_mismatches_run2"]==0,"gate mismatch evidence drift")
req(e["independent_validation_run1"]=="PASS" and e["independent_validation_run2"]=="PASS","independent validation evidence drift")
req(e["repeated_build_hashes_and_test_outcomes_match"] is True,"build/test repeat evidence drift")
req(e["governed_signature_count"]==4,"signature count drift")
req(e["clean_signature_sha256"]=="579955e0068382e4b2269e0faedd06470efcdb206ccb0646895ce417cb7a721e","clean signature drift")
req(e["bad_signature_sha256"]=="4cc6cc3e9382b83110ff3cbdb5556fa9d43e4e8af976984e72012f38064caf09","bad signature drift")
expected_results={
"S6X_GATE_OBSERVATIONS_003.csv":"cb840a8d89267b313be79280d2909e708327cb5ca333e23dbfc7e50b9e37dc63",
"S6X_SUMMARY_003.json":"1640d813ecedd88a010c7af08d7ddcefaee70e58d5c72c089d3511136a9dea45",
"S6X_EVIDENCE_RECORDS_003.json":"0c9ce23c2d4579e255f38406a719405b5d797b465337be06ec0583f0b2e36522",
"S6X_INDEPENDENT_VALIDATION_003.json":"ad73d59e9ca2b991117a56b2ae9a60f9f23091f0f885202fe43bf68ab346bf4f",
"S6X_RESULTS_HASH_MANIFEST_003.json":"00ce8718f86ca632a46b5456186203893fc092ef6114e0b45f891e901657c80d"
}
req(e["repeated_result_files"]==expected_results,"repeated result hash bindings drift")
req(e["read_only_closeout_diagnostic"]=="PASS" and e["scientific_work_rerun_during_closeout"] is False and e["result_files_modified_during_closeout"] is False and e["tracked_repository_mutation"] is False,"closeout preservation drift")

ad=f["acceptance_disposition"]
req(ad["scientific_execution_completed"] is True and ad["deterministic_repeat_execution_completed"] is True,"Attempt 003 execution completion drift")
req(ad["scientific_acceptance_contract"]=="PASS","scientific acceptance not preserved")
req(ad["runner_terminal_pass_reached"] is False and ad["runner_exit_code"]==1,"runner terminal failure drift")
req(ad["scientific_failure"] is False and ad["runner_control_failure"] is True,"failure classification drift")
root=f["root_cause_classification"]
req(root["failing_expression"]=='echo "$name_sha256=$H1"',"failing expression drift")
req(root["intended_expression"]=='echo "${name}_sha256=$H1"',"intended expression drift")
d=f["disposition"]
for key in ("result_freeze_authorized","canonical_output_commit_authorized","manuscript_claim_use_authorized","figure_revision_authorized","study6_modification_authorized","study6_s6x_pooling_authorized","venue_lock_authorized"):
    req(d[key] is False,f"Attempt 003 prohibited scope opened: {key}")
req(d["delete_or_reuse_attempt_directory"] is False and d["canonical_execution_003_reuse_authorized"] is False,"Attempt 003 reuse opened")

c=json.loads(CORRECTION.read_text())
req(c["correction_id"]=="S6X-BUILD-EXECUTION-PROTOCOL-CORRECTION-004","Correction 004 id drift")
req(c["attempt_003_failure_freeze"]["blob"]=="44059848fe984b2de0e06a61b8416575266fab72","Correction 004 freeze binding drift")
req(c["attempt_003_scientific_disposition"]["scientific_acceptance_contract"]=="PASS","Correction 004 loses scientific acceptance evidence")
cc=c["correction"]
req(cc["predecessor_expression"]=='echo "$name_sha256=$H1"',"Correction predecessor expression drift")
req(cc["corrected_expression"]=='echo "${name}_sha256=$H1"',"Correction expression drift")
req(cc["reporting_expression_changed"] is True,"reporting correction absent")
for key in ("build_commands_changed","digest_transport_changed","source_or_fixture_changed","environment_changed","artifact_path_changed","signing_logic_changed","population_logic_changed","validation_logic_changed","acceptance_thresholds_changed","scientific_logic_changed"):
    req(cc[key] is False,f"Correction 004 exceeds reporting-only scope: {key}")
u=c["unchanged_scientific_contract"]
req(u["planned_gate_observations_per_repetition"]==396 and u["block_a_rows"]==12 and u["block_b_rows"]==384,"population contract changed")
req(u["repetitions"]==2 and u["builds_per_repetition"]==4 and u["total_builds"]==8,"build plan changed")
req(u["build_commands"]==["make native_std.prep","make native_std.install","make native_std.runtest"],"build commands changed")
req(u["clean_primary_rebuild_sha256_match_required"] is True and u["bad_primary_rebuild_sha256_match_required"] is True and u["clean_bad_artifact_sha256_must_differ"] is True,"artifact acceptance changed")
req(u["required_gate_mismatches"]==0 and u["repeated_scientific_output_hash_mismatches_allowed"]==0,"mismatch allowance changed")
req(all(v is False for v in c["authorization"].values()),"Correction 004 authorizes execution")

a=json.loads(AUTH.read_text())
req(a["authorization_id"]=="S6X-CANONICAL-RUNTIME-AUTH-004","Auth 004 id drift")
req(a["supersedes_runtime_authorization_id"]=="S6X-CANONICAL-RUNTIME-AUTH-003","Auth supersession drift")
req(a["status"]=="PREPARED_ON_FEATURE_BRANCH__NOT_EFFECTIVE","Auth 004 effective early")
req(a["predecessor"]["attempt_003_failure_freeze_blob"]=="44059848fe984b2de0e06a61b8416575266fab72","Auth 004 freeze binding drift")
req(a["predecessor"]["protocol_correction_blob"]=="2146de81c09a6c8b240e257fed09618baa1aa33f","Auth 004 correction binding drift")
req(a["predecessor"]["attempt_003_scientific_acceptance"]=="PASS","Auth 004 loses Attempt 003 scientific acceptance")
b=a["frozen_bindings"]
req(b["evidence_schema_004_blob"]=="af697b5407bf1eda49667109d208aa9e57030494" and b["runtime_population_generator_004_blob"]=="965fde110b7dc754553efe08b1530beeba752908" and b["independent_validator_004_blob"]=="b4c7a81ae74e118d820ae2ada107d9e15e40ed2e" and b["runtime_runner_004_blob"]=="99088f34886c50d38efaabf1c0aca4679fe07342","Auth 004 runtime bindings drift")
scope=a["authorization_scope"]
for key in ("frozen_environment_use_authorized","recursive_pinned_submodule_materialization_authorized","cfs_build_authorized","semantic_fixture_application_to_build_authorized","research_only_artifact_signing_authorized","provenance_observation_generation_authorized","independent_rebuild_authorized","qualification_gate_execution_authorized","scientific_execution_authorized","independent_reference_validation_authorized","deterministic_repeat_execution_authorized"):
    req(scope[key] is True,f"prospective authorized scope closed: {key}")
for key in ("result_freeze_authorized","canonical_output_commit_authorized","manuscript_claim_use_authorized","figure_revision_authorized","study6_modification_authorized","study6_s6x_pooling_authorized","venue_lock_authorized"):
    req(scope[key] is False,f"prohibited Auth 004 scope open: {key}")
rc=a["runtime_constraints"]
req(rc["campaign_root"]=="study6x/workspace/S6X_CANONICAL_EXECUTION_004","Campaign 004 binding drift")
req(rc["repetitions"]==2 and rc["builds_per_repetition"]==4 and rc["total_builds"]==8,"Auth 004 build plan drift")
req(rc["expected_gate_observations_per_repetition"]==396 and rc["expected_block_a_rows"]==12 and rc["expected_block_b_rows"]==384,"Auth 004 population drift")
req(rc["artifact_path"]=="build-native_std/exe/cpu1/cf/lc.so","artifact path drift")
req(rc["artifact_digest_transport"]=="DEDICATED_SHA256_FILES" and rc["artifact_digest_regex"]=="^[0-9a-f]{64}$","digest transport drift")
req(a["scientific_acceptance"]["clean_primary_rebuild_sha256_match_required"] is True,"clean reproducibility weakened")
req(a["scientific_acceptance"]["bad_primary_rebuild_sha256_match_required"] is True,"bad reproducibility weakened")
req(a["scientific_acceptance"]["clean_bad_artifact_sha256_must_differ"] is True,"clean/bad distinction weakened")
req(a["scientific_acceptance"]["primary_reference_gate_mismatches_allowed"]==0 and a["scientific_acceptance"]["repeated_scientific_output_hash_mismatches_allowed"]==0,"mismatch allowances changed")
req(all(v is False for v in a["execution_state_at_record_creation"].values()),"Auth 004 records execution early")
req(a["effectivity"]["record_effective_only_when_tracked_on_main"] is True and a["effectivity"]["post_merge_ci_required_before_execution"] is True and a["effectivity"]["actual_runtime_execution_requires_explicit_post_merge_author_instruction"] is True,"Auth 004 execution gate weakened")

s=json.loads(STATUS.read_text())
req(s["attempt_003"]["freeze_blob"]=="44059848fe984b2de0e06a61b8416575266fab72","status freeze binding drift")
req(s["attempt_003"]["scientific_acceptance"]=="PASS" and s["attempt_003"]["runner_terminal_pass"] is False,"status Attempt 003 disposition drift")
req(s["correction_004"]["blob"]=="2146de81c09a6c8b240e257fed09618baa1aa33f","status correction binding drift")
req(s["authorization_candidate"]["authorization_blob"]=="d5a329be6c0803c5345845746c66844db8cfb552","status Auth 004 binding drift")
req(s["authorization_candidate"]["authorization_effective_now"] is False,"status marks Auth 004 effective")
req(all(v is False for v in s["executed_now"].values()),"status records Campaign 004 execution")

# Schema 004: identity/title only.
expected_schema=copy.deepcopy(json.loads(SCHEMA3.read_text()))
expected_schema["$id"]="S6X_EVIDENCE_SCHEMA_004"
expected_schema["title"]="S6X-EAP-001 Evidence Record Corrected Runtime 004"
req(json.loads(SCHEMA4.read_text())==expected_schema,"Schema 004 changes exceed version identity")

# Runtime/validator 004 are logically identical to 003 after version normalization.
r4=RUNTIME4.read_text().replace("S6X-CANONICAL-RUNTIME-AUTH-004","S6X-CANONICAL-RUNTIME-AUTH-003")
for x4,x3 in (
("S6X_EVIDENCE_RECORDS_004.json","S6X_EVIDENCE_RECORDS_003.json"),
("S6X_GATE_OBSERVATIONS_004.csv","S6X_GATE_OBSERVATIONS_003.csv"),
("S6X_SUMMARY_004.json","S6X_SUMMARY_003.json")):
    r4=r4.replace(x4,x3)
req(r4==RUNTIME3.read_text(),"Runtime 004 scientific logic differs from 003")

v4=VALIDATOR4.read_text()
for x4,x3 in (
("S6X_GATE_OBSERVATIONS_004.csv","S6X_GATE_OBSERVATIONS_003.csv"),
("S6X_SUMMARY_004.json","S6X_SUMMARY_003.json"),
("S6X_EVIDENCE_RECORDS_004.json","S6X_EVIDENCE_RECORDS_003.json"),
("S6X_INDEPENDENT_VALIDATION_004.json","S6X_INDEPENDENT_VALIDATION_003.json"),
("S6X_RESULTS_HASH_MANIFEST_004.json","S6X_RESULTS_HASH_MANIFEST_003.json")):
    v4=v4.replace(x4,x3)
req(v4==VALIDATOR3.read_text(),"Validator 004 scientific logic differs from 003")

# Runner 004 must equal a mechanically versioned Runner 003 plus exactly one reporting-expression repair.
expected_runner=RUNNER3.read_text()
for x3,x4 in (
("S6X_CANONICAL_RUNTIME_AUTH_003.json","S6X_CANONICAL_RUNTIME_AUTH_004.json"),
("S6X_CANONICAL_EXECUTION_003","S6X_CANONICAL_EXECUTION_004"),
("run_canonical_population_003.py","run_canonical_population_004.py"),
("validate_canonical_execution_003.py","validate_canonical_execution_004.py"),
("S6X-CANONICAL-RUNTIME-AUTH-003","S6X-CANONICAL-RUNTIME-AUTH-004"),
("S6X_GATE_OBSERVATIONS_003.csv","S6X_GATE_OBSERVATIONS_004.csv"),
("S6X_SUMMARY_003.json","S6X_SUMMARY_004.json"),
("S6X_EVIDENCE_RECORDS_003.json","S6X_EVIDENCE_RECORDS_004.json"),
("S6X_INDEPENDENT_VALIDATION_003.json","S6X_INDEPENDENT_VALIDATION_004.json"),
("S6X_RESULTS_HASH_MANIFEST_003.json","S6X_RESULTS_HASH_MANIFEST_004.json")):
    expected_runner=expected_runner.replace(x3,x4)
expected_runner=expected_runner.replace('  echo "$name_sha256=$H1"','  echo "${name}_sha256=$H1"')
req(RUNNER4.read_text()==expected_runner,"Runner 004 differs beyond version bindings + single reporting repair")
runner4=RUNNER4.read_text()
req('echo "$name_sha256=$H1"' not in runner4,"unbound reporting expression retained")
req('echo "${name}_sha256=$H1"' in runner4,"correct reporting expression absent")
req("S6X_CANONICAL_EXECUTION_003" not in runner4,"Campaign 003 reuse retained")
for phrase in (
"make native_std.prep","make native_std.install","make native_std.runtest",
"run_once run1","run_once run2","observations_per_run=396","repetitions=2","total_builds=8",
"build-native_std/exe/cpu1/cf/lc.so",
"result_freeze=NO","manuscript_claim_use=NO"):
    req(phrase in runner4,f"Runner 004 control missing: {phrase}")

# Direct syntax checks for versioned executable artifacts.
subprocess.run(["bash","-n",str(RUNNER4)],cwd=ROOT,check=True)
compile(RUNTIME4.read_text(),str(RUNTIME4),"exec")
compile(VALIDATOR4.read_text(),str(VALIDATOR4),"exec")

tracked=subprocess.check_output(["git","ls-files"],cwd=ROOT,text=True).splitlines()
forbidden={
"S6X_GATE_OBSERVATIONS_004.csv",
"S6X_SUMMARY_004.json",
"S6X_EVIDENCE_RECORDS_004.json",
"S6X_INDEPENDENT_VALIDATION_004.json",
"S6X_RESULTS_HASH_MANIFEST_004.json"
}
req(not any(Path(x).name in forbidden for x in tracked),"Campaign 004 result tracked before execution")
req("python scripts/audit_paper2_s6x_attempt003_correction004.py" in WORKFLOW.read_text(),"CI hook missing")

print("paper2_s6x_attempt003_correction004_audit=PASS")
print("attempt003_failure_freeze=PASS")
print("attempt003_scientific_acceptance=PASS")
print("attempt003_runner_terminal_pass=NO")
print("correction004_scope=POST_EXECUTION_REPORTING_VARIABLE_EXPANSION_ONLY")
print("scientific_logic_changed=NO")
print("acceptance_thresholds_changed=NO")
print("runner004_bash_syntax=PASS")
print("runtime004_python_syntax=PASS")
print("validator004_python_syntax=PASS")
print("runtime_authorization_004_prepared=YES")
print("authorization_004_effective=NO_PENDING_MERGE")
print("execution_004_performed=NO")
print("result_freeze=NO")
print("canonical_output_commit=NO")
print("manuscript_claim_use=NO")
