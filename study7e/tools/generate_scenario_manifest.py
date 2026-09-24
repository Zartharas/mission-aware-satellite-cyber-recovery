#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from study7e.src.aerc_design import affected_paths, build_scenario_manifest, domain_map, manifest_counts


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
                "primary_source_domain",
                "primary_key_domain",
                "primary_execution_domain",
                "primary_transport_domain",
                "primary_authority_domain",
                "corr_source_domain",
                "corr_key_domain",
                "corr_execution_domain",
                "corr_transport_domain",
                "corr_authority_domain",
                "expected_affected_paths",
            ]
        )
        for row in rows:
            aliases = domain_map(row.topology)
            expected_paths = ",".join(sorted(affected_paths(row.topology, row.fault_profile)))
            writer.writerow(
                [
                    row.scenario_id,
                    row.block,
                    row.true_authorization,
                    row.true_health_ready,
                    row.security_signal,
                    row.topology,
                    row.fault_profile,
                    aliases["primary"]["source"],
                    aliases["primary"]["key"],
                    aliases["primary"]["execution"],
                    aliases["primary"]["transport"],
                    aliases["primary"]["authority"],
                    aliases["corroborator"]["source"],
                    aliases["corroborator"]["key"],
                    aliases["corroborator"]["execution"],
                    aliases["corroborator"]["transport"],
                    aliases["corroborator"]["authority"],
                    expected_paths,
                ]
            )

    print(f"wrote_design_manifest={args.output}")
    print(f"rows={counts['TOTAL']}")
    print("scientific_results_generated=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
