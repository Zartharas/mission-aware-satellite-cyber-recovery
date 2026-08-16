#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
IMAGE="ivvitc/nos3-64@sha256:06aa945988a7770b759022c2e1f6f2531818c087fe41a4739d3a3a7f2a9dcce2"

SEED=9201
RUN_ID="${RUN_ID:-$(date -u +%Y%m%dT%H%M%SZ)-wp8-recovery-binding-dev}"
SAFE_ID="$(printf '%s' "$RUN_ID" | tr '[:upper:]' '[:lower:]' | tr -cs 'a-z0-9_.-' '-')"

NETWORK="mascr-$SAFE_ID"
CFS="mascr-$SAFE_ID-cfs"
PROXY="mascr-$SAFE_ID-recovery-proxy"
POLICY="mascr-$SAFE_ID-recovery-policy"
TLM_PORT=5013

EVIDENCE="$ROOT/results/wp8/runtime-binding/recovery/$RUN_ID"
GROUND="$EVIDENCE/immutable-ground"
OBS="$EVIDENCE/runtime-observation"

FACTOR_JSON="$GROUND/factor-context.json"
EVENT_JSON="$GROUND/event-instance.json"
POLICY_JSON="$GROUND/policy-decision.json"
APPROVED="$GROUND/approved-update.pkg"
TAMPERED="$GROUND/tampered-update.pkg"
MANIFEST="$GROUND/approved-manifest.json"
VERIFY_TAMPERED="$GROUND/verify-tampered.json"
ROLLBACK_REQUEST="$GROUND/rollback-request.json"
REQUEST_VALIDATION="$GROUND/rollback-request-validation.json"
SOURCE_VERIFY="$GROUND/replacement-source-verification.json"
TERMINAL_COPY="$GROUND/terminal-recovered-candidate.pkg"
TERMINAL_VERIFY="$GROUND/terminal-recovery-verification.json"
NOOP_JSON="$GROUND/post-recovery-authorized-noop.json"
ENABLE_JSON="$GROUND/preposition-telemetry-output.json"
SEND_JSON="$GROUND/post-recovery-send-data-types.json"
TRUTH_JSONL="$GROUND/post-recovery-telemetry-truth.jsonl"
POLICY_JSONL="$OBS/post-recovery-policy-visible.jsonl"
HEALTH_JSON="$GROUND/post-recovery-health.json"
RECOVERY_MANIFEST="$GROUND/trusted-recovery-evidence-manifest.json"
SUMMARY_JSON="$GROUND/recovery-observation-summary.json"
OBSERVATION_JSON="$EVIDENCE/runtime-binding-observation.json"
RUN_RECORD="$EVIDENCE/run-record.json"
PROVENANCE="$EVIDENCE/binding-provenance.json"
EVENT_SUCCESS_NS_FILE="$OBS/event-success-monotonic-ns.txt"
EVENT_SLOT_SHA_FILE="$OBS/event-slot-sha256.txt"
EVENT_WATCH_LOG="$OBS/event-slot-watcher.log"

CF_BACKING_DIR="/work/nos3/fsw/build/exe/cpu1/cf"
STAGE_BACKING="$CF_BACKING_DIR/mission-aware-e3-candidate.pkg"
TEMP_BACKING="$CF_BACKING_DIR/mission-aware-wp8-rollback.tmp"

NOMINAL_EVIDENCE="$ROOT/artifacts/runtime/$RUN_ID"
NOMINAL_LOG="$OBS/nominal-runtime.log"
RUNTIME_MANIFEST="$NOMINAL_EVIDENCE/runtime-manifest.txt"

PILOT_CONFIG="$ROOT/configs/wp8_pilot_design.json"
TOOLCHAIN="$ROOT/configs/toolchain-lock.json"
SCHEMA="$ROOT/configs/experiment_run.schema.json"

PRE_PID=""
EVENT_WATCH_PID=""
RESULT="RUN_INVALID"
PHASE="INITIALIZATION"

mono_ns() {
  python3 -c 'import time; print(time.monotonic_ns())'
}

count_noop_marker() {
  docker logs "$CFS" 2>&1 |
    grep -Fc 'SAMPLE: NOOP command received' || true
}

count_mid() {
  python3 - "$1" "$2" <<'PY'
import json
import sys
from pathlib import Path

path = Path(sys.argv[1])
mid = int(sys.argv[2], 0)

if not path.exists():
    print(0)
    raise SystemExit(0)

count = 0
for line in path.read_text(encoding="utf-8").splitlines():
    if not line.strip():
        continue
    row = json.loads(line)
    if row.get("mid") == mid:
        count += 1
print(count)
PY
}

wait_for_delta() {
  local path="$1" mid="$2" before="$3" delta="$4" label="$5"
  local now expected
  expected=$((before + delta))
  for _ in $(seq 1 30); do
    now="$(count_mid "$path" "$mid")"
    if [[ "$now" -eq "$expected" ]]; then
      printf '%s\n' "$now"
      return 0
    fi
    if [[ "$now" -gt "$expected" ]]; then
      echo "[ERROR] $label count exceeded expected: now=$now expected=$expected" >&2
      return 2
    fi
    sleep 0.2
  done
  now="$(count_mid "$path" "$mid")"
  echo "[ERROR] $label timeout: now=$now expected=$expected" >&2
  return 1
}

wait_noop_delta() {
  local before="$1"
  local now
  for _ in $(seq 1 75); do
    now="$(count_noop_marker)"
    if [[ "$now" -eq $((before + 1)) ]]; then
      printf '%s\n' "$now"
      return 0
    fi
    if [[ "$now" -gt $((before + 1)) ]]; then
      echo "[ERROR] authorized NOOP marker exceeded expected delta" >&2
      return 2
    fi
    sleep 0.2
  done
  now="$(count_noop_marker)"
  echo "[ERROR] authorized NOOP marker timeout: before=$before now=$now" >&2
  return 1
}

bind_invalid_observation() {
  [[ -f "$FACTOR_JSON" ]] || return 0
  [[ ! -f "$RUN_RECORD" ]] || return 0

  local invalid_reason
  invalid_reason="$(
    printf '%s' "$PHASE" |
    tr '[:upper:]' '[:lower:]' |
    tr -cs 'a-z0-9_' '_'
  )"
  invalid_reason="development_preflight_failure_phase_${invalid_reason}"

  PYTHONPATH="$ROOT" python3 - \
    "$FACTOR_JSON" "$TOOLCHAIN" "$EVIDENCE" \
    "$RUN_RECORD" "$PROVENANCE" "$invalid_reason" "$ROOT" <<'PY'
