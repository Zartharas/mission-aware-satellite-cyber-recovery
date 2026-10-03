#!/usr/bin/env python3
"""Fail-closed Paper 2 CEAS R1 editorial-only derivation audit. NO scientific execution."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
BASE = "4cd0c30a276b3c5a0494736b93a8d08dc1ed8df4"
P2 = ROOT / "publication/Paper_2_Studies_3_4_6"
R4 = P2 / "Post_Rejection_Rebuild/PAPER2_REBUILD_MANUSCRIPT_R4_2026-10-01.md"
R1 = P2 / "CEAS_Space_Journal/MANUSCRIPT_CEAS_R1_2026-10-01.md"
FIG = P2 / "Post_Rejection_Rebuild/figures/PAPER2_R2_FIGURE1_RESIDUAL_BOUNDARIES.svg"
STATUS = P2 / "CEAS_Space_Journal/STATUS_R1.json"
WF = ROOT / ".github/workflows/validate-research-configs.yml"
ABSTRACT = "Satellite cyber-recovery qualification depends on the evidence visible when a recovery step is authorized, rather than on hidden system truth. We examine which trust failures remain invisible under three separately frozen finite models of temporal evidence, producer composition, and recovery-artifact assurance. Study 3 (1,380 trajectories) distinguishes bounded reliance on truthful but stale authorization records from a false authorization claim validly signed by a compromised trusted producer. In a separately governed stress test, S3X uses 1,919 extreme European Space Agency telemetry inter-sample intervals solely as evidence-refresh-hiatus proxies; timing shifts when the false claim reaches the decision without correcting its first-refresh classification. Study 4 (4,608 observations across 18 vote/provenance rules) shows that producer diversity changes first and systematic unsafe-qualification boundaries, sometimes at the cost of benign-evidence availability. Study 6 (420 observations) reduces the modeled incorrect artifact states still qualified from four of five under signature-only checking to one of five under a six-signal gate. In separate executable stress test S6X, two repetitions of 396 observations using pinned NASA core Flight System/Limit Checker source distinguish clean and controlled bad-source artifacts in a research functional harness, while all six gate-visible signals remain satisfied. The engineering result is a mechanism-specific map of the property each qualification gate can and cannot establish. These models do not demonstrate operational spacecraft recovery, pooled effects, or external empirical replication."
BRIDGE = "For space-system engineering, this is a recovery-qualification requirements question rather than a test of an operational recovery sequence. A satellite recovery gate must specify what a signed authorization record, a multi-producer decision, or an approved software baseline actually warrants before it permits progression. The three independently evaluated mechanisms expose different missing properties; their qualitative synthesis identifies questions for mission-specific verification, not an experimentally integrated spacecraft architecture or a comparison of learned recovery selectors."
MANUSCRIPT_BLOB = "a16fba122ad1b42a54c26bffee68ff05ad477b51"
ORIGINAL_BLOB = "069e319864b1f5c1ee201b31872e68572fea1923"
FIGURE_BLOB = "5f68ac156b4e27c7bfd99e006623196c250c94a1"
FIGURE_SHA256 = "adfdfaf833c8624bb405209be22ef6b2f002cdec53f081ce097f67e728eedffc"
ANCHOR = "The narrower problem here is whether the evidence visible to a recovery-qualification decision is sufficient to distinguish a modeled safe state from an unsafe one."
SEC = {"I":1,"II":2,"III":3,"IV":4,"V":5,"VI":6,"VII":7,"VIII":8,"IX":9}
TAB = {"I":1,"II":2,"III":3,"IV":4,"V":5}

def req(ok, message):
    if not ok:
        raise SystemExit("FAIL_CEAS_R1: "+message)

def blob(rel):
    return subprocess.check_output(["git", "hash-object", str(rel.relative_to(ROOT))], cwd=ROOT, text=True).strip()

req(blob(R4)==ORIGINAL_BLOB,"R4 drift")
req(blob(R1)==MANUSCRIPT_BLOB,"CEAS R1 manuscript blob drift")
req(blob(FIG)==FIGURE_BLOB and hashlib.sha256(FIG.read_bytes()).hexdigest()==FIGURE_SHA256,"canonical Figure 1 drift")
original=R4.read_text(encoding="utf-8")
candidate=R1.read_text(encoding="utf-8")
orig_start=original.index("## I. Introduction\n")
orig_ack=original.index("## Acknowledgment and AI-Assistance Disclosure\n")
orig_refs=original.index("## References\n")
original_body=original[orig_start:orig_ack]
original_references=original[orig_refs:].rstrip()
req(original_body.count(ANCHOR)==1,"Introduction exact anchor drift")

def adapt_body(text):
    cur=0
    out=[]
    for line in text.replace(ANCHOR,ANCHOR+"\n\n"+BRIDGE).rstrip().split("\n"):
        m=re.match(r"^## (I|II|III|IV|V|VI|VII|VIII|IX)\. (.+)$",line)
        if m:
            cur=SEC[m.group(1)]
            out.append("## "+str(cur)+" "+m.group(2))
            continue
        m=re.match(r"^### Table (I|II|III|IV|V)\. (.+)$",line)
        if m:
            out.append("**Table "+str(TAB[m.group(1)])+"** "+m.group(2))
            continue
        m=re.match(r"^### ([A-Z])\. (.+)$",line)
        if m:
            req(cur>0,"orphan subsection")
            out.append("### "+str(cur)+"."+str(ord(m.group(1))-64)+" "+m.group(2))
            continue
        line=re.sub(r"\bTable (IV|III|II|I|V)\b",lambda m:"Table "+str(TAB[m.group(1)]),line)
        line=line.replace("**Figure 1. Residual trust boundaries","**Fig. 1** Residual trust boundaries")
        line=line.replace("Figure 1","Fig. 1")
        line=line.replace("(figures/PAPER2_R2_FIGURE1_RESIDUAL_BOUNDARIES.svg)","(../Post_Rejection_Rebuild/figures/PAPER2_R2_FIGURE1_RESIDUAL_BOUNDARIES.svg)")
        out.append(line)
    return "\n".join(out)

expected_body=adapt_body(original_body)
actual_body=candidate.split("## 1 Introduction\n",1)[1].split("## AI-use declaration\n",1)[0]
req(actual_body==expected_body.split("## 1 Introduction\n",1)[1]+"\n\n","scientific body edits exceed one intro bridge and publisher format conversions")
req(candidate.endswith(original_references+"\n"),"R4 reference contents or order modified")
actual_abstract=candidate.split("## Abstract\n\n",1)[1].split("\n\n**Keywords:**",1)[0].strip()
req(actual_abstract==ABSTRACT,"CEAS abstract content drift")
word_count=len(actual_abstract.split())
req(150<=word_count<=250,"CEAS abstract word count")
terms=re.search(r"^\*\*Index Terms—\*\*\s*(.+)$",original,re.M).group(1)
req("**Keywords:** "+terms in candidate and len(terms.split(","))==6,"source six keywords not preserved")
req(len(re.findall(r"^\*\*Table [1-5]\*\*",candidate,re.M))==5,"five original table bodies/captions")
req(candidate.count("![Fig. 1.")==1,"figure inclusion count")
req(candidate.count("Fig. 1")>=3,"figure callout/caption absent")
req(candidate.count("## Statements and Declarations")==1 and candidate.count("## AI-use declaration")==1,"declarations absent")
req(candidate.count("Aman Singh")==2 or candidate.count("Aman Singh")>=2,"sole human authorship missing")
for phrase in ("not an external empirical replication of Study 6","No pooled N","APPROVED_BAD_SOURCE","research-only objective adjudication","does not establish a vulnerability in cFS or Limit Checker"):
    req(phrase in candidate,"scientific claim firewall absent: "+phrase)
status=json.loads(STATUS.read_text(encoding="utf-8"))
req(status["source_main"]==BASE and status["source_r4_blob_sha1"]==ORIGINAL_BLOB,"status authority drift")
req(status["ceas_r1_manuscript_blob_sha1"]==MANUSCRIPT_BLOB and status["ceas_abstract_whitespace_words"]==word_count,"status candidate drift")
req(status["ceas_keywords_count"]==6 and status["table_count"]==5 and status["figure1_insertions"]==1,"status layout drift")
for field in ("venue_lock","merge","scientific_execution","source_r4_mutation","figure1_source_mutation","experimental_populations_pooled","publisher_derivative_final_release","publisher_portal_activity","publisher_submission","github_visibility_change"):
    req(status["authorization"][field] is False,"closed authorization opened: "+field)
allowed={
".github/workflows/validate-research-configs.yml",
"scripts/audit_paper2_ceas_r1.py",
"publication/Paper_2_Studies_3_4_6/CEAS_Space_Journal/README.md",
"publication/Paper_2_Studies_3_4_6/CEAS_Space_Journal/MANUSCRIPT_CEAS_R1_2026-10-01.md",
"publication/Paper_2_Studies_3_4_6/CEAS_Space_Journal/LIVE_SCOPE_REQUIREMENTS_AUDIT_2026-10-01.md",
"publication/Paper_2_Studies_3_4_6/CEAS_Space_Journal/PRESERVATION_AND_PORTFOLIO_AUDIT_R1_2026-10-01.md",
"publication/Paper_2_Studies_3_4_6/CEAS_Space_Journal/STATUS_R1.json",
}
changed=set(subprocess.check_output(["git","diff","--name-only",BASE+"...HEAD"],cwd=ROOT,text=True).splitlines())
req(changed==allowed,"changed path whitelist mismatch "+str(sorted(changed^allowed)))
w=WF.read_text(encoding="utf-8")
req("python scripts/audit_paper2_ceas_r1.py" in w and "paper2-r4-historical-audit" in w and BASE in w,"workflow scope missing")
print("paper2_ceas_r1_audit=PASS")
print("source_R4_exact_git_blob=PASS")
print("Figure1_original_sha256=PASS")
print("scientific_methods_results_conclusion_unchanged_except_format_and_single_intro_bridge=PASS")
print("reference_entries_exactly_preserved=PASS")
print("ceas_abstract_words="+str(word_count))
print("six_keywords_five_tables_one_figure=PASS")
print("seven_file_branch_whitelist=PASS")
print("venue_lock=NO")
print("publisher_submission=NO")
