#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
IMAGE="ivvitc/nos3-64@sha256:06aa945988a7770b759022c2e1f6f2531818c087fe41a4739d3a3a7f2a9dcce2"

if [[ "$#" -ne 2 ]]; then
  echo "usage: $0 <R01-R04> <development-seed>" >&2
  exit 2
fi

CELL_ID="$1"
DEVELOPMENT_SEED="$2"
CELL_SAFE="$(printf '%s' "$CELL_ID" | tr '[:upper:]' '[:lower:]')"
RUN_ID="${RUN_ID:-$(date -u +%Y%m%dT%H%M%SZ)-wp8-recovery-${CELL_SAFE}-dev}"
SAFE_ID="$(printf '%s' "$RUN_ID" | tr '[:upper:]' '[:lower:]' | tr -cs 'a-z0-9_.-' '-')"
NETWORK="mascr-$SAFE_ID"
CFS="mascr-$SAFE_ID-cfs"
GATEWAY="mascr-$SAFE_ID-recovery-gateway"

EVIDENCE="$ROOT/results/wp8/runtime-binding/recovery-executor-development/$RUN_ID"
GROUND="$EVIDENCE/immutable-ground"
OBS="$EVIDENCE/runtime-observation"
PLAN_JSON="$GROUND/execution-plan.json"
FACTOR_JSON="$GROUND/factor-context.json"
EVENT_JSON="$GROUND/event-instance.json"
POLICY_JSON="$GROUND/runtime-policy-decision.json"
APPROVED="$GROUND/approved-update.pkg"
TAMPERED="$GROUND/tampered-update.pkg"
MANIFEST="$GROUND/approved-manifest.json"
VERIFY_TAMPERED="$GROUND/verify-tampered.json"
ROLLBACK_JSON="$GROUND/rollback-preparation.json"
NOOP_JSON="$GROUND/authorized-noop-probe.json"
POST_SLOT_JSON="$GROUND/post-response-slot.json"
SCOPE_JSON="$GROUND/development-evidence-scope.json"
MEASUREMENT_JSON="$GROUND/recovery-runtime-measurement.json"
RAW_JSON="$GROUND/recovery-runtime-observation-raw.json"
DERIVED_JSON="$GROUND/recovery-runtime-observation-derived.json"
INVALID_JSON="$EVIDENCE/development-run-invalid.json"
INGRESS_JSONL="$GROUND/gateway-ingress.jsonl"
DECISION_JSONL="$GROUND/gateway-decisions.jsonl"
EVENT_SUCCESS_NS_FILE="$OBS/event-success-monotonic-ns.txt"
EVENT_SLOT_SHA_FILE="$OBS/event-slot-sha256.txt"
EVENT_WATCH_LOG="$OBS/event-slot-watcher.log"
NOMINAL_LOG="$OBS/nominal-runtime.log"

CF_BACKING_DIR="/work/nos3/fsw/build/exe/cpu1/cf"
STAGE_BACKING="$CF_BACKING_DIR/mission-aware-e3-candidate.pkg"
TEMP_BACKING="$CF_BACKING_DIR/mission-aware-wp8-rollback.tmp"
PILOT_CONFIG="$ROOT/configs/wp8_pilot_design.json"

PRE_PID=""
EVENT_WATCH_PID=""
RESULT="RUN_INVALID"
PHASE="INITIALIZATION"

mono_ns() { python3 -c 'import time; print(time.monotonic_ns())'; }
count_reset_marker() { docker logs "$CFS" 2>&1 | grep -Fc 'SAMPLE: RESET counters command received' || true; }
count_noop_marker() { docker logs "$CFS" 2>&1 | grep -Fc 'SAMPLE: NOOP command received' || true; }

decision_count() {
  python3 - "$DECISION_JSONL" <<'PY'
import sys
from pathlib import Path
p=Path(sys.argv[1])
print(0 if not p.exists() else sum(1 for x in p.read_text(encoding="utf-8").splitlines() if x.strip()))
PY
}

wait_decisions() {
  local expected="$1" now
  for _ in $(seq 1 75); do
    now="$(decision_count)"
    [[ "$now" -eq "$expected" ]] && return 0
    [[ "$now" -gt "$expected" ]] && return 2
    sleep 0.2
  done
  return 1
}

wait_noop_delta() {
  local before="$1" now
  for _ in $(seq 1 75); do
    now="$(count_noop_marker)"
    [[ "$now" -eq $((before + 1)) ]] && return 0
    [[ "$now" -gt $((before + 1)) ]] && return 2
    sleep 0.2
  done
  return 1
}

