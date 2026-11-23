#!/usr/bin/env python3
"""G3: synthetic-only oracle/selector parity, 18 pinned cases, no real data.

Reads ONLY a small allowlist of tracked source/specification files. No network,
no ESA/OPS-SAT/Hack-A-Sat path arguments, no telemetry, no publication action.
Run from a fresh checkout of the authorized draft PR; leaves frozen files alone.
"""
from __future__ import annotations

import argparse
import copy
from datetime import datetime, timezone
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path
import re
import sys
import platform

from g3_independent_oracle import (
    FIELDS, POLICIES, IncompleteObservation, oracle_action,
)

# These pins are immutable normative INPUTS, not outputs of this G3 run.
PINNED = {
    "study2/src/study2_security/selectors.py": "6ac7d0767a719c6305a5a47555cc9d0cfc74fa23",
    "study10/G1_SEMANTIC_CONTROL_SPEC_DRAFT_20261121.md": "29c97ef13c8bc92b51f09a1b3ad033dba9371081",
    "study10/G2_FREEZE_MANIFEST_CANDIDATE_20261121.json": "a20ca25c439d97150c56eeec197cc891c83aa1ad",
    "study10/G2_PROTOCOL_FREEZE_RECEIPT_20261122.json": "38e5da5edc193b358012bc9c2c3180917d7419ac",
    "study10/G3_STATIC_SYNTHETIC_ORACLE_READINESS_INVENTORY_20261123.json": "001dfbc88d642ba507dd7cd1868c99fe49cb3fed",
}
FROZEN_SELECTOR_SHA256 = "3bd5b607095807acf93a929d6d67c5cc1d2f592e5b0650c14032a7724e5f5505"
G3_CASES = (
    "P0_BASE", "S10_SYN_T_LOWER", "S10_SYN_T_UPPER",
    "S10_SYN_N_FUTURE_ISSUE", "S10_SYN_N_EXPIRED",
    "S10_SYN_N_EPOCH_MISMATCH", "S10_SYN_N_EPOCH_UNKNOWN",
    "S10_SYN_N_CRITERIA", "S10_SYN_N_CRITERIA_VALUE",
    "S10_SYN_N_LEDGER_INCOMPLETE", "S10_SYN_N_CONTRADICTION",
    "S10_SYN_N_CRC", "S10_SYN_N_APID", "S10_SYN_N_TIME",
    "S10_SYN_N_LABEL", "S10_SYN_N_COMMAND", "S10_SYN_N_MISSING",
    "S10_SYN_N_MIXING",
)
REQUIRED_KEYS = (
    "approved_version", "integrity_measurement_valid", "authorization_valid",
    "measured_state_current", "authorized_command_path_restored",
    "ground_spacecraft_state_agreed", "required_telemetry_restored",
    "health_checks_passed", "no_residual_unauthorized_state",
    "recovery_manifest_complete",
)


class G3Failure(Exception):
    pass


def _git_blob_sha1(data: bytes) -> str:
    prefix = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(prefix + data).hexdigest()  # Git object ID, NOT password use


def _safe_repo_file(repo: Path, rel: str) -> Path:
    if rel not in PINNED:
        raise G3Failure("UNAPPROVED_FILE_READ_ATTEMPT")
    p = repo / rel
    if p.is_symlink() or not p.is_file():
        raise G3Failure("MISSING_OR_SYMLINKED_FROZEN_INPUT")
    if p.resolve().is_relative_to(repo.resolve()) is not True:
        raise G3Failure("FROZEN_FILE_PATH_ESCAPE")
    return p


def read_pinned(repo: Path) -> dict[str, bytes]:
    pinned: dict[str, bytes] = {}
    for name, sha in PINNED.items():
        data = _safe_repo_file(repo, name).read_bytes()
        if _git_blob_sha1(data) != sha:
            raise G3Failure("FROZEN_SOURCE_BLOB_MISMATCH:" + name)
        pinned[name] = data
    sel = pinned["study2/src/study2_security/selectors.py"]
    if hashlib.sha256(sel).hexdigest() != FROZEN_SELECTOR_SHA256:
        raise G3Failure("FROZEN_SELECTOR_SHA256_MISMATCH")
    return pinned


