# WP5 E4 — Telemetry Observability Degradation

## Final canonical design

E4 uses **matched fresh-runtime trials** rather than repeatedly generating Data Types telemetry inside one TO_LAB process.

The two trials have identical mission state, contact condition, evidence condition, seed, pinned software, container image, command packet, and isolated network topology. They differ only in the research proxy condition:

- **control:** forward MID `0x08E9`;
- **degraded:** capture MID `0x08E9` in immutable truth but do not forward it to policy-visible evidence.

Each fresh runtime receives exactly one `SEND_DATA_TYPES` command. This avoids treating repeated-command behavior inside one TO_LAB process as part of E4.

## Evidence sequence

### Control trial

1. Launch a fresh accepted nominal NOS3 runtime.
2. Start the bound UDP truth proxy in `control`.
3. Enable TO_LAB output to the proxy.
4. Send exactly one `SEND_DATA_TYPES`.
5. Require immutable truth `0x08E9 +1`.
6. Require policy-visible `0x08E9 +1`.
7. Require truth `forwarded_to_policy=true`.
8. Require the nominal runtime to finish PASS.

### Degraded trial

1. Launch a second fresh accepted nominal NOS3 runtime with the same experimental inputs.
2. Start the same proxy in `degraded`.
3. Enable TO_LAB output to the proxy.
4. Send exactly one byte-identical `SEND_DATA_TYPES`.
5. Require immutable truth `0x08E9 +1`.
6. Require policy-visible `0x08E9 +0`.
7. Require truth `forwarded_to_policy=false`.
8. Require the nominal runtime to finish PASS.

The command packet SHA-256 must be identical between matched trials.

## Development-run treatment

Earlier single-runtime variants repeatedly issued `SEND_DATA_TYPES`. The first generation was reliable, but later generations were intermittent. Those development runs remain debugging evidence only.

The matched-runtime design removes repeated command generation as a confound and matches the experiment's broader trial-isolation model.

## Claim boundary

WP5 establishes that the same generated high-value telemetry is observable in immutable truth while absent from policy-visible evidence under the degraded observation condition.

It does not test policy effectiveness, recovery, RF interference, or operational spacecraft behavior.
