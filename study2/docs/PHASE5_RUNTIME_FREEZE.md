# Study 2 Phase 5 — Runtime Freeze and Development Calibration

**Status:** `PHASE5_RUNTIME_FREEZE_CANDIDATE_RUNTIME_NOT_AUTHORIZED`

Phase 5 converts the frozen Phase-4 experimental design into an executable, hash-bound software-in-the-loop runtime contract without consuming any frozen Study-2 campaign seed.

## Scientific boundary

This phase remains pre-campaign. It does not alter Study-1 evidence, rerun Study-1 analysis, execute an operational spacecraft or RF system, use real credentials, or generate Study-2 analysis observations.

`study2_campaign_runtime_authorized = false`

`runtime_gate = CLOSED`

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

The runtime rejects a campaign seed in development mode. Campaign mode rejects all non-campaign seeds and additionally requires an active, unconsumed authorization envelope bound to the exact repository commit and cryptographic runtime/protocol manifests.

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

## Development runner

The development runner uses synthetic deterministic Ed25519 producer keys and deterministic logical evidence. It exercises all 85 frozen cell types with only the development seed namespace.

The policy receives only policy-visible evidence/contact/context. Research-only adjudication truth is placed in a separate output namespace and is never a selector argument.

Block-B contact trials may perform a deterministic follow-up evaluation when the frozen contact schedule next becomes available. This is logical SIL progression, not sleeping or wall-clock timing.

## Runtime authorization boundary

Phase 5 defines the authorization schema but intentionally contains no active authorization. A future Phase-6 authorization must bind:

- exact repository commit;
- frozen protocol SHA-256;
- cell-matrix SHA-256;
- trial-manifest SHA-256;
- Phase-5 runtime-freeze SHA-256;
- container recipe SHA-256;
- explicit exact-campaign scope;
- active=true and consumed=false.

Until such an authorization is merged and independently validated, campaign mode cannot execute a frozen Study-2 seed.
