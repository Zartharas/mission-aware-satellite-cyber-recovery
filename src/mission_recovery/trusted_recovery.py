from __future__ import annotations

from typing import Any

from .rollback_requests import compute_rollback_request_sha256
from .update_artifacts import verify_candidate


def validate_rollback_request(
    *,
    request: dict[str, Any],
    policy_decision: dict[str, Any],
    manifest: dict[str, Any],
    pre_recovery_candidate_sha256: str,
) -> dict[str, Any]:
    reasons: list[str] = []

    computed_request_sha256 = compute_rollback_request_sha256(request)
    if request.get("request_sha256") != computed_request_sha256:
        reasons.append("request_sha256_mismatch")

    if policy_decision.get("selected_action") != "REQUEST_VERIFIED_ROLLBACK":
        reasons.append("policy_not_rollback_authorized")

    if request.get("action") != "REQUEST_VERIFIED_ROLLBACK":
        reasons.append("wrong_action")

    if request.get("action") != policy_decision.get("selected_action"):
        reasons.append("request_policy_action_mismatch")

    if request.get("event_id") != policy_decision.get("event_id"):
        reasons.append("event_binding_mismatch")

    if (
        request.get("requested_policy_id")
        != policy_decision.get("requested_policy_id")
    ):
        reasons.append("requested_policy_mismatch")

    if (
        request.get("delegated_policy_id")
        != policy_decision.get("delegated_policy_id")
    ):
        reasons.append("delegated_policy_mismatch")

    if request.get("request_ready") is not True:
        reasons.append("request_not_ready")

    if request.get("rollback_available") is not True:
        reasons.append("rollback_not_available")

    if request.get("component") != manifest["component"]:
        reasons.append("component_mismatch")

    if request.get("approved_version") != manifest["approved_version"]:
        reasons.append("approved_version_mismatch")

    if request.get("approved_target_sha256") != manifest["approved_sha256"]:
        reasons.append("approved_target_mismatch")

    if (
        request.get("rejected_candidate_sha256")
        != pre_recovery_candidate_sha256
    ):
        reasons.append("rejected_candidate_mismatch")

    rejection_reasons = request.get("rejection_reasons")
    if (
        not isinstance(rejection_reasons, list)
        or "sha256_mismatch" not in rejection_reasons
    ):
        reasons.append("rejection_reason_missing")

    if request.get("rollback_staging_performed") is not False:
        reasons.append("rollback_staging_already_performed")

    if request.get("rollback_activation_performed") is not False:
        reasons.append("rollback_activation_already_performed")

    if request.get("recovery_execution_performed") is not False:
        reasons.append("recovery_already_performed")

    if request.get("trusted_recovery_verified") is not False:
        reasons.append("trusted_recovery_already_verified")

    if policy_decision.get("oracle_ground_truth_read") is not False:
        reasons.append("policy_oracle_boundary_violation")

    if request.get("oracle_ground_truth_read") is not False:
        reasons.append("oracle_boundary_violation")

    return {
        "accepted": not reasons,
        "reasons": reasons,
        "request_sha256": request.get("request_sha256"),
        "computed_request_sha256": computed_request_sha256,
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
