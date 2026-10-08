#!/usr/bin/env python3
"""Static-only P2X v2f workspace contract auditor. No workspace IO or execution."""
import sys
import copy
import json
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
GATE = ROOT / "paper2x/phase_a/V2F_NOMINAL_RUNTIME_QUALIFICATION_GATE_2026-10-07.json"
CONTRACT = ROOT / "paper2x/phase_a/V2F_RUNTIME_WORKSPACE_MATERIALIZATION_CONTRACT_2026-10-08.json"
EVIDENCE = "p2xa-nos3-v2f-build-20261007T185149Z-a61cae46f1"
MANIFEST_SHA = "cb5e84137cb090adc8fb24b9b2f78c0d239d2fb93c74393a0e8b71815cc86dee"
DESCRIPTOR_SHA = "08ea45ca09c9a82b5456bea1f93cf325c1a61a8ae4332c5a8dea1b7d4dfbb736"
NINE = [
    "cfg/build/launch.sh",
    "fsw/build/exe/cpu1/core-cpu1",
    "sims/build/bin/nos3-single-simulator",
    "sims/build/bin/nos3-sim-cmdbus-bridge",
    "gsw/build/support/standalone",
    "cfg/build/InOut/Inp_Sim.txt",
    "cfg/build/InOut/Inp_IPC.txt",
    "sims/build/bin/nos_engine_server_config.json",
    "sims/build/bin/nos3-simulator.xml"
]


def require(value: bool, why: str) -> None:
    if not value:
        raise SystemExit("P2X_V2F_WORKSPACE_CONTRACT_HOLD=" + why)


def safe_relative(path: str) -> bool:
    if not isinstance(path, str) or not path:
        return False
    parts = PurePosixPath(path).parts
    return (not path.startswith("/") and
            all(x not in ("", ".", "..") for x in path.split("/")) and
            "\\" not in path and
            not any(x in ("..", ".") for x in parts))


