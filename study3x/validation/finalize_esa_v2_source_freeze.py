#!/usr/bin/env python3
"""Finalize the S3X ESA-v2 source identity from local verified bytes.

This is a provenance utility, not a scientific runner. It verifies the two
authorized outer archives, validates two read-only schema reports produced by
scripts/inspect_s3x_esa_schema.py, and writes a source-freeze JSON document.

It does not derive telemetry gaps, build a trace population, or execute a
recovery policy.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

EXPECTED = {
    "ESA-Mission1": {
        "archive_name": "ESA-Mission1.zip",
        "md5": "9770ad12ed730238f37c42d5c27ab436",
        "channel_count": 76,
    },
    "ESA-Mission2": {
        "archive_name": "ESA-Mission2.zip",
        "md5": "bfc72012691427d9327eb41f726ce45e",
        "channel_count": 100,
    },
}

REQUIRED_CSV = {
    "labels.csv": {"ID", "Channel", "StartTime", "EndTime"},
    "anomaly_types.csv": {"ID", "Category"},
    "telecommands.csv": {"Telecommand", "Priority"},
}


def digest(path: Path, algorithm: str) -> str:
    h = hashlib.new(algorithm)
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_schema_report(path: Path, mission: str) -> dict:
    report = load_json(path)
    if report.get("experiment_id") != "S3X-ETA-001":
        raise SystemExit(f"{path}: wrong experiment_id")
    if report.get("mode") != "READ_ONLY_SOURCE_SCHEMA_INSPECTION":
        raise SystemExit(f"{path}: wrong inspection mode")
    if report.get("scientific_recovery_execution") is not False:
        raise SystemExit(f"{path}: scientific execution flag must be false")
    if report.get("mission_directory_name") != mission:
        raise SystemExit(f"{path}: mission mismatch")

    expected_count = EXPECTED[mission]["channel_count"]
    if report.get("channel_archive_count_inspected") != expected_count:
        raise SystemExit(
            f"{path}: expected {expected_count} inspected channels, "
            f"got {report.get('channel_archive_count_inspected')}"
        )

    csv = report.get("csv", {})
    for name, required in REQUIRED_CSV.items():
        item = csv.get(name, {})
        if item.get("present") is not True:
            raise SystemExit(f"{path}: missing {name}")
        missing = set(item.get("required_columns_missing", []))
        if missing:
            raise SystemExit(f"{path}: {name} missing columns: {sorted(missing)}")
        present = set(item.get("columns", []))
        if not required.issubset(present):
            raise SystemExit(f"{path}: {name} does not contain required schema")

    channels = report.get("channels", [])
    if len(channels) != expected_count:
        raise SystemExit(f"{path}: channel detail count mismatch")

    for row in channels:
        cadence = row.get("cadence", {})
        for key in (
            "duplicate_timestamp_count",
            "nonmonotonic_transition_count",
        ):
            if key not in cadence:
                raise SystemExit(f"{path}: missing cadence field {key} for {row.get('file')}")
        if not row.get("sha256"):
            raise SystemExit(f"{path}: missing per-channel sha256 for {row.get('file')}")

    return report


def summarize_cadence(report: dict) -> dict:
    duplicate_channels = 0
    nonmonotonic_channels = 0
    medians = []
    maxima = []
    for row in report["channels"]:
        cadence = row["cadence"]
        if int(cadence.get("duplicate_timestamp_count", 0)) > 0:
            duplicate_channels += 1
        if int(cadence.get("nonmonotonic_transition_count", 0)) > 0:
            nonmonotonic_channels += 1
        if cadence.get("median_seconds") is not None:
            medians.append(float(cadence["median_seconds"]))
        if cadence.get("max_seconds") is not None:
            maxima.append(float(cadence["max_seconds"]))
    return {
        "channels": len(report["channels"]),
        "channels_with_duplicate_timestamps": duplicate_channels,
        "channels_with_nonmonotonic_transitions": nonmonotonic_channels,
        "min_channel_median_delta_seconds": min(medians) if medians else None,
        "max_channel_median_delta_seconds": max(medians) if medians else None,
        "max_observed_inter_sample_delta_seconds": max(maxima) if maxima else None,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mission1-archive", type=Path, required=True)
    parser.add_argument("--mission2-archive", type=Path, required=True)
    parser.add_argument("--mission1-schema", type=Path, required=True)
    parser.add_argument("--mission2-schema", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    archive_args = {
        "ESA-Mission1": args.mission1_archive.resolve(),
        "ESA-Mission2": args.mission2_archive.resolve(),
    }
    schema_args = {
        "ESA-Mission1": args.mission1_schema.resolve(),
        "ESA-Mission2": args.mission2_schema.resolve(),
    }

    archive_records = []
    schema_records = {}
    for mission in ("ESA-Mission1", "ESA-Mission2"):
        archive = archive_args[mission]
        expected = EXPECTED[mission]
        if not archive.is_file():
            raise SystemExit(f"archive not found: {archive}")
        if archive.name != expected["archive_name"]:
            raise SystemExit(f"{mission}: expected archive name {expected['archive_name']}")

        md5 = digest(archive, "md5")
        if md5 != expected["md5"]:
            raise SystemExit(
                f"{mission}: Zenodo MD5 mismatch; expected {expected['md5']} got {md5}"
            )
        archive_records.append(
            {
                "mission": mission,
                "archive_name": archive.name,
                "size_bytes": archive.stat().st_size,
                "zenodo_md5": md5,
                "local_sha256": digest(archive, "sha256"),
            }
        )

        schema_report = validate_schema_report(schema_args[mission], mission)
        schema_records[mission] = {
            "report_file": schema_args[mission].name,
            "report_sha256": digest(schema_args[mission], "sha256"),
            "cadence_summary": summarize_cadence(schema_report),
        }

    freeze = {
        "schema": 1,
        "freeze_id": "S3X-ESA-V2-SOURCE-FREEZE-001",
        "experiment_id": "S3X-ETA-001",
        "dataset": "ESA Anomaly Dataset",
        "version": "v2",
        "doi": "10.5281/zenodo.15237121",
        "missions": ["ESA-Mission1", "ESA-Mission2"],
        "archives": archive_records,
        "schema_reports": schema_records,
        "source_identity_frozen": True,
        "gap_rule_frozen": False,
        "trace_population_frozen": False,
        "recovery_policy_execution_performed": False,
        "scientific_results_generated": False,
        "interpretation_controls": [
            "telemetry gap is not asserted to be RF contact loss",
            "telemetry anomaly is not asserted to be cyberattack truth",
            "gap duration is not asserted to be recovery latency",
        ],
        "next_gate": "AUTHOR_REVIEW_OF_CADENCE_EVIDENCE_BEFORE_GAP_RULE_FREEZE",
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(freeze, indent=2) + "\n", encoding="utf-8")
    print("s3x_source_freeze_finalization=PASS")
    print(f"freeze_file={args.output}")
    print("gap_rule_frozen=NO")
    print("trace_population_frozen=NO")
    print("scientific_execution=NO")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
