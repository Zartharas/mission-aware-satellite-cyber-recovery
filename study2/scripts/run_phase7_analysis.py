#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import random
import sys
import zipfile
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "study2" / "src"))

from study2_security.cell_matrix import materialize_cell_matrix, matrix_sha256  # noqa: E402

EXPECTED_ZIP_SHA256 = "195860bd44b38ccf170f02cb1cb392583217296d08640c99b18b52286403e133"
EXPECTED_OBSERVATIONS_SHA256 = "8dcc850c561d7e3c0bf7478263b534cae83cbbb55183c313e879dd7d61127854"
EXPECTED_LEDGER_SHA256 = "755d6541263ac31589934200ea5071cdbcacae1ea197d044bbd3e6f7f7d1dbc5"
EXPECTED_MANIFEST_SHA256 = "190612473717b7768ceccb4596a20d90cd7d532bf7581330ce94d609cb752e67"
EXPECTED_CELL_MATRIX_SHA256 = "5087e46f9d416fe5b741fedcb4b1a9d848342087c6e317614dec26a56c2dc081"
EXPECTED_VALID = 3872
EXPECTED_INVALID = 0
EXPECTED_CELLS = 85
TAU = 240.0
Z95 = 1.959963984540054
BOOTSTRAP_REPLICATES = 20000

PRIMARY_ENDPOINTS: dict[str, tuple[str, str]] = {
    "unsafe_permissive_response_rate": ("binary", "lower"),
    "false_conservative_response_rate": ("binary", "lower"),
    "evidence_qualified_trusted_recovery": ("binary", "higher"),
    "recovery_rmst_s": ("continuous", "lower"),
    "residual_unauthorized_state": ("binary", "lower"),
    "legitimate_command_rejection_rate": ("binary", "lower"),
}
SECONDARY_ENDPOINTS: dict[str, tuple[str, str]] = {
    "time_to_containment_s": ("continuous", "lower"),
    "ground_spacecraft_state_divergence": ("binary", "lower"),
    "response_selection_stability": ("binary", "higher"),
}
ALL_SCALAR_ENDPOINTS = {**PRIMARY_ENDPOINTS, **SECONDARY_ENDPOINTS}


def canonical_json_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def fail(message: str) -> None:
    raise SystemExit(f"PHASE7_FAIL_CLOSED: {message}")


