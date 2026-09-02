from __future__ import annotations

import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

PRODUCERS = ("P1", "P2", "P3", "P4", "P5", "P6", "P7")
DOMAIN = {"P1":"D1","P2":"D1","P3":"D1","P4":"D2","P5":"D2","P6":"D3","P7":"D3"}


def as_bool(value: str) -> bool:
    if value == "True":
        return True
    if value == "False":
        return False
    raise ValueError(value)


def load(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else "study4_runtime")
    rows = load(root / "observations.csv")
    thresholds = load(root / "thresholds.csv")
    report = json.loads((root / "REPORT.json").read_text(encoding="utf-8"))
    errors: list[str] = []
    if len(rows) != 4608:
        errors.append(f"observation_count={len(rows)}")
    if len(thresholds) != 36:
        errors.append(f"threshold_count={len(thresholds)}")
    if report.get("observations") != 4608 or report.get("rules") != 18:
        errors.append("report_membership")

    grouped: dict[tuple[str, str, int], list[bool]] = defaultdict(list)
    for row in rows:
        members = tuple(filter(None, row["affected_members"].split(";")))
        affected = set(members)
        q_total = int(row["q_total"])
        q_domains = int(row["q_domains"])
        block = row["block"]
        if block == "SAFETY":
            true_voters = affected
        elif block == "AVAILABILITY":
            true_voters = set(PRODUCERS) - affected
        else:
            errors.append(f"bad_block:{block}")
            continue
        true_votes = len(true_voters)
        true_domains = len({DOMAIN[p] for p in true_voters})
        qualified = true_votes >= q_total and true_domains >= q_domains
        if int(row["true_votes"]) != true_votes:
            errors.append("true_votes")
        if int(row["true_vote_domains"]) != true_domains:
            errors.append("true_domains")
        if as_bool(row["qualified"]) != qualified:
            errors.append("qualified")
        unsafe = qualified if block == "SAFETY" else False
        false_conservative = (not qualified) if block == "AVAILABILITY" else False
        if as_bool(row["unsafe_qualified"]) != unsafe:
            errors.append("unsafe")
        if as_bool(row["false_conservative"]) != false_conservative:
            errors.append("false_conservative")
        grouped[(row["rule_id"], block, int(row["affected_count"]))].append(unsafe if block == "SAFETY" else false_conservative)

    expected_thresholds = {}
    curves: dict[tuple[str, str], dict[int, float]] = defaultdict(dict)
    for (rule, block, k), flags in grouped.items():
        curves[(rule, block)][k] = sum(flags) / len(flags)
    for key, curve in curves.items():
        first = next((k for k in sorted(curve) if curve[k] > 0), None)
        systematic = next((k for k in sorted(curve) if curve[k] == 1.0), None)
        expected_thresholds[key] = (first, systematic)
    for row in thresholds:
        key = (row["rule_id"], row["block"])
        first, systematic = expected_thresholds[key]
        if int(row["first_failure_count"]) != first or int(row["systematic_failure_count"]) != systematic:
            errors.append(f"threshold:{key}")

    if errors:
        raise SystemExit(f"study4_independent_audit=FAIL errors={len(errors)} preview={errors[:20]}")
    print("study4_independent_audit=PASS")
    print("study4_observation_mismatches=0")
    print("study4_threshold_mismatches=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
