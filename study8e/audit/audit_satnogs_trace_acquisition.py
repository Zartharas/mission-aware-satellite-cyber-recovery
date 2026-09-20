#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

FIELDS = ("id", "start", "end", "ground_station", "norad_cat_id")
START = "2026-06-01T00:00:00Z"
END = "2026-07-01T00:00:00Z"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_dt(value: object) -> datetime:
    if not isinstance(value, str):
        raise ValueError("timestamp_not_string")
    text = value[:-1] + "+00:00" if value.endswith("Z") else value
    dt = datetime.fromisoformat(text)
    if dt.tzinfo is None:
        raise ValueError("timestamp_missing_timezone")
    return dt.astimezone(timezone.utc)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--acquisition-dir", required=True, type=Path)
    ap.add_argument("--output", required=True, type=Path)
    args = ap.parse_args()

    root = args.acquisition_dir
    manifest_path = root / "TRACE_ACQUISITION_MANIFEST.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("acquisition_id") != "S8E-SATNOGS-TRACE-001":
        raise SystemExit("unexpected acquisition identity")
    if manifest.get("pair_count") != 32:
        raise SystemExit("trace acquisition must contain exactly 32 pairs")
    if manifest.get("materialized_fields") != list(FIELDS):
        raise SystemExit("unexpected materialized field set")

    start_dt = parse_dt(START)
    end_dt = parse_dt(END)
    global_ids: set[int] = set()
    total_records = 0
    pair_checks = []

    for pair in manifest["pairs"]:
        order = int(pair["selection_order"])
        norad = int(pair["norad_cat_id"])
        station = int(pair["ground_station"])
        trace = root / str(pair["trace_file"])
        if not trace.is_file():
            raise SystemExit(f"missing trace file: {trace}")
        actual_hash = sha256(trace)
        if actual_hash != pair["trace_sha256"]:
            raise SystemExit(f"trace hash mismatch for selection_order={order}")

        records = 0
        local_ids: set[int] = set()
        with trace.open("r", encoding="utf-8") as fh:
            for line_number, line in enumerate(fh, start=1):
                row = json.loads(line)
                if sorted(row) != sorted(FIELDS):
                    raise SystemExit(
                        f"unexpected trace fields selection_order={order} line={line_number}"
                    )
                rid = row["id"]
                if isinstance(rid, bool) or not isinstance(rid, int):
                    raise SystemExit(f"invalid observation id selection_order={order}")
                if rid in local_ids or rid in global_ids:
                    raise SystemExit(f"duplicate observation id={rid}")
                local_ids.add(rid)
                global_ids.add(rid)
                if row["norad_cat_id"] != norad or row["ground_station"] != station:
                    raise SystemExit(f"pair identity mismatch selection_order={order}")
                row_start = parse_dt(row["start"])
                row_end = parse_dt(row["end"])
                if not (start_dt <= row_start < end_dt):
                    raise SystemExit(f"start outside source window selection_order={order}")
                if not (start_dt < row_end <= end_dt):
                    raise SystemExit(f"end outside source window selection_order={order}")
                if row_end <= row_start:
                    raise SystemExit(f"nonpositive source window selection_order={order}")
                records += 1

        if records != int(pair["valid_records"]):
            raise SystemExit(f"record count mismatch selection_order={order}")
        total_records += records
        pair_checks.append({
            "selection_order": order,
            "norad_cat_id": norad,
            "ground_station": station,
            "valid_records": records,
            "trace_sha256": actual_hash,
            "status": "PASS",
        })

    if total_records != int(manifest["total_valid_records"]):
        raise SystemExit("global valid record count mismatch")

    invalid_file = root / str(manifest["invalid_records_file"])
    if not invalid_file.is_file():
        raise SystemExit("missing invalid record file")
    if sha256(invalid_file) != manifest["invalid_records_sha256"]:
        raise SystemExit("invalid-record file hash mismatch")

    for page in manifest["page_provenance"]:
        parsed = urlparse(page["request_url"])
        if parsed.scheme != "https" or parsed.netloc != "network.satnogs.org":
            raise SystemExit("page provenance escaped frozen SatNOGS host")
        if parsed.path != "/api/observations/":
            raise SystemExit("unexpected page provenance API path")
        if int(page["records"]) < 0 or int(page["records"]) > 25:
            raise SystemExit("unexpected page size")

    report = {
        "schema": 1,
        "experiment_id": "S8E-ECTV-001",
        "audit_id": "S8E-SATNOGS-TRACE-AUDIT-001",
        "status": "PASS",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "acquisition_manifest_sha256": sha256(manifest_path),
        "pair_count": 32,
        "total_valid_records": total_records,
        "total_invalid_records": int(manifest["total_invalid_records"]),
        "unique_observation_ids": len(global_ids),
        "pair_checks": pair_checks,
        "page_provenance_records": len(manifest["page_provenance"]),
        "scope_boundary": {
            "duration_distribution_computed": False,
            "inter_opportunity_gap_computed": False,
            "burstiness_computed": False,
            "payload_rate_threshold_computed": False,
            "recovery_model_executed": False,
            "study8e_real_trace_endpoint_computed": False,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("Study 8E trace acquisition independent audit: PASS")
    print(f"audit_sha256={sha256(args.output)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