def check_contract(c: dict, gate: dict) -> None:
    review_path = ROOT / "paper2x/phase_a/V2F_RUNTIME_DEPENDENCY_COVERAGE_REVIEW_2026-10-08.json"
    r = json.loads(review_path.read_text(encoding="utf-8"))
    require(r["record_id"] ==
            "P2X-V2F-RUNTIME-DEPENDENCY-AND-MATERIALIZER-VERIFIER-STATIC-REVIEW-2026-10-08" and
            r["classification"] == "STATIC_SOURCE_CODE_REVIEW_ONLY__NO_WORKSPACE_PROOF" and
            r["authority"]["reviewed_head"] == "98b57564c6f448299b63584e32dc0aeabb023725" and
            r["authority"]["validated_workflow_run"] == 1422 and
            r["authority"]["evidence_id"] == EVIDENCE and
            r["authority"]["manifest_sha256"] == MANIFEST_SHA and
            r["authority"]["qualified_raw_artifacts"] == 9 and
            r["authority"]["runtime_tested"] is False,
            "review_parent_authority")
    require(r["qualified_nine_artifacts"] == NINE and
            r["runtime_dependency_closure"] == "UNRESOLVED" and
            r["inventory_coverage"] ==
            "CANDIDATE_DEPENDENCY_CLASSES_IDENTIFIED__ACTUAL_FRESH_WORKSPACE_INVENTORY_NOT_COLLECTED",
            "review_not_actual_inventory")
    classes = r["dependency_classes"]
    require(len(classes) == 11 and
            len(set(x["id"] for x in classes)) == len(classes) and
            all(x["coverage"] in ("RAW_BUILD_9_OF_9_ONLY", "UNVERIFIED") and
                x["runtime_observed"] is False and
                x["workspace_inventory_collected"] is False and
                x["path_examples"] and x["source_trace"]
                for x in classes) and
            sum(x["coverage"] == "RAW_BUILD_9_OF_9_ONLY" for x in classes) == 1,
            "review_coverage_false_claim")
    require(r["legacy_materializer"]["status"] == "NOT_V2F_AUTHORIZED_OR_BOUND" and
            r["legacy_materializer"]["july_exclusions_not_adopted"] is True and
            r["legacy_materializer"]["reuse_without_exact_v2f_review_forbidden"] is True,
            "legacy_materializer_scope")
    builder = r["future_materializer_design"]
    verifier = r["future_independent_verifier_design"]
    require(builder["status"] == "INTERFACE_DESIGN_ONLY__NO_EXECUTABLE_IMPLEMENTATION" and
            builder["source_inventory_emitted"] is False and
            builder["workspace_materialized"] is False and
            builder["allow_implicit_exclusion"] is False and
            builder["publish_before_independent_check"] is False and
            len(builder["required_phases"]) == 8 and
            verifier["status"] == "INDEPENDENT_VERIFIER_NOT_IMPLEMENTED" and
            verifier["separate_implementation_required"] is True and
            verifier["results_observed"] is False and
            len(verifier["negative_controls_required"]) >= 10 and
            len(set(verifier["negative_controls_required"])) ==
            len(verifier["negative_controls_required"]) and
            all(x is False for k,x in r["authorization_scope"].items()
                if k not in ("design_review","static_validation")) and
            r["authorization_scope"]["design_review"] is True and
            r["authorization_scope"]["static_validation"] is True,
            "future_implementation_or_execution_open")
    require(c["record_id"] ==
            "P2X-V2F-RUNTIME-WORKSPACE-MATERIALIZATION-AND-INDEPENDENT-VERIFICATION-CONTRACT-2026-10-08" and
            c["experiment_id"] == "P2X-NOS3-RG-001" and
            c["classification"] == "STATIC_DESIGN_ONLY__MATERIALIZATION_NOT_AUTHORIZED" and
            c["design_parent_head"] == "639d2c89ff922b0c746f4101cbf6f1338bdeb66d", "contract_identity")
    p = c["provenance"]
    require(p["v2f_build_executed_head"] == "8f5faef3830646eae065e8210216a2ed4301316c" and
            p["evidence_id"] == EVIDENCE and
            p["manifest_sha256"] == MANIFEST_SHA and
            p["descriptor_map_sha256"] == DESCRIPTOR_SHA and
            p["raw_identity"] == "9_OF_9" and
            p["independent_build_readback"] == "PASS" and
            p["source_population"] == "primary", "parent_provenance")
    require(p["manifest_relative_path"] ==
            "artifacts/runtime/" + EVIDENCE + "/p2x-v2f-build-manifest.json" and
            p["primary_source_relative_path"] ==
            "artifacts/runtime/" + EVIDENCE + "/primary/source" and
            p["independent_comparison_relative_path"] ==
            "artifacts/runtime/" + EVIDENCE + "/repeat/source",
            "source_selection")
    for key in ("manifest_relative_path", "primary_source_relative_path",
                "independent_comparison_relative_path"):
        require(safe_relative(p[key]), "unsafe_source_path:" + key)
    require(p["pinned_fortytwo_binary_sha256"] ==
            "b4d054bdd8a95dd429201466833fba8403efec4bdef09a9ed7040131dda3006d" and
            p["pinned_oci_image"] ==
            "ivvitc/nos3-64@sha256:06aa945988a7770b759022c2e1f6f2531818c087fe41a4739d3a3a7f2a9dcce2",
            "pin_drift")
    w = c["future_workspace"]
    for name in ("dedicated_run_id_required", "staging_directory_must_be_new",
                 "exclusive_creation_required", "refuse_existing_final_or_staging_path",
                 "atomic_publication_after_verification_required",
                 "never_use_canonical_external_nos3",
                 "never_mount_preserved_v2f_evidence_in_runtime",
                 "never_hardlink_preserved_source_files",
                 "no_fallback_to_legacy_v2_manifest",
                 "no_fallback_to_historical_build_locks",
                 "read_original_build_evidence_only",
                 "require_build_evidence_hash_before_and_after",
                 "source_cannot_be_dereferenced_or_mutated",
                 "no_runtime_container_or_network_created"):
        require(w[name] is True, "workspace_copy_policy:" + name)
    require(w["materialization_performed"] is False and
            w["final_workspace_exists_verified"] is False and
            w["root_namespace"] == "artifacts/runtime" and
            w["source_tree_name"] == "nos3" and
            w["companion_fortytwo_tree_name"] == "fortytwo",
            "workspace_not_created")
    inventory = c["required_fresh_workspace_inventory"]
    require(inventory["nine_qualified_paths"] == NINE and
            len(set(inventory["nine_qualified_paths"])) == 9 and
            all(safe_relative(x) for x in inventory["nine_qualified_paths"]) and
            inventory["runtime_dependency_closure_status"] == "UNRESOLVED" and
            inventory["artifacts_beyond_nine"] ==
            "UNASSESSED__DO_NOT_INFER_RUNTIME_DEPENDENCY_CLOSURE" and
            inventory["required_dependency_coverage"] ==
            "MUST_BE_PROVEN_BEFORE_ANY_MATERIALIZATION_ACCEPTANCE",
            "nine_is_not_runtime_closure")
    for key in ("require_recursive_regular_file_sha256_inventory", "require_file_mode_and_size",
                "require_directory_inventory_and_mode", "require_explicit_symlink_targets",
                "prohibit_symlink_escape", "prohibit_special_files_without_explicit_policy",
                "require_no_hardlink_alias_to_preserved_source",
                "require_git_submodule_metadata_scope_review",
                "preserve_required_runtime_configs_byte_identically",
                "separately_stage_pinned_fortytwo_candidate",
                "verify_fortytwo_binary_sha256",
                "require_cfs_shared_libraries_configuration_tables_and_support_files_review",
                "require_nos3_simulator_resources_and_ipc_inputs_review"):
        require(inventory[key] is True, "inventory_policy:" + key)
    v = c["independent_verification_contract"]
    require(v["implementation_status"] == "NOT_IMPLEMENTED" and
            v["execution_status"] == "NOT_EXECUTED" and
            v["proof_observed"] is False, "independent_verification_not_yet_done")
    for key in ("compare_primary_and_repeat_nine_raw_hashes",
                "exact_source_and_destination_inventory_comparison",
                "verify_all_materialized_regular_file_sha256",
                "verify_modes_sizes_directories_and_symlink_targets",
                "reject_unlisted_destination_paths",
                "reject_missing_expected_paths",
                "reject_source_to_destination_hardlinks",
                "reject_outside_workspace_symlinks",
                "reject_canonical_nos3_aliasing",
                "reject_unreviewed_runtime_mutations",
                "verify_fortytwo_pin_and_binary_hash",
                "verify_original_evidence_unchanged_after_copy",
                "require_independent_verifier_code_separate_from_future_materializer",
                "require_terminal_fail_closed_evidence_and_run_scoped_provenance",
                "allow_zero_unreviewed_variance"):
        require(v[key] is True, "independent_verifier_policy:" + key)
    require(all(value is False for value in c["future_execution_gates"].values()),
            "execution_gate_must_be_closed")
    require(gate["decision"] == "V2F_MANIFEST_SHA256_BOUND__RUNTIME_NOT_AUTHORIZED" and
            gate["parent_v2f_manifest_sha256"] == MANIFEST_SHA and
            gate["parent_v2f_evidence_id"] == EVIDENCE and
            gate["runtime_workspace_design_status"] ==
            "STATIC_CONTRACT_ONLY__NO_WORKSPACE_CREATED" and
            gate["runtime_workspace_contract"] ==
            "paper2x/phase_a/V2F_RUNTIME_WORKSPACE_MATERIALIZATION_CONTRACT_2026-10-08.json" and
            gate["runtime_workspace_materialization_authorized"] is False and
            gate["runtime_workspace_materialized"] is False and
            gate["runtime_workspace_independent_verification_implemented"] is False and
            gate["runtime_workspace_independent_verification_executed"] is False and
            gate["runtime_workspace_runtime_authorized"] is False and
            gate["execution_authorized"] is False and
            all(gate["authorization_scope"][key] is False for key in (
                "nominal_runtime_execution","benign_internal_cfs_noop","cosmos",
                "faults","scientific_observations","final_environment_acceptance",
                "merge_pr215")),
            "tracked_gate_not_fail_closed")


