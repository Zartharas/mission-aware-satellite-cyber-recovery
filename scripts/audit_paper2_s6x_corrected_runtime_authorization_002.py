#!/usr/bin/env python3
from __future__ import annotations
import copy
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
AUTH=ROOT/"study6x/S6X_CANONICAL_RUNTIME_AUTH_002.json"
STATUS=ROOT/"publication/Paper_2_Studies_3_4_6/Post_Rejection_Rebuild/S6X_CANONICAL_RUNTIME_AUTHORIZATION_002_STATUS.json"
SCHEMA1=ROOT/"study6x/S6X_EVIDENCE_SCHEMA_CANDIDATE_001.json"
SCHEMA2=ROOT/"study6x/S6X_EVIDENCE_SCHEMA_002.json"
RUNTIME1=ROOT/"study6x/runtime/run_canonical_population.py"
RUNTIME2=ROOT/"study6x/runtime/run_canonical_population_002.py"
VALIDATOR1=ROOT/"study6x/audit/validate_canonical_execution.py"
VALIDATOR2=ROOT/"study6x/audit/validate_canonical_execution_002.py"
RUNNER1=ROOT/"study6x/validation/run_local_canonical_execution.sh"
RUNNER2=ROOT/"study6x/validation/run_local_canonical_execution_002.sh"
WORKFLOW=ROOT/".github/workflows/validate-research-configs.yml"

EXPECTED={
"study6x/S6X_CANONICAL_RUNTIME_AUTH_001.json":"bcf6d06fc2a6ce149e6f3596e8d1eea53cd64838",
"study6x/S6X_BUILD_EXECUTION_PROTOCOL_CORRECTION_002.json":"90b1d14e1b80d4c2d04404c46feae11ced26fb2b",
"study6x/S6X_BUILD_ENVIRONMENT_FREEZE_002.json":"235d7524f254ae3ad0ff6a4f331be59aceb3aaed",
"study6x/S6X_SOURCE_PIN.json":"2af7cb503c3cf8715d31341d731df0533fabfa29",
"study6x/S6X_EVIDENCE_SCHEMA_CANDIDATE_001.json":"4bb8ebff2607046645235aeef115116fb30dd125",
"study6x/runtime/run_canonical_population.py":"ea1cd0ea2034d7c94bcc6e236e44c235c48970b0",
"study6x/audit/validate_canonical_execution.py":"e91777ebf07a3b6987d5a5d6937532f5ae40e251",
"study6x/validation/run_local_canonical_execution.sh":"474c7261ffec27365fe2e14924eb3a6053b6a107",
"study6x/runtime/gate_evaluator.py":"c6045b249daa6a3ff3b2ff54982b047c299fd04c",
"study6x/audit/reference_gate_evaluator.py":"c3834f478196fe3fd3e9290ff0ecc603a0933247",
"study6x/fixtures/S6X_FIXTURE_GT_EQ_BOUNDARY_001.patch":"e3189e5a06ff47a2cf68bb7d343c563a300dc313",
"study6x/fixtures/S6X_INVARIANT_HARNESS_EQUALITY_001.patch":"b3318be396a6c4e5c98f2339846d9ea59bcd5def",
"study6x/src/invariant_oracle.py":"70b555cec84cb455c72094c6539df3873662182d",
"study6x/S6X_EVIDENCE_SCHEMA_002.json":"84e75f623db3ced5061afad7919a76e9680d7efe",
"study6x/runtime/run_canonical_population_002.py":"7f520d1f42a5ccf9dd5690a816eb1cd9709bb1f2",
"study6x/audit/validate_canonical_execution_002.py":"2eafb0080dc0e2b418bf70700e90cb6ea9ae63e8",
"study6x/validation/run_local_canonical_execution_002.sh":"abe58d12e764b104709de0b14d0b257f7480db4f",
"study6x/S6X_CANONICAL_RUNTIME_AUTH_002.json":"a7bdaf9b177e644ed7e932c5723507c264c0277a",
"publication/Paper_2_Studies_3_4_6/Post_Rejection_Rebuild/S6X_CANONICAL_RUNTIME_AUTHORIZATION_002_STATUS.json":"23efe881903ba7b9b26a8ccc1d451db0bf6faa3e"
}

def fail(m):
    print(f"[FAIL] {m}",file=sys.stderr)
    raise SystemExit(1)
def req(c,m):
    if not c: fail(m)
def blob(rel):
    return subprocess.check_output(["git","hash-object",rel],cwd=ROOT,text=True).strip()

