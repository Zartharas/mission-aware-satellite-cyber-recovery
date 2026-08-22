#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
IMAGE="ivvitc/nos3-64@sha256:06aa945988a7770b759022c2e1f6f2531818c087fe41a4739d3a3a7f2a9dcce2"
DEVELOPMENT_CONTACT_WINDOW_SECONDS=2

[[ "$#" -eq 1 ]] || {
  echo "usage: WP9B2_CONFIRM=EXECUTE-D01 $0 <D01|D02>" >&2
  exit 2
}
CASE_ID="$1"
case "$CASE_ID" in
  D01|D02) ;;
  *) echo "[ERROR] P6 development runner supports D01/D02 only" >&2; exit 2 ;;
esac

EXPECTED_CONFIRM="EXECUTE-$CASE_ID"
[[ "${WP9B2_CONFIRM:-}" == "$EXPECTED_CONFIRM" ]] || {
  echo "[ERROR] exact case confirmation required: WP9B2_CONFIRM=$EXPECTED_CONFIRM" >&2
  exit 2
}

cd "$ROOT"

for command in docker git python3 shasum; do
  command -v "$command" >/dev/null 2>&1 || {
    echo "[ERROR] missing command: $command" >&2
    exit 1
  }
done

test -z "$(git status --short)" || {
  echo "[ERROR] repository worktree must be clean before WP9-B2 P6 development runtime" >&2
  exit 1
}

PYTHONPATH="$ROOT" python3 -m src.mission_recovery.wp9b2_p6_development validate

docker info >/dev/null 2>&1 || {
  echo "[ERROR] Docker daemon unavailable" >&2
  exit 1
}
docker image inspect "$IMAGE" >/dev/null 2>&1 || {
  echo "[ERROR] pinned NOS3 image unavailable" >&2
  exit 1
}

echo "wp9b2_p6_docker_daemon=PASS"
echo "wp9b2_p6_pinned_image=PASS"

REPO_COMMIT="$(git rev-parse HEAD)"
SEED="$(
  python3 - "$ROOT/configs/wp9b2_development_cases.json" "$CASE_ID" <<'PY'
import json,sys
from pathlib import Path
data=json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
row=next(x for x in data["cases"] if x["case_id"]==sys.argv[2])
print(row["development_seed"])
PY
)"
RUN_ID="${RUN_ID:-$(date -u +%Y%m%dT%H%M%SZ)-wp9b2-${CASE_ID,,}-s${SEED}-$(python3 -c 'import uuid; print(uuid.uuid4().hex)')}"
SAFE_ID="$(printf '%s' "$RUN_ID" | tr '[:upper:]' '[:lower:]' | tr -cs 'a-z0-9_.-' '-')"
NETWORK="mascr-$SAFE_ID"
CFS="mascr-$SAFE_ID-cfs"

EVIDENCE="$ROOT/results/wp9/development/wp9b2/p6/$RUN_ID"
GROUND="$EVIDENCE/immutable-ground"
OBS="$EVIDENCE/runtime-observation"
PLAN_JSON="$GROUND/development-plan.json"
EVENT_JSON="$GROUND/event-instance.json"
PRE_POLICY_JSON="$GROUND/pre-authorization-policy-decision.json"
APPROVED="$GROUND/approved-update.pkg"
TAMPERED="$GROUND/tampered-update.pkg"
MANIFEST_JSON="$GROUND/approved-manifest.json"
TAMPERED_VERIFY_JSON="$GROUND/tampered-verification.json"
EVENT_OBS_JSON="$GROUND/event-activation-observation.json"
RUNTIME_POLICY_JSON="$GROUND/runtime-p6-policy-observation.json"
PRE_RELEASE_JSON="$GROUND/pre-release-authorization-probe.json"
AUTH_JSON="$GROUND/authorization-observation.json"
HANDOFF_JSON="$GROUND/p6-p5-handoff.json"
P5_POLICY_JSON="$GROUND/post-authorization-policy-decision.json"
ROLLBACK_REQUEST_JSON="$GROUND/rollback-request.json"
ROLLBACK_VALIDATION_JSON="$GROUND/rollback-request-validation.json"
REPLACEMENT_VERIFY_JSON="$GROUND/replacement-source-verification.json"
SUMMARY_JSON="$EVIDENCE/development-summary.json"
INVALID_JSON="$EVIDENCE/development-run-invalid.json"
NOMINAL_LOG="$OBS/nominal-runtime.log"
NOMINAL_EVIDENCE="$ROOT/artifacts/runtime/$RUN_ID"

