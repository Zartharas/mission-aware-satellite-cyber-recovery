from __future__ import annotations

from collections import Counter, defaultdict
import csv
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from study5.src.bridge_model import portability_rows, sufficiency_rows, transferability_rows  # noqa: E402


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def analyze(output: Path) -> dict[str, object]:
    portability = portability_rows()
    sufficiency = sufficiency_rows()
    transferability = transferability_rows()
    write_csv(output / "portability_observations.csv", portability)
    write_csv(output / "input_sufficiency.csv", sufficiency)
    write_csv(output / "transferability.csv", transferability)
    attack_labels = {"COMMAND_FLOODING", "DATA_INJECTION", "DEFENCE_IMPAIRMENT", "STORAGE_EXHAUSTION"}
    grouped: dict[tuple[str, str], set[str]] = defaultdict(set)
    for row in portability:
        if row["label"] in attack_labels:
            grouped[(str(row["context"]), str(row["policy"]))].add(str(row["action"]))
    invariant_groups = sum(1 for actions in grouped.values() if len(actions) == 1)
    covered = sum(bool(r["directly_available_from_cucdid_row"]) for r in sufficiency)
    report = {
        "schema": 1,
        "experiment_id": "S5-CUCD-001",
        "status": "COMPLETE",
        "portability_observations": len(portability),
        "input_sufficiency_rows": len(sufficiency),
        "transferability_rows": len(transferability),
        "direct_recovery_input_coverage_count": covered,
        "direct_recovery_input_coverage_fraction": covered / len(sufficiency),
        "attack_subtype_invariant_groups": invariant_groups,
        "attack_subtype_groups_total": len(grouped),
        "attack_subtype_action_invariance": invariant_groups == len(grouped),
        "action_counts": dict(sorted(Counter(str(r["action"]) for r in portability).items())),
        "row_level_cucdid_policy_benchmark_performed": False,
        "ids_accuracy_claimed": False
    }
    (output / "REPORT.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, sort_keys=True))
    return report


if __name__ == "__main__":
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("study5_runtime")
    analyze(out)
