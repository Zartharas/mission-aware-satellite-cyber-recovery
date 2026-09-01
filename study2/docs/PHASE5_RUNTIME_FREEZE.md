# Study 2 Phase 5 — Runtime Freeze and Development Calibration

**Status:** `PHASE5_RUNTIME_FREEZE_CANDIDATE_RUNTIME_NOT_AUTHORIZED`

Phase 5 converts the frozen Phase-4 experimental design into an executable, hash-bound software-in-the-loop runtime contract without consuming any frozen Study-2 campaign seed.

## Scientific boundary

This phase remains pre-campaign. It does not alter Study-1 evidence, rerun Study-1 analysis, execute an operational spacecraft or RF system, use real credentials, or generate Study-2 analysis observations.

`study2_campaign_runtime_authorized = false`

`runtime_gate = CLOSED`

## Prospective protocol amendment PA1

Before any campaign observation or campaign seed consumption, Phase 5 records `STUDY2_PROTOCOL_AMENDMENT_1.json`.

The amendment corrects only the planned contact analysis: K0-K3 remain an ordered outage trend, while K4 is treated as a prespecified intermittent/flapping-contact contrast rather than as the next ordinal severity level. It changes no cell, seed, sample size, primary outcome, treatment, policy, or stopping rule.

Protocol-amendment file SHA-256:

`987559dfc1ccc28a50f3299161bfe1ff39e352d5891fb9b488672867fbf44246`

## Frozen logical-time calibration

The time basis is deterministic logical SIL time, not measured spacecraft-link latency and not MacBook/GitHub wall-clock duration.

- decision time: 10 logical seconds
- current evidence issue time: 8 logical seconds
- evidence validity: 5 logical seconds
- recovery processing increment: 5 logical seconds
- right-censor horizon: 240 logical seconds
- K0: contact available over [0, 240]
- K1: contact available over [20, 240]
- K2: contact available over [60, 240]
- K3: contact available over [180, 240]
- K4: intermittent windows [25,35], [75,90], [145,165], [220,240]

These values are prospective model constants. They must not be changed after frozen campaign outcomes are generated.

## Seed isolation

Development-only seeds are `2900001-2900064`.

Frozen campaign seeds remain exactly:

- A96: `2100001-2100096`
- B32: `2200001-2200032`
- C32: `2300001-2300032`
- D32: `2400001-2400032`
- E32: `2500001-2500032`

The runtime rejects a campaign seed in development mode. Campaign mode rejects all non-campaign seeds and additionally requires a repository-backed, active, unconsumed Phase-6 authorization envelope.

## Exact trial membership

`study2_security.trial_manifest.materialize_trial_manifest()` expands the frozen 85-cell matrix into exactly 3,872 ordered trial positions.

Canonical SHA-256:

`190612473717b7768ceccb4596a20d90cd7d532bf7581330ce94d609cb752e67`

The first position is `S2-AEATR-001:A01:2100001`; the final position is `S2-AEATR-001:E09:2500032`.

## Attempt-history controls

The Phase-5 attempt ledger preserves the Study-1 governance pattern without reusing Study-1 data:

- globally unique run IDs;
- exact-next-trial enforcement;
- retained INVALID attempts;
- INVALID does not advance the frozen position;
- no automatic retry;
- no automatic next-trial execution;
- no post-hoc seed substitution.

The Phase-6 campaign operator must use this exact-next-trial ledger boundary; direct development fixtures are not campaign evidence.

## Development runner

The development runner uses synthetic deterministic Ed25519 producer keys and deterministic logical evidence. It exercises all 85 frozen cell types with only the development seed namespace.

The policy receives only policy-visible evidence/contact/context. Research-only adjudication truth is placed in a separate output namespace and is never a selector argument.

Block-B contact trials may perform a deterministic follow-up evaluation when the frozen contact schedule next becomes available. This is logical SIL progression, not sleeping or wall-clock timing.

## Runtime authorization boundary

Phase 5 defines the authorization schema but intentionally contains no `study2/PHASE6_CAMPAIGN_AUTHORIZATION.json`. Even a correctly constructed in-memory authorization is rejected while that repository-backed file is absent.

Future authorization bindings are derived by the runtime itself, not supplied by the caller. They include:

- frozen protocol file SHA-256;
- prospective protocol-amendment SHA-256;
- cell-matrix SHA-256;
- trial-manifest SHA-256;
- Phase-5 runtime-freeze SHA-256;
- Dockerfile/container-recipe SHA-256;
- a runtime-bundle SHA-256 over the Study-2 security package and frozen static runtime inputs;
- a Phase-5 base commit for provenance;
- explicit exact-campaign scope;
- `active=true` and `consumed=false`.

The runtime-freeze canonical SHA-256 for this candidate is:

`40e38ebc1dccc8b549d36bcbf6c2aca4a52ade7c6ecb87670224ef643d741434`

Until a future Phase-6 authorization is committed, independently validated, and invoked through the campaign operator, campaign mode remains closed.
