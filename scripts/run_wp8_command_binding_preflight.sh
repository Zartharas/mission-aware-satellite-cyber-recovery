#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
IMAGE="ivvitc/nos3-64@sha256:06aa945988a7770b759022c2e1f6f2531818c087fe41a4739d3a3a7f2a9dcce2"

SEED=9101
RUN_ID="${RUN_ID:-$(date -u +%Y%m%dT%H%M%SZ)-wp8-command-binding-dev}"
SAFE_ID="$(printf '%s' "$RUN_ID" | tr '[:upper:]' '[:lower:]' | tr -cs 'a-z0-9_.-' '-')"

NETWORK="mascr-$SAFE_ID"
CFS="mascr-$SAFE_ID-cfs"
GATEWAY="mascr-$SAFE_ID-wp8-gateway"

EVIDENCE="$ROOT/results/wp8/runtime-binding/command/$RUN_ID"
GROUND="$EVIDENCE/immutable-ground"
OBS="$EVIDENCE/runtime-observation"

FACTOR_JSON="$GROUND/factor-context.json"
EVENT_JSON="$GROUND/event-instance.json"
EVENT_SEND_JSON="$GROUND/event-activation-send.json"
POLICY_JSON="$GROUND/policy-decision.json"
INGRESS_JSONL="$GROUND/gateway-ingress.jsonl"
DECISION_JSONL="$GROUND/gateway-decisions.jsonl"
ATTACKER1_JSON="$GROUND/attacker-reset-probe-1.json"
ATTACKER2_JSON="$GROUND/attacker-reset-probe-2.json"
AUTHORIZED_JSON="$GROUND/authorized-noop-probe.json"
SUMMARY_JSON="$GROUND/command-observation-summary.json"
OBSERVATION_JSON="$EVIDENCE/runtime-binding-observation.json"
RUN_RECORD="$EVIDENCE/run-record.json"
PROVENANCE="$EVIDENCE/binding-provenance.json"

NOMINAL_EVIDENCE="$ROOT/artifacts/runtime/$RUN_ID"
NOMINAL_LOG="$OBS/nominal-runtime.log"
RUNTIME_MANIFEST="$NOMINAL_EVIDENCE/runtime-manifest.txt"

PILOT_CONFIG="$ROOT/configs/wp8_pilot_design.json"
TOOLCHAIN="$ROOT/configs/toolchain-lock.json"
SCHEMA="$ROOT/configs/experiment_run.schema.json"

PRE_PID=""
RESULT="RUN_INVALID"
PHASE="INITIALIZATION"

mono_ns() {
  python3 -c 'import time; print(time.monotonic_ns())'
}

count_reset_marker() {
  docker logs "$CFS" 2>&1 |
    grep -Fc 'SAMPLE: RESET counters command received' || true
}

count_noop_marker() {
  docker logs "$CFS" 2>&1 |
    grep -Fc 'SAMPLE: NOOP command received' || true
}

wait_exact_delta() {
  local counter="$1" before="$2" delta="$3" label="$4"
  local now
  for _ in $(seq 1 75); do
    now="$("$counter")"
    if [[ "$now" -eq $((before + delta)) ]]; then
      printf '%s\n' "$now"
      return 0
    fi
    if [[ "$now" -gt $((before + delta)) ]]; then
      echo "[ERROR] $label exceeded expected marker delta" >&2
      return 2
    fi
    sleep 0.2
  done
  now="$("$counter")"
  echo "[ERROR] $label timeout: before=$before now=$now delta=$delta" >&2
  return 1
}

decision_count() {
  python3 - "$DECISION_JSONL" <<'PY'
import json
import sys
from pathlib import Path

path = Path(sys.argv[1])
if not path.exists():
    print(0)
else:
    print(sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip()))
PY
}

