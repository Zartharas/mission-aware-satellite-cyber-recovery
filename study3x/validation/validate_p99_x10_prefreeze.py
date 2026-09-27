#!/usr/bin/env python3
"""Pre-freeze validation for the S3X P99_X10 diagnostic candidate.

This validator consumes only the already generated Phase-5A R2 aggregate
artifacts. It does not read source telemetry archives, emit timestamp-level
intervals, execute recovery logic, or freeze a gap rule.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
from typing import Iterable

EXPERIMENT_ID = "S3X-ETA-001"
SOURCE_FREEZE_ID = "S3X-ESA-V2-SOURCE-FREEZE-001"
CANDIDATE_RULE = "P99_X10"

EXPECTED_SENSITIVITY_SHA256 = (
    "f690dd230b2897dd74ec880be0de9c207cbb3c975fb4f7740bb18b49df55b88e"
)
EXPECTED_FREQUENCY_SHA256 = (
    "1399dde74c0cad144e4be4b5c0af201030eaf9ae70621c8b5b70ff9a52b78349"
)
EXPECTED_SUMMARY_SHA256 = (
    "c57fb506c08f03f69f3bed7326355bc97a318f7b6b5015c7745cc3e956865cc6"
)
EXPECTED_PROJECTION_SHA256 = (
    "f15338f1790f60d83d2c849542f6d6e3b21a8c49f7d413cdc5098e35952294d1"
)

EXPECTED_CHANNELS = 176
EXPECTED_SENSITIVITY_ROWS = 1408
EXPECTED_TOTAL_EXCEEDANCES = 1919
EXPECTED_CHANNELS_WITH_EXCEEDANCES = 171
EXPECTED_ZERO_CHANNELS = {
    ("ESA-Mission2", "channel_66.zip"),
    ("ESA-Mission2", "channel_67.zip"),
    ("ESA-Mission2", "channel_68.zip"),
    ("ESA-Mission2", "channel_69.zip"),
    ("ESA-Mission2", "channel_100.zip"),
}
PROJECTION_COLUMNS = (
    "mission",
    "channel_file",
    "channel_sha256",
    "positive_delta_count",
    "cadence_p99_seconds",
    "threshold_seconds",
    "exceedance_count",
)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def fail(message: str) -> None:
    raise SystemExit(message)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def normalized_float(value: str | float) -> str:
    return format(float(value), ".17g")


def canonical_projection(rows: Iterable[dict[str, str]]) -> bytes:
    selected = sorted(
        rows,
        key=lambda row: (row["mission"], row["channel_file"]),
    )
    lines = [",".join(PROJECTION_COLUMNS)]
    for row in selected:
        lines.append(
            ",".join(
                (
                    row["mission"],
                    row["channel_file"],
                    row["channel_sha256"],
                    str(int(row["positive_delta_count"])),
                    normalized_float(row["cadence_p99_seconds"]),
                    normalized_float(row["threshold_seconds"]),
                    str(int(row["exceedance_count"])),
                )
            )
        )
    return ("\n".join(lines) + "\n").encode("utf-8")


def projection_sha256(rows: Iterable[dict[str, str]]) -> str:
    return hashlib.sha256(canonical_projection(rows)).hexdigest()


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_summary(
    summary: dict,
    sensitivity_sha: str,
    frequency_sha: str,
) -> None:
    require(summary.get("schema") == 2, "R2 summary schema must be 2")
    require(
        summary.get("audit_id") == "S3X-GAP-SENSITIVITY-002",
        "unexpected R2 summary audit_id",
    )
    require(
        summary.get("experiment_id") == EXPERIMENT_ID,
        "unexpected R2 experiment_id",
    )
    require(
        summary.get("mode") == "READ_ONLY_CADENCE_GAP_SENSITIVITY",
        "unexpected R2 summary mode",
    )
    require(
        summary.get("source_freeze", {}).get("freeze_id") == SOURCE_FREEZE_ID,
        "unexpected source-freeze identity",
    )
    require(
        summary.get("channels_analyzed") == EXPECTED_CHANNELS,
        "unexpected R2 channel count",
    )
    require(summary.get("candidate_rule_count") == 8, "unexpected R2 rule count")

    output_contract = summary.get("output_contract", {})
    require(
        output_contract.get("schema_version") == 2,
        "unexpected output-contract schema version",
    )
    require(
        output_contract.get("legacy_metric_name_collision_present") is False,
        "legacy output collision must remain absent",
    )

    output_files = summary.get("output_files", {})
    require(
        output_files.get("sensitivity_csv", {}).get("sha256") == sensitivity_sha,
        "summary sensitivity CSV hash binding mismatch",
    )
    require(
        output_files.get("delta_frequency_csv", {}).get("sha256") == frequency_sha,
        "summary delta-frequency CSV hash binding mismatch",
    )

    for key in (
        "gap_rule_selected",
        "gap_rule_frozen",
        "trace_population_frozen",
        "timestamp_level_gap_traces_emitted",
        "recovery_policy_execution_performed",
        "scientific_results_generated",
    ):
        require(summary.get(key) is False, f"closed R2 gate changed: {key}")


def validate_candidate_rows(rows: list[dict[str, str]]) -> dict:
    require(
        len(rows) == EXPECTED_SENSITIVITY_ROWS,
        f"unexpected sensitivity row count: {len(rows)}",
    )

    candidate = [row for row in rows if row["candidate_rule"] == CANDIDATE_RULE]
    require(
        len(candidate) == EXPECTED_CHANNELS,
        f"expected {EXPECTED_CHANNELS} P99_X10 rows, got {len(candidate)}",
    )

    keys = [(row["mission"], row["channel_file"]) for row in candidate]
    require(len(keys) == len(set(keys)), "duplicate P99_X10 channel rows")

    for row in candidate:
        p99 = float(row["cadence_p99_seconds"])
        threshold = float(row["threshold_seconds"])
        require(
            math.isclose(threshold, p99 * 10.0, rel_tol=0.0, abs_tol=1e-9),
            f"P99_X10 threshold formula mismatch: {row['mission']}/{row['channel_file']}",
        )

        count = int(row["exceedance_count"])
        if count > 0:
            minimum = row["exceedance_min_seconds"]
            require(
                minimum != "",
                f"missing minimum exceedance: {row['mission']}/{row['channel_file']}",
            )
            require(
                float(minimum) > threshold,
                f"non-strict exceedance detected: {row['mission']}/{row['channel_file']}",
            )
        else:
            for field in (
                "exceedance_min_seconds",
                "exceedance_median_seconds",
                "exceedance_p95_seconds",
                "exceedance_p99_seconds",
                "exceedance_max_seconds",
            ):
                require(
                    row[field] == "",
                    f"zero-count row has populated {field}: "
                    f"{row['mission']}/{row['channel_file']}",
                )
            require(
                float(row["cadence_max_seconds"]) <= threshold,
                f"zero-count row has cadence max above threshold: "
                f"{row['mission']}/{row['channel_file']}",
            )

    total = sum(int(row["exceedance_count"]) for row in candidate)
    with_exceedances = sum(int(row["exceedance_count"]) > 0 for row in candidate)
    zero_channels = {
        (row["mission"], row["channel_file"])
        for row in candidate
        if int(row["exceedance_count"]) == 0
    }

    require(
        total == EXPECTED_TOTAL_EXCEEDANCES,
        f"P99_X10 aggregate mismatch: expected {EXPECTED_TOTAL_EXCEEDANCES}, got {total}",
    )
    require(
        with_exceedances == EXPECTED_CHANNELS_WITH_EXCEEDANCES,
        "unexpected P99_X10 nonzero-channel count",
    )
    require(
        zero_channels == EXPECTED_ZERO_CHANNELS,
        f"zero-exceedance channel set mismatch: {sorted(zero_channels)}",
    )

    projection_sha = projection_sha256(candidate)
    require(
        projection_sha == EXPECTED_PROJECTION_SHA256,
        "P99_X10 canonical channel projection SHA-256 mismatch",
    )

    return {
        "channels": len(candidate),
        "total_exceedance_count": total,
        "channels_with_exceedances": with_exceedances,
        "channels_with_zero_exceedances": len(zero_channels),
        "zero_exceedance_channels": [
            {"mission": mission, "channel_file": channel}
            for mission, channel in sorted(zero_channels)
        ],
        "canonical_channel_projection_sha256": projection_sha,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sensitivity-csv", type=Path, required=True)
    parser.add_argument("--delta-frequency-csv", type=Path, required=True)
    parser.add_argument("--summary-json", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    args = parser.parse_args()

    for path in (
        args.sensitivity_csv,
        args.delta_frequency_csv,
        args.summary_json,
    ):
        require(path.is_file(), f"missing required R2 artifact: {path}")

    sensitivity_sha = sha256(args.sensitivity_csv)
    frequency_sha = sha256(args.delta_frequency_csv)
    summary_sha = sha256(args.summary_json)

    require(
        sensitivity_sha == EXPECTED_SENSITIVITY_SHA256,
        "R2 sensitivity CSV SHA-256 mismatch",
    )
    require(
        frequency_sha == EXPECTED_FREQUENCY_SHA256,
        "R2 delta-frequency CSV SHA-256 mismatch",
    )
    require(
        summary_sha == EXPECTED_SUMMARY_SHA256,
        "R2 summary JSON SHA-256 mismatch",
    )

    summary = load_json(args.summary_json)
    validate_summary(summary, sensitivity_sha, frequency_sha)
    result = validate_candidate_rows(load_csv(args.sensitivity_csv))

    record = {
        "schema": 1,
        "audit_id": "S3X-P99-X10-PREFREEZE-VALIDATION-001",
        "experiment_id": EXPERIMENT_ID,
        "mode": "PREFREEZE_AGGREGATE_VALIDATION_ONLY",
        "candidate_rule": CANDIDATE_RULE,
        "candidate_status": "VALIDATED_FOR_AUTHOR_REVIEW_NOT_SELECTED_NOT_FROZEN",
        "inputs": {
            "sensitivity_csv": {
                "file": args.sensitivity_csv.name,
                "sha256": sensitivity_sha,
            },
            "delta_frequency_csv": {
                "file": args.delta_frequency_csv.name,
                "sha256": frequency_sha,
            },
            "summary_json": {
                "file": args.summary_json.name,
                "sha256": summary_sha,
            },
        },
        "formula": "threshold_seconds = 10 * channel-specific cadence_p99_seconds",
        "comparison": "positive inter-sample delta > threshold_seconds",
        "validation": result,
        "telemetry_archives_read": False,
        "gap_rule_selected": False,
        "gap_rule_frozen": False,
        "trace_population_frozen": False,
        "timestamp_level_gap_traces_emitted": False,
        "recovery_policy_execution_performed": False,
        "scientific_results_generated": False,
        "interpretation_controls": [
            "P99_X10 is a pre-freeze candidate diagnostic, not a selected or frozen gap rule",
            "telemetry gap is not asserted to be RF contact loss",
            "telemetry anomaly is not asserted to be cyberattack truth",
            "gap duration is not asserted to be recovery latency",
            "no timestamp-level gap trace is emitted by this validator",
        ],
        "next_gate": (
            "AUTHOR_REVIEW_OF_P99_X10_PRE_FREEZE_VALIDATION_"
            "BEFORE_GAP_RULE_FREEZE_OR_TIMESTAMP_TRACE_EXTRACTION"
        ),
    }

    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(
        json.dumps(record, indent=2) + "\n",
        encoding="utf-8",
    )

    print("S3X_P99_X10_PREFREEZE_VALIDATION=PASS")
    print(f"channels={result['channels']}")
    print(f"total_exceedance_count={result['total_exceedance_count']}")
    print(
        "channels_with_zero_exceedances="
        f"{result['channels_with_zero_exceedances']}"
    )
    print(
        "canonical_channel_projection_sha256="
        f"{result['canonical_channel_projection_sha256']}"
    )
    print(f"output_json={args.output_json.resolve()}")
    print("gap_rule_selected=NO")
    print("gap_rule_frozen=NO")
    print("trace_extraction=NO")
    print("recovery_policy_execution=NO")
    print("scientific_execution=NO")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