emit_invalid() {
  local rc="$1"
  [[ -d "$EVIDENCE" ]] || return 0
  [[ -f "$INVALID_JSON" ]] && return 0
  python3 - "$INVALID_JSON" "$RUN_ID" "$CELL_ID" "$DEVELOPMENT_SEED" "$PHASE" "$rc" "${REPO_COMMIT:-unknown}" <<'PY'
import json,sys
from pathlib import Path
p,run_id,cell,seed,phase,rc,commit=sys.argv[1:]
Path(p).write_text(json.dumps({
    "schema":1,
    "classification":"WP8_RECOVERY_EXECUTOR_DEVELOPMENT_RUN_INVALID",
    "run_id":run_id,
    "cell_id":cell,
    "development_seed":int(seed),
    "failed_phase":phase,
    "exit_code":int(rc),
    "repo_commit":commit,
    "development_preflight":True,
    "pilot_data":False,
    "pilot_seed_consumed":False,
    "runtime_binding_performed":False,
    "fabricated_primary_metrics":False,
},sort_keys=True,indent=2)+"\n",encoding="utf-8")
PY
}

cleanup() {
  local rc=$?
  set +e
  docker rm -f "$GATEWAY" >/dev/null 2>&1 || true
  if docker inspect "$CFS" >/dev/null 2>&1; then
    docker exec "$CFS" rm -f "$STAGE_BACKING" "$TEMP_BACKING" >/dev/null 2>&1 || true
  fi
  if [[ -n "$EVENT_WATCH_PID" ]] && kill -0 "$EVENT_WATCH_PID" >/dev/null 2>&1; then
    kill -TERM "$EVENT_WATCH_PID" >/dev/null 2>&1 || true
    wait "$EVENT_WATCH_PID" >/dev/null 2>&1 || true
  fi
  if [[ -n "$PRE_PID" ]] && kill -0 "$PRE_PID" >/dev/null 2>&1; then
    kill -TERM "$PRE_PID" >/dev/null 2>&1 || true
    wait "$PRE_PID" >/dev/null 2>&1 || true
  fi
  if [[ "$RESULT" == "PASS" && "$rc" -eq 0 ]]; then
    echo "WP8_RECOVERY_STAGE1_DEVELOPMENT_EXECUTOR=PASS"
    echo "development_preflight=true"
    echo "pilot_data=false"
    echo "pilot_seed_consumed=false"
    echo "runtime_binding_performed=false"
    echo "primary_metrics_emitted=false"
    echo "terminal_state_emitted=false"
    echo "evidence_directory=$EVIDENCE"
  else
    emit_invalid "$rc" || true
    echo "WP8_RECOVERY_STAGE1_DEVELOPMENT_EXECUTOR=FAIL" >&2
    echo "failed_phase=$PHASE" >&2
    echo "evidence_directory=$EVIDENCE" >&2
  fi
}
trap cleanup EXIT
trap 'exit 130' INT TERM

cd "$ROOT"
test -z "$(git status --short)" || {
  echo "[ERROR] repository worktree must be clean before development runtime" >&2
  exit 1
}

for command in docker git python3 shasum; do
  command -v "$command" >/dev/null 2>&1 || exit 1
done
docker info >/dev/null 2>&1
docker image inspect "$IMAGE" >/dev/null 2>&1
REPO_COMMIT="$(git rev-parse HEAD)"

mkdir -p "$GROUND" "$OBS"
: > "$INGRESS_JSONL"
: > "$DECISION_JSONL"

PHASE="DEVELOPMENT_PLAN_PREFLIGHT"
PYTHONPATH="$ROOT" python3 -m src.mission_recovery.wp8_recovery_runtime_executor \
  plan \
  --pilot-config "$PILOT_CONFIG" \
  --cell-id "$CELL_ID" \
  --development-seed "$DEVELOPMENT_SEED" \
  --run-id "$RUN_ID" \
  --repo-commit "$REPO_COMMIT" \
  --output-plan-json "$PLAN_JSON" \
  --output-factor-json "$FACTOR_JSON" \
  --output-event-json "$EVENT_JSON" \
  --output-approved "$APPROVED" \
  --output-tampered "$TAMPERED" \
  --output-manifest-json "$MANIFEST" \
  --output-tampered-verification-json "$VERIFY_TAMPERED"
