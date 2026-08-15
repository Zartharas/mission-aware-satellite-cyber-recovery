#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
IMAGE="ivvitc/nos3-64@sha256:06aa945988a7770b759022c2e1f6f2531818c087fe41a4739d3a3a7f2a9dcce2"

RUN_SET_ID="${RUN_SET_ID:-$(date -u +%Y%m%dT%H%M%SZ)-wp6-p7}"
SET_DIR="$ROOT/results/wp6/p7/$RUN_SET_ID"
mkdir -p "$SET_DIR"

ACTIVE_PRE_PID=""
ACTIVE_CFS=""
ACTIVE_GATEWAY=""

cleanup_active() {
  set +e
  if [[ -n "$ACTIVE_GATEWAY" ]]; then
    docker rm -f "$ACTIVE_GATEWAY" >/dev/null 2>&1 || true
  fi
  if [[ -n "$ACTIVE_PRE_PID" ]] && kill -0 "$ACTIVE_PRE_PID" >/dev/null 2>&1; then
    kill -TERM "$ACTIVE_PRE_PID" >/dev/null 2>&1 || true
    wait "$ACTIVE_PRE_PID" >/dev/null 2>&1 || true
  fi
  ACTIVE_PRE_PID=""
  ACTIVE_CFS=""
  ACTIVE_GATEWAY=""
}

trap cleanup_active EXIT

count_noop_marker() {
  docker logs "$ACTIVE_CFS" 2>&1 |
    grep -Fc 'SAMPLE: NOOP command received' || true
}

wait_noop_exact() {
  local before="$1" delta="$2" label="$3"
  local now
  for _ in $(seq 1 15); do
    now="$(count_noop_marker)"
    if [[ "$now" -eq $((before + delta)) ]]; then
      printf '%s\n' "$now"
      return 0
    fi
    if [[ "$now" -gt $((before + delta)) ]]; then
      echo "[ERROR] $label exceeded expected NOOP delta" >&2
      return 2
    fi
    sleep 1
  done
  now="$(count_noop_marker)"
  echo "[ERROR] $label timeout: before=$before now=$now expected_delta=$delta" >&2
  return 1
}

prepare_decision() {
  local event_id="$1"
  local state="$2"
  local contact="$3"
  local evidence="$4"
  local expected_delegate="$5"
  local expected_action="$6"
  local event_json="$7"
  local decision_json="$8"
  local plan_json="$9"

  PYTHONPATH="$ROOT" python3 - \
    "$event_id" "$state" "$contact" "$evidence" \
    "$expected_delegate" "$expected_action" \
    "$event_json" "$decision_json" "$plan_json" <<'PY'
import copy, json, sys
from pathlib import Path

from src.mission_recovery.events import materialize_event
from src.mission_recovery.p7_effect_dispatch import build_p7_effect_plan
from src.mission_recovery.policies import evaluate_policy

(
    event_id,
    state,
    contact,
    evidence_condition,
    expected_delegate,
    expected_action,
    event_path,
    decision_path,
    plan_path,
)=sys.argv[1:]

event=materialize_event(
    event_id,
    mission_state=state,
    contact_condition=contact,
    evidence_condition=evidence_condition,
    seed=1,
)
decision=evaluate_policy("P7",event)
plan=build_p7_effect_plan(decision)

assert decision["requested_policy_id"]=="P7"
assert decision["delegated_policy_id"]==expected_delegate
assert decision["selected_action"]==expected_action
assert decision["oracle_ground_truth_read"] is False
assert plan["delegated_policy_id"]==expected_delegate
assert plan["selected_action"]==expected_action

changed=copy.deepcopy(event)
for key,value in list(changed["ground_truth"].items()):
    if isinstance(value,bool):
        changed["ground_truth"][key]=not value

mutated=evaluate_policy("P7",changed)
assert mutated==decision

Path(event_path).write_text(
    json.dumps(event,sort_keys=True,indent=2)+"\n",
    encoding="utf-8",
)
Path(decision_path).write_text(
    json.dumps(decision,sort_keys=True,indent=2)+"\n",
    encoding="utf-8",
)
Path(plan_path).write_text(
    json.dumps(plan,sort_keys=True,indent=2)+"\n",
    encoding="utf-8",
)

print("p7_decision=PASS")
print("p7_delegate="+decision["delegated_policy_id"])
print("p7_action="+decision["selected_action"])
print("p7_decision_basis="+decision["decision_basis"])
print("p7_evidence_insufficient="+str(decision["evidence_insufficient"]).lower())
print("p7_ground_truth_mutation_invariance=PASS")
print("p7_oracle_ground_truth_read=false")
PY
}