for p in (AUTH,STATUS,SCHEMA1,SCHEMA2,RUNTIME1,RUNTIME2,VALIDATOR1,VALIDATOR2,RUNNER1,RUNNER2,WORKFLOW):
    req(p.is_file(),f"missing {p.relative_to(ROOT)}")
for rel,sha in EXPECTED.items():
    req(blob(rel)==sha,f"bound drift: {rel}")

a=json.loads(AUTH.read_text())
req(a["authorization_id"]=="S6X-CANONICAL-RUNTIME-AUTH-002","auth id drift")
req(a["supersedes_runtime_authorization_id"]=="S6X-CANONICAL-RUNTIME-AUTH-001","supersession drift")
req(a["status"]=="PREPARED_ON_FEATURE_BRANCH__NOT_EFFECTIVE","auth state drift")
p=a["predecessor"]
req(p["environment_freeze_merge_commit"]=="8f58b198b12886387130757476632193f5821fc2","freeze merge binding drift")
req(p["environment_freeze_post_merge_ci_run_number"]==1305,"post-merge CI number drift")
req(p["environment_freeze_post_merge_ci_run_id"]==36655074056,"post-merge CI id drift")
req(p["environment_freeze_post_merge_ci_conclusion"]=="success","post-merge CI conclusion drift")
b=a["frozen_bindings"]
req(b["build_environment_freeze_002_blob"]=="235d7524f254ae3ad0ff6a4f331be59aceb3aaed","freeze blob binding drift")
req(b["evidence_schema_002_blob"]=="84e75f623db3ced5061afad7919a76e9680d7efe","schema blob binding drift")
req(b["runtime_population_generator_002_blob"]=="7f520d1f42a5ccf9dd5690a816eb1cd9709bb1f2","runtime blob binding drift")
req(b["independent_validator_002_blob"]=="2eafb0080dc0e2b418bf70700e90cb6ea9ae63e8","validator blob binding drift")
req(b["runtime_runner_002_blob"]=="abe58d12e764b104709de0b14d0b257f7480db4f","runner blob binding drift")
req(b["environment_image_id"]=="sha256:5c7549f7fdeef8198126c6759056db78d0f358afcfedb3f2e4972bfadd33674c","image binding drift")
req(b["environment_tar_sha256"]=="fb6a35cf6499de64042da62858de93a8b3c43940fa19ec11d26012f83b5ca331","tar binding drift")

scope=a["authorization_scope"]
for k in ("frozen_environment_use_authorized","recursive_pinned_submodule_materialization_authorized","cfs_build_authorized","semantic_fixture_application_to_build_authorized","research_only_artifact_signing_authorized","provenance_observation_generation_authorized","independent_rebuild_authorized","qualification_gate_execution_authorized","scientific_execution_authorized","independent_reference_validation_authorized","deterministic_repeat_execution_authorized"):
    req(scope[k] is True,f"authorized scope closed: {k}")
for k in ("result_freeze_authorized","canonical_output_commit_authorized","manuscript_claim_use_authorized","figure_revision_authorized","study6_modification_authorized","study6_s6x_pooling_authorized","venue_lock_authorized"):
    req(scope[k] is False,f"prohibited scope open: {k}")

c=a["runtime_constraints"]
req(c["environment_tar"]=="study6x/workspace/S6X_ENVIRONMENT_V2_MATERIALIZATION_002/S6X_BUILD_ENVIRONMENT_002.tar","environment tar path drift")
req(c["environment_tag"]=="s6x-build-env:002","environment tag drift")
req(c["campaign_root"]=="study6x/workspace/S6X_CANONICAL_EXECUTION_002","campaign id drift")
req(c["artifact_path"]=="build-native_std/exe/cpu1/cf/lc.so","corrected artifact path drift")
req(c["repetitions"]==2 and c["builds_per_repetition"]==4 and c["total_builds"]==8,"repeat/build drift")
req(c["expected_gate_observations_per_repetition"]==396 and c["expected_block_a_rows"]==12 and c["expected_block_b_rows"]==384,"population count drift")
req(a["scientific_acceptance"]["primary_reference_gate_mismatches_allowed"]==0,"gate mismatch allowance drift")
req(a["scientific_acceptance"]["repeated_scientific_output_hash_mismatches_allowed"]==0,"repeat mismatch allowance drift")
req(all(v is False for v in a["execution_state_at_record_creation"].values()),"execution recorded early")
req(a["effectivity"]["actual_runtime_execution_requires_explicit_post_merge_author_instruction"] is True,"explicit execution gate removed")

