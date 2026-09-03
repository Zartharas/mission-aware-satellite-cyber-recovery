from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import Counter
from itertools import combinations, product
from pathlib import Path

DATASET = Path("study8/results/S8-PQC-ICR-001/canonical_observations.csv")
OUTPUT = Path("study8/analysis/results/independent_findings.json")
EXPECTED_DIGEST = "cfc65b6663be4e9f17a00ed102730f8642efcbbd844045acce032ff09a0bcabf"
EXPERIMENT_ID = "S8-PQC-ICR-001"
PLAN_ID = "S8-SAP-001"

PROFILE_ORDER = ("PROFILE_512_44", "PROFILE_768_65", "PROFILE_1024_87")
POLICY_ORDER = ("P0_HARD_CUTOVER", "P1_STAGED_CUTOVER", "P2_HYBRID_OVERLAP", "P3_CONTACT_AWARE_STAGED")
REGIME_ORDER = ("R1_FREQUENT_SMALL", "R2_PERIODIC_MEDIUM", "R3_SPARSE_LARGE", "R4_CLUSTERED_MEDIUM")
DISRUPTION_ORDER = (
    "A0_NONE",
    "A1_DROP_FIRST_LARGEST_OBJECT_FRAGMENT",
    "A2_DELAY_FIRST_TRANSITION_PROOF_ONE_CONTACT",
    "A3_STALE_EPOCH_REPLAY_AT_COMMIT",
)
PHASE_ORDER = (0, 1, 2, 3, 4, 5)
DEADLINE_ORDER = (12, 24, 48)
COUNT = 3456

NUMERIC_FIELDS = (
    "contacts_consumed",
    "cryptographic_bytes_transferred",
    "transition_attempts",
    "legacy_exposure_slots",
    "control_unavailable_slots",
)
FLAG_FIELDS = ("rollback_invoked", "stale_epoch_acceptance")


def digest(path: Path) -> str:
    obj = hashlib.sha256()
    obj.update(path.read_bytes())
    return obj.hexdigest()


def b01(text: str) -> int:
    v = text.strip().casefold()
    table = {"1": 1, "true": 1, "yes": 1, "0": 0, "false": 0, "no": 0}
    if v not in table:
        raise AssertionError(f"bad bool {text!r}")
    return table[v]


def maybe_int(text: str):
    s = text.strip()
    return None if not s else int(s)


def reduced(numerator: int, denominator: int) -> tuple[int, int]:
    if denominator == 0:
        raise ZeroDivisionError
    g = math.gcd(abs(numerator), abs(denominator))
    numerator //= g
    denominator //= g
    if denominator < 0:
        numerator = -numerator
        denominator = -denominator
    return numerator, denominator


def ratio_record(numerator: int, denominator: int) -> dict:
    n, d = reduced(numerator, denominator)
    return {
        "numerator": n,
        "denominator": d,
        "fraction": f"{n}/{d}",
        "decimal_6": f"{n / d:.6f}",
    }


def prop_record(successes: int, total: int) -> dict:
    ans = {"successes": successes, "total": total}
    ans.update(ratio_record(successes, total))
    return ans


def diff_record(ls: int, lt: int, rs: int, rt: int) -> dict:
    num = ls * rt - rs * lt
    den = lt * rt
    n, d = reduced(num, den)
    return {
        "left_successes": ls,
        "left_total": lt,
        "right_successes": rs,
        "right_total": rt,
        "numerator": n,
        "denominator": d,
        "fraction": f"{n}/{d}",
        "decimal_6": f"{n / d:.6f}",
        "percentage_points_6": f"{(n / d) * 100:.6f}",
    }


