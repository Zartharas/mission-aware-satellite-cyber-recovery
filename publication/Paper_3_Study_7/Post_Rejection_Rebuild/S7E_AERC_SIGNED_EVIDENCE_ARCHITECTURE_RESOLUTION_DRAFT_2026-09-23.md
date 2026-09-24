# S7E-AERC-001 Signed-Evidence Architecture Resolution Draft — 2026-09-23

**State:** technical draft only — not author-approved or frozen  
**Canonical execution:** NOT AUTHORIZED

## 1. Signing-key placement

Recommended draft pattern: **external deterministic test signing harness**.

Private Ed25519 test keys remain outside cFS flight-software applications. The cFS verifier, qualifier, decision app, action sink, and producer app do not store private keys.

The controlled host-side Study-7E harness owns test signing keys and performs deterministic signing without external network dependency.

This preserves the intended distinction between:

- **key-domain compromise** (F3/F4): controlled access to the targeted test signing key; and
- **execution-domain compromise** (F12): producer behavior can be altered without automatically granting signing-key access.

The producer path may construct/emit or forward signed evidence through the controlled test boundary, but it does not embed private keys.

This is a pre-canonical design decision only. Final key generation, storage, registry IDs, and hashes remain unfrozen.

## 2. T4 authority-domain representation

Recommended draft pattern: **signed opaque authority ID + harness provenance**, with **no second authority-signature hierarchy**.

The signed v2 evidence body already carries an opaque `authority_id`. The harness keeps the authority-domain alias map and stage provenance outside policy-visible inputs.

Stage semantics:

- authority state exists upstream of source/producer signing;
- F10 changes the primary authority output before canonicalization/signing;
- F1 changes the authorization claim at the source stage after authority output but before signing;
- T0–T3 may alias authority IDs according to the topology manifest;
- T4 uses distinct primary/corroborator authority IDs and independent authority-domain state.

This models authority separation directly without adding another cryptographic layer that would introduce an additional key hierarchy and confound the planned trust-domain factors.

## 3. Why this is the smaller scientifically cleaner design

The experiment asks how separation of source, signing-key, execution, transport, and authority domains changes behavior. It does not require every trust domain to have its own signature protocol.

One producer signature over an opaque authority identifier is sufficient to prevent post-signature authority relabeling while allowing the harness to inject authority-stage faults independently from source-stage and key-stage faults.

The architecture therefore keeps:

- one Ed25519 producer-evidence signature per evidence path;
- independent research-only domain provenance;
- explicit stage-ordered fault injection;
- no private key in cFS FSW.

## 4. Remaining blockers before freeze

Still unresolved:

1. exact local harness↔producer injection/IPC mechanism;
2. final deterministic test-key generation and private-key storage procedure;
3. final opaque source/key/authority registries;
4. logical-time unit, freshness thresholds, epoch semantics, and replay rule;
5. exact F3/F4/F9/F10/F11/F12 byte/stage transformations;
6. independent leakage/audit assertions for the revised producer/qualifier path.

No policy feature is bound to this design yet. No protocol freeze or canonical execution is authorized.
