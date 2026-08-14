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


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def build_approved_update() -> bytes:
    return _canonical(
        {
            "schema": 1,
            "artifact_type": "synthetic_mission_table",
            "component": "sample",
            "version": "2.0.0",
            "payload": {
                "profile": "nominal",
                "sample_noop_count": 1,
                "sample_noop_period_seconds": 5,
            },
            "provenance": {
                "issuer": "mission-aware-research-approved",
                "source": "synthetic-only",
            },
            "executable": False,
        }
    )


def build_tampered_update() -> bytes:
    # Same claimed version/provenance envelope; payload is modified.
    return _canonical(
        {
            "schema": 1,
            "artifact_type": "synthetic_mission_table",
            "component": "sample",
            "version": "2.0.0",
            "payload": {
                "profile": "nominal",
                "sample_noop_count": 3,
                "sample_noop_period_seconds": 5,
            },
            "provenance": {
                "issuer": "mission-aware-research-approved",
                "source": "synthetic-only",
            },
            "executable": False,
        }
    )


def build_downgrade_update() -> bytes:
    return _canonical(
        {
            "schema": 1,
            "artifact_type": "synthetic_mission_table",
            "component": "sample",
            "version": "1.9.0",
            "payload": {
                "profile": "nominal",
                "sample_noop_count": 1,
                "sample_noop_period_seconds": 5,
            },
            "provenance": {
                "issuer": "mission-aware-research-approved",
                "source": "synthetic-only",
            },
            "executable": False,
        }
    )


def build_manifest() -> dict[str, Any]:
    approved = build_approved_update()
    return {
        "schema": 1,
        "component": "sample",
        "approved_version": "2.0.0",
        "minimum_allowed_version": "2.0.0",
        "approved_sha256": sha256_hex(approved),
        "artifact_type": "synthetic_mission_table",
        "executable": False,
    }


def verify_candidate(candidate: bytes, manifest: dict[str, Any]) -> dict[str, Any]:
    reasons: list[str] = []
    actual_sha = sha256_hex(candidate)

    try:
        metadata = json.loads(candidate.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return {
            "accepted": False,
            "actual_sha256": actual_sha,
            "reasons": ["invalid_artifact_encoding"],
        }

    if actual_sha != manifest["approved_sha256"]:
        reasons.append("sha256_mismatch")

    if metadata.get("component") != manifest["component"]:
        reasons.append("component_mismatch")

    version = metadata.get("version")
    if version != manifest["approved_version"]:
        reasons.append("version_not_approved")

    # For this controlled catalog, semantic-version tuples are sufficient.
    if isinstance(version, str):
        try:
            vt = tuple(int(x) for x in version.split("."))
            mt = tuple(int(x) for x in manifest["minimum_allowed_version"].split("."))
            if vt < mt:
                reasons.append("version_below_minimum")
        except ValueError:
            reasons.append("invalid_version")
    else:
        reasons.append("invalid_version")

    if metadata.get("executable") is not False:
        reasons.append("unexpected_executable_artifact")

    return {
        "accepted": not reasons,
        "actual_sha256": actual_sha,
        "reasons": reasons,
        "version": version,
    }
