#!/usr/bin/env python3
"""Evidence-first CEAS R2 audit; never re-runs frozen experiments."""
from __future__ import annotations
import hashlib
import json
import re
import subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/"publication/Paper_2_Studies_3_4_6"
C=P/"CEAS_Space_Journal"
R4=P/"Post_Rejection_Rebuild/PAPER2_REBUILD_MANUSCRIPT_R4_2026-10-01.md"
R1=C/"MANUSCRIPT_CEAS_R1_2026-10-01.md"
R2=C/"MANUSCRIPT_CEAS_R2_2026-10-02.md"
FIG=P/"Post_Rejection_Rebuild/figures/PAPER2_R2_FIGURE1_RESIDUAL_BOUNDARIES.svg"
BASE="4cd0c30a276b3c5a0494736b93a8d08dc1ed8df4"
EXPECTED_R2="e1160c4cb5607ead24f7ba87de978a3198b88c76"
def chk(ok,info):
    if not ok: raise SystemExit("FAIL_CEAS_R2_"+info)
def blob(path):
    return subprocess.check_output(["git","hash-object",str(path.relative_to(ROOT))],cwd=ROOT,text=True).strip()
chk(blob(R4)=="069e319864b1f5c1ee201b31872e68572fea1923","R4_DRIFT")
chk(blob(R1)=="a16fba122ad1b42a54c26bffee68ff05ad477b51","R1_DRIFT")
chk(blob(R2)==EXPECTED_R2,"R2_BLOB")
chk(blob(FIG)=="5f68ac156b4e27c7bfd99e006623196c250c94a1","FIG_BLOB")
chk(hashlib.sha256(FIG.read_bytes()).hexdigest()=="adfdfaf833c8624bb405209be22ef6b2f002cdec53f081ce097f67e728eedffc","FIG_SHA256")
for p,sha in {
"study3/results/RESULTS_FREEZE.json":"afb81cad030c3c6e638c9b9807a9c214f293daa5",
"study4/results/RESULTS_FREEZE.json":"c0ba06f10c75520e49f6088d45ec1b5c097ce58f",
"study6/results/RESULTS_FREEZE.json":"255fcd808694071a89869a341174dadc0e5d37a8",
"study6x/S6X_CANONICAL_RESULT_FREEZE_004.json":"2e6b213b994062fd108e4b8435d9c0c36d93fdc0"
}.items():chk(blob(ROOT/p)==sha,"FROZEN_RESULT_DRIFT_"+p)
old=R1.read_text(encoding="utf-8")
new=R2.read_text(encoding="utf-8")
ab=new.split("## Abstract\n\n",1)[1].split("\n\n**Keywords:**",1)[0].strip()
chk(len(ab.split())==232 and 150<=len(ab.split())<=250,"ABSTRACT")
chk("S3X" not in ab and "S6X" not in ab,"ABSTRACT_UNDEFINED_LABEL")
terms=lambda x:x.split("**Keywords:**",1)[1].split("\n",1)[0].strip()
chk(terms(old)==terms(new) and len(terms(new).split(","))==6,"KEYWORDS")
def table(x,n):
    q=re.search(r"(?m)^\*\*Table "+str(n)+r"\*\* ([^\n]*)\n\n((?:^\|.*\n)+)",x)
    chk(q is not None,"TABLE_MISSING_"+str(n))
    return q.group(1),q.group(2)
for n in range(1,6):chk(table(old,n)==table(new,n),"TABLE_BODY_CHANGED_"+str(n))
chk(len(re.findall(r"(?m)^!\[Fig\. 1",new))==1,"FIGURE_COUNT")
chk("../Post_Rejection_Rebuild/figures/PAPER2_R2_FIGURE1_RESIDUAL_BOUNDARIES.svg" in new,"FIGURE_PATH")
chk(len(re.findall(r"(?m)^## [1-9] ",new))==9 and not re.search(r"(?m)^#### ",new),"SECTION_LEVELS")
for n in ("1,380","67,620","4,608","420","1,919","34,542","30,704","32/64","63/64","46/46","7,676","3,838","cb840a8d89267b313be79280d2909e708327cb5ca333e23dbfc7e50b9e37dc63"):
    chk(n in new,"EXACT_FINDING_LOST_"+n)
