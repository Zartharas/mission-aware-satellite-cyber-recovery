# WP4 D-064 Exclusive-Writer Technical-Control Remediation Design R2

Date: 2026-08-10
Governance ID: `D-063R2-C3B-I2D-D064-RD1`
Phase: `DESIGN_AND_GOVERNANCE_ONLY`
Active contract: `0.4.13` — unchanged by this design
Successor contract revision: `UNASSIGNED`
D-064 authorization: `false`
Runtime authorization: `false`
Runtime attempts authorized: `0`
WP5 execution authorization: `false`

## 1. Governing disposition

This record freezes the corrected R2 remediation architecture discovered during
D-064 preauthorization review. It does **not** authorize source implementation,
successor artifact creation, static-verifier execution, execution #11, authorized
root selection or creation, D-064, runtime, Docker/NOS3/Fortytwo activity,
materialization, event injection, or WP5.

The current accepted v3 implementation remains the historical execution-#10
static-PASS baseline. Its exact bytes are preserved and are not silently edited.
The existing static PASS is valid for that exact historical identity chain only
and cannot be reused as static acceptance for the successor implementation.

## 2. Bound current baseline

- merged main: `1f75c7a7249df9057e1518fd5004928a0411a203`
- merged tree: `416b8234c72f95956842ca63cc85799615caf172`
- active contract SHA-256: `f161169bf8096be3c9f94718c460ad3d39b6b6b6a43c1d633d3c3ec210ac15d2`
- accepted v3 candidate SHA-256: `599c534df37b127f7325ad513eecc4b24bdc0d37a56c32b4448a0b0099c13a1f`
- historical transaction-v1 SHA-256: `0d2e76aab5b9e604b632f19caf2f2c9b584b191c9b7fafaff9bd1ae0d9ecff83`
- historical v3 generator SHA-256: `7140b7ff1aa1873ac020bae24d2a921a343f3d1fde86c6bbb4aece45cf229812`
- historical v3 verifier SHA-256: `e803d59b0a0afb0fb49c05b42053ab07cc866494711c09248ba49574b6bb1c2b`
- canonical runtime-material manifest SHA-256: `5026176de3084c8015fd7f84827ce8a4e5d44df7e986bc142815eb0d649e81cd`
- D-064 preauthorization gap classifier artifact SHA-256: `1a9c3834bb43411200ad677b8130a1c5eb2f2f63f4e45b65eecd87246465283c`
- corrected remediation-design R2 artifact SHA-256: `8723d5b19948df0ccc703c0ae7928e3eb70aa81de3e9032eb2702134412d17eb`
- current static verification: `PASS`
- execution #10: consumed, no rerun
- current D-064 status: `READY_FOR_SEPARATE_D064_CONSIDERATION`
- current runtime authorization: `false`
- current runtime attempts: `0`

## 3. Blocking technical findings frozen before D-064

The accepted transaction-v1/candidate-v3 chain is not eligible for D-064
authorization because the preauthorization classifier established three
technical gaps relative to D-063R2-PB1/TM1:

1. technical authorized-root ACL validation is not implemented;
2. a serialized transaction lock is not implemented;
3. the transaction receipt does not bind retained exclusive-writer evidence
   references and instead retains the historical
   `SATISFIED_DEEP_IMMUTABLE_CONTEXT` marker.

The first three already-implemented controls remain preserved as historical
evidence: authorized-root owner/mode/symlink/device-inode controls, staging mode
`0700`, and final-destination no-replace collision protection.

## 4. Versioned successor architecture

The remediation is a versioned successor, not an in-place rewrite:

- successor transaction tool: `scripts/nos3_runtime_transaction_v2.py`
- successor generator: `scripts/prepare_passive_time_witness_runtime_candidate_v4.sh`
- successor generated candidate version: `V4`
- successor verifier: `scripts/verify_passive_time_witness_runtime_candidate_v4_static.sh`
- successor generated candidate is not tracked as a repository source artifact
- canonical manifest identity is reused unchanged
- successor contract schema is required, but its field name is not frozen here
- successor contract revision remains `UNASSIGNED`

