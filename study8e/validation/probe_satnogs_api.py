#!/usr/bin/env python3
"""Bounded SatNOGS API source/schema probe for S8E-ECTV-001.

This probe is deliberately pre-analysis. It performs one HTTP GET against the
prospectively frozen June 2026 source window and records only source identity,
HTTP/pagination behavior, response shape, required-field presence, and field
types. It does not emit row values, compute durations/gaps, select a scientific
population, or execute any recovery model.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

EXPERIMENT_ID = "S8E-ECTV-001"
BASE_URL = "https://network.satnogs.org/api/observations/"
START = "2026-06-01T00:00:00Z"
END = "2026-07-01T00:00:00Z"
REQUIRED_FIELDS = ("id", "start", "end", "ground_station", "norad_cat_id")
ALLOWED_HEADER_NAMES = (
    "content-type",
    "link",
    "retry-after",
    "x-ratelimit-limit",
    "x-ratelimit-remaining",
    "x-ratelimit-reset",
    "ratelimit-limit",
    "ratelimit-remaining",
    "ratelimit-reset",
)


def canonical_json_bytes(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")


def typename(value: object) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int):
        return "integer"
    if isinstance(value, float):
        return "number"
    if isinstance(value, str):
        return "string"
    if isinstance(value, list):
        return "array"
    if isinstance(value, dict):
        return "object"
    return type(value).__name__


def extract_records(payload: object) -> tuple[list[object], str, list[str]]:
    if isinstance(payload, list):
        return payload, "array", []
    if isinstance(payload, dict):
        top_keys = sorted(str(k) for k in payload)
        for key in ("results", "observations", "data"):
            candidate = payload.get(key)
            if isinstance(candidate, list):
                return candidate, f"object.{key}", top_keys
        return [], "object_without_recognized_record_array", top_keys
    return [], typename(payload), []


def selected_headers(headers) -> dict[str, str]:
    lower = {k.lower(): v for k, v in headers.items()}
    return {name: lower[name] for name in ALLOWED_HEADER_NAMES if name in lower}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)

    params = {
        "start": START,
        "end": END,
        "format": "json",
        "page_size": "1",
    }
    url = BASE_URL + "?" + urlencode(params)
    request = Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": "S8E-ECTV-001-source-schema-probe/1.0",
        },
        method="GET",
    )

    report: dict[str, object] = {
        "schema": 1,
        "experiment_id": EXPERIMENT_ID,
        "stage": "BOUNDED_SOURCE_IDENTITY_SCHEMA_PROBE",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "request": {
            "base_url": BASE_URL,
            "query": params,
            "request_count": 1,
        },
        "scope_boundary": {
            "row_values_persisted": False,
            "duration_computed": False,
            "gap_computed": False,
            "population_selected": False,
            "recovery_model_executed": False,
            "study8e_endpoint_computed": False,
        },
    }

    try:
        with urlopen(request, timeout=60) as response:
            body = response.read()
            status = response.status
            headers = response.headers
    except HTTPError as exc:
        body = exc.read()
        status = exc.code
        headers = exc.headers
        report["http"] = {
            "status": status,
            "response_sha256": hashlib.sha256(body).hexdigest(),
            "response_bytes": len(body),
            "selected_headers": selected_headers(headers),
            "error": "HTTPError",
        }
        args.output.write_bytes(canonical_json_bytes(report))
        print(f"SatNOGS bounded probe HTTP failure: {status}", file=sys.stderr)
        return 2
    except URLError as exc:
        report["http"] = {"error": "URLError", "reason_type": type(exc.reason).__name__}
        args.output.write_bytes(canonical_json_bytes(report))
        print(f"SatNOGS bounded probe network failure: {type(exc.reason).__name__}", file=sys.stderr)
        return 3

    report["http"] = {
        "status": status,
        "response_sha256": hashlib.sha256(body).hexdigest(),
        "response_bytes": len(body),
        "selected_headers": selected_headers(headers),
    }

    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        report["response"] = {
            "json_parse": "FAIL",
            "body_text_persisted": False,
        }
        args.output.write_bytes(canonical_json_bytes(report))
        print("SatNOGS bounded probe returned non-JSON content", file=sys.stderr)
        return 4

    records, shape, top_keys = extract_records(payload)
    first = records[0] if records else None
    first_keys = sorted(str(k) for k in first) if isinstance(first, dict) else []
    required_presence = {field: field in first_keys for field in REQUIRED_FIELDS}
    required_types = {
        field: typename(first[field]) if isinstance(first, dict) and field in first else "missing"
        for field in REQUIRED_FIELDS
    }

    report["response"] = {
        "json_parse": "PASS",
        "top_level_type": typename(payload),
        "record_container_shape": shape,
        "top_level_keys": top_keys,
        "records_on_probe_response": len(records),
        "first_record_keys": first_keys,
        "required_fields_present": required_presence,
        "required_field_types": required_types,
        "row_values_persisted": False,
        "json_pagination_metadata_present": {
            key: key in top_keys for key in ("count", "next", "previous", "results")
        },
        "link_header_present": bool(selected_headers(headers).get("link")),
    }

    ok = (
        status == 200
        and bool(records)
        and isinstance(first, dict)
        and all(required_presence.values())
    )
    report["overall_status"] = "PASS" if ok else "FAIL"
    args.output.write_bytes(canonical_json_bytes(report))

    print(f"SatNOGS bounded source/schema probe: {report['overall_status']}")
    print(f"HTTP status: {status}")
    print(f"Record container: {shape}")
    print(f"Records returned by bounded probe: {len(records)}")
    print(f"Required fields present: {all(required_presence.values())}")
    print("No row values, timing endpoints, or recovery endpoints were emitted.")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
