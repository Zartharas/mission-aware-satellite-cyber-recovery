# S7E-AERC-001 Qualifier Time/Replay and Fault-Transformation Draft — 2026-09-23

**Status:** draft, not frozen  
**Canonical execution:** NOT AUTHORIZED

## Qualifier semantics

The draft uses controlled logical ticks only. The producer signs `issued_logical_time`; the qualifier owns the freshness threshold. No wall-clock value or producer-selected expiration window enters the contract.

Candidate freshness rule:

`fresh = issued_time <= now_tick && (now_tick - issued_time) <= freshness_max_age_ticks`

The numeric threshold remains unresolved.

The signed opaque scenario ID is a context gate, not a policy feature. Wrong-scenario evidence is dropped as non-applicable.

Structural `complete` does not duplicate signature/trust/freshness/epoch features.

For structurally complete evidence with an invalid signature, the parsed authorization claim remains available as the independent authorization feature while `signature_valid=0`. Deterministic D0/D1 remain fail closed because signature validity is separately required.

## Sequence/replay semantics

Authenticated sequence state is path-local and keyed by signed scenario/role/source/key/epoch.

- first valid sequence: baseline;
- higher valid sequence: advance;
- same sequence + byte-identical body: idempotent duplicate;
- same sequence + different valid body: sticky contradiction;
- lower valid sequence: rollback/replay inconsistency and sticky contradiction;
- invalid-signature evidence does not advance authenticated sequence baseline.

Contradiction state resets at scenario/epoch boundary.

## Candidate fault transformations

The draft fixes a stage order:

authority → source → serialization → signing → execution emission → transport → qualifier.

Notable proposals:

- F1/F2: false authorization at source stage, then legitimate signing;
- F3/F4: compromised key signs a false current-context claim;
- F5/F6: retain exact signed bytes but evaluate one tick beyond the eventually frozen freshness threshold;
- F7/F8: message suppression;
- F9: after signing, XOR bit 0 at byte 47 (epoch LSB), preserving structure but invalidating signature and epoch;
- F10: authority output is flipped before source signing;
- F11: F10 first, then F9 post-signature transport mutation;
- F12: execution compromise emits two separately signed same-sequence bodies with opposite authorization values, producing path-local equivocation.

These transformations are designed to keep fault cause/domain research-only while allowing the policy-visible effects to arise through the implemented evidence path.

## Remaining blockers

No numeric freshness threshold, epoch mapping, final registries, final keys, or transformation freeze is authorized. F9 and F12 in particular require author review before protocol freeze.
