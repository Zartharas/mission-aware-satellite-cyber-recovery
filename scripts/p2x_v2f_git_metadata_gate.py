#!/usr/bin/env python3
"""Static v2f Git-metadata control validator.

This script performs no Docker execution, no build, no source mutation and no runtime.
It validates only the prospective v2f control contract and closed authorization gate.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
D = ROOT / "paper2x" / "phase_a"
GATE = D / "V2F_OFFLINE_BUILD_EXECUTION_GATE_2026-10-05.json"
PROPOSAL = D / "V2F_GIT_METADATA_DETERMINISM_PROPOSAL_2026-10-05.md"

SAFE_DIR = "/work/nos3"
NOS3 = "5a3bdee6be9a2c67fdf994ae6db56d5c60395302"
NOS3_DESC = "v1_07_05"
ONAIR = "aa5559c0f234eba263041b6007573f16870194e5"
ONAIR_DESC = "v0.0.13-119-gaa5559c"

ENV_CONFIG = {
    "GIT_CONFIG_COUNT": "1",
    "GIT_CONFIG_KEY_0": "safe.directory",
    "GIT_CONFIG_VALUE_0": SAFE_DIR,
}


def hold(why: str) -> None:
    raise SystemExit("P2X_V2F_STATIC_HOLD=" + why)


def require(ok: bool, why: str) -> None:
    if not ok:
        hold(why)


def validate_gate() -> dict:
    gate = json.loads(GATE.read_text(encoding="utf-8"))
    require(gate["record_id"] ==
            "P2X-PHASE-A-V2F-OFFLINE-BUILD-EXECUTION-GATE-2026-10-05",
            "wrong_gate_record")
    require(gate["experiment_id"] == "P2X-NOS3-RG-001",
            "wrong_experiment")
    design_only = gate["decision"] == "DESIGN_AND_STATIC_VALIDATION_ONLY"
    probe_authorized = gate["decision"] == "AUTHOR_EXPLICITLY_APPROVED_V2F_READ_ONLY_HOST_PROBE"
    probe_pass = gate["decision"] == "V2F_READ_ONLY_PROBE_PASS__FULL_BUILD_NOT_AUTHORIZED"
    implementation_static = gate["decision"] == "V2F_IMPLEMENTATION_AND_STATIC_VALIDATION_ONLY__FULL_BUILD_NOT_AUTHORIZED"
    build_authorized = gate["decision"] == "AUTHOR_EXPLICITLY_APPROVED_V2F_OFFLINE_REBUILD"
    require(design_only or probe_authorized or probe_pass or implementation_static or
            build_authorized, "invalid_decision")
    require(gate["execution_authorized"] is build_authorized,
            "execution_authorization_state")
    scope = gate["authorization_scope"]
    require(scope["v2f_design"] is True and
            scope["static_validation"] is True,
            "design_static_scope_missing")
    require(scope["read_only_host_probe"] is probe_authorized and
            gate.get("probe_authorized", False) is probe_authorized and
            (gate.get("probe_result") == "PASS"
             if (probe_pass or implementation_static or build_authorized) else True) and
            scope["offline_full_build"] is build_authorized and
            scope["nominal_runtime"] is False and
            scope["cosmos"] is False and
            scope["faults"] is False and
            scope["merge_pr215"] is False,
            "execution_runtime_or_merge_scope_open")
    require(gate["environment_final_acceptance"] is False,
            "final_acceptance_open")
    require(gate["proposed_git_safe_directory"] == SAFE_DIR,
            "safe_directory_drift")
    require(gate["expected_nos3_describe"] == NOS3_DESC,
            "nos3_descriptor_drift")
    require(gate["expected_onair_submodule_head"] == ONAIR,
            "onair_head_drift")
    require(gate["expected_onair_submodule_describe"] == ONAIR_DESC,
            "onair_descriptor_drift")
    return gate


def validate_proposal() -> None:
    text = PROPOSAL.read_text(encoding="utf-8")
    required = (
        "V2F_DESIGN_AND_STATIC_VALIDATION_ONLY__NO_BUILD_AUTHORIZED",
        "GIT_CONFIG_COUNT=1",
        "GIT_CONFIG_KEY_0=safe.directory",
        "GIT_CONFIG_VALUE_0=/work/nos3",
        "v1_07_05",
        "v0.0.13-119-gaa5559c",
        "9/9",
        "V2F_DUAL_OFFLINE_BUILD_BYTE_IDENTITY_PASS__RUNTIME_UNTESTED",
        "separate explicit author decision",
    )
    for token in required:
        require(token.lower() in text.lower(), "proposal_missing:" + token)


def self_test() -> None:
    validate_gate()
    validate_proposal()

    require(ENV_CONFIG == {
        "GIT_CONFIG_COUNT": "1",
        "GIT_CONFIG_KEY_0": "safe.directory",
        "GIT_CONFIG_VALUE_0": "/work/nos3",
    }, "env_config_contract")

    require(re.fullmatch(r"[0-9a-f]{40}", NOS3) is not None,
            "nos3_pin_format")
    require(re.fullmatch(r"[0-9a-f]{40}", ONAIR) is not None,
            "onair_pin_format")
    require(NOS3_DESC == "v1_07_05" and
            ONAIR_DESC == "v0.0.13-119-gaa5559c",
            "descriptor_fixture")

    print("P2X_V2F_SAFE_DIRECTORY_ENV_CONTRACT=PASS")
    print("P2X_V2F_DESCRIPTOR_EXPECTATION_SELF_TEST=PASS")
    g = validate_gate()
    probe_authorized = g["decision"] == "AUTHOR_EXPLICITLY_APPROVED_V2F_READ_ONLY_HOST_PROBE"
    probe_pass = g["decision"] == "V2F_READ_ONLY_PROBE_PASS__FULL_BUILD_NOT_AUTHORIZED"
    implementation_static = g["decision"] == "V2F_IMPLEMENTATION_AND_STATIC_VALIDATION_ONLY__FULL_BUILD_NOT_AUTHORIZED"
    build_authorized = g["decision"] == "AUTHOR_EXPLICITLY_APPROVED_V2F_OFFLINE_REBUILD"
    print("P2X_V2F_EXECUTION_AUTHORIZATION=" +
          ("FULL_BUILD_AUTHORIZED_HOST_ONLY" if build_authorized
           else "FULL_BUILD_CLOSED"))
    print("P2X_V2F_READ_ONLY_HOST_PROBE=" +
          ("AUTHORIZED" if probe_authorized else
           "PASS_RECORDED_CLOSED" if
           (probe_pass or implementation_static or build_authorized)
           else "NOT_AUTHORIZED"))
    print("P2X_V2F_DOCKER_EXECUTED=NO")
    print("P2X_V2F_BUILD_EXECUTED=NO")


def inspect() -> None:
    gate = validate_gate()
    validate_proposal()
    print("P2X_V2F_STATIC_INSPECTION=PASS")
    print("P2X_V2F_PARENT_V2E_RESULT=" + gate["parent_v2e_result"])
    print("P2X_V2F_SAFE_DIRECTORY=" + SAFE_DIR)
    print("P2X_V2F_EXPECTED_NOS3_DESCRIBE=" + NOS3_DESC)
    print("P2X_V2F_EXPECTED_ONAIR_SUBMODULE_DESCRIBE=" + ONAIR_DESC)
    print("P2X_V2F_READ_ONLY_HOST_PROBE=" +
          ("AUTHORIZED" if gate["decision"] ==
           "AUTHOR_EXPLICITLY_APPROVED_V2F_READ_ONLY_HOST_PROBE"
           else "PASS_RECORDED_CLOSED" if gate["decision"] in (
               "V2F_READ_ONLY_PROBE_PASS__FULL_BUILD_NOT_AUTHORIZED",
               "V2F_IMPLEMENTATION_AND_STATIC_VALIDATION_ONLY__FULL_BUILD_NOT_AUTHORIZED",
               "AUTHOR_EXPLICITLY_APPROVED_V2F_OFFLINE_REBUILD")
           else "NOT_AUTHORIZED"))
    print("P2X_V2F_FULL_BUILD=" +
          ("AUTHORIZED_NOT_RUN" if gate["decision"] ==
           "AUTHOR_EXPLICITLY_APPROVED_V2F_OFFLINE_REBUILD"
           else "NOT_AUTHORIZED"))
    print("P2X_V2F_RUNTIME=NOT_AUTHORIZED")


def main() -> None:
    args = sys.argv[1:] or ["--inspect"]
    require(len(args) == 1 and args[0] in ("--inspect", "--self-test"),
            "usage")
    if args[0] == "--self-test":
        self_test()
    else:
        inspect()


if __name__ == "__main__":
    main()