wait_decision_count() {
  local expected="$1"
  local now
  for _ in $(seq 1 75); do
    now="$(decision_count)"
    if [[ "$now" -eq "$expected" ]]; then
      return 0
    fi
    if [[ "$now" -gt "$expected" ]]; then
      echo "[ERROR] gateway decision count exceeded $expected" >&2
      return 2
    fi
    sleep 0.2
  done
  echo "[ERROR] gateway decision count did not reach $expected" >&2
  return 1
}

emit_invalid_record() {
  local rc="$1"
  [[ -f "$RUN_RECORD" ]] && return 0
  [[ -f "$FACTOR_JSON" ]] || return 0

  PYTHONPATH="$ROOT" python3 - \
    "$FACTOR_JSON" "$TOOLCHAIN" "$RUN_RECORD" "$PROVENANCE" \
    "$PHASE" "$rc" "$REPO_COMMIT" <<'PY'
import json
import sys
from pathlib import Path

from src.mission_recovery.wp8_runtime_binding import (
    bind_invalid_runtime_observation,
    environment_from_toolchain_lock,
)

factor_path, toolchain_path, run_path, prov_path, phase, rc, commit = sys.argv[1:]
factor = json.loads(Path(factor_path).read_text(encoding="utf-8"))
toolchain = json.loads(Path(toolchain_path).read_text(encoding="utf-8"))

environment = environment_from_toolchain_lock(
    toolchain,
    snapshot_id=f"repo-{commit}",
)

bundle = bind_invalid_runtime_observation(
    factor_context=factor,
    environment=environment,
    invalid_run_reason=f"wp8_command_binding_preflight_failed:{phase}:rc={rc}",
    source_observation_refs=[
        f"results/wp8/runtime-binding/command/{factor['run_id']}/runtime-observation/nominal-runtime.log",
    ],
    notes="Non-pilot command-family runtime-binding development preflight.",
)

Path(run_path).write_text(
    json.dumps(bundle["run_record"], sort_keys=True, indent=2) + "\n",
    encoding="utf-8",
)
Path(prov_path).write_text(
    json.dumps(bundle["binding_provenance"], sort_keys=True, indent=2) + "\n",
    encoding="utf-8",
)
print("invalid_run_record_retained=true")
print("fabricated_primary_metrics=false")
PY
}

cleanup() {
  local rc=$?
  set +e

  docker rm -f "$GATEWAY" >/dev/null 2>&1 || true

  if [[ -n "$PRE_PID" ]] && kill -0 "$PRE_PID" >/dev/null 2>&1; then
    kill -TERM "$PRE_PID" >/dev/null 2>&1 || true
    wait "$PRE_PID" >/dev/null 2>&1 || true
  fi

  if [[ "$RESULT" != "PASS" || "$rc" -ne 0 ]]; then
    emit_invalid_record "$rc" || true
    echo "WP8_COMMAND_BINDING_PREFLIGHT=FAIL" >&2
    echo "failed_phase=$PHASE" >&2
    echo "evidence_directory=$EVIDENCE" >&2
  else
    echo "WP8_COMMAND_BINDING_PREFLIGHT=PASS"
    echo "development_preflight=true"
    echo "pilot_data=false"
    echo "evidence_directory=$EVIDENCE"
  fi
}
trap cleanup EXIT
trap 'exit 130' INT TERM

cd "$ROOT"

test -z "$(git status --short)" || {
  echo "[ERROR] repository worktree must be clean before development preflight" >&2
  exit 1
}

REPO_COMMIT="$(git rev-parse HEAD)"
RUNNER_SHA="$(shasum -a 256 "$0" | awk '{print $1}')"

mkdir -p "$GROUND" "$OBS"
: > "$INGRESS_JSONL"
: > "$DECISION_JSONL"

PHASE="FACTOR_AND_EVENT_MATERIALIZATION"

PYTHONPATH="$ROOT" python3 - \
  "$FACTOR_JSON" "$EVENT_JSON" "$RUN_ID" "$SEED" <<'PY'
import json
import sys
from pathlib import Path

from src.mission_recovery.events import materialize_event