CF_BACKING_DIR="/work/nos3/fsw/build/exe/cpu1/cf"
STAGE_BACKING="$CF_BACKING_DIR/mission-aware-wp9b2-p6-event.pkg"
TEMP_APPROVED="$CF_BACKING_DIR/mission-aware-wp9b2-p6-approved.tmp"

PRE_PID=""
RESULT="RUN_INVALID"
PHASE="INITIALIZATION"

mono_ns() {
  python3 -c 'import time; print(time.monotonic_ns())'
}

emit_invalid() {
  local rc="$1"
  [[ -d "$EVIDENCE" ]] || return 0
  [[ -f "$INVALID_JSON" ]] && return 0
  python3 - "$INVALID_JSON" "$RUN_ID" "$CASE_ID" "$SEED" "$PHASE" "$rc" "$REPO_COMMIT" <<'PY'
import json,sys
from pathlib import Path
path,run_id,case_id,seed,phase,rc,commit=sys.argv[1:]
Path(path).write_text(json.dumps({
    "schema":1,
    "classification":"WP9B2_P6_DEVELOPMENT_RUN_INVALID",
    "run_id":run_id,
    "case_id":case_id,
    "development_seed":int(seed),
    "failed_phase":phase,
    "exit_code":int(rc),
    "repo_commit":commit,
    "development_preflight":True,
    "development_runtime_data":False,
    "campaign_seed_consumed":False,
    "campaign_data":False,
    "experiment_failure_claimed":False,
    "automatic_next_case":False
},sort_keys=True,indent=2)+"\n",encoding="utf-8")
PY
}

cleanup() {
  local rc=$?
  set +e
  if docker inspect "$CFS" >/dev/null 2>&1; then
    docker exec "$CFS" rm -f "$STAGE_BACKING" "$TEMP_APPROVED" >/dev/null 2>&1 || true
  fi
  if [[ -n "$PRE_PID" ]] && kill -0 "$PRE_PID" >/dev/null 2>&1; then
    kill -TERM "$PRE_PID" >/dev/null 2>&1 || true
    wait "$PRE_PID" >/dev/null 2>&1 || true
  fi
  if [[ "$RESULT" == "PASS" && "$rc" -eq 0 ]]; then
    echo "WP9B2_P6_DEVELOPMENT_RUNTIME=PASS"
    echo "case_id=$CASE_ID"
    echo "development_seed=$SEED"
    echo "development_runtime_data=true"
    echo "campaign_seed_consumed=false"
    echo "campaign_data=false"
    echo "actual_recovery_execution_performed=false"
    echo "trusted_recovery_claim=false"
    echo "automatic_next_case=false"
    echo "evidence_directory=$EVIDENCE"
  else
    emit_invalid "$rc" || true
    echo "WP9B2_P6_DEVELOPMENT_RUNTIME=FAIL" >&2
    echo "case_id=$CASE_ID" >&2
    echo "failed_phase=$PHASE" >&2
    echo "evidence_directory=$EVIDENCE" >&2
  fi
  exit "$rc"
}
trap cleanup EXIT
trap 'exit 130' INT TERM

mkdir -p "$GROUND" "$OBS"

PHASE="DEVELOPMENT_PLAN"
PYTHONPATH="$ROOT" python3 -m src.mission_recovery.wp9b2_p6_development plan \
  --case-id "$CASE_ID" \
  --run-id "$RUN_ID" \
  --repo-commit "$REPO_COMMIT" \
  --output-plan-json "$PLAN_JSON" \
  --output-event-json "$EVENT_JSON" \
  --output-policy-json "$PRE_POLICY_JSON" \
  --output-approved "$APPROVED" \
  --output-tampered "$TAMPERED" \
  --output-manifest-json "$MANIFEST_JSON" \
  --output-tampered-verification-json "$TAMPERED_VERIFY_JSON"
echo "wp9b2_p6_development_plan=PASS"

PHASE="NOMINAL_RUNTIME_LAUNCH"
RUN_ID="$RUN_ID" DURATION_SECONDS=70 STARTUP_GRACE_SECONDS=20 \
  bash "$ROOT/scripts/run_nominal_runtime_preflight.sh" >"$NOMINAL_LOG" 2>&1 &
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

docker exec "$CFS" test -d "$CF_BACKING_DIR"
[[ "$(docker network inspect "$NETWORK" --format '{{.Internal}}')" == true ]]
[[ -z "$(docker port "$CFS")" ]]
docker exec "$CFS" rm -f "$STAGE_BACKING" "$TEMP_APPROVED"
echo "nominal_runtime_ready=PASS"
echo "nominal_isolation=PASS"

