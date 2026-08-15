from __future__ import annotations

from typing import Any

from .update_artifacts import verify_candidate


def validate_rollback_request(
    *,
    request: dict[str, Any],
    manifest: dict[str, Any],
    pre_recovery_candidate_sha256: str,
) -> dict[str, Any]:
    reasons: list[str] = []

    if request.get("action") != "REQUEST_VERIFIED_ROLLBACK":
        reasons.append("wrong_action")

    if request.get("request_ready") is not True:
        reasons.append("request_not_ready")

    if request.get("approved_target_sha256") != manifest["approved_sha256"]:
        reasons.append("approved_target_mismatch")

    if (
        request.get("rejected_candidate_sha256")
        != pre_recovery_candidate_sha256
    ):
        reasons.append("rejected_candidate_mismatch")

    if request.get("oracle_ground_truth_read") is not False:
        reasons.append("oracle_boundary_violation")

    return {
        "accepted": not reasons,
        "reasons": reasons,
        "approved_target_sha256": manifest["approved_sha256"],
        "rejected_candidate_sha256": pre_recovery_candidate_sha256,
    }


def verify_replacement_source(
    candidate: bytes,
    manifest: dict[str, Any],
) -> dict[str, Any]:
    result = verify_candidate(candidate, manifest)
    return {
        "accepted": result["accepted"],
        "actual_sha256": result["actual_sha256"],
        "reasons": result["reasons"],
        "version": result.get("version"),
    }


def verify_terminal_recovery(
    *,
    terminal_candidate: bytes,
    manifest: dict[str, Any],
    rejected_candidate_sha256: str,
) -> dict[str, Any]:
    verification = verify_candidate(terminal_candidate, manifest)
    actual_sha = verification["actual_sha256"]

    terminal_matches_approved = (
        actual_sha == manifest["approved_sha256"]
    )
    terminal_differs_from_rejected = (
        actual_sha != rejected_candidate_sha256
    )

    trusted = (
        verification["accepted"]
        and terminal_matches_approved
        and terminal_differs_from_rejected
    )

    reasons = list(verification["reasons"])
    if not terminal_matches_approved:
        reasons.append("terminal_not_approved_target")
    if not terminal_differs_from_rejected:
        reasons.append("terminal_still_rejected_candidate")

    return {
        "trusted_recovery_verified": trusted,
        "terminal_candidate_accepted": verification["accepted"],
        "terminal_sha256": actual_sha,
        "approved_target_sha256": manifest["approved_sha256"],
        "rejected_candidate_sha256": rejected_candidate_sha256,
        "terminal_matches_approved": terminal_matches_approved,
        "terminal_differs_from_rejected": terminal_differs_from_rejected,
        "version": verification.get("version"),
        "reasons": sorted(set(reasons)),
    }
