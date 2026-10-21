#!/usr/bin/env python3
from __future__ import annotations
import copy
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
FREEZE=ROOT/"study6x/S6X_EXECUTION_ATTEMPT_002_FAILURE_FREEZE.json"
CORRECTION=ROOT/"study6x/S6X_BUILD_EXECUTION_PROTOCOL_CORRECTION_003.json"
AUTH=ROOT/"study6x/S6X_CANONICAL_RUNTIME_AUTH_003.json"
STATUS=ROOT/"publication/Paper_2_Studies_3_4_6/Post_Rejection_Rebuild/S6X_ATTEMPT002_FAILURE_FREEZE_CORRECTION_003_STATUS.json"
SCHEMA2=ROOT/"study6x/S6X_EVIDENCE_SCHEMA_002.json"
SCHEMA3=ROOT/"study6x/S6X_EVIDENCE_SCHEMA_003.json"
RUNTIME2=ROOT/"study6x/runtime/run_canonical_population_002.py"
RUNTIME3=ROOT/"study6x/runtime/run_canonical_population_003.py"
VALIDATOR2=ROOT/"study6x/audit/validate_canonical_execution_002.py"
VALIDATOR3=ROOT/"study6x/audit/validate_canonical_execution_003.py"
RUNNER2=ROOT/"study6x/validation/run_local_canonical_execution_002.sh"
RUNNER3=ROOT/"study6x/validation/run_local_canonical_execution_003.sh"
WORKFLOW=ROOT/".github/workflows/validate-research-configs.yml"

EXPECTED={
"study6x/S6X_CANONICAL_RUNTIME_AUTH_002.json":"a7bdaf9b177e644ed7e932c5723507c264c0277a",
"study6x/validation/run_local_canonical_execution_002.sh":"abe58d12e764b104709de0b14d0b257f7480db4f",
"study6x/S6X_BUILD_ENVIRONMENT_FREEZE_002.json":"235d7524f254ae3ad0ff6a4f331be59aceb3aaed",
"study6x/S6X_SOURCE_PIN.json":"2af7cb503c3cf8715d31341d731df0533fabfa29",
"study6x/fixtures/S6X_FIXTURE_GT_EQ_BOUNDARY_001.patch":"e3189e5a06ff47a2cf68bb7d343c563a300dc313",
"study6x/fixtures/S6X_INVARIANT_HARNESS_EQUALITY_001.patch":"b3318be396a6c4e5c98f2339846d9ea59bcd5def",
"study6x/src/invariant_oracle.py":"70b555cec84cb455c72094c6539df3873662182d",
"study6x/runtime/gate_evaluator.py":"c6045b249daa6a3ff3b2ff54982b047c299fd04c",
"study6x/audit/reference_gate_evaluator.py":"c3834f478196fe3fd3e9290ff0ecc603a0933247",
"study6x/S6X_EVIDENCE_SCHEMA_002.json":"84e75f623db3ced5061afad7919a76e9680d7efe",
"study6x/runtime/run_canonical_population_002.py":"7f520d1f42a5ccf9dd5690a816eb1cd9709bb1f2",
"study6x/audit/validate_canonical_execution_002.py":"2eafb0080dc0e2b418bf70700e90cb6ea9ae63e8",
"study6x/S6X_EXECUTION_ATTEMPT_002_FAILURE_FREEZE.json":"7608fb45151850e4d07709a26a5daa1f70b00ccc",
"study6x/S6X_BUILD_EXECUTION_PROTOCOL_CORRECTION_003.json":"35271a7e5aa672e63072c4b228dc321cca6f1826",
"study6x/S6X_EVIDENCE_SCHEMA_003.json":"768298234860a886b919af6449cec026478e7e81",
"study6x/runtime/run_canonical_population_003.py":"aa998b3fd50b76d9f2f9c95db28ca90adced8209",
"study6x/audit/validate_canonical_execution_003.py":"da55bb1d807494addff10759dd99921e3e51ecff",
"study6x/validation/run_local_canonical_execution_003.sh":"3f3379cedcdbd89b1fd3f2eb793e7522dfbd0283",
"study6x/S6X_CANONICAL_RUNTIME_AUTH_003.json":"b5399dce4f671733e0637e19965e0a6a6605ee78",
"publication/Paper_2_Studies_3_4_6/Post_Rejection_Rebuild/S6X_ATTEMPT002_FAILURE_FREEZE_CORRECTION_003_STATUS.json":"7a4a5d26cd38ada3e417b6c8106ee1c8ae24d557"
}

