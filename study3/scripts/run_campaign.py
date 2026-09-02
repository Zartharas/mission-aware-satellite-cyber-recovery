from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from temporal_model import as_rows, run_population  # noqa: E402


def _write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError("cannot write empty CSV")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _aggregate(summary_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    groups: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in summary_rows:
        groups[str(row["cell_id"])].append(row)

    output: list[dict[str, object]] = []
    numeric = (
        "unsafe_permissive_epoch_rate",
        "unsafe_qualified_epoch_rate",
        "unsafe_qualified_exposure_s",
        "unsafe_qualified_episode_count",
        "cache_unsafe_qualified_epochs",
        "v5_affected_unsafe_qualified_epochs",
        "protective_epoch_rate",
        "action_transition_count",
    )
    for cell_id in sorted(groups):
        rows = groups[cell_id]
        first = rows[0]
        result: dict[str, object] = {
            "cell_id": cell_id,
            "contact": first["contact"],
            "evidence": first["evidence"],
            "persistence": first["persistence"],
            "policy": first["policy"],
            "onset_phases": len(rows),
        }
        for key in numeric:
            result[f"mean_{key}"] = sum(float(row[key]) for row in rows) / len(rows)
        result["trajectories_with_any_unsafe_qualification"] = sum(
            float(row["unsafe_qualified_epochs"]) > 0 for row in rows
        )
        result["trajectories_with_v5_affected_unsafe_qualification"] = sum(
            float(row["v5_affected_unsafe_qualified_epochs"]) > 0 for row in rows
        )
        output.append(result)
    if len(output) != 30:
        raise AssertionError("aggregate must contain 30 Study-3 cells")
    return output


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="study3/results/campaign")
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()

    epochs, summaries = run_population()
    if len(epochs) != 67620:
        raise AssertionError(f"expected 67,620 epoch rows, found {len(epochs)}")
    if len(summaries) != 1380:
        raise AssertionError(f"expected 1,380 trajectory rows, found {len(summaries)}")

    if args.validate_only:
        print("study3_population_validation=PASS")
        print("study3_trajectories=1380")
        print("study3_epoch_rows=67620")
        return 0

    out = Path(args.output)
    epoch_path = out / "epochs.csv"
    summary_path = out / "trajectory_summary.csv"
    aggregate_path = out / "cell_summary.csv"
    report_path = out / "REPORT.json"

    summary_rows = as_rows(summaries)
    _write_csv(epoch_path, as_rows(epochs))
    _write_csv(summary_path, summary_rows)
    _write_csv(aggregate_path, _aggregate(summary_rows))

    report = {
        "schema": 1,
        "experiment_id": "S3-K4E-001",
        "status": "CAMPAIGN_COMPLETE_PENDING_INDEPENDENT_REPRODUCTION",
        "time_basis": "DETERMINISTIC_LOGICAL_SIL_TIME_NOT_WALL_CLOCK",
        "cells": 30,
        "trajectories": 1380,
        "epoch_rows": 67620,
        "onset_phases_per_cell": 46,
        "random_campaign_seeds": False,
        "false_qualification_origins": ["PRE_ONSET_CACHE", "V5_AFFECTED_RECORD"],
        "files": {
            "epochs.csv": _sha256(epoch_path),
            "trajectory_summary.csv": _sha256(summary_path),
            "cell_summary.csv": _sha256(aggregate_path),
        },
        "science_boundaries": {
            "study1_modified": False,
            "study2_modified": False,
            "operational_spacecraft_or_rf": False,
            "global_policy_rank": False,
        },
    }
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("study3_campaign=PASS")
    print(f"study3_trajectories={report['trajectories']}")
    print(f"study3_epoch_rows={report['epoch_rows']}")
    for name, sha in report["files"].items():
        print(f"study3_sha256[{name}]={sha}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
