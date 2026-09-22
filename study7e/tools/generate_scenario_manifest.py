#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from study7e.src.aerc_design import build_scenario_manifest, manifest_counts


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate the prospective Study-7E scenario manifest. This produces design inputs, not scientific results."
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    rows = build_scenario_manifest()
    counts = manifest_counts(rows)
    if counts["TOTAL"] != 280:
        raise SystemExit(f"unexpected manifest cardinality: {counts}")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(
            [
                "scenario_id",
                "block",
                "true_authorization",
                "true_health_ready",
                "security_signal",
                "topology",
                "fault_profile",
            ]
        )
        for row in rows:
            writer.writerow(
                [
                    row.scenario_id,
                    row.block,
                    row.true_authorization,
                    row.true_health_ready,
                    row.security_signal,
                    row.topology,
                    row.fault_profile,
                ]
            )

    print(f"wrote_design_manifest={args.output}")
    print(f"rows={counts['TOTAL']}")
    print("scientific_results_generated=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
