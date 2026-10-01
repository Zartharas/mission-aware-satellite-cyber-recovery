#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
REBUILD=ROOT/"publication/Paper_2_Studies_3_4_6/Post_Rejection_Rebuild"
RECORD=ROOT/"study6x/S6X_INTERPRETATION_CLAIM_USE_001.json"
REPORT=REBUILD/"S6X_RESULT_INTERPRETATION_AND_CLAIM_USE_R1_2026-09-30.md"
INSERTS=REBUILD/"PAPER2_REBUILD_S6X_MANUSCRIPT_INSERTS_R1_2026-09-30.md"
R2=REBUILD/"PAPER2_REBUILD_MANUSCRIPT_R2_2026-09-28.md"
R3=REBUILD/"PAPER2_REBUILD_MANUSCRIPT_R3_2026-09-30.md"
DISPLAY=REBUILD/"PAPER2_R3_S6X_DISPLAY_DECISION_2026-09-30.md"
CLAIMMAP=REBUILD/"PAPER2_REBUILD_R3_CLAIM_SOURCE_MAP_2026-09-30.md"
STATUS=REBUILD/"PAPER2_REBUILD_R3_STATUS.json"
FREEZE=ROOT/"study6x/S6X_CANONICAL_RESULT_FREEZE_004.json"
WORKFLOW=ROOT/".github/workflows/validate-research-configs.yml"
FIGURE=REBUILD/"figures/PAPER2_R2_FIGURE1_RESIDUAL_BOUNDARIES.svg"

BASE="2ddbd795c4734654f421616de996911fa62ee27a"
EXPECTED={
"publication/Paper_2_Studies_3_4_6/Post_Rejection_Rebuild/PAPER2_REBUILD_MANUSCRIPT_R2_2026-09-28.md":"9e3f345a3a16102c39bb978f4e522c261e80cfb4",
"publication/Paper_2_Studies_3_4_6/Post_Rejection_Rebuild/figures/PAPER2_R2_FIGURE1_RESIDUAL_BOUNDARIES.svg":"5f68ac156b4e27c7bfd99e006623196c250c94a1",
"study6x/S6X_CANONICAL_RESULT_FREEZE_004.json":"2e6b213b994062fd108e4b8435d9c0c36d93fdc0",
"study6x/S6X_CANONICAL_RUNTIME_AUTH_004.json":"d5a329be6c0803c5345845746c66844db8cfb552",
"study6x/validation/run_local_canonical_execution_004.sh":"99088f34886c50d38efaabf1c0aca4679fe07342",
"study6x/S6X_EVIDENCE_SCHEMA_004.json":"af697b5407bf1eda49667109d208aa9e57030494",
"study6x/runtime/run_canonical_population_004.py":"965fde110b7dc754553efe08b1530beeba752908",
"study6x/audit/validate_canonical_execution_004.py":"b4c7a81ae74e118d820ae2ada107d9e15e40ed2e",
"study6x/runtime/gate_evaluator.py":"c6045b249daa6a3ff3b2ff54982b047c299fd04c",
"study6x/audit/reference_gate_evaluator.py":"c3834f478196fe3fd3e9290ff0ecc603a0933247",
"study6x/fixtures/S6X_INVARIANT_HARNESS_EQUALITY_001.patch":"b3318be396a6c4e5c98f2339846d9ea59bcd5def",
"study6x/fixtures/S6X_FIXTURE_GT_EQ_BOUNDARY_001.patch":"e3189e5a06ff47a2cf68bb7d343c563a300dc313",
"study6x/src/invariant_oracle.py":"70b555cec84cb455c72094c6539df3873662182d",
"study6x/S6X_INTERPRETATION_CLAIM_USE_001.json":"a0786f278d5315b438ad6416a91be8cb16262b83",
"publication/Paper_2_Studies_3_4_6/Post_Rejection_Rebuild/S6X_RESULT_INTERPRETATION_AND_CLAIM_USE_R1_2026-09-30.md":"d524cc551e64c0a625cfe9d878c618fb08b4d0ce",
"publication/Paper_2_Studies_3_4_6/Post_Rejection_Rebuild/PAPER2_REBUILD_S6X_MANUSCRIPT_INSERTS_R1_2026-09-30.md":"3a6cbfb9036c97bb9b96e59c5aa99df2a06ebec9",
"publication/Paper_2_Studies_3_4_6/Post_Rejection_Rebuild/PAPER2_REBUILD_MANUSCRIPT_R3_2026-09-30.md":"2182ea02634854da92d6d6049e6fdd269b11bac8",
"publication/Paper_2_Studies_3_4_6/Post_Rejection_Rebuild/PAPER2_R3_S6X_DISPLAY_DECISION_2026-09-30.md":"d8f85d295f1bed53bcf81b5cb0cd0cd8a6958c96",
"publication/Paper_2_Studies_3_4_6/Post_Rejection_Rebuild/PAPER2_REBUILD_R3_CLAIM_SOURCE_MAP_2026-09-30.md":"65755824c3d2f69e955b604fe5a57a2cc8db04f6",
"publication/Paper_2_Studies_3_4_6/Post_Rejection_Rebuild/PAPER2_REBUILD_R3_STATUS.json":"4319c2923c30aba7bc33cae97817487862dce290",
}

