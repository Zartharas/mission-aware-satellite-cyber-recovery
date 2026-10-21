#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
FREEZE=ROOT/"study6x/S6X_BUILD_ENVIRONMENT_FREEZE_001.json"
STATUS=ROOT/"publication/Paper_2_Studies_3_4_6/Post_Rejection_Rebuild/S6X_BUILD_ENVIRONMENT_FREEZE_STATUS.json"
REPORT=ROOT/"publication/Paper_2_Studies_3_4_6/Post_Rejection_Rebuild/S6X_BUILD_ENVIRONMENT_FREEZE_REVIEW_2026-09-29.md"
WORKFLOW=ROOT/".github/workflows/validate-research-configs.yml"

EXPECTED={
"study6x/S6X_BUILD_EXECUTION_PROTOCOL_CANDIDATE_001.json":"8a76adf848b44753a6b5579a40b1d98f23ff94ad",
"study6x/validation/S6X_BUILD_ENVIRONMENT_001.Dockerfile":"fb8b7fad49bdcebd7d00273b79b02553b539467e",
"study6x/validation/prepare_build_environment_001.sh":"1d251b4538a9b4130277d95f9fddd4eb42facfdf",
"study6x/validation/closeout_pre_runtime_validation.sh":"bbbf3a0bad33b7a7318a52545ef0c63aceef5708",
}

def fail(m): print(f"[FAIL] {m}",file=sys.stderr); raise SystemExit(1)
def require(c,m):
    if not c: fail(m)
def blob(rel):
    return subprocess.check_output(["git","hash-object",rel],cwd=ROOT,text=True).strip()

for p in (FREEZE,STATUS,REPORT,WORKFLOW): require(p.is_file(),f"missing {p.relative_to(ROOT)}")
for rel,sha in EXPECTED.items(): require(blob(rel)==sha,f"tracked dependency drift: {rel}")

f=json.loads(FREEZE.read_text())
require(f["freeze_id"]=="S6X-BUILD-ENVIRONMENT-FREEZE-001","freeze id drift")
require(f["environment"]["platform"]=="linux/amd64","platform drift")
require(f["environment"]["base_image"]=="amd64/ubuntu:noble-20260911@sha256:496754492fb28b4d3049432f2ca787449331e23fb14f0dd3fffea86bf5a93eb4","base image drift")
require(f["environment"]["local_image_id"]=="sha256:3877a5c519fff5266cc4d34e43ac90f6430320851928f42906c79ecd58f7bb43","image id drift")
require(f["environment"]["saved_image_tar_sha256"]=="7b043f3c330fa992a119996f43f83d8d3c6621650933460bb8f71c587ddeb21d","image tar hash drift")
for k,v in f["verified_negative_actions"].items(): require(v is False,f"negative action unexpectedly true: {k}")
for k,v in f["authorization"].items():
    if k=="environment_identity_freeze_on_merge": require(v is True,"freeze-on-merge disabled")
    else: require(v is False,f"closed authorization unexpectedly open: {k}")

s=json.loads(STATUS.read_text())
require(s["environment_candidate_review"]=="PASS","candidate review not pass")
require(s["environment_freeze_effective"] is False,"freeze prematurely effective")
require(s["cfs_build"] is False,"cfs build opened")
require(s["scientific_execution"] is False,"scientific execution opened")

wf=WORKFLOW.read_text()
require("python scripts/audit_paper2_s6x_build_environment_freeze.py" in wf,"CI hook missing")

print("paper2_s6x_build_environment_freeze_audit=PASS")
print("environment_candidate_review=PASS")
print("environment_freeze_effective=NO_PENDING_MERGE")
print("cfs_build_authorized=NO")
print("scientific_execution_authorized=NO")