def fail(m):
    print(f"[FAIL] {m}",file=sys.stderr)
    raise SystemExit(1)
def req(c,m):
    if not c: fail(m)
def blob(rel):
    return subprocess.check_output(["git","hash-object",rel],cwd=ROOT,text=True).strip()

for p in (FREEZE,CORRECTION,AUTH,STATUS,SCHEMA2,SCHEMA3,RUNTIME2,RUNTIME3,VALIDATOR2,VALIDATOR3,RUNNER2,RUNNER3,WORKFLOW):
    req(p.is_file(),f"missing {p.relative_to(ROOT)}")
for rel,sha in EXPECTED.items():
    req(blob(rel)==sha,f"bound drift: {rel}")

f=json.loads(FREEZE.read_text())
req(f["attempt_id"]=="S6X-EXEC-ATTEMPT-002","attempt id drift")
req(f["status"]=="FAILED_CLOSED_PRE_SCIENTIFIC_OBSERVATION_GENERATION__RUNNER_STDOUT_HASH_CAPTURE_CONTROL_DEFECT","attempt status drift")
e=f["author_supplied_forensic_evidence"]
req(e["console_log_sha256"]=="71c2a8ffb6d2d3657611e0310229938e051a453983877be69a7e65047eb36d3b","console binding drift")
req(e["signature_file_count"]==0 and e["canonical_result_file_count"]==0 and e["run2_started"] is False,"execution boundary drift")
req(e["run1_build_workspaces_completed"]==4,"build workspace count drift")
req(e["clean_primary_artifact_sha256"]==e["clean_rebuild_artifact_sha256"]=="7311d8d1b89ffe2ca0e43ca1e2f6430db28d2f9532ebf426c4870ab5847f1670","clean reproducibility evidence drift")
req(e["bad_primary_artifact_sha256"]==e["bad_rebuild_artifact_sha256"]=="275ae69dc92dd60f023d203664ab5fda021b46100a58d1f670a8546dd57f031c","bad reproducibility evidence drift")
req(e["clean_primary_artifact_sha256"]!=e["bad_primary_artifact_sha256"],"clean/bad distinction drift")
req(e["clean_primary_runtest_rc"]==0 and e["clean_rebuild_runtest_rc"]==0,"clean runtest evidence drift")
req(e["bad_primary_runtest_rc"]==2 and e["bad_rebuild_runtest_rc"]==2,"bad runtest evidence drift")
r=f["root_cause_classification"]
req(r["artifact_reproducibility_failure"] is False and r["runner_control_failure"] is True and r["stdout_hash_capture_contamination"] is True,"root cause classification drift")
d=f["disposition"]
req(d["delete_or_reuse_attempt_directory"] is False and d["canonical_execution_002_reuse_authorized"] is False,"Attempt 002 reuse opened")
req(d["result_freeze_authorized"] is False and d["manuscript_claim_use_authorized"] is False,"Attempt 002 claims opened")

