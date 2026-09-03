from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def load_json(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def sha256(relative: str) -> str:
    digest = hashlib.sha256()
    with (ROOT / relative).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    close = load_json("study8/STUDY8_TECHNICAL_CLOSE.json")
    freeze = load_json("study8/analysis/RESULTS_FREEZE_MANIFEST.json")
    audit = load_json("study8/results/S8-PQC-ICR-001/independent_audit_summary.json")
    findings = load_json("study8/analysis/results/primary_findings.json")

    assert close["schema"] == 1
    assert close["study_id"] == "S8-PQC-ICR-001"
    assert close["status"] == "TECHNICALLY_CLOSED_PUBLICATION_INTEGRATION_NOT_STARTED"

    science_merge = close["science_merge"]
    assert science_merge["pull_request"] == 89
    assert science_merge["validated_head"] == "1356b73d1edc01c8618c9290460f4fbf22c458df"
    assert science_merge["main_commit"] == "63106778559c3127a7d6e8765d52939b73a3f35b"
    assert science_merge["post_merge_ci"]["run_id"] == 33761681328
    assert science_merge["post_merge_ci"]["run_attempt"] == 1
    assert science_merge["post_merge_ci"]["conclusion"] == "success"

    population = close["canonical_population"]
    for key in ("expected_rows", "primary_rows", "independent_rows", "exact_row_matches"):
        assert population[key] == 3456, (key, population[key])
    assert population["mismatch_count"] == 0

    assert audit["experiment_id"] == "S8-PQC-ICR-001"
    assert audit["expected_population"] == 3456
    assert audit["primary_rows"] == 3456
    assert audit["independent_rows"] == 3456
    assert audit["exact_row_matches"] == 3456
    assert audit["mismatch_count"] == 0
    assert audit["all_rows_match"] is True
    assert audit["status"] == "INDEPENDENT_ROW_BY_ROW_AUDIT_PASS"

    assert freeze["freeze_id"] == "S8-RESULTS-FREEZE-001"
    assert freeze["experiment_id"] == "S8-PQC-ICR-001"
    assert freeze["statistical_findings_frozen"] is True
    assert freeze["canonical_reexecution_authorized"] is False
    assert freeze["analysis_reexecution_authorized"] is False
    assert freeze["publication_authorized"] is False

    for relative, expected in freeze["bound_files"].items():
        observed = sha256(relative)
        assert observed == expected, f"SHA-256 mismatch for {relative}: {observed} != {expected}"

    frozen_hashes = close["frozen_sha256"]
    assert frozen_hashes["canonical_observations_csv"] == freeze["bound_files"][
        "study8/results/S8-PQC-ICR-001/canonical_observations.csv"
    ]
    assert frozen_hashes["primary_findings_json"] == freeze["bound_files"][
        "study8/analysis/results/primary_findings.json"
    ]
    assert frozen_hashes["independent_findings_json"] == freeze["bound_files"][
        "study8/analysis/results/independent_findings.json"
    ]
    assert frozen_hashes["interpretation_audit_json"] == freeze["bound_files"][
        "study8/analysis/results/interpretation_audit.json"
    ]

    assert findings["population_semantics"] == "complete_deterministic_finite_population"
    assert findings["population_validation"]["row_count"] == 3456
    assert findings["population_validation"]["unique_factor_positions"] == 3456
    assert findings["inference_policy"]["sampling_p_values"] is False
    assert findings["inference_policy"]["sampling_confidence_intervals"] is False
    assert findings["inference_policy"]["bootstrap"] is False
    assert findings["inference_policy"]["permutation_tests"] is False

    policy_success = findings["primary"]["policy_success"]
    assert set(policy_success) == {
        "P0_HARD_CUTOVER",
        "P1_STAGED_CUTOVER",
        "P2_HYBRID_OVERLAP",
        "P3_CONTACT_AWARE_STAGED",
    }
    assert all(item["fraction"] == "635/864" for item in policy_success.values())
    assert findings["primary"]["P3_minus_P1_success_risk_difference"]["fraction"] == "0/1"
    assert findings["primary"]["P3_minus_P1_success_risk_difference"]["percentage_points_6"] == "0.000000"

    primary = close["frozen_primary_finding"]
    assert primary["policy_success_each"] == "635/864"
    assert primary["P3_minus_P1_risk_difference"] == "0/1"
    assert primary["negative_primary_finding_preserved"] is True
    assert primary["hypothesis_rescue_permitted"] is False

    profiles = findings["cryptographic_profile_analysis"]["marginal_success_by_profile"]
    assert profiles["PROFILE_512_44"]["fraction"] == "15/16"
    assert profiles["PROFILE_768_65"]["fraction"] == "187/288"
    assert profiles["PROFILE_1024_87"]["fraction"] == "89/144"
    assert findings["cryptographic_profile_analysis"]["paired_ordered_profile_check"][
        "non_increasing_success_pattern_count"
    ] == 1152

    publication = close["publication"]
    assert publication["publication_integration_authorized"] is False
    assert publication["publication_package_created"] is False
    assert publication["venue_selected_for_study8"] is False

    execution = close["execution"]
    assert execution["canonical_reexecution_authorized"] is False
    assert execution["analysis_reexecution_authorized"] is False
    assert execution["new_scientific_execution_authorized"] is False

    print("study8_technical_close=PASS")
    print("canonical_rows=3456")
    print("independent_rows=3456")
    print("row_mismatches=0")
    print("primary_policy_success=635/864")
    print("P3_minus_P1=0/1")
    print("publication_integration_authorized=false")
    print("scientific_reexecution_authorized=false")


if __name__ == "__main__":
    main()