launch_nominal() {
  local run_id="$1"
  local nominal_log="$2"

  local safe_id
  safe_id="$(printf '%s' "$run_id" | tr '[:upper:]' '[:lower:]' | tr -cs 'a-z0-9_.-' '-')"

  ACTIVE_CFS="mascr-$safe_id-cfs"

  RUN_ID="$run_id" \
  DURATION_SECONDS=60 \
  STARTUP_GRACE_SECONDS=20 \
  bash "$ROOT/scripts/run_nominal_runtime_preflight.sh" \
    >"$nominal_log" 2>&1 &
  ACTIVE_PRE_PID=$!

  echo "nominal_runtime_launch=PASS"

  local ready=0 state
  for _ in $(seq 1 180); do
    kill -0 "$ACTIVE_PRE_PID" >/dev/null 2>&1 || break
    state="$(docker inspect "$ACTIVE_CFS" --format '{{.State.Status}}' 2>/dev/null || echo missing)"
    if [[ "$state" == running ]]; then
      ready=1
      break
    fi
    sleep 1
  done

  [[ "$ready" -eq 1 ]] || {
    echo "[ERROR] nominal cFS container not observed" >&2
    tail -120 "$nominal_log" >&2 || true
    return 1
  }

  echo "nominal_cfs_running=PASS"

  local network="mascr-$safe_id"
  [[ "$(docker network inspect "$network" --format '{{.Internal}}')" == true ]]
  [[ -z "$(docker port "$ACTIVE_CFS")" ]]
  echo "nominal_isolation=PASS"
}

finish_nominal() {
  local run_id="$1"
  local nominal_log="$2"

  set +e
  wait "$ACTIVE_PRE_PID"
  local rc=$?
  set -e
  ACTIVE_PRE_PID=""

  [[ "$rc" -eq 0 ]] || {
    echo "[ERROR] nominal runtime failed: rc=$rc" >&2
    tail -160 "$nominal_log" >&2 || true
    return 1
  }

  grep -Fq 'NOMINAL_RUNTIME_PREFLIGHT_STATUS=PASS' "$nominal_log"
  test -f "$ROOT/artifacts/runtime/$run_id/runtime-manifest.txt"

  echo "validated_nominal_runtime_pass=true"
}

