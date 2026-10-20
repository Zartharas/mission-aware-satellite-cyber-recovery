# Rebuilt Paper 3 — Venue-Neutral R2 Scientific Preservation Audit

**Audit ID:** `PAPER3-S7-S7E-MANUSCRIPT-AUDIT-R2-001`  
**Date:** 2026-09-24  
**R2 manuscript:** `PAPER3_REBUILT_MANUSCRIPT_R2.md`  
**Basis R1 scientific audit:** `PAPER3-S7-S7E-MANUSCRIPT-AUDIT-R1-001`  
**Result:** **PASS**

## Scope

R2 is a literature-positioning and bibliography revision of the scientifically audited R1. It does not change the frozen Study-7 or Study-7E protocol, models, population, endpoints, execution, or result interpretation.

## Mechanical preservation checks

The R2 manuscript was checked for the following frozen values and boundaries:

- Study 7 total = 1,033 observations;
- Study 7E held-out population = 196 scenarios / 784 decisions;
- D0 aggregate = 40 errors / 9 unsafe / 31 FCH / 25 ENTER / 171 HOLD;
- L0 aggregate = 47 / 21 / 26 / 42 / 154;
- D1 aggregate = 49 / 4 / 45 / 6 / 190;
- L1 aggregate = 43 / 31 / 12 / 66 / 130;
- D0/L0 disagreement = 67/196;
- D1/L1 disagreement = 72/196;
- C0 all-HOLD zero-error control retained;
- F12 adverse learned transfer retained;
- global policy ranking explicitly prohibited;
- Study 7 and Study 7E remain unpooled.

All checks passed.

## Literature-positioning changes

R2 adds adjacent literature covering:

- secure spacecraft recovery using trusted hardware;
- space-system software-resiliency architecture;
- mission-specific defensible cybersecurity architecture;
- spacecraft flight-software attack-surface analysis;
- malicious spacecraft peripherals in cFS;
- contemporaneous cFS trust-boundary analysis;
- satellite adversarial-ML risk assessment;
- system-level adversarial resilience for spaceborne anomaly detection.

R2 explicitly narrows novelty so that the paper does **not** claim to originate secure spacecraft recovery, resilient spacecraft architecture, cFS security, trust boundaries, or generic satellite ML security.

The retained contribution is the specific combination of downstream recovery authorization, equal-information deterministic/learned pairs, explicit domain aliasing, prospectively frozen fault semantics, model freeze before held-out transfer, and exact safety/availability endpoint accounting.

The targeted search statement is explicitly labeled a negative search observation rather than proof of novelty.

## Bibliography corrections

R2 corrects or strengthens:

- [7] Hai S. Le / AAAI metadata and DOI;
- [8] Haoming Jing / PMLR metadata;
- [10] cFE citation to NASA Software Catalog GSC-18128-1;
- [13] NOS3 citation to NASA Software Catalog GSC-17737-1.

Reference [2] remains bound to repository provenance. The live web tool did not independently resolve its Zenodo DOI in this session; this is recorded as a verification limitation, not evidence of an invalid DOI.

## R2 inventory

- approximate text word count: 6,769;
- references: 21;
- venue: not locked;
- submission: not authorized.

## Decision

`PASS__R2_PRESERVES_FROZEN_SCIENCE_AND_TIGHTENS_LITERATURE_BOUNDARY`

R2 is suitable for venue-selection review. Venue-specific rewriting remains gated on explicit author choice.
