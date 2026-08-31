#!/usr/bin/env python3
"""Post-publication reproduction implementation for the frozen WP10 analysis.

This is not the original WP10 analysis source. The original executable analysis
code was not preserved. This module reconstructs the documented statistical
procedure from the frozen 720-row analysis extraction and the locked 240-row P4
analysis table, then validates the reproduced quantities against preserved,
cryptographically verified WP10 outputs.

The implementation is analysis-only. It does not read or modify the raw WP9
campaign, run NOS3/cFS, consume campaign seeds, or change the statistical
population.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import sys
import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable

import numpy as np
import pandas as pd
from scipy.stats import beta, rankdata
import statsmodels.api as sm

LOCKED_SHA256 = "bf219d71162df708343f4be85bb258a083f5012e696c23619d0a46b7a2f2f265"
P4_LOCKED_SHA256 = "f848a448cc75818d37a7827df9e8936ff7a4bf60075ca25b102e858df7f56af3"
ANALYSIS_MEMBERSHIP_SHA256 = "a2bf0c8f352f4386e74a500d97ea8f73e0c39d03bfe10ac0ebcf02470af9f70e"
C1_BOOTSTRAP_SEED = 13772462244504663816
C2_BOOTSTRAP_SEED = 7873538898909399172
BOOTSTRAP_REPLICATES = 20_000
TAU_S = 30.0
FINAL_COMMIT_COMPLETE_SEEDS = tuple(range(10002, 10031))

# The original P5 bootstrap RNG seed was not preserved in the authoritative
# outputs. This reconstruction seed is deterministically derived from the locked
# input identity and a public namespace. It is used only for an independent
# classification-stability check; original P5 point estimates and reference CIs
# remain the historical authority.
P5_RECONSTRUCTION_NAMESPACE = b"post-publication-wp10-p5-bootstrap-v1|"
P5_RECONSTRUCTION_SEED = int.from_bytes(
    hashlib.sha256(P5_RECONSTRUCTION_NAMESPACE + LOCKED_SHA256.encode("ascii")).digest()[:8],
    "big",
)

P5_GROUPS = {
    "G01": ["A01", "A02"],
    "G02": ["A03", "A04", "A07"],
    "G03": ["A05", "A06"],
    "G04": ["A08", "A09"],
    "G05": ["A10", "A11", "A14", "A16"],
    "G06": ["A12", "A13", "A15"],
    "G07": ["A17", "A18"],
    "G08": ["A19", "A20", "A21"],
    "G09": ["A22", "A23", "A24"],
}
P7_CELL_BY_GROUP = {
    "G01": "A02", "G02": "A04", "G03": "A06", "G04": "A09",
    "G05": "A11", "G06": "A13", "G07": "A18", "G08": "A21",
    "G09": "A24",
}


def sha256_file(file: Path) -> str:
    h = hashlib.sha256()
    with file.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def read_tsv(file: Path) -> pd.DataFrame:
    return pd.read_csv(file, sep="\t")


def cp_interval(successes: int, n: int, alpha: float = 0.05) -> tuple[float, float]:
    if not (0 <= successes <= n and n > 0):
        raise ValueError((successes, n))
    low = 0.0 if successes == 0 else float(beta.ppf(alpha / 2, successes, n - successes + 1))
    high = 1.0 if successes == n else float(beta.ppf(1 - alpha / 2, successes + 1, n - successes))
    return low, high


def zero_event_one_sided_upper(n: int, alpha: float = 0.05) -> float:
    return 1.0 - alpha ** (1.0 / n)


def bootstrap_indices(seed: int, n: int = 30, reps: int = BOOTSTRAP_REPLICATES) -> np.ndarray:
    rng = random.Random(seed)
    return np.fromiter(
        (rng.randrange(n) for _ in range(reps * n)),
        dtype=np.int16,
        count=reps * n,
    ).reshape(reps, n)


def percentile95(values: np.ndarray) -> tuple[float, float]:
    q = np.quantile(values, [0.025, 0.975])
    return float(q[0]), float(q[1])


def mean_bootstrap_ci(values: np.ndarray, indices: np.ndarray) -> tuple[float, float]:
    return percentile95(values[indices].mean(axis=1))


def paired_cell_array(df: pd.DataFrame, cell_id: str, column: str) -> np.ndarray:
    out = (
        df.loc[df.cell_id == cell_id, ["campaign_seed", column]]
        .sort_values("campaign_seed")[column]
        .to_numpy(dtype=float)
    )
    if len(out) != 30:
        raise AssertionError(f"{cell_id}:{column}: expected 30, got {len(out)}")
    return out


def sign(x: float, eps: float = 1e-12) -> int:
    return 1 if x > eps else -1 if x < -eps else 0


def assert_close(actual: float, expected: float, tol: float, label: str) -> None:
    if not math.isclose(float(actual), float(expected), rel_tol=tol, abs_tol=tol):
        raise AssertionError(f"{label}: actual={actual!r} expected={expected!r} tol={tol}")


def validate_locked_input(df: pd.DataFrame, locked_file: Path) -> None:
    if sha256_file(locked_file) != LOCKED_SHA256:
        raise AssertionError("locked 720-row extraction SHA-256 mismatch")
    if len(df) != 720:
        raise AssertionError(f"expected 720 rows, found {len(df)}")
    if df.cell_id.nunique() != 24 or not (df.groupby("cell_id").size() == 30).all():
        raise AssertionError("24 cells x 30 seed repetitions invariant failed")
    if set(df.campaign_seed) != set(range(10001, 10031)):
        raise AssertionError("campaign seed set mismatch")
    if int(df.M05_verified_recovery_event.sum()) != 180:
        raise AssertionError("M05 observed-event count mismatch")
    if int((df.M05_verified_recovery_event == 0).sum()) != 540:
        raise AssertionError("M05 censoring count mismatch")
    censored_times = df.loc[df.M05_verified_recovery_event == 0, "M05_verified_recovery_analysis_time_s"]
    if not np.allclose(censored_times, TAU_S):
        raise AssertionError("M05 administrative censoring horizon mismatch")
    if int((df.M03_safety_invariant_violation_count != 0).sum()) != 0:
        raise AssertionError("M03 structural-zero invariant mismatch")


def reproduce_c1(df: pd.DataFrame) -> dict:
    idx = bootstrap_indices(C1_BOOTSTRAP_SEED)
    results: list[dict] = []
    mappings = [
        ("M04_containment_RMST", "M04_containment_analysis_time_s"),
        ("M05_verified_recovery_RMST", "M05_verified_recovery_analysis_time_s"),
    ]
    for endpoint, col in mappings:
        p6 = paired_cell_array(df, "A17", col) - paired_cell_array(df, "A16", col)
        p7 = paired_cell_array(df, "A18", col) - paired_cell_array(df, "A11", col)
        interaction = p6 - p7
        for contrast, vector in [
            ("P6_C1_minus_C0", p6),
            ("P7_C1_minus_C0", p7),
            ("contact_by_policy_interaction", interaction),
        ]:
            low, high = mean_bootstrap_ci(vector, idx)
            results.append({
                "endpoint": endpoint,
                "contrast": contrast,
                "estimate_seconds": float(vector.mean()),
                "bootstrap95_low": low,
                "bootstrap95_high": high,
            })

    # P1 predeclared primary contrasts are all structural zeros in the frozen data.
    p1_rows = df[df.P1_block].copy()
    p1_checks = {}
    p1_cols = {
        "M01": p1_rows.M01_unauthorized_effect_completed.astype(float),
        "M02": p1_rows.M02_mission_objective_completion_ratio.astype(float),
        "M03": p1_rows.M03_safety_invariant_violation_count.astype(float),
        "M06": p1_rows.M06_legitimate_command_rejection_rate.astype(float),
    }
    for label, series in p1_cols.items():
        p1_checks[label] = int(series.nunique()) == 1

    terminal_cells = {
        "P2": {"P6_C0": "A16", "P6_C1": "A17", "P7_C0": "A11", "P7_C1": "A18"},
        "P3": {"P5_T0": "A14", "P5_T1": "A15", "P7_T0": "A11", "P7_T1": "A13"},
    }
    terminal = []
    for proposition, cells in terminal_cells.items():
        for label, cell in cells.items():
            sub = df[df.cell_id == cell]
            trusted = int((sub.terminal_state == "TRUSTED_RECOVERY_CONFIRMED").sum())
            low, high = cp_interval(trusted, len(sub))
            terminal.append({
                "proposition": proposition, "cell_label": label, "cell_id": cell,
                "trusted": trusted, "n": len(sub), "trusted_rate": trusted / len(sub),
                "exact95_low": low, "exact95_high": high,
            })

    p3_discordance = []
    for label, cell in {"P5_T0": "A14", "P5_T1": "A15", "P7_T0": "A11", "P7_T1": "A13"}.items():
        sub = df[df.cell_id == cell]
        trusted = int((sub.terminal_state == "TRUSTED_RECOVERY_CONFIRMED").sum())
        unverified = int((sub.terminal_state == "OPERATIONAL_BUT_UNVERIFIED").sum())
        restored = trusted + unverified
        p3_discordance.append({
            "cell_label": label, "cell_id": cell, "behaviorally_restored": restored,
            "trusted_recovery": trusted, "operational_but_unverified": unverified,
            "restored_but_unverified_fraction": (unverified / restored) if restored else None,
        })

    return {
        "rmst": results,
        "p1_structural_primary": p1_checks,
        "terminal_exact": terminal,
        "m03_one_sided95_upper": zero_event_one_sided_upper(30),
        "p3_trusted_recovery": {
            "P5_T1_minus_T0": 0.0,
            "P7_T1_minus_T0": -1.0,
            "evidence_by_policy_interaction": 1.0,
        },
        "p3_verification_discordance": p3_discordance,
    }


@dataclass
class MixedFit:
    proposition: str
    terms: list[str]
    params: np.ndarray
    cov: np.ndarray
    bse: np.ndarray
    optimizer: str
    random_intercept_variance: float
    residual_variance: float


def fit_mixed_model(df: pd.DataFrame, proposition: str) -> MixedFit:
    if proposition == "P2":
        cells = ["A16", "A17", "A11", "A18"]
        sub = df[df.cell_id.isin(cells)].copy().sort_values(["campaign_seed", "cell_id"])
        p = (sub.requested_policy_id == "P6").astype(float).to_numpy()
        c = (sub.contact_condition_id == "C1").astype(float).to_numpy()
        terms = ["Intercept", "P6", "C1", "P6_x_C1"]
    elif proposition == "P3":
        cells = ["A14", "A15", "A11", "A13"]
        sub = df[df.cell_id.isin(cells)].copy().sort_values(["campaign_seed", "cell_id"])
        p = (sub.requested_policy_id == "P5").astype(float).to_numpy()
        c = (sub.evidence_condition_id == "T1").astype(float).to_numpy()
        terms = ["Intercept", "P5", "T1", "P5_x_T1"]
    else:
        raise ValueError(proposition)
    exog = np.column_stack([np.ones(len(sub)), p, c, p * c])
    endog = sub.M07_ground_spacecraft_state_divergence_s.to_numpy(dtype=float)
    groups = sub.campaign_seed.to_numpy()
    model = sm.MixedLM(endog, exog, groups=groups)
    result = None
    selected = None
    errors = []
    for optimizer in ["lbfgs", "bfgs", "cg", "powell", "nm"]:
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                candidate = model.fit(reml=True, method=optimizer, disp=False)
            if bool(candidate.converged):
                result = candidate
                selected = optimizer
                break
            errors.append(f"{optimizer}:not-converged")
        except Exception as exc:  # preserved optimizer fallback behavior
            errors.append(f"{optimizer}:{type(exc).__name__}:{exc}")
    if result is None or selected is None:
        raise RuntimeError("mixed model failed: " + "; ".join(errors))
    k = len(terms)
    cov = np.asarray(result.cov_params())[:k, :k]
    params = np.asarray(result.fe_params, dtype=float)
    bse = np.sqrt(np.diag(cov))
    return MixedFit(
        proposition=proposition,
        terms=terms,
        params=params,
        cov=cov,
        bse=bse,
        optimizer=selected,
        random_intercept_variance=float(np.asarray(result.cov_re)[0, 0]),
        residual_variance=float(result.scale),
    )


def linear_contrast(fit: MixedFit, weights: Iterable[float]) -> tuple[float, float, float, float]:
    w = np.asarray(list(weights), dtype=float)
    estimate = float(w @ fit.params)
    se = float(np.sqrt(w @ fit.cov @ w))
    z = 1.959963984540054
    return estimate, se, estimate - z * se, estimate + z * se


def proposition_arrays(df: pd.DataFrame, proposition: str, column: str) -> dict[str, np.ndarray]:
    if proposition == "P2":
        mapping = {"P6_C0": "A16", "P6_C1": "A17", "P7_C0": "A11", "P7_C1": "A18"}
    elif proposition == "P3":
        mapping = {"P5_T0": "A14", "P5_T1": "A15", "P7_T0": "A11", "P7_T1": "A13"}
    else:
        raise ValueError(proposition)
    return {label: paired_cell_array(df, cell, column) for label, cell in mapping.items()}


def contrast_vectors(arrays: dict[str, np.ndarray], proposition: str) -> list[tuple[str, np.ndarray]]:
    if proposition == "P2":
        p6 = arrays["P6_C1"] - arrays["P6_C0"]
        p7 = arrays["P7_C1"] - arrays["P7_C0"]
        return [
            ("P6_C1_minus_C0", p6),
            ("P7_C1_minus_C0", p7),
            ("contact_by_policy_interaction", p6 - p7),
        ]
    p5 = arrays["P5_T1"] - arrays["P5_T0"]
    p7 = arrays["P7_T1"] - arrays["P7_T0"]
    return [
        ("P5_T1_minus_T0", p5),
        ("P7_T1_minus_T0", p7),
        ("evidence_by_policy_interaction", p5 - p7),
    ]


def rank_transformed_arrays(df: pd.DataFrame, proposition: str) -> dict[str, np.ndarray]:
    arrays = proposition_arrays(df, proposition, "M07_ground_spacecraft_state_divergence_s")
    labels = list(arrays)
    stacked = np.concatenate([arrays[label] for label in labels])
    transformed = (rankdata(stacked, method="average") - 1.0) / (len(stacked) - 1.0)
    return {
        label: transformed[i * 30:(i + 1) * 30]
        for i, label in enumerate(labels)
    }


def quantile_bootstrap_contrasts(
    arrays: dict[str, np.ndarray], proposition: str, q: float, indices: np.ndarray
) -> list[tuple[str, float, float, float]]:
    boot_quantiles = {label: np.quantile(values[indices], q, axis=1) for label, values in arrays.items()}
    point_quantiles = {label: float(np.quantile(values, q)) for label, values in arrays.items()}
    if proposition == "P2":
        point = [
            ("P6_C1_minus_C0", point_quantiles["P6_C1"] - point_quantiles["P6_C0"]),
            ("P7_C1_minus_C0", point_quantiles["P7_C1"] - point_quantiles["P7_C0"]),
        ]
        boot = [
            boot_quantiles["P6_C1"] - boot_quantiles["P6_C0"],
            boot_quantiles["P7_C1"] - boot_quantiles["P7_C0"],
        ]
        point.append(("contact_by_policy_interaction", point[0][1] - point[1][1]))
        boot.append(boot[0] - boot[1])
    else:
        point = [
            ("P5_T1_minus_T0", point_quantiles["P5_T1"] - point_quantiles["P5_T0"]),
            ("P7_T1_minus_T0", point_quantiles["P7_T1"] - point_quantiles["P7_T0"]),
        ]
        boot = [
            boot_quantiles["P5_T1"] - boot_quantiles["P5_T0"],
            boot_quantiles["P7_T1"] - boot_quantiles["P7_T0"],
        ]
        point.append(("evidence_by_policy_interaction", point[0][1] - point[1][1]))
        boot.append(boot[0] - boot[1])
    out = []
    for (name, estimate), values in zip(point, boot):
        low, high = percentile95(values)
        out.append((name, estimate, low, high))
    return out


def reproduce_c2(df: pd.DataFrame) -> dict:
    idx = bootstrap_indices(C2_BOOTSTRAP_SEED)
    fixed_effects = []
    model_contrasts = []
    raw_bootstrap = []
    rank_sensitivity = []
    quantile_sensitivity = []
    mixed_estimate_by_key = {}
    raw_estimate_by_key = {}
    rank_estimate_by_key = {}
    median_estimate_by_key = {}

    for proposition in ["P2", "P3"]:
        fit = fit_mixed_model(df, proposition)
        z = 1.959963984540054
        for term, est, se in zip(fit.terms, fit.params, fit.bse):
            fixed_effects.append({
                "proposition": proposition, "term": term, "estimate": float(est),
                "standard_error": float(se), "wald95_low": float(est - z * se),
                "wald95_high": float(est + z * se), "optimizer": fit.optimizer,
            })
        if proposition == "P2":
            contrast_specs = [
                ("P6_C1_minus_C0", [0, 0, 1, 1]),
                ("P7_C1_minus_C0", [0, 0, 1, 0]),
                ("contact_by_policy_interaction", [0, 0, 0, 1]),
            ]
        else:
            contrast_specs = [
                ("P5_T1_minus_T0", [0, 0, 1, 1]),
                ("P7_T1_minus_T0", [0, 0, 1, 0]),
                ("evidence_by_policy_interaction", [0, 0, 0, 1]),
            ]
        for name, weights in contrast_specs:
            estimate, se, low, high = linear_contrast(fit, weights)
            mixed_estimate_by_key[(proposition, name)] = estimate
            model_contrasts.append({
                "proposition": proposition, "contrast": name, "estimate_seconds": estimate,
                "standard_error": se, "wald95_low": low, "wald95_high": high,
            })

        arrays = proposition_arrays(df, proposition, "M07_ground_spacecraft_state_divergence_s")
        for name, vector in contrast_vectors(arrays, proposition):
            low, high = mean_bootstrap_ci(vector, idx)
            estimate = float(vector.mean())
            raw_estimate_by_key[(proposition, name)] = estimate
            raw_bootstrap.append({
                "proposition": proposition, "contrast": name, "estimate_seconds": estimate,
                "bootstrap95_low": low, "bootstrap95_high": high,
            })

        ranked = rank_transformed_arrays(df, proposition)
        for name, vector in contrast_vectors(ranked, proposition):
            low, high = mean_bootstrap_ci(vector, idx)
            estimate = float(vector.mean())
            rank_estimate_by_key[(proposition, name)] = estimate
            rank_sensitivity.append({
                "proposition": proposition, "contrast": name, "rank01_contrast": estimate,
                "bootstrap95_low": low, "bootstrap95_high": high,
            })

        for q in [0.25, 0.5, 0.75]:
            for name, estimate, low, high in quantile_bootstrap_contrasts(arrays, proposition, q, idx):
                quantile_sensitivity.append({
                    "proposition": proposition, "quantile": q, "contrast": name,
                    "quantile_contrast_seconds": estimate, "bootstrap95_low": low,
                    "bootstrap95_high": high,
                })
                if q == 0.5:
                    median_estimate_by_key[(proposition, name)] = estimate

    cross_method = []
    for key in sorted(mixed_estimate_by_key):
        proposition, contrast = key
        values = [
            mixed_estimate_by_key[key], raw_estimate_by_key[key],
            rank_estimate_by_key[key], median_estimate_by_key[key],
        ]
        signs = [sign(value) for value in values if sign(value) != 0]
        cross_method.append({
            "proposition": proposition, "contrast": contrast,
            "mixed_model_estimate": values[0], "mixed_model_sign": sign(values[0]),
            "raw_bootstrap_estimate": values[1], "raw_bootstrap_sign": sign(values[1]),
            "rank_estimate": values[2], "rank_sign": sign(values[2]),
            "median_estimate": values[3], "median_sign": sign(values[3]),
            "direction_consistent_nonzero_methods": len(set(signs)) <= 1,
        })

    return {
        "fixed_effects": fixed_effects,
        "model_contrasts": model_contrasts,
        "raw_bootstrap": raw_bootstrap,
        "rank_sensitivity": rank_sensitivity,
        "quantile_sensitivity": quantile_sensitivity,
        "cross_method": cross_method,
    }


def counts_string(series: pd.Series) -> str:
    counts = series.value_counts().sort_index()
    return ",".join(f"{key}:{int(value)}" for key, value in counts.items())


def reproduce_p4(p4: pd.DataFrame) -> dict:
    if len(p4) != 240 or p4.cell_id.nunique() != 8:
        raise AssertionError("P4 locked population mismatch")
    selection = []
    for cell, sub in p4.groupby("cell_id", sort=True):
        selection.append({
            "cell_id": cell,
            "event_id": sub.event_id.iloc[0],
            "evidence_condition_id": sub.evidence_condition_id.iloc[0],
            "requested_policy_id": sub.requested_policy_id.iloc[0],
            "n": len(sub),
            "effective_policy_counts": counts_string(sub.effective_policy_id),
            "selected_action_counts": counts_string(sub.selected_action),
            "effective_policy_cell_deterministic": sub.effective_policy_id.nunique() == 1,
            "selected_action_cell_deterministic": sub.selected_action.nunique() == 1,
        })

    switch_rows = []
    for event in ["E1", "E3"]:
        esub = p4[p4.event_id == event]
        for construct, column in [("selected_action", "selected_action"), ("effective_policy", "effective_policy_id")]:
            rates = {}
            cis = {}
            for policy in ["P2", "P7"]:
                psub = esub[esub.requested_policy_id == policy]
                pivot = psub.pivot(index="campaign_seed", columns="evidence_condition_id", values=column)
                switches = (pivot["T1"] != pivot["T0"]).astype(float).to_numpy()
                rates[policy] = float(switches.mean())
                successes = int(switches.sum())
                cis[policy] = cp_interval(successes, len(switches))
            diff = rates["P7"] - rates["P2"]
            switch_rows.append({
                "event_id": event, "selection_construct": construct,
                "P2_switch_rate": rates["P2"], "P2_exact95_low": cis["P2"][0], "P2_exact95_high": cis["P2"][1],
                "P7_switch_rate": rates["P7"], "P7_exact95_low": cis["P7"][0], "P7_exact95_high": cis["P7"][1],
                "P7_minus_P2_switch_difference": diff, "bootstrap95_low": diff, "bootstrap95_high": diff,
            })

    endpoint_map: dict[str, Callable[[pd.DataFrame], np.ndarray]] = {
        "M01_unauthorized_effect": lambda d: d.M01_unauthorized_effect_completed.astype(float).to_numpy(),
        "M02_mission_completion": lambda d: d.M02_mission_objective_completion_ratio.astype(float).to_numpy(),
        "M03_safety_violation_count": lambda d: d.M03_safety_invariant_violation_count.astype(float).to_numpy(),
        "mission_loss": lambda d: d.mission_loss.astype(float).to_numpy(),
        "trusted_recovery": lambda d: d.trusted_recovery.astype(float).to_numpy(),
        "recovery_failed": lambda d: d.recovery_failed.astype(float).to_numpy(),
        "operational_unverified": lambda d: d.operational_unverified.astype(float).to_numpy(),
        "M06_legitimate_rejection_rate": lambda d: d.M06_legitimate_command_rejection_rate.astype(float).to_numpy(),
    }
    blocked = []
    for event in ["E1", "E3"]:
        esub = p4[p4.event_id == event]
        for endpoint, extractor in endpoint_map.items():
            by_policy = {}
            for policy in ["P2", "P7"]:
                psub = esub[esub.requested_policy_id == policy]
                t0 = psub[psub.evidence_condition_id == "T0"].sort_values("campaign_seed")
                t1 = psub[psub.evidence_condition_id == "T1"].sort_values("campaign_seed")
                by_policy[policy] = extractor(t1) - extractor(t0)
            interaction = by_policy["P7"] - by_policy["P2"]
            for contrast, vector in [
                ("P2_T1_minus_T0", by_policy["P2"]),
                ("P7_T1_minus_T0", by_policy["P7"]),
                ("evidence_by_requested_policy_interaction", interaction),
            ]:
                blocked.append({
                    "event_id": event, "endpoint": endpoint, "contrast": contrast,
                    "estimate": float(vector.mean()), "bootstrap95_low": float(vector.mean()),
                    "bootstrap95_high": float(vector.mean()),
                })

    p4_commit_counts = p4.execution_commit.value_counts().to_dict()
    return {
        "selection": selection,
        "switch": switch_rows,
        "blocked_contrasts": blocked,
        "p4_execution_commit_distribution": {str(k): int(v) for k, v in p4_commit_counts.items()},
        "complete_final_commit_seed_blocks": 29,
    }


def p5_cell_estimates(df: pd.DataFrame, seed_filter: set[int] | None = None) -> pd.DataFrame:
    work = df if seed_filter is None else df[df.campaign_seed.isin(seed_filter)]
    rows = []
    for group_id, cells in P5_GROUPS.items():
        for cell in cells:
            sub = work[work.cell_id == cell]
            rows.append({
                "group_id": group_id, "cell_id": cell,
                "requested_policy_id": sub.requested_policy_id.iloc[0],
                "effective_policy_id": sub.effective_policy_id.iloc[0], "n": len(sub),
                "M01": float(sub.M01_unauthorized_effect_completed.astype(float).mean()),
                "M02": float(sub.M02_mission_objective_completion_ratio.mean()),
                "M03": float(sub.M03_safety_invariant_violation_count.mean()),
                "M05_RMST_tau30": float(sub.M05_verified_recovery_analysis_time_s.mean()),
                "M05_observed": int(sub.M05_verified_recovery_event.sum()),
                "M05_censored": int((sub.M05_verified_recovery_event == 0).sum()),
                "M06": float(sub.M06_legitimate_command_rejection_rate.mean()),
            })
    return pd.DataFrame(rows)


def p5_vector(row: pd.Series) -> np.ndarray:
    # Minimize all coordinates by negating M02 (which is maximized).
    return np.array([row.M01, -row.M02, row.M03, row.M05_RMST_tau30, row.M06], dtype=float)


def pareto_relation(a: pd.Series, b: pd.Series, tol: float = 1e-12) -> str:
    va, vb = p5_vector(a), p5_vector(b)
    if np.allclose(va, vb, atol=tol, rtol=0):
        return "EMPIRICAL_TIE"
    if np.all(va <= vb + tol) and np.any(va < vb - tol):
        return "A_DOMINATES_B"
    if np.all(vb <= va + tol) and np.any(vb < va - tol):
        return "B_DOMINATES_A"
    return "TRADEOFF"


def pareto_front(cell_estimates: pd.DataFrame, group_id: str) -> list[str]:
    group = cell_estimates[cell_estimates.group_id == group_id].set_index("cell_id")
    front = []
    for cell, row in group.iterrows():
        dominated = False
        for other, other_row in group.iterrows():
            if other == cell:
                continue
            if pareto_relation(other_row, row) == "A_DOMINATES_B":
                dominated = True
                break
        if not dominated:
            front.append(cell)
    return sorted(front)


def p5_seed_benefit_vectors(df: pd.DataFrame, p7_cell: str, comparator_cell: str) -> dict[str, np.ndarray]:
    p7 = df[df.cell_id == p7_cell].sort_values("campaign_seed")
    comp = df[df.cell_id == comparator_cell].sort_values("campaign_seed")
    if not np.array_equal(p7.campaign_seed.to_numpy(), comp.campaign_seed.to_numpy()):
        raise AssertionError("P5 seed alignment failed")
    return {
        "M01": comp.M01_unauthorized_effect_completed.astype(float).to_numpy() - p7.M01_unauthorized_effect_completed.astype(float).to_numpy(),
        "M02": p7.M02_mission_objective_completion_ratio.to_numpy(float) - comp.M02_mission_objective_completion_ratio.to_numpy(float),
        "M03": comp.M03_safety_invariant_violation_count.to_numpy(float) - p7.M03_safety_invariant_violation_count.to_numpy(float),
        "M05": comp.M05_verified_recovery_analysis_time_s.to_numpy(float) - p7.M05_verified_recovery_analysis_time_s.to_numpy(float),
        "M06": comp.M06_legitimate_command_rejection_rate.to_numpy(float) - p7.M06_legitimate_command_rejection_rate.to_numpy(float),
    }


def marginal_ci_relation(metric_cis: dict[str, tuple[float, float]], eps: float = 1e-12) -> str:
    lows = np.array([lo for lo, _ in metric_cis.values()])
    highs = np.array([hi for _, hi in metric_cis.values()])
    if np.all(lows >= -eps) and np.any(lows > eps):
        return "MARGINAL_CI_SUPPORTS_P7_DOMINANCE"
    if np.all(highs <= eps) and np.any(highs < -eps):
        return "MARGINAL_CI_SUPPORTS_COMPARATOR_DOMINANCE"
    return "UNCERTAIN_OR_TIED_UNDER_MARGINAL_CIS"


def reproduce_p5(df: pd.DataFrame) -> dict:
    estimates = p5_cell_estimates(df)
    fronts = {group: pareto_front(estimates, group) for group in P5_GROUPS}
    statuses = []
    pairwise = []
    reconstruction_idx = bootstrap_indices(P5_RECONSTRUCTION_SEED)
    reference_pairs = []
    for group, cells in P5_GROUPS.items():
        p7_cell = P7_CELL_BY_GROUP[group]
        p7_row = estimates[estimates.cell_id == p7_cell].iloc[0]
        dominates, dominated_by, tie_trade = [], [], []
        for comparator in cells:
            if comparator == p7_cell:
                continue
            comp_row = estimates[estimates.cell_id == comparator].iloc[0]
            rel = pareto_relation(p7_row, comp_row)
            if rel == "A_DOMINATES_B":
                point_relation = "P7_EMPIRICALLY_DOMINATES"
                dominates.append(comparator)
            elif rel == "B_DOMINATES_A":
                point_relation = "P7_EMPIRICALLY_DOMINATED"
                dominated_by.append(comparator)
            elif rel == "EMPIRICAL_TIE":
                point_relation = "EMPIRICAL_TIE"
                tie_trade.append(comparator)
            else:
                point_relation = "EMPIRICAL_TRADEOFF"
                tie_trade.append(comparator)
            vectors = p5_seed_benefit_vectors(df, p7_cell, comparator)
            metric_cis = {}
            for metric, vector in vectors.items():
                low, high = mean_bootstrap_ci(vector, reconstruction_idx)
                metric_cis[metric] = (low, high)
                pairwise.append({
                    "group_id": group, "P7_cell": p7_cell, "comparator_cell": comparator,
                    "metric": metric, "benefit_estimate": float(vector.mean()),
                    "reconstruction_bootstrap95_low": low,
                    "reconstruction_bootstrap95_high": high,
                    "point_estimate_relation": point_relation,
                })
            reference_pairs.append({
                "group_id": group, "P7_cell": p7_cell, "comparator_cell": comparator,
                "point_estimate_relation": point_relation,
                "reconstruction_marginal_CI_relation": marginal_ci_relation(metric_cis),
            })
        statuses.append({
            "group_id": group, "P7_cell": p7_cell,
            "P7_on_point_estimate_pareto_front": p7_cell in fronts[group],
            "pareto_front_cells": ",".join(fronts[group]),
            "P7_dominates_cells": ",".join(dominates),
            "P7_dominated_by_cells": ",".join(dominated_by),
            "P7_tradeoff_or_tie_cells": ",".join(tie_trade),
        })

    final_df = df[df.campaign_seed.isin(FINAL_COMMIT_COMPLETE_SEEDS)]
    final_est = p5_cell_estimates(final_df, set(FINAL_COMMIT_COMPLETE_SEEDS))
    final_fronts = {group: pareto_front(final_est, group) for group in P5_GROUPS}
    sensitivity = []
    for group, cells in P5_GROUPS.items():
        p7 = P7_CELL_BY_GROUP[group]
        full_p7_row = estimates[estimates.cell_id == p7].iloc[0]
        final_p7_row = final_est[final_est.cell_id == p7].iloc[0]
        relation_stable = True
        direction_stable = True
        for comparator in cells:
            if comparator == p7:
                continue
            full_comp = estimates[estimates.cell_id == comparator].iloc[0]
            final_comp = final_est[final_est.cell_id == comparator].iloc[0]
            relation_stable &= pareto_relation(full_p7_row, full_comp) == pareto_relation(final_p7_row, final_comp)
            full_vectors = p5_seed_benefit_vectors(df, p7, comparator)
            final_vectors = p5_seed_benefit_vectors(final_df, p7, comparator)
            for metric in full_vectors:
                direction_stable &= sign(float(full_vectors[metric].mean())) == sign(float(final_vectors[metric].mean()))
        sensitivity.append({
            "group_id": group, "P7_cell": p7,
            "full_seed_count": 30, "final_commit_seed_count": 29,
            "full_P7_on_front": p7 in fronts[group],
            "final_commit_P7_on_front": p7 in final_fronts[group],
            "full_front_cells": ",".join(fronts[group]),
            "final_commit_front_cells": ",".join(final_fronts[group]),
            "P7_front_membership_stable": (p7 in fronts[group]) == (p7 in final_fronts[group]),
            "pairwise_relation_stable": bool(relation_stable),
            "metric_direction_stable": bool(direction_stable),
        })
    return {
        "cell_estimates": estimates.to_dict(orient="records"),
        "fronts": fronts,
        "statuses": statuses,
        "pairwise_independent_bootstrap": pairwise,
        "pair_classifications": reference_pairs,
        "sensitivity": sensitivity,
        "reconstruction_bootstrap_seed": P5_RECONSTRUCTION_SEED,
        "original_p5_bootstrap_seed_preserved": False,
    }


def records_by_keys(records: list[dict], keys: tuple[str, ...]) -> dict[tuple, dict]:
    return {tuple(row[k] for k in keys): row for row in records}


def validate_against_references(result: dict, expected_dir: Path) -> dict:
    checks: dict[str, object] = {}

    ref_c1 = read_tsv(expected_dir / "19-wp10c1-p2-rmst-contrasts.tsv")
    got_c1 = records_by_keys(result["c1"]["rmst"], ("endpoint", "contrast"))
    for _, row in ref_c1.iterrows():
        key = (row.endpoint, row.contrast)
        got = got_c1[key]
        for col in ["estimate_seconds", "bootstrap95_low", "bootstrap95_high"]:
            assert_close(got[col], row[col], 2e-12, f"C1 {key} {col}")
    checks["C1_RMST_exact_numeric_regression"] = "PASS"

    ref_terminal = read_tsv(expected_dir / "20-wp10c1-p2-p3-terminal-exact.tsv")
    got_terminal = records_by_keys(result["c1"]["terminal_exact"], ("proposition", "cell_label"))
    for _, row in ref_terminal.iterrows():
        got = got_terminal[(row.proposition, row.cell_label)]
        if got["trusted"] != int(row.trusted) or got["n"] != int(row.n):
            raise AssertionError("C1 terminal count mismatch")
        assert_close(got["exact95_low"], row.exact95_low, 2e-12, "C1 exact low")
        assert_close(got["exact95_high"], row.exact95_high, 2e-12, "C1 exact high")
    checks["C1_terminal_exact_regression"] = "PASS"

    ref_p1 = read_tsv(expected_dir / "18-wp10c1-p1-blocked-contrasts.tsv")
    if not all(result["c1"]["p1_structural_primary"].values()):
        raise AssertionError("P1 structural-primary reproduction failed")
    if not np.allclose(ref_p1[["estimate", "bootstrap95_low", "bootstrap95_high"]].to_numpy(float), 0.0):
        raise AssertionError("preserved P1 primary contrasts unexpectedly nonzero")
    checks["C1_P1_primary_null_regression"] = "PASS"

    ref_p3_discordance = read_tsv(expected_dir / "23-wp10c1-p3-verification-discordance.tsv")
    got_disc = records_by_keys(result["c1"]["p3_verification_discordance"], ("cell_label", "cell_id"))
    for _, row in ref_p3_discordance.iterrows():
        got = got_disc[(row.cell_label, row.cell_id)]
        for col in ["behaviorally_restored", "trusted_recovery", "operational_but_unverified"]:
            if int(got[col]) != int(row[col]):
                raise AssertionError(f"P3 verification-discordance mismatch {row.cell_label}/{col}")
    checks["C1_P3_verification_discordance_regression"] = "PASS"

    ref_c2_boot = read_tsv(expected_dir / "30-wp10c2-m07-seed-block-bootstrap.tsv")
    got_c2_boot = records_by_keys(result["c2"]["raw_bootstrap"], ("proposition", "contrast"))
    for _, row in ref_c2_boot.iterrows():
        got = got_c2_boot[(row.proposition, row.contrast)]
        for col in ["estimate_seconds", "bootstrap95_low", "bootstrap95_high"]:
            assert_close(got[col], row[col], 2e-12, f"C2 bootstrap {row.proposition}/{row.contrast}/{col}")
    checks["C2_raw_bootstrap_exact_numeric_regression"] = "PASS"

    ref_rank = read_tsv(expected_dir / "31-wp10c2-m07-rank-sensitivity.tsv")
    got_rank = records_by_keys(result["c2"]["rank_sensitivity"], ("proposition", "contrast"))
    for _, row in ref_rank.iterrows():
        got = got_rank[(row.proposition, row.contrast)]
        for col in ["rank01_contrast", "bootstrap95_low", "bootstrap95_high"]:
            assert_close(got[col], row[col], 2e-12, f"C2 rank {row.proposition}/{row.contrast}/{col}")
    checks["C2_rank_exact_numeric_regression"] = "PASS"

    ref_quantile = read_tsv(expected_dir / "32-wp10c2-m07-quantile-sensitivity.tsv")
    got_quantile = records_by_keys(result["c2"]["quantile_sensitivity"], ("proposition", "quantile", "contrast"))
    for _, row in ref_quantile.iterrows():
        q = {"Q25": 0.25, "Q50": 0.5, "Q75": 0.75}[str(row['quantile'])]
        got = got_quantile[(row.proposition, q, row.contrast)]
        assert_close(got["quantile_contrast_seconds"], row.contrast_seconds, 2e-12, f"C2 quantile {row.proposition}/{row['quantile']}/{row.contrast}/contrast")
        for col in ["bootstrap95_low", "bootstrap95_high"]:
            assert_close(got[col], row[col], 2e-12, f"C2 quantile {row.proposition}/{row['quantile']}/{row.contrast}/{col}")
    checks["C2_quantile_exact_numeric_regression"] = "PASS"

    ref_fixed = read_tsv(expected_dir / "28-wp10c2-m07-fixed-effects.tsv")
    got_fixed = records_by_keys(result["c2"]["fixed_effects"], ("proposition", "term"))
    for _, row in ref_fixed.iterrows():
        got = got_fixed[(row.proposition, row.term)]
        for col in ["estimate", "standard_error", "wald95_low", "wald95_high"]:
            assert_close(got[col], row[col], 2e-6, f"C2 mixed model {row.proposition}/{row.term}/{col}")
    checks["C2_mixed_model_numeric_regression"] = "PASS"

    ref_cross = read_tsv(expected_dir / "33-wp10c2-m07-cross-method-direction.tsv")
    got_cross = records_by_keys(result["c2"]["cross_method"], ("proposition", "contrast"))
    for _, row in ref_cross.iterrows():
        got = got_cross[(row.proposition, row.contrast)]
        if bool(got["direction_consistent_nonzero_methods"]) != bool(row.direction_consistent_nonzero_methods):
            raise AssertionError(f"C2 cross-method direction mismatch {row.proposition}/{row.contrast}")
    checks["C2_cross_method_direction_regression"] = "PASS"

    ref_p4_selection = read_tsv(expected_dir / "43-wp10d2r1-selection-cell-distributions.tsv")
    got_p4_selection = records_by_keys(result["p4"]["selection"], ("cell_id",))
    for _, row in ref_p4_selection.iterrows():
        got = got_p4_selection[(row.cell_id,)]
        for col in ["n", "effective_policy_counts", "selected_action_counts"]:
            if str(got[col]) != str(row[col]):
                raise AssertionError(f"P4 selection-distribution mismatch {row.cell_id}/{col}")
    checks["P4_selection_distribution_regression"] = "PASS"

    ref_p4_switch = read_tsv(expected_dir / "44-wp10d2r1-selection-switch-contrasts.tsv")
    got_p4_switch = records_by_keys(result["p4"]["switch"], ("event_id", "selection_construct"))
    for _, row in ref_p4_switch.iterrows():
        got = got_p4_switch[(row.event_id, row.selection_construct)]
        for col in ["P2_switch_rate", "P7_switch_rate", "P7_minus_P2_switch_difference", "bootstrap95_low", "bootstrap95_high"]:
            assert_close(got[col], row[col], 2e-12, f"P4 switch {row.event_id}/{row.selection_construct}/{col}")
    checks["P4_selection_switch_regression"] = "PASS"

    ref_p4_blocked = read_tsv(expected_dir / "46-wp10d2r1-downstream-blocked-contrasts.tsv")
    got_p4_blocked = records_by_keys(result["p4"]["blocked_contrasts"], ("event_id", "endpoint", "contrast"))
    for _, row in ref_p4_blocked.iterrows():
        got = got_p4_blocked[(row.event_id, row.endpoint, row.contrast)]
        for col in ["estimate", "bootstrap95_low", "bootstrap95_high"]:
            assert_close(got[col], row[col], 2e-12, f"P4 blocked {row.event_id}/{row.endpoint}/{row.contrast}/{col}")
    checks["P4_downstream_contrast_regression"] = "PASS"

    ref_p5_cells = read_tsv(expected_dir / "62-wp10f-p5-cell-primary-estimates.tsv")
    got_p5_cells = records_by_keys(result["p5"]["cell_estimates"], ("group_id", "cell_id"))
    for _, row in ref_p5_cells.iterrows():
        got = got_p5_cells[(row.group_id, row.cell_id)]
        for col in ["M01", "M02", "M03", "M05_RMST_tau30", "M06"]:
            assert_close(got[col], row[col], 2e-12, f"P5 cell {row.group_id}/{row.cell_id}/{col}")
    checks["P5_cell_primary_exact_regression"] = "PASS"

    ref_status = read_tsv(expected_dir / "66-wp10f-p5-condition-specific-p7-status.tsv").fillna("")
    got_status = records_by_keys(result["p5"]["statuses"], ("group_id",))
    for _, row in ref_status.iterrows():
        got = got_status[(row.group_id,)]
        if bool(got["P7_on_point_estimate_pareto_front"]) != bool(row.P7_on_point_estimate_pareto_front):
            raise AssertionError(f"P5 front membership mismatch {row.group_id}")
        if got["pareto_front_cells"] != str(row.pareto_front_cells):
            raise AssertionError(f"P5 front cells mismatch {row.group_id}")
    checks["P5_point_pareto_front_regression"] = "PASS"

    ref_pair = read_tsv(expected_dir / "64-wp10f-p5-p7-pairwise-primary-contrasts.tsv")
    got_pair = records_by_keys(result["p5"]["pairwise_independent_bootstrap"], ("group_id", "P7_cell", "comparator_cell", "metric"))
    for _, row in ref_pair.iterrows():
        got = got_pair[(row.group_id, row.P7_cell, row.comparator_cell, row.metric)]
        assert_close(got["benefit_estimate"], row.P7_benefit_estimate, 2e-12, f"P5 pair point estimate {row.group_id}/{row.comparator_cell}/{row.metric}")
    checks["P5_pairwise_point_estimate_regression"] = "PASS"

    ref_pair_class = read_tsv(expected_dir / "65-wp10f-p5-pairwise-uncertainty-classification.tsv")
    got_class = records_by_keys(result["p5"]["pair_classifications"], ("group_id", "P7_cell", "comparator_cell"))
    for _, row in ref_pair_class.iterrows():
        got = got_class[(row.group_id, row.P7_cell, row.comparator_cell)]
        if got["point_estimate_relation"] != row.point_estimate_relation:
            raise AssertionError(f"P5 point pair relation mismatch {row.group_id}/{row.comparator_cell}")
        if got["reconstruction_marginal_CI_relation"] != row.marginal_bootstrap_CI_relation:
            raise AssertionError(
                "P5 independent-bootstrap classification mismatch "
                f"{row.group_id}/{row.comparator_cell}: {got['reconstruction_marginal_CI_relation']} != {row.marginal_bootstrap_CI_relation}"
            )
    checks["P5_independent_bootstrap_classification_regression"] = "PASS"
    checks["P5_original_bootstrap_endpoint_exact_replay"] = "NOT_CLAIMED_OR_REQUIRED_SEED_NOT_PRESERVED"

    ref_sens = read_tsv(expected_dir / "67-wp10f-p5-final-commit-block-sensitivity.tsv")
    got_sens = records_by_keys(result["p5"]["sensitivity"], ("group_id",))
    for _, row in ref_sens.iterrows():
        got = got_sens[(row.group_id,)]
        if got["full_front_cells"] != row.full_front_cells or got["final_commit_front_cells"] != row.final_commit_front_cells:
            raise AssertionError(f"P5 final-commit sensitivity front mismatch {row.group_id}")
        if not got["P7_front_membership_stable"]:
            raise AssertionError(f"P5 final-commit front unstable {row.group_id}")
        if bool(got["pairwise_relation_stable"]) != bool(row.pairwise_relation_stable):
            raise AssertionError(f"P5 final-commit pair relation mismatch {row.group_id}")
        if bool(got["metric_direction_stable"]) != bool(row.metric_direction_stable):
            raise AssertionError(f"P5 final-commit metric direction mismatch {row.group_id}")
    checks["P5_final_commit_sensitivity_regression"] = "PASS"

    return checks


def write_outputs(result: dict, out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(result["c1"]["rmst"]).to_csv(out / "reproduced-c1-p2-rmst.tsv", sep="\t", index=False)
    pd.DataFrame(result["c2"]["raw_bootstrap"]).to_csv(out / "reproduced-c2-m07-bootstrap.tsv", sep="\t", index=False)
    pd.DataFrame(result["c2"]["fixed_effects"]).to_csv(out / "reproduced-c2-mixed-model-fixed-effects.tsv", sep="\t", index=False)
    pd.DataFrame(result["p4"]["switch"]).to_csv(out / "reproduced-p4-selection-switch.tsv", sep="\t", index=False)
    pd.DataFrame(result["p5"]["statuses"]).to_csv(out / "reproduced-p5-pareto-status.tsv", sep="\t", index=False)
    pd.DataFrame(result["p5"]["pair_classifications"]).to_csv(out / "reproduced-p5-pairwise-classification.tsv", sep="\t", index=False)


def main() -> int:
    if sys.version_info[:2] != (3, 11):
        raise SystemExit(
            "WP10 statistical reconstruction requires CPython 3.11.x; "
            f"observed {sys.version.split()[0]}"
        )

    parser = argparse.ArgumentParser()
    parser.add_argument("--reference-dir", type=Path, default=Path(__file__).parent / "reference")
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--validate", action="store_true")
    args = parser.parse_args()

    reference = args.reference_dir.resolve()
    locked = reference / "locked-analysis-extraction-720.tsv"
    p4_locked = reference / "p4-locked-analysis-240.tsv"
    expected = reference / "expected"

    if not locked.is_file() or not p4_locked.is_file():
        raise SystemExit("required locked reproduction inputs are missing")
    if sha256_file(p4_locked) != P4_LOCKED_SHA256:
        raise SystemExit("P4 locked analysis table SHA-256 mismatch")

    df = read_tsv(locked)
    p4 = read_tsv(p4_locked)
    validate_locked_input(df, locked)

    result = {
        "provenance": {
            "implementation_role": "POST_PUBLICATION_RECONSTRUCTION_VALIDATED_AGAINST_PRESERVED_WP10_OUTPUTS",
            "original_analysis_source_preserved": False,
            "locked_input_sha256": LOCKED_SHA256,
            "p4_locked_input_sha256": P4_LOCKED_SHA256,
            "analysis_membership_sha256": ANALYSIS_MEMBERSHIP_SHA256,
            "valid_runs": 720,
            "cells": 24,
            "campaign_seeds": 30,
            "c1_bootstrap_seed_recovered": C1_BOOTSTRAP_SEED,
            "c2_bootstrap_seed_recovered": C2_BOOTSTRAP_SEED,
            "p5_original_bootstrap_seed_preserved": False,
            "p5_reconstruction_bootstrap_seed": P5_RECONSTRUCTION_SEED,
            "bootstrap_replicates": BOOTSTRAP_REPLICATES,
            "tau_s": TAU_S,
            "p_values_computed": False,
            "weighted_score_computed": False,
            "global_policy_ranking_computed": False,
            "simultaneous_pareto_confidence_claim": False,
        },
        "c1": reproduce_c1(df),
        "c2": reproduce_c2(df),
        "p4": reproduce_p4(p4),
        "p5": reproduce_p5(df),
    }

    if args.validate:
        result["validation"] = validate_against_references(result, expected)
        result["validation"]["overall"] = "PASS"

    if args.output_dir:
        write_outputs(result, args.output_dir)
        (args.output_dir / "reproduction-validation.json").write_text(
            json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
    else:
        print(json.dumps(result.get("validation", result["provenance"]), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
