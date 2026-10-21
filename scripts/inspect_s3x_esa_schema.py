#!/usr/bin/env python3
"""Read-only local schema inspector for S3X-ETA-001 candidate ESA data.

This utility does not execute any recovery-policy experiment. It inspects an
already extracted ESA-Mission1 or ESA-Mission2 directory and emits JSON
metadata describing source structure and timestamp cadence.

The script never edits source files.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd


REQUIRED_CSV_COLUMNS = {
    "labels.csv": {"ID", "Channel", "StartTime", "EndTime"},
    "anomaly_types.csv": {"ID", "Category"},
    "telecommands.csv": {"Telecommand", "Priority"},
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def inspect_csv(root: Path, name: str) -> dict:
    path = root / name
    if not path.is_file():
        return {"present": False}
    df = pd.read_csv(path)
    required = REQUIRED_CSV_COLUMNS[name]
    return {
        "present": True,
        "sha256": sha256(path),
        "rows": int(len(df)),
        "columns": list(df.columns),
        "required_columns_present": sorted(required.intersection(df.columns)),
        "required_columns_missing": sorted(required.difference(df.columns)),
    }


def cadence_summary(index: pd.Index) -> dict:
    dt = pd.to_datetime(index)
    series = pd.Series(dt)
    duplicate_count = int(series.duplicated().sum())
    nonmonotonic_count = int((series.diff().dropna() < pd.Timedelta(0)).sum())
    deltas = series.sort_values().drop_duplicates().diff().dropna()
    positive = deltas[deltas > pd.Timedelta(0)]
    if positive.empty:
        stats = {}
    else:
        seconds = positive.dt.total_seconds()
        mode_values = seconds.mode()
        stats = {
            "positive_delta_count": int(len(seconds)),
            "min_seconds": float(seconds.min()),
            "median_seconds": float(seconds.median()),
            "mode_seconds": float(mode_values.iloc[0]) if not mode_values.empty else None,
            "p95_seconds": float(seconds.quantile(0.95)),
            "p99_seconds": float(seconds.quantile(0.99)),
            "max_seconds": float(seconds.max()),
        }
    return {
        "duplicate_timestamp_count": duplicate_count,
        "nonmonotonic_transition_count": nonmonotonic_count,
        **stats,
    }


def inspect_channel(path: Path) -> dict:
    df = pd.read_pickle(path)
    result = {
        "file": path.name,
        "sha256": sha256(path),
        "rows": int(len(df)),
        "columns": [str(c) for c in df.columns],
        "index_type": type(df.index).__name__,
        "index_dtype": str(df.index.dtype),
        "first_timestamp": str(df.index[0]) if len(df) else None,
        "last_timestamp": str(df.index[-1]) if len(df) else None,
    }
    result["cadence"] = cadence_summary(df.index)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("mission_dir", type=Path)
    parser.add_argument(
        "--max-channels",
        type=int,
        default=0,
        help="0 inspects all channel ZIPs; positive values inspect the first N sorted archives",
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    root = args.mission_dir.resolve()
    if not root.is_dir():
        raise SystemExit(f"mission directory not found: {root}")

    channels_dir = root / "channels"
    channel_files = sorted(channels_dir.glob("channel_*.zip"))
    if args.max_channels > 0:
        channel_files = channel_files[: args.max_channels]

    report = {
        "schema": 1,
        "experiment_id": "S3X-ETA-001",
        "mode": "READ_ONLY_SOURCE_SCHEMA_INSPECTION",
        "mission_directory_name": root.name,
        "csv": {name: inspect_csv(root, name) for name in REQUIRED_CSV_COLUMNS},
        "channel_archive_count_inspected": len(channel_files),
        "channels": [inspect_channel(path) for path in channel_files],
        "scientific_recovery_execution": False,
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("s3x_schema_inspection=PASS")
    print(f"output={args.output}")
    print(f"channels_inspected={len(channel_files)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
