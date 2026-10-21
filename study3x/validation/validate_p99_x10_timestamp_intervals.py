#!/usr/bin/env python3
"""Independent validator for authorized S3X Phase-6 candidate intervals.

This module does not import the extractor. It independently re-reads the frozen
source, recomputes P99_X10 eligibility, and compares the complete candidate CSV
against independently derived interval identities and aggregate invariants.
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
MISSIONS = ("ESA-Mission1", "ESA-Mission2")
MULTIPLIER = 10.0
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
PROJECTION_COLUMNS = (
    "mission",
    "channel_file",
    "channel_sha256",
    "positive_delta_count",
    "cadence_p99_seconds",
    "threshold_seconds",
    "exceedance_count",
)


def stop(message: str) -> None:
    raise SystemExit(message)


def require(condition: bool, message: str) -> None:
    if not condition:
        stop(message)


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def independent_quantile_linear(values: Sequence[float], q: float) -> float:
    if not values:
        raise ValueError("empty quantile input")
    ordered = sorted(float(value) for value in values)
    position = (len(ordered) - 1) * q
    lower = int(math.floor(position))
    upper = int(math.ceil(position))
    if lower == upper:
        return ordered[lower]
    weight = position - lower
    return ordered[lower] + (ordered[upper] - ordered[lower]) * weight


def independent_interval_id(
    mission: str,
    channel_file: str,
    channel_sha256: str,
    preceding_timestamp_ns: int,
    following_timestamp_ns: int,
) -> str:
    fields = (
        EXPERIMENT_ID,
        GAP_RULE_FREEZE_ID,
        mission,
        channel_file,
        channel_sha256,
        str(int(preceding_timestamp_ns)),
        str(int(following_timestamp_ns)),
    )
    return "S3X-INT-" + hashlib.sha256("|".join(fields).encode("utf-8")).hexdigest()


def channel_number(name: str) -> int:
    match = re.fullmatch(r"channel_(\d+)\.zip", name)
    if not match:
        raise ValueError(f"unexpected channel file: {name}")
    return int(match.group(1))


def candidate_sort_key(row: dict) -> tuple:
    return (
        MISSIONS.index(row["mission"]),
        channel_number(row["channel_file"]),
        int(row["preceding_timestamp_ns"]),
        int(row["following_timestamp_ns"]),
        row["interval_id"],
    )


def verify_protocol(path: Path) -> None:
    protocol = read_json(path)
    require(protocol.get("protocol_id") == PROTOCOL_ID, "protocol id mismatch")
    require(protocol.get("experiment_id") == EXPERIMENT_ID, "protocol experiment mismatch")
    model = protocol.get("authorization_model", {})
    require(model.get("timestamp_level_extraction_authorized") is False, "design protocol opened extraction")
    require(model.get("runtime_requires_separate_versioned_authorization_record") is True, "runtime authorization separation missing")
    numeric = protocol.get("numeric_method", {})
    require(numeric.get("comparison_operator") == ">", "protocol strict comparison drift")
    require(numeric.get("threshold_runtime_override_allowed") is False, "threshold override unexpectedly allowed")
    require(numeric.get("multiplier_runtime_override_allowed") is False, "multiplier override unexpectedly allowed")


def verify_authorization(path: Path, protocol_path: Path) -> None:
    record = read_json(path)
    require(record.get("authorization_id") == "S3X-PHASE6-TIMESTAMP-EXTRACTION-AUTH-001", "authorization id mismatch")
    require(record.get("experiment_id") == EXPERIMENT_ID, "authorization experiment mismatch")
    require(record.get("protocol_id") == PROTOCOL_ID, "authorization protocol mismatch")
    require(record.get("protocol_sha256") == digest(protocol_path), "authorization protocol hash mismatch")
    require(record.get("design_merge_verified") is True, "authorization does not verify Phase-6 design merge")
    require(record.get("design_post_merge_ci_success") is True, "authorization does not verify successful design post-merge CI")
    require(record.get("author_execution_approval_recorded") is True, "authorization does not record author execution approval")
    require(record.get("timestamp_level_extraction_authorized") is True, "timestamp extraction not authorized")
    require(record.get("trace_population_freeze_authorized") is False, "trace freeze unexpectedly authorized")
    require(record.get("recovery_policy_execution_authorized") is False, "recovery execution unexpectedly authorized")
    require(record.get("scientific_execution_authorized") is False, "scientific execution unexpectedly authorized")


def verify_gap_rule(path: Path) -> None:
    freeze = read_json(path)
    require(freeze.get("freeze_id") == GAP_RULE_FREEZE_ID, "gap-rule freeze mismatch")
    require(freeze.get("experiment_id") == EXPERIMENT_ID, "gap-rule experiment mismatch")
    rule = freeze.get("rule", {})
    require(rule.get("name") == RULE_NAME, "gap rule changed")
    require(rule.get("status") == "SELECTED_AND_FROZEN", "gap rule not frozen")
    require(rule.get("comparison_operator") == ">", "gap-rule operator changed")
    require(float(rule.get("multiplier")) == MULTIPLIER, "gap-rule multiplier changed")
    lock = freeze.get("lock_policy", {})
    require(lock.get("retune_after_timestamp_trace_inspection") is False, "gap-rule retuning gate opened")


def verify_source_freeze(path: Path, archives: dict[str, Path]) -> dict:
    require(digest(path) == SOURCE_FREEZE_SHA256, "source-freeze SHA-256 mismatch")
    freeze = read_json(path)
    require(freeze.get("freeze_id") == SOURCE_FREEZE_ID, "source-freeze id mismatch")
    require(freeze.get("experiment_id") == EXPERIMENT_ID, "source-freeze experiment mismatch")
    require(freeze.get("source_identity_frozen") is True, "source identity not frozen")
    require(tuple(freeze.get("missions", [])) == MISSIONS, "source mission order mismatch")

    records = {row.get("mission"): row for row in freeze.get("archives", [])}
    for mission in MISSIONS:
        archive = archives[mission]
        require(archive.is_file(), f"missing source archive: {archive}")
        actual = digest(archive)
        require(actual == EXPECTED_ARCHIVE_SHA256[mission], f"{mission}: source archive hash mismatch")
        require(records.get(mission, {}).get("local_sha256") == actual, f"{mission}: archive freeze binding mismatch")
        require(
            freeze.get("schema_reports", {}).get(mission, {}).get("report_sha256")
            == EXPECTED_SCHEMA_SHA256[mission],
            f"{mission}: schema report freeze binding mismatch",
        )
    return freeze


def resolve_mission_dir(root: Path, mission: str) -> Path:
    for candidate in (root / mission, root):
        if (candidate / "channels").is_dir() and (candidate / "labels.csv").is_file():
            return candidate.resolve()
    stop(f"unable to resolve {mission} from {root}")


def load_schema(source_freeze_path: Path, freeze: dict, mission: str) -> dict:
    record = freeze["schema_reports"][mission]
    path = source_freeze_path.parent / record["report_file"]
    require(path.is_file(), f"missing schema report: {path}")
    require(digest(path) == EXPECTED_SCHEMA_SHA256[mission], f"{mission}: schema report hash mismatch")
    report = read_json(path)
    require(report.get("experiment_id") == EXPERIMENT_ID, f"{mission}: schema experiment mismatch")
    require(report.get("mission_directory_name") == mission, f"{mission}: schema mission mismatch")
    require(report.get("channel_archive_count_inspected") == EXPECTED_CHANNEL_COUNTS[mission], f"{mission}: schema channel count mismatch")
    require(len(report.get("channels", [])) == EXPECTED_CHANNEL_COUNTS[mission], f"{mission}: schema channel detail mismatch")
    return report


def independently_recompute_channel(
    mission: str,
    channel_record: dict,
    mission_dir: Path,
) -> tuple[list[dict], dict]:
    try:
        import pandas as pd
    except Exception as exc:
        stop(f"pandas is required for independent validation: {exc}")

    path = mission_dir / "channels" / channel_record["file"]
    require(path.is_file(), f"missing channel archive: {path}")
    channel_sha = digest(path)
    require(channel_sha == channel_record.get("sha256"), f"{mission}/{channel_record['file']}: channel hash mismatch")

    frame = pd.read_pickle(path)
    require(len(frame) == int(channel_record.get("rows")), f"{mission}/{channel_record['file']}: row count mismatch")
    idx = pd.to_datetime(frame.index)
    ns_values = [int(value) for value in idx.asi8]
    require(len(ns_values) >= 2, f"{mission}/{channel_record['file']}: insufficient timestamps")

    differences = [current - previous for previous, current in zip(ns_values, ns_values[1:])]
    require(not any(value == 0 for value in differences), f"{mission}/{channel_record['file']}: duplicate timestamp")
    require(not any(value < 0 for value in differences), f"{mission}/{channel_record['file']}: nonmonotonic timestamp")
    positive_seconds = [value / 1_000_000_000.0 for value in differences if value > 0]
    require(bool(positive_seconds), f"{mission}/{channel_record['file']}: no positive deltas")

    p99 = independent_quantile_linear(positive_seconds, 0.99)
    threshold = p99 * MULTIPLIER
    expected = []
    for index, difference_ns in enumerate(differences):
        if difference_ns <= 0:
            continue
        delta_seconds = difference_ns / 1_000_000_000.0
        if not delta_seconds > threshold:
            continue
        preceding = ns_values[index]
        following = ns_values[index + 1]
        expected.append(
            {
                "mission": mission,
                "channel_file": channel_record["file"],
                "channel_sha256": channel_sha,
                "preceding_timestamp_ns": preceding,
                "following_timestamp_ns": following,
                "preceding_timestamp": idx[index].isoformat(),
                "following_timestamp": idx[index + 1].isoformat(),
                "delta_nanoseconds": difference_ns,
                "delta_seconds": delta_seconds,
                "cadence_p99_seconds": p99,
                "threshold_seconds": threshold,
                "interval_id": independent_interval_id(
                    mission,
                    channel_record["file"],
                    channel_sha,
                    preceding,
                    following,
                ),
            }
        )

    projection = {
        "mission": mission,
        "channel_file": channel_record["file"],
        "channel_sha256": channel_sha,
        "positive_delta_count": len(positive_seconds),
        "cadence_p99_seconds": p99,
        "threshold_seconds": threshold,
        "exceedance_count": len(expected),
    }
    return expected, projection


def projection_sha256(rows: list[dict]) -> str:
    selected = sorted(rows, key=lambda row: (row["mission"], row["channel_file"]))
    lines = [",".join(PROJECTION_COLUMNS)]
    for row in selected:
        lines.append(
            ",".join(
                (
                    row["mission"],
                    row["channel_file"],
                    row["channel_sha256"],
                    str(int(row["positive_delta_count"])),
                    format(float(row["cadence_p99_seconds"]), ".17g"),
                    format(float(row["threshold_seconds"]), ".17g"),
                    str(int(row["exceedance_count"])),
                )
            )
        )
    return hashlib.sha256(("\n".join(lines) + "\n").encode("utf-8")).hexdigest()


def read_candidate_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def validate_candidate_rows(actual: list[dict[str, str]], expected: list[dict]) -> None:
    require(len(actual) == EXPECTED_TOTAL_INTERVALS, "candidate CSV row count mismatch")
    require(len(expected) == EXPECTED_TOTAL_INTERVALS, "independent interval count mismatch")
    require(actual == sorted(actual, key=candidate_sort_key), "candidate CSV ordering is not deterministic")

    actual_ids = [row["interval_id"] for row in actual]
    require(len(actual_ids) == len(set(actual_ids)), "duplicate candidate interval id")

    expected_by_id = {row["interval_id"]: row for row in expected}
    require(set(actual_ids) == set(expected_by_id), "candidate interval-id population mismatch")

    for row in actual:
        exp = expected_by_id[row["interval_id"]]
        require(row["schema_version"] == "1", "candidate schema version mismatch")
        require(row["experiment_id"] == EXPERIMENT_ID, "candidate experiment id mismatch")
        require(row["source_freeze_id"] == SOURCE_FREEZE_ID, "candidate source freeze mismatch")
        require(row["source_freeze_sha256"] == SOURCE_FREEZE_SHA256, "candidate source hash mismatch")
        require(row["gap_rule_freeze_id"] == GAP_RULE_FREEZE_ID, "candidate gap freeze mismatch")
        require(row["gap_rule"] == RULE_NAME, "candidate rule mismatch")
        require(row["comparison_operator"] == ">", "candidate comparison operator mismatch")
        require(row["diagnostic_label"] == "EXTREME_TELEMETRY_INTER_SAMPLE_INTERVAL_DIAGNOSTIC", "candidate diagnostic label mismatch")
        for key in (
            "mission",
            "channel_file",
            "channel_sha256",
            "preceding_timestamp",
            "following_timestamp",
            "interval_id",
        ):
            require(row[key] == str(exp[key]), f"candidate field mismatch: {key}")
        for key in ("preceding_timestamp_ns", "following_timestamp_ns", "delta_nanoseconds"):
            require(int(row[key]) == int(exp[key]), f"candidate integer field mismatch: {key}")
        require(int(row["following_timestamp_ns"]) > int(row["preceding_timestamp_ns"]), "candidate timestamp order invalid")
        require(
            int(row["delta_nanoseconds"])
            == int(row["following_timestamp_ns"]) - int(row["preceding_timestamp_ns"]),
            "candidate delta nanoseconds mismatch",
        )
        for key in ("delta_seconds", "cadence_p99_seconds", "threshold_seconds"):
            require(float(row[key]) == float(exp[key]), f"candidate numeric field mismatch: {key}")
        require(float(row["delta_seconds"]) > float(row["threshold_seconds"]), "non-strict candidate interval detected")
        recomputed_id = independent_interval_id(
            row["mission"],
            row["channel_file"],
            row["channel_sha256"],
            int(row["preceding_timestamp_ns"]),
            int(row["following_timestamp_ns"]),
        )
        require(recomputed_id == row["interval_id"], "candidate interval id recomputation mismatch")


def verify_output_documents(
    csv_path: Path,
    summary_path: Path,
    manifest_path: Path,
    protocol_path: Path,
    authorization_path: Path,
    gap_rule_path: Path,
    projection_sha: str,
) -> None:
    summary = read_json(summary_path)
    require(summary.get("experiment_id") == EXPERIMENT_ID, "summary experiment mismatch")
    require(summary.get("mode") == "CANDIDATE_TIMESTAMP_INTERVAL_MATERIALIZATION", "summary mode mismatch")
    require(summary.get("total_intervals") == EXPECTED_TOTAL_INTERVALS, "summary interval count mismatch")
    require(summary.get("channels_with_intervals") == EXPECTED_CHANNELS_WITH_INTERVALS, "summary nonzero channel count mismatch")
    require(summary.get("channels_with_zero_intervals") == len(EXPECTED_ZERO_CHANNELS), "summary zero channel count mismatch")
    require(summary.get("canonical_channel_projection_sha256") == projection_sha, "summary projection hash mismatch")
    require(summary.get("trace_population_frozen") is False, "summary unexpectedly freezes trace population")
    require(summary.get("recovery_policy_execution_performed") is False, "summary unexpectedly records recovery execution")
    require(summary.get("scientific_results_generated") is False, "summary unexpectedly records scientific results")
    require(summary.get("manuscript_claim_use") is False, "summary unexpectedly enables manuscript use")

    manifest = read_json(manifest_path)
    require(manifest.get("protocol_id") == PROTOCOL_ID, "manifest protocol mismatch")
    require(manifest.get("protocol_sha256") == digest(protocol_path), "manifest protocol hash mismatch")
    require(manifest.get("authorization_record_sha256") == digest(authorization_path), "manifest authorization hash mismatch")
    require(manifest.get("source_freeze_sha256") == SOURCE_FREEZE_SHA256, "manifest source hash mismatch")
    require(manifest.get("gap_rule_freeze_id") == GAP_RULE_FREEZE_ID, "manifest gap freeze mismatch")
    require(manifest.get("gap_rule_freeze_sha256") == digest(gap_rule_path), "manifest gap freeze hash mismatch")
    require(manifest.get("outputs", {}).get("interval_csv", {}).get("sha256") == digest(csv_path), "manifest interval CSV hash mismatch")
    require(manifest.get("outputs", {}).get("summary_json", {}).get("sha256") == digest(summary_path), "manifest summary hash mismatch")
    require(manifest.get("trace_population_frozen") is False, "manifest unexpectedly freezes trace population")
    require(manifest.get("recovery_policy_execution_performed") is False, "manifest unexpectedly records recovery execution")
    require(manifest.get("scientific_results_generated") is False, "manifest unexpectedly records scientific results")


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
    parser.add_argument("--interval-csv", type=Path, required=True)
    parser.add_argument("--summary-json", type=Path, required=True)
    parser.add_argument("--manifest-json", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    args = parser.parse_args()

    protocol_path = args.protocol.resolve()
    authorization_path = args.authorization_record.resolve()
    gap_rule_path = args.gap_rule_freeze.resolve()
    source_freeze_path = args.source_freeze.resolve()

    verify_protocol(protocol_path)
    verify_authorization(authorization_path, protocol_path)
    verify_gap_rule(gap_rule_path)

    archives = {
        "ESA-Mission1": args.mission1_archive.resolve(),
        "ESA-Mission2": args.mission2_archive.resolve(),
    }
    source_freeze = verify_source_freeze(source_freeze_path, archives)
    mission_dirs = {
        "ESA-Mission1": resolve_mission_dir(args.mission1_dir.resolve(), "ESA-Mission1"),
        "ESA-Mission2": resolve_mission_dir(args.mission2_dir.resolve(), "ESA-Mission2"),
    }

    expected = []
    projections = []
    per_channel_counts = []
    for mission in MISSIONS:
        report = load_schema(source_freeze_path, source_freeze, mission)
        for channel_record in sorted(report["channels"], key=lambda row: channel_number(row["file"])):
            rows, projection = independently_recompute_channel(
                mission,
                channel_record,
                mission_dirs[mission],
            )
            expected.extend(rows)
            projections.append(projection)
            per_channel_counts.append(
                (mission, channel_record["file"], len(rows))
            )

    projection_sha = projection_sha256(projections)
    require(projection_sha == EXPECTED_PROJECTION_SHA256, "independent canonical projection SHA-256 mismatch")

    zero_set = {
        (mission, channel)
        for mission, channel, count in per_channel_counts
        if count == 0
    }
    require(zero_set == EXPECTED_ZERO_CHANNELS, "independent zero-channel set mismatch")
    require(
        sum(count > 0 for _, _, count in per_channel_counts)
        == EXPECTED_CHANNELS_WITH_INTERVALS,
        "independent channels-with-intervals mismatch",
    )

    interval_csv = args.interval_csv.resolve()
    summary_json = args.summary_json.resolve()
    manifest_json = args.manifest_json.resolve()
    for path in (interval_csv, summary_json, manifest_json):
        require(path.is_file(), f"missing candidate output: {path}")

    actual = read_candidate_csv(interval_csv)
    validate_candidate_rows(actual, expected)
    verify_output_documents(
        interval_csv,
        summary_json,
        manifest_json,
        protocol_path,
        authorization_path,
        gap_rule_path,
        projection_sha,
    )

    validation = {
        "schema": 1,
        "audit_id": "S3X-PHASE6-TIMESTAMP-INTERVAL-VALIDATION-001",
        "experiment_id": EXPERIMENT_ID,
        "mode": "INDEPENDENT_SOURCE_RECOMPUTATION_VALIDATION",
        "status": "PASS",
        "channels": sum(EXPECTED_CHANNEL_COUNTS.values()),
        "total_intervals": len(actual),
        "channels_with_intervals": EXPECTED_CHANNELS_WITH_INTERVALS,
        "channels_with_zero_intervals": len(EXPECTED_ZERO_CHANNELS),
        "canonical_channel_projection_sha256": projection_sha,
        "candidate_csv_sha256": digest(interval_csv),
        "summary_json_sha256": digest(summary_json),
        "manifest_json_sha256": digest(manifest_json),
        "trace_population_frozen": False,
        "recovery_policy_execution_performed": False,
        "scientific_results_generated": False,
        "manuscript_claim_use": False,
    }
    args.output_json.resolve().write_text(
        json.dumps(validation, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    print("S3X_PHASE6_TIMESTAMP_INTERVAL_VALIDATION=PASS")
    print(f"channels={validation['channels']}")
    print(f"total_intervals={validation['total_intervals']}")
    print(f"canonical_channel_projection_sha256={projection_sha}")
    print("trace_population_frozen=NO")
    print("recovery_policy_execution=NO")
    print("scientific_execution=NO")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