def bootstrap_seed(estimand_id: str) -> int:
    digest = hashlib.sha256(("S2-P7-BOOTSTRAP|" + estimand_id).encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big")


def percentile(sorted_values: list[float], p: float) -> float:
    if not sorted_values:
        fail("percentile requested for empty sample")
    h = (len(sorted_values) - 1) * p
    lo = int(math.floor(h))
    hi = int(math.ceil(h))
    if lo == hi:
        return sorted_values[lo]
    return sorted_values[lo] + (h - lo) * (sorted_values[hi] - sorted_values[lo])


def bootstrap_mean_ci(values: list[float], estimand_id: str) -> tuple[float, float]:
    if not values:
        fail(f"empty bootstrap sample for {estimand_id}")
    rng = random.Random(bootstrap_seed(estimand_id))
    n = len(values)
    means: list[float] = []
    for _ in range(BOOTSTRAP_REPLICATES):
        means.append(sum(values[rng.randrange(n)] for _ in range(n)) / n)
    means.sort()
    return percentile(means, 0.025), percentile(means, 0.975)


def wilson_ci(events: int, n: int) -> tuple[float, float]:
    if n <= 0:
        fail("Wilson interval requested with n<=0")
    p = events / n
    z2 = Z95 * Z95
    denom = 1.0 + z2 / n
    center = (p + z2 / (2.0 * n)) / denom
    half = Z95 * math.sqrt((p * (1.0 - p) / n) + (z2 / (4.0 * n * n))) / denom
    return max(0.0, center - half), min(1.0, center + half)


def sign_test_p(values: list[float], eps: float = 1e-12) -> float:
    nz = [v for v in values if abs(v) > eps]
    n = len(nz)
    if n == 0:
        return 1.0
    positive = sum(v > 0 for v in nz)
    tail = min(positive, n - positive)
    prob = sum(math.comb(n, k) for k in range(tail + 1)) / (2 ** n)
    return min(1.0, 2.0 * prob)


def holm_adjust(rows: list[dict[str, Any]], p_key: str = "p_raw") -> None:
    indexed = [(i, float(row[p_key])) for i, row in enumerate(rows)]
    ordered = sorted(indexed, key=lambda x: (x[1], x[0]))
    m = len(ordered)
    previous = 0.0
    adjusted: dict[int, float] = {}
    for rank0, (idx, p) in enumerate(ordered):
        multiplier = m - rank0
        value = min(1.0, multiplier * p)
        value = max(previous, value)
        previous = value
        adjusted[idx] = value
    for i, row in enumerate(rows):
        row["p_holm"] = adjusted[i]


def endpoint_value(obs: dict[str, Any], endpoint: str) -> float:
    if endpoint == "unsafe_permissive_response_rate":
        return float(bool(obs["adjudication_only"]["unsafe_permissive"]))
    if endpoint == "false_conservative_response_rate":
        return float(bool(obs["adjudication_only"]["false_conservative"]))
    if endpoint == "evidence_qualified_trusted_recovery":
        recovered = bool(obs["evidence_qualified_trusted_recovery"])
        t = obs["time_to_evidence_qualified_trusted_recovery_s"]
        censored = bool(obs["time_to_recovery_right_censored"])
        if recovered:
            if t is None or censored:
                fail(f"inconsistent recovery event fields for {obs['trial_id']}")
            if not 0.0 <= float(t) <= TAU:
                fail(f"recovery time outside frozen horizon for {obs['trial_id']}")
        else:
            if t is not None or not censored:
                fail(f"inconsistent recovery censor fields for {obs['trial_id']}")
        return float(recovered)
    if endpoint == "recovery_rmst_s":
        recovered = bool(obs["evidence_qualified_trusted_recovery"])
        if recovered:
            return min(float(obs["time_to_evidence_qualified_trusted_recovery_s"]), TAU)
        return TAU
    if endpoint == "residual_unauthorized_state":
        return float(bool(obs["adjudication_only"]["residual_unauthorized_state"]))
    if endpoint == "legitimate_command_rejection_rate":
        return float(bool(obs["adjudication_only"]["legitimate_command_rejected"]))
    if endpoint == "time_to_containment_s":
        return float(obs["time_to_containment_s"])
    if endpoint == "ground_spacecraft_state_divergence":
        return float(bool(obs["ground_spacecraft_state_divergence"]))
    if endpoint == "response_selection_stability":
        return float(bool(obs["response_selection_stability"]))
    fail(f"unknown endpoint {endpoint}")


def expected_seed_range(seed_set: str) -> list[int]:
    ranges = {
        "A96": (2100001, 2100096),
        "B32": (2200001, 2200032),
        "C32": (2300001, 2300032),
        "D32": (2400001, 2400032),
        "E32": (2500001, 2500032),
    }
    start, end = ranges[seed_set]
    return list(range(start, end + 1))


def read_jsonl(data: bytes) -> list[dict[str, Any]]:
    return [json.loads(line) for line in data.decode("utf-8").splitlines() if line.strip()]


def load_and_verify(zip_path: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any], dict[str, Any]]:
    if sha256_file(zip_path) != EXPECTED_ZIP_SHA256:
        fail("authoritative ZIP SHA-256 mismatch")

    with zipfile.ZipFile(zip_path, "r") as archive:
        required = {
            "attempt_ledger.jsonl",
            "evidence_hashes.json",
            "campaign_summary.json",
            "observations.jsonl",
            "runtime_bindings.json",
        }
        if set(archive.namelist()) != required:
            fail(f"unexpected artifact membership: {archive.namelist()}")
        raw = {name: archive.read(name) for name in required}

    evidence_hashes = json.loads(raw["evidence_hashes.json"])
    for filename, expected in evidence_hashes["files"].items():
        actual = sha256_bytes(raw[filename])
        if actual != expected:
            fail(f"internal evidence hash mismatch for {filename}")

    if sha256_bytes(raw["observations.jsonl"]) != EXPECTED_OBSERVATIONS_SHA256:
        fail("observations SHA-256 mismatch")
    if sha256_bytes(raw["attempt_ledger.jsonl"]) != EXPECTED_LEDGER_SHA256:
        fail("attempt ledger SHA-256 mismatch")

    summary = json.loads(raw["campaign_summary.json"])
    bindings = json.loads(raw["runtime_bindings.json"])
    observations = read_jsonl(raw["observations.jsonl"])
    ledger = read_jsonl(raw["attempt_ledger.jsonl"])

    if summary["trial_manifest_sha256"] != EXPECTED_MANIFEST_SHA256:
        fail("campaign summary trial-manifest hash mismatch")
    if not summary["campaign_complete"]:
        fail("campaign is not complete")
    if summary["valid_observations"] != EXPECTED_VALID or summary["invalid_attempts"] != EXPECTED_INVALID:
        fail("campaign summary count mismatch")
    if len(observations) != EXPECTED_VALID or len(ledger) != EXPECTED_VALID:
        fail("record count mismatch")
    if any(row["attempt_status"] != "VALID" for row in observations):
        fail("non-VALID observation present")
    if any(row["attempt_status"] != "VALID" for row in ledger):
        fail("non-VALID ledger attempt present")
    if len({row["trial_id"] for row in observations}) != EXPECTED_VALID:
        fail("duplicate observation trial_id")
    if len({row["run_id"] for row in observations}) != EXPECTED_VALID:
        fail("duplicate observation run_id")
    if len({row["trial_id"] for row in ledger}) != EXPECTED_VALID:
        fail("duplicate ledger trial_id")
    if len({row["run_id"] for row in ledger}) != EXPECTED_VALID:
        fail("duplicate ledger run_id")
    if any(bool(row["oracle_was_selector_input"]) for row in observations):
        fail("selector-oracle isolation violated")
    if any(bool(row["automatic_retry_allowed"]) for row in observations):
        fail("automatic retry unexpectedly allowed")
    if any(bool(row["automatic_next_trial_allowed"]) for row in observations):
        fail("automatic next-trial unexpectedly allowed")
    if any(float(row["censor_horizon_s"]) != TAU for row in observations):
        fail("censor horizon differs from frozen 240 logical seconds")
    if any(row["time_basis"] != "DETERMINISTIC_LOGICAL_SIL_TIME_NOT_WALL_CLOCK" for row in observations):
        fail("unexpected time basis")

    matrix = materialize_cell_matrix()
    if matrix_sha256(matrix) != EXPECTED_CELL_MATRIX_SHA256:
        fail("cell matrix hash mismatch")
    if len(matrix["cells"]) != EXPECTED_CELLS:
        fail("cell matrix count mismatch")

    expected_membership = []
    for cell in matrix["cells"]:
        expected_membership.extend((cell["cell_id"], seed) for seed in expected_seed_range(cell["seed_set"]))
    observed_membership = [(row["cell_id"], int(row["seed"])) for row in observations]
    ledger_membership = [(row["cell_id"], int(row["seed"])) for row in ledger]
    if observed_membership != expected_membership:
        fail("observation membership/order differs from frozen manifest")
    if ledger_membership != expected_membership:
        fail("ledger membership/order differs from frozen manifest")
    for obs_row, led_row in zip(observations, ledger):
        for key in ("cell_id", "seed", "trial_id", "run_id", "attempt_status"):
            if obs_row[key] != led_row[key]:
                fail(f"ledger/observation mismatch for {key}")

    return observations, ledger, summary, bindings


