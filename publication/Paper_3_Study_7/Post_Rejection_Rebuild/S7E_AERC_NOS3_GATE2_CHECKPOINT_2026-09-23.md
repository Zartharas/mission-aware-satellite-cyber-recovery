# S7E-AERC-001 NOS3 Gate-2 Feasibility Checkpoint — 2026-09-23

**Experiment:** `S7E-AERC-001`  
**Branch:** `paper3/s7e-aerc-implementation-feasibility-20260922`  
**Pull request:** #167  
**Qualification head:** `178fdbd4871c2f6f89b62a8f4f0d2ce826853188`  
**Phase:** pre-freeze implementation/feasibility only  
**Canonical scientific execution:** NOT AUTHORIZED

## Result

**Gate 2 — bounded NOS3 v1.7.5 flight-software/test + simulator build feasibility: PASS**

This checkpoint records engineering feasibility only.

## Exact evidence

- NOS3 release: `v1_07_05` / 1.7.5
- NOS3 commit: `5a3bdee6be9a2c67fdf994ae6db56d5c60395302`
- workflow: `Study 7E bounded NOS3 feasibility`
- workflow ID: `365185951`
- run ID: `35870689230` — `success`
- job ID: `107213663081` — `success`
- artifact ID: `10755347006`
- artifact digest: `sha256:28397de31e1eed3a37304f9e552ba936222a1a6d53555c28585c817485d4ef38`
- bounded container image declared by the workflow: `ivvitc/nos3-64:20260619`

The job successfully completed:

1. exact NOS3 checkout and recursive submodule initialization;
2. pinned gitlink assertions for cFE, OSAL, PSP, SBN, and CryptoLib;
3. `make config`;
4. `make build-test`;
5. `make test-fsw`;
6. `make build-sim`;
7. bounded stop-point assertions and provenance artifact upload.

The run explicitly recorded:

- `study7e_scientific_scenarios_executed=0`;
- `scientific_results_generated=false`;
- `nos3_bounded_feasibility=PASS`.

## Key pinned NOS3 gitlinks confirmed

- cFE: `87e273743f3d07ed9216462b461e9f398ff96c87`
- OSAL: `08a79bb6ac02b9ced8aa555853ecdd96e5ebc1a7`
- PSP: `d0a5d6fa4093d473a929fde42a0983e489d89d4a`
- SBN: `240f90f56641d43e5db1dae457d7ef8772a1c659`
- CryptoLib: `d4f91523b7f2f247b89bbde9e156cd8420e2cb86`

## Current upstream context

As checked on 2026-09-23, the current official GitHub releases are:

- NASA cFS: `v7.0.1`;
- NASA NOS3: `v1_07_05` / 1.7.5.

Thus the Study-7E candidate pins remain aligned with the current official releases at this checkpoint.

## Warnings observed

The successful NOS3 run emitted non-fatal compiler warnings in `hwlib.h` and a GitHub Actions Node.js deprecation warning affecting `actions/checkout@v4` and `actions/upload-artifact@v4`. These did not fail the bounded build but remain maintenance/tooling considerations for a future frozen environment.

## Evidence boundary

Gate 2 establishes that the pinned NOS3 release and its native pinned dependency graph can be configured, unit-test-built/tested, and simulator-built reproducibly in the controlled CI qualification used here.

Gate 2 does **not** establish:

- NOS3 launch/runtime behavior for Study 7E;
- Study-7E custom-app integration into NOS3;
- deterministic Study-7E scenario control;
- T3/T4 multi-instance/SBN behavior;
- ground-command/telemetry capture for Study 7E;
- absence of uncontrolled runtime network dependencies;
- scientific results, flight qualification, certification, or operational validation.

## Next gate

Do not select or freeze a stack yet. Complete the preselection seam proofs already required by the 2026-09-22 compatibility decision, then perform the cFS-vs-NOS3 selection.
