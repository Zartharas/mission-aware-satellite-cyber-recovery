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
probe=(ROOT/"scripts/probe_paper2x_fortytwo_build_recipe.sh").read_text()
for token in ("october_control_not_reproducible_review_environment_first",
    "pinned_default_shader","make GUIFLAG= SHADERFLAG= 42","make GUIFLAG= 42",
    "--network none","git -C \"$FT\" archive \"$PIN\"",
    "Historical_build_recipe_unresolved_do_not_modify_original_freeze",
    "P2X_42_CANDIDATE_PROMOTION=NO","P2X_42_RUNTIME=NO","july_fortytwo_lock_mutated"):
    chk(token in probe,"FORTYTWO_RECIPE_PROBE_"+token)
for forbidden in ("make clean","rm -rf","docker pull","git push","run-ci-noop"):
    chk(forbidden not in probe,"FORTYTWO_PROBE_DISALLOWED_"+forbidden)
variance=(D/"FORTYTWO_BUILD_VARIANCE_DIAGNOSIS_2026-10-03.md").read_text()
for token in ("b4d054bdd8a95dd429201466833fba8403efec4bdef09a9ed7040131dda3006d",
    "9c0062d2a447a6340e7c191850ff952d3f8768dd307e3e7fb141e777961e60c7",
    "LOG_NOT_AVAILABLE","separate P2X environment baseline","No runtime"):
    chk(token.lower() in variance.lower(),"FORTYTWO_VARIANCE_RECORD_"+token)
v2=(D/"ENVIRONMENT_V2_ADOPTION_PROPOSAL_2026-10-03.md").read_text()
for token in ("AUTHOR_APPROVED_V2_CANDIDATE_POLICY__ENVIRONMENT_NOT_YET_QUALIFIED",
    "b4d054bdd8a95dd429201466833fba8403efec4bdef09a9ed7040131dda3006d",
    "9c0062d2a447a6340e7c191850ff952d3f8768dd307e3e7fb141e777961e60c7",
    "NOS3","COSMOS","independent","no runtime","historical locks",
    "October control","shader-default"):
    chk(token.lower() in v2.lower(),"P2X_V2_DRAFT_SCOPE_"+token)
v2auth=json.loads((D/"ENVIRONMENT_V2_AUTHORIZATION_2026-10-03.json").read_text())
chk(v2auth["decision"]=="AUTHOR_APPROVED_PROSPECTIVE_V2_CANDIDATE_POLICY","V2_AUTHOR_APPROVAL")
chk(v2auth["environment_final_acceptance"] is False and
    v2auth["new_runtime_evidence_observed"] is False,"V2_NOT_FALSELY_COMPLETED")
chk(v2auth["fortytwo"]["p2x_candidate_sha256"]=="b4d054bdd8a95dd429201466833fba8403efec4bdef09a9ed7040131dda3006d","V2_SEPARATE_FORTYTWO")
chk(v2auth["fortytwo"]["july_status"]=="NOT_BYTE_REPRODUCED__IMMUTABLE_PAPER1_REFERENCE","JULY_NOT_RELABELED")
chk(v2auth["authorization_scope"]["offline_build"] is True and
    v2auth["authorization_scope"]["primary_g0_g1_trial"] is False,"V2_SCOPE_FIREWALL")
chk(data["v2_authorization_record"]=="paper2x/phase_a/ENVIRONMENT_V2_AUTHORIZATION_2026-10-03.json" and
    data["v2_candidate_policy_approved"] is True,"V2_PHASE_A_BINDING")
build=(ROOT/"scripts/build_paper2x_phase_a_nos3_v2.sh").read_text()
for token in ("preexisting_build_dir_no_overwrite","cp -R \"$NOS3\" \"$SNAPSHOT\"",
    "build_once primary \"$NOS3\"","build_once repeat \"$SNAPSHOT\"",
    "--network none","make build-fsw","make build-sim","make build-cryptolib",
    "P2X_PHASE_A_V2_9_ARTIFACT_REPEAT_MATCH","original-locks-sha256.txt",
    "verify_paper2x_phase_a_v2.py","P2X_PHASE_A_V2_RUNTIME_EXECUTED=NO"):
    chk(token in build,"V2_TWO_OFFLINE_BUILDS_"+token)
