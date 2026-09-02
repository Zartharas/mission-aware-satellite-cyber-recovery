from __future__ import annotations

import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from quorum_model import N, as_rows, run_population  # noqa: E402


def summarize(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    groups: dict[tuple[str, str, int], list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        groups[(str(row["rule_id"]), str(row["block"]), int(row["affected_count"]))].append(row)

    output: list[dict[str, object]] = []
    for (rule_id, block, affected_count), group in sorted(groups.items()):
        key = "unsafe_qualified" if block == "SAFETY" else "false_conservative"
        failures = sum(bool(row[key]) for row in group)
        output.append(
            {
                "rule_id": rule_id,
                "block": block,
                "affected_count": affected_count,
                "affected_fraction": affected_count / N,
                "subset_count": len(group),
                "failure_count": failures,
                "failure_rate": failures / len(group),
            }
        )
    return output


def thresholds(summary: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[tuple[str, str], dict[int, float]] = defaultdict(dict)
    for row in summary:
        grouped[(str(row["rule_id"]), str(row["block"]))][int(row["affected_count"])] = float(row["failure_rate"])

    output: list[dict[str, object]] = []
    for (rule_id, block), curve in sorted(grouped.items()):
        first = next((k for k in sorted(curve) if curve[k] > 0), None)
        systematic = next((k for k in sorted(curve) if curve[k] == 1.0), None)
        output.append(
            {
                "rule_id": rule_id,
                "block": block,
                "first_failure_count": first,
                "systematic_failure_count": systematic,
                "first_failure_fraction": None if first is None else first / N,
                "systematic_failure_fraction": None if systematic is None else systematic / N,
            }
        )
    return output


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError("cannot write empty CSV")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    output = Path(sys.argv[1] if len(sys.argv) > 1 else "study4/results/canonical")
    output.mkdir(parents=True, exist_ok=True)
    observations = as_rows(run_population())
    curves = summarize(observations)
    threshold_rows = thresholds(curves)
    write_csv(output / "observations.csv", observations)
    write_csv(output / "failure_curves.csv", curves)
    write_csv(output / "thresholds.csv", threshold_rows)
    report = {
        "schema": 1,
        "experiment_id": "S4-MPQ-001",
        "status": "COMPLETE",
        "producer_count": 7,
        "provenance_domains": 3,
        "rules": 18,
        "observations": len(observations),
        "threshold_rows": len(threshold_rows),
        "random_seeds": False,
    }
    (output / "REPORT.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
