#!/usr/bin/env python3
"""Fail-closed audit for Paper-2 S3X Phase-7B pre-runtime implementation."""

from __future__ import annotations

from dataclasses import asdict
import importlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

S3X = ROOT / "study3x"
REBUILD = ROOT / "publication/Paper_2_Studies_3_4_6/Post_Rejection_Rebuild"

PROTOCOL = S3X / "config/S3X_PHASE7_RECOVERY_REPLAY_PROTOCOL_001.json"
TRACE_FREEZE = S3X / "config/S3X_PHASE6_TRACE_POPULATION_FREEZE_001.json"
CANDIDATE = S3X / "config/S3X_PHASE7_IMPLEMENTATION_FREEZE_CANDIDATE_001.json"
PRIMARY = S3X / "src/recovery_replay.py"
REFERENCE = S3X / "audit/reference_replay.py"
STATUS = REBUILD / "PAPER2_PHASE7B_IMPLEMENTATION_STATUS.json"
DESIGN = REBUILD / "PHASE7B_PRE_RUNTIME_IMPLEMENTATION_R1_2026-09-27.md"
WORKFLOW = ROOT / ".github/workflows/validate-research-configs.yml"
PARENT_MODEL = ROOT / "study3/src/temporal_model.py"

EXPECTED_BASE = "445435aaa1618e0a08df35071221451f35ef5e98"
EXPECTED_PROTOCOL_BLOB = "f42fe8c0c58ee3b9152e629f5673bd5c71ffede4"
EXPECTED_TRACE_FREEZE_BLOB = "ed0bdcec443b7f0c3ee80d441e1122f32e499d3e"
EXPECTED_PARENT_MODEL_BLOB = "b13e62456c144db0e12808bf700586c1c844c33d"
EXPECTED_PRIMARY_BLOB = "09a1c887f8861a6e5dba6059cab2ab906befbbcd"
EXPECTED_REFERENCE_BLOB = "9e13446323be67115950374cb5debfaa7532a17e"
EXPECTED_INTERVAL_SHA = "cfa4fa3d88cb525237cbfe347fabe8485021351f3b639bdb58f79c575d8a51bc"


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


def synthetic_interval(
    *,
    interval_id: str,
    delta: str,
    cadence: str,
    threshold: str,
) -> dict[str, object]:
    return {
        "schema_version": 1,
        "experiment_id": "S3X-ETA-001",
        "source_freeze_id": "S3X-ESA-V2-SOURCE-FREEZE-001",
        "source_freeze_sha256": "synthetic-not-used",
        "gap_rule_freeze_id": "S3X-P99X10-GAP-RULE-FREEZE-001",
        "gap_rule": "P99_X10",
        "mission": "SYNTHETIC-MISSION",
        "channel_file": "synthetic_channel.zip",
        "channel_sha256": "synthetic-not-used",
        "preceding_timestamp_ns": 0,
        "following_timestamp_ns": 1,
        "preceding_timestamp": "SYNTHETIC-T0",
        "following_timestamp": "SYNTHETIC-T1",
        "delta_nanoseconds": 1,
        "delta_seconds": delta,
        "cadence_p99_seconds": cadence,
        "threshold_seconds": threshold,
        "comparison_operator": ">",
        "diagnostic_label": "EXTREME_TELEMETRY_INTER_SAMPLE_INTERVAL_DIAGNOSTIC",
        "interval_id": interval_id,
    }


