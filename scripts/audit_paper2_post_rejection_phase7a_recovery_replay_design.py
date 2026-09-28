#!/usr/bin/env python3
"""Fail-closed audit for Paper-2 S3X Phase-7A recovery-replay design."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
S3X = ROOT / "study3x"
REBUILD = ROOT / "publication/Paper_2_Studies_3_4_6/Post_Rejection_Rebuild"

PROTOCOL = S3X / "config/S3X_PHASE7_RECOVERY_REPLAY_PROTOCOL_001.json"
STATUS = REBUILD / "PAPER2_PHASE7A_RECOVERY_REPLAY_DESIGN_STATUS.json"
DESIGN = REBUILD / "PHASE7A_RECOVERY_REPLAY_DESIGN_R1_2026-09-27.md"
WORKFLOW = ROOT / ".github/workflows/validate-research-configs.yml"
PHASE6C = S3X / "config/S3X_PHASE6_TRACE_POPULATION_FREEZE_001.json"
STUDY3_MODEL = ROOT / "study3/src/temporal_model.py"
STUDY3_PROTOCOL = ROOT / "study3/STUDY3_PROTOCOL.json"
STUDY3_RESULTS_FREEZE = ROOT / "study3/results/RESULTS_FREEZE.json"

EXPECTED_BASE = "38b45cd5e4674c78b432f24bfff2457affb3cb12"
EXPECTED_PHASE6C_BLOB = "ed0bdcec443b7f0c3ee80d441e1122f32e499d3e"
EXPECTED_MODEL_BLOB = "b13e62456c144db0e12808bf700586c1c844c33d"
EXPECTED_STUDY3_PROTOCOL_BLOB = "ba798c3fddc5400cb45103c5fb2694b6ecfd475c"
EXPECTED_STUDY3_RESULTS_BLOB = "afb81cad030c3c6e638c9b9807a9c214f293daa5"
EXPECTED_INTERVAL_SHA = "cfa4fa3d88cb525237cbfe347fabe8485021351f3b639bdb58f79c575d8a51bc"
EXPECTED_PROJECTION = "f15338f1790f60d83d2c849542f6d6e3b21a8c49f7d413cdc5098e35952294d1"
EXPECTED_CASES = 34542


def fail(message: str) -> None:
    print(f"[FAIL] {message}", file=sys.stderr)
    raise SystemExit(1)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def git_blob(path: Path) -> str:
    return subprocess.check_output(
        ["git", "hash-object", str(path.relative_to(ROOT))],
        cwd=ROOT,
        text=True,
    ).strip()


def load_study3_model():
    spec = importlib.util.spec_from_file_location("study3_phase7_parent_model", STUDY3_MODEL)
    require(spec is not None and spec.loader is not None, "cannot load Study-3 temporal model")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    for path in (
        PROTOCOL, STATUS, DESIGN, WORKFLOW, PHASE6C,
        STUDY3_MODEL, STUDY3_PROTOCOL, STUDY3_RESULTS_FREEZE,
    ):
        require(path.is_file(), f"missing Phase-7A dependency: {path.relative_to(ROOT)}")

    require(git_blob(PHASE6C) == EXPECTED_PHASE6C_BLOB, "Phase-6C freeze blob drift")
    require(git_blob(STUDY3_MODEL) == EXPECTED_MODEL_BLOB, "Study-3 temporal-model blob drift")
    require(git_blob(STUDY3_PROTOCOL) == EXPECTED_STUDY3_PROTOCOL_BLOB, "Study-3 protocol blob drift")
    require(git_blob(STUDY3_RESULTS_FREEZE) == EXPECTED_STUDY3_RESULTS_BLOB, "Study-3 results-freeze blob drift")

    p = read_json(PROTOCOL)
    require(p.get("schema") == 1, "protocol schema drift")
    require(p.get("protocol_id") == "S3X-PHASE7-RECOVERY-REPLAY-DESIGN-001", "protocol id drift")
    require(p.get("experiment_id") == "S3X-ETA-001", "experiment id drift")
    require(p.get("status") == "DESIGN_ONLY__NO_RECOVERY_OR_SCIENTIFIC_EXECUTION_AUTHORIZED", "design-only status drift")
    require(p.get("branch_base_main_commit") == EXPECTED_BASE, "base main binding drift")

    freeze = p["frozen_inputs"]["trace_population_freeze"]
    require(freeze["freeze_id"] == "S3X-P99X10-TRACE-POPULATION-FREEZE-001", "trace freeze id drift")
    require(freeze["git_blob_sha1"] == EXPECTED_PHASE6C_BLOB, "protocol Phase-6C blob binding drift")
    require(freeze["intervals"] == 1919, "frozen interval count drift")
    require(freeze["channels"] == 176, "frozen channel count drift")
    require(freeze["interval_csv_sha256"] == EXPECTED_INTERVAL_SHA, "interval CSV SHA drift")
    require(freeze["canonical_channel_projection_sha256"] == EXPECTED_PROJECTION, "projection SHA drift")

    parent = p["frozen_inputs"]["study3_semantics"]
    require(parent["experiment_id"] == "S3-K4E-001", "parent Study-3 id drift")
    require(parent["temporal_model_git_blob_sha1"] == EXPECTED_MODEL_BLOB, "parent model binding drift")
    require(parent["protocol_git_blob_sha1"] == EXPECTED_STUDY3_PROTOCOL_BLOB, "parent protocol binding drift")
    require(parent["results_freeze_git_blob_sha1"] == EXPECTED_STUDY3_RESULTS_BLOB, "parent results binding drift")
    require(parent["parent_population_is_read_only"] is True, "parent read-only control missing")
    require(parent["pool_with_parent_study"] is False, "parent pooling unexpectedly enabled")

    timing = p["source_timing_abstraction"]
    require(timing["cadence_unit_definition"].startswith("For interval i"), "cadence-unit definition drift")
    require(timing["normalized_hiatus_formula"] == "g_i = delta_seconds / cadence_p99_seconds", "normalized-gap formula drift")
    require("g_i > 10" in timing["frozen_membership_implication"], "strict P99_X10 consequence missing")
    for key in ("operational_contact_claim", "rf_outage_claim", "spacecraft_outage_claim", "command_availability_claim"):
        require(timing[key] is False, f"unsupported timing claim opened: {key}")

    transition = p["modeled_state_transition"]
    require(transition["hidden_truth_available_to_policy"] is False, "hidden truth leaked to policy")
    require(transition["pre_hiatus_cache_fresh_through_units"] == 1, "freshness normalization drift")
    require(transition["repeated_post_refresh_behavior_modeled"] is False, "unsupported repeated-refresh behavior opened")

    grid = p["factor_grid"]
    require(grid["intervals"] == 1919, "case-grid interval count drift")
    require(grid["policies"] == 3, "case-grid policy count drift")
    require(grid["evidence_states"] == 3, "case-grid evidence count drift")
    require(len(grid["timing_arms"]) == 2, "case-grid timing-arm count drift")
    require(grid["persistence_dimension"] is False, "persistence dimension unexpectedly opened")
    require(grid["expected_cases"] == EXPECTED_CASES, "case-grid total drift")
    require(1919 * 3 * 3 * 2 == EXPECTED_CASES, "case-grid arithmetic error")

    model = load_study3_model()
    require(model.EVIDENCE_TTL_S / model.EPOCH_S == 1, "Study-3 one-epoch freshness ratio drift")

    expected_actions = {
        "S2_B0_FAIL_CLOSED": {
            (True, False): "PROCEED_TO_RECOVERY_GATE",
            (True, True): "PROCEED_TO_RECOVERY_GATE",
            (False, False): "RESTRICT_AND_REQUEST_AUTHORIZATION",
            (False, True): "RESTRICT_AND_REQUEST_AUTHORIZATION",
        },
        "S2_B2_RISK_THRESHOLD": {
            (True, False): "RESTRICT_AND_REQUEST_AUTHORIZATION",
            (True, True): "RESTRICT_AND_REQUEST_AUTHORIZATION",
            (False, False): "HOLD_AND_REQUIRE_EVIDENCE",
            (False, True): "HOLD_AND_REQUIRE_EVIDENCE",
        },
        "S2_S1_EVIDENCE_AWARE": {
            (True, False): "RESTRICT_AND_REQUEST_AUTHORIZATION",
            (True, True): "PROCEED_TO_RECOVERY_GATE",
            (False, False): "HOLD_AND_REQUIRE_EVIDENCE",
            (False, True): "HOLD_AND_REQUIRE_EVIDENCE",
        },
    }
    for policy, table in expected_actions.items():
        for (qualified, proxy), expected in table.items():
            actual = model.select_action(
                policy,
                evidence_qualified=qualified,
                security_signal=True,
                contact=proxy,
            )
            require(actual == expected, f"Study-3 policy semantic drift: {policy}/{qualified}/{proxy}")

    evidence = p["evidence_states"]
    require(evidence["V0"]["first_refresh_claim_authorization_valid"] is False, "V0 claim drift")
    require(evidence["V0"]["first_refresh_signature_valid"] is True, "V0 signature drift")
    require(evidence["V4"]["first_refresh_claim_authorization_valid"] is True, "V4 claim drift")
    require(evidence["V4"]["first_refresh_signature_valid"] is False, "V4 signature drift")
    require(evidence["V5"]["first_refresh_claim_authorization_valid"] is True, "V5 claim drift")
    require(evidence["V5"]["first_refresh_signature_valid"] is True, "V5 signature drift")

    # Cross-check modeled V0/V4/V5 first-refresh semantics against the immutable parent code.
    for label, expected in {
        "V0": (False, True, False),
        "V4": (True, False, True),
        "V5": (True, True, True),
    }.items():
        persistence = "NONE" if label == "V0" else "ONE_SHOT"
        cell = model.Cell("K0", label, persistence, "S2_B0_FAIL_CLOSED")
        rec = model._new_record(cell, t_s=10, onset_s=10, affected_already=False)
        actual = (rec.claim_authorization_valid, rec.signature_valid, rec.treatment_affected)
        require(actual == expected, f"parent evidence semantic drift: {label}")

    auth = p["authorization_model"]
    require(auth["phase7a_design_authorized"] is True, "Phase-7A design authorization missing")
    for key in (
        "implementation_authorized",
        "recovery_policy_execution_authorized",
        "scientific_execution_authorized",
        "manuscript_claim_use_authorized",
    ):
        require(auth[key] is False, f"closed execution gate opened: {key}")
    require(auth["runtime_requires_separate_versioned_authorization_record"] is True, "separate runtime authorization missing")
    require(auth["protocol_merge_requires_separate_author_review"] is True, "separate protocol merge review missing")
    require(auth["post_merge_ci_required_before_any_implementation_or_execution_authorization"] is True, "post-merge CI gate missing")

    status = read_json(STATUS)
    require(status["status"] == "PHASE7A_DESIGN_PREPARED__NO_RECOVERY_OR_SCIENTIFIC_EXECUTION", "Phase-7A status drift")
    require(status["branch_base_commit"] == EXPECTED_BASE, "Phase-7A status base drift")
    require(status["predecessor"]["trace_population_effective"] is True, "effective Phase-6C freeze not recorded")
    require(status["design"]["expected_cases"] == EXPECTED_CASES, "Phase-7A status case count drift")
    require(status["still_closed"]["recovery_policy_execution"] is True, "status opened recovery execution")
    require(status["still_closed"]["scientific_execution"] is True, "status opened scientific execution")
    require(status["still_closed"]["manuscript_claim_use"] is True, "status opened manuscript claims")

    workflow = WORKFLOW.read_text(encoding="utf-8")
    require(
        "python scripts/audit_paper2_post_rejection_phase7a_recovery_replay_design.py"
        in workflow,
        "Phase-7A audit not wired into CI",
    )

    # No scientific S3X output tree is permitted by the design phase.
    for forbidden in (S3X / "results", S3X / "canonical", S3X / "traces"):
        require(not forbidden.exists(), f"forbidden S3X scientific path exists: {forbidden.relative_to(ROOT)}")

    design = DESIGN.read_text(encoding="utf-8")
    for phrase in (
        "DESIGN ONLY",
        "34,542",
        "evidence-refresh hiatus proxy",
        "does **not** cross ONE_SHOT/PERSISTENT",
        "not external empirical replication",
    ):
        require(phrase.lower() in design.lower(), f"design control missing: {phrase}")

    print("paper2_phase7a_recovery_replay_design_audit=PASS")
    print("trace_population_frozen=YES")
    print("phase7_expected_cases=34542")
    print("phase7_implementation_authorized=NO")
    print("recovery_policy_execution=NO")
    print("scientific_execution=NO")
    print("manuscript_claim_use=NO")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