import json
import sys
from pathlib import Path

from src.mission_recovery.wp8_runtime_binding import (
    bind_invalid_runtime_observation,
    environment_from_toolchain_lock,
)

(
    factor_path,
    toolchain_path,
    evidence_dir,
    run_record_path,
    provenance_path,
    invalid_reason,
    root_path,
) = sys.argv[1:]

factor = json.loads(Path(factor_path).read_text(encoding="utf-8"))
toolchain = json.loads(Path(toolchain_path).read_text(encoding="utf-8"))
root = Path(root_path)
evidence = Path(evidence_dir)

refs = []
for path in sorted(evidence.rglob("*")):
    if path.is_file():
        try:
            refs.append(str(path.relative_to(root)))
        except ValueError:
            refs.append(str(path))

result = bind_invalid_runtime_observation(
    factor_context=factor,
    environment=environment_from_toolchain_lock(
        toolchain,
        snapshot_id=f"repo-{factor['repo_commit']}",
        host_architecture=None,
    ),
    invalid_run_reason=invalid_reason,
    source_observation_refs=refs,
    notes=(
        "WP8 recovery-family runtime-binding development preflight "
        "failed; retained as RUN_INVALID and is not pilot data."
    ),
)

Path(run_record_path).write_text(
    json.dumps(result["run_record"], sort_keys=True, indent=2) + "\n",
    encoding="utf-8",
)
Path(provenance_path).write_text(
    json.dumps(result["binding_provenance"], sort_keys=True, indent=2) + "\n",
    encoding="utf-8",
)

print("invalid_run_retained=PASS")
print("invalid_run_reason=" + invalid_reason)
PY
}