run_command_case() {
  local case_id="$1"
  local state="$2"
  local contact="$3"
  local evidence="$4"
  local expected_delegate="$5"
  local expected_action="$6"
  local expected_attack_delta="$7"
  local expected_auth_delta="$8"

  local run_id="${RUN_SET_ID}-${case_id}"
  local safe_id
  safe_id="$(printf '%s' "$run_id" | tr '[:upper:]' '[:lower:]' | tr -cs 'a-z0-9_.-' '-')"

  local case_dir="$SET_DIR/$case_id"
  local ground="$case_dir/immutable-ground"
  local obs="$case_dir/runtime-observation"
  mkdir -p "$ground" "$obs"

  local event_json="$ground/event-instance.json"
  local decision_json="$ground/p7-decision.json"
  local plan_json="$ground/effect-plan.json"
  local ingress_jsonl="$ground/gateway-ingress.jsonl"
  local decisions_jsonl="$ground/gateway-decisions.jsonl"
  local attack_send="$ground/attacker-noop-send.json"
  local auth_send="$ground/authorized-noop-send.json"
  local summary="$case_dir/summary.json"
  local nominal_log="$obs/nominal-runtime.log"

  : > "$ingress_jsonl"
  : > "$decisions_jsonl"

  echo "============================================================"
  echo "P7_COMMAND_CASE=$case_id"
  echo "event_id=E1"
  echo "mission_state=$state"
  echo "contact_condition=$contact"
  echo "evidence_condition=$evidence"
  echo "expected_delegate=$expected_delegate"
  echo "============================================================"

  prepare_decision \
    E1 "$state" "$contact" "$evidence" \
    "$expected_delegate" "$expected_action" \
    "$event_json" "$decision_json" "$plan_json"

  launch_nominal "$run_id" "$nominal_log"

  local network="mascr-$safe_id"
  ACTIVE_GATEWAY="mascr-$safe_id-wp6-p7-gateway"

  docker run -d --platform linux/amd64 \
    --name "$ACTIVE_GATEWAY" \
    --hostname wp6-gateway \
    --network "$network" \
    --network-alias wp6-gateway \
    --env PYTHONPATH=/research \
    --mount "type=bind,source=$ROOT/src,target=/research/src,readonly" \
    --mount "type=bind,source=$ground,target=/evidence" \
    "$IMAGE" \
    python3 -m src.mission_recovery.policy_gateway serve \
      --action "$expected_action" \
      --isolated-source modeled_attacker \
      --truth-jsonl /evidence/gateway-ingress.jsonl \
      --decision-jsonl /evidence/gateway-decisions.jsonl >/dev/null

  local gateway_ready=0
  local hex_port
  hex_port="$(printf '%04X' 19091)"

  for _ in $(seq 1 15); do
    if [[ "$(docker inspect "$ACTIVE_GATEWAY" --format '{{.State.Status}}' 2>/dev/null || echo missing)" == running ]] && \
       docker exec "$ACTIVE_GATEWAY" sh -lc \
         "awk '\$2 ~ /:${hex_port}\$/ {found=1} END {exit found ? 0 : 1}' /proc/net/udp" \
         >/dev/null 2>&1
    then
      gateway_ready=1
      break
    fi
    sleep 1
  done

  [[ "$gateway_ready" -eq 1 ]] || {
    echo "[ERROR] P7 gateway did not bind UDP 19091" >&2
    docker logs "$ACTIVE_GATEWAY" 2>&1 | tail -80 >&2 || true
    return 1
  }

  [[ -z "$(docker port "$ACTIVE_GATEWAY")" ]]
  echo "p7_effect_gateway_ready=PASS"

  local baseline after_attack after_auth

  baseline="$(count_noop_marker)"

  docker run --rm --platform linux/amd64 \
    --network "$network" \
    --env PYTHONPATH=/research \
    --mount "type=bind,source=$ROOT/src,target=/research/src,readonly" \
    --mount "type=bind,source=$ground,target=/evidence" \
    "$IMAGE" \
    python3 -m src.mission_recovery.policy_gateway send \
      --source-id modeled_attacker \
      --command-class sample_noop \
      --gateway-host wp6-gateway \
      --result-json "/evidence/$(basename "$attack_send")"

  if [[ "$expected_attack_delta" -eq 1 ]]; then
    after_attack="$(wait_noop_exact "$baseline" 1 "${case_id}_attacker")"
  else
    sleep 3
    after_attack="$(count_noop_marker)"
    test "$after_attack" -eq "$baseline" || {
      echo "[ERROR] case $case_id attacker NOOP unexpectedly accepted" >&2
      return 1
    }
  fi
  echo "attacker_noop_acceptance_delta=$expected_attack_delta"

  docker run --rm --platform linux/amd64 \
    --network "$network" \
    --env PYTHONPATH=/research \
    --mount "type=bind,source=$ROOT/src,target=/research/src,readonly" \
    --mount "type=bind,source=$ground,target=/evidence" \
    "$IMAGE" \
    python3 -m src.mission_recovery.policy_gateway send \
      --source-id authorized_ground \
      --command-class sample_noop \
      --gateway-host wp6-gateway \
      --result-json "/evidence/$(basename "$auth_send")"

  if [[ "$expected_auth_delta" -eq 1 ]]; then
    after_auth="$(wait_noop_exact "$after_attack" 1 "${case_id}_authorized")"
  else
    sleep 3
    after_auth="$(count_noop_marker)"
    test "$after_auth" -eq "$after_attack" || {
      echo "[ERROR] case $case_id authorized NOOP unexpectedly accepted" >&2
      return 1
    }
  fi
  echo "authorized_noop_acceptance_delta=$expected_auth_delta"

  python3 - \
    "$ingress_jsonl" "$decisions_jsonl" \
    "$expected_delegate" "$expected_action" \
    "$expected_attack_delta" "$expected_auth_delta" <<'PY'
import json, sys
from pathlib import Path

def rows(path):
    return [
        json.loads(line)
        for line in Path(path).read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

ingress=rows(sys.argv[1])
decisions=rows(sys.argv[2])
delegate=sys.argv[3]
action=sys.argv[4]
attack_delta=int(sys.argv[5])
auth_delta=int(sys.argv[6])

assert len(ingress)==2,ingress
assert len(decisions)==2,decisions
assert [r["source_id"] for r in ingress]==[
    "modeled_attacker",
    "authorized_ground",
]
assert [r["command_class"] for r in ingress]==[
    "sample_noop",
    "sample_noop",
]
assert ingress[0]["packet_sha256"]==ingress[1]["packet_sha256"]
assert ingress[0]["packet_sha256"]=="722b8fe72fb18ee581c970ea92c100f435fa90ccccaf0a05bf3e8bee0c4d13bd"

assert all(r["action"]==action for r in decisions)
expected_forward=[bool(attack_delta),bool(auth_delta)]
actual=[r["forwarded"] for r in decisions]
assert actual==expected_forward,(delegate,actual,expected_forward)

print("p7_gateway_ingress_pair=PASS")
print("p7_gateway_effect_decisions=PASS")
print("p7_command_packet_identity=PASS")
PY

  docker rm -f "$ACTIVE_GATEWAY" >/dev/null
  ACTIVE_GATEWAY=""

  finish_nominal "$run_id" "$nominal_log"

  local runtime_sha
  runtime_sha="$(
    shasum -a 256 "$ROOT/artifacts/runtime/$run_id/runtime-manifest.txt" |
    awk '{print $1}'
  )"

  python3 - \
    "$event_json" "$decision_json" "$plan_json" \
    "$summary" "$case_id" \
    "$expected_attack_delta" "$expected_auth_delta" \
    "$runtime_sha" <<'PY'
import hashlib, json, sys
from pathlib import Path

event=json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
decision=json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
plan=json.loads(Path(sys.argv[3]).read_text(encoding="utf-8"))
case_id=sys.argv[5]
attack_delta=int(sys.argv[6])
auth_delta=int(sys.argv[7])
runtime_sha=sys.argv[8]

summary={
    "schema":1,
    "classification":"WP6_P7_COMMAND_EFFECT_CASE_PASS",
    "case_id":case_id,
    "event_id":event["event_id"],
    "mission_state":event["mission_state"],
    "contact_condition":event["contact_condition"],
    "evidence_condition":event["evidence_condition"],
    "seed":event["seed"],
    "event_instance_sha256":event["instance_sha256"],
    "p7_decision_sha256":decision["decision_sha256"],
    "delegated_policy_id":decision["delegated_policy_id"],
    "selected_action":decision["selected_action"],
    "decision_basis":decision["decision_basis"],
    "evidence_insufficient":decision["evidence_insufficient"],
    "effect_family":plan["effect_family"],
    "command_packet_sha256":"722b8fe72fb18ee581c970ea92c100f435fa90ccccaf0a05bf3e8bee0c4d13bd",
    "attacker_noop_acceptance_delta":attack_delta,
    "authorized_noop_acceptance_delta":auth_delta,
    "modeled_unauthorized_effect_completed":attack_delta==1,
    "legitimate_command_rejection_rate":0.0 if auth_delta==1 else 1.0,
    "validated_nominal_runtime_pass":True,
    "nominal_runtime_manifest_sha256":runtime_sha,
    "oracle_ground_truth_read":False,
    "ground_truth_mutation_invariance":True,
    "final_effect_size_claim":False,
    "mission_objective_completion_claim":False,
    "trusted_recovery_claim":False
}

encoded=(json.dumps(summary,sort_keys=True,indent=2)+"\n").encode()
Path(sys.argv[4]).write_bytes(encoded)
print("case_summary_sha256="+hashlib.sha256(encoded).hexdigest())
PY

  echo "P7_COMMAND_EFFECT_CASE=PASS"
  echo "case_id=$case_id"
  echo "delegated_policy=$expected_delegate"
  echo "modeled_unauthorized_effect_completed=$([[ "$expected_attack_delta" -eq 1 ]] && echo true || echo false)"
  echo "legitimate_command_rejection_rate=$([[ "$expected_auth_delta" -eq 1 ]] && echo 0.0 || echo 1.0)"

  cleanup_active
}

