# WP4 Runtime Preflight — Gate 3B Phase 1

## Status

This phase validates bounded, headless NOS3/cFS component startup on a project-scoped internal Docker network. It does not send a spacecraft command, score telemetry, inject a cyber event, or qualify as either of the two accepted nominal baseline runs.

## Why the preflight is separate

The selected upstream NOS3 CI launcher is useful as a reference, but it is not used unchanged because it:

- refers to a mutable NOS3 image tag;
- starts a COSMOS container that performs an online package installation;
- expects graphical/X11 resources for 42;
- uses broad container and network cleanup patterns that could affect unrelated Docker workloads.

The research wrapper instead uses the pinned NOS3 image digest, project and run labels, a Docker `--internal` bridge network, no published host ports, no Docker-socket mount, a bounded observation interval, exact-resource cleanup, and retained runtime evidence.

## Components launched

The preflight launches the following components from the previously built and locked artifacts:

1. NOS Engine server
2. NOS time driver
3. 42 truth simulator
4. NOS3 `truth42sim` adapter
5. Fifteen component hardware simulators, each through `nos3-single-simulator`
6. NOS3 simulation command-bus bridge
7. CryptoLib standalone support process
8. cFS/cFE flight software

The frozen component simulator set follows the pinned NOS3 `scripts/ci_launch.sh` list:

- `camsim`
- `generic-css-sim`
- `generic-eps-sim`
- `generic-fss-sim`
- `gps`
- `generic-imu-sim`
- `generic-mag-sim`
- `generic-reactionwheel-sim0`
- `generic-reactionwheel-sim1`
- `generic-reactionwheel-sim2`
- `generic-radio-sim`
- `sample-sim`
- `generic-star-tracker-sim`
- `generic-thruster-sim`
- `generic-torquer-sim`

The default XML also marks the time driver, terminals, and command-bus bridge active. The wrapper therefore does not use `nos3-all-simulators`, because that aggregate executable attempts to instantiate all active entries while the time driver and command-bus bridge are already launched by their dedicated executables. The command-bus bridge remains a separate process, matching the pinned upstream launch topology.

The NOS Engine server uses detached interactive-TTY mode, matching the pinned upstream CI launcher, and receives both `nos-engine-server` and `sc01-nos-engine-server` network aliases required by the frozen XML configuration.

The runtime copy of `Inp_Sim.txt` changes only the 42 `Graphics Front End?` setting from `TRUE` to `FALSE`. The committed NOS3 and 42 source trees are not modified. The 42 source tree is mounted read-only, while its generated runtime input/output directory is mounted separately at `/work/fortytwo-inout`.

## Safety controls

The wrapper must fail when:

- a required lock does not show `PASS`;
- NOS3 or 42 is not at the frozen commit;
- either external source worktree is dirty;
- a required runtime artifact is missing;
- the pinned image digest is absent;
- an earlier project-labeled runtime remains active;
- the created Docker network is not internal;
- a component exits during the observation interval;
- a component is connected to an unexpected network;
- a component publishes a host port;
- a component mounts the Docker socket.

Cleanup targets only resources carrying the exact project and run labels. Unrelated Docker containers and networks are not selected.

## Recorded infrastructure failures

### Run `20260725T182801Z`

- Classification: `RUN_INVALID`
- Exit code: `125`
- Cause: Docker could not create a writable child bind mount beneath the read-only `/work/fortytwo` source-tree mount.
- Correction: mount the generated 42 input/output directory separately at `/work/fortytwo-inout`.

### Run `20260725T183634Z`

- Classification: `RUN_INVALID`
- Exit code: `1`
- NOS Engine container: exited cleanly with code `0` under a non-interactive launch mode.
- Aggregate simulator container: exited with code `139`.
- Immediate fatal condition: `SIM_CMDBUS_BRIDGE` was treated as an ordinary plug-in model by `nos3-all-simulators`, but the bridge is provided by the dedicated `nos3-sim-cmdbus-bridge` executable.
- Correction: follow the pinned upstream topology by starting the engine in detached interactive-TTY mode, launching `truth42sim`, launching the frozen hardware-simulator set individually, and retaining the dedicated command-bus bridge process.

Neither failure is a cyber, containment, mission, or recovery result. Both are retained as infrastructure evidence supporting testbed debugging and reproducibility.

## Run procedure

Pull the new phase files:

```bash
git pull origin main
git log --oneline --decorate -8
git status
```

Confirm no stale project resources remain:

```bash
bash scripts/cleanup_nominal_runtime.sh
```

Run the default 60-second preflight:

```bash
DURATION_SECONDS=60 STARTUP_GRACE_SECONDS=20 bash scripts/run_nominal_runtime_preflight.sh
```

The accepted terminal output is:

```text
NOMINAL_RUNTIME_PREFLIGHT_STATUS=PASS
```

A failure is classified as infrastructure evidence:

```text
NOMINAL_RUNTIME_PREFLIGHT_STATUS=FAIL
```

A failed preflight does not count as a cyber, containment, or recovery result.

## Evidence review

The wrapper stores ignored evidence under:

```text
artifacts/runtime/<RUN_ID>/
```

Review the most recent run:

```bash
LATEST="$(find artifacts/runtime -mindepth 1 -maxdepth 1 -type d | sort | tail -n 1)"
printf 'Latest evidence: %s\n' "$LATEST"
cat "$LATEST/runtime-manifest.txt"
column -s, -t < "$LATEST/liveness.csv"
grep -RniE 'fatal|segmentation|abort|exception|error' "$LATEST"/*.log || true
git status --short
```

Expected repository behavior:

- generated runtime evidence remains ignored;
- NOS3 and 42 source worktrees remain clean;
- project containers and the project runtime network are removed by the exit trap;
- the top-level repository has no new tracked changes.

## Acceptance boundary

Gate 3B Phase 1 passes when one bounded preflight produces `NOMINAL_RUNTIME_PREFLIGHT_STATUS=PASS`, all required components remain live, the network and mount controls pass, cleanup is complete, and the logs show no unexplained fatal condition.

Passing this phase authorizes development of Gate 3B Phase 2 only:

- pin or eliminate the ground-software dependency;
- define one exact benign cFE command;
- define the command-acceptance counter or state change;
- define required telemetry fields and timing tolerances;
- run the complete nominal command/telemetry baseline twice from clean runtime state.

WP5 event injection remains blocked until both full nominal baseline runs pass and immutable ground-truth logging is verified separately from policy-visible evidence.