cleanup() {
  local rc=$?
  set +e

  docker rm -f "$PROXY" "$POLICY" >/dev/null 2>&1 || true

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

  if [[ "$RESULT" == PASS && "$rc" -eq 0 ]]; then
    echo "WP8_RECOVERY_BINDING_PREFLIGHT=PASS"
    echo "development_preflight=true"
    echo "pilot_data=false"
    echo "evidence_directory=$EVIDENCE"
  else
    bind_invalid_observation || true
    echo "WP8_RECOVERY_BINDING_PREFLIGHT=FAIL" >&2
    echo "failure_phase=$PHASE" >&2
    echo "development_preflight=true" >&2
    echo "pilot_data=false" >&2
    echo "evidence_directory=$EVIDENCE" >&2
  fi

  exit "$rc"
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

mkdir -p "$GROUND" "$OBS"
: > "$TRUTH_JSONL"
: > "$POLICY_JSONL"

REPO_COMMIT="$(git -C "$ROOT" rev-parse HEAD)"
RUNNER_SHA="$(shasum -a 256 "$ROOT/scripts/run_wp8_recovery_binding_preflight.sh" | awk '{print $1}')"

PHASE="FACTOR_EVENT_MATERIALIZATION"

PYTHONPATH="$ROOT" python3 - \
  "$FACTOR_JSON" "$EVENT_JSON" "$APPROVED" "$TAMPERED" \
  "$MANIFEST" "$VERIFY_TAMPERED" "$RUN_ID" "$SEED" "$REPO_COMMIT" <<'PY'
import json
import sys
from pathlib import Path

from src.mission_recovery.events import materialize_event
from src.mission_recovery.update_artifacts import (
    build_approved_update,
    build_manifest,
    build_tampered_update,
    verify_candidate,
)

(
    factor_path,
    event_path,
    approved_path,
    tampered_path,
    manifest_path,
    verify_path,
    run_id,
    seed,
    repo_commit,
) = sys.argv[1:]

seed = int(seed)
event = materialize_event(
    "E3",
    mission_state="M4",
    contact_condition="C0",
    evidence_condition="T0",
    seed=seed,
)
approved = build_approved_update()
tampered = build_tampered_update()
manifest = build_manifest()
tampered_verify = verify_candidate(tampered, manifest)

assert event["policy_visible_evidence"]["integrity_check_passed"] is False
assert event["policy_visible_evidence"]["approved_version"] is False
assert event["policy_visible_evidence"]["rollback_available"] is True
assert event["ground_truth"]["update_integrity_valid"] is False
assert tampered_verify["accepted"] is False
assert "sha256_mismatch" in tampered_verify["reasons"]

factor = {
    "run_id": run_id,
    "model_version": "0.3.0",
    "seed": seed,
    "mission_state_id": "M4",
    "event_id": "E3",
    "policy_id": "P5",
    "contact_condition_id": "C0",
    "evidence_condition_id": "T0",
    "repo_commit": repo_commit,
}

Path(factor_path).write_text(
    json.dumps(factor, sort_keys=True, indent=2) + "\n",
    encoding="utf-8",
)
Path(event_path).write_text(
    json.dumps(event, sort_keys=True, indent=2) + "\n",
    encoding="utf-8",
)
Path(approved_path).write_bytes(approved)
Path(tampered_path).write_bytes(tampered)
Path(manifest_path).write_text(
    json.dumps(manifest, sort_keys=True, indent=2) + "\n",
    encoding="utf-8",
)
Path(verify_path).write_text(
    json.dumps(tampered_verify, sort_keys=True, indent=2) + "\n",
    encoding="utf-8",
)

print("recovery_factor_event_materialization=PASS")
PY

APPROVED_SHA="$(shasum -a 256 "$APPROVED" | awk '{print $1}')"
TAMPERED_SHA="$(shasum -a 256 "$TAMPERED" | awk '{print $1}')"

test "$APPROVED_SHA" = "42945a2622fa351b3a3fdc31e002cbe326cb7a42a958ee757f317abea67b6697"
test "$TAMPERED_SHA" = "ff96d61205cc2c49b6d7d73fc36b9544c0deea79d7a9304cc1fb9f1f8986053d"
test "$APPROVED_SHA" != "$TAMPERED_SHA"

echo "development_seed=9201"
echo "pilot_seed_consumed=false"
echo "approved_artifact_identity=PASS"
echo "tampered_artifact_identity=PASS"

PHASE="NOMINAL_RUNTIME_LAUNCH"

RUN_ID="$RUN_ID" \
DURATION_SECONDS=90 \
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

CI_READY=0
for _ in $(seq 1 90); do
  kill -0 "$PRE_PID" >/dev/null 2>&1 || break
  if docker exec "$CFS" sh -lc \
    "cat /proc/net/udp /proc/net/udp6 2>/dev/null | awk '\$2 ~ /:1394\$/ {found=1} END {exit found ? 0 : 1}'" \
    >/dev/null 2>&1
  then
    CI_READY=1
    break
  fi
  sleep 1
done

[[ "$CI_READY" -eq 1 ]] || {
  echo "[ERROR] cFS CI_LAB UDP 5012 not ready" >&2
  exit 1
}

docker exec "$CFS" test -d "$CF_BACKING_DIR"
[[ "$(docker network inspect "$NETWORK" --format '{{.Internal}}')" == true ]]
[[ -z "$(docker port "$CFS")" ]]

echo "nominal_ci_lab_udp_5012=PASS"
echo "nominal_isolation=PASS"

docker exec "$CFS" rm -f "$STAGE_BACKING" "$TEMP_BACKING"
docker exec "$CFS" test ! -e "$STAGE_BACKING"
docker exec "$CFS" test ! -e "$TEMP_BACKING"

PHASE="MEASUREMENT_PLANE_PREPOSITION"

docker run -d --platform linux/amd64 \
  --name "$POLICY" \
  --hostname recovery-policy \
  --network "$NETWORK" \
  --network-alias recovery-policy \
  --env PYTHONPATH=/research \
  --mount "type=bind,source=$ROOT/src,target=/research/src,readonly" \
  --mount "type=bind,source=$OBS,target=/evidence" \
  "$IMAGE" \
  python3 -m src.mission_recovery.telemetry_visibility observer \
    --jsonl /evidence/post-recovery-policy-visible.jsonl \
    --port 19090 >/dev/null

docker run -d --platform linux/amd64 \
  --name "$PROXY" \
  --hostname recovery-proxy \
  --network "$NETWORK" \
  --network-alias recovery-proxy \
  --env PYTHONPATH=/research \
  --mount "type=bind,source=$ROOT/src,target=/research/src,readonly" \
  --mount "type=bind,source=$GROUND,target=/truth" \
  "$IMAGE" \
  python3 -m src.mission_recovery.telemetry_visibility proxy \
    --truth-jsonl /truth/post-recovery-telemetry-truth.jsonl \
    --mode control \
    --listen-port "$TLM_PORT" \
    --policy-host recovery-policy \
    --policy-port 19090 >/dev/null

PROXY_READY=0
HEX_TLM_PORT="$(printf '%04X' "$TLM_PORT")"
for _ in $(seq 1 20); do
  if [[ "$(docker inspect "$PROXY" --format '{{.State.Status}}' 2>/dev/null || echo missing)" == running ]] && \
     docker exec "$PROXY" sh -lc \
       "awk '\$2 ~ /:${HEX_TLM_PORT}\$/ {found=1} END {exit found ? 0 : 1}' /proc/net/udp" \
       >/dev/null 2>&1 &&
     [[ "$(docker inspect "$POLICY" --format '{{.State.Status}}' 2>/dev/null || echo missing)" == running ]]
  then
    PROXY_READY=1
    break
  fi
  sleep 0.5
done

[[ "$PROXY_READY" -eq 1 ]] || {
  echo "[ERROR] recovery telemetry measurement plane not ready" >&2
  exit 1
}

run_e4_adapter() {
  local result_file="$1"
  shift
  docker run --rm --platform linux/amd64 \
    --network "$NETWORK" \
    --env PYTHONPATH=/research \
    --mount "type=bind,source=$ROOT/src,target=/research/src,readonly" \
    --mount "type=bind,source=$GROUND,target=/evidence" \
    "$IMAGE" \
    python3 -m src.mission_recovery.nos3_e4_adapter \
      "$@" \
      --result-json "/evidence/$result_file"
}

run_e4_adapter "$(basename "$ENABLE_JSON")" enable-output --destination recovery-proxy

ENABLE_READY=0
for _ in $(seq 1 20); do
  if docker logs "$CFS" 2>&1 |
    grep -Fq 'TO telemetry output enabled for IP recovery-proxy'
  then
    ENABLE_READY=1
    break
  fi
  sleep 0.5
done
[[ "$ENABLE_READY" -eq 1 ]]

test "$(count_mid "$TRUTH_JSONL" 0x08E9)" -eq 0
test "$(count_mid "$POLICY_JSONL" 0x08E9)" -eq 0

echo "recovery_measurement_plane_ready=PASS"
echo "probe_adapter_e4_used_as_health_probe_only=true"

RUN_START_NS="$(mono_ns)"
RUN_START_UTC="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

PHASE="EVENT_OBSERVER_PREPOSITION"

: > "$EVENT_WATCH_LOG"

(
  set +e

  docker exec "$CFS" sh -lc '
    path="$1"
    expected="$2"

    echo WP8_EVENT_SLOT_WATCHER_READY

    i=0
    while [ "$i" -lt 3000 ]; do
      if [ -f "$path" ]; then
        observed_sha="$(
          sha256sum "$path" 2>/dev/null |
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
  if grep -Fq 'WP8_EVENT_SLOT_WATCHER_READY' "$EVENT_WATCH_LOG" 2>/dev/null; then
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

echo "immutable_activation_slot_observer_prepositioned=PASS"
echo "event_success_observer_ready_before_t0=true"

PHASE="EVENT_ACTIVATION"

EVENT_ACTIVATION_NS="$(mono_ns)"

docker cp "$TAMPERED" "$CFS:$STAGE_BACKING"

echo "e3_modeled_activation_slot_injection=PASS"
echo "event_activation_before_response=true"
echo "recovery_policy_trigger_uses_ground_truth=false"

PHASE="POLICY_SELECTION"

PYTHONPATH="$ROOT" python3 - \
  "$EVENT_JSON" "$POLICY_JSON" <<'PY'
import json
import sys
from pathlib import Path

from src.mission_recovery.policies import evaluate_policy

event = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
decision = evaluate_policy("P5", event)

assert event["event_id"] == "E3"
assert event["policy_visible_evidence"]["integrity_check_passed"] is False
assert event["policy_visible_evidence"]["rollback_available"] is True
assert decision["selected_action"] == "REQUEST_VERIFIED_ROLLBACK"
assert decision["oracle_ground_truth_read"] is False

Path(sys.argv[2]).write_text(
    json.dumps(decision, sort_keys=True, indent=2) + "\n",
    encoding="utf-8",
)

print("p5_policy_selection=PASS")
print("policy_oracle_ground_truth_read=false")
PY

POLICY_SELECTION_NS="$(mono_ns)"
test "$POLICY_SELECTION_NS" -ge "$EVENT_ACTIVATION_NS"

PHASE="POLICY_ENFORCEMENT"

PYTHONPATH="$ROOT" python3 - \
  "$EVENT_JSON" "$POLICY_JSON" "$MANIFEST" "$VERIFY_TAMPERED" \
  "$APPROVED" "$TAMPERED_SHA" \
  "$ROLLBACK_REQUEST" "$REQUEST_VALIDATION" "$SOURCE_VERIFY" <<'PY'
import json
import sys
from pathlib import Path

from src.mission_recovery.rollback_requests import (
    build_verified_rollback_request,
)
from src.mission_recovery.trusted_recovery import (
    validate_rollback_request,
    verify_replacement_source,
)

(
    event_path,
    policy_path,
    manifest_path,
    verify_tampered_path,
    approved_path,
    tampered_sha,
    request_path,
    request_validation_path,
    source_verify_path,
) = sys.argv[1:]

event = json.loads(Path(event_path).read_text(encoding="utf-8"))
policy = json.loads(Path(policy_path).read_text(encoding="utf-8"))
manifest = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
tampered_verify = json.loads(
    Path(verify_tampered_path).read_text(encoding="utf-8")
)

request = build_verified_rollback_request(
    event_instance=event,
    policy_decision=policy,
    manifest=manifest,
    candidate_verification=tampered_verify,
)
validation = validate_rollback_request(
    request=request,
    policy_decision=policy,
    manifest=manifest,
    pre_recovery_candidate_sha256=tampered_sha,
)
source_verify = verify_replacement_source(
    Path(approved_path).read_bytes(),
    manifest,
)

assert validation["accepted"] is True
assert validation["reasons"] == []
assert source_verify["accepted"] is True
assert source_verify["reasons"] == []
assert policy["oracle_ground_truth_read"] is False
assert request["oracle_ground_truth_read"] is False

Path(request_path).write_text(
    json.dumps(request, sort_keys=True, indent=2) + "\n",
    encoding="utf-8",
)
Path(request_validation_path).write_text(
    json.dumps(validation, sort_keys=True, indent=2) + "\n",
    encoding="utf-8",
)
Path(source_verify_path).write_text(
    json.dumps(source_verify, sort_keys=True, indent=2) + "\n",
    encoding="utf-8",
)

print("rollback_request_validation=PASS")
print("replacement_source_verification=PASS")
print("p5_enforcement_nonoracle=PASS")
PY

POLICY_ENFORCEMENT_NS="$(mono_ns)"
test "$POLICY_ENFORCEMENT_NS" -ge "$POLICY_SELECTION_NS"

if kill -0 "$EVENT_WATCH_PID" >/dev/null 2>&1; then
  echo "[ERROR] prepositioned E3 event-success observer had not completed by the policy-enforcement boundary" >&2
  exit 1
fi

set +e
wait "$EVENT_WATCH_PID"
EVENT_WATCH_RC=$?
set -e
EVENT_WATCH_PID=""

[[ "$EVENT_WATCH_RC" -eq 0 ]] || {
  echo "[ERROR] immutable E3 event-success watcher failed: rc=$EVENT_WATCH_RC" >&2
  cat "$EVENT_WATCH_LOG" >&2 || true
  exit 1
}

test -f "$EVENT_SUCCESS_NS_FILE"
test -f "$EVENT_SLOT_SHA_FILE"

EVENT_SUCCESS_NS="$(cat "$EVENT_SUCCESS_NS_FILE")"
EVENT_SLOT_SHA="$(cat "$EVENT_SLOT_SHA_FILE")"

test "$EVENT_SUCCESS_NS" -ge "$EVENT_ACTIVATION_NS"
test "$EVENT_SUCCESS_NS" -le "$POLICY_ENFORCEMENT_NS"
test "$EVENT_SLOT_SHA" = "$TAMPERED_SHA"

echo "immutable_activation_slot_observer=PASS"
echo "event_success_observed=true"
echo "event_success_observed_by_policy_enforcement_boundary=true"
echo "policy_selection_not_gated_on_event_success=true"
echo "policy_enforcement_not_gated_on_event_success=true"
echo "recovery_effect_not_delayed_for_ground_truth_observer=true"

PHASE="POST_ENFORCEMENT_RECOVERY_EFFECT"

docker cp "$APPROVED" "$CFS:$TEMP_BACKING"

TEMP_SHA="$(
  docker exec "$CFS" sha256sum "$TEMP_BACKING" |
  awk '{print $1}'
)"
test "$TEMP_SHA" = "$APPROVED_SHA"

echo "verified_recovery_temp_stage=PASS"

docker exec "$CFS" mv -f "$TEMP_BACKING" "$STAGE_BACKING"
docker exec "$CFS" test ! -e "$TEMP_BACKING"

TERMINAL_SLOT_SHA="$(
  docker exec "$CFS" sha256sum "$STAGE_BACKING" |
  awk '{print $1}'
)"
test "$TERMINAL_SLOT_SHA" = "$APPROVED_SHA"
test "$TERMINAL_SLOT_SHA" != "$TAMPERED_SHA"

