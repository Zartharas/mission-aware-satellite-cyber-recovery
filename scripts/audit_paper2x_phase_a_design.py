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
# Prospective v2e implementation is allowed for STATIC VALIDATION ONLY. Its tracked
# execution gate must stay closed until a separate explicit author decision.
v2e_gate=json.loads((D/"V2E_OFFLINE_BUILD_EXECUTION_GATE_2026-10-03.json").read_text())
chk(v2e_gate["record_id"]==
    "P2X-PHASE-A-V2E-OFFLINE-BUILD-EXECUTION-GATE-2026-10-03" and
    v2e_gate["experiment_id"]=="P2X-NOS3-RG-001","V2E_DISTINCT_SCOPE")
v2e_closed=(v2e_gate["decision"]=="DESIGN_AND_STATIC_VALIDATION_ONLY" and
            v2e_gate["execution_authorized"] is False and
            v2e_gate["authorization_scope"]["offline_full_build"] is False)
v2e_authorized=(v2e_gate["decision"]=="AUTHOR_EXPLICITLY_APPROVED_V2E_OFFLINE_REBUILD" and
                v2e_gate["execution_authorized"] is True and
                v2e_gate["authorization_scope"]["offline_full_build"] is True)
v2e_held=(v2e_gate["decision"]=="V2E_EXECUTED_HOLD__V2F_NOT_AUTHORIZED" and
          v2e_gate["execution_authorized"] is False and
          v2e_gate["authorization_scope"]["offline_full_build"] is False)
chk((v2e_closed or v2e_authorized or v2e_held) and
    v2e_gate["authorization_scope"]["nominal_runtime"] is False and
    v2e_gate["authorization_scope"]["cosmos"] is False and
    v2e_gate["authorization_scope"]["faults"] is False and
    v2e_gate["authorization_scope"]["merge_pr215"] is False and
    v2e_gate["environment_final_acceptance"] is False,"V2E_AUTHORIZATION_SCOPE_FIREWALL")
launcher=(ROOT/"scripts/p2x_v2e_seed_launcher.py").read_text()
builder=(ROOT/"scripts/build_paper2x_phase_a_nos3_v2e.py").read_text()
v2e_readback=(ROOT/"scripts/verify_paper2x_phase_a_v2e.py").read_text()
for t in ("P2X-v2e\\x00","P2X_V2E_SEED_SOURCE=", "-frandom-seed=",
          "source", "obj", "os.execv(compiler", "path_outside_fixed_container_root"):
    chk(t in launcher,"V2E_STABLE_SOURCE_AND_OBJECT_SEED_"+t)
for t in ("--inspect", "--self-test", "--build",
          "separate_v2e_authorization_absent__no_build",
          'if mode == ["--build"]:', "execution_authorized",
          "shutil.copytree(source, target, symlinks=True, ignore=ignore_builds(source))",
          "staged_submodule_worktree_external_alias:",
          "original_v2_hold_manifest_sha256", "p2xa-nos3-v2e-build-",
          "BUILDDATE=", "HOSTNAME=", "USER=",
          "CMAKE_C_COMPILER_LAUNCHER=/usr/bin/python3;",
          "--network", "--hostname", "BUILD_HOST",
          "p2x_v2e_seed_launcher.py", "seed_pairs", "primary",
          "repeat", "nine_raw_SHA_mismatch_preserve_both_new_builds",
          "verify_paper2x_phase_a_v2e.py", "no_runtime_performed"):
    chk(t in builder,"V2E_BUILDER_BOUNDARY_"+t)
for forbidden in ("rm -rf", "make clean", "scripts/build_nominal_nos3.sh",
                  "run-ci-noop", "docker pull"):
    chk(forbidden not in builder,"V2E_NO_DESTRUCTIVE_OR_RUNTIME_COMMAND_"+forbidden)
for t in ("p2x-v2e-build-manifest.json",
          "V2E_DUAL_OFFLINE_BUILD_BYTE_IDENTITY_PASS__RUNTIME_UNTESTED",
          "original_v2_hold_manifest_sha256",
          "OLD_PRIMARY", "OLD_REPEAT", "historical_locks_sha256_before",
          "historical_locks_sha256_after", "seed_value",
          "source_check", "copied_submodule_external_worktree:", "raw_sha_or_byte_size_difference:",
          "P2X_V2E_INDEPENDENT_NINE_RAW_SHA256_READBACK=PASS",
          "P2X_V2E_ENVIRONMENT_FINAL_ACCEPTANCE=NO"):
    chk(t in v2e_readback,"V2E_INDEPENDENT_READBACK_"+t)
