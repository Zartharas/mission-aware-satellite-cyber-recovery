from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from fractions import Fraction
from itertools import combinations, product
from pathlib import Path

DATA = Path("study8/results/S8-PQC-ICR-001/canonical_observations.csv")
OUT = Path("study8/analysis/results/primary_findings.json")
EXPECTED_SHA256 = "cfc65b6663be4e9f17a00ed102730f8642efcbbd844045acce032ff09a0bcabf"
PLAN_ID = "S8-SAP-001"
EXPERIMENT_ID = "S8-PQC-ICR-001"

PROFILES = ["PROFILE_512_44", "PROFILE_768_65", "PROFILE_1024_87"]
POLICIES = ["P0_HARD_CUTOVER", "P1_STAGED_CUTOVER", "P2_HYBRID_OVERLAP", "P3_CONTACT_AWARE_STAGED"]
REGIMES = ["R1_FREQUENT_SMALL", "R2_PERIODIC_MEDIUM", "R3_SPARSE_LARGE", "R4_CLUSTERED_MEDIUM"]
DISRUPTIONS = ["A0_NONE", "A1_DROP_FIRST_LARGEST_OBJECT_FRAGMENT", "A2_DELAY_FIRST_TRANSITION_PROOF_ONE_CONTACT", "A3_STALE_EPOCH_REPLAY_AT_COMMIT"]
PHASES = [0, 1, 2, 3, 4, 5]
DEADLINES = [12, 24, 48]
EXPECTED_ROWS = 3456

NUMERIC_SECONDARY = [
    "contacts_consumed",
    "cryptographic_bytes_transferred",
    "transition_attempts",
    "legacy_exposure_slots",
    "control_unavailable_slots",
]
BINARY_SECONDARY = ["rollback_invoked", "stale_epoch_acceptance"]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_bool(value: str) -> int:
    x = value.strip().lower()
    if x in {"1", "true", "yes"}:
        return 1
    if x in {"0", "false", "no"}:
        return 0
    raise ValueError(f"invalid boolean: {value!r}")


def parse_optional_int(value: str):
    x = value.strip()
    if x == "":
        return None
    return int(x)


def frac_parts(fr: Fraction) -> dict:
    return {
        "numerator": fr.numerator,
        "denominator": fr.denominator,
        "fraction": f"{fr.numerator}/{fr.denominator}",
        "decimal_6": f"{float(fr):.6f}",
    }


def proportion_record(successes: int, total: int) -> dict:
    d = {"successes": successes, "total": total}
    d.update(frac_parts(Fraction(successes, total)))
    return d


def difference_record(left_success: int, left_total: int, right_success: int, right_total: int) -> dict:
    fr = Fraction(left_success, left_total) - Fraction(right_success, right_total)
    d = {
        "left_successes": left_success,
        "left_total": left_total,
        "right_successes": right_success,
        "right_total": right_total,
    }
    d.update(frac_parts(fr))
    d["percentage_points_6"] = f"{float(fr) * 100:.6f}"
    return d


