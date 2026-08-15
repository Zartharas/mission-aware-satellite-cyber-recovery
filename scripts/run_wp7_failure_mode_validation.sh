#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="${1:-$PWD}"
ROOT="$(cd "$ROOT" && pwd)"
VALIDATED_IMPLEMENTATION_COMMIT="6ca65908309742cea31a0588167274ecdf6a497e"
IMAGE="ivvitc/nos3-64@sha256:06aa945988a7770b759022c2e1f6f2531818c087fe41a4739d3a3a7f2a9dcce2"
BASE_RUN_ID="${RUN_ID:-$(date -u +%Y%m%dT%H%M%SZ)-wp7-failure-modes}"
EVIDENCE="$ROOT/results/wp7/failure-modes/$BASE_RUN_ID"
CF_BACKING_DIR="/work/nos3/fsw/build/exe/cpu1/cf"
STAGE_BACKING="$CF_BACKING_DIR/mission-aware-e3-candidate.pkg"
TEMP_BACKING="$CF_BACKING_DIR/mission-aware-wp7-rollback.tmp"
ACTIVE_PID=""
ACTIVE_CFS=""

mkdir -p "$EVIDENCE"

cleanup_active() {
  set +e
  if [[ -n "$ACTIVE_CFS" ]] && docker inspect "$ACTIVE_CFS" >/dev/null 2>&1; then
    docker exec "$ACTIVE_CFS" rm -f "$STAGE_BACKING" "$TEMP_BACKING" >/dev/null 2>&1 || true
  fi
  if [[ -n "$ACTIVE_PID" ]] && kill -0 "$ACTIVE_PID" >/dev/null 2>&1; then
    kill -TERM "$ACTIVE_PID" >/dev/null 2>&1 || true
    wait "$ACTIVE_PID" >/dev/null 2>&1 || true
  fi
  ACTIVE_PID=""
  ACTIVE_CFS=""
  set -e
}
trap cleanup_active EXIT INT TERM

cd "$ROOT"

EXECUTION_COMMIT="$(git rev-parse HEAD)"

git cat-file -e "$VALIDATED_IMPLEMENTATION_COMMIT^{commit}" 2>/dev/null || {
  echo "validated_implementation_commit_identity=FAIL" >&2
  exit 1
}

git merge-base --is-ancestor \
  "$VALIDATED_IMPLEMENTATION_COMMIT" "$EXECUTION_COMMIT" || {
  echo "execution_commit_descends_from_validated=FAIL" >&2
  exit 1
}

IMPLEMENTATION_PATHS=(
  configs/wp5_event_catalog.json
  configs/wp6_policy_rules.json
  configs/wp7_trusted_recovery_adapter.json
  scripts/run_nominal_runtime_preflight.sh
  scripts/run_wp7_trusted_recovery_test.sh
  src/mission_recovery
)

if ! git diff --quiet \
  "$VALIDATED_IMPLEMENTATION_COMMIT".."$EXECUTION_COMMIT" -- \
  "${IMPLEMENTATION_PATHS[@]}"; then
  echo "validated_implementation_paths_unchanged=FAIL" >&2
  git diff --name-only \
    "$VALIDATED_IMPLEMENTATION_COMMIT".."$EXECUTION_COMMIT" -- \
    "${IMPLEMENTATION_PATHS[@]}" >&2
  exit 1
fi

test -z "$(git status --short)" || {
  echo "repository_worktree_clean=FAIL" >&2
  git status --short >&2
  exit 1
}
docker info >/dev/null 2>&1
docker image inspect "$IMAGE" >/dev/null 2>&1

python3 -m unittest discover -s tests -p 'test_*.py' >/dev/null
bash -n scripts/run_wp7_trusted_recovery_test.sh

echo "validated_implementation_commit_identity=PASS"
echo "execution_commit_descends_from_validated=PASS"
echo "validated_implementation_paths_unchanged=PASS"
echo "repository_worktree_clean=PASS"
echo "pre_failure_static_validation=PASS"

# -----------------------------------------------------------------------------
# FM1: A request whose digest is internally consistent but whose policy binding
# is altered must still be rejected. This tests semantic authorization binding,
# not cryptographic authentication.
# -----------------------------------------------------------------------------
FM1="$EVIDENCE/fm1-invalid-request-binding"
mkdir -p "$FM1"
PYTHONPATH="$ROOT" python3 - "$FM1/result.json" <<'PY'
import copy
import json
import sys
from pathlib import Path