CONTAINMENT_NS="$(mono_ns)"
test "$CONTAINMENT_NS" -ge "$POLICY_ENFORCEMENT_NS"

echo "recovery_containment_predicate_observed=true"
echo "approved_candidate_replaced_rejected_sha=true"
echo "rejected_sha_absent_from_modeled_activation_slot=true"

PHASE="POST_RECOVERY_VERIFICATION"

docker cp "$CFS:$STAGE_BACKING" "$TERMINAL_COPY" >/dev/null

PYTHONPATH="$ROOT" python3 - \
  "$TERMINAL_COPY" "$MANIFEST" "$TAMPERED_SHA" "$TERMINAL_VERIFY" <<'PY'
import json
import sys
from pathlib import Path

from src.mission_recovery.trusted_recovery import (
    verify_terminal_recovery,
)

candidate = Path(sys.argv[1]).read_bytes()
manifest = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))

result = verify_terminal_recovery(
    terminal_candidate=candidate,
    manifest=manifest,
    rejected_candidate_sha256=sys.argv[3],
)

assert result["trusted_recovery_verified"] is True
assert result["terminal_candidate_accepted"] is True
assert result["terminal_matches_approved"] is True
assert result["terminal_differs_from_rejected"] is True
assert result["terminal_sha256"] == manifest["approved_sha256"]
assert result["version"] == manifest["approved_version"]
assert result["reasons"] == []