c=json.loads(CORRECTION.read_text())
req(c["correction_id"]=="S6X-BUILD-EXECUTION-PROTOCOL-CORRECTION-003","correction id drift")
req(c["attempt_002_failure_freeze"]["blob"]=="7608fb45151850e4d07709a26a5daa1f70b00ccc","freeze binding drift")
req(c["root_cause"]["artifact_reproducibility_failure"] is False and c["root_cause"]["scientific_acceptance_failure"] is False,"false scientific failure classification")
cc=c["correction"]
req(cc["digest_transport"]=="DEDICATED_SHA256_FILES","digest transport drift")
req(cc["digest_validation_regex"]=="^[0-9a-f]{64}$","digest regex drift")
req(cc["build_stdout_stderr_transport"]=="DEDICATED_PER_BUILD_LOG_FILE","build log transport drift")
req(cc["command_substitution_of_build_one_removed"] is True,"stdout capture defect not removed")
req(cc["exact_artifact_sha256_comparisons_preserved"] is True,"SHA acceptance weakened")
req(cc["build_commands_changed"] is False and cc["source_or_fixture_changed"] is False and cc["environment_changed"] is False and cc["artifact_path_changed"] is False and cc["scientific_logic_changed"] is False,"correction exceeds runner control boundary")
u=c["unchanged_scientific_contract"]
req(u["planned_gate_observations_per_repetition"]==396 and u["block_a_rows"]==12 and u["block_b_rows"]==384,"population changed")
req(u["repetitions"]==2 and u["builds_per_repetition"]==4 and u["total_builds"]==8,"build plan changed")
req(u["build_commands"]==["make native_std.prep","make native_std.install","make native_std.runtest"],"build commands changed")
req(u["clean_primary_rebuild_sha256_match_required"] is True and u["bad_primary_rebuild_sha256_match_required"] is True and u["clean_bad_artifact_sha256_must_differ"] is True,"artifact acceptance changed")
req(u["required_gate_mismatches"]==0 and u["repeated_scientific_output_hash_mismatches_allowed"]==0,"mismatch allowance changed")
req(all(v is False for v in c["authorization"].values()),"Correction 003 authorizes execution")

a=json.loads(AUTH.read_text())
req(a["authorization_id"]=="S6X-CANONICAL-RUNTIME-AUTH-003","auth id drift")
req(a["supersedes_runtime_authorization_id"]=="S6X-CANONICAL-RUNTIME-AUTH-002","auth supersession drift")
req(a["status"]=="PREPARED_ON_FEATURE_BRANCH__NOT_EFFECTIVE","Auth 003 effective early")
req(a["predecessor"]["attempt_002_failure_freeze_blob"]=="7608fb45151850e4d07709a26a5daa1f70b00ccc","Auth 003 freeze binding drift")
req(a["predecessor"]["protocol_correction_blob"]=="35271a7e5aa672e63072c4b228dc321cca6f1826","Auth 003 correction binding drift")
b=a["frozen_bindings"]
req(b["evidence_schema_003_blob"]=="768298234860a886b919af6449cec026478e7e81" and b["runtime_population_generator_003_blob"]=="aa998b3fd50b76d9f2f9c95db28ca90adced8209" and b["independent_validator_003_blob"]=="da55bb1d807494addff10759dd99921e3e51ecff" and b["runtime_runner_003_blob"]=="3f3379cedcdbd89b1fd3f2eb793e7522dfbd0283","Auth 003 versioned runtime binding drift")
scope=a["authorization_scope"]
for k in ("frozen_environment_use_authorized","recursive_pinned_submodule_materialization_authorized","cfs_build_authorized","semantic_fixture_application_to_build_authorized","research_only_artifact_signing_authorized","provenance_observation_generation_authorized","independent_rebuild_authorized","qualification_gate_execution_authorized","scientific_execution_authorized","independent_reference_validation_authorized","deterministic_repeat_execution_authorized"):
    req(scope[k] is True,f"authorized scope closed: {k}")
for k in ("result_freeze_authorized","canonical_output_commit_authorized","manuscript_claim_use_authorized","figure_revision_authorized","study6_modification_authorized","study6_s6x_pooling_authorized","venue_lock_authorized"):
    req(scope[k] is False,f"prohibited scope open: {k}")
