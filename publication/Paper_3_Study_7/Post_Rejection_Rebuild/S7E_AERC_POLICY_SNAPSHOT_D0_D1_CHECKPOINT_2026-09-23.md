# S7E-AERC-001 Shared Snapshot and Deterministic D0/D1 Checkpoint — 2026-09-23

**Experiment:** `S7E-AERC-001`  
**Selected baseline:** standalone cFS v7.0.1  
**Qualification head:** `b13f0d0cd6db3aa0f6e965e9303e7068544f3184`  
**Pull request:** #167  
**Canonical scientific execution:** NOT AUTHORIZED

## Result

**Shared policy-visible B/C snapshot contract and deterministic D0/D1 runtime: PASS**

This gate establishes a common cFS snapshot surface for the Study-7E policy-visible feature vectors and demonstrates the two deterministic comparators against fixed engineering-only inputs.

It does not implement learned policies, signature verification, production model training, or canonical scientific execution.

## Exact evidence

- workflow: `Study 7E cFS runtime smoke`
- workflow ID: `365269942`
- run ID: `35885631864`
- job ID: `107264993826`
- conclusion: `success`
- artifact ID: `10761799281`
- artifact digest: `sha256:0b8ce4878099acad5e06257106f26aaac0cc6db58e1aa258db0312f66f15ee47`
- repository validation run `35885631683`: success
- pre-canonical qualification run `35885631522`: success

## Snapshot contract

Experimental cFS message IDs:

- base snapshot: `0x0EE5`
- corroborated snapshot: `0x0EE6`
- policy decision record: `0x0EE7`

Feature cardinality:

- base B snapshot: 9 ordered binary features;
- corroborated C snapshot: 16 ordered binary features;
- base snapshots require the unused 7 slots to remain zero;
- reserved bytes must remain zero.

The future D0/L0 pair is bound to the same base-snapshot message bytes, and the future D1/L1 pair is bound to the same corroborated-snapshot message bytes. No learned runtime is implemented in this gate.

## Positive runtime cases

`AERC_POLICY DECISION scenario=0x53374551 policy=D0_BASE action=ENTER_RECOVERY_GATE sequence=1 feature_count=9`

`AERC_POLICY DECISION scenario=0x53374552 policy=D0_BASE action=HOLD sequence=2 feature_count=9`

`AERC_POLICY DECISION scenario=0x53374553 policy=D1_CORROBORATED action=ENTER_RECOVERY_GATE sequence=3 feature_count=16`

`AERC_POLICY DECISION scenario=0x53374554 policy=D1_CORROBORATED action=HOLD sequence=4 feature_count=16`

Matching recovery-sink records were observed for all four accepted decisions with policy IDs 1/3 and matching receipt sequence 1–4.

## Fail-closed runtime cases

Malformed message size:

`AERC_POLICY REJECT_LENGTH expected=40 actual=20 status=0x00000000`

Base/corroborated feature-count mismatch:

`AERC_POLICY REJECT_CONTRACT scenario=0x5337455E policy=D0_BASE reason=1 expected_count=9 actual_count=16 index=0`

Non-binary feature input:

`AERC_POLICY REJECT_FEATURE scenario=0x5337455F index=9 value=2`

The accepted decision sequence remained 1–4, demonstrating that rejected snapshots did not create policy decisions.

## Governance boundary

The same qualification head passed the flight-software truth-leakage guard:

`study7e_fsw_truth_leakage=PASS`

The runtime recorded:

- `research_truth_visible_to_policy_runtime=false`;
- `learned_policy_runtime_executed=false`;
- `study7e_scientific_scenarios_executed=0`;
- `scientific_results_generated=false`.

This gate does not establish:

- real authorization/signature verification;
- L0/L1 runtime behavior;
- trained or frozen production models;
- fault-injection results;
- topology-transfer results;
- canonical Study-7E observations;
- flight qualification/certification.

## Next gate

Perform a bounded compatibility/provenance review for the real-signature verification dependency needed by the authorization path. Ed25519 remains the protocol candidate, but no crypto runtime is selected or added by this checkpoint.