Path(sys.argv[4]).write_text(
    json.dumps(result, sort_keys=True, indent=2) + "\n",
    encoding="utf-8",
)

print("independent_terminal_verification=PASS")
print("approved_version_current=true")
print("integrity_measurement_valid=true")
PY

MEASURED_STATE_NS="$(mono_ns)"
test "$MEASURED_STATE_NS" -ge "$CONTAINMENT_NS"

NOOP_BEFORE="$(count_noop_marker)"

docker run --rm --platform linux/amd64 \
  --network "$NETWORK" \
  --env PYTHONPATH=/research \
  --mount "type=bind,source=$ROOT/src,target=/research/src,readonly" \
  --mount "type=bind,source=$GROUND,target=/evidence" \
  "$IMAGE" \
  python3 -m src.mission_recovery.nos3_e1_adapter \
    --command-class sample_noop \
    --result-json "/evidence/$(basename "$NOOP_JSON")"

NOOP_AFTER="$(wait_noop_delta "$NOOP_BEFORE")"
test "$NOOP_AFTER" -eq $((NOOP_BEFORE + 1))
COMMAND_PATH_NS="$(mono_ns)"

echo "post_recovery_authorized_noop=PASS"
echo "probe_adapter_e1_used_as_health_probe_only=true"
echo "legitimate_commands_attempted=1"
echo "legitimate_commands_rejected=0"

TRUTH_BEFORE="$(count_mid "$TRUTH_JSONL" 0x08E9)"
POLICY_BEFORE="$(count_mid "$POLICY_JSONL" 0x08E9)"

run_e4_adapter "$(basename "$SEND_JSON")" send-data-types

TRUTH_AFTER="$(wait_for_delta "$TRUTH_JSONL" 0x08E9 "$TRUTH_BEFORE" 1 recovery_truth)"
POLICY_AFTER="$(wait_for_delta "$POLICY_JSONL" 0x08E9 "$POLICY_BEFORE" 1 recovery_policy)"

test "$TRUTH_AFTER" -eq $((TRUTH_BEFORE + 1))
test "$POLICY_AFTER" -eq $((POLICY_BEFORE + 1))

python3 - "$TRUTH_JSONL" "$TRUTH_BEFORE" <<'PY'
import json
import sys
from pathlib import Path

rows = [
    json.loads(line)
    for line in Path(sys.argv[1]).read_text(encoding="utf-8").splitlines()
    if line.strip() and json.loads(line).get("mid") == 0x08E9
]
before = int(sys.argv[2])
assert len(rows) == before + 1
assert rows[-1]["forwarded_to_policy"] is True
print("post_recovery_truth_forwarding_decision=PASS")
PY

TELEMETRY_NS="$(mono_ns)"

echo "post_recovery_truth_high_value_delta=1"
echo "post_recovery_policy_high_value_delta=1"
echo "required_telemetry_restored=true"

PHASE="TRUSTED_RECOVERY_EVIDENCE"

[[ "$(docker inspect "$CFS" --format '{{.State.Status}}')" == running ]]
[[ "$(docker inspect "$PROXY" --format '{{.State.Status}}')" == running ]]
[[ "$(docker inspect "$POLICY" --format '{{.State.Status}}')" == running ]]

docker exec "$CFS" sh -lc \
  "cat /proc/net/udp /proc/net/udp6 2>/dev/null | awk '\$2 ~ /:1394\$/ {found=1} END {exit found ? 0 : 1}'"

FINAL_SLOT_SHA="$(
  docker exec "$CFS" sha256sum "$STAGE_BACKING" |
  awk '{print $1}'
)"
test "$FINAL_SLOT_SHA" = "$APPROVED_SHA"
test "$FINAL_SLOT_SHA" != "$TAMPERED_SHA"
docker exec "$CFS" test ! -e "$TEMP_BACKING"

HEALTH_NS="$(mono_ns)"

python3 - \
  "$HEALTH_JSON" "$HEALTH_NS" \
  "$NOOP_BEFORE" "$NOOP_AFTER" \
  "$TRUTH_BEFORE" "$TRUTH_AFTER" \
  "$POLICY_BEFORE" "$POLICY_AFTER" \
  "$FINAL_SLOT_SHA" "$APPROVED_SHA" "$TAMPERED_SHA" <<'PY'
import json
import sys
from pathlib import Path

(
    path,
    health_ns,
    noop_before,
    noop_after,
    truth_before,
    truth_after,
    policy_before,
    policy_after,
    final_slot_sha,
    approved_sha,
    tampered_sha,
) = sys.argv[1:]

payload = {
    "schema": 1,
    "health_check_monotonic_ns": int(health_ns),
    "cfs_running": True,
    "ci_lab_udp_5012_ready": True,
    "authorized_noop_marker_delta": int(noop_after) - int(noop_before),
    "high_value_mid": "0x08E9",
    "truth_high_value_delta": int(truth_after) - int(truth_before),
    "policy_high_value_delta": int(policy_after) - int(policy_before),
    "modeled_activation_slot_sha256": final_slot_sha,
    "approved_sha256": approved_sha,
    "rejected_sha256": tampered_sha,
    "approved_state_current": final_slot_sha == approved_sha,
    "rejected_state_absent": final_slot_sha != tampered_sha,
    "health_checks_passed": True,
}

assert payload["authorized_noop_marker_delta"] == 1
assert payload["truth_high_value_delta"] == 1
assert payload["policy_high_value_delta"] == 1
assert payload["approved_state_current"] is True
assert payload["rejected_state_absent"] is True

Path(path).write_text(
    json.dumps(payload, sort_keys=True, indent=2) + "\n",
    encoding="utf-8",
)