chk("from build_paper2x_phase_a_nos3_v2e" not in v2e_readback and
    "import build_paper2x_phase_a_nos3_v2e" not in v2e_readback,
    "V2E_READBACK_NOT_INDEPENDENT")
for script,marker in (
    ("p2x_v2e_seed_launcher.py","P2X_V2E_SOURCE_OBJECT_SEED_SELF_TEST=PASS"),
    ("build_paper2x_phase_a_nos3_v2e.py","P2X_V2E_EXCLUDE_OLD_BUILD_OUTPUTS_SELF_TEST=PASS"),
    ("verify_paper2x_phase_a_v2e.py","P2X_V2E_RAW_BYTE_NEGATIVE_CONTROL=PASS")):
    out=subprocess.run(["python3",str(ROOT/"scripts"/script),"--self-test"],
                       capture_output=True,text=True,cwd=ROOT)
    chk(out.returncode==0 and marker in out.stdout,
        "V2E_STATIC_SELF_TEST_"+script+":"+out.stderr[:150])
if v2e_closed or v2e_held:
    no_build=subprocess.run(["python3",str(ROOT/"scripts/build_paper2x_phase_a_nos3_v2e.py"),
                             "--build"],capture_output=True,text=True,cwd=ROOT)
    chk(no_build.returncode!=0 and
        "P2X_V2E_BUILDER_HOLD=separate_v2e_authorization_absent__no_build" in
        no_build.stdout+no_build.stderr,"V2E_PRE_SIDE_EFFECT_BUILD_DENIAL")
    print("P2X_V2E_FULL_OFFLINE_BUILD=" +
          ("HOLD_PRESERVED_NO_RERUN" if v2e_held else "NOT_AUTHORIZED"))
else:
    # Once the author opens the host-only build gate, CI must never invoke --build:
    # doing so could turn a static workflow into an experiment on a capable runner.
    print("P2X_V2E_PRE_SIDE_EFFECT_BUILD_DENIAL=NOT_RUN_AFTER_AUTHOR_AUTHORIZATION")
    print("P2X_V2E_FULL_OFFLINE_BUILD=AUTHOR_AUTHORIZED_HOST_ONLY")
print("P2X_V2E_IMPLEMENTATION_AND_AUTHORIZATION_AUDIT=PASS")

v2f=(D/"V2F_GIT_METADATA_DETERMINISM_PROPOSAL_2026-10-05.md").read_text()
for token in ("V2F_DESIGN_AND_STATIC_VALIDATION_ONLY__NO_BUILD_AUTHORIZED",
              "GIT_CONFIG_COUNT=1","GIT_CONFIG_KEY_0=safe.directory",
              "GIT_CONFIG_VALUE_0=/work/nos3","v1_07_05",
              "v0.0.13-119-gaa5559c","9/9",
              "V2F_DUAL_OFFLINE_BUILD_BYTE_IDENTITY_PASS__RUNTIME_UNTESTED"):
    chk(token.lower() in v2f.lower(),"V2F_DESIGN_"+token)
v2f_gate=json.loads((D/"V2F_OFFLINE_BUILD_EXECUTION_GATE_2026-10-05.json").read_text())
chk(v2f_gate["record_id"]==
    "P2X-PHASE-A-V2F-OFFLINE-BUILD-EXECUTION-GATE-2026-10-05" and
    v2f_gate["experiment_id"]=="P2X-NOS3-RG-001","V2F_DISTINCT_SCOPE")
v2f_design_only=(v2f_gate["decision"]=="DESIGN_AND_STATIC_VALIDATION_ONLY" and
                 v2f_gate.get("probe_authorized",False) is False and
                 v2f_gate["authorization_scope"]["read_only_host_probe"] is False)
v2f_probe_authorized=(v2f_gate["decision"]==
    "AUTHOR_EXPLICITLY_APPROVED_V2F_READ_ONLY_HOST_PROBE" and
    v2f_gate.get("probe_authorized") is True and
    v2f_gate["authorization_scope"]["read_only_host_probe"] is True)
v2f_probe_pass=(v2f_gate["decision"]==
    "V2F_READ_ONLY_PROBE_PASS__FULL_BUILD_NOT_AUTHORIZED" and
    v2f_gate.get("probe_authorized") is False and
    v2f_gate.get("probe_result")=="PASS" and
    v2f_gate["authorization_scope"]["read_only_host_probe"] is False and
    v2f_gate.get("descriptor_map_sha256")==
    "499525c90430ae0dd17fc297be0388b2eae51fdb6623f3d338b0a2f392460278")