PHASE="E3_EVENT_ACTIVATION"
TAMPERED_SHA="$(shasum -a 256 "$TAMPERED" | awk '{print $1}')"
EVENT_ACTIVATION_NS="$(mono_ns)"
docker cp "$TAMPERED" "$CFS:$STAGE_BACKING"
OBSERVED_EVENT_SHA="$(
  docker exec "$CFS" sh -lc \
    "sha256sum '$STAGE_BACKING' | awk '{print \$1}'"
)"
[[ "$OBSERVED_EVENT_SHA" == "$TAMPERED_SHA" ]] || {
  echo "[ERROR] E3 event activation hash mismatch" >&2
  exit 1
}
python3 - "$EVENT_OBS_JSON" "$EVENT_ACTIVATION_NS" "$OBSERVED_EVENT_SHA" <<'PY'
import json,sys
from pathlib import Path
path,ns,sha=sys.argv[1:]
Path(path).write_text(json.dumps({
    "schema":1,
    "event_activation_observed":True,
    "event_activation_monotonic_ns":int(ns),
    "observed_sha256":sha,
    "observation_source":"runtime_cfs_staging_slot_sha256"
},sort_keys=True,indent=2)+"\n",encoding="utf-8")
PY
echo "e3_event_activation_observed=PASS"

PHASE="P6_RUNTIME_POLICY_OBSERVATION"
POLICY_OBS_NS="$(mono_ns)"
PYTHONPATH="$ROOT" python3 -m src.mission_recovery.wp9b2_p6_development observe-policy \
  --plan-json "$PLAN_JSON" \
  --observed-monotonic-ns "$POLICY_OBS_NS" \
  --output-json "$RUNTIME_POLICY_JSON"
echo "p6_wait_policy_observed=PASS"

RESPONSE_BOUNDARY_NS="$(mono_ns)"
[[ ! -e "$ROLLBACK_REQUEST_JSON" ]] || {
  echo "[ERROR] rollback request exists before authorization boundary" >&2
  exit 1
}

PHASE="SYNTHETIC_AUTHORIZATION_OBSERVATION"
if [[ "$CASE_ID" == "D01" ]]; then
  PRE_RELEASE_PROBE_PERFORMED=false
  PRE_RELEASE_AUTH_CURRENT=false
  RELEASE_AFTER_WINDOW_COUNT=0
  MISSED_WINDOWS=0
  AVAILABLE_AT_BOUNDARY=true
  AUTH_OBS_NS="$(mono_ns)"
  : > "$PRE_RELEASE_JSON"
else
  PRE_RELEASE_PROBE_PERFORMED=true
  PRE_RELEASE_AUTH_CURRENT=false
  RELEASE_AFTER_WINDOW_COUNT=1
  MISSED_WINDOWS=1
  AVAILABLE_AT_BOUNDARY=false
  PRE_PROBE_NS="$(mono_ns)"
  python3 - "$PRE_RELEASE_JSON" "$PRE_PROBE_NS" <<'PY'
import json,sys
from pathlib import Path
Path(sys.argv[1]).write_text(json.dumps({
    "schema":1,
    "pre_release_probe_performed":True,
    "observed_monotonic_ns":int(sys.argv[2]),
    "authorization_current":False,
    "rollback_request_exists":False
},sort_keys=True,indent=2)+"\n",encoding="utf-8")
PY
  [[ ! -e "$ROLLBACK_REQUEST_JSON" ]] || {
    echo "[ERROR] rollback request exists during D02 pre-release probe" >&2
    exit 1
  }
  RELEASE_DEADLINE_NS=$((RESPONSE_BOUNDARY_NS + DEVELOPMENT_CONTACT_WINDOW_SECONDS * 1000000000))
  while true; do
    NOW_NS="$(mono_ns)"
    [[ "$NOW_NS" -ge "$RELEASE_DEADLINE_NS" ]] && break
    sleep 0.05
  done
  [[ ! -e "$ROLLBACK_REQUEST_JSON" ]] || {
    echo "[ERROR] rollback request exists before D02 authorization release" >&2
    exit 1
  }
  AUTH_OBS_NS="$(mono_ns)"
fi

python3 - \
  "$AUTH_JSON" "$CASE_ID" "$RESPONSE_BOUNDARY_NS" "$AUTH_OBS_NS" \
  "$AVAILABLE_AT_BOUNDARY" "$MISSED_WINDOWS" "$PRE_RELEASE_PROBE_PERFORMED" \
  "$PRE_RELEASE_AUTH_CURRENT" "$RELEASE_AFTER_WINDOW_COUNT" <<'PY'