def load_contract(files: dict[str, bytes]) -> tuple[dict, dict, dict]:
    md = files["study10/G1_SEMANTIC_CONTROL_SPEC_DRAFT_20261121.md"].decode("utf-8")
    blocks = re.findall(r"```json\s*\n(\{[\s\S]*?\})\s*\n```", md)
    fixture_candidates = [json.loads(b) for b in blocks if '"S10_SYN_P0_V3_DRAFT"' in b]
    if len(fixture_candidates) != 1:
        raise G3Failure("G1_SYNTHETIC_FIXTURE_NOT_UNIQUE")
    fixture = fixture_candidates[0]
    manifest = json.loads(files["study10/G2_FREEZE_MANIFEST_CANDIDATE_20261121.json"])
    inv = json.loads(files["study10/G3_STATIC_SYNTHETIC_ORACLE_READINESS_INVENTORY_20261123.json"])
    receipt = json.loads(files["study10/G2_PROTOCOL_FREEZE_RECEIPT_20261122.json"])
    if receipt["scientific_controls"]["G4_source_semantic_adjudication"] != "BLOCKED_RIGHTS_AND_EXPLICIT_AUTHORIZATION":
        raise G3Failure("FROZEN_G4_EXECUTION_BOUNDARY_CHANGED")
    spec = manifest["synthetic_controls"]
    g3 = inv["frozen_synthetic_contract"]
    if (spec["fixture_id"] != fixture.get("id") or fixture.get("role") != "SYNTHETIC_ONLY"
        or spec["assumed_accepted_claim_count"] != 10 or fixture["cryptographic_check"].get("real_signature_verified") is not False
        or spec["no_real_signature_verification"] is not True):
        raise G3Failure("SYNTHETIC_ONLY_FIXTURE_CONTRACT_MISMATCH")
    if (tuple(spec["mutation_case_ids"]) != G3_CASES or tuple(x["id"] for x in g3["synthetic_control_cases"]) != G3_CASES
        or spec["mutation_case_count"] != 18 or any(x["executed"] for x in g3["synthetic_control_cases"])):
        raise G3Failure("FROZEN_EIGHTEEN_CASE_SET_MISMATCH")
    if (tuple(spec["required_value_keys"]) != REQUIRED_KEYS or tuple(g3["exact_criteria"]) != REQUIRED_KEYS
        or tuple(g3["normalized_bool_order"]) != FIELDS or tuple(g3["four_frozen_primary_policies"]) != POLICIES):
        raise G3Failure("SYNTHETIC_SCHEMA_OR_POLICY_PIN_MISMATCH")
    if (fixture.get("expected_normalized_mapping") != spec["expected_normalized_inputs"]
        or tuple(fixture["expected_normalized_mapping"]) != FIELDS
        or list(fixture["expected_normalized_mapping"].values()) != g3["P0_normalized_boolean_values"]):
        raise G3Failure("P0_NORMALIZED_MAPPING_DRIFT")
    # Compare exact prospective ledger IDs with the G1 section, not a new case list.
    section = md.split("## 11. Prospective negative-control mutation ledger", 1)
    if len(section) != 2:
        raise G3Failure("G1_MUTATION_LEDGER_MISSING")
    body = section[1].split("## 12.", 1)[0]
    ids = [m.group(1) for line in body.splitlines()
           if (m := re.match(r"^\|\s*`(P0_BASE|S10_SYN_[A-Z0-9_]+)`\s*\|", line))]
    if tuple(ids) != G3_CASES:
        raise G3Failure("G1_VS_FROZEN_18_CASE_LEDGER_MISMATCH")
    return fixture, manifest, inv


def _known_state(value: object) -> bool | None:
    return {"known_true": True, "known_false": False, "unknown": None}.get(value)


