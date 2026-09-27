#!/usr/bin/env python3
"""Read-only cadence/gap-threshold sensitivity audit for S3X-ETA-001.

This utility analyzes positive inter-sample intervals from the already frozen
ESA Anomaly Dataset v2 Mission-1 and Mission-2 source bytes. It evaluates a
fixed set of candidate threshold formulas without selecting or freezing any
gap rule and without emitting timestamp-level gap traces.

It does not execute a recovery policy and does not generate S3X scientific
results.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from collections import Counter
from pathlib import Path
from typing import Iterable, Sequence

FREEZE_ID = "S3X-ESA-V2-SOURCE-FREEZE-001"
EXPERIMENT_ID = "S3X-ETA-001"
MISSIONS = ("ESA-Mission1", "ESA-Mission2")
EXPECTED_CHANNEL_COUNTS = {
    "ESA-Mission1": 76,
    "ESA-Mission2": 100,
}
RULES = (
    ("P99_X1", "p99_multiple", 1.0),
    ("P99_X2", "p99_multiple", 2.0),
    ("P99_X3", "p99_multiple", 3.0),
    ("P99_X5", "p99_multiple", 5.0),
    ("P99_X10", "p99_multiple", 10.0),
    ("MAX_P99_MEDIAN_X2", "max_p99_median_multiple", 2.0),
    ("MAX_P99_MEDIAN_X3", "max_p99_median_multiple", 3.0),
    ("MAX_P99_MEDIAN_X5", "max_p99_median_multiple", 5.0),
)

OUTPUT_SCHEMA_VERSION = 2
AUDIT_ID = "S3X-GAP-SENSITIVITY-002"
SENSITIVITY_OUTPUT = "S3X_GAP_SENSITIVITY_002.csv"
FREQUENCY_OUTPUT = "S3X_DELTA_FREQUENCIES_002.csv"
SUMMARY_OUTPUT = "S3X_GAP_SENSITIVITY_SUMMARY_002.json"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def quantile_linear(values: Sequence[float], q: float) -> float:
    """Return the linear-interpolated sample quantile (pandas/numpy default style)."""
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


def basic_stats(values: Sequence[float]) -> dict:
    if not values:
        return {
            "count": 0,
            "min_seconds": None,
            "median_seconds": None,
            "p95_seconds": None,
            "p99_seconds": None,
            "max_seconds": None,
            "sum_interval_seconds": 0.0,
        }
    ordered = sorted(float(v) for v in values)
    return {
        "count": len(ordered),
        "min_seconds": ordered[0],
        "median_seconds": quantile_linear(ordered, 0.5),
        "p95_seconds": quantile_linear(ordered, 0.95),
        "p99_seconds": quantile_linear(ordered, 0.99),
        "max_seconds": ordered[-1],
        "sum_interval_seconds": float(sum(ordered)),
    }


def candidate_thresholds(deltas: Sequence[float]) -> dict[str, float]:
    if not deltas:
        raise ValueError("candidate thresholds require positive deltas")
    median = quantile_linear(deltas, 0.5)
    p99 = quantile_linear(deltas, 0.99)
    result: dict[str, float] = {}
    for name, kind, multiplier in RULES:
        if kind == "p99_multiple":
            threshold = p99 * multiplier
        elif kind == "max_p99_median_multiple":
            threshold = max(p99, median * multiplier)
        else:
            raise RuntimeError(f"unknown rule kind: {kind}")
        result[name] = float(threshold)
    return result


def evaluate_rule(deltas: Sequence[float], threshold: float) -> dict:
    if threshold < 0:
        raise ValueError("threshold must be non-negative")
    positive = [float(v) for v in deltas if float(v) > 0.0]
    if len(positive) != len(deltas):
        raise ValueError("all supplied deltas must be strictly positive")
    exceed = [v for v in positive if v > threshold]
    stats = basic_stats(exceed)
    return {
        "threshold_seconds": float(threshold),
        "positive_delta_count": len(positive),
        "exceedance_count": len(exceed),
        "exceedance_fraction": (len(exceed) / len(positive)) if positive else 0.0,
        "exceedance_min_seconds": stats["min_seconds"],
        "exceedance_median_seconds": stats["median_seconds"],
        "exceedance_p95_seconds": stats["p95_seconds"],
        "exceedance_p99_seconds": stats["p99_seconds"],
        "exceedance_max_seconds": stats["max_seconds"],
        "sum_interval_seconds_represented_by_exceedances": stats[
            "sum_interval_seconds"
        ],
        "sum_excess_above_threshold_seconds": float(
            sum(v - threshold for v in exceed)
        ),
    }


def top_delta_frequencies(
    deltas: Sequence[float], top_n: int = 10
) -> list[tuple[float, int]]:
    if top_n < 1:
        raise ValueError("top_n must be at least one")
    counts = Counter(float(v) for v in deltas)
    return sorted(counts.items(), key=lambda item: (-item[1], item[0]))[:top_n]


def cadence_class(median: float, mode: float) -> str:
    return f"median={median:.12g}|mode={mode:.12g}"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_freeze(freeze_path: Path) -> dict:
    freeze = load_json(freeze_path)
    if freeze.get("freeze_id") != FREEZE_ID:
        raise SystemExit(f"{freeze_path}: unexpected freeze_id")
    if freeze.get("experiment_id") != EXPERIMENT_ID:
        raise SystemExit(f"{freeze_path}: unexpected experiment_id")
    if freeze.get("source_identity_frozen") is not True:
        raise SystemExit(f"{freeze_path}: source identity is not frozen")
    for key in (
        "gap_rule_frozen",
        "trace_population_frozen",
        "recovery_policy_execution_performed",
        "scientific_results_generated",
    ):
        if freeze.get(key) is not False:
            raise SystemExit(f"{freeze_path}: {key} must remain false")
    if tuple(freeze.get("missions", [])) != MISSIONS:
        raise SystemExit(f"{freeze_path}: mission set/order mismatch")
    return freeze


def load_and_bind_schema(
    freeze_dir: Path, freeze: dict, mission: str
) -> tuple[dict, Path]:
    record = freeze["schema_reports"][mission]
    path = freeze_dir / record["report_file"]
    if not path.is_file():
        raise SystemExit(f"missing schema report: {path}")
    actual_sha = sha256(path)
    if actual_sha != record["report_sha256"]:
        raise SystemExit(
            f"{mission}: schema report SHA-256 mismatch; "
            f"expected {record['report_sha256']} got {actual_sha}"
        )
    report = load_json(path)
    if report.get("experiment_id") != EXPERIMENT_ID:
        raise SystemExit(f"{mission}: schema report experiment_id mismatch")
    if report.get("mode") != "READ_ONLY_SOURCE_SCHEMA_INSPECTION":
        raise SystemExit(f"{mission}: schema report mode mismatch")
    if report.get("scientific_recovery_execution") is not False:
        raise SystemExit(f"{mission}: schema report scientific flag must be false")
    if report.get("mission_directory_name") != mission:
        raise SystemExit(f"{mission}: schema report mission name mismatch")
    expected = EXPECTED_CHANNEL_COUNTS[mission]
    if report.get("channel_archive_count_inspected") != expected:
        raise SystemExit(f"{mission}: expected {expected} inspected channels")
    if len(report.get("channels", [])) != expected:
        raise SystemExit(f"{mission}: channel detail count mismatch")
    return report, path


def extract_positive_deltas(channel_path: Path) -> list[float]:
    # pandas remains a runtime-only dependency already used by the source inspector.
    try:
        import pandas as pd
    except Exception as exc:  # pragma: no cover - exercised on user runtime
        raise SystemExit(
            "pandas is required for local ESA channel inspection; "
            f"original import error: {exc}"
        ) from exc

    df = pd.read_pickle(channel_path)
    index = pd.to_datetime(df.index)
    if len(index) < 2:
        return []

    ns = [int(v) for v in index.asi8]
    deltas_ns = [ns[i] - ns[i - 1] for i in range(1, len(ns))]
    duplicate_count = sum(1 for v in deltas_ns if v == 0)
    nonmonotonic_count = sum(1 for v in deltas_ns if v < 0)
    if duplicate_count or nonmonotonic_count:
        raise SystemExit(
            f"{channel_path}: unexpected timestamp ordering drift; "
            f"duplicates={duplicate_count} nonmonotonic={nonmonotonic_count}"
        )
    return [v / 1_000_000_000.0 for v in deltas_ns if v > 0]


def analyze_channel(
    mission: str,
    channel_record: dict,
    mission_dir: Path,
) -> tuple[list[dict], list[dict], dict]:
    channel_path = mission_dir / "channels" / channel_record["file"]
    if not channel_path.is_file():
        raise SystemExit(f"missing channel archive: {channel_path}")
    actual_sha = sha256(channel_path)
    if actual_sha != channel_record["sha256"]:
        raise SystemExit(
            f"{channel_path}: SHA-256 mismatch; "
            f"expected {channel_record['sha256']} got {actual_sha}"
        )

    deltas = extract_positive_deltas(channel_path)
    if not deltas:
        raise SystemExit(f"{channel_path}: no positive inter-sample deltas")

    base = basic_stats(deltas)
    frequencies = top_delta_frequencies(deltas, top_n=10)
    mode_seconds = frequencies[0][0]
    class_id = cadence_class(base["median_seconds"], mode_seconds)
    thresholds = candidate_thresholds(deltas)

    sensitivity_rows: list[dict] = []
    for rule_name, _, _ in RULES:
        evaluated = evaluate_rule(deltas, thresholds[rule_name])
        sensitivity_rows.append(
            {
                "mission": mission,
                "channel_file": channel_record["file"],
                "channel_sha256": actual_sha,
                "rows": channel_record["rows"],
                "positive_delta_count": len(deltas),
                "cadence_class": class_id,
                "cadence_min_seconds": base["min_seconds"],
                "cadence_median_seconds": base["median_seconds"],
                "cadence_mode_seconds": mode_seconds,
                "cadence_p95_seconds": base["p95_seconds"],
                "cadence_p99_seconds": base["p99_seconds"],
                "cadence_max_seconds": base["max_seconds"],
                "cadence_sum_interval_seconds": base["sum_interval_seconds"],
                "candidate_rule": rule_name,
                **evaluated,
            }
        )

    frequency_rows = [
        {
            "mission": mission,
            "channel_file": channel_record["file"],
            "cadence_class": class_id,
            "rank": rank,
            "delta_seconds": delta,
            "count": count,
            "fraction_of_positive_deltas": count / len(deltas),
        }
        for rank, (delta, count) in enumerate(frequencies, start=1)
    ]

    channel_summary = {
        "mission": mission,
        "channel_file": channel_record["file"],
        "positive_delta_count": len(deltas),
        "cadence_class": class_id,
        "cadence_min_seconds": base["min_seconds"],
        "cadence_median_seconds": base["median_seconds"],
        "cadence_mode_seconds": mode_seconds,
        "cadence_p95_seconds": base["p95_seconds"],
        "cadence_p99_seconds": base["p99_seconds"],
        "cadence_max_seconds": base["max_seconds"],
        "cadence_sum_interval_seconds": base["sum_interval_seconds"],
    }
    return sensitivity_rows, frequency_rows, channel_summary


def aggregate_rule(rows: Iterable[dict]) -> dict:
    selected = list(rows)
    if not selected:
        raise ValueError("aggregate_rule requires rows")
    total_positive = sum(int(r["positive_delta_count"]) for r in selected)
    total_exceed = sum(int(r["exceedance_count"]) for r in selected)
    fractions = [float(r["exceedance_fraction"]) for r in selected]
    return {
        "channels": len(selected),
        "channels_with_exceedances": sum(
            1 for r in selected if int(r["exceedance_count"]) > 0
        ),
        "channels_with_zero_exceedances": sum(
            1 for r in selected if int(r["exceedance_count"]) == 0
        ),
        "total_positive_delta_count": total_positive,
        "total_exceedance_count": total_exceed,
        "pooled_exceedance_fraction": (
            total_exceed / total_positive if total_positive else 0.0
        ),
        "max_channel_exceedance_fraction": max(fractions) if fractions else 0.0,
        "channels_over_1pct_exceedance_fraction": sum(f > 0.01 for f in fractions),
        "channels_over_5pct_exceedance_fraction": sum(f > 0.05 for f in fractions),
        "channels_over_10pct_exceedance_fraction": sum(f > 0.10 for f in fractions),
        "sum_interval_seconds_represented_by_exceedances": float(
            sum(
                float(r["sum_interval_seconds_represented_by_exceedances"])
                for r in selected
            )
        ),
        "sum_excess_above_threshold_seconds": float(
            sum(float(r["sum_excess_above_threshold_seconds"]) for r in selected)
        ),
    }


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise SystemExit(f"refusing to write empty CSV: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def resolve_mission_dir(root: Path, mission: str) -> Path:
    candidates = (root / mission, root)
    for candidate in candidates:
        if (candidate / "channels").is_dir() and (candidate / "labels.csv").is_file():
            return candidate.resolve()
    raise SystemExit(f"unable to resolve {mission} mission directory from {root}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mission1-dir", type=Path, required=True)
    parser.add_argument("--mission2-dir", type=Path, required=True)
    parser.add_argument("--source-freeze", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    freeze_path = args.source_freeze.resolve()
    freeze = validate_freeze(freeze_path)
    freeze_dir = freeze_path.parent

    mission_dirs = {
        "ESA-Mission1": resolve_mission_dir(args.mission1_dir.resolve(), "ESA-Mission1"),
        "ESA-Mission2": resolve_mission_dir(args.mission2_dir.resolve(), "ESA-Mission2"),
    }

    all_sensitivity: list[dict] = []
    all_frequencies: list[dict] = []
    channel_summaries: list[dict] = []
    bound_schema = {}

    for mission in MISSIONS:
        report, schema_path = load_and_bind_schema(freeze_dir, freeze, mission)
        bound_schema[mission] = {
            "file": schema_path.name,
            "sha256": sha256(schema_path),
        }
        for channel_record in report["channels"]:
            sensitivity, frequencies, summary = analyze_channel(
                mission,
                channel_record,
                mission_dirs[mission],
            )
            all_sensitivity.extend(sensitivity)
            all_frequencies.extend(frequencies)
            channel_summaries.append(summary)

    expected_rows = sum(EXPECTED_CHANNEL_COUNTS.values()) * len(RULES)
    if len(all_sensitivity) != expected_rows:
        raise SystemExit(
            f"sensitivity row count mismatch: expected {expected_rows}, "
            f"got {len(all_sensitivity)}"
        )
    if len(channel_summaries) != sum(EXPECTED_CHANNEL_COUNTS.values()):
        raise SystemExit("channel summary count mismatch")

    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)
    sensitivity_path = out / SENSITIVITY_OUTPUT
    frequency_path = out / FREQUENCY_OUTPUT
    summary_path = out / SUMMARY_OUTPUT

    write_csv(sensitivity_path, all_sensitivity)
    write_csv(frequency_path, all_frequencies)

    cadence_classes = Counter(r["cadence_class"] for r in channel_summaries)
    mission_cadence_classes = {
        mission: dict(
            sorted(
                Counter(
                    r["cadence_class"]
                    for r in channel_summaries
                    if r["mission"] == mission
                ).items()
            )
        )
        for mission in MISSIONS
    }

    rules_summary = {}
    for rule_name, _, _ in RULES:
        rule_rows = [r for r in all_sensitivity if r["candidate_rule"] == rule_name]
        rules_summary[rule_name] = {
            "all_missions": aggregate_rule(rule_rows),
            "by_mission": {
                mission: aggregate_rule(
                    r for r in rule_rows if r["mission"] == mission
                )
                for mission in MISSIONS
            },
        }

    summary = {
        "schema": OUTPUT_SCHEMA_VERSION,
        "audit_id": AUDIT_ID,
        "experiment_id": EXPERIMENT_ID,
        "mode": "READ_ONLY_CADENCE_GAP_SENSITIVITY",
        "source_freeze": {
            "freeze_id": FREEZE_ID,
            "file": freeze_path.name,
            "sha256": sha256(freeze_path),
            "bound_schema_reports": bound_schema,
        },
        "missions": list(MISSIONS),
        "channels_analyzed": len(channel_summaries),
        "candidate_rule_count": len(RULES),
        "candidate_rules": [
            {"name": name, "kind": kind, "multiplier": multiplier}
            for name, kind, multiplier in RULES
        ],
        "cadence_classes_all_missions": dict(sorted(cadence_classes.items())),
        "cadence_classes_by_mission": mission_cadence_classes,
        "rules_summary": rules_summary,
        "output_contract": {
            "schema_version": OUTPUT_SCHEMA_VERSION,
            "cadence_fields": [
                "cadence_min_seconds",
                "cadence_median_seconds",
                "cadence_mode_seconds",
                "cadence_p95_seconds",
                "cadence_p99_seconds",
                "cadence_max_seconds",
                "cadence_sum_interval_seconds",
            ],
            "exceedance_fields": [
                "exceedance_count",
                "exceedance_fraction",
                "exceedance_min_seconds",
                "exceedance_median_seconds",
                "exceedance_p95_seconds",
                "exceedance_p99_seconds",
                "exceedance_max_seconds",
                "sum_interval_seconds_represented_by_exceedances",
                "sum_excess_above_threshold_seconds",
            ],
            "legacy_metric_name_collision_present": False,
        },
        "output_files": {
            "sensitivity_csv": {
                "file": sensitivity_path.name,
                "sha256": sha256(sensitivity_path),
            },
            "delta_frequency_csv": {
                "file": frequency_path.name,
                "sha256": sha256(frequency_path),
            },
        },
        "gap_rule_selected": False,
        "gap_rule_frozen": False,
        "trace_population_frozen": False,
        "timestamp_level_gap_traces_emitted": False,
        "recovery_policy_execution_performed": False,
        "scientific_results_generated": False,
        "interpretation_controls": [
            "candidate thresholds are sensitivity diagnostics, not selected gap rules",
            "telemetry gap is not asserted to be RF contact loss",
            "telemetry anomaly is not asserted to be cyberattack truth",
            "gap duration is not asserted to be recovery latency",
            "no timestamp-level gap population is emitted by this audit",
        ],
        "next_gate": "AUTHOR_REVIEW_OF_GAP_SENSITIVITY_BEFORE_ANY_GAP_RULE_SELECTION",
    }
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    print("S3X_GAP_SENSITIVITY_AUDIT_R2=PASS")
    print(f"output_schema_version={OUTPUT_SCHEMA_VERSION}")
    print(f"channels_analyzed={len(channel_summaries)}")
    print(f"candidate_rules={len(RULES)}")
    print(f"sensitivity_rows={len(all_sensitivity)}")
    print(f"sensitivity_csv={sensitivity_path}")
    print(f"delta_frequency_csv={frequency_path}")
    print(f"summary_json={summary_path}")
    print(f"sensitivity_csv_sha256={sha256(sensitivity_path)}")
    print(f"delta_frequency_csv_sha256={sha256(frequency_path)}")
    print("gap_rule_selected=NO")
    print("gap_rule_frozen=NO")
    print("trace_extraction=NO")
    print("recovery_policy_execution=NO")
    print("scientific_execution=NO")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
