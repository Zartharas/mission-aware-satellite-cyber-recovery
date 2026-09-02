from __future__ import annotations

import csv
import json
from itertools import combinations
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
PROTOCOL = json.loads((ROOT / "study6" / "STUDY6_PROTOCOL.json").read_text(encoding="utf-8"))
SIGNALS = tuple(PROTOCOL["assurance_signals"])
GATES = {key: tuple(value) for key, value in PROTOCOL["gates"].items()}
STATES = PROTOCOL["baseline_states"]


def b(value: str) -> bool:
    if value == "True":
        return True
    if value == "False":
        return False
    raise AssertionError(f"unexpected boolean {value!r}")


def expected_qualifies(values: dict[str, object], gate_id: str) -> bool:
    return all(bool(values[name]) for name in GATES[gate_id])


def main() -> None:
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "study6_runtime"
    mismatches = 0

    with (out / "gate_state_matrix.csv").open(encoding="utf-8", newline="") as handle:
        rows_a = list(csv.DictReader(handle))
    if len(rows_a) != 36:
        raise AssertionError(f"expected 36 block-A rows, got {len(rows_a)}")
    seen_a: set[tuple[str, str]] = set()
    for row in rows_a:
        key = (row["state_id"], row["gate_id"])
        if key in seen_a:
            mismatches += 1
            continue
        seen_a.add(key)
        values = STATES[row["state_id"]]
        expected = expected_qualifies(values, row["gate_id"])
        objective = bool(values["objective_baseline_correct"])
        if b(row["qualified"]) != expected:
            mismatches += 1
        if b(row["objective_baseline_correct"]) != objective:
            mismatches += 1
        if b(row["unsafe_qualified"]) != (expected and not objective):
            mismatches += 1
        if b(row["correct_rejected"]) != ((not expected) and objective):
            mismatches += 1

    with (out / "benign_unavailability.csv").open(encoding="utf-8", newline="") as handle:
        rows_b = list(csv.DictReader(handle))
    if len(rows_b) != 384:
        raise AssertionError(f"expected 384 block-B rows, got {len(rows_b)}")

    expected_subsets: set[tuple[str, ...]] = set()
    for size in range(len(SIGNALS) + 1):
        expected_subsets.update(combinations(SIGNALS, size))

    seen_b: set[tuple[str, str]] = set()
    for row in rows_b:
        missing = tuple() if row["missing_signals"] == "NONE" else tuple(row["missing_signals"].split("+"))
        if missing not in expected_subsets:
            mismatches += 1
        key = (row["missing_signals"], row["gate_id"])
        if key in seen_b:
            mismatches += 1
            continue
        seen_b.add(key)
        values: dict[str, object] = {name: True for name in SIGNALS}
        for name in missing:
            values[name] = False
        expected = expected_qualifies(values, row["gate_id"])
        if int(row["missing_count"]) != len(missing):
            mismatches += 1
        if b(row["qualified"]) != expected:
            mismatches += 1
        if b(row["objective_baseline_correct"]) is not True:
            mismatches += 1
        if b(row["benign_availability_loss"]) != (not expected):
            mismatches += 1

    report = json.loads((out / "REPORT.json").read_text(encoding="utf-8"))
    if report["finite_population_observations"] != 420:
        mismatches += 1
    if report["objective_correctness_oracle_is_gate_input"] is not False:
        mismatches += 1
    if report["malware_or_exploit_implemented"] is not False:
        mismatches += 1

    if mismatches:
        raise SystemExit(f"study6_independent_audit=FAIL mismatches={mismatches}")
    print("study6_independent_audit=PASS")
    print(json.dumps({"experiment_id": "S6-SCTR-001", "mismatches": 0, "block_a": 36, "block_b": 384, "total": 420}, sort_keys=True))


if __name__ == "__main__":
    main()
