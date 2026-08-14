#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
IMAGE="ivvitc/nos3-64@sha256:06aa945988a7770b759022c2e1f6f2531818c087fe41a4739d3a3a7f2a9dcce2"
RUN_ID="${RUN_ID:-$(date -u +%Y%m%dT%H%M%SZ)}"
SAFE_ID="$(printf '%s' "$RUN_ID" | tr '[:upper:]' '[:lower:]' | tr -cs 'a-z0-9_.-' '-')"
NETWORK="mascr-$SAFE_ID"
CFS="mascr-$SAFE_ID-cfs"

EVIDENCE="$ROOT/results/wp5/e3/$RUN_ID"
GROUND="$EVIDENCE/immutable-ground"
OBS="$EVIDENCE/runtime-observation"
EVENT_JSON="$GROUND/event-instance.json"
APPROVED="$GROUND/approved-update.pkg"
TAMPERED="$GROUND/tampered-update.pkg"
MANIFEST="$GROUND/approved-manifest.json"
VERIFY_APPROVED="$GROUND/verify-approved.json"
VERIFY_TAMPERED="$GROUND/verify-tampered.json"
SUMMARY="$EVIDENCE/summary.json"

STAGE_VIRTUAL="/cf/mission-aware-e3-candidate.pkg"
CF_BACKING_DIR="/work/nos3/fsw/build/exe/cpu1/cf"
STAGE_BACKING="$CF_BACKING_DIR/mission-aware-e3-candidate.pkg"
NOMINAL_EVIDENCE="$ROOT/artifacts/runtime/$RUN_ID"
NOMINAL_LOG="$OBS/nominal-runtime.log"

PRE_PID=""
RESULT="RUN_INVALID"

mkdir -p "$GROUND" "$OBS"

cleanup() {
  local rc=$?
  set +e
  if docker inspect "$CFS" >/dev/null 2>&1; then
    docker exec "$CFS" rm -f "$STAGE_BACKING" >/dev/null 2>&1 || true
  fi
  if [[ -n "$PRE_PID" ]] && kill -0 "$PRE_PID" >/dev/null 2>&1; then
    kill -TERM "$PRE_PID" >/dev/null 2>&1 || true
    wait "$PRE_PID" >/dev/null 2>&1 || true
  fi
  if [[ "$RESULT" == E3_RUNTIME_ADAPTER_PASS && "$rc" -eq 0 ]]; then
    echo "WP5_E3_RUNTIME_TEST=PASS"
    echo "evidence_directory=$EVIDENCE"
  else
    echo "WP5_E3_RUNTIME_TEST=FAIL" >&2
    echo "evidence_directory=$EVIDENCE" >&2
  fi
}
trap cleanup EXIT

for cmd in docker git python3 shasum; do
  command -v "$cmd" >/dev/null || {
    echo "[ERROR] missing required command: $cmd" >&2
    exit 1
  }
done

docker info >/dev/null 2>&1
docker image inspect "$IMAGE" >/dev/null 2>&1

echo "runner_docker_daemon=PASS"
echo "runner_pinned_image=PASS"

PYTHONPATH="$ROOT" python3 - \
  "$EVENT_JSON" "$APPROVED" "$TAMPERED" "$MANIFEST" \
  "$VERIFY_APPROVED" "$VERIFY_TAMPERED" <<'PY'
import json, sys
from pathlib import Path

from src.mission_recovery.events import materialize_event
from src.mission_recovery.update_artifacts import (
    build_approved_update,
    build_manifest,
    build_tampered_update,
    verify_candidate,
)

event_path, approved_path, tampered_path, manifest_path, va_path, vt_path = map(Path, sys.argv[1:])

event=materialize_event(
    "E3",
    mission_state="M4",
    contact_condition="C0",
    evidence_condition="T0",
    seed=1,
)
approved=build_approved_update()
tampered=build_tampered_update()
manifest=build_manifest()
va=verify_candidate(approved,manifest)
vt=verify_candidate(tampered,manifest)

assert event["ground_truth"]["update_integrity_valid"] is False
assert va["accepted"] is True
assert vt["accepted"] is False
assert "sha256_mismatch" in vt["reasons"]

