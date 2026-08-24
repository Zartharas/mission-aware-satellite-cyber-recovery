#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

IMAGE="ivvitc/nos3-64@sha256:06aa945988a7770b759022c2e1f6f2531818c087fe41a4739d3a3a7f2a9dcce2"
CAMPAIGN_ROOT="$ROOT/results/wp9/campaign"
HISTORY="$CAMPAIGN_ROOT/attempt-history.json"

usage() {
  cat >&2 <<'EOF'
usage:
  run_wp9_r069_campaign_one_position.sh validate-static
  run_wp9_r069_campaign_one_position.sh run-once

run-once executes exactly the next frozen campaign position derived from the
retained attempt ledger. It never retries automatically and never executes the
following position automatically.
EOF
}

[[ "$#" -eq 1 ]] || {
  usage
  exit 2
}

COMMAND="$1"

validate_static() {
  ./scripts/run_wp9_r066_final_campaign_trial.sh validate-static
  PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$ROOT" python3 -m \
    src.mission_recovery.wp9_r069_campaign_one_position_operator \
    validate-static
}

runtime_safety_audit() {
  local run_id="$1"
  local safe_id="$2"
  local residual_containers=""
  local residual_networks=""
  local residual_aliases=""

  residual_containers="$(
    docker ps -a --format '{{.Names}}' 2>/dev/null |
      grep -F "$safe_id" || true
  )"
  residual_networks="$(
    docker network ls --format '{{.Name}}' 2>/dev/null |
      grep -F "$safe_id" || true
  )"
  residual_aliases="$(
    find results/wp9/development -type l -name "$run_id" -print 2>/dev/null || true
  )"

  if [[ -n "$residual_containers" ]]; then
    echo "[SAFETY WARNING] residual run containers:"
    printf '%s\n' "$residual_containers"
  else
    echo "residual_run_containers=none"
  fi

  if [[ -n "$residual_networks" ]]; then
    echo "[SAFETY WARNING] residual run networks:"
    printf '%s\n' "$residual_networks"
  else
    echo "residual_run_networks=none"
  fi

  if [[ -n "$residual_aliases" ]]; then
    echo "[SAFETY WARNING] compatibility evidence aliases remain:"
    printf '%s\n' "$residual_aliases"
  else
    echo "compatibility_alias_cleanup=PASS"
  fi

  [[ -z "$residual_containers" && -z "$residual_networks" && -z "$residual_aliases" ]]
}

case "$COMMAND" in
  validate-static)
    validate_static
    ;;

  run-once)
    echo
    echo "============================================================"
    echo "1. EXACT CURRENT MAIN / CLEAN WORKTREE"
    echo "============================================================"

    [[ "$(git rev-parse --abbrev-ref HEAD)" == "main" ]] || {
      echo "[BLOCKED] campaign operator must run from main"
      exit 10
    }

    [[ -z "$(git status --short)" ]] || {
      echo "[BLOCKED] tracked worktree is not clean"
      git status --short
      exit 11
    }

    git fetch origin main
    LOCAL_SHA="$(git rev-parse HEAD)"
    ORIGIN_SHA="$(git rev-parse origin/main)"
    LOCAL_TREE="$(git rev-parse HEAD^{tree})"

    echo "local_head_sha=$LOCAL_SHA"
    echo "origin_main_sha=$ORIGIN_SHA"
    echo "local_head_tree=$LOCAL_TREE"

    [[ "$LOCAL_SHA" == "$ORIGIN_SHA" ]] || {
      echo "[BLOCKED] local main is not the exact current origin/main"
      echo "Run: git pull --ff-only origin main"
      exit 12
    }

    echo "exact_current_main=PASS"
    echo "tracked_worktree=clean"

    echo
    echo "============================================================"
    echo "2. STATIC / CONTINUITY / SCHEMA CONTRACTS"
    echo "============================================================"

    validate_static

    echo
    echo "============================================================"
    echo "3. DOCKER / PINNED NOS3 / CLEAN SNAPSHOT"
    echo "============================================================"

    command -v docker >/dev/null 2>&1 || {
      echo "[BLOCKED] docker command unavailable"
      exit 13
    }
    docker info >/dev/null 2>&1 || {
      echo "[BLOCKED] Docker daemon unavailable"
      exit 14
    }
    docker image inspect "$IMAGE" >/dev/null 2>&1 || {
      echo "[BLOCKED] pinned NOS3 image unavailable"
      exit 15
    }

    PRE_CONTAINERS="$(
      docker ps -a --format '{{.Names}}' |
        grep -E '^mascr-' || true
    )"
    PRE_NETWORKS="$(
      docker network ls --format '{{.Name}}' |
        grep -E '^mascr-' || true
    )"

    [[ -z "$PRE_CONTAINERS" ]] || {
      echo "[BLOCKED] residual MASCR containers exist:"
      printf '%s\n' "$PRE_CONTAINERS"
      exit 16
    }
    [[ -z "$PRE_NETWORKS" ]] || {
      echo "[BLOCKED] residual MASCR networks exist:"
      printf '%s\n' "$PRE_NETWORKS"
      exit 17
    }

    echo "docker_daemon=PASS"
    echo "pinned_nos3_image=PASS"
    echo "clean_runtime_snapshot=PASS"

    TMP="$(mktemp -d /tmp/wp9-r069-one-position.XXXXXX)"
    trap 'rm -rf "$TMP"' EXIT

    echo
    echo "============================================================"
    echo "4. DERIVE EXACT NEXT FROZEN POSITION"
    echo "============================================================"

    RUN_ID_OVERRIDE="$(
      PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$ROOT" python3 - "$HISTORY" <<'PY'