factor_path, event_path, run_id, seed = sys.argv[1:]

factor = {
    "run_id": run_id,
    "model_version": "0.3.0",
    "seed": int(seed),
    "mission_state_id": "M0",
    "event_id": "E1",
    "policy_id": "P1",
    "contact_condition_id": "C0",
    "evidence_condition_id": "T0",
}

event = materialize_event(
    "E1",
    mission_state="M0",
    contact_condition="C0",
    evidence_condition="T0",
    seed=int(seed),
)

Path(factor_path).write_text(
    json.dumps(factor, sort_keys=True, indent=2) + "\n",
    encoding="utf-8",
)
Path(event_path).write_text(
    json.dumps(event, sort_keys=True, indent=2) + "\n",
    encoding="utf-8",
)

print("development_seed=9101")
print("pilot_seed_consumed=false")
print("factor_event_materialization=PASS")
PY

PHASE="NOMINAL_RUNTIME_LAUNCH"

RUN_ID="$RUN_ID" \
DURATION_SECONDS=60 \
STARTUP_GRACE_SECONDS=20 \
bash "$ROOT/scripts/run_nominal_runtime_preflight.sh" \
  >"$NOMINAL_LOG" 2>&1 &
PRE_PID=$!

echo "nominal_runtime_launch=PASS"

PHASE="CFS_READINESS"

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

CI_READY=0
for _ in $(seq 1 90); do
  kill -0 "$PRE_PID" >/dev/null 2>&1 || break
  if docker exec "$CFS" sh -lc \
    "cat /proc/net/udp /proc/net/udp6 2>/dev/null | awk '\$2 ~ /:1394$/ {found=1} END {exit found ? 0 : 1}'" \
    >/dev/null 2>&1
  then
    CI_READY=1
    break
  fi
  sleep 1
done
[[ "$CI_READY" -eq 1 ]]

[[ "$(docker network inspect "$NETWORK" --format '{{.Internal}}')" == true ]]
[[ -z "$(docker port "$CFS")" ]]

echo "nominal_cfs_running=PASS"
echo "nominal_ci_lab_udp_5012=PASS"
echo "nominal_isolation=PASS"

RUN_START_NS="$(mono_ns)"
RUN_START_UTC="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

PHASE="EVENT_ACTIVATION"

RESET_BEFORE_EVENT="$(count_reset_marker)"
EVENT_ACTIVATION_NS="$(mono_ns)"

docker run --rm --platform linux/amd64 \
  --network "$NETWORK" \
  --env PYTHONPATH=/research \
  --mount "type=bind,source=$ROOT/src,target=/research/src,readonly" \
  --mount "type=bind,source=$GROUND,target=/evidence" \
  "$IMAGE" \
  python3 -m src.mission_recovery.nos3_e1_adapter \
    --event-json /evidence/event-instance.json \
    --command-class sample_reset_counters \
    --result-json /evidence/event-activation-send.json

RESET_AFTER_EVENT="$(
  wait_exact_delta count_reset_marker "$RESET_BEFORE_EVENT" 1 event_activation_reset
)"
EVENT_SUCCESS_NS="$(mono_ns)"

python3 - "$EVENT_SEND_JSON" <<'PY'
import json
import sys
from pathlib import Path

row = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
assert row["command_class"] == "sample_reset_counters"
assert row["target"] == "nos-fsw:5012"
assert row["packet_sha256"] == (
    "c8a8692bad90aab74ffe550c87e93ed83838d4b4f45c57a609a00455292d41cb"
)
print("e1_direct_reset_activation=PASS")
PY

test "$EVENT_SUCCESS_NS" -ge "$EVENT_ACTIVATION_NS"

echo "event_activation_before_response=true"
echo "event_success_observed=true"
echo "reset_marker_delta_event=1"

PHASE="POLICY_SELECTION"

PYTHONPATH="$ROOT" python3 - "$EVENT_JSON" "$POLICY_JSON" <<'PY'
import json
import sys
from pathlib import Path

