#!/usr/bin/env python3
"""Study 9 pre-freeze dataset integrity and reproducibility validator.

This program is deliberately pre-analysis. It verifies exact artifact identity,
container integrity, CSV structure, preregistered artifact-policy boundaries,
and deterministic parsing for the three proposed Study 9 source populations.
It does NOT perform recovery-state semantic mapping, selector execution,
action-identifiability analysis, statistical inference, or dataset repair.

Standard-library only so the same code can run natively on macOS and inside a
minimal Linux/Python container.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import platform
import sys
import zipfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import BinaryIO, Iterable

SCHEMA_VERSION = 1
STUDY_ID = "S9-RTSI-001"
CHUNK = 8 * 1024 * 1024

EXPECTED = {
    "CUCD_ID_V3": {
        "zip_sha256": "da3d95886feae0bc913a9e5beec1368571f51c80ecc811e40f6cc29edf33f2f0",
        "zip_size": 3131777,
        "member_count": 13,
        "raw": {
            "basename": "consolidated_dataset_raw.csv",
            "sha256": "2a6bb7bc9856099eef468dfe7df0043718a57c6ce84328e26b1883fa560c6ca2",
            "rows": 25000,
            "columns": 31,
        },
        "augmented": {
            "basename": "noised_dataset.csv",
            "sha256": "656fc2f23544469d8cbdca631747debc8dae7164621a2cd6740a5928cfae3c68",
            "rows": 22465,
            "columns": 23,
        },
        "required_basenames": [
            "README.md",
            "checksums.txt",
            "label_schema.json",
            "augmentation_script.py",
            "command_flood_script.txt",
            "data_injection_script.txt",
            "defence_impairment_script.txt",
            "storage_exhaustion_script.txt",
            "normal_ops_script.txt",
        ],
        "raw_label_counts": {"0": 5000, "1": 5000, "2": 5000, "3": 5000, "4": 5000},
    },
    "AEGISSAT_2025": {
        "basename": "AegisSat-AD.csv",
        "size": 190028590,
        "md5": "f5b53ba9d080fe1795def09bdecd7cb9",
        "sha256": "dcbaa9bb23c6492087d5dd6a5e0729e42fa84a2d43f5370bca967276426e487e",
        "rows": 137965,
        "columns": 176,
        "required_fields": [
            "run_id",
            "TLE File Name",
            "Epoch_Time",
            "UTC_Time",
            "command",
            "attacks.cpuhightarget.duration",
            "attacks.cpuhightarget.target",
        ],
        "attack_annotation_fields": [
            "attacks.cpuhightarget.duration",
            "attacks.cpuhightarget.target",
        ],
    },
    "UNSW_IOTSAT_2026": {
        "zip_sha256": "21f747325041e633df135aed2e12de4de518a5c4e62ded2270d7bbd0523c9d9d",
        "zip_size": 1431174739,
        "member_count": 6,
        "members": {
            "FEATURE_DOCUMENTATION.md": {
                "size": 22810,
                "sha256": "98d5a71eb3637d3cf71976655a24bb3f788c38da7b60f4703d27638b6a305b38",
            },
            "FEATURES.csv": {
                "size": 17398,
                "sha256": "95ccd70edd114bbf879ec163c4e801f4b5f3dd87a7767d434dcf15f2930cb476",
            },
            "UNSW_IoTSAT.csv": {
                "size": 145079423,
                "sha256": "06ef6681c90fbf4c43c0e8993cc2ccc803c21fa32ed30cbf54165b526c851521",
                "rows": 404798,
                "columns": 49,
            },
            "UNSW_IoTSAT.json": {
                "size": 664617049,
                "sha256": "b11775b7100e23430d6ef9ac0f21c15b3d946683fa043340de7547d3cc360ff5",
            },
            "UNSW_IoTSAT_with_CCSDS_fields.csv": {
                "size": 150632208,
                "sha256": "c117d04d7bfb8fa06413e2855c72fa8001dc0d8b58ffff4314cf41e08c4e8854",
                "rows": 404798,
                "columns": 52,
            },
            "UNSW_IoTSAT_With_Feature_Engineering.csv": {
                "size": 470804757,
                "sha256": "34a921079ecb908868e6038336b927cdc4683492a58dc026542affec9cbef1e5",
                "rows": 404798,
                "columns": 109,
            },
        },
        "excluded_base_fields": [
            "Vertical_Category",
            "Horizontal_Speed_ms",
            "Reception_Time",
            "Data_Quality_Score",
        ],
        "ccsds_label_conditioned_fields": [
            "CCSDS_MC_Frame_Count",
            "CCSDS_Packet_Sequence_Count",
            "CCSDS_APID",
        ],
        "excluded_artifacts": [
            "UNSW_IoTSAT.json",
            "UNSW_IoTSAT_With_Feature_Engineering.csv",
        ],
    },
}


class ValidationFailure(RuntimeError):
    pass


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def hashes_stream(stream: BinaryIO) -> tuple[str, str, int]:
    sha = hashlib.sha256()
    md5 = hashlib.md5()
    total = 0
    while True:
        block = stream.read(CHUNK)
        if not block:
            break
        sha.update(block)
        md5.update(block)
        total += len(block)
    return sha.hexdigest(), md5.hexdigest(), total


def hashes_file(path: Path) -> tuple[str, str, int]:
    with path.open("rb") as handle:
        return hashes_stream(handle)


def canonical_json_bytes(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")


def check(name: str, actual: object, expected: object) -> dict:
    return {"name": name, "pass": actual == expected, "actual": actual, "expected": expected}


def find_member(zf: zipfile.ZipFile, basename: str) -> zipfile.ZipInfo:
    matches = [info for info in zf.infolist() if not info.is_dir() and Path(info.filename).name == basename]
    if len(matches) != 1:
        raise ValidationFailure(f"Expected exactly one ZIP member named {basename!r}; found {len(matches)}")
    return matches[0]


def scan_csv_text(text, numeric_integrity: bool = False, label_field: str | None = None) -> dict:
    csv.field_size_limit(sys.maxsize)
    reader = csv.reader(text)
    header = next(reader, None)
    if header is None:
        raise ValidationFailure("CSV is empty and has no header")
    width = len(header)
    rows = 0
    width_mismatches = 0
    blank_values = 0
    nonnumeric_values = 0
    nonfinite_values = 0
    label_counts: Counter[str] = Counter()
    label_index = header.index(label_field) if label_field and label_field in header else None

    for row in reader:
        rows += 1
        if len(row) != width:
            width_mismatches += 1
        if label_index is not None and label_index < len(row):
            raw_label = row[label_index].strip()
            try:
                f = float(raw_label)
                label_counts[str(int(f)) if f.is_integer() else raw_label] += 1
            except Exception:
                label_counts[raw_label] += 1
        if numeric_integrity:
            for value in row:
                v = value.strip()
                if v == "":
                    blank_values += 1
                    continue
                try:
                    number = float(v)
                except Exception:
                    nonnumeric_values += 1
                    continue
                if not math.isfinite(number):
                    nonfinite_values += 1

    return {
        "rows": rows,
        "columns": width,
        "header": header,
        "row_width_mismatches": width_mismatches,
        "blank_values": blank_values if numeric_integrity else None,
        "nonnumeric_values": nonnumeric_values if numeric_integrity else None,
        "nonfinite_values": nonfinite_values if numeric_integrity else None,
        "label_counts": dict(sorted(label_counts.items())) if label_index is not None else None,
    }


def scan_csv_file(path: Path, numeric_integrity: bool = False, label_field: str | None = None) -> dict:
    with path.open("r", encoding="utf-8-sig", errors="strict", newline="") as text:
        return scan_csv_text(text, numeric_integrity=numeric_integrity, label_field=label_field)


def scan_csv_member(zf: zipfile.ZipFile, info: zipfile.ZipInfo, numeric_integrity: bool = False,
                    label_field: str | None = None) -> dict:
    import io
    with zf.open(info, "r") as raw:
        with io.TextIOWrapper(raw, encoding="utf-8-sig", errors="strict", newline="") as text:
            return scan_csv_text(text, numeric_integrity=numeric_integrity, label_field=label_field)


def verify_member_hash(zf: zipfile.ZipFile, info: zipfile.ZipInfo) -> dict:
    with zf.open(info, "r") as stream:
        sha, md5, size = hashes_stream(stream)
    return {"path": info.filename, "size": size, "sha256": sha, "md5": md5}


def validate_cucd(path: Path) -> dict:
    exp = EXPECTED["CUCD_ID_V3"]
    sha, md5, size = hashes_file(path)
    checks = [
        check("zip_sha256", sha, exp["zip_sha256"]),
        check("zip_size", size, exp["zip_size"]),
    ]
    with zipfile.ZipFile(path, "r") as zf:
        files = [i for i in zf.infolist() if not i.is_dir()]
        checks.append(check("zip_member_count", len(files), exp["member_count"]))
        basenames = sorted(Path(i.filename).name for i in files)
        missing_required = sorted(set(exp["required_basenames"]) - set(basenames))
        checks.append(check("required_members_present", missing_required, []))

        raw_info = find_member(zf, exp["raw"]["basename"])
        aug_info = find_member(zf, exp["augmented"]["basename"])
        raw_hash = verify_member_hash(zf, raw_info)
        aug_hash = verify_member_hash(zf, aug_info)
        checks.extend([
            check("raw_sha256", raw_hash["sha256"], exp["raw"]["sha256"]),
            check("augmented_sha256", aug_hash["sha256"], exp["augmented"]["sha256"]),
        ])

        raw_csv = scan_csv_member(zf, raw_info, numeric_integrity=True, label_field="Label")
        aug_csv = scan_csv_member(zf, aug_info, numeric_integrity=True, label_field="Label")
        checks.extend([
            check("raw_rows", raw_csv["rows"], exp["raw"]["rows"]),
            check("raw_columns", raw_csv["columns"], exp["raw"]["columns"]),
            check("raw_row_width_mismatches", raw_csv["row_width_mismatches"], 0),
            check("raw_blank_values", raw_csv["blank_values"], 0),
            check("raw_nonnumeric_values", raw_csv["nonnumeric_values"], 0),
            check("raw_nonfinite_values", raw_csv["nonfinite_values"], 0),
            check("raw_label_counts", raw_csv["label_counts"], exp["raw_label_counts"]),
            check("augmented_rows", aug_csv["rows"], exp["augmented"]["rows"]),
            check("augmented_columns", aug_csv["columns"], exp["augmented"]["columns"]),
            check("augmented_row_width_mismatches", aug_csv["row_width_mismatches"], 0),
            check("augmented_blank_values", aug_csv["blank_values"], 0),
            check("augmented_nonnumeric_values", aug_csv["nonnumeric_values"], 0),
            check("augmented_nonfinite_values", aug_csv["nonfinite_values"], 0),
        ])

    return {
        "status": "PASS" if all(c["pass"] for c in checks) else "FAIL",
        "checks": checks,
        "artifact": {"size": size, "sha256": sha, "md5": md5},
        "canonical_artifact": exp["raw"]["basename"],
        "derived_companion": exp["augmented"]["basename"],
        "label_evidence_role": "OFFLINE_GROUND_TRUTH_ONLY",
        "raw_schema": raw_csv,
        "augmented_schema": aug_csv,
    }


def validate_aegissat(path: Path) -> dict:
    exp = EXPECTED["AEGISSAT_2025"]
    sha, md5, size = hashes_file(path)
    csv_info = scan_csv_file(path)
    checks = [
        check("filename", path.name, exp["basename"]),
        check("size", size, exp["size"]),
        check("sha256", sha, exp["sha256"]),
        check("md5", md5, exp["md5"]),
        check("rows", csv_info["rows"], exp["rows"]),
        check("columns", csv_info["columns"], exp["columns"]),
        check("row_width_mismatches", csv_info["row_width_mismatches"], 0),
        check("required_fields_present", sorted(set(exp["required_fields"]) - set(csv_info["header"])), []),
    ]
    return {
        "status": "PASS" if all(c["pass"] for c in checks) else "FAIL",
        "checks": checks,
        "artifact": {"size": size, "sha256": sha, "md5": md5},
        "schema": csv_info,
        "canonical_artifact": exp["basename"],
        "attack_annotation_fields": exp["attack_annotation_fields"],
        "attack_annotation_evidence_role": "OFFLINE_GROUND_TRUTH_OR_EXPERIMENT_METADATA_ONLY",
    }


def last_nonwhitespace_byte(zf: zipfile.ZipFile, info: zipfile.ZipInfo) -> str | None:
    last = None
    with zf.open(info, "r") as stream:
        while True:
            block = stream.read(CHUNK)
            if not block:
                break
            stripped = block.rstrip()
            if stripped:
                last = stripped[-1]
    return chr(last) if last is not None else None


def validate_unsw(path: Path) -> dict:
    exp = EXPECTED["UNSW_IOTSAT_2026"]
    sha, md5, size = hashes_file(path)
    checks = [
        check("zip_sha256", sha, exp["zip_sha256"]),
        check("zip_size", size, exp["zip_size"]),
    ]
    member_results = {}
    csv_results = {}
    with zipfile.ZipFile(path, "r") as zf:
        files = [i for i in zf.infolist() if not i.is_dir()]
        checks.append(check("zip_member_count", len(files), exp["member_count"]))
        for basename, member_exp in exp["members"].items():
            info = find_member(zf, basename)
            observed = verify_member_hash(zf, info)
            member_results[basename] = observed
            checks.extend([
                check(f"{basename}:size", observed["size"], member_exp["size"]),
                check(f"{basename}:sha256", observed["sha256"], member_exp["sha256"]),
            ])
            if "rows" in member_exp:
                csv_observed = scan_csv_member(zf, info)
                csv_results[basename] = csv_observed
                checks.extend([
                    check(f"{basename}:rows", csv_observed["rows"], member_exp["rows"]),
                    check(f"{basename}:columns", csv_observed["columns"], member_exp["columns"]),
                    check(f"{basename}:row_width_mismatches", csv_observed["row_width_mismatches"], 0),
                ])

        base_header = csv_results["UNSW_IoTSAT.csv"]["header"]
        ccsds_header = csv_results["UNSW_IoTSAT_with_CCSDS_fields.csv"]["header"]
        checks.extend([
            check("excluded_base_fields_present_for_policy_application",
                  sorted(set(exp["excluded_base_fields"]) - set(base_header)), []),
            check("ccsds_label_conditioned_fields_present",
                  sorted(set(exp["ccsds_label_conditioned_fields"]) - set(ccsds_header)), []),
        ])
        json_info = find_member(zf, "UNSW_IoTSAT.json")
        json_last = last_nonwhitespace_byte(zf, json_info)
        checks.append(check("known_json_unterminated_boundary_preserved", json_last, "}"))

    return {
        "status": "PASS" if all(c["pass"] for c in checks) else "FAIL",
        "checks": checks,
        "artifact": {"size": size, "sha256": sha, "md5": md5},
        "members": member_results,
        "csv_schemas": csv_results,
        "canonical_artifact": "UNSW_IoTSAT.csv",
        "excluded_artifacts": exp["excluded_artifacts"],
        "excluded_base_fields": exp["excluded_base_fields"],
        "ccsds_label_conditioned_fields": exp["ccsds_label_conditioned_fields"],
        "ccsds_label_conditioned_evidence_role": "NOT_OPERATIONAL_NATIVE",
        "json_last_nonwhitespace_byte": json_last,
    }


def environment_report(label: str) -> dict:
    return {
        "label": label,
        "python": sys.version,
        "python_executable": sys.executable,
        "platform": platform.platform(),
        "machine": platform.machine(),
        "system": platform.system(),
        "release": platform.release(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cucd-zip", required=True, type=Path)
    parser.add_argument("--aegissat-csv", required=True, type=Path)
    parser.add_argument("--unsw-zip", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--environment-label", default="unspecified")
    args = parser.parse_args()

    inputs = [args.cucd_zip, args.aegissat_csv, args.unsw_zip]
    for item in inputs:
        if not item.is_file():
            raise SystemExit(f"Input file not found: {item}")

    args.output.mkdir(parents=True, exist_ok=True)
    validator_sha = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()

    try:
        datasets = {
            "CUCD_ID_V3": validate_cucd(args.cucd_zip),
            "AEGISSAT_2025": validate_aegissat(args.aegissat_csv),
            "UNSW_IOTSAT_2026": validate_unsw(args.unsw_zip),
        }
        overall = "PASS" if all(d["status"] == "PASS" for d in datasets.values()) else "FAIL"
    except (ValidationFailure, zipfile.BadZipFile, UnicodeError, csv.Error, OSError) as exc:
        print(f"VALIDATION ERROR: {exc}", file=sys.stderr)
        return 2

    core = {
        "schema": SCHEMA_VERSION,
        "study_id": STUDY_ID,
        "stage": "PRE_FREEZE_DATASET_REPRODUCIBILITY_VALIDATION",
        "overall_status": overall,
        "validator_sha256": validator_sha,
        "scope_boundary": {
            "dataset_bytes_modified": False,
            "semantic_mapping_performed": False,
            "recovery_selector_executed": False,
            "study9_endpoints_computed": False,
            "attack_labels_used_as_operational_state": False,
            "missing_state_imputed": False,
            "population_frozen_by_this_validator": False,
        },
        "datasets": datasets,
    }
    core_bytes = canonical_json_bytes(core)
    core_sha = sha256_bytes(core_bytes)
    (args.output / "validation_core.json").write_bytes(core_bytes)

    report = {
        "schema": SCHEMA_VERSION,
        "study_id": STUDY_ID,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "environment": environment_report(args.environment_label),
        "input_paths": {
            "cucd_zip": str(args.cucd_zip.resolve()),
            "aegissat_csv": str(args.aegissat_csv.resolve()),
            "unsw_zip": str(args.unsw_zip.resolve()),
        },
        "validation_core_sha256": core_sha,
        "overall_status": overall,
    }
    (args.output / "validation_report.json").write_bytes(canonical_json_bytes(report))

    print(f"Study 9 pre-freeze validation: {overall}")
    print(f"Deterministic core SHA-256: {core_sha}")
    for dataset_id, result in datasets.items():
        failed = [c["name"] for c in result["checks"] if not c["pass"]]
        print(f"  {dataset_id}: {result['status']}" + (f" failed={failed}" if failed else ""))
    return 0 if overall == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
