# S7E-AERC-001 Signed-Evidence v2 Host Feasibility Checkpoint — 2026-09-23

**Experiment:** `S7E-AERC-001`  
**State:** engineering feasibility only  
**Qualification head:** `7f33cbb9653f3016a8ce87a17105a56ade644bba`  
**Canonical execution:** NOT AUTHORIZED

## Result

**64-byte signed-evidence v2 host-side serializer/signing feasibility: PASS**

The reviewed draft candidate was serialized explicitly in big-endian form, parsed back to the same fields, signed with Monocypher 4.0.3 using the published RFC 8032 Section 7.1 Test 1 seed, and verified with the corresponding public key.

The RFC seed is standard public test-vector material. It is not final Study-7E experiment key material.

## Exact CI evidence

- workflow: `Study 7E signed-evidence v2 feasibility`
- workflow ID: `365357473`
- run ID: `35896385014`
- job ID: `107301223761`
- conclusion: `success`
- artifact ID: `10767022256`
- artifact digest: `sha256:ebd5af65fbbbc5a0bd555362d5eb88f125c43f3e7f5c29aeaacc37fc2d6a1d1a`

## Exact engineering vector

Serialized 64-byte body:

`5337452d414552432d415554482d5631010101005337480100001001000030010000200100000000000000000000000700000000000003e80000000000000001`

Body SHA-256:

`d877eb02f03851e34889b635c40008ec5b9eaa48cc0669720356ef6caaa92c73`

RFC 8032 Test 1 public key:

`d75a980182b10ab7d54bfed3c964073a0ee172f3daa62325af021a68f707511a`

Deterministic signature over the 64-byte candidate body:

`471f3c1a399077191999ce25390a176aa85a06e919cc472f9d0a5b1df2b5f9eed13e572e8708c61a1d4480d38c932829f1cafd567d68bd78fe78a526ba6f320b`

## Assertions

- `SIGNED_EVIDENCE_V2_SERIALIZE_PARSE=PASS`
- `SIGNED_EVIDENCE_V2_RFC8032_KEY_DERIVATION=PASS`
- `SIGNED_EVIDENCE_V2_SIGN_VERIFY=PASS`
- `SIGNED_EVIDENCE_V2_PROTECTED_FIELD_MUTATIONS_REJECT=PASS`
- `SIGNED_EVIDENCE_V2_MALFORMED_RESERVED_REJECT=PASS`
- `SIGNED_EVIDENCE_V2_INVALID_FIELD_REJECT=PASS`
- `SIGNED_EVIDENCE_V2_SECRET_KEY_IN_CFS_FSW=false`
- `SIGNED_EVIDENCE_V2_FINAL_KEY_REGISTRY_FROZEN=false`
- `SIGNED_EVIDENCE_V2_POLICY_BINDING=false`

The mutation gate changes protected bytes including scenario ID, authorization, source ID, authority ID, key ID, logical time, and sequence and requires verification failure.

## Boundary

This checkpoint proves only that the current 64-byte draft has an unambiguous host-side implementation and can be signed/verified with the selected Monocypher dependency.

It does **not** freeze:

- canonical signed bytes;
- final experiment keys;
- public-key registries;
- freshness/epoch/replay semantics;
- fault transformations;
- qualifier-to-policy binding;
- protocol/environment;
- learned models.

The run executed zero Study-7E scientific scenarios and generated no scientific results.
