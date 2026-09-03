from __future__ import annotations

import hashlib
import json
from pathlib import Path

PRIMARY = Path("study8/analysis/results/primary_findings.json")
INDEPENDENT = Path("study8/analysis/results/independent_findings.json")
OUT = Path("study8/analysis/results/findings_audit.json")
EXPECTED_DATASET_SHA256 = "cfc65b6663be4e9f17a00ed102730f8642efcbbd844045acce032ff09a0bcabf"
PLAN_ID = "S8-SAP-001"
EXPERIMENT_ID = "S8-PQC-ICR-001"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    p = json.loads(PRIMARY.read_text(encoding="utf-8"))
    i = json.loads(INDEPENDENT.read_text(encoding="utf-8"))
    if p != i:
        raise SystemExit("primary and independent statistical findings differ")
    if PRIMARY.read_bytes() != INDEPENDENT.read_bytes():
        raise SystemExit("canonicalized primary and independent findings bytes differ")
    if p["source_dataset_sha256"] != EXPECTED_DATASET_SHA256:
        raise SystemExit("unexpected source dataset hash")
    if p["plan_id"] != PLAN_ID or p["experiment_id"] != EXPERIMENT_ID:
        raise SystemExit("plan or experiment mismatch")
    if p["population_validation"]["row_count"] != 3456:
        raise SystemExit("unexpected analyzed row count")
    if p["statistical_findings_frozen"] is not False:
        raise SystemExit("findings unexpectedly frozen")
    if p["results_merge_authorized"] is not False:
        raise SystemExit("results merge unexpectedly authorized")

    result = {
        "schema": 1,
        "experiment_id": EXPERIMENT_ID,
        "plan_id": PLAN_ID,
        "source_dataset_sha256": EXPECTED_DATASET_SHA256,
        "primary_findings_sha256": sha256(PRIMARY),
        "independent_findings_sha256": sha256(INDEPENDENT),
        "byte_identical_findings": True,
        "object_identical_findings": True,
        "analyzed_rows": 3456,
        "sampling_inference_performed": False,
        "findings_interpretation_completed": False,
        "statistical_findings_frozen": False,
        "results_merge_authorized": False,
        "status": "INDEPENDENT_STATISTICAL_REPRODUCTION_PASS_FINDINGS_NOT_FROZEN"
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("phase8_independent_statistical_reproduction=PASS")
    print(f"phase8_findings_sha256={result['primary_findings_sha256']}")


if __name__ == "__main__":
    main()