s=json.loads(STATUS.read_text())
req(s["predecessor"]["environment_freeze_governance_effective"] is True,"merged freeze not recognized")
req(s["authorization_candidate"]["authorization_effective_now"] is False,"authorization effective before merge")
req(s["versioned_runtime_artifacts"]["scientific_logic_changed"] is False,"scientific logic marked changed")
req(all(v is False for v in s["executed_now"].values()),"status records execution")

# Schema 002 must be Schema 001 with only identity/title/corrected artifact path changes.
expected_schema=copy.deepcopy(json.loads(SCHEMA1.read_text()))
expected_schema["$id"]="S6X_EVIDENCE_SCHEMA_002"
expected_schema["title"]="S6X-EAP-001 Evidence Record Corrected Runtime 002"
expected_schema["properties"]["artifact"]["properties"]["path"]["const"]="build-native_std/exe/cpu1/cf/lc.so"
req(json.loads(SCHEMA2.read_text())==expected_schema,"schema v2 changes exceed authorized operational correction")

# Runtime generator and validator must be logically identical after version-token normalization.
r2=RUNTIME2.read_text()
r2=r2.replace("S6X-CANONICAL-RUNTIME-AUTH-002","S6X-CANONICAL-RUNTIME-AUTH-001")
for a2,a1 in (
("S6X_EVIDENCE_RECORDS_002.json","S6X_EVIDENCE_RECORDS_001.json"),
("S6X_GATE_OBSERVATIONS_002.csv","S6X_GATE_OBSERVATIONS_001.csv"),
("S6X_SUMMARY_002.json","S6X_SUMMARY_001.json")):
    r2=r2.replace(a2,a1)
req(r2==RUNTIME1.read_text(),"runtime v2 scientific logic differs from v1")

v2=VALIDATOR2.read_text()
for a2,a1 in (
("S6X_GATE_OBSERVATIONS_002.csv","S6X_GATE_OBSERVATIONS_001.csv"),
("S6X_SUMMARY_002.json","S6X_SUMMARY_001.json"),
("S6X_EVIDENCE_RECORDS_002.json","S6X_EVIDENCE_RECORDS_001.json"),
("S6X_INDEPENDENT_VALIDATION_002.json","S6X_INDEPENDENT_VALIDATION_001.json"),
("S6X_RESULTS_HASH_MANIFEST_002.json","S6X_RESULTS_HASH_MANIFEST_001.json")):
    v2=v2.replace(a2,a1)
req(v2==VALIDATOR1.read_text(),"validator v2 scientific logic differs from v1")

runner=RUNNER2.read_text()
for phrase in (
'S6X_CANONICAL_RUNTIME_AUTH_002.json',
'S6X_ENVIRONMENT_V2_MATERIALIZATION_002/S6X_BUILD_ENVIRONMENT_002.tar',
'S6X_CANONICAL_EXECUTION_002',
'sha256:5c7549f7fdeef8198126c6759056db78d0f358afcfedb3f2e4972bfadd33674c',
'fb6a35cf6499de64042da62858de93a8b3c43940fa19ec11d26012f83b5ca331',
's6x-build-env:002',
'build-native_std/exe/cpu1/cf/lc.so',
'make native_std.prep',
'make native_std.install',
'make native_std.runtest',
'run_once run1',
'run_once run2',
'observations_per_run=396',
'repetitions=2',
'total_builds=8',
'result_freeze=NO',
'manuscript_claim_use=NO'):
    req(phrase in runner,f"runner control missing: {phrase}")
req("build-native_std/exe/cpu1/lc.so" not in runner,"obsolete artifact path retained in corrected runner")
req("S6X_CANONICAL_EXECUTION_001" not in runner,"Attempt 001 campaign reuse retained in corrected runner")

tracked=subprocess.check_output(["git","ls-files"],cwd=ROOT,text=True).splitlines()
forbidden={
"S6X_GATE_OBSERVATIONS_002.csv",
"S6X_SUMMARY_002.json",
"S6X_EVIDENCE_RECORDS_002.json",
"S6X_INDEPENDENT_VALIDATION_002.json",
"S6X_RESULTS_HASH_MANIFEST_002.json"
}
req(not any(Path(x).name in forbidden for x in tracked),"scientific result tracked before execution")
req("python scripts/audit_paper2_s6x_corrected_runtime_authorization_002.py" in WORKFLOW.read_text(),"CI hook missing")

print("paper2_s6x_corrected_runtime_authorization_002_audit=PASS")
print("environment_freeze_002_effective=YES")
print("corrected_runtime_authorization_002_prepared=YES")
print("authorization_effective=NO_PENDING_MERGE")
print("scientific_logic_changed=NO")
print("cfs_build_performed=NO")
print("scientific_execution_performed=NO")
print("result_freeze=NO")
print("manuscript_claim_use=NO")
