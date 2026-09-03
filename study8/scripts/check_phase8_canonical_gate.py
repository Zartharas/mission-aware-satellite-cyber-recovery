from __future__ import annotations

import hashlib
import json
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AUTH_PATH = ROOT / "study8/CAMPAIGN_AUTHORIZATION.json"
REQUEST_PATH = ROOT / "study8/runtime/CANONICAL_RUN_REQUEST.json"
BINDING_PATH = ROOT / "study8/PRE_RUNTIME_HASH_BINDING.json"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def main() -> None:
    auth = json.loads(AUTH_PATH.read_text(encoding="utf-8"))
    request = json.loads(REQUEST_PATH.read_text(encoding="utf-8"))
    binding = json.loads(BINDING_PATH.read_text(encoding="utf-8"))

    assert auth["authorization_id"] == "S8-CANONICAL-001"
    assert auth["experiment_id"] == "S8-PQC-ICR-001"
    assert auth["single_use"] is True
    assert auth["consumed"] is False
    assert auth["canonical_execution_authorized"] is True
    assert auth["results_generation_authorized"] is True
    assert auth["independent_reproduction_authorized"] is True
    assert auth["independent_rowwise_audit_authorized"] is True
    assert auth["scientific_interpretation_authorized"] is False
    assert auth["statistical_findings_freeze_authorized"] is False
    assert auth["results_merge_authorized"] is False
    assert auth["expected_population_observations"] == 3456
    assert auth["required_post_merge_ci_run_id"] == 33712086123
    assert auth["required_post_merge_ci_conclusion"] == "success"

    assert request["request_id"] == auth["canonical_run_request_id"]
    assert request["authorization_id"] == auth["authorization_id"]
    assert request["requested_population_observations"] == 3456
    assert request["require_exact_rowwise_parity"] is True
    assert request["allow_scientific_interpretation"] is False
    assert request["allow_statistical_findings_freeze"] is False
    assert request["allow_results_merge"] is False

    assert binding["binding_id"] == auth["pre_runtime_binding_id"]
    assert binding["status"] == "HASH_BOUND_VERIFIED_PRE_RUNTIME"
    assert binding["bound_files"] == auth["bound_files"]

    branch = os.environ.get("GITHUB_REF_NAME", git("branch", "--show-current"))
    attempt = os.environ.get("GITHUB_RUN_ATTEMPT", "1")
    assert branch == auth["required_branch"], (branch, auth["required_branch"])
    assert attempt == "1", f"single-use canonical execution rejects rerun attempt {attempt}"

    head = git("rev-parse", "HEAD")
    parents = git("show", "-s", "--format=%P", "HEAD").split()
    assert len(parents) == 1, parents
    assert parents[0] == auth["authorized_parent_main_commit"], (head, parents)
    assert request["expected_parent_main_commit"] == parents[0]

    for relative, expected in auth["bound_files"].items():
        path = ROOT / relative
        assert path.is_file(), relative
        actual = sha256(path)
        assert actual == expected, f"hash mismatch {relative}: {actual} != {expected}"

    assert not (ROOT / "study8/results/S8-PQC-ICR-001").exists()

    print("phase8_canonical_gate=PASS")
    print(f"canonical_trigger_head={head}")
    print(f"authorized_parent_main_commit={parents[0]}")
    print("single_use_run_attempt=1")
    print("expected_population=3456")
    print("scientific_interpretation=PROHIBITED")


if __name__ == "__main__":
    main()
