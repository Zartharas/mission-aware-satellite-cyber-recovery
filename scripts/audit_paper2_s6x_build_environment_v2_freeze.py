#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
FREEZE = ROOT / "study6x/S6X_BUILD_ENVIRONMENT_FREEZE_002.json"
STATUS = ROOT / "publication/Paper_2_Studies_3_4_6/Post_Rejection_Rebuild/S6X_BUILD_ENVIRONMENT_V2_FREEZE_STATUS.json"
REPORT = ROOT / "publication/Paper_2_Studies_3_4_6/Post_Rejection_Rebuild/S6X_BUILD_ENVIRONMENT_V2_FREEZE_REVIEW_2026-09-29.md"
WORKFLOW = ROOT / ".github/workflows/validate-research-configs.yml"

EXPECTED = {
    "study6x/S6X_EXECUTION_ATTEMPT_001_FAILURE_FREEZE.json": "d381cc8ac4faf1d9ae465bbf76bed85f3353732b",
    "study6x/S6X_BUILD_EXECUTION_PROTOCOL_CORRECTION_002.json": "90b1d14e1b80d4c2d04404c46feae11ced26fb2b",
    "study6x/S6X_ENVIRONMENT_V2_MATERIALIZATION_AUTH_001.json": "c007d432bf2334a80b37e23b2dcfdf8060272d37",
    "study6x/validation/S6X_BUILD_ENVIRONMENT_002.Dockerfile": "4e3c150e03129c7e84c08a7570d04b9b883dda6b",
    "study6x/validation/prepare_build_environment_002.sh": "e729cbafbadeab7ce899cd18f5c82e2a2b7015bb",
    "publication/Paper_2_Studies_3_4_6/Post_Rejection_Rebuild/NEW_CHAT_HANDOFF_2026-09-29_S6X_ENV_V2.md": "bc385d2df53260179dd25ea865669965784dca82",
    "publication/Paper_2_Studies_3_4_6/Post_Rejection_Rebuild/S6X_ENVIRONMENT_V2_MATERIALIZATION_STATUS.json": "5c397adb9c775548db8a42a3b3e1ee6bd1649db8",
}

def fail(message: str) -> None:
    print(f"[FAIL] {message}", file=sys.stderr)
    raise SystemExit(1)

def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)

def blob(relative: str) -> str:
    return subprocess.check_output(
        ["git", "hash-object", relative],
        cwd=ROOT,
        text=True,
    ).strip()

for path in (FREEZE, STATUS, REPORT, WORKFLOW):
    require(path.is_file(), f"missing {path.relative_to(ROOT)}")

for relative, expected_sha in EXPECTED.items():
    require(blob(relative) == expected_sha, f"tracked dependency drift: {relative}")

freeze = json.loads(FREEZE.read_text(encoding="utf-8"))
require(freeze["freeze_id"] == "S6X-BUILD-ENVIRONMENT-FREEZE-002", "freeze id drift")
require(freeze["authorized_main_commit"] == "78790a85f63cbed87a199f27e41ff69672a45200", "authorized main drift")
require(freeze["environment"]["environment_id"] == "S6X-BUILD-ENVIRONMENT-002", "environment id drift")
require(freeze["environment"]["platform"] == "linux/amd64", "platform drift")
require(
    freeze["environment"]["base_image"]
    == "amd64/ubuntu:noble-20260911@sha256:496754492fb28b4d3049432f2ca787449331e23fb14f0dd3fffea86bf5a93eb4",
    "base image drift",
)
require(
    freeze["environment"]["local_image_id"]
    == "sha256:5c7549f7fdeef8198126c6759056db78d0f358afcfedb3f2e4972bfadd33674c",
    "image id drift",
)
require(
    freeze["environment"]["saved_image_tar_sha256"]
    == "fb6a35cf6499de64042da62858de93a8b3c43940fa19ec11d26012f83b5ca331",
    "image tar hash drift",
)
require(
    freeze["source_evidence"]["authorized_materialization_candidate_json_sha256"]
    == "ac22af3e11637120e3db8ba90415653cc6b052c2e53864059ab65a3506d529ed",
    "candidate json hash drift",
)
require(
    freeze["source_evidence"]["authorized_materialization_log_sha256"]
    == "dc1baac5152960abd57d8cfe4b02025ffaa9082d746268989f3d41197cf59875",
    "materialization log hash drift",
)
require(any(x == "jq=jq-1.7" for x in freeze["environment"]["tool_versions"]), "jq version missing")

for key, value in freeze["verified_negative_actions"].items():
    require(value is False, f"negative action unexpectedly true: {key}")

for key, value in freeze["authorization"].items():
    if key == "environment_identity_freeze_on_merge":
        require(value is True, "freeze-on-merge disabled")
    else:
        require(value is False, f"closed authorization unexpectedly open: {key}")

require(
    freeze["preserved_attempt_001"]["console_log_sha256"]
    == "8882e854fa150491d5948ff7e0c081f21f4323b8c7b35be2da77a51ca38173dd",
    "Attempt 001 preservation drift",
)
require(
    freeze["preserved_pre_authorization_materialization"]["image_tar_sha256"]
    == "571c32894280d3f69183c643b9461d19b8c69836371dbacfb090478cbc6bb918",
    "preauthorization materialization preservation drift",
)

status = json.loads(STATUS.read_text(encoding="utf-8"))
require(status["materialization_review"] == "PASS", "materialization review not pass")
require(status["environment_freeze_effective"] is False, "freeze prematurely effective")
require(status["runtime_authorization_002_created"] is False, "Runtime Authorization 002 created early")
for key in (
    "cfs_build",
    "fixture_applied",
    "artifact_signing",
    "independent_rebuild",
    "gate_execution",
    "scientific_execution",
    "canonical_results_generated",
    "result_freeze",
    "manuscript_claim_use",
):
    require(status[key] is False, f"closed status unexpectedly true: {key}")

tracked = subprocess.check_output(["git", "ls-files"], cwd=ROOT, text=True).splitlines()
forbidden = {
    "S6X_BUILD_ENVIRONMENT_002.tar",
    "S6X_BUILD_ENVIRONMENT_FREEZE_CANDIDATE_002.json",
    "S6X_BUILD_ENVIRONMENT_002_materialization.log",
}
require(
    not any(Path(item).name in forbidden for item in tracked),
    "local Environment-002 materialization bytes tracked",
)

workflow = WORKFLOW.read_text(encoding="utf-8")
require(
    "python scripts/audit_paper2_s6x_build_environment_v2_freeze.py" in workflow,
    "Environment-v2 freeze CI hook missing",
)

print("paper2_s6x_build_environment_v2_freeze_audit=PASS")
print("environment_v2_candidate_review=PASS")
print("environment_v2_freeze_effective=NO_PENDING_MERGE")
print("runtime_authorization_002_created=NO")
print("cfs_build_authorized=NO")
print("scientific_execution_authorized=NO")
