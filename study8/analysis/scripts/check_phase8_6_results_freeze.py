from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
ANALYSIS = ROOT / "study8" / "analysis"
MANIFEST = ANALYSIS / "RESULTS_FREEZE_MANIFEST.json"
SUMS = ANALYSIS / "RESULTS_FREEZE_SHA256SUMS.txt"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert manifest["freeze_id"] == "S8-RESULTS-FREEZE-001"
    assert manifest["statistical_findings_frozen"] is True
    assert manifest["results_merge_authorized"] is False
    assert manifest["publication_authorized"] is False
    assert manifest["canonical_reexecution_authorized"] is False
    assert manifest["analysis_reexecution_authorized"] is False
    assert manifest["primary_independent_findings_byte_identical"] is True
    assert manifest["primary_finding_frozen"]["policy_success_each"] == "635/864"
    assert manifest["primary_finding_frozen"]["P3_minus_P1_risk_difference"] == "0/1"
    assert manifest["primary_finding_frozen"]["negative_primary_finding_preserved"] is True
    assert manifest["primary_finding_frozen"]["hypothesis_rescue_authorized"] is False

    bound = manifest["bound_files"]
    assert len(bound) == 12
    for rel, expected in bound.items():
        path = ROOT / rel
        assert path.is_file(), rel
        actual = sha256(path)
        assert actual == expected, f"hash mismatch: {rel}: {actual} != {expected}"

    primary = ROOT / "study8/analysis/results/primary_findings.json"
    independent = ROOT / "study8/analysis/results/independent_findings.json"
    assert primary.read_bytes() == independent.read_bytes()

    interpretation = json.loads((ROOT / "study8/analysis/results/interpretation_audit.json").read_text(encoding="utf-8"))
    assert interpretation["primary_finding"]["P3_minus_P1_risk_difference"] == "0/1"
    assert interpretation["primary_finding"]["all_six_pairwise_policy_success_differences_zero"] is True
    assert interpretation["adversarial_review"]["primary_hypothesis_rescue_attempted"] is False
    assert interpretation["adversarial_review"]["sampling_significance_claim_attempted"] is False
    assert interpretation["adversarial_review"]["operational_latency_or_rf_claim_attempted"] is False

    plan = json.loads((ROOT / "study8/analysis/PHASE8_5_STATISTICAL_ANALYSIS_PLAN.json").read_text(encoding="utf-8"))
    assert plan["inference_policy"]["sampling_p_values"] is False
    assert plan["inference_policy"]["sampling_confidence_intervals"] is False
    assert plan["inference_policy"]["bootstrap"] is False
    assert plan["inference_policy"]["permutation_tests"] is False

    expected_lines = [f"{digest}  {rel}" for rel, digest in bound.items()]
    actual_lines = [line for line in SUMS.read_text(encoding="utf-8").splitlines() if line]
    assert actual_lines == expected_lines

    print("phase8_6_results_freeze_binding=PASS")
    print("bound_files=12")
    print("primary_findings_sha256=" + bound["study8/analysis/results/primary_findings.json"])
    print("interpretation_audit_sha256=" + bound["study8/analysis/results/interpretation_audit.json"])
    print("statistical_findings=FROZEN")
    print("results_merge=PROHIBITED")


if __name__ == "__main__":
    main()
