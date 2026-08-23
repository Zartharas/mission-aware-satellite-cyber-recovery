#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

[[ "$#" -ge 1 ]] || {
  echo "usage: $0 <validate-static|plan-case|authorization-request|execute-case> [args...]" >&2
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
      src.mission_recovery.wp9_r065_bounded_runtime_integration \
      validate-static
    ;;

  plan-case)
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH="$ROOT" \
    python3 -m \
      src.mission_recovery.wp9_r065_bounded_runtime_integration \
      plan-case \
      "$@"
    ;;

  authorization-request)
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH="$ROOT" \
    python3 -m \
      src.mission_recovery.wp9_r065_bounded_runtime_integration \
      authorization-request \
      "$@"
    ;;

  execute-case)
    echo "[BLOCKED] R-065 static/TDD preparation: execution remains blocked" >&2
    echo "[BLOCKED] no NOS3 runtime is authorized by this gate" >&2
    echo "[BLOCKED] a separate exact single-case runtime authorization is required" >&2
    exit 3
    ;;

  *)
    echo "usage: $0 <validate-static|plan-case|authorization-request|execute-case> [args...]" >&2
    exit 2
    ;;
esac
