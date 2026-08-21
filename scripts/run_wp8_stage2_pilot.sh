#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PILOT_CONFIG="$ROOT/configs/wp8_pilot_design.json"
STAGE1_LEDGER="$ROOT/results/wp8/pilot/stage1/stage1-ledger.json"
STAGE2_DIR="$ROOT/results/wp8/pilot/stage2"
STAGE2_LEDGER="$STAGE2_DIR/stage2-ledger.json"

cd "$ROOT"

test -z "$(git status --short)" || {
  echo "[ERROR] repository worktree must be clean before Stage-2 pilot" >&2
  exit 1
}

for cmd in git python3 docker; do
  command -v "$cmd" >/dev/null 2>&1 || {
    echo "[ERROR] missing required command: $cmd" >&2
    exit 1
  }
done

[[ -s "$STAGE1_LEDGER" ]] || {
  echo "[ERROR] Stage-1 ledger is missing" >&2
  exit 1
}

HEAD_SHA="$(git rev-parse HEAD)"
VALIDATED_SHA="${WP8_STAGE2_VALIDATED_COMMIT:-}"
VALIDATED_CI_RUN_ID="${WP8_STAGE2_VALIDATED_CI_RUN_ID:-}"
REVIEWED_INVALID_RUN_IDS="${WP8_STAGE2_REVIEWED_INVALID_RUN_IDS:-}"

[[ -n "$VALIDATED_SHA" && "$VALIDATED_SHA" == "$HEAD_SHA" ]] || {
  echo "[ERROR] Stage-2 execution requires exact validated commit identity" >&2
  echo "current_head=$HEAD_SHA" >&2
  echo "provided_validated_commit=${VALIDATED_SHA:-missing}" >&2
  exit 2
}

[[ "$VALIDATED_CI_RUN_ID" =~ ^[0-9]+$ ]] || {
  echo "[ERROR] Stage-2 execution requires validated CI run ID" >&2
  exit 2
}

NEXT_JSON="$(
PYTHONPATH="$ROOT" python3 - \
  "$PILOT_CONFIG" "$STAGE1_LEDGER" "$STAGE2_LEDGER" \
  "$REVIEWED_INVALID_RUN_IDS" <<'PY'
import json
import sys
from pathlib import Path

from src.mission_recovery.wp8_stage2_pilot import (
    new_stage2_ledger,
    stage2_progress,
)

pilot = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
stage1 = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
stage2_path = Path(sys.argv[3])
reviewed = {
    value
    for value in sys.argv[4].split(",")
    if value
}
stage2 = (
    json.loads(stage2_path.read_text(encoding="utf-8"))
    if stage2_path.exists()
    else new_stage2_ledger(pilot)
)

progress = stage2_progress(
    pilot,
    stage1,
    stage2,
    reviewed_invalid_run_ids=reviewed,
)
if progress["progression_blocked_for_review"]:
    raise SystemExit("Stage-2 progression is blocked by retained RUN_INVALID")
if progress["stage_2_complete"]:
    print(json.dumps({"complete": True}))
else:
    row = progress["next_repetition"]
    print(json.dumps({
        "complete": False,
        "cell_id": row["cell_id"],
        "seed": row["seed"],
        "runtime_path": row["runtime_path"],
        "runtime_family": row["runtime_family"],
        "prior_attempt_count": len(stage2["attempts"]),
        "valid_repetition_count": progress["valid_repetition_count"],
        "remaining_valid_repetitions": progress["remaining_valid_repetitions"],
        "reviewed_invalid_attempt_count": progress[
            "reviewed_invalid_attempt_count"
        ],
    }, sort_keys=True))
PY
)"

COMPLETE="$(
  python3 -c 'import json,sys; print(str(json.loads(sys.argv[1])["complete"]).lower())' \
    "$NEXT_JSON"
)"

if [[ "$COMPLETE" == "true" ]]; then
  echo "STAGE2_PILOT_STATUS=COMPLETE"
  exit 0
fi

