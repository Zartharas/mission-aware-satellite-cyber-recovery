#!/usr/bin/env python3
"""Read-only verification of Paper-2 Phase-1 analytical derivations.

This script reads frozen Study-3/4/6 protocol/result projections only.
It does not execute a scientific campaign and writes no scientific output.
"""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def verify_study3() -> None:
    protocol = json.loads((ROOT / "study3/STUDY3_PROTOCOL.json").read_text())
    rows = load_csv(ROOT / "study3/results/canonical/cell_summary.csv")
    by_id = {row["cell_id"]: row for row in rows}

    assert protocol["evidence_valid_for_seconds"] == 5

    v0 = by_id["K4_V0_NONE_S2_B0_FAIL_CLOSED"]
    assert int(v0["trajectories_with_any_unsafe_qualification"]) == 3
    expected = 3 * 5 / 46
    assert abs(float(v0["mean_unsafe_qualified_exposure_s"]) - expected) < 1e-12

    for policy in ("S2_B0_FAIL_CLOSED", "S2_S1_EVIDENCE_AWARE"):
        row = by_id[f"K4_V5_PERSISTENT_{policy}"]
        assert int(row["trajectories_with_any_unsafe_qualification"]) == 46
        assert int(row["trajectories_with_v5_affected_unsafe_qualification"]) == 46

    b2 = by_id["K4_V5_PERSISTENT_S2_B2_RISK_THRESHOLD"]
    assert int(b2["trajectories_with_any_unsafe_qualification"]) == 0


def verify_study4() -> None:
    protocol = json.loads((ROOT / "study4/STUDY4_PROTOCOL.json").read_text())
    rows = load_csv(ROOT / "study4/results/canonical/thresholds.csv")
    n = int(protocol["producer_count"])
    sizes = sorted((len(v) for v in protocol["provenance_domains"].values()), reverse=True)

    def largest_capacity(k: int) -> int:
        return sum(sizes[:k]) if k > 0 else 0

    mismatches: list[str] = []
    for row in rows:
        match = re.fullmatch(r"Q(\d+)_D(\d+)", row["rule_id"])
        assert match
        q, d = map(int, match.groups())
        if row["block"] == "SAFETY":
            first = q
            systematic = max(q, largest_capacity(d - 1) + 1)
        else:
            first = min(n - q + 1, n - largest_capacity(d - 1))
            systematic = n - q + 1
        if (int(row["first_failure_count"]), int(row["systematic_failure_count"])) != (
            first,
            systematic,
        ):
            mismatches.append(f'{row["rule_id"]}:{row["block"]}')

    assert len(rows) == 36
    assert not mismatches, mismatches


def verify_study6() -> None:
    protocol = json.loads((ROOT / "study6/STUDY6_PROTOCOL.json").read_text())
    rows = load_csv(ROOT / "study6/results/CANONICAL_GATE_SUMMARY.csv")
    states = protocol["baseline_states"]
    signals = protocol["assurance_signals"]

    clean = states["CLEAN_APPROVED"]
    bad = states["APPROVED_BAD_SOURCE"]

    assert clean["objective_baseline_correct"] is True
    assert bad["objective_baseline_correct"] is False
    assert all(clean[s] == bad[s] is True for s in signals)

    for row in rows:
        required = int(row["required_signal_count"])
        expected_loss = 2 ** len(signals) - 2 ** (len(signals) - required)
        assert int(row["benign_loss_subset_count"]) == expected_loss
        assert "APPROVED_BAD_SOURCE" in row["unsafe_qualified_states"].split(";")


def main() -> int:
    verify_study3()
    verify_study4()
    verify_study6()
    print("paper2_phase1_theory_verification=PASS")
    print("study3_temporal_derivation=PASS")
    print("study4_closed_form_thresholds=PASS_36_OF_36")
    print("study6_observability_and_benign_loss=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
