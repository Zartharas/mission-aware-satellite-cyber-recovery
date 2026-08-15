#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
IMAGE="ivvitc/nos3-64@sha256:06aa945988a7770b759022c2e1f6f2531818c087fe41a4739d3a3a7f2a9dcce2"

RUN_ID="${RUN_ID:-$(date -u +%Y%m%dT%H%M%SZ)-wp7-trusted-recovery}"
SAFE_ID="$(printf '%s' "$RUN_ID" | tr '[:upper:]' '[:lower:]' | tr -cs 'a-z0-9_.-' '-')"

NETWORK="mascr-$SAFE_ID"
CFS="mascr-$SAFE_ID-cfs"

EVIDENCE="$ROOT/results/wp7/trusted-recovery/$RUN_ID"
GROUND="$EVIDENCE/immutable-ground"
OBS="$EVIDENCE/runtime-observation"

EVENT_JSON="$GROUND/event-instance.json"
POLICY_JSON="$GROUND/policy-decision.json"
APPROVED="$GROUND/approved-update.pkg"
TAMPERED="$GROUND/tampered-update.pkg"
MANIFEST="$GROUND/approved-manifest.json"
VERIFY_TAMPERED="$GROUND/verify-tampered.json"
ROLLBACK_REQUEST="$GROUND/rollback-request.json"
REQUEST_VALIDATION="$GROUND/rollback-request-validation.json"
PRE_TERMINAL_COPY="$GROUND/pre-recovery-candidate.pkg"
PRE_TERMINAL_VERIFY="$GROUND/pre-recovery-terminal-verification.json"
SOURCE_VERIFY="$GROUND/replacement-source-verification.json"
TERMINAL_COPY="$GROUND/terminal-recovered-candidate.pkg"
TERMINAL_VERIFY="$GROUND/terminal-recovery-verification.json"
SUMMARY="$EVIDENCE/summary.json"

CF_BACKING_DIR="/work/nos3/fsw/build/exe/cpu1/cf"
STAGE_BACKING="$CF_BACKING_DIR/mission-aware-e3-candidate.pkg"
TEMP_BACKING="$CF_BACKING_DIR/mission-aware-wp7-rollback.tmp"

NOMINAL_EVIDENCE="$ROOT/artifacts/runtime/$RUN_ID"
NOMINAL_LOG="$OBS/nominal-runtime.log"

PRE_PID=""
PHASE="PRE_RUNTIME"
RESULT="RUN_INVALID"

mkdir -p "$GROUND" "$OBS"

cleanup() {
  local rc=$?
  set +e
  if docker inspect "$CFS" >/dev/null 2>&1; then
    docker exec "$CFS" rm -f "$STAGE_BACKING" "$TEMP_BACKING" >/dev/null 2>&1 || true
  fi
  if [[ -n "$PRE_PID" ]] && kill -0 "$PRE_PID" >/dev/null 2>&1; then
    kill -TERM "$PRE_PID" >/dev/null 2>&1 || true
    wait "$PRE_PID" >/dev/null 2>&1 || true
  fi

  if [[ "$RESULT" == PASS && "$rc" -eq 0 ]]; then
    echo "WP7_TRUSTED_RECOVERY_TRIAL=PASS"
    echo "evidence_directory=$EVIDENCE"
  else
    echo "WP7_TRUSTED_RECOVERY_TRIAL=FAIL" >&2
    echo "failure_phase=$PHASE" >&2
    echo "evidence_directory=$EVIDENCE" >&2
  fi
}
trap cleanup EXIT

docker info >/dev/null 2>&1
docker image inspect "$IMAGE" >/dev/null 2>&1

PYTHONPATH="$ROOT" python3 - \
  "$EVENT_JSON" "$POLICY_JSON" "$APPROVED" "$TAMPERED" \
  "$MANIFEST" "$VERIFY_TAMPERED" "$ROLLBACK_REQUEST" <<'PY'
import json
import sys
from pathlib import Path

from src.mission_recovery.events import materialize_event
from src.mission_recovery.policies import evaluate_policy
from src.mission_recovery.rollback_requests import (
    build_verified_rollback_request,
)
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
    request_path,
)=sys.argv[1:]

