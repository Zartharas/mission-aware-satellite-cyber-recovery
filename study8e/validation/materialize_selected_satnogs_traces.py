#!/usr/bin/env python3
"""Materialize the frozen POP-002 SatNOGS first-page timing corpus.

Pre-analysis acquisition only. Exactly one June-window first-page query is
issued for each pair in S8E-SATNOGS-POP-002. The returned count for each pair
must exactly match the count frozen during corrected population qualification.
Only protocol-approved fields are persisted. Timestamps are parsed only for
source-window and start-before-end integrity checks. No duration, gap,
burstiness, capacity, policy, profile, or recovery endpoint is computed.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

BASE_URL = "https://network.satnogs.org/api/observations/"
MONTH_START = "2026-06-01T00:00:00Z"
MONTH_END = "2026-07-01T00:00:00Z"
EXPECTED_FREEZE_ID = "S8E-SATNOGS-POP-002"
EXPECTED_TOTAL = 476
FIELDS = ("id", "start", "end", "ground_station", "norad_cat_id")
USER_AGENT = "S8E-ECTV-001-trace-materializer-pop002/1.0"
REQUEST_DELAY_SECONDS = 2.5


class MaterializationError(RuntimeError):
    pass


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_json_bytes(value: object) -> bytes:
    return (
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        )
        + "\n"
    ).encode("utf-8")


def parse_ts(value: object) -> datetime:
    if not isinstance(value, str):
        raise MaterializationError(
            f"timestamp is not string: {type(value).__name__}"
        )
    text = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        dt = datetime.fromisoformat(text)
    except ValueError as exc:
        raise MaterializationError("timestamp is not ISO-8601 parseable") from exc
    if dt.tzinfo is None:
        raise MaterializationError("timestamp lacks timezone")
    return dt.astimezone(timezone.utc)


def load_freeze(path: Path) -> tuple[list[dict[str, object]], int]:
    doc = json.loads(path.read_text(encoding="utf-8"))
    if doc.get("freeze_id") != EXPECTED_FREEZE_ID:
        raise MaterializationError(
            f"wrong population freeze: {doc.get('freeze_id')!r}"
        )
    pairs = doc.get("selected_pairs")
    expected_total = doc.get("frozen_first_page_record_total")
    if not isinstance(pairs, list) or len(pairs) != 20:
        raise MaterializationError(
            "POP-002 must contain exactly 20 frozen selected pairs"
        )
    if expected_total != EXPECTED_TOTAL:
        raise MaterializationError(
            f"POP-002 frozen total {expected_total!r} != {EXPECTED_TOTAL}"
        )
    return pairs, int(expected_total)


def fetch_pair(
    norad: int,
    station: int,
) -> tuple[list[object], dict[str, object]]:
    params = {
        "start": MONTH_START,
        "end": MONTH_END,
        "norad_cat_id": str(norad),
        "ground_station": str(station),
        "format": "json",
    }
    req = Request(
        BASE_URL + "?" + urlencode(params),
        headers={"Accept": "application/json", "User-Agent": USER_AGENT},
        method="GET",
    )
    try:
        with urlopen(req, timeout=60) as response:
            body = response.read()
            status = response.status
            link = response.headers.get("Link")
    except HTTPError as exc:
        body = exc.read()
        raise MaterializationError(
            f"HTTP error {exc.code} for pair {norad}/{station}, "
            f"body_sha256={sha256_bytes(body)}"
        ) from exc
    except URLError as exc:
        raise MaterializationError(
            f"network error for pair {norad}/{station}: "
            f"{type(exc.reason).__name__}"
        ) from exc

    if status != 200:
        raise MaterializationError(
            f"unexpected HTTP status {status} for pair {norad}/{station}"
        )
    try:
        payload = json.loads(body)
    except json.JSONDecodeError as exc:
        raise MaterializationError(
            f"non-JSON response for pair {norad}/{station}, "
            f"body_sha256={sha256_bytes(body)}"
        ) from exc
    if not isinstance(payload, list):
        raise MaterializationError(
            f"unexpected response shape for pair {norad}/{station}"
        )

    return payload, {
        "response_sha256": sha256_bytes(body),
        "response_bytes": len(body),
        "records": len(payload),
        "next_cursor_present": bool(
            link and ('rel="next"' in link or "rel=next" in link)
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--population-freeze", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()

    pairs, expected_total = load_freeze(args.population_freeze)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    pair_dir = args.output_dir / "pairs"
    pair_dir.mkdir(parents=True, exist_ok=True)

    month_start = parse_ts(MONTH_START)
    month_end = parse_ts(MONTH_END)

    combined_records: list[dict[str, object]] = []
    pair_manifest: list[dict[str, object]] = []
    global_ids: set[int] = set()

    for idx, pair in enumerate(pairs, start=1):
        order = pair.get("selection_order")
        norad = pair.get("norad_cat_id")
        station = pair.get("ground_station")
        eligibility = pair.get("eligibility_evidence")
        if (
            order != idx
            or not isinstance(norad, int)
            or not isinstance(station, int)
            or not isinstance(eligibility, dict)
        ):
            raise MaterializationError("invalid frozen pair identity/order")

        expected_count = eligibility.get("first_page_records")
        if not isinstance(expected_count, int) or expected_count < 20:
            raise MaterializationError(
                f"invalid frozen first-page count for pair {norad}/{station}"
            )

        raw_rows, response_meta = fetch_pair(norad, station)
        if len(raw_rows) != expected_count:
            raise MaterializationError(
                f"pair {norad}/{station} returned {len(raw_rows)} records, "
                f"expected frozen first-page count {expected_count}"
            )

        clean: list[dict[str, object]] = []
        pair_ids: set[int] = set()
        for raw in raw_rows:
            if not isinstance(raw, dict):
                raise MaterializationError(
                    f"pair {norad}/{station} contains non-object row"
                )
            if any(field not in raw for field in FIELDS):
                raise MaterializationError(
                    f"pair {norad}/{station} missing approved field"
                )
            row = {field: raw[field] for field in FIELDS}
            if not isinstance(row["id"], int):
                raise MaterializationError(
                    f"pair {norad}/{station} has non-integer id"
                )
            if row["id"] in pair_ids:
                raise MaterializationError(
                    f"pair {norad}/{station} has duplicate observation id"
                )
            if row["id"] in global_ids:
                raise MaterializationError(
                    f"observation id {row['id']} occurs in more than one pair"
                )
            pair_ids.add(row["id"])
            global_ids.add(row["id"])

            if (
                row["norad_cat_id"] != norad
                or row["ground_station"] != station
            ):
                raise MaterializationError(
                    f"pair filter mismatch for {norad}/{station}: "
                    f"{row['norad_cat_id']}/{row['ground_station']}"
                )

            start = parse_ts(row["start"])
            end = parse_ts(row["end"])
            if not (month_start <= start < month_end):
                raise MaterializationError(
                    f"pair {norad}/{station} start outside frozen month"
                )
            if not (month_start < end <= month_end):
                raise MaterializationError(
                    f"pair {norad}/{station} end outside frozen month"
                )
            if not start < end:
                raise MaterializationError(
                    f"pair {norad}/{station} has end <= start"
                )
            clean.append(row)

        pair_payload = b"".join(
            canonical_json_bytes(row) for row in clean
        )
        pair_name = f"{idx:02d}_norad{norad}_station{station}.jsonl"
        pair_path = pair_dir / pair_name
        pair_path.write_bytes(pair_payload)

        pair_manifest.append(
            {
                "selection_order": idx,
                "norad_cat_id": norad,
                "ground_station": station,
                "frozen_expected_records": expected_count,
                "records": len(clean),
                "file": f"pairs/{pair_name}",
                "file_sha256": sha256_bytes(pair_payload),
                "source_response_sha256": response_meta["response_sha256"],
                "source_response_bytes": response_meta["response_bytes"],
                "source_next_cursor_present": response_meta[
                    "next_cursor_present"
                ],
            }
        )

        for row in clean:
            combined_records.append(
                {
                    "selection_order": idx,
                    **row,
                }
            )

        if idx != len(pairs):
            time.sleep(REQUEST_DELAY_SECONDS)

    if len(combined_records) != expected_total:
        raise MaterializationError(
            f"combined record count {len(combined_records)} "
            f"!= frozen total {expected_total}"
        )

    combined_bytes = b"".join(
        canonical_json_bytes(row) for row in combined_records
    )
    combined_path = args.output_dir / "satnogs_pop002_firstpage_476.jsonl"
    combined_path.write_bytes(combined_bytes)

    csv_path = args.output_dir / "satnogs_pop002_firstpage_476.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=("selection_order",) + FIELDS,
        )
        writer.writeheader()
        writer.writerows(combined_records)

    manifest = {
        "schema": 1,
        "experiment_id": "S8E-ECTV-001",
        "artifact_id": "S8E-SATNOGS-TRACE-002",
        "population_freeze": EXPECTED_FREEZE_ID,
        "materialization_deviation": "S8E-DEV-SATNOGS-TRACE-CAP-002",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "source_window": {
            "start": MONTH_START,
            "end_exclusive": MONTH_END,
        },
        "source_ordering": ["-start", "-end"],
        "pairs": len(pairs),
        "records_total": len(combined_records),
        "requests_issued": len(pairs),
        "persisted_fields": list(FIELDS),
        "canonical_jsonl": {
            "file": combined_path.name,
            "sha256": sha256_bytes(combined_bytes),
            "bytes": len(combined_bytes),
        },
        "csv_projection": {
            "file": csv_path.name,
            "sha256": sha256_bytes(csv_path.read_bytes()),
            "bytes": csv_path.stat().st_size,
        },
        "pair_artifacts": pair_manifest,
        "validation": {
            "all_pair_record_counts_match_pop002_freeze": True,
            "all_pair_identifiers_match_pop002_freeze": True,
            "all_observation_ids_unique_across_corpus": True,
            "all_timestamps_parseable_and_timezone_aware": True,
            "all_start_before_end": True,
            "all_rows_within_frozen_source_window": True,
        },
        "scope_boundary": {
            "duration_values_computed": False,
            "gap_values_computed": False,
            "burstiness_computed": False,
            "payload_rate_threshold_computed": False,
            "recovery_model_executed": False,
            "policy_or_profile_endpoint_computed": False,
        },
    }
    manifest_path = args.output_dir / "TRACE_ARTIFACT_MANIFEST.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    print("Study 8E POP-002 trace materialization: PASS")
    print(f"pairs={len(pairs)}")
    print(f"records_total={len(combined_records)}")
    print(f"requests_issued={len(pairs)}")
    print(
        "canonical_jsonl_sha256="
        f"{manifest['canonical_jsonl']['sha256']}"
    )
    print("No timing distribution or recovery endpoint was computed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
