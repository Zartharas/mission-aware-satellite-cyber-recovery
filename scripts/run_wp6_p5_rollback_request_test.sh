#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
IMAGE="ivvitc/nos3-64@sha256:06aa945988a7770b759022c2e1f6f2531818c087fe41a4739d3a3a7f2a9dcce2"

POLICY_ID="${POLICY_ID:?POLICY_ID must be P0 or P5}"
case "$POLICY_ID" in
  P0|P5) ;;
  *) echo "[ERROR] unsupported POLICY_ID=$POLICY_ID" >&2; exit 1 ;;
esac

RUN_ID="${RUN_ID:-$(date -u +%Y%m%dT%H%M%SZ)-wp6-$POLICY_ID-p5}"
SAFE_ID="$(printf '%s' "$RUN_ID" | tr '[:upper:]' '[:lower:]' | tr -cs 'a-z0-9_.-' '-')"

NETWORK="mascr-$SAFE_ID"
CFS="mascr-$SAFE_ID-cfs"

EVIDENCE="$ROOT/results/wp6/p5/$RUN_ID"
GROUND="$EVIDENCE/immutable-ground"
OBS="$EVIDENCE/runtime-observation"

EVENT_JSON="$GROUND/event-instance.json"
POLICY_JSON="$GROUND/policy-decision.json"
APPROVED="$GROUND/approved-update.pkg"
TAMPERED="$GROUND/tampered-update.pkg"
MANIFEST="$GROUND/approved-manifest.json"
VERIFY_TAMPERED="$GROUND/verify-tampered.json"
ROLLBACK_REQUEST="$GROUND/rollback-request.json"
SUMMARY="$EVIDENCE/summary.json"

STAGE_VIRTUAL="/cf/mission-aware-e3-candidate.pkg"
CF_BACKING_DIR="/work/nos3/fsw/build/exe/cpu1/cf"
STAGE_BACKING="$CF_BACKING_DIR/mission-aware-e3-candidate.pkg"
ROLLBACK_BACKING="$CF_BACKING_DIR/mission-aware-p5-rollback.pkg"

NOMINAL_EVIDENCE="$ROOT/artifacts/runtime/$RUN_ID"
NOMINAL_LOG="$OBS/nominal-runtime.log"

PRE_PID=""
RESULT="RUN_INVALID"

mkdir -p "$GROUND" "$OBS"

cleanup() {
  local rc=$?
  set +e
  if docker inspect "$CFS" >/dev/null 2>&1; then
    docker exec "$CFS" rm -f "$STAGE_BACKING" "$ROLLBACK_BACKING" >/dev/null 2>&1 || true
  fi
  if [[ -n "$PRE_PID" ]] && kill -0 "$PRE_PID" >/dev/null 2>&1; then
    kill -TERM "$PRE_PID" >/dev/null 2>&1 || true
    wait "$PRE_PID" >/dev/null 2>&1 || true
  fi
  if [[ "$RESULT" == PASS && "$rc" -eq 0 ]]; then
    echo "WP6_P5_POLICY_EFFECT_TRIAL=PASS"
    echo "policy_id=$POLICY_ID"
    echo "evidence_directory=$EVIDENCE"
  else
    echo "WP6_P5_POLICY_EFFECT_TRIAL=FAIL" >&2
    echo "policy_id=$POLICY_ID" >&2
    echo "evidence_directory=$EVIDENCE" >&2
  fi
}
trap cleanup EXIT

docker info >/dev/null 2>&1
docker image inspect "$IMAGE" >/dev/null 2>&1

PYTHONPATH="$ROOT" python3 - \
  "$EVENT_JSON" "$POLICY_JSON" "$APPROVED" "$TAMPERED" \
  "$MANIFEST" "$VERIFY_TAMPERED" "$POLICY_ID" <<'PY'
import json, sys
from pathlib import Path

from src.mission_recovery.events import materialize_event
from src.mission_recovery.policies import evaluate_policy
from src.mission_recovery.update_artifacts import (
    build_approved_update,
    build_manifest,
    build_tampered_update,
    verify_candidate,
)

(
    event_path,
    policy_path,
    approved_path,
    tampered_path,
    manifest_path,
    verify_path,
    policy_id,
)=sys.argv[1:]

event=materialize_event(
    "E3",
    mission_state="M4",
    contact_condition="C0",
    evidence_condition="T0",
    seed=1,
)
decision=evaluate_policy(policy_id,event)
approved=build_approved_update()
tampered=build_tampered_update()
manifest=build_manifest()
verification=verify_candidate(tampered,manifest)