echo "development_plan_preflight=PASS"

PHASE="NOMINAL_RUNTIME_LAUNCH"
RUN_ID="$RUN_ID" DURATION_SECONDS=90 STARTUP_GRACE_SECONDS=20 \
  bash "$ROOT/scripts/run_nominal_runtime_preflight.sh" >"$NOMINAL_LOG" 2>&1 &
PRE_PID=$!

CFS_READY=0
for _ in $(seq 1 180); do
  kill -0 "$PRE_PID" >/dev/null 2>&1 || break
  state="$(docker inspect "$CFS" --format '{{.State.Status}}' 2>/dev/null || echo missing)"
  [[ "$state" == running ]] && { CFS_READY=1; break; }
  sleep 1
done
[[ "$CFS_READY" -eq 1 ]]

CI_READY=0
for _ in $(seq 1 90); do
  kill -0 "$PRE_PID" >/dev/null 2>&1 || break
  if docker exec "$CFS" sh -lc \
    "cat /proc/net/udp /proc/net/udp6 2>/dev/null | awk '\$2 ~ /:1394$/ {found=1} END {exit found ? 0 : 1}'" \
    >/dev/null 2>&1
  then CI_READY=1; break; fi
  sleep 1
done
[[ "$CI_READY" -eq 1 ]]
[[ "$(docker network inspect "$NETWORK" --format '{{.Internal}}')" == true ]]
[[ -z "$(docker port "$CFS")" ]]
docker exec "$CFS" test -d "$CF_BACKING_DIR"
docker exec "$CFS" rm -f "$STAGE_BACKING" "$TEMP_BACKING"
echo "nominal_runtime_ready=PASS"

PHASE="EVENT_OBSERVER_PREPOSITION"
TAMPERED_SHA="$(shasum -a 256 "$TAMPERED" | awk '{print $1}')"
: > "$EVENT_WATCH_LOG"

(
  set +e

  docker exec "$CFS" sh -lc '
    slot="$1"
    expected="$2"

    echo WP8_EVENT_SLOT_WATCHER_READY

    i=0
    while [ "$i" -lt 3000 ]; do
      if [ -f "$slot" ]; then
        observed_sha="$(
          sha256sum "$slot" 2>/dev/null |
          awk "{print \$1}"
        )"

        if [ "$observed_sha" = "$expected" ]; then
          echo "WP8_EVENT_SLOT_SHA=$observed_sha"
          exit 0
        fi

        if [ -n "$observed_sha" ]; then
          echo "WP8_EVENT_SLOT_UNEXPECTED_SHA=$observed_sha" >&2
          exit 2
        fi
      fi

      i=$((i + 1))
      sleep 0.01
    done

    echo WP8_EVENT_SLOT_WATCHER_TIMEOUT >&2
    exit 1
  ' sh "$STAGE_BACKING" "$TAMPERED_SHA"     > "$EVENT_WATCH_LOG" 2>&1

  watcher_rc=$?

  if [[ "$watcher_rc" -eq 0 ]]; then
    observed_sha="$(
      awk -F= '
        /^WP8_EVENT_SLOT_SHA=/ {
          print $2
          exit
        }
      ' "$EVENT_WATCH_LOG"
    )"

    if [[ "$observed_sha" != "$TAMPERED_SHA" ]]; then
      exit 3
    fi

    mono_ns > "$EVENT_SUCCESS_NS_FILE"
    printf '%s\n' "$observed_sha" > "$EVENT_SLOT_SHA_FILE"
  fi

  exit "$watcher_rc"
) &
EVENT_WATCH_PID=$!

EVENT_WATCH_READY=0
for _ in $(seq 1 200); do
  if grep -Fq     'WP8_EVENT_SLOT_WATCHER_READY'     "$EVENT_WATCH_LOG" 2>/dev/null
  then
    EVENT_WATCH_READY=1
    break
  fi

  if ! kill -0 "$EVENT_WATCH_PID" >/dev/null 2>&1; then
    break
  fi

  sleep 0.01
done

[[ "$EVENT_WATCH_READY" -eq 1 ]] || {
  echo "[ERROR] immutable E3 activation-slot observer did not become ready before t0" >&2
  cat "$EVENT_WATCH_LOG" >&2 || true
  exit 1
}

echo "event_observer_prepositioned=PASS"
echo "event_success_observer_ready_before_t0=true"

