#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import statistics
import sys
import zipfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Sequence

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "study2" / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from study2_security.cell_matrix import materialize_cell_matrix  # noqa: E402

EXPERIMENT_ID = "S2-AEATR-001"
TAU_S = 240.0
Z95 = 1.959963984540054
EXPECTED_ZIP_SHA256 = "195860bd44b38ccf170f02cb1cb392583217296d08640c99b18b52286403e133"
EXPECTED_FILE_SHA256 = {
    "observations.jsonl": "8dcc850c561d7e3c0bf7478263b534cae83cbbb55183c313e879dd7d61127854",
    "attempt_ledger.jsonl": "755d6541263ac31589934200ea5071cdbcacae1ea197d044bbd3e6f7f7d1dbc5",
    "runtime_bindings.json": "4d8d1a4db3c9594946eab06a72c2bb71f1dbb13860bdbd01598ca4694ce4f31a",
    "campaign_summary.json": "247bdf2e57a1d0c4b7aaf9e9811d1abf331bcd1cd655dddf3e5c2b5b2da82f99",
    "evidence_hashes.json": "a1a53153356db3434e7ac427225f2a9b620bbec74c3436e2c87a8cbf0b0ffa50",
}
EXPECTED_TRIAL_MANIFEST_SHA256 = "190612473717b7768ceccb4596a20d90cd7d532bf7581330ce94d609cb752e67"
EXPECTED_VALID = 3872
EXPECTED_INVALID = 0

BINARY_ENDPOINTS = {
    "unsafe_permissive_response_rate": ("adjudication_only", "unsafe_permissive"),
    "false_conservative_response_rate": ("adjudication_only", "false_conservative"),
    "evidence_qualified_trusted_recovery": ("evidence_qualified_trusted_recovery",),
    "residual_unauthorized_state": ("adjudication_only", "residual_unauthorized_state"),
    "legitimate_command_rejection_rate": ("adjudication_only", "legitimate_command_rejected"),
}
TIME_ENDPOINT = "time_to_evidence_qualified_trusted_recovery"
PRIMARY_ENDPOINTS = tuple(BINARY_ENDPOINTS) + (TIME_ENDPOINT,)

