# WP4 Gate 3B Phase 2 — Telemetry Setup Addendum

## Purpose

This addendum corrects the startup assumption in the original benign command and telemetry baseline protocol. The pinned Telemetry Output application does not emit telemetry immediately after cFS startup. Its initialization explicitly sets both output-enabled and output-active state to zero.

The first baseline attempt, run `20260725T212156Z`, therefore waited for `SAMPLE_HK_TLM` while the flight-software telemetry output remained disabled. The probe received zero sample packets and transmitted zero commands. The run is classified `RUN_INVALID`; it is not a failed benign-command result.

This addendum supersedes any earlier wording that could be interpreted as permitting only one total command transmission in a baseline run. The frozen accounting is now exactly:

1. one nominal setup command, `TO_ENABLE_OUTPUT`;
2. one measured command, `SAMPLE_NOOP_CC`.

No additional command is permitted.

## Pinned setup-command contract

The setup command is grounded in the pinned NOS3 ground definition and pinned TO implementation.

| Field | Frozen value |
|---|---|
| Application | `TO` |
| Command | `TO_ENABLE_OUTPUT` |
| CCSDS stream ID | `0x1880` |
| CCSDS sequence control | `0xC000` |
| CCSDS length field | `19` |
| Function code | `2` |
| Destination-host field | `radio-sim`, NUL-padded to 16 bytes |
| Destination port | `5011`, little-endian |
| Total packet length | `26` bytes |
| Packet hex | `1880c0000013021d726164696f2d73696d000000000000009313` |
| Packet SHA-256 | `c9b26e373b21170039deb6ab4d54c49401581eae5d8f3d1eaf304e65f300d3bb` |

The setup command enables the nominal telemetry route. It is infrastructure initialization, not the measured response variable.

## Readiness-gated release

The ground probe binds UDP port `6011` first but waits for a host-created trigger before transmitting anything. The trigger may be released only after all of the following are observed:

1. the ground probe reports `GROUND_PROBE_READY`;
2. the cFS container is running and its log contains `entering OPERATIONAL state`;
3. the radio container is running and its log contains `Successfully connected to TCP server!`;
4. the project network remains internal;
5. no host ports or Docker-socket mounts are present.

The wrapper then writes `immutable-ground/probe/start-baseline.trigger` atomically. The probe observes that trigger and transmits exactly one setup command.

A missing readiness marker, trigger failure, setup-vector mismatch, duplicate setup transmission, or setup-evidence failure is `RUN_INVALID`.

## Measured command remains unchanged

After telemetry output is enabled, the probe must:

1. receive at least two stable `SAMPLE_HK_TLM` packets;
2. freeze the final stable packet as the pre-command baseline;
3. transmit exactly one `SAMPLE_NOOP_CC` packet;
4. observe `CMD_COUNT == before + 1 mod 256`;
5. observe unchanged `CMD_ERR_COUNT` and `DEVICE_ERR_COUNT` within 30 seconds.

Only the `SAMPLE_NOOP_CC` transition is the measured benign-command outcome. The TO setup command must occur before the sample counter baseline is frozen.

## Evidence separation

The setup trigger, setup packet bytes, setup packet hash, orchestration readiness markers, and container state are immutable-ground evidence only. They must not appear in policy-visible evidence.

Policy-visible evidence remains limited to legitimate telemetry fields and contact-state information available to a future response policy. It receives no setup trigger, container state, truth-sink status, or evaluation annotation.

The setup evidence and measured-command evidence are independently reviewable, while the immutable-ground and policy-visible trees continue to receive independent hashes.

## Safety boundary

The setup command is a normal, pinned telemetry-output activation command sent only inside the project-labeled internal Docker network. It is not an adversarial event, malformed packet, replay, credential action, RF operation, scan, interception, or operational-target interaction.

Event injection remains disabled. The first accepted baseline run must be reviewed before a second clean run is attempted, and two accepted clean runs plus cross-run comparison remain mandatory before any event-library implementation begins.