import json,sys
from pathlib import Path
(
 path,case_id,boundary_ns,observed_ns,available,missed,
 probe_performed,pre_current,release_count
)=sys.argv[1:]
contact="C0" if case_id=="D01" else "C1"
Path(path).write_text(json.dumps({
    "schema":1,
    "case_id":case_id,
    "source":"synthetic_ground_authorization_schedule",
    "contact_condition_id":contact,
    "response_boundary_monotonic_ns":int(boundary_ns),
    "authorization_observed_monotonic_ns":int(observed_ns),
    "available_at_response_boundary":available=="true",
    "missed_contact_windows":int(missed),
    "pre_release_probe_performed":probe_performed=="true",
    "pre_release_authorization_current":pre_current=="true",
    "release_after_modeled_window_count":int(release_count),
    "authorization_current":True,
    "rollback_request_exists_before_authorization":False,
    "development_contact_window_seconds":2,
    "development_contact_window_final_campaign_parameter":False,
    "real_human_operator_used":False,
    "real_world_ground_contact_used":False
},sort_keys=True,indent=2)+"\n",encoding="utf-8")
PY

echo "synthetic_authorization_observed=PASS"
echo "available_at_response_boundary=$AVAILABLE_AT_BOUNDARY"
echo "missed_contact_windows=$MISSED_WINDOWS"

PHASE="P6_TO_P5_HANDOFF"
HANDOFF_NS="$(mono_ns)"
PYTHONPATH="$ROOT" python3 -m src.mission_recovery.wp9b2_p6_development handoff \
  --plan-json "$PLAN_JSON" \
  --authorization-json "$AUTH_JSON" \
  --handoff-monotonic-ns "$HANDOFF_NS" \
  --output-json "$HANDOFF_JSON" \
  --output-p5-policy-json "$P5_POLICY_JSON" \
  --output-rollback-request-json "$ROLLBACK_REQUEST_JSON" \
  --output-rollback-validation-json "$ROLLBACK_VALIDATION_JSON" \
  --output-replacement-verification-json "$REPLACEMENT_VERIFY_JSON"
echo "p6_to_p5_handoff=PASS"

PHASE="APPROVED_REPLACEMENT_RUNTIME_STAGING"
APPROVED_SHA="$(shasum -a 256 "$APPROVED" | awk '{print $1}')"
docker cp "$APPROVED" "$CFS:$TEMP_APPROVED"
STAGED_APPROVED_SHA="$(
  docker exec "$CFS" sh -lc \
    "sha256sum '$TEMP_APPROVED' | awk '{print \$1}'"
)"
[[ "$STAGED_APPROVED_SHA" == "$APPROVED_SHA" ]] || {
  echo "[ERROR] staged approved replacement source hash mismatch" >&2
  exit 1
}
echo "approved_replacement_runtime_staging=PASS"

PHASE="P6_DEVELOPMENT_ACCEPTANCE"
PYTHONPATH="$ROOT" python3 -m src.mission_recovery.wp9b2_p6_development finalize \
  --plan-json "$PLAN_JSON" \
  --event-observation-json "$EVENT_OBS_JSON" \
  --runtime-policy-observation-json "$RUNTIME_POLICY_JSON" \
  --authorization-json "$AUTH_JSON" \
  --handoff-json "$HANDOFF_JSON" \
  --staged-approved-sha256 "$STAGED_APPROVED_SHA" \
  --output-summary-json "$SUMMARY_JSON"
echo "wp9b2_p6_acceptance=PASS"

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
test -f "$NOMINAL_EVIDENCE/runtime-manifest.txt"
echo "nominal_runtime_completion=PASS"

PHASE="CLEANUP_AUDIT"
RESIDUAL="$(docker ps --format '{{.Names}}' | grep -F "$SAFE_ID" || true)"
[[ -z "$RESIDUAL" ]] || {
  echo "[ERROR] residual WP9-B2 P6 runtime containers remain" >&2
  printf '%s\n' "$RESIDUAL" >&2
  exit 1
}
echo "residual_runtime=none"

RESULT="PASS"

echo "development_contact_window_s=$DEVELOPMENT_CONTACT_WINDOW_SECONDS"
echo "development_contact_window_final_campaign_parameter=false"
echo "actual_recovery_execution_performed=false"
echo "trusted_recovery_claim=false"