import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

from src.mission_recovery.wp9_r064_attempt_history import (
    next_required_trial_from_attempt_history,
)

path = Path(sys.argv[1])
if path.exists():
    history = json.loads(path.read_text(encoding="utf-8"))
else:
    history = []
if not isinstance(history, list):
    raise ValueError("campaign attempt history must be a JSON array")
next_trial = next_required_trial_from_attempt_history(history)
if next_trial is None:
    raise ValueError("frozen campaign is already complete")
is_retry = bool(history and history[-1].get("attempt_status") == "INVALID")
stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
retry = "-retry" if is_retry else ""
print(
    f"{stamp}-wp9-r069-p{int(next_trial['global_order_index']):04d}{retry}-"
    f"s{int(next_trial['campaign_seed'])}-{str(next_trial['cell_id']).lower()}-"
    f"{uuid.uuid4().hex}"
)
PY
    )"

    [[ -n "$RUN_ID_OVERRIDE" ]] || {
      echo "[BLOCKED] unable to generate next run ID"
      exit 18
    }

    PREPARE_ARGS=(
      --attempt-history-json "$HISTORY"
      --campaign-root "$CAMPAIGN_ROOT"
      --current-repo-sha "$LOCAL_SHA"
      --run-id "$RUN_ID_OVERRIDE"
      --output-dir "$TMP/prepared"
    )

    PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$ROOT" python3 -m \
      src.mission_recovery.wp9_r069_campaign_one_position_operator \
      prepare-next "${PREPARE_ARGS[@]}"

    SUMMARY="$TMP/prepared/request-summary.json"
    REQUEST="$TMP/prepared/request.json"
    EXEC_OUT="$TMP/executor-return.json"

    eval "$(
      PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$ROOT" python3 - "$SUMMARY" "$REQUEST" <<'PY'
import json
import shlex
import sys
from pathlib import Path

summary = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
request = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
values = {
    "RUN_ID": summary["run_id"],
    "SEED": str(summary["campaign_seed"]),
    "CELL": summary["cell_id"],
    "GLOBAL_INDEX": str(summary["global_order_index"]),
    "CELL_ORDER_INDEX": str(summary["cell_order_index"]),
    "EVENT_ID": summary["event_id"],
    "RUNTIME_FAMILY": summary["runtime_family"],
    "RUNTIME_VARIANT": summary["runtime_variant"],
    "EVIDENCE": request["evidence_directory"],
}
for key, value in values.items():
    print(key + "=" + shlex.quote(str(value)))
