#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
from dataclasses import asdict
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from study3x.src.recovery_replay_v2 import (  # noqa: E402
    EVIDENCE_STATES,
    POLICIES,
    TIMING_ARMS,
    EXPECTED_INTERVAL_ARTIFACT_SHA256,
    evaluate_case,
    fraction_text,
    parse_interval_row,
)

AUTHORIZATION_ID = "S3X-PHASE7-RUNTIME-AUTH-002"
EXPECTED_INTERVALS = 1919
EXPECTED_CASES = 34542
CASE_FILENAME = "S3X_PHASE7_CASE_RESULTS_001.csv"
COMPARISON_FILENAME = "S3X_PHASE7_MATCHED_COMPARISONS_001.csv"
SUMMARY_FILENAME = "S3X_PHASE7_SUMMARY_001.json"

CASE_FIELDS = [
    "experiment_id",
    "protocol_id",
    "trace_freeze_id",
    "interval_id",
    "mission",
    "channel_file",
    "policy",
    "evidence_state",
    "timing_arm",
    "delta_seconds",
    "cadence_p99_seconds",
    "normalized_hiatus_units",
    "cache_origin_unsafe_qualified_exposure_cadence_units",
    "protective_hiatus_duration_cadence_units",
    "first_refresh_time_cadence_units",
    "first_refresh_action",
    "first_refresh_gate_qualified",
    "first_refresh_unsafe_permissive",
    "first_refresh_unsafe_qualified",
    "first_refresh_unsafe_qualification_origin",
    "v5_first_refresh_qualification_delay_cadence_units",
]

COMPARISON_FIELDS = [
    "comparison_family",
    "interval_id",
    "mission",
    "channel_file",
    "policy_left",
    "policy_right",
    "evidence_state",
    "timing_arm_left",
    "timing_arm_right",
    "metric",
    "left_value",
    "right_value",
    "difference_cadence_units",
    "classification",
]


def fail(message: str) -> None:
    raise SystemExit(f"ERROR: {message}")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_fraction(text: str | None) -> Fraction | None:
    if text is None or text == "":
        return None
    token = str(text)
    if "/" in token:
        n, d = token.split("/", 1)
        return Fraction(int(n), int(d))
    return Fraction(int(token), 1)


def bool_text(value: bool) -> str:
    return "true" if value else "false"


def load_authorization(path: Path) -> dict:
    record = load_json(path)
    if record.get("authorization_id") != AUTHORIZATION_ID:
        fail("unexpected Phase-7 runtime authorization id")
    if record.get("experiment_id") != "S3X-ETA-001":
        fail("unexpected experiment id in runtime authorization")
    scope = record.get("authorization_scope", {})
    required_true = (
        "real_frozen_interval_artifact_read_authorized",
        "real_1919_interval_expansion_authorized",
        "recovery_policy_execution_authorized",
        "scientific_execution_authorized",
        "independent_reference_validation_authorized",
        "deterministic_repeat_execution_authorized",
    )
    for key in required_true:
        if scope.get(key) is not True:
            fail(f"runtime authorization scope is not open: {key}")
    required_false = (
        "result_freeze_authorized",
        "manuscript_claim_use_authorized",
        "p99_x10_retuning_authorized",
        "interval_membership_retuning_authorized",
        "study3_modification_authorized",
        "study3_s3x_pooling_authorized",
    )
    for key in required_false:
        if scope.get(key) is not False:
            fail(f"runtime authorization improperly opens: {key}")
    return record


def load_intervals(path: Path) -> list[dict[str, str]]:
    actual_hash = sha256(path)
    if actual_hash != EXPECTED_INTERVAL_ARTIFACT_SHA256:
        fail(
            "frozen interval CSV SHA-256 mismatch: "
            f"expected={EXPECTED_INTERVAL_ARTIFACT_SHA256} actual={actual_hash}"
        )
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != EXPECTED_INTERVALS:
        fail(f"expected {EXPECTED_INTERVALS} frozen intervals, found {len(rows)}")
    ids = [row.get("interval_id", "") for row in rows]
    if len(set(ids)) != EXPECTED_INTERVALS or any(not value for value in ids):
        fail("frozen interval ids must be non-empty and unique")
    for row in rows:
        parse_interval_row(row)
    return rows