print("post_recovery_health_snapshot=PASS")
PY

RECOVERY_MANIFEST_READY_NS="$(mono_ns)"

python3 - \
  "$ROOT" "$RECOVERY_MANIFEST" \
  "$EVENT_JSON" "$POLICY_JSON" "$MANIFEST" "$VERIFY_TAMPERED" \
  "$ROLLBACK_REQUEST" "$REQUEST_VALIDATION" "$SOURCE_VERIFY" \
  "$TERMINAL_VERIFY" "$NOOP_JSON" "$SEND_JSON" \
  "$TRUTH_JSONL" "$POLICY_JSONL" "$HEALTH_JSON" \
  "$EVENT_ACTIVATION_NS" "$EVENT_SUCCESS_NS" \
  "$POLICY_SELECTION_NS" "$POLICY_ENFORCEMENT_NS" \
  "$CONTAINMENT_NS" "$MEASURED_STATE_NS" \
  "$COMMAND_PATH_NS" "$TELEMETRY_NS" "$HEALTH_NS" \
  "$RECOVERY_MANIFEST_READY_NS" "$APPROVED_SHA" "$TAMPERED_SHA" <<'PY'
import hashlib
import json
import sys
from pathlib import Path

root = Path(sys.argv[1])
manifest_path = Path(sys.argv[2])

evidence_paths = [Path(value) for value in sys.argv[3:16]]
(
    event_activation_ns,
    event_success_ns,
    policy_selection_ns,
    policy_enforcement_ns,
    containment_ns,
    measured_state_ns,
    command_path_ns,
    telemetry_ns,
    health_ns,
    manifest_ready_ns,
    approved_sha,
    tampered_sha,
) = sys.argv[16:]

timeline = {
    "event_activation_ns": int(event_activation_ns),
    "event_success_ns": int(event_success_ns),
    "policy_selection_ns": int(policy_selection_ns),
    "policy_enforcement_ns": int(policy_enforcement_ns),
    "containment_ns": int(containment_ns),
    "measured_state_ns": int(measured_state_ns),
    "authorized_command_path_probe_ns": int(command_path_ns),
    "required_telemetry_probe_ns": int(telemetry_ns),
    "health_check_ns": int(health_ns),
    "recovery_manifest_ready_ns": int(manifest_ready_ns),
}

assert (
    timeline["event_activation_ns"]
    <= timeline["policy_selection_ns"]
    <= timeline["policy_enforcement_ns"]
    <= timeline["containment_ns"]
    <= timeline["measured_state_ns"]
    <= timeline["authorized_command_path_probe_ns"]
    <= timeline["required_telemetry_probe_ns"]
    <= timeline["health_check_ns"]
    <= timeline["recovery_manifest_ready_ns"]
)
assert (
    timeline["event_activation_ns"]
    <= timeline["event_success_ns"]
    <= timeline["containment_ns"]
)

source_evidence = {}
for path in evidence_paths:
    data = path.read_bytes()
    try:
        ref = str(path.relative_to(root))
    except ValueError:
        ref = str(path)
    source_evidence[ref] = hashlib.sha256(data).hexdigest()

criteria = {
    "approved_version": True,
    "integrity_measurement_valid": True,
    "authorization_valid": True,
    "measured_state_current": True,
    "authorized_command_path_restored": True,
    "ground_spacecraft_state_agreed": True,
    "required_telemetry_restored": True,
    "health_checks_passed": True,
    "no_residual_unauthorized_state": True,
    "recovery_manifest_complete": True,
}

payload = {
    "schema": 1,
    "classification": "WP8_RECOVERY_EVIDENCE_MANIFEST_READY",
    "study_event_id": "E3",
    "policy_id": "P5",
    "development_preflight": True,
    "pilot_data": False,
    "modeled_activation_slot": "/cf/mission-aware-e3-candidate.pkg",
    "approved_sha256": approved_sha,
    "rejected_sha256": tampered_sha,
    "terminal_state_candidate": "TRUSTED_RECOVERY_CONFIRMED",
    "controller_timeline_ns": timeline,
    "trusted_recovery_criteria": criteria,
    "source_evidence_sha256": source_evidence,
    "complete": True,
    "scientific_claim_boundary": (
        "controlled_staged_synthetic_update_state_only_no_operational_"
        "firmware_activation_or_flight_reflash_claim"
    ),
    "probe_adapter_reuse": {
        "nos3_e1_adapter": (
            "post_recovery_SAMPLE_NOOP_health_probe_only_not_E1_study_event"
        ),
        "nos3_e4_adapter": (
            "post_recovery_TO_LAB_telemetry_health_probe_only_not_E4_study_event"
        ),
    },
}

assert all(criteria.values())
assert payload["complete"] is True

manifest_path.write_text(
    json.dumps(payload, sort_keys=True, indent=2) + "\n",
    encoding="utf-8",
)

print("trusted_recovery_evidence_manifest=PASS")
PY

python3 - "$RECOVERY_MANIFEST" <<'PY'
import json
import sys
from pathlib import Path

manifest = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))

assert manifest["complete"] is True
assert manifest["terminal_state_candidate"] == "TRUSTED_RECOVERY_CONFIRMED"
assert all(manifest["trusted_recovery_criteria"].values())
assert manifest["development_preflight"] is True
assert manifest["pilot_data"] is False

print("trusted_recovery_evidence_manifest_validation=PASS")
PY

TRUSTED_RECOVERY_NS="$(mono_ns)"
test "$TRUSTED_RECOVERY_NS" -ge "$RECOVERY_MANIFEST_READY_NS"

RUN_END_NS="$(mono_ns)"
RUN_END_UTC="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
test "$RUN_END_NS" -ge "$TRUSTED_RECOVERY_NS"

echo "trusted_recovery_verified=true"
echo "trusted_recovery_manifest_precedes_timestamp=true"

PHASE="POST_RUN_NOMINAL_VALIDATION"

docker rm -f "$PROXY" "$POLICY" >/dev/null

set +e
wait "$PRE_PID"
PRE_RC=$?
set -e
PRE_PID=""

[[ "$PRE_RC" -eq 0 ]] || {
  echo "[ERROR] nominal runtime failed after trusted-recovery classification: rc=$PRE_RC" >&2
  tail -160 "$NOMINAL_LOG" >&2 || true
  exit 1
}