v2f_implementation_static=(v2f_gate["decision"]==
    "V2F_IMPLEMENTATION_AND_STATIC_VALIDATION_ONLY__FULL_BUILD_NOT_AUTHORIZED" and
    v2f_gate.get("probe_authorized") is False and
    v2f_gate.get("probe_result")=="PASS" and
    v2f_gate["authorization_scope"].get("v2f_implementation") is True and
    v2f_gate["authorization_scope"]["read_only_host_probe"] is False and
    v2f_gate.get("descriptor_map_sha256")==
    "499525c90430ae0dd17fc297be0388b2eae51fdb6623f3d338b0a2f392460278")
v2f_build_authorized=(v2f_gate["decision"]==
    "AUTHOR_EXPLICITLY_APPROVED_V2F_OFFLINE_REBUILD" and
    v2f_gate.get("probe_authorized") is False and
    v2f_gate.get("probe_result")=="PASS" and
    v2f_gate.get("implementation_static_validation")=="PASS" and
    v2f_gate["authorization_scope"].get("v2f_implementation") is True and
    v2f_gate["authorization_scope"]["read_only_host_probe"] is False and
    v2f_gate.get("descriptor_map_sha256")==
    "499525c90430ae0dd17fc297be0388b2eae51fdb6623f3d338b0a2f392460278")
chk((v2f_design_only or v2f_probe_authorized or v2f_probe_pass or
     v2f_implementation_static or v2f_build_authorized) and
    v2f_gate["execution_authorized"] is v2f_build_authorized and
    v2f_gate["authorization_scope"]["v2f_design"] is True and
    v2f_gate["authorization_scope"]["static_validation"] is True and
    v2f_gate["authorization_scope"]["offline_full_build"] is v2f_build_authorized and
    v2f_gate["authorization_scope"]["nominal_runtime"] is False and
    v2f_gate["authorization_scope"]["cosmos"] is False and
    v2f_gate["authorization_scope"]["faults"] is False and
    v2f_gate["authorization_scope"]["merge_pr215"] is False and
    v2f_gate["environment_final_acceptance"] is False,
    "V2F_PROBE_SCOPE_FIREWALL")
v2f_static=(ROOT/"scripts/p2x_v2f_git_metadata_gate.py").read_text()
for token in ("GIT_CONFIG_COUNT","GIT_CONFIG_KEY_0","safe.directory",
              "GIT_CONFIG_VALUE_0","/work/nos3","v1_07_05",
              "v0.0.13-119-gaa5559c","READ_ONLY_HOST_PROBE=",
              "P2X_V2F_FULL_BUILD=","AUTHORIZED_NOT_RUN","NOT_AUTHORIZED"):
    chk(token in v2f_static,"V2F_STATIC_GATE_"+token)
for forbidden in ("docker run","make build-fsw","run-ci-noop","docker pull","rm -rf"):
    chk(forbidden not in v2f_static,"V2F_STATIC_NO_EXECUTION_"+forbidden)
v2f_test=subprocess.run(
    ["python3",str(ROOT/"scripts/p2x_v2f_git_metadata_gate.py"),"--self-test"],
    capture_output=True,text=True,cwd=ROOT)
chk(v2f_test.returncode==0 and
    "P2X_V2F_SAFE_DIRECTORY_ENV_CONTRACT=PASS" in v2f_test.stdout and
    (("P2X_V2F_EXECUTION_AUTHORIZATION=FULL_BUILD_AUTHORIZED_HOST_ONLY" in v2f_test.stdout)
     if v2f_build_authorized else
     ("P2X_V2F_EXECUTION_AUTHORIZATION=FULL_BUILD_CLOSED" in v2f_test.stdout)) and
    ("P2X_V2F_READ_ONLY_HOST_PROBE=AUTHORIZED" in v2f_test.stdout
     if v2f_probe_authorized else
     "P2X_V2F_READ_ONLY_HOST_PROBE=PASS_RECORDED_CLOSED" in v2f_test.stdout
     if (v2f_probe_pass or v2f_implementation_static or v2f_build_authorized) else
     "P2X_V2F_READ_ONLY_HOST_PROBE=NOT_AUTHORIZED" in v2f_test.stdout),
    "V2F_STATIC_SELF_TEST:"+v2f_test.stderr[:180])
print("P2X_V2F_DESIGN_AND_STATIC_VALIDATION_AUDIT=PASS")

