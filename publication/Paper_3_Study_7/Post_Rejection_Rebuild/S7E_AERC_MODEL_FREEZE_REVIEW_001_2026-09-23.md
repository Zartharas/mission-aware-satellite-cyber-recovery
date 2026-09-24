# S7E-AERC-001 Model-Freeze Review 001 — 2026-09-23

**Review ID:** S7E-AERC-MODEL-FREEZE-REVIEW-001  
**Candidate:** S7E-AERC-MODEL-FREEZE-CANDIDATE-001  
**Result:** **PASS WITH FREEZE-TIME PRESERVATION CONTROLS**  
**Model freeze activated:** NO  
**Held-out E1/E2/C0 evaluation:** NOT AUTHORIZED  
**Canonical execution:** NOT AUTHORIZED  
**PR #167 merge:** NOT AUTHORIZED

## Review scope

This review evaluates whether the candidate-of-record produced by deterministic TR0/TR1 training is sufficiently bound, reproducible, leakage-controlled, and internally consistent to be presented for a separate author model-freeze decision.

It does not freeze either learner and does not authorize any E1/E2/C0 inference.

## Candidate of record

- workflow run: `35939164352`
- job: `107442994831`
- training source commit: `65e8afd21316bdb40928ff30d3a1534c3893ad34`
- artifact ID: `10784198198`
- artifact files: 14
- artifact ZIP SHA-256: `e7d92ab35f34df5f34e54c7e8245e43663bdc4f20717aae643d5dbbc3ff68e01`
- candidate payload SHA-256: `49dd341bbef9f5ba694c2b127a30246cbe612f1598458b85594a4078503d4dfb`
- current artifact expiry: `2026-10-24T00:36:42Z`

## Integrity and provenance review

The exact downloaded candidate ZIP was inspected directly.

- all 13 pre-existing output files referenced by `training_execution_record.json` match their recorded SHA-256 values;
- the 14th ZIP member is the execution record itself;
- the candidate payload hash matches the execution record;
- the candidate ZIP hash matches the GitHub Actions artifact digest;
- L0 primary and audit semantic exports are byte-identical;
- L1 primary and audit semantic exports are byte-identical;
- L0 primary and audit joblib artifacts are byte-identical;
- L1 primary and audit joblib artifacts are byte-identical;
- the canonical semantic hashes match the hashes recorded during training.

## Dataset and leakage review

Training remains exactly:

- TR0: 12
- TR1: 72
- total: 84
- HOLD: 66
- ENTER_RECOVERY_GATE: 18

The downloaded L0 dataset contains exactly 84 rows with 9 features.  
The downloaded L1 dataset contains exactly 84 rows with 16 features.

Only TR0/TR1 appear in either dataset. E1, E2, and C0 are absent.

No held-out prediction/metric path was introduced, and the execution contracts continue to reject privileged research-truth fields from learner inputs.

## Model identity

### L0_BASE

- algorithm: `DecisionTreeClassifier`
- feature count: 9
- nodes: 11
- maximum depth: 4
- semantic SHA-256: `1060d526704f21d4ee72be1ace6916c061b0c254de64246b1f469a576ba42ef1`
- primary runtime artifact SHA-256: `5b38a0088c4dd0cb2ce3739993cd2d9ee7949eb1a86c188ca1bd95b38cb5f4b1`

### L1_CORROBORATED

- algorithm: `DecisionTreeClassifier`
- feature count: 16
- nodes: 15
- maximum depth: 5
- semantic SHA-256: `499fc92b714948c9a837861d4810051f51ab014f3f261a13df85646f7832f558`
- primary runtime artifact SHA-256: `6c4b589766f1df51fad2bde80350000f24c53b215ef345079fd81a8a7b98b960`

Both learners use classes `ENTER_RECOVERY_GATE` and `HOLD`.

## Runtime provenance

Training used:

- Python 3.11.16
- scikit-learn 1.9.1
- NumPy 2.4.6
- SciPy 1.17.1
- joblib 1.6.0
- threadpoolctl 3.7.0
- cloudpickle 3.1.2
- narwhals 2.26.0
- pip 26.2.1

The complete installed-distribution inventory is bound by SHA-256:

`023a745c1edde1a929030fbc15245811f828365aba11b0485c5b139a402fdd08`

## Adversarial review

No evidence was found of:

- E1/E2/C0 leakage into training;
- privileged-field leakage into the learner vectors;
- held-out inference or metrics;
- primary/audit semantic divergence;
- silent hyperparameter changes;
- model-freeze activation;
- canonical-execution activation.

A non-authoritative duplicate training run occurred after checkpointing because of pull-request path-trigger behavior. It reproduced the same datasets, dependency inventory, semantic model identities, and primary runtime model artifacts. The production-training workflow has since been sealed so later PR updates cannot automatically refit the models.

## Persistence and security finding

The runtime artifacts are `.joblib` files and therefore use a pickle-based persistence mechanism. They must be treated as trusted executable serialization objects, hash-verified before loading, and loaded only under the bound compatible environment.

The current GitHub Actions artifact is temporary. Model freeze must not rely on the 30-day Actions retention as the sole durable copy.

## Required controls at model-freeze activation

1. Preserve the exact candidate-of-record artifact, or an immutable equivalent, before expiry.
2. Verify the candidate ZIP SHA-256 before accepting the payload.
3. Freeze the L0/L1 semantic hashes above as the authoritative behavioral model identities.
4. Preserve and enforce the exact dependency inventory for any joblib loading.
5. Treat the joblib source as trusted-only and hash-verify it before load.
6. Keep E1/E2/C0 unavailable until separate held-out-evaluation authorization.

## Verdict

**PASS — S7E-AERC-MODEL-FREEZE-CANDIDATE-001 is scientifically and technically suitable to be presented for a separate model-freeze authorization, provided the freeze-time preservation controls above are implemented.**

This review does not itself freeze the models.

## Next gate

Separate explicit authorization to activate `S7E-AERC-MODEL-FREEZE-001`.

That later authorization still must not automatically authorize E1/E2/C0 inference, canonical scientific execution, PR #167 merge, or publication/result claims.
