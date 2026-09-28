#!/usr/bin/env python3
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
WORKFLOW = ROOT / ".github/workflows/validate-research-configs.yml"

CANDIDATE2 = S3X / "config/S3X_PHASE7_IMPLEMENTATION_FREEZE_CANDIDATE_002.json"
AUTH2 = S3X / "config/S3X_PHASE7_RUNTIME_AUTH_002.json"
STATUS = REBUILD / "PAPER2_PHASE7D_FLOAT_CONTRACT_CORRECTION_STATUS.json"
DOC = REBUILD / "PHASE7D_FLOAT_CONTRACT_CORRECTION_R1_2026-09-27.md"

EXPECTED = {
    "study3x/config/S3X_PHASE7_IMPLEMENTATION_FREEZE_CANDIDATE_002.json":
        "d7ee15c6a2bfe818ee016eadba0893ef74aa8f18",
    "study3x/config/S3X_PHASE7_RUNTIME_AUTH_002.json":
        "bb7978052cf03bdfaa628a44d7d268d73e9c005a",
    "study3x/src/recovery_replay_v2.py":
        "40e3bd0406f1f0bedecbac9cb1386699a8619318",
    "study3x/audit/reference_replay_v2.py":
        "26444d206f18bededa656b1de56d9ba0948c6ef3",
    "study3x/runtime/run_phase7_replay_v2.py":
        "f2a789edd24a0e23ff0d256312fc7d2b7e656573",
    "study3x/audit/validate_phase7_replay_v2.py":
        "15796f7b8e2da3f92e941021839b387ad365394e",
    "study3x/validation/run_local_phase7_replay_v2.sh":
        "95cb497cd0465a34e1e8e17609c4e5f781ba8aaf",
}

HISTORICAL = {
    "study3x/config/S3X_PHASE7_RUNTIME_AUTH_001.json":
        "f9dda173cecbbf0902c48f5c291cd7025c3df8d3",
    "study3x/src/recovery_replay.py":
        "09a1c887f8861a6e5dba6059cab2ab906befbbcd",
    "study3x/audit/reference_replay.py":
        "9e13446323be67115950374cb5debfaa7532a17e",
    "study3x/runtime/run_phase7_replay.py":
        "1aefa814d8f619dcd5ac9c0848950965660b5c90",
    "study3x/audit/validate_phase7_replay.py":
        "df9faa48a92d0cccd32d77365a163518f8574d5b",
    "study3x/validation/run_local_phase7_replay.sh":
        "e5b8ead787a1811070a953ff7803c948defea95d",
}

EXPECTED_INPUT_SHA = "cfa4fa3d88cb525237cbfe347fabe8485021351f3b639bdb58f79c575d8a51bc"


def require(condition: bool, message: str) -> None:
    if not condition:
        print(f"[FAIL] {message}", file=sys.stderr)
        raise SystemExit(1)


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def git_blob(rel: str) -> str:
    return subprocess.check_output(
        ["git", "hash-object", rel],
        cwd=ROOT,
        text=True,
    ).strip()


def synthetic_float_serialization_row() -> dict[str, object]:
    return {
        "schema_version": 1,
        "experiment_id": "S3X-ETA-001",
        "source_freeze_id": "S3X-ESA-V2-SOURCE-FREEZE-001",
        "source_freeze_sha256": "synthetic",
        "gap_rule_freeze_id": "S3X-P99X10-GAP-RULE-FREEZE-001",
        "gap_rule": "P99_X10",
        "mission": "SYNTHETIC-MISSION",
        "channel_file": "synthetic_channel.zip",
        "channel_sha256": "synthetic",
        "preceding_timestamp_ns": 0,
        "following_timestamp_ns": 800000000,
        "preceding_timestamp": "SYNTHETIC-T0",
        "following_timestamp": "SYNTHETIC-T1",
        "delta_nanoseconds": 800000000,
        "delta_seconds": "0.8",
        "cadence_p99_seconds": "0.07",
        "threshold_seconds": "0.7000000000000001",
        "comparison_operator": ">",
        "diagnostic_label": "EXTREME_TELEMETRY_INTER_SAMPLE_INTERVAL_DIAGNOSTIC",
        "interval_id": "S3X-SYNTH-FLOAT-CONTRACT",
    }


