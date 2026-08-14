from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CATALOG = ROOT / "configs" / "wp5_event_catalog.json"

ALLOWED_MISSION_STATES = {"M0", "M2", "M4"}
ALLOWED_CONTACT_CONDITIONS = {"C0", "C1"}
ALLOWED_EVIDENCE_CONDITIONS = {"T0", "T1"}


def _canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(
            value,
            ensure_ascii=True,
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
    ).encode("utf-8")


def load_catalog(path: Path | str = DEFAULT_CATALOG) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def event_definition(event_id: str, path: Path | str = DEFAULT_CATALOG) -> dict[str, Any]:
    catalog = load_catalog(path)
    for event in catalog["events"]:
        if event["id"] == event_id:
            return event
    raise KeyError(event_id)


def materialize_event(
    event_id: str,
    *,
    mission_state: str,
    contact_condition: str,
    evidence_condition: str,
    seed: int,
    path: Path | str = DEFAULT_CATALOG,
) -> dict[str, Any]:
    if mission_state not in ALLOWED_MISSION_STATES:
        raise ValueError(f"unsupported mission_state: {mission_state}")
    if contact_condition not in ALLOWED_CONTACT_CONDITIONS:
        raise ValueError(f"unsupported contact_condition: {contact_condition}")
    if evidence_condition not in ALLOWED_EVIDENCE_CONDITIONS:
        raise ValueError(f"unsupported evidence_condition: {evidence_condition}")

    definition = event_definition(event_id, path)

    policy_visible = dict(definition["policy_evidence"])
    omitted: list[str] = []
    if evidence_condition == "T1":
        omitted = list(definition["reduced_evidence_omit"])
        for key in omitted:
            policy_visible.pop(key, None)

    payload = {
        "schema": 1,
        "catalog_version": load_catalog(path)["catalog_version"],
        "event_id": definition["id"],
        "event_name": definition["name"],
        "execution_mode": "synthetic_model_only",
        "mission_state": mission_state,
        "contact_condition": contact_condition,
        "evidence_condition": evidence_condition,
        "seed": int(seed),
        "sparta": list(definition["sparta"]),
        "hypotheses": list(definition["hypotheses"]),
        "ground_truth": dict(definition["ground_truth"]),
        "policy_visible_evidence": policy_visible,
        "policy_evidence_omitted": omitted,
        "expected_modeled_effects": list(definition["expected_modeled_effects"]),
        "prohibited_actions": list(definition["prohibited_actions"]),
    }

    payload["instance_sha256"] = hashlib.sha256(_canonical_bytes(payload)).hexdigest()
    return payload
