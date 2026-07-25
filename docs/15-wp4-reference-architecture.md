# WP4 Reference Architecture — Gate 3 Draft

## Purpose

This architecture maps the frozen scientific requirements and red-team findings to a software-only NOS3/cFS testbed. The architecture is designed to prevent the response policy from seeing experiment ground truth and to ensure that trusted recovery is evaluated independently.

## Architecture principles

1. Separate immutable ground truth from policy-visible evidence.
2. Keep the complete experiment inside internal Docker networks.
3. Use exact upstream commits and image digests.
4. Treat safe mode as both a defensive response and an adversarially inducible condition.
5. Make recovery verification external to the response policy.
6. Start headless; graphical tools are optional observability aids.
7. Reset from a clean baseline between scored runs.
8. Record every run configuration and terminal state in the frozen schema.

## Zones

### Z0 — Host and repository zone

Contains:

- macOS host
- Research Git repository
- Git and GitHub CLI
- Ignored `external/`, `data/`, and raw `results/` storage
- Docker Desktop and engine

Controls:

- No real mission credentials or data
- NOS3 source resides under ignored `external/nos3`
- Raw runs are append-only after completion
- Host firewall remains enabled
- No antenna, SDR, or intentional radiator

### Z1 — Experiment-control zone

Contains:

- Scenario orchestrator
- Randomization and seed controller
- Immutable ground-truth event log
- Trial timeout and emergency-stop controller
- Snapshot/reset controller

Security boundary:

- Not reachable from simulated adversary components
- Does not expose immutable truth to P7
- Does not mount the Docker socket inside experiment services
- May control containers only through host-side scripts

### Z2 — Policy-visible observation zone

Contains:

- Telemetry collector
- Ground-observed authorization state
- Evidence freshness evaluator
- Detection/event abstraction
- Policy input adapter

Purpose:

- Builds the incomplete or manipulated evidence set available to a response policy
- Implements T0 and T1 without changing immutable ground truth
- Records what the policy actually saw at decision time

### Z3 — Ground and command zone

Contains:

- Synthetic operator identity store
- Ground command client
- Authorization gateway
- Command queue
- Ground-side approved-version and recovery-state record

Purpose:

- Provides only synthetic commands, identities, and authorization state
- Implements command rejection and ground-spacecraft divergence metrics

### Z4 — Link and contact zone

Contains:

- Contact-window controller
- Delay, drop, reorder, duplication, and staleness emulator
- Uplink and downlink queues

Purpose:

- Implements C0 and C1
- Implements E6 and non-adversarial communication impairment
- Exposes only modeled software interfaces; no RF path exists

### Z5 — Spacecraft simulation zone

Contains:

- NOS3 simulator services
- cFS flight software pinned by NOS3
- Mission-state controller
- Synthetic subsystem simulators
- Command ingest and telemetry generation
- Safe-mode and recovery state machine

Purpose:

- Executes nominal and adversarial scenarios
- Emits policy-visible telemetry separately from immutable truth
- Maintains local spacecraft authorization and approved-version state

### Z6 — Response and recovery zone

Contains:

- P0/P1/P2/P4/P5/P7 policy implementations
- Identity/source isolation adapter
- Selective command restriction adapter
- Safe-mode adapter
- Rollback controller
- Read-only approved image and configuration store

Controls:

- Policies may consume only Z2 inputs
- Rollback artifacts are mounted read-only
- Policy actions are logged before execution
- Every action has a bounded timeout and declared failure state

### Z7 — Independent recovery-verification zone

Contains:

- Version and configuration verifier
- Integrity measurement verifier
- Authorization-state convergence checker
- Evidence freshness checker
- Health-check evaluator
- Residual unauthorized-state checker
- Terminal-state classifier

Purpose:

- Determines whether `TRUSTED_RECOVERY_CONFIRMED` is allowed
- Does not rely on the response policy's self-reported success
- Reads immutable truth and separately collected recovery evidence

## Docker network model

### `ma-sim`

- Docker `internal` network
- Connects Z2 through Z7 experiment services
- No default outbound internet route
- No `--network host`

### `ma-control`

- Docker `internal` network
- Restricted to orchestration endpoints that require container-level access
- The experiment orchestrator remains host-side where practical

### Optional local UI exposure

Browser-based ground tools may bind only to `127.0.0.1`. UI access is not required for automated scored trials.

## Storage model

| Storage | Access | Purpose |
|---|---|---|
| Approved recovery store | Read-only to Z6/Z7 | Approved image/configuration and hashes |
| Run configuration | Read-only after start | Frozen scenario inputs |
| Immutable truth log | Append-only from Z1 | Actual event and state timeline |
| Policy-visible log | Append-only | Evidence shown to each policy |
| Action log | Append-only | Response actions and outcomes |
| Raw result directory | New directory per run | Run artifacts and manifest |

## Red-team requirement mapping

| Red-team concern | Architecture requirement |
|---|---|
| Policy sees ground truth | Z1 and Z2 are separate; P7 reads Z2 only |
| Telemetry manipulation changes truth | T1 changes Z2 evidence, not Z1 truth |
| Safe-mode abuse | Safe mode is modeled as response P4 and as an inducible state transition |
| Stale but consistent evidence | Z7 verifies timestamps and freshness independently |
| Ground/spacecraft split-brain | Z3 and Z5 maintain separate authorization/version states |
| Clock or replay ambiguity | Z1 assigns monotonic trial time and immutable sequence identifiers |
| Overly accurate contact forecast | Z4 provides the declared forecast/error model to policies |
| Response destroys evidence | Action logs are written outside policy-controlled storage |
| Recovery loop | Z1 enforces transition counts and terminal timeouts |
| P7 overfitting | Policies use the same action adapters and frozen catalog; scenario order and seeds are external |

## Initial implementation stages

### Stage 0 — Runtime validation

- Verify Docker daemon and Compose
- Run `linux/amd64` container
- Create and inspect internal network
- Validate experiment schemas

### Stage 1 — Upstream pinning

- Clone NOS3 at the selected commit
- Initialize recursive submodules
- Record all submodule SHAs
- Pull and record container digest
- Preserve licenses

### Stage 2 — Nominal headless baseline

- Build or launch minimal NOS3/cFS environment
- Confirm cFS reaches operational state
- Send an authorized no-op or benign command
- Receive expected telemetry
- Record a valid nominal run manifest

### Stage 3 — State and contact controls

- Implement M0, M2, and M4 state adapters
- Implement C0 and C1
- Verify that immutable and policy-visible timelines remain separable

### Stage 4 — Response and recovery primitives

- Implement P0, P1, P2, P4, and P5 before P7
- Implement independent Z7 recovery verification
- Verify terminal-state logic

### Stage 5 — Mission-aware policy

- Implement P7 only after baseline actions and metrics are stable
- Prohibit direct access to immutable truth
- Record all policy inputs and selected actions

## Gate 3 acceptance criteria

WP4 architecture is accepted when:

1. The runtime verification script passes.
2. NOS3 and recursive submodules are locked.
3. Container image digest is recorded.
4. The schema positive test passes and negative test fails as expected.
5. Internal networks are verified.
6. A nominal command/telemetry run is reproducible twice from a clean reset.
7. The architecture can record separate ground truth and policy-visible evidence.
8. The ROE addendum contains tested shutdown commands.

## Explicit limitations

- The testbed is not a flight-qualified spacecraft system.
- Software-emulated contact and resource states approximate operational constraints.
- Results will support claims about the experimental architecture and tested policy classes, not all satellites.
- No conclusion about real-world attack prevalence will be drawn from synthetic scenarios.