assert event["policy_visible_evidence"]["integrity_check_passed"] is False
assert event["policy_visible_evidence"]["rollback_available"] is True
assert verification["accepted"] is False
assert "sha256_mismatch" in verification["reasons"]

Path(event_path).write_text(
    json.dumps(event,sort_keys=True,indent=2)+"\n",
    encoding="utf-8",
)
Path(policy_path).write_text(
    json.dumps(decision,sort_keys=True,indent=2)+"\n",
    encoding="utf-8",
)
Path(approved_path).write_bytes(approved)
Path(tampered_path).write_bytes(tampered)
Path(manifest_path).write_text(
    json.dumps(manifest,sort_keys=True,indent=2)+"\n",
    encoding="utf-8",
)
Path(verify_path).write_text(
    json.dumps(verification,sort_keys=True,indent=2)+"\n",
    encoding="utf-8",
)
PY

ACTION="$(
python3 - "$POLICY_JSON" <<'PY'
import json, sys
from pathlib import Path
print(json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))["selected_action"])
PY
)"

case "$POLICY_ID:$ACTION" in
  P0:OBSERVE_ONLY|P5:REQUEST_VERIFIED_ROLLBACK) ;;
  *)
    echo "[ERROR] unexpected policy action: $POLICY_ID -> $ACTION" >&2
    exit 1
    ;;
esac

echo "policy_decision=PASS"
echo "policy_id=$POLICY_ID"
echo "policy_action=$ACTION"

APPROVED_SHA="$(shasum -a 256 "$APPROVED" | awk '{print $1}')"
TAMPERED_SHA="$(shasum -a 256 "$TAMPERED" | awk '{print $1}')"

test "$APPROVED_SHA" = "42945a2622fa351b3a3fdc31e002cbe326cb7a42a958ee757f317abea67b6697"
test "$TAMPERED_SHA" = "ff96d61205cc2c49b6d7d73fc36b9544c0deea79d7a9304cc1fb9f1f8986053d"

echo "approved_artifact_identity=PASS"
echo "tampered_artifact_identity=PASS"

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
  echo "[ERROR] cFS backing directory unavailable" >&2
  exit 1
}

[[ "$(docker network inspect "$NETWORK" --format '{{.Internal}}')" == true ]]
[[ -z "$(docker port "$CFS")" ]]
echo "nominal_isolation=PASS"

docker exec "$CFS" rm -f "$STAGE_BACKING" "$ROLLBACK_BACKING"
docker exec "$CFS" test ! -e "$STAGE_BACKING"
docker exec "$CFS" test ! -e "$ROLLBACK_BACKING"

docker cp "$TAMPERED" "$CFS:$STAGE_BACKING"

STAGED_SHA="$(
  docker exec "$CFS" sha256sum "$STAGE_BACKING" |
  awk '{print $1}'
)"
test "$STAGED_SHA" = "$TAMPERED_SHA" || {
  echo "[ERROR] staged candidate hash mismatch" >&2
  exit 1
}

echo "tampered_candidate_stage=PASS"
echo "simulator_virtual_stage_path=$STAGE_VIRTUAL"

if [[ "$POLICY_ID" == P5 ]]; then
  PYTHONPATH="$ROOT" python3 - \
    "$EVENT_JSON" "$POLICY_JSON" "$MANIFEST" "$VERIFY_TAMPERED" \
    "$ROLLBACK_REQUEST" <<'PY'
import json, sys
from pathlib import Path

from src.mission_recovery.rollback_requests import (
    build_verified_rollback_request,
)

event=json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
decision=json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
manifest=json.loads(Path(sys.argv[3]).read_text(encoding="utf-8"))
verification=json.loads(Path(sys.argv[4]).read_text(encoding="utf-8"))

request=build_verified_rollback_request(
    event_instance=event,
    policy_decision=decision,
    manifest=manifest,
    candidate_verification=verification,
)

Path(sys.argv[5]).write_text(
    json.dumps(request,sort_keys=True,indent=2)+"\n",
    encoding="utf-8",
)

print("rollback_request_sha256="+request["request_sha256"])
PY

  test -f "$ROLLBACK_REQUEST"
  echo "rollback_request_created=true"
else
  test ! -e "$ROLLBACK_REQUEST"
  echo "rollback_request_created=false"
fi

# WP6 stops at the request boundary.
STAGED_SHA_AFTER="$(
  docker exec "$CFS" sha256sum "$STAGE_BACKING" |
  awk '{print $1}'
)"
test "$STAGED_SHA_AFTER" = "$TAMPERED_SHA"

