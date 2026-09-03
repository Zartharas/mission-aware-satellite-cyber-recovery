# Phase 8.1 Implementation and Independent-Auditor Construction Freeze

**Experiment:** `S8-PQC-ICR-001`  
**Parent design lock:** `b5172e1d4ba79b60b8fccbd119f087a33c6fd037`  
**Authorization date:** 2026-09-02  
**Status:** `PHASE8_1_IMPLEMENTATION_CONSTRUCTED_RUNTIME_NOT_AUTHORIZED`

**Pre-runtime design amendment:** `S8-DESIGN-AMEND-001`

## Authorized scope

Phase 8.1 authorizes construction only:

- one primary deterministic implementation of the frozen Phase-8.0 logical contact/recovery model;
- one independently written reference auditor that does not import the primary implementation;
- development-fixture definitions and unit-test code;
- a static implementation-freeze checker;
- provenance documentation.

This authorization does not permit canonical population execution, campaign authorization, results generation, statistical analysis, scientific interpretation, or opening the later pre-runtime PR.

## New implementation paths

```text
study8/PHASE8_1_IMPLEMENTATION_AUTHORIZATION.json
study8/PHASE8_0_AMENDMENT_1.json
study8/src/contact_recovery_model.py
study8/audit/independent_reference.py
study8/tests/test_phase8_models.py
study8/scripts/check_phase8_1_implementation_freeze.py
study8/docs/PHASE8_1_IMPLEMENTATION_FREEZE.md
study8/docs/PHASE8_0_AMENDMENT_1.md
```

The original Phase-8.0 six-file design lock remains in history unchanged; `S8-DESIGN-AMEND-001` is an explicit pre-runtime overlay prompted by implementation review.

## Primary implementation

`study8/src/contact_recovery_model.py` implements:

- the frozen 3 × 4 × 4 × 4 × 6 × 3 factor lattice;
- exact profile object-byte budgets;
- the four 48-slot contact regimes and six deterministic phase offsets;
- the common object priority and partial-byte persistence;
- A1 lost-fragment, A2 proof-delay, and A3 stale-epoch-replay abstractions;
- P0/P1/P2/P3 policy semantics relevant to modeled exposure and control availability;
- the P3 nominal future-contact guard with no access to future disruption outcomes;
- strict `completion_slot < deadline`;
- deterministic terminal-state classification.

The module has no campaign CLI. Direct execution exits with a closed-gate message.

## Independent auditor

`study8/audit/independent_reference.py` is separately written and does not import the primary model. It independently reconstructs a case from factor values and can later compare a supplied observation with its own recomputation.

The auditor also refuses direct artifact-audit execution at Phase 8.1.

This is implementation independence inside the repository. It is not described as an external human review, separate laboratory replication, or operational validation.

## Pre-runtime operationalization conventions

The frozen design named several secondary endpoints without fully specifying discrete-slot counting. Phase 8.1 fixes those conventions before any campaign execution:

- `legacy_exposure_slots`: count slots from recovery start until predecessor revocation; P0 is zero, while P1/P2/P3 count `[0, commit_slot)` and are censored at the deadline if no commit occurs.
- `control_unavailable_slots`: P0 counts `[0, commit_slot)` because predecessor acceptance ends at recovery start and successor acceptance begins at commit; P1/P2/P3 are zero under their frozen acceptance semantics.
- `dual_epoch_overlap_slots`: added by `S8-DESIGN-AMEND-001` to remove the P1/P2 observational alias; for P2 it is the logical slot-index separation from proof acceptance to commit (or deadline censoring), and is zero for other policies.
- `cryptographic_bytes_transferred`: counts every modeled cryptographic byte allocation, including an A1 fragment that is lost and later retransmitted.
- `contacts_consumed`: counts a contact when bytes are allocated or when A1/A2/A3/P3 consumes or blocks an otherwise actionable protocol opportunity.
- `transition_attempts`: counts commit presentations; the A3 stale replay counts as one attempt and the later legitimate commit, if reached, counts as another.
- A2 implementation convention: when the transition-proof object first becomes ready during an eligible contact, that contact is the one withheld opportunity; proof bytes cannot use the remaining capacity in that contact.

These conventions add no physical-time interpretation and do not alter the frozen factor lattice.

## Structural-zero safety fields

Under the frozen four disruption schedules, no valid factor cell intentionally causes:

- forged-signature acceptance;
- stale-epoch acceptance;
- transition-proof cryptographic rejection;
- rollback invocation.

Accordingly, `stale_epoch_acceptance` and `rollback_invoked` are expected structural-zero safety outputs unless an implementation defect is detected. They must not be presented later as treatment-effect evidence merely because the observed value is zero.

`TRANSITION_PROOF_REJECTED` and `ROLLBACK_BLOCKED` remain reserved safety terminal states in the design vocabulary but are not expected to be populated by the current frozen factor lattice.

## Development fixtures

Four non-canonical development fixtures are defined in test code solely for later CI parity checks between the primary and independent implementations.

They are not campaign observations and must never be included in the 3,456-row scientific population.

Phase 8.1 construction does not execute those fixtures.

## Closed gates

```text
development_fixture_execution_authorized=false
pre_runtime_pr_authorized=false
canonical_execution_authorized=false
campaign_authorization_present=false
results_generation_authorized=false
scientific_interpretation_authorized=false
```

The following remain prohibited:

```text
study8/results/
study8/runtime/
study8/CAMPAIGN_AUTHORIZATION.json
```

## Advancement criterion

The next gate is a separate pre-runtime review/PR authorization. That gate may run static checks and non-canonical development tests in CI, review implementation/auditor independence, and bind hashes before any campaign authorization exists.

No full-population execution is permitted until a later explicit campaign authorization is committed and independently validated.