PY
    )"

    SAFE_ID="$(
      printf '%s' "$RUN_ID" |
        tr '[:upper:]' '[:lower:]' |
        tr -cs 'a-z0-9_.-' '-'
    )"

    echo
    echo "global_order_index=$GLOBAL_INDEX"
    echo "campaign_seed=$SEED"
    echo "cell_order_index=$CELL_ORDER_INDEX"
    echo "cell_id=$CELL"
    echo "event_id=$EVENT_ID"
    echo "runtime_family=$RUNTIME_FAMILY"
    echo "runtime_variant=$RUNTIME_VARIANT"
    echo "run_id=$RUN_ID"
    echo "repo_commit=$LOCAL_SHA"
    echo "evidence_directory=$EVIDENCE"

    echo
    echo "============================================================"
    echo "5. ZERO-WRITE EVIDENCE FRESHNESS"
    echo "============================================================"

    PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$ROOT" python3 -m \
      src.mission_recovery.wp9_r066_campaign_evidence_freshness \
      check \
      --request-json "$REQUEST"

    echo
    echo "============================================================"
    echo "6. EXACTLY ONE AUTHORIZED CAMPAIGN INVOCATION"
    echo "============================================================"

    RC=0
    if WP9_R066_FINAL_CAMPAIGN_RUNTIME_AUTHORIZED=1 \
       WP9_R066_AUTHORIZED_RUN_ID="$RUN_ID" \
       WP9_R066_AUTHORIZED_SEED="$SEED" \
       WP9_R066_AUTHORIZED_CELL="$CELL" \
       WP9_R066_AUTHORIZED_REPO_SHA="$LOCAL_SHA" \
       ./scripts/run_wp9_r066_final_campaign_trial.sh \
         execute-request \
         --request-json "$REQUEST" \
         --output-json "$EXEC_OUT"
    then
      RC=0
    else
      RC=$?
    fi

    echo "executor_return_code=$RC"

    if [[ "$RC" -ne 0 ]]; then
      echo
      echo "============================================================"
      echo "7. NONZERO RETURN — RETAIN AND HARD STOP"
      echo "============================================================"
      echo "automatic_retry_performed=false"
      echo "automatic_next_case_performed=false"
      echo "attempt_history_append_performed=false"

      if [[ -d "$ROOT/$EVIDENCE" ]]; then
        echo "evidence_directory_exists=true"
        find "$ROOT/$EVIDENCE" -maxdepth 3 -type f -print
        MARKER="$ROOT/$EVIDENCE/immutable-ground/campaign-seed-consumption.json"
        if [[ -f "$MARKER" ]]; then
          echo "campaign_seed_commit_marker_present=true"
          cat "$MARKER"
        else
          echo "campaign_seed_commit_marker_present=false"
        fi
        if [[ -f "$ROOT/$EVIDENCE/source-harness.stderr.log" ]]; then
          echo "--- source-harness.stderr.log (tail) ---"
          tail -80 "$ROOT/$EVIDENCE/source-harness.stderr.log"
        fi
      else
        echo "evidence_directory_exists=false"
      fi

      runtime_safety_audit "$RUN_ID" "$SAFE_ID" || true
      echo "tracked_worktree_after_failure=$(test -z "$(git status --short)" && echo clean || echo DIRTY)"
      echo
      echo "STOP HERE. Do not rerun automatically."
      exit "$RC"
    fi

    [[ -f "$EXEC_OUT" ]] || {
      echo "[RETAIN / STOP] executor returned zero without result JSON"
      runtime_safety_audit "$RUN_ID" "$SAFE_ID" || true
      exit 90
    }

    echo
    echo "============================================================"
    echo "7. ATOMIC ATTEMPT-HISTORY APPEND"
    echo "============================================================"

    APPEND_RC=0
    if PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$ROOT" python3 -m \
      src.mission_recovery.wp9_r069_campaign_one_position_operator \
      append-result \
      --attempt-history-json "$HISTORY" \
      --request-json "$REQUEST" \
      --executor-result-json "$EXEC_OUT"
    then
      APPEND_RC=0
    else
      APPEND_RC=$?
    fi

    if [[ "$APPEND_RC" -ne 0 ]]; then
      echo "attempt_history_append=FAIL"
      echo "automatic_retry_performed=false"
      echo "automatic_next_case_performed=false"
      runtime_safety_audit "$RUN_ID" "$SAFE_ID" || true
      echo "tracked_worktree_after_append_failure=$(test -z "$(git status --short)" && echo clean || echo DIRTY)"
      echo "STOP HERE. Retained runtime result requires ledger review; do not execute another position."
      exit "$APPEND_RC"
    fi

    echo "attempt_history_append=PASS"

    echo
    echo "============================================================"
    echo "8. RETAINED RESULT SUMMARY"
    echo "============================================================"

    SUMMARY_RC=0
    if PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$ROOT" python3 - "$EXEC_OUT" <<'PY'