def main() -> int:
    for rel, wanted in {**HISTORICAL, **EXPECTED}.items():
        path = ROOT / rel
        require(path.is_file(), f"missing bound file: {rel}")
        require(git_blob(rel) == wanted, f"bound blob drift: {rel}")

    require(CANDIDATE2.is_file(), "corrected implementation candidate missing")
    require(AUTH2.is_file(), "corrected runtime authorization missing")
    require(STATUS.is_file(), "Phase-7D status missing")
    require(DOC.is_file(), "Phase-7D correction note missing")

    candidate = read_json(CANDIDATE2)
    require(
        candidate["implementation_candidate_id"]
        == "S3X-PHASE7-IMPLEMENTATION-CANDIDATE-002",
        "candidate-002 id drift",
    )
    require(
        candidate["supersedes_implementation_candidate_id"]
        == "S3X-PHASE7-IMPLEMENTATION-CANDIDATE-001",
        "candidate supersession drift",
    )
    require(
        candidate["correction_basis"]["classification"]
        == "IMPLEMENTATION_VALIDATION_CONTRACT_MISMATCH__NOT_DATA_OR_RULE_FAILURE",
        "root-cause classification drift",
    )
    require(candidate["correction_basis"]["frozen_population_changed"] is False, "frozen population changed")
    require(candidate["correction_basis"]["p99_x10_rule_changed"] is False, "P99_X10 changed")
    require(candidate["correction_basis"]["interval_membership_changed"] is False, "interval membership changed")
    require(candidate["correction_basis"]["scientific_cases_generated_by_failed_attempt"] == 0, "failed attempt generated cases")
    require(candidate["numerical_contract"]["tolerance_added"] is False, "numeric tolerance added")
    require(candidate["numerical_contract"]["epsilon_added"] is False, "numeric epsilon added")
    require(candidate["numerical_contract"]["retuning_performed"] is False, "retuning performed")
    require(
        candidate["frozen_bindings"]["frozen_interval_artifact_sha256"] == EXPECTED_INPUT_SHA,
        "frozen input SHA drift",
    )

    auth = read_json(AUTH2)
    require(auth["authorization_id"] == "S3X-PHASE7-RUNTIME-AUTH-002", "auth-002 id drift")
    require(auth["supersedes_authorization_id"] == "S3X-PHASE7-RUNTIME-AUTH-001", "auth supersession drift")
    require(auth["status"] == "PREPARED_ON_FEATURE_BRANCH__NOT_EFFECTIVE", "auth-002 effectivity drift")
    require(
        auth["correction_predecessor"]["prior_execution_attempt"]
        == "STOPPED_BEFORE_CASE_GENERATION",
        "prior failure boundary drift",
    )
    require(
        auth["correction_predecessor"]["frozen_input_sha256_verified_during_failed_attempt"]
        == EXPECTED_INPUT_SHA,
        "prior frozen input verification drift",
    )
    require(auth["numerical_contract"]["tolerance_or_epsilon_introduced"] is False, "auth adds tolerance")
    require(auth["numerical_contract"]["gap_rule_retuned"] is False, "auth retunes gap rule")
    require(auth["numerical_contract"]["membership_reselected"] is False, "auth reselects membership")
    require(
        auth["frozen_bindings"]["local_runtime_gate_v2"]["git_blob_sha1"]
        == EXPECTED["study3x/validation/run_local_phase7_replay_v2.sh"],
        "auth v2 runner binding drift",
    )
    require(auth["effectivity"]["record_merge_requires_separate_author_review"] is True, "separate merge review missing")
    require(auth["effectivity"]["post_merge_ci_required_before_reexecution"] is True, "post-merge CI gate missing")
    require(
        auth["effectivity"][
            "actual_corrected_runtime_execution_requires_explicit_post_merge_author_instruction"
        ] is True,
        "explicit corrected runtime instruction gate missing",
    )
    require(all(value is False for value in auth["execution_state_at_record_creation"].values()), "auth-002 records execution at creation")

    status = read_json(STATUS)
    require(
        status["status"]
        == "PHASE7D_CORRECTION_PREPARED__NOT_EFFECTIVE__NO_SCIENTIFIC_RESULTS",
        "Phase-7D status drift",
    )
    observed = status["observed_attempt"]
    require(observed["authorized_main_verified"] is True, "authorized main not recorded")
    require(observed["frozen_interval_csv_sha256_verified"] == EXPECTED_INPUT_SHA, "observed input SHA drift")
    require(observed["case_generation_started"] is False, "case generation incorrectly recorded")
    require(observed["case_rows_generated"] == 0, "failed attempt case count drift")
    require(observed["independent_validation_started"] is False, "independent validation incorrectly recorded")
    require(all(value is False for value in status["executed_now"].values()), "corrected execution recorded before merge")

    v1 = importlib.import_module("study3x.src.recovery_replay")
    v2 = importlib.import_module("study3x.src.recovery_replay_v2")
    ref2 = importlib.import_module("study3x.audit.reference_replay_v2")

    fixture = synthetic_float_serialization_row()
    require(
        float(fixture["threshold_seconds"])
        == float(fixture["cadence_p99_seconds"]) * 10.0,
        "synthetic fixture does not reproduce Phase-6 float relation",
    )

    old_failed = False
    try:
        v1.parse_interval_row(fixture)
    except ValueError as exc:
        old_failed = "threshold relationship is inconsistent" in str(exc)
    require(old_failed, "v1 regression fixture no longer reproduces observed defect")

    parsed = v2.parse_interval_row(fixture)
    require(parsed.normalized_hiatus.numerator == 80, "v2 normalized numerator drift")
    require(parsed.normalized_hiatus.denominator == 7, "v2 normalized denominator drift")

    primary = asdict(
        v2.evaluate_case(
            fixture,
            policy="S2_S1_EVIDENCE_AWARE",
            evidence_state="V5",
            timing_arm="EMPIRICAL_HIATUS_PROXY",
        )
    )
    reference = ref2.evaluate_reference(
        fixture,
        policy="S2_S1_EVIDENCE_AWARE",
        evidence_state="V5",
        timing_arm="EMPIRICAL_HIATUS_PROXY",
    )
    for field in (
        "normalized_hiatus_units",
        "first_refresh_action",
        "first_refresh_gate_qualified",
        "first_refresh_unsafe_qualified",
        "v5_first_refresh_qualification_delay_cadence_units",
    ):
        require(primary[field] == reference[field], f"v2 primary/reference drift: {field}")

    bad = dict(fixture)
    bad["threshold_seconds"] = "0.7"
    corrected_rejected = False
    try:
        v2.parse_interval_row(bad)
    except ValueError as exc:
        corrected_rejected = "threshold float relationship" in str(exc)
    require(corrected_rejected, "v2 accepted threshold inconsistent with Phase-6 float contract")

    tracked = subprocess.check_output(["git", "ls-files"], cwd=ROOT, text=True).splitlines()
    forbidden_names = {
        "S3X_PHASE7_CASE_RESULTS_001.csv",
        "S3X_PHASE7_MATCHED_COMPARISONS_001.csv",
        "S3X_PHASE7_SUMMARY_001.json",
        "S3X_PHASE7_INDEPENDENT_VALIDATION_001.json",
        "S3X_PHASE7_RESULTS_HASH_MANIFEST_001.json",
    }
    require(
        not any(Path(path).name in forbidden_names for path in tracked),
        "scientific Phase-7 output tracked during correction",
    )

    workflow = WORKFLOW.read_text(encoding="utf-8")
    require(
        "python scripts/audit_paper2_post_rejection_phase7d_float_contract_correction.py"
        in workflow,
        "Phase-7D audit not wired into CI",
    )

    print("paper2_phase7d_float_contract_correction_audit=PASS")
    print("historical_v1_provenance_preserved=YES")
    print("phase6_float_contract_reproduced=YES")
    print("tolerance_added=NO")
    print("p99_x10_retuned=NO")
    print("interval_membership_changed=NO")
    print("failed_attempt_case_rows=0")
    print("corrected_runtime_effective=NO")
    print("corrected_scientific_execution=NO")
    print("result_freeze=NO")
    print("manuscript_claim_use=NO")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
