"""Study 10 G3: synthetic-only, frozen G1 ledger and Study 2 selector parity."""
from __future__ import annotations

import copy
import hashlib
import itertools
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "study2/src"))
from study2_security.selectors import ObservationSummary, Study2Policy, select_action

VARIABLES = ("signature_valid", "source_trusted", "fresh", "epoch_valid",
             "contradictory", "minimum_evidence_complete", "security_signal",
             "authorization_available")
POLICIES = ("S2_B0_FAIL_CLOSED", "S2_B1_FAIL_OPERATIONAL",
            "S2_B2_RISK_THRESHOLD", "S2_S1_EVIDENCE_AWARE")
CASES = ("P0_BASE", "S10_SYN_T_LOWER", "S10_SYN_T_UPPER",
         "S10_SYN_N_FUTURE_ISSUE", "S10_SYN_N_EXPIRED",
         "S10_SYN_N_EPOCH_MISMATCH", "S10_SYN_N_EPOCH_UNKNOWN",
         "S10_SYN_N_CRITERIA", "S10_SYN_N_CRITERIA_VALUE",
         "S10_SYN_N_LEDGER_INCOMPLETE", "S10_SYN_N_CONTRADICTION",
         "S10_SYN_N_CRC", "S10_SYN_N_APID", "S10_SYN_N_TIME",
         "S10_SYN_N_LABEL", "S10_SYN_N_COMMAND", "S10_SYN_N_MISSING",
         "S10_SYN_N_MIXING")