def _closed_ledger(fixture: dict) -> tuple[bool | None, bool | None]:
    ledger = fixture["accepted_claims"]
    claims = ledger["claims"]
    if ledger["current_claims_count"] != len(claims):
        raise G3Failure("SYNTHETIC_LEDGER_COUNT_INCONSISTENT")
    if len({x["claim_id"] for x in claims}) != len(claims):
        raise G3Failure("DUPLICATE_SYNTHETIC_CLAIM_ID")
    required = fixture["synthetic_requirements_equality_contract"]["required_values"]
    if tuple(required) != REQUIRED_KEYS or set(fixture["accepted_recovery_criteria"]) != set(REQUIRED_KEYS):
        raise G3Failure("SYNTHETIC_REQUIRED_KEYS_MISMATCH")
    if ledger["inventory_complete"] is not True:
        return None, None
    accepted = [c for c in claims if c.get("accepted") is True and c.get("current") is True]
    for c in accepted:
        if c.get("subject") != fixture["decision_point"]["subject"] or c.get("epoch") != fixture["evidence_epoch"]["claimed"]:
            raise G3Failure("ACCEPTED_SYNTHETIC_CLAIM_OUTSIDE_SUBJECT_EPOCH")
        if c.get("acceptance_basis") != "SYNTHETIC_PREMISE_NOT_CRYPTOGRAPHICALLY_VERIFIED":
            raise G3Failure("SYNTHETIC_CLAIM_IMPERSONATES_CRYPTOGRAPHIC_VERIFICATION")
    # The accepted claims, not the declaration's cached contradictory field,
    # must determine contradictions under a complete known trusted-source set.
    trust = set(fixture.get("synthetic_trusted_source_ids", [fixture["trusted_source"]["source_id"]]))
    grouped: dict[tuple[str, str, int], set[str]] = {}
    values: dict[str, str] = {}
    for c in accepted:
        if c["source_id"] not in trust:
            continue
        grouped.setdefault((c["subject"], c["key"], c["epoch"]), set()).add(json.dumps(c["value"], sort_keys=True))
        values[c["key"]] = c["value"]
    contradictory = any(len(vals) > 1 for vals in grouped.values())
    # Completeness additionally requires matching accepted criterion metadata.
    all_expected = True
    for key, expected in required.items():
        entry = fixture["accepted_recovery_criteria"][key]
        claim_ids = {c["claim_id"] for c in accepted if c["key"] == key and c["value"] == expected}
        if not (entry.get("present") is True and entry.get("accepted") is True
                and entry.get("claim_id") in claim_ids and values.get(key) == expected):
            all_expected = False
    return all_expected, contradictory


def project_synthetic(fixture: dict) -> dict[str, bool | None]:
    """Synthetic evidence-to-state interface, never a real verifier result."""
    if fixture.get("role") != "SYNTHETIC_ONLY" or fixture["cryptographic_check"].get("real_signature_verified") is not False:
        raise G3Failure("NON_SYNTHETIC_OR_REAL_VERIFIER_CLAIM")
    minimum_complete, contradictory = _closed_ledger(fixture)
    t = fixture["freshness"]
    times = (t.get("issue_time"), t.get("now_s"), t.get("valid_for_s"))
    freshness = None if any(x is None for x in times) else times[0] <= times[1] <= times[0] + times[2]
    claimed, expected = fixture["evidence_epoch"].get("claimed"), fixture["evidence_epoch"].get("expected")
    epoch_valid = None if claimed is None or expected is None else claimed == expected
    result = {
        "signature_valid": _known_state(fixture["cryptographic_check"].get("state")),
        "source_trusted": _known_state(fixture["trusted_source"].get("membership")),
        "fresh": freshness,
        "epoch_valid": epoch_valid,
        "contradictory": contradictory,
        "minimum_evidence_complete": minimum_complete,
        "security_signal": _known_state(fixture["operational_guard"].get("state")),
        "authorization_available": _known_state(fixture["authorization_path"].get("state")),
    }
    if tuple(result) != FIELDS:
        raise G3Failure("RECOVERY_STATE_INTERFACE_ORDER_DRIFT")
    return result


