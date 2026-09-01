from __future__ import annotations

import hashlib
import json
from typing import Any


A_PROFILES = (
    ("V0", "A0", "K0", "current"),
    ("V1", "A0", "K0", "omission"),
    ("V2", "A0", "K0", "staleness"),
    ("V3", "A0", "K0", "source_disagreement"),
    ("V4", "A1", "K0", "post_signature_manipulation"),
    ("V5", "A1", "K0", "single_source_partial_compromise"),
)
A_POLICIES = ("S2_B0_FAIL_CLOSED", "S2_B2_RISK_THRESHOLD", "S2_S1_EVIDENCE_AWARE")
B_POLICIES = ("S2_B0_FAIL_CLOSED", "S2_B1_FAIL_OPERATIONAL", "S2_B2_RISK_THRESHOLD", "S2_S1_EVIDENCE_AWARE")
C_POLICIES = ("S2_B0_FAIL_CLOSED", "S2_B1_FAIL_OPERATIONAL", "S2_S1_EVIDENCE_AWARE")
D_SELECTORS = ("S2_S1_EVIDENCE_AWARE", "PI_NO_MISSION", "PI_NO_EVIDENCE", "PI_NO_CONTACT", "PI_SECURITY_ONLY")
E_PROFILES = (
    ("A1", "K0", "single_source_partial_compromise"),
    ("A2", "K2", "single_source_partial_compromise_plus_contact_loss"),
    ("A3", "K0", "multi_source_partial_compromise"),
)


def materialize_cell_matrix() -> dict[str, Any]:
    cells: list[dict[str, Any]] = []
    i = 1
    for evidence, adversary, contact, mechanism in A_PROFILES:
        for policy in A_POLICIES:
            cells.append({
                "cell_id": f"A{i:02d}", "block": "A_PRIMARY_EVIDENCE_MECHANISM",
                "event": "E3", "mission": "M2", "contact": contact,
                "evidence": evidence, "adversary": adversary,
                "mechanism": mechanism, "policy": policy, "seed_set": "A96",
            })
            i += 1

    i = 1
    for contact in ("K0", "K1", "K2", "K3", "K4"):
        for policy in B_POLICIES:
            cells.append({
                "cell_id": f"B{i:02d}", "block": "B_CONTACT_AUTHORIZATION",
                "event": "E3", "mission": "M2", "contact": contact,
                "evidence": "V0", "adversary": "A0", "mechanism": "current",
                "policy": policy, "seed_set": "B32",
            })
            i += 1

    i = 1
    for family in ("telemetry_loss", "state_inconsistency", "contact_or_authorization_loss"):
        for cause in ("BENIGN", "ADVERSARIAL"):
            for policy in C_POLICIES:
                cells.append({
                    "cell_id": f"C{i:02d}", "block": "C_FAULT_ATTACK_AMBIGUITY",
                    "ambiguity_family": family, "cause": cause,
                    "policy": policy, "seed_set": "C32",
                })
                i += 1

    i = 1
    for context in ("unauthorized_command", "update_recovery", "replay", "evidence_loss"):
        for selector in D_SELECTORS:
            cells.append({
                "cell_id": f"D{i:02d}", "block": "D_CONTEXT_ABLATION",
                "context": context, "selector": selector, "seed_set": "D32",
            })
            i += 1

    i = 1
    for adversary, contact, mechanism in E_PROFILES:
        for policy in A_POLICIES:
            cells.append({
                "cell_id": f"E{i:02d}", "block": "E_ADVERSARY_BUDGET_STRESS",
                "event": "E3", "mission": "M2", "contact": contact,
                "evidence": "V5", "adversary": adversary,
                "mechanism": mechanism, "policy": policy, "seed_set": "E32",
            })
            i += 1

    return {
        "schema": 1,
        "experiment_id": "S2-AEATR-001",
        "status": "CELL_MATRIX_FROZEN_PRE_RUNTIME",
        "seed_sets": {
            "A96": {"count": 96, "start": 2100001, "end": 2100096},
            "B32": {"count": 32, "start": 2200001, "end": 2200032},
            "C32": {"count": 32, "start": 2300001, "end": 2300032},
            "D32": {"count": 32, "start": 2400001, "end": 2400032},
            "E32": {"count": 32, "start": 2500001, "end": 2500032},
        },
        "cells": cells,
    }


def canonical_bytes(matrix: dict[str, Any]) -> bytes:
    return (json.dumps(matrix, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def matrix_sha256(matrix: dict[str, Any] | None = None) -> str:
    return hashlib.sha256(canonical_bytes(matrix or materialize_cell_matrix())).hexdigest()


def target_valid_observations(matrix: dict[str, Any] | None = None) -> int:
    data = matrix or materialize_cell_matrix()
    return sum(data["seed_sets"][cell["seed_set"]]["count"] for cell in data["cells"])