run_p5_case() {
  local case_id="E"
  local run_id="${RUN_SET_ID}-${case_id}"
  local safe_id
  safe_id="$(printf '%s' "$run_id" | tr '[:upper:]' '[:lower:]' | tr -cs 'a-z0-9_.-' '-')"

  local case_dir="$SET_DIR/$case_id"
  local ground="$case_dir/immutable-ground"
  local obs="$case_dir/runtime-observation"
  mkdir -p "$ground" "$obs"

  local event_json="$ground/event-instance.json"
  local decision_json="$ground/p7-decision.json"
  local plan_json="$ground/effect-plan.json"
  local approved="$ground/approved-update.pkg"
  local tampered="$ground/tampered-update.pkg"
  local manifest="$ground/approved-manifest.json"
  local verify="$ground/verify-tampered.json"
  local request="$ground/rollback-request.json"
  local summary="$case_dir/summary.json"
  local nominal_log="$obs/nominal-runtime.log"

  local cf_dir="/work/nos3/fsw/build/exe/cpu1/cf"
  local staged="$cf_dir/mission-aware-e3-candidate.pkg"
  local rollback="$cf_dir/mission-aware-p7-rollback.pkg"

  echo "============================================================"
  echo "P7_ROLLBACK_CASE=E"
  echo "event_id=E3"
  echo "mission_state=M4"
  echo "contact_condition=C0"
  echo "evidence_condition=T0"
  echo "expected_delegate=P5"
  echo "============================================================"

  prepare_decision \
    E3 M4 C0 T0 \
    P5 REQUEST_VERIFIED_ROLLBACK \
    "$event_json" "$decision_json" "$plan_json"

  PYTHONPATH="$ROOT" python3 - \
    "$approved" "$tampered" "$manifest" "$verify" <<'PY'
import json,sys
from pathlib import Path

from src.mission_recovery.update_artifacts import (
    build_approved_update,
    build_manifest,
    build_tampered_update,
    verify_candidate,
)

approved=build_approved_update()
tampered=build_tampered_update()
manifest=build_manifest()
verification=verify_candidate(tampered,manifest)

assert verification["accepted"] is False
assert "sha256_mismatch" in verification["reasons"]

Path(sys.argv[1]).write_bytes(approved)
Path(sys.argv[2]).write_bytes(tampered)
Path(sys.argv[3]).write_text(
    json.dumps(manifest,sort_keys=True,indent=2)+"\n",
    encoding="utf-8",
)
Path(sys.argv[4]).write_text(
    json.dumps(verification,sort_keys=True,indent=2)+"\n",
    encoding="utf-8",
)
PY

  local approved_sha tampered_sha
  approved_sha="$(shasum -a 256 "$approved" | awk '{print $1}')"
  tampered_sha="$(shasum -a 256 "$tampered" | awk '{print $1}')"

  test "$approved_sha" = "42945a2622fa351b3a3fdc31e002cbe326cb7a42a958ee757f317abea67b6697"
  test "$tampered_sha" = "ff96d61205cc2c49b6d7d73fc36b9544c0deea79d7a9304cc1fb9f1f8986053d"

  echo "approved_artifact_identity=PASS"
  echo "tampered_artifact_identity=PASS"

  launch_nominal "$run_id" "$nominal_log"

  docker exec "$ACTIVE_CFS" test -d "$cf_dir"
  docker exec "$ACTIVE_CFS" rm -f "$staged" "$rollback"
  docker cp "$tampered" "$ACTIVE_CFS:$staged"

  local staged_sha
  staged_sha="$(
    docker exec "$ACTIVE_CFS" sha256sum "$staged" |
    awk '{print $1}'
  )"
  test "$staged_sha" = "$tampered_sha"

  echo "p7_tampered_candidate_stage=PASS"

  PYTHONPATH="$ROOT" python3 - \
    "$event_json" "$decision_json" "$manifest" "$verify" "$request" <<'PY'