grep -Fq 'NOMINAL_RUNTIME_PREFLIGHT_STATUS=PASS' "$NOMINAL_LOG"
test -f "$RUNTIME_MANIFEST"

echo "validated_nominal_runtime_pass=true"

PHASE="OBSERVATION_BINDING"

REL="results/wp8/runtime-binding/recovery/$RUN_ID"

python3 - \
  "$FACTOR_JSON" "$RECOVERY_MANIFEST" "$SUMMARY_JSON" "$OBSERVATION_JSON" \
  "$RUN_START_NS" "$EVENT_ACTIVATION_NS" "$EVENT_SUCCESS_NS" \
  "$POLICY_SELECTION_NS" "$POLICY_ENFORCEMENT_NS" \
  "$CONTAINMENT_NS" "$TRUSTED_RECOVERY_NS" "$RUN_END_NS" \
  "$RUN_START_UTC" "$RUN_END_UTC" "$RUNNER_SHA" "$REPO_COMMIT" "$REL" <<'PY'
import json
import sys
from pathlib import Path

(
    factor_path,
    recovery_manifest_path,
    summary_path,
    observation_path,
    run_start_ns,
    event_activation_ns,
    event_success_ns,
    policy_selection_ns,
    policy_enforcement_ns,
    containment_ns,
    trusted_recovery_ns,
    run_end_ns,
    run_start_utc,
    run_end_utc,
    runner_sha,
    repo_commit,
    rel,
) = sys.argv[1:]

factor = json.loads(Path(factor_path).read_text(encoding="utf-8"))
recovery_manifest = json.loads(
    Path(recovery_manifest_path).read_text(encoding="utf-8")
)

clock = {
    "run_start_ns": int(run_start_ns),
    "event_activation_ns": int(event_activation_ns),
    "event_success_ns": int(event_success_ns),
    "policy_selection_ns": int(policy_selection_ns),
    "policy_enforcement_ns": int(policy_enforcement_ns),
    "containment_ns": int(containment_ns),
    "trusted_recovery_ns": int(trusted_recovery_ns),
    "run_end_ns": int(run_end_ns),
}

assert (
    clock["run_start_ns"]
    <= clock["event_activation_ns"]
    <= clock["policy_selection_ns"]
    <= clock["policy_enforcement_ns"]
    <= clock["containment_ns"]
    <= clock["trusted_recovery_ns"]
    <= clock["run_end_ns"]
)
assert (
    clock["event_activation_ns"]
    <= clock["event_success_ns"]
    <= clock["containment_ns"]
)

summary = {
    "schema": 1,
    "classification": "WP8_RECOVERY_RUNTIME_BINDING_DEVELOPMENT_PASS",
    "development_preflight": True,
    "pilot_data": False,
    "seed": factor["seed"],
    "repo_commit": repo_commit,
    "runner_sha256": runner_sha,
    "event_before_response_order": True,
    "policy_trigger_uses_ground_truth": False,
    "event_observer_prepositioned_before_t0": True,
    "event_success_observed_by_policy_enforcement_boundary": True,
    "recovery_effect_delayed_for_ground_truth_observer": False,
    "modeled_activation_slot_event_success": True,
    "containment_observed": True,
    "trusted_recovery_verified": True,
    "trusted_recovery_manifest_precedes_timestamp": True,
    "all_ten_recovery_criteria_current": True,
    "probe_adapter_e1_study_event": False,
    "probe_adapter_e4_study_event": False,
    "clock_ns": clock,
}

Path(summary_path).write_text(
    json.dumps(summary, sort_keys=True, indent=2) + "\n",
    encoding="utf-8",
)

criteria = recovery_manifest["trusted_recovery_criteria"]
assert all(criteria.values())

recovery_observations = {
    "approved_version": {
        "available_current": True,
        "evidence_ref": f"{rel}/immutable-ground/terminal-recovery-verification.json",
    },
    "integrity_measurement_valid": {
        "available_current": True,
        "evidence_ref": f"{rel}/immutable-ground/terminal-recovery-verification.json",
    },
    "authorization_valid": {
        "available_current": True,
        "evidence_ref": f"{rel}/immutable-ground/rollback-request-validation.json",
    },
    "measured_state_current": {
        "available_current": True,
        "evidence_ref": f"{rel}/immutable-ground/trusted-recovery-evidence-manifest.json",
    },
    "authorized_command_path_restored": {
        "available_current": True,
        "evidence_ref": f"{rel}/immutable-ground/post-recovery-health.json",
    },
    "ground_spacecraft_state_agreed": {
        "available_current": True,
        "evidence_ref": f"{rel}/immutable-ground/trusted-recovery-evidence-manifest.json",
    },
    "required_telemetry_restored": {
        "available_current": True,
        "evidence_ref": f"{rel}/immutable-ground/post-recovery-health.json",
    },
    "health_checks_passed": {
        "available_current": True,
        "evidence_ref": f"{rel}/immutable-ground/post-recovery-health.json",
    },
    "no_residual_unauthorized_state": {
        "available_current": True,
        "evidence_ref": f"{rel}/immutable-ground/trusted-recovery-evidence-manifest.json",
    },
    "recovery_manifest_complete": {
        "available_current": True,
        "evidence_ref": f"{rel}/immutable-ground/trusted-recovery-evidence-manifest.json",
    },
}

