# Threat and Mission Model — Red-Team Review

## Review purpose

This review attempts to invalidate the current threat model, expose assumptions that could predetermine the results, and define controls required before implementation. It is not an authorization to test operational systems.

## Red-team conclusion

The frozen pilot is scientifically viable, but the initial threat model was too favorable to the defender. It assumed the response policy received trustworthy mission state, timing, and recovery evidence while the adversary affected only commands, updates, or selected telemetry. That assumption could make the mission-aware policy appear effective by construction.

The model must therefore distinguish:

1. Immutable experiment ground truth
2. Spacecraft-observed state
3. Ground-observed state
4. Policy-engine input state
5. Evidence used to declare recovery

These representations may disagree during a trial.

## Critical attack surfaces omitted from the first draft

### RT-1 Policy-input manipulation

An adversary may not need to defeat the response engine directly. Manipulating mission-state labels, telemetry freshness, clock values, authorization state, or contact forecasts may cause the engine to choose the wrong otherwise-valid action.

**Required control:** Log the ground-truth value and every policy-visible value separately. P7 must never read the immutable ground-truth channel.

### RT-2 Safe-mode abuse

Safe mode can preserve spacecraft survival, but it can also suspend mission activity, reduce observability, change command handling, or activate contingency paths. Repeatedly inducing safe mode may become a denial-of-service strategy.

**Required control:** Track initiator, reason, state-entry evidence, commands permitted in safe mode, evidence retained, and safe-mode dwell time. A safe-mode transition is not automatically a successful response.

### RT-3 Recovery-image or recovery-authority compromise

Rollback is unsafe when the approved image, manifest, signing authority, or version inventory is stale or compromised.

**Required control:** The pilot may model image modification and authorization mismatch, but the immutable experiment root remains outside the adversary boundary. Recovery must fail closed when no approved evidence chain is available.

### RT-4 Stale but internally consistent evidence

A complete evidence bundle may still describe an old state. Internal consistency alone cannot establish current trust.

**Required control:** Every recovery-evidence element requires a timestamp or sequence identifier and a configured freshness threshold.

### RT-5 Ground/spacecraft split-brain

The ground segment may consider an identity revoked or an image approved while the spacecraft retains an earlier state because of missed contact or interrupted update.

**Required control:** Measure divergence duration and prevent normal command operations until convergence or a predeclared emergency-authority path is invoked.

### RT-6 Time and replay assumptions

Replay detection depends on time, counters, sequence windows, or stored state. Clock skew, reset, or counter rollback can change whether an old command is accepted.

**Required control:** The event model must record the freshness mechanism used and must not assume a perfect shared clock.

### RT-7 Contact-schedule oracle

Providing P7 with exact future contact availability gives it information that a real spacecraft may not possess.

**Required control:** Separate scheduled contact, predicted contact, and actual contact. The pilot should expose only the configured policy-visible contact estimate.

### RT-8 Response-induced loss of evidence

Isolation, restart, rollback, and safe mode may destroy volatile evidence or stop relevant telemetry.

**Required control:** Measure evidence retained after each policy. Evidence preservation is a mission objective, not an automatic side effect.

### RT-9 Recovery loops and oscillation

An adaptive policy may repeatedly move between containment, safe mode, and rollback without reaching a stable terminal state.

**Required control:** Record policy transitions and enforce a maximum transition count or trial duration. Exceeding the bound results in `RECOVERY_FAILED`, not silent continuation.

### RT-10 Overpowered mission-aware policy

P7 may effectively encode the correct answer for each scenario if rules are hand-written after observing outcomes.

**Required control:** Freeze P7 decision logic before the final campaign. Develop and tune it only on pilot conditions or a separated development set. Report rule complexity and all condition-specific exceptions.

## Threat-agent scope

### Included adversary capabilities

- Use a synthetic valid-but-unauthorized identity
- Replay a captured laboratory command
- Submit a valid command outside authorized mission state
- Modify or downgrade a synthetic update artifact
- Interrupt an update or recovery transfer
- Suppress, delay, or stale selected synthetic telemetry/evidence
- Cause one modeled missed contact window
- Induce disagreement between ground and spacecraft authorization/version state
- Attempt repeated safe-mode entry through modeled events

### Excluded adversary capabilities

- Host or hypervisor compromise
- Modification of immutable orchestration logs
- Cryptographic primitive break
- Operational credential access
- Live RF transmission or interference
- Operational satellite or ground-station access
- Classified or proprietary data access
- Physical destruction or orbital-manipulation claims

## Required trust zones

| Zone | Contents | Adversary access |
|---|---|---|
| Z0 Immutable experiment control | Orchestrator, random seed, ground truth, raw append-only log | None |
| Z1 Trusted recovery root | Approved baseline hashes, root authorization, pristine snapshot reference | No modification in pilot |
| Z2 Ground operations | Synthetic operator identity, command gateway, ground authorization state | Event-dependent |
| Z3 Emulated link/contact | Delay, loss, ordering, contact availability | Controlled manipulation |
| Z4 Flight software and mission state | Command ingest, state machine, update/recovery logic | Event-dependent |
| Z5 Telemetry and policy evidence | Telemetry, integrity evidence, state estimates, policy inputs | Suppression/staleness in T1 |
| Z6 Response-policy engine | P0–P7 implementations | No direct code modification; inputs may be degraded |

## Model validity threats

### Construct validity

- Safe mode may be implemented as a label rather than a sustainable state.
- Mission completion may overvalue easily measurable tasks.
- Trusted recovery may become a checklist disconnected from actual residual state.

**Mitigation:** Implement measurable state transitions, resource constraints, residual-state checks, and current evidence requirements.

### Internal validity

- Different policies may receive different information.
- Cleanup between runs may be incomplete.
- P7 may be tuned against the final scenarios.

**Mitigation:** Use identical policy-visible inputs where applicable, clean snapshots, recorded seeds, frozen policy logic, and randomized run order.

### External validity

- NOS3/cFS represents only a bounded small-satellite software environment.
- Software-emulated links do not reproduce RF physics.
- Results will not generalize automatically to military, GEO, crewed, or proprietary missions.

**Mitigation:** State the architecture and exclusions precisely; claim method and conditional findings rather than universal operational effectiveness.

### Conclusion validity

- Rare terminal failures may require more runs than average metrics suggest.
- Composite scoring can conceal unacceptable losses.

**Mitigation:** Use pilot-based sample planning, report terminal-state distributions and invariant violations, and keep Pareto analysis separate from primary outcomes.

## Mandatory changes before WP4 implementation

- Policy-visible state must be separated from immutable ground truth.
- Contact information must distinguish scheduled, predicted, and actual contact.
- Evidence objects must include freshness metadata.
- Safe-mode entry, dwell, permitted commands, and evidence loss must be measured.
- P7 decision logic must be versioned and frozen before the final campaign.
- Recovery loops must have an explicit terminal rule.
- Run cleanup and snapshot restoration must be automatically verified.

## Red-team disposition

**Conditional pass.** The model may advance toward architecture selection after the mandatory changes are represented in configuration and testbed requirements. The review does not approve operational testing, RF activity, or use of non-public data.