rc=a["runtime_constraints"]
req(rc["campaign_root"]=="study6x/workspace/S6X_CANONICAL_EXECUTION_003","campaign id drift")
req(rc["artifact_digest_transport"]=="DEDICATED_SHA256_FILES" and rc["artifact_digest_regex"]=="^[0-9a-f]{64}$","Auth 003 digest transport drift")
req(rc["build_stdout_stderr_transport"]=="DEDICATED_PER_BUILD_LOG_FILE","Auth 003 log transport drift")
req(rc["artifact_path"]=="build-native_std/exe/cpu1/cf/lc.so","artifact path drift")
req(rc["repetitions"]==2 and rc["builds_per_repetition"]==4 and rc["total_builds"]==8,"Auth 003 build plan drift")
req(rc["expected_gate_observations_per_repetition"]==396 and rc["expected_block_a_rows"]==12 and rc["expected_block_b_rows"]==384,"Auth 003 population drift")
req(a["scientific_acceptance"]["clean_primary_rebuild_sha256_match_required"] is True,"clean SHA acceptance weakened")
req(a["scientific_acceptance"]["bad_primary_rebuild_sha256_match_required"] is True,"bad SHA acceptance weakened")
req(a["scientific_acceptance"]["clean_bad_artifact_sha256_must_differ"] is True,"clean/bad distinction weakened")
req(a["scientific_acceptance"]["primary_reference_gate_mismatches_allowed"]==0 and a["scientific_acceptance"]["repeated_scientific_output_hash_mismatches_allowed"]==0,"mismatch allowance changed")
req(all(v is False for v in a["execution_state_at_record_creation"].values()),"Auth 003 records execution early")
req(a["effectivity"]["record_effective_only_when_tracked_on_main"] is True and a["effectivity"]["post_merge_ci_required_before_execution"] is True and a["effectivity"]["actual_runtime_execution_requires_explicit_post_merge_author_instruction"] is True,"Auth 003 effectivity gate weakened")

s=json.loads(STATUS.read_text())
req(s["attempt_002"]["freeze_blob"]=="7608fb45151850e4d07709a26a5daa1f70b00ccc","status freeze binding drift")
req(s["correction_003"]["blob"]=="35271a7e5aa672e63072c4b228dc321cca6f1826","status correction binding drift")
req(s["authorization_candidate"]["authorization_blob"]=="b5399dce4f671733e0637e19965e0a6a6605ee78","status auth binding drift")
req(s["authorization_candidate"]["authorization_effective_now"] is False,"status marks Auth 003 effective")
req(s["correction_003"]["scientific_logic_changed"] is False and s["correction_003"]["acceptance_thresholds_changed"] is False,"status marks scientific change")
req(all(v is False for v in s["executed_now"].values()),"status records Execution 003")

# Schema 003 changes only version identity/title relative to Schema 002.
expected_schema=copy.deepcopy(json.loads(SCHEMA2.read_text()))
expected_schema["$id"]="S6X_EVIDENCE_SCHEMA_003"
expected_schema["title"]="S6X-EAP-001 Evidence Record Corrected Runtime 003"
req(json.loads(SCHEMA3.read_text())==expected_schema,"schema 003 changes exceed version identity")

# Runtime 003 and validator 003 are scientifically identical to 002 after version-token normalization.
r3=RUNTIME3.read_text().replace("S6X-CANONICAL-RUNTIME-AUTH-003","S6X-CANONICAL-RUNTIME-AUTH-002")
for x3,x2 in (
("S6X_EVIDENCE_RECORDS_003.json","S6X_EVIDENCE_RECORDS_002.json"),
("S6X_GATE_OBSERVATIONS_003.csv","S6X_GATE_OBSERVATIONS_002.csv"),
("S6X_SUMMARY_003.json","S6X_SUMMARY_002.json")):
    r3=r3.replace(x3,x2)
req(r3==RUNTIME2.read_text(),"runtime 003 scientific logic differs from 002")