event_path.write_text(json.dumps(event,sort_keys=True,indent=2)+"\n",encoding="utf-8")
approved_path.write_bytes(approved)
tampered_path.write_bytes(tampered)
manifest_path.write_text(json.dumps(manifest,sort_keys=True,indent=2)+"\n",encoding="utf-8")
va_path.write_text(json.dumps(va,sort_keys=True,indent=2)+"\n",encoding="utf-8")
vt_path.write_text(json.dumps(vt,sort_keys=True,indent=2)+"\n",encoding="utf-8")

print("approved_artifact_verification=PASS")
print("tampered_artifact_rejection=PASS")
print("approved_sha256="+manifest["approved_sha256"])
print("tampered_sha256="+vt["actual_sha256"])
PY

APPROVED_SHA="$(shasum -a 256 "$APPROVED" | awk '{print $1}')"
TAMPERED_SHA="$(shasum -a 256 "$TAMPERED" | awk '{print $1}')"

test "$APPROVED_SHA" != "$TAMPERED_SHA"
echo "artifact_hash_divergence=PASS"

RUN_ID="$RUN_ID" \
DURATION_SECONDS=60 \
STARTUP_GRACE_SECONDS=20 \
bash "$ROOT/scripts/run_nominal_runtime_preflight.sh" \
  >"$NOMINAL_LOG" 2>&1 &
PRE_PID=$!

echo "nominal_runtime_launch=PASS"

CFS_READY=0
for _ in $(seq 1 180); do
  kill -0 "$PRE_PID" >/dev/null 2>&1 || break
  state="$(docker inspect "$CFS" --format '{{.State.Status}}' 2>/dev/null || echo missing)"
  if [[ "$state" == running ]]; then
    CFS_READY=1
    break
  fi
  sleep 1
done

[[ "$CFS_READY" -eq 1 ]] || {
  echo "[ERROR] nominal cFS container not observed" >&2
  tail -120 "$NOMINAL_LOG" >&2 || true
  exit 1
}
echo "nominal_cfs_running=PASS"

docker exec "$CFS" test -d "$CF_BACKING_DIR" || {
  echo "[ERROR] Linux backing directory for cFS /cf is unavailable: $CF_BACKING_DIR" >&2
  exit 1
}
echo "simulator_cf_virtual_path=$STAGE_VIRTUAL"
echo "simulator_cf_backing_dir=$CF_BACKING_DIR"
echo "simulator_cf_backing_path=PASS"

[[ "$(docker network inspect "$NETWORK" --format '{{.Internal}}')" == true ]]
[[ -z "$(docker port "$CFS")" ]]
echo "nominal_isolation=PASS"

# Control stage: approved synthetic package.
docker cp "$APPROVED" "$CFS:$STAGE_BACKING"
CONTROL_SHA="$(
  docker exec "$CFS" sha256sum "$STAGE_BACKING" |
  awk '{print $1}'
)"
test "$CONTROL_SHA" = "$APPROVED_SHA" || {
  echo "[ERROR] approved control stage hash mismatch" >&2
  exit 1
}
echo "approved_control_stage=PASS"

docker exec "$CFS" rm -f "$STAGE_BACKING"
docker exec "$CFS" test ! -e "$STAGE_BACKING"
echo "approved_control_cleanup=PASS"

# E3 event stage: same claimed version, modified bytes.
docker cp "$TAMPERED" "$CFS:$STAGE_BACKING"
EVENT_SHA="$(
  docker exec "$CFS" sha256sum "$STAGE_BACKING" |
  awk '{print $1}'
)"

test "$EVENT_SHA" = "$TAMPERED_SHA" || {
  echo "[ERROR] tampered stage does not match event artifact" >&2
  exit 1
}
test "$EVENT_SHA" != "$APPROVED_SHA" || {
  echo "[ERROR] tampered event unexpectedly matches approved hash" >&2
  exit 1
}

echo "tampered_event_stage=PASS"
echo "simulator_integrity_mismatch=PASS"

# WP5 does not activate the compromised artifact.
docker exec "$CFS" rm -f "$STAGE_BACKING"
docker exec "$CFS" test ! -e "$STAGE_BACKING"
echo "tampered_event_cleanup=PASS"
echo "update_activation_performed=false"

