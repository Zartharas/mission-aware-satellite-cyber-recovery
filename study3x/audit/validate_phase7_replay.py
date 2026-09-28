#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from study3x.audit.reference_replay import (  # noqa: E402
    EVIDENCE_STATES,
    POLICIES,
    TIMING_ARMS,
    evaluate_reference,
)

AUTHORIZATION_ID = "S3X-PHASE7-RUNTIME-AUTH-001"
EXPECTED_INTERVAL_SHA256 = (
    "cfa4fa3d88cb525237cbfe347fabe8485021351f3b639bdb58f79c575d8a51bc"
)
EXPECTED_INTERVALS = 1919
EXPECTED_CASES = 34542
EXPECTED_COMPARISONS = EXPECTED_INTERVALS * (3 * 3 + 3 + 2 * 2)

CASE_FILENAME = "S3X_PHASE7_CASE_RESULTS_001.csv"
COMPARISON_FILENAME = "S3X_PHASE7_MATCHED_COMPARISONS_001.csv"
SUMMARY_FILENAME = "S3X_PHASE7_SUMMARY_001.json"
VALIDATION_FILENAME = "S3X_PHASE7_INDEPENDENT_VALIDATION_001.json"

PARITY_FIELDS = (
    "interval_id",
    "policy",
    "evidence_state",
    "timing_arm",
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
)


def fail(message: str) -> None:
    raise SystemExit(f"ERROR: {message}")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def parse_bool(value: str) -> bool:
    if value == "True":
        return True
    if value == "False":
        return False
    raise ValueError(f"unexpected CSV boolean representation: {value!r}")


def ratio(text: str | None) -> Fraction | None:
    if text is None or text == "":
        return None
    if "/" in text:
        n, d = text.split("/", 1)
        return Fraction(int(n), int(d))
    return Fraction(int(text), 1)


def fraction_text(value: Fraction) -> str:
    return (
        str(value.numerator)
        if value.denominator == 1
        else f"{value.numerator}/{value.denominator}"
    )


def bool_text(value: bool) -> str:
    return "true" if value else "false"


def verify_authorization(path: Path) -> dict:
    auth = read_json(path)
    if auth.get("authorization_id") != AUTHORIZATION_ID:
        fail("unexpected runtime authorization id")
    scope = auth.get("authorization_scope", {})
    for key in (
        "real_frozen_interval_artifact_read_authorized",
        "real_1919_interval_expansion_authorized",
        "recovery_policy_execution_authorized",
        "scientific_execution_authorized",
        "independent_reference_validation_authorized",
        "deterministic_repeat_execution_authorized",
    ):
        if scope.get(key) is not True:
            fail(f"authorization is not open for: {key}")
    for key in (
        "result_freeze_authorized",
        "manuscript_claim_use_authorized",
        "p99_x10_retuning_authorized",
        "interval_membership_retuning_authorized",
        "study3_modification_authorized",
        "study3_s3x_pooling_authorized",
    ):
        if scope.get(key) is not False:
            fail(f"authorization improperly opens: {key}")
    return auth