from src.mission_recovery.policies import evaluate_policy

event = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
decision = evaluate_policy("P1", event)

assert decision["delegated_policy_id"] == "P1"
assert decision["selected_action"] == "ISOLATE_MODELED_SOURCE"

Path(sys.argv[2]).write_text(
    json.dumps(decision, sort_keys=True, indent=2) + "\n",
    encoding="utf-8",
)

print("p1_policy_selection=PASS")
PY

POLICY_SELECTION_NS="$(mono_ns)"
test "$POLICY_SELECTION_NS" -ge "$EVENT_SUCCESS_NS"

PHASE="POLICY_ENFORCEMENT"

docker run -d --platform linux/amd64 \
  --name "$GATEWAY" \
  --hostname wp8-gateway \
  --network "$NETWORK" \
  --network-alias wp8-gateway \
  --env PYTHONPATH=/research \
  --mount "type=bind,source=$ROOT/src,target=/research/src,readonly" \
  --mount "type=bind,source=$GROUND,target=/evidence" \
  "$IMAGE" \
  python3 -m src.mission_recovery.policy_gateway serve \
    --action ISOLATE_MODELED_SOURCE \
    --isolated-source modeled_attacker \
    --truth-jsonl /evidence/gateway-ingress.jsonl \
    --decision-jsonl /evidence/gateway-decisions.jsonl >/dev/null

GATEWAY_READY=0
HEX_GATEWAY_PORT="$(printf '%04X' 19091)"
for _ in $(seq 1 75); do
  if [[ "$(docker inspect "$GATEWAY" --format '{{.State.Status}}' 2>/dev/null || echo missing)" == running ]] &&
     docker exec "$GATEWAY" sh -lc \
       "awk '\$2 ~ /:${HEX_GATEWAY_PORT}$/ {found=1} END {exit found ? 0 : 1}' /proc/net/udp" \
       >/dev/null 2>&1
  then
    GATEWAY_READY=1
    break
  fi
  sleep 0.2
done
[[ "$GATEWAY_READY" -eq 1 ]] || {
  echo "[ERROR] WP8 gateway did not become ready" >&2
  docker logs "$GATEWAY" 2>&1 | tail -80 >&2 || true
  exit 1
}

POLICY_ENFORCEMENT_NS="$(mono_ns)"
test "$POLICY_ENFORCEMENT_NS" -ge "$POLICY_SELECTION_NS"

echo "policy_gateway_ready=PASS"
echo "policy_enforcement_after_event=true"

send_gateway_command() {
  local source_id="$1" command_class="$2" result_file="$3"
  docker run --rm --platform linux/amd64 \
    --network "$NETWORK" \
    --env PYTHONPATH=/research \
    --mount "type=bind,source=$ROOT/src,target=/research/src,readonly" \
    --mount "type=bind,source=$GROUND,target=/evidence" \
    "$IMAGE" \
    python3 -m src.mission_recovery.policy_gateway send \
      --source-id "$source_id" \
      --command-class "$command_class" \
      --gateway-host wp8-gateway \
      --result-json "/evidence/$result_file"
}

PHASE="POST_ENFORCEMENT_CONTAINMENT_PROBES"

RESET_BEFORE_CONTAINMENT="$(count_reset_marker)"

send_gateway_command \
  modeled_attacker sample_reset_counters \
  "$(basename "$ATTACKER1_JSON")"
wait_decision_count 1
sleep 0.4
test "$(count_reset_marker)" -eq "$RESET_BEFORE_CONTAINMENT"

send_gateway_command \
  modeled_attacker sample_reset_counters \
  "$(basename "$ATTACKER2_JSON")"
wait_decision_count 2
sleep 0.4

RESET_AFTER_CONTAINMENT="$(count_reset_marker)"
test "$RESET_AFTER_CONTAINMENT" -eq "$RESET_BEFORE_CONTAINMENT"

python3 - "$DECISION_JSONL" <<'PY'
import json
import sys
from pathlib import Path

