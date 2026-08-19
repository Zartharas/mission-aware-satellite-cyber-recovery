#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PILOT_CONFIG="$ROOT/configs/wp8_pilot_design.json"
LEDGER_DIR="$ROOT/results/wp8/pilot/stage1"
LEDGER="$LEDGER_DIR/stage1-ledger.json"

cd "$ROOT"

test -z "$(git status --short)" || {
  echo "[ERROR] repository worktree must be clean before Stage-1 pilot" >&2
  exit 1
}

for cmd in git python3 docker; do
  command -v "$cmd" >/dev/null 2>&1 || {
    echo "[ERROR] missing required command: $cmd" >&2
    exit 1
  }
done

NEXT="$(
PYTHONPATH="$ROOT" python3 - "$PILOT_CONFIG" "$LEDGER" <<'PY'
import json
import sys
from pathlib import Path
from src.mission_recovery.wp8_stage1_pilot import (
    deterministic_stage1_cell_ids,
    new_stage1_ledger,
    stage1_progress,
)
pilot=json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
ledger_path=Path(sys.argv[2])
if ledger_path.exists():
    ledger=json.loads(ledger_path.read_text(encoding="utf-8"))
else:
    ledger=new_stage1_ledger(pilot)
progress=stage1_progress(pilot,ledger)
if progress["pilot_halt_required"]:
    raise SystemExit("Stage-1 pilot halt condition is active")
valid={row["cell_id"] for row in ledger["attempts"] if row["status"]=="VALID"}
for cell_id in deterministic_stage1_cell_ids(pilot):
    if cell_id not in valid:
        print(cell_id)
        break
else:
    print("COMPLETE")
PY
)"

if [[ "$NEXT" == COMPLETE ]]; then
  echo "STAGE1_PILOT_STATUS=COMPLETE"
  exit 0
fi

if [[ "$#" -gt 1 ]]; then
  echo "usage: $0 [expected-next-cell]" >&2
  exit 2
fi
if [[ "$#" -eq 1 && "$1" != "$NEXT" ]]; then
  echo "[ERROR] requested cell $1 is not frozen next cell $NEXT" >&2
  exit 2
fi
CELL_ID="$NEXT"

RUN_ID="$(
PYTHONPATH="$ROOT" python3 - "$CELL_ID" <<'PY'
import sys
from src.mission_recovery.wp8_stage1_pilot import allocate_run_id
print(allocate_run_id(cell_id=sys.argv[1],seed=101))
PY
)"

PYTHONPATH="$ROOT" python3 -m src.mission_recovery.wp8_stage1_runtime_wiring   check-gate   --pilot-config "$PILOT_CONFIG"   --cell-id "$CELL_ID"   --run-id "$RUN_ID" >/dev/null

docker info >/dev/null 2>&1
mkdir -p "$LEDGER_DIR"

ROUTE="$(
PYTHONPATH="$ROOT" python3 - "$PILOT_CONFIG" "$CELL_ID" <<'PY'
import json,sys
from pathlib import Path
from src.mission_recovery.wp8_stage1_runtime_wiring import (
    PILOT_RUNTIME_PATH_BY_CELL,
    require_active_pilot,
)
pilot=json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
cell_id=sys.argv[2]
require_active_pilot(pilot,cell_id=cell_id)
print(PILOT_RUNTIME_PATH_BY_CELL[cell_id])
PY
)"

EVIDENCE="$ROOT/results/wp8/pilot/stage1/$RUN_ID"
mkdir -p "$EVIDENCE"
CONTROLLER_LOG="$EVIDENCE/controller.log"

case "$ROUTE" in
  command_generic)
    COMMAND=(bash "$ROOT/scripts/run_wp8_command_stage1_development.sh" "$CELL_ID")
    ;;
  recovery_generic)
    COMMAND=(bash "$ROOT/scripts/run_wp8_recovery_stage1_development.sh" "$CELL_ID")
    ;;
  recovery_full_trusted)
    COMMAND=(bash "$ROOT/scripts/run_wp8_recovery_binding_preflight.sh" "$CELL_ID")
    ;;
  observability_generic)
    COMMAND=(bash "$ROOT/scripts/run_wp8_observability_stage1_development.sh" "$CELL_ID")
    ;;
  *)
    echo "[ERROR] unsupported Stage-1 runtime path: $ROUTE" >&2
    exit 2
    ;;
