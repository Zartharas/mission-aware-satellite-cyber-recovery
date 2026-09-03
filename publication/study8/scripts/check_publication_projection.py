#!/usr/bin/env python3
"""Validate Study-8 publication projections without scientific re-execution.

This checker reads frozen Study-8 evidence and publication artifacts only. It does not
execute the canonical model, call either statistical implementation, or create new
scientific summaries.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PUB = ROOT / "publication" / "study8"

EXPECTED_HASHES = {
    "study8/results/S8-PQC-ICR-001/canonical_observations.csv": "cfc65b6663be4e9f17a00ed102730f8642efcbbd844045acce032ff09a0bcabf",
    "study8/analysis/results/primary_findings.json": "26a8ac4d1039917323e75a294775dd14a2b563adb12a5d2fcdb47ce8f15c992e",
    "study8/analysis/results/independent_findings.json": "26a8ac4d1039917323e75a294775dd14a2b563adb12a5d2fcdb47ce8f15c992e",
    "study8/analysis/results/interpretation_audit.json": "620827f83fb566ff6ceae1b66c8f51f61ef8e5bbdabbb1c4b5a48b5187a82413",
}

ERRORS: list[str] = []


def fail(message: str) -> None:
    ERRORS.append(message)
    print(f"[FAIL] {message}", file=sys.stderr)


def ok(message: str) -> None:
    print(f"[OK] {message}")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def validate_frozen_hashes() -> None:
    before = len(ERRORS)
    for rel, expected in EXPECTED_HASHES.items():
        path = ROOT / rel
        require(path.is_file(), f"missing frozen source: {rel}")
        if path.is_file():
            require(sha256(path) == expected, f"frozen SHA-256 mismatch: {rel}")
    if len(ERRORS) == before:
        ok(f"frozen Study-8 evidence hashes verified: {len(EXPECTED_HASHES)}")


def load_findings() -> dict:
    return json.loads((ROOT / "study8/analysis/results/primary_findings.json").read_text(encoding="utf-8"))


def validate_frozen_findings_contract(findings: dict) -> None:
    before = len(ERRORS)
    require(findings["population_validation"]["row_count"] == 3456, "frozen row count drift")
    require(findings["population_validation"]["unique_factor_positions"] == 3456, "factor-position count drift")
    require(findings["primary"]["P3_minus_P1_success_risk_difference"]["fraction"] == "0/1", "primary P3-P1 contrast drift")
    for policy in (
        "P0_HARD_CUTOVER",
        "P1_STAGED_CUTOVER",
        "P2_HYBRID_OVERLAP",
        "P3_CONTACT_AWARE_STAGED",
    ):
        item = findings["primary"]["policy_success"][policy]
        require(item["successes"] == 635 and item["total"] == 864, f"policy result drift: {policy}")

    expected_profiles = {
        "PROFILE_512_44": (1080, 1152),
        "PROFILE_768_65": (748, 1152),
        "PROFILE_1024_87": (712, 1152),
    }
    for profile, expected in expected_profiles.items():
        item = findings["cryptographic_profile_analysis"]["marginal_success_by_profile"][profile]
        require((item["successes"], item["total"]) == expected, f"profile result drift: {profile}")

    paired = findings["cryptographic_profile_analysis"]["paired_ordered_profile_check"]
    require(paired["non_increasing_success_pattern_count"] == 1152, "matched profile ordering count drift")
    require(paired["pattern_counts"] == {"000": 72, "100": 332, "110": 36, "111": 712}, "profile pattern-count drift")

    for dimension in ("regime", "profile", "disruption", "deadline"):
        for stratum, item in findings["stratified_P3_minus_P1"][dimension].items():
            require(item["P3_minus_P1"]["fraction"] == "0/1", f"nonzero frozen P3-P1 stratum: {dimension}/{stratum}")
    if len(ERRORS) == before:
        ok("frozen primary/profile/stratified findings contract verified")


def csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def validate_primary_table() -> None:
    before = len(ERRORS)
    rows = csv_rows(PUB / "tables/table-s8-2-primary-profile.csv")
    by_key = {(row["result_family"], row["item"]): row for row in rows}
    expected = {
        ("policy", "P0_HARD_CUTOVER"): ("635", "864", "73.495370"),
        ("policy", "P1_STAGED_CUTOVER"): ("635", "864", "73.495370"),
        ("policy", "P2_HYBRID_OVERLAP"): ("635", "864", "73.495370"),
        ("policy", "P3_CONTACT_AWARE_STAGED"): ("635", "864", "73.495370"),
        ("profile", "PROFILE_512_44"): ("1080", "1152", "93.750000"),
        ("profile", "PROFILE_768_65"): ("748", "1152", "64.930556"),
        ("profile", "PROFILE_1024_87"): ("712", "1152", "61.805556"),
    }
    for key, values in expected.items():
        row = by_key.get(key)
        require(row is not None, f"missing publication result row: {key}")
        if row:
            require((row["successes"], row["total"], row["success_percent"]) == values, f"publication result mismatch: {key}")
    require(by_key[("policy", "P3_CONTACT_AWARE_STAGED")]["contrast_vs_reference_percentage_points"] == "0.000000", "publication primary contrast is not zero")
    if len(ERRORS) == before:
        ok("primary/profile publication table matches frozen findings")


def validate_strata_table() -> None:
    before = len(ERRORS)
    rows = csv_rows(PUB / "tables/table-s8-3-p3-vs-p1-strata.csv")
    require(len(rows) == 14, f"expected 14 prespecified strata rows, found {len(rows)}")
    for row in rows:
        require(row["P3_minus_P1_percentage_points"] == "0.000000", f"nonzero publication stratum contrast: {row['dimension']}/{row['stratum']}")
        require(row["P1_successes"] == row["P3_successes"], f"P1/P3 success-count mismatch in publication table: {row['dimension']}/{row['stratum']}")
        require(row["P1_total"] == row["P3_total"], f"P1/P3 denominator mismatch in publication table: {row['dimension']}/{row['stratum']}")
    required = {
        ("regime", "R4_CLUSTERED_MEDIUM", "125", "216"),
        ("deadline", "D12", "94", "288"),
        ("deadline", "D48", "288", "288"),
        ("disruption", "A1_DROP_FIRST_LARGEST_OBJECT_FRAGMENT", "160", "216"),
        ("profile", "PROFILE_512_44", "270", "288"),
    }
    actual = {(r["dimension"], r["stratum"], r["P1_successes"], r["P1_total"]) for r in rows}
    require(required.issubset(actual), "one or more sentinel strata rows do not match frozen findings")
    if len(ERRORS) == before:
        ok("all prespecified P3-vs-P1 publication strata verified")


def validate_tradeoff_table() -> None:
    before = len(ERRORS)
    rows = {r["policy"]: r for r in csv_rows(PUB / "tables/table-s8-4-policy-tradeoffs.csv")}
    require(rows["P0_HARD_CUTOVER"]["mean_control_unavailable_slots"] == "12.195602", "P0 control-unavailable projection drift")
    require(rows["P0_HARD_CUTOVER"]["mean_legacy_exposure_slots"] == "0.000000", "P0 legacy-exposure projection drift")
    require(rows["P1_STAGED_CUTOVER"]["mean_legacy_exposure_slots"] == "12.195602", "P1 legacy-exposure projection drift")
    require(rows["P2_HYBRID_OVERLAP"]["mean_dual_epoch_overlap_slots"] == "3.403935", "P2 overlap projection drift")
    p3 = rows["P3_CONTACT_AWARE_STAGED"]
    require(p3["mean_contacts"] == "2.843750", "P3 contacts projection drift")
    require(p3["mean_modeled_crypto_bytes"] == "16551.819444", "P3 byte projection drift")
    require(p3["mean_transition_attempts"] == "0.923611", "P3 attempts projection drift")
    require(p3["mean_legacy_exposure_slots"] == "12.497685", "P3 legacy exposure projection drift")
    if len(ERRORS) == before:
        ok("policy state/resource publication table matches frozen findings")


def validate_manuscript() -> None:
    before = len(ERRORS)
    text = (PUB / "manuscript/manuscript.md").read_text(encoding="utf-8")
    required_tokens = (
        "3,456",
        "635/864",
        "0.000000",
        "1080/1152",
        "748/1152",
        "712/1152",
        "1152/1152",
        "12,560 bytes",
        "17,460 bytes",
        "24,236 bytes",
        "A2",
        "same required object bundle",
        "no physical duration",
        "not a NIST- or CCSDS-prescribed transition protocol",
        "does not support sampling-based generalization",
        EXPECTED_HASHES["study8/results/S8-PQC-ICR-001/canonical_observations.csv"],
        EXPECTED_HASHES["study8/analysis/results/primary_findings.json"],
    )
    for token in required_tokens:
        require(token in text, f"manuscript required frozen/boundary token missing: {token!r}")
    require("first PQC study for satellites" not in text, "prohibited novelty claim found")
    require("first crypto-agility" not in text, "prohibited crypto-agility novelty claim found")
    if len(ERRORS) == before:
        ok("manuscript frozen-result and claim-boundary sentinels verified")


def validate_traceability_and_references() -> None:
    before = len(ERRORS)
    trace = csv_rows(PUB / "claim-traceability.csv")
    require(len(trace) == 15, f"expected 15 claim-traceability rows, found {len(trace)}")
    require(len({r["claim_id"] for r in trace}) == 15, "claim IDs are not unique")

    bib = (PUB / "references/references.bib").read_text(encoding="utf-8")
    keys = set(re.findall(r"(?m)^@\w+\{([^,]+),", bib))
    required_keys = {
        "NIST_FIPS203_2024",
        "NIST_FIPS204_2024",
        "NIST_SP800227_2025",
        "NIST_CSWP39_2026",
        "IEEE3536_2026",
        "CCSDS_SDLS",
        "GSMA_PQ07_2026",
        "Eichen_etal_2026",
        "Ghosh_Nath_2026",
        "Kim_2026_PQCSpace",
    }
    require(required_keys.issubset(keys), f"required bibliography keys missing: {sorted(required_keys - keys)}")
    if len(ERRORS) == before:
        ok("claim traceability and core publication references verified")


def main() -> int:
    print("=== STUDY 8 PUBLICATION PROJECTION VALIDATION ===")
    validate_frozen_hashes()
    findings = load_findings()
    validate_frozen_findings_contract(findings)
    validate_primary_table()
    validate_strata_table()
    validate_tradeoff_table()
    validate_manuscript()
    validate_traceability_and_references()
    print(f"errors={len(ERRORS)}")
    if ERRORS:
        print("study8_publication_projection=FAIL", file=sys.stderr)
        return 1
    print("scientific_reexecution=PROHIBITED")
    print("publication_submission=PROHIBITED")
    print("study8_publication_projection=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
