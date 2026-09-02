from __future__ import annotations

import csv
import json
import sys
from collections import Counter, defaultdict
from dataclasses import asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "study7" / "src"))

from learned_selector_model import evaluation_rows, train_visible_only, train_with_corroboration


def _write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError("rows required")
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("study7_runtime")
    out.mkdir(parents=True, exist_ok=True)
    rows = evaluation_rows()
    if len(rows) != 1033:
        raise SystemExit(f"unexpected population: {len(rows)}")
    _write_csv(out / "observations.csv", rows)

    l0 = train_visible_only()
    l1 = train_with_corroboration()
    models = {
        "schema": 1,
        "experiment_id": "S7-LSO-001",
        "L0_ERM_VISIBLE_ONLY": asdict(l0),
        "L1_ERM_WITH_INDEPENDENT_CORROBORATION": asdict(l1),
    }
    (out / "TRAINED_MODELS.json").write_text(
        json.dumps(models, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    grouped: dict[tuple[str, str], Counter[str]] = defaultdict(Counter)
    for row in rows:
        key = (str(row["block"]), str(row["policy"]))
        grouped[key]["observations"] += 1
        grouped[key]["errors"] += int(row["objective_decision_error"])
        grouped[key]["unsafe_proceed"] += int(row["unsafe_proceed"])
        grouped[key]["false_conservative_hold"] += int(row["false_conservative_hold"])
        grouped[key]["proceed"] += int(row["decision_proceed"])

    summary_rows: list[dict[str, object]] = []
    for (block, policy), counts in sorted(grouped.items()):
        summary_rows.append(
            {
                "block": block,
                "policy": policy,
                "observations": counts["observations"],
                "objective_decision_errors": counts["errors"],
                "unsafe_proceed": counts["unsafe_proceed"],
                "false_conservative_hold": counts["false_conservative_hold"],
                "proceed_decisions": counts["proceed"],
            }
        )
    _write_csv(out / "policy_summary.csv", summary_rows)

    block_c = [row for row in rows if row["block"] == "C_HIDDEN_TRUTH_COLLISION"]
    collision = {
        (str(row["scenario"]), str(row["policy"])): row for row in block_c
    }
    report = {
        "schema": 1,
        "experiment_id": "S7-LSO-001",
        "status": "COMPLETE",
        "finite_population_observations": len(rows),
        "block_a_observations": sum(r["block"] == "A_VISIBLE_LATTICE" for r in rows),
        "block_b_observations": sum(r["block"] == "B_CORROBORATION_LATTICE" for r in rows),
        "block_c_observations": len(block_c),
        "visible_only_training_errors": l0.training_errors,
        "corroboration_training_errors": l1.training_errors,
        "block_a_visible_only_errors": sum(
            int(r["objective_decision_error"])
            for r in rows
            if r["block"] == "A_VISIBLE_LATTICE"
        ),
        "block_b_corroboration_errors": sum(
            int(r["objective_decision_error"])
            for r in rows
            if r["block"] == "B_CORROBORATION_LATTICE"
        ),
        "block_b_corroboration_unsafe_proceed": sum(
            int(r["unsafe_proceed"])
            for r in rows
            if r["block"] == "B_CORROBORATION_LATTICE"
        ),
        "block_b_corroboration_false_conservative": sum(
            int(r["false_conservative_hold"])
            for r in rows
            if r["block"] == "B_CORROBORATION_LATTICE"
        ),
        "v5_independent_disagreement": {
            policy: {
                "decision_proceed": int(collision[("V5_INDEPENDENT_DISAGREEMENT", policy)]["decision_proceed"]),
                "unsafe_proceed": int(collision[("V5_INDEPENDENT_DISAGREEMENT", policy)]["unsafe_proceed"]),
            }
            for policy in (
                "D0_S1_VISIBLE_ONLY",
                "L0_ERM_VISIBLE_ONLY",
                "L1_ERM_WITH_INDEPENDENT_CORROBORATION",
            )
        },
        "v5_correlated_false_corroboration": {
            policy: {
                "decision_proceed": int(collision[("V5_CORRELATED_FALSE_CORROBORATION", policy)]["decision_proceed"]),
                "unsafe_proceed": int(collision[("V5_CORRELATED_FALSE_CORROBORATION", policy)]["unsafe_proceed"]),
            }
            for policy in (
                "D0_S1_VISIBLE_ONLY",
                "L0_ERM_VISIBLE_ONLY",
                "L1_ERM_WITH_INDEPENDENT_CORROBORATION",
            )
        },
        "hidden_objective_authorization_is_policy_input": False,
        "attack_optimizer_implemented": False,
        "reinforcement_learning_implemented": False,
        "global_model_ranking_claimed": False,
        "current_computers_and_security_manuscript_modified": False,
    }
    (out / "REPORT.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