def reference_cases(intervals: list[dict[str, str]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for interval in intervals:
        for policy in POLICIES:
            for evidence_state in EVIDENCE_STATES:
                for timing_arm in TIMING_ARMS:
                    rows.append(
                        evaluate_reference(
                            interval,
                            policy=policy,
                            evidence_state=evidence_state,
                            timing_arm=timing_arm,
                        )
                    )
    if len(rows) != EXPECTED_CASES:
        fail(f"reference case-count drift: {len(rows)}")
    return rows


def key(row: dict[str, object]) -> tuple[str, str, str, str]:
    return (
        str(row["interval_id"]),
        str(row["policy"]),
        str(row["evidence_state"]),
        str(row["timing_arm"]),
    )


def compare_cases(
    actual_rows: list[dict[str, str]],
    expected_rows: list[dict[str, object]],
) -> int:
    if len(actual_rows) != EXPECTED_CASES:
        fail(f"case result row count drift: {len(actual_rows)}")
    actual = {key(row): row for row in actual_rows}
    expected = {key(row): row for row in expected_rows}
    if len(actual) != EXPECTED_CASES or len(expected) != EXPECTED_CASES:
        fail("case key uniqueness drift")
    if set(actual) != set(expected):
        fail("case key set does not match reference population")

    mismatches = 0
    for k in sorted(expected):
        a = actual[k]
        e = expected[k]
        for field in PARITY_FIELDS:
            av: object = a.get(field)
            ev: object = e.get(field)
            if field in (
                "first_refresh_gate_qualified",
                "first_refresh_unsafe_permissive",
                "first_refresh_unsafe_qualified",
            ):
                av = parse_bool(str(av))
            if field == "v5_first_refresh_qualification_delay_cadence_units":
                av = None if av in ("", None) else av
            if av != ev:
                mismatches += 1
                if mismatches <= 3:
                    print(
                        "MISMATCH",
                        k,
                        field,
                        f"actual={av!r}",
                        f"expected={ev!r}",
                        file=sys.stderr,
                    )
    return mismatches


def reference_comparisons(
    intervals: list[dict[str, str]],
    cases: list[dict[str, object]],
) -> list[dict[str, str]]:
    idx = {key(row): row for row in cases}
    output: list[dict[str, str]] = []

    def diff(left: str | None, right: str | None) -> str:
        l = ratio(left)
        r = ratio(right)
        if l is None or r is None:
            return ""
        return fraction_text(l - r)

    for interval in intervals:
        iid = interval["interval_id"]
        mission = interval["mission"]
        channel = interval["channel_file"]

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
            left_delay = gap["v5_first_refresh_qualification_delay_cadence_units"]
            right_delay = control["v5_first_refresh_qualification_delay_cadence_units"]
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
                "left_value": str(left_delay or ""),
                "right_value": str(right_delay or ""),
                "difference_cadence_units": diff(
                    None if left_delay is None else str(left_delay),
                    None if right_delay is None else str(right_delay),
                ),
                "classification": (
                    "BOTH_QUALIFY"
                    if left_delay is not None and right_delay is not None
                    else "NOT_BOTH_QUALIFY"
                ),
            })
            left_cache = str(gap["cache_origin_unsafe_qualified_exposure_cadence_units"])
            right_cache = str(control["cache_origin_unsafe_qualified_exposure_cadence_units"])
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
                "left_value": left_cache,
                "right_value": right_cache,
                "difference_cadence_units": diff(left_cache, right_cache),
                "classification": "DETERMINISTIC_MATCHED_DIFFERENCE",
            })

        for evidence_state in EVIDENCE_STATES:
            b0 = idx[(iid, "S2_B0_FAIL_CLOSED", evidence_state, "EMPIRICAL_HIATUS_PROXY")]
            s1 = idx[(iid, "S2_S1_EVIDENCE_AWARE", evidence_state, "EMPIRICAL_HIATUS_PROXY")]
            left = str(b0["cache_origin_unsafe_qualified_exposure_cadence_units"])
            right = str(s1["cache_origin_unsafe_qualified_exposure_cadence_units"])
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
                "left_value": left,
                "right_value": right,
                "difference_cadence_units": diff(left, right),
                "classification": "DETERMINISTIC_MATCHED_DIFFERENCE",
            })

        for arm in TIMING_ARMS:
            b2 = idx[(iid, "S2_B2_RISK_THRESHOLD", "V5", arm)]
            for policy in ("S2_B0_FAIL_CLOSED", "S2_S1_EVIDENCE_AWARE"):
                other = idx[(iid, policy, "V5", arm)]
                left = bool(other["first_refresh_unsafe_qualified"])
                right = bool(b2["first_refresh_unsafe_qualified"])
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
                    "left_value": bool_text(left),
                    "right_value": bool_text(right),
                    "difference_cadence_units": "",
                    "classification": "AGREE" if left == right else "DISAGREE",
                })

    if len(output) != EXPECTED_COMPARISONS:
        fail(f"reference comparison-count drift: {len(output)}")
    return output


def compare_comparisons(
    actual: list[dict[str, str]],
    expected: list[dict[str, str]],
) -> int:
    if len(actual) != EXPECTED_COMPARISONS:
        fail(f"matched comparison row-count drift: {len(actual)}")
    if len(expected) != EXPECTED_COMPARISONS:
        fail("reference comparison row-count drift")
    mismatches = 0
    for index, (a, e) in enumerate(zip(actual, expected), start=1):
        if a != e:
            mismatches += 1
            if mismatches <= 3:
                print(
                    f"COMPARISON_MISMATCH row={index} actual={a!r} expected={e!r}",
                    file=sys.stderr,
                )
    return mismatches


