# Phase 8.0 Design Lock Candidate

**Study:** `S8-PQC-ICR-001`  
**Base main commit:** `f582c36cc5747a6703ec651bb957bbfea5852a7e`  
**Authorized:** 2026-09-02  
**Status:** `PHASE8_0_DESIGN_LOCK_CANDIDATE_RUNTIME_NOT_AUTHORIZED`

## Prerequisite gate

Phase 8.0 was not opened until the redundant Phase-7 post-merge CI gate was confirmed. GitHub Actions run `33690506536` completed successfully on main commit `f582c36cc5747a6703ec651bb957bbfea5852a7e` for the Study-7 canonical-results freeze.

Phase 7 is therefore closed before this Phase-8 branch begins.

## Authorized scope

The authorization covers only:

1. current standards/literature verification;
2. protocol design;
3. finite synthetic logical-time/contact model;
4. NIST-standardized cryptographic-object byte budgets;
5. claim-boundary lock;
6. independent adversarial review of the design and candidate finite population.

It does **not** authorize implementation, runtime execution, canonical evidence generation, statistical results, manuscript claims, or merging this design into frozen Study-1/Study-2 science.

## Six-file design-lock scope

The initial Phase-8.0 repository change is intentionally limited to:

```text
study8/STUDY8_PROTOCOL.json
study8/STUDY8_LITERATURE_REGISTER.md
study8/STUDY8_CLAIM_BOUNDARY.md
study8/STUDY8_CONTACT_MODEL.md
study8/STUDY8_CRYPTO_OBJECT_BUDGETS.json
study8/docs/PHASE8_0_DESIGN_LOCK.md
```

No implementation file belongs in this gate.

## Candidate finite population

The proposed full-factorial population is:

```text
3 cryptographic profiles
× 4 recovery policies
× 4 contact regimes
× 4 disruption schedules
× 6 compromise phase offsets
× 3 logical deadlines
= 3,456 observations
```

`3,456` is a **candidate population**, not yet a runtime freeze. It may be frozen only after adversarial review establishes that factor levels are non-aliased enough for the intended questions, treatment semantics are deterministic, deadline behavior is unambiguous, and no cell requires an empirical spacecraft/RF interpretation.

## Required independent adversarial review

Before any implementation file may be created, the review must challenge at least:

- novelty over existing space-PQC and space crypto-agility literature;
- factor aliasing or analytically duplicate cells;
- unfair treatment-specific byte burdens;
- hidden physical-time assumptions;
- ambiguity in deadline inclusivity;
- ambiguity in contact segmentation/retransmission;
- epoch/replay safety invariants;
- whether P3 uses only information legitimately visible to the modeled controller;
- whether the primary endpoint can be reconstructed independently;
- whether any wording could be mistaken for spacecraft/RF/PQC runtime measurement.

Any material finding requires a design-only repair followed by another review. No finding may be repaired by proceeding to runtime.

## Closed gates

```text
runtime_authorized=false
canonical_execution_authorized=false
implementation_creation_authorized=false
results_directory_authorized=false
campaign_authorization_present=false
independent_adversarial_design_review=PENDING
```

The following paths must not be created under this authorization:

```text
study8/src/
study8/analysis/
study8/results/
study8/runtime/
study8/CAMPAIGN_AUTHORIZATION.json
```

## Phase-8 publication boundary

Phase 8 remains a separate companion-publication line. Studies 1–7 stay frozen and unpooled. The Computers & Security Study-1/Study-2 manuscript record must not be changed by Phase-8 results.

## Advancement criterion

Phase 8.0 may advance from `DESIGN_LOCK_CANDIDATE` to `DESIGN_LOCKED` only after the independent adversarial review is recorded and every material issue is either repaired or explicitly blocks advancement.

Runtime remains closed even after a successful Phase-8.0 design review; implementation requires a later, separate authorization/gate.