rows = [
    json.loads(line)
    for line in Path(sys.argv[1]).read_text(encoding="utf-8").splitlines()
    if line.strip()
]
assert len(rows) == 2, rows
for row in rows:
    assert row["source_id"] == "modeled_attacker"
    assert row["command_class"] == "sample_reset_counters"
    assert row["forwarded"] is False
    assert row["action"] == "ISOLATE_MODELED_SOURCE"

print("two_matched_attacker_reset_probes_blocked=PASS")
PY

CONTAINMENT_NS="$(mono_ns)"
test "$CONTAINMENT_NS" -ge "$POLICY_ENFORCEMENT_NS"

echo "containment_predicate_observed=true"
echo "post_enforcement_attacker_reset_marker_delta=0"

PHASE="AUTHORIZED_SERVICE_PROBE"

NOOP_BEFORE="$(count_noop_marker)"

send_gateway_command \
  authorized_ground sample_noop \
  "$(basename "$AUTHORIZED_JSON")"
wait_decision_count 3

NOOP_AFTER="$(
  wait_exact_delta count_noop_marker "$NOOP_BEFORE" 1 authorized_noop
)"

python3 - "$DECISION_JSONL" <<'PY'
import json
import sys
from pathlib import Path

rows = [
    json.loads(line)
    for line in Path(sys.argv[1]).read_text(encoding="utf-8").splitlines()
    if line.strip()
]
assert len(rows) == 3, rows
row = rows[2]
assert row["source_id"] == "authorized_ground"
assert row["command_class"] == "sample_noop"
assert row["forwarded"] is True
assert row["action"] == "ISOLATE_MODELED_SOURCE"

print("authorized_noop_forwarded=PASS")
PY

echo "authorized_noop_marker_delta=1"
echo "legitimate_commands_attempted=1"
echo "legitimate_commands_rejected=0"

docker rm -f "$GATEWAY" >/dev/null

PHASE="NOMINAL_RUNTIME_COMPLETION"

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
test -f "$RUNTIME_MANIFEST"

RUN_END_NS="$(mono_ns)"
RUN_END_UTC="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

echo "validated_nominal_runtime_pass=true"

PHASE="OBSERVATION_BINDING"

REL="results/wp8/runtime-binding/command/$RUN_ID"

python3 - \
  "$FACTOR_JSON" "$SUMMARY_JSON" "$OBSERVATION_JSON" \
  "$RUN_START_NS" "$EVENT_ACTIVATION_NS" "$EVENT_SUCCESS_NS" \
  "$POLICY_SELECTION_NS" "$POLICY_ENFORCEMENT_NS" "$CONTAINMENT_NS" \
  "$RUN_END_NS" "$RUN_START_UTC" "$RUN_END_UTC" \
  "$RESET_BEFORE_EVENT" "$RESET_AFTER_EVENT" \
  "$RESET_BEFORE_CONTAINMENT" "$RESET_AFTER_CONTAINMENT" \
  "$NOOP_BEFORE" "$NOOP_AFTER" \
  "$RUNNER_SHA" "$REPO_COMMIT" "$REL" <<'PY'
import json
import sys
from pathlib import Path

(
    factor_path,
    summary_path,
    observation_path,
    run_start_ns,
    event_activation_ns,
    event_success_ns,
    policy_selection_ns,
    policy_enforcement_ns,
    containment_ns,
    run_end_ns,
    run_start_utc,
    run_end_utc,
    reset_before_event,
    reset_after_event,
    reset_before_containment,
    reset_after_containment,
    noop_before,
    noop_after,
    runner_sha,
    repo_commit,
    rel,
) = sys.argv[1:]

factor = json.loads(Path(factor_path).read_text(encoding="utf-8"))

numbers = {
    key: int(value)
    for key, value in {
        "run_start_ns": run_start_ns,
        "event_activation_ns": event_activation_ns,
        "event_success_ns": event_success_ns,
        "policy_selection_ns": policy_selection_ns,
        "policy_enforcement_ns": policy_enforcement_ns,
        "containment_ns": containment_ns,
        "run_end_ns": run_end_ns,
    }.items()
}

