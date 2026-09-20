#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from itertools import product
from pathlib import Path

from study8.src.contact_recovery_model import DISRUPTIONS, POLICIES, PROFILE_OBJECTS
from study8e.audit.independent_external_reference import independent_evaluate
from study8e.src.external_contact_recovery_model import ExternalCase, evaluate_case

FIXTURES = (
    {
        "id": "SYNTH_CONTIGUOUS_LONG",
        "windows": ((0, 30),),
        "horizon_s": 30,
        "rate_bps": 10_000,
    },
    {
        "id": "SYNTH_TWO_WINDOWS",
        "windows": ((0, 10), (20, 40)),
        "horizon_s": 40,
        "rate_bps": 10_000,
    },
    {
        "id": "SYNTH_CLUSTERED",
        "windows": ((0, 4), (5, 9), (20, 27), (28, 36)),
        "horizon_s": 36,
        "rate_bps": 12_000,
    },
)


def stable_json_bytes(value: object) -> bytes:
    return (
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False)
        + "\n"
    ).encode("utf-8")


def normalize_for_json(value: object) -> object:
    if isinstance(value, Fraction):
        return {
            "numerator": value.numerator,
            "denominator": value.denominator,
        }
    if isinstance(value, dict):
        return {
            str(k): normalize_for_json(v)
            for k, v in value.items()
        }
    if isinstance(value, (list, tuple)):
        return [normalize_for_json(v) for v in value]
    return value


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)

    comparisons = 0
    mismatches: list[dict[str, object]] = []

    for profile, policy, disruption, fixture in product(
        PROFILE_OBJECTS,
        POLICIES,
        DISRUPTIONS,
        FIXTURES,
    ):
        main_result = evaluate_case(
            ExternalCase(
                profile=profile,
                policy=policy,
                disruption=disruption,
                horizon_s=Fraction(int(fixture["horizon_s"])),
                rate_bps=int(fixture["rate_bps"]),
            ),
            fixture["windows"],
        )
        independent_result = independent_evaluate(
            profile=profile,
            policy=policy,
            disruption=disruption,
            horizon_s=int(fixture["horizon_s"]),
            rate_bps=int(fixture["rate_bps"]),
            windows=fixture["windows"],
        )
        comparisons += 1
        if main_result != independent_result:
            mismatch_keys = sorted(
                key
                for key in set(main_result) | set(independent_result)
                if main_result.get(key) != independent_result.get(key)
            )
            mismatches.append(
                {
                    "profile": profile,
                    "policy": policy,
                    "disruption": disruption,
                    "fixture": fixture["id"],
                    "mismatch_keys": mismatch_keys,
                    "main": normalize_for_json(main_result),
                    "independent": normalize_for_json(independent_result),
                }
            )

    report = {
        "schema": 1,
        "experiment_id": "S8E-ECTV-001",
        "audit_id": "S8E-SYNTH-AUDIT-001",
        "status": "PASS" if not mismatches else "FAIL",
        "scope": "SYNTHETIC_FIXTURES_ONLY",
        "fixture_count": len(FIXTURES),
        "profiles": len(PROFILE_OBJECTS),
        "policies": len(POLICIES),
        "disruptions": len(DISRUPTIONS),
        "comparisons": comparisons,
        "mismatch_count": len(mismatches),
        "mismatches": mismatches,
        "fixture_contract": normalize_for_json(FIXTURES),
        "real_satnogs_trace_loaded": False,
        "real_trace_endpoint_computed": False,
        "study8_modified": False,
    }
    encoded = stable_json_bytes(report)
    args.output.write_bytes(encoded)
    print(f"synthetic_comparisons={comparisons}")
    print(f"synthetic_mismatches={len(mismatches)}")
    print(f"audit_report_sha256={hashlib.sha256(encoded).hexdigest()}")
    return 0 if not mismatches else 1


if __name__ == "__main__":
    raise SystemExit(main())
