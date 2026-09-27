#!/usr/bin/env python3
"""Fail-closed audit for Paper-2 Phase-5C P99_X10 gap-rule freeze."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
S3X = ROOT / "study3x"
REBUILD = ROOT / "publication/Paper_2_Studies_3_4_6/Post_Rejection_Rebuild"

EXPECTED_PREFREEZE_SHA256 = (
    "cdf9894a6bf1f3dbe9dadb11ec1484b0c540118b05d108d7a38ed33af5930be0"
)
EXPECTED_PROJECTION_SHA256 = (
    "f15338f1790f60d83d2c849542f6d6e3b21a8c49f7d413cdc5098e35952294d1"
)
EXPECTED_R2_HASHES = {
    "sensitivity_csv": "f690dd230b2897dd74ec880be0de9c207cbb3c975fb4f7740bb18b49df55b88e",
    "delta_frequency_csv": "1399dde74c0cad144e4be4b5c0af201030eaf9ae70621c8b5b70ff9a52b78349",
    "summary_json": "c57fb506c08f03f69f3bed7326355bc97a318f7b6b5015c7745cc3e956865cc6",
}
EXPECTED_ZERO_CHANNELS = {
    ("ESA-Mission2", "channel_100.zip"),
    ("ESA-Mission2", "channel_66.zip"),
    ("ESA-Mission2", "channel_67.zip"),
    ("ESA-Mission2", "channel_68.zip"),
    ("ESA-Mission2", "channel_69.zip"),
}


def fail(message: str) -> None:
    print(f"[FAIL] {message}", file=sys.stderr)
    raise SystemExit(1)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def main() -> int:
    freeze_path = S3X / "config/S3X_GAP_RULE_FREEZE_001.json"
    status_path = REBUILD / "PAPER2_PHASE5C_P99X10_GAP_RULE_FREEZE_STATUS.json"
    gate_path = REBUILD / "PHASE5C_P99X10_GAP_RULE_FREEZE_GATE_R1_2026-09-26.md"

    for path in (freeze_path, status_path, gate_path):
        require(
            path.is_file(),
            f"required Phase-5C file missing: {path.relative_to(ROOT)}",
        )

    freeze = json.loads(freeze_path.read_text(encoding="utf-8"))
    status = json.loads(status_path.read_text(encoding="utf-8"))

    require(freeze.get("schema") == 1, "unexpected freeze schema")
    require(
        freeze.get("freeze_id") == "S3X-P99X10-GAP-RULE-FREEZE-001",
        "unexpected freeze id",
    )
    require(freeze.get("experiment_id") == "S3X-ETA-001", "unexpected experiment id")

    rule = freeze.get("rule", {})
    require(rule.get("name") == "P99_X10", "unexpected frozen rule")
    require(rule.get("status") == "SELECTED_AND_FROZEN", "rule not frozen")
    require(
        rule.get("formula")
        == "threshold_seconds = 10 * channel-specific cadence_p99_seconds",
        "frozen formula drift",
    )
    require(
        rule.get("comparison") == "positive inter-sample delta > threshold_seconds",
        "frozen comparison drift",
    )
    require(rule.get("comparison_operator") == ">", "comparison must remain strict >")
    require(rule.get("multiplier") == 10.0, "multiplier drift")
    require(
        rule.get("reference_statistic") == "channel-specific cadence_p99_seconds",
        "reference statistic drift",
    )

    selection = freeze.get("selection_basis", {})
    require(
        selection.get("type")
        == "DATA_INFORMED_SELECTION_FROM_PRESPECIFIED_PHASE5_CANDIDATE_FAMILY",
        "selection characterization drift",
    )
    require(
        selection.get("cadence_class_specific_multiplier_introduced") is False,
        "cadence-class-specific multiplier must remain absent",
    )
    require(
        selection.get("max_p99_median_family_advanced") is False,
        "MAX_P99_MEDIAN family must remain unadvanced",
    )
    require(len(selection.get("candidate_family", [])) == 8, "candidate family size drift")
    require("P99_X10" in selection.get("candidate_family", []), "P99_X10 missing from candidate family")

    provenance = freeze.get("provenance", {})
    require(
        provenance.get("source_freeze", {}).get("freeze_id")
        == "S3X-ESA-V2-SOURCE-FREEZE-001",
        "source freeze id drift",
    )
    require(
        provenance.get("source_freeze", {}).get("sha256")
        == "dd1d71dc074588c12cae24c3718ed758fabd36c41b22755f57ccf98964db9f27",
        "source freeze hash drift",
    )
    require(
        provenance.get("cadence_review", {}).get("sha256")
        == "7355988e25401d6808019f78723eb7356e1646936be41664ce270667cf454b48",
        "cadence review hash drift",
    )

    r2 = provenance.get("sensitivity_r2", {})
    for key, expected in EXPECTED_R2_HASHES.items():
        require(r2.get(key, {}).get("sha256") == expected, f"R2 hash drift: {key}")

    prefreeze = provenance.get("prefreeze_validation", {})
    require(
        prefreeze.get("sha256") == EXPECTED_PREFREEZE_SHA256,
        "pre-freeze validation hash drift",
    )
    require(prefreeze.get("status") == "PASS", "pre-freeze validation must be PASS")
    require(prefreeze.get("channels") == 176, "pre-freeze channel count drift")
    require(
        prefreeze.get("total_exceedance_count") == 1919,
        "pre-freeze aggregate drift",
    )
    require(
        prefreeze.get("channels_with_exceedances") == 171,
        "pre-freeze nonzero-channel count drift",
    )
    require(
        prefreeze.get("channels_with_zero_exceedances") == 5,
        "pre-freeze zero-channel count drift",
    )
    require(
        prefreeze.get("canonical_channel_projection_sha256")
        == EXPECTED_PROJECTION_SHA256,
        "canonical projection hash drift",
    )

    zero_channels = {
        (item.get("mission"), item.get("channel_file"))
        for item in freeze.get("zero_exceedance_channels", [])
    }
    require(zero_channels == EXPECTED_ZERO_CHANNELS, "zero-exceedance channel set drift")

    lock = freeze.get("lock_policy", {})
    require(lock.get("immutable_for_next_trace_extraction") is True, "freeze not locked for extraction")
    require(lock.get("retune_after_timestamp_trace_inspection") is False, "post-inspection retuning opened")
    require(lock.get("overwrite_this_freeze") is False, "freeze overwrite allowed")
    require(
        lock.get("change_requires_new_versioned_protocol_and_separate_authorization") is True,
        "versioned change control missing",
    )

    gates = freeze.get("gates", {})
    require(gates.get("gap_rule_selected") is True, "gap rule not selected")
    require(gates.get("gap_rule_frozen") is True, "gap rule not frozen")
    for key in (
        "timestamp_level_gap_trace_extraction",
        "trace_population_frozen",
        "recovery_policy_execution_performed",
        "scientific_results_generated",
        "manuscript_claim_use",
    ):
        require(gates.get(key) is False, f"closed freeze gate changed: {key}")

    require(
        status.get("status") == "AUTHORIZED_RULE_FREEZE__AWAITING_CI",
        "unexpected Phase-5C status",
    )
    local = status.get("predecessor", {}).get("local_prefreeze_validation", {})
    require(local.get("status") == "PASS", "Phase-5B local validation not bound as PASS")
    require(local.get("sha256") == EXPECTED_PREFREEZE_SHA256, "status pre-freeze hash drift")
    require(local.get("worktree_clean_after_run") is True, "pre-freeze post-run worktree not clean")

    status_freeze = status.get("freeze", {})
    require(
        status_freeze.get("freeze_id") == "S3X-P99X10-GAP-RULE-FREEZE-001",
        "status freeze id drift",
    )
    require(status_freeze.get("gap_rule_selected") is True, "status does not select rule")
    require(status_freeze.get("gap_rule_frozen") is True, "status does not freeze rule")

    prohibited = status.get("prohibited", {})
    for key in (
        "timestamp_level_gap_trace_extraction",
        "trace_population_freeze",
        "recovery_policy_execution",
        "scientific_execution",
        "manuscript_claim_use",
    ):
        require(prohibited.get(key) is True, f"closed Phase-5C gate not recorded: {key}")

    for forbidden in (
        S3X / "results",
        S3X / "canonical",
        S3X / "traces",
    ):
        require(
            not forbidden.exists(),
            f"forbidden S3X scientific path exists: {forbidden.relative_to(ROOT)}",
        )

    print("paper2_phase5c_p99x10_gap_rule_freeze_audit=PASS")
    print("gap_rule=P99_X10")
    print("gap_rule_selected=YES")
    print("gap_rule_frozen=YES")
    print("trace_extraction=NO")
    print("trace_population_freeze=NO")
    print("recovery_policy_execution=NO")
    print("scientific_execution=NO")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
