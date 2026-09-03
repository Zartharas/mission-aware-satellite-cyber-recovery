# Study 8 Synthetic Contact Model

**Experiment:** `S8-PQC-ICR-001`  
**Phase:** 8.0 design candidate  
**Model type:** deterministic finite logical-time/contact-budget model  
**Runtime status:** not authorized

## Logical time

The model uses integer slots `t = 0..47`. A slot is an ordering unit only. It has no defined duration and must not be converted to seconds, milliseconds, orbital periods, RF propagation time, or any other physical quantity.

The observation horizon is one synthetic 48-slot cycle.

## Contact semantics

A contact window is represented by:

```text
(start_slot, capacity_bytes)
```

Every contact in the Phase-8.0 candidate is one logical slot wide. `capacity_bytes` is a synthetic upper bound on cryptographic-object bytes that the model may move during that opportunity.

The budget deliberately excludes transport headers, CCSDS framing, certificates, error-correction coding, retransmission protocols, RF effects, and implementation overhead.

Cryptographic objects may be segmented across contact opportunities. Partial bytes persist across contacts unless the frozen disruption schedule explicitly discards them. An object becomes protocol-actionable only after all of its bytes have arrived.

A single abstract shared byte budget is used per contact. Uplink/downlink direction is not modeled in Phase 8.0.

## Contact regimes

All four regimes contain exactly `65,536` nominal cryptographic-budget bytes over the complete 48-slot cycle. This controls total-cycle capacity while varying temporal distribution.

### R1_FREQUENT_SMALL

- capacity per contact: `4,096` bytes
- base contact slots: `[0, 2, 5, 8, 11, 14, 17, 20, 23, 26, 29, 32, 35, 38, 41, 44]`
- contacts per cycle: `16`
- nominal cycle capacity: `65,536` bytes

### R2_PERIODIC_MEDIUM

- capacity per contact: `8,192` bytes
- base contact slots: `[0, 5, 11, 17, 23, 29, 35, 41]`
- contacts per cycle: `8`
- nominal cycle capacity: `65,536` bytes

### R3_SPARSE_LARGE

- capacity per contact: `16,384` bytes
- base contact slots: `[0, 11, 23, 37]`
- contacts per cycle: `4`
- nominal cycle capacity: `65,536` bytes

### R4_CLUSTERED_MEDIUM

- capacity per contact: `8,192` bytes
- base contact slots: `[0, 1, 13, 14, 29, 30, 44, 45]`
- contacts per cycle: `8`
- nominal cycle capacity: `65,536` bytes

## Compromise placement / phase offset

The candidate population crosses each regime with six compromise phase offsets:

```text
p ∈ {0,1,2,3,4,5}
```

For a base contact slot `s`, the effective post-compromise slot is:

```text
effective_slot = (s - p) mod 48
```

Effective slots are sorted before evaluation. This construction represents six deterministic placements of the compromise within the repeating synthetic contact cycle while preserving the number of contacts and total 48-slot capacity.

The offsets are design factors only; they do not correspond to orbital phase, clock time, or physical geometry.

## Recovery deadlines

Three logical deadlines are candidates:

```text
D12 = 12 slots
D24 = 24 slots
D48 = 48 slots
```

A recovery is on time only when `TRUST_RESTORED` is reached strictly within the selected finite horizon according to the frozen implementation convention. The exact boundary convention (`< deadline` versus `<= deadline`) must be fixed in the independent design review before implementation.

## Disruption schedules

### A0_NONE

No adversarial transport disruption.

### A1_DROP_FIRST_LARGEST_OBJECT_FRAGMENT

Identify the largest cryptographic object in the selected Q-profile. The first contact allocation carrying bytes of that object is discarded once. The contact capacity consumed by those bytes is not restored. The object must retransmit the lost bytes in later contact capacity.

This is a transport-disruption abstraction, not cryptanalysis.

### A2_DELAY_FIRST_TRANSITION_PROOF_ONE_CONTACT

When the transition-proof signature first becomes ready to transmit, it is withheld for exactly one subsequent eligible contact opportunity. Other already-ready objects may use that contact capacity. If no other object is ready, the remaining capacity is unused.

### A3_STALE_EPOCH_REPLAY_AT_COMMIT

At the first logical commit opportunity, a previously valid stale-epoch commit is presented. The replay must fail the monotonic epoch check. It consumes that logical commit opportunity and defers the legitimate new-epoch commit to a later eligible opportunity, but it adds no bytes to the NIST-derived cryptographic-object budget.

This deliberately separates epoch-safety behavior from assumptions about the size of a legacy replay object.

## Frozen-model constraints for later implementation

A conforming implementation must:

1. materialize the same contact schedule from `(regime, phase_offset)`;
2. never invent physical-time conversions;
3. account for every scheduled cryptographic byte;
4. preserve partial-object bytes except under A1;
5. prevent later messages from becoming actionable before their prerequisites are complete;
6. treat A3 as replay of a valid stale object rather than a forgery;
7. terminate deterministically at either `TRUST_RESTORED` or one frozen terminal failure state;
8. emit enough provenance to independently reconstruct every observation.