def exact_median(vals: list[int]) -> tuple[int, int]:
    seq = sorted(vals)
    if not seq:
        raise AssertionError("empty median")
    k = len(seq)
    if k % 2:
        return seq[k // 2], 1
    return reduced(seq[k // 2 - 1] + seq[k // 2], 2)


def describe(vals: list[int]) -> dict:
    if not vals:
        return {"n": 0}
    total = sum(vals)
    mn, md = exact_median(vals)
    return {
        "n": len(vals),
        "sum": total,
        "mean": ratio_record(total, len(vals)),
        "median": {**ratio_record(mn, md)},
        "min": min(vals),
        "max": max(vals),
    }


def read_table() -> list[dict]:
    if digest(DATASET) != EXPECTED_DIGEST:
        raise AssertionError("dataset digest differs")
    with DATASET.open("r", newline="", encoding="utf-8") as handle:
        raw = list(csv.DictReader(handle))
    converted = []
    for r in raw:
        item = dict(r)
        item["phase_offset"] = int(item["phase_offset"])
        item["deadline"] = int(item["deadline"])
        item["trusted_recovery_success"] = b01(item["trusted_recovery_success"])
        item["recovery_completion_slot"] = maybe_int(item["recovery_completion_slot"])
        for name in NUMERIC_FIELDS + ("dual_epoch_overlap_slots", "proof_accepted_slot", "commit_slot"):
            item[name] = maybe_int(item[name])
        for name in FLAG_FIELDS:
            item[name] = b01(item[name])
        converted.append(item)
    return converted


def finite_population_validation(records: list[dict]) -> dict:
    if len(records) != COUNT:
        raise AssertionError("wrong row count")
    ids = {r["observation_id"] for r in records}
    if len(ids) != COUNT:
        raise AssertionError("duplicate observation id")

    keys = [
        (r["profile"], r["policy"], r["regime"], r["disruption"], r["phase_offset"], r["deadline"])
        for r in records
    ]
    if len(set(keys)) != COUNT:
        raise AssertionError("duplicate factor position")
    target = set(product(PROFILE_ORDER, POLICY_ORDER, REGIME_ORDER, DISRUPTION_ORDER, PHASE_ORDER, DEADLINE_ORDER))
    if set(keys) != target:
        raise AssertionError("incomplete factor lattice")

    pc = Counter(r["policy"] for r in records)
    if any(pc[p] != 864 for p in POLICY_ORDER):
        raise AssertionError("policy imbalance")
    for r in records:
        if r["trusted_recovery_success"] not in (0, 1):
            raise AssertionError("primary not binary")
        if r["trusted_recovery_success"] and r["recovery_completion_slot"] is None:
            raise AssertionError("successful row without completion")
        if r["policy"] != "P2_HYBRID_OVERLAP" and (r["dual_epoch_overlap_slots"] or 0) != 0:
            raise AssertionError("overlap outside P2")

    return {
        "row_count": len(records),
        "unique_observation_ids": len(ids),
        "unique_factor_positions": len(set(keys)),
        "policy_counts": dict(sorted(pc.items())),
        "canonical_sha256": digest(DATASET),
        "full_cartesian_lattice_exact": True,
        "non_p2_dual_epoch_overlap_zero": True,
    }


def filter_rows(records: list[dict], **where) -> list[dict]:
    return [r for r in records if all(r[k] == v for k, v in where.items())]


def success_summary(records: list[dict], field: str) -> dict:
    levels = sorted({r[field] for r in records}, key=str)
    result = {}
    for level in levels:
        rows = filter_rows(records, **{field: level})
        result[str(level)] = prop_record(sum(r["trusted_recovery_success"] for r in rows), len(rows))
    return result


def policy_summary(records: list[dict]) -> dict:
    result = {}
    for p in POLICY_ORDER:
        rows = filter_rows(records, policy=p)
        result[p] = prop_record(sum(r["trusted_recovery_success"] for r in rows), len(rows))
    return result


def contrasts_from_policy(summary: dict) -> list[dict]:
    ans = []
    for left, right in combinations(POLICY_ORDER, 2):
        a, b = summary[left], summary[right]
        item = {"left": left, "right": right}
        item.update(diff_record(a["successes"], a["total"], b["successes"], b["total"]))
        ans.append(item)
    return ans


def p3_p1_strata(records: list[dict]) -> dict:
    result = {}
    for field in ("regime", "profile", "disruption", "deadline"):
        layer = {}
        for level in sorted({r[field] for r in records}, key=str):
            subset = filter_rows(records, **{field: level})
            p3 = filter_rows(subset, policy="P3_CONTACT_AWARE_STAGED")
            p1 = filter_rows(subset, policy="P1_STAGED_CUTOVER")
            s3 = sum(x["trusted_recovery_success"] for x in p3)
            s1 = sum(x["trusted_recovery_success"] for x in p1)
            layer[str(level)] = {
                "P3": prop_record(s3, len(p3)),
                "P1": prop_record(s1, len(p1)),
                "P3_minus_P1": diff_record(s3, len(p3), s1, len(p1)),
            }
        result[field] = layer
    return result


def profile_section(records: list[dict]) -> dict:
    marginal = success_summary(records, "profile")
    requested = (
        ("PROFILE_768_65", "PROFILE_512_44"),
        ("PROFILE_1024_87", "PROFILE_512_44"),
        ("PROFILE_1024_87", "PROFILE_768_65"),
    )
    pairwise = []
    for left, right in requested:
        a, b = marginal[left], marginal[right]
        row = {"left": left, "right": right}
        row.update(diff_record(a["successes"], a["total"], b["successes"], b["total"]))
        pairwise.append(row)

    slots = {}
    for r in records:
        key = (r["policy"], r["regime"], r["disruption"], r["phase_offset"], r["deadline"])
        slots.setdefault(key, {})[r["profile"]] = r["trusted_recovery_success"]
    patterns = Counter()
    ordered = 0
    for values in slots.values():
        seq = tuple(values[p] for p in PROFILE_ORDER)
        patterns["".join(str(x) for x in seq)] += 1
        if seq[0] >= seq[1] >= seq[2]:
            ordered += 1

    return {
        "marginal_success_by_profile": marginal,
        "contrasts": pairwise,
        "paired_ordered_profile_check": {
            "positions": len(slots),
            "non_increasing_success_pattern_count": ordered,
            "non_increasing_success_pattern_proportion": prop_record(ordered, len(slots)),
            "pattern_counts": dict(sorted(patterns.items())),
        },
    }


def secondary_section(records: list[dict]) -> dict:
    result = {}
    for p in POLICY_ORDER:
        rows = filter_rows(records, policy=p)
        successes = [r for r in rows if r["trusted_recovery_success"] == 1]
        section = {
            "recovery_completion_slot_successes_only": describe(
                [r["recovery_completion_slot"] for r in successes]
            )
        }
        for name in NUMERIC_FIELDS:
            vals = [r[name] for r in rows]
            if any(v is None for v in vals):
                raise AssertionError(f"missing {name}")
            section[name] = describe(vals)
        overlaps = [r["dual_epoch_overlap_slots"] for r in rows]
        if any(v is None for v in overlaps):
            raise AssertionError("missing overlap")
        section["dual_epoch_overlap_slots"] = describe(overlaps)
        for name in FLAG_FIELDS:
            yes = sum(r[name] for r in rows)
            section[name] = prop_record(yes, len(rows))
        tc = Counter(r["terminal_state"] for r in rows)
        section["terminal_state"] = {
            label: prop_record(number, len(rows))
            for label, number in sorted(tc.items())
        }
        result[p] = section
    return result


def main() -> None:
    records = read_table()
    validation = finite_population_validation(records)
    policies = policy_summary(records)
    left = policies["P3_CONTACT_AWARE_STAGED"]
    right = policies["P1_STAGED_CUTOVER"]

    output = {
        "schema": 1,
        "experiment_id": EXPERIMENT_ID,
        "plan_id": PLAN_ID,
        "source_dataset": str(DATASET),
        "source_dataset_sha256": EXPECTED_DIGEST,
        "population_semantics": "complete_deterministic_finite_population",
        "inference_policy": {
            "sampling_p_values": False,
            "sampling_confidence_intervals": False,
            "bootstrap": False,
            "permutation_tests": False,
        },
        "population_validation": validation,
        "primary": {
            "policy_success": policies,
            "P3_minus_P1_success_risk_difference": diff_record(
                left["successes"], left["total"], right["successes"], right["total"]
            ),
        },
        "supporting_policy_contrasts": contrasts_from_policy(policies),
        "stratified_P3_minus_P1": p3_p1_strata(records),
        "cryptographic_profile_analysis": profile_section(records),
        "secondary_by_policy": secondary_section(records),
        "claim_boundary": "modeled logical contact/recovery behavior and standardized cryptographic-object byte budgets only",
        "statistical_findings_frozen": False,
        "results_merge_authorized": False,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"phase8_independent_statistics_rows={len(records)}")
    print(f"phase8_independent_findings_sha256={digest(OUTPUT)}")


if __name__ == "__main__":
    main()