set +e
wait "$PRE_PID"
PRE_RC=$?
set -e
PRE_PID=""

[[ "$PRE_RC" -eq 0 ]] || {
  echo "[ERROR] nominal runtime failed after E3 staging: rc=$PRE_RC" >&2
  tail -160 "$NOMINAL_LOG" >&2 || true
  exit 1
}
grep -Fq 'NOMINAL_RUNTIME_PREFLIGHT_STATUS=PASS' "$NOMINAL_LOG"
test -f "$NOMINAL_EVIDENCE/runtime-manifest.txt"

NOMINAL_MANIFEST_SHA="$(
  shasum -a 256 "$NOMINAL_EVIDENCE/runtime-manifest.txt" |
  awk '{print $1}'
)"

python3 - \
  "$EVENT_JSON" "$MANIFEST" "$VERIFY_APPROVED" "$VERIFY_TAMPERED" \
  "$SUMMARY" "$RUN_ID" "$APPROVED_SHA" "$TAMPERED_SHA" "$CONTROL_SHA" \
  "$EVENT_SHA" "$NOMINAL_MANIFEST_SHA" <<'PY'
import hashlib, json, sys
from pathlib import Path

(event_path, manifest_path, va_path, vt_path, summary_path,
 run_id, approved_sha, tampered_sha, control_sha, event_sha, runtime_sha) = sys.argv[1:]

event=json.loads(Path(event_path).read_text(encoding="utf-8"))
manifest=json.loads(Path(manifest_path).read_text(encoding="utf-8"))
va=json.loads(Path(va_path).read_text(encoding="utf-8"))
vt=json.loads(Path(vt_path).read_text(encoding="utf-8"))

assert event["event_id"] == "E3"
assert event["ground_truth"]["update_integrity_valid"] is False
assert va["accepted"] is True
assert vt["accepted"] is False
assert "sha256_mismatch" in vt["reasons"]
assert manifest["approved_sha256"] == approved_sha == control_sha
assert tampered_sha == event_sha
assert tampered_sha != approved_sha

summary={
    "schema":1,
    "run_id":run_id,
    "classification":"WP5_E3_RUNTIME_ADAPTER_PASS",
    "scientific_claim_boundary":"artifact-compromise detection and simulator staging only; no activation or rollback-effectiveness claim",
    "event_id":"E3",
    "canonical_variant":"integrity_tamper_same_claimed_version",
    "mission_state":"M4",
    "approved_version":"2.0.0",
    "claimed_version_unchanged":True,
    "approved_sha256":approved_sha,
    "tampered_sha256":tampered_sha,
    "approved_candidate_validated":True,
    "tampered_candidate_rejected":True,
    "tampered_rejection_reasons":vt["reasons"],
    "approved_control_stage_hash_match":True,
    "tampered_event_stage_hash_match":True,
    "simulator_integrity_mismatch_observed":True,
    "simulator_virtual_stage_path":"/cf/mission-aware-e3-candidate.pkg",
    "simulator_linux_backing_stage_path":"/work/nos3/fsw/build/exe/cpu1/cf/mission-aware-e3-candidate.pkg",
    "update_activation_performed":False,
    "validated_nominal_runtime_pass":True,
    "nominal_runtime_manifest_sha256":runtime_sha,
    "operational_target":False,
    "operational_firmware":False
}
encoded=(json.dumps(summary,sort_keys=True,indent=2)+"\n").encode()
Path(summary_path).write_bytes(encoded)
print("summary_sha256="+hashlib.sha256(encoded).hexdigest())
PY

RESULT="E3_RUNTIME_ADAPTER_PASS"

echo "event_id=E3"
echo "canonical_variant=integrity_tamper_same_claimed_version"
echo "approved_candidate_validated=true"
echo "tampered_candidate_rejected=true"
echo "approved_control_stage_hash_match=true"
echo "tampered_event_stage_hash_match=true"
echo "simulator_integrity_mismatch_observed=true"
echo "update_activation_performed=false"
echo "validated_nominal_runtime_pass=true"
echo "policy_effectiveness_claim=false"