def main() -> int:
    for path in (
        PROTOCOL,
        TRACE_FREEZE,
        CANDIDATE,
        PRIMARY,
        REFERENCE,
        STATUS,
        DESIGN,
        WORKFLOW,
        PARENT_MODEL,
    ):
        require(path.is_file(), f"missing Phase-7B dependency: {path.relative_to(ROOT)}")

    require(git_blob(PROTOCOL) == EXPECTED_PROTOCOL_BLOB, "Phase-7 protocol blob drift")
    require(git_blob(TRACE_FREEZE) == EXPECTED_TRACE_FREEZE_BLOB, "trace-freeze blob drift")
    require(git_blob(PARENT_MODEL) == EXPECTED_PARENT_MODEL_BLOB, "parent Study-3 model blob drift")
    require(git_blob(PRIMARY) == EXPECTED_PRIMARY_BLOB, "primary implementation blob drift")
    require(git_blob(REFERENCE) == EXPECTED_REFERENCE_BLOB, "reference implementation blob drift")

    candidate = read_json(CANDIDATE)
    require(
        candidate.get("status")
        == "PRE_RUNTIME_IMPLEMENTATION_CANDIDATE__NOT_FROZEN__NO_REAL_DATA_EXECUTION",
        "implementation candidate status drift",
    )
    require(candidate.get("branch_base_main_commit") == EXPECTED_BASE, "candidate base binding drift")

    bindings = candidate["frozen_bindings"]
    require(bindings["phase7_protocol_git_blob_sha1"] == EXPECTED_PROTOCOL_BLOB, "protocol binding drift")
    require(bindings["trace_population_freeze_git_blob_sha1"] == EXPECTED_TRACE_FREEZE_BLOB, "trace binding drift")
    require(bindings["parent_study3_temporal_model_git_blob_sha1"] == EXPECTED_PARENT_MODEL_BLOB, "parent-model binding drift")
    require(bindings["frozen_interval_artifact_sha256"] == EXPECTED_INTERVAL_SHA, "interval SHA binding drift")
    require(bindings["frozen_interval_count"] == 1919, "frozen interval count drift")
    require(bindings["expected_case_count"] == 34542, "prospective case count drift")

    files = candidate["implementation_files"]
    require(files["primary"]["git_blob_sha1"] == EXPECTED_PRIMARY_BLOB, "primary candidate binding drift")
    require(files["reference"]["git_blob_sha1"] == EXPECTED_REFERENCE_BLOB, "reference candidate binding drift")

    scope = candidate["pre_runtime_scope"]
    require(scope["synthetic_fixture_execution_authorized"] is True, "synthetic verification not authorized")
    require(scope["real_frozen_interval_artifact_read_authorized"] is False, "real artifact read unexpectedly opened")
    require(scope["real_1919_interval_expansion_authorized"] is False, "real population expansion unexpectedly opened")
    require(scope["recovery_policy_execution_authorized"] is False, "recovery execution unexpectedly opened")
    require(scope["scientific_execution_authorized"] is False, "scientific execution unexpectedly opened")
    require(scope["manuscript_claim_use_authorized"] is False, "manuscript use unexpectedly opened")
    require(scope["accepted_primary_reference_mismatches"] == 0, "mismatch acceptance drift")

    controls = candidate["implementation_controls"]
    require(controls["direct_module_execution_fails_closed"] is True, "direct-execution fail-close missing")
    require(controls["reference_does_not_import_primary_implementation"] is True, "reference independence control missing")
    require(controls["reference_reimplements_policy_table"] is True, "reference policy reimplementation missing")
    require(controls["timing_arithmetic_is_exact_rational"] is True, "exact-rational arithmetic control missing")
    require(controls["no_randomness"] is True, "randomness unexpectedly allowed")
    require(controls["no_network_access"] is True, "network access unexpectedly allowed")
    require(controls["no_source_trace_membership_selection"] is True, "source membership selection unexpectedly allowed")
    require(controls["no_gap_rule_retuning"] is True, "gap-rule retuning unexpectedly allowed")

    protocol = read_json(PROTOCOL)
    require(protocol["factor_grid"]["expected_cases"] == 34542, "Phase-7A case-grid drift")
    require(protocol["factor_grid"]["persistence_dimension"] is False, "persistence dimension opened")
    require(protocol["authorization_model"]["implementation_authorized"] is False, "historical Phase-7A record was mutated")
    require(protocol["authorization_model"]["recovery_policy_execution_authorized"] is False, "historical runtime gate mutated")
    require(protocol["authorization_model"]["scientific_execution_authorized"] is False, "historical scientific gate mutated")

    primary = importlib.import_module("study3x.src.recovery_replay")
    reference = importlib.import_module("study3x.audit.reference_replay")

    require(
        primary.EXPECTED_INTERVAL_ARTIFACT_SHA256 == EXPECTED_INTERVAL_SHA,
        "primary frozen-artifact hash constant drift",
    )

    parity_fields = (
        "interval_id",
        "policy",
        "evidence_state",
        "timing_arm",
        "normalized_hiatus_units",
        "cache_origin_unsafe_qualified_exposure_cadence_units",
        "protective_hiatus_duration_cadence_units",
        "first_refresh_time_cadence_units",
        "first_refresh_action",
        "first_refresh_gate_qualified",
        "first_refresh_unsafe_permissive",
        "first_refresh_unsafe_qualified",
        "first_refresh_unsafe_qualification_origin",
        "v5_first_refresh_qualification_delay_cadence_units",
    )
    fixtures = (
        synthetic_interval(interval_id="S3X-SYNTH-A", delta="25", cadence="2", threshold="20"),
        synthetic_interval(interval_id="S3X-SYNTH-B", delta="31.5", cadence="2.5", threshold="25"),
        synthetic_interval(interval_id="S3X-SYNTH-C", delta="27.5", cadence="2.5", threshold="25"),
    )
    mismatches = []
    case_count = 0
    for row in fixtures:
        require(len(primary.evaluate_interval(row)) == 18, "synthetic interval did not expand to 18 cases")
        for policy in primary.POLICIES:
            for evidence_state in primary.EVIDENCE_STATES:
                for timing_arm in primary.TIMING_ARMS:
                    case_count += 1
                    actual = asdict(
                        primary.evaluate_case(
                            row,
                            policy=policy,
                            evidence_state=evidence_state,
                            timing_arm=timing_arm,
                        )
                    )
                    expected = reference.evaluate_reference(
                        row,
                        policy=policy,
                        evidence_state=evidence_state,
                        timing_arm=timing_arm,
                    )
                    for field in parity_fields:
                        if actual[field] != expected[field]:
                            mismatches.append(
                                (
                                    row["interval_id"],
                                    policy,
                                    evidence_state,
                                    timing_arm,
                                    field,
                                    actual[field],
                                    expected[field],
                                )
                            )
    require(case_count == 54, "synthetic parity case count drift")
    require(mismatches == [], f"primary/reference mismatches: {mismatches[:3]}")

    # Exact prespecified policy consequences on a synthetic >10-cadence interval.
    row = fixtures[0]
    b0_gap = primary.evaluate_case(
        row,
        policy="S2_B0_FAIL_CLOSED",
        evidence_state="V5",
        timing_arm="EMPIRICAL_HIATUS_PROXY",
    )
    require(
        b0_gap.cache_origin_unsafe_qualified_exposure_cadence_units == "1",
        "B0 cache-origin exposure drift",
    )
    require(b0_gap.first_refresh_unsafe_qualified is True, "B0/V5 first-refresh qualification drift")

    s1_gap = primary.evaluate_case(
        row,
        policy="S2_S1_EVIDENCE_AWARE",
        evidence_state="V5",
        timing_arm="EMPIRICAL_HIATUS_PROXY",
    )
    require(
        s1_gap.cache_origin_unsafe_qualified_exposure_cadence_units == "0",
        "S1 cache-origin exposure drift",
    )
    require(s1_gap.first_refresh_unsafe_qualified is True, "S1/V5 first-refresh qualification drift")

    b2_gap = primary.evaluate_case(
        row,
        policy="S2_B2_RISK_THRESHOLD",
        evidence_state="V5",
        timing_arm="EMPIRICAL_HIATUS_PROXY",
    )
    require(b2_gap.first_refresh_unsafe_qualified is False, "B2/V5 first-refresh restriction drift")

    status = read_json(STATUS)
    require(
        status["status"]
        == "PHASE7B_IMPLEMENTATION_PREPARED__SYNTHETIC_VALIDATION_ONLY__NO_REAL_EXECUTION",
        "Phase-7B status drift",
    )
    require(status["branch_base_commit"] == EXPECTED_BASE, "Phase-7B base status drift")
    require(status["predecessor"]["phase7_design_contract_effective"] is True, "Phase-7A design effectivity missing")
    for key in (
        "real_frozen_interval_artifact_read",
        "real_1919_interval_expansion",
        "recovery_policy_execution",
        "scientific_execution",
        "manuscript_claim_use",
        "implementation_freeze_effectivity",
        "runtime_authorization",
    ):
        require(status["still_closed"][key] is True, f"closed Phase-7B gate opened: {key}")

    # Phase 7B itself introduced no real-data runner. A later separately governed
    # Phase-7C authorization may add exactly one bound local gate; any other
    # Phase-7 shell runner remains a fail-closed condition.
    tracked = subprocess.check_output(["git", "ls-files"], cwd=ROOT, text=True).splitlines()
    phase7_runner_names = [
        p for p in tracked
        if p.startswith("study3x/") and "phase7" in p.lower() and p.endswith(".sh")
    ]
    allowed_later_runner = "study3x/validation/run_local_phase7_replay.sh"
    if phase7_runner_names:
        require(
            phase7_runner_names == [allowed_later_runner],
            f"ungoverned Phase-7 real-data runner tracked: {phase7_runner_names}",
        )
        later_auth = S3X / "config/S3X_PHASE7_RUNTIME_AUTH_001.json"
        require(later_auth.is_file(), "Phase-7C runner exists without versioned runtime authorization")
        later = read_json(later_auth)
        require(
            later.get("status") == "PREPARED_ON_FEATURE_BRANCH__NOT_EFFECTIVE",
            "Phase-7C authorization preparation state drift",
        )
        require(
            later.get("effectivity", {}).get("record_merge_requires_separate_author_review") is True,
            "Phase-7C runner lacks separate merge authorization control",
        )
        require(
            later.get("effectivity", {}).get("actual_runtime_execution_requires_explicit_post_merge_author_instruction") is True,
            "Phase-7C runner lacks explicit post-merge execution instruction gate",
        )
    for forbidden in (S3X / "results", S3X / "canonical", S3X / "traces"):
        require(not forbidden.exists(), f"forbidden S3X scientific output path exists: {forbidden.relative_to(ROOT)}")

    primary_text = PRIMARY.read_text(encoding="utf-8")
    reference_text = REFERENCE.read_text(encoding="utf-8")
    require("real frozen-interval recovery-policy execution is not authorized" in primary_text, "primary direct-execution guard missing")
    require("real frozen-interval validation is not authorized" in reference_text, "reference direct-execution guard missing")
    require("study3x.src.recovery_replay" not in reference_text, "reference imports primary implementation")

    workflow = WORKFLOW.read_text(encoding="utf-8")
    require(
        "python scripts/audit_paper2_post_rejection_phase7b_replay_implementation.py"
        in workflow,
        "Phase-7B audit not wired into CI",
    )

    print("paper2_phase7b_replay_implementation_audit=PASS")
    print("synthetic_fixture_intervals=3")
    print("synthetic_primary_reference_cases=54")
    print("primary_reference_mismatches=0")
    print("real_frozen_interval_artifact_read=NO")
    print("real_1919_interval_expansion=NO")
    print("recovery_policy_execution=NO")
    print("scientific_execution=NO")
    print("manuscript_claim_use=NO")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