event=materialize_event(
    "E3",
    mission_state="M4",
    contact_condition="C0",
    evidence_condition="T0",
    seed=1,
)
decision=evaluate_policy("P5",event)
approved=build_approved_update()
tampered=build_tampered_update()
manifest=build_manifest()
verification=verify_candidate(tampered,manifest)

assert decision["selected_action"]=="REQUEST_VERIFIED_ROLLBACK"
assert verification["accepted"] is False
assert "sha256_mismatch" in verification["reasons"]

request=build_verified_rollback_request(
    event_instance=event,
    policy_decision=decision,
    manifest=manifest,
    candidate_verification=verification,
)

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
Path(request_path).write_text(
    json.dumps(request,sort_keys=True,indent=2)+"\n",
    encoding="utf-8",
)
PY

APPROVED_SHA="$(shasum -a 256 "$APPROVED" | awk '{print $1}')"
TAMPERED_SHA="$(shasum -a 256 "$TAMPERED" | awk '{print $1}')"

test "$APPROVED_SHA" = "42945a2622fa351b3a3fdc31e002cbe326cb7a42a958ee757f317abea67b6697"
test "$TAMPERED_SHA" = "ff96d61205cc2c49b6d7d73fc36b9544c0deea79d7a9304cc1fb9f1f8986053d"

echo "approved_artifact_identity=PASS"
echo "tampered_artifact_identity=PASS"
echo "rollback_request_created=PASS"

PYTHONPATH="$ROOT" python3 - \
  "$ROLLBACK_REQUEST" "$MANIFEST" "$TAMPERED_SHA" \
  "$REQUEST_VALIDATION" <<'PY'
import json
import sys
from pathlib import Path

from src.mission_recovery.trusted_recovery import (
    validate_rollback_request,
)

request=json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
manifest=json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))

result=validate_rollback_request(
    request=request,
    manifest=manifest,
    pre_recovery_candidate_sha256=sys.argv[3],
)
assert result["accepted"] is True
assert result["reasons"]==[]

Path(sys.argv[4]).write_text(
    json.dumps(result,sort_keys=True,indent=2)+"\n",
    encoding="utf-8",
)

print("rollback_request_validation=PASS")
PY

PYTHONPATH="$ROOT" python3 - \
  "$APPROVED" "$MANIFEST" "$SOURCE_VERIFY" <<'PY'
import json
import sys
from pathlib import Path

from src.mission_recovery.trusted_recovery import (
    verify_replacement_source,
)

candidate=Path(sys.argv[1]).read_bytes()
manifest=json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))

result=verify_replacement_source(candidate,manifest)
assert result["accepted"] is True
assert result["reasons"]==[]

Path(sys.argv[3]).write_text(
    json.dumps(result,sort_keys=True,indent=2)+"\n",
    encoding="utf-8",
)

print("replacement_source_verification=PASS")
PY

RUN_ID="$RUN_ID" \
DURATION_SECONDS=60 \
STARTUP_GRACE_SECONDS=20 \
bash "$ROOT/scripts/run_nominal_runtime_preflight.sh" \
  >"$NOMINAL_LOG" 2>&1 &
PRE_PID=$!

PHASE="RUNTIME_LAUNCHED"
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

docker exec "$CFS" test -d "$CF_BACKING_DIR"
[[ "$(docker network inspect "$NETWORK" --format '{{.Internal}}')" == true ]]
[[ -z "$(docker port "$CFS")" ]]
echo "nominal_isolation=PASS"

docker exec "$CFS" rm -f "$STAGE_BACKING" "$TEMP_BACKING"
docker cp "$TAMPERED" "$CFS:$STAGE_BACKING"

STAGED_TAMPERED_SHA="$(
  docker exec "$CFS" sha256sum "$STAGE_BACKING" |
  awk '{print $1}'
)"
test "$STAGED_TAMPERED_SHA" = "$TAMPERED_SHA"

PHASE="TAMPERED_CANDIDATE_STAGED"
echo "tampered_candidate_stage=PASS"

docker cp "$CFS:$STAGE_BACKING" "$PRE_TERMINAL_COPY" >/dev/null