v3=VALIDATOR3.read_text()
for x3,x2 in (
("S6X_GATE_OBSERVATIONS_003.csv","S6X_GATE_OBSERVATIONS_002.csv"),
("S6X_SUMMARY_003.json","S6X_SUMMARY_002.json"),
("S6X_EVIDENCE_RECORDS_003.json","S6X_EVIDENCE_RECORDS_002.json"),
("S6X_INDEPENDENT_VALIDATION_003.json","S6X_INDEPENDENT_VALIDATION_002.json"),
("S6X_RESULTS_HASH_MANIFEST_003.json","S6X_RESULTS_HASH_MANIFEST_002.json")):
    v3=v3.replace(x3,x2)
req(v3==VALIDATOR2.read_text(),"validator 003 scientific logic differs from 002")

runner2=RUNNER2.read_text()
runner3=RUNNER3.read_text()
req('CLEAN_PRIMARY="$(build_one' in runner2 and 'BAD_PRIMARY="$(build_one' in runner2,"predecessor defect signature missing")
req('CLEAN_PRIMARY="$(build_one' not in runner3 and 'BAD_PRIMARY="$(build_one' not in runner3,"stdout-capture defect retained in runner 003")
for phrase in (
'S6X_CANONICAL_RUNTIME_AUTH_003.json',
'S6X_CANONICAL_EXECUTION_003',
'run_canonical_population_003.py',
'validate_canonical_execution_003.py',
'build-native_std/exe/cpu1/cf/lc.so',
'make native_std.prep',
'make native_std.install',
'make native_std.runtest',
'run_once run1',
'run_once run2',
'observations_per_run=396',
'repetitions=2',
'total_builds=8',
'build_stdout_stderr.log',
'^[0-9a-f]{64}$',
'result_freeze=NO',
'manuscript_claim_use=NO'):
    req(phrase in runner3,f"runner 003 control missing: {phrase}")
req('printf \'%s\\n\' "$digest" > "$hash_out"' in runner3,"digest-only file transport missing")
req('CLEAN_PRIMARY="$(cat "$runroot/hashes/clean_primary.sha256")"' in runner3,"clean primary digest file read missing")
req('BAD_REBUILD="$(cat "$runroot/hashes/bad_rebuild.sha256")"' in runner3,"bad rebuild digest file read missing")
req("S6X_CANONICAL_EXECUTION_002" not in runner3,"Attempt 002 campaign reuse retained")
req("build-native_std/exe/cpu1/lc.so" not in runner3,"obsolete artifact path restored")

tracked=subprocess.check_output(["git","ls-files"],cwd=ROOT,text=True).splitlines()
forbidden={
"S6X_GATE_OBSERVATIONS_003.csv",
"S6X_SUMMARY_003.json",
"S6X_EVIDENCE_RECORDS_003.json",
"S6X_INDEPENDENT_VALIDATION_003.json",
"S6X_RESULTS_HASH_MANIFEST_003.json"
}
req(not any(Path(x).name in forbidden for x in tracked),"Execution 003 result tracked before execution")
req("python scripts/audit_paper2_s6x_attempt002_correction003.py" in WORKFLOW.read_text(),"CI hook missing")

# Direct syntax gates for versioned executable artifacts outside the generic CI scan roots.
subprocess.run(["bash","-n",str(RUNNER3)],cwd=ROOT,check=True)
compile(RUNTIME3.read_text(),str(RUNTIME3),"exec")
compile(VALIDATOR3.read_text(),str(VALIDATOR3),"exec")

print("runner003_bash_syntax=PASS")
print("runtime003_python_syntax=PASS")
print("validator003_python_syntax=PASS")
print("paper2_s6x_attempt002_correction003_audit=PASS")
print("attempt002_failure_freeze=PASS")
print("attempt002_artifact_reproducibility=PASS")
print("attempt002_canonical_observations=0")
print("correction003_scope=RUNNER_HASH_CHANNEL_ISOLATION_ONLY")
print("scientific_logic_changed=NO")
print("acceptance_thresholds_changed=NO")
print("runtime_authorization_003_prepared=YES")
print("authorization_003_effective=NO_PENDING_MERGE")
print("execution_003_performed=NO")
print("result_freeze=NO")
print("manuscript_claim_use=NO")
