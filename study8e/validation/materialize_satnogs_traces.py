#!/usr/bin/env python3
"""Materialize frozen Study 8E SatNOGS traces without computing endpoints.

The program follows cursor pagination for the 32 pairs frozen in
S8E-SATNOGS-POP-001. It persists only id/start/end/ground_station/norad_cat_id,
plus request/response provenance. It does not compute duration, gaps, burstiness,
capacity, payload-rate thresholds, policy/profile results, or recovery outcomes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlparse
from urllib.request import Request, urlopen

BASE_URL = "https://network.satnogs.org/api/observations/"
START = "2026-06-01T00:00:00Z"
END = "2026-07-01T00:00:00Z"
FIELDS = ("id", "start", "end", "ground_station", "norad_cat_id")
USER_AGENT = "S8E-ECTV-001-trace-materializer/1.0"
LINK_RE = re.compile(r'<([^>]+)>\s*;\s*rel="([^"]+)"')


class AcquisitionError(RuntimeError):
    pass


def canonical_bytes(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def parse_dt(value: object) -> datetime:
    if not isinstance(value, str):
        raise ValueError("timestamp_not_string")
    text = value[:-1] + "+00:00" if value.endswith("Z") else value
    dt = datetime.fromisoformat(text)
    if dt.tzinfo is None:
        raise ValueError("timestamp_missing_timezone")
    return dt.astimezone(timezone.utc)


def next_link(header: str | None) -> str | None:
    if not header:
        return None
    for url, rel in LINK_RE.findall(header):
        if rel == "next":
            return url
    return None


def safe_request_url(url: str) -> str:
    parsed = urlparse(url)
    return parsed._replace(scheme="https", netloc="network.satnogs.org", fragment="").geturl()


def get_page(url: str, request_index: int) -> tuple[list[object], dict[str, object], str | None]:
    req = Request(url, headers={"Accept": "application/json", "User-Agent": USER_AGENT}, method="GET")
    try:
        with urlopen(req, timeout=90) as response:
            body = response.read()
            status = response.status
            link = response.headers.get("Link")
            retry = response.headers.get("Retry-After")
    except HTTPError as exc:
        body = exc.read()
        raise AcquisitionError(
            f"HTTPError request={request_index} status={exc.code} "
            f"body_sha256={sha256_bytes(body)} retry_after={exc.headers.get('Retry-After')!r}"
        ) from exc
    except URLError as exc:
        raise AcquisitionError(
            f"URLError request={request_index} reason_type={type(exc.reason).__name__}"
        ) from exc

    if status != 200:
        raise AcquisitionError(f"unexpected_status request={request_index} status={status}")

    try:
        payload = json.loads(body)
    except json.JSONDecodeError as exc:
        raise AcquisitionError(
            f"non_json request={request_index} response_sha256={sha256_bytes(body)}"
        ) from exc
    if not isinstance(payload, list):
        raise AcquisitionError(
            f"unexpected_shape request={request_index} type={type(payload).__name__}"
        )

    provenance = {
        "request_index": request_index,
        "request_url": safe_request_url(url),
        "http_status": status,
        "response_bytes": len(body),
        "response_sha256": sha256_bytes(body),
        "records": len(payload),
        "retry_after_present": retry is not None,
        "next_cursor_present": next_link(link) is not None,
    }
    return payload, provenance, next_link(link)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--population-freeze", required=True, type=Path)
    ap.add_argument("--output-dir", required=True, type=Path)
    ap.add_argument("--minimum-request-interval-seconds", type=float, default=61.0)
    ap.add_argument("--maximum-api-requests", type=int, default=180)
    args = ap.parse_args()

    freeze = json.loads(args.population_freeze.read_text(encoding="utf-8"))
    if freeze.get("freeze_id") != "S8E-SATNOGS-POP-001":
        raise SystemExit("unexpected population freeze identity")
    pairs = freeze.get("selected_pairs")
    if not isinstance(pairs, list) or len(pairs) != 32:
        raise SystemExit("frozen population must contain exactly 32 selected pairs")

    out = args.output_dir
    traces_dir = out / "traces"
    traces_dir.mkdir(parents=True, exist_ok=True)
    invalid_path = out / "invalid_records.jsonl"
    invalid_fh = invalid_path.open("w", encoding="utf-8")

    start_dt = parse_dt(START)
    end_dt = parse_dt(END)
    request_count = 0
    last_request_monotonic: float | None = None
    seen_ids_global: set[int] = set()
    pair_manifests: list[dict[str, object]] = []
    all_page_provenance: list[dict[str, object]] = []
    total_valid = 0
    total_invalid = 0

    def rate_wait() -> None:
        nonlocal last_request_monotonic
        if last_request_monotonic is None:
            return
        elapsed = time.monotonic() - last_request_monotonic
        remaining = args.minimum_request_interval_seconds - elapsed
        if remaining > 0:
            time.sleep(remaining)

    try:
        for pair in pairs:
            order = int(pair["selection_order"])
            norad = int(pair["norad_cat_id"])
            station = int(pair["ground_station"])
            trace_path = traces_dir / f"{order:02d}_norad_{norad}_station_{station}.jsonl"
            trace_fh = trace_path.open("w", encoding="utf-8")
            pair_valid = 0
            pair_invalid = 0
            pair_page_hashes: list[str] = []

            params = {
                "start": START,
                "end": END,
                "satellite__norad_cat_id": str(norad),
                "ground_station": str(station),
                "format": "json",
            }
            url: str | None = BASE_URL + "?" + urlencode(params)
            page_number = 0

            while url is not None:
                if request_count >= args.maximum_api_requests:
                    raise AcquisitionError(
                        f"maximum_api_requests_reached cap={args.maximum_api_requests}"
                    )
                rate_wait()
                request_count += 1
                last_request_monotonic = time.monotonic()
                rows, provenance, url = get_page(url, request_count)
                page_number += 1
                provenance.update({
                    "selection_order": order,
                    "norad_cat_id": norad,
                    "ground_station": station,
                    "page_number": page_number,
                })
                all_page_provenance.append(provenance)
                pair_page_hashes.append(str(provenance["response_sha256"]))

                for row in rows:
                    reason: list[str] = []
                    if not isinstance(row, dict):
                        reason.append("row_not_object")
                        record = {}
                    else:
                        record = {field: row.get(field) for field in FIELDS}

                    if any(field not in row for field in FIELDS) if isinstance(row, dict) else True:
                        reason.append("missing_required_field")

                    rid = record.get("id")
                    if isinstance(rid, bool) or not isinstance(rid, int):
                        reason.append("invalid_id_type")
                    elif rid in seen_ids_global:
                        reason.append("duplicate_observation_id")

                    rn = record.get("norad_cat_id")
                    rs = record.get("ground_station")
                    if rn != norad:
                        reason.append("norad_pair_mismatch")
                    if rs != station:
                        reason.append("station_pair_mismatch")

                    try:
                        row_start = parse_dt(record.get("start"))
                        row_end = parse_dt(record.get("end"))
                        if not (start_dt <= row_start < end_dt):
                            reason.append("start_outside_frozen_window")
                        if not (start_dt < row_end <= end_dt):
                            reason.append("end_outside_frozen_window")
                        if row_end <= row_start:
                            reason.append("end_not_after_start")
                    except (ValueError, TypeError):
                        reason.append("invalid_timestamp")

                    if reason:
                        invalid_fh.write(json.dumps({
                            "selection_order": order,
                            "norad_cat_id": norad,
                            "ground_station": station,
                            "reason": sorted(set(reason)),
                            "record": record,
                        }, sort_keys=True) + "\n")
                        pair_invalid += 1
                        total_invalid += 1
                        continue

                    assert isinstance(rid, int)
                    seen_ids_global.add(rid)
                    trace_fh.write(json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n")
                    pair_valid += 1
                    total_valid += 1

            trace_fh.close()
            trace_bytes = trace_path.read_bytes()
            pair_manifests.append({
                "selection_order": order,
                "norad_cat_id": norad,
                "ground_station": station,
                "valid_records": pair_valid,
                "invalid_records": pair_invalid,
                "pages": page_number,
                "trace_file": str(trace_path.relative_to(out)),
                "trace_sha256": sha256_bytes(trace_bytes),
                "response_page_sha256": pair_page_hashes,
            })

        invalid_fh.close()
        invalid_bytes = invalid_path.read_bytes()
        manifest = {
            "schema": 1,
            "experiment_id": "S8E-ECTV-001",
            "acquisition_id": "S8E-SATNOGS-TRACE-001",
            "source_population_freeze": "S8E-SATNOGS-POP-001",
            "generated_utc": datetime.now(timezone.utc).isoformat(),
            "source_url": BASE_URL,
            "source_window_utc": {"start": START, "end_exclusive": END},
            "materialized_fields": list(FIELDS),
            "pair_count": len(pair_manifests),
            "total_valid_records": total_valid,
            "total_invalid_records": total_invalid,
            "api_requests": request_count,
            "minimum_request_interval_seconds": args.minimum_request_interval_seconds,
            "maximum_api_requests": args.maximum_api_requests,
            "pairs": pair_manifests,
            "invalid_records_file": str(invalid_path.relative_to(out)),
            "invalid_records_sha256": sha256_bytes(invalid_bytes),
            "page_provenance": all_page_provenance,
            "scope_boundary": {
                "duration_distribution_computed": False,
                "inter_opportunity_gap_computed": False,
                "burstiness_computed": False,
                "payload_rate_threshold_computed": False,
                "recovery_model_executed": False,
                "policy_or_profile_endpoint_computed": False,
                "study8_modified": False,
                "acta_package_modified": False,
            },
        }
        manifest_path = out / "TRACE_ACQUISITION_MANIFEST.json"
        manifest_path.write_bytes(canonical_bytes(manifest))
        print(f"acquisition_id={manifest['acquisition_id']}")
        print(f"pairs={len(pair_manifests)}")
        print(f"valid_records={total_valid}")
        print(f"invalid_records={total_invalid}")
        print(f"api_requests={request_count}")
        print(f"manifest_sha256={sha256_bytes(manifest_path.read_bytes())}")
        print("No timing distribution or recovery endpoint was computed.")
        return 0

    except AcquisitionError as exc:
        invalid_fh.close()
        failure = {
            "schema": 1,
            "experiment_id": "S8E-ECTV-001",
            "acquisition_id": "S8E-SATNOGS-TRACE-001",
            "status": "FAIL_CLOSED_PARTIAL_ACQUISITION",
            "generated_utc": datetime.now(timezone.utc).isoformat(),
            "failure": str(exc),
            "api_requests": request_count,
            "pairs_completed": len(pair_manifests),
            "total_valid_records_so_far": total_valid,
            "total_invalid_records_so_far": total_invalid,
            "page_provenance": all_page_provenance,
            "scope_boundary": {
                "timing_endpoint_computed": False,
                "recovery_model_executed": False,
            },
        }
        (out / "TRACE_ACQUISITION_FAILURE.json").write_bytes(canonical_bytes(failure))
        print(f"Study 8E trace acquisition failed closed: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
