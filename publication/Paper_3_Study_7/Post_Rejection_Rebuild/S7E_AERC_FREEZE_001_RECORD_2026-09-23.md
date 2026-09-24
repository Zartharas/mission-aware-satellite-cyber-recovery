# S7E-AERC-001 Freeze Record 001 — 2026-09-23

**Freeze ID:** `S7E-AERC-FREEZE-001`  
**Qualified candidate:** `S7E-AERC-FC-001`  
**Author freeze approval:** YES  
**Production L0/L1 training:** NOT AUTHORIZED  
**Production model freeze:** NOT AUTHORIZED  
**Canonical scientific execution:** NOT AUTHORIZED  
**PR #167 merge:** NOT AUTHORIZED  
**Publication/result claims:** NOT AUTHORIZED

## Freeze action

The author explicitly approved `S7E-AERC-FC-001` for Study-7E protocol, environment, public-key registry, fault-transformation, and learner-protocol freeze.

The freeze is implemented by `study7e/FREEZE_MANIFEST_001.json`, which binds the exact previously qualified Git blobs rather than mutating those historical candidate inputs after qualification.

This preserves the evidentiary chain from candidate design through qualification to freeze.

## Frozen components

1. **Protocol** — exact signed-evidence, qualifier/replay, policy-contract, topology/fault, manifest-generation, and related design blobs recorded by the freeze manifest.
2. **Environment** — standalone cFS v7.0.1 at `088b2fa828db9ff7e00733f1908e0eeb59f66ce3`; Monocypher 4.0.3 at `ab2b16dd619ad5f6979a4fbe69cfa324a6fcc35f`; learner runtime Python 3.11.16 / scikit-learn 1.9.1.
3. **Public-key registry** — three deterministic non-secret Ed25519 research public keys in `study7e/configs/frozen_public_key_registry_001.json`; no private key is committed or placed in cFS.
4. **Fault transformations** — F0-F12 frozen by exact source blob `292db65822a866bce5e4ad50278b98090bf4d24b`, with F5/F6 logical-tick staleness, F9 byte-47 mutation, F11 ordered authority+transport mutation, and F12 signed equivocation semantics preserved.
5. **Learner protocol** — one shared deterministic `DecisionTreeClassifier` rule for L0/L1, TR0/TR1-only training eligibility, E1/E2/C0 exclusion, fixed hyperparameters, and deterministic random state. No model has been trained.

## Frozen execution parameters

- clock: scenario-local logical tick;
- freshness max age: `0` ticks;
- nominal issue/evaluation tick: `0`;
- stale fault evaluation tick: `1`;
- evidence epoch: `1`;
- opaque registry algorithm: SHA-256 first four bytes as big-endian u32 with zero/collision retry;
- prospective scenario registry entries: `280`;
- current collision count: `0`.

## Qualification basis

The qualified candidate head was `aeb14388e6355e84bd7b33d498945b16f3c2ebe6`.

Exact-head qualification evidence included:

- freeze-candidate workflow `35922344027`;
- freeze contract job `107389099534` — success;
- deterministic public-key job `107389099391` — success;
- pre-canonical workflow `35922344075`;
- pre-canonical contracts job `107389099454` — success;
- upstream-identities job `107389099288` — success.

## Amendment rule

The frozen source blobs are immutable for `S7E-AERC-FREEZE-001`.

Any semantic change requires:

1. a new freeze candidate;
2. a new freeze identifier;
3. re-qualification;
4. explicit author approval before use.

A change to signed-evidence schema, public-key registry, or execution contract also requires a new evidence epoch rather than modification of epoch 1.

## Explicitly outside this freeze

This freeze does **not** authorize:

- training L0 or L1 production models;
- freezing trained model artifacts;
- canonical Study-7E scenario execution;
- creation of canonical results;
- PR #167 merge;
- publication claims based on Study-7E outcomes.

The next gate is a separately authorized deterministic production-training run plan. Until such authorization is granted, the frozen learner protocol remains untrained.
