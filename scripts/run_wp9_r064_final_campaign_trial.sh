#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

[[ "$#" -ge 1 ]] || {
  echo "usage: $0 <validate-static|authorization-request|execute-trial> [args...]" >&2
  exit 2
}

COMMAND="$1"
shift

case "$COMMAND" in
  validate-static)
    [[ "$#" -eq 0 ]] || {
      echo "usage: $0 validate-static" >&2
      exit 2
    }

    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH="$ROOT" \
    python3 -m \
      src.mission_recovery.wp9_final_campaign_bridge \
      validate-static

    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH="$ROOT" \
    python3 -m \
      src.mission_recovery.wp9_r064_attempt_history \
      validate-static
    ;;

  authorization-request)
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH="$ROOT" \
    python3 -m \
      src.mission_recovery.wp9_final_campaign_bridge \
      authorization-request \
      "$@"
    ;;

  execute-trial)
    echo "[BLOCKED] R-064 static/TDD gate: campaign execution remains blocked" >&2
    echo "[BLOCKED] bounded non-campaign-seed runtime integration validation is required" >&2
    echo "[BLOCKED] validated attempt history and a separate exact single-trial authorization are required" >&2
    exit 3
    ;;

  *)
    echo "usage: $0 <validate-static|authorization-request|execute-trial> [args...]" >&2
    exit 2
    ;;
esac
