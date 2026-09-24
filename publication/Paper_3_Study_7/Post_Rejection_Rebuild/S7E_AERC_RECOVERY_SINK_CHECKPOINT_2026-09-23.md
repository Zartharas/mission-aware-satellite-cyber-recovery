# S7E-AERC-001 Recovery Action Sink Checkpoint — 2026-09-23

**Experiment:** `S7E-AERC-001`  
**Selected baseline:** standalone cFS v7.0.1  
**Qualification head:** `ec2637b5d1c6710e6ac97b32d45cbde2750c1d42`  
**Pull request:** #167  
**Canonical scientific execution:** NOT AUTHORIZED

## Result

**Pre-canonical recovery action sink: PASS**

The selected cFS baseline can load and run the Study-7E recovery-action sink, record both allowed requested actions, and fail closed on malformed or invalid requests.

## Exact evidence

- workflow: `Study 7E pre-canonical qualification`
- workflow ID: `364617426`
- run ID: `35882223951`
- job ID: `107253301919`
- job conclusion: `success`

Compile/runtime assertions:

- `aerc_recovery_sink_compile=PASS`
- `aerc_recovery_sink_runtime=PASS`
- `aerc_sink_probe_runtime=PASS`

Positive records:

`AERC_RECOVERY_SINK RECORD scenario=0x53374541 policy=1 action=HOLD sequence=1`

`AERC_RECOVERY_SINK RECORD scenario=0x53374542 policy=3 action=ENTER_RECOVERY_GATE sequence=2`

Fail-closed records:

`AERC_RECOVERY_SINK REJECT_LENGTH expected=24 actual=20 status=0x00000000`

`AERC_RECOVERY_SINK REJECT_ACTION scenario=0x5337454F policy=2 action=255`

Probe completion:

`AERC_SINK_PROBE PASS hold_scenario=0x53374541 enter_scenario=0x53374542 records=2 negatives=2`

The invalid requests did not advance the receipt sequence: the second valid record remained sequence 2.

## Defect correction provenance

The first sink runtime attempt at head `05b649d87b73bc54f0f92f308ee51150698f1962` (run `35880938202`, job `107248890678`) correctly failed the runtime gate.

Two cFS/OSAL integration defects were found:

1. `aerc_recovery_sink.so` exceeded the OSAL filesystem-name limit and failed with `OS_FS_ERR_NAME_TOO_LONG (-104)`;
2. the long probe entry symbol was truncated by the cFE startup field to `AERC_SINK_PROBE_Mai`.

The final implementation uses the shorter module `aerc_sink.so`, entry `AERC_SINK_Main`, and probe entry `AERC_SPROBE_Main`. The corrected final gate is green.

## Security hardening added before the final rerun

The sink validates the embedded cFE message length with `CFE_MSG_GetSize()` before casting the request payload. It also rejects unknown policy/action values. The engineering probe exercises both malformed-length and invalid-action cases.

## Scientific boundary

This gate establishes only a deterministic recording sink for **requested** actions.

It does not establish:

- that either requested action is scientifically or operationally correct;
- D0/D1/L0/L1 policy behavior;
- authorization/signature verification;
- fault-injection outcomes;
- canonical Study-7E results;
- hardware actuation;
- flight qualification or certification.

The run recorded:

- `study7e_scientific_scenarios_executed=0`;
- `scientific_results_generated=false`.

## Next gate

Implement the shared policy-visible B/C evidence/snapshot contract and deterministic D0/D1 decision path using engineering-only inputs. Do not introduce research-only truth fields. The real-signature/Ed25519 dependency decision remains separate and must be reviewed before authorization-producer/verification implementation.