def fail(msg):
    print(f"[FAIL] {msg}",file=sys.stderr)
    raise SystemExit(1)

def req(cond,msg):
    if not cond: fail(msg)

def blob(rel):
    return subprocess.check_output(["git","hash-object",rel],cwd=ROOT,text=True).strip()

def j(path):
    return json.loads(path.read_text(encoding="utf-8"))

for rel,sha in EXPECTED.items():
    req((ROOT/rel).is_file(),f"missing {rel}")
    req(blob(rel)==sha,f"bound blob drift: {rel}")

freeze=j(FREEZE)
req(freeze["freeze_id"]=="S6X-CANONICAL-RESULT-FREEZE-004","freeze id drift")
req(freeze["campaign_id"]=="S6X_CANONICAL_EXECUTION_004","campaign id drift")
req(freeze["terminal_execution_evidence"]["runner_exit_code"]==0,"runner rc drift")
req(freeze["terminal_execution_evidence"]["runner_terminal_pass"] is True,"terminal PASS missing")
req(freeze["terminal_execution_evidence"]["console_log_sha256"]=="e45bd9c912d34a9d56c9a7368b2b5714e491eee45dd8640c25412d963d0f5c3c","console binding drift")
req(freeze["scientific_population_evidence"]["observations_per_repetition"]==396,"population drift")
req(freeze["scientific_population_evidence"]["block_a_rows_per_repetition"]==12,"Block A drift")
req(freeze["scientific_population_evidence"]["block_b_rows_per_repetition"]==384,"Block B drift")
req(freeze["scientific_population_evidence"]["run1_primary_reference_gate_mismatches"]==0,"run1 mismatch")
req(freeze["scientific_population_evidence"]["run2_primary_reference_gate_mismatches"]==0,"run2 mismatch")
req(freeze["deterministic_repeat_result_hashes"]["repeat_identity"]=="PASS","repeat identity drift")

rec=j(RECORD)
req(rec["record_id"]=="S6X-INTERPRETATION-CLAIM-USE-001","claim-use id drift")
req(rec["authorized_main_commit"]==BASE,"claim-use base drift")
auth=rec["authorization_basis"]
for key in ("interpretation_authorized","rebuild_manuscript_claim_use_authorized"):
    req(auth[key] is True,f"authorization closed: {key}")
for key in ("r2_mutation_authorized","historical_taes_submission_mutation_authorized","scientific_reexecution_authorized","result_mutation_authorized","figure1_revision_authorized","study6_mutation_authorized","study6_s6x_pooling_authorized"):
    req(auth[key] is False,f"prohibited authorization open: {key}")
fr=rec["frozen_result_authority"]
req(fr["freeze_id"]=="S6X-CANONICAL-RESULT-FREEZE-004","claim-use freeze binding drift")
req(fr["freeze_record_git_blob_sha1"]=="2e6b213b994062fd108e4b8435d9c0c36d93fdc0","claim-use freeze blob drift")
req(fr["effective_main_commit"]==BASE,"claim-use effective main drift")
req(fr["post_merge_ci_run_number"]==1314 and fr["post_merge_ci_run_id"]==36808689393 and fr["post_merge_ci_conclusion"]=="success","claim-use CI drift")
req(fr["runner_exit_code"]==0 and fr["runner_terminal_pass"] is True,"claim-use terminal PASS drift")
req(fr["observations_per_repetition"]==396 and fr["repetitions"]==2 and fr["total_builds"]==8,"claim-use execution counts drift")
req(fr["primary_reference_gate_mismatches"]==0 and fr["independent_validation"]=="PASS" and fr["deterministic_repeat_results"]=="PASS","claim-use validation drift")

