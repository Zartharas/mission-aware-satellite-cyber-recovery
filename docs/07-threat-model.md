# Threat Model — Draft

## Protected assets

- Command authority
- Flight-software integrity
- Mission-state integrity
- Telemetry integrity and availability
- Recovery images and configuration
- Ground/spacecraft state synchronization
- Safety-critical control functions
- Evidence used to declare recovery

## Trust boundaries

1. Operator to ground application
2. Ground application to command gateway
3. Gateway to simulated link
4. Link to flight command ingest
5. Flight software to subsystem simulators
6. Telemetry generation to ground display/analytics
7. Update pipeline to onboard verification
8. Recovery controller to trusted image/configuration

## Adversary capabilities — initial

The adversary may:
- Possess a valid but unauthorized test identity
- Replay a previously captured lab command
- Submit a syntactically valid command in an invalid state
- Modify a synthetic update artifact
- Suppress or alter selected telemetry in the simulator
- Cause contact or data delay in the emulated link

The adversary may not:
- Access real systems
- Transmit RF
- Obtain classified/proprietary information
- Break standardized cryptography
- Control the host or experiment orchestrator
- Modify immutable ground-truth logs

## Safety invariants — examples

- Critical control commands require authorized state and identity.
- Low-power state must preserve a minimum energy reserve.
- Recovery must not activate an unverified image.
- Ground and spacecraft command-authority state must converge before normal operations resume.
- A response may not disable all recovery paths.
- Trusted recovery requires current evidence, not stale telemetry.

## Out of scope

- Nation-state attribution
- Physical destruction modeling
- Real orbital collision risk
- Live RF interference
- Classified mission behavior
- Human operator cognition
