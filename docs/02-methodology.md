# Proposed Methodology

## Study type

Theory-informed design-science research with controlled software-in-the-loop experimentation.

## Units of analysis

A trial is one fully specified combination of:
- Initial mission state
- Cyber event
- Evidence condition
- Contact condition
- Response policy
- Recovery procedure
- Random seed

## Experimental phases

### Phase A — Nominal baseline

Verify:
- Mission-state transitions
- Command processing
- Telemetry generation
- Contact-window behavior
- Resource accounting
- Normal safe-mode and rollback behavior

### Phase B — Event validation

Validate each synthetic cyber event independently and confirm that:
- It produces a deterministic intended effect
- It cannot leave the isolated lab
- It is distinguishable from ordinary faults where required
- All event parameters are logged

### Phase C — Policy comparison

Compare response policies under randomized scenario order and clean snapshots.

### Phase D — Trusted recovery

Require explicit integrity, version, authorization, attestation, telemetry, and health evidence before a trial is marked recovered.

### Phase E — Robustness

Repeat selected trials under:
- Missing telemetry
- Delayed telemetry
- Packet loss
- Clock skew
- Ground/spacecraft state disagreement
- Incorrect response confidence

## Primary endpoints

1. Mission objective completion ratio
2. Residual unauthorized effect
3. Safety-invariant violation
4. Time to verified trusted recovery
5. Recovery success
6. Legitimate command rejection

## Secondary endpoints

- Time to detect
- Time to contain
- Time in safe/degraded mode
- Contact windows consumed
- CPU, memory, and simulated power overhead
- Evidence completeness
- Incident timeline reconstruction accuracy

## Statistical plan — initial

- Use pilot runs to estimate variability and failure rates.
- Pre-register primary outcomes and exclusion criteria.
- Use mixed-effects or generalized mixed-effects models where repeated scenario families create dependence.
- Use survival analysis or time-to-event methods for trusted recovery.
- Report effect sizes and confidence intervals.
- Use bootstrap sensitivity analysis where distributional assumptions are weak.
- Use Pareto-front analysis for security-versus-mission trade-offs.
- Treat any weighted composite score as secondary and sensitivity-tested.

## Reproducibility controls

- Pinned commits and dependency versions
- Clean VM/container snapshots
- Recorded random seeds
- Machine-readable experiment specifications
- Immutable raw run logs
- Checksums for all artifacts
- Separate code and data provenance
- Documented failed and excluded runs
