# Paper 2 Phase-1 Adversarial Protocol Review R1

**Status:** `DESIGN_REVIEW_COMPLETE__NO_EXECUTION_AUTHORIZED`

This review challenges the proposed extensions as if they were being evaluated by a skeptical reviewer. It does not execute a new experiment.

## S3X-ETA-001

**Decision:** `CONDITIONAL_GO_FOR_SOURCE_SCREENING_ONLY`

### Strength

It directly addresses the weakest external-validity feature of Study 3: dependence on one hand-designed intermittent schedule.

### Main threat

Telemetry observation gaps are not automatically spacecraft contact loss. Gaps may arise from sampling policy, preprocessing, downlink handling, recording choices, or anomaly-dataset construction.

### Required controls before execution

- inspect authoritative dataset documentation and raw timestamp structure;
- distinguish regular sampling cadence from actual missing/absent intervals;
- freeze a deterministic gap-extraction rule before recovery evaluation;
- use timing/availability only, never anomaly labels as cyberattack truth;
- call resulting traces `empirical telemetry-availability traces`, not orbital-contact schedules unless an authoritative source proves that interpretation;
- exclude any trace source already used as Study-8E experimental evidence.

**Assessment:** potentially high value if the source supports genuine temporal availability structure. Otherwise stop rather than force the dataset.

## S4X-JCU-001

**Decision:** `HOLD__NOT_CURRENTLY_JUSTIFIED`

### Strength

It would close the explicit Study-4 limitation that compromise and unavailability were evaluated separately.

### Main threat

The new state count would look impressive while adding little explanatory power. Under the frozen absolute-threshold semantics, several joint-state effects may be derivable analytically.

### Required precondition for revival

Identify at least one scientifically material question that cannot be answered by the new closed-form threshold characterization. If no such question survives, do not execute S4X.

**Assessment:** theory first; extension likely unnecessary for the next paper unless a concrete nontrivial interaction is demonstrated prospectively.

## S6X-EAP-001

**Decision:** `CONDITIONAL_GO_FOR_ENVIRONMENT_AND_INVARIANT_DESIGN_ONLY`

### Strength

It directly addresses the strongest construct-validity weakness of Study 6: objective correctness is currently a Boolean research adjudication rather than an executable property of an aerospace software artifact.

### Main threats

- merely using cFS does not make a generic software-supply-chain test aerospace-specific;
- a trivial intentionally wrong program could make the result tautological;
- using the functional correctness test as gate input would destroy the intended observability contrast;
- a single local build process may overstate independence.

### Required controls before execution

- pin a public cFS revision and identify a concrete non-operational application behavior tied to a documented interface/invariant;
- define functional correctness before constructing artifact variants;
- keep correctness adjudication strictly outside gate-visible evidence;
- define research-only signing keys and non-production provenance;
- use at least two separately instantiated build environments/processes for the independent-rebuild signal if feasible;
- ensure the approved-bad-source fixture is benign and demonstrates a semantic failure, not malware/exploit behavior;
- prospectively bind artifact states, gates, tests, and expected evidence fields before observing results.

**Assessment:** high potential value, but only if the executable correctness test is meaningful and independent of the assurance gate.

## Portfolio decision

Priority order for further Paper-2 strengthening:

1. complete S3X source-structure screening;
2. complete S6X cFS environment/invariant design;
3. keep S4X on hold;
4. do not begin manuscript R11/R12 until the two high-priority extension designs have either passed or failed their go/no-go gates;
5. do not select a new venue until the evidence boundary of the rebuilt paper is known.

No new scientific execution is authorized by this review.
