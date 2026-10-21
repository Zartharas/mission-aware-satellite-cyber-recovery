# Study 7E / Paper 3 — New-Chat Continuation Handoff

**Repository:** `Zartharas/mission-aware-satellite-cyber-recovery`  
**PR:** #167  
**Branch:** `paper3/s7e-aerc-implementation-feasibility-20260922`  
**Handoff basis head:** `94b6aaf6e670edbb160d460882c3a2d7e8e0e168`  
**PR state at handoff preparation:** OPEN / UNMERGED / MERGEABLE  
**Publication/result claims:** NOT AUTHORIZED  
**PR merge:** NOT AUTHORIZED

## 1. Current scientific state

Study 7E (`S7E-AERC-001`) has progressed through:

1. AR-1 through AR-5 approval for pre-canonical implementation;
2. signed-evidence v2 and qualifier/fault feasibility;
3. cFS producer/qualifier runtime qualification;
4. EP-1 through EP-5 execution-parameter approval;
5. protocol/environment/public-key/fault-transform/learner-protocol freeze under `S7E-AERC-FREEZE-001`;
6. deterministic L0/L1 production training under `S7E-AERC-TRAINPLAN-001`;
7. model review and freeze under `S7E-AERC-MODEL-FREEZE-001`;
8. held-out plan qualification under `S7E-AERC-HELDOUT-PLAN-001`;
9. authorized one-shot E1/E2/C0 scientific execution under `S7E-AERC-HELDOUT-EXEC-001`;
10. valid complete-population result checkpoint `S7E-AERC-HELDOUT-RESULTS-001`.

The next scientific gate is **results review/interpretation and a separate result-freeze decision**. Do not write manuscript/publication claims or merge PR #167 without separate authorization.

## 2. Held-out execution of record

The first workflow run after authorization, run `35948684512`, stopped during model-freeze preflight because a historical integrity test still required the held-out authorization file to be absent.

That aborted run executed:

- scientific scenarios: 0
- policy predictions: 0
- scientific results: none

It is retained in `study7e/HELD_OUT_EVALUATION_STATE.json` as a pre-inference aborted run.

The corrected scientific execution of record is:

- workflow: `Study 7E held-out evaluation 001`
- run: `35948870036`
- job: `107472877604`
- source commit: `1cbc4be58a99e9add139e73efc9ab42a4f275864`
- artifact ID: `10787499194`
- artifact SHA-256: `cc436ee98e20bb13643f58af738f42885b499a81bddad2766cb90f3e0860da35`
- artifact expiry: `2026-10-24T02:50:03Z`
- scenario-manifest SHA-256: `2d9e8e4b155cd4fe079010341e9bdbbfc1a1ab5e94f3467c1b5da8063d38c4fb`

Population:

- E1: 84
- E2: 104
- C0: 8
- total scenarios: 196
- total policy decisions: 784
- invalid scenarios: 0
- audit matches: 784
- audit mismatches: 0

The one-shot workflow is sealed. The result checkpoint prevents further execution under the same execution ID, including manual dispatch. Any later campaign requires a new execution ID and new explicit authorization.

## 3. Exact held-out endpoint counts

Overall exact finite-population counts:

| Policy | Decision errors | Unsafe proceed | False-conservative hold | ENTER | HOLD |
|---|---:|---:|---:|---:|---:|
| D0_BASE | 40 | 9 | 31 | 25 | 171 |
| L0_BASE | 47 | 21 | 26 | 42 | 154 |
| D1_CORROBORATED | 49 | 4 | 45 | 6 | 190 |
| L1_CORROBORATED | 43 | 31 | 12 | 66 | 130 |

By block (error / unsafe / false-conservative):

- E1 (84): D0 = 18/3/15; L0 = 21/9/12; D1 = 24/3/21; L1 = 17/11/6.
- E2 (104): D0 = 22/6/16; L0 = 26/12/14; D1 = 25/1/24; L1 = 26/20/6.
- C0 (8): all four policies HOLD in all 8 scenarios with 0 error.

Paired disagreements:

- D0 vs L0: 67/196 overall; E1 27/84; E2 40/104; C0 0/8.
- D1 vs L1: 72/196 overall; E1 29/84; E2 43/104; C0 0/8.

Overall corroboration deltas:

- deterministic D1-D0: unsafe proceed -5; false-conservative hold +14;
- learned L1-L0: unsafe proceed +10; false-conservative hold -14.

**Do not interpret these aggregates as a global policy ranking.** The frozen protocol requires topology/fault stratification and exact finite-population interpretation.

## 4. Frozen identities

### Protocol/environment freeze

`S7E-AERC-FREEZE-001` is active.

Key frozen execution semantics:

- cFS baseline: v7.0.1 commit `088b2fa828db9ff7e00733f1908e0eeb59f66ce3`
- Ed25519 verification: Monocypher 4.0.3 commit `ab2b16dd619ad5f6979a4fbe69cfa324a6fcc35f`
- freshness max age: 0 logical ticks
- evidence epoch: 1
- no private signing keys in cFS FSW
- F0-F12 transformations frozen

### Model freeze

`S7E-AERC-MODEL-FREEZE-001` is active.

- L0 semantic SHA-256: `1060d526704f21d4ee72be1ace6916c061b0c254de64246b1f469a576ba42ef1`
- L1 semantic SHA-256: `499fc92b714948c9a837861d4810051f51ab014f3f261a13df85646f7832f558`
- L0 runtime SHA-256: `5b38a0088c4dd0cb2ce3739993cd2d9ee7949eb1a86c188ca1bd95b38cb5f4b1`
- L1 runtime SHA-256: `6c4b589766f1df51fad2bde80350000f24c53b215ef345079fd81a8a7b98b960`
- dependency inventory SHA-256: `023a745c1edde1a929030fbc15245811f828365aba11b0485c5b139a402fdd08`
- L0 training dataset SHA-256: `435b938b714d7eeb87284af8a2beb823a0d8e5a4a2220d96e784411a64680f20`
- L1 training dataset SHA-256: `70e3fc366d8c618a3e27d533aa436b1230d6231a82759f1dfb67850ca343df61`

## 5. Authorizations and prohibitions

Explicit authorizations already granted:

- AR-1 through AR-5 pre-canonical implementation
- EP-1 through EP-5 pre-freeze candidate
- `S7E-AERC-FREEZE-001` activation
- deterministic L0/L1 production training
- model-freeze review
- `S7E-AERC-MODEL-FREEZE-001` activation
- held-out evaluation plan preparation/review
- exact E1/E2/C0 scientific execution

Still **not authorized**:

- post-hoc model/hyperparameter changes
- retraining
- population expansion
- endpoint expansion
- retry of sealed `S7E-AERC-HELDOUT-EXEC-001`
- PR #167 merge
- manuscript/publication result claims

## 6. Key repository records

- `study7e/FREEZE_MANIFEST_001.json`
- `study7e/MODEL_FREEZE_MANIFEST_001.json`
- `study7e/HELD_OUT_EVALUATION_AUTHORIZATION.json`
- `study7e/HELD_OUT_EVALUATION_STATE.json`
- `study7e/HELD_OUT_EVALUATION_PLAN_STATE.json`
- `study7e/results/S7E-AERC-HELDOUT-EXEC-001/result_checkpoint.json`
- `study7e/results/S7E-AERC-HELDOUT-EXEC-001/exact_endpoint_counts.json`
- `study7e/results/S7E-AERC-HELDOUT-EXEC-001/audit_reconciliation.json`
- `publication/Paper_3_Study_7/Post_Rejection_Rebuild/S7E_AERC_HELD_OUT_EXEC_001_RESULTS_CHECKPOINT_2026-09-23.md`

## 7. Current governance/CI note

At handoff preparation, all current Study-7E checks were green except `Study 7E pre-canonical qualification`, whose only failing assertion was the historical rule that `study7e/results/` must be empty.

The handoff commit updates `study7e/validation/validate_precanonical.py` so this historical validator accepts only the explicitly authorized and sealed `S7E-AERC-HELDOUT-RESULTS-001` checkpoint, while continuing to require:

- zero invalid scenarios;
- zero audit mismatches;
- one-shot seal;
- no retry;
- no model retraining/post-hoc model change;
- no PR merge;
- no publication/result claims.

Verify the exact handoff head CI before starting interpretation work.

## 8. Required next work in the next chat

1. Verify PR #167 current head and all Study-7E governance workflows.
2. Confirm the revised pre-canonical validator is green.
3. Review the raw/checkpointed held-out results scientifically, emphasizing topology/fault strata rather than aggregate ranking.
4. Perform an adversarial interpretation review against RQ1-RQ4 and frozen claim boundaries.
5. Decide whether a **result freeze** is scientifically justified.
6. Stop for explicit author result-freeze approval before manuscript/publication claims.
7. Do not merge PR #167 unless separately authorized.

## 9. Efficiency rules for continuation

- Treat repository state as authoritative; do not reconstruct already-completed work.
- Batch GitHub reads/writes.
- Use exact-head guards before writes.
- Inspect only failed CI job logs.
- Do not poll unrelated workflows repeatedly.
- The held-out scientific workflow is sealed; do not rerun it.
- If the platform actually returns `Message delivery timed out. Please try again.`, report that exact error and stop retrying the same operation.