PYTHONPATH="$ROOT" python3 - \
  "$PRE_TERMINAL_COPY" "$MANIFEST" "$TAMPERED_SHA" \
  "$PRE_TERMINAL_VERIFY" <<'PY'
import json
import sys
from pathlib import Path

from src.mission_recovery.trusted_recovery import (
    verify_terminal_recovery,
)

candidate=Path(sys.argv[1]).read_bytes()
manifest=json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))

result=verify_terminal_recovery(
    terminal_candidate=candidate,
    manifest=manifest,
    rejected_candidate_sha256=sys.argv[3],
)

assert result["trusted_recovery_verified"] is False
assert result["terminal_matches_approved"] is False
assert result["terminal_differs_from_rejected"] is False
assert "sha256_mismatch" in result["reasons"]

Path(sys.argv[4]).write_text(
    json.dumps(result,sort_keys=True,indent=2)+"\n",
    encoding="utf-8",
)

print("pre_recovery_negative_terminal_verification=PASS")
PY

docker cp "$APPROVED" "$CFS:$TEMP_BACKING"

TEMP_SHA="$(
  docker exec "$CFS" sha256sum "$TEMP_BACKING" |
  awk '{print $1}'
)"
test "$TEMP_SHA" = "$APPROVED_SHA"

echo "verified_recovery_temp_stage=PASS"

RECOVERY_START_NS="$(python3 -c 'import time; print(time.monotonic_ns())')"

docker exec "$CFS" mv -f "$TEMP_BACKING" "$STAGE_BACKING"

PHASE="RECOVERY_REPLACEMENT_EXECUTED"
echo "atomic_recovery_replace=PASS"

docker exec "$CFS" test ! -e "$TEMP_BACKING"
TERMINAL_SHA_CONTAINER="$(
  docker exec "$CFS" sha256sum "$STAGE_BACKING" |
  awk '{print $1}'
)"
test "$TERMINAL_SHA_CONTAINER" = "$APPROVED_SHA"
test "$TERMINAL_SHA_CONTAINER" != "$TAMPERED_SHA"

docker cp "$CFS:$STAGE_BACKING" "$TERMINAL_COPY" >/dev/null

PYTHONPATH="$ROOT" python3 - \
  "$TERMINAL_COPY" "$MANIFEST" "$TAMPERED_SHA" \
  "$TERMINAL_VERIFY" <<'PY'
import json
import sys
from pathlib import Path

from src.mission_recovery.trusted_recovery import (
    verify_terminal_recovery,
)

candidate=Path(sys.argv[1]).read_bytes()
manifest=json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))

result=verify_terminal_recovery(
    terminal_candidate=candidate,
    manifest=manifest,
    rejected_candidate_sha256=sys.argv[3],
)

assert result["trusted_recovery_verified"] is True
assert result["terminal_candidate_accepted"] is True
assert result["terminal_matches_approved"] is True
assert result["terminal_differs_from_rejected"] is True
assert result["terminal_sha256"]==manifest["approved_sha256"]
assert result["reasons"]==[]

Path(sys.argv[4]).write_text(
    json.dumps(result,sort_keys=True,indent=2)+"\n",
    encoding="utf-8",
)

print("independent_terminal_verification=PASS")
print("trusted_recovery_verified=true")
PY

RECOVERY_END_NS="$(python3 -c 'import time; print(time.monotonic_ns())')"
test "$RECOVERY_END_NS" -ge "$RECOVERY_START_NS"

PHASE="TRUSTED_RECOVERY_VERIFIED"

set +e
wait "$PRE_PID"
PRE_RC=$?
set -e
PRE_PID=""

[[ "$PRE_RC" -eq 0 ]] || {
  echo "[ERROR] nominal runtime failed after recovery: rc=$PRE_RC" >&2
  tail -160 "$NOMINAL_LOG" >&2 || true
  exit 1
}

grep -Fq 'NOMINAL_RUNTIME_PREFLIGHT_STATUS=PASS' "$NOMINAL_LOG"
test -f "$NOMINAL_EVIDENCE/runtime-manifest.txt"

echo "validated_nominal_runtime_pass=true"