observation = {
    "factor_context": factor,
    "runtime_observation": {
        "family": "recovery",
        "clock": {
            "run_start_utc": run_start_utc,
            "run_end_utc": run_end_utc,
            "run_start_ns": clock["run_start_ns"],
            "event_activation_ns": clock["event_activation_ns"],
            "containment_ns": clock["containment_ns"],
            "trusted_recovery_ns": clock["trusted_recovery_ns"],
            "run_end_ns": clock["run_end_ns"],
        },
        "event_success": {
            "predicate": True,
            "observed_ns": clock["event_success_ns"],
            "evidence_ref": f"{rel}/runtime-observation/event-slot-sha256.txt",
        },
        "objective_results": {
            "MO-4": {
                "completed": True,
                "evidence_ref": f"{rel}/immutable-ground/trusted-recovery-evidence-manifest.json",
            },
            "MO-5": {
                "completed": True,
                "evidence_ref": f"{rel}/immutable-ground/trusted-recovery-evidence-manifest.json",
            },
        },
        "invariant_violation_intervals": [],
        "legitimate_commands": {
            "attempted": 1,
            "rejected": 0,
            "evidence_ref": f"{rel}/immutable-ground/post-recovery-health.json",
        },
        "ground_spacecraft_divergence_intervals": [
            {
                "state_key": "approved_version",
                "start_ns": clock["event_success_ns"],
                "end_ns": clock["containment_ns"],
            }
        ],
        "recovery_observations": recovery_observations,
        "recovery_checklist_excluded": [],
        "terminal_state_predicates": {
            "run_invalid": False,
            "mission_loss": False,
            "trusted_recovery_confirmed": True,
            "operational_restored": True,
            "recovery_failed": False,
            "contained": True,
        },
        "containment_evidence_ref": (
            f"{rel}/immutable-ground/trusted-recovery-evidence-manifest.json"
        ),
        "trusted_recovery_evidence_ref": (
            f"{rel}/immutable-ground/trusted-recovery-evidence-manifest.json"
        ),
        "terminal_state_evidence_refs": [
            f"{rel}/immutable-ground/terminal-recovery-verification.json",
            f"{rel}/immutable-ground/post-recovery-health.json",
            f"{rel}/immutable-ground/trusted-recovery-evidence-manifest.json",
        ],
        "source_observation_refs": [
            f"{rel}/immutable-ground/event-instance.json",
            f"{rel}/runtime-observation/event-slot-sha256.txt",
            f"{rel}/runtime-observation/event-slot-watcher.log",
            f"{rel}/immutable-ground/policy-decision.json",
            f"{rel}/immutable-ground/rollback-request-validation.json",
            f"{rel}/immutable-ground/replacement-source-verification.json",
            f"{rel}/immutable-ground/terminal-recovery-verification.json",
            f"{rel}/immutable-ground/post-recovery-authorized-noop.json",
            f"{rel}/immutable-ground/post-recovery-send-data-types.json",
            f"{rel}/immutable-ground/post-recovery-telemetry-truth.jsonl",
            f"{rel}/runtime-observation/post-recovery-policy-visible.jsonl",
            f"{rel}/immutable-ground/post-recovery-health.json",
            f"{rel}/immutable-ground/trusted-recovery-evidence-manifest.json",
            f"artifacts/runtime/{factor['run_id']}/runtime-manifest.txt",
        ],
        "development_preflight": True,
    },
    "notes": (
        "WP8 recovery-family runtime-binding development preflight; "
        "controlled staged synthetic update state only; not Stage-1 pilot data."
    ),
}

Path(observation_path).write_text(
    json.dumps(observation, sort_keys=True, indent=2) + "\n",
    encoding="utf-8",
)

print("recovery_runtime_observation_materialized=PASS")
PY

PYTHONPATH="$ROOT" python3 -m src.mission_recovery.wp8_runtime_binding \
  --observation-json "$OBSERVATION_JSON" \
  --pilot-config "$PILOT_CONFIG" \
  --toolchain-lock "$TOOLCHAIN" \
  --snapshot-id "repo-$REPO_COMMIT" \
  --host-architecture "$(uname -m)" \
  --output-run-json "$RUN_RECORD" \
  --output-provenance-json "$PROVENANCE"

PHASE="BOUND_RECORD_VALIDATION"

python3 - \
  "$SCHEMA" "$RUN_RECORD" "$PROVENANCE" "$SUMMARY_JSON" "$RECOVERY_MANIFEST" <<'PY'
import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

schema = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
record = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
provenance = json.loads(Path(sys.argv[3]).read_text(encoding="utf-8"))
summary = json.loads(Path(sys.argv[4]).read_text(encoding="utf-8"))
recovery_manifest = json.loads(Path(sys.argv[5]).read_text(encoding="utf-8"))

errors = list(
    Draft202012Validator(
        schema,
        format_checker=FormatChecker(),
    ).iter_errors(record)
)
assert not errors, [error.message for error in errors]

assert record["seed"] == 9201
assert record["event_id"] == "E3"
assert record["mission_state_id"] == "M4"
assert record["policy_id"] == "P5"
assert record["terminal_state"] == "TRUSTED_RECOVERY_CONFIRMED"

assert record["outcomes"]["unauthorized_effect_completed"] is True
assert record["outcomes"]["mission_objective_completion_ratio"] == 1.0
assert record["outcomes"]["safety_invariant_violations"] == []
assert record["outcomes"]["legitimate_command_rejection_rate"] == 0.0
assert record["outcomes"]["evidence_completeness_ratio"] == 1.0
assert record["outcomes"]["ground_spacecraft_state_divergence_s"] > 0.0

assert record["timing"]["containment_s"] is not None
assert record["timing"]["containment_s"] > 0.0
assert record["timing"]["verified_recovery_s"] is not None
assert record["timing"]["verified_recovery_s"] >= record["timing"]["containment_s"]

assert all(value is True for value in record["recovery_evidence"].values())

assert provenance["development_preflight"] is True
assert provenance["pilot_data"] is False
assert summary["policy_trigger_uses_ground_truth"] is False
assert summary["event_observer_prepositioned_before_t0"] is True
assert summary["event_success_observed_by_policy_enforcement_boundary"] is True
assert summary["recovery_effect_delayed_for_ground_truth_observer"] is False
assert summary["trusted_recovery_manifest_precedes_timestamp"] is True
assert summary["all_ten_recovery_criteria_current"] is True
assert recovery_manifest["complete"] is True
assert all(recovery_manifest["trusted_recovery_criteria"].values())

print("schema_valid_recovery_bound_run_record=PASS")
print("event_before_response_runtime_order=PASS")
print("unauthorized_effect_observed=true")
print("containment_observed=true")
print("trusted_recovery_verified=true")
print("mission_objective_completion_ratio=1.0")
print("legitimate_command_rejection_rate=0.0")
print("evidence_completeness_ratio=1.0")
print("policy_trigger_uses_ground_truth=false")
print("event_observer_prepositioned_before_t0=true")
print("event_success_observed_by_policy_enforcement_boundary=true")
print("recovery_effect_delayed_for_ground_truth_observer=false")
print("all_ten_recovery_criteria_current=true")
print("development_preflight=true")
print("pilot_data=false")
PY

RESULT="PASS"
PHASE="COMPLETE"
