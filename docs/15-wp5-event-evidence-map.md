# WP5 Event Evidence Map

## Evidence-first rule

Every retained event must answer five questions before simulator integration:

1. **Why is this event scientifically relevant?**
2. **What external/threat-model evidence supports the event family?**
3. **What immutable ground truth defines what actually happened?**
4. **What subset of evidence is visible to the response policy?**
5. **What observable outcome can falsify or support a paper hypothesis?**

## Selected event families

| ID | Synthetic event | External mapping | Primary research role |
|---|---|---|---|
| E1 | Unauthorized valid command | SPARTA IA-0007.02 | Tests mission-state-dependent command containment |
| E2 | Replayed command | SPARTA EX-0001.01 | Tests stale authorization / replay handling |
| E3 | Compromised update | SPARTA IA-0007.01; EX-0004 | Tests rollback and verified trusted recovery |
| E4 | Telemetry observability degradation | SPARTA DE-0003.06 | Tests response/recovery under incomplete evidence |

Ground-contact delay (`C0`/`C1`) is an experimental condition, not a fifth attack.

## Source rationale

- NASA describes NOS3 as an open-source software-only small-satellite testbed, supporting its use as experiment infrastructure rather than the contribution.
- NIST SP 800-160 Vol. 2 Rev. 1 frames cyber resilience around anticipating, withstanding, recovering from, and adapting to cyber adversity while reducing mission risk.
- SPARTA explicitly documents malicious commanding through a valid ground system, command-packet replay, compromise of on-orbit updates, and telemetry-downlink mode manipulation.

## Ground-truth / policy-evidence separation

`configs/wp5_event_catalog.json` defines both:

- immutable event ground truth; and
- policy-visible evidence.

`src/mission_recovery/events.py` materializes deterministic event instances. Under reduced-evidence condition `T1`, policy-visible fields are omitted while immutable ground truth is unchanged.

That separation prevents an experimental oracle from leaking directly into the policy.

## Hypothesis traceability

- **H1:** response effects differ by mission state → E1-E4 across M0/M2/M4
- **H2:** restrictive containment trades unauthorized-effect reduction for mission interruption → E1-E3 across baseline policies
- **H3:** contact delay worsens ground-dependent containment/recovery → E1/E2 under C0/C1
- **H4:** evidence-based rollback improves verified recovery over restart-only recovery → E3
- **H5:** mission-aware selection improves the security/mission Pareto frontier without dominating every condition → E1-E4
- **H6:** reduced/manipulated telemetry increases ineffective or unsafe response selection → E4 and T1

## Current WP5 boundary

This first WP5 increment implements event semantics and deterministic evidence generation only.

It does **not** yet transmit commands or manipulate NOS3. The next increment will add bounded simulator adapters one event at a time, reusing these frozen semantic definitions.