for forbidden in ("rm -rf","make clean","scripts/build_nominal_nos3.sh","run-ci-noop","docker pull"):
    chk(forbidden not in build,"V2_BUILD_PROHIBITION_"+forbidden)
finalizer=(ROOT/"scripts/finalize_paper2x_phase_a_v2.py").read_text()
for token in ("historical_five", "split(maxsplit=1)",
              "P2X_PHASE_A_V2_9_ARTIFACT_REPEAT_MATCH",
              "P2X_PHASE_A_V2_BUILD_REEXECUTED=NO", "original_historical_lock_changed:",
              "historical_lock_parser_count", "p2x-v2-build-manifest.json"):
    chk(token in finalizer,"V2_RECOVERY_FINALIZER_"+token)
chk("finalize_paper2x_phase_a_v2.py" in build,"V2_BUILD_SHARED_FINALIZER")
regression=subprocess.run(["python3",str(ROOT/"scripts/finalize_paper2x_phase_a_v2.py"),
                           "--self-test-lock"],cwd=ROOT,capture_output=True,text=True)
chk(regression.returncode==0 and
    "P2X_V2_HISTORICAL_LOCK_PATH_WITH_SPACES_REGRESSION=PASS" in regression.stdout,
    "V2_HISTORICAL_CHECKSUM_SPACES_REGRESSION_"+regression.stderr[:180])
readback=(ROOT/"scripts/verify_paper2x_phase_a_v2.py").read_text()
chk("pieces = line.split(maxsplit=1)" in readback,"V2_READBACK_PATH_WITH_SPACES")
for token in ("TWO_INDEPENDENT_OFFLINE_BUILDS_MATCH__RUNTIME_UNTESTED",
    "independent_build_drift:","historical_lock_drift:","old_reference_changed:",
    "P2X_PHASE_A_ENV_V2_INDEPENDENT_READBACK=PASS","environment_final_acceptance"):
    chk(token in readback,"V2_READBACK_"+token)
chk("P2X_V2_MANIFEST" in sh and "verify_paper2x_phase_a_v2.py" in sh and
    "environment_v2_build_manifest_sha256" in sh,"P2X_RUNTIME_BOUND_TO_V2_MANIFEST")
v2d=(ROOT/"scripts/probe_paper2x_v2d_cmake_launcher.sh").read_text()
for token in ("--read-only","--network none","--tmpfs /tmp:",
     "CMAKE_C_COMPILER_LAUNCHER","-frandom-seed=",
     "P2X_V2D_SOURCE_UNIQUE_SEED_STRINGS=PASS",
     "P2X_V2D_FULL_NOS3_BYTE_REPRODUCIBILITY=NOT_TESTED",
     "HOST_NOS3_SOURCE_MUTATION=NO"):
    chk(token in v2d,"V2D_ISOLATED_CMAKE_PROBE_"+token)
# Regression: the first pilot omitted Docker -i, so the heredoc reached EOF in
# bash -s inside Docker and the wrapper emitted a FALSE PASS without running the
# fixture. Require stdin forwarding and exact captured in-container witnesses.
# Second pilot regression: the quoted command substitution containing a heredoc
# failed bash -n on the author's macOS Bash (3.2). Keep a portable direct if/heredoc,
# write only an ephemeral host /tmp log, require observed in-container markers.
chk("if docker run --rm -i --read-only" in v2d,"V2D_DOCKER_STDIN_ATTACHED")
chk('PROBE_LOG="$(mktemp' in v2d and
    """trap 'rm -f -- "$PROBE_LOG"' EXIT""" in v2d,"V2D_EPHEMERAL_LOG_AUTO_CLEANUP")
