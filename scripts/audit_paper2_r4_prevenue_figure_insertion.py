#!/usr/bin/env python3
"""Paper 2 R4 figure-insertion/prevenue-only fail-closed audit. No science execution."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
D=ROOT/"publication/Paper_2_Studies_3_4_6/Post_Rejection_Rebuild"
BASE="d3cf8af3def805db7fda97dbda457b7c21f80c84"
R3=D/"PAPER2_REBUILD_MANUSCRIPT_R3_2026-09-30.md"
R4=D/"PAPER2_REBUILD_MANUSCRIPT_R4_2026-10-01.md"
FIG=D/"figures/PAPER2_R2_FIGURE1_RESIDUAL_BOUNDARIES.svg"
INSERT=D/"PAPER2_R4_FIGURE1_INSERTION_2026-10-01.md"
VENUE=D/"PAPER2_R4_LIVE_PREVENUE_SCOPE_SCREEN_2026-10-01.md"
STATUS=D/"PAPER2_R4_PREVENUE_STATUS.json"
WORKFLOW=ROOT/".github/workflows/validate-research-configs.yml"

BOUND={
"publication/Paper_2_Studies_3_4_6/Post_Rejection_Rebuild/PAPER2_REBUILD_MANUSCRIPT_R3_2026-09-30.md":"2182ea02634854da92d6d6049e6fdd269b11bac8",
"publication/Paper_2_Studies_3_4_6/Post_Rejection_Rebuild/PAPER2_REBUILD_MANUSCRIPT_R2_2026-09-28.md":"9e3f345a3a16102c39bb978f4e522c261e80cfb4",
"publication/Paper_2_Studies_3_4_6/Post_Rejection_Rebuild/figures/PAPER2_R2_FIGURE1_RESIDUAL_BOUNDARIES.svg":"5f68ac156b4e27c7bfd99e006623196c250c94a1",
"study6x/S6X_CANONICAL_RESULT_FREEZE_004.json":"2e6b213b994062fd108e4b8435d9c0c36d93fdc0",
"study6x/S6X_INTERPRETATION_CLAIM_USE_001.json":"a0786f278d5315b438ad6416a91be8cb16262b83",
"publication/Paper_2_Studies_3_4_6/Post_Rejection_Rebuild/PAPER2_REBUILD_MANUSCRIPT_R4_2026-10-01.md":"069e319864b1f5c1ee201b31872e68572fea1923",
"publication/Paper_2_Studies_3_4_6/Post_Rejection_Rebuild/PAPER2_R4_FIGURE1_INSERTION_2026-10-01.md":"63a67b805350e1766cbb9dbcd961bb84290bb63e",
"publication/Paper_2_Studies_3_4_6/Post_Rejection_Rebuild/PAPER2_R4_LIVE_PREVENUE_SCOPE_SCREEN_2026-10-01.md":"75548203fc0bd0bb5d5666b72f9805b64a995915",
"publication/Paper_2_Studies_3_4_6/Post_Rejection_Rebuild/PAPER2_R4_PREVENUE_STATUS.json":"4326eef05fc81d2322519a4671e0941129e55e15",
}

def req(ok,msg):
    if not ok: raise SystemExit("FAIL: "+msg)

def blob(rel):
    return subprocess.check_output(["git","hash-object",rel],cwd=ROOT,text=True).strip()

for rel,sha in BOUND.items():
    req((ROOT/rel).is_file(),"missing: "+rel)
    req(blob(rel)==sha,"bound blob drift: "+rel)
req(hashlib.sha256(FIG.read_bytes()).hexdigest()=="adfdfaf833c8624bb405209be22ef6b2f002cdec53f081ce097f67e728eedffc","canonical SVG SHA-256 drift")

r3=R3.read_text(encoding="utf-8")
r4=R4.read_text(encoding="utf-8")
ins=INSERT.read_text(encoding="utf-8")
req(ins.count("## Exact manuscript insertion\n")==1,"figure insertion authority absent/ambiguous")
fig_text=ins.split("## Exact manuscript insertion\n",1)[1]
anchor="The arithmetic sum of these populations is not a meaningful sample size. Study 3 uses trajectories, S3X uses interval-policy-evidence-arm cases, Study 4 uses rule-by-subset observations, and Study 6 uses artifact-state and assurance-unavailability observations. No pooled N, pooled rate, pooled confidence interval, or combined policy score is defined."
req(r3.count(anchor)==1,"R3 insertion anchor ambiguous")
old_header="> **Post-rejection rebuild R2 — venue-neutral manuscript draft.**"
new_header="> **Post-rejection rebuild R4 — pre-venue figure-integrated manuscript candidate (not a submitted package).**"
old_note="> R3 preserves R2 and the historical submitted TAES R10 package as immutable prior versions while integrating the author-approved S6X frozen-result claim-use package."
new_note="> R4 preserves R3, R2, and the historical submitted TAES R10 package as immutable prior versions; it inserts the unchanged, visually audited Figure 1 into the author-approved S6X-integrated manuscript."
req(r3.count(old_header)==1 and r3.count(old_note)==1,"R3 header/note anchor drift")
rebuild=r3.replace(old_header,new_header).replace(old_note,new_note).replace(anchor,anchor+"\n"+fig_text)
req(rebuild==r4,"R4 diff exceeds header/version update + exact Figure-1 insertion")

req(r4.count("![Figure 1.")==1,"Figure 1 markdown embedding count drift")
req(r4.count("**Figure 1. Residual trust boundaries")==1,"Figure 1 caption count drift")
callout=r4.find("Figure 1 summarizes the three residual")
image=r4.find("![Figure 1.")
caption=r4.find("**Figure 1. Residual trust")
sec4=r4.find("## IV. RQ1")
req(0<callout<image<caption<sec4,"Figure placement/citation/order drift")
req(r4.count("### Table V. S6X executable validation")==1,"Table V not preserved")
for boundary in ("not an external empirical replication of Study 6","research-only objective adjudication","does not pool S6X with Study 6","does not establish a vulnerability in cFS or Limit Checker"):
    req(boundary in r4,"R3/S6X claim firewall absent: "+boundary)
req((r4.count("### Table I.")==1 and r4.count("### Table II.")==1 and r4.count("### Table III.")==1 and r4.count("### Table IV.")==1 and r4.count("### Table V.")==1),"Table numbering changed")
req(7000 <= len(r4.split()) <= 9000,"R4 word-count sanity envelope drift")

v=VENUE.read_text(encoding="utf-8")
for required in ("Journal of Information Security and Applications","IEEE Systems Journal","Aerospace (MDPI)","TAES prescreening concerns","VENUE_NOT_LOCKED","NO_SUBMISSION","not a selection or acceptance forecast"):
    req(required.lower() in v.lower(),"venue screen missing: "+required)
for url in (
"https://shop.elsevier.com/journals/journal-of-information-security-and-applications/2214-2126",
"https://ieeesystemscouncil.org/publication/ieee-systems-journal/instructions-for-authors",
"https://www.mdpi.com/journal/aerospace/about"):
    req(url in v,"source URL absent: "+url)

st=json.loads(STATUS.read_text(encoding="utf-8"))
req(st["record_id"]=="PAPER2-PREVENUE-R4-FIGURE1-INSERTION-AND-LIVE-VENUE-SCREEN-001","status ID drift")
req(st["base_main"]==BASE and st["preceding_ci"]["conclusion"]=="success","authoritative base/CI drift")
req(st["candidate"]["manuscript_r4_git_blob_sha1"]=="069e319864b1f5c1ee201b31872e68572fea1923","status R4 blob drift")
req(st["candidate"]["word_like_count"]==7863,"status word count drift")
req(st["candidate"]["figure1_original_svg_preserved"] is True and st["candidate"]["table_v_preserved"] is True,"display protection weakened")
req(st["candidate"]["s3x_study3_pooling"] is False and st["candidate"]["s6x_study6_pooling"] is False and st["candidate"]["s6x_as_fourth_figure_panel"] is False,"science boundary weakened")
for name,val in st["publication_boundaries"].items():
    req(val is False,"prohibited publication action opened: "+name)
req(st["companion_records"]["exact_figure_insertion_git_blob_sha1"]=="63a67b805350e1766cbb9dbcd961bb84290bb63e","insertion blob drift")
req(st["companion_records"]["live_venue_screen_git_blob_sha1"]=="75548203fc0bd0bb5d5666b72f9805b64a995915","venue screen blob drift")

allowed={
".github/workflows/validate-research-configs.yml",
"scripts/audit_paper2_r4_prevenue_figure_insertion.py",
"publication/Paper_2_Studies_3_4_6/Post_Rejection_Rebuild/PAPER2_REBUILD_MANUSCRIPT_R4_2026-10-01.md",
"publication/Paper_2_Studies_3_4_6/Post_Rejection_Rebuild/PAPER2_R4_FIGURE1_INSERTION_2026-10-01.md",
"publication/Paper_2_Studies_3_4_6/Post_Rejection_Rebuild/PAPER2_R4_LIVE_PREVENUE_SCOPE_SCREEN_2026-10-01.md",
"publication/Paper_2_Studies_3_4_6/Post_Rejection_Rebuild/PAPER2_R4_PREVENUE_STATUS.json",
"publication/Paper_2_Studies_3_4_6/Post_Rejection_Rebuild/PAPER2_R5_PUBLICATION_READINESS_AND_ABSTRACT_CANDIDATE_2026-10-08.md",
"publication/Paper_2_Studies_3_4_6/Post_Rejection_Rebuild/PAPER2_CEAS_MANUSCRIPT_R5_2026-10-09.md",
"publication/Paper_2_Studies_3_4_6/Post_Rejection_Rebuild/PAPER2_CEAS_TITLE_PAGE_DRAFT_2026-10-09.md",
"publication/Paper_2_Studies_3_4_6/Post_Rejection_Rebuild/PAPER2_CEAS_COVER_LETTER_DRAFT_2026-10-09.md",
"publication/Paper_2_Studies_3_4_6/Post_Rejection_Rebuild/PAPER2_CEAS_JOURNAL_COMPLIANCE_GATE_2026-10-09.json",
"publication/Paper_2_Studies_3_4_6/Post_Rejection_Rebuild/PAPER2_CEAS_SUBMISSION_READINESS_2026-10-09.md",
"scripts/audit_paper2_ceas_r5.py",
"scripts/build_paper2_ceas_package.py",
"publication/Paper_2_Studies_3_4_6/Post_Rejection_Rebuild/PAPER2_CEAS_REFERENCE_INTEGRITY_SCREEN_2026-10-09.json",
"publication/Paper_2_Studies_3_4_6/Post_Rejection_Rebuild/PAPER2_CEAS_REFERENCE_INTEGRITY_SCREEN_2026-10-09.md",
}
changed=set(subprocess.check_output(["git","diff","--name-only",f"{BASE}...HEAD"],cwd=ROOT,text=True).splitlines())
req(changed==allowed,"branch diff whitelist drift: "+str(sorted(changed^allowed)))
r5_text=(D/"PAPER2_R5_PUBLICATION_READINESS_AND_ABSTRACT_CANDIDATE_2026-10-08.md").read_text(encoding="utf-8")
for token in (
    "no changes to the authoritative R4 source",
    "P2X is not an R4 study population",
    "No venue lock",
    "no submission",
    "R5_PREVENUE_READINESS_REVIEW_PREPARED__NO_VENUE_LOCK__NO_SUBMISSION"):
    req(token.lower() in r5_text.lower(), "R5 scope missing: "+token)
abstract=r5_text.split("## Condensed abstract candidate — editorial draft only",1)[1].split("**Draft abstract whitespace-word count:**",1)[0]
req(150<=len(abstract.split())<=250,"R5 abstract length out of advisory envelope")
req("source manuscript" not in r5_text or "preserve" in r5_text,
    "R5 science source disposition unexpected")
req("python scripts/audit_paper2_r4_prevenue_figure_insertion.py" in WORKFLOW.read_text(),"missing R4 CI hook")
ceas=subprocess.run(["python3",str(ROOT/"scripts/audit_paper2_ceas_r5.py")],cwd=ROOT,
    capture_output=True,text=True)
req(ceas.returncode==0 and "PAPER2_CEAS_R5_EDITORIAL_STATIC=PASS" in ceas.stdout,
    "CEAS R5 controlled-derivative audit: "+ceas.stdout+ceas.stderr)
package=subprocess.run(["python3",str(ROOT/"scripts/build_paper2_ceas_package.py"),"--check"],
    cwd=ROOT,capture_output=True,text=True)
req(package.returncode==0 and "CEAS_PACKAGE_RENDER=NOT_EXECUTED" in package.stdout,
    "CEAS source-only build check: "+package.stdout+package.stderr)
print("paper2_r4_prevenue_figure_insertion_audit=PASS")
print("r3_blob_preserved=YES")
print("figure1_svg_sha256_preserved=YES")
print("figure1_callout_caption_order=PASS")
print("table_i_to_v_preserved=YES")
print("r4_only_authorized_insert_and_version_change=YES")
print("venue_shortlist_prepared=YES")
print("venue_lock=NO")
print("publisher_specific_derivative=NO")
print("submission=NO")