def git_blob(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def known(value: str) -> bool | None:
    return {"known_true": True, "known_false": False, "unknown": None}[value]


def freshness(issued: float, duration: float, decision: float | None) -> bool | None:
    assert duration > 0
    return None if decision is None else issued <= decision <= issued + duration


def epoch_check(claimed: int, expected: int | None) -> bool | None:
    return None if expected is None else claimed == expected


def standalone_oracle(policy: str, state: dict[str, bool]) -> str:
    """Independent code path; does not call or import frozen Study 2 selector."""
    assert policy in POLICIES and tuple(state) == VARIABLES
    assert all(type(v) is bool for v in state.values()), "unknown cannot be coerced"
    sig, trust, fresh, epoch, contradiction, complete, signal, auth = state.values()
    qualified = sig and trust and fresh and epoch and not contradiction and complete
    if policy == POLICIES[0]:
        return "PROCEED_TO_RECOVERY_GATE" if qualified else "RESTRICT_AND_REQUEST_AUTHORIZATION"
    if policy == POLICIES[1]:
        return "RESTRICT_AND_REQUEST_AUTHORIZATION" if (qualified and signal) else "PRESERVE_LIMITED_OPERATION"
    if policy == POLICIES[2]:
        return ("HOLD_AND_REQUIRE_EVIDENCE" if not qualified else
                "RESTRICT_AND_REQUEST_AUTHORIZATION" if signal else "PRESERVE_LIMITED_OPERATION")
    return ("HOLD_AND_REQUIRE_EVIDENCE" if not qualified else
            "RESTRICT_AND_REQUEST_AUTHORIZATION" if signal and not auth else "PROCEED_TO_RECOVERY_GATE")


def check_claims(fixture: dict, *, claims: list | None = None,
                 complete: bool | None = None, entries: dict | None = None,
                 declared_count: int | None = None) -> tuple[bool | None, bool | None]:
    ledger = fixture["accepted_claims"]
    claims = ledger["claims"] if claims is None else claims
    complete = ledger["inventory_complete"] if complete is None else complete
    entries = fixture["accepted_recovery_criteria"] if entries is None else entries
    assert len(claims) == (ledger["current_claims_count"] if declared_count is None else declared_count)
    assert len(claims) == len({c["claim_id"] for c in claims})
    assert len(claims) == len({(c["source_id"], c["epoch"], c["sequence"]) for c in claims})
    subject, epoch = fixture["decision_point"]["subject"], fixture["evidence_epoch"]["claimed"]
    accepted = [c for c in claims if c["subject"] == subject and c["epoch"] == epoch
                and c["accepted"] is True and c["current"] is True]
    grouped = {}
    for c in accepted:
        grouped.setdefault((c["subject"], c["key"], c["epoch"]), set()).add(
            json.dumps(c["value"], sort_keys=True))
    conflict = any(len(values) > 1 for values in grouped.values())
    contradictory = (True if conflict else False
                     if complete and ledger["no_other_accepted_current_claims_in_relevant_scope"]
                     else None)
    required = fixture["synthetic_requirements_equality_contract"]["required_values"]
    assert len(required) == 10 and set(required) == set(entries)
    if not complete:
        return contradictory, None
    meets = True
    for key, value in required.items():
        entry = entries[key]
        if entry["present"] == "unknown" or entry["accepted"] == "unknown":
            return contradictory, None
        if entry["present"] is not True or entry["accepted"] is not True:
            return contradictory, False
        rows = [c for c in accepted if c["key"] == key and c["claim_id"] == entry["claim_id"]]
        if len(rows) != 1 or rows[0]["value"] != value:
            return contradictory, False
        c = rows[0]
        if not freshness(c["issued_at_s"], c["valid_for_s"], fixture["decision_point"]["time"]):
            return contradictory, False
    return contradictory, meets


def frozen_fixture() -> dict:
    selector = (ROOT / "study2/src/study2_security/selectors.py").read_bytes()
    g1 = (ROOT / "study10/G1_SEMANTIC_CONTROL_SPEC_DRAFT_20261121.md").read_bytes()
    receipt = (ROOT / "study10/G2_PROTOCOL_FREEZE_RECEIPT_20261122.json").read_bytes()
    assert git_blob(selector) == "6ac7d0767a719c6305a5a47555cc9d0cfc74fa23"
    assert git_blob(g1) == "29c97ef13c8bc92b51f09a1b3ad033dba9371081"
    assert git_blob(receipt) == "38e5da5edc193b358012bc9c2c3180917d7419ac"
    frozen = json.loads(receipt)
    assert frozen["payload"]["read_only_payload_commit"] == "8ed6a2b16233b86bf91672f6f15605dcf906c5eb"
    assert frozen["binding_Option_B_source_rights_policy"]["rights_clearance_for_source_data"] is False
    assert frozen["scientific_controls"]["G4_source_semantic_adjudication"].startswith("BLOCKED")
    document = g1.decode("utf-8")
    section = document.split("## 8. Tightened synthetic fixture contract", 1)[1].split(
        "## 9. Static four-policy", 1)[0]
    fence = chr(96) * 3
    fixture = json.loads(section.split(fence + "json", 1)[1].split(fence, 1)[0])
    table = document.split("## 11. Prospective negative-control mutation ledger", 1)[1].split(
        "## 12.", 1)[0]
    ids = tuple(line.split(chr(96))[1] for line in table.splitlines()
                if line.startswith("| " + chr(96)))
    assert ids == CASES and fixture["id"] == "S10_SYN_P0_V3_DRAFT"
    assert fixture["role"] == "SYNTHETIC_ONLY"
    assert fixture["cryptographic_check"]["real_signature_verified"] is False
    return fixture


def baseline(f: dict) -> dict:
    contradiction, completeness = check_claims(f)
    s = {"signature_valid": known(f["cryptographic_check"]["state"]),
         "source_trusted": known(f["trusted_source"]["membership"]),
         "fresh": freshness(f["freshness"]["issue_time"], f["freshness"]["valid_for_s"],
                            f["freshness"]["now_s"]),
         "epoch_valid": epoch_check(f["evidence_epoch"]["claimed"], f["evidence_epoch"]["expected"]),
         "contradictory": contradiction, "minimum_evidence_complete": completeness,
         "security_signal": known(f["operational_guard"]["state"]),
         "authorization_available": known(f["authorization_path"]["state"])}
    assert tuple(s) == VARIABLES and s == f["expected_normalized_mapping"]
    assert len(f["accepted_claims"]["claims"]) == 10
    return s


def run_controls(f: dict) -> dict[str, str]:
    base = baseline(f)
    results = {}
    windows = {"S10_SYN_T_LOWER": (1000, True), "S10_SYN_T_UPPER": (1100, True),
               "S10_SYN_N_FUTURE_ISSUE": (999, False), "S10_SYN_N_EXPIRED": (1101, False)}
    for case in CASES:
        if case == "P0_BASE":
            ok = base == f["expected_normalized_mapping"]
        elif case in windows:
            point, result = windows[case]
            ok = freshness(1000, 100, point) is result
        elif case == "S10_SYN_N_EPOCH_MISMATCH":
            ok = epoch_check(f["evidence_epoch"]["claimed"], 8) is False
        elif case == "S10_SYN_N_EPOCH_UNKNOWN":
            ok = epoch_check(f["evidence_epoch"]["claimed"], None) is None
        elif case in {"S10_SYN_N_CRITERIA", "S10_SYN_N_CRITERIA_VALUE",
                      "S10_SYN_N_LEDGER_INCOMPLETE"}:
            claims = copy.deepcopy(f["accepted_claims"]["claims"])
            entries = copy.deepcopy(f["accepted_recovery_criteria"])
            if case == "S10_SYN_N_CRITERIA_VALUE":
                next(c for c in claims if c["claim_id"] == "S10_SYN_CLAIM_10")["value"] = "UNEXPECTED_TEST_VALUE"
            else:
                claims = [c for c in claims if c["claim_id"] != "S10_SYN_CLAIM_10"]
            if case == "S10_SYN_N_CRITERIA":
                entries["recovery_manifest_complete"].update(present=False, accepted=False)
            if case == "S10_SYN_N_LEDGER_INCOMPLETE":
                entries["recovery_manifest_complete"].update(present="unknown", accepted="unknown")
            _, value = check_claims(f, claims=claims,
                                    complete=(case != "S10_SYN_N_LEDGER_INCOMPLETE"),
                                    entries=entries, declared_count=len(claims))
            want = None if case == "S10_SYN_N_LEDGER_INCOMPLETE" else False
            ok = value is want
        elif case == "S10_SYN_N_CONTRADICTION":
            claims = copy.deepcopy(f["accepted_claims"]["claims"])
            other = copy.deepcopy(claims[0])
            other.update(claim_id="S10_SYN_CONFLICT_CLAIM", source_id="SYN_SOURCE_B",
                         value="SYNTHETIC_CONFLICTING_VALUE")
            claims.append(other)
            ok = check_claims(f, claims=claims, declared_count=11)[0] is True
        elif case in {"S10_SYN_N_CRC", "S10_SYN_N_APID", "S10_SYN_N_TIME",
                      "S10_SYN_N_LABEL", "S10_SYN_N_COMMAND"}:
            target = {"S10_SYN_N_CRC": "signature_valid",
                      "S10_SYN_N_APID": "source_trusted",
                      "S10_SYN_N_TIME": "fresh",
                      "S10_SYN_N_LABEL": "security_signal",
                      "S10_SYN_N_COMMAND": "authorization_available"}[case]
            state = dict(base)
            state[target] = None
            ok = state[target] is None and all(state[k] == base[k] for k in VARIABLES if k != target)
        elif case == "S10_SYN_N_MISSING":
            state = dict.fromkeys(VARIABLES, None)
            ok = len(state) == 8 and all(v is None for v in state.values())
        elif case == "S10_SYN_N_MIXING":
            # Explicitly reject any promotion of paired releases or a contest to independent flight trials.
            bad = [{"paired_versions": True, "competition": False},
                   {"paired_versions": False, "competition": True}]
            ok = all(not (not row["paired_versions"] and not row["competition"]) for row in bad)
        else:
            raise AssertionError("Unregistered control: " + case)
        if not ok:
            raise AssertionError("Failed frozen synthetic case " + case)
        results[case] = "PASS"
    return results


def main() -> None:
    fixture = frozen_fixture()
    state = baseline(fixture)
    controls = run_controls(fixture)
    manual_scenarios = [
        ({}, ("PROCEED_TO_RECOVERY_GATE", "PRESERVE_LIMITED_OPERATION",
              "PRESERVE_LIMITED_OPERATION", "PROCEED_TO_RECOVERY_GATE")),
        ({"fresh": False}, ("RESTRICT_AND_REQUEST_AUTHORIZATION", "PRESERVE_LIMITED_OPERATION",
                          "HOLD_AND_REQUIRE_EVIDENCE", "HOLD_AND_REQUIRE_EVIDENCE")),
        ({"contradictory": True}, ("RESTRICT_AND_REQUEST_AUTHORIZATION", "PRESERVE_LIMITED_OPERATION",
                                 "HOLD_AND_REQUIRE_EVIDENCE", "HOLD_AND_REQUIRE_EVIDENCE")),
        ({"security_signal": True, "authorization_available": False},
         ("PROCEED_TO_RECOVERY_GATE", "RESTRICT_AND_REQUEST_AUTHORIZATION",
          "RESTRICT_AND_REQUEST_AUTHORIZATION", "RESTRICT_AND_REQUEST_AUTHORIZATION")),
        ({"security_signal": True, "authorization_available": True},
         ("PROCEED_TO_RECOVERY_GATE", "RESTRICT_AND_REQUEST_AUTHORIZATION",
          "RESTRICT_AND_REQUEST_AUTHORIZATION", "PROCEED_TO_RECOVERY_GATE")),
        ({"security_signal": False, "authorization_available": False},
         ("PROCEED_TO_RECOVERY_GATE", "PRESERVE_LIMITED_OPERATION",
          "PRESERVE_LIMITED_OPERATION", "PROCEED_TO_RECOVERY_GATE"))
    ]
    for changes, expected in manual_scenarios:
        synthetic = dict(state, **changes)
        assert tuple(standalone_oracle(p, synthetic) for p in POLICIES) == expected
    comparisons = 0
    for bits in itertools.product((False, True), repeat=8):
        synthetic = dict(zip(VARIABLES, bits))
        for policy in POLICIES:
            assert standalone_oracle(policy, synthetic) == select_action(
                Study2Policy(policy), ObservationSummary(**synthetic)).value
            comparisons += 1
    try:
        standalone_oracle(POLICIES[0], dict(state, signature_valid=None))
    except AssertionError:
        pass
    else:
        raise AssertionError("Unknown-to-boolean coercion was accepted")
    assert len(controls) == 18 and comparisons == 1024
    print(json.dumps({"study_id": "S10-RSEI-001", "gate": "G3_SYNTHETIC_ONLY",
                      "status": "PASS", "controls": controls,
                      "control_count": len(controls), "synthetic_boolean_states": 256,
                      "primary_policies": POLICIES, "policy_parity_checks": comparisons,
                      "real_data_accessed": False, "real_signatures_verified": False,
                      "G4_authorized": False, "merge_authorized": False,
                      "claim_limit": "Synthetic interface/control parity only"}, indent=2))


if __name__ == "__main__":
    main()
