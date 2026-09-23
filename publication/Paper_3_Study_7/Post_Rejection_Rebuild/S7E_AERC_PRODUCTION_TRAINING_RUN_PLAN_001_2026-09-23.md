# S7E-AERC-001 Production Training Run Plan 001 — 2026-09-23

**Plan:** `S7E-AERC-TRAINPLAN-001`  
**Frozen protocol:** `S7E-AERC-FREEZE-001`  
**Status:** preparation/review only  
**Production L0/L1 training:** NOT AUTHORIZED  
**Production model freeze:** NOT AUTHORIZED  
**Held-out E1/E2/C0 evaluation:** NOT AUTHORIZED  
**Canonical scientific execution:** NOT AUTHORIZED  
**PR #167 merge:** NOT AUTHORIZED

## Objective

Define the exact deterministic procedure that will be used if production L0/L1 training is separately authorized. This plan performs no model fit and creates no model artifact.

## Frozen training contract

The frozen learner protocol fixes a shared `DecisionTreeClassifier` rule for both learned comparators. Training is restricted to `TR0` and `TR1`; `E1`, `E2`, and `C0` remain held out.

The training partition is fixed at:

- TR0: 12 scenarios;
- TR1: 72 scenarios;
- total: 84 scenarios.

Under the frozen `objective_action()` rule, the expected training labels are:

- `HOLD`: 66;
- `ENTER_RECOVERY_GATE`: 18.

The same 84 scenario labels are used for L0 and L1. Only the feature views differ.

## Feature views

### L0_BASE

Nine features, in exact frozen order:

1. `primary_signature_valid`
2. `primary_source_trusted`
3. `primary_fresh`
4. `primary_epoch_valid`
5. `primary_noncontradictory`
6. `primary_complete`
7. `primary_authorization`
8. `health_ready`
9. `security_signal`

### L1_CORROBORATED

The same nine base features followed by:

10. `corr_signature_valid`
11. `corr_source_trusted`
12. `corr_fresh`
13. `corr_epoch_valid`
14. `corr_noncontradictory`
15. `corr_complete`
16. `corr_authorization`

Research-only truth and experiment metadata—including true authorization/health, fault profile, topology, domain alias map, and the objective label itself—are prohibited from model inputs.

## Deterministic dataset construction

If training is later authorized:

1. verify `S7E-AERC-FREEZE-001` integrity;
2. require a separate training-authorization record naming this plan;
3. materialize exactly one frozen policy snapshot for each TR0/TR1 scenario;
4. project only the frozen L0/L1 feature vectors;
5. join the research-side objective label only after snapshot capture/projection;
6. order rows by TR0 then TR1 and ascending numeric scenario suffix;
7. serialize each learner dataset as canonical UTF-8 JSON Lines;
8. compute and bind SHA-256 over the exact bytes for both L0 and L1 before any fit operation.

No evaluation-block row may enter the training materialization path.

## Learner runtime

Frozen top-level runtime:

- Python 3.11.16;
- scikit-learn 1.9.1;
- `DecisionTreeClassifier`;
- criterion `gini`;
- splitter `best`;
- no maximum depth;
- `min_samples_split=2`;
- `min_samples_leaf=1`;
- `max_features=None`;
- `class_weight=None`;
- `ccp_alpha=0.0`;
- `random_state=2571582253`.

No cross-validation, hyperparameter search, or evaluation-set tuning is permitted.

## Dependency provenance

The freeze explicitly pins Python and scikit-learn but does not enumerate exact transitive package versions. The training run therefore must create an isolated environment and record the exact resolved dependency inventory **before fit**, including NumPy, SciPy, joblib, threadpoolctl, pip, and the complete installed-distribution list. The inventory itself receives a SHA-256 provenance hash.

This does not alter the frozen scientific learner rule. It records the concrete software resolution used for the one production training event. If the resolved environment is considered unacceptable during preflight, training stops before fit.

## Future authorized fit sequence

After all pre-fit gates pass, a future training authorization would permit:

1. one primary L0 fit;
2. one primary L1 fit;
3. one audit refit of each learner from the identical bound dataset bytes and identical parameters;
4. comparison of deterministic semantic model fingerprints;
5. preparation of a **model-freeze candidate** containing dataset hashes, dependency inventory hash, semantic model hashes, and runtime-artifact hashes.

Training then stops. E1/E2/C0 evaluation remains prohibited until the trained models are separately reviewed and frozen.

## Model identity

The scientific identity of each trained tree will use a deterministic semantic export of the learned tree structure and metadata, with lossless floating-point representation, plus SHA-256. A runtime artifact hash will also be recorded. Primary/audit semantic hashes must match for each learner.

No trained artifact becomes authoritative merely because training succeeded. Model freeze remains a separate human authorization.

## Adversarial review

The plan addresses the main failure modes before training:

- training/evaluation leakage is blocked by the frozen block contract;
- privileged research truth is excluded from model features;
- both learned comparators use the same frozen algorithm/hyperparameter rule;
- dataset bytes are hashed before fit;
- exact software resolution is captured before fit;
- an independent audit refit checks deterministic model identity;
- no performance result can influence hyperparameters;
- no held-out evaluation occurs before model freeze;
- no model artifact is considered frozen without separate authorization.

Residual risk: exact transitive learner dependency versions were not enumerated in `S7E-AERC-FREEZE-001`. The run plan mitigates this by recording the complete resolved environment before fit and stopping if preflight review rejects it. This provenance must accompany any later model-freeze candidate.

## Authorization boundary

This document is a run plan only. The next human gate, after plan qualification, is explicit authorization to perform the deterministic L0/L1 production training run under this plan. That authorization will still not authorize model freeze, held-out evaluation, canonical scientific execution, PR merge, or publication/result claims.