def mutate(fixture: dict, case: str) -> dict | None:
    f = copy.deepcopy(fixture)
    ledger = f["accepted_claims"]
    if case == "P0_BASE":
        return f
    if case in {"S10_SYN_T_LOWER", "S10_SYN_T_UPPER", "S10_SYN_N_FUTURE_ISSUE", "S10_SYN_N_EXPIRED"}:
        t = {"S10_SYN_T_LOWER": 1000, "S10_SYN_T_UPPER": 1100, "S10_SYN_N_FUTURE_ISSUE": 999, "S10_SYN_N_EXPIRED": 1101}[case]
        f["freshness"]["now_s"] = t
        return f  # time-only probe; accepted ledger remains at as_of 1050
    if case == "S10_SYN_N_EPOCH_MISMATCH":
        f["evidence_epoch"]["expected"] = 8
    elif case == "S10_SYN_N_EPOCH_UNKNOWN":
        f["evidence_epoch"]["expected"] = None
    elif case in {"S10_SYN_N_CRITERIA", "S10_SYN_N_LEDGER_INCOMPLETE"}:
        ledger["claims"] = [c for c in ledger["claims"] if c["claim_id"] != "S10_SYN_CLAIM_10"]
        ledger["current_claims_count"] = 9
        f["accepted_recovery_criteria"]["recovery_manifest_complete"]["present"] = False if case == "S10_SYN_N_CRITERIA" else None
        f["accepted_recovery_criteria"]["recovery_manifest_complete"]["accepted"] = False if case == "S10_SYN_N_CRITERIA" else None
        if case == "S10_SYN_N_LEDGER_INCOMPLETE":
            ledger["inventory_complete"] = False
    elif case == "S10_SYN_N_CRITERIA_VALUE":
        for c in ledger["claims"]:
            if c["claim_id"] == "S10_SYN_CLAIM_10":
                c["value"] = "UNEXPECTED_TEST_VALUE"
    elif case == "S10_SYN_N_CONTRADICTION":
        f["synthetic_trusted_source_ids"] = ["SYN_SOURCE_A", "SYN_SOURCE_B"]
        c = copy.deepcopy(ledger["claims"][0]);c["source_id"] = "SYN_SOURCE_B";c["claim_id"] = "S10_SYN_CLAIM_11";c["value"] = "DIFFERENT_SYNTHETIC_VERSION";c["sequence"] = 1
        ledger["claims"].append(c);ledger["current_claims_count"] = 11
        ledger["no_other_accepted_current_claims_for_subject_key_epoch"] = False
        ledger["no_other_accepted_current_claims_in_relevant_scope"] = False
    elif case == "S10_SYN_N_CRC":
        f["cryptographic_check"]["state"] = "unknown";f["cryptographic_check"]["crc_valid"] = True
    elif case == "S10_SYN_N_APID":
        f["trusted_source"]["membership"] = "unknown";f["trusted_source"]["APID"] = 42
    elif case == "S10_SYN_N_TIME":
        f["freshness"]["valid_for_s"] = None;f["freshness"]["now_s"] = None
    elif case == "S10_SYN_N_LABEL":
        f["operational_guard"]["state"] = "unknown";f["operational_guard"]["offline_ground_truth_substitute"] = True
    elif case == "S10_SYN_N_COMMAND":
        f["authorization_path"]["state"] = "unknown";f["authorization_path"]["command_status"] = "COMPLETED"
    elif case == "S10_SYN_N_MISSING":
        f["cryptographic_check"]["state"] = "unknown";f["trusted_source"]["membership"] = "unknown"
        f["freshness"]["now_s"] = None;f["evidence_epoch"]["expected"] = None
        f["operational_guard"]["state"] = "unknown";f["authorization_path"]["state"] = "unknown"
        ledger["inventory_complete"] = False;ledger["claims"] = [];ledger["current_claims_count"] = 0
    elif case == "S10_SYN_N_MIXING":
        return None  # Cohort provenance guard; reject before any policy call.
    else:
        raise G3Failure("UNKNOWN_OR_UNFROZEN_SYNTHETIC_CASE")
    return f


