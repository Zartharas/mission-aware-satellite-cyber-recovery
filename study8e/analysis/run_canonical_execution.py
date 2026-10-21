#!/usr/bin/env python3
"""Canonical real-trace execution for S8E-ECTV-001.

This program implements S8E-CANON-EXEC-001. It consumes only the already
frozen TRACE-002 JSONL artifact and repository governance files. It does not
query SatNOGS, mutate Study 8, or infer physical link throughput.

Scientific outputs are deterministic: no wall-clock timestamps, random values,
or machine-specific paths are written into them.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from decimal import Decimal, ROUND_HALF_EVEN, localcontext
from fractions import Fraction
from pathlib import Path
from typing import Callable, Iterable, Mapping, Sequence

from study8.src.contact_recovery_model import PROFILE_OBJECTS
from study8e.audit.independent_canonical_bound import (
    independent_strict_sufficient_upper_bound_bps,
)
from study8e.audit.independent_external_reference import independent_evaluate
from study8e.src.external_contact_recovery_model import (
    ExternalCase,
    evaluate_case,
    minimum_integer_rate_bps,
)


EXPERIMENT_ID = "S8E-ECTV-001"
PROTOCOL_ID = "S8E-CANON-EXEC-001"
TRACE_FREEZE_ID = "S8E-SATNOGS-TRACE-002"
POPULATION_FREEZE_ID = "S8E-SATNOGS-POP-002"
IMPLEMENTATION_FREEZE_ID = "S8E-IMPLFREEZE-001"

SOURCE_END_TEXT = "2026-07-01T00:00:00Z"
HORIZONS_HOURS = (6, 12, 24)
PROFILE_ORDER = (
    "PROFILE_512_44",
    "PROFILE_768_65",
    "PROFILE_1024_87",
)
POLICY_ORDER = (
    "P0_HARD_CUTOVER",
    "P1_STAGED_CUTOVER",
    "P2_HYBRID_OVERLAP",
    "P3_CONTACT_AWARE_STAGED",
)
DISRUPTION_ORDER = (
    "A0_NONE",
    "A1_DROP_FIRST_LARGEST_OBJECT_FRAGMENT",
    "A2_DELAY_FIRST_TRANSITION_PROOF_ONE_CONTACT",
    "A3_STALE_EPOCH_REPLAY_AT_COMMIT",
)

MICROS_PER_SECOND = 1_000_000
SECONDS_PER_HOUR = 3600
UTC = timezone.utc
EPOCH = datetime(1970, 1, 1, tzinfo=UTC)

ISO_UTC_RE = re.compile(
    r"^(?P<base>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})"
    r"(?:\.(?P<fraction>\d{1,6}))?"
    r"(?P<zone>Z|\+00:00)$"
)


class CanonicalExecutionError(RuntimeError):
    """Fail-closed canonical execution error."""


@dataclass(frozen=True)
class RawObservation:
    selection_order: int
    observation_id: int
    start_us: int
    end_us: int
    ground_station: int
    norad_cat_id: int


@dataclass(frozen=True)
class MergedWindow:
    selection_order: int
    norad_cat_id: int
    ground_station: int
    merged_index: int
    start_us: int
    end_us: int
    observation_ids: tuple[int, ...]


@dataclass(frozen=True)
class Anchor:
    selection_order: int
    norad_cat_id: int
    ground_station: int
    anchor_index: int
    anchor_id: str
    anchor_us: int
    merged_window_index: int


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_json_bytes(value: object) -> bytes:
    return (
        json.dumps(
            value,
            indent=2,
            sort_keys=True,
            ensure_ascii=False,
            separators=(",", ": "),
        )
        + "\n"
    ).encode("utf-8")


def parse_utc_microseconds(text: object) -> int:
    if not isinstance(text, str):
        raise CanonicalExecutionError("timestamp must be a string")
    match = ISO_UTC_RE.fullmatch(text)
    if not match:
        raise CanonicalExecutionError(
            f"timestamp is not canonical UTC ISO-8601 with <=6 fractional digits: {text!r}"
        )
    base = datetime.strptime(match.group("base"), "%Y-%m-%dT%H:%M:%S").replace(
        tzinfo=UTC
    )
    fraction = match.group("fraction") or ""
    micros = int(fraction.ljust(6, "0")) if fraction else 0
    value = base + timedelta(microseconds=micros)
    delta = value - EPOCH
    return (
        delta.days * 86400 * MICROS_PER_SECOND
        + delta.seconds * MICROS_PER_SECOND
        + delta.microseconds
    )


def format_utc_microseconds(value_us: int) -> str:
    value = EPOCH + timedelta(microseconds=value_us)
    if value.microsecond:
        return value.isoformat(timespec="microseconds").replace("+00:00", "Z")
    return value.isoformat(timespec="seconds").replace("+00:00", "Z")


def fraction_text(value: Fraction | None) -> str:
    if value is None:
        return ""
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def microseconds_seconds_text(value_us: int) -> str:
    sign = "-" if value_us < 0 else ""
    value_us = abs(value_us)
    whole, fraction = divmod(value_us, MICROS_PER_SECOND)
    if fraction == 0:
        return f"{sign}{whole}"
    frac_text = f"{fraction:06d}".rstrip("0")
    return f"{sign}{whole}.{frac_text}"


def median_fraction(values: Sequence[Fraction]) -> Fraction | None:
    if not values:
        return None
    ordered = sorted(values)
    n = len(ordered)
    middle = n // 2
    if n % 2:
        return ordered[middle]
    return (ordered[middle - 1] + ordered[middle]) / 2


def decimal_from_fraction(value: Fraction) -> Decimal:
    with localcontext() as ctx:
        ctx.prec = 80
        return Decimal(value.numerator) / Decimal(value.denominator)


def rounded_decimal_text(value: Decimal, places: int = 12) -> str:
    quantum = Decimal(1).scaleb(-places)
    return format(value.quantize(quantum, rounding=ROUND_HALF_EVEN), "f")


def population_sd_fraction_decimal(values: Sequence[Fraction]) -> Decimal | None:
    if len(values) < 2:
        return None
    mean = sum(values, Fraction(0, 1)) / len(values)
    variance = (
        sum(((value - mean) ** 2 for value in values), Fraction(0, 1))
        / len(values)
    )
    with localcontext() as ctx:
        ctx.prec = 80
        variance_decimal = decimal_from_fraction(variance)
        return variance_decimal.sqrt()


def ceil_fraction(value: Fraction) -> int:
    return -(-value.numerator // value.denominator)


def exact_proportion(numerator: int, denominator: int) -> dict[str, object]:
    if denominator <= 0:
        return {
            "numerator": numerator,
            "denominator": denominator,
            "fraction": None,
            "decimal_6": None,
        }
    frac = Fraction(numerator, denominator)
    with localcontext() as ctx:
        ctx.prec = 40
        dec = Decimal(frac.numerator) / Decimal(frac.denominator)
    return {
        "numerator": numerator,
        "denominator": denominator,
        "fraction": fraction_text(frac),
        "decimal_6": format(
            dec.quantize(Decimal("0.000001"), rounding=ROUND_HALF_EVEN),
            "f",
        ),
    }


def load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def load_frozen_contracts(
    *,
    protocol_path: Path,
    population_path: Path,
    trace_freeze_path: Path,
    implementation_freeze_path: Path,
) -> tuple[dict[str, object], dict[str, object], dict[str, object], dict[str, object]]:
    protocol = load_json(protocol_path)
    population = load_json(population_path)
    trace_freeze = load_json(trace_freeze_path)
    implementation = load_json(implementation_freeze_path)

    if not isinstance(protocol, dict) or protocol.get("protocol_id") != PROTOCOL_ID:
        raise CanonicalExecutionError("wrong canonical execution protocol")
    if (
        not isinstance(population, dict)
        or population.get("freeze_id") != POPULATION_FREEZE_ID
    ):
        raise CanonicalExecutionError("wrong POP-002 population freeze")
    if (
        not isinstance(trace_freeze, dict)
        or trace_freeze.get("freeze_id") != TRACE_FREEZE_ID
    ):
        raise CanonicalExecutionError("wrong TRACE-002 freeze")
    if (
        not isinstance(implementation, dict)
        or implementation.get("freeze_id") != IMPLEMENTATION_FREEZE_ID
    ):
        raise CanonicalExecutionError("wrong implementation freeze")

    return protocol, population, trace_freeze, implementation


def load_trace(
    trace_jsonl: Path,
    population: Mapping[str, object],
    trace_freeze: Mapping[str, object],
) -> dict[int, list[RawObservation]]:
    corpus = trace_freeze.get("corpus")
    if not isinstance(corpus, dict):
        raise CanonicalExecutionError("TRACE-002 corpus metadata missing")
    expected_records = corpus.get("records")
    expected_hash = (
        corpus.get("canonical_jsonl", {})
        if isinstance(corpus.get("canonical_jsonl"), dict)
        else {}
    ).get("sha256")
    if expected_records != 476:
        raise CanonicalExecutionError("TRACE-002 frozen record count is not 476")
    if sha256_file(trace_jsonl) != expected_hash:
        raise CanonicalExecutionError("TRACE-002 JSONL SHA-256 mismatch")

    selected_pairs = population.get("selected_pairs")
    if not isinstance(selected_pairs, list) or len(selected_pairs) != 20:
        raise CanonicalExecutionError("POP-002 must contain exactly 20 selected pairs")

    pair_contract: dict[int, tuple[int, int, int]] = {}
    for pair in selected_pairs:
        if not isinstance(pair, dict):
            raise CanonicalExecutionError("invalid POP-002 pair record")
        order = pair.get("selection_order")
        norad = pair.get("norad_cat_id")
        station = pair.get("ground_station")
        eligibility = pair.get("eligibility_evidence")
        if (
            not isinstance(order, int)
            or not isinstance(norad, int)
            or not isinstance(station, int)
            or not isinstance(eligibility, dict)
            or not isinstance(eligibility.get("first_page_records"), int)
        ):
            raise CanonicalExecutionError("malformed POP-002 pair contract")
        pair_contract[order] = (
            norad,
            station,
            int(eligibility["first_page_records"]),
        )

    grouped: dict[int, list[RawObservation]] = defaultdict(list)
    global_ids: set[int] = set()
    line_count = 0

    with trace_jsonl.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                raise CanonicalExecutionError(
                    f"blank line in TRACE-002 at line {line_number}"
                )
            row = json.loads(line)
            if not isinstance(row, dict):
                raise CanonicalExecutionError("TRACE-002 row is not an object")
            required = (
                "selection_order",
                "id",
                "start",
                "end",
                "ground_station",
                "norad_cat_id",
            )
            if any(key not in row for key in required):
                raise CanonicalExecutionError("TRACE-002 row missing required field")

            order = row["selection_order"]
            observation_id = row["id"]
            station = row["ground_station"]
            norad = row["norad_cat_id"]
            if not all(
                isinstance(value, int)
                for value in (order, observation_id, station, norad)
            ):
                raise CanonicalExecutionError("TRACE-002 identifier type mismatch")
            if order not in pair_contract:
                raise CanonicalExecutionError("TRACE-002 contains unknown selection_order")
            expected_norad, expected_station, _ = pair_contract[order]
            if norad != expected_norad or station != expected_station:
                raise CanonicalExecutionError("TRACE-002 pair identity mismatch")
            if observation_id in global_ids:
                raise CanonicalExecutionError("duplicate TRACE-002 observation id")
            global_ids.add(observation_id)

            start_us = parse_utc_microseconds(row["start"])
            end_us = parse_utc_microseconds(row["end"])
            if end_us <= start_us:
                raise CanonicalExecutionError("TRACE-002 end <= start")

            grouped[order].append(
                RawObservation(
                    selection_order=order,
                    observation_id=observation_id,
                    start_us=start_us,
                    end_us=end_us,
                    ground_station=station,
                    norad_cat_id=norad,
                )
            )
            line_count += 1

    if line_count != expected_records:
        raise CanonicalExecutionError(
            f"TRACE-002 records {line_count} != frozen {expected_records}"
        )

    if set(grouped) != set(pair_contract):
        raise CanonicalExecutionError("TRACE-002 does not preserve all POP-002 traces")

    for order, rows in grouped.items():
        _, _, expected_count = pair_contract[order]
        if len(rows) != expected_count:
            raise CanonicalExecutionError(
                f"trace {order} count {len(rows)} != frozen {expected_count}"
            )

    return dict(grouped)


def merge_trace_windows(rows: Sequence[RawObservation]) -> list[MergedWindow]:
    if not rows:
        return []
    ordered = sorted(
        rows,
        key=lambda row: (row.start_us, row.end_us, row.observation_id),
    )
    selection_order = ordered[0].selection_order
    norad = ordered[0].norad_cat_id
    station = ordered[0].ground_station

    merged_raw: list[tuple[int, int, list[int]]] = []
    for row in ordered:
        if (
            row.selection_order != selection_order
            or row.norad_cat_id != norad
            or row.ground_station != station
        ):
            raise CanonicalExecutionError("cross-trace row in merge input")

        if not merged_raw or row.start_us > merged_raw[-1][1]:
            merged_raw.append(
                (row.start_us, row.end_us, [row.observation_id])
            )
        else:
            old_start, old_end, ids = merged_raw[-1]
            merged_raw[-1] = (
                old_start,
                max(old_end, row.end_us),
                ids + [row.observation_id],
            )

    return [
        MergedWindow(
            selection_order=selection_order,
            norad_cat_id=norad,
            ground_station=station,
            merged_index=index,
            start_us=start_us,
            end_us=end_us,
            observation_ids=tuple(sorted(ids)),
        )
        for index, (start_us, end_us, ids) in enumerate(merged_raw, start=1)
    ]


def timing_outputs(
    merged_by_trace: Mapping[int, Sequence[MergedWindow]],
    raw_counts: Mapping[int, int],
) -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]]]:
    window_rows: list[dict[str, object]] = []
    gap_rows: list[dict[str, object]] = []
    summary_rows: list[dict[str, object]] = []

    for order in sorted(merged_by_trace):
        windows = list(merged_by_trace[order])
        if not windows:
            raise CanonicalExecutionError(f"trace {order} has no merged windows")

        duration_fracs = [
            Fraction(window.end_us - window.start_us, MICROS_PER_SECOND)
            for window in windows
        ]
        gap_fracs: list[Fraction] = []

        for window in windows:
            window_rows.append(
                {
                    "trace_selection_order": order,
                    "norad_cat_id": window.norad_cat_id,
                    "ground_station": window.ground_station,
                    "merged_window_index": window.merged_index,
                    "start_utc": format_utc_microseconds(window.start_us),
                    "end_utc": format_utc_microseconds(window.end_us),
                    "duration_seconds": microseconds_seconds_text(
                        window.end_us - window.start_us
                    ),
                    "source_observation_ids": ";".join(
                        str(value) for value in window.observation_ids
                    ),
                }
            )

        for gap_index, (left, right) in enumerate(
            zip(windows, windows[1:]),
            start=1,
        ):
            gap_us = right.start_us - left.end_us
            if gap_us <= 0:
                raise CanonicalExecutionError("non-positive gap after union")
            gap_frac = Fraction(gap_us, MICROS_PER_SECOND)
            gap_fracs.append(gap_frac)
            gap_rows.append(
                {
                    "trace_selection_order": order,
                    "norad_cat_id": left.norad_cat_id,
                    "ground_station": left.ground_station,
                    "gap_index": gap_index,
                    "previous_window_end_utc": format_utc_microseconds(
                        left.end_us
                    ),
                    "next_window_start_utc": format_utc_microseconds(
                        right.start_us
                    ),
                    "gap_seconds": microseconds_seconds_text(gap_us),
                }
            )

        duration_median = median_fraction(duration_fracs)
        gap_median = median_fraction(gap_fracs)
        gap_mean = (
            sum(gap_fracs, Fraction(0, 1)) / len(gap_fracs)
            if gap_fracs
            else None
        )
        gap_sd = population_sd_fraction_decimal(gap_fracs)

        gap_cv = None
        gap_burstiness = None
        if (
            gap_sd is not None
            and gap_mean is not None
            and gap_mean > 0
        ):
            mean_dec = decimal_from_fraction(gap_mean)
            with localcontext() as ctx:
                ctx.prec = 80
                gap_cv = gap_sd / mean_dec
                denominator = gap_sd + mean_dec
                if denominator != 0:
                    gap_burstiness = (gap_sd - mean_dec) / denominator

        first = windows[0]
        summary_rows.append(
            {
                "trace_selection_order": order,
                "norad_cat_id": first.norad_cat_id,
                "ground_station": first.ground_station,
                "raw_observation_count": raw_counts[order],
                "merged_window_count": len(windows),
                "gap_count": len(gap_fracs),
                "duration_min_seconds": fraction_text(min(duration_fracs)),
                "duration_median_seconds": fraction_text(duration_median),
                "duration_max_seconds": fraction_text(max(duration_fracs)),
                "gap_min_seconds": (
                    fraction_text(min(gap_fracs)) if gap_fracs else ""
                ),
                "gap_median_seconds": fraction_text(gap_median),
                "gap_max_seconds": (
                    fraction_text(max(gap_fracs)) if gap_fracs else ""
                ),
                "gap_mean_seconds": fraction_text(gap_mean),
                "gap_population_sd_seconds": (
                    rounded_decimal_text(gap_sd)
                    if gap_sd is not None
                    else ""
                ),
                "gap_coefficient_of_variation": (
                    rounded_decimal_text(gap_cv)
                    if gap_cv is not None
                    else ""
                ),
                "gap_burstiness_index": (
                    rounded_decimal_text(gap_burstiness)
                    if gap_burstiness is not None
                    else ""
                ),
            }
        )

    return window_rows, gap_rows, summary_rows


def build_anchors(
    merged_by_trace: Mapping[int, Sequence[MergedWindow]],
    source_end_us: int,
) -> list[Anchor]:
    anchors: list[Anchor] = []
    followup_us = 24 * SECONDS_PER_HOUR * MICROS_PER_SECOND

    for order in sorted(merged_by_trace):
        windows = list(merged_by_trace[order])
        eligible = [
            window
            for window in windows
            if window.end_us + followup_us <= source_end_us
        ]
        for eligible_index, window in enumerate(eligible, start=1):
            anchors.append(
                Anchor(
                    selection_order=order,
                    norad_cat_id=window.norad_cat_id,
                    ground_station=window.ground_station,
                    anchor_index=eligible_index,
                    anchor_id=f"TRACE{order:02d}-A{eligible_index:03d}",
                    anchor_us=window.end_us,
                    merged_window_index=window.merged_index,
                )
            )
    return anchors


def relative_future_windows(
    *,
    anchor: Anchor,
    merged_windows: Sequence[MergedWindow],
    horizon_hours: int,
) -> list[tuple[Fraction, Fraction]]:
    horizon_us = horizon_hours * SECONDS_PER_HOUR * MICROS_PER_SECOND
    horizon_end_us = anchor.anchor_us + horizon_us
    result: list[tuple[Fraction, Fraction]] = []

    for window in merged_windows:
        if window.merged_index <= anchor.merged_window_index:
            continue
        if window.start_us < anchor.anchor_us:
            raise CanonicalExecutionError("future window starts before anchor")
        if window.start_us >= horizon_end_us:
            continue
        clipped_end = min(window.end_us, horizon_end_us)
        if clipped_end <= window.start_us:
            continue
        result.append(
            (
                Fraction(
                    window.start_us - anchor.anchor_us,
                    MICROS_PER_SECOND,
                ),
                Fraction(
                    clipped_end - anchor.anchor_us,
                    MICROS_PER_SECOND,
                ),
            )
        )
    return result


def sufficient_upper_bound_bps(
    profile: str,
    windows: Sequence[tuple[Fraction, Fraction]],
) -> int | None:
    if not windows:
        return None
    durations = [end - start for start, end in windows]
    if any(duration <= 0 for duration in durations):
        raise CanonicalExecutionError("non-positive future window duration")
    shortest = min(durations)
    sizes = PROFILE_OBJECTS[profile]
    burden_bytes = sum(sizes.values()) + max(sizes.values())
    ratio = Fraction(8 * burden_bytes, 1) / shortest
    bound = ratio.numerator // ratio.denominator + 1
    return max(1, bound)


def reference_threshold(
    *,
    profile: str,
    policy: str,
    disruption: str,
    horizon_s: Fraction,
    windows: Sequence[tuple[Fraction, Fraction]],
    upper_bound_bps: int,
) -> int | None:
    def succeeds(rate_bps: int) -> bool:
        result = independent_evaluate(
            profile=profile,
            policy=policy,
            disruption=disruption,
            horizon_s=horizon_s,
            rate_bps=rate_bps,
            windows=windows,
        )
        return bool(result["trusted_recovery_success"])

    if not succeeds(upper_bound_bps):
        return None

    low = 1
    high = upper_bound_bps
    while low < high:
        mid = (low + high) // 2
        if succeeds(mid):
            high = mid
        else:
            low = mid + 1

    threshold = low
    if not succeeds(threshold):
        raise CanonicalExecutionError("reference threshold does not succeed")
    if threshold > 1 and succeeds(threshold - 1):
        raise CanonicalExecutionError(
            "reference threshold predecessor unexpectedly succeeds"
        )
    return threshold


def comparable_result(result: Mapping[str, object]) -> dict[str, object]:
    return {
        key: result[key]
        for key in (
            "trusted_recovery_success",
            "recovery_completion_time_s",
            "windows_consumed",
            "cryptographic_bytes_transferred",
            "transition_attempts",
            "legacy_exposure_s",
            "control_unavailable_s",
            "dual_epoch_overlap_s",
            "rollback_invoked",
            "stale_epoch_acceptance",
            "terminal_state",
            "proof_accepted_time_s",
            "commit_time_s",
            "p3_guard_blocked",
        )
    }


def serialize_case_result(
    *,
    anchor: Anchor,
    horizon_hours: int,
    profile: str,
    policy: str,
    disruption: str,
    future_window_count: int,
    upper_bound_bps: int | None,
    threshold: int | None,
    threshold_result: Mapping[str, object] | None,
    upper_bound_result: Mapping[str, object] | None,
) -> dict[str, object]:
    finite = threshold is not None
    return {
        "trace_selection_order": anchor.selection_order,
        "norad_cat_id": anchor.norad_cat_id,
        "ground_station": anchor.ground_station,
        "anchor_id": anchor.anchor_id,
        "anchor_time_utc": format_utc_microseconds(anchor.anchor_us),
        "horizon_hours": horizon_hours,
        "profile": profile,
        "policy": policy,
        "disruption": disruption,
        "future_merged_window_count": future_window_count,
        "sufficient_upper_bound_bps": (
            upper_bound_bps if upper_bound_bps is not None else ""
        ),
        "finite_threshold": int(finite),
        "minimum_rate_bps": threshold if threshold is not None else "",
        "trusted_recovery_success_at_threshold": (
            threshold_result["trusted_recovery_success"]
            if threshold_result is not None
            else ""
        ),
        "recovery_completion_elapsed_seconds": (
            fraction_text(threshold_result["recovery_completion_time_s"])
            if threshold_result is not None
            else ""
        ),
        "windows_consumed_at_threshold": (
            threshold_result["windows_consumed"]
            if threshold_result is not None
            else ""
        ),
        "cryptographic_bytes_transferred_at_threshold": (
            threshold_result["cryptographic_bytes_transferred"]
            if threshold_result is not None
            else ""
        ),
        "transition_attempts_at_threshold": (
            threshold_result["transition_attempts"]
            if threshold_result is not None
            else ""
        ),
        "legacy_exposure_seconds_at_threshold": (
            fraction_text(threshold_result["legacy_exposure_s"])
            if threshold_result is not None
            else ""
        ),
        "control_unavailable_seconds_at_threshold": (
            fraction_text(threshold_result["control_unavailable_s"])
            if threshold_result is not None
            else ""
        ),
        "dual_epoch_overlap_seconds_at_threshold": (
            fraction_text(threshold_result["dual_epoch_overlap_s"])
            if threshold_result is not None
            else ""
        ),
        "rollback_invoked_at_threshold": (
            threshold_result["rollback_invoked"]
            if threshold_result is not None
            else ""
        ),
        "stale_epoch_acceptance_at_threshold": (
            threshold_result["stale_epoch_acceptance"]
            if threshold_result is not None
            else ""
        ),
        "terminal_state_at_threshold": (
            threshold_result["terminal_state"]
            if threshold_result is not None
            else ""
        ),
        "terminal_state_at_sufficient_upper_bound": (
            upper_bound_result["terminal_state"]
            if upper_bound_result is not None and not finite
            else ""
        ),
        "p3_guard_blocked_at_sufficient_upper_bound": (
            upper_bound_result["p3_guard_blocked"]
            if upper_bound_result is not None and not finite
            else ""
        ),
        "rollback_invoked_at_sufficient_upper_bound": (
            upper_bound_result["rollback_invoked"]
            if upper_bound_result is not None and not finite
            else ""
        ),
        "stale_epoch_acceptance_at_sufficient_upper_bound": (
            upper_bound_result["stale_epoch_acceptance"]
            if upper_bound_result is not None and not finite
            else ""
        ),
    }


def threshold_value_for_ordering(value: int | None) -> tuple[int, int]:
    return (1, 0) if value is None else (0, value)


def csv_write(path: Path, rows: Sequence[Mapping[str, object]]) -> None:
    if not rows:
        raise CanonicalExecutionError(f"refusing to write empty CSV: {path.name}")
    fieldnames = list(rows[0].keys())
    for row in rows:
        if list(row.keys()) != fieldnames:
            raise CanonicalExecutionError(
                f"inconsistent CSV row schema for {path.name}"
            )
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=fieldnames,
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)


def group_counts(
    case_rows: Sequence[Mapping[str, object]],
    dimension: str,
) -> dict[str, object]:
    grouped: dict[str, Counter[str]] = defaultdict(Counter)
    for row in case_rows:
        key = str(row[dimension])
        grouped[key]["total"] += 1
        if row["finite_threshold"] == 1:
            grouped[key]["finite"] += 1
        else:
            grouped[key]["nonfinite"] += 1

    output: dict[str, object] = {}
    for key in sorted(grouped):
        counter = grouped[key]
        output[key] = {
            "total": counter["total"],
            "finite": counter["finite"],
            "nonfinite": counter["nonfinite"],
            "finite_fraction": exact_proportion(
                counter["finite"],
                counter["total"],
            ),
        }
    return output


def run_canonical(
    *,
    trace_jsonl: Path,
    protocol_path: Path,
    population_path: Path,
    trace_freeze_path: Path,
    implementation_freeze_path: Path,
    output_dir: Path,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    protocol, population, trace_freeze, implementation = load_frozen_contracts(
        protocol_path=protocol_path,
        population_path=population_path,
        trace_freeze_path=trace_freeze_path,
        implementation_freeze_path=implementation_freeze_path,
    )

    trace_grouped = load_trace(trace_jsonl, population, trace_freeze)
    merged_by_trace = {
        order: merge_trace_windows(rows)
        for order, rows in sorted(trace_grouped.items())
    }

    timing_window_rows, timing_gap_rows, timing_summary_rows = timing_outputs(
        merged_by_trace,
        {order: len(rows) for order, rows in trace_grouped.items()},
    )
    source_end_us = parse_utc_microseconds(SOURCE_END_TEXT)
    anchors = build_anchors(merged_by_trace, source_end_us)

    anchor_rows = [
        {
            "trace_selection_order": anchor.selection_order,
            "norad_cat_id": anchor.norad_cat_id,
            "ground_station": anchor.ground_station,
            "anchor_index": anchor.anchor_index,
            "anchor_id": anchor.anchor_id,
            "anchor_time_utc": format_utc_microseconds(anchor.anchor_us),
            "source_merged_window_index": anchor.merged_window_index,
        }
        for anchor in anchors
    ]

    if not anchor_rows:
        raise CanonicalExecutionError(
            "canonical anchor population is empty; preserve failure evidence"
        )

    case_rows: list[dict[str, object]] = []
    case_thresholds: dict[
        tuple[int, str, int, str, str, str], int | None
    ] = {}
    case_windows: dict[
        tuple[int, str, int], list[tuple[Fraction, Fraction]]
    ] = {}
    independent_mismatches: list[dict[str, object]] = []
    case_keys: set[tuple[object, ...]] = set()

    for anchor in anchors:
        trace_windows = merged_by_trace[anchor.selection_order]

        for horizon_hours in HORIZONS_HOURS:
            horizon_s = Fraction(horizon_hours * SECONDS_PER_HOUR, 1)
            windows = relative_future_windows(
                anchor=anchor,
                merged_windows=trace_windows,
                horizon_hours=horizon_hours,
            )
            case_windows[
                (anchor.selection_order, anchor.anchor_id, horizon_hours)
            ] = windows

            for profile in PROFILE_ORDER:
                upper_bound = sufficient_upper_bound_bps(profile, windows)
                independent_upper_bound = (
                    independent_strict_sufficient_upper_bound_bps(
                        profile,
                        windows,
                    )
                )
                if upper_bound != independent_upper_bound:
                    raise CanonicalExecutionError(
                        "primary/reference sufficient upper-bound mismatch "
                        f"for trace={anchor.selection_order} "
                        f"anchor={anchor.anchor_id} "
                        f"horizon={horizon_hours} "
                        f"profile={profile}: "
                        f"{upper_bound!r} != {independent_upper_bound!r}"
                    )

                for policy in POLICY_ORDER:
                    for disruption in DISRUPTION_ORDER:
                        key = (
                            anchor.selection_order,
                            anchor.anchor_id,
                            horizon_hours,
                            profile,
                            policy,
                            disruption,
                        )
                        if key in case_keys:
                            raise CanonicalExecutionError(
                                f"duplicate canonical case key: {key}"
                            )
                        case_keys.add(key)

                        main_threshold: int | None
                        ref_threshold: int | None
                        threshold_main_result = None
                        threshold_ref_result = None
                        upper_main_result = None
                        upper_ref_result = None

                        if upper_bound is None:
                            main_threshold = None
                            ref_threshold = None
                        else:
                            main_threshold = minimum_integer_rate_bps(
                                profile=profile,
                                policy=policy,
                                disruption=disruption,
                                horizon_s=horizon_s,
                                windows=windows,
                                max_rate_bps=upper_bound,
                            )
                            ref_threshold = reference_threshold(
                                profile=profile,
                                policy=policy,
                                disruption=disruption,
                                horizon_s=horizon_s,
                                windows=windows,
                                upper_bound_bps=upper_bound,
                            )

                            if main_threshold != ref_threshold:
                                independent_mismatches.append(
                                    {
                                        "case_key": list(key),
                                        "kind": "threshold",
                                        "primary": main_threshold,
                                        "reference": ref_threshold,
                                    }
                                )

                            if main_threshold is not None:
                                threshold_main_result = evaluate_case(
                                    ExternalCase(
                                        profile=profile,
                                        policy=policy,
                                        disruption=disruption,
                                        horizon_s=horizon_s,
                                        rate_bps=main_threshold,
                                    ),
                                    windows,
                                )
                                threshold_ref_result = independent_evaluate(
                                    profile=profile,
                                    policy=policy,
                                    disruption=disruption,
                                    horizon_s=horizon_s,
                                    rate_bps=main_threshold,
                                    windows=windows,
                                )
                                if comparable_result(
                                    threshold_main_result
                                ) != comparable_result(threshold_ref_result):
                                    independent_mismatches.append(
                                        {
                                            "case_key": list(key),
                                            "kind": "threshold_state",
                                            "primary": {
                                                name: fraction_text(value)
                                                if isinstance(value, Fraction)
                                                else value
                                                for name, value in comparable_result(
                                                    threshold_main_result
                                                ).items()
                                            },
                                            "reference": {
                                                name: fraction_text(value)
                                                if isinstance(value, Fraction)
                                                else value
                                                for name, value in comparable_result(
                                                    threshold_ref_result
                                                ).items()
                                            },
                                        }
                                    )
                            else:
                                upper_main_result = evaluate_case(
                                    ExternalCase(
                                        profile=profile,
                                        policy=policy,
                                        disruption=disruption,
                                        horizon_s=horizon_s,
                                        rate_bps=upper_bound,
                                    ),
                                    windows,
                                )
                                upper_ref_result = independent_evaluate(
                                    profile=profile,
                                    policy=policy,
                                    disruption=disruption,
                                    horizon_s=horizon_s,
                                    rate_bps=upper_bound,
                                    windows=windows,
                                )
                                if comparable_result(
                                    upper_main_result
                                ) != comparable_result(upper_ref_result):
                                    independent_mismatches.append(
                                        {
                                            "case_key": list(key),
                                            "kind": "sufficient_bound_state",
                                            "primary_terminal": upper_main_result[
                                                "terminal_state"
                                            ],
                                            "reference_terminal": upper_ref_result[
                                                "terminal_state"
                                            ],
                                        }
                                    )

                        case_thresholds[key] = main_threshold
                        case_rows.append(
                            serialize_case_result(
                                anchor=anchor,
                                horizon_hours=horizon_hours,
                                profile=profile,
                                policy=policy,
                                disruption=disruption,
                                future_window_count=len(windows),
                                upper_bound_bps=upper_bound,
                                threshold=main_threshold,
                                threshold_result=threshold_main_result,
                                upper_bound_result=upper_main_result,
                            )
                        )

    expected_cases = len(anchors) * 144
    if len(case_rows) != expected_cases:
        raise CanonicalExecutionError(
            f"case count {len(case_rows)} != expected {expected_cases}"
        )

    p3_p1_rows: list[dict[str, object]] = []
    common_rate_audit_mismatches = 0

    for anchor in anchors:
        for horizon_hours in HORIZONS_HOURS:
            horizon_s = Fraction(horizon_hours * SECONDS_PER_HOUR, 1)
            windows = case_windows[
                (anchor.selection_order, anchor.anchor_id, horizon_hours)
            ]
            for profile in PROFILE_ORDER:
                for disruption in DISRUPTION_ORDER:
                    p1_key = (
                        anchor.selection_order,
                        anchor.anchor_id,
                        horizon_hours,
                        profile,
                        "P1_STAGED_CUTOVER",
                        disruption,
                    )
                    p3_key = (
                        anchor.selection_order,
                        anchor.anchor_id,
                        horizon_hours,
                        profile,
                        "P3_CONTACT_AWARE_STAGED",
                        disruption,
                    )
                    p1 = case_thresholds[p1_key]
                    p3 = case_thresholds[p3_key]

                    if p1 is not None and p3 is not None:
                        feasibility_class = "both_finite"
                        threshold_diff = p3 - p1
                        common_rate = max(p1, p3)
                        p1_common = evaluate_case(
                            ExternalCase(
                                profile=profile,
                                policy="P1_STAGED_CUTOVER",
                                disruption=disruption,
                                horizon_s=horizon_s,
                                rate_bps=common_rate,
                            ),
                            windows,
                        )
                        p3_common = evaluate_case(
                            ExternalCase(
                                profile=profile,
                                policy="P3_CONTACT_AWARE_STAGED",
                                disruption=disruption,
                                horizon_s=horizon_s,
                                rate_bps=common_rate,
                            ),
                            windows,
                        )
                        p1_ref = independent_evaluate(
                            profile=profile,
                            policy="P1_STAGED_CUTOVER",
                            disruption=disruption,
                            horizon_s=horizon_s,
                            rate_bps=common_rate,
                            windows=windows,
                        )
                        p3_ref = independent_evaluate(
                            profile=profile,
                            policy="P3_CONTACT_AWARE_STAGED",
                            disruption=disruption,
                            horizon_s=horizon_s,
                            rate_bps=common_rate,
                            windows=windows,
                        )
                        if (
                            comparable_result(p1_common)
                            != comparable_result(p1_ref)
                            or comparable_result(p3_common)
                            != comparable_result(p3_ref)
                        ):
                            common_rate_audit_mismatches += 1
                        if (
                            not p1_common["trusted_recovery_success"]
                            or not p3_common["trusted_recovery_success"]
                        ):
                            raise CanonicalExecutionError(
                                "P1/P3 common-rate comparison did not preserve success"
                            )

                        common_fields = {
                            "common_rate_bps": common_rate,
                            "p3_minus_p1_legacy_exposure_seconds": fraction_text(
                                p3_common["legacy_exposure_s"]
                                - p1_common["legacy_exposure_s"]
                            ),
                            "p3_minus_p1_control_unavailable_seconds": fraction_text(
                                p3_common["control_unavailable_s"]
                                - p1_common["control_unavailable_s"]
                            ),
                            "p3_minus_p1_windows_consumed": (
                                p3_common["windows_consumed"]
                                - p1_common["windows_consumed"]
                            ),
                            "p3_minus_p1_cryptographic_bytes_transferred": (
                                p3_common["cryptographic_bytes_transferred"]
                                - p1_common["cryptographic_bytes_transferred"]
                            ),
                            "p3_minus_p1_transition_attempts": (
                                p3_common["transition_attempts"]
                                - p1_common["transition_attempts"]
                            ),
                        }
                    elif p1 is None and p3 is None:
                        feasibility_class = "both_nonfinite"
                        threshold_diff = ""
                        common_fields = {
                            "common_rate_bps": "",
                            "p3_minus_p1_legacy_exposure_seconds": "",
                            "p3_minus_p1_control_unavailable_seconds": "",
                            "p3_minus_p1_windows_consumed": "",
                            "p3_minus_p1_cryptographic_bytes_transferred": "",
                            "p3_minus_p1_transition_attempts": "",
                        }
                    elif p1 is not None:
                        feasibility_class = "P1_only_finite"
                        threshold_diff = ""
                        common_fields = {
                            "common_rate_bps": "",
                            "p3_minus_p1_legacy_exposure_seconds": "",
                            "p3_minus_p1_control_unavailable_seconds": "",
                            "p3_minus_p1_windows_consumed": "",
                            "p3_minus_p1_cryptographic_bytes_transferred": "",
                            "p3_minus_p1_transition_attempts": "",
                        }
                    else:
                        feasibility_class = "P3_only_finite"
                        threshold_diff = ""
                        common_fields = {
                            "common_rate_bps": "",
                            "p3_minus_p1_legacy_exposure_seconds": "",
                            "p3_minus_p1_control_unavailable_seconds": "",
                            "p3_minus_p1_windows_consumed": "",
                            "p3_minus_p1_cryptographic_bytes_transferred": "",
                            "p3_minus_p1_transition_attempts": "",
                        }

                    p3_p1_rows.append(
                        {
                            "trace_selection_order": anchor.selection_order,
                            "norad_cat_id": anchor.norad_cat_id,
                            "ground_station": anchor.ground_station,
                            "anchor_id": anchor.anchor_id,
                            "anchor_time_utc": format_utc_microseconds(
                                anchor.anchor_us
                            ),
                            "horizon_hours": horizon_hours,
                            "profile": profile,
                            "disruption": disruption,
                            "p1_minimum_rate_bps": (
                                p1 if p1 is not None else ""
                            ),
                            "p3_minimum_rate_bps": (
                                p3 if p3 is not None else ""
                            ),
                            "feasibility_classification": feasibility_class,
                            "p3_minus_p1_minimum_rate_bps": threshold_diff,
                            **common_fields,
                        }
                    )

    if common_rate_audit_mismatches:
        independent_mismatches.append(
            {
                "kind": "common_rate_state",
                "count": common_rate_audit_mismatches,
            }
        )

    profile_rows: list[dict[str, object]] = []
    for anchor in anchors:
        for horizon_hours in HORIZONS_HOURS:
            for policy in POLICY_ORDER:
                for disruption in DISRUPTION_ORDER:
                    values: list[int | None] = []
                    for profile in PROFILE_ORDER:
                        key = (
                            anchor.selection_order,
                            anchor.anchor_id,
                            horizon_hours,
                            profile,
                            policy,
                            disruption,
                        )
                        values.append(case_thresholds[key])

                    ordered_ok = (
                        threshold_value_for_ordering(values[0])
                        <= threshold_value_for_ordering(values[1])
                        <= threshold_value_for_ordering(values[2])
                    )
                    profile_rows.append(
                        {
                            "trace_selection_order": anchor.selection_order,
                            "norad_cat_id": anchor.norad_cat_id,
                            "ground_station": anchor.ground_station,
                            "anchor_id": anchor.anchor_id,
                            "anchor_time_utc": format_utc_microseconds(
                                anchor.anchor_us
                            ),
                            "horizon_hours": horizon_hours,
                            "policy": policy,
                            "disruption": disruption,
                            "profile_512_44_minimum_rate_bps": (
                                values[0] if values[0] is not None else ""
                            ),
                            "profile_768_65_minimum_rate_bps": (
                                values[1] if values[1] is not None else ""
                            ),
                            "profile_1024_87_minimum_rate_bps": (
                                values[2] if values[2] is not None else ""
                            ),
                            "nondecreasing_burden_ordering": int(ordered_ok),
                            "ordering_violation": int(not ordered_ok),
                        }
                    )

    audit = {
        "schema": 1,
        "experiment_id": EXPERIMENT_ID,
        "protocol_id": PROTOCOL_ID,
        "audit_id": "S8E-CANON-AUDIT-001",
        "status": "PASS" if not independent_mismatches else "FAIL",
        "canonical_case_count": len(case_rows),
        "primary_reference_mismatch_count": len(independent_mismatches),
        "mismatches": independent_mismatches,
        "reference_implementation": (
            "study8e/audit/independent_external_reference.py"
        ),
        "real_trace_case_audit": True,
    }

    if independent_mismatches:
        (output_dir / "INDEPENDENT_AUDIT.json").write_bytes(
            canonical_json_bytes(audit)
        )
        raise CanonicalExecutionError(
            f"independent audit mismatches: {len(independent_mismatches)}"
        )

    p3_classes = Counter(
        str(row["feasibility_classification"]) for row in p3_p1_rows
    )
    finite_differences = [
        int(row["p3_minus_p1_minimum_rate_bps"])
        for row in p3_p1_rows
        if row["feasibility_classification"] == "both_finite"
    ]
    equal_count = sum(value == 0 for value in finite_differences)
    p3_lower_count = sum(value < 0 for value in finite_differences)
    p3_higher_count = sum(value > 0 for value in finite_differences)

    finite_count = sum(
        int(row["finite_threshold"]) for row in case_rows
    )
    nonfinite_count = len(case_rows) - finite_count
    ordering_violations = sum(
        int(row["ordering_violation"]) for row in profile_rows
    )

    threshold_values = [
        int(row["minimum_rate_bps"])
        for row in case_rows
        if row["finite_threshold"] == 1
    ]

    findings = {
        "schema": 1,
        "experiment_id": EXPERIMENT_ID,
        "protocol_id": PROTOCOL_ID,
        "results_id": "S8E-CANON-RESULTS-002",
        "frozen_inputs": {
            "population_freeze": POPULATION_FREEZE_ID,
            "trace_freeze": TRACE_FREEZE_ID,
            "trace_jsonl_sha256": sha256_file(trace_jsonl),
            "implementation_freeze": IMPLEMENTATION_FREEZE_ID,
        },
        "population": {
            "trace_count": len(merged_by_trace),
            "raw_observation_count": sum(
                len(rows) for rows in trace_grouped.values()
            ),
            "merged_window_count": sum(
                len(windows) for windows in merged_by_trace.values()
            ),
            "eligible_anchor_count": len(anchors),
            "cases_per_anchor": 144,
            "canonical_case_count": len(case_rows),
            "expected_case_count": expected_cases,
            "eligible_anchors_by_trace": {
                str(order): sum(
                    anchor.selection_order == order for anchor in anchors
                )
                for order in sorted(merged_by_trace)
            },
        },
        "finite_threshold": {
            "finite_count": finite_count,
            "nonfinite_count": nonfinite_count,
            "finite_fraction": exact_proportion(
                finite_count,
                len(case_rows),
            ),
            "finite_threshold_bps_summary": {
                "minimum": min(threshold_values)
                if threshold_values
                else None,
                "median": fraction_text(
                    median_fraction(
                        [Fraction(value, 1) for value in threshold_values]
                    )
                )
                if threshold_values
                else None,
                "maximum": max(threshold_values)
                if threshold_values
                else None,
            },
            "by_horizon": group_counts(case_rows, "horizon_hours"),
            "by_profile": group_counts(case_rows, "profile"),
            "by_policy": group_counts(case_rows, "policy"),
            "by_disruption": group_counts(case_rows, "disruption"),
        },
        "p3_vs_p1": {
            "matched_comparison_count": len(p3_p1_rows),
            "feasibility_classification_counts": dict(
                sorted(p3_classes.items())
            ),
            "both_finite_equal_threshold_count": equal_count,
            "both_finite_p3_lower_threshold_count": p3_lower_count,
            "both_finite_p3_higher_threshold_count": p3_higher_count,
            "both_finite_threshold_difference_summary": {
                "minimum": min(finite_differences)
                if finite_differences
                else None,
                "median": fraction_text(
                    median_fraction(
                        [
                            Fraction(value, 1)
                            for value in finite_differences
                        ]
                    )
                )
                if finite_differences
                else None,
                "maximum": max(finite_differences)
                if finite_differences
                else None,
            },
        },
        "profile_burden_ordering": {
            "matched_comparison_count": len(profile_rows),
            "ordering_violation_count": ordering_violations,
            "ordering_preserved_count": len(profile_rows)
            - ordering_violations,
        },
        "structural_safety_fields": {
            "stale_epoch_acceptance_sum_at_finite_thresholds": sum(
                int(row["stale_epoch_acceptance_at_threshold"] or 0)
                for row in case_rows
            ),
            "rollback_invoked_sum_at_finite_thresholds": sum(
                int(row["rollback_invoked_at_threshold"] or 0)
                for row in case_rows
            ),
            "stale_epoch_acceptance_sum_at_nonfinite_sufficient_bounds": sum(
                int(row["stale_epoch_acceptance_at_sufficient_upper_bound"] or 0)
                for row in case_rows
            ),
            "rollback_invoked_sum_at_nonfinite_sufficient_bounds": sum(
                int(row["rollback_invoked_at_sufficient_upper_bound"] or 0)
                for row in case_rows
            ),
        },
        "independent_audit": {
            "status": audit["status"],
            "case_mismatch_count": 0,
        },
        "study8_directional_comparison_boundary": {
            "equal_total_capacity_R1_R4_reestimated": False,
            "causal_between_trace_timing_claim_permitted": False,
            "pooling_with_study8": False,
        },
    }

    csv_write(
        output_dir / "TRACE_TIMING_WINDOWS.csv",
        timing_window_rows,
    )
    csv_write(
        output_dir / "TRACE_TIMING_GAPS.csv",
        timing_gap_rows,
    )
    csv_write(
        output_dir / "TRACE_TIMING_SUMMARY.csv",
        timing_summary_rows,
    )
    csv_write(
        output_dir / "ANCHOR_MANIFEST.csv",
        anchor_rows,
    )
    csv_write(
        output_dir / "CANONICAL_CASE_RESULTS.csv",
        case_rows,
    )
    csv_write(
        output_dir / "P3_P1_CONTRASTS.csv",
        p3_p1_rows,
    )
    csv_write(
        output_dir / "PROFILE_ORDERING_CHECKS.csv",
        profile_rows,
    )
    (output_dir / "CANONICAL_FINDINGS.json").write_bytes(
        canonical_json_bytes(findings)
    )
    (output_dir / "INDEPENDENT_AUDIT.json").write_bytes(
        canonical_json_bytes(audit)
    )

    scientific_files = (
        "TRACE_TIMING_WINDOWS.csv",
        "TRACE_TIMING_GAPS.csv",
        "TRACE_TIMING_SUMMARY.csv",
        "ANCHOR_MANIFEST.csv",
        "CANONICAL_CASE_RESULTS.csv",
        "P3_P1_CONTRASTS.csv",
        "PROFILE_ORDERING_CHECKS.csv",
        "CANONICAL_FINDINGS.json",
        "INDEPENDENT_AUDIT.json",
    )
    manifest = {
        "schema": 1,
        "experiment_id": EXPERIMENT_ID,
        "protocol_id": PROTOCOL_ID,
        "results_id": "S8E-CANON-RESULTS-001",
        "files": {
            name: {
                "sha256": sha256_file(output_dir / name),
                "bytes": (output_dir / name).stat().st_size,
            }
            for name in scientific_files
        },
    }
    (output_dir / "RESULTS_HASH_MANIFEST.json").write_bytes(
        canonical_json_bytes(manifest)
    )

    print("Study 8E canonical execution: PASS")
    print(f"trace_count={len(merged_by_trace)}")
    print(f"eligible_anchor_count={len(anchors)}")
    print(f"canonical_case_count={len(case_rows)}")
    print(f"finite_threshold_count={finite_count}")
    print(f"nonfinite_threshold_count={nonfinite_count}")
    print(f"p3_p1_comparisons={len(p3_p1_rows)}")
    print(f"profile_ordering_violations={ordering_violations}")
    print("independent_case_mismatches=0")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trace-jsonl", required=True, type=Path)
    parser.add_argument("--protocol", required=True, type=Path)
    parser.add_argument("--population", required=True, type=Path)
    parser.add_argument("--trace-freeze", required=True, type=Path)
    parser.add_argument("--implementation-freeze", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()

    run_canonical(
        trace_jsonl=args.trace_jsonl,
        protocol_path=args.protocol,
        population_path=args.population,
        trace_freeze_path=args.trace_freeze,
        implementation_freeze_path=args.implementation_freeze,
        output_dir=args.output_dir,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