from src.mission_recovery.events import materialize_event
from src.mission_recovery.policies import evaluate_policy
from src.mission_recovery.rollback_requests import (
    build_verified_rollback_request,
    compute_rollback_request_sha256,
)
from src.mission_recovery.trusted_recovery import validate_rollback_request
from src.mission_recovery.update_artifacts import (
    build_manifest,
    build_tampered_update,
    verify_candidate,
)

event = materialize_event(
    "E3",
    mission_state="M4",
    contact_condition="C0",
    evidence_condition="T0",
    seed=1,
)
policy = evaluate_policy("P5", event)
manifest = build_manifest()
tampered = build_tampered_update()
verification = verify_candidate(tampered, manifest)
request = build_verified_rollback_request(
    event_instance=event,
    policy_decision=policy,
    manifest=manifest,
    candidate_verification=verification,
)

changed = copy.deepcopy(request)
changed["requested_policy_id"] = "P0"
changed["request_sha256"] = compute_rollback_request_sha256(changed)

result = validate_rollback_request(
    request=changed,
    policy_decision=policy,
    manifest=manifest,
    pre_recovery_candidate_sha256=verification["actual_sha256"],
)

assert result["accepted"] is False
assert "requested_policy_mismatch" in result["reasons"]
assert "request_sha256_mismatch" not in result["reasons"]

out = {
    "failure_mode": "invalid_request_policy_binding",
    "expected_rejection": True,
    "accepted": result["accepted"],
    "reasons": result["reasons"],
    "digest_consistent_after_mutation": (
        result["request_sha256"] == result["computed_request_sha256"]
    ),
    "cryptographic_authentication_claim": False,
    "status": "PASS",
}
Path(sys.argv[1]).write_text(
    json.dumps(out, sort_keys=True, indent=2) + "\n",
    encoding="utf-8",
)
PY

echo "fm1_invalid_request_binding=PASS"

# -----------------------------------------------------------------------------
# FM2: A tampered replacement source must be rejected before any recovery
# execution is attempted.
# -----------------------------------------------------------------------------
FM2="$EVIDENCE/fm2-tampered-replacement-source"
mkdir -p "$FM2"
PYTHONPATH="$ROOT" python3 - "$FM2/result.json" <<'PY'
import json
import sys
from pathlib import Path

from src.mission_recovery.trusted_recovery import verify_replacement_source
from src.mission_recovery.update_artifacts import (
    build_manifest,
    build_tampered_update,
)

manifest = build_manifest()
result = verify_replacement_source(build_tampered_update(), manifest)

assert result["accepted"] is False
assert "sha256_mismatch" in result["reasons"]

out = {
    "failure_mode": "tampered_replacement_source",
    "expected_rejection": True,
    "accepted": result["accepted"],
    "reasons": result["reasons"],
    "recovery_execution_performed": False,
    "status": "PASS",
}
Path(sys.argv[1]).write_text(
    json.dumps(out, sort_keys=True, indent=2) + "\n",
    encoding="utf-8",
)
PY

echo "fm2_tampered_replacement_source=PASS"