EXPECTED_CASES: dict[str, tuple[str, bool | None]] = {
    "P0_BASE": ("ALL_KNOWN", True),
    "S10_SYN_T_LOWER": ("fresh", True),
    "S10_SYN_T_UPPER": ("fresh", True),
    "S10_SYN_N_FUTURE_ISSUE": ("fresh", False),
    "S10_SYN_N_EXPIRED": ("fresh", False),
    "S10_SYN_N_EPOCH_MISMATCH": ("epoch_valid", False),
    "S10_SYN_N_EPOCH_UNKNOWN": ("epoch_valid", None),
    "S10_SYN_N_CRITERIA": ("minimum_evidence_complete", False),
    "S10_SYN_N_CRITERIA_VALUE": ("minimum_evidence_complete", False),
    "S10_SYN_N_LEDGER_INCOMPLETE": ("minimum_evidence_complete", None),
    "S10_SYN_N_CONTRADICTION": ("contradictory", True),
    "S10_SYN_N_CRC": ("signature_valid", None),
    "S10_SYN_N_APID": ("source_trusted", None),
    "S10_SYN_N_TIME": ("fresh", None),
    "S10_SYN_N_LABEL": ("security_signal", None),
    "S10_SYN_N_COMMAND": ("authorization_available", None),
    "S10_SYN_N_MISSING": ("ALL_UNKNOWN", True),
    "S10_SYN_N_MIXING": ("REJECT_COHORT_POOLING", None),
}
TIME_ONLY_CASES = frozenset(("S10_SYN_T_LOWER", "S10_SYN_T_UPPER", "S10_SYN_N_FUTURE_ISSUE", "S10_SYN_N_EXPIRED"))


def load_frozen_selector(repo: Path):
    path = _safe_repo_file(repo, "study2/src/study2_security/selectors.py")
    name = "_study10_g3_frozen_selector_exact_pin"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise G3Failure("FROZEN_SELECTOR_IMPORT_FAILED")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _production_action(sel, policy: str, observed: dict[str, bool]) -> str:
    # Validate before calling dataclass, which is not itself tri-state protected.
    if set(observed) != set(FIELDS) or any(type(observed[x]) is not bool for x in FIELDS):
        raise IncompleteObservation("UNKNOWN_STATE_NOT_A_PRODUCTION_SELECTOR_INPUT")
    p = sel.Study2Policy(policy)
    dataclass_obs = sel.ObservationSummary(**observed)
    return sel.select_action(p, dataclass_obs).value


def case_suite(fixture: dict, sel) -> tuple[list[dict], int, list[dict]]:
    results: list[dict] = []
    complete_calls = 0
    differences: list[dict] = []
    for case in G3_CASES:
        mutated = mutate(fixture, case)
        focus, expected = EXPECTED_CASES[case]
        if case == "S10_SYN_N_MIXING":
            results.append({"id": case, "status": "PASS_REJECTED_COHORT_MIXING", "selector_calls": 0})
            continue
        assert mutated is not None
        obs = project_synthetic(mutated)
        value = (all(type(x) is bool for x in obs.values()) if focus == "ALL_KNOWN"
                 else all(x is None for x in obs.values()) if focus == "ALL_UNKNOWN"
                 else obs[focus])
        ok = type(value) is type(expected) and value == expected
        if not ok:
            differences.append({"id": case, "failure": "FROZEN_SYNTHETIC_EXPECTATION_MISMATCH", "focus": focus})
        # Isolated time cases explicitly do not imply a full decision snapshot.
        only_time = case in TIME_ONLY_CASES
        complete = all(type(x) is bool for x in obs.values()) and not only_time
        action_count = 0
        if complete and ok:
            for p in POLICIES:
                independent = oracle_action(p, obs)
                real = _production_action(sel, p, obs)
                complete_calls += 1;action_count += 1
                if real != independent:
                    differences.append({"id": case, "policy": p, "failure": "ORACLE_SELECTOR_MISMATCH"})
        else:
            # Explicitly ensure the oracle rejects a non-Boolean projected state.
            if not only_time and any(x is None for x in obs.values()):
                for p in POLICIES:
                    try:
                        oracle_action(p, obs)
                    except IncompleteObservation:
                        pass
                    else:
                        differences.append({"id": case, "policy": p, "failure": "UNKNOWN_COERCED_BY_ORACLE"})
        results.append({"id": case, "status": "PASS" if ok else "FAIL_EXPECTATION", "focus": focus,
                        "observed": "KNOWN_TRUE" if value is True else "KNOWN_FALSE" if value is False else "UNKNOWN" if value is None else "PRESENT",
                        "selector_calls": action_count, "time_only": only_time})
    if len(results) != 18 or set(r["id"] for r in results) != set(G3_CASES):
        raise G3Failure("EIGHTEEN_CASE_RESULT_INCOMPLETE")
    return results, complete_calls, differences