def build_cases(interval_rows: list[dict[str, str]]) -> list[dict[str, object]]:
    cases: list[dict[str, object]] = []
    for row in interval_rows:
        for policy in POLICIES:
            for evidence_state in EVIDENCE_STATES:
                for timing_arm in TIMING_ARMS:
                    cases.append(
                        asdict(
                            evaluate_case(
                                row,
                                policy=policy,
                                evidence_state=evidence_state,
                                timing_arm=timing_arm,
                            )
                        )
                    )
    if len(cases) != EXPECTED_CASES:
        fail(f"expected {EXPECTED_CASES} cases, generated {len(cases)}")
    return cases


def case_index(cases: list[dict[str, object]]) -> dict[tuple[str, str, str, str], dict[str, object]]:
    index = {
        (
            str(row["interval_id"]),
            str(row["policy"]),
            str(row["evidence_state"]),
            str(row["timing_arm"]),
        ): row
        for row in cases
    }
    if len(index) != EXPECTED_CASES:
        fail("case key uniqueness drift")
    return index


def difference(left: str | None, right: str | None) -> str:
    l = parse_fraction(left)
    r = parse_fraction(right)
    if l is None or r is None:
        return ""
    return fraction_text(l - r)


def build_comparisons(
    interval_rows: list[dict[str, str]],
    cases: list[dict[str, object]],
) -> list[dict[str, str]]:
    idx = case_index(cases)
    output: list[dict[str, str]] = []

    for interval in interval_rows:
        iid = interval["interval_id"]
        mission = interval["mission"]
        channel = interval["channel_file"]

        # Prespecified gap-vs-continuous V5 comparison.
        for policy in POLICIES:
            gap = idx[(iid, policy, "V5", "EMPIRICAL_HIATUS_PROXY")]
            control = idx[(iid, policy, "V5", "MATCHED_CONTINUOUS_REFRESH_CONTROL")]
            lg = bool(gap["first_refresh_gate_qualified"])
            rg = bool(control["first_refresh_gate_qualified"])
            output.append({
                "comparison_family": "GAP_VS_CONTINUOUS_V5",
                "interval_id": iid,
                "mission": mission,
                "channel_file": channel,
                "policy_left": policy,
                "policy_right": policy,
                "evidence_state": "V5",
                "timing_arm_left": "EMPIRICAL_HIATUS_PROXY",
                "timing_arm_right": "MATCHED_CONTINUOUS_REFRESH_CONTROL",
                "metric": "FIRST_REFRESH_GATE_QUALIFICATION",
                "left_value": bool_text(lg),
                "right_value": bool_text(rg),
                "difference_cadence_units": "",
                "classification": (
                    "AGREE_TRUE" if lg and rg
                    else "AGREE_FALSE" if not lg and not rg
                    else "DISAGREE"
                ),
            })
            output.append({
                "comparison_family": "GAP_VS_CONTINUOUS_V5",
                "interval_id": iid,
                "mission": mission,
                "channel_file": channel,
                "policy_left": policy,
                "policy_right": policy,
                "evidence_state": "V5",
                "timing_arm_left": "EMPIRICAL_HIATUS_PROXY",
                "timing_arm_right": "MATCHED_CONTINUOUS_REFRESH_CONTROL",
                "metric": "V5_FIRST_REFRESH_QUALIFICATION_DELAY",
                "left_value": str(gap["v5_first_refresh_qualification_delay_cadence_units"] or ""),
                "right_value": str(control["v5_first_refresh_qualification_delay_cadence_units"] or ""),
                "difference_cadence_units": difference(
                    gap["v5_first_refresh_qualification_delay_cadence_units"],
                    control["v5_first_refresh_qualification_delay_cadence_units"],
                ),
                "classification": (
                    "BOTH_QUALIFY"
                    if gap["v5_first_refresh_qualification_delay_cadence_units"] is not None
                    and control["v5_first_refresh_qualification_delay_cadence_units"] is not None
                    else "NOT_BOTH_QUALIFY"
                ),
            })
            output.append({
                "comparison_family": "GAP_VS_CONTINUOUS_V5",
                "interval_id": iid,
                "mission": mission,
                "channel_file": channel,
                "policy_left": policy,
                "policy_right": policy,
                "evidence_state": "V5",
                "timing_arm_left": "EMPIRICAL_HIATUS_PROXY",
                "timing_arm_right": "MATCHED_CONTINUOUS_REFRESH_CONTROL",
                "metric": "CACHE_ORIGIN_UNSAFE_QUALIFIED_EXPOSURE",
                "left_value": str(gap["cache_origin_unsafe_qualified_exposure_cadence_units"]),
                "right_value": str(control["cache_origin_unsafe_qualified_exposure_cadence_units"]),
                "difference_cadence_units": difference(
                    str(gap["cache_origin_unsafe_qualified_exposure_cadence_units"]),
                    str(control["cache_origin_unsafe_qualified_exposure_cadence_units"]),
                ),
                "classification": "DETERMINISTIC_MATCHED_DIFFERENCE",
            })

        # Prespecified B0-vs-S1 empirical-hiatus cache-boundary comparison.
        for evidence_state in EVIDENCE_STATES:
            b0 = idx[(iid, "S2_B0_FAIL_CLOSED", evidence_state, "EMPIRICAL_HIATUS_PROXY")]
            s1 = idx[(iid, "S2_S1_EVIDENCE_AWARE", evidence_state, "EMPIRICAL_HIATUS_PROXY")]
            output.append({
                "comparison_family": "B0_VS_S1_GAP_CACHE_BOUNDARY",
                "interval_id": iid,
                "mission": mission,
                "channel_file": channel,
                "policy_left": "S2_B0_FAIL_CLOSED",
                "policy_right": "S2_S1_EVIDENCE_AWARE",
                "evidence_state": evidence_state,
                "timing_arm_left": "EMPIRICAL_HIATUS_PROXY",
                "timing_arm_right": "EMPIRICAL_HIATUS_PROXY",
                "metric": "CACHE_ORIGIN_UNSAFE_QUALIFIED_EXPOSURE",
                "left_value": str(b0["cache_origin_unsafe_qualified_exposure_cadence_units"]),
                "right_value": str(s1["cache_origin_unsafe_qualified_exposure_cadence_units"]),
                "difference_cadence_units": difference(
                    str(b0["cache_origin_unsafe_qualified_exposure_cadence_units"]),
                    str(s1["cache_origin_unsafe_qualified_exposure_cadence_units"]),
                ),
                "classification": "DETERMINISTIC_MATCHED_DIFFERENCE",
            })

        # Prespecified B0/S1-vs-B2 V5 first-refresh classification.
        for arm in TIMING_ARMS:
            b2 = idx[(iid, "S2_B2_RISK_THRESHOLD", "V5", arm)]
            for policy in ("S2_B0_FAIL_CLOSED", "S2_S1_EVIDENCE_AWARE"):
                other = idx[(iid, policy, "V5", arm)]
                output.append({
                    "comparison_family": "B0_S1_VS_B2_V5_RESUMPTION",
                    "interval_id": iid,
                    "mission": mission,
                    "channel_file": channel,
                    "policy_left": policy,
                    "policy_right": "S2_B2_RISK_THRESHOLD",
                    "evidence_state": "V5",
                    "timing_arm_left": arm,
                    "timing_arm_right": arm,
                    "metric": "FIRST_REFRESH_UNSAFE_QUALIFIED",
                    "left_value": bool_text(bool(other["first_refresh_unsafe_qualified"])),
                    "right_value": bool_text(bool(b2["first_refresh_unsafe_qualified"])),
                    "difference_cadence_units": "",
                    "classification": (
                        "AGREE"
                        if bool(other["first_refresh_unsafe_qualified"])
                        == bool(b2["first_refresh_unsafe_qualified"])
                        else "DISAGREE"
                    ),
                })

    expected = EXPECTED_INTERVALS * (3 * 3 + 3 + 2 * 2)
    if len(output) != expected:
        fail(f"matched comparison row-count drift: expected={expected} actual={len(output)}")
    return output


