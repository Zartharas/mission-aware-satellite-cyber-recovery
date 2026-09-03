from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
ANALYSIS = ROOT / "study8" / "analysis"
RESULTS = ANALYSIS / "results"
CANONICAL = ROOT / "study8" / "results" / "S8-PQC-ICR-001" / "canonical_observations.csv"

EXPECTED_CANONICAL_SHA256 = "cfc65b6663be4e9f17a00ed102730f8642efcbbd844045acce032ff09a0bcabf"
EXPECTED_ANALYSIS_RUN_ID = 33713616663
EXPECTED_ANALYSIS_HEAD = "e661e070e481d8a0fea14ec96f777a7253de1f10"
EXPECTED_ANALYSIS_EVIDENCE_COMMIT = "b9c1c2c1ca59cc5bdc04e3226b1858577d3ea0f3"
EXPECTED_PLAN_LOCK = "4ecbe51fda3d053a4b950a2ad7c95439146b14ae"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    auth = load(ANALYSIS / "PHASE8_6_RESULTS_FREEZE_AUTHORIZATION.json")
    phase5_auth = load(ANALYSIS / "PHASE8_5_ANALYSIS_AUTHORIZATION.json")
    plan = load(ANALYSIS / "PHASE8_5_STATISTICAL_ANALYSIS_PLAN.json")
    audit = load(RESULTS / "findings_audit.json")
    interpretation = load(RESULTS / "interpretation_audit.json")
    provenance = load(RESULTS / "analysis_provenance.json")

    assert auth["authorization_id"] == "S8-RESULTS-FREEZE-001"
    assert auth["source_analysis_evidence_commit"] == EXPECTED_ANALYSIS_EVIDENCE_COMMIT
    assert auth["source_plan_lock_commit"] == EXPECTED_PLAN_LOCK
    assert auth["source_canonical_dataset_sha256"] == EXPECTED_CANONICAL_SHA256
    assert auth["statistical_findings_freeze_authorized"] is True
    assert auth["analysis_output_hash_binding_authorized"] is True
    assert auth["interpretation_audit_hash_binding_authorized"] is True
    assert auth["results_freeze_pr_authorized"] is True
    assert auth["complete_pr_ci_authorized"] is True
    assert auth["results_merge_authorized"] is False
    assert auth["publication_authorized"] is False
    assert auth["canonical_reexecution_authorized"] is False
    assert auth["analysis_reexecution_authorized"] is False
    assert auth["scientific_files_may_change"] is False

    assert phase5_auth["statistical_analysis_authorized"] is True
    assert phase5_auth["results_merge_authorized"] is False
    assert phase5_auth["statistical_findings_freeze_authorized"] is False
    assert phase5_auth["sampling_inference_authorized"] is False

    assert plan["plan_id"] == "S8-SAP-001"
    assert plan["population_semantics"] == "complete_deterministic_finite_population"
    assert plan["inference_policy"]["sampling_p_values"] is False
    assert plan["inference_policy"]["sampling_confidence_intervals"] is False
    assert plan["inference_policy"]["bootstrap"] is False
    assert plan["inference_policy"]["permutation_tests"] is False

    assert audit["status"] == "INDEPENDENT_STATISTICAL_REPRODUCTION_PASS_FINDINGS_NOT_FROZEN"
    assert audit["analyzed_rows"] == 3456
    assert audit["byte_identical_findings"] is True
    assert audit["object_identical_findings"] is True
    assert audit["sampling_inference_performed"] is False
    assert audit["statistical_findings_frozen"] is False
    assert audit["results_merge_authorized"] is False

    assert interpretation["audit_id"] == "S8-FINDINGS-AUDIT-001"
    assert interpretation["analysis_run_id"] == EXPECTED_ANALYSIS_RUN_ID
    assert interpretation["analysis_evidence_commit"] == EXPECTED_ANALYSIS_EVIDENCE_COMMIT
    assert interpretation["canonical_dataset_sha256"] == EXPECTED_CANONICAL_SHA256
    assert interpretation["independent_statistical_reproduction_pass"] is True
    assert interpretation["primary_finding"]["P3_minus_P1_risk_difference"] == "0/1"
    assert interpretation["primary_finding"]["all_six_pairwise_policy_success_differences_zero"] is True
    assert interpretation["adversarial_review"]["primary_hypothesis_rescue_attempted"] is False
    assert interpretation["adversarial_review"]["sampling_significance_claim_attempted"] is False
    assert interpretation["adversarial_review"]["operational_latency_or_rf_claim_attempted"] is False
    assert interpretation["scientific_interpretation_completed"] is True
    assert interpretation["statistical_findings_frozen"] is False
    assert interpretation["results_merge_authorized"] is False
    assert interpretation["publication_authorized"] is False

    assert provenance["github_run_id"] == EXPECTED_ANALYSIS_RUN_ID
    assert provenance["analysis_trigger_head"] == EXPECTED_ANALYSIS_HEAD
    assert provenance["plan_lock_commit"] == EXPECTED_PLAN_LOCK
    assert provenance["canonical_observations_sha256"] == EXPECTED_CANONICAL_SHA256
    assert provenance["sampling_inference_performed"] is False
    assert provenance["statistical_findings_frozen"] is False
    assert provenance["results_merge_authorized"] is False

    assert sha256(CANONICAL) == EXPECTED_CANONICAL_SHA256
    assert sha256(RESULTS / "primary_findings.json") == sha256(RESULTS / "independent_findings.json")

    print("phase8_6_freeze_candidate=PASS")
    print("canonical_dataset_sha256=" + sha256(CANONICAL))
    print("primary_findings_sha256=" + sha256(RESULTS / "primary_findings.json"))
    print("independent_findings_sha256=" + sha256(RESULTS / "independent_findings.json"))
    print("interpretation_audit_sha256=" + sha256(RESULTS / "interpretation_audit.json"))
    print("results_merge=PROHIBITED")


if __name__ == "__main__":
    main()