def static_six_examples(inv: dict, sel) -> tuple[int, list[dict]]:
    base = {k: v for k, v in zip(FIELDS, inv["frozen_synthetic_contract"]["P0_normalized_boolean_values"])}
    results = []
    for case in inv["frozen_synthetic_contract"]["static_selector_examples"]:
        s = dict(base)
        if case["id"] == "STATIC_FRESH_FALSE":
            s["fresh"] = False
        elif case["id"] == "STATIC_CONTRADICTORY_TRUE":
            s["contradictory"] = True
        else:
            s["security_signal"] = case["security_signal"]
            s["authorization_available"] = case["authorization_available"]
        if (s["signature_valid"] and s["source_trusted"] and s["fresh"] and s["epoch_valid"]
            and not s["contradictory"] and s["minimum_evidence_complete"]) != case["evidence_qualified"]:
            results.append({"id": case["id"], "failure": "FROZEN_STATIC_EVIDENCE_EXPECTATION_MISMATCH"})
        for p in POLICIES:
            actual = _production_action(sel, p, s)
            independent = oracle_action(p, s)
            if actual != case["expected_actions"][p] or independent != actual:
                results.append({"id": case["id"], "policy": p, "failure": "FROZEN_STATIC_ORACLE_EXPECTATION_MISMATCH"})
    return 6 * 4, results


def exhaustive_parity(sel) -> tuple[int, list[dict], str, dict[str, int]]:
    errors: list[dict] = []
    rows: list[str] = []
    counts: dict[str, int] = {p: 0 for p in POLICIES}
    for bits in itertools.product((False, True), repeat=8):
        obs = dict(zip(FIELDS, bits))
        pattern = "".join("1" if bit else "0" for bit in bits)
        for p in POLICIES:
            action = _production_action(sel, p, obs)
            independent = oracle_action(p, obs)
            counts[p] += 1
            rows.append(f"{pattern}|{p}|{action}|{independent}")
            if action != independent:
                errors.append({"input_bits": pattern, "policy": p,
                               "failure": "INDEPENDENT_ORACLE_PARITY_MISMATCH",
                               "production": action, "oracle": independent})
    return sum(counts.values()), errors, hashlib.sha256(("\n".join(rows) + "\n").encode()).hexdigest(), counts