RUNTIME_SHA="$(
  shasum -a 256 "$NOMINAL_EVIDENCE/runtime-manifest.txt" |
  awk '{print $1}'
)"

python3 - \
  "$EVENT_JSON" "$POLICY_JSON" "$ROLLBACK_REQUEST" \
  "$REQUEST_VALIDATION" "$SOURCE_VERIFY" \
  "$PRE_TERMINAL_VERIFY" "$TERMINAL_VERIFY" "$SUMMARY" \
  "$RECOVERY_START_NS" "$RECOVERY_END_NS" "$RUNTIME_SHA" <<'PY'
import hashlib
import json
import sys
from pathlib import Path

(
    event_path,
    policy_path,
    request_path,
    request_validation_path,
    source_verify_path,
    pre_verify_path,
    terminal_verify_path,
    summary_path,
    start_ns,
    end_ns,
    runtime_sha,
)=sys.argv[1:]

event=json.loads(Path(event_path).read_text(encoding="utf-8"))
policy=json.loads(Path(policy_path).read_text(encoding="utf-8"))
request=json.loads(Path(request_path).read_text(encoding="utf-8"))
request_validation=json.loads(
    Path(request_validation_path).read_text(encoding="utf-8")
)
source_verify=json.loads(
    Path(source_verify_path).read_text(encoding="utf-8")
)
pre_verify=json.loads(
    Path(pre_verify_path).read_text(encoding="utf-8")
)
terminal=json.loads(
    Path(terminal_verify_path).read_text(encoding="utf-8")
)

start_ns=int(start_ns)
end_ns=int(end_ns)
duration_ms=(end_ns-start_ns)/1_000_000.0

assert request_validation["accepted"] is True
assert source_verify["accepted"] is True
assert pre_verify["trusted_recovery_verified"] is False
assert terminal["trusted_recovery_verified"] is True

summary={
    "schema":1,
    "classification":"WP7_TRUSTED_RECOVERY_TRIAL_PASS",
    "event_id":"E3",
    "mission_state":"M4",
    "contact_condition":"C0",
    "evidence_condition":"T0",
    "seed":1,
    "policy_id":"P5",
    "policy_action":policy["selected_action"],
    "event_instance_sha256":event["instance_sha256"],
    "decision_sha256":policy["decision_sha256"],
    "rollback_request_sha256":request["request_sha256"],
    "rollback_request_valid":True,
    "pre_recovery_candidate_rejected":True,
    "replacement_source_manifest_valid":True,
    "recovery_execution_performed":True,
    "atomic_same_filesystem_replace":True,
    "terminal_candidate_manifest_valid":True,
    "terminal_sha256":terminal["terminal_sha256"],
    "approved_target_sha256":terminal["approved_target_sha256"],
    "rejected_candidate_sha256":terminal["rejected_candidate_sha256"],
    "terminal_sha_matches_approved_target":True,
    "terminal_sha_differs_from_rejected_candidate":True,
    "recovery_temp_absent":True,
    "trusted_recovery_verified":True,
    "validated_nominal_runtime_pass":True,
    "nominal_runtime_manifest_sha256":runtime_sha,
    "time_to_trusted_recovery_ms":duration_ms,
    "timing_scope":"atomic_replace_through_independent_terminal_verification",
    "single_run_descriptive_only":True,
    "operational_firmware_activation_claim":False,
    "final_recovery_success_rate_claim":False,
    "final_time_to_trusted_recovery_effect_claim":False
}

encoded=(json.dumps(summary,sort_keys=True,indent=2)+"\n").encode()
Path(summary_path).write_bytes(encoded)

print("summary_sha256="+hashlib.sha256(encoded).hexdigest())
print(f"time_to_trusted_recovery_ms={duration_ms:.3f}")
PY

RESULT="PASS"

echo "recovery_execution_performed=true"
echo "terminal_sha_matches_approved_target=true"
echo "terminal_sha_differs_from_rejected_candidate=true"
echo "recovery_temp_absent=true"
echo "trusted_recovery_verified=true"
echo "single_run_descriptive_only=true"
echo "operational_firmware_activation_claim=false"
