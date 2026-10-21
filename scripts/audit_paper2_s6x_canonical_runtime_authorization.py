#!/usr/bin/env python3
from __future__ import annotations
import json, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
AUTH=ROOT/"study6x/S6X_CANONICAL_RUNTIME_AUTH_001.json"
STATUS=ROOT/"publication/Paper_2_Studies_3_4_6/Post_Rejection_Rebuild/S6X_CANONICAL_RUNTIME_AUTHORIZATION_STATUS.json"
RUNNER=ROOT/"study6x/validation/run_local_canonical_execution.sh"
PRIMARY=ROOT/"study6x/runtime/gate_evaluator.py"; REFERENCE=ROOT/"study6x/audit/reference_gate_evaluator.py"
RUNTIME=ROOT/"study6x/runtime/run_canonical_population.py"; VALIDATOR=ROOT/"study6x/audit/validate_canonical_execution.py"
WORKFLOW=ROOT/".github/workflows/validate-research-configs.yml"
EXPECTED={
"study6x/S6X_BUILD_EXECUTION_PROTOCOL_CANDIDATE_001.json":"8a76adf848b44753a6b5579a40b1d98f23ff94ad",
"study6x/S6X_BUILD_ENVIRONMENT_FREEZE_001.json":"438d31763cf7c910138ea4a83e4faaee4eca0f62",
"study6x/S6X_SOURCE_PIN.json":"2af7cb503c3cf8715d31341d731df0533fabfa29",
"study6x/S6X_EVIDENCE_SCHEMA_CANDIDATE_001.json":"4bb8ebff2607046645235aeef115116fb30dd125",
"study6x/fixtures/S6X_FIXTURE_GT_EQ_BOUNDARY_001.patch":"e3189e5a06ff47a2cf68bb7d343c563a300dc313",
"study6x/fixtures/S6X_INVARIANT_HARNESS_EQUALITY_001.patch":"b3318be396a6c4e5c98f2339846d9ea59bcd5def"}
def req(c,m):
    if not c: print(f"[FAIL] {m}",file=sys.stderr); raise SystemExit(1)
def blob(rel): return subprocess.check_output(["git","hash-object",rel],cwd=ROOT,text=True).strip()
for p in (AUTH,STATUS,RUNNER,PRIMARY,REFERENCE,RUNTIME,VALIDATOR,WORKFLOW): req(p.is_file(),f"missing {p.relative_to(ROOT)}")
for rel,sha in EXPECTED.items(): req(blob(rel)==sha,f"bound drift: {rel}")
a=json.loads(AUTH.read_text()); req(a["authorization_id"]=="S6X-CANONICAL-RUNTIME-AUTH-001","auth id drift")
req(a["status"]=="PREPARED_ON_FEATURE_BRANCH__NOT_EFFECTIVE","auth state drift")
req(a["predecessor"]["environment_freeze_post_merge_ci_run_number"]==1296,"CI binding drift")
req(a["predecessor"]["environment_freeze_post_merge_ci_conclusion"]=="success","CI conclusion drift")
scope=a["authorization_scope"]
for k in ("frozen_environment_use_authorized","cfs_build_authorized","semantic_fixture_application_to_build_authorized","research_only_artifact_signing_authorized","provenance_observation_generation_authorized","independent_rebuild_authorized","qualification_gate_execution_authorized","scientific_execution_authorized","independent_reference_validation_authorized","deterministic_repeat_execution_authorized"): req(scope[k] is True,f"authorized scope closed: {k}")
for k in ("result_freeze_authorized","canonical_output_commit_authorized","manuscript_claim_use_authorized","figure_revision_authorized","study6_modification_authorized","study6_s6x_pooling_authorized","venue_lock_authorized"): req(scope[k] is False,f"prohibited scope open: {k}")
c=a["runtime_constraints"]; req(c["repetitions"]==2 and c["total_builds"]==8,"repeat/build drift")
req(c["expected_gate_observations_per_repetition"]==396,"observation drift")
req(all(v is False for v in a["execution_state_at_record_creation"].values()),"execution recorded early")
s=json.loads(STATUS.read_text()); req(s["authorization_candidate"]["authorization_effective_now"] is False,"effective before merge")
req(all(v is False for v in s["executed_now"].values()),"status records execution")
runner=RUNNER.read_text()
for phrase in ('if [ "$(git branch --show-current)" != "main" ]',"7b043f3c330fa992a119996f43f83d8d3c6621650933460bb8f71c587ddeb21d","run_once run1","run_once run2","total_builds=8","observations_per_run=396","result_freeze=NO","manuscript_claim_use=NO"): req(phrase in runner,f"runner control missing: {phrase}")
tracked=subprocess.check_output(["git","ls-files"],cwd=ROOT,text=True).splitlines()
forbidden={"S6X_GATE_OBSERVATIONS_001.csv","S6X_SUMMARY_001.json","S6X_EVIDENCE_RECORDS_001.json","S6X_INDEPENDENT_VALIDATION_001.json","S6X_RESULTS_HASH_MANIFEST_001.json"}
req(not any(Path(x).name in forbidden for x in tracked),"scientific result tracked before execution")
req("python scripts/audit_paper2_s6x_canonical_runtime_authorization.py" in WORKFLOW.read_text(),"CI hook missing")
print("paper2_s6x_canonical_runtime_authorization_audit=PASS")
print("authorization_prepared=YES"); print("authorization_effective=NO")
print("scientific_execution_performed=NO"); print("result_freeze=NO"); print("manuscript_claim_use=NO")
