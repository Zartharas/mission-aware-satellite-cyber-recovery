#!/usr/bin/env python3
"""Fail-closed audit for Paper-2 post-rejection Phase-1 state.

This checker is read-only. It validates the TAES decision record, frozen
Study-3/4/6 identities, Phase-1 governance, non-overlap controls, and the
closed-form/read-only derivations. It never executes a scientific campaign.
"""

from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

TAES = ROOT / "publication/Paper_2_Studies_3_4_6/IEEE_Transactions_on_Aerospace_and_Electronic_Systems"
REBUILD = ROOT / "publication/Paper_2_Studies_3_4_6/Post_Rejection_Rebuild"

TAES_ID = "TAES-2026-4182"
UUID = "cd1dfa89-4a24-4451-bdd4-af31ce3367f4"
EXPECTED = {
    "study3": ("S3-K4E-001", 1380),
    "study4": ("S4-MPQ-001", 4608),
    "study6": ("S6-SCTR-001", 420),
}


def fail(message: str) -> None:
    print(f"[FAIL] {message}", file=sys.stderr)
    raise SystemExit(1)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def load_json(path: Path) -> dict:
    if not path.is_file():
        fail(f"missing JSON: {path.relative_to(ROOT)}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        fail(f"invalid JSON {path.relative_to(ROOT)}: {exc}")


def load_csv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        fail(f"missing CSV: {path.relative_to(ROOT)}")
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def check_decision_and_status() -> None:
    decision = TAES / "TAES_EDITORIAL_DECISION_2026-09-26.md"
    require(decision.is_file(), "missing TAES editorial decision record")
    text = decision.read_text(encoding="utf-8")
    for marker in (
        TAES_ID,
        "2026-09-26",
        "External peer review:** No",
        "TAES_R10_SUBMISSION_PACKAGE=IMMUTABLE_PROVENANCE",
        "NEW_EXPERIMENT_EXECUTION_AUTHORIZED=NO",
    ):
        require(marker in text, f"decision record missing marker: {marker}")

    status = load_json(TAES / "TAES_PACKAGE_STATUS.json")
    require(status.get("manuscript_id") == TAES_ID, "TAES manuscript ID drift")
    require(status.get("research_exchange_submission_uuid") == UUID, "TAES UUID drift")
    require(
        status.get("status") == "REJECTED__EDITORIAL_PRESCREEN__NO_EXTERNAL_REVIEW",
        "TAES current status drift",
    )
    require(status.get("decision_date") == "2026-09-26", "TAES decision date drift")
    require(status.get("external_peer_review") is False, "external peer-review flag drift")
    require(status.get("submitted_package_frozen") is True, "R10 freeze flag drift")
    require(
        status.get("science_status") == "STUDIES_3_4_6_FROZEN_UNCHANGED",
        "Paper-2 frozen-science status drift",
    )

    rebuild = status.get("post_rejection_rebuild", {})
    require(rebuild.get("phase") == "PHASE1", "Paper-2 rebuild phase drift")
    require(rebuild.get("extension_execution_authorized") is False, "extension execution unexpectedly authorized")
    require(rebuild.get("manuscript_rewrite_authorized") is False, "manuscript rewrite unexpectedly authorized")
    require(rebuild.get("venue_lock_authorized") is False, "venue lock unexpectedly authorized")


def check_frozen_foundation() -> None:
    status = load_json(REBUILD / "PAPER2_REBUILD_STATUS.json")
    require(
        status.get("status") == "PHASE1_AUTHORIZED__DESIGN_AND_FORMAL_ANALYSIS_ONLY__NO_NEW_EXECUTION",
        "Phase-1 rebuild status drift",
    )
    require(status.get("next_gate") == "AUTHOR_REVIEW_OF_PHASE1_PACKAGE_BEFORE_SOURCE_FREEZE_OR_IMPLEMENTATION", "Phase-1 next gate drift")

    foundation = {
        row["experiment_id"]: (row["population"], row["mutable"])
        for row in status.get("frozen_foundation", [])
    }
    for _, (experiment_id, population) in EXPECTED.items():
        require(experiment_id in foundation, f"missing frozen foundation {experiment_id}")
        actual_population, mutable = foundation[experiment_id]
        require(actual_population == population, f"{experiment_id} population drift")
        require(mutable is False, f"{experiment_id} unexpectedly mutable")

    phase1 = status.get("phase1", {})
    for key in (
        "manuscript_rewrite_authorized",
        "new_venue_lock_authorized",
        "new_extension_implementation_authorized",
        "new_extension_execution_authorized",
    ):
        require(phase1.get(key) is False, f"Phase-1 gate unexpectedly open: {key}")

    nonoverlap = status.get("nonoverlap", {})
    require(nonoverlap.get("pooling_allowed") is False, "Paper-2 pooling unexpectedly allowed")
    excluded = set(nonoverlap.get("excluded_as_new_paper2_evidence", []))
    require(
        excluded == {"Study 1", "Study 2", "Study 5", "Study 7", "Study 7E", "Study 8", "Study 8E", "Study 9"},
        "Paper-2 non-overlap exclusion set drift",
    )


def check_study3_derivation() -> None:
    protocol = load_json(ROOT / "study3/STUDY3_PROTOCOL.json")
    require(protocol.get("experiment_id") == "S3-K4E-001", "Study-3 experiment identity drift")
    require(protocol.get("evidence_valid_for_seconds") == 5, "Study-3 freshness lifetime drift")

    rows = load_csv(ROOT / "study3/results/canonical/cell_summary.csv")
    by_id = {row["cell_id"]: row for row in rows}

    v0 = by_id["K4_V0_NONE_S2_B0_FAIL_CLOSED"]
    require(int(v0["trajectories_with_any_unsafe_qualification"]) == 3, "Study-3 V0/K4 cache count drift")
    require(
        abs(float(v0["mean_unsafe_qualified_exposure_s"]) - (3 * 5 / 46)) < 1e-12,
        "Study-3 V0/K4 cache exposure derivation mismatch",
    )

    for policy in ("S2_B0_FAIL_CLOSED", "S2_S1_EVIDENCE_AWARE"):
        row = by_id[f"K4_V5_PERSISTENT_{policy}"]
        require(int(row["trajectories_with_any_unsafe_qualification"]) == 46, f"Study-3 persistent V5 {policy} trajectory count drift")
        require(int(row["trajectories_with_v5_affected_unsafe_qualification"]) == 46, f"Study-3 persistent V5 {policy} origin count drift")

    b2 = by_id["K4_V5_PERSISTENT_S2_B2_RISK_THRESHOLD"]
    require(int(b2["trajectories_with_any_unsafe_qualification"]) == 0, "Study-3 B2 persistent-V5 boundary drift")


def check_study4_derivation() -> None:
    protocol = load_json(ROOT / "study4/STUDY4_PROTOCOL.json")
    require(protocol.get("experiment_id") == "S4-MPQ-001", "Study-4 experiment identity drift")
    n = int(protocol["producer_count"])
    sizes = sorted((len(v) for v in protocol["provenance_domains"].values()), reverse=True)
    rows = load_csv(ROOT / "study4/results/canonical/thresholds.csv")
    require(len(rows) == 36, f"Study-4 threshold row count drift: {len(rows)}")

    def largest_capacity(k: int) -> int:
        return sum(sizes[:k]) if k > 0 else 0

    mismatches: list[str] = []
    for row in rows:
        match = re.fullmatch(r"Q(\d+)_D(\d+)", row["rule_id"])
        require(match is not None, f"Study-4 malformed rule id: {row['rule_id']}")
        q, d = map(int, match.groups())
        if row["block"] == "SAFETY":
            first = q
            systematic = max(q, largest_capacity(d - 1) + 1)
        elif row["block"] == "AVAILABILITY":
            first = min(n - q + 1, n - largest_capacity(d - 1))
            systematic = n - q + 1
        else:
            fail(f"Study-4 unexpected block: {row['block']}")

        actual = (int(row["first_failure_count"]), int(row["systematic_failure_count"]))
        expected = (first, systematic)
        if actual != expected:
            mismatches.append(f"{row['rule_id']}:{row['block']} actual={actual} expected={expected}")

    require(not mismatches, "Study-4 closed-form mismatch: " + "; ".join(mismatches))


def check_study6_derivation() -> None:
    protocol = load_json(ROOT / "study6/STUDY6_PROTOCOL.json")
    require(protocol.get("experiment_id") == "S6-SCTR-001", "Study-6 experiment identity drift")
    states = protocol["baseline_states"]
    signals = protocol["assurance_signals"]

    clean = states["CLEAN_APPROVED"]
    bad = states["APPROVED_BAD_SOURCE"]
    require(clean["objective_baseline_correct"] is True, "Study-6 clean correctness drift")
    require(bad["objective_baseline_correct"] is False, "Study-6 bad-source correctness drift")
    require(all(clean[s] is True and bad[s] is True for s in signals), "Study-6 observational equivalence drift")

    rows = load_csv(ROOT / "study6/results/CANONICAL_GATE_SUMMARY.csv")
    require(len(rows) == 6, f"Study-6 gate summary row count drift: {len(rows)}")
    for row in rows:
        required = int(row["required_signal_count"])
        expected_loss = 2 ** len(signals) - 2 ** (len(signals) - required)
        require(
            int(row["benign_loss_subset_count"]) == expected_loss,
            f"Study-6 benign-loss formula mismatch for {row['gate_id']}",
        )
        require(
            "APPROVED_BAD_SOURCE" in row["unsafe_qualified_states"].split(";"),
            f"Study-6 approved-bad-source residual missing for {row['gate_id']}",
        )


def check_design_only_extension_state() -> None:
    status = load_json(REBUILD / "PAPER2_REBUILD_STATUS.json")
    states = {row["experiment_id"]: row["state"] for row in status["candidate_extensions"]}
    require(
        states["S3X-ETA-001"] == "CONDITIONAL_GO_FOR_SOURCE_SCREENING_ONLY__EXECUTION_NOT_AUTHORIZED",
        "S3X state drift",
    )
    require(
        states["S4X-JCU-001"] == "HOLD__NOT_CURRENTLY_JUSTIFIED__EXECUTION_NOT_AUTHORIZED",
        "S4X state drift",
    )
    require(
        states["S6X-EAP-001"] == "CONDITIONAL_GO_FOR_ENVIRONMENT_AND_INVARIANT_DESIGN_ONLY__EXECUTION_NOT_AUTHORIZED",
        "S6X state drift",
    )

    for name in (
        "S3X_ETA_PROTOCOL_DRAFT_R1_2026-09-26.md",
        "S4X_JCU_PROTOCOL_DRAFT_R1_2026-09-26.md",
        "S6X_EAP_PROTOCOL_DRAFT_R1_2026-09-26.md",
        "PAPER2_NONOVERLAP_GATE_2026-09-26.md",
        "PHASE1_ADVERSARIAL_PROTOCOL_REVIEW_R1_2026-09-26.md",
    ):
        require((REBUILD / name).is_file(), f"missing Phase-1 design record: {name}")


def main() -> int:
    check_decision_and_status()
    check_frozen_foundation()
    check_study3_derivation()
    check_study4_derivation()
    check_study6_derivation()
    check_design_only_extension_state()
    print("paper2_post_rejection_phase1_audit=PASS")
    print("paper2_taes_decision_state=PASS")
    print("paper2_frozen_foundation=PASS")
    print("paper2_study3_derivation=PASS")
    print("paper2_study4_closed_form=PASS_36_OF_36")
    print("paper2_study6_observability=PASS")
    print("paper2_extension_execution_authorized=NO")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