docker exec "$CFS" test ! -e "$ROLLBACK_BACKING"

echo "tampered_candidate_remains_staged=true"
echo "approved_rollback_staged=false"
echo "rollback_activation_performed=false"
echo "recovery_execution_performed=false"
echo "trusted_recovery_verified=false"

if [[ "$POLICY_ID" == P5 ]]; then
  python3 - "$ROLLBACK_REQUEST" "$APPROVED_SHA" "$TAMPERED_SHA" <<'PY'
import json, sys
from pathlib import Path

request=json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))

assert request["action"]=="REQUEST_VERIFIED_ROLLBACK"
assert request["approved_target_sha256"]==sys.argv[2]
assert request["rejected_candidate_sha256"]==sys.argv[3]
assert request["request_ready"] is True
assert request["rollback_staging_performed"] is False
assert request["rollback_activation_performed"] is False
assert request["recovery_execution_performed"] is False
assert request["trusted_recovery_verified"] is False
assert request["oracle_ground_truth_read"] is False

print("rollback_request_approved_target_binding=PASS")
print("rollback_request_rejected_candidate_binding=PASS")
print("rollback_request_oracle_guard=PASS")
PY
fi

set +e
wait "$PRE_PID"
PRE_RC=$?
set -e
PRE_PID=""

[[ "$PRE_RC" -eq 0 ]] || {
  echo "[ERROR] nominal runtime failed: rc=$PRE_RC" >&2
  tail -160 "$NOMINAL_LOG" >&2 || true
  exit 1
}

grep -Fq 'NOMINAL_RUNTIME_PREFLIGHT_STATUS=PASS' "$NOMINAL_LOG"
test -f "$NOMINAL_EVIDENCE/runtime-manifest.txt"

RUNTIME_SHA="$(
  shasum -a 256 "$NOMINAL_EVIDENCE/runtime-manifest.txt" |
  awk '{print $1}'
)"

REQUEST_SHA=""
if [[ "$POLICY_ID" == P5 ]]; then
  REQUEST_SHA="$(shasum -a 256 "$ROLLBACK_REQUEST" | awk '{print $1}')"
fi

python3 - \
  "$EVENT_JSON" "$POLICY_JSON" "$SUMMARY" "$POLICY_ID" \
  "$APPROVED_SHA" "$TAMPERED_SHA" "$STAGED_SHA_AFTER" \
  "$RUNTIME_SHA" "$REQUEST_SHA" <<'PY'
import hashlib, json, sys
from pathlib import Path

(
    event_path,
    policy_path,
    summary_path,
    policy_id,
    approved_sha,
    tampered_sha,
    staged_sha_after,
    runtime_sha,
    request_file_sha,
)=sys.argv[1:]

event=json.loads(Path(event_path).read_text(encoding="utf-8"))
decision=json.loads(Path(policy_path).read_text(encoding="utf-8"))

assert staged_sha_after==tampered_sha
request_created=policy_id=="P5"

summary={
    "schema":1,
    "classification":"WP6_P5_POLICY_EFFECT_TRIAL_PASS",
    "policy_id":policy_id,
    "policy_action":decision["selected_action"],
    "event_id":"E3",
    "mission_state":"M4",
    "contact_condition":"C0",
    "evidence_condition":"T0",
    "seed":1,
    "event_instance_sha256":event["instance_sha256"],
    "decision_sha256":decision["decision_sha256"],
    "approved_target_sha256":approved_sha,
    "tampered_candidate_sha256":tampered_sha,
    "tampered_candidate_staged":True,
    "tampered_candidate_remains_staged":True,
    "rollback_request_created":request_created,
    "rollback_request_file_sha256":request_file_sha or None,
    "approved_rollback_staged":False,
    "rollback_activation_performed":False,
    "recovery_execution_performed":False,
    "trusted_recovery_verified":False,
    "validated_nominal_runtime_pass":True,
    "nominal_runtime_manifest_sha256":runtime_sha,
    "oracle_ground_truth_read":False,
    "recovery_success_claim":False,
    "time_to_trusted_recovery_claim":False
}
encoded=(json.dumps(summary,sort_keys=True,indent=2)+"\n").encode()
Path(summary_path).write_bytes(encoded)
print("summary_sha256="+hashlib.sha256(encoded).hexdigest())
PY

RESULT="PASS"

echo "validated_nominal_runtime_pass=true"
echo "oracle_ground_truth_read=false"
echo "recovery_success_claim=false"
echo "time_to_trusted_recovery_claim=false"
