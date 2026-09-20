#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


class ValidationError(RuntimeError):
    pass


def load(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValidationError(f"{path} is not a JSON object")
    return value


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationError(message)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()
    root = args.root

    protocol = load(root / "study8e/CANONICAL_EXECUTION_PROTOCOL_001.json")
    authorization = load(root / "study8e/CANONICAL_EXECUTION_AUTHORIZATION_20260920.json")
    population = load(root / "study8e/SATNOGS_POPULATION_FREEZE_002.json")
    trace = load(root / "study8e/SATNOGS_TRACE_ARTIFACT_FREEZE_002.json")
    impl = load(root / "study8e/IMPLEMENTATION_FREEZE_001.json")

    require(protocol["experiment_id"] == "S8E-ECTV-001", "wrong experiment id")
    require(protocol["protocol_id"] == "S8E-CANON-EXEC-001", "wrong protocol id")
    require(
        protocol["status"] == "CANONICAL_EXECUTION_PROTOCOL_FREEZE_CANDIDATE__NO_REAL_TRACE_ENDPOINTS_COMPUTED",
        "protocol status does not preserve pre-execution gate",
    )

    frozen = protocol["frozen_inputs"]
    require(frozen["population_freeze"] == population["freeze_id"], "population freeze mismatch")
    require(frozen["trace_freeze"] == trace["freeze_id"], "trace freeze mismatch")
    require(frozen["implementation_freeze"] == impl["freeze_id"], "implementation freeze mismatch")
    require(frozen["trace_records"] == trace["corpus"]["records"] == 476, "trace record mismatch")
    require(frozen["trace_pairs"] == trace["corpus"]["pairs"] == 20, "trace pair mismatch")
    require(
        frozen["trace_artifact_zip_sha256"] == trace["execution"]["artifact_zip_sha256"],
        "trace ZIP hash mismatch",
    )
    require(
        frozen["trace_manifest_sha256"] == trace["execution"]["manifest_sha256"],
        "trace manifest hash mismatch",
    )
    require(
        frozen["trace_jsonl_sha256"] == trace["corpus"]["canonical_jsonl"]["sha256"],
        "trace JSONL hash mismatch",
    )
    require(
        frozen["implementation_primary_git_blob_sha1"]
        == impl["implementation_files"]["study8e/src/external_contact_recovery_model.py"]["git_blob_sha1"],
        "primary implementation identity mismatch",
    )
    require(
        frozen["implementation_reference_git_blob_sha1"]
        == impl["implementation_files"]["study8e/audit/independent_external_reference.py"]["git_blob_sha1"],
        "reference implementation identity mismatch",
    )

    grid = protocol["factor_grid"]
    require(grid["horizons_hours"] == [6, 12, 24], "horizon grid drift")
    require(
        grid["profiles"] == [
            "PROFILE_512_44",
            "PROFILE_768_65",
            "PROFILE_1024_87",
        ],
        "profile grid drift",
    )
    require(
        grid["policies"] == [
            "P0_HARD_CUTOVER",
            "P1_STAGED_CUTOVER",
            "P2_HYBRID_OVERLAP",
            "P3_CONTACT_AWARE_STAGED",
        ],
        "policy grid drift",
    )
    require(
        grid["disruptions"] == [
            "A0_NONE",
            "A1_DROP_FIRST_LARGEST_OBJECT_FRAGMENT",
            "A2_DELAY_FIRST_TRANSITION_PROOF_ONE_CONTACT",
            "A3_STALE_EPOCH_REPLAY_AT_COMMIT",
        ],
        "disruption grid drift",
    )
    expected_per_anchor = (
        len(grid["horizons_hours"])
        * len(grid["profiles"])
        * len(grid["policies"])
        * len(grid["disruptions"])
    )
    require(expected_per_anchor == 144, "factor product must equal 144")
    require(grid["cases_per_anchor"] == expected_per_anchor, "cases_per_anchor drift")

    anchor = protocol["anchor_population"]
    require(anchor["same_window_reuse_after_anchor"] is False, "same-window reuse changed")
    require(anchor["no_post_result_anchor_dropping"] is True, "anchor dropping guard changed")
    require(
        "24 hours" in anchor["eligibility"]
        and "2026-07-01T00:00:00Z" in anchor["eligibility"],
        "anchor forward-coverage boundary drift",
    )

    coverage = protocol["trace_preparation"]["forward_coverage_proof"]
    require("older" in coverage["implication"], "forward-coverage proof missing older-page property")
    require("complete backward history" in coverage["boundary"], "backward-history limitation missing")

    minimum_rate = protocol["minimum_rate_endpoint"]
    require(minimum_rate["lower_bound_bps"] == 1, "threshold lower bound drift")
    require(minimum_rate["no_arbitrary_fixed_rate_cap"] is True, "fixed rate cap introduced")
    require(
        minimum_rate["threshold_search"]
        == "Monotone integer binary search from 1 through the sufficient upper bound, inclusive.",
        "threshold search drift",
    )
    require(
        minimum_rate["sufficient_upper_bound"]["no_available_future_window"]
        == "no finite threshold",
        "zero-window threshold semantics drift",
    )

    audit = protocol["independent_audit"]
    require(audit["required"] is True, "independent audit disabled")
    require(audit["threshold_search_reimplemented_separately"] is True, "independent threshold solver disabled")
    require(audit["acceptance"] == "zero mismatches across every canonical case", "audit acceptance drift")

    gate = protocol["execution_authorization_gate"]
    require(gate["protocol_merge_and_post_merge_validation_required"] is True, "protocol merge gate disabled")
    require(gate["separate_explicit_author_authorization_required_after_merge"] is True, "separate execution authorization disabled")
    require(gate["real_trace_execution_allowed_by_this_protocol_branch"] is False, "protocol branch improperly authorizes execution")
    require(gate["scientific_endpoint_computation_before_that_authorization"] == "PROHIBITED", "endpoint prohibition drift")

    auth = authorization
    require(auth["authorization_id"] == "S8E-CANON-AUTH-001", "authorization id drift")
    require(auth["authorized"]["canonical_execution_protocol_design"] is True, "protocol design not authorized")
    require(auth["authorized"]["protocol_exact_head_validation"] is True, "protocol validation not authorized")
    require(auth["authorized"]["canonical_execution_after_protocol_merge"] is False, "authorization improperly enables canonical execution")
    for key in (
        "real_TRACE002_timing_endpoint_computation",
        "real_TRACE002_minimum_rate_endpoint_computation",
        "policy_profile_disruption_scientific_execution",
        "canonical_result_freeze",
    ):
        require(auth["not_authorized"][key] is True, f"{key} must remain not authorized")

    outputs = protocol["canonical_outputs"]
    require(len(outputs) == len(set(outputs)), "duplicate canonical output names")
    require("CANONICAL_CASE_RESULTS.csv" in outputs, "case results output missing")
    require("INDEPENDENT_AUDIT.json" in outputs, "independent audit output missing")
    require("RESULTS_HASH_MANIFEST.json" in outputs, "hash manifest output missing")

    prohibited_now = [
        root / "study8e/results/CANONICAL_CASE_RESULTS.csv",
        root / "study8e/results/CANONICAL_FINDINGS.json",
        root / "study8e/results/INDEPENDENT_AUDIT.json",
        root / "study8e/results/RESULTS_HASH_MANIFEST.json",
    ]
    require(
        not any(path.exists() for path in prohibited_now),
        "canonical scientific result artifact exists before execution authorization",
    )

    print("Study 8E canonical execution protocol validation: PASS")
    print("protocol_id=S8E-CANON-EXEC-001")
    print("cases_per_anchor=144")
    print("real_trace_execution_authorized=false")
    print("scientific_endpoint_artifacts_present=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
