# Phase 8 Pre-Runtime Design Amendment 1

**Experiment:** `S8-PQC-ICR-001`  
**Amendment:** `S8-DESIGN-AMEND-001`  
**Parent design lock:** `b5172e1d4ba79b60b8fccbd119f087a33c6fd037`  
**Status:** `PRE_RUNTIME_DESIGN_AMENDMENT_LOCKED_NO_POPULATION_CHANGE`

Phase-8.1 implementation construction exposed four specification issues that were not visible in the Phase-8.0 static review. Because no runtime or campaign execution has occurred, they are repaired now as an explicit pre-runtime amendment rather than being silently encoded in software.

## 1. P1/P2 observational alias

The Phase-8.0 endpoint set did not measure P2's defining period in which the successor epoch is accepted after transition-proof acceptance while the predecessor remains accepted until commit. Consequently, P1 and P2 would have been observationally identical.

The amendment adds:

```text
dual_epoch_overlap_slots
```

For `P2_HYBRID_OVERLAP` only:

```text
max(0, min(commit_slot_or_deadline, deadline) - proof_accepted_slot)
```

It is zero if transition proof is never accepted and zero for all non-P2 policies.

This is a logical slot-index separation. It is not an empirical time, spacecraft latency, operational risk estimate, or measured security exposure.

## 2. A2 contact convention

When the transition-proof object first becomes ready during a contact, that same contact is the one withheld opportunity under `A2_DELAY_FIRST_TRANSITION_PROOF_ONE_CONTACT`. Proof bytes may not use the remaining capacity in that contact. Transmission becomes eligible again at the next scheduled contact.

## 3. P3 terminal specificity

If `P3_CONTACT_AWARE_STAGED` actively blocks commit because nominal remaining scheduled capacity before the deadline is smaller than the unsent commit-plus-confirmation requirement, the terminal state is specifically:

```text
CONTACT_BUDGET_EXHAUSTED
```

That specific guard outcome takes precedence over a generic incomplete-transfer label for the same blocked commit.

## 4. Deadline-truncated R1 schedule multiplicity

All 24 `(regime, phase_offset)` full-cycle schedules remain unique. However, at D12 and D24:

- R1 phase offsets `1` and `4` have identical pre-deadline contact-slot sets;
- R1 phase offsets `2` and `5` have identical pre-deadline contact-slot sets.

The six phase offsets remain separate, equally weighted factor positions because they represent distinct placements in the frozen repeating 48-slot construction. The study must not claim that every deadline-truncated schedule is unique.

## No population change

The factor lattice remains:

```text
3 × 4 × 4 × 4 × 6 × 3 = 3,456
```

No cryptographic size, contact regime, policy definition, disruption factor, phase level, or deadline level is added or removed.

## Closed gates

```text
runtime_authorized=false
canonical_execution_authorized=false
campaign_authorization_present=false
results_generation_authorized=false
```
