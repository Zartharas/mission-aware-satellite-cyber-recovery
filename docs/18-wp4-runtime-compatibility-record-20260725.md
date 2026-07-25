# WP4 Runtime Compatibility Record — 2026-07-25

## Status

Gate 3B Phase 1 passed in bounded run `20260725T201918Z`. The result is classified as `RUNTIME_PREFLIGHT_PASS`, with exit code 0. The pass establishes that the scoped headless NOS3 stack can remain live on the project internal Docker network under the frozen toolchain and launch topology.

This is an infrastructure and isolation result only. It does not establish benign command acceptance, telemetry correctness, cryptographic semantics, trusted recovery, or readiness for event injection.

## Successful-run evidence

The run used a 60-second observation period after a 30-second startup grace period. All 21 expected runtime components were recorded as `running:0` at startup and throughout the bounded observation. The liveness record contained no non-running rows.

The manifest recorded:

- `truth_sink_connection=ready` at `2026-07-25T20:19:34Z`;
- `radio_tcp_8010_listener=ready` at `2026-07-25T20:19:39Z`;
- `runtime_preflight_status=PASS`;
- `terminal_classification=RUNTIME_PREFLIGHT_PASS`;
- `event_injection=disabled`;
- an internal bridge network, with no host ports and no Docker-socket mounts.

The truth sink connected to `fortytwo:9999` and continuously drained the synthetic truth stream. The generic-radio simulator initially retried the 42 port-4286 connection, then reported a successful connection. It subsequently bound `radio-sim:8010`, accepted the CryptoLib TCP connection, and established its telemetry forwarding path to `cryptolib:8011`.

The local runtime evidence remains under ignored path `artifacts/runtime/20260725T201918Z`. A compact committed record is stored at `artifacts/nominal-runtime-preflight-lock.txt`.

## Confirmed working components

The accepted topology kept NOS Engine, the time driver, headless 42, the internal truth sink, cFS, the command-bus bridge, CryptoLib, and fourteen non-camera hardware simulators live through the bounded check. Project-scoped cleanup completed without leaving labeled containers or networks.

## Compatibility findings

### COSMOS-dependent truth streamer

The selected NOS3 XML configures `truth42sim` to receive truth data from 42 on port 9999 and then send truth telemetry to hostname `cosmos` on port 5111. The infrastructure-only headless check does not launch COSMOS, so the full `truth42sim` process does not belong in this phase. It will be restored only when a controlled and frozen ground-software or telemetry-sink dependency is defined.

### Ordered 42 IPC dependency

Run `20260725T192635Z` established that the generic-radio simulator remained alive but never exposed its CryptoLib-facing TCP listener on port 8010. Its log showed repeated connection refusals to the 42 host on port 4286.

The pinned `Inp_IPC.txt` defines the truth-data server on port 9999 before the later FSS, IMU, star-tracker, EPS, and radio server entries. The pinned simulator XML normally supplies the port-9999 client through `truth42sim`. Because the headless scope omitted that client, 42 did not progress to the later port-4286 radio stream.

The accepted preflight therefore launches a minimal read-only client on the internal Docker network. It connects only to `fortytwo:9999`, drains the synthetic truth stream, and records connection state and byte counts. It does not publish host ports, contact COSMOS, inject commands, or expose truth data to policy logic. This is a compatibility substitute, not the final ground-truth evidence implementation.

### CryptoLib transport

Run `20260725T191239Z` showed that CryptoLib could start and then exit with container code 255 while all preceding scoped components remained live. The wrapper now explicitly selects TCP on the radio and CryptoLib, preserves CryptoLib interactive stdin, and requires an observed `radio-sim:8010` listener before CryptoLib is launched.

In the passing run, the radio accepted the CryptoLib TCP connection and remained live. CryptoLib itself produced no log output, so the result proves process liveness and transport establishment only; it does not prove correct encryption, authentication, packet transformation, or command validation.

### Camera payload simulator

The camera simulator exited cleanly with code 0 in an earlier compatibility run. The filtered evidence did not establish why it returned. The frozen minimum pilot covers nominal, low-power/eclipse, and software-update/recovery mission states, not a payload mission state. The camera remains omitted from this phase and must be independently validated before any future payload extension.

### Generic radio hostname

The XML expects the radio process to resolve as `radio-sim`. An earlier wrapper assigned only `generic-radio-sim`, causing name-resolution and UDP-bind errors. The accepted wrapper assigns `radio-sim` as the primary hostname and retains `generic-radio-sim` as a secondary alias.

### Terminal environment

The time driver previously stayed live but reported an unknown terminal. The accepted wrapper sets `TERM=xterm` for all runtime containers.

### 42 material messages

The 42 log reported repeated missing-material messages and default-material substitutions during startup. These messages did not terminate 42 or any dependent component during the accepted run. They are retained as known initialization output and must not be silently interpreted as validated visual-model fidelity.

### Evidence availability on dependency failure

The liveness CSV is created before container startup. A readiness-gate failure therefore retains a valid header and all available container logs and inspections, even when the full startup observation has not begun.

### Log interpretation

A bridge warning about an inferred plug-in can coexist with a live dedicated bridge process. The cFS initialization text `CFE_PSP_AttachExceptions Called` is not sufficient by itself to classify a runtime exception. Acceptance is based on component liveness, exit codes, isolation checks, dependency readiness, and component-specific evidence rather than broad keyword matching alone.

## Accepted Phase 1 scope

The accepted bounded check launches NOS Engine, the time driver, headless 42, a byte-count-only internal truth sink, fourteen hardware simulators relevant to the frozen pilot, the dedicated command-bus bridge, CryptoLib, and cFS.

It deliberately omits COSMOS, the COSMOS-forwarding `truth42sim` process, and `camsim`. These omissions and the truth-sink substitute are recorded in the runtime manifest and are not silent health assumptions.

## Acceptance boundary and next gate

Gate 3B Phase 1 is complete. Gate 3B Phase 2 must now define and reproduce the benign command-and-telemetry baseline twice from clean runtime state. That phase must specify the exact cFE command, command-acceptance assertion, required telemetry fields, timing tolerances, controlled ground endpoint, and separate immutable ground-truth and policy-visible evidence paths.

Event injection remains blocked until both benign baseline runs pass and the evidence-separation requirement is demonstrated.