assert (
    numbers["run_start_ns"]
    <= numbers["event_activation_ns"]
    <= numbers["event_success_ns"]
    <= numbers["policy_selection_ns"]
    <= numbers["policy_enforcement_ns"]
    <= numbers["containment_ns"]
    <= numbers["run_end_ns"]
)

counts = {
    "reset_before_event": int(reset_before_event),
    "reset_after_event": int(reset_after_event),
    "reset_before_containment": int(reset_before_containment),
    "reset_after_containment": int(reset_after_containment),
    "noop_before": int(noop_before),
    "noop_after": int(noop_after),
}

assert counts["reset_after_event"] - counts["reset_before_event"] == 1
assert (
    counts["reset_after_containment"]
    - counts["reset_before_containment"]
    == 0
)
assert counts["noop_after"] - counts["noop_before"] == 1

summary = {
    "schema": 1,
    "classification": "WP8_COMMAND_RUNTIME_BINDING_DEVELOPMENT_PASS",
    "development_preflight": True,
    "pilot_data": False,
    "seed": factor["seed"],
    "repo_commit": repo_commit,
    "runner_sha256": runner_sha,
    "event_before_response_order": True,
    "event_reset_marker_delta": 1,
    "post_enforcement_attacker_reset_marker_delta": 0,
    "matched_attacker_reset_probe_count": 2,
    "authorized_noop_marker_delta": 1,
    "legitimate_commands_attempted": 1,
    "legitimate_commands_rejected": 0,
    "clock_ns": numbers,
}

Path(summary_path).write_text(
    json.dumps(summary, sort_keys=True, indent=2) + "\n",
    encoding="utf-8",
)

recovery_applicable = {
    "authorization_valid": {
        "available_current": True,
        "evidence_ref": f"{rel}/immutable-ground/gateway-decisions.jsonl",
    },
    "authorized_command_path_restored": {
        "available_current": True,
        "evidence_ref": f"{rel}/immutable-ground/command-observation-summary.json",
    },
    "ground_spacecraft_state_agreed": {
        "available_current": True,
        "evidence_ref": f"{rel}/immutable-ground/command-observation-summary.json",
    },
    "health_checks_passed": {
        "available_current": True,
        "evidence_ref": f"artifacts/runtime/{factor['run_id']}/runtime-manifest.txt",
    },
    "no_residual_unauthorized_state": {
        "available_current": True,
        "evidence_ref": f"{rel}/immutable-ground/command-observation-summary.json",
    },
    "recovery_manifest_complete": {
        "available_current": True,
        "evidence_ref": f"{rel}/immutable-ground/command-observation-summary.json",
    },
}

excluded = [
    "approved_version",
    "integrity_measurement_valid",
    "measured_state_current",
    "required_telemetry_restored",
]

