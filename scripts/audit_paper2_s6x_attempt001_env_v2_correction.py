#!/usr/bin/env python3
from __future__ import annotations
import json, subprocess, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
FREEZE=ROOT/"study6x/S6X_EXECUTION_ATTEMPT_001_FAILURE_FREEZE.json"
PROTOCOL=ROOT/"study6x/S6X_BUILD_EXECUTION_PROTOCOL_CORRECTION_002.json"
DOCKERFILE=ROOT/"study6x/validation/S6X_BUILD_ENVIRONMENT_002.Dockerfile"
PREP=ROOT/"study6x/validation/prepare_build_environment_002.sh"
STATUS=ROOT/"publication/Paper_2_Studies_3_4_6/Post_Rejection_Rebuild/S6X_ATTEMPT001_ENV_V2_CORRECTION_STATUS.json"
REPORT=ROOT/"publication/Paper_2_Studies_3_4_6/Post_Rejection_Rebuild/S6X_ATTEMPT001_FAILURE_FREEZE_ENV_V2_CORRECTION_2026-09-29.md"
WORKFLOW=ROOT/".github/workflows/validate-research-configs.yml"

IMMUTABLE={
"study6x/S6X_BUILD_ENVIRONMENT_FREEZE_001.json":"438d31763cf7c910138ea4a83e4faaee4eca0f62",
"study6x/S6X_BUILD_EXECUTION_PROTOCOL_CANDIDATE_001.json":"8a76adf848b44753a6b5579a40b1d98f23ff94ad",
"study6x/S6X_CANONICAL_RUNTIME_AUTH_001.json":"bcf6d06fc2a6ce149e6f3596e8d1eea53cd64838",
"study6x/validation/S6X_BUILD_ENVIRONMENT_001.Dockerfile":"fb8b7fad49bdcebd7d00273b79b02553b539467e",
"study6x/validation/prepare_build_environment_001.sh":"1d251b4538a9b4130277d95f9fddd4eb42facfdf",
"study6x/validation/run_local_canonical_execution.sh":"474c7261ffec27365fe2e14924eb3a6053b6a107",
}

def req(c,m):
    if not c:
        print(f"[FAIL] {m}",file=sys.stderr)
        raise SystemExit(1)
def blob(rel):
    return subprocess.check_output(["git","hash-object",rel],cwd=ROOT,text=True).strip()

for p in (FREEZE,PROTOCOL,DOCKERFILE,PREP,STATUS,REPORT,WORKFLOW):
    req(p.is_file(),f"missing {p.relative_to(ROOT)}")
for rel,sha in IMMUTABLE.items():
    req(blob(rel)==sha,f"historical S6X record drift: {rel}")

f=json.loads(FREEZE.read_text())
req(f["attempt_id"]=="S6X-EXEC-ATTEMPT-001","attempt id drift")
req(f["status"]=="FAILED_CLOSED_PRE_SCIENTIFIC_OBSERVATION_GENERATION__TOOLING_ONLY","attempt classification drift")
req(f["author_supplied_forensic_evidence"]["clean_primary_runtest_rc"]==2,"runtest rc drift")
req(f["author_supplied_forensic_evidence"]["clean_primary_runtest_failure"]=="jq_not_found_before_ctest_execution","jq root cause drift")
req(f["author_supplied_forensic_evidence"]["canonical_gate_observations_generated"]==0,"unexpected observations")
req(f["root_cause_classification"]["scientific_failure"] is False,"scientific failure wrongly asserted")
req(f["root_cause_classification"]["environment_prerequisite_failure"] is True,"environment failure missing")
req(f["root_cause_classification"]["artifact_path_contract_failure"] is True,"artifact-path failure missing")
req(f["disposition"]["preserve_attempt_directory"] is True,"attempt preservation missing")
req(f["disposition"]["canonical_execution_001_reuse_authorized"] is False,"attempt reuse opened")
req(f["disposition"]["result_freeze_authorized"] is False,"result freeze opened")

d=DOCKERFILE.read_text()
for token in (
    "amd64/ubuntu:noble-20260911@sha256:496754492fb28b4d3049432f2ca787449331e23fb14f0dd3fffea86bf5a93eb4",
    "build-essential","ca-certificates","cmake","file","git","jq","openssl","python3"
):
    req(token in d,f"Environment 002 Dockerfile missing {token}")

prep=PREP.read_text()
for token in (
    'TAG="s6x-build-env:002"',
    'S6X_BUILD_ENVIRONMENT_002.tar',
    'S6X_BUILD_ENVIRONMENT_FREEZE_CANDIDATE_002.json',
    'printf "jq="; jq --version',
    'cfs_build_authorized=NO',
    'scientific_execution=NO'
):
    req(token in prep,f"Environment 002 prep control missing: {token}")

p=json.loads(PROTOCOL.read_text())
req(p["correction_id"]=="S6X-BUILD-EXECUTION-PROTOCOL-CORRECTION-002","protocol correction id drift")
u=p["unchanged_scientific_contract"]
req(u["planned_gate_observations_per_repetition"]==396,"population count drift")
req(u["block_a_rows"]==12 and u["block_b_rows"]==384,"block count drift")
req(u["repetitions"]==2 and u["total_builds"]==8,"repeat/build count drift")
req(u["build_commands"]==["make native_std.prep","make native_std.install","make native_std.runtest"],"build command drift")
req(p["correction_1_environment_v2"]["required_packages"].count("jq")==1,"jq correction missing")
req(p["correction_2_artifact_path"]["corrected_path"]=="build-native_std/exe/cpu1/cf/lc.so","artifact path correction drift")
req(p["attempt_and_runtime_disposition"]["canonical_execution_001"]=="DO_NOT_REUSE","attempt path reuse opened")
req(p["attempt_and_runtime_disposition"]["corrected_campaign_id_candidate"]=="S6X_CANONICAL_EXECUTION_002","new campaign id drift")
req(all(v is False for v in p["authorization"].values()),"correction PR opened execution authority")

s=json.loads(STATUS.read_text())
req(s["environment_v2_materialized"] is False,"Environment 002 materialized in correction PR")
req(s["cfs_build_executed"] is False,"cFS build recorded")
req(s["scientific_execution"] is False,"scientific execution recorded")
req(s["canonical_results_generated"] is False,"canonical results recorded")
req(s["result_freeze"] is False and s["manuscript_claim_use"] is False,"downstream authority opened")

wf=WORKFLOW.read_text()
req("python scripts/audit_paper2_s6x_attempt001_env_v2_correction.py" in wf,"CI hook missing")

print("paper2_s6x_attempt001_env_v2_correction_audit=PASS")
print("attempt001_failure_frozen=YES")
print("environment001_immutable=YES")
print("runtime_auth001_immutable=YES")
print("environment_v2_materialized=NO")
print("scientific_execution=NO")
print("result_freeze=NO")
