# S6X Attempt 001 Failure Freeze and Environment v2 Correction Design

**Date:** 2026-09-29  
**Experiment:** `S6X-EAP-001`  
**Authoritative base:** `cfb76ef62ed081c9cdaac450e420cca3c5507542`

## Attempt 001 classification

`S6X-EXEC-ATTEMPT-001` is preserved as a fail-closed tooling-only attempt that stopped before scientific observation generation.

Observed evidence establishes:

- clean primary build materialized;
- the equality-boundary harness was applied to the clean source;
- the semantic bad-source fixture was not applied;
- `native_std.runtest` returned 2 because `jq` was missing before test execution;
- no canonical gate observations or result artifacts were generated;
- run 2 did not start;
- the runner expected `build-native_std/exe/cpu1/lc.so`, while CPU1 installed LC at `build-native_std/exe/cpu1/cf/lc.so`.

The failed-attempt console log SHA-256 is:

`8882e854fa150491d5948ff7e0c081f21f4323b8c7b35be2da77a51ca38173dd`

The author-supplied forensic transcript reviewed for this freeze has SHA-256:

`022865339f2360eeb9feeb329d41f8cdf29a1f731c9a76d65a0c030488c583cd`

## Environment v2

Environment 001 remains immutable. Environment 002 uses the same pinned Ubuntu base and existing package set plus `jq`, which pinned cFS `target-rules.mk` requires for `native_std.runtest`.

No environment image is built in this PR. After merge and post-merge CI, a separate author gate may materialize Environment 002 and freeze its exact image ID and tar SHA-256.

## Artifact-path correction

The corrected designated artifact is:

`build-native_std/exe/cpu1/cf/lc.so`

Attempt 001 observed SHA-256:

`7311d8d1b89ffe2ca0e43ca1e2f6430db28d2f9532ebf426c4870ab5847f1670`

The matching build-tree artifact had the same SHA-256, providing corroboration without changing the CPU1-only designated-artifact rule.

## Scientific contract unchanged

This correction does not alter the hypothesis, source pins, equality invariant, semantic fixture, six assurance signals, gate definitions, 12 + 384 observation design, two repetitions, eight-build campaign, full `native_std.runtest`, primary/reference evaluator separation, or Study-6/S6X non-pooling boundary.

## Closed actions

No Environment 002 materialization, cFS build, fixture application to a build, signing, independent rebuild, gate execution, scientific execution, result freeze, or manuscript claim use is authorized in this PR.

## Next gate

`AUTHOR_REVIEW_AFTER_S6X_ATTEMPT001_FAILURE_FREEZE_ENV_V2_CORRECTION_PR_AND_PREMERGE_CI_BEFORE_MERGE`
