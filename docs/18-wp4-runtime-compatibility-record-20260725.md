# WP4 Runtime Compatibility Record — 2026-07-25

## Status

The bounded headless runtime check has not passed yet. Run `20260725T190105Z` remains classified as `RUN_INVALID` because the failures arose from testbed dependencies rather than from any scored study condition.

## Confirmed working components

The corrected individual-launch topology kept NOS Engine, the time driver, 42, cFS, CryptoLib, the command-bus bridge, and fourteen non-camera hardware simulators live at the startup observation. Project-scoped cleanup completed without leaving labeled containers or networks.

## Compatibility findings

### COSMOS-dependent truth streamer

The selected NOS3 XML configures `truth42sim` to send truth telemetry to hostname `cosmos` on port 5111. The infrastructure-only headless check does not launch COSMOS, so this process does not belong in this phase. It will be restored only when a controlled and frozen ground-software or telemetry-sink dependency is defined.

### Camera payload simulator

The camera simulator exited cleanly with code 0. Its implementation normally remains in a loop until explicitly stopped, but the filtered evidence does not establish why it returned. The frozen minimum pilot covers nominal, low-power/eclipse, and software-update/recovery mission states, not a payload mission state. The camera is therefore omitted from this phase and must be independently validated before any future payload extension.

### Generic radio hostname

The XML expects the radio process to resolve as `radio-sim`. The earlier wrapper assigned only `generic-radio-sim`, causing name-resolution and UDP-bind errors. The revised wrapper assigns `radio-sim` as the primary hostname and retains `generic-radio-sim` as a secondary alias.

### Terminal environment

The time driver stayed live but reported an unknown terminal. The revised wrapper sets `TERM=xterm` for all runtime containers.

### Log interpretation

A bridge warning about an inferred plug-in can coexist with a live dedicated bridge process. The cFS initialization text `CFE_PSP_AttachExceptions Called` is not sufficient by itself to classify a runtime exception. Acceptance is based on component liveness, exit codes, isolation checks, and component-specific evidence rather than broad keyword matching alone.

## Revised Phase 1 scope

The next bounded check launches NOS Engine, the time driver, headless 42, fourteen hardware simulators relevant to the frozen pilot, the dedicated command-bus bridge, CryptoLib, and cFS.

It deliberately omits COSMOS, `truth42sim`, and `camsim` from this infrastructure-only phase. These omissions are recorded in the runtime manifest and are not silent health assumptions.

## Acceptance boundary

Every launched process must remain live for the bounded observation period. All containers must remain only on the project internal network, with no host ports and no Docker-socket mounts. Evidence capture and project-scoped cleanup must complete successfully.

Passing this check does not complete the nominal baseline gate. The benign command and telemetry baseline must still be defined and reproduced twice, and ground-truth evidence must remain separate from policy-visible evidence before later experimental work begins.