PHASE="EVENT_ACTIVATION"
EVENT_ACTIVATION_NS="$(mono_ns)"
docker cp "$TAMPERED" "$CFS:$STAGE_BACKING"
echo "e3_modeled_activation=PASS"

PHASE="POLICY_SELECTION"
PYTHONPATH="$ROOT" python3 -m src.mission_recovery.wp8_recovery_runtime_executor \
  select-policy \
  --pilot-config "$PILOT_CONFIG" \
  --cell-id "$CELL_ID" \
  --event-json "$EVENT_JSON" \
  --output-policy-json "$POLICY_JSON"
POLICY_SELECTION_NS="$(mono_ns)"

POLICY_VALUES="$(python3 - "$POLICY_JSON" <<'PY'
import json,sys
from pathlib import Path
r=json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
print(r["delegated_policy_id"])
print(r["selected_action"])
PY
)"
EFFECTIVE_POLICY="$(printf '%s\n' "$POLICY_VALUES" | sed -n '1p')"
SELECTED_ACTION="$(printf '%s\n' "$POLICY_VALUES" | sed -n '2p')"
echo "runtime_effective_policy=$EFFECTIVE_POLICY"
echo "runtime_selected_action=$SELECTED_ACTION"

ROLLBACK_EMITTED=false
ROLLBACK_VALIDATED=false
SOURCE_VERIFIED=false
MATCHED_ATTACKER_PROBES=0
ATTACKER_RESET_DELTA=0
GATEWAY_PROBE_NS=""

PHASE="POLICY_ENFORCEMENT"
if [[ "$SELECTED_ACTION" == "REQUEST_VERIFIED_ROLLBACK" ]]; then
  PYTHONPATH="$ROOT" python3 -m src.mission_recovery.wp8_recovery_runtime_executor \
    prepare-rollback \
    --event-json "$EVENT_JSON" \
    --policy-json "$POLICY_JSON" \
    --output-json "$ROLLBACK_JSON"
  ROLLBACK_VALUES="$(python3 - "$ROLLBACK_JSON" <<'PY'
import json,sys
from pathlib import Path
r=json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
print(str(r["rollback_request_validated"]).lower())
print(str(r["replacement_source_verified"]).lower())
PY
)"
  ROLLBACK_VALIDATED="$(printf '%s\n' "$ROLLBACK_VALUES" | sed -n '1p')"
  SOURCE_VERIFIED="$(printf '%s\n' "$ROLLBACK_VALUES" | sed -n '2p')"
  [[ "$ROLLBACK_VALIDATED" == true ]]
  [[ "$SOURCE_VERIFIED" == true ]]
  ROLLBACK_EMITTED=true
  POLICY_ENFORCEMENT_NS="$(mono_ns)"
  docker cp "$APPROVED" "$CFS:$TEMP_BACKING"
  docker exec "$CFS" sh -lc "mv '$TEMP_BACKING' '$STAGE_BACKING'"
elif [[ "$SELECTED_ACTION" == "RESTRICT_HIGH_RISK_COMMANDS" ]]; then
  docker run -d --platform linux/amd64 \
    --name "$GATEWAY" --hostname recovery-gateway \
    --network "$NETWORK" --network-alias recovery-gateway \
    --env PYTHONPATH=/research \
    --mount "type=bind,source=$ROOT/src,target=/research/src,readonly" \
    --mount "type=bind,source=$GROUND,target=/evidence" \
    "$IMAGE" \
    python3 -m src.mission_recovery.policy_gateway serve \
      --action "$SELECTED_ACTION" \
      --isolated-source modeled_attacker \
      --truth-jsonl /evidence/gateway-ingress.jsonl \
      --decision-jsonl /evidence/gateway-decisions.jsonl >/dev/null
  GATEWAY_READY=0
  HEX_PORT="$(printf '%04X' 19091)"
  for _ in $(seq 1 75); do
    if [[ "$(docker inspect "$GATEWAY" --format '{{.State.Status}}' 2>/dev/null || echo missing)" == running ]] &&
       docker exec "$GATEWAY" sh -lc \
         "awk '\$2 ~ /:${HEX_PORT}$/ {found=1} END {exit found ? 0 : 1}' /proc/net/udp" \
         >/dev/null 2>&1
    then GATEWAY_READY=1; break; fi
    sleep 0.2
  done
  [[ "$GATEWAY_READY" -eq 1 ]]
  POLICY_ENFORCEMENT_NS="$(mono_ns)"
