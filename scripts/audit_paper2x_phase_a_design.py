#!/usr/bin/env python3
"""Fail-closed static audit of authorized P2X Phase A; DOES NOT launch Docker."""
import json
import re
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
D=ROOT/"paper2x/phase_a"
BASE="b23f2785c3168ecb228098fa641412589cef9d86"
def chk(ok,k):
    if not ok:raise SystemExit("P2X_PHASE_A_DESIGN_FAIL_"+k)
data=json.loads((D/"PHASE_A_AUTHORIZATION_2026-10-03.json").read_text())
chk(data["record_id"]=="P2X-PHASE-A-AUTHORIZED-2026-10-03","AUTHORIZED_SCOPE")
chk(data["experiment_id"]=="P2X-NOS3-RG-001" and data["parent_design_commit"]==BASE,"PINNED_DESIGN")
chk(data["locked_nos3"]=="5a3bdee6be9a2c67fdf994ae6db56d5c60395302","NOS3_PIN")
chk(data["locked_nos3_lc_submodule"]=="5daef363c95d71c1ff3c5e9dcd4dddab560e8b39","NOS3_LC_GITLINK")
chk(data["locked_nos3_hwlib_submodule"]=="d65f77dea94467b7cb71053eb2f58f7a0cde3b02","NOS3_HWLIB_GITLINK")
chk(data["locked_image"]=="ivvitc/nos3-64@sha256:06aa945988a7770b759022c2e1f6f2531818c087fe41a4739d3a3a7f2a9dcce2","IMAGE_PIN")
chk(data["current_session_observed"]["session_docker_binary_available"] is False and
    data["current_session_observed"]["run_attempted_in_this_session"] is False,"NO_FALSE_LIVE_RUN")
approved=data["approved_actions"];prohibited=data["prohibited_actions"]
chk(any("benign_SAMPLE_NOOP" in x for x in approved),"ONE_BENIGN_NOOP_ONLY")
for word in ("fault_injection","generate_F1_F2_C0_C1_C2_primary_results","submit_CEAS","change_NOS3"):
    chk(any(word in x for x in prohibited),"PROHIBITION_"+word)
sh=(ROOT/"scripts/run_paper2x_phase_a_nominal.sh").read_text()
for key in ("wrong_project_root","wrong_research_repository_origin","EXPECTED_HWLIB","5daef363c95d71c1ff3c5e9dcd4dddab560e8b39","verify_nos3_source_lock.sh","run_nominal_runtime_preflight.sh",
            "18fac000000100dc","SAMPLE: NOOP command received",
            "PHASE_A_PARTIAL_CFS_INGEST_PROOF__COSMOS_GROUND_CONFIRMATION_OPEN",
            "internal_test_sender_udp_not_COSMOS",
            "P2X_PHASE_A_COSMOS_TELEMETRY=PENDING_SEPARATE_EVIDENCE"):
    chk(key in sh,"NOMINAL_SCRIPT_BOUNDARY_"+key)
for k in ("scripts/run_wp6_p7_mission_aware_integration.sh",
          "scripts/run_wp7_trusted_recovery_test.sh","make clean","git checkout","docker pull"):
    chk(k not in sh,"DISALLOWED_RUNTIME_COMMAND_"+k)
chk("no new scientific" in sh.lower() or "no paper-1/p7 policy code" in sh.lower(),"NO_OTHER_PAPER_POLICY")
chk("docker run --rm --platform linux/amd64 --network" in sh,"INTERNAL_GROUND_SENDER")
chk("P2X_PHASE_A_RESULT=PARTIAL_CFS_INGEST_PROOF_ONLY" in sh,"NO_FULL_GATE_ACCEPTANCE")
ft=(ROOT/"scripts/restore_paper2x_phase_a_fortytwo.sh").read_text()
for token in ("wrong_project_root","fortytwo_binary_differs_from_july_freeze_hold_before_NOS3_build","eda252bf31f27850e867e698cfdd963e143ead1f","9c0062d2a447a6340e7c191850ff952d3f8768dd307e3e7fb141e777961e60c7","--network none","make GUIFLAG= SHADERFLAG= 42","historical_nos3_build_lock_changed","FORTYTWO_DESTINATION=MISSING","RUNTIME_EXECUTED=NO"):
    chk(token in ft,"FORTYTWO_OFFLINE_RECONSTRUCTION_GUARD_"+token)
for forbidden in ("make clean","scripts/build_nominal_nos3.sh","run-ci-noop","git push","docker pull"):
    chk(forbidden not in ft,"FORTYTWO_RECONSTRUCTION_OUT_OF_SCOPE_"+forbidden)
template=json.loads((D/"COSMOS_GROUND_OBSERVATION_TEMPLATE.json").read_text())
chk(template["session_id"] is None and template["observed_utc"] is None,"UNFILLED_GROUND_TEMPLATE")
chk(template["pin_nos3"]==data["locked_nos3"],"PINNED_TEMPLATE")
chk(all(template["ground"][x] is None for x in ("radio_tx_bytes_before","radio_tx_bytes_after",
"radio_rx_bytes_before","radio_rx_bytes_after","counter_before","counter_after","cfs_console_event_observed")),"NO_INVENTED_GROUND_DATA")
chk(template["scope"]["independent_visual_review_completed"] is False,"INDEPENDENT_REVIEW_OPEN")
checker=(ROOT/"scripts/verify_paper2x_phase_a_evidence.py").read_text()
for k in ("CANDIDATE_FOR_INDEPENDENT_VISUAL_REVIEW__PHASE_A_NOT_YET_ACCEPTED",
"counter_after","cfs_console_event_observed","--check-template"):
    chk(k in checker,"EVIDENCE_VERIFIER_"+k)
for filename in ("RUNBOOK_2026-10-03.md",):
    doc=(D/filename).read_text()
    for token in ("A0","A1","A2","A3","CFS_RADIO","TO_ENABLE_OUTPUT","radio_sim",
                  "5011","CFE_ES_NOOP","COSMOS_GSW_PLATFORM_BLOCKED"):
        chk(token in doc,"RUNBOOK_"+token)
wf=(ROOT/".github/workflows/validate-research-configs.yml").read_text()
chk("paper2x-design-historical-audit" in wf and "python scripts/audit_paper2x_phase_a_design.py" in wf,"WORKFLOW_SCOPE")
allowed={
".github/workflows/validate-research-configs.yml",
"scripts/restore_paper2x_phase_a_fortytwo.sh",
"paper2x/phase_a/PHASE_A_AUTHORIZATION_2026-10-03.json",
"paper2x/phase_a/RUNBOOK_2026-10-03.md",
"paper2x/phase_a/COSMOS_GROUND_OBSERVATION_TEMPLATE.json",
"scripts/run_paper2x_phase_a_nominal.sh",
"scripts/verify_paper2x_phase_a_evidence.py",
"scripts/audit_paper2x_phase_a_design.py"
}
changed=set(subprocess.check_output(["git","diff","--name-only",BASE+"...HEAD"],cwd=ROOT,text=True).splitlines())
chk(changed==allowed,"PHASE_A_WHITELIST_DIFF_"+str(sorted(changed^allowed)))
print("P2X_PHASE_A_SCOPE_AND_STATIC_AUDIT=PASS")
print("BENIGN_INTERNAL_CFS_NOOP_CODE_REVIEW=PASS")
print("PINNED_COSMOS_TELEMETRY_OPERATOR_PROOF_STILL_REQUIRED=PASS")
print("DOCKER_RUNTIME_EXECUTION_IN_CI=NO")
print("NEW_SCIENTIFIC_OUTPUT=NO")