A_POLICIES = ("S2_B0_FAIL_CLOSED", "S2_B2_RISK_THRESHOLD", "S2_S1_EVIDENCE_AWARE")
B_POLICIES = ("S2_B0_FAIL_CLOSED", "S2_B1_FAIL_OPERATIONAL", "S2_B2_RISK_THRESHOLD", "S2_S1_EVIDENCE_AWARE")
A_PROFILE_ORDER = ("V0", "V1", "V2", "V3", "V4", "V5")
D_SELECTORS = ("S2_S1_EVIDENCE_AWARE", "PI_NO_MISSION", "PI_NO_EVIDENCE", "PI_NO_CONTACT", "PI_SECURITY_ONLY")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def canonical_json_line(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=True, allow_nan=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def mean_ci(values: Sequence[float], *, bounds: tuple[float, float] | None = None) -> tuple[float, float, float, float]:
    if not values:
        raise ValueError("cannot summarize an empty sequence")
    mean = statistics.fmean(values)
    if len(values) == 1:
        sd = 0.0
        se = 0.0
    else:
        sd = statistics.stdev(values)
        se = sd / math.sqrt(len(values))
    lo = mean - Z95 * se
    hi = mean + Z95 * se
    if bounds is not None:
        lo = max(bounds[0], lo)
        hi = min(bounds[1], hi)
    return mean, sd, lo, hi


def wilson_interval(successes: int, n: int) -> tuple[float, float]:
    if n <= 0 or successes < 0 or successes > n:
        raise ValueError("invalid Wilson inputs")
    p = successes / n
    z2 = Z95 * Z95
    denom = 1.0 + z2 / n
    center = (p + z2 / (2.0 * n)) / denom
    half = Z95 * math.sqrt((p * (1.0 - p) + z2 / (4.0 * n)) / n) / denom
    lo = max(0.0, center - half)
    hi = min(1.0, center + half)
    if successes == 0:
        lo = 0.0
    if successes == n:
        hi = 1.0
    return lo, hi


def normal_two_sided_p(values: Sequence[float]) -> float:
    if not values:
        raise ValueError("cannot test an empty sequence")
    mean = statistics.fmean(values)
    if len(values) == 1:
        return 1.0 if mean == 0.0 else 0.0
    sd = statistics.stdev(values)
    if sd == 0.0:
        return 1.0 if mean == 0.0 else 0.0
    z = abs(mean) / (sd / math.sqrt(len(values)))
    return math.erfc(z / math.sqrt(2.0))


def exact_mcnemar_p(first: Sequence[int], reference: Sequence[int]) -> float:
    if len(first) != len(reference) or not first:
        raise ValueError("paired binary vectors must be non-empty and equal length")
    b = sum(1 for a, r in zip(first, reference) if a == 1 and r == 0)
    c = sum(1 for a, r in zip(first, reference) if a == 0 and r == 1)
    discordant = b + c
    if discordant == 0:
        return 1.0
    tail_k = min(b, c)
    tail = sum(math.comb(discordant, k) for k in range(tail_k + 1)) / (2 ** discordant)
    return min(1.0, 2.0 * tail)


def holm_adjust(p_values: Sequence[float]) -> list[float]:
    m = len(p_values)
    if m == 0:
        return []
    order = sorted(range(m), key=lambda i: (p_values[i], i))
    adjusted = [0.0] * m
    running = 0.0
    for rank, index in enumerate(order):
        candidate = min(1.0, (m - rank) * p_values[index])
        running = max(running, candidate)
        adjusted[index] = min(1.0, running)
    return adjusted


def nested_value(row: dict[str, Any], path: tuple[str, ...]) -> Any:
    value: Any = row
    for key in path:
        value = value[key]
    return value


def binary_value(row: dict[str, Any], endpoint: str) -> int:
    value = nested_value(row, BINARY_ENDPOINTS[endpoint])
    if type(value) is not bool:
        raise ValueError(f"{endpoint} must be boolean")
    return int(value)


def recovery_restricted_time(row: dict[str, Any]) -> float:
    event = row["evidence_qualified_trusted_recovery"]
    censored = row["time_to_recovery_right_censored"]
    event_time = row["time_to_evidence_qualified_trusted_recovery_s"]
    if type(event) is not bool or type(censored) is not bool:
        raise ValueError("recovery event/censor flags must be boolean")
    if event:
        if censored or event_time is None:
            raise ValueError("uncensored recovery requires a recovery event time")
        value = float(event_time)
        if value < 0.0 or value > TAU_S:
            raise ValueError("recovery event time outside frozen horizon")
        return value
    if not censored or event_time is not None:
        raise ValueError("censored recovery must have null event time and censor flag true")
    return TAU_S


def containment_restricted_time(row: dict[str, Any]) -> float:
    event_time = row["time_to_containment_s"]
    if event_time is None:
        return TAU_S
    value = float(event_time)
    if value < 0.0 or value > TAU_S:
        raise ValueError("containment event time outside frozen horizon")
    return value


def primary_value(row: dict[str, Any], endpoint: str) -> float:
    if endpoint in BINARY_ENDPOINTS:
        return float(binary_value(row, endpoint))
    if endpoint == TIME_ENDPOINT:
        return recovery_restricted_time(row)
    raise KeyError(endpoint)


def expected_positions() -> list[tuple[str, int, str]]:
    matrix = materialize_cell_matrix()
    positions: list[tuple[str, int, str]] = []
    for cell in matrix["cells"]:
        spec = matrix["seed_sets"][cell["seed_set"]]
        for seed in range(spec["start"], spec["end"] + 1):
            positions.append((cell["cell_id"], seed, f"{EXPERIMENT_ID}:{cell['cell_id']}:{seed}"))
    if len(positions) != EXPECTED_VALID:
        raise AssertionError("frozen matrix does not materialize 3,872 positions")
    return positions


def load_artifact(artifact_zip: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any], dict[str, Any], dict[str, Any]]:
    if sha256_file(artifact_zip) != EXPECTED_ZIP_SHA256:
        raise ValueError("artifact ZIP SHA-256 mismatch")
    with zipfile.ZipFile(artifact_zip) as archive:
        names = set(archive.namelist())
        if names != set(EXPECTED_FILE_SHA256):
            raise ValueError(f"artifact file set mismatch: {sorted(names)}")
        raw = {name: archive.read(name) for name in EXPECTED_FILE_SHA256}
    for name, expected in EXPECTED_FILE_SHA256.items():
        actual = sha256_bytes(raw[name])
        if actual != expected:
            raise ValueError(f"{name} SHA-256 mismatch: {actual}")
    observations = [json.loads(line) for line in raw["observations.jsonl"].splitlines() if line.strip()]
    ledger = [json.loads(line) for line in raw["attempt_ledger.jsonl"].splitlines() if line.strip()]
    runtime_bindings = json.loads(raw["runtime_bindings.json"])
    campaign_summary = json.loads(raw["campaign_summary.json"])
    evidence_hashes = json.loads(raw["evidence_hashes.json"])
    return observations, ledger, runtime_bindings, campaign_summary, evidence_hashes