CELL_ID="$(python3 -c 'import json,sys; print(json.loads(sys.argv[1])["cell_id"])' "$NEXT_JSON")"
SEED="$(python3 -c 'import json,sys; print(json.loads(sys.argv[1])["seed"])' "$NEXT_JSON")"
ROUTE="$(python3 -c 'import json,sys; print(json.loads(sys.argv[1])["runtime_path"])' "$NEXT_JSON")"
FAMILY="$(python3 -c 'import json,sys; print(json.loads(sys.argv[1])["runtime_family"])' "$NEXT_JSON")"
PRIOR_ATTEMPTS="$(python3 -c 'import json,sys; print(json.loads(sys.argv[1])["prior_attempt_count"])' "$NEXT_JSON")"
VALID_COUNT="$(python3 -c 'import json,sys; print(json.loads(sys.argv[1])["valid_repetition_count"])' "$NEXT_JSON")"
REMAINING="$(python3 -c 'import json,sys; print(json.loads(sys.argv[1])["remaining_valid_repetitions"])' "$NEXT_JSON")"
REVIEWED_INVALID_COUNT="$(python3 -c 'import json,sys; print(json.loads(sys.argv[1])["reviewed_invalid_attempt_count"])' "$NEXT_JSON")"

if [[ "$#" -gt 2 ]]; then
  echo "usage: $0 [expected-next-cell] [expected-seed]" >&2
  exit 2
fi
if [[ "$#" -ge 1 && "$1" != "$CELL_ID" ]]; then
  echo "[ERROR] requested cell $1 is not frozen Stage-2 next cell $CELL_ID" >&2
  exit 2
fi
if [[ "$#" -eq 2 && "$2" != "$SEED" ]]; then
  echo "[ERROR] requested seed $2 is not frozen Stage-2 next seed $SEED" >&2
  exit 2
fi

REQUIRED_CONFIRM="EXECUTE-${CELL_ID}-SEED${SEED}"
ACTUAL_CONFIRM="${WP8_CONFIRM_STAGE2_NEXT:-}"
[[ "$ACTUAL_CONFIRM" == "$REQUIRED_CONFIRM" ]] || {
  echo "[ERROR] Stage-2 deliberate confirmation mismatch" >&2
  echo "required_confirmation=$REQUIRED_CONFIRM" >&2
  exit 2
}

RUN_ID="$(
PYTHONPATH="$ROOT" python3 - "$CELL_ID" "$SEED" <<'PY'
import sys
from src.mission_recovery.wp8_stage2_pilot import allocate_stage2_run_id
print(allocate_stage2_run_id(cell_id=sys.argv[1], seed=int(sys.argv[2])))
PY
)"

PYTHONPATH="$ROOT" python3 -m src.mission_recovery.wp8_stage2_runtime_wiring \
  check-gate \
  --pilot-config "$PILOT_CONFIG" \
  --stage1-ledger "$STAGE1_LEDGER" \
  --cell-id "$CELL_ID" \
  --seed "$SEED" \
  --run-id "$RUN_ID" >/dev/null

docker info >/dev/null 2>&1

echo "stage2_cell=$CELL_ID"
echo "stage2_seed=$SEED"
echo "stage2_run_id=$RUN_ID"
echo "stage2_runtime_path=$ROUTE"
echo "stage2_runtime_family=$FAMILY"
echo "stage2_prior_attempt_count=$PRIOR_ATTEMPTS"
echo "stage2_prior_valid_repetition_count=$VALID_COUNT"
echo "stage2_remaining_valid_repetitions_before=$REMAINING"
echo "stage2_reviewed_invalid_attempt_count=$REVIEWED_INVALID_COUNT"
echo "stage2_validated_commit=$VALIDATED_SHA"
echo "stage2_validated_ci_run_id=$VALIDATED_CI_RUN_ID"
echo "pilot_data_generation_begin=true"

mkdir -p "$STAGE2_DIR"
EVIDENCE="$STAGE2_DIR/$RUN_ID"
mkdir -p "$EVIDENCE"
CONTROLLER_LOG="$EVIDENCE/controller.log"

case "$ROUTE" in
  command_generic)
    COMMAND=(bash "$ROOT/scripts/run_wp8_command_stage1_development.sh" "$CELL_ID")
    ;;
  recovery_full_trusted)
    COMMAND=(bash "$ROOT/scripts/run_wp8_recovery_binding_preflight.sh" "$CELL_ID")
    ;;
  observability_generic)
    COMMAND=(bash "$ROOT/scripts/run_wp8_observability_stage1_development.sh" "$CELL_ID")
    ;;
  *)
    echo "[ERROR] unsupported Stage-2 runtime path: $ROUTE" >&2
    exit 2
    ;;