def pair_values(by_cell_seed: dict[str, dict[int, dict[str, Any]]], test_cell: str, reference_cell: str, endpoint: str) -> tuple[list[int], list[float], list[float], list[float]]:
    test = by_cell_seed[test_cell]
    ref = by_cell_seed[reference_cell]
    seeds_test = sorted(test)
    seeds_ref = sorted(ref)
    if seeds_test != seeds_ref:
        fail(f"pairing mismatch {test_cell} vs {reference_cell}")
    tv = [endpoint_value(test[s], endpoint) for s in seeds_test]
    rv = [endpoint_value(ref[s], endpoint) for s in seeds_test]
    diff = [a - b for a, b in zip(tv, rv)]
    return seeds_test, tv, rv, diff


def effect_row(*, contrast_id: str, endpoint: str, block: str, family: str, test_label: str, reference_label: str, differences: list[float], primary: bool, notes: str = "") -> dict[str, Any]:
    estimate = sum(differences) / len(differences)
    lo, hi = bootstrap_mean_ci(differences, contrast_id)
    row: dict[str, Any] = {
        "contrast_id": contrast_id,
        "block": block,
        "family": family,
        "endpoint": endpoint,
        "endpoint_role": "primary" if endpoint in PRIMARY_ENDPOINTS else "secondary",
        "favorable_direction": ALL_SCALAR_ENDPOINTS[endpoint][1],
        "test": test_label,
        "reference": reference_label,
        "n_pairs": len(differences),
        "estimate_test_minus_reference": estimate,
        "ci95_low": lo,
        "ci95_high": hi,
        "notes": notes,
    }
    if not primary:
        row["p_raw"] = sign_test_p(differences)
    return row