import json,sys
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

assert request["requested_policy_id"]=="P7"
assert request["delegated_policy_id"]=="P5"
assert request["action"]=="REQUEST_VERIFIED_ROLLBACK"
assert request["oracle_ground_truth_read"] is False
assert request["rollback_staging_performed"] is False
assert request["rollback_activation_performed"] is False
assert request["recovery_execution_performed"] is False
assert request["trusted_recovery_verified"] is False

Path(sys.argv[5]).write_text(
    json.dumps(request,sort_keys=True,indent=2)+"\n",
    encoding="utf-8",
)

print("p7_rollback_request_sha256="+request["request_sha256"])
PY

  test -f "$request"

  local staged_after
  staged_after="$(
    docker exec "$ACTIVE_CFS" sha256sum "$staged" |
    awk '{print $1}'
  )"
  test "$staged_after" = "$tampered_sha"
  docker exec "$ACTIVE_CFS" test ! -e "$rollback"

  echo "p7_rollback_request_created=true"
  echo "p7_tampered_candidate_remains_staged=true"
  echo "p7_approved_rollback_staged=false"
  echo "p7_rollback_activation_performed=false"
  echo "p7_recovery_execution_performed=false"
  echo "p7_trusted_recovery_verified=false"

  docker exec "$ACTIVE_CFS" rm -f "$staged"

  finish_nominal "$run_id" "$nominal_log"

  local runtime_sha request_file_sha
  runtime_sha="$(
    shasum -a 256 "$ROOT/artifacts/runtime/$run_id/runtime-manifest.txt" |
    awk '{print $1}'
  )"
  request_file_sha="$(shasum -a 256 "$request" | awk '{print $1}')"

  python3 - \
    "$event_json" "$decision_json" "$plan_json" "$request" \
    "$summary" "$approved_sha" "$tampered_sha" \
    "$runtime_sha" "$request_file_sha" <<'PY'