v2f_probe=(ROOT/"scripts/probe_paper2x_v2f_git_metadata.py").read_text()
for token in ("--read-only","--network","none","GIT_CONFIG_COUNT=1",
              "GIT_CONFIG_KEY_0=safe.directory","GIT_CONFIG_VALUE_0=/work/nos3",
              "mission_vars.cache","dependency_descriptors","TRIALS = 5",
              "P2X_V2F_DEPENDENCY_DESCRIPTOR_MAP_REPEATABILITY=PASS",
              "P2X_V2F_FULL_BUILD_AUTHORIZATION=NO",
              "P2X_V2F_ENVIRONMENT_FINAL_ACCEPTANCE=NO"):
    chk(token in v2f_probe,"V2F_READ_ONLY_PROBE_"+token)
for forbidden in ("make build-fsw","make build-sim","make build-cryptolib",
                  "run-ci-noop","docker pull","rm -rf"):
    chk(forbidden not in v2f_probe,"V2F_READ_ONLY_PROBE_NO_"+forbidden)
probe_test=subprocess.run(
    ["python3",str(ROOT/"scripts/probe_paper2x_v2f_git_metadata.py"),"--self-test"],
    capture_output=True,text=True,cwd=ROOT)
chk(probe_test.returncode==0 and
    "P2X_V2F_PROBE_STATIC_SELF_TEST=PASS" in probe_test.stdout and
    "P2X_V2F_BUILD_EXECUTED=NO" in probe_test.stdout,
    "V2F_READ_ONLY_PROBE_STATIC_SELF_TEST:"+probe_test.stderr[:180])
print("P2X_V2F_READ_ONLY_PROBE_STATIC_AUDIT=PASS")

v2f_desc=(ROOT/"scripts/p2x_v2f_descriptor_map.py").read_text()
v2f_builder=(ROOT/"scripts/build_paper2x_phase_a_nos3_v2f.py").read_text()
v2f_readback=(ROOT/"scripts/verify_paper2x_phase_a_v2f.py").read_text()
for token in ("mission_vars.cache","GIT_CONFIG_COUNT","GIT_CONFIG_KEY_0",
              "safe.directory","GIT_CONFIG_VALUE_0","/work/nos3",
              "git_safe_directory_scope_too_narrow","safe_directories",
              "components/onair/fsw","v1_07_05","v0.0.13-119-gaa5559c",
              "dependency_descriptors"):
    chk(token in v2f_desc,"V2F_DESCRIPTOR_HELPER_"+token)
for forbidden in ("docker run","make build-fsw","run-ci-noop","docker pull","rm -rf"):
    chk(forbidden not in v2f_desc,"V2F_DESCRIPTOR_HELPER_NO_"+forbidden)
for token in ("--inspect","--self-test","--build",
              "separate_v2f_authorization_absent__no_build",
              "V2F_IMPLEMENTATION_AND_STATIC_VALIDATION_ONLY__FULL_BUILD_NOT_AUTHORIZED",
              "GIT_CONFIG_COUNT=","safe.directory",
              "GIT_CONFIG_VALUE_0=/work/nos3","submodule_paths_from_status",
              "safe_directory_paths","configure_and_descriptor",
              "prebuild_dependency_descriptor_maps_differ",
              "p2xa-nos3-v2f-build-","p2x-v2f-build-manifest.json",
              "V2F_DUAL_OFFLINE_BUILD_BYTE_IDENTITY_PASS__RUNTIME_UNTESTED",
              "nine_raw_SHA_mismatch_preserve_both_new_builds",
              "verify_paper2x_phase_a_v2f.py","old_v2e_evidence_overwritten",
              "no_runtime_performed","extra_options: list[str] | None",
              "descriptor_helper_mount_after_image","docker_option_after_image",
              "ROOT_PLUS_ALL_REGISTERED_RECURSIVE_SUBMODULE_WORKTREES",
              "cmake -DCMAKE_INSTALL_PREFIX=exe -DCMAKE_BUILD_TYPE=debug ../cfe",
              "make --no-print-directory -C fsw/build mission-install",
              "CFS_APP_PATH=../components","MISSION_DEFS=../cfg/build/",
              "MISSIONCONFIG=../cfg/build/nos3",
              "descriptor_gate_not_before_compilation",
              "git_safe_directories"):
    chk(token in v2f_builder,"V2F_BUILDER_"+token)
for forbidden in ("rm -rf","make clean","scripts/build_nominal_nos3.sh",
                  "run-ci-noop","docker pull"):
    chk(forbidden not in v2f_builder,"V2F_BUILDER_NO_"+forbidden)