def slope4(y0: float, y1: float, y2: float, y3: float) -> float:
    ys = (y0, y1, y2, y3)
    xs = (0.0, 1.0, 2.0, 3.0)
    xbar = 1.5
    return sum((x - xbar) * y for x, y in zip(xs, ys)) / 5.0


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        fail(f"refusing to write empty table {path.name}")
    fieldnames: list[str] = []
    seen: set[str] = set()
    for row in rows:
        for key in row:
            if key not in seen:
                seen.add(key)
                fieldnames.append(key)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def analyze(observations: list[dict[str, Any]], output_dir: Path, spec_path: Path | None) -> dict[str, Any]:
    matrix = materialize_cell_matrix()
    cells = matrix["cells"]
    by_cell_seed: dict[str, dict[int, dict[str, Any]]] = {cell["cell_id"]: {} for cell in cells}
    for row in observations:
        by_cell_seed[row["cell_id"]][int(row["seed"])] = row

    cell_estimates: list[dict[str, Any]] = []
    terminal_counts: list[dict[str, Any]] = []
    for cell in cells:
        cid = cell["cell_id"]
        rows = [by_cell_seed[cid][seed] for seed in sorted(by_cell_seed[cid])]
        for endpoint, (etype, direction) in ALL_SCALAR_ENDPOINTS.items():
            values = [endpoint_value(row, endpoint) for row in rows]
            estimate = sum(values) / len(values)
            if etype == "binary":
                events = int(sum(values))
                lo, hi = wilson_ci(events, len(values))
            else:
                events = ""
                lo, hi = bootstrap_mean_ci(values, f"CELL|{cid}|{endpoint}")
            cell_estimates.append({
                "cell_id": cid,
                "block": cell["block"],
                "endpoint": endpoint,
                "endpoint_role": "primary" if endpoint in PRIMARY_ENDPOINTS else "secondary",
                "type": etype,
                "favorable_direction": direction,
                "n": len(values),
                "events": events,
                "estimate": estimate,
                "ci95_low": lo,
                "ci95_high": hi,
            })
        counts = Counter(row["recovery_terminal_state"] for row in rows)
        for state in sorted(counts):
            terminal_counts.append({
                "cell_id": cid,
                "block": cell["block"],
                "recovery_terminal_state": state,
                "count": counts[state],
                "n": len(rows),
                "proportion": counts[state] / len(rows),
            })

    primary_rows: list[dict[str, Any]] = []
    a_cells = [c for c in cells if c["block"] == "A_PRIMARY_EVIDENCE_MECHANISM"]
    a_lookup = {(c["evidence"], c["policy"]): c["cell_id"] for c in a_cells}
    a_policies = ("S2_B0_FAIL_CLOSED", "S2_B2_RISK_THRESHOLD", "S2_S1_EVIDENCE_AWARE")
    for endpoint in PRIMARY_ENDPOINTS:
        for policy in a_policies:
            base = a_lookup[("V0", policy)]
            for evidence in ("V1", "V2", "V3", "V4", "V5"):
                test = a_lookup[(evidence, policy)]
                _, _, _, diff = pair_values(by_cell_seed, test, base, endpoint)
                primary_rows.append(effect_row(
                    contrast_id=f"A_MECH|{endpoint}|{policy}|{evidence}-V0",
                    endpoint=endpoint,
                    block="A_PRIMARY_EVIDENCE_MECHANISM",
                    family="A_MECHANISM",
                    test_label=f"{evidence}/{policy}",
                    reference_label=f"V0/{policy}",
                    differences=diff,
                    primary=True,
                ))
        for evidence in ("V0", "V1", "V2", "V3", "V4", "V5"):
            s1 = a_lookup[(evidence, "S2_S1_EVIDENCE_AWARE")]
            for baseline in ("S2_B0_FAIL_CLOSED", "S2_B2_RISK_THRESHOLD"):
                ref = a_lookup[(evidence, baseline)]
                _, _, _, diff = pair_values(by_cell_seed, s1, ref, endpoint)
                primary_rows.append(effect_row(
                    contrast_id=f"A_POLICY|{endpoint}|{evidence}|S1-{baseline}",
                    endpoint=endpoint,
                    block="A_PRIMARY_EVIDENCE_MECHANISM",
                    family="A_POLICY",
                    test_label=f"{evidence}/S2_S1_EVIDENCE_AWARE",
                    reference_label=f"{evidence}/{baseline}",
                    differences=diff,
                    primary=True,
                ))

    secondary_rows: list[dict[str, Any]] = []
    holm_groups: dict[tuple[str, str], list[dict[str, Any]]] = {}

    def add_secondary(row: dict[str, Any], holm_family: str) -> None:
        row["holm_family"] = holm_family
        secondary_rows.append(row)
        holm_groups.setdefault((holm_family, row["endpoint"]), []).append(row)

    b_cells = [c for c in cells if c["block"] == "B_CONTACT_AUTHORIZATION"]
    b_lookup = {(c["contact"], c["policy"]): c["cell_id"] for c in b_cells}
    b_policies = ("S2_B0_FAIL_CLOSED", "S2_B1_FAIL_OPERATIONAL", "S2_B2_RISK_THRESHOLD", "S2_S1_EVIDENCE_AWARE")
    b_seeds = expected_seed_range("B32")
    for endpoint in ALL_SCALAR_ENDPOINTS:
        slopes_by_policy: dict[str, list[float]] = {}
        k4diff_by_policy: dict[str, list[float]] = {}
        for policy in b_policies:
            slopes: list[float] = []
            k4diffs: list[float] = []
            for seed in b_seeds:
                ys = [endpoint_value(by_cell_seed[b_lookup[(k, policy)]][seed], endpoint) for k in ("K0", "K1", "K2", "K3")]
                slopes.append(slope4(*ys))
                k4 = endpoint_value(by_cell_seed[b_lookup[("K4", policy)]][seed], endpoint)
                k4diffs.append(k4 - ys[0])
            slopes_by_policy[policy] = slopes
            k4diff_by_policy[policy] = k4diffs
            add_secondary(effect_row(
                contrast_id=f"B_ORDERED|{endpoint}|{policy}", endpoint=endpoint, block="B_CONTACT_AUTHORIZATION", family="B_ORDERED",
                test_label=f"{policy} K0-K3 slope", reference_label="zero slope", differences=slopes, primary=False,
                notes="per logical contact-severity step; K4 excluded from ordinal trend"), "B_ORDERED")
            add_secondary(effect_row(
                contrast_id=f"B_K4|{endpoint}|{policy}|K4-K0", endpoint=endpoint, block="B_CONTACT_AUTHORIZATION", family="B_K4",
                test_label=f"{policy} K4", reference_label=f"{policy} K0", differences=k4diffs, primary=False,
                notes="prespecified intermittent-contact contrast; K4 is not ordinal score 4"), "B_K4")
        for baseline in ("S2_B0_FAIL_CLOSED", "S2_B1_FAIL_OPERATIONAL", "S2_B2_RISK_THRESHOLD"):
            slope_diff = [a - b for a, b in zip(slopes_by_policy["S2_S1_EVIDENCE_AWARE"], slopes_by_policy[baseline])]
            add_secondary(effect_row(
                contrast_id=f"B_ORDERED_INT|{endpoint}|S1-{baseline}", endpoint=endpoint, block="B_CONTACT_AUTHORIZATION", family="B_ORDERED",
                test_label="S2_S1_EVIDENCE_AWARE K0-K3 slope", reference_label=f"{baseline} K0-K3 slope", differences=slope_diff, primary=False,
                notes="policy-by-contact interaction as difference in within-seed slopes"), "B_ORDERED")
            did = [a - b for a, b in zip(k4diff_by_policy["S2_S1_EVIDENCE_AWARE"], k4diff_by_policy[baseline])]
            add_secondary(effect_row(
                contrast_id=f"B_K4_INT|{endpoint}|S1-{baseline}", endpoint=endpoint, block="B_CONTACT_AUTHORIZATION", family="B_K4",
                test_label="S2_S1_EVIDENCE_AWARE K4-K0", reference_label=f"{baseline} K4-K0", differences=did, primary=False,
                notes="policy-by-intermittent-contact interaction as difference-in-differences"), "B_K4")

    c_cells = [c for c in cells if c["block"] == "C_FAULT_ATTACK_AMBIGUITY"]
    c_lookup = {(c["ambiguity_family"], c["cause"], c["policy"]): c["cell_id"] for c in c_cells}
    for endpoint in ALL_SCALAR_ENDPOINTS:
        for ambiguity_family in ("telemetry_loss", "state_inconsistency", "contact_or_authorization_loss"):
            for policy in ("S2_B0_FAIL_CLOSED", "S2_B1_FAIL_OPERATIONAL", "S2_S1_EVIDENCE_AWARE"):
                test = c_lookup[(ambiguity_family, "ADVERSARIAL", policy)]
                ref = c_lookup[(ambiguity_family, "BENIGN", policy)]
                _, _, _, diff = pair_values(by_cell_seed, test, ref, endpoint)
                add_secondary(effect_row(
                    contrast_id=f"C_AMBIG|{endpoint}|{ambiguity_family}|{policy}|ADV-BENIGN", endpoint=endpoint,
                    block="C_FAULT_ATTACK_AMBIGUITY", family="C_AMBIGUITY",
                    test_label=f"{ambiguity_family}/ADVERSARIAL/{policy}", reference_label=f"{ambiguity_family}/BENIGN/{policy}",
                    differences=diff, primary=False, notes="matched policy-visible ambiguity pair"), "C_AMBIGUITY")

    d_cells = [c for c in cells if c["block"] == "D_CONTEXT_ABLATION"]
    d_lookup = {(c["context"], c["selector"]): c["cell_id"] for c in d_cells}
    for endpoint in ALL_SCALAR_ENDPOINTS:
        for context in ("unauthorized_command", "update_recovery", "replay", "evidence_loss"):
            ref = d_lookup[(context, "S2_S1_EVIDENCE_AWARE")]
            for selector in ("PI_NO_MISSION", "PI_NO_EVIDENCE", "PI_NO_CONTACT", "PI_SECURITY_ONLY"):
                test = d_lookup[(context, selector)]
                _, _, _, diff = pair_values(by_cell_seed, test, ref, endpoint)
                add_secondary(effect_row(
                    contrast_id=f"D_ABL|{endpoint}|{context}|{selector}-S1", endpoint=endpoint, block="D_CONTEXT_ABLATION", family="D_ABLATION",
                    test_label=f"{context}/{selector}", reference_label=f"{context}/S2_S1_EVIDENCE_AWARE", differences=diff,
                    primary=False, notes="paired context ablation"), "D_ABLATION")

    e_cells = [c for c in cells if c["block"] == "E_ADVERSARY_BUDGET_STRESS"]
    e_lookup = {(c["adversary"], c["policy"]): c["cell_id"] for c in e_cells}
    e_seeds = expected_seed_range("E32")
    for endpoint in ALL_SCALAR_ENDPOINTS:
        for policy in a_policies:
            a1 = e_lookup[("A1", policy)]
            a2 = e_lookup[("A2", policy)]
            a3 = e_lookup[("A3", policy)]
            _, _, _, d21 = pair_values(by_cell_seed, a2, a1, endpoint)
            add_secondary(effect_row(
                contrast_id=f"E_STRESS|{endpoint}|{policy}|A2-A1", endpoint=endpoint, block="E_ADVERSARY_BUDGET_STRESS", family="E_STRESS",
                test_label=f"A2/K2/{policy}", reference_label=f"A1/K0/{policy}", differences=d21, primary=False,
                notes="A2 is explicitly contact-coupled; not an unconfounded adversary-only effect"), "E_STRESS")
            _, _, _, d31 = pair_values(by_cell_seed, a3, a1, endpoint)
            add_secondary(effect_row(
                contrast_id=f"E_STRESS|{endpoint}|{policy}|A3-A1", endpoint=endpoint, block="E_ADVERSARY_BUDGET_STRESS", family="E_STRESS",
                test_label=f"A3/K0/{policy}", reference_label=f"A1/K0/{policy}", differences=d31, primary=False,
                notes="same K0 contact; multi-source versus single-source partial compromise"), "E_STRESS")
            slopes: list[float] = []
            for seed in e_seeds:
                ys = [endpoint_value(by_cell_seed[e_lookup[(a, policy)]][seed], endpoint) for a in ("A1", "A2", "A3")]
                slopes.append(sum((x - 2.0) * y for x, y in zip((1.0, 2.0, 3.0), ys)) / 2.0)
            add_secondary(effect_row(
                contrast_id=f"E_STRESS|{endpoint}|{policy}|ORDERED", endpoint=endpoint, block="E_ADVERSARY_BUDGET_STRESS", family="E_STRESS",
                test_label=f"{policy} A1-A3 ordered slope", reference_label="zero slope", differences=slopes, primary=False,
                notes="descriptive ordered stress summary; A2 remains contact-coupled"), "E_STRESS")

    for rows in holm_groups.values():
        holm_adjust(rows)

    output_dir.mkdir(parents=True, exist_ok=True)
    write_csv(output_dir / "cell_estimates.csv", cell_estimates)
    write_csv(output_dir / "primary_contrasts.csv", primary_rows)
    write_csv(output_dir / "secondary_contrasts.csv", secondary_rows)
    write_csv(output_dir / "terminal_state_counts.csv", terminal_counts)

    summary = {
        "schema": 1,
        "experiment_id": "S2-AEATR-001",
        "phase": 7,
        "classification": "PRESPECIFIED_ANALYSIS_RESULTS_CANDIDATE_PENDING_REPOSITORY_FREEZE",
        "source_artifact_zip_sha256": EXPECTED_ZIP_SHA256,
        "observations_sha256": EXPECTED_OBSERVATIONS_SHA256,
        "attempt_ledger_sha256": EXPECTED_LEDGER_SHA256,
        "trial_manifest_sha256": EXPECTED_MANIFEST_SHA256,
        "cell_matrix_sha256": EXPECTED_CELL_MATRIX_SHA256,
        "valid_observations_analyzed": len(observations),
        "invalid_attempts": 0,
        "cell_count": len(cells),
        "primary_contrast_rows": len(primary_rows),
        "secondary_contrast_rows": len(secondary_rows),
        "cell_estimate_rows": len(cell_estimates),
        "terminal_state_rows": len(terminal_counts),
        "bootstrap_replicates": BOOTSTRAP_REPLICATES,
        "right_censor_horizon_s": TAU,
        "time_basis": "DETERMINISTIC_LOGICAL_SIL_TIME_NOT_WALL_CLOCK",
        "global_weighted_policy_score": "PROHIBITED_AND_NOT_COMPUTED",
        "exploratory_endpoint_scalarization": "NOT_PERFORMED",
    }
    if spec_path is not None:
        summary["analysis_spec_sha256"] = sha256_file(spec_path)
    (output_dir / "phase7_summary.json").write_bytes(canonical_json_bytes(summary))

    result_files = ["cell_estimates.csv", "primary_contrasts.csv", "secondary_contrasts.csv", "terminal_state_counts.csv", "phase7_summary.json"]
    hash_manifest = {
        "schema": 1,
        "experiment_id": "S2-AEATR-001",
        "phase": 7,
        "source_artifact_zip_sha256": EXPECTED_ZIP_SHA256,
        "files": {name: sha256_file(output_dir / name) for name in result_files},
    }
    (output_dir / "PHASE7_RESULTS_HASHES.json").write_bytes(canonical_json_bytes(hash_manifest))
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence-zip", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--analysis-spec", type=Path)
    args = parser.parse_args()
    observations, _, campaign_summary, _ = load_and_verify(args.evidence_zip)
    result = analyze(observations, args.output_dir, args.analysis_spec)
    print("STUDY2_PHASE7_ANALYSIS=PASS")
    print(f"campaign_valid_observations={campaign_summary['valid_observations']}")
    print(f"phase7_primary_contrasts={result['primary_contrast_rows']}")
    print(f"phase7_secondary_contrasts={result['secondary_contrast_rows']}")
    print(f"phase7_cell_estimates={result['cell_estimate_rows']}")
    print(f"phase7_results_hashes={sha256_file(args.output_dir / 'PHASE7_RESULTS_HASHES.json')}")


if __name__ == "__main__":
    main()