def median_fraction(values: list[int]) -> Fraction:
    vals = sorted(values)
    n = len(vals)
    if n == 0:
        raise ValueError("median of empty list")
    if n % 2:
        return Fraction(vals[n // 2], 1)
    return Fraction(vals[n // 2 - 1] + vals[n // 2], 2)


def numeric_summary(values: list[int]) -> dict:
    if not values:
        return {"n": 0}
    total = sum(values)
    mean = Fraction(total, len(values))
    med = median_fraction(values)
    return {
        "n": len(values),
        "sum": total,
        "mean": frac_parts(mean),
        "median": frac_parts(med),
        "min": min(values),
        "max": max(values),
    }


def load_rows() -> list[dict]:
    if sha256(DATA) != EXPECTED_SHA256:
        raise SystemExit("canonical dataset SHA-256 mismatch")
    rows = []
    with DATA.open(newline="", encoding="utf-8") as f:
        for raw in csv.DictReader(f):
            row = dict(raw)
            row["phase_offset"] = int(row["phase_offset"])
            row["deadline"] = int(row["deadline"])
            row["trusted_recovery_success"] = parse_bool(row["trusted_recovery_success"])
            row["recovery_completion_slot"] = parse_optional_int(row["recovery_completion_slot"])
            for field in NUMERIC_SECONDARY + ["dual_epoch_overlap_slots", "proof_accepted_slot", "commit_slot"]:
                row[field] = parse_optional_int(row[field])
            for field in BINARY_SECONDARY:
                row[field] = parse_bool(row[field])
            rows.append(row)
    return rows


def validate_population(rows: list[dict]) -> dict:
    if len(rows) != EXPECTED_ROWS:
        raise AssertionError((len(rows), EXPECTED_ROWS))
    ids = [r["observation_id"] for r in rows]
    if len(set(ids)) != EXPECTED_ROWS:
        raise AssertionError("observation_id not unique")

    observed = Counter(
        (r["profile"], r["policy"], r["regime"], r["disruption"], r["phase_offset"], r["deadline"])
        for r in rows
    )
    expected = {
        key
        for key in product(PROFILES, POLICIES, REGIMES, DISRUPTIONS, PHASES, DEADLINES)
    }
    if set(observed) != expected or any(v != 1 for v in observed.values()):
        raise AssertionError("factor lattice mismatch")

    policy_counts = Counter(r["policy"] for r in rows)
    if policy_counts != Counter({p: 864 for p in POLICIES}):
        raise AssertionError(policy_counts)

    if any(r["trusted_recovery_success"] not in {0, 1} for r in rows):
        raise AssertionError("nonbinary primary endpoint")
    for r in rows:
        if r["trusted_recovery_success"] == 1 and r["recovery_completion_slot"] is None:
            raise AssertionError("success missing completion slot")
        if r["policy"] != "P2_HYBRID_OVERLAP" and (r["dual_epoch_overlap_slots"] or 0) != 0:
            raise AssertionError("non-P2 dual epoch overlap nonzero")

    return {
        "row_count": len(rows),
        "unique_observation_ids": len(set(ids)),
        "unique_factor_positions": len(observed),
        "policy_counts": dict(sorted(policy_counts.items())),
        "canonical_sha256": sha256(DATA),
        "full_cartesian_lattice_exact": True,
        "non_p2_dual_epoch_overlap_zero": True,
    }


def success_by(rows: list[dict], field: str) -> dict:
    out = {}
    for level in sorted({r[field] for r in rows}, key=str):
        subset = [r for r in rows if r[field] == level]
        successes = sum(r["trusted_recovery_success"] for r in subset)
        out[str(level)] = proportion_record(successes, len(subset))
    return out


def policy_success(rows: list[dict]) -> dict:
    out = {}
    for policy in POLICIES:
        subset = [r for r in rows if r["policy"] == policy]
        out[policy] = proportion_record(sum(r["trusted_recovery_success"] for r in subset), len(subset))
    return out


def all_policy_contrasts(ps: dict) -> list[dict]:
    out = []
    for left, right in combinations(POLICIES, 2):
        lr = ps[left]
        rr = ps[right]
        rec = {"left": left, "right": right}
        rec.update(difference_record(lr["successes"], lr["total"], rr["successes"], rr["total"]))
        out.append(rec)
    return out


def stratified_primary(rows: list[dict]) -> dict:
    result = {}
    for field in ["regime", "profile", "disruption", "deadline"]:
        strata = {}
        levels = sorted({r[field] for r in rows}, key=str)
        for level in levels:
            x = [r for r in rows if r[field] == level]
            p3 = [r for r in x if r["policy"] == "P3_CONTACT_AWARE_STAGED"]
            p1 = [r for r in x if r["policy"] == "P1_STAGED_CUTOVER"]
            p3s = sum(r["trusted_recovery_success"] for r in p3)
            p1s = sum(r["trusted_recovery_success"] for r in p1)
            strata[str(level)] = {
                "P3": proportion_record(p3s, len(p3)),
                "P1": proportion_record(p1s, len(p1)),
                "P3_minus_P1": difference_record(p3s, len(p3), p1s, len(p1)),
            }
        result[field] = strata
    return result


def profile_analysis(rows: list[dict]) -> dict:
    profile_success = success_by(rows, "profile")
    contrasts = []
    for left, right in [
        ("PROFILE_768_65", "PROFILE_512_44"),
        ("PROFILE_1024_87", "PROFILE_512_44"),
        ("PROFILE_1024_87", "PROFILE_768_65"),
    ]:
        l = profile_success[left]
        r = profile_success[right]
        rec = {"left": left, "right": right}
        rec.update(difference_record(l["successes"], l["total"], r["successes"], r["total"]))
        contrasts.append(rec)

    by_position = defaultdict(dict)
    for r in rows:
        key = (r["policy"], r["regime"], r["disruption"], r["phase_offset"], r["deadline"])
        by_position[key][r["profile"]] = r["trusted_recovery_success"]

    patterns = Counter()
    non_increasing = 0
    for values in by_position.values():
        seq = tuple(values[p] for p in PROFILES)
        pattern = "".join(map(str, seq))
        patterns[pattern] += 1
        if seq[0] >= seq[1] >= seq[2]:
            non_increasing += 1

    return {
        "marginal_success_by_profile": profile_success,
        "contrasts": contrasts,
        "paired_ordered_profile_check": {
            "positions": len(by_position),
            "non_increasing_success_pattern_count": non_increasing,
            "non_increasing_success_pattern_proportion": proportion_record(non_increasing, len(by_position)),
            "pattern_counts": dict(sorted(patterns.items())),
        },
    }


def secondary_analysis(rows: list[dict]) -> dict:
    out = {}
    for policy in POLICIES:
        subset = [r for r in rows if r["policy"] == policy]
        success_rows = [r for r in subset if r["trusted_recovery_success"] == 1]
        rec = {
            "recovery_completion_slot_successes_only": numeric_summary(
                [r["recovery_completion_slot"] for r in success_rows]
            )
        }
        for field in NUMERIC_SECONDARY:
            vals = [r[field] for r in subset]
            if any(v is None for v in vals):
                raise AssertionError(f"missing {field}")
            rec[field] = numeric_summary(vals)
        dual_vals = [r["dual_epoch_overlap_slots"] for r in subset]
        if any(v is None for v in dual_vals):
            raise AssertionError("missing dual_epoch_overlap_slots")
        rec["dual_epoch_overlap_slots"] = numeric_summary(dual_vals)
        for field in BINARY_SECONDARY:
            count = sum(r[field] for r in subset)
            rec[field] = proportion_record(count, len(subset))
        term = Counter(r["terminal_state"] for r in subset)
        rec["terminal_state"] = {
            state: proportion_record(count, len(subset))
            for state, count in sorted(term.items())
        }
        out[policy] = rec
    return out


def main() -> None:
    rows = load_rows()
    validation = validate_population(rows)
    ps = policy_success(rows)
    p3 = ps["P3_CONTACT_AWARE_STAGED"]
    p1 = ps["P1_STAGED_CUTOVER"]

    findings = {
        "schema": 1,
        "experiment_id": EXPERIMENT_ID,
        "plan_id": PLAN_ID,
        "source_dataset": str(DATA),
        "source_dataset_sha256": EXPECTED_SHA256,
        "population_semantics": "complete_deterministic_finite_population",
        "inference_policy": {
            "sampling_p_values": False,
            "sampling_confidence_intervals": False,
            "bootstrap": False,
            "permutation_tests": False,
        },
        "population_validation": validation,
        "primary": {
            "policy_success": ps,
            "P3_minus_P1_success_risk_difference": difference_record(
                p3["successes"], p3["total"], p1["successes"], p1["total"]
            ),
        },
        "supporting_policy_contrasts": all_policy_contrasts(ps),
        "stratified_P3_minus_P1": stratified_primary(rows),
        "cryptographic_profile_analysis": profile_analysis(rows),
        "secondary_by_policy": secondary_analysis(rows),
        "claim_boundary": "modeled logical contact/recovery behavior and standardized cryptographic-object byte budgets only",
        "statistical_findings_frozen": False,
        "results_merge_authorized": False,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(findings, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"phase8_primary_statistics_rows={len(rows)}")
    print(f"phase8_primary_findings_sha256={sha256(OUT)}")


if __name__ == "__main__":
    main()