def validate_summary(summary: dict, cases: list[dict[str, object]], comparison_count: int) -> None:
    population = summary.get("population", {})
    if population.get("frozen_intervals") != EXPECTED_INTERVALS:
        fail("summary frozen interval count drift")
    if population.get("cases") != EXPECTED_CASES:
        fail("summary case count drift")
    if population.get("matched_comparison_rows") != comparison_count:
        fail("summary comparison row count drift")

    expected_gate = sum(bool(row["first_refresh_gate_qualified"]) for row in cases)
    expected_unsafe_q = sum(bool(row["first_refresh_unsafe_qualified"]) for row in cases)
    expected_unsafe_p = sum(bool(row["first_refresh_unsafe_permissive"]) for row in cases)
    first = summary.get("first_refresh", {})
    if first.get("gate_qualified_cases") != expected_gate:
        fail("summary gate-qualified count drift")
    if first.get("unsafe_qualified_cases") != expected_unsafe_q:
        fail("summary unsafe-qualified count drift")
    if first.get("unsafe_permissive_cases") != expected_unsafe_p:
        fail("summary unsafe-permissive count drift")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--authorization-record", required=True)
    parser.add_argument("--interval-csv", required=True)
    parser.add_argument("--case-results", required=True)
    parser.add_argument("--matched-comparisons", required=True)
    parser.add_argument("--summary-json", required=True)
    parser.add_argument("--output-json", required=True)
    args = parser.parse_args()

    auth_path = Path(args.authorization_record).resolve()
    interval_path = Path(args.interval_csv).resolve()
    case_path = Path(args.case_results).resolve()
    comparison_path = Path(args.matched_comparisons).resolve()
    summary_path = Path(args.summary_json).resolve()
    output_path = Path(args.output_json).resolve()

    verify_authorization(auth_path)

    actual_interval_sha = sha256(interval_path)
    if actual_interval_sha != EXPECTED_INTERVAL_SHA256:
        fail(
            "frozen interval SHA mismatch: "
            f"expected={EXPECTED_INTERVAL_SHA256} actual={actual_interval_sha}"
        )

    intervals = read_csv(interval_path)
    if len(intervals) != EXPECTED_INTERVALS:
        fail(f"expected {EXPECTED_INTERVALS} intervals, found {len(intervals)}")
    interval_ids = [row["interval_id"] for row in intervals]
    if len(set(interval_ids)) != EXPECTED_INTERVALS:
        fail("interval ids are not unique")

    expected_cases = reference_cases(intervals)
    actual_cases = read_csv(case_path)
    case_mismatches = compare_cases(actual_cases, expected_cases)
    if case_mismatches != 0:
        fail(f"independent case-level validation found {case_mismatches} mismatches")

    expected_comparisons = reference_comparisons(intervals, expected_cases)
    actual_comparisons = read_csv(comparison_path)
    comparison_mismatches = compare_comparisons(
        actual_comparisons,
        expected_comparisons,
    )
    if comparison_mismatches != 0:
        fail(
            "independent matched-comparison validation found "
            f"{comparison_mismatches} mismatches"
        )

    summary = read_json(summary_path)
    validate_summary(summary, expected_cases, len(expected_comparisons))

    validation = {
        "schema": 1,
        "experiment_id": "S3X-ETA-001",
        "protocol_id": "S3X-PHASE7-RECOVERY-REPLAY-DESIGN-001",
        "authorization_id": AUTHORIZATION_ID,
        "frozen_interval_csv_sha256": actual_interval_sha,
        "frozen_intervals": EXPECTED_INTERVALS,
        "reference_cases_recomputed": EXPECTED_CASES,
        "case_level_mismatches": 0,
        "matched_comparison_rows_recomputed": EXPECTED_COMPARISONS,
        "matched_comparison_mismatches": 0,
        "summary_validation": "PASS",
        "validation_characterization": (
            "SEPARATELY_IMPLEMENTED_REPOSITORY_REFERENCE_EVALUATOR__"
            "NOT_INDEPENDENT_HUMAN_OR_EXTERNAL_REPLICATION"
        ),
        "scientific_execution_validation": "PASS",
        "result_freeze_authorized": False,
        "manuscript_claim_use_authorized": False,
    }
    output_path.write_text(
        json.dumps(validation, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    print("S3X_PHASE7_INDEPENDENT_VALIDATION=PASS")
    print(f"frozen_intervals={EXPECTED_INTERVALS}")
    print(f"reference_cases_recomputed={EXPECTED_CASES}")
    print("case_level_mismatches=0")
    print(f"matched_comparison_rows={EXPECTED_COMPARISONS}")
    print("matched_comparison_mismatches=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