def build_summary(cases: list[dict[str, object]], comparison_count: int) -> dict[str, object]:
    action_counts: dict[str, int] = {}
    unsafe_qualified = 0
    unsafe_permissive = 0
    gate_qualified = 0
    by_policy: dict[str, dict[str, int]] = {
        policy: {
            "cases": 0,
            "first_refresh_gate_qualified": 0,
            "first_refresh_unsafe_qualified": 0,
            "first_refresh_unsafe_permissive": 0,
        }
        for policy in POLICIES
    }
    by_evidence: dict[str, dict[str, int]] = {
        evidence: {
            "cases": 0,
            "first_refresh_gate_qualified": 0,
            "first_refresh_unsafe_qualified": 0,
        }
        for evidence in EVIDENCE_STATES
    }
    by_arm: dict[str, dict[str, int]] = {
        arm: {
            "cases": 0,
            "first_refresh_gate_qualified": 0,
            "first_refresh_unsafe_qualified": 0,
        }
        for arm in TIMING_ARMS
    }

    for row in cases:
        action = str(row["first_refresh_action"])
        action_counts[action] = action_counts.get(action, 0) + 1
        gq = bool(row["first_refresh_gate_qualified"])
        uq = bool(row["first_refresh_unsafe_qualified"])
        up = bool(row["first_refresh_unsafe_permissive"])
        gate_qualified += int(gq)
        unsafe_qualified += int(uq)
        unsafe_permissive += int(up)

        policy = str(row["policy"])
        evidence = str(row["evidence_state"])
        arm = str(row["timing_arm"])
        by_policy[policy]["cases"] += 1
        by_policy[policy]["first_refresh_gate_qualified"] += int(gq)
        by_policy[policy]["first_refresh_unsafe_qualified"] += int(uq)
        by_policy[policy]["first_refresh_unsafe_permissive"] += int(up)
        by_evidence[evidence]["cases"] += 1
        by_evidence[evidence]["first_refresh_gate_qualified"] += int(gq)
        by_evidence[evidence]["first_refresh_unsafe_qualified"] += int(uq)
        by_arm[arm]["cases"] += 1
        by_arm[arm]["first_refresh_gate_qualified"] += int(gq)
        by_arm[arm]["first_refresh_unsafe_qualified"] += int(uq)

    return {
        "schema": 1,
        "experiment_id": "S3X-ETA-001",
        "protocol_id": "S3X-PHASE7-RECOVERY-REPLAY-DESIGN-001",
        "trace_freeze_id": "S3X-P99X10-TRACE-POPULATION-FREEZE-001",
        "authorization_id": AUTHORIZATION_ID,
        "population": {
            "frozen_intervals": EXPECTED_INTERVALS,
            "cases": EXPECTED_CASES,
            "matched_comparison_rows": comparison_count,
        },
        "first_refresh": {
            "gate_qualified_cases": gate_qualified,
            "unsafe_qualified_cases": unsafe_qualified,
            "unsafe_permissive_cases": unsafe_permissive,
            "action_counts": dict(sorted(action_counts.items())),
        },
        "by_policy": by_policy,
        "by_evidence_state": by_evidence,
        "by_timing_arm": by_arm,
        "analysis_note": (
            "Complete finite deterministic modeled population; no sampling inference, "
            "confidence interval, p-value, bootstrap, permutation test, global policy "
            "score, or pooled Study-3 analysis is produced."
        ),
        "interpretation_firewall": [
            "ESA telemetry inter-sample intervals are timing inputs only.",
            "The refresh-opportunity proxy is not operational contact availability.",
            "V4 and V5 are modeled trust states, not ESA labels.",
            "Gap duration is not spacecraft recovery latency.",
            "This extension is not external empirical replication of Study 3.",
        ],
    }


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--authorization-record", required=True)
    parser.add_argument("--interval-csv", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    auth_path = Path(args.authorization_record).resolve()
    interval_path = Path(args.interval_csv).resolve()
    out = Path(args.output_dir).resolve()

    load_authorization(auth_path)
    rows = load_intervals(interval_path)

    if out.exists() and any(out.iterdir()):
        fail(f"output directory must be empty: {out}")
    out.mkdir(parents=True, exist_ok=True)

    cases = build_cases(rows)
    comparisons = build_comparisons(rows, cases)
    summary = build_summary(cases, len(comparisons))

    write_csv(out / CASE_FILENAME, CASE_FIELDS, cases)
    write_csv(out / COMPARISON_FILENAME, COMPARISON_FIELDS, comparisons)
    (out / SUMMARY_FILENAME).write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    print("S3X_PHASE7_PRIMARY_RUNTIME=PASS")
    print(f"frozen_intervals={len(rows)}")
    print(f"cases={len(cases)}")
    print(f"matched_comparison_rows={len(comparisons)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