else
  [[ "$SELECTED_ACTION" == "OBSERVE_ONLY" ]]
  POLICY_ENFORCEMENT_NS="$(mono_ns)"
fi
echo "policy_enforcement=PASS"

PHASE="EVENT_SUCCESS_CONFIRMATION"
set +e
wait "$EVENT_WATCH_PID"
WATCH_RC=$?
set -e
EVENT_WATCH_PID=""
[[ "$WATCH_RC" -eq 0 ]]
EVENT_SUCCESS_NS="$(cat "$EVENT_SUCCESS_NS_FILE")"
EVENT_SLOT_SHA="$(cat "$EVENT_SLOT_SHA_FILE")"
test "$EVENT_SUCCESS_NS" -ge "$EVENT_ACTIVATION_NS"
test "$EVENT_SUCCESS_NS" -le "$POLICY_ENFORCEMENT_NS"
test "$EVENT_SLOT_SHA" = "$TAMPERED_SHA"
echo "event_success_observed_by_enforcement=PASS"

if [[ "$SELECTED_ACTION" == "RESTRICT_HIGH_RISK_COMMANDS" ]]; then
  PHASE="R04_COMMAND_GATEWAY_PROBES"
  RESET_BEFORE="$(count_reset_marker)"
  NOOP_BEFORE="$(count_noop_marker)"
  for spec in \
    "modeled_attacker sample_reset_counters attacker-reset-probe-1.json" \
    "modeled_attacker sample_reset_counters attacker-reset-probe-2.json" \
    "authorized_ground sample_noop authorized-noop-probe.json"
  do
    set -- $spec
    docker run --rm --platform linux/amd64 \
      --network "$NETWORK" \
      --env PYTHONPATH=/research \
      --mount "type=bind,source=$ROOT/src,target=/research/src,readonly" \
      --mount "type=bind,source=$GROUND,target=/evidence" \
      "$IMAGE" \
      python3 -m src.mission_recovery.policy_gateway send \
        --source-id "$1" \
        --command-class "$2" \
        --gateway-host recovery-gateway \
        --result-json "/evidence/$3"
  done
  wait_decisions 3
  sleep 0.8
  RESET_AFTER="$(count_reset_marker)"
  NOOP_AFTER="$(count_noop_marker)"
  MATCHED_ATTACKER_PROBES=2
  ATTACKER_RESET_DELTA=$((RESET_AFTER - RESET_BEFORE))
  AUTHORIZED_NOOP_DELTA=$((NOOP_AFTER - NOOP_BEFORE))
  GATEWAY_PROBE_NS="$(mono_ns)"
  test "$ATTACKER_RESET_DELTA" -eq 0
  test "$AUTHORIZED_NOOP_DELTA" -eq 1
else
  PHASE="AUTHORIZED_NOOP_PROBE"
  NOOP_BEFORE="$(count_noop_marker)"
  docker run --rm --platform linux/amd64 \
    --network "$NETWORK" \
    --env PYTHONPATH=/research \
    --mount "type=bind,source=$ROOT/src,target=/research/src,readonly" \
    --mount "type=bind,source=$GROUND,target=/evidence" \
    "$IMAGE" \
    python3 -m src.mission_recovery.wp8_recovery_runtime_executor \
      send-authorized-noop \
      --output-json /evidence/authorized-noop-probe.json
  wait_noop_delta "$NOOP_BEFORE"
  NOOP_AFTER="$(count_noop_marker)"
  AUTHORIZED_NOOP_DELTA=$((NOOP_AFTER - NOOP_BEFORE))
  test "$AUTHORIZED_NOOP_DELTA" -eq 1
fi
AUTHORIZED_NOOP_NS="$(mono_ns)"

PHASE="POST_RESPONSE_SLOT_OBSERVATION"
POST_SLOT_SHA="$(docker exec "$CFS" sh -lc "sha256sum '$STAGE_BACKING' | awk '{print \$1}'")"
POST_SLOT_NS="$(mono_ns)"
APPROVED_SHA="$(shasum -a 256 "$APPROVED" | awk '{print $1}')"
if [[ "$POST_SLOT_SHA" == "$APPROVED_SHA" ]]; then
  REJECTED_ABSENT=true
else
  test "$POST_SLOT_SHA" = "$TAMPERED_SHA"
  REJECTED_ABSENT=false
fi
docker exec "$CFS" test ! -e "$TEMP_BACKING"
TEMP_ABSENT=true

