# WP4 Runtime Compatibility Record — 2026-07-25

## Status

The bounded headless runtime check has not passed yet. The retained compatibility runs remain classified as `RUN_INVALID` because the failures arose from testbed dependencies rather than from any scored study condition.

## Confirmed working components

The corrected individual-launch topology has kept NOS Engine, the time driver, 42, cFS, the command-bus bridge, and fourteen non-camera hardware simulators live through progressively later startup gates. Project-scoped cleanup has completed without leaving labeled containers or networks.

## Compatibility findings

### COSMOS-dependent truth streamer

The selected NOS3 XML configures `truth42sim` to receive truth data from 42 on port 9999 and then send truth telemetry to hostname `cosmos` on port 5111. The infrastructure-only headless check does not launch COSMOS, so the full `truth42sim` process does not belong in this phase. It will be restored only when a controlled and frozen ground-software or telemetry-sink dependency is defined.

### Ordered 42 IPC dependency

Run `20260725T192635Z` established that the generic-radio simulator remained alive but never exposed its CryptoLib-facing TCP listener on port 8010. Its log showed repeated connection refusals to the 42 host on port 4286.

The pinned `Inp_IPC.txt` defines the truth-data server on port 9999 before the later FSS, IMU, star-tracker, EPS, and radio server entries. The pinned simulator XML normally supplies the port-9999 client through `truth42sim`. Because the headless scope omitted that client, the current working diagnosis is that 42 did not progress to the later port-4286 radio stream. This is a testbed initialization dependency, not a radio, CryptoLib, or policy result.

The revised preflight therefore launches a minimal read-only client on the internal Docker network. It connects only to `fortytwo:9999`, drains the synthetic truth stream, and records connection state and byte counts. It does not publish host ports, contact COSMOS, inject commands, or expose truth data to policy logic. This is a preflight compatibility substitute, not yet the final ground-truth evidence implementation.

### CryptoLib transport

Run `20260725T191239Z` showed that CryptoLib could start and then exit with container code 255 while all preceding scoped components remained live. The pinned standalone program uses status `-1` for a failed socket path, which appears as 255 at the container boundary. The wrapper now explicitly selects TCP on the radio and CryptoLib, preserves CryptoLib interactive stdin, and requires an observed `radio-sim:8010` listener before CryptoLib is launched.

### Camera payload simulator

The camera simulator exited cleanly with code 0. Its implementation normally remains in a loop until explicitly stopped, but the filtered evidence does not establish why it returned. The frozen minimum pilot covers nominal, low-power/eclipse, and software-update/recovery mission states, not a payload mission state. The camera is therefore omitted from this phase and must be independently validated before any future payload extension.

### Generic radio hostname

The XML expects the radio process to resolve as `radio-sim`. An earlier wrapper assigned only `generic-radio-sim`, causing name-resolution and UDP-bind errors. The revised wrapper assigns `radio-sim` as the primary hostname and retains `generic-radio-sim` as a secondary alias.

### Terminal environment

The time driver stayed live but reported an unknown terminal. The revised wrapper sets `TERM=xterm` for all runtime containers.

### Evidence availability on dependency failure

The liveness CSV is now created before container startup. A readiness-gate failure therefore retains a valid header and all available container logs and inspections, even when the full startup observation has not begun. The absence of CryptoLib or liveness rows in earlier runs reflects that the wrapper correctly stopped before those components were launched.

### Log interpretation

A bridge warning about an inferred plug-in can coexist with a live dedicated bridge process. The cFS initialization text `CFE_PSP_AttachExceptions Called` is not sufficient by itself to classify a runtime exception. Acceptance is based on component liveness, exit codes, isolation checks, dependency readiness, and component-specific evidence rather than broad keyword matching alone.

## Revised Phase 1 scope

The next bounded check launches NOS Engine, the time driver, headless 42, a byte-count-only internal truth sink, fourteen hardware simulators relevant to the frozen pilot, the dedicated command-bus bridge, CryptoLib, and cFS.

It deliberately omits COSMOS, the COSMOS-forwarding `truth42sim` process, and `camsim`. These omissions and the truth-sink substitute are recorded in the runtime manifest and are not silent health assumptions.

## Acceptance boundary

The truth sink must connect to port 9999, the radio must expose its TCP listener on port 8010, and every launched process must then remain live for the bounded observation period. All containers must remain only on the project internal network, with no host ports and no Docker-socket mounts. Evidence capture and project-scoped cleanup must complete successfully.

Passing this check does not complete the nominal baseline gate. The benign command and telemetry baseline must still be defined and reproduced twice, and immutable ground-truth evidence must remain separate from policy-visible evidence before later experimental work begins.