esac

set +e
WP8_STAGE2_PILOT=1 \
WP8_STAGE2_CONTROLLER=1 \
WP8_PILOT_SEED="$SEED" \
RUN_ID="$RUN_ID" \
"${COMMAND[@]}" 2>&1 | tee "$CONTROLLER_LOG"
RC=${PIPESTATUS[0]}
set -e

ATTEMPT_STATUS="$EVIDENCE/controller-attempt-status.txt"

PYTHONPATH="$ROOT" python3 - \
  "$PILOT_CONFIG" "$STAGE1_LEDGER" "$STAGE2_LEDGER" \
  "$CELL_ID" "$SEED" "$RUN_ID" "$EVIDENCE" "$CONTROLLER_LOG" \
  "$RC" "$ATTEMPT_STATUS" "$REVIEWED_INVALID_RUN_IDS" <<'PY'
import json
import re
import sys
from pathlib import Path

from src.mission_recovery.wp8_stage2_pilot import (
    new_stage2_ledger,
    record_stage2_attempt,
    stage2_progress,
)

(
    pilot_path,
    stage1_ledger_path,
    stage2_ledger_path,
    cell_id,
    seed,
    run_id,
    evidence_path,
    log_path,
    rc,
    attempt_status_path,
    reviewed_invalid_run_ids,
) = sys.argv[1:]

reviewed = {
    value
    for value in reviewed_invalid_run_ids.split(",")
    if value
}
seed = int(seed)
rc = int(rc)
pilot = json.loads(Path(pilot_path).read_text(encoding="utf-8"))
stage1 = json.loads(
    Path(stage1_ledger_path).read_text(encoding="utf-8")
)
stage2_file = Path(stage2_ledger_path)
stage2 = (
    json.loads(stage2_file.read_text(encoding="utf-8"))
    if stage2_file.exists()
    else new_stage2_ledger(pilot)
)
evidence = Path(evidence_path)
log_text = Path(log_path).read_text(
    encoding="utf-8",
    errors="replace",
)
acceptance_path = evidence / "stage2-acceptance.json"
run_record_path = evidence / "run-record.json"
provenance_path = evidence / "binding-provenance.json"
attempt_status = "RUN_INVALID"