claims={x["claim_id"]:x for x in rec["manuscript_eligible_claims"]}
expected_ids={
"S6X-C1-EXECUTABLE-ARTIFACT-REPRODUCIBILITY",
"S6X-C2-FUNCTIONAL-ADJUDICATION-BOUNDARY",
"S6X-C3-SIX-SIGNAL-OBSERVATIONAL-EQUIVALENCE",
"S6X-C4-BENIGN-UNAVAILABILITY-REPLAY",
"S6X-C5-DETERMINISTIC-REPEATABILITY",
"S6X-C6-RQ3-SYNTHESIS",
}
req(set(claims)==expected_ids,"eligible S6X claim set drift")
req(all(x["eligible"] is True for x in claims.values()),"eligible claim disabled")
withheld="\n".join(rec["prohibited_or_withheld_claims"])
for phrase in (
"external empirical replication of Study 6",
"pooled with the 420-observation Study-6 population",
"discovered vulnerability in NASA cFS or Limit Checker",
"unmodified upstream cFS/LC test suite",
"one of the six Study-6 qualification signals",
"operational risk",
"global ranking",
):
    req(phrase in withheld,f"missing claim firewall: {phrase}")
scope=rec["manuscript_use_scope"]
req(scope["post_rejection_rebuild_only"] is True and scope["historical_submitted_r10_immutable"] is True and scope["r2_immutable"] is True,"manuscript scope immutability drift")
req(scope["r3_candidate_authorized"] is True,"R3 not authorized")
req(scope["figure1_revision_required"] is False and scope["figure1_revision_authorized"] is False,"Figure 1 unexpectedly opened")
req(scope["claim_use_effective_only_after_record_merge_and_successful_post_merge_ci"] is True,"claim-use effectivity weakened")

r3=R3.read_text(encoding="utf-8")
r2=R2.read_text(encoding="utf-8")
req(r3.startswith("# Residual Trust Boundaries in Satellite Cyber-Recovery Qualification:"),"title changed unexpectedly")
req("Table V. S6X executable validation of the Study-6 observability mechanism" in r3,"Table V missing")
req(r3.count("### Table V.")==1,"Table V count drift")
for phrase in (
"S6X-EAP-001",
"not an external empirical replication of Study 6",
"research-only objective adjudication",
"augmented `native_std.runtest`",
"does not establish a vulnerability in cFS or Limit Checker",
"functional test/harness is research-only objective adjudication",
"all five canonical result files were byte-identical",
"does not pool S6X with Study 6",
):
    req(phrase in r3,f"R3 missing required boundary: {phrase}")
req("S6X is an external empirical replication of Study 6." not in r3,"R3 contains prohibited positive replication claim")
req("S6X observations are pooled" not in r3,"R3 contains pooling claim")
req("S6X demonstrates that NASA cFS" not in r3,"R3 contains prohibited NASA/cFS overclaim")
req("S6X demonstrates a real attacker" not in r3,"R3 contains real-attacker overclaim")

report=REPORT.read_text(encoding="utf-8")
inserts=INSERTS.read_text(encoding="utf-8")
display=DISPLAY.read_text(encoding="utf-8")
claimmap=CLAIMMAP.read_text(encoding="utf-8")
for txt,label in ((report,"report"),(inserts,"inserts"),(display,"display"),(claimmap,"claim map")):
    req("S6X" in txt,f"{label} missing S6X")
req("TABLE_V_REQUIRED__FIGURE1_REVISION_NOT_WARRANTED" in display,"display decision drift")
req("Figure 1 is not revised in this phase." in display,"Figure 1 boundary missing")
req("R3 adds Table V and leaves Figure 1 unchanged." in claimmap,"claim map display decision drift")

