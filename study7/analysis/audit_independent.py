from __future__ import annotations

import csv
import json
import sys
from itertools import product
from pathlib import Path


def objective(base: tuple[int, ...], hidden: int | None = None) -> int:
    h = base[7] if hidden is None else hidden
    return int(all(base[:6]) and ((not base[6]) or bool(h)))


def train_l0() -> tuple[int, int, int, int]:
    training = []
    for auth in (0, 1):
        v = (1, 1, 1, 1, 1, 1, 0, auth)
        training.append((v, objective(v)))
    for auth in (0, 1):
        v = (1, 1, 1, 1, 1, 1, 1, auth)
        training.append((v, objective(v)))
    for i in range(6):
        v = [1, 1, 1, 1, 1, 1, 0, 1]
        v[i] = 0
        t = tuple(v)
        training.append((t, objective(t)))
    best = None
    for q in range(1, 5):
        for wa in range(5):
            for ws in range(-4, 1):
                for threshold in range(1, 31):
                    errors = sum(
                        int(int(q * sum(v[:6]) + wa * v[7] + ws * v[6] >= threshold) != y)
                        for v, y in training
                    )
                    candidate = (errors, abs(q) + abs(wa) + abs(ws), threshold, q, wa, ws)
                    if best is None or candidate < best:
                        best = candidate
    assert best is not None
    return best[3], best[4], best[5], best[2]


def train_l1() -> tuple[int, int, int, int, int]:
    training = []
    for auth in (0, 1):
        for corr in (0, 1):
            v = (1, 1, 1, 1, 1, 1, 0, auth, corr)
            training.append((v, objective(v[:8])))
    for auth in (0, 1):
        v = (1, 1, 1, 1, 1, 1, 1, auth, auth)
        training.append((v, objective(v[:8])))
    v = (1, 1, 1, 1, 1, 1, 1, 1, 0)
    training.append((v, objective(v[:8], hidden=0)))
    for i in range(6):
        v = [1, 1, 1, 1, 1, 1, 0, 1, 1]
        v[i] = 0
        t = tuple(v)
        training.append((t, objective(t[:8])))
    best = None
    for q in range(1, 5):
        for wa in range(5):
            for wc in range(5):
                for ws in range(-5, 1):
                    for threshold in range(1, 35):
                        errors = sum(
                            int(
                                int(
                                    q * sum(v[:6])
                                    + wa * v[7]
                                    + wc * v[8]
                                    + ws * v[6]
                                    >= threshold
                                ) != y
                            )
                            for v, y in training
                        )
                        candidate = (
                            errors,
                            abs(q) + abs(wa) + abs(wc) + abs(ws),
                            threshold,
                            q,
                            wa,
                            wc,
                            ws,
                        )
                        if best is None or candidate < best:
                            best = candidate
    assert best is not None
    return best[3], best[4], best[5], best[6], best[2]


def p0(base: tuple[int, ...]) -> int:
    return objective(base)


def pl0(base: tuple[int, ...], weights: tuple[int, int, int, int]) -> int:
    q, wa, ws, t = weights
    return int(q * sum(base[:6]) + wa * base[7] + ws * base[6] >= t)


def pl1(base: tuple[int, ...], corr: int, weights: tuple[int, int, int, int, int]) -> int:
    q, wa, wc, ws, t = weights
    return int(q * sum(base[:6]) + wa * base[7] + wc * corr + ws * base[6] >= t)


def main() -> None:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("study7_runtime")
    l0 = train_l0()
    l1 = train_l1()
    models = json.loads((root / "TRAINED_MODELS.json").read_text(encoding="utf-8"))
    assert l0 == (
        models["L0_ERM_VISIBLE_ONLY"]["quality_weight"],
        models["L0_ERM_VISIBLE_ONLY"]["authorization_weight"],
        models["L0_ERM_VISIBLE_ONLY"]["security_weight"],
        models["L0_ERM_VISIBLE_ONLY"]["threshold"],
    )
    assert l1 == (
        models["L1_ERM_WITH_INDEPENDENT_CORROBORATION"]["quality_weight"],
        models["L1_ERM_WITH_INDEPENDENT_CORROBORATION"]["authorization_weight"],
        models["L1_ERM_WITH_INDEPENDENT_CORROBORATION"]["corroboration_weight"],
        models["L1_ERM_WITH_INDEPENDENT_CORROBORATION"]["security_weight"],
        models["L1_ERM_WITH_INDEPENDENT_CORROBORATION"]["threshold"],
    )

    with (root / "observations.csv").open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    assert len(rows) == 1033
    mismatches = 0
    for row in rows:
        base = tuple(int(row[k]) for k in (
            "signature_valid", "source_trusted", "fresh", "epoch_valid",
            "noncontradictory", "minimum_evidence_complete", "security_signal", "authorization_available"
        ))
        hidden = int(row["hidden_authorization"])
        expected_objective = objective(base, hidden=hidden)
        if row["policy"] == "D0_S1_VISIBLE_ONLY":
            expected_decision = p0(base)
        elif row["policy"] == "L0_ERM_VISIBLE_ONLY":
            expected_decision = pl0(base, l0)
        else:
            corr = int(row["independent_corroboration"])
            expected_decision = pl1(base, corr, l1)
        expected_error = int(expected_decision != expected_objective)
        expected_unsafe = int(expected_decision == 1 and expected_objective == 0)
        expected_false = int(expected_decision == 0 and expected_objective == 1)
        actual = (
            int(row["objective_safe_to_proceed"]), int(row["decision_proceed"]),
            int(row["objective_decision_error"]), int(row["unsafe_proceed"]),
            int(row["false_conservative_hold"])
        )
        expected = (expected_objective, expected_decision, expected_error, expected_unsafe, expected_false)
        mismatches += int(actual != expected)
    report = json.loads((root / "REPORT.json").read_text(encoding="utf-8"))
    assert report["finite_population_observations"] == 1033
    assert report["block_a_visible_only_errors"] == 0
    assert report["block_b_corroboration_errors"] == 2
    assert report["block_b_corroboration_unsafe_proceed"] == 1
    assert report["block_b_corroboration_false_conservative"] == 1
    assert mismatches == 0
    print("study7_independent_audit=PASS")
    print(json.dumps({"observations": len(rows), "mismatches": mismatches, "l0": l0, "l1": l1}, sort_keys=True))


if __name__ == "__main__":
    main()
