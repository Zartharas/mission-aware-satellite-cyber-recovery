# S7E-AERC-001 Model Freeze 001 — 2026-09-23

**Model freeze ID:** `S7E-AERC-MODEL-FREEZE-001`  
**Candidate of record:** `S7E-AERC-MODEL-FREEZE-CANDIDATE-001`  
**Review:** `S7E-AERC-MODEL-FREEZE-REVIEW-001` — PASS with preservation controls  
**Authorization:** model freeze only

## Activation

The reviewed L0 and L1 models are frozen by:

- exact semantic model identities;
- exact primary runtime model bytes preserved as base64 text;
- exact dependency inventory;
- exact pre-fit binding;
- exact candidate payload and training execution record;
- frozen dataset hashes and training partition.

The historical candidate payload remains unchanged and still states that it was not frozen at candidate-generation time. The authoritative activation is `study7e/MODEL_FREEZE_MANIFEST_001.json`.

## Frozen semantic identities

- L0_BASE: `1060d526704f21d4ee72be1ace6916c061b0c254de64246b1f469a576ba42ef1`
- L1_CORROBORATED: `499fc92b714948c9a837861d4810051f51ab014f3f261a13df85646f7832f558`

## Frozen runtime-artifact identities

- L0_BASE: `5b38a0088c4dd0cb2ce3739993cd2d9ee7949eb1a86c188ca1bd95b38cb5f4b1`
- L1_CORROBORATED: `6c4b589766f1df51fad2bde80350000f24c53b215ef345079fd81a8a7b98b960`

The runtime payloads are pickle/joblib objects. Integrity verification must decode and hash them without deserializing. Actual loading is trusted-source-only and requires the bound environment.

## Boundaries

This freeze does **not** authorize:

- E1/E2/C0 held-out inference or metrics;
- canonical scientific execution;
- PR #167 merge;
- publication/result claims.

The next gate is separate held-out-evaluation planning/review and explicit authorization.
