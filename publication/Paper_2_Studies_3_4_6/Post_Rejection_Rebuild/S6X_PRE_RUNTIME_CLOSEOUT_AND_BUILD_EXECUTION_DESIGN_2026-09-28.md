# S6X-EAP-001 Pre-Runtime Closeout and Build/Execution Design

**Date:** 2026-09-28  
**Status:** `DESIGN_PREPARED__LOCAL_POST_FIX_CLOSEOUT_STILL_REQUIRED__NO_CFS_BUILD__NO_SCIENTIFIC_EXECUTION`  
**Authoritative base:** `3194c939d5c3d9869187d5c794e380690dc31a44`

## 1. Why this phase does not close S6X yet

The earlier local pre-runtime attempt reached the pinned cFS and Limit Checker revisions and passed the independent Python oracle tests, but stopped at the validator message:

`baseline GT expression count is not exactly one`

That failure was later classified and corrected as a validator-scoping defect: the same GT/GE expressions appear in both signed and unsigned comparison functions, while the validator had searched the whole source file.

The corrected validator is tracked, but no verified **post-fix local rerun** is present in the authoritative repository or recovered prior evidence. Therefore the S6X pre-runtime gate remains open. This package supplies the exact closeout procedure; it does not manufacture the missing local evidence.

## 2. Frozen source and semantic fixture

S6X remains bound to:

- cFS `v7.0.1` commit `088b2fa828db9ff7e00733f1908e0eeb59f66ce3`;
- Limit Checker commit `a1c3a47ea1fa5c0d7751d6ff88848dc9bd8a6c7a`;
- Study-6 dependency `S6-SCTR-001`, unchanged and unpooled.

The controlled semantic fixture remains exactly:

- baseline: `WPValue > CompareValue`;
- controlled incorrect source: `WPValue >= CompareValue`;
- location: `LC_SignedCompare`, `LC_OPER_GT`;
- fixture: `S6X_FIXTURE_GT_EQ_BOUNDARY_001`.

The fixture is not applied in this phase.

## 3. Compiled independent functional invariant

Source-text validation alone is not sufficient for the scientific campaign. The objective-correctness adjudicator must exercise compiled LC behavior at the equality boundary and must remain outside the qualification gate.

A new research-only unit-test patch, `S6X_INVARIANT_HARNESS_EQUALITY_001.patch`, modifies the existing LC signed GT/GE unit tests so that:

- GT evaluates `WPValue=0`, `CompareValue=0`, expected **FALSE**;
- GE evaluates `WPValue=0`, `CompareValue=0`, expected **TRUE**.

The harness patch is applied to **both** CLEAN_APPROVED and APPROVED_BAD_SOURCE build trees. It does not add a qualification signal.

Expected scientific interpretation if execution is later authorized:

- a clean compiled LC build should pass the equality-boundary harness;
- the controlled `>=` source fixture should cause the GT equality-boundary harness to fail;
- this expected direction is prospective design, not a result.

If either direction does not occur, the scientific campaign fails closed.

## 4. Linux build environment

NASA cFS v7.0.1 documents the native Linux development/test configuration:

```text
make native_std.prep
make native_std.install
make native_std.runtest
```

S6X therefore does not use a host-native macOS cFS build. The candidate environment is `linux/amd64` using the dated Ubuntu base:

`amd64/ubuntu:noble-20260911@sha256:496754492fb28b4d3049432f2ca787449331e23fb14f0dd3fffea86bf5a93eb4`

The tracked Dockerfile installs Make/GCC through `build-essential`, CMake, Git, Python 3, OpenSSL, `file`, and CA certificates.

The environment is not considered frozen merely because the Dockerfile is tracked. Before any cFS build, the local preparation script must:

1. build the environment image only;
2. save that image to an ignored local tar;
3. compute the tar SHA-256;
4. record the Docker image ID and exact tool versions;
5. emit `S6X_BUILD_ENVIRONMENT_FREEZE_CANDIDATE_001.json`.

The resulting image tar hash, not the mutable package repositories, becomes the exact local environment identity for the prospective campaign.

## 5. Canonical S6X scope

S6X-EAP-001 is deliberately **not** a full external replication of the five incorrect Study-6 artifact states.

### Block A — paired artifact observability

Two executable source states only:

1. `CLEAN_APPROVED`
2. `APPROVED_BAD_SOURCE`