observation = {
    "factor_context": factor,
    "runtime_observation": {
        "family": "command",
        "clock": {
            "run_start_utc": run_start_utc,
            "run_end_utc": run_end_utc,
            "run_start_ns": numbers["run_start_ns"],
            "event_activation_ns": numbers["event_activation_ns"],
            "containment_ns": numbers["containment_ns"],
            "trusted_recovery_ns": None,
            "run_end_ns": numbers["run_end_ns"],
        },
        "event_success": {
            "predicate": True,
            "observed_ns": numbers["event_success_ns"],
            "evidence_ref": f"{rel}/immutable-ground/command-observation-summary.json",
        },
        "objective_results": {
            "MO-1": {
                "completed": False,
                "evidence_ref": f"{rel}/immutable-ground/command-observation-summary.json",
            },
            "MO-3": {
                "completed": True,
                "evidence_ref": f"{rel}/immutable-ground/command-observation-summary.json",
            },
        },
        "invariant_violation_intervals": [],
        "legitimate_commands": {
            "attempted": 1,
            "rejected": 0,
            "evidence_ref": f"{rel}/immutable-ground/gateway-decisions.jsonl",
        },
        "ground_spacecraft_divergence_intervals": [
            {
                "state_key": "command_authority",
                "start_ns": numbers["event_success_ns"],
                "end_ns": numbers["containment_ns"],
            }
        ],
        "recovery_observations": recovery_applicable,
        "recovery_checklist_excluded": excluded,
        "terminal_state_predicates": {
            "run_invalid": False,
            "mission_loss": False,
            "trusted_recovery_confirmed": False,
            "operational_restored": True,
            "recovery_failed": False,
            "contained": True,
        },
        "containment_evidence_ref": f"{rel}/immutable-ground/command-observation-summary.json",
        "trusted_recovery_evidence_ref": None,
        "terminal_state_evidence_refs": [
            f"{rel}/immutable-ground/command-observation-summary.json",
            f"artifacts/runtime/{factor['run_id']}/runtime-manifest.txt",
        ],
        "source_observation_refs": [
            f"{rel}/immutable-ground/event-instance.json",
            f"{rel}/immutable-ground/event-activation-send.json",
            f"{rel}/immutable-ground/policy-decision.json",
            f"{rel}/immutable-ground/gateway-ingress.jsonl",
            f"{rel}/immutable-ground/gateway-decisions.jsonl",
            f"{rel}/immutable-ground/command-observation-summary.json",
            f"artifacts/runtime/{factor['run_id']}/runtime-manifest.txt",
        ],
        "development_preflight": True,
    },
    "notes": (
        "WP8 command-family runtime-binding development preflight; "
        "not Stage-1 pilot data."
    ),
}

Path(observation_path).write_text(
    json.dumps(observation, sort_keys=True, indent=2) + "\n",
    encoding="utf-8",
)

print("command_runtime_observation_materialized=PASS")
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
  "$SCHEMA" "$RUN_RECORD" "$PROVENANCE" "$SUMMARY_JSON" <<'PY'
import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

schema = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
record = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
provenance = json.loads(Path(sys.argv[3]).read_text(encoding="utf-8"))
summary = json.loads(Path(sys.argv[4]).read_text(encoding="utf-8"))

errors = list(
    Draft202012Validator(
        schema,
        format_checker=FormatChecker(),
    ).iter_errors(record)
)
assert not errors, [error.message for error in errors]

assert record["run_id"].endswith("-wp8-command-binding-dev")
assert record["seed"] == 9101
assert record["event_id"] == "E1"
assert record["policy_id"] == "P1"
assert record["terminal_state"] == "OPERATIONAL_BUT_UNVERIFIED"

assert record["outcomes"]["unauthorized_effect_completed"] is True
assert record["outcomes"]["mission_objective_completion_ratio"] == 0.5
assert record["outcomes"]["safety_invariant_violations"] == []
assert record["outcomes"]["legitimate_command_rejection_rate"] == 0.0
assert record["outcomes"]["evidence_completeness_ratio"] == 1.0
assert record["outcomes"]["ground_spacecraft_state_divergence_s"] > 0.0

assert record["timing"]["containment_s"] is not None
assert record["timing"]["containment_s"] > 0.0
assert record["timing"]["verified_recovery_s"] is None

assert provenance["development_preflight"] is True
assert provenance["pilot_data"] is False
assert summary["development_preflight"] is True
assert summary["pilot_data"] is False
assert summary["event_before_response_order"] is True
assert summary["matched_attacker_reset_probe_count"] == 2

print("schema_valid_command_bound_run_record=PASS")
print("event_before_response_runtime_order=PASS")
print("unauthorized_effect_observed=true")
print("containment_observed=true")
print("mission_objective_completion_ratio=0.5")
print("legitimate_command_rejection_rate=0.0")
print("development_preflight=true")
print("pilot_data=false")
PY

RESULT="PASS"
PHASE="COMPLETE"
