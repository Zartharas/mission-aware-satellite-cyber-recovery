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
      echo "usage: $0 execute-case <Z01-Z09>" >&2
      exit 2
    }
    CASE_ID="$1"
    case "$CASE_ID" in
      Z01) DEVELOPMENT_SEED=9941 ;;
      Z02) DEVELOPMENT_SEED=9942 ;;
      Z03) DEVELOPMENT_SEED=9943 ;;
      Z04) DEVELOPMENT_SEED=9944 ;;
      Z05) DEVELOPMENT_SEED=9945 ;;
      Z06) DEVELOPMENT_SEED=9946 ;;
      Z07) DEVELOPMENT_SEED=9947 ;;
      Z08) DEVELOPMENT_SEED=9948 ;;
      Z09) DEVELOPMENT_SEED=9949 ;;
      *)
        echo "[BLOCKED] R-065 runtime supports only Z01-Z09" >&2
        exit 3
        ;;
    esac

    [[ "${WP9_R065_DEVELOPMENT_RUNTIME_AUTHORIZED:-0}" == "1" ]] || {
      echo "[BLOCKED] R-065 development runtime authorization is not active" >&2
      exit 3
    }
    [[ "${WP9_R065_AUTHORIZED_CASE:-}" == "$CASE_ID" ]] || {
      echo "[BLOCKED] R-065 authorization is not for $CASE_ID" >&2
      exit 3
    }
    [[ "${WP9_R065_AUTHORIZED_SEED:-}" == "$DEVELOPMENT_SEED" ]] || {
      echo "[BLOCKED] R-065 authorization is not for development seed $DEVELOPMENT_SEED" >&2
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
    CASE_SAFE="$(printf '%s' "$CASE_ID" | tr '[:upper:]' '[:lower:]')"
    RUN_ID="${RUN_ID:-$(date -u +%Y%m%dT%H%M%SZ)-wp9-r065-${CASE_SAFE}-s${DEVELOPMENT_SEED}-${TOKEN}}"
    EVIDENCE_DIRECTORY="$ROOT/results/wp9/development/r065/integration/$RUN_ID"
    mkdir -p "$EVIDENCE_DIRECTORY/runtime-observation"

    echo "r065_exact_single_case_runtime_authorization=PASS"
    echo "authorized_case=$CASE_ID"
    echo "authorized_seed=$DEVELOPMENT_SEED"
    echo "authorized_repo_sha=$REPO_COMMIT"
    echo "automatic_retry_allowed=false"
    echo "automatic_next_case_allowed=false"
    echo "campaign_seed_consumed=false"
    echo "campaign_data_generated=false"

    if [[ "$CASE_ID" == "Z01" ]]; then
      PYTHONDONTWRITEBYTECODE=1 \
      PYTHONPATH="$ROOT" \
      python3 -m \
        src.mission_recovery.wp9_r065_runtime_mechanism_driver \
        execute-z01 \
        --run-id "$RUN_ID" \
        --repo-commit "$REPO_COMMIT"
    else
      PYTHONDONTWRITEBYTECODE=1 \
      PYTHONPATH="$ROOT" \
      python3 -m \
        src.mission_recovery.wp9_r065_remaining_runtime_mechanism_driver \
        execute-case \
        --case-id "$CASE_ID" \
        --run-id "$RUN_ID" \
        --repo-commit "$REPO_COMMIT"
    fi
    ;;

  *)
    echo "usage: $0 <validate-static|plan-case|authorization-request|execute-case> [args...]" >&2
    exit 2
    ;;
esac
