from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

PLAN_LOCK_COMMIT = "4ecbe51fda3d053a4b950a2ad7c95439146b14ae"
SOURCE_EVIDENCE_COMMIT = "a31c574e4887e3b92b72dad84933905feb100ef8"
EXPECTED_DATASET_SHA256 = "cfc65b6663be4e9f17a00ed102730f8642efcbbd844045acce032ff09a0bcabf"

AUTH = Path("study8/analysis/PHASE8_5_ANALYSIS_AUTHORIZATION.json")
PLAN = Path("study8/analysis/PHASE8_5_STATISTICAL_ANALYSIS_PLAN.json")
CANONICAL_AUTH = Path("study8/CAMPAIGN_AUTHORIZATION.json")
CANONICAL_AUDIT = Path("study8/results/S8-PQC-ICR-001/independent_audit_summary.json")
DATA = Path("study8/results/S8-PQC-ICR-001/canonical_observations.csv")


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], text=True).strip()


def main() -> None:
    auth = load(AUTH)
    plan = load(PLAN)
    campaign = load(CANONICAL_AUTH)
    audit = load(CANONICAL_AUDIT)

    parents = git("rev-list", "--parents", "-n", "1", "HEAD").split()
    if len(parents) != 2 or parents[1] != PLAN_LOCK_COMMIT:
        raise SystemExit("analysis construction trigger must have the plan-lock commit as its sole parent")
    if git("rev-parse", f"{PLAN_LOCK_COMMIT}^") != SOURCE_EVIDENCE_COMMIT:
        raise SystemExit("plan-lock lineage does not point to canonical evidence commit")

    if sha256(DATA) != EXPECTED_DATASET_SHA256:
        raise SystemExit("canonical dataset hash mismatch")
    if auth["authorization_id"] != "S8-ANALYSIS-001":
        raise SystemExit("analysis authorization mismatch")
    if auth["outcome_values_inspected_before_plan_lock"] is not False:
        raise SystemExit("plan timing boundary violated")
    if auth["statistical_analysis_authorized"] is not True:
        raise SystemExit("statistical analysis not authorized")
    if auth["statistical_findings_freeze_authorized"] is not False:
        raise SystemExit("findings freeze must remain closed")
    if auth["results_merge_authorized"] is not False:
        raise SystemExit("results merge must remain closed")
    if plan["plan_id"] != "S8-SAP-001" or plan["plan_status"] != "LOCKED_BEFORE_OUTCOME_VALUE_INSPECTION":
        raise SystemExit("analysis plan not locked")
    if plan["source_dataset_sha256"] != EXPECTED_DATASET_SHA256:
        raise SystemExit("plan dataset binding mismatch")
    if plan["inference_policy"]["sampling_p_values"] is not False:
        raise SystemExit("sampling p-values must be disabled")
    if campaign["status"] != "CONSUMED_CANONICAL_EXECUTION_AUDITED_PASS":
        raise SystemExit("canonical campaign not consumed/audited")
    if campaign["rowwise_audit_mismatch_count"] != 0:
        raise SystemExit("canonical rowwise mismatch")
    if audit["status"] != "INDEPENDENT_ROW_BY_ROW_AUDIT_PASS" or audit["mismatch_count"] != 0:
        raise SystemExit("canonical independent audit not pass")

    print("phase8_5_analysis_gate=PASS")
    print(f"phase8_5_plan_lock_commit={PLAN_LOCK_COMMIT}")
    print(f"phase8_5_source_evidence_commit={SOURCE_EVIDENCE_COMMIT}")
    print(f"phase8_5_dataset_sha256={EXPECTED_DATASET_SHA256}")
    print("statistical_findings_freeze=PROHIBITED")
    print("results_merge=PROHIBITED")


if __name__ == "__main__":
    main()