for token in ("p2x-v2f-build-manifest.json",
              "V2F_DUAL_OFFLINE_BUILD_BYTE_IDENTITY_PASS__RUNTIME_UNTESTED",
              "git_safe_directory_injected_ephemerally","git_safe_directories",
              "root_plus_registered_recursive_submodule_worktrees",
              "cfs_app_path","mission_defs","missionconfig",
              "prebuild_dependency_descriptor_maps_identical",
              "dependency_descriptor_map_sha256","probe_descriptor_map_sha256",
              "preserved_v2e_manifest_sha256","onair_version_not_stabilized",
              "P2X_V2F_INDEPENDENT_NINE_RAW_SHA256_READBACK=PASS",
              "P2X_V2F_DEPENDENCY_DESCRIPTOR_MAP_READBACK=PASS",
              "P2X_V2F_ENVIRONMENT_FINAL_ACCEPTANCE=NO"):
    chk(token in v2f_readback,"V2F_READBACK_"+token)
chk("from build_paper2x_phase_a_nos3_v2f" not in v2f_readback and
    "import build_paper2x_phase_a_nos3_v2f" not in v2f_readback,
    "V2F_READBACK_NOT_INDEPENDENT")
for script,marker in (
    ("p2x_v2f_descriptor_map.py","P2X_V2F_DESCRIPTOR_HELPER_SELF_TEST=PASS"),
    ("build_paper2x_phase_a_nos3_v2f.py","P2X_V2F_DESCRIPTOR_MAP_GATE_SELF_TEST=PASS"),
    ("verify_paper2x_phase_a_v2f.py","P2X_V2F_RAW_BYTE_NEGATIVE_CONTROL=PASS")):
    out=subprocess.run(["python3",str(ROOT/"scripts"/script),"--self-test"],
                       capture_output=True,text=True,cwd=ROOT)
    chk(out.returncode==0 and marker in out.stdout,
        "V2F_IMPLEMENTATION_SELF_TEST_"+script+":"+out.stderr[:160])
if not v2f_build_authorized:
    no_v2f_build=subprocess.run(
        ["python3",str(ROOT/"scripts/build_paper2x_phase_a_nos3_v2f.py"),"--build"],
        capture_output=True,text=True,cwd=ROOT)
    chk(no_v2f_build.returncode!=0 and
        "P2X_V2F_BUILDER_HOLD=separate_v2f_authorization_absent__no_build" in
        no_v2f_build.stdout+no_v2f_build.stderr,
        "V2F_PRE_SIDE_EFFECT_BUILD_DENIAL")
    print("P2X_V2F_FULL_OFFLINE_BUILD=NOT_AUTHORIZED")
else:
    print("P2X_V2F_PRE_SIDE_EFFECT_BUILD_DENIAL=NOT_RUN_AFTER_AUTHOR_AUTHORIZATION")
    print("P2X_V2F_FULL_OFFLINE_BUILD=AUTHOR_AUTHORIZED_HOST_ONLY")
print("P2X_V2F_IMPLEMENTATION_AND_STATIC_VALIDATION_AUDIT=PASS")



handoff=(D/"P2X_V2E_CONTINUATION_HANDOFF_2026-10-04.md").read_text()
for token in ("22404f78ecfb73b57d56a6a6817c96232e9ef653",
              "37176565708","BUILD_BYTE_REPRODUCTION_HOLD",
              "execution_authorized=false","9/9",
              "separate_v2e_authorization_absent__no_build",
              "P2X_V2D_INNER_GATE=PASS","draft/unmerged"):
    chk(token.lower() in handoff.lower(),"V2E_HANDOFF_"+token)
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
"paper2x/phase_a/P2X_V2E_CONTINUATION_HANDOFF_2026-10-04.md",
"scripts/p2x_v2e_seed_launcher.py",
"scripts/build_paper2x_phase_a_nos3_v2e.py",
"scripts/verify_paper2x_phase_a_v2e.py",
"paper2x/phase_a/V2E_OFFLINE_BUILD_EXECUTION_GATE_2026-10-03.json",
"paper2x/phase_a/V2F_GIT_METADATA_DETERMINISM_PROPOSAL_2026-10-05.md",
"paper2x/phase_a/V2F_OFFLINE_BUILD_EXECUTION_GATE_2026-10-05.json",
"scripts/p2x_v2f_git_metadata_gate.py",
"scripts/probe_paper2x_v2f_git_metadata.py",
"scripts/p2x_v2f_descriptor_map.py",
"scripts/build_paper2x_phase_a_nos3_v2f.py",
"scripts/verify_paper2x_phase_a_v2f.py",
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