Each is evaluated under the six frozen Study-6 gate definitions.

Planned gate observations:

`2 states × 6 gates = 12`

The primary question is whether the clean and controlled-incorrect artifacts can carry the same six gate-visible assurance signals, receive the same qualification decisions, and still differ under the independent compiled functional invariant.

### Block B — clean-artifact assurance unavailability

Using only the objectively correct CLEAN_APPROVED evidence record, evaluate every subset of unavailable assurance signals:

`64 subsets × 6 gates = 384`

This is a deterministic evidence-layer calculation. It requires no additional artifact mutation.

### Total planned S6X gate observations

`12 + 384 = 396`

This population remains separate from the 420 frozen Study-6 observations.

## 6. Build isolation and reproducibility

If later authorized, four isolated build workspaces are required:

1. CLEAN primary;
2. CLEAN independent rebuild;
3. APPROVED_BAD_SOURCE primary;
4. APPROVED_BAD_SOURCE independent rebuild.

All four use the exact frozen environment image.

The research invariant harness patch is applied to all four LC source trees. The semantic `>`→`>=` fixture is applied only to the two APPROVED_BAD_SOURCE trees.

The prospective primary artifact is:

`build-native_std/exe/cpu1/lc.so`

Before scientific execution, the authorized build runner must require that this resolves to exactly one regular file in every build. A path/layout mismatch is a protocol failure, not permission to silently choose a different artifact.

`independent_reproduced_build_match` is prospectively defined as exact SHA-256 equality of the designated LC artifact across independently instantiated builds using the same frozen environment image.

If CLEAN does not reproduce exactly, stop. Do not substitute a normalized hash, fuzzy comparison, or different artifact after seeing the result.

## 7. Research-only signing and evidence

Only ephemeral S6X research keys may be used.

Prospective signature algorithm: **Ed25519** using OpenSSL 3.

No NASA, mission, production, employer, or third-party credentials are permitted.

Each evidence record must bind:

- exact cFS and LC revisions;
- source state and fixture identity;
- frozen environment image/tar hash;
- exact build instance;
- designated artifact SHA-256;
- research-only signature result;
- target-digest verification;
- provenance verification;
- independent-rebuild comparison;
- experimental source-review attestation;
- experimental release-approval attestation;
- independent compiled-invariant result.

Source review and release approval are experimental process attestations only. They are not semantic-correctness claims.

## 8. Primary validation requirements

The future campaign must use:

- two deterministic repetitions;
- a primary gate evaluator;
- a separately implemented reference gate evaluator that does not call the primary evaluator;
- zero case-level gate mismatches;
- zero correctness-oracle mismatches;
- an output hash manifest;
- result freeze before interpretation or manuscript claim use.

## 9. Explicitly closed actions

This phase does **not** authorize:

- cFS/LC compilation;
- semantic fixture application to a build;
- research artifact signing;
- provenance observation generation;
- independent artifact rebuild;
- qualification-gate execution;
- canonical S6X result generation;
- S6X manuscript claims;
- R2 or Figure-1 modification based on S6X;
- venue lock.

## 10. Required local closeout evidence

Run the tracked closeout harness after this package is merged:

`study6x/validation/closeout_pre_runtime_validation.sh`

It must produce:

- `study6x/workspace/S6X_PRE_RUNTIME_VALIDATION_001.json`;
- `study6x/workspace/S6X_PRE_RUNTIME_VALIDATION_001.txt`;
- `study6x/workspace/S6X_PRE_RUNTIME_CLOSEOUT_001.json`.

The build-environment preparation script may then materialize, but not execute cFS inside, the exact candidate environment and produce:

- `study6x/workspace/S6X_BUILD_ENVIRONMENT_FREEZE_CANDIDATE_001.json`;
- a local saved environment image tar and SHA-256.

Those records must be reviewed before any cFS build.

## 11. Gate

Current gate after this design PR:

`AUTHOR_REVIEW_AFTER_S6X_PRE_RUNTIME_CLOSEOUT_EVIDENCE_AND_BUILD_PROTOCOL_PREMERGE_CI_BEFORE_MERGE`

After merge and successful local closeout/environment preparation, the next scientific gate may be:

`AUTHOR_REVIEW_BEFORE_S6X_CANONICAL_SCIENTIFIC_EXECUTION`

but only if the local closeout and environment-freeze candidate are verified first.