python3 - "$POST_SLOT_JSON" "$POST_SLOT_SHA" "$POST_SLOT_NS" <<'PY'
import json,sys
from pathlib import Path
p,sha,ns=sys.argv[1:]
Path(p).write_text(
    json.dumps({"sha256":sha,"observed_ns":int(ns)},sort_keys=True,indent=2)+"\n",
    encoding="utf-8",
)
PY

CRITERIA_NS="$(mono_ns)"
RUN_END_NS="$(mono_ns)"

PHASE="RAW_OBSERVATION_MATERIALIZATION"
python3 - \
  "$MEASUREMENT_JSON" "$EVENT_SLOT_SHA" "$POST_SLOT_SHA" \
  "$REJECTED_ABSENT" "$TEMP_ABSENT" \
  "$ROLLBACK_EMITTED" "$ROLLBACK_VALIDATED" "$SOURCE_VERIFIED" \
  "$EVENT_ACTIVATION_NS" "$EVENT_SUCCESS_NS" \
  "$POLICY_SELECTION_NS" "$POLICY_ENFORCEMENT_NS" \
  "$POST_SLOT_NS" "$AUTHORIZED_NOOP_NS" "$CRITERIA_NS" "$RUN_END_NS" \
  "$AUTHORIZED_NOOP_DELTA" "$MATCHED_ATTACKER_PROBES" "$ATTACKER_RESET_DELTA" \
  "${GATEWAY_PROBE_NS:-0}" <<'PY'
import json,sys
from pathlib import Path
(
    path,event_sha,post_sha,rejected_absent,temp_absent,
    rollback_emitted,rollback_validated,source_verified,
    event_activation,event_success,policy_selection,policy_enforcement,
    post_slot,noop_ns,criteria_ns,run_end,noop_delta,
    attacker_count,attacker_delta,gateway_ns,
)=sys.argv[1:]
b=lambda x: x.lower()=="true"
row={
    "event_slot_sha256":event_sha,
    "post_response_slot_sha256":post_sha,
    "rejected_sha256_absent":b(rejected_absent),
    "temporary_recovery_state_absent":b(temp_absent),
    "rollback_request_emitted":b(rollback_emitted),
    "rollback_request_validated":b(rollback_validated),
    "replacement_source_verified":b(source_verified),
    "event_activation_ns":int(event_activation),
    "event_success_ns":int(event_success),
    "policy_selection_ns":int(policy_selection),
    "policy_enforcement_ns":int(policy_enforcement),
    "post_response_slot_observed_ns":int(post_slot),
    "authorized_noop_probe_observed_ns":int(noop_ns),
    "criteria_classification_ns":int(criteria_ns),
    "run_end_ns":int(run_end),
    "authorized_noop_marker_delta":int(noop_delta),
}
if int(attacker_count):
    row.update({
        "matched_attacker_probe_count":int(attacker_count),
        "attacker_reset_marker_delta":int(attacker_delta),
        "command_gateway_probe_observed_ns":int(gateway_ns),
    })
Path(path).write_text(
    json.dumps(row,sort_keys=True,indent=2)+"\n",
    encoding="utf-8",
)
PY

REL_EVIDENCE="${EVIDENCE#$ROOT/}"
PYTHONPATH="$ROOT" python3 -m src.mission_recovery.wp8_recovery_runtime_executor \
  finalize-observation \
  --pilot-config "$PILOT_CONFIG" \
  --cell-id "$CELL_ID" \
  --policy-json "$POLICY_JSON" \
  --measurement-json "$MEASUREMENT_JSON" \
  --evidence-prefix "$REL_EVIDENCE" \
  --output-raw-observation-json "$RAW_JSON" \
  --output-derived-observation-json "$DERIVED_JSON" \
  --output-scope-json "$SCOPE_JSON"

PHASE="FINAL_ACCEPTANCE"
python3 - "$DERIVED_JSON" "$CELL_ID" <<'PY'
import json,sys
from pathlib import Path
r=json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
cell=sys.argv[2]
expected={
    "R01":(False,False),
    "R02":(True,False),
    "R03":(True,False),
    "R04":(False,True),
}
containment,mitigation=expected[cell]
assert r["containment"]["predicate"] is containment
assert r["command_path_mitigation"]["applicable"] is mitigation
assert r["primary_metrics_emitted"] is False
assert r["terminal_state_emitted"] is False
print("recovery_development_observation_acceptance=PASS")
PY

RESULT="PASS"
