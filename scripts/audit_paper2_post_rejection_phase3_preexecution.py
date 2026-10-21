#!/usr/bin/env python3
"""Fail-closed audit for Paper-2 Phase-3 pre-execution state.

This audit verifies that the newly authorized S3X source-verification and S6X
pre-runtime implementation workspaces exist while scientific execution,
building, artifact generation, and publication use remain closed.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REBUILD = ROOT / "publication/Paper_2_Studies_3_4_6/Post_Rejection_Rebuild"
S3X = ROOT / "study3x"
S6X = ROOT / "study6x"

PHASE3_STATUS = REBUILD / "PAPER2_PHASE3_PREEXECUTION_STATUS.json"


def fail(message: str) -> None:
    print(f"[FAIL] {message}", file=sys.stderr)
    raise SystemExit(1)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def load_json(path: Path) -> dict:
    if not path.is_file():
        fail(f"missing JSON: {path.relative_to(ROOT)}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        fail(f"invalid JSON {path.relative_to(ROOT)}: {exc}")


def check_phase3_status() -> None:
    status = load_json(PHASE3_STATUS)
    require(status.get("phase") == "POST_REJECTION_REBUILD_PHASE3_PREEXECUTION", "Phase-3 identifier drift")
    require(
        status.get("status")
        == "AUTHORIZED_S3X_SOURCE_VERIFICATION_AND_S6X_PRE_RUNTIME_IMPLEMENTATION__NO_SCIENTIFIC_EXECUTION",
        "Phase-3 status drift",
    )
    require(
        status.get("branch_base_commit") == "a2b6f2e02c4075d2e9cd1976888dae38464a11c1",
        "Phase-3 branch base drift",
    )

    predecessor = status.get("predecessor", {})
    require(predecessor.get("pull_request") == 173, "Phase-3 predecessor PR drift")
    require(
        predecessor.get("merge_commit") == "a2b6f2e02c4075d2e9cd1976888dae38464a11c1",
        "Phase-3 predecessor merge drift",
    )
    require(predecessor.get("pre_merge_ci", {}).get("conclusion") == "success", "PR #173 pre-merge CI not bound success")
    require(predecessor.get("post_merge_ci", {}).get("conclusion") == "success", "PR #173 post-merge CI not bound success")

    frozen = status.get("frozen_foundation", {})
    require(frozen.get("study3", {}).get("mutable") is False, "Study 3 unexpectedly mutable")
    require(frozen.get("study4", {}).get("mutable") is False, "Study 4 unexpectedly mutable")
    require(frozen.get("study6", {}).get("mutable") is False, "Study 6 unexpectedly mutable")
    require(frozen.get("pooling_allowed") is False, "Paper-2 pooling unexpectedly allowed")

    s3x = status.get("s3x", {})
    require(s3x.get("local_source_verification_authorized") is True, "S3X local verification not authorized")
    require(s3x.get("source_identity_freeze_authorized") is True, "S3X source freeze not authorized")
    require(s3x.get("source_identity_freeze_completed") is False, "S3X source freeze incorrectly claimed complete")
    require(s3x.get("gap_rule_freeze_authorized") is False, "S3X gap rule unexpectedly authorized")
    require(s3x.get("trace_extraction_authorized") is False, "S3X trace extraction unexpectedly authorized")
    require(s3x.get("scientific_execution_authorized") is False, "S3X scientific execution unexpectedly authorized")

    s6x = status.get("s6x", {})
    require(s6x.get("implementation_workspace_authorized") is True, "S6X implementation workspace not authorized")
    require(s6x.get("pre_runtime_validation_authorized") is True, "S6X pre-runtime validation not authorized")
    require(s6x.get("build_authorized") is False, "S6X build unexpectedly authorized")
    require(s6x.get("fixture_application_to_build_authorized") is False, "S6X fixture application unexpectedly authorized")
    require(s6x.get("artifact_signing_authorized") is False, "S6X artifact signing unexpectedly authorized")
    require(s6x.get("scientific_execution_authorized") is False, "S6X scientific execution unexpectedly authorized")
    require(s6x.get("canonical_results_authorized") is False, "S6X canonical results unexpectedly authorized")

    manuscript = status.get("manuscript", {})
    require(manuscript.get("rewrite_authorized") is False, "Paper-2 manuscript rewrite unexpectedly authorized")
    require(manuscript.get("venue_lock_authorized") is False, "Paper-2 venue lock unexpectedly authorized")
    require(manuscript.get("publisher_submission_authorized") is False, "Paper-2 publisher submission unexpectedly authorized")


def check_s3x_workspace() -> None:
    require(S3X.is_dir(), "study3x workspace missing")
    auth = load_json(S3X / "S3X_SOURCE_VERIFICATION_AUTHORIZATION_20260926.json")
    require(auth.get("experiment_id") == "S3X-ETA-001", "S3X authorization identity drift")
    permissions = auth.get("permissions", {})
    require(permissions.get("local_archive_verification_authorized") is True, "S3X archive verification not authorized")
    require(permissions.get("source_identity_freeze_authorized") is True, "S3X source freeze not authorized")
    for key in (
        "gap_rule_freeze_authorized",
        "trace_extraction_authorized",
        "recovery_policy_execution_authorized",
        "scientific_execution_authorized",
        "manuscript_claim_use_authorized",
    ):
        require(permissions.get(key) is False, f"S3X closed gate unexpectedly open: {key}")

    require((S3X / "validation/finalize_esa_v2_source_freeze.py").is_file(), "S3X finalizer missing")
    require((S3X / "validation/run_local_source_freeze.sh").is_file(), "S3X local freeze runner missing")

    require(not (S3X / "results").exists(), "S3X results directory must not exist")
    require(not (S3X / "canonical").exists(), "S3X canonical directory must not exist")
    require(not (S3X / "S3X_SOURCE_FREEZE_001.json").exists(), "S3X freeze cannot be pre-populated without local verification")


def check_s6x_workspace() -> None:
    require(S6X.is_dir(), "study6x workspace missing")
    auth = load_json(S6X / "S6X_PREEXECUTION_AUTHORIZATION_20260926.json")
    permissions = auth.get("permissions", {})
    require(permissions.get("implementation_workspace_authorized") is True, "S6X workspace authorization drift")
    require(permissions.get("pre_runtime_validation_authorized") is True, "S6X pre-runtime authorization drift")
    for key in (
        "build_authorized",
        "fixture_application_to_build_authorized",
        "artifact_signing_authorized",
        "provenance_observation_generation_authorized",
        "independent_rebuild_authorized",
        "scientific_execution_authorized",
        "canonical_results_authorized",
    ):
        require(permissions.get(key) is False, f"S6X closed gate unexpectedly open: {key}")

    pin = load_json(S6X / "S6X_SOURCE_PIN.json")
    require(pin.get("source_pin_id") == "S6X-CFS-LC-V701-PIN-001", "S6X source pin identity drift")
    require(pin.get("cfs", {}).get("tag_commit") == "088b2fa828db9ff7e00733f1908e0eeb59f66ce3", "cFS commit drift")
    require(pin.get("limit_checker", {}).get("commit") == "a1c3a47ea1fa5c0d7751d6ff88848dc9bd8a6c7a", "LC commit drift")

    blobs = pin.get("limit_checker", {}).get("tracked_blobs", {})
    require(blobs.get("fsw/src/lc_watch.c") == "67e8bb9d6270a1c5251343f08fa8e67717b7049f", "LC source blob drift")
    require(blobs.get("docs/lc_FunctionalRequirements.csv") == "22b5af26c37d7687a620b4997c3bd71a5871142e", "LC requirements blob drift")
    require(blobs.get("unit-test/lc_watch_tests.c") == "18a18d6099150146a5a02644aaebb298de261f52", "LC test blob drift")

    protocol = load_json(S6X / "S6X_PREEXECUTION_PROTOCOL.json")
    require(protocol.get("populations_pooled") is False, "S6X population pooling drift")
    require(protocol.get("objective_correctness_adjudicator", {}).get("gate_visible") is False, "S6X objective adjudicator leaked into gate")
    require(protocol.get("fixture", {}).get("applied") is False, "S6X fixture unexpectedly marked applied")
    require(protocol.get("build_authorized") is False, "S6X build unexpectedly authorized in protocol")
    require(protocol.get("scientific_execution_authorized") is False, "S6X scientific execution unexpectedly authorized in protocol")

    patch = (S6X / "fixtures/S6X_FIXTURE_GT_EQ_BOUNDARY_001.patch").read_text(encoding="utf-8")
    require(patch.count("-            EvalResult = (WPValue > CompareValue)") == 1, "S6X patch baseline hunk drift")
    require(patch.count("+            EvalResult = (WPValue >= CompareValue)") == 1, "S6X patch controlled hunk drift")

    require((S6X / "src/invariant_oracle.py").is_file(), "S6X invariant oracle missing")
    require((S6X / "tests/test_invariant_oracle.py").is_file(), "S6X oracle tests missing")
    require((S6X / "validation/validate_local_cfs_pin.py").is_file(), "S6X source-pin validator missing")

    for forbidden in ("results", "canonical", "build", "external", ".research_keys"):
        require(not (S6X / forbidden).exists(), f"tracked/visible S6X forbidden pre-execution path exists: {forbidden}")


def main() -> int:
    check_phase3_status()
    check_s3x_workspace()
    check_s6x_workspace()
    print("paper2_post_rejection_phase3_preexecution_audit=PASS")
    print("s3x_source_verification_authorized=YES")
    print("s3x_source_freeze_completed=NO")
    print("s3x_trace_extraction_authorized=NO")
    print("s6x_pre_runtime_implementation=PASS")
    print("s6x_build_authorized=NO")
    print("s6x_scientific_execution_authorized=NO")
    print("paper2_manuscript_rewrite_authorized=NO")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