def self_test(c: dict, gate: dict) -> None:
    check_contract(c, gate)
    trials = (
        ("runtime_enabled", lambda q: q["future_execution_gates"].__setitem__(
            "nominal_runtime_execution_authorized", True)),
        ("manifest_drift", lambda q: q["provenance"].__setitem__(
            "manifest_sha256", "0" * 64)),
        ("path_traversal", lambda q: q["provenance"].__setitem__(
            "primary_source_relative_path", "../untrusted")),
        ("missing_nine", lambda q: q["required_fresh_workspace_inventory"].__setitem__(
            "nine_qualified_paths", NINE[:-1])),
        ("closure_false_claim", lambda q: q["required_fresh_workspace_inventory"].__setitem__(
            "runtime_dependency_closure_status", "PASS")),
        ("workspace_false_claim", lambda q: q["future_workspace"].__setitem__(
            "materialization_performed", True)),
        ("verifier_false_claim", lambda q: q["independent_verification_contract"].__setitem__(
            "proof_observed", True)),
    )
    for label, change in trials:
        test = copy.deepcopy(c)
        change(test)
        try:
            check_contract(test, gate)
        except SystemExit as err:
            require("P2X_V2F_WORKSPACE_CONTRACT_HOLD=" in str(err),
                    "negative_control_wrong_failure:" + label)
        else:
            require(False, "negative_control_accepted:" + label)
    print("P2X_V2F_WORKSPACE_CONTRACT_NEGATIVE_CONTROLS=PASS")


def main() -> None:
    mode = sys.argv[1:]
    if mode in (["--materialize"], ["--verify-workspace"], ["--run"]):
        raise SystemExit("P2X_V2F_WORKSPACE_EXECUTION_HOLD=STATIC_DESIGN_ONLY")
    require(mode in (["--inspect"], ["--self-test"]),
            "usage:--inspect_or_--self-test__execution_denied")
    c = json.loads(CONTRACT.read_text(encoding="utf-8"))
    gate = json.loads(GATE.read_text(encoding="utf-8"))
    check_contract(c, gate)
    if mode == ["--self-test"]:
        self_test(c, gate)
    print("P2X_V2F_WORKSPACE_CONTRACT_STATIC=PASS")
    print("P2X_V2F_WORKSPACE_MATERIALIZATION=NOT_AUTHORIZED")
    print("P2X_V2F_INDEPENDENT_WORKSPACE_VERIFICATION=NOT_EXECUTED")
    print("P2X_V2F_NOMINAL_RUNTIME=NOT_AUTHORIZED")
    print("P2X_V2F_SCIENTIFIC_OBSERVATIONS=NO")
    print("P2X_V2F_FINAL_ENVIRONMENT_ACCEPTANCE=NO")


if __name__ == "__main__":
    main()