def run(repo: Path) -> tuple[dict, int]:
    source = read_pinned(repo)
    fixture, _, inv = load_contract(source)
    sel = load_frozen_selector(repo)
    p0 = project_synthetic(fixture)
    if p0 != fixture["expected_normalized_mapping"]:
        raise G3Failure("SYNTHETIC_P0_MAPPING_PARITY_MISMATCH")
    cases, case_calls, case_diffs = case_suite(fixture, sel)
    static_calls, static_diffs = static_six_examples(inv, sel)
    count, exhaustive_diffs, digest, per_policy = exhaustive_parity(sel)
    failures = case_diffs + static_diffs + exhaustive_diffs
    done = (len(cases) == 18 and all(x["status"].startswith("PASS") for x in cases)
            and count == 1024 and per_policy == dict.fromkeys(POLICIES, 256)
            and static_calls == 24 and not failures)
    report = {
        "schema_version": 1, "study_id": "S10-RSEI-001", "stage": "G3_SYNTHETIC_ONLY",
        "run_utc": datetime.now(timezone.utc).isoformat(),
        "status": "G3_SYNTHETIC_PARITY_PASS_NOT_G4_AUTHORIZED" if done else "G3_SYNTHETIC_PARITY_FAIL_CLOSED",
        "frozen_selector_sha256_verified": FROZEN_SELECTOR_SHA256,
        "pinned_g1_fixture_blob_verified": PINNED["study10/G1_SEMANTIC_CONTROL_SPEC_DRAFT_20261121.md"],
        "pinned_g2_receipt_blob_verified": PINNED["study10/G2_PROTOCOL_FREEZE_RECEIPT_20261122.json"],
        "frozen_18_case_ids": list(G3_CASES),
        "synthetic_cases_passed": sum(x["status"].startswith("PASS") for x in cases),
        "synthetic_cases_total": 18, "synthetic_case_results": cases,
        "static_selector_examples_verified": 6 if not static_diffs else 0,
        "static_policy_comparisons": static_calls,
        "synthetic_case_full_boolean_selector_comparisons": case_calls,
        "exhaustive_complete_boolean_states": 256,
        "primary_policies": list(POLICIES), "per_policy_parity_comparisons": per_policy,
        "exhaustive_parity_comparisons": count,
        "exhaustive_parity_sha256": digest,
        "parity_mismatch_count": len(failures), "parity_mismatches": failures[:25],
        "environment": {"python": platform.python_version(), "implementation": platform.python_implementation()},
        "oracle_implementation_imports_frozen_selector": False,
        "synthetic_signature_outcome_is_interface_stub": True,
        "real_Ed25519_signature_verified": False,
        "real_source_files_accessed": False,
        "original_telemetry_processed": False,
        "G4_06_authorized": False, "PR_merge_authorized": False,
        "journal_publication_authorized": False,
        "G4_05_later_execution_boundary_recheck_required": True,
        "G3_internal_tests_are_not_independent_human_peer_review": True,
    }
    return report, 0 if done else 2


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    try:
        result, code = run(args.repo)
    except (G3Failure, ValueError, KeyError, TypeError, OSError, SyntaxError, IncompleteObservation) as exc:
        result = {"schema_version": 1, "study_id": "S10-RSEI-001", "stage": "G3_SYNTHETIC_ONLY",
                  "status": "G3_SYNTHETIC_PREFLIGHT_FAIL_CLOSED", "failure_code": str(exc) if isinstance(exc, G3Failure) else type(exc).__name__,
                  "G4_06_authorized": False, "PR_merge_authorized": False, "original_telemetry_processed": False}
        code = 2
    rendered = json.dumps(result, sort_keys=True, indent=2) + "\n"
    if args.report is not None:
        if args.report.is_symlink() or args.report.exists():
            print("REPORT_EXISTS_OR_SYMLINK_REFUSED", file=sys.stderr)
            return 2
        # Fail-closed; never overwrite an earlier evidence report.
        try:
            import os
            fd = os.open(args.report, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                f.write(rendered)
        except OSError:
            print("REPORT_WRITE_FAILED", file=sys.stderr)
            return 2
    print(json.dumps({"status": result["status"], "cases_passed": result.get("synthetic_cases_passed", 0),
                      "cases_total": result.get("synthetic_cases_total", 18),
                      "exhaustive_comparisons": result.get("exhaustive_parity_comparisons", 0),
                      "mismatches": result.get("parity_mismatch_count", "NOT_RUN"),
                      "G4_06_authorized": False, "PR_merge_authorized": False}, sort_keys=True))
    return code


if __name__ == "__main__":
    raise SystemExit(main())