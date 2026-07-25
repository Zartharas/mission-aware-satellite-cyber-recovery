# WP4 Benign Baseline Plaintext Transport Addendum

## Status

Design implemented; isolated static verification pending.

Event injection remains disabled. This addendum does not authorize event-library implementation or scored cyber experimentation.

## Purpose

The benign baseline gate must first establish that the pinned flight software can receive one lawful no-op command and return the expected housekeeping evidence. Runs `20260725T212156Z`, `20260725T215659Z`, and `20260725T230542Z` were retained as `RUN_INVALID` because no `SAMPLE_HK_TLM` reached the ground probe and no measured command was transmitted.

The third run proved the CI_LAB/TO_LAB interface correction itself was active:

- CI_LAB listened on UDP `5012`;
- TO_LAB enabled output to `active-gs:5011`;
- the radio runtime copy contained the bounded `5010 -> 5012` correction;
- the radio container carried the `active-gs` alias;
- all scoped runtime components remained healthy;
- cleanup and both evidence hashes passed.

## Confirmed packet-layer incompatibility

The pinned flight applications and the pinned standalone CryptoLib program operate at different packet layers in this topology:

1. CI_LAB expects a plain cFS command packet on UDP `5012`.
2. TO_LAB emits plain cFS telemetry packets to UDP `5011`.
3. The standalone CryptoLib TC path constructs and secures a transfer frame before forwarding it.
4. The standalone CryptoLib TM path calls `Crypto_TM_ProcessSecurity()` before it will forward recovered space packets to UDP `6011`.

Accordingly, the standalone CryptoLib program is not a transparent relay for the plain CI_LAB/TO_LAB packets used by this nominal command/telemetry gate. Keeping it in this gate would test an incompatible integration topology rather than the frozen no-op acceptance claim.

## Corrected baseline transport profile

The nominal baseline uses a deterministic internal plaintext UDP relay:

```text
Ground probe:6010
        |
        v
Allowlisted relay (compatibility alias: cryptolib)
        |
        v
Radio:8010 -> CI_LAB:5012

TO_LAB:5011 -> Radio:5011
        |
        v
Allowlisted relay:8011 -> Ground probe:6011
```

The relay starts before the radio so the existing radio configuration can resolve the compatibility alias. The alias name does not indicate that CryptoLib is running.

## Relay restrictions

The relay has no general command-forwarding interface. It must:

- accept only packet `18fac000000100dc`;
- require SHA-256 `722b8fe72fb18ee581c970ea92c100f435fa90ccccaf0a05bf3e8bee0c4d13bd`;
- forward at most one command per run;
- reject any altered or duplicate command state as `RUN_INVALID`;
- forward telemetry without modification;
- remain on the project-labeled internal Docker network;
- publish no host ports;
- mount no Docker socket;
- have no external egress.

A baseline PASS additionally requires independent relay-log evidence of exactly one command receive, exactly one matching command forward, at least one telemetry forward, and zero relay-invalid events.

## Evidence boundary

Relay logs, runtime configuration, container inspection, liveness, orchestration timestamps, and truth-sink evidence are immutable-ground evidence only. Policy-visible evidence remains limited to legitimate SAMPLE telemetry fields and timestamps. The relay does not expose orchestration or truth data to a future policy.

## CryptoLib scope

CryptoLib remains pinned and source-reviewed, but cryptographic semantics are explicitly deferred. No result from the plaintext-relay baseline may be described as validating SDLS, TC protection, TM processing, security-association behavior, or cryptographic recovery.

A later gate must use a compatible flight-side or transfer-frame-aware CryptoLib integration before any cryptographic claim is permitted.

## Acceptance gate

Two separate clean plaintext-relay baseline runs are required. Each run must satisfy:

- two stable pre-command `SAMPLE_HK_TLM` packets;
- exactly one measured `SAMPLE_NOOP_CC` transmission;
- `CMD_COUNT` increases by one modulo 256;
- `CMD_ERR_COUNT` remains unchanged;
- `DEVICE_ERR_COUNT` remains unchanged;
- relay command and telemetry accounting passes;
- all scoped runtime components remain healthy;
- cleanup leaves no project resources;
- immutable-ground and policy-visible evidence hashes validate independently.

The two accepted runs must then pass cross-run structural comparison. Event injection remains blocked after this gate until the separate experiment-design authorization is recorded.