def validate_integrity(
    observations: Sequence[dict[str, Any]],
    ledger: Sequence[dict[str, Any]],
    campaign_summary: dict[str, Any],
) -> None:
    if len(observations) != EXPECTED_VALID:
        raise ValueError(f"observation count mismatch: {len(observations)}")
    if len(ledger) != EXPECTED_VALID + EXPECTED_INVALID:
        raise ValueError(f"attempt ledger count mismatch: {len(ledger)}")
    if campaign_summary.get("valid_observations") != EXPECTED_VALID or campaign_summary.get("invalid_attempts") != EXPECTED_INVALID:
        raise ValueError("campaign summary counts mismatch")
    if campaign_summary.get("trial_manifest_sha256") != EXPECTED_TRIAL_MANIFEST_SHA256:
        raise ValueError("trial manifest SHA mismatch in campaign summary")

    expected = expected_positions()
    if len({row["trial_id"] for row in observations}) != EXPECTED_VALID:
        raise ValueError("duplicate observation trial identity")
    if len({row["run_id"] for row in observations}) != EXPECTED_VALID:
        raise ValueError("duplicate observation run_id")
    if len({row["run_id"] for row in ledger}) != len(ledger):
        raise ValueError("duplicate attempt ledger run_id")

    for position, (row, led, expected_id) in enumerate(zip(observations, ledger, expected), start=1):
        cell_id, seed, trial_id = expected_id
        expected_run_id = f"S2-P6-{position:04d}-A1"
        if row.get("attempt_status") != "VALID" or led.get("attempt_status") != "VALID":
            raise ValueError(f"non-VALID retained attempt at position {position}")
        identity = (row.get("cell_id"), row.get("seed"), row.get("trial_id"))
        if identity != (cell_id, seed, trial_id):
            raise ValueError(f"frozen trial order/membership mismatch at position {position}: {identity}")
        if row.get("run_id") != expected_run_id or led.get("run_id") != expected_run_id:
            raise ValueError(f"run_id mismatch at position {position}")
        for key in ("cell_id", "seed", "trial_id", "run_id", "attempt_status"):
            if led.get(key) != row.get(key):
                raise ValueError(f"ledger/observation mismatch for {key} at position {position}")
        if row.get("experiment_id") != EXPERIMENT_ID or row.get("runtime_mode") != "CAMPAIGN":
            raise ValueError(f"runtime identity mismatch at position {position}")
        if row.get("oracle_was_selector_input") is not False:
            raise ValueError(f"oracle isolation violated at position {position}")
        if float(row.get("censor_horizon_s")) != TAU_S:
            raise ValueError(f"censor horizon mismatch at position {position}")
        for endpoint in BINARY_ENDPOINTS:
            binary_value(row, endpoint)
        recovery_restricted_time(row)
        containment_restricted_time(row)
        for key in ("ground_spacecraft_state_divergence", "response_selection_stability"):
            if type(row.get(key)) is not bool:
                raise ValueError(f"{key} must be boolean at position {position}")
        if not isinstance(row.get("recovery_terminal_state"), str) or not row["recovery_terminal_state"]:
            raise ValueError(f"missing terminal state at position {position}")
        stored = row.get("observation_sha256")
        unhashed = dict(row)
        unhashed.pop("observation_sha256", None)
        if stored != sha256_bytes(canonical_json_line(unhashed)):
            raise ValueError(f"observation content hash mismatch at position {position}")


def cell_lookup() -> dict[str, dict[str, Any]]:
    return {cell["cell_id"]: cell for cell in materialize_cell_matrix()["cells"]}