def retain_invalid(
    *,
    invalid_class,
    invalid_cause,
    exit_code,
    invalid_origin,
    audit_error_type=None,
    audit_error=None,
):
    evidence.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema": 1,
        "classification": "WP8_STAGE2_RUN_INVALID",
        "cell_id": cell_id,
        "seed": seed,
        "run_id": run_id,
        "exit_code": int(exit_code),
        "invalid_class": invalid_class,
        "invalid_cause": invalid_cause,
        "invalid_origin": invalid_origin,
        "experiment_failure_claimed": False,
        "development_preflight": False,
        "pilot_data": False,
        "fabricated_primary_metrics": False,
    }
    if audit_error_type is not None:
        payload["audit_error_type"] = audit_error_type
    if audit_error is not None:
        payload["audit_error"] = audit_error[:500]

    (evidence / "pilot-run-invalid.json").write_text(
        json.dumps(payload, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )

    record_stage2_attempt(
        pilot=pilot,
        ledger=stage2,
        cell_id=cell_id,
        seed=seed,
        run_id=run_id,
        status="RUN_INVALID",
        retained_evidence_ref=str(evidence.relative_to(Path.cwd())),
        invalid_class=invalid_class,
        invalid_cause=invalid_cause,
    )


if rc == 0:
    try:
        if not (
            acceptance_path.is_file()
            and run_record_path.is_file()
            and provenance_path.is_file()
        ):
            raise ValueError(
                "runner returned success without complete Stage-2 bound evidence"
            )

        acceptance = json.loads(
            acceptance_path.read_text(encoding="utf-8")
        )
        provenance = json.loads(
            provenance_path.read_text(encoding="utf-8")
        )

        if acceptance.get("cell_id") != cell_id:
            raise ValueError("Stage-2 acceptance cell mismatch")
        if int(acceptance.get("seed")) != seed:
            raise ValueError("Stage-2 acceptance seed mismatch")
        if provenance.get("development_preflight") is not False:
            raise ValueError("successful Stage-2 provenance is marked development")
        if provenance.get("pilot_data") is not True:
            raise ValueError("successful Stage-2 provenance lacks pilot_data=true")

        record_stage2_attempt(
            pilot=pilot,
            ledger=stage2,
            cell_id=cell_id,
            seed=seed,
            run_id=run_id,
            status="VALID",
            retained_evidence_ref=str(evidence.relative_to(Path.cwd())),
            schema_valid=acceptance["schema_valid"],
            raw_metric_inputs_complete=acceptance[
                "raw_metric_inputs_complete"
            ],
            expected_policy_semantics_met=acceptance[
                "expected_policy_semantics_met"
            ],
        )
        attempt_status = "VALID"
    except Exception as exc:
        retain_invalid(
            invalid_class="non_infrastructure",
            invalid_cause="controller_post_runner_audit_failure",
            exit_code=0,
            invalid_origin="controller_post_run_audit",
            audit_error_type=type(exc).__name__,
            audit_error=str(exc),
        )
        print("stage2_controller_post_runner_audit_invalid=true")
else:
    matches = re.findall(
        r"(?:failure_phase|failed_phase)=([A-Za-z0-9_]+)",
        log_text,
    )
    phase = matches[-1] if matches else "family_runner_exit"
    upper = phase.upper()
    infrastructure = any(
        token in upper
        for token in (
            "INITIALIZATION",
            "NOMINAL",
            "CFS",
            "CI_",
            "NETWORK",
            "DOCKER",
            "STARTUP",
            "DESTINATION",
        )
    )
    invalid_class = (
        "infrastructure" if infrastructure else "non_infrastructure"
    )
    cause = re.sub(
        r"[^a-z0-9_]+",
        "_",
        phase.lower(),
    ).strip("_")
    if not cause:
        cause = f"family_runner_exit_{rc}"

    retain_invalid(
        invalid_class=invalid_class,
        invalid_cause=cause,
        exit_code=rc,
        invalid_origin="family_runner",
    )

stage2_file.write_text(
    json.dumps(stage2, sort_keys=True, indent=2) + "\n",
    encoding="utf-8",
)
Path(attempt_status_path).write_text(
    attempt_status + "\n",
    encoding="utf-8",
)

progress = stage2_progress(
    pilot,
    stage1,
    stage2,
    reviewed_invalid_run_ids=reviewed,
)
print(
    "stage2_valid_repetition_count="
    + str(progress["valid_repetition_count"])
)
print(
    "stage2_remaining_valid_repetitions="
    + str(progress["remaining_valid_repetitions"])
)
print(
    "stage2_reviewed_invalid_attempt_count="
    + str(progress["reviewed_invalid_attempt_count"])
)
print(
    "stage2_unreviewed_invalid_attempt_count="
    + str(progress["unreviewed_invalid_attempt_count"])
)
print(
    "stage2_progression_blocked_for_review="
    + str(progress["progression_blocked_for_review"]).lower()
)
print(
    "stage2_complete="
    + str(progress["stage_2_complete"]).lower()
)
next_item = progress["next_repetition"]
if next_item is None:
    print("stage2_next_cell=None")
    print("stage2_next_seed=None")
else:
    print("stage2_next_cell=" + next_item["cell_id"])
    print("stage2_next_seed=" + str(next_item["seed"]))
PY

ATTEMPT_STATUS_VALUE="$(cat "$ATTEMPT_STATUS")"

if [[ "$ATTEMPT_STATUS_VALUE" != "VALID" ]]; then
  echo "STAGE2_PILOT_REPETITION=RUN_INVALID"
  echo "DO_NOT_RERUN_WITHOUT_REVIEW=true"
  if [[ "$RC" -ne 0 ]]; then
    exit "$RC"
  fi
  exit 3
fi

echo "STAGE2_PILOT_REPETITION=VALID"
echo "stage2_cell=$CELL_ID"
echo "stage2_seed=$SEED"
echo "stage2_run_id=$RUN_ID"
echo "pilot_data_generated=true"
echo "automatic_next_repetition_invoked=false"