st=j(STATUS)
req(st["record_id"]=="PAPER2-POST-REJECTION-MANUSCRIPT-REBUILD-R3-S6X-001","R3 status id drift")
req(st["authorized_main_commit"]==BASE,"R3 status base drift")
req(st["immutable_prior_manuscript"]["git_blob_sha1"]=="9e3f345a3a16102c39bb978f4e522c261e80cfb4","R2 binding drift")
req(st["immutable_prior_manuscript"]["mutation_authorized"] is False,"R2 mutation opened")
req(st["s6x_claim_use"]["record_blob"]=="a0786f278d5315b438ad6416a91be8cb16262b83","claim-use record blob drift")
req(st["r3_candidate"]["git_blob_sha1"]=="2182ea02634854da92d6d6049e6fdd269b11bac8","R3 blob drift")
req(st["r3_candidate"]["word_count"]==7628,"R3 word count drift")
req(st["display_decision"]["table_v_added"] is True and st["display_decision"]["figure1_revision_required"] is False and st["display_decision"]["figure1_mutation"] is False,"R3 display controls drift")
req(all(v is False for v in st["science_controls"].values()),"science control opened")
req(all(v is False for v in st["publication_controls"].values()),"publication control opened")

allowed={
".github/workflows/validate-research-configs.yml",
"study6x/S6X_INTERPRETATION_CLAIM_USE_001.json",
"publication/Paper_2_Studies_3_4_6/Post_Rejection_Rebuild/S6X_RESULT_INTERPRETATION_AND_CLAIM_USE_R1_2026-09-30.md",
"publication/Paper_2_Studies_3_4_6/Post_Rejection_Rebuild/PAPER2_REBUILD_S6X_MANUSCRIPT_INSERTS_R1_2026-09-30.md",
"publication/Paper_2_Studies_3_4_6/Post_Rejection_Rebuild/PAPER2_REBUILD_MANUSCRIPT_R3_2026-09-30.md",
"publication/Paper_2_Studies_3_4_6/Post_Rejection_Rebuild/PAPER2_R3_S6X_DISPLAY_DECISION_2026-09-30.md",
"publication/Paper_2_Studies_3_4_6/Post_Rejection_Rebuild/PAPER2_REBUILD_R3_CLAIM_SOURCE_MAP_2026-09-30.md",
"publication/Paper_2_Studies_3_4_6/Post_Rejection_Rebuild/PAPER2_REBUILD_R3_STATUS.json",
"scripts/audit_paper2_s6x_interpretation_claim_use_r3.py",
}
changed=set(subprocess.check_output(["git","diff","--name-only",f"{BASE}...HEAD"],cwd=ROOT,text=True).splitlines())
req(changed==allowed,f"unexpected R3 phase diff: {sorted(changed ^ allowed)}")
req(blob("publication/Paper_2_Studies_3_4_6/Post_Rejection_Rebuild/PAPER2_REBUILD_MANUSCRIPT_R2_2026-09-28.md")=="9e3f345a3a16102c39bb978f4e522c261e80cfb4","R2 mutated")
req(blob("publication/Paper_2_Studies_3_4_6/Post_Rejection_Rebuild/figures/PAPER2_R2_FIGURE1_RESIDUAL_BOUNDARIES.svg")=="5f68ac156b4e27c7bfd99e006623196c250c94a1","Figure 1 mutated")

tracked=subprocess.check_output(["git","ls-files"],cwd=ROOT,text=True).splitlines()
req(not any(x.startswith("study6x/workspace/S6X_CANONICAL_EXECUTION_004/") for x in tracked),"raw Campaign 004 workspace tracked")
req("study6x/workspace/S6X_CANONICAL_EXECUTION_004_console.log" not in tracked,"Campaign 004 console tracked")
req("python scripts/audit_paper2_s6x_interpretation_claim_use_r3.py" in WORKFLOW.read_text(encoding="utf-8"),"CI hook missing")

print("paper2_s6x_interpretation_claim_use_r3_audit=PASS")
print("effective_result_freeze_004_verified=YES")
print("eligible_s6x_claims=6")
print("r2_immutable=YES")
print("r3_candidate_prepared=YES")
print("table_v_added=YES")
print("figure1_revision=NO")
print("study6_s6x_pooling=NO")
print("external_empirical_replication_claim=NO")
print("cfs_lc_vulnerability_claim=NO")
print("scientific_reexecution=NO")
print("result_mutation=NO")
print("historical_taes_r10_mutation=NO")
