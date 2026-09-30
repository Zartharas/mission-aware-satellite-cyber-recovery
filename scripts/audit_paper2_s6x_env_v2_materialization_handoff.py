#!/usr/bin/env python3
from __future__ import annotations
import json, subprocess, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
AUTH=ROOT/"study6x/S6X_ENVIRONMENT_V2_MATERIALIZATION_AUTH_001.json"
STATUS=ROOT/"publication/Paper_2_Studies_3_4_6/Post_Rejection_Rebuild/S6X_ENVIRONMENT_V2_MATERIALIZATION_STATUS.json"
HANDOFF=ROOT/"publication/Paper_2_Studies_3_4_6/Post_Rejection_Rebuild/NEW_CHAT_HANDOFF_2026-09-29_S6X_ENV_V2.md"
CURRENT=ROOT/"docs/CURRENT_PUBLICATION_STATE.md"
WORKFLOW=ROOT/".github/workflows/validate-research-configs.yml"

BOUND={
"study6x/S6X_EXECUTION_ATTEMPT_001_FAILURE_FREEZE.json":"d381cc8ac4faf1d9ae465bbf76bed85f3353732b",
"study6x/S6X_BUILD_EXECUTION_PROTOCOL_CORRECTION_002.json":"90b1d14e1b80d4c2d04404c46feae11ced26fb2b",
"study6x/validation/S6X_BUILD_ENVIRONMENT_002.Dockerfile":"4e3c150e03129c7e84c08a7570d04b9b883dda6b",
"study6x/validation/prepare_build_environment_002.sh":"e729cbafbadeab7ce899cd18f5c82e2a2b7015bb",
}

def req(c,m):
    if not c:
        print(f"[FAIL] {m}",file=sys.stderr)
        raise SystemExit(1)
def blob(rel):
    return subprocess.check_output(["git","hash-object",rel],cwd=ROOT,text=True).strip()

for p in (AUTH,STATUS,HANDOFF,CURRENT,WORKFLOW):
    req(p.is_file(),f"missing {p.relative_to(ROOT)}")
for rel,sha in BOUND.items():
    req(blob(rel)==sha,f"bound S6X correction drift: {rel}")

a=json.loads(AUTH.read_text())
req(a["authorization_id"]=="S6X-ENVIRONMENT-V2-MATERIALIZATION-AUTH-001","authorization id drift")
req(a["author_approval"]["approved"] is True,"author approval missing")
scope=a["authorized_scope"]
for k in ("local_environment_002_docker_build","save_environment_002_image_tar","compute_environment_002_tar_sha256","capture_environment_002_image_id","capture_tool_versions_including_jq","verify_linux_amd64"):
    req(scope[k] is True,f"materialization scope closed: {k}")
for k in ("cfs_build","fixture_application","artifact_signing","provenance_generation","independent_rebuild","gate_execution","scientific_execution","result_freeze","manuscript_claim_use","figure_revision","study6_s6x_pooling","venue_lock"):
    req(scope[k] is False,f"prohibited scope opened: {k}")

s=json.loads(STATUS.read_text())
req(s["environment_v2_materialization_authorized"] is True,"materialization not authorized")
req(s["environment_v2_materialized"] is False,"environment recorded materialized before local output")
req(s["environment_v2_frozen"] is False,"environment frozen before review")
req(s["cfs_build_executed"] is False and s["scientific_execution"] is False,"execution recorded early")
req(s["result_freeze"] is False and s["manuscript_claim_use"] is False,"downstream authority opened")

h=HANDOFF.read_text()
for token in (
    "AUTHOR_REVIEW_AFTER_S6X_ENVIRONMENT_V2_LOCAL_MATERIALIZATION_BEFORE_FREEZE_PR",
    "prepare_build_environment_002.sh",
    "S6X_BUILD_ENVIRONMENT_FREEZE_CANDIDATE_002.json",
    "S6X_CANONICAL_EXECUTION_001",
    "Do not build cFS",
    "S6X_CANONICAL_EXECUTION_002",
):
    req(token in h,f"handoff missing {token}")

c=CURRENT.read_text()
req("S6X Environment 002 local materialization is authorized" in c,"current publication state not updated")
req("scientific execution remains closed" in c,"scientific-execution boundary missing")

req("python scripts/audit_paper2_s6x_env_v2_materialization_handoff.py" in WORKFLOW.read_text(),"CI hook missing")

tracked=subprocess.check_output(["git","ls-files"],cwd=ROOT,text=True).splitlines()
forbidden={"S6X_BUILD_ENVIRONMENT_002.tar","S6X_BUILD_ENVIRONMENT_FREEZE_CANDIDATE_002.json"}
req(not any(Path(x).name in forbidden for x in tracked),"local Environment 002 output tracked prematurely")

print("paper2_s6x_env_v2_materialization_handoff_audit=PASS")
print("environment_v2_materialization_authorized=YES")
print("environment_v2_materialized=NO")
print("cfs_build_executed=NO")
print("scientific_execution=NO")
print("result_freeze=NO")
