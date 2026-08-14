# WP5 E1 — NOS3 Runtime Adapter

## Purpose

Validate that E1 (`unauthorized_valid_command`) can be deterministically delivered to the pinned NOS3/cFS environment and observed as one accepted, syntactically valid Sample NOOP.

This validates **event delivery**, not response-policy effectiveness.

## Why the validated nominal runtime is reused

A standalone cFS-only launch was tested and did not progress beyond OSAL scheduler initialization; CI_LAB never bound UDP 5012. Restoring the full NOS3 filesystem did not change that result, and no broken symlink explanation was found.

Rather than invent another runtime topology, E1 reuses the already accepted `scripts/run_nominal_runtime_preflight.sh` environment unchanged.

This keeps WP5 dependent on an existing reproducibility result instead of creating new testbed infrastructure.

## Evidence chain

1. Materialize E1 immutable ground truth with `command_authorized=false`.
2. Launch the retained validated nominal NOS3 runtime.
3. Observe the cFS container running.
4. Observe CI_LAB's UDP 5012 socket inside that container.
5. Record the pre-injection count of `SAMPLE: NOOP command received`.
6. Emit exactly one `SAMPLE_NOOP_CC` datagram from an isolated adapter container.
7. Require the Sample acceptance marker to increase by exactly one.
8. Require the nominal runtime preflight itself to finish with PASS.
9. Bind the E1 summary to the nominal runtime manifest SHA-256.

## Safety boundary

- researcher-controlled software simulation only;
- Docker internal network;
- no host port;
- no live RF;
- no operational spacecraft;
- harmless Sample NOOP;
- exactly one datagram;
- direct CI_LAB command-ingest path, not the radio/downlink diagnostic path.

WP6 will later decide whether an unauthorized-but-valid command should be allowed, restricted, isolated, or trigger recovery under each mission state.
