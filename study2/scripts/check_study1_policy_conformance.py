#!/usr/bin/env python3
from __future__ import annotations

from copy import deepcopy

from mission_recovery.events import materialize_event
from mission_recovery.policies import evaluate_policy
from study2_security.study1_baseline import expected_p7_decision

EVENTS = ("E1", "E2", "E3", "E4")
MISSIONS = ("M0", "M2", "M4")
CONTACTS = ("C0", "C1")
EVIDENCE = ("T0", "T1")


def main() -> int:
    cases = 0
    for event_id in EVENTS:
        for mission_state in MISSIONS:
            for contact_condition in CONTACTS:
                for evidence_condition in EVIDENCE:
                    event = materialize_event(
                        event_id,
                        mission_state=mission_state,
                        contact_condition=contact_condition,
                        evidence_condition=evidence_condition,
                        seed=0,
                    )
                    expected = expected_p7_decision(
                        event_id,
                        mission_state,
                        contact_condition,
                        evidence_condition,
                    )
                    decision = evaluate_policy("P7", event)

                    assert decision["evidence_insufficient"] is (
                        not expected["evidence_sufficient"]
                    )
                    assert decision["delegated_policy_id"] == expected["delegated_policy_id"]
                    assert decision["selected_action"] == expected["selected_action"]
                    assert decision["decision_basis"] == expected["decision_basis"]
                    assert decision["oracle_ground_truth_read"] is False

                    altered = deepcopy(event)
                    altered["ground_truth"] = {
                        "study2_conformance_mutation": "must_not_affect_policy"
                    }
                    assert evaluate_policy("P7", altered) == decision
                    cases += 1

    if cases != 48:
        raise AssertionError(f"expected 48 Study-1 conformance cases; got {cases}")
    print(f"study1_p7_conformance_cases={cases}")
    print("study1_oracle_isolation=PASS")
    print("study1_p7_conformance=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
