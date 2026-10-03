#!/usr/bin/env python3
"""Validate the P2X-NOS3-RG-001 prospective protocol. Never executes experiments."""
from pathlib import Path
import json, re, subprocess

ROOT=Path(__file__).resolve().parents[1]
BASE="4cd0c30a276b3c5a0494736b93a8d08dc1ed8df4"
D=ROOT/"paper2x"
PROTOCOL=D/"protocol/P2X-NOS3-RG-001.json"
def chk(cond,msg):
    if not cond:raise SystemExit("P2X_DESIGN_FAIL_"+msg)
spec=json.loads(PROTOCOL.read_text(encoding="utf-8"))
chk(spec["schema"]==1 and spec["experiment_id"]=="P2X-NOS3-RG-001","ID")
chk(spec["phase"]=="DESIGN_ONLY__NO_RUNTIME_AUTHORIZATION" and spec["outcome_data_present"] is False,"NO_SCIENTIFIC_RESULTS")
chk(spec["main_authority"]==BASE,"SOURCE_AUTHORITY")
chk(spec["infrastructure"]["reused_tooling_only"] is True and spec["infrastructure"]["historical_result_row_reuse_authorized"] is False,"TOOLING_ONLY")
chk(spec["infrastructure"]["policy_code_from_other_papers_reuse_authorized"] is False,"NO_PAPER1_POLICY")
checks={
    "nos3_commit":"5a3bdee6be9a2c67fdf994ae6db56d5c60395302",
    "nos3_image_digest":"ivvitc/nos3-64@sha256:06aa945988a7770b759022c2e1f6f2531818c087fe41a4739d3a3a7f2a9dcce2",
}
for k,v in checks.items():chk(spec["infrastructure"][k]==v,"PIN_"+k)
prepare=(ROOT/"scripts/prepare_nos3_candidate.sh").read_text(encoding="utf-8")
source_lock=(ROOT/"scripts/verify_nos3_source_lock.sh").read_text(encoding="utf-8")
build=(ROOT/"scripts/build_nominal_nos3.sh").read_text(encoding="utf-8")
chk(checks["nos3_commit"] in prepare and checks["nos3_commit"] in source_lock and checks["nos3_commit"] in build,"NOS3_PIN_BINDING")
chk(checks["nos3_image_digest"] in source_lock and checks["nos3_image_digest"] in build,"IMAGE_PIN_BINDING")
arms=spec["comparison_arms"]
chk([x["id"] for x in arms]==["G0","G1"],"ARMS")
g0=set(arms[0]["inputs"]);g1=set(arms[1]["inputs"])
chk(g1-g0=={"pre_admission_functional_conformance"} and g0-g1==set(),"ONLY_ONE_ADDITIONAL_SIGNAL")
chk(arms[0]["functional_conformance_visible"] is False and arms[1]["functional_conformance_visible"] is True,"SIGNAL_GATE")
cases=spec["scenario_register"]
chk([x["id"] for x in cases]==["C0","C1","C2","F1","F2","CAL1"],"SCENARIO_REGISTER")
chk([x["id"] for x in cases if x["primary"]]==["C0","C1","C2","F1","F2"],"PRIMARY_IDS")
chk(cases[-1]["primary"] is False,"HISTORICAL_CALIBRATION_EXCLUDED")
for k in ("fault_injector","functional_checker","truth_oracle","raw_trace_audit"):
    chk(bool(spec["independent_evaluation"].get(k)),"INDEPENDENT_ROLE_"+k)
chk("not a variable in G0 or G1" in spec["independent_evaluation"]["truth_oracle"],"TRUTH_ORACLE_SEPARATION")
metrics=spec["measurements"]
for k in ("cfs_CI_receipt_verified","unsafe_dispatch_count_by_scenario_and_gate","correct_case_held_or_deferred_count","functional_evidence_collection_latency_ms","oracle_gate_information_separation"):
    chk(k in metrics,"REAL_EVIDENCE_METRIC_"+k)
for k,v in spec["guardrails"].items():chk(v is True,"GUARDRAIL_"+k)
chk(len(spec["preexecution_gates"])>=7,"EXPLICIT_AUTHORIZATION_GATES")
docs=[D/"README.md",D/"docs/PREREGISTERED_STUDY_AND_ARCHITECTURE_2026-10-03.md",D/"docs/EXECUTION_GATE_AND_PORTFOLIO_FIREWALL_2026-10-03.md"]
for doc in docs:
    text=doc.read_text(encoding="utf-8")
    chk("P2X-NOS3-RG-001" in text,"DOC_ID_"+doc.name)
    chk("NO_RUNTIME" in text or "No build" in text or "No publisher" in text or "Design-only" in text,"DOC_SCOPE_"+doc.name)
allowed={
".github/workflows/validate-research-configs.yml",
"paper2x/README.md",
"paper2x/protocol/P2X-NOS3-RG-001.json",
"paper2x/docs/PREREGISTERED_STUDY_AND_ARCHITECTURE_2026-10-03.md",
"paper2x/docs/EXECUTION_GATE_AND_PORTFOLIO_FIREWALL_2026-10-03.md",
"scripts/audit_paper2x_design.py"
}
changed=set(subprocess.check_output(["git","diff","--name-only",BASE+"...HEAD"],cwd=ROOT,text=True).splitlines())
chk(changed==allowed,"CHANGED_PATH_WHITELIST_"+str(sorted(changed^allowed)))
wf=(ROOT/".github/workflows/validate-research-configs.yml").read_text(encoding="utf-8")
chk("paper2-r4-historical-audit" in wf and "python scripts/audit_paper2x_design.py" in wf,"CI_CORRECT_PHASE_SCOPING")
print("P2X_PROSPECTIVE_DESIGN_AUDIT=PASS")
print("NOS3_SOURCE_AND_IMAGE_PIN_REUSE_ONLY=PASS")
print("REAL_COMMAND_TELEMETRY_AND_INDEPENDENT_ORACLE_DESIGNED=PASS")
print("PRIMARY_FAULT_FAMILIES_NEW_OLD_S6X_CALIBRATION_EXCLUDED=PASS")
print("CROSS_PAPER_DATA_MIGRATION=NO")
print("EXPERIMENTS_EXECUTED=NO")
print("PUBLISHER_SUBMISSION=NO")