prepare_runtime_case() {
  local case_id="$1"
  local case_dir="$2"
  local case_run_id="$BASE_RUN_ID-$case_id"
  local safe_id
  safe_id="$(printf '%s' "$case_run_id" | tr '[:upper:]' '[:lower:]' | tr -cs 'a-z0-9_.-' '-')"
  local cfs="mascr-$safe_id-cfs"
  local network="mascr-$safe_id"
  local log="$case_dir/nominal-runtime.log"

  mkdir -p "$case_dir/ground" "$case_dir/observation"

  PYTHONPATH="$ROOT" python3 - \
    "$case_dir/ground/approved-update.pkg" \
    "$case_dir/ground/tampered-update.pkg" \
    "$case_dir/ground/approved-manifest.json" \
    "$case_dir/ground/policy-decision.json" \
    "$case_dir/ground/rollback-request.json" \
    "$case_dir/ground/request-validation.json" \
    "$case_dir/ground/source-verification.json" <<'PY'
import json
import sys
from pathlib import Path

from src.mission_recovery.events import materialize_event
from src.mission_recovery.policies import evaluate_policy
from src.mission_recovery.rollback_requests import build_verified_rollback_request
from src.mission_recovery.trusted_recovery import (
    validate_rollback_request,
    verify_replacement_source,
)
from src.mission_recovery.update_artifacts import (
    build_approved_update,
    build_manifest,
    build_tampered_update,
    verify_candidate,
)

(
    approved_path,
    tampered_path,
    manifest_path,
    policy_path,
    request_path,
    request_validation_path,
    source_validation_path,
) = sys.argv[1:]

approved = build_approved_update()
tampered = build_tampered_update()
manifest = build_manifest()
event = materialize_event(
    "E3",
    mission_state="M4",
    contact_condition="C0",
    evidence_condition="T0",
    seed=1,
)
policy = evaluate_policy("P5", event)
candidate_verification = verify_candidate(tampered, manifest)
request = build_verified_rollback_request(
    event_instance=event,
    policy_decision=policy,
    manifest=manifest,
    candidate_verification=candidate_verification,
)
request_validation = validate_rollback_request(
    request=request,
    policy_decision=policy,
    manifest=manifest,
    pre_recovery_candidate_sha256=candidate_verification["actual_sha256"],
)
source_validation = verify_replacement_source(approved, manifest)

assert request_validation["accepted"] is True
assert source_validation["accepted"] is True

Path(approved_path).write_bytes(approved)
Path(tampered_path).write_bytes(tampered)
for path, value in (
    (manifest_path, manifest),
    (policy_path, policy),
    (request_path, request),
    (request_validation_path, request_validation),
    (source_validation_path, source_validation),
):
    Path(path).write_text(
        json.dumps(value, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
PY

  RUN_ID="$case_run_id" \
  DURATION_SECONDS=60 \
  STARTUP_GRACE_SECONDS=20 \
  bash "$ROOT/scripts/run_nominal_runtime_preflight.sh" >"$log" 2>&1 &
  ACTIVE_PID=$!
  ACTIVE_CFS="$cfs"

  local ready=0
  for _ in $(seq 1 180); do
    kill -0 "$ACTIVE_PID" >/dev/null 2>&1 || break
    if [[ "$(docker inspect "$cfs" --format '{{.State.Status}}' 2>/dev/null || echo missing)" == running ]]; then
      ready=1
      break
    fi
    sleep 1
  done
  [[ "$ready" -eq 1 ]] || {
    tail -120 "$log" >&2 || true
    echo "runtime_case_ready=FAIL case=$case_id" >&2
    exit 1
  }

  [[ "$(docker network inspect "$network" --format '{{.Internal}}')" == true ]]
  [[ -z "$(docker port "$cfs")" ]]
  docker exec "$cfs" test -d "$CF_BACKING_DIR"
  docker exec "$cfs" rm -f "$STAGE_BACKING" "$TEMP_BACKING"
  docker cp "$case_dir/ground/tampered-update.pkg" "$cfs:$STAGE_BACKING" >/dev/null

  local tampered_sha
  tampered_sha="$(shasum -a 256 "$case_dir/ground/tampered-update.pkg" | awk '{print $1}')"
  test "$(docker exec "$cfs" sha256sum "$STAGE_BACKING" | awk '{print $1}')" = "$tampered_sha"

  printf '%s\n' "$case_run_id" > "$case_dir/observation/run-id.txt"
  printf '%s\n' "$cfs" > "$case_dir/observation/cfs-container.txt"
}

finish_runtime_case() {
  local case_dir="$1"
  local log="$case_dir/nominal-runtime.log"
  local rc
  set +e
  wait "$ACTIVE_PID"
  rc=$?
  set -e
  ACTIVE_PID=""
  ACTIVE_CFS=""
  [[ "$rc" -eq 0 ]] || {
    echo "runtime_case_nominal_completion=FAIL rc=$rc" >&2
    tail -160 "$log" >&2 || true
    exit 1
  }
  grep -Fq 'NOMINAL_RUNTIME_PREFLIGHT_STATUS=PASS' "$log"
}

# -----------------------------------------------------------------------------
# FM3: Interruption immediately before atomic replace. The verified replacement
# may have reached the temporary path, but the rejected staged candidate must
# remain unchanged and terminal trust must remain false.
# -----------------------------------------------------------------------------
FM3="$EVIDENCE/fm3-interruption-before-atomic-replace"
prepare_runtime_case "fm3" "$FM3"

APPROVED="$FM3/ground/approved-update.pkg"
TAMPERED="$FM3/ground/tampered-update.pkg"
MANIFEST="$FM3/ground/approved-manifest.json"
APPROVED_SHA="$(shasum -a 256 "$APPROVED" | awk '{print $1}')"
TAMPERED_SHA="$(shasum -a 256 "$TAMPERED" | awk '{print $1}')"

docker cp "$APPROVED" "$ACTIVE_CFS:$TEMP_BACKING" >/dev/null
test "$(docker exec "$ACTIVE_CFS" sha256sum "$TEMP_BACKING" | awk '{print $1}')" = "$APPROVED_SHA"

# Controlled interruption point: do not execute mv. Remove the temporary object
# as cleanup and verify that the staged candidate was not advanced.
docker exec "$ACTIVE_CFS" rm -f "$TEMP_BACKING"
test "$(docker exec "$ACTIVE_CFS" sha256sum "$STAGE_BACKING" | awk '{print $1}')" = "$TAMPERED_SHA"
docker cp "$ACTIVE_CFS:$STAGE_BACKING" "$FM3/observation/terminal-candidate.pkg" >/dev/null

PYTHONPATH="$ROOT" python3 - \
  "$FM3/observation/terminal-candidate.pkg" "$MANIFEST" "$TAMPERED_SHA" \
  "$FM3/result.json" <<'PY'
import json
import sys
from pathlib import Path

from src.mission_recovery.trusted_recovery import verify_terminal_recovery

candidate = Path(sys.argv[1]).read_bytes()
manifest = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
result = verify_terminal_recovery(
    terminal_candidate=candidate,
    manifest=manifest,
    rejected_candidate_sha256=sys.argv[3],
)

assert result["trusted_recovery_verified"] is False
assert result["terminal_matches_approved"] is False
assert result["terminal_differs_from_rejected"] is False
assert "terminal_still_rejected_candidate" in result["reasons"]

out = {
    "failure_mode": "interruption_before_atomic_replace",
    "controlled_interruption_point": "after_verified_temp_stage_before_mv",
    "atomic_replace_executed": False,
    "terminal_trust": result,
    "claim_boundary": (
        "models interruption before the replace operation; does not claim "
        "power-loss or filesystem crash-consistency guarantees"
    ),
    "status": "PASS",
}
Path(sys.argv[4]).write_text(
    json.dumps(out, sort_keys=True, indent=2) + "\n",
    encoding="utf-8",
)
PY

docker exec "$ACTIVE_CFS" test ! -e "$TEMP_BACKING"
finish_runtime_case "$FM3"
echo "fm3_interruption_before_atomic_replace=PASS"

# -----------------------------------------------------------------------------
# FM4: The approved object is atomically installed, then deliberately corrupted
# before independent terminal verification. The verifier must refuse trust.
# -----------------------------------------------------------------------------
FM4="$EVIDENCE/fm4-post-replace-terminal-corruption"
prepare_runtime_case "fm4" "$FM4"

APPROVED="$FM4/ground/approved-update.pkg"
TAMPERED="$FM4/ground/tampered-update.pkg"
MANIFEST="$FM4/ground/approved-manifest.json"
APPROVED_SHA="$(shasum -a 256 "$APPROVED" | awk '{print $1}')"
TAMPERED_SHA="$(shasum -a 256 "$TAMPERED" | awk '{print $1}')"

docker cp "$APPROVED" "$ACTIVE_CFS:$TEMP_BACKING" >/dev/null
test "$(docker exec "$ACTIVE_CFS" sha256sum "$TEMP_BACKING" | awk '{print $1}')" = "$APPROVED_SHA"
docker exec "$ACTIVE_CFS" mv -f "$TEMP_BACKING" "$STAGE_BACKING"
test "$(docker exec "$ACTIVE_CFS" sha256sum "$STAGE_BACKING" | awk '{print $1}')" = "$APPROVED_SHA"

# Controlled corruption after replacement but before terminal verification.
docker exec "$ACTIVE_CFS" sh -c "printf ' ' >> '$STAGE_BACKING'"
CORRUPTED_SHA="$(docker exec "$ACTIVE_CFS" sha256sum "$STAGE_BACKING" | awk '{print $1}')"
test "$CORRUPTED_SHA" != "$APPROVED_SHA"
test "$CORRUPTED_SHA" != "$TAMPERED_SHA"
docker cp "$ACTIVE_CFS:$STAGE_BACKING" "$FM4/observation/terminal-candidate.pkg" >/dev/null

PYTHONPATH="$ROOT" python3 - \
  "$FM4/observation/terminal-candidate.pkg" "$MANIFEST" "$TAMPERED_SHA" \
  "$FM4/result.json" <<'PY'
import json
import sys
from pathlib import Path

from src.mission_recovery.trusted_recovery import verify_terminal_recovery

candidate = Path(sys.argv[1]).read_bytes()
manifest = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
result = verify_terminal_recovery(
    terminal_candidate=candidate,
    manifest=manifest,
    rejected_candidate_sha256=sys.argv[3],
)

assert result["trusted_recovery_verified"] is False
assert result["terminal_matches_approved"] is False
assert result["terminal_differs_from_rejected"] is True
assert "sha256_mismatch" in result["reasons"]
assert "terminal_not_approved_target" in result["reasons"]

out = {
    "failure_mode": "post_replace_terminal_corruption",
    "atomic_replace_executed": True,
    "controlled_corruption_before_terminal_verification": True,
    "terminal_trust": result,
    "status": "PASS",
}
Path(sys.argv[4]).write_text(
    json.dumps(out, sort_keys=True, indent=2) + "\n",
    encoding="utf-8",
)
PY

docker exec "$ACTIVE_CFS" test ! -e "$TEMP_BACKING"
finish_runtime_case "$FM4"
echo "fm4_post_replace_terminal_corruption=PASS"

python3 - "$EVIDENCE" "$VALIDATED_IMPLEMENTATION_COMMIT" "$EXECUTION_COMMIT" <<'PY'
import hashlib
import json
import sys
from pathlib import Path

root = Path(sys.argv[1])
validated_commit = sys.argv[2]
execution_commit = sys.argv[3]

cases = {
    "fm1_invalid_request_binding": root / "fm1-invalid-request-binding" / "result.json",
    "fm2_tampered_replacement_source": root / "fm2-tampered-replacement-source" / "result.json",
    "fm3_interruption_before_atomic_replace": root / "fm3-interruption-before-atomic-replace" / "result.json",
    "fm4_post_replace_terminal_corruption": root / "fm4-post-replace-terminal-corruption" / "result.json",
}
loaded = {name: json.loads(path.read_text(encoding="utf-8")) for name, path in cases.items()}
assert all(value["status"] == "PASS" for value in loaded.values())

summary = {
    "schema": 1,
    "classification": "WP7_FAILURE_MODE_VALIDATION_PASS",
    "validated_implementation_commit": validated_commit,
    "execution_commit": execution_commit,
    "validated_implementation_paths_unchanged": True,
    "failure_modes": {name: "PASS" for name in cases},
    "fresh_runtime_per_runtime_failure_mode": True,
    "runtime_failure_mode_count": 2,
    "non_runtime_failure_mode_count": 2,
    "trusted_recovery_failure_detection_validated": True,
    "single_campaign_descriptive_only": True,
    "recovery_success_rate_claim": False,
    "filesystem_crash_consistency_claim": False,
    "operational_firmware_recovery_claim": False,
    "live_spacecraft_recovery_claim": False,
}
encoded = (json.dumps(summary, sort_keys=True, indent=2) + "\n").encode()
(root / "summary.json").write_bytes(encoded)
print("summary_sha256=" + hashlib.sha256(encoded).hexdigest())
PY

# The runtime preflight owns container/network cleanup. Verify that no project
# containers remain after both fresh-runtime failure cases.
LEFTOVER="$(docker ps -a --filter 'label=research.project=mission-aware-satellite-cyber-recovery' --format '{{.Names}}')"
test -z "$LEFTOVER" || {
  echo "nos3_post_run_clean=FAIL" >&2
  printf '%s\n' "$LEFTOVER" >&2
  exit 1
}

test -z "$(git status --short)" || {
  echo "repository_worktree_clean_after_campaign=FAIL" >&2
  git status --short >&2
  exit 1
}

echo "trusted_recovery_failure_detection_validated=true"
echo "single_campaign_descriptive_only=true"
echo "recovery_success_rate_claim=false"
echo "filesystem_crash_consistency_claim=false"
echo "operational_firmware_recovery_claim=false"
echo "nos3_post_run_clean=PASS"
echo "repository_worktree_clean_after_campaign=PASS"
echo "WP7_FAILURE_MODE_VALIDATION=PASS"
echo "evidence_directory=$EVIDENCE"