The exact v3 candidate, generator, verifier, and transaction-v1 identities remain
historical and immutable. No successor file is created by this governance gate.

## 5. Authorized-root ACL control design

The first D-064 successor is reviewed for the controlled Darwin host only.

- ACL inspection is descriptor-bound using the Darwin ACL API
  (`acl_get_fd_np` / entry iteration / `acl_free`);
- policy for the first D-064 attempt is
  `NO_EXTENDED_ACL_ENTRIES_FOR_FIRST_D064_ATTEMPT`;
- ACL retrieval or parsing uncertainty fails closed;
- ACL state is validated against the opened authorized-root descriptor;
- ACL validation is repeated immediately before outer transaction publication;
- this technical control does not establish that no external host writer exists.

The strict no-extended-ACL policy is intentionally narrower than interpreting a
complex allowlist for the first bounded attempt.

## 6. Serialized materialization control design

The successor transaction tool must serialize cooperating materializers using
`fcntl.flock` with `LOCK_EX|LOCK_NB`.

Required properties:

- lock-file basename is **not frozen by this design**;
- lock file mode: `0600`;
- lock object must be regular, link count one, owned by the effective UID, and
  on the authorized-root device;
- lock acquisition occurs before staging creation;
- contention fails closed before staging/materialization;
- the lock is held through the transaction `finally` boundary;
- lock/release failures are fail-closed where they affect transaction validity.

`flock` is advisory. Therefore this control may prove serialization among
cooperating materializers, but the CLI must **not** claim that it proves absence
of another host writer.

## 7. Retained exclusive-writer evidence binding

A canonical retained host-evidence artifact is required before D-064 may later
be considered.

This design freezes only the authority model:

- exact host-evidence schema is **not** frozen here;
- host-evidence path is not authorization authority;
- SHA-256 of the actual retained evidence bytes is authority;
- the future successor contract must bind that SHA-256;
- the transaction tool must hash the actual evidence bytes it receives;
- the transaction receipt must bind the same evidence SHA-256;
- the receipt must record ACL-validation and serialization-control disposition;
- host operational evidence remains a separate gate and must still establish
  the TM1 conditions that the transaction CLI cannot prove itself.

No evidence file is created and no authorized root is selected in this phase.

## 8. Static-verification and phase boundary

Any correction to the transaction tool changes its identity. Because the
candidate receipt schema must also change, the successor candidate/generator
identity changes; because the static verifier binds those identities, the
successor verifier changes as well.

Therefore:

- current v3 static PASS reuse for v4: `false`;
- new static verification required: `true`;
- execution #10 rerun authorized: `false`;
- next future production static-verifier execution number: `11`;
- execution #11 authorized now: `false`;
- source implementation authorized now: `false`;
- authorized-root selection authorized now: `false`;
- authorized-root creation authorized now: `false`;
- D-064 authorized now: `false`;
- runtime authorized now: `false`;
- runtime attempts authorized now: `0`.

The next phase after independent review and publication of this design is a
**separately authorized versioned-v4 source implementation gate**. Publication
of this design alone does not authorize implementation.

## 9. Interpretation and research-claim boundary

Nothing in this design establishes a scientific outcome, mission impact,
generic-radio defect, callback invocation, CryptoLib behavior, or SDLS behavior.
The eventual bounded passive attempt, if separately authorized after the entire
replacement static-verification and host-evidence sequence, remains limited to
the interpretation constraints already frozen by D-061.

## 10. Next acceptance gate

`C3B_I2D_D064_V4_REMEDIATION_DESIGN_INDEPENDENT_GOVERNANCE_REVIEW`

The independent review must bind this record and lock byte-for-byte, prove the
active contract and historical v3 identities remain unchanged, prove no
successor source exists, and keep execution #11, authorized-root creation,
D-064, runtime, and WP5 closed.
