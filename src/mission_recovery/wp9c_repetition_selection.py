from __future__ import annotations

import argparse
import json
import math
import random
import statistics
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
Z95 = 1.959963984540054
EPS = 1e-12

DEFAULT_CONFIG = ROOT / "configs/wp9c_repetition_selection.json"
CAMPAIGN_CONFIG = ROOT / "configs/wp9_campaign_design.json"
PILOT_CONFIG = ROOT / "configs/wp8_pilot_design.json"
STAGE1_LEDGER = ROOT / "results/wp8/pilot/stage1/stage1-ledger.json"
STAGE2_LEDGER = ROOT / "results/wp8/pilot/stage2/stage2-ledger.json"


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _mean(values: list[float]) -> float:
    if not values:
        raise ValueError("mean requires at least one value")
    return sum(values) / len(values)


def _sd(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    return statistics.stdev(values)


def _constant(values: list[float]) -> bool:
    if not values:
        return True
    lo = min(values)
    hi = max(values)
    return abs(hi - lo) <= EPS


def _quantile(values: list[float], probability: float) -> float:
    if not values:
        raise ValueError("quantile requires at least one value")
    if probability <= 0:
        return min(values)
    if probability >= 1:
        return max(values)
    ordered = sorted(values)
    position = probability * (len(ordered) - 1)
    lower = int(math.floor(position))
    upper = int(math.ceil(position))
    if lower == upper:
        return ordered[lower]
    fraction = position - lower
    return ordered[lower] * (1.0 - fraction) + ordered[upper] * fraction


def wilson_half_width(probability: float, trials: int) -> float:
    if trials <= 0:
        raise ValueError("Wilson interval requires positive trials")
    p = min(1.0, max(0.0, float(probability)))
    z2 = Z95 * Z95
    denominator = 1.0 + z2 / trials
    radius = Z95 * math.sqrt(
        p * (1.0 - p) / trials + z2 / (4.0 * trials * trials)
    ) / denominator
    return radius


def validate_method_config(config: dict[str, Any], campaign: dict[str, Any]) -> None:
    if config.get("decision_id") != "R-050":
        raise ValueError("WP9-C method decision is not R-050")
    boundary = config["scientific_boundary"]
    for key in (
        "pilot_effects_used_as_final_effect_assumptions",
        "expected_values_used_as_metric_inputs",
        "campaign_runtime_execution_performed",
        "campaign_seed_consumed",
        "campaign_data_generated",
        "final_campaign_execution_authorized",
    ):
        if boundary[key] is not False:
            raise ValueError(f"WP9-C crossed blocked boundary: {key}")
    if boundary["read_only_pilot_inputs"] is not True:
        raise ValueError("WP9-C pilot inputs must be read-only")

    frozen = campaign["repetition_selection"]
    if config["candidate_valid_repetitions_per_cell"] != frozen[
        "candidate_valid_repetitions_per_cell"
    ]:
        raise ValueError("WP9-C candidates differ from R-044")
    if config["candidate_total_valid_executions"] != frozen[
        "candidate_total_valid_executions"
    ]:
        raise ValueError("WP9-C candidate totals differ from R-044")

    targets = config["precision_targets"]
    expected_targets = {
        "bounded_ratio_95pct_ci_half_width": frozen[
            "ratio_metric_95pct_ci_half_width_target"
        ],
        "binary_95pct_ci_half_width": frozen[
            "binary_metric_95pct_ci_half_width_target"
        ],
        "time_relative_95pct_ci_half_width": frozen[
            "time_metric_relative_95pct_ci_half_width_target"
        ],
        "model_fit_convergence_rate": frozen["model_fit_convergence_target"],
    }
    if targets != expected_targets:
        raise ValueError("WP9-C precision targets differ from R-044")

    empirical = config["empirical_resampling"]
    if int(empirical["iterations"]) < 1000:
        raise ValueError("WP9-C empirical bootstrap requires at least 1000 iterations")
    if empirical["resample_unit"] != "pilot_seed_block":
        raise ValueError("WP9-C must resample pilot seed blocks")
    if empirical["same_resampled_seed_index_applied_to_all_seven_anchors"] is not True:
        raise ValueError("WP9-C must preserve cross-anchor seed blocks")
    if empirical["right_censoring_preserved"] is not True:
        raise ValueError("WP9-C must preserve right censoring")

    stability = config["conservative_sensitivity"]["model_stability"]
    if int(stability["iterations"]) < 1000:
        raise ValueError("WP9-C stability simulation requires at least 1000 iterations")
    if stability["primary_block_cell_counts"] != {
        "P1": 6,
        "P2": 4,
        "P3": 4,
        "P4": 8,
    }:
        raise ValueError("WP9-C primary block sizes changed")


def _extract_record(
    *,
    run_record: dict[str, Any],
    cell_id: str,
    seed: int,
) -> dict[str, Any]:
    raw = run_record["raw_metric_evidence"]
    outcomes = run_record["outcomes"]
    timing = run_record["timing"]
    legitimate = raw["legitimate_commands"]
    attempted = int(legitimate["attempted"])
    rejected = int(legitimate["rejected"])
    if attempted < 0 or rejected < 0 or rejected > attempted:
        raise ValueError(f"{run_record['run_id']}: invalid legitimate command counts")
    if attempted == 0:
        raise ValueError(
            f"{run_record['run_id']}: legitimate-command precision requires observed denominator"
        )

    run_end_s = float(raw["run_end_s"])
    if not math.isfinite(run_end_s) or run_end_s <= 0:
        raise ValueError(f"{run_record['run_id']}: invalid run_end_s")

    containment_observed = bool(raw["containment"]["predicate"])
    recovery_observed = bool(raw["trusted_recovery"]["predicate"])
    containment_s = timing.get("containment_s")
    recovery_s = timing.get("verified_recovery_s")
    if containment_observed and containment_s is None:
        raise ValueError(f"{run_record['run_id']}: observed containment lacks time")
    if recovery_observed and recovery_s is None:
        raise ValueError(f"{run_record['run_id']}: observed recovery lacks time")

    containment_restricted = (
        float(containment_s) if containment_observed else run_end_s
    )
    recovery_restricted = float(recovery_s) if recovery_observed else run_end_s

    values = {
        "cell_id": cell_id,
        "seed": int(seed),
        "run_id": run_record["run_id"],
        "mission_objective_completion_ratio": float(
            outcomes["mission_objective_completion_ratio"]
        ),
        "evidence_completeness_ratio": float(
            outcomes["evidence_completeness_ratio"]
        ),
        "unauthorized_effect_completed": bool(
            outcomes["unauthorized_effect_completed"]
        ),
        "trusted_recovery_confirmed": recovery_observed,
        "legitimate_attempted": attempted,
        "legitimate_rejected": rejected,
        "legitimate_rejection_indicator": rejected > 0,
        "time_to_containment_s": containment_restricted,
        "time_to_verified_recovery_s": recovery_restricted,
        "ground_spacecraft_state_divergence_s": float(
            outcomes["ground_spacecraft_state_divergence_s"]
        ),
        "containment_observed": containment_observed,
        "trusted_recovery_observed": recovery_observed,
        "terminal_state": run_record["terminal_state"],
    }
    for key in (
        "mission_objective_completion_ratio",
        "evidence_completeness_ratio",
        "time_to_containment_s",
        "time_to_verified_recovery_s",
        "ground_spacecraft_state_divergence_s",
    ):
        value = float(values[key])
        if not math.isfinite(value) or value < 0:
            raise ValueError(f"{run_record['run_id']}: invalid metric {key}")
    return values


def load_balanced_anchor_records(
    root: Path,
    config: dict[str, Any],
) -> dict[str, list[dict[str, Any]]]:
    pilot = _load(root / "configs/wp8_pilot_design.json")
    stage1 = _load(root / "results/wp8/pilot/stage1/stage1-ledger.json")
    stage2 = _load(root / "results/wp8/pilot/stage2/stage2-ledger.json")
    input_contract = config["input_contract"]
    anchors = list(input_contract["anchor_cell_ids"])
    seeds = [int(value) for value in input_contract["anchor_seed_ids"]]

    cells = {row["cell_id"]: row for row in pilot["cells"]}
    if set(anchors) - set(cells):
        raise ValueError("WP9-C anchor cell missing from pilot design")

    valid_total = 0
    invalid_stage1 = 0
    invalid_stage2 = 0
    by_anchor: dict[str, dict[int, dict[str, Any]]] = {
        cell_id: {} for cell_id in anchors
    }

    for stage_name, ledger, acceptance_name in (
        ("stage1", stage1, "stage1-acceptance.json"),
        ("stage2", stage2, "stage2-acceptance.json"),
    ):
        for attempt in ledger["attempts"]:
            if attempt["status"] != "VALID":
                if stage_name == "stage1":
                    invalid_stage1 += 1
                else:
                    invalid_stage2 += 1
                continue
            valid_total += 1
            cell_id = attempt["cell_id"]
            if cell_id not in by_anchor:
                continue
            seed = int(attempt["seed"])
            evidence = root / attempt["retained_evidence_ref"]
            run_record = _load(evidence / "run-record.json")
            provenance = _load(evidence / "binding-provenance.json")
            acceptance = _load(evidence / acceptance_name)
            if provenance.get("pilot_data") is not True:
                raise ValueError(f"{attempt['run_id']}: anchor is not pilot data")
            if provenance.get("development_preflight") is not False:
                raise ValueError(f"{attempt['run_id']}: anchor marked development")
            if acceptance.get("schema_valid") is not True:
                raise ValueError(f"{attempt['run_id']}: anchor schema invalid")
            if acceptance.get("raw_metric_inputs_complete") is not True:
                raise ValueError(f"{attempt['run_id']}: anchor raw metrics incomplete")
            if run_record["run_id"] != attempt["run_id"]:
                raise ValueError(f"{attempt['run_id']}: run identity mismatch")
            if seed in by_anchor[cell_id]:
                raise ValueError(f"{cell_id}: duplicate seed {seed}")
            by_anchor[cell_id][seed] = _extract_record(
                run_record=run_record,
                cell_id=cell_id,
                seed=seed,
            )

    if valid_total != int(input_contract["valid_pilot_records"]):
        raise ValueError(f"WP9-C valid pilot count changed: {valid_total}")
    if invalid_stage1 != int(input_contract["stage1_excluded_invalid_records"]):
        raise ValueError("WP9-C Stage-1 invalid count changed")
    if invalid_stage2 != int(input_contract["stage2_invalid_records"]):
        raise ValueError("WP9-C Stage-2 invalid count changed")

    result: dict[str, list[dict[str, Any]]] = {}
    for cell_id in anchors:
        observed = by_anchor[cell_id]
        if set(observed) != set(seeds):
            raise ValueError(
                f"{cell_id}: anchor seed balance changed: {sorted(observed)}"
            )
        result[cell_id] = [observed[seed] for seed in seeds]
    return result


def _metric_values(records: list[dict[str, Any]], metric: str) -> list[float]:
    if metric == "unauthorized_effect_completed":
        return [float(bool(row[metric])) for row in records]
    if metric == "trusted_recovery_confirmed":
        return [float(bool(row[metric])) for row in records]
    if metric == "legitimate_command_rejection_rate":
        return [
            row["legitimate_rejected"] / row["legitimate_attempted"]
            for row in records
        ]
    return [float(row[metric]) for row in records]


def _weighted_estimator(
    records: list[dict[str, Any]],
    weights: list[int],
    metric: str,
) -> float:
    total_runs = sum(weights)
    if total_runs <= 0:
        raise ValueError("bootstrap weights contain no runs")
    if metric == "legitimate_command_rejection_rate":
        attempted = sum(
            weight * int(row["legitimate_attempted"])
            for row, weight in zip(records, weights)
        )
        rejected = sum(
            weight * int(row["legitimate_rejected"])
            for row, weight in zip(records, weights)
        )
        if attempted <= 0:
            raise ValueError("bootstrap legitimate-command denominator is zero")
        return rejected / attempted
    values = _metric_values(records, metric)
    return sum(weight * value for weight, value in zip(weights, values)) / total_runs


def empirical_precision_for_candidate(
    *,
    anchors: dict[str, list[dict[str, Any]]],
    config: dict[str, Any],
    candidate: int,
) -> dict[str, Any]:
    empirical = config["empirical_resampling"]
    iterations = int(empirical["iterations"])
    rng = random.Random(int(empirical["random_seed"]) + int(candidate))
    anchor_ids = list(config["input_contract"]["anchor_cell_ids"])
    ratio_metrics = list(config["metric_classes"]["bounded_ratio"])
    binary_metrics = list(config["metric_classes"]["binary_or_binomial"])
    time_metrics = list(config["metric_classes"]["time"])
    metrics = ratio_metrics + binary_metrics + time_metrics

    distributions: dict[tuple[str, str], list[float]] = {
        (cell_id, metric): []
        for cell_id in anchor_ids
        for metric in metrics
    }
    seed_count = len(config["input_contract"]["anchor_seed_ids"])
    for _ in range(iterations):
        weights = [0] * seed_count
        for _run in range(candidate):
            weights[rng.randrange(seed_count)] += 1
        for cell_id in anchor_ids:
            records = anchors[cell_id]
            for metric in metrics:
                distributions[(cell_id, metric)].append(
                    _weighted_estimator(records, weights, metric)
                )

    low_p, high_p = [float(x) for x in empirical["percentile_interval"]]
    targets = config["precision_targets"]
    rows = []
    nonstructural_pass = True
    structural_count = 0
    worst_by_class: dict[str, float] = {
        "bounded_ratio": 0.0,
        "binary_or_binomial": 0.0,
        "time": 0.0,
    }

    for cell_id in anchor_ids:
        records = anchors[cell_id]
        for metric in metrics:
            original = _metric_values(records, metric)
            structural = _constant(original)
            distribution = distributions[(cell_id, metric)]
            low = _quantile(distribution, low_p)
            high = _quantile(distribution, high_p)
            half_width = (high - low) / 2.0
            point = _weighted_estimator(records, [1] * len(records), metric)

            if metric in ratio_metrics:
                metric_class = "bounded_ratio"
                target = float(targets["bounded_ratio_95pct_ci_half_width"])
                precision_value = half_width
            elif metric in binary_metrics:
                metric_class = "binary_or_binomial"
                target = float(targets["binary_95pct_ci_half_width"])
                precision_value = half_width
            else:
                metric_class = "time"
                target = float(targets["time_relative_95pct_ci_half_width"])
                precision_value = (
                    half_width / abs(point) if abs(point) > EPS else math.inf
                )

            if structural:
                status = "STRUCTURAL_DEGENERATE_REQUIRES_SENSITIVITY"
                structural_count += 1
            else:
                passed = precision_value <= target
                status = "PASS" if passed else "FAIL"
                nonstructural_pass = nonstructural_pass and passed
                worst_by_class[metric_class] = max(
                    worst_by_class[metric_class], precision_value
                )
            rows.append(
                {
                    "anchor_cell_id": cell_id,
                    "metric": metric,
                    "metric_class": metric_class,
                    "point_estimate": point,
                    "bootstrap_ci_low": low,
                    "bootstrap_ci_high": high,
                    "half_width": half_width,
                    "precision_value": precision_value,
                    "target": target,
                    "structural": structural,
                    "status": status,
                }
            )

    return {
        "candidate": int(candidate),
        "iterations": iterations,
        "rows": rows,
        "nonstructural_precision_pass": nonstructural_pass,
        "structural_endpoint_count": structural_count,
        "structural_endpoints_require_sensitivity": structural_count > 0,
        "worst_nonstructural_precision_by_class": worst_by_class,
    }


def conservative_precision_for_candidate(
    *,
    anchors: dict[str, list[dict[str, Any]]],
    config: dict[str, Any],
    candidate: int,
) -> dict[str, Any]:
    sensitivity = config["conservative_sensitivity"]
    targets = config["precision_targets"]
    ratio_metrics = list(config["metric_classes"]["bounded_ratio"])
    binary_metrics = list(config["metric_classes"]["binary_or_binomial"])
    time_metrics = list(config["metric_classes"]["time"])
    rows = []
    all_pass = True

    for cell_id in config["input_contract"]["anchor_cell_ids"]:
        records = anchors[cell_id]
        runs = len(records)
        for metric in binary_metrics:
            if metric == "legitimate_command_rejection_rate":
                successes = sum(
                    bool(row["legitimate_rejection_indicator"])
                    for row in records
                )
            else:
                successes = sum(bool(row[metric]) for row in records)
            p_sens = (successes + 1.0) / (runs + 2.0)
            half_width = wilson_half_width(p_sens, int(candidate))
            target = float(targets["binary_95pct_ci_half_width"])
            passed = half_width <= target
            all_pass = all_pass and passed
            rows.append(
                {
                    "anchor_cell_id": cell_id,
                    "metric": metric,
                    "metric_class": "binary_or_binomial",
                    "sensitivity_probability": p_sens,
                    "precision_value": half_width,
                    "target": target,
                    "status": "PASS" if passed else "FAIL",
                }
            )

        ratio_rule = sensitivity["bounded_ratio"]
        for metric in ratio_metrics:
            values = _metric_values(records, metric)
            observed_sd = _sd(values)
            sd_sens = min(
                float(ratio_rule["sd_cap_for_unit_interval"]),
                max(
                    float(ratio_rule["sample_sd_inflation_factor"]) * observed_sd,
                    float(ratio_rule["absolute_sd_floor"]),
                ),
            )
            half_width = Z95 * sd_sens / math.sqrt(candidate)
            target = float(targets["bounded_ratio_95pct_ci_half_width"])
            passed = half_width <= target
            all_pass = all_pass and passed
            rows.append(
                {
                    "anchor_cell_id": cell_id,
                    "metric": metric,
                    "metric_class": "bounded_ratio",
                    "observed_sd": observed_sd,
                    "sensitivity_sd": sd_sens,
                    "precision_value": half_width,
                    "target": target,
                    "status": "PASS" if passed else "FAIL",
                }
            )

        time_rule = sensitivity["time"]
        for metric in time_metrics:
            values = _metric_values(records, metric)
            observed_mean = _mean(values)
            observed_sd = _sd(values)
            observed_cv = (
                observed_sd / abs(observed_mean)
                if abs(observed_mean) > EPS
                else 0.0
            )
            cv_sens = max(
                float(time_rule["sample_cv_inflation_factor"]) * observed_cv,
                float(time_rule["relative_cv_floor"]),
            )
            relative_half_width = Z95 * cv_sens / math.sqrt(candidate)
            target = float(targets["time_relative_95pct_ci_half_width"])
            passed = relative_half_width <= target
            all_pass = all_pass and passed
            rows.append(
                {
                    "anchor_cell_id": cell_id,
                    "metric": metric,
                    "metric_class": "time",
                    "observed_mean": observed_mean,
                    "observed_cv": observed_cv,
                    "sensitivity_cv": cv_sens,
                    "precision_value": relative_half_width,
                    "target": target,
                    "status": "PASS" if passed else "FAIL",
                }
            )

    worst: dict[str, float] = {}
    for row in rows:
        key = row["metric_class"]
        worst[key] = max(worst.get(key, 0.0), float(row["precision_value"]))
    return {
        "candidate": int(candidate),
        "rows": rows,
        "precision_pass": all_pass,
        "worst_precision_by_class": worst,
    }


def extreme_laplace_binary_probability(
    anchors: dict[str, list[dict[str, Any]]]
) -> dict[str, Any]:
    rows = []
    extreme = 0.5
    for cell_id, records in anchors.items():
        for metric in (
            "unauthorized_effect_completed",
            "trusted_recovery_confirmed",
            "legitimate_rejection_indicator",
        ):
            successes = sum(bool(row[metric]) for row in records)
            p_sens = (successes + 1.0) / (len(records) + 2.0)
            extremity = max(p_sens, 1.0 - p_sens)
            extreme = max(extreme, extremity)
            rows.append(
                {
                    "anchor_cell_id": cell_id,
                    "metric": metric,
                    "successes": int(successes),
                    "runs": len(records),
                    "laplace_probability": p_sens,
                    "extreme_probability": extremity,
                }
            )
    return {"extreme_probability": extreme, "rows": rows}


def model_stability_for_candidate(
    *,
    extreme_probability: float,
    config: dict[str, Any],
    candidate: int,
) -> dict[str, Any]:
    rule = config["conservative_sensitivity"]["model_stability"]
    iterations = int(rule["iterations"])
    rng = random.Random(int(rule["random_seed"]) + int(candidate))
    p = float(extreme_probability)
    cell_nondegenerate_probability = 1.0 - p ** candidate - (1.0 - p) ** candidate
    block_rates: dict[str, float] = {}
    analytic_rates: dict[str, float] = {}
    for block, cell_count_raw in rule["primary_block_cell_counts"].items():
        cell_count = int(cell_count_raw)
        converged = 0
        for _ in range(iterations):
            if all(
                rng.random() < cell_nondegenerate_probability
                for _cell in range(cell_count)
            ):
                converged += 1
        block_rates[block] = converged / iterations
        analytic_rates[block] = cell_nondegenerate_probability ** cell_count
    minimum_rate = min(block_rates.values())
    target = float(config["precision_targets"]["model_fit_convergence_rate"])
    return {
        "candidate": int(candidate),
        "iterations": iterations,
        "extreme_probability": p,
        "cell_nondegenerate_probability": cell_nondegenerate_probability,
        "block_convergence_rates": block_rates,
        "analytic_block_rates": analytic_rates,
        "minimum_convergence_rate": minimum_rate,
        "target": target,
        "convergence_pass": minimum_rate >= target,
    }


def run_selection(
    *,
    root: Path = ROOT,
    method_config_path: Path | None = None,
) -> dict[str, Any]:
    config_path = method_config_path or (root / "configs/wp9c_repetition_selection.json")
    config = _load(config_path)
    campaign = _load(root / "configs/wp9_campaign_design.json")
    validate_method_config(config, campaign)
    anchors = load_balanced_anchor_records(root, config)
    extreme = extreme_laplace_binary_probability(anchors)

    candidate_rows = []
    recommended = None
    for candidate_raw in config["candidate_valid_repetitions_per_cell"]:
        candidate = int(candidate_raw)
        empirical = empirical_precision_for_candidate(
            anchors=anchors,
            config=config,
            candidate=candidate,
        )
        sensitivity = conservative_precision_for_candidate(
            anchors=anchors,
            config=config,
            candidate=candidate,
        )
        stability = model_stability_for_candidate(
            extreme_probability=float(extreme["extreme_probability"]),
            config=config,
            candidate=candidate,
        )
        overall = (
            empirical["nonstructural_precision_pass"]
            and sensitivity["precision_pass"]
            and stability["convergence_pass"]
        )
        candidate_rows.append(
            {
                "candidate_valid_repetitions_per_cell": candidate,
                "candidate_total_valid_executions": int(
                    config["candidate_total_valid_executions"][str(candidate)]
                ),
                "empirical": empirical,
                "conservative_sensitivity": sensitivity,
                "model_stability": stability,
                "selection_gate_pass": overall,
            }
        )
        if overall and recommended is None:
            recommended = candidate

    return {
        "schema": 1,
        "decision_id": "R-050",
        "classification": (
            "WP9C_REPETITION_CANDIDATE_IDENTIFIED"
            if recommended is not None
            else "WP9C_NO_CANDIDATE_PASSES"
        ),
        "recommended_valid_repetitions_per_cell": recommended,
        "recommended_total_valid_executions": (
            None
            if recommended is None
            else int(config["candidate_total_valid_executions"][str(recommended)])
        ),
        "candidate_results": candidate_rows,
        "binary_sensitivity_envelope": extreme,
        "pilot_anchor_count": len(anchors),
        "pilot_anchor_repetitions_each": len(next(iter(anchors.values()))),
        "selection_method_frozen": True,
        "selection_result_reviewed": False,
        "repetition_count_frozen": False,
        "runtime_execution_performed": False,
        "campaign_seed_consumed": False,
        "campaign_data_generated": False,
        "final_campaign_execution_authorized": False,
    }


def _print_summary(result: dict[str, Any]) -> None:
    print("WP9C_REPETITION_SELECTION=PASS")
    print("classification=" + result["classification"])
    recommendation = result["recommended_valid_repetitions_per_cell"]
    print(
        "recommended_valid_repetitions_per_cell="
        + ("none" if recommendation is None else str(recommendation))
    )
    total = result["recommended_total_valid_executions"]
    print(
        "recommended_total_valid_executions="
        + ("none" if total is None else str(total))
    )
    for row in result["candidate_results"]:
        candidate = row["candidate_valid_repetitions_per_cell"]
        empirical = row["empirical"]
        sensitivity = row["conservative_sensitivity"]
        stability = row["model_stability"]
        print(
            f"candidate_{candidate}="
            f"overall_{str(row['selection_gate_pass']).lower()},"
            f"empirical_{str(empirical['nonstructural_precision_pass']).lower()},"
            f"sensitivity_{str(sensitivity['precision_pass']).lower()},"
            f"model_{str(stability['convergence_pass']).lower()},"
            f"model_rate_{stability['minimum_convergence_rate']:.4f},"
            f"structural_deferred_{empirical['structural_endpoint_count']}"
        )
    print("selection_method_frozen=true")
    print("selection_result_reviewed=false")
    print("repetition_count_frozen=false")
    print("runtime_execution_performed=false")
    print("campaign_seed_consumed=false")
    print("campaign_data_generated=false")
    print("final_campaign_execution_authorized=false")


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)

    validate = sub.add_parser("validate-method")
    validate.add_argument("--config", default=str(DEFAULT_CONFIG))

    select = sub.add_parser("select")
    select.add_argument("--config", default=str(DEFAULT_CONFIG))
    select.add_argument("--output-json")

    args = parser.parse_args()
    config_path = Path(args.config)
    if args.command == "validate-method":
        config = _load(config_path)
        campaign = _load(CAMPAIGN_CONFIG)
        validate_method_config(config, campaign)
        print("WP9C_REPETITION_METHOD=PASS")
        print("runtime_execution_performed=false")
        print("campaign_seed_consumed=false")
        print("campaign_data_generated=false")
        print("repetition_count_frozen=false")
        print("final_campaign_execution_authorized=false")
        return 0

    result = run_selection(root=ROOT, method_config_path=config_path)
    if args.output_json:
        Path(args.output_json).write_text(
            json.dumps(result, sort_keys=True, indent=2) + "\n",
            encoding="utf-8",
        )
    _print_summary(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
