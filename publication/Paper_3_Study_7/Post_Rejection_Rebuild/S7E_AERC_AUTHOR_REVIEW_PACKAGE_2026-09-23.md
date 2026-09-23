# S7E-AERC-001 Author Review Package — 2026-09-23

**State:** author review required  
**Protocol freeze:** NO  
**Canonical execution:** NOT AUTHORIZED  
**PR merge:** NOT AUTHORIZED

## Why review is required now

The following pre-canonical engineering gates are green:

- recovery action sink;
- shared B/C snapshot and deterministic D0/D1 runtime;
- Monocypher Ed25519 dependency selection and cFE verification boundary;
- 64-byte signed-evidence v2 host serialization/signing feasibility;
- host-only qualifier/replay/F0-F12 contract feasibility.

The next step would implement the producer/qualifier path in cFS. That would embed several currently draft semantic choices into flight-software code. Those choices should be explicitly approved before implementation.

## AR-1 — 64-byte signed-evidence v2 layout

**Recommendation: approve for pre-canonical implementation only.**

Proposed signed body:

- fixed 64 bytes;
- explicit big-endian serialization;
- domain separator `S7E-AERC-AUTH-V1`;
- producer role and authorization claim;
- opaque signed scenario/source/authority/key IDs;
- 64-bit evidence epoch;
- 64-bit controlled logical time;
- 64-bit evidence sequence;
- no topology/fault labels.

The exact layout has already passed host serialization/signing feasibility.

## AR-2 — signing-key placement

**Recommendation: approve external deterministic host-side test signing harness.**

Private test keys remain outside all cFS FSW. Producer/qualifier/verifier/decision/sink applications contain no private keys.

This preserves key-domain compromise as distinct from execution-domain compromise and avoids embedding experiment secrets into cFS binaries.

Canonical execution, if later authorized, would use a local deterministic signer only—no network signing dependency.

## AR-3 — T4 authority representation

**Recommendation: approve signed opaque authority ID + harness provenance, with no second authority signature layer.**

T4 separates primary/corroborator authority-domain IDs and harness authority state.

F10 changes authority output before source/producer signing. F1 changes the claim at the source stage after authority output. The fault cause remains research-only.

A second authority signature is not proposed because it would add another cryptographic/key hierarchy not required by RQ2 and would confound the planned trust-domain factors.

## AR-4 — qualifier semantics

**Recommendation: approve for pre-canonical implementation only.**

- `complete` is structural/applicability only;
- source trust, signature, freshness, and epoch validity remain separate features;
- structurally complete invalid-signature evidence preserves its parsed authorization claim while `signature_valid=0`;
- controlled logical ticks only; freshness threshold remains external and numerically unfrozen;
- exact duplicate is idempotent;
- valid same-sequence different-body evidence sets sticky path-local `noncontradictory=0`;
- valid lower-sequence replay also sets path-local `noncontradictory=0`;
- invalid signatures do not advance authenticated sequence state;
- cross-path primary/corroborator disagreement is not itself the same-path contradiction feature.

The host-only contract gate passed 17 tests for these semantics.

## AR-5 — F0-F12 transformation semantics

**Recommendation: approve current draft transformations for continued pre-canonical implementation.**

Key cases:

- F1/F2: false authorization at source stage, then legitimate signing;
- F3/F4: compromised key signs a false current-context claim;
- F5/F6: exact signed evidence is retained until one tick beyond the eventually frozen freshness threshold;
- F7/F8: message suppression;
- F9: post-signature XOR of bit 0 at byte 47 (epoch LSB), preserving structure while making signature and epoch invalid;
- F10: authority output is false before source signing;
- F11: F10 followed by F9 in fixed order;
- F12: two valid same-sequence opposite-authorization bodies, causing path-local equivocation.

Topology propagation continues to use the existing `domain_map()`/`affected_paths()` implementation and has passed host contract tests across all 13 profiles.

## Not being approved or frozen in this review

Even if AR-1 through AR-5 are approved, the following remain unresolved and unfrozen:

- numeric freshness threshold;
- logical-tick calibration;
- final epoch mapping;
- final opaque scenario/source/key/authority registries;
- final test key material and hashes;
- final fault-transform freeze;
- protocol/environment freeze;
- L0/L1 production training/freeze;
- canonical Study-7E execution;
- publication claims from Study-7E results;
- PR #167 merge.

## Effect of approval

Approval of AR-1 through AR-5 would authorize only the next **pre-canonical implementation** step:

1. implement cFS qualifier plumbing using configurable, non-frozen timing/registry values;
2. implement producer message plumbing with the external deterministic signing boundary;
3. add leakage, contract, and runtime tests;
4. continue proof-before-freeze engineering qualification.

It would not authorize scientific execution or any freeze listed above.
