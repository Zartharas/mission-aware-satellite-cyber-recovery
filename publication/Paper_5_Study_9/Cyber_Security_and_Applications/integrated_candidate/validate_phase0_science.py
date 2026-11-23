#!/usr/bin/env python3
"""Read-only Phase 0 / Phase 1 checks. No raw telemetry, network or selector execution."""
from __future__ import annotations
from collections import Counter
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
CANONICAL = ROOT / "study9/results/S9-RTSI-001_CANONICAL_RUN_20260914"
DERIVED = HERE / "study10_derived"
PINS = {
    "S10_G4_TierA_32Slot_PublishedSchema.json":
        "f727bc80823d9fe5a47d44c361b9aefcdadc6b5a144331f2857079ce91508d1c",
    "S10_G4_TierC_16_StratumPolicy_NonEvaluable.json":
        "93dd4f92810a33f0dbe13dd11f842f732a4ccc9fac322a762fcab557185623f6",
    "S10_RQ_E3_ESA_V1V2_Aggregate_Metadata.json":
        "ba343e858b4d54256f8f4d8b118bb87a95a49a0d99baebc394ac5517c418ddc9",
}
SOURCE_ROWS = {
    "CUCD_ID_V3": 25000,
    "AEGISSAT_2025": 137965,
    "UNSW_IOTSAT_2026": 404798,
}
S9_CLASSES = {
    "CUCD_ID_V3": {"ABSENT": 4, "AMBIGUOUS": 4},
    "AEGISSAT_2025": {"ABSENT": 3, "AMBIGUOUS": 5},
    "UNSW_IOTSAT_2026": {"ABSENT": 3, "AMBIGUOUS": 5},
}
POLICIES = {
    "S2_B0_FAIL_CLOSED": (2, 6),
    "S2_B1_FAIL_OPERATIONAL": (2, 7),
    "S2_B2_RISK_THRESHOLD": (3, 7),
    "S2_S1_EVIDENCE_AWARE": (3, 8),
}
S10_CLASSES = {
    "ESA_ADB_V2_MISSION1": {"ABSENT": 4, "AMBIGUOUS": 4},
    "ESA_ADB_V2_MISSION2": {"ABSENT": 4, "AMBIGUOUS": 4},
    "ESA_ADB_V2_MISSION3": {"ABSENT": 5, "AMBIGUOUS": 3},
    "OPS_SAT_AD_SEGMENTS": {"ABSENT": 5, "AMBIGUOUS": 3},
}


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def group_counts(records, key, by):
    result = {}
    for row in records:
        result.setdefault(row[key], Counter())[row[by]] += 1
    return {k: dict(v) for k, v in result.items()}


def check():
    frozen = load_json(HERE / "PHASE0_PROTECTED_BASELINE_20261123.json")
    assert frozen["reviewed_head"] == "25f88adb20b790dc0de0104aab4e5426ccf1a00a"
    assert frozen["approved_scope"] == [
        "PHASE_0_PROTECTION", "PHASE_1_MANUSCRIPT_SCIENTIFIC_INTERPRETATION_NOVELTY"
    ]
    assert sum(SOURCE_ROWS.values()) == 567763
    for name, sha in PINS.items():
        data = (DERIVED / name).read_bytes()
        assert hashlib.sha256(data).hexdigest() == sha, name
    a = load_json(DERIVED / "S10_G4_TierA_32Slot_PublishedSchema.json")
    c = load_json(DERIVED / "S10_G4_TierC_16_StratumPolicy_NonEvaluable.json")
    e = load_json(DERIVED / "S10_RQ_E3_ESA_V1V2_Aggregate_Metadata.json")
    assert len(a["adjudications"]) == 32
    assert group_counts(a["adjudications"], "dataset_id", "mapping_class") == S10_CLASSES
    assert len(c["policy_results"]) == 16
    assert all(x["Tier_C_disposition"] == "NOT_EVALUABLE_FOR_OPERATIONAL_ACTION"
               for x in c["policy_results"])
    assert c["input_Tier_A_sha256"] == PINS["S10_G4_TierA_32Slot_PublishedSchema.json"]
    assert e["totals"]["matched_channels"] == 224
    assert e["totals"]["paired_common_field_cells"] == 896
    assert e["totals"]["changed_common_field_values"] == 54
    assert e["totals"]["channels_only_v1"] == 0 and e["totals"]["channels_only_v2"] == 0
    assert e["channel_identifiers_in_report"] is False
    assert e["metadata_values_in_report"] is False
    m = load_json(CANONICAL / "mapping_matrix.json")
    p = load_json(CANONICAL / "policy_strata.json")
    assert len(m) == 24
    assert group_counts(m, "dataset_id", "mapping_class") == S9_CLASSES
    assert len(p["datasets"]) == 3
    for dataset in p["datasets"]:
        key = dataset["dataset_id"]
        assert key in SOURCE_ROWS
        assert dataset["native_state_group_count"] == 1
        assert len(dataset["policy_strata"]) == 4
        for policy in dataset["policy_strata"]:
            assert policy["policy"] in POLICIES
            expected_actions, expected_sidecar = POLICIES[policy["policy"]]
            assert policy["source_row_count"] == SOURCE_ROWS[key]
            assert policy["unique_action_fraction"] == {
                "denominator": SOURCE_ROWS[key], "numerator": 0}
            assert len(policy["group_results"]) == 1
            group = policy["group_results"][0]
            assert group["multiplicity"] == SOURCE_ROWS[key]
            assert group["action_set_cardinality"] == expected_actions
            assert group["guaranteed_sidecar_cardinality"] == expected_sidecar
    tex = (HERE / "CSA_S9_S10_INTEGRATED_CANDIDATE.tex").read_text(encoding="utf-8")
    for anchor in [
        "25,000", "137,965", "404,798", "567,763",
        "0/8", "14 ambiguous", "18 absent", "16",
        "224", "896", "842", "54",
        r"\{0,1\}^{8}", "NOT\_EVALUABLE\_FOR\_OPERATIONAL\_ACTION",
        "Post-results integration",
    ]:
        assert anchor in tex, f"Missing audited manuscript anchor {anchor!r}"
    print("PAPER5_PHASE0_FROZEN_ASSERTIONS_PASS: source results unchanged")


if __name__ == "__main__":
    check()
