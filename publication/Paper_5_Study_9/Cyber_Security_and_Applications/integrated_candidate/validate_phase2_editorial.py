#!/usr/bin/env python3
"""Phase 2 manuscript-only traceability checks against already archived sources."""
from __future__ import annotations
from collections import Counter
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
S9 = ROOT / "study9/results/S9-RTSI-001_CANONICAL_RUN_20260914/mapping_matrix.json"
S10 = HERE / "study10_derived/S10_G4_TierA_32Slot_PublishedSchema.json"
APPENDIX = HERE / "PHASE2_FIELD_LEVEL_EVIDENCE_APPENDIX.tex"
MANUSCRIPT = HERE / "CSA_S9_S10_INTEGRATED_CANDIDATE.tex"
LEDGER = HERE / "PHASE2_RQ_EVIDENCE_AND_ADVERSARIAL_LEDGER_20261123.md"

def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))

def validate():
    s9 = load_json(S9)
    s10 = load_json(S10)["adjudications"]
    appendix = APPENDIX.read_text(encoding="utf-8")
    manuscript = MANUSCRIPT.read_text(encoding="utf-8")
    ledger = LEDGER.read_text(encoding="utf-8")
    assert len(s9) == 24 and len(s10) == 32
    assert Counter(x["mapping_class"] for x in s9) == {"AMBIGUOUS": 14, "ABSENT": 10}
    assert Counter(x["mapping_class"] for x in s10) == {"AMBIGUOUS": 14, "ABSENT": 18}
    for prefix, data in (("S9", s9), ("S10", s10)):
        for row in data:
            marker = f"% P2MAP {prefix} {row['dataset_id']} {row['recovery_state_variable']} {row['mapping_class']}"
            if prefix == "S10":
                marker += f" {row['evidence_visibility_role']}"
            assert appendix.count(marker + "\n") == 1, marker
            section = appendix.split(marker + "\n", 1)[1].split("\n% P2MAP ", 1)[0]
            expected_class = "A" if row["mapping_class"] == "AMBIGUOUS" else "X"
            if prefix == "S10":
                role = {"EXPERIMENT_METADATA_ONLY": "M",
                        "OFFLINE_GROUND_TRUTH_ONLY": "G",
                        "DOCUMENTATION_ONLY": "D"}[row["evidence_visibility_role"]]
                expected_class += "/" + role
            assert " & " + expected_class + " & " in section.splitlines()[0], marker
            for key in ("native_field_names", "excluded_fields", "excluded_as_substitutes"):
                for field in row.get(key, []):
                    assert r"\url{" + field + "}" in section, (marker, field)
    assert len(re.findall(r"^% P2MAP S9 ", appendix, re.M)) == 24
    assert len(re.findall(r"^% P2MAP S10 ", appendix, re.M)) == 32
    assert r"\label{tab:phase2rq}" in manuscript
    assert r"\label{fig:phase2gates}" in manuscript
    supplement = (HERE / "PHASE2_FIELD_LEVEL_EVIDENCE_SUPPLEMENT.tex").read_text(encoding="utf-8")
    assert r"\input{PHASE2_FIELD_LEVEL_EVIDENCE_APPENDIX.tex}" in supplement
    assert r"\input{PHASE2_FIELD_LEVEL_EVIDENCE_APPENDIX.tex}" not in manuscript
    assert "Supplementary Appendix S1" in manuscript
    assert r"\label{app:fieldledger}" in appendix
    for rq in ("RQ1", "RQ2", "RQ3", "RQ4", "RQ-E1", "RQ-E2", "RQ-E3", "RQ-E4", "RQ-E5"):
        assert manuscript.count(r"\texttt{" + rq + "} &") == 1, rq
        assert "| " + rq + " |" in ledger, rq
    assert "Hack-A-Sat" in manuscript and "secondary, unpooled competition context" in manuscript
    assert "G2-frozen" in manuscript and "the completed answer addresses the frozen primary comparison" in manuscript
    assert "original semantic mapping-stability aspect of RQ-E3 remains unanswered" in manuscript
    assert "OpenAI ChatGPT (GPT-6, revision on 23 November 2026)" in manuscript
    assert "the exact model used for its earlier draft was not recorded" in manuscript
    assert "The empirical contribution is the auditable source-to-predicate classification" in manuscript
    assert "not an independent replay of original source inspection" in manuscript
    refs = (HERE / "references.bib").read_text(encoding="utf-8")
    for citation in ("im2026ccsds", "ramsey2026stargate", "qasim2026safe", "torstensson2026warrants"):
        assert ("{" + citation + ",") in refs and (r"\cite{" + citation + "}") in manuscript, citation
    assert "no change of a recovery-state mapping class is established" in manuscript
    assert "16/16" in manuscript and "1,024" in manuscript
    assert "unconstrained Boolean completion space" in manuscript
    assert "physical realizability" in manuscript
    assert "24 source-to-predicate judgments" in manuscript
    assert "sole-author, AI-assisted workflow" in manuscript
    assert "Draft declaration pending sole-author confirmation" in manuscript
    assert "tahir2025benchmark" in refs and r"\cite{tahir2025benchmark}" in manuscript
    assert "preregistered public space-cyber datasets" not in manuscript
    assert "04317102b87eb63312ba4e1599f87a3971858d03" in manuscript
    assert "8ed6a2b16233b86bf91672f6f15605dcf906c5eb" in manuscript
    print("PAPER5_PHASE2_EDITORIAL_FIELD_TRACEABILITY_PASS: 9 RQs, 24 S9 + 32 S10 mappings")

if __name__ == "__main__":
    validate()
