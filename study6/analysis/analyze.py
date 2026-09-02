from __future__ import annotations

import csv
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from study6.src.artifact_trust_model import GATES, adversarial_rows, benign_unavailability_rows


def write_csv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "study6_runtime"
    out.mkdir(parents=True, exist_ok=True)

    block_a = adversarial_rows()
    block_b = benign_unavailability_rows()

    write_csv(
        out / "gate_state_matrix.csv",
        block_a,
        ["block", "state_id", "gate_id", "qualified", "objective_baseline_correct", "unsafe_qualified", "correct_rejected"],
    )
    write_csv(
        out / "benign_unavailability.csv",
        block_b,
        ["block", "missing_signals", "missing_count", "gate_id", "qualified", "objective_baseline_correct", "benign_availability_loss"],
    )

    summary: list[dict[str, object]] = []
    for gate_id in GATES:
        a = [row for row in block_a if row["gate_id"] == gate_id]
        b = [row for row in block_b if row["gate_id"] == gate_id]
        unsafe_states = sorted(str(row["state_id"]) for row in a if row["unsafe_qualified"])
        detected_states = sorted(
            str(row["state_id"])
            for row in a
            if (not row["objective_baseline_correct"]) and (not row["qualified"])
        )
        loss_rows = [row for row in b if row["benign_availability_loss"]]
        summary.append({
            "gate_id": gate_id,
            "required_signal_count": len(GATES[gate_id]),
            "unsafe_qualified_state_count": len(unsafe_states),
            "unsafe_qualified_states": ";".join(unsafe_states) if unsafe_states else "NONE",
            "incorrect_state_rejection_count": len(detected_states),
            "incorrect_states_rejected": ";".join(detected_states) if detected_states else "NONE",
            "benign_loss_subset_count": len(loss_rows),
            "minimum_missing_signals_for_benign_loss": min((int(row["missing_count"]) for row in loss_rows), default=-1),
        })

    write_csv(
        out / "gate_summary.csv",
        summary,
        [
            "gate_id",
            "required_signal_count",
            "unsafe_qualified_state_count",
            "unsafe_qualified_states",
            "incorrect_state_rejection_count",
            "incorrect_states_rejected",
            "benign_loss_subset_count",
            "minimum_missing_signals_for_benign_loss",
        ],
    )

    report = {
        "schema": 1,
        "experiment_id": "S6-SCTR-001",
        "status": "COMPLETE",
        "finite_population_observations": len(block_a) + len(block_b),
        "block_a_observations": len(block_a),
        "block_b_observations": len(block_b),
        "gates": len(GATES),
        "baseline_states": 6,
        "benign_missing_signal_subsets": 64,
        "objective_correctness_oracle_is_gate_input": False,
        "malware_or_exploit_implemented": False,
        "global_gate_ranking_claimed": False,
    }
    (out / "REPORT.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