for s in ("existence demonstration","researcher-introduced","research-only","outside the six qualification inputs","### 3.1 Illustrative engineering allocation","### 3.2 Manuscript preparation disclosure","third-party redistribution restrictions"):
    chk(s.lower() in new.lower(),"CLAIM_FIREWALL_LOST_"+s)
b,refs=new.split("## References\n",1)
entries=re.findall(r"(?m)^\[(\d+)\] (.*)$",refs)
chk(len(entries)==19 and [int(x) for x,y in entries]==list(range(1,20)),"BIB_19")
cites=[int(x) for x in re.findall(r"\[(\d+)\]",b)]
chk(set(cites)==set(range(1,20)),"CITATION_COVERAGE")
first=[]
for k in cites:
    if k not in first:first.append(k)
chk(first==list(range(1,20)),"CITATION_FIRST_USE")
for s in ("2608.14532","2603.23745","draft-ietf-rats-multi-verifier"):
    chk(s not in refs,"UNPUBLISHED_FORMAL_REFERENCE_"+s)
for s in ("10.1007/s12567-023-00529-5","10.1007/s12567-024-00589-1"):
    chk(s in refs,"CEAS_REF_MISSING_"+s)
sec8=new.split("## 8 Validity",1)[1].split("## 9 Conclusion",1)[0]
chk(len(sec8.split())<480 and "Construct validity" in sec8 and "External validation" in sec8,"SECTION8")
st=json.loads((C/"STATUS_R2.json").read_text(encoding="utf-8"))
chk(st["manuscript_r2_blob"]==EXPECTED_R2 and st["abstract_whitespace_words"]==232,"STATUS")
chk(st["no_new_science"] is True,"SCIENCE_GATE")
for n in ("submit_authorized","merge_authorized","archival_deposit_authorized","editorial_contact_sent","new_experiment_authorized"):
    chk(st["release_gates"][n] is False,"AUTHORIZATION_OPENED_"+n)
allowed=set((
".github/workflows/validate-research-configs.yml",
"publication/Paper_2_Studies_3_4_6/CEAS_Space_Journal/README.md",
"publication/Paper_2_Studies_3_4_6/CEAS_Space_Journal/MANUSCRIPT_CEAS_R1_2026-10-01.md",
"publication/Paper_2_Studies_3_4_6/CEAS_Space_Journal/LIVE_SCOPE_REQUIREMENTS_AUDIT_2026-10-01.md",
"publication/Paper_2_Studies_3_4_6/CEAS_Space_Journal/PRESERVATION_AND_PORTFOLIO_AUDIT_R1_2026-10-01.md",
"publication/Paper_2_Studies_3_4_6/CEAS_Space_Journal/STATUS_R1.json",
"scripts/audit_paper2_ceas_r1.py",
"publication/Paper_2_Studies_3_4_6/CEAS_Space_Journal/MANUSCRIPT_CEAS_R2_2026-10-02.md",
"publication/Paper_2_Studies_3_4_6/CEAS_Space_Journal/REFERENCE_AND_CLAIM_AUDIT_R2_2026-10-02.md",
"publication/Paper_2_Studies_3_4_6/CEAS_Space_Journal/DATA_AND_CODE_MANIFEST_R2_2026-10-02.md",
"publication/Paper_2_Studies_3_4_6/CEAS_Space_Journal/SUBMISSION_READINESS_R2_2026-10-02.md",
"publication/Paper_2_Studies_3_4_6/CEAS_Space_Journal/STATUS_R2.json",
"scripts/audit_paper2_ceas_r2.py",
"scripts/build_paper2_ceas_r2_preview.sh",
))
actual=set(subprocess.check_output(["git","diff","--name-only",BASE+"...HEAD"],cwd=ROOT,text=True).splitlines())
chk(actual==allowed,"DIFF_WHITELIST_"+str(sorted(actual^allowed)))
w=(ROOT/".github/workflows/validate-research-configs.yml").read_text()
chk("paper2-r1-historical-audit" in w and "python scripts/audit_paper2_ceas_r2.py" in w,"WORKFLOW")
print("CEAS_R2_SCIENCE_AND_EDITORIAL_AUDIT=PASS")
print("R4_R1_FIG1_AND_FROZEN_BLOBS=PASS")
print("FIVE_TABLE_BODIES_IDENTICAL=PASS")
print("ABSTRACT=232 KEYWORDS=6 REFS=19")
print("SCIENCE_EXECUTION=NO PUBLISHER_SUBMISSION=NO")
