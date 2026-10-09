#!/usr/bin/env python3
"""Fail-closed CEAS Paper-2 R5 editorial derivative audit. No scientific execution."""
from __future__ import annotations
import hashlib
import re
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
D=ROOT/"publication/Paper_2_Studies_3_4_6/Post_Rejection_Rebuild"
R4=D/"PAPER2_REBUILD_MANUSCRIPT_R4_2026-10-01.md"
R5=D/"PAPER2_CEAS_MANUSCRIPT_R5_2026-10-09.md"
GUIDE=D/"PAPER2_CEAS_JOURNAL_COMPLIANCE_GATE_2026-10-09.json"
def chk(ok,why):
    if not ok: raise SystemExit("P2_CEAS_R5_HOLD="+why)
def main():
    import json
    source=R4.read_text(encoding="utf-8")
    target=R5.read_text(encoding="utf-8")
    gate=json.loads(GUIDE.read_text(encoding="utf-8"))
    hash_obj=subprocess.check_output(["git","hash-object",str(R4)],cwd=ROOT,text=True).strip()
    chk(hash_obj=="069e319864b1f5c1ee201b31872e68572fea1923","immutable_r4_blob_drift")
    ab=target.split("## Abstract\n\n",1)[1].split("**Keywords:**",1)[0].strip()
    chk(150<=len(ab.split())<=250 and len(ab.split())==228,"abstract_length_or_drift")
    kw=target.split("**Keywords:**",1)[1].split("\n",1)[0]
    chk(len([x for x in kw.split(";") if x.strip()])==6,"keywords_not_six")
    fig_caption=next((x for x in target.splitlines() if x.startswith("**Fig. 1** ")),None)
    chk(target.count("**Fig. 1**")==1 and target.count("![Fig. 1")==1 and
        fig_caption is not None and not fig_caption.endswith("."),
        "figure_caption_or_embedding")
    chk(not any(x in ab for x in ("S3X","S6X"," cFS"," ESA ")),
        "undefined_abstract_abbreviation")
    chk(all(target.count("**Table "+str(n)+"**")==1 for n in range(1,6)),
        "not_five_arabic_tables")
    chk(all(("#" not in line or not re.match(r"^## [IVX]+\\.",line))
            for line in target.splitlines()),"old_roman_headings")
    chk(all("[{}]".format(i) in target for i in range(1,21)),
        "reference_number_missing")
    chk(target.count("## Statements and Declarations")==1 and
        "## AI assistance and author responsibility" in target and
        "## References" in target,"declarations_or_ai_missing")
    for anchor in (
        "1,919 extreme inter-sample intervals",
        "4,608 rule-by-subset observations",
        "two repetitions of 396 observations",
        "eight governed builds",
        "not operational spacecraft recovery",
        "does not pool S6X with Study 6",
    ):
        chk(anchor.lower() in target.lower(),"frozen_scope_missing:"+anchor)
    chk(gate["article_type"]=="Original Research Article" and
        gate["manuscript_r4_blob_immutable"]==hash_obj and
        gate["deliverables"]["manuscript_docx"]=="NOT_RENDERED" and
        gate["deliverables"]["manuscript_pdf"]=="NOT_RENDERED" and
        gate["final_submission_ready"] is False and
        gate["authorization"]["portal_actions"] is False and
        gate["authorization"]["runtime_execution"] is False,
        "submission_or_runtime_scope_open")
    chk("[AUTHOR CONFIRM" in target and "[AUTHOR ACTION REQUIRED" in target,
        "unverified_statements_silently_filled")
    print("PAPER2_CEAS_R5_EDITORIAL_STATIC=PASS")
    print("FROZEN_R4_SOURCE=UNCHANGED")
    print("STUDY3_STUDY4_STUDY6_S3X_S6X=SEPARATE")
    print("CEAS_DOCX_PDF_VISUAL_QA=PENDING")
    print("CEAS_SUBMISSION=NOT_AUTHORIZED")
if __name__=="__main__":main()
