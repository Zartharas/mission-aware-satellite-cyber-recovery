#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

usage() {
  cat >&2 <<'EOF'
usage:
  run_wp9_r066_final_campaign_trial.sh validate-static
  run_wp9_r066_final_campaign_trial.sh authorization-request <R-064 args...>
  run_wp9_r066_final_campaign_trial.sh build-request \
    --plan-json FILE --authorization-json FILE --attempt-history-json FILE \
    --current-repo-sha SHA --output-json FILE
  run_wp9_r066_final_campaign_trial.sh execute-request \
    --request-json FILE --output-json FILE
EOF
}

[[ "$#" -ge 1 ]] || {
  usage
  exit 2
}

COMMAND="$1"
shift

case "$COMMAND" in
  validate-static)
    [[ "$#" -eq 0 ]] || {
      usage
      exit 2
    }

    PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$ROOT" python3 -m \
      src.mission_recovery.wp9_final_campaign_bridge \
      validate-static

    PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$ROOT" python3 -m \
      src.mission_recovery.wp9_r064_attempt_history \
      validate-static

    PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$ROOT" python3 -m \
      src.mission_recovery.wp9_r066_final_campaign_runtime_binding \
      validate-static

    PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$ROOT" python3 -m \
      src.mission_recovery.wp9_r066_campaign_runtime_executor \
      validate-static
    ;;

  authorization-request)
    PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$ROOT" python3 -m \
      src.mission_recovery.wp9_final_campaign_bridge \
      authorization-request \
      "$@"
    ;;

  build-request)
    PLAN_JSON=""
    AUTHORIZATION_JSON=""
    ATTEMPT_HISTORY_JSON=""
    CURRENT_REPO_SHA=""
    OUTPUT_JSON=""

    while [[ "$#" -gt 0 ]]; do
      case "$1" in
        --plan-json)
          [[ "$#" -ge 2 ]] || { usage; exit 2; }
          PLAN_JSON="$2"
          shift 2
          ;;
        --authorization-json)
          [[ "$#" -ge 2 ]] || { usage; exit 2; }
          AUTHORIZATION_JSON="$2"
          shift 2
          ;;
        --attempt-history-json)
          [[ "$#" -ge 2 ]] || { usage; exit 2; }
          ATTEMPT_HISTORY_JSON="$2"
          shift 2
          ;;
        --current-repo-sha)
          [[ "$#" -ge 2 ]] || { usage; exit 2; }
          CURRENT_REPO_SHA="$2"
          shift 2
          ;;
        --output-json)
          [[ "$#" -ge 2 ]] || { usage; exit 2; }
          OUTPUT_JSON="$2"
          shift 2
          ;;
        *)
          usage
          exit 2
          ;;
      esac
    done

    [[ -n "$PLAN_JSON" && -n "$AUTHORIZATION_JSON" && \
       -n "$ATTEMPT_HISTORY_JSON" && -n "$CURRENT_REPO_SHA" && \
       -n "$OUTPUT_JSON" ]] || {
      usage
      exit 2
    }

    PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$ROOT" python3 - \
      "$PLAN_JSON" "$AUTHORIZATION_JSON" "$ATTEMPT_HISTORY_JSON" \
      "$CURRENT_REPO_SHA" "$OUTPUT_JSON" <<'PY'
import json
import sys
from pathlib import Path

from src.mission_recovery.wp9_r066_final_campaign_runtime_binding import (
    build_campaign_runtime_request,
)

plan_path, auth_path, history_path, current_sha, output_path = sys.argv[1:]
plan = json.loads(Path(plan_path).read_text(encoding="utf-8"))
auth = json.loads(Path(auth_path).read_text(encoding="utf-8"))
history = json.loads(Path(history_path).read_text(encoding="utf-8"))
if not isinstance(history, list):
    raise ValueError("R-066 attempt-history JSON must be an array")
request = build_campaign_runtime_request(
    plan=plan,
    authorization=auth,
    attempt_history=history,
    current_repo_sha=current_sha,
)
Path(output_path).parent.mkdir(parents=True, exist_ok=True)
Path(output_path).write_text(
    json.dumps(request, sort_keys=True, indent=2) + "\n",
    encoding="utf-8",
)
print("WP9_R066_FINAL_CAMPAIGN_RUNTIME_REQUEST=PASS")
print("global_order_index=" + str(request["global_order_index"]))
print("campaign_seed=" + str(request["campaign_seed"]))
print("cell_id=" + request["cell_id"])
print("run_id=" + request["run_id"])
print("attempt_history_validated=true")
print("runtime_execution_performed=false")
print("campaign_seed_consumed=false")
print("campaign_data_generated=false")
print("campaign_runtime_authorized=false")
PY
    ;;

  execute-request)
    REQUEST_JSON=""
    OUTPUT_JSON=""

    while [[ "$#" -gt 0 ]]; do
      case "$1" in
        --request-json)
          [[ "$#" -ge 2 ]] || { usage; exit 2; }
          REQUEST_JSON="$2"
          shift 2
          ;;
        --output-json)
          [[ "$#" -ge 2 ]] || { usage; exit 2; }
          OUTPUT_JSON="$2"
          shift 2
          ;;
        *)
          usage
          exit 2
          ;;
      esac
    done

    [[ -n "$REQUEST_JSON" && -n "$OUTPUT_JSON" ]] || {
      usage
      exit 2
    }

    # Fail before authorization reaches a runtime harness if this run-id already
    # owns a campaign evidence directory. This independently protects against a
    # stale/incomplete externally supplied attempt-history array.
    PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$ROOT" python3 -m \
      src.mission_recovery.wp9_r066_campaign_evidence_freshness \
      check \
      --request-json "$REQUEST_JSON"

    # The hardened Python executor checks exact run-id/seed/cell/repository
    # authorization before invoking one runtime harness. No retry or next-case
    # execution path exists here.
    PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$ROOT" python3 -m \
      src.mission_recovery.wp9_r066_campaign_runtime_executor \
      execute-request \
      --request-json "$REQUEST_JSON" \
      --output-json "$OUTPUT_JSON"
    ;;

  *)
    usage
    exit 2
    ;;
esac