import hashlib,json,sys
from pathlib import Path

event=json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
decision=json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
plan=json.loads(Path(sys.argv[3]).read_text(encoding="utf-8"))
request=json.loads(Path(sys.argv[4]).read_text(encoding="utf-8"))

assert decision["delegated_policy_id"]=="P5"
assert plan["effect_family"]=="rollback_request"
assert request["approved_target_sha256"]==sys.argv[6]
assert request["rejected_candidate_sha256"]==sys.argv[7]

summary={
    "schema":1,
    "classification":"WP6_P7_ROLLBACK_REQUEST_CASE_PASS",
    "case_id":"E",
    "event_id":"E3",
    "mission_state":"M4",
    "contact_condition":"C0",
    "evidence_condition":"T0",
    "seed":1,
    "event_instance_sha256":event["instance_sha256"],
    "p7_decision_sha256":decision["decision_sha256"],
    "delegated_policy_id":"P5",
    "selected_action":"REQUEST_VERIFIED_ROLLBACK",
    "decision_basis":decision["decision_basis"],
    "effect_family":"rollback_request",
    "approved_target_sha256":sys.argv[6],
    "tampered_candidate_sha256":sys.argv[7],
    "rollback_request_file_sha256":sys.argv[9],
    "rollback_request_created":True,
    "tampered_candidate_remained_staged_during_observation":True,
    "approved_rollback_staged":False,
    "rollback_activation_performed":False,
    "recovery_execution_performed":False,
    "trusted_recovery_verified":False,
    "validated_nominal_runtime_pass":True,
    "nominal_runtime_manifest_sha256":sys.argv[8],
    "oracle_ground_truth_read":False,
    "ground_truth_mutation_invariance":True,
    "recovery_success_claim":False,
    "time_to_trusted_recovery_claim":False
}

encoded=(json.dumps(summary,sort_keys=True,indent=2)+"\n").encode()
Path(sys.argv[5]).write_bytes(encoded)
print("case_summary_sha256="+hashlib.sha256(encoded).hexdigest())
PY

  echo "P7_ROLLBACK_REQUEST_CASE=PASS"
  echo "case_id=E"
  echo "delegated_policy=P5"

  cleanup_active
}

docker info >/dev/null 2>&1
docker image inspect "$IMAGE" >/dev/null 2>&1

run_command_case A M0 C0 T0 P1 ISOLATE_MODELED_SOURCE 0 1
run_command_case B M0 C1 T0 P2 RESTRICT_HIGH_RISK_COMMANDS 1 1
run_command_case C M2 C0 T0 P2 RESTRICT_HIGH_RISK_COMMANDS 1 1
run_command_case D M2 C0 T1 P4 ENTER_SAFE_MODE 0 0
run_p5_case

python3 - "$SET_DIR" "$RUN_SET_ID" <<'PY'
import hashlib,json,sys
from pathlib import Path

root=Path(sys.argv[1])
run_set_id=sys.argv[2]

cases={}
for case_id in ("A","B","C","D","E"):
    cases[case_id]=json.loads(
        (root/case_id/"summary.json").read_text(encoding="utf-8")
    )

assert cases["A"]["delegated_policy_id"]=="P1"
assert cases["B"]["delegated_policy_id"]=="P2"
assert cases["C"]["delegated_policy_id"]=="P2"
assert cases["D"]["delegated_policy_id"]=="P4"
assert cases["E"]["delegated_policy_id"]=="P5"