chk('bash -s >"$PROBE_LOG" 2>&1 <<\'IN_CONTAINER\'' in v2d and
    "IN_CONTAINER\nthen\n" in v2d,"V2D_PORTABLE_HEREDOC_EXIT_CAPTURE")
chk("PROBE_OUTPUT" not in v2d,"V2D_NO_MAC_BASH_NESTED_HEREDOC_REGRESSION")
chk('count="$(grep -Fxc -- "$marker" "$PROBE_LOG" || true)"' in v2d and
    'test "$count" = "1" || fail' in v2d,"V2D_EXACT_INNER_MARKERS_REQUIRED")
outer=v2d.split("IN_CONTAINER\nthen\n",1)
chk(len(outer)==2,"V2D_HEREDOC_TERMINATION")
for token in ("P2X_V2D_SOURCE_UNIQUE_SEED_STRINGS=PASS",
              "P2X_V2D_CMAKE_COMPILER_LAUNCHER_REPEATABILITY=PASS",
              "P2X_V2D_GCNO_HEADER_REPRODUCIBILITY=PASS",
              "P2X_V2D_FULL_NOS3_BYTE_REPRODUCIBILITY=NOT_TESTED"):
    chk(token in outer[1],"V2D_OUTER_GATE_"+token)
chk(v2d.index('echo "P2X_V2D_INNER_GATE=PASS"') <
    v2d.index('echo "P2X_V2D_PROBE=PASS"'),"V2D_NO_FALSE_OUTER_PASS")
chk(subprocess.run(["bash","-n",str(ROOT/"scripts/probe_paper2x_v2d_cmake_launcher.sh")],
                   cwd=ROOT,capture_output=True).returncode==0,"V2D_PORTABLE_STRUCTURE_SYNTAX")
for forbidden in ("--mount","rm -rf","docker pull","make build-fsw","run-ci-noop"):
    chk(forbidden not in v2d,"V2D_DISALLOWED_"+forbidden)
v2dnote=(D/"GCOV_DETERMINISM_DIAGNOSIS_2026-10-03.md").read_text()
for token in ("4294967295","83379182","83381227",
    "10/10","BUILD_BYTE_REPRODUCTION_HOLD",
    "source-specific","No full NOS3 rebuild"):
    chk(token.lower() in v2dnote.lower(),"V2D_GCOV_EVIDENCE_"+token)
v2e=(D/"DETERMINISTIC_V2E_REBUILD_PROPOSAL_2026-10-03.md").read_text()
for token in ("PROSPECTIVE_V2E_DESIGN_READY__NO_FULL_REBUILD_AUTHORIZED_BY_THIS_RECORD",
             "202610030000","p2x-v2e-builder","source/object",
             "9/9 raw exact byte identities","BUILDDATE/HOSTNAME/USER",
             "BUILD_BYTE_REPRODUCTION_HOLD","RUNTIME_UNTESTED"):
    chk(token.lower() in v2e.lower(),"V2E_DESIGN_"+token)
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
"scripts/probe_paper2x_v2d_cmake_launcher.sh",
"paper2x/phase_a/GCOV_DETERMINISM_DIAGNOSIS_2026-10-03.md",
"paper2x/phase_a/DETERMINISTIC_V2E_REBUILD_PROPOSAL_2026-10-03.md",
"scripts/finalize_paper2x_phase_a_v2.py",
"paper2x/phase_a/ENVIRONMENT_V2_AUTHORIZATION_2026-10-03.json",
"scripts/build_paper2x_phase_a_nos3_v2.sh",
"scripts/verify_paper2x_phase_a_v2.py",
"paper2x/phase_a/ENVIRONMENT_V2_ADOPTION_PROPOSAL_2026-10-03.md",
"scripts/probe_paper2x_fortytwo_build_recipe.sh",
"paper2x/phase_a/FORTYTWO_BUILD_VARIANCE_DIAGNOSIS_2026-10-03.md",
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