import json
import sys
from pathlib import Path

outer = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
runner = outer.get("runner_result", {})
print("attempt_status=" + str(outer.get("attempt_status")))
print("run_id=" + str(outer.get("run_id")))
print("campaign_seed=" + str(outer.get("campaign_seed")))
print("cell_id=" + str(outer.get("cell_id")))
print("runtime_execution_performed=" + str(bool(outer.get("runtime_execution_performed"))).lower())
print("campaign_seed_consumed=" + str(bool(outer.get("campaign_seed_consumed"))).lower())
print("campaign_data_generated=" + str(bool(outer.get("campaign_data_generated"))).lower())
for key in (
    "classification",
    "event_id",
    "runtime_family",
    "runtime_variant",
    "treatment_fidelity_valid",
    "raw_metric_inputs_complete",
    "outcome_matches_predeclared_expectation",
    "unexpected_scientific_outcome_retained",
    "source_harness_return_code",
    "invalid_attempt_retained",
):
    if key in runner:
        value = runner[key]
        if isinstance(value, bool):
            value = str(value).lower()
        print(f"{key}={value}")
record = runner.get("run_record")
if isinstance(record, dict):
    print("terminal_state=" + str(record.get("terminal_state")))
    timing = record.get("timing", {})
    outcomes = record.get("outcomes", {})
    if isinstance(timing, dict):
        for key in ("event_activation_s", "containment_s", "verified_recovery_s"):
            if key in timing:
                print(f"{key}={timing[key]}")
    if isinstance(outcomes, dict):
        for key in (
            "evidence_completeness_ratio",
            "ground_spacecraft_state_divergence_s",
            "legitimate_command_rejection_rate",
            "mission_objective_completion_ratio",
            "unauthorized_effect_completed",
            "safety_invariant_violations",
        ):
            if key in outcomes:
                print(f"{key}={outcomes[key]}")
PY
    then
      SUMMARY_RC=0
    else
      SUMMARY_RC=$?
    fi

    if [[ "$SUMMARY_RC" -ne 0 ]]; then
      echo "[RETAIN / STOP] result summary rendering failed after ledger append"
      runtime_safety_audit "$RUN_ID" "$SAFE_ID" || true
      echo "tracked_worktree_after_summary_failure=$(test -z "$(git status --short)" && echo clean || echo DIRTY)"
      echo "STOP HERE. Do not execute another campaign position."
      exit "$SUMMARY_RC"
    fi

    echo
    echo "============================================================"
    echo "9. POST-RUNTIME SAFETY / HARD STOP"
    echo "============================================================"

    SAFETY_FAIL=0
    runtime_safety_audit "$RUN_ID" "$SAFE_ID" || SAFETY_FAIL=1
    if [[ -n "$(git status --short)" ]]; then
      echo "[SAFETY WARNING] tracked worktree changed during trial"
      git status --short
      SAFETY_FAIL=1
    else
      echo "tracked_worktree_after_trial=clean"
    fi

    echo "completed_global_order_index=$GLOBAL_INDEX"
    echo "completed_campaign_seed=$SEED"
    echo "completed_cell_id=$CELL"
    echo "automatic_retry_performed=false"
    echo "automatic_next_case_performed=false"
    echo "following_position_execution_performed=false"
    echo "campaign_wide_execution_performed=false"

    if [[ "$SAFETY_FAIL" -ne 0 ]]; then
      echo "[RETAIN / STOP] post-runtime safety audit requires review"
      exit 96
    fi

    echo "r069_one_position_operator=COMPLETE"
    echo "STOP HERE. Paste the complete output into ChatGPT."
    ;;

  *)
    usage
    exit 2
    ;;
esac
