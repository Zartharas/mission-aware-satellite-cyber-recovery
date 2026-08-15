from __future__ import annotations

import hashlib
import json
from typing import Any


def _canonical(value: Any) -> bytes:
    return (
        json.dumps(
            value,
            ensure_ascii=True,
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
    ).encode("utf-8")


def compute_rollback_request_sha256(
    request: dict[str, Any],
) -> str:
    payload = dict(request)
    payload.pop("request_sha256", None)
    return hashlib.sha256(_canonical(payload)).hexdigest()


def build_verified_rollback_request(
    *,
    event_instance: dict[str, Any],
    policy_decision: dict[str, Any],
    manifest: dict[str, Any],
    candidate_verification: dict[str, Any],
) -> dict[str, Any]:
    if policy_decision["selected_action"] != "REQUEST_VERIFIED_ROLLBACK":
        raise ValueError("policy action is not REQUEST_VERIFIED_ROLLBACK")

    evidence = dict(event_instance["policy_visible_evidence"])

    if evidence.get("rollback_available") is not True:
        raise ValueError("policy-visible rollback availability not established")

    if evidence.get("integrity_check_passed") is not False:
        raise ValueError("policy-visible integrity failure not established")

    if candidate_verification.get("accepted") is not False:
        raise ValueError("candidate is not rejected")

    reasons = sorted(candidate_verification.get("reasons", []))
    if "sha256_mismatch" not in reasons:
        raise ValueError("candidate rejection lacks sha256_mismatch")

    payload = {
        "schema": 1,
        "event_id": event_instance["event_id"],
        "requested_policy_id": policy_decision["requested_policy_id"],
        "delegated_policy_id": policy_decision["delegated_policy_id"],
        "action": "REQUEST_VERIFIED_ROLLBACK",
        "component": manifest["component"],
        "approved_version": manifest["approved_version"],
        "approved_target_sha256": manifest["approved_sha256"],
        "rejected_candidate_sha256": candidate_verification["actual_sha256"],
        "rejection_reasons": reasons,
        "rollback_available": True,
        "request_ready": True,
        "rollback_staging_performed": False,
        "rollback_activation_performed": False,
        "recovery_execution_performed": False,
        "trusted_recovery_verified": False,
        "oracle_ground_truth_read": False,
    }

    request_sha256 = compute_rollback_request_sha256(payload)
    return {
        **payload,
        "request_sha256": request_sha256,
    }
