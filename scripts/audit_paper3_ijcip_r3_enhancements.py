#!/usr/bin/env python3
"""Fail-closed read-only R3 science/figure/portfolio publication gate."""
import hashlib
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AREA = ROOT / "publication/Paper_3_Study_7/Rebuilt_Study7_7E"
R3 = AREA / "IJCIP"
DATA = ROOT / "study7e/results/S7E-AERC-HELDOUT-EXEC-001"
POLICIES = ("D0_BASE", "L0_BASE", "D1_CORROBORATED", "L1_CORROBORATED")

def verify(ok, message):
    if not ok:
        raise AssertionError(message)

def data(path):
    return json.loads(path.read_text(encoding="utf-8"))

def main():
    manuscript = (R3 / "PAPER3_IJCIP_MANUSCRIPT_R3.md").read_text(encoding="utf-8")
    guard = (AREA / "PAPER3_IJCIP_R3_REVIEWER_DEFENSE_2026-10-20.md").read_text(encoding="utf-8")
    s7 = data(ROOT / "study7/results/RESULTS_FREEZE.json")
    freeze = data(ROOT / "study7e/RESULT_FREEZE_STATE.json")
    checkpoint = data(DATA / "result_checkpoint.json")
    counts_file = DATA / "exact_endpoint_counts.json"
    counts = data(counts_file)
    verify(s7["population"]["total"] == 1033 and s7["status"] == "CANONICAL_RESULTS_FROZEN", "S7 freeze mismatch")
    verify(freeze["result_freeze_active"] and freeze["scientific_execution_sealed"], "S7E freeze inactive")
    verify(freeze["scientific_execution_of_record"] == "S7E-AERC-HELDOUT-EXEC-001", "wrong scientific execution")
    verify(freeze["frozen_population"] == {"E1":84,"E2":104,"C0":8,"total_scenarios":196,"total_policy_decisions":784}, "frozen population drift")
    verify(checkpoint["validity"]["invalid_scenarios"] == 0 and checkpoint["validity"]["audit_mismatches"] == 0, "invalid/audit mismatch")
    verify(counts["population"] == {"decisions":784,"scenarios":196}, "result population drift")
    digest = hashlib.sha256(counts_file.read_bytes()).hexdigest()
    verify(digest == checkpoint["artifact_file_sha256"]["exact_endpoint_counts.json"], "frozen counts artifact SHA256 drift")
    table = {}
    # The same policy identifiers also appear in the topology-controlled table.
    # Select only Section 4.2; any ambiguity in its aggregate table fails closed.
    aggregate_section = manuscript.split("### 4.2 Study 7E: aggregate held-out outcomes", 1)[1].split(
        "### 4.3 Held-out block results", 1
    )[0]
    for line in aggregate_section.splitlines():
        if re.match(r"^\|\s*(D0_BASE|L0_BASE|D1_CORROBORATED|L1_CORROBORATED)\s*\|", line):
            parts = [p.strip() for p in line.strip().strip("|").split("|")]
            verify(len(parts) == 6 and parts[0] not in table, "ambiguous overall table")
            table[parts[0]] = tuple(map(int, parts[1:]))
    verify(set(table) == set(POLICIES), "R3 policy table missing")
    for p in POLICIES:
        r = counts["overall"][p]
        expected = (r["objective_decision_error"],r["unsafe_proceed"],r["false_conservative_hold"],r["actions"]["ENTER_RECOVERY_GATE"],r["actions"]["HOLD"])
        frozen = checkpoint["endpoint_counts"]["overall"][p]
        cp = (frozen["objective_decision_error"],frozen["unsafe_proceed"],frozen["false_conservative_hold"],frozen["ENTER_RECOVERY_GATE"],frozen["HOLD"])
        verify(table[p] == expected == cp, "R3/frozen count mismatch: " + p)
        verify(expected[0] == expected[1]+expected[2] and expected[3]+expected[4] == 196, "count invariant failed")
        for block, size in (("E1",84),("E2",104),("C0",8)):
            part = counts["by_block"][block][p]
            verify(part["n"] == size, "block size mismatch")
            if block == "C0":
                verify(part["objective_decision_error"] == 0 and part["unsafe_proceed"] == 0 and part["actions"]["HOLD"] == 8, "C0 null altered")
    for k,n in (("D0_vs_L0",67),("D1_vs_L1",72)):
        verify(checkpoint["paired_disagreement_counts"][k]["ALL"] == n and f"{n} of 196" in manuscript, "paired comparator drift")
    ns = "{http://www.w3.org/2000/svg}"
    fig1 = R3 / "figures/PAPER3_IJCIP_FIG1_ARCHITECTURE.svg"
    fig2 = R3 / "figures/PAPER3_IJCIP_FIG2_ENDPOINTS.svg"
    diagrams = [ET.parse(fig1).getroot(),ET.parse(fig2).getroot()]
    for name,svg in zip((fig1.name,fig2.name),diagrams):
        verify(svg.get("role") == "img" and svg.find(ns+"title") is not None and svg.find(ns+"desc") is not None, "SVG accessibility metadata absent")
        verify("(figures/" + name + ")" in manuscript, "uncited SVG")
    diagram_text = " ".join((e.text or "") for e in diagrams[0].iter())
    for marker in ("Source domain","Key domain","Execution domain","Transport domain","Authority domain","cFS engineering qualification","Frozen Python inference","NEVER supplied"):
        verify(marker in diagram_text, "architecture boundary absent: "+marker)
    bars = {e.get("data-policy"):(int(e.get("data-unsafe")),int(e.get("data-fch"))) for e in diagrams[1].iter(ns+"g") if e.get("data-policy")}
    verify(set(bars) == set(POLICIES), "graphic policy labels drift")
    for p in POLICIES:
        r = counts["overall"][p]
        verify(bars[p] == (r["unsafe_proceed"],r["false_conservative_hold"]), "graphic endpoints drift")
    for marker in ("No combined sample size or pooled error rate is computed","not flight-software-in-the-loop learned inference","F12","C0 no-signal","No Study-7 or Study-7E scientific execution is rerun","Declaration of generative AI and AI-assisted technologies"):
        verify(marker in manuscript, "essential qualification removed: "+marker)
    for marker in ("Paper 1","Paper 2","Paper 4","Paper 5","P2X","NO new scientific observation","NOT GRANTED"):
        verify(marker in guard, "cross-study firewall missing: "+marker)
    print("PAPER3_FROZEN_STUDY7_AND_STUDY7E=PASS")
    print("PAPER3_MANUSCRIPT_ENDPOINTS_AND_FIGURES=PASS")
    print("PAPER3_CROSS_STUDY_FIREWALL=PASS")
    print("PAPER3_IJCIP_R3_ENHANCEMENT_GATE=PASS")

if __name__ == "__main__":
    main()
