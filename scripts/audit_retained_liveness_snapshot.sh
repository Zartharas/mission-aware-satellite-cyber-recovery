#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUN_DIR="${1:-}"

if [[ -z "$RUN_DIR" ]]; then
  echo "Usage: bash scripts/audit_retained_liveness_snapshot.sh artifacts/downlink-diagnostics/<run-id>" >&2
  exit 2
fi
if [[ "$RUN_DIR" != /* ]]; then
  RUN_DIR="$ROOT/$RUN_DIR"
fi
[[ -d "$RUN_DIR" ]] || {
  echo "[ERROR] Retained run directory not found: $RUN_DIR" >&2
  exit 2
}

python3 - "$RUN_DIR" <<'PY'
from __future__ import annotations

import json
import sys
from pathlib import Path

run_dir = Path(sys.argv[1]).resolve()
manifest_path = run_dir / "baseline-manifest.txt"
orch = run_dir / "immutable-ground" / "orchestration"
liveness_path = orch / "liveness.csv"


def parse_kv(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.is_file():
        return values
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            values[key] = value
    return values


manifest = parse_kv(manifest_path)
expected = int(manifest.get("expected_runtime_component_count", "0") or 0)

liveness_lines = []
if liveness_path.is_file():
    liveness_lines = [
        line
        for line in liveness_path.read_text(encoding="utf-8", errors="replace").splitlines()
        if line.strip()
    ]
liveness_header_present = int(bool(liveness_lines))
liveness_data_rows = max(0, len(liveness_lines) - 1)
liveness_nonrunning_rows = 0
for line in liveness_lines[1:]:
    columns = line.split(",")
    if len(columns) < 4 or columns[3] != "running:0":
        liveness_nonrunning_rows += 1

inspect_files = sorted(orch.glob("inspect-*.json"))
inspect_snapshots = 0
inspect_running = 0
inspect_nonrunning: list[str] = []
for path in inspect_files:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        inspect_nonrunning.append(f"{path.name}:unreadable")
        continue
    if isinstance(payload, list):
        payload = payload[0] if payload else {}
    if not isinstance(payload, dict):
        inspect_nonrunning.append(f"{path.name}:invalid")
        continue
    inspect_snapshots += 1
    state = payload.get("State", {})
    status = state.get("Status", "missing") if isinstance(state, dict) else "missing"
    exit_code = state.get("ExitCode", "missing") if isinstance(state, dict) else "missing"
    name = payload.get("Name", path.stem)
    if isinstance(name, str):
        name = name.lstrip("/")
    if status == "running" and exit_code == 0:
        inspect_running += 1
    else:
        inspect_nonrunning.append(f"{name}:{status}:{exit_code}")

if liveness_data_rows == 0:
    checkpoint_diagnosis = "NO_CHECKPOINT_ROWS_PRE_READINESS_EXIT"
elif liveness_nonrunning_rows == 0:
    checkpoint_diagnosis = "CHECKPOINT_ROWS_ALL_RUNNING"
else:
    checkpoint_diagnosis = "CHECKPOINT_NONRUNNING_ROW_PRESENT"

if inspect_snapshots == expected and inspect_running == expected and not inspect_nonrunning:
    snapshot_diagnosis = "FINAL_CAPTURE_ALL_EXPECTED_COMPONENTS_RUNNING"
elif inspect_snapshots == 0:
    snapshot_diagnosis = "FINAL_CONTAINER_INSPECT_SNAPSHOTS_MISSING"
else:
    snapshot_diagnosis = "FINAL_CONTAINER_INSPECT_SNAPSHOT_MISMATCH"

print("RETAINED_LIVENESS_SNAPSHOT_AUDIT")
print(f"run_dir={run_dir}")
print(f"expected_runtime_components={expected}")
print(f"liveness_csv_present={int(liveness_path.is_file())}")
print(f"liveness_csv_header_present={liveness_header_present}")
print(f"liveness_csv_data_rows={liveness_data_rows}")
print(f"liveness_csv_nonrunning_rows={liveness_nonrunning_rows}")
print(f"liveness_checkpoint_diagnosis={checkpoint_diagnosis}")
print(f"final_container_inspect_snapshots={inspect_snapshots}")
print(f"final_container_inspect_running={inspect_running}")
print(f"final_container_inspect_nonrunning={len(inspect_nonrunning)}")
print(f"final_snapshot_diagnosis={snapshot_diagnosis}")
if inspect_nonrunning:
    print("[NONRUNNING_OR_INVALID_SNAPSHOTS]")
    for item in inspect_nonrunning:
        print(item)
print("runtime_launched=0")
print("docker_invoked=0")
print("command_transmission_possible=0")
print("RETAINED_LIVENESS_SNAPSHOT_AUDIT_STATUS=COMPLETE")
PY
