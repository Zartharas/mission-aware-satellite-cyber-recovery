# P2X v2f runtime workspace — materialization and independent verification design

**Status:** `STATIC_DESIGN_ONLY__MATERIALIZATION_NOT_AUTHORIZED`. The sole author authorized the contract/design after exact-head workflow **#1419 SUCCESS** on `639d2c89ff922b0c746f4101cbf6f1338bdeb66d`. No workspace has been created or copied; no runtime started.

## Parent binding (read-only source authority)

- Experiment: `P2X-NOS3-RG-001`; v2f build: raw **9/9** independent SHA-256 identity, **runtime untested**.
- Source commit for the qualified build: `8f5faef3830646eae065e8210216a2ed4301316c`.
- Evidence root: `artifacts/runtime/p2xa-nos3-v2f-build-20261007T185149Z-a61cae46f1` (ignored, preserved on the author host).
- Manifest path: `artifacts/runtime/p2xa-nos3-v2f-build-20261007T185149Z-a61cae46f1/p2x-v2f-build-manifest.json`.
- Exact host-observed manifest SHA-256: `cb5e84137cb090adc8fb24b9b2f78c0d239d2fb93c74393a0e8b71815cc86dee`.
- Pre-compilation dependency-descriptor SHA-256: `08ea45ca09c9a82b5456bea1f93cf325c1a61a8ae4332c5a8dea1b7d4dfbb736`.
- Prospective source: `primary/source`; repeat is an independent integrity cross-check, **never** a merged or patched input.
- Canonical `external/nos3` and older v2/v2e runtime artifacts are **not** valid substitutes.

## Materialization model — future, requiring separate authorization

1. Perform `verify_paper2x_phase_a_v2f.py` against the exact parent manifest and recheck the bound manifest hash and source/repeat 9/9 before any future copy. Record the source and protected historical evidence hashes *before* and *after*.
2. Produce a **complete recursive source inventory**. The nine proven build outputs alone do **not** cover cFS shared libraries, configurations/tables, additional NOS3 simulator resources, Git submodule metadata, and FourtyTwo runtime inputs. Stop on missing/unclassified file classes. Do not assume existing July locks cover v2f runtime closure.
3. Specify a new unique run ID, run-scoped workspace under ignored `artifacts/runtime`, and a separate stage directory; exclusive-create only and refuse preexisting destinations. Never copy into the canonical checkout. **No direct runtime mount of the frozen evidence directory** and no source hardlinks are permitted.
4. A future reviewed materializer must preserve all required file bytes, modes, directories and in-root symlink targets, with explicit exact-path exclusions and reasons only. Reject symlink escapes, device/special-file surprises, external Git worktree metadata references, or unreviewed hardlink aliases. Materialization and validation must not write to preserved evidence.
5. Verify the FourtyTwo candidate separately at revision `eda252bf31f27850e867e698cfdd963e143ead1f` and binary SHA-256 `b4d054bdd8a95dd429201466833fba8403efec4bdef09a9ed7040131dda3006d`; copy it into an independent companion workspace, not via direct runtime mount of canonical FourtyTwo.
6. Construct a deterministic source-to-destination inventory manifest. The **independent** verifier (separate code from the future copier) must compare regular-file hashes, sizes, modes, directory entries, symlink targets, excluded paths, absence of unexpected files, source/destination aliasing and original-evidence immutability. Any mismatch or unsupported object is a HOLD. Publish the workspace atomically **only after** independent verification.
7. Any eventual v2f runtime adapter must separately bind the verified run-scoped workspace, pinned OCI and internal-only network, and must pass a new exact-head CI gate plus a separate explicit author approval. Do **not** reuse `P2X_V2_MANIFEST`, call `run_paper2x_phase_a_nominal.sh` unchanged, or run the current `run_nominal_runtime_preflight.sh` against `external/nos3`.

## Explicit unresolved prerequisites

- Full dependency closure beyond the nine build-identity artifacts: **UNRESOLVED**.
- Precise source-tree path inclusion/exclusion and permissions/symlink policies: **DESIGN ONLY**.
- Future workspace inventory emission, materialization implementation, and actual host copy: **NOT IMPLEMENTED / NOT AUTHORIZED**.
- Independent workspace verifier implementation and any observed workspace proof: **NOT IMPLEMENTED / NOT EXECUTED**.
- Legacy preflight mount/path adaptation and 21-component cFS/NOS3/42 runtime readiness: **NOT VERIFIED**.

## Current hard boundary

`scripts/audit_paper2x_v2f_workspace_contract.py` validates the **tracked specification only**, using in-memory negative fixtures. Its `--materialize`, `--verify-workspace` and `--run` modes are all unconditionally denied. A passing static contract must **never** be reported as workspace materialization or runtime evidence.

Nominal runtime, benign SAMPLE NOOP, COSMOS, fault campaign, scientific observations, final environment acceptance and PR #215 merge remain **UNAUTHORIZED**. The parent 9/9 build claim remains unchanged.
