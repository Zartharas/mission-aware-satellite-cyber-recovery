#!/usr/bin/env python3
"""Deterministic, rate-bounded SatNOGS pair selection for S8E-ECTV-001.

This is a pre-analysis population-selection program. It accesses only the
minimum public API rows required by the prospectively recorded deviation
S8E-DEV-SATNOGS-CURSOR-THROTTLE-001. It does not compute contact durations,
inter-contact gaps, clustering/burstiness, payload-rate thresholds, policy
outcomes, profile outcomes, or any recovery endpoint.

Persisted scientific selection state is limited to source request identities,
response hashes, pair identifiers, deterministic rank, eligibility evidence,
and exact selection bookkeeping.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urlencode, urlparse
from urllib.request import Request, urlopen

EXPERIMENT_ID = "S8E-ECTV-001"
DEVIATION_ID = "S8E-DEV-SATNOGS-FILTER-PARAM-002"
DISCOVERY_DEVIATION_ID = "S8E-DEV-SATNOGS-CURSOR-THROTTLE-001"
BASE_URL = "https://network.satnogs.org/api/observations/"
MONTH_START = "2026-06-01T00:00:00Z"
MONTH_END = "2026-07-01T00:00:00Z"
TARGET_PAIRS = 32
MAX_PER_NORAD = 2
MAX_PER_STATION = 2
MIN_OBSERVATIONS = 20
HARD_REQUEST_CAP = 50
REQUEST_DELAY_SECONDS = 2.5
USER_AGENT = "S8E-ECTV-001-population-freeze/1.0"

SEED_WINDOWS = (
    ("2026-06-02T15:50:00Z", "2026-06-02T16:00:00Z"),
    ("2026-06-05T21:20:00Z", "2026-06-05T21:30:00Z"),
    ("2026-06-08T07:30:00Z", "2026-06-08T07:40:00Z"),
    ("2026-06-12T04:20:00Z", "2026-06-12T04:30:00Z"),
    ("2026-06-13T05:00:00Z", "2026-06-13T05:10:00Z"),
    ("2026-06-16T11:30:00Z", "2026-06-16T11:40:00Z"),
    ("2026-06-21T00:50:00Z", "2026-06-21T01:00:00Z"),
    ("2026-06-22T06:10:00Z", "2026-06-22T06:20:00Z"),
    ("2026-06-26T01:00:00Z", "2026-06-26T01:10:00Z"),
    ("2026-06-28T22:10:00Z", "2026-06-28T22:20:00Z"),
)


class SelectionFailure(RuntimeError):
    pass


def canonical_json_bytes(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")


def rank_pair(norad_cat_id: int, ground_station: int) -> str:
    material = f"SATNOGS|{norad_cat_id}|{ground_station}".encode("ascii")
    return hashlib.sha256(material).hexdigest()


def pair_pool_sha256(pairs: set[tuple[int, int]]) -> str:
    rows = [f"{norad}|{station}" for norad, station in sorted(pairs)]
    return hashlib.sha256(("\n".join(rows) + "\n").encode("ascii")).hexdigest()


def next_cursor_present(link_header: str | None) -> bool:
    if not link_header:
        return False
    return 'rel="next"' in link_header or "rel=next" in link_header


def request_page(params: dict[str, str], request_index: int) -> tuple[list[object], dict[str, object]]:
    query = urlencode(params)
    url = BASE_URL + "?" + query
    req = Request(
        url,
        headers={"Accept": "application/json", "User-Agent": USER_AGENT},
        method="GET",
    )
    try:
        with urlopen(req, timeout=60) as response:
            body = response.read()
            status = response.status
            link = response.headers.get("Link")
            retry_after = response.headers.get("Retry-After")
    except HTTPError as exc:
        body = exc.read()
        raise SelectionFailure(
            f"HTTPError request={request_index} status={exc.code} "
            f"body_sha256={hashlib.sha256(body).hexdigest()} "
            f"retry_after={exc.headers.get('Retry-After')!r}"
        ) from exc
    except URLError as exc:
        raise SelectionFailure(
            f"URLError request={request_index} reason_type={type(exc.reason).__name__}"
        ) from exc

    if status != 200:
        raise SelectionFailure(f"Unexpected HTTP status request={request_index} status={status}")

    try:
        payload = json.loads(body)
    except json.JSONDecodeError as exc:
        raise SelectionFailure(
            f"Non-JSON response request={request_index} "
            f"body_sha256={hashlib.sha256(body).hexdigest()}"
        ) from exc

    if not isinstance(payload, list):
        raise SelectionFailure(
            f"Unexpected response shape request={request_index} type={type(payload).__name__}"
        )

    evidence = {
        "request_index": request_index,
        "response_sha256": hashlib.sha256(body).hexdigest(),
        "response_bytes": len(body),
        "records_on_first_page": len(payload),
        "next_cursor_present": next_cursor_present(link),
        "retry_after_present": retry_after is not None,
    }
    return payload, evidence


def valid_pair_from_row(row: object) -> tuple[int, int] | None:
    if not isinstance(row, dict):
        return None
    norad = row.get("norad_cat_id")
    station = row.get("ground_station")
    if isinstance(norad, bool) or isinstance(station, bool):
        return None
    if not isinstance(norad, int) or not isinstance(station, int):
        return None
    return norad, station


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)

    request_count = 0
    request_evidence: list[dict[str, object]] = []
    candidate_pairs: set[tuple[int, int]] = set()
    seed_invalid_identifier_rows = 0

    def do_request(params: dict[str, str], purpose: str) -> list[object]:
        nonlocal request_count
        if request_count >= HARD_REQUEST_CAP:
            raise SelectionFailure("Hard request cap reached before attempted request")
        request_count += 1
        rows, ev = request_page(params, request_count)
        ev["purpose"] = purpose
        request_evidence.append(ev)
        if request_count < HARD_REQUEST_CAP:
            time.sleep(REQUEST_DELAY_SECONDS)
        return rows

    try:
        for seed_index, (start, end) in enumerate(SEED_WINDOWS):
            rows = do_request(
                {"start": start, "end": end, "format": "json"},
                f"seed_discovery_{seed_index:02d}",
            )
            for row in rows:
                pair = valid_pair_from_row(row)
                if pair is None:
                    seed_invalid_identifier_rows += 1
                    continue
                candidate_pairs.add(pair)

        ranked = sorted(
            (
                {
                    "norad_cat_id": norad,
                    "ground_station": station,
                    "rank_sha256": rank_pair(norad, station),
                }
                for norad, station in candidate_pairs
            ),
            key=lambda x: (x["rank_sha256"], x["norad_cat_id"], x["ground_station"]),
        )

        selected: list[dict[str, object]] = []
        norad_selected: Counter[int] = Counter()
        station_selected: Counter[int] = Counter()
        skipped_cap = 0
        evaluated = 0
        rejected_below_threshold = 0

        for candidate in ranked:
            if len(selected) >= TARGET_PAIRS or request_count >= HARD_REQUEST_CAP:
                break

            norad = int(candidate["norad_cat_id"])
            station = int(candidate["ground_station"])
            if norad_selected[norad] >= MAX_PER_NORAD or station_selected[station] >= MAX_PER_STATION:
                skipped_cap += 1
                continue

            rows = do_request(
                {
                    "start": MONTH_START,
                    "end": MONTH_END,
                    "norad_cat_id": str(norad),
                    "ground_station": str(station),
                    "format": "json",
                },
                "pair_qualification",
            )
            evaluated += 1
            for row in rows:
                pair = valid_pair_from_row(row)
                if pair != (norad, station):
                    raise SelectionFailure(
                        f"pair qualification filter mismatch requested={norad}/{station} observed={pair}"
                    )
            first_page_records = len(rows)
            if first_page_records < MIN_OBSERVATIONS:
                rejected_below_threshold += 1
                continue

            selected.append({
                "norad_cat_id": norad,
                "ground_station": station,
                "rank_sha256": candidate["rank_sha256"],
                "eligibility_evidence": {
                    "minimum_required_observations": MIN_OBSERVATIONS,
                    "first_page_records": first_page_records,
                    "threshold_met": True,
                },
            })
            norad_selected[norad] += 1
            station_selected[station] += 1

        target_reached = len(selected) == TARGET_PAIRS
        status = "TARGET_REACHED" if target_reached else "INCOMPLETE_HARD_CAP_OR_CANDIDATE_EXHAUSTION"

        report = {
            "schema": 1,
            "experiment_id": EXPERIMENT_ID,
            "deviation_id": DEVIATION_ID,
            "stage": "DETERMINISTIC_RATE_BOUNDED_PAIR_SELECTION_CORRECTED_FILTER",
            "generated_utc": datetime.now(timezone.utc).isoformat(),
            "status": status,\n            "supersedes_population_freeze": "S8E-SATNOGS-POP-001",\n            "filter_parameter": "norad_cat_id",
            "source": {
                "base_url": BASE_URL,
                "month_start": MONTH_START,
                "month_end_exclusive": MONTH_END,
                "seed_windows_utc": [list(x) for x in SEED_WINDOWS],
            },
            "selection_contract": {
                "target_pairs": TARGET_PAIRS,
                "minimum_observations": MIN_OBSERVATIONS,
                "maximum_pairs_per_norad_cat_id": MAX_PER_NORAD,
                "maximum_pairs_per_ground_station": MAX_PER_STATION,
                "hard_request_cap": HARD_REQUEST_CAP,
                "request_delay_seconds": REQUEST_DELAY_SECONDS,
            },
            "candidate_discovery": {
                "seed_request_count": len(SEED_WINDOWS),
                "unique_candidate_pair_count": len(candidate_pairs),
                "candidate_pair_pool_sha256": pair_pool_sha256(candidate_pairs),
                "invalid_identifier_rows": seed_invalid_identifier_rows,
                "candidate_identities_persisted_in_report": False,
            },
            "qualification": {
                "candidates_evaluated": evaluated,
                "candidates_rejected_below_threshold": rejected_below_threshold,
                "candidates_skipped_due_to_entity_caps": skipped_cap,
                "selected_pair_count": len(selected),
            },
            "selected_pairs": selected,
            "request_evidence": request_evidence,
            "scope_boundary": {
                "duration_computed": False,
                "gap_computed": False,
                "clustering_or_burstiness_computed": False,
                "status_or_transmitter_baud_used": False,
                "recovery_model_executed": False,
                "policy_or_profile_endpoint_computed": False,
                "timing_endpoint_computed": False,
                "study8_modified": False,
                "acta_package_modified": False,
            },
        }
        args.output.write_bytes(canonical_json_bytes(report))

    except SelectionFailure as exc:
        failure = {
            "schema": 1,
            "experiment_id": EXPERIMENT_ID,
            "deviation_id": DEVIATION_ID,
            "stage": "DETERMINISTIC_RATE_BOUNDED_PAIR_SELECTION_CORRECTED_FILTER",
            "generated_utc": datetime.now(timezone.utc).isoformat(),
            "status": "FAIL_CLOSED",
            "failure": str(exc),
            "request_count": request_count,
            "request_evidence": request_evidence,
            "candidate_discovery": {
                "unique_candidate_pair_count_so_far": len(candidate_pairs),
                "candidate_pair_pool_sha256_so_far": pair_pool_sha256(candidate_pairs),
                "candidate_identities_persisted_in_report": False,
            },
            "scope_boundary": {
                "duration_computed": False,
                "gap_computed": False,
                "recovery_model_executed": False,
                "study8e_endpoint_computed": False,
            },
        }
        args.output.write_bytes(canonical_json_bytes(failure))
        print(f"Study 8E pair selection failed closed: {exc}", file=sys.stderr)
        return 2

    print(f"Study 8E pair selection status: {status}")
    print(f"Requests issued: {request_count}/{HARD_REQUEST_CAP}")
    print(f"Candidate pairs discovered: {len(candidate_pairs)}")
    print(f"Candidates evaluated: {evaluated}")
    print(f"Selected pairs: {len(selected)}/{TARGET_PAIRS}")
    print("No timing distributions or recovery endpoints were computed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
