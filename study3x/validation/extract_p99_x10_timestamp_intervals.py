#!/usr/bin/env python3
"""Deterministic candidate timestamp-interval extractor for S3X Phase 6.

This module is dormant by default. Real-source execution requires a separate,
versioned authorization record that is intentionally absent from Phase 6A.

It does not freeze a trace population, execute recovery policy logic, generate
scientific results, or make operational interpretations of telemetry gaps.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
from pathlib import Path
from typing import Sequence

EXPERIMENT_ID = "S3X-ETA-001"
PROTOCOL_ID = "S3X-PHASE6-TIMESTAMP-TRACE-EXTRACTION-PROTOCOL-001"
SOURCE_FREEZE_ID = "S3X-ESA-V2-SOURCE-FREEZE-001"
SOURCE_FREEZE_SHA256 = "dd1d71dc074588c12cae24c3718ed758fabd36c41b22755f57ccf98964db9f27"
GAP_RULE_FREEZE_ID = "S3X-P99X10-GAP-RULE-FREEZE-001"
RULE_NAME = "P99_X10"
MULTIPLIER = 10.0
MISSIONS = ("ESA-Mission1", "ESA-Mission2")
EXPECTED_CHANNEL_COUNTS = {"ESA-Mission1": 76, "ESA-Mission2": 100}
EXPECTED_ARCHIVE_SHA256 = {
    "ESA-Mission1": "ba28f761b1deab4dbba4728793bff139fea39dbf9cf0d9c559d619ffe75d5a72",
    "ESA-Mission2": "e8a89be1917b6754a10bd323441e87a82c8cf2e84ed162442c2dcf72ecc346d5",
}
EXPECTED_SCHEMA_SHA256 = {
    "ESA-Mission1": "696ad9bfa90ff37e2c22bb7eb0c1778af4225a09b02038130698d402b53aaa0a",
    "ESA-Mission2": "25533581a3585a8b3056081e1e47f4907d7664103aad5527e374510c0ffba62e",
}
EXPECTED_TOTAL_INTERVALS = 1919
EXPECTED_CHANNELS_WITH_INTERVALS = 171
EXPECTED_ZERO_CHANNELS = {
    ("ESA-Mission2", "channel_66.zip"),
    ("ESA-Mission2", "channel_67.zip"),
    ("ESA-Mission2", "channel_68.zip"),
    ("ESA-Mission2", "channel_69.zip"),
    ("ESA-Mission2", "channel_100.zip"),
}
EXPECTED_PROJECTION_SHA256 = "f15338f1790f60d83d2c849542f6d6e3b21a8c49f7d413cdc5098e35952294d1"
OUTPUT_CSV = "S3X_P99_X10_TIMESTAMP_INTERVALS_001.csv"
OUTPUT_SUMMARY = "S3X_P99_X10_TIMESTAMP_INTERVALS_SUMMARY_001.json"
OUTPUT_MANIFEST = "S3X_P99_X10_TIMESTAMP_INTERVALS_MANIFEST_001.json"

FIELDNAMES = [
    "schema_version",
    "experiment_id",
    "source_freeze_id",
    "source_freeze_sha256",
    "gap_rule_freeze_id",
    "gap_rule",
    "mission",
    "channel_file",
    "channel_sha256",
    "preceding_timestamp_ns",
    "following_timestamp_ns",
    "preceding_timestamp",
    "following_timestamp",
    "delta_nanoseconds",
    "delta_seconds",
    "cadence_p99_seconds",
    "threshold_seconds",
    "comparison_operator",
    "diagnostic_label",
    "interval_id",
]


def fail(message: str) -> None:
    raise SystemExit(message)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: dict) -> None:
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def quantile_linear(values: Sequence[float], q: float) -> float:
    """Match the Phase-5 repository linear-interpolated quantile exactly."""
    if not values:
        raise ValueError("quantile requires at least one value")
    if not 0.0 <= q <= 1.0:
        raise ValueError("q must be within [0, 1]")
    ordered = sorted(float(v) for v in values)
    if len(ordered) == 1:
        return ordered[0]
    h = (len(ordered) - 1) * q
    lo = math.floor(h)
    hi = math.ceil(h)
    if lo == hi:
        return ordered[lo]
    fraction = h - lo
    return ordered[lo] + (ordered[hi] - ordered[lo]) * fraction


def eligible_delta(delta_seconds: float, cadence_p99_seconds: float) -> bool:
    return float(delta_seconds) > float(cadence_p99_seconds) * MULTIPLIER


def channel_number(channel_file: str) -> int:
    match = re.fullmatch(r"channel_(\d+)\.zip", channel_file)
    if not match:
        raise ValueError(f"unexpected channel file name: {channel_file}")
    return int(match.group(1))


def interval_id(
    mission: str,
    channel_file: str,
    channel_sha256: str,
    preceding_timestamp_ns: int,
    following_timestamp_ns: int,
) -> str:
    preimage = "|".join(
        [
            EXPERIMENT_ID,
            GAP_RULE_FREEZE_ID,
            mission,
            channel_file,
            channel_sha256,
            str(int(preceding_timestamp_ns)),
            str(int(following_timestamp_ns)),
        ]
    )
    return "S3X-INT-" + hashlib.sha256(preimage.encode("utf-8")).hexdigest()


def row_sort_key(row: dict) -> tuple:
    mission_rank = MISSIONS.index(row["mission"])
    return (
        mission_rank,
        channel_number(row["channel_file"]),
        int(row["preceding_timestamp_ns"]),
        int(row["following_timestamp_ns"]),
        row["interval_id"],
    )


def resolve_mission_dir(root: Path, mission: str) -> Path:
    for candidate in (root / mission, root):
        if (candidate / "channels").is_dir() and (candidate / "labels.csv").is_file():
            return candidate.resolve()
    fail(f"unable to resolve {mission} mission directory from {root}")


def verify_protocol(path: Path) -> dict:
    protocol = load_json(path)
    if protocol.get("protocol_id") != PROTOCOL_ID:
        fail("unexpected Phase-6 protocol id")
    if protocol.get("experiment_id") != EXPERIMENT_ID:
        fail("unexpected Phase-6 experiment id")
    auth = protocol.get("authorization_model", {})
    if auth.get("phase6a_design_authorized") is not True:
        fail("Phase-6A design is not authorized")
    if auth.get("timestamp_level_extraction_authorized") is not False:
        fail("design protocol must not itself authorize runtime extraction")
    if auth.get("runtime_requires_separate_versioned_authorization_record") is not True:
        fail("separate runtime authorization requirement missing")
    numeric = protocol.get("numeric_method", {})
    if numeric.get("comparison_operator") != ">":
        fail("protocol comparison operator drift")
    if numeric.get("threshold_runtime_override_allowed") is not False:
        fail("runtime threshold override unexpectedly enabled")
    if numeric.get("multiplier_runtime_override_allowed") is not False:
        fail("runtime multiplier override unexpectedly enabled")
    return protocol


def verify_authorization(path: Path, protocol_path: Path) -> dict:
    record = load_json(path)
    if record.get("schema") != 1:
        fail("unexpected runtime authorization schema")
    if record.get("authorization_id") != "S3X-PHASE6-TIMESTAMP-EXTRACTION-AUTH-001":
        fail("unexpected runtime authorization id")
    if record.get("experiment_id") != EXPERIMENT_ID:
        fail("runtime authorization experiment mismatch")
    if record.get("protocol_id") != PROTOCOL_ID:
        fail("runtime authorization protocol mismatch")
    if record.get("protocol_sha256") != sha256(protocol_path):
        fail("runtime authorization protocol hash mismatch")
    if record.get("timestamp_level_extraction_authorized") is not True:
        fail("timestamp-level extraction is not authorized")
    if record.get("trace_population_freeze_authorized") is not False:
        fail("runtime authorization must not freeze the trace population")
    if record.get("recovery_policy_execution_authorized") is not False:
        fail("runtime authorization must not authorize recovery execution")
    if record.get("scientific_execution_authorized") is not False:
        fail("runtime authorization must not authorize scientific execution")
    return record


def verify_gap_rule_freeze(path: Path) -> dict:
    freeze = load_json(path)
    if freeze.get("freeze_id") != GAP_RULE_FREEZE_ID:
        fail("gap-rule freeze id mismatch")
    if freeze.get("experiment_id") != EXPERIMENT_ID:
        fail("gap-rule experiment mismatch")
    rule = freeze.get("rule", {})
    if rule.get("name") != RULE_NAME or rule.get("status") != "SELECTED_AND_FROZEN":
        fail("P99_X10 is not selected and frozen")
    if rule.get("comparison_operator") != ">":
        fail("gap-rule comparison is not strict greater-than")
    if float(rule.get("multiplier")) != MULTIPLIER:
        fail("gap-rule multiplier drift")
    if rule.get("reference_statistic") != "channel-specific cadence_p99_seconds":
        fail("gap-rule reference statistic drift")
    lock = freeze.get("lock_policy", {})
    if lock.get("retune_after_timestamp_trace_inspection") is not False:
        fail("post-inspection retuning unexpectedly enabled")
    return freeze


def verify_source_freeze(
    path: Path,
    mission_archives: dict[str, Path],
) -> dict:
    if sha256(path) != SOURCE_FREEZE_SHA256:
        fail("source-freeze SHA-256 mismatch")
    freeze = load_json(path)
    if freeze.get("freeze_id") != SOURCE_FREEZE_ID:
        fail("source-freeze id mismatch")
    if freeze.get("experiment_id") != EXPERIMENT_ID:
        fail("source-freeze experiment mismatch")
    if freeze.get("source_identity_frozen") is not True:
        fail("source identity is not frozen")
    if tuple(freeze.get("missions", [])) != MISSIONS:
        fail("source-freeze mission order mismatch")

    archive_records = {
        row.get("mission"): row for row in freeze.get("archives", [])
    }
    for mission in MISSIONS:
        archive = mission_archives[mission]
        if not archive.is_file():
            fail(f"missing frozen source archive: {archive}")
        actual = sha256(archive)
        if actual != EXPECTED_ARCHIVE_SHA256[mission]:
            fail(f"{mission}: outer archive SHA-256 mismatch")
        record = archive_records.get(mission, {})
        if record.get("local_sha256") != actual:
            fail(f"{mission}: source-freeze archive binding mismatch")

    schema = freeze.get("schema_reports", {})
    for mission in MISSIONS:
        if schema.get(mission, {}).get("report_sha256") != EXPECTED_SCHEMA_SHA256[mission]:
            fail(f"{mission}: source-freeze schema report binding mismatch")
    return freeze


def load_schema_report(source_freeze_path: Path, freeze: dict, mission: str) -> dict:
    record = freeze["schema_reports"][mission]
    path = source_freeze_path.parent / record["report_file"]
    if not path.is_file():
        fail(f"missing schema report: {path}")
    if sha256(path) != EXPECTED_SCHEMA_SHA256[mission]:
        fail(f"{mission}: schema report SHA-256 mismatch")
    report = load_json(path)
    if report.get("experiment_id") != EXPERIMENT_ID:
        fail(f"{mission}: schema report experiment mismatch")
    if report.get("mission_directory_name") != mission:
        fail(f"{mission}: schema report mission mismatch")
    if report.get("channel_archive_count_inspected") != EXPECTED_CHANNEL_COUNTS[mission]:
        fail(f"{mission}: schema report channel count mismatch")
    channels = report.get("channels", [])
    if len(channels) != EXPECTED_CHANNEL_COUNTS[mission]:
        fail(f"{mission}: schema channel detail count mismatch")
    return report


def format_timestamp(pd, value_ns: int) -> str:
    return pd.Timestamp(int(value_ns), unit="ns").isoformat()


def extract_channel(
    mission: str,
    channel_record: dict,
    mission_dir: Path,
) -> tuple[list[dict], float]:
    try:
        import pandas as pd
    except Exception as exc:
        fail(f"pandas is required for authorized local extraction: {exc}")

    channel_path = mission_dir / "channels" / channel_record["file"]
    if not channel_path.is_file():
        fail(f"missing channel archive: {channel_path}")
    actual_sha = sha256(channel_path)
    if actual_sha != channel_record.get("sha256"):
        fail(f"{mission}/{channel_record['file']}: channel SHA-256 mismatch")

    df = pd.read_pickle(channel_path)
    if int(channel_record.get("rows")) != len(df):
        fail(f"{mission}/{channel_record['file']}: row-count mismatch")

    index = pd.to_datetime(df.index)
    ns = [int(v) for v in index.asi8]
    if len(ns) < 2:
        fail(f"{mission}/{channel_record['file']}: fewer than two timestamps")

    deltas_ns = [ns[i] - ns[i - 1] for i in range(1, len(ns))]
    duplicates = sum(v == 0 for v in deltas_ns)
    nonmonotonic = sum(v < 0 for v in deltas_ns)
    if duplicates or nonmonotonic:
        fail(
            f"{mission}/{channel_record['file']}: timestamp ordering drift "
            f"duplicates={duplicates} nonmonotonic={nonmonotonic}"
        )

    positive_seconds = [v / 1_000_000_000.0 for v in deltas_ns if v > 0]
    if not positive_seconds:
        fail(f"{mission}/{channel_record['file']}: no positive deltas")

    p99 = quantile_linear(positive_seconds, 0.99)
    threshold = p99 * MULTIPLIER
    rows = []
    for i, delta_ns in enumerate(deltas_ns, start=1):
        if delta_ns <= 0:
            continue
        delta_seconds = delta_ns / 1_000_000_000.0
        if not eligible_delta(delta_seconds, p99):
            continue
        previous_ns = ns[i - 1]
        following_ns = ns[i]
        row = {
            "schema_version": 1,
            "experiment_id": EXPERIMENT_ID,
            "source_freeze_id": SOURCE_FREEZE_ID,
            "source_freeze_sha256": SOURCE_FREEZE_SHA256,
            "gap_rule_freeze_id": GAP_RULE_FREEZE_ID,
            "gap_rule": RULE_NAME,
            "mission": mission,
            "channel_file": channel_record["file"],
            "channel_sha256": actual_sha,
            "preceding_timestamp_ns": previous_ns,
            "following_timestamp_ns": following_ns,
            "preceding_timestamp": format_timestamp(pd, previous_ns),
            "following_timestamp": format_timestamp(pd, following_ns),
            "delta_nanoseconds": delta_ns,
            "delta_seconds": delta_seconds,
            "cadence_p99_seconds": p99,
            "threshold_seconds": threshold,
            "comparison_operator": ">",
            "diagnostic_label": "EXTREME_TELEMETRY_INTER_SAMPLE_INTERVAL_DIAGNOSTIC",
            "interval_id": interval_id(
                mission,
                channel_record["file"],
                actual_sha,
                previous_ns,
                following_ns,
            ),
        }
        rows.append(row)
    return rows, p99


def channel_projection_sha256(channel_counts: list[dict]) -> str:
    lines = []
    for row in sorted(
        channel_counts,
        key=lambda item: (
            MISSIONS.index(item["mission"]),
            channel_number(item["channel_file"]),
        ),
    ):
        lines.append(
            "|".join(
                [
                    row["mission"],
                    row["channel_file"],
                    row["channel_sha256"],
                    format(float(row["cadence_p99_seconds"]), ".17g"),
                    format(float(row["threshold_seconds"]), ".17g"),
                    str(int(row["interval_count"])),
                ]
            )
        )
    payload = ("\n".join(lines) + "\n").encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=FIELDNAMES,
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mission1-archive", type=Path, required=True)
    parser.add_argument("--mission2-archive", type=Path, required=True)
    parser.add_argument("--mission1-dir", type=Path, required=True)
    parser.add_argument("--mission2-dir", type=Path, required=True)
    parser.add_argument("--source-freeze", type=Path, required=True)
    parser.add_argument("--gap-rule-freeze", type=Path, required=True)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--authorization-record", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    protocol_path = args.protocol.resolve()
    verify_protocol(protocol_path)
    verify_authorization(args.authorization_record.resolve(), protocol_path)
    verify_gap_rule_freeze(args.gap_rule_freeze.resolve())

    mission_archives = {
        "ESA-Mission1": args.mission1_archive.resolve(),
        "ESA-Mission2": args.mission2_archive.resolve(),
    }
    source_freeze_path = args.source_freeze.resolve()
    source_freeze = verify_source_freeze(source_freeze_path, mission_archives)

    mission_dirs = {
        "ESA-Mission1": resolve_mission_dir(args.mission1_dir.resolve(), "ESA-Mission1"),
        "ESA-Mission2": resolve_mission_dir(args.mission2_dir.resolve(), "ESA-Mission2"),
    }

    all_rows = []
    channel_counts = []
    for mission in MISSIONS:
        report = load_schema_report(source_freeze_path, source_freeze, mission)
        ordered_channels = sorted(
            report["channels"],
            key=lambda item: channel_number(item["file"]),
        )
        for channel_record in ordered_channels:
            rows, p99 = extract_channel(
                mission,
                channel_record,
                mission_dirs[mission],
            )
            all_rows.extend(rows)
            channel_counts.append(
                {
                    "mission": mission,
                    "channel_file": channel_record["file"],
                    "channel_sha256": channel_record["sha256"],
                    "cadence_p99_seconds": p99,
                    "threshold_seconds": p99 * MULTIPLIER,
                    "interval_count": len(rows),
                }
            )

    all_rows.sort(key=row_sort_key)
    ids = [row["interval_id"] for row in all_rows]
    if len(ids) != len(set(ids)):
        fail("duplicate interval ids detected")
    if len(all_rows) != EXPECTED_TOTAL_INTERVALS:
        fail(
            f"aggregate interval mismatch: expected {EXPECTED_TOTAL_INTERVALS}, "
            f"got {len(all_rows)}"
        )

    nonzero = sum(int(row["interval_count"]) > 0 for row in channel_counts)
    zero_set = {
        (row["mission"], row["channel_file"])
        for row in channel_counts
        if int(row["interval_count"]) == 0
    }
    if nonzero != EXPECTED_CHANNELS_WITH_INTERVALS:
        fail("channels-with-intervals invariant mismatch")
    if zero_set != EXPECTED_ZERO_CHANNELS:
        fail(f"zero-interval channel set mismatch: {sorted(zero_set)}")

    projection_sha = channel_projection_sha256(channel_counts)
    if projection_sha != EXPECTED_PROJECTION_SHA256:
        fail(
            "canonical channel projection mismatch; refusing output rather than "
            "retuning or accepting representation drift"
        )

    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)
    csv_path = out / OUTPUT_CSV
    summary_path = out / OUTPUT_SUMMARY
    manifest_path = out / OUTPUT_MANIFEST

    write_csv(csv_path, all_rows)
    summary = {
        "schema": 1,
        "experiment_id": EXPERIMENT_ID,
        "mode": "CANDIDATE_TIMESTAMP_INTERVAL_MATERIALIZATION",
        "gap_rule": RULE_NAME,
        "comparison": "positive inter-sample delta > threshold_seconds",
        "channels": len(channel_counts),
        "total_intervals": len(all_rows),
        "channels_with_intervals": nonzero,
        "channels_with_zero_intervals": len(zero_set),
        "zero_interval_channels": [
            {"mission": mission, "channel_file": channel}
            for mission, channel in sorted(zero_set)
        ],
        "canonical_channel_projection_sha256": projection_sha,
        "trace_population_frozen": False,
        "recovery_policy_execution_performed": False,
        "scientific_results_generated": False,
        "manuscript_claim_use": False,
        "interpretation": "extreme telemetry inter-sample interval diagnostic only",
    }
    write_json(summary_path, summary)

    manifest = {
        "schema": 1,
        "experiment_id": EXPERIMENT_ID,
        "protocol_id": PROTOCOL_ID,
        "protocol_sha256": sha256(protocol_path),
        "authorization_record_sha256": sha256(args.authorization_record.resolve()),
        "source_freeze_id": SOURCE_FREEZE_ID,
        "source_freeze_sha256": SOURCE_FREEZE_SHA256,
        "gap_rule_freeze_id": GAP_RULE_FREEZE_ID,
        "gap_rule_freeze_sha256": sha256(args.gap_rule_freeze.resolve()),
        "outputs": {
            "interval_csv": {"file": csv_path.name, "sha256": sha256(csv_path)},
            "summary_json": {"file": summary_path.name, "sha256": sha256(summary_path)},
        },
        "trace_population_frozen": False,
        "recovery_policy_execution_performed": False,
        "scientific_results_generated": False,
    }
    write_json(manifest_path, manifest)

    print("S3X_PHASE6_TIMESTAMP_INTERVAL_EXTRACTION=PASS")
    print(f"channels={len(channel_counts)}")
    print(f"total_intervals={len(all_rows)}")
    print(f"channels_with_intervals={nonzero}")
    print(f"channels_with_zero_intervals={len(zero_set)}")
    print(f"canonical_channel_projection_sha256={projection_sha}")
    print("trace_population_frozen=NO")
    print("recovery_policy_execution=NO")
    print("scientific_execution=NO")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
