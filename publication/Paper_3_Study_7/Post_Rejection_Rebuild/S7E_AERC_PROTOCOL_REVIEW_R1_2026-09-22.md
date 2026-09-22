# S7E-AERC-001 Protocol Review R1

**Review ID:** `S7E-AERC-PROTOCOL-REVIEW-R1`  
**Date:** 2026-09-22  
**Stage:** pre-freeze implementation review  
**Scientific execution:** NOT AUTHORIZED  
**Outcome:** `DESIGN_DEFECT_FOUND_AND_CORRECTED_BEFORE_EXECUTION`

## Finding

The first protocol draft trained `L0_BASE` and `L1_CORROBORATED` only on scenarios with `security_signal=1`, while the C0 control block evaluated `security_signal=0`.

That design would make C0 partly a test of an unseen feature value rather than a clean architecture/policy comparison. A learned selector could fail C0 merely because no no-signal example existed in training. That would create an avoidable reviewer attack and could unfairly disadvantage the learned policies relative to the deterministic comparators.

## Correction

The prospective population is revised before protocol freeze and before scientific execution.

### Training

- TR1: original 72 security-response scenarios on T0-T2 and F0-F5.
- TR0: 12 no-signal baseline scenarios on T0-T2 and F0 only.
- total training = 84.

### Evaluation

- E1: 72 unseen-fault scenarios.
- E2: 96 held-out-topology scenarios.
- C0: 8 no-signal controls on held-out T3-T4 and F0 only.
- total canonical evaluation = 176 scenarios.
- four policies per evaluation scenario = 704 planned decision observations.

### Total manifest

The complete prospective manifest remains exactly 260 scenarios:

`84 + 72 + 96 + 8 = 260`.

## Why this is stronger

- both values of `security_signal` occur in learned-policy training;
- no C0 scenario duplicates a TR0 topology/state combination;
- T3/T4 remain held out from training;
- E1 still holds out F6-F11 from T0-T2 training;
- no result was inspected because no scientific execution exists.

## Governance

This correction changes only the prospective design. It does not alter Study 7, does not constitute a Study-7E result, and does not authorize canonical execution.