esac

echo "stage1_cell=$CELL_ID"
echo "stage1_seed=101"
echo "stage1_run_id=$RUN_ID"
echo "stage1_runtime_path=$ROUTE"
echo "pilot_data_generation_begin=true"

set +e
WP8_STAGE1_PILOT=1 WP8_STAGE1_CONTROLLER=1 RUN_ID="$RUN_ID" "${COMMAND[@]}" 2>&1 | tee "$CONTROLLER_LOG"
RC=${PIPESTATUS[0]}
set -e

ATTEMPT_STATUS="$EVIDENCE/controller-attempt-status.txt"

PYTHONPATH="$ROOT" python3 - \
  "$PILOT_CONFIG" "$LEDGER" "$CELL_ID" "$RUN_ID" \
  "$EVIDENCE" "$CONTROLLER_LOG" "$RC" "$ATTEMPT_STATUS" <<'PY'
import json
import re
import sys
from pathlib import Path

from src.mission_recovery.wp8_stage1_pilot import (
    new_stage1_ledger,
    record_attempt,
    stage1_progress,
)

(
    pilot_path,
    ledger_path,
    cell_id,
    run_id,
    evidence_path,
    log_path,
    rc,
    attempt_status_path,
) = sys.argv[1:]

rc = int(rc)
pilot = json.loads(Path(pilot_path).read_text(encoding="utf-8"))
ledger_file = Path(ledger_path)
ledger = (
    json.loads(ledger_file.read_text(encoding="utf-8"))
    if ledger_file.exists()
    else new_stage1_ledger(pilot)
)
evidence = Path(evidence_path)
log_text = Path(log_path).read_text(
    encoding="utf-8",
    errors="replace",
)
acceptance_path = evidence / "stage1-acceptance.json"
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
        "classification": "WP8_STAGE1_RUN_INVALID",
        "cell_id": cell_id,
        "seed": 101,
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

    record_attempt(
        pilot=pilot,
        ledger=ledger,
        cell_id=cell_id,
        run_id=run_id,
        status="RUN_INVALID",
        retained_evidence_ref=str(
            evidence.relative_to(Path.cwd())
        ),
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
                "runner returned success without complete bound evidence"
            )

        acceptance = json.loads(
            acceptance_path.read_text(encoding="utf-8")
        )
        provenance = json.loads(
            provenance_path.read_text(encoding="utf-8")
        )

        if provenance.get("development_preflight") is not False:
            raise ValueError(
                "successful pilot provenance is marked development"
            )
        if provenance.get("pilot_data") is not True:
            raise ValueError(
                "successful pilot provenance lacks pilot_data=true"
            )

        record_attempt(
            pilot=pilot,
            ledger=ledger,
            cell_id=cell_id,
            run_id=run_id,
            status="VALID",
            retained_evidence_ref=str(
                evidence.relative_to(Path.cwd())
            ),
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
        print("controller_post_runner_audit_invalid=true")
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

ledger_file.write_text(
    json.dumps(ledger, sort_keys=True, indent=2) + "\n",
    encoding="utf-8",
)
Path(attempt_status_path).write_text(
    attempt_status + "\n",
    encoding="utf-8",
)

progress = stage1_progress(pilot, ledger)
print("stage1_valid_cell_count=" + str(progress["valid_cell_count"]))
print(
    "stage1_all_cells_valid="
    + str(progress["stage_1_all_cells_valid"]).lower()
)
print(
    "stage1_pilot_halt_required="
    + str(progress["pilot_halt_required"]).lower()
)
print(
    "stage2_progression_gate_passed="
    + str(progress["stage_2_progression_gate_passed"]).lower()
)
PY

ATTEMPT_STATUS_VALUE="$(cat "$ATTEMPT_STATUS")"

if [[ "$ATTEMPT_STATUS_VALUE" != "VALID" ]]; then
  echo "STAGE1_PILOT_CELL=RUN_INVALID"
  if [[ "$RC" -ne 0 ]]; then
    exit "$RC"
  fi
  exit 3
fi

echo "STAGE1_PILOT_CELL=VALID"
echo "stage1_cell=$CELL_ID"
echo "stage1_seed=101"
echo "stage1_run_id=$RUN_ID"
echo "pilot_data_generated=true"
