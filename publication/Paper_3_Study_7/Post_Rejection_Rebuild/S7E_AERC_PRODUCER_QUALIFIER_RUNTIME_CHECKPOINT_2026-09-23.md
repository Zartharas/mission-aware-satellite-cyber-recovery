# S7E-AERC-001 Producer/Qualifier Runtime Checkpoint — 2026-09-23

**Experiment:** `S7E-AERC-001`  
**Author approval:** AR-1 through AR-5, pre-canonical implementation only  
**Selected stack:** standalone cFS v7.0.1 at `088b2fa828db9ff7e00733f1908e0eeb59f66ce3`  
**Qualification head:** `ea58629c70a6022343db6a7bce7ee05cd08083e0`  
**Canonical scientific execution:** NOT AUTHORIZED

## Result

**Producer bridge → signed-evidence qualifier → D0/D1 → recovery sink: PASS**

The author-approved pre-canonical path compiles and executes in the selected cFS baseline.

## Exact GitHub Actions evidence

- workflow: `Study 7E cFS runtime smoke`
- workflow ID: `365269942`
- run ID: `35911617367`
- job ID: `107352621226`
- conclusion: `success`
- artifact ID: `10774070814`
- artifact digest: `sha256:5d8f3a49a411e0acf6993d9742b8cb148e7a11c187bbeb5038516164aeed8ff8`

Compile markers:

- `aerc_eprod_compile=PASS`
- `aerc_qualifier_compile=PASS`
- `aerc_qualifier_probe_compile=PASS`

## Positive signed-evidence path

Primary evidence:

`AERC_QUAL SNAPSHOT scenario=0x53374A01 kind=BASE sig=1 trust=1 fresh=1 epoch=1 noncontra=1 complete=1 auth=1`

`AERC_POLICY DECISION scenario=0x53374A01 policy=D0_BASE action=ENTER_RECOVERY_GATE sequence=1 feature_count=9`

Corroborator evidence:

`AERC_QUAL SNAPSHOT scenario=0x53374A01 kind=CORR sig=1 trust=1 fresh=1 epoch=1 noncontra=1 complete=1 auth=1`

`AERC_POLICY DECISION scenario=0x53374A01 policy=D1_CORROBORATED action=ENTER_RECOVERY_GATE sequence=2 feature_count=16`

## F9 transport-corruption path

The engineering probe mutates byte 47 of the already signed v2 body without resigning.

Observed qualifier output:

`AERC_QUAL SNAPSHOT scenario=0x53374A02 kind=BASE sig=0 trust=1 fresh=1 epoch=0 noncontra=1 complete=1 auth=1`

Observed deterministic policy result:

`AERC_POLICY DECISION scenario=0x53374A02 policy=D0_BASE action=HOLD sequence=3 feature_count=9`

This demonstrates the approved feature-independence behavior: the parsed authorization claim remains `1` while signature and epoch qualification fail independently.

## F12 execution-equivocation path

First valid body:

`AERC_QUAL SNAPSHOT scenario=0x53374A03 kind=BASE sig=1 trust=1 fresh=1 epoch=1 noncontra=1 complete=1 auth=1`

`AERC_POLICY DECISION scenario=0x53374A03 policy=D0_BASE action=ENTER_RECOVERY_GATE sequence=4 feature_count=9`

Second separately signed body uses the same sequence/context but the opposite authorization claim:

`AERC_QUAL SNAPSHOT scenario=0x53374A03 kind=BASE sig=1 trust=1 fresh=1 epoch=1 noncontra=0 complete=1 auth=0`

`AERC_POLICY DECISION scenario=0x53374A03 policy=D0_BASE action=HOLD sequence=5 feature_count=9`

This demonstrates sticky path-local equivocation detection without making topology/fault labels policy-visible.

## Fail-closed producer ingress

Malformed short ingress:

`AERC_EPROD REJECT_LENGTH expected=148 actual=20 status=0x00000000`

Probe completion:

`AERC_QPROBE PASS base_enter=2 corr_enter=1 f9_hold=1 f12_hold=1 malformed=1 decisions=5`

## Security and research boundary

Runtime markers:

- `aerc_producer_bridge_runtime=PASS`
- `aerc_qualifier_runtime=PASS`
- `aerc_precanonical_policy_binding_runtime=PASS`
- `private_key_in_cfs_fsw=false`
- `final_registry_frozen=false`
- `canonical_policy_binding_frozen=false`
- `research_truth_visible_to_qualifier_runtime=false`
- `study7e_scientific_scenarios_executed=0`
- `scientific_results_generated=false`

The tracked cFS FSW validator additionally rejects the published engineering test private seeds and direct `crypto_ed25519_sign(` usage if they appear anywhere under `study7e/fsw`.

## Defects corrected during qualification

Three implementation/harness defects were corrected without changing the approved AR-1 through AR-5 semantics:

1. cFE v7.0.1 compatibility: replaced nonexistent `CFE_STATUS_BAD_ARGUMENT` with an available generic cFE failure status;
2. OSAL module-table exhaustion: isolated the producer/qualifier phase by removing unrelated startup `CFE_APP`/`CFE_LIB` entries before loading the five required AERC applications;
3. snapshot initialization ordering: set `FeatureCount` after `CFE_MSG_Init` so cFE message initialization cannot clear the field.

The final qualification head contains all three corrections.

## Still not frozen

This checkpoint does not freeze:

- numeric freshness threshold;
- logical-time calibration;
- epoch mapping;
- opaque scenario/source/key/authority registry values;
- final test keys or hashes;
- final F0-F12 byte transformations as canonical protocol;
- L0/L1 production models;
- protocol/environment;
- canonical execution.

PR #167 remains open and unmerged.