# Contact-only contrast: A -> B.
for key in ("event_id","mission_state","evidence_condition","seed"):
    assert cases["A"][key]==cases["B"][key],key
assert cases["A"]["contact_condition"] != cases["B"]["contact_condition"]
assert cases["A"]["modeled_unauthorized_effect_completed"] is False
assert cases["B"]["modeled_unauthorized_effect_completed"] is True

# Mission-state-only contrast: A -> C.
for key in ("event_id","contact_condition","evidence_condition","seed"):
    assert cases["A"][key]==cases["C"][key],key
assert cases["A"]["mission_state"] != cases["C"]["mission_state"]
assert cases["A"]["modeled_unauthorized_effect_completed"] is False
assert cases["C"]["modeled_unauthorized_effect_completed"] is True

# Evidence-only contrast: C -> D.
for key in ("event_id","mission_state","contact_condition","seed"):
    assert cases["C"][key]==cases["D"][key],key
assert cases["C"]["evidence_condition"] != cases["D"]["evidence_condition"]
assert cases["C"]["modeled_unauthorized_effect_completed"] is True
assert cases["D"]["modeled_unauthorized_effect_completed"] is False
assert cases["C"]["legitimate_command_rejection_rate"]==0.0
assert cases["D"]["legitimate_command_rejection_rate"]==1.0

assert cases["E"]["rollback_request_created"] is True
assert cases["E"]["approved_rollback_staged"] is False
assert cases["E"]["recovery_execution_performed"] is False
assert cases["E"]["trusted_recovery_verified"] is False

assert all(c["oracle_ground_truth_read"] is False for c in cases.values())
assert all(c["ground_truth_mutation_invariance"] is True for c in cases.values())
assert all(c["validated_nominal_runtime_pass"] is True for c in cases.values())

summary={
    "schema":1,
    "classification":"WP6_P7_MISSION_AWARE_EFFECT_INTEGRATION_PASS",
    "run_set_id":run_set_id,
    "case_delegates":{
        case_id:cases[case_id]["delegated_policy_id"]
        for case_id in ("A","B","C","D","E")
    },
    "contact_only_contrast":{
        "left":"A",
        "right":"B",
        "delegate_change":"P1_to_P2",
        "unauthorized_effect_change":"false_to_true",
        "observed":True
    },
    "mission_state_only_contrast":{
        "left":"A",
        "right":"C",
        "delegate_change":"P1_to_P2",
        "unauthorized_effect_change":"false_to_true",
        "observed":True
    },
    "evidence_only_contrast":{
        "left":"C",
        "right":"D",
        "delegate_change":"P2_to_P4",
        "unauthorized_effect_change":"true_to_false",
        "legitimate_command_rejection_rate_change":"0.0_to_1.0",
        "observed":True
    },
    "p5_rollback_request_effect":{
        "request_created":True,
        "approved_rollback_staged":False,
        "recovery_execution_performed":False,
        "trusted_recovery_verified":False
    },
    "all_nominal_runtimes_pass":True,
    "oracle_ground_truth_read":False,
    "ground_truth_mutation_invariance":True,
    "negative_case_present":True,
    "final_effect_size_claim":False,
    "containment_latency_claim":False,
    "mission_objective_completion_claim":False,
    "trusted_recovery_claim":False
}

encoded=(json.dumps(summary,sort_keys=True,indent=2)+"\n").encode()
(root/"summary.json").write_bytes(encoded)
print("integration_summary_sha256="+hashlib.sha256(encoded).hexdigest())
PY

echo "wp6_p7_runtime_matrix=PASS"
echo "case_A_delegate=P1"
echo "case_B_delegate=P2"
echo "case_C_delegate=P2"
echo "case_D_delegate=P4"
echo "case_E_delegate=P5"
echo "contact_only_selector_effect_contrast=PASS"
echo "mission_state_only_selector_effect_contrast=PASS"
echo "evidence_only_selector_effect_contrast=PASS"
echo "negative_case_p7_allows_e1_effect_under_p2=true"
echo "p7_p4_legitimate_command_rejection_rate=1.0"
echo "p7_p5_recovery_execution_performed=false"
echo "oracle_ground_truth_read=false"
echo "ground_truth_mutation_invariance=PASS"
echo "all_nominal_runtimes_pass=true"
