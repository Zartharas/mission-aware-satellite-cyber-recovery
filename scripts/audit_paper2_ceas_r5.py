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
    ceas_figure=D/"figures/PAPER2_CEAS_FIG1_TRUST_BOUNDARIES_R5.svg"
    original_figure=D/"figures/PAPER2_R2_FIGURE1_RESIDUAL_BOUNDARIES.svg"
    chk(ceas_figure.is_file() and original_figure.is_file(),"ceas_or_legacy_figure_missing")
    chk(hashlib.sha256(ceas_figure.read_bytes()).hexdigest()=="b83c9614879a66184495f3905a5d3866eb8cbdffd7e1ee6065f8eaf49748e119" and
        hashlib.sha256(original_figure.read_bytes()).hexdigest()=="adfdfaf833c8624bb405209be22ef6b2f002cdec53f081ce097f67e728eedffc",
        "approved_ceas_figure_or_immutable_legacy_figure_drift")
    svg=ceas_figure.read_text(encoding="utf-8")
    for token in ("(a)  Study 3", "(b)  Study 4", "(c)  Study 6",
                  "V5 can qualify", "S3X:", "S6X:", "APPROVED_BAD_SOURCE",
                  "timing proxies, not measured RF outages", "not visible to the six-signal gate"):
        chk(token in svg, "approved_figure_scientific_label_missing:"+token)
    chk("P2X" not in svg and "S4X" not in svg and target.count("![](figures/PAPER2_R2_FIGURE1_RESIDUAL_BOUNDARIES.svg)")==0,
        "prohibited_extension_or_legacy_figure_reintroduced")
    ab=target.split("## Abstract\n\n",1)[1].split("**Keywords:**",1)[0].strip()
    chk(150<=len(ab.split())<=250 and len(ab.split())==228,"abstract_length_or_drift")
    kw=target.split("**Keywords:**",1)[1].split("\n",1)[0]
    chk(len([x for x in kw.split(";") if x.strip()])==6,"keywords_not_six")
    fig_caption=next((x for x in target.splitlines() if x.startswith("**Fig. 1** ")),None)
    chk(target.count("**Fig. 1**")==1 and target.count("![](figures/PAPER2_CEAS_FIG1_TRUST_BOUNDARIES_R5.svg)")==1 and
        fig_caption is not None and not fig_caption.endswith("."),
        "figure_caption_or_embedding")
    chk(not any(x in ab for x in ("S3X","S6X"," cFS"," ESA ")),
        "undefined_abstract_abbreviation")
    chk(all(target.count("**Table "+str(n)+"**")==1 for n in range(1,6)),
        "not_five_arabic_tables")
    chk("decision boundary.\n\n### 2.2 Evidence Freshness and Semantic Trust" in target,
        "heading_2_2_separator_missing")
    chk("G0–G5 abbreviate the full gate identifiers" in target,
        "table4_full_gate_legend_missing")
    chk(all(("#" not in line or not re.match(r"^## [IVX]+\\.",line))
            for line in target.splitlines()),"old_roman_headings")
    chk(all("[{}]".format(i) in target for i in range(1,20)) and
        [int(x) for x in re.findall(r"^\[(\d+)\]\s", target, re.MULTILINE)] == list(range(1,20)),
        "reference_number_missing_or_reference_count_not_19")
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
    refscreen=json.loads((D/"PAPER2_CEAS_REFERENCE_INTEGRITY_SCREEN_2026-10-09.json").read_text(encoding="utf-8"))
    chk(refscreen["total"]==20 and
        refscreen["automated"]["matched"]==14 and
        refscreen["automated"]["mismatch"]==1 and
        refscreen["automated"]["not_found"]==5 and
        refscreen["automated"]["retracted_reported"]==0 and
        refscreen["full_manual_reference_qa"] is False and
        "draft-ietf-rats-multi-verifier" not in target and
        "https://theupdateframework.github.io/specification/v1.0.36/" in target,
        "CEAS_REFERENCE_SCREEN_FIREWALL")
    deliverables=gate["deliverables"]
    figure_record=gate.get("figure1_ceas_derivative",{})
    fifth=gate.get("visual_qa_history", [])[-1:]
    chk(figure_record.get("svg_sha256")=="b83c9614879a66184495f3905a5d3866eb8cbdffd7e1ee6065f8eaf49748e119" and
        figure_record.get("svg_git_blob_sha1")=="728fa602ee1b73a363ed56173b695f778cd0b89d" and
        figure_record.get("path")=="publication/Paper_2_Studies_3_4_6/Post_Rejection_Rebuild/figures/PAPER2_CEAS_FIG1_TRUST_BOUNDARIES_R5.svg" and
        figure_record.get("author_approved_draft_integration") is True and
        figure_record.get("full_source_docx_pdf_visual_qa")=="PENDING" and
        deliverables["figure_visual_qa"]=="APPROVED_CEAS_DERIVATIVE__FULL_SOURCE_RENDER_QA_PENDING" and
        deliverables["manuscript_docx"]=="HISTORICAL_FIFTH_PREVIEW_VALIDATED__FRESH_RENDER_PENDING" and
        deliverables["manuscript_pdf"]=="HISTORICAL_FIFTH_PREVIEW_VALIDATED__FRESH_RENDER_PENDING" and
        deliverables["five_tables_visual_qa"]=="HISTORICAL_FIFTH_PREVIEW_PASS__FRESH_RENDER_PENDING" and
        len(fifth)==1 and fifth[0]["source_head"]=="0fa0ee59af9e2b05aafc42c23795c2539f5af188" and
        fifth[0]["verdict"]=="TABLE_PAGINATION_PASS__OVERALL_SUBMISSION_HOLD",
        "ceas_figure_integration_or_historical_preview_guard")
    chk(gate["article_type"]=="Original Research Article" and
        gate["manuscript_r4_blob_immutable"]==hash_obj and
        (not_rendered or verified_draft) and
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
