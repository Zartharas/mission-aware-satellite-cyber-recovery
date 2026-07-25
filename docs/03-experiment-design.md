# Initial Experiment Design

## System model

The initial testbed should contain:

- Ground command client
- Identity and authorization layer
- Contact-window scheduler
- Link impairment emulator
- cFS/NOS3 flight-software environment
- Mission-state controller
- Telemetry collector
- Event correlator
- Response-policy engine
- Rollback and recovery validator

## Mission states

| ID | State | Critical condition |
|---|---|---|
| M0 | Nominal | Routine command and telemetry |
| M1 | Payload active | Mission data collection must continue where safe |
| M2 | Low power/eclipse | Power-preservation constraints dominate |
| M3 | Critical control activity | Command blocking may create safety risk |
| M4 | Software update | Integrity and rollback are critical |
| M5 | Safe mode | Restricted function intended to preserve the system |
| M6 | Recovery | Trust and configuration are being re-established |

## Event families

| ID | Event | SPARTA relationship | Safety boundary |
|---|---|---|---|
| E1 | Unauthorized valid command | Valid-command abuse | Synthetic identity and command |
| E2 | Replay of authorized command | Replay/command abuse | Recorded lab command only |
| E3 | Abnormal command sequence | Valid-command misuse | Restricted command catalogue |
| E4 | Modified update | Software/firmware corruption | Synthetic package |
| E5 | Unauthorized downgrade | Software lifecycle abuse | Synthetic version |
| E6 | Telemetry suppression | Disrupt/deceive downlink | Software-only data path |
| E7 | Telemetry falsification | Sensor/telemetry manipulation | Synthetic channels |
| E8 | Contact loss during response | Operational impairment | Simulated scheduler |

## Response policies

| ID | Policy |
|---|---|
| P0 | Observe only |
| P1 | Revoke identity or source |
| P2 | Restrict selected command classes |
| P3 | Suspend command processing |
| P4 | Enter safe mode |
| P5 | Roll back software/configuration |
| P6 | Wait for ground authorization |
| P7 | Mission-aware policy |

## Trusted recovery checklist

A trial is recovered only when all applicable conditions pass:

- Approved software/configuration version
- Valid integrity hash
- Valid package or provenance signature
- Current attestation or equivalent measurement
- Restored authorized command path
- Ground/spacecraft state agreement
- Required telemetry restored
- Health checks passed
- No residual unauthorized process/configuration
- Recovery evidence stored in the run manifest

## Initial pilot matrix

Use a reduced pilot:

- Events: E1, E4, E6
- Mission states: M0, M2, M4
- Policies: P0, P1/P2, P4, P5, P7
- Contact: immediate, one missed pass
- Telemetry: full, reduced

This creates a manageable pilot before expanding the design.

## Stopping conditions

Stop a trial if:
- The simulator enters an undefined state
- A safety invariant is violated beyond the modeled recovery boundary
- Evidence collection fails
- The event escapes the isolated namespace
- The run cannot be reproduced from the same snapshot and seed
