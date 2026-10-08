# P2X v2f nominal-runtime launcher candidate — static design only

**Experiment:** `P2X-NOS3-RG-001`. **Scope:** sole-author-authorized design and static validation only. This is not runtime authorization and makes no new empirical claim.

## Frozen parent and binding

- Parent offline build: `V2F_DUAL_OFFLINE_BUILD_BYTE_IDENTITY_PASS__RUNTIME_UNTESTED`, 9/9 raw SHA-256 identity.
- Parent execution commit: `8f5faef3830646eae065e8210216a2ed4301316c`.
- Preserved evidence ID: `p2xa-nos3-v2f-build-20261007T185149Z-a61cae46f1`.
- Relative manifest: `artifacts/runtime/p2xa-nos3-v2f-build-20261007T185149Z-a61cae46f1/p2x-v2f-build-manifest.json`.
- Host-observed manifest SHA-256: `cb5e84137cb090adc8fb24b9b2f78c0d239d2fb93c74393a0e8b71815cc86dee`. GitHub CI checks the recorded binding but does not possess ignored host evidence bytes.
- Pinned OCI: `ivvitc/nos3-64@sha256:06aa945988a7770b759022c2e1f6f2531818c087fe41a4739d3a3a7f2a9dcce2`. NOS3: `5a3bdee6be9a2c67fdf994ae6db56d5c60395302`. LC/HWLIB remain at the registered pins.

## Why the legacy runner cannot be reused

`scripts/run_paper2x_phase_a_nominal.sh` binds `P2X_V2_MANIFEST` to the v2 verifier and its `run-ci-noop` mode launches a runtime stack. `scripts/run_nominal_runtime_preflight.sh` hard-codes `$ROOT/external/nos3`, creates a Docker bridge and starts 21 NOS3/42/cFS components using its canonical checkout. The v2f 9/9 PASS concerns two fresh build candidates under ignored evidence, **not** the canonical `external/nos3` artifacts. A legacy v2 PASS or July runtime lock cannot substitute for v2f provenance.

## Proposed future runtime preparation — NOT IMPLEMENTED OR AUTHORIZED

1. Bind `P2X_V2F_MANIFEST` to the exact host manifest path and validate raw manifest SHA-256, parent executed commit, descriptor map, and fresh 9/9 artifacts independently.
2. Select the preserved **primary** candidate (`artifacts/runtime/p2xa-nos3-v2f-build-20261007T185149Z-a61cae46f1/primary/source`), with the byte-identical repeat as a non-executed comparison; do not silently use `external/nos3`.
3. Construct a separate fresh run-scoped, independently validated runtime workspace, never executing in-place from either preserved build candidate and never altering the historical v2/v2e/v2f evidence. Any required copy exclusions, modes, symlinks, and generated runtime inputs need explicit review and a materialization manifest first.
4. Design a v2f-specific preflight adapter to point every relevant runtime mount/config and required artifact at that workspace. The existing launcher/preflight must not be called unchanged. Verify 42 binary pin, full dependency graph, cFS/NOS3 configuration, IPC and 21-component readiness.
5. Require internal-only networking, no host-published ports, exact resource labels, bounded runtime duration, evidence capture and non-destructive cleanup. Do not conflate a benign UDP cFS SAMPLE NOOP with COSMOS downlink proof.
6. Before any runtime, pass a separate CI-validated execution gate with an explicit, **new** sole-author authorization. COSMOS, faults, scientific observations, final acceptance, and PR #215 merge remain separate closed decisions.

## Executable prevention

`scripts/p2x_v2f_nominal_runtime_candidate.py --inspect` and `--self-test` inspect only tracked metadata. Its `--run` path unconditionally fails **before** any container, source materialization, runtime action, or evidence write. No helper in this static package starts runtime. The legacy runners are left untouched.

**Allowed present classification:** `V2F_MANIFEST_SHA256_BOUND__RUNTIME_NOT_AUTHORIZED`.

**Forbidden:** nominal runtime execution, benign cFS NOOP, COSMOS, faults, scientific observations, final environment acceptance, and PR #215 merge.