def rows_by_cell(observations: Sequence[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in observations:
        grouped[row["cell_id"]].append(row)
    for rows in grouped.values():
        rows.sort(key=lambda item: item["seed"])
    return dict(grouped)


def _cell_meta(cell: dict[str, Any]) -> dict[str, Any]:
    keys = (
        "cell_id", "block", "event", "mission", "contact", "evidence", "adversary",
        "mechanism", "policy", "seed_set", "ambiguity_family", "cause", "context", "selector",
    )
    return {key: cell.get(key, "") for key in keys}


def cell_summary(observations: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
    cells = cell_lookup()
    grouped = rows_by_cell(observations)
    output: list[dict[str, Any]] = []
    for cell_id in [cell["cell_id"] for cell in materialize_cell_matrix()["cells"]]:
        rows = grouped[cell_id]
        record = _cell_meta(cells[cell_id])
        record["n"] = len(rows)
        for endpoint in BINARY_ENDPOINTS:
            values = [binary_value(row, endpoint) for row in rows]
            successes = sum(values)
            lo, hi = wilson_interval(successes, len(values))
            record[f"{endpoint}_count"] = successes
            record[f"{endpoint}_rate"] = successes / len(values)
            record[f"{endpoint}_ci95_low"] = lo
            record[f"{endpoint}_ci95_high"] = hi
        recovery = [recovery_restricted_time(row) for row in rows]
        mean, sd, lo, hi = mean_ci(recovery, bounds=(0.0, TAU_S))
        record["recovery_rmst_240_s"] = mean
        record["recovery_rmst_sd_s"] = sd
        record["recovery_rmst_ci95_low_s"] = lo
        record["recovery_rmst_ci95_high_s"] = hi
        containment = [containment_restricted_time(row) for row in rows]
        mean, sd, lo, hi = mean_ci(containment, bounds=(0.0, TAU_S))
        record["containment_rmst_240_s"] = mean
        record["containment_rmst_sd_s"] = sd
        record["containment_rmst_ci95_low_s"] = lo
        record["containment_rmst_ci95_high_s"] = hi
        for field in ("ground_spacecraft_state_divergence", "response_selection_stability"):
            values = [int(row[field]) for row in rows]
            lo, hi = wilson_interval(sum(values), len(values))
            record[f"{field}_count"] = sum(values)
            record[f"{field}_rate"] = sum(values) / len(values)
            record[f"{field}_ci95_low"] = lo
            record[f"{field}_ci95_high"] = hi
        record["containment_events"] = sum(row["time_to_containment_s"] is not None for row in rows)
        record["containment_right_censored"] = sum(row["time_to_containment_s"] is None for row in rows)
        record["recovery_events"] = sum(row["evidence_qualified_trusted_recovery"] for row in rows)
        record["recovery_right_censored"] = sum(row["time_to_recovery_right_censored"] for row in rows)
        output.append(record)
    return output


def terminal_state_summary(observations: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
    cells = cell_lookup()
    grouped = rows_by_cell(observations)
    output: list[dict[str, Any]] = []
    for cell_id in [cell["cell_id"] for cell in materialize_cell_matrix()["cells"]]:
        counts = Counter(row["recovery_terminal_state"] for row in grouped[cell_id])
        n = len(grouped[cell_id])
        for state in sorted(counts):
            output.append({
                **_cell_meta(cells[cell_id]),
                "terminal_state": state,
                "count": counts[state],
                "proportion": counts[state] / n,
                "n": n,
            })
    return output


def paired_vectors(
    grouped: dict[str, list[dict[str, Any]]],
    first_cell: str,
    reference_cell: str,
    endpoint: str,
) -> tuple[list[float], list[float]]:
    first = {row["seed"]: row for row in grouped[first_cell]}
    reference = {row["seed"]: row for row in grouped[reference_cell]}
    if set(first) != set(reference):
        raise ValueError(f"seed pairing mismatch: {first_cell} vs {reference_cell}")
    seeds = sorted(first)
    return (
        [primary_value(first[seed], endpoint) for seed in seeds],
        [primary_value(reference[seed], endpoint) for seed in seeds],
    )


def paired_contrast_record(
    *,
    family: str,
    label: str,
    endpoint: str,
    first_cell: str,
    reference_cell: str,
    grouped: dict[str, list[dict[str, Any]]],
    inferential: bool,
    profile_note: str = "",
) -> dict[str, Any]:
    first, reference = paired_vectors(grouped, first_cell, reference_cell, endpoint)
    differences = [a - b for a, b in zip(first, reference)]
    bounds = (-1.0, 1.0) if endpoint in BINARY_ENDPOINTS else None
    effect, sd, lo, hi = mean_ci(differences, bounds=bounds)
    record: dict[str, Any] = {
        "family": family,
        "contrast": label,
        "endpoint": endpoint,
        "endpoint_type": "binary_risk_difference" if endpoint in BINARY_ENDPOINTS else "rmst_240_s_mean_difference",
        "first_cell": first_cell,
        "reference_cell": reference_cell,
        "paired_n": len(differences),
        "effect_first_minus_reference": effect,
        "paired_sd": sd,
        "ci95_low": lo,
        "ci95_high": hi,
        "profile_note": profile_note,
    }
    if inferential:
        if endpoint in BINARY_ENDPOINTS:
            record["raw_p_value"] = exact_mcnemar_p([int(v) for v in first], [int(v) for v in reference])
        else:
            record["raw_p_value"] = normal_two_sided_p(differences)
    return record


def primary_contrasts(observations: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
    cells = cell_lookup()
    grouped = rows_by_cell(observations)
    by_a: dict[tuple[str, str], str] = {}
    for cell in cells.values():
        if cell["block"] == "A_PRIMARY_EVIDENCE_MECHANISM":
            by_a[(cell["evidence"], cell["policy"])] = cell["cell_id"]
    output: list[dict[str, Any]] = []
    for policy in A_POLICIES:
        reference = by_a[("V0", policy)]
        for evidence in A_PROFILE_ORDER[1:]:
            first = by_a[(evidence, policy)]
            for endpoint in PRIMARY_ENDPOINTS:
                output.append(paired_contrast_record(
                    family="A_TREATMENT_WITHIN_POLICY",
                    label=f"{evidence}-V0 within {policy}",
                    endpoint=endpoint,
                    first_cell=first,
                    reference_cell=reference,
                    grouped=grouped,
                    inferential=False,
                ))
    for evidence in A_PROFILE_ORDER:
        s1 = by_a[(evidence, "S2_S1_EVIDENCE_AWARE")]
        for reference_policy in ("S2_B0_FAIL_CLOSED", "S2_B2_RISK_THRESHOLD"):
            reference = by_a[(evidence, reference_policy)]
            for endpoint in PRIMARY_ENDPOINTS:
                output.append(paired_contrast_record(
                    family="A_POLICY_WITHIN_PROFILE",
                    label=f"S2_S1_EVIDENCE_AWARE-{reference_policy} within {evidence}",
                    endpoint=endpoint,
                    first_cell=s1,
                    reference_cell=reference,
                    grouped=grouped,
                    inferential=False,
                ))
    return output


def _b_index(cells: dict[str, dict[str, Any]]) -> dict[tuple[str, str], str]:
    return {
        (cell["contact"], cell["policy"]): cell["cell_id"]
        for cell in cells.values()
        if cell["block"] == "B_CONTACT_AUTHORIZATION"
    }


def _trend_slope(values: Sequence[float]) -> float:
    if len(values) != 4:
        raise ValueError("K0-K3 trend requires exactly four values")
    x = (0.0, 1.0, 2.0, 3.0)
    xbar = 1.5
    ybar = statistics.fmean(values)
    numerator = sum((xi - xbar) * (yi - ybar) for xi, yi in zip(x, values))
    denominator = sum((xi - xbar) ** 2 for xi in x)
    return numerator / denominator


def secondary_contrasts(observations: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
    cells = cell_lookup()
    grouped = rows_by_cell(observations)
    output: list[dict[str, Any]] = []

    b = _b_index(cells)
    for policy in B_POLICIES:
        k0 = b[("K0", policy)]
        for contact in ("K1", "K2", "K3", "K4"):
            first = b[(contact, policy)]
            for endpoint in PRIMARY_ENDPOINTS:
                output.append(paired_contrast_record(
                    family="B_CONTACT_VS_K0",
                    label=f"{contact}-K0 within {policy}",
                    endpoint=endpoint,
                    first_cell=first,
                    reference_cell=k0,
                    grouped=grouped,
                    inferential=True,
                ))

    for policy in B_POLICIES:
        cells_by_k = [b[(contact, policy)] for contact in ("K0", "K1", "K2", "K3")]
        seed_maps = [{row["seed"]: row for row in grouped[cell_id]} for cell_id in cells_by_k]
        seeds = sorted(seed_maps[0])
        if any(set(m) != set(seeds) for m in seed_maps[1:]):
            raise ValueError(f"K0-K3 trend seed mismatch for {policy}")
        for endpoint in PRIMARY_ENDPOINTS:
            slopes = [
                _trend_slope([primary_value(m[seed], endpoint) for m in seed_maps])
                for seed in seeds
            ]
            bounds = (-1.0, 1.0) if endpoint in BINARY_ENDPOINTS else None
            effect, sd, lo, hi = mean_ci(slopes, bounds=bounds)
            output.append({
                "family": "B_K0_K3_ORDERED_TREND",
                "contrast": f"K0-K3 slope within {policy}",
                "endpoint": endpoint,
                "endpoint_type": "per_contact_step_slope",
                "first_cell": "|".join(cells_by_k),
                "reference_cell": "",
                "paired_n": len(slopes),
                "effect_first_minus_reference": effect,
                "paired_sd": sd,
                "ci95_low": lo,
                "ci95_high": hi,
                "raw_p_value": normal_two_sided_p(slopes),
                "profile_note": "K4 excluded from ordinal trend by frozen plan",
            })

    s1_policy = "S2_S1_EVIDENCE_AWARE"
    for policy in ("S2_B0_FAIL_CLOSED", "S2_B1_FAIL_OPERATIONAL", "S2_B2_RISK_THRESHOLD"):
        for contact in ("K1", "K2", "K3", "K4"):
            policy_k, policy_k0 = b[(contact, policy)], b[("K0", policy)]
            s1_k, s1_k0 = b[(contact, s1_policy)], b[("K0", s1_policy)]
            maps = [{row["seed"]: row for row in grouped[c]} for c in (policy_k, policy_k0, s1_k, s1_k0)]
            seeds = sorted(maps[0])
            if any(set(m) != set(seeds) for m in maps[1:]):
                raise ValueError("interaction seed mismatch")
            for endpoint in PRIMARY_ENDPOINTS:
                diffs = [
                    (primary_value(maps[0][seed], endpoint) - primary_value(maps[1][seed], endpoint))
                    - (primary_value(maps[2][seed], endpoint) - primary_value(maps[3][seed], endpoint))
                    for seed in seeds
                ]
                effect, sd, lo, hi = mean_ci(diffs)
                output.append({
                    "family": "B_POLICY_BY_CONTACT_INTERACTION",
                    "contrast": f"({policy}:{contact}-K0)-(S2_S1_EVIDENCE_AWARE:{contact}-K0)",
                    "endpoint": endpoint,
                    "endpoint_type": "difference_in_differences",
                    "first_cell": f"{policy_k}|{policy_k0}",
                    "reference_cell": f"{s1_k}|{s1_k0}",
                    "paired_n": len(diffs),
                    "effect_first_minus_reference": effect,
                    "paired_sd": sd,
                    "ci95_low": lo,
                    "ci95_high": hi,
                    "raw_p_value": normal_two_sided_p(diffs),
                    "profile_note": "",
                })

    c: dict[tuple[str, str, str], str] = {}
    for cell in cells.values():
        if cell["block"] == "C_FAULT_ATTACK_AMBIGUITY":
            c[(cell["ambiguity_family"], cell["cause"], cell["policy"])] = cell["cell_id"]
    for family in ("telemetry_loss", "state_inconsistency", "contact_or_authorization_loss"):
        for policy in ("S2_B0_FAIL_CLOSED", "S2_B1_FAIL_OPERATIONAL", "S2_S1_EVIDENCE_AWARE"):
            first = c[(family, "ADVERSARIAL", policy)]
            reference = c[(family, "BENIGN", policy)]
            for endpoint in PRIMARY_ENDPOINTS:
                output.append(paired_contrast_record(
                    family="C_AMBIGUITY",
                    label=f"ADVERSARIAL-BENIGN within {family}/{policy}",
                    endpoint=endpoint,
                    first_cell=first,
                    reference_cell=reference,
                    grouped=grouped,
                    inferential=True,
                ))

    d: dict[tuple[str, str], str] = {}
    for cell in cells.values():
        if cell["block"] == "D_CONTEXT_ABLATION":
            d[(cell["context"], cell["selector"])] = cell["cell_id"]
    for context in ("unauthorized_command", "update_recovery", "replay", "evidence_loss"):
        reference = d[(context, "S2_S1_EVIDENCE_AWARE")]
        for selector in D_SELECTORS[1:]:
            first = d[(context, selector)]
            for endpoint in PRIMARY_ENDPOINTS:
                output.append(paired_contrast_record(
                    family="D_ABLATION",
                    label=f"{selector}-S2_S1_EVIDENCE_AWARE within {context}",
                    endpoint=endpoint,
                    first_cell=first,
                    reference_cell=reference,
                    grouped=grouped,
                    inferential=True,
                ))

    e: dict[tuple[str, str, str], str] = {}
    for cell in cells.values():
        if cell["block"] == "E_ADVERSARY_BUDGET_STRESS":
            e[(cell["adversary"], cell["contact"], cell["policy"])] = cell["cell_id"]
    profiles = (("A1", "K0"), ("A2", "K2"), ("A3", "K0"))
    stress_pairs = (
        (("A2", "K2"), ("A1", "K0"), "A2/K2-A1/K0"),
        (("A3", "K0"), ("A1", "K0"), "A3/K0-A1/K0"),
        (("A3", "K0"), ("A2", "K2"), "A3/K0-A2/K2"),
    )
    for policy in A_POLICIES:
        for first_profile, reference_profile, label in stress_pairs:
            first = e[(*first_profile, policy)]
            reference = e[(*reference_profile, policy)]
            note = "A2/K2 contrasts are profile contrasts; adversary level is coupled with contact loss" if "A2/K2" in label else ""
            for endpoint in PRIMARY_ENDPOINTS:
                output.append(paired_contrast_record(
                    family="E_STRESS_PROFILE",
                    label=f"{label} within {policy}",
                    endpoint=endpoint,
                    first_cell=first,
                    reference_cell=reference,
                    grouped=grouped,
                    inferential=True,
                    profile_note=note,
                ))
    for adversary, contact in profiles:
        first = e[(adversary, contact, "S2_S1_EVIDENCE_AWARE")]
        for reference_policy in ("S2_B0_FAIL_CLOSED", "S2_B2_RISK_THRESHOLD"):
            reference = e[(adversary, contact, reference_policy)]
            for endpoint in PRIMARY_ENDPOINTS:
                output.append(paired_contrast_record(
                    family="E_POLICY_WITHIN_PROFILE",
                    label=f"S2_S1_EVIDENCE_AWARE-{reference_policy} within {adversary}/{contact}",
                    endpoint=endpoint,
                    first_cell=first,
                    reference_cell=reference,
                    grouped=grouped,
                    inferential=True,
                    profile_note="A2/K2 is a coupled adversary/contact stress profile" if adversary == "A2" else "",
                ))

    for endpoint in PRIMARY_ENDPOINTS:
        for family in (
            "B_CONTACT_VS_K0",
            "B_K0_K3_ORDERED_TREND",
            "B_POLICY_BY_CONTACT_INTERACTION",
            "C_AMBIGUITY",
            "D_ABLATION",
            "E_STRESS_PROFILE",
            "E_POLICY_WITHIN_PROFILE",
        ):
            indices = [i for i, row in enumerate(output) if row["family"] == family and row["endpoint"] == endpoint]
            adjusted = holm_adjust([float(output[i]["raw_p_value"]) for i in indices])
            for i, adj in zip(indices, adjusted):
                output[i]["holm_adjusted_p_value"] = adj
                output[i]["holm_reject_alpha_0_05"] = adj <= 0.05
    return output


def write_csv(path: Path, rows: Sequence[dict[str, Any]]) -> None:
    if not rows:
        raise ValueError(f"refusing to write empty CSV: {path}")
    fieldnames: list[str] = []
    for row in rows:
        for key in row:
            if key not in fieldnames:
                fieldnames.append(key)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def report_markdown(
    observations: Sequence[dict[str, Any]],
    primary: Sequence[dict[str, Any]],
    secondary: Sequence[dict[str, Any]],
) -> str:
    significant = Counter(
        row["family"] for row in secondary if row.get("holm_reject_alpha_0_05") is True
    )
    lines = [
        "# Study 2 Phase 7 Prespecified Statistical Analysis",
        "",
        "## Analysis boundary",
        "",
        f"- Frozen Phase-6 observations analyzed: **{len(observations):,}**.",
        "- Invalid attempts: **0**.",
        f"- Recovery and containment time-to-event outcomes use restricted time at **{TAU_S:.0f} s**.",
        "- Primary Block-A contrasts are reported as paired effect sizes with 95% confidence intervals; no primary p-value gate is used.",
        "- Secondary multiplicity is Holm-adjusted separately within each named contrast family and primary endpoint.",
        "- No weighted global policy score or global policy rank is computed.",
        "",
        "## RQ1 — Evidence conditions and partial compromise",
        "",
        f"Block A contributes {sum(r['family'] == 'A_TREATMENT_WITHIN_POLICY' for r in primary)} treatment-within-policy endpoint contrasts and {sum(r['family'] == 'A_POLICY_WITHIN_PROFILE' for r in primary)} policy-within-profile endpoint contrasts. Interpret authenticated V5 evidence as policy-visible evidence, not as an objective correctness oracle.",
        "",
        "## RQ2 — Contact and authorization constraints",
        "",
        "K0–K3 are treated as the ordered contact series; K4 intermittent/flapping contact is reported separately. Policy-by-contact effects are paired difference-in-differences.",
        "",
        "## RQ3 — Matched benign/adversarial ambiguity",
        "",
        "C-family contrasts are adversarial minus benign under matched policy-visible evidence. Hidden cause labels are used only for adjudication/analysis.",
        "",
        "## RQ4 — Context contribution",
        "",
        "D-family estimates compare each prespecified context ablation with the full evidence-aware selector within the same context and paired seed.",
        "",
        "## RQ5 — Baselines and adversary-budget stress",
        "",
        "E-family stress estimates include A1/K0, A2/K2, and A3/K0 profiles. Any contrast involving A2/K2 is explicitly a coupled adversary/contact profile contrast, not an unconfounded adversary-only effect.",
        "",
        "## Secondary multiplicity summary",
        "",
    ]
    for family in (
        "B_CONTACT_VS_K0",
        "B_K0_K3_ORDERED_TREND",
        "B_POLICY_BY_CONTACT_INTERACTION",
        "C_AMBIGUITY",
        "D_ABLATION",
        "E_STRESS_PROFILE",
        "E_POLICY_WITHIN_PROFILE",
    ):
        total = sum(r["family"] == family for r in secondary)
        lines.append(f"- `{family}`: {significant[family]} Holm-rejected endpoint contrasts out of {total}.")
    lines.extend([
        "",
        "## Interpretation constraints",
        "",
        "- Evidence-qualified trusted recovery is not identical to objectively safe recovery.",
        "- The adjudication oracle was not a selector input.",
        "- Secondary n=32 blocks are estimation/sensitivity blocks and are not claimed to be powered for small effects.",
        "- No Study-1 empirical result is recalculated here.",
        "",
        "Full estimates are in `cell_summary.csv`, `primary_contrasts.csv`, `secondary_contrasts.csv`, and `terminal_state_summary.csv`.",
        "",
    ])
    return "\n".join(lines)


def output_hashes(output_dir: Path, names: Iterable[str]) -> dict[str, str]:
    return {name: sha256_file(output_dir / name) for name in names}


def run_analysis(artifact_zip: Path, output_dir: Path) -> dict[str, Any]:
    observations, ledger, runtime_bindings, campaign_summary, evidence_hashes = load_artifact(artifact_zip)
    validate_integrity(observations, ledger, campaign_summary)

    cell_rows = cell_summary(observations)
    primary_rows = primary_contrasts(observations)
    secondary_rows = secondary_contrasts(observations)
    terminal_rows = terminal_state_summary(observations)

    output_dir.mkdir(parents=True, exist_ok=True)
    write_csv(output_dir / "cell_summary.csv", cell_rows)
    write_csv(output_dir / "primary_contrasts.csv", primary_rows)
    write_csv(output_dir / "secondary_contrasts.csv", secondary_rows)
    write_csv(output_dir / "terminal_state_summary.csv", terminal_rows)
    (output_dir / "ANALYSIS_REPORT.md").write_text(
        report_markdown(observations, primary_rows, secondary_rows),
        encoding="utf-8",
    )
    summary = {
        "schema": 1,
        "experiment_id": EXPERIMENT_ID,
        "classification": "STUDY2_PHASE7_PRESPECIFIED_ANALYSIS",
        "analysis_population_valid_observations": len(observations),
        "invalid_attempts": campaign_summary["invalid_attempts"],
        "cell_count": len(cell_rows),
        "primary_endpoint_count": len(PRIMARY_ENDPOINTS),
        "primary_contrast_rows": len(primary_rows),
        "secondary_contrast_rows": len(secondary_rows),
        "terminal_state_rows": len(terminal_rows),
        "recovery_rmst_tau_s": TAU_S,
        "containment_rmst_tau_s": TAU_S,
        "trial_manifest_sha256": campaign_summary["trial_manifest_sha256"],
        "artifact_zip_sha256": EXPECTED_ZIP_SHA256,
        "source_file_sha256": EXPECTED_FILE_SHA256,
        "runtime_bindings": runtime_bindings,
        "evidence_hash_manifest": evidence_hashes,
        "analysis_constraints": {
            "weighted_global_policy_score": False,
            "global_policy_rank": False,
            "study1_reanalysis": False,
            "post_hoc_seed_replacement": False,
            "outcome_dependent_exclusion": False,
        },
    }
    (output_dir / "analysis_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    names = (
        "cell_summary.csv",
        "primary_contrasts.csv",
        "secondary_contrasts.csv",
        "terminal_state_summary.csv",
        "ANALYSIS_REPORT.md",
        "analysis_summary.json",
    )
    hashes = output_hashes(output_dir, names)
    (output_dir / "output_hashes.json").write_text(
        json.dumps({"schema": 1, "sha256": hashes}, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return summary


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the frozen Study-2 Phase-7 statistical analysis.")
    parser.add_argument("--artifact-zip", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    summary = run_analysis(args.artifact_zip, args.output_dir)
    print("STUDY2_PHASE7_ANALYSIS=PASS")
    print(f"valid_observations={summary['analysis_population_valid_observations']}")
    print(f"cell_count={summary['cell_count']}")
    print(f"primary_contrast_rows={summary['primary_contrast_rows']}")
    print(f"secondary_contrast_rows={summary['secondary_contrast_rows']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
