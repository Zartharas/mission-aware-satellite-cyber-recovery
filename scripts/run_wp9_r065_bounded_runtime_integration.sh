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
    [[ "$#" -eq 1 ]] || {
      echo "usage: $0 execute-case <Z01>" >&2
      exit 2
    }
    CASE_ID="$1"
    [[ "$CASE_ID" == "Z01" ]] || {
      echo "[BLOCKED] concrete R-065 runtime mechanism currently supports Z01 only" >&2
      echo "[BLOCKED] Z02-Z09 remain fail-closed" >&2
      exit 3
    }
    [[ "${WP9_R065_DEVELOPMENT_RUNTIME_AUTHORIZED:-0}" == "1" ]] || {
      echo "[BLOCKED] R-065 development runtime authorization is not active" >&2
      exit 3
    }
    [[ "${WP9_R065_AUTHORIZED_CASE:-}" == "Z01" ]] || {
      echo "[BLOCKED] R-065 authorization is not for Z01" >&2
      exit 3
    }
    [[ "${WP9_R065_AUTHORIZED_SEED:-}" == "9941" ]] || {
      echo "[BLOCKED] R-065 authorization is not for development seed 9941" >&2
      exit 3
    }

    REPO_COMMIT="$(git rev-parse HEAD)"
    [[ "${WP9_R065_AUTHORIZED_REPO_SHA:-}" == "$REPO_COMMIT" ]] || {
      echo "[BLOCKED] R-065 authorization SHA does not match current repository HEAD" >&2
      exit 3
    }
    test -z "$(git status --short)" || {
      echo "[ERROR] repository worktree must be clean before R-065 runtime" >&2
      exit 1
    }

    TOKEN="$(python3 - <<'PY'
import uuid
print(uuid.uuid4().hex)
PY
)"
    RUN_ID="${RUN_ID:-$(date -u +%Y%m%dT%H%M%SZ)-wp9-r065-z01-s9941-${TOKEN}}"
    EVIDENCE_DIRECTORY="$ROOT/results/wp9/development/r065/integration/$RUN_ID"
    mkdir -p "$EVIDENCE_DIRECTORY/runtime-observation"

    echo "r065_exact_single_case_runtime_authorization=PASS"
    echo "authorized_case=Z01"
    echo "authorized_seed=9941"
    echo "authorized_repo_sha=$REPO_COMMIT"
    echo "automatic_retry_allowed=false"
    echo "automatic_next_case_allowed=false"
    echo "campaign_seed_consumed=false"
    echo "campaign_data_generated=false"

    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH="$ROOT" \
    python3 -m \
      src.mission_recovery.wp9_r065_runtime_mechanism_driver \
      execute-z01 \
      --run-id "$RUN_ID" \
      --repo-commit "$REPO_COMMIT"
    ;;

  *)
    echo "usage: $0 <validate-static|plan-case|authorization-request|execute-case> [args...]" >&2
    exit 2
    ;;
esac
