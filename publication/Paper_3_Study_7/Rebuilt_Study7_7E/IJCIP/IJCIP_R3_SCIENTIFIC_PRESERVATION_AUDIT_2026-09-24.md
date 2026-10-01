# Paper 3 — IJCIP R3 Scientific-Preservation Audit

**Audit ID:** `PAPER3-S7-S7E-IJCIP-R3-PRESERVATION-AUDIT-001`  
**Date:** 2026-09-24  
**Manuscript:** `PAPER3_IJCIP_MANUSCRIPT_R3.md`  
**Basis head:** `c36d7e0f4fc09f51439c09c890de14a9129e96bb`  
**Result:** **PASS**

## 1. Purpose

This audit verifies that IJCIP-specific framing and compliance edits did not alter the frozen scientific record of Study 7 or Study 7E.

## 2. Frozen quantitative checks

Verified present and unchanged in R3:

- Study 7 population: 1,033 observations;
- Study 7E held-out scenarios: 196;
- Study 7E policy decisions: 784;
- D0 aggregate: 40 errors / 9 unsafe / 31 FCH / 25 ENTER / 171 HOLD;
- L0 aggregate: 47 / 21 / 26 / 42 / 154;
- D1 aggregate: 49 / 4 / 45 / 6 / 190;
- L1 aggregate: 43 / 31 / 12 / 66 / 130;
- D0/L0 paired disagreement: 67/196;
- D1/L1 paired disagreement: 72/196;
- F12 adverse learned-transfer finding retained;
- C0 all-HOLD zero-error null/control finding retained.

## 3. Scientific-boundary checks

Verified:

- no Study-7/Study-7E pooled sample or pooled error metric;
- no global policy ranking;
- no global ML-superiority claim;
- no monotonic trust-separation claim;
- no operational spacecraft or critical-infrastructure probability claim;
- no claim of measured cross-sector cascading failure;
- no CISA "Space Systems Sector" assertion;
- cFS remains architecture grounding rather than flight qualification.

## 4. IJCIP adaptation checks

Verified:

- title and abstract establish the space-enabled critical-infrastructure context;
- six keywords exactly;
- bounded critical-infrastructure subsection added;
- Study-7 learner simplicity explicitly framed as an experimental control;
- OPS-SAT/operational-telemetry rationale added;
- research-process AI provenance disclosed in Methods;
- Elsevier-style manuscript-preparation AI declaration placed before References;
- Funding, CRediT, competing-interest, ethics, data-availability, and code-availability sections added;
- 24 references total, including U.S. Space Priorities Framework, CISA Communications, and SPD-5 context.

## 5. Literal-string guard note

A simple prohibited-phrase search flagged the words `quantify cross-sector cascading failures`.

This is a **false positive**. In the manuscript the phrase occurs only inside an explicit negative boundary stating that the controlled experiments do not quantify such failures. The surrounding scientific meaning is correct and should not be weakened merely to satisfy a literal string detector.

## 6. Decision

`PASS__IJCIP_R3_PRESERVES_FROZEN_SCIENCE`

The next gate is repository CI followed by final live verification of any journal-specific Guide/portal items that could not be accessed during this audit.

This audit does not authorize PR #168 merge or publisher submission.
