# WP4 Passive Time-Witness Runtime-Control Design (D-061)

Date: 2026-07-28
Decision: D-061
Phase: DESIGN-AND-GOVERNANCE ONLY
Contract version target: 0.4.7 (`PASSIVE_TIME_WITNESS_RUNTIME_CONTROL_DESIGN_LOCKED_IMPLEMENTATION_PENDING`)
Implementation decision required: D-062
Static-gate decision required: D-063
Runtime-authorization decision required: D-064
Static gate of record: D-060 (`artifacts/wp4-passive-time-witness-static-gate-lock.txt`)

## Governing rule

This document locks the runtime-control remediation design only. **D-061 does not implement any script, does not execute or emit any candidate, does not run a static verifier, and does not authorize a runtime.** No runtime, diagnostic, baseline, command transmission, event injection, or scientific outcome is authorized. Every contract gate remains closed: `gate.diagnostic_runtime_authorized=false`, `gate.diagnostic_runtime_attempts_authorized=0`, and `gate.accepted_runtime_entrypoint_sha256` is unchanged.

The current accepted candidate hash `0fe76023ccc968f0aa12fa27db0a5ae21597b03e53066cebb5cf56bc29572259` remains a **D-060 static-baseline identity only** and is **not eligible for runtime authorization in its present form**. D-061 does **not revoke or rewrite D-060**; the D-060 static gate and its lock remain the accepted static implementation baseline. D-061 requires a **versioned replacement** candidate and generator rather than silently editing the accepted historical candidate.

## Part 1 verification (starting state, confirmed)

- branch `wp4-d061-runtime-control-design`; HEAD `d1d68d4e80546ce7a92b92bb84a275c18ecedc8e`; clean working tree.
- contract version `0.4.6`; status `PASSIVE_TIME_WITNESS_STATIC_GATE_ACCEPTED_RUNTIME_NOT_AUTHORIZED`.
- `gate.diagnostic_runtime_authorized=false`; `gate.diagnostic_runtime_attempts_authorized=0`; `gate.passive_time_witness_static_verification=PASS`; accepted entrypoint identity `0fe76023...`; D-060 accepted exactly once.

## Part 2 read-only precedent findings

Inspection of the accepted bounded runtime/diagnostic runners (radio-socket-metadata v2/v3, downlink hardened, plaintext relay, benign baseline) and `scripts/cleanup_nominal_runtime.sh` established the following repository conventions, which the future v2 candidate must follow:

- **Shell discipline**: `set -Eeuo pipefail` at the top of every accepted runner.
- **EXIT trap cleanup**: `trap cleanup EXIT` with `cleanup()` capturing `local rc=$?`, performing teardown, calling `trap - EXIT`, and `exit "$rc"` (universal across accepted runners).
- **Docker-resource teardown**: project-labeled `docker rm -f` of `label=research.project=…` containers and `docker network rm` of project-labeled networks, gated by a "no project-labeled resources → OK" precheck; **no global `docker prune`** (`scripts/cleanup_nominal_runtime.sh`).
- **Readiness waits**: bounded `timeout_seconds` + `sleep 1` polling loops for log markers / UDP listeners (radio `wait_for_socket_trace`, plaintext `wait_for_udp_listener`, benign `wait_for_log_marker`). These bound **readiness**, not the passive observation window.
- **Verifier hash binding**: the accepted static verifier emits the candidate, hashes it, compiles the witness in a `--network none` pinned-image container, runs self-tests, and fails closed unless exact PASS tokens print — establishing the precedent that a v2 static verifier must bind its PASS to the exact v2 generator and generated-candidate hashes.

### Observation-duration resolution (unresolved by precedent)

There is **no accepted repository precedent for an exact passive time-witness observation-duration value**. The benign-baseline frozen durations (`BASELINE_TIMEOUT` 120–600s range, `ACCEPTANCE_TIMEOUT=30`) and the radio accepted wait values are **readiness/acceptance timeouts**, not a deterministic passive-observation window. Per the design rule, **D-061 does not select an arbitrary observation duration**. The exact observation-duration value is recorded as **unresolved** and must be frozen during the future D-062 implementation disposition (via a governed contract field or a hard-locked constant in the v2 candidate), with its derivation recorded in the D-062 implementation lock.

## Part 3 design documents (this phase creates design documents and a design lock only)

This phase creates only:
- `tracker/WP4_PASSIVE_TIME_WITNESS_RUNTIME_CONTROL_DESIGN_20260728.md` (this document)
- `artifacts/wp4-passive-time-witness-runtime-control-design-lock.txt`

It creates **no implementation scripts**. The following names are **design references only** and are **not created under D-061**:
- `scripts/prepare_passive_time_witness_runtime_candidate_v2.sh` (future v2 generator)
- `scripts/verify_passive_time_witness_runtime_candidate_v2_static.sh` (future v2 static verifier)

## Part 4 required v2 control architecture

The future v2 candidate must be a **self-contained, fail-closed runtime entrypoint** containing all runtime controls internally. It must **not** rely on an undocumented external operator procedure for duration or cleanup. Every control below is a hard requirement for the D-062 implementation and D-063 static gate; none is satisfied by the current candidate.

### A. Deterministic bounded observation

- exactly one observation-duration value;
- the value is supplied by a governed contract field or a hard-locked constant in the v2 candidate (not an unbounded or environment-defaulted value);
- strict integer validation (reject empty, negative, zero, or non-integer; reject values outside the frozen accepted value);
- no unlimited duration and no empty duration;
- no user-controlled expansion outside the accepted value (no operator override);
- a bounded wait for the passive observation (the candidate waits for the frozen duration after readiness, then stops the observation);
- the timeout/observation result is **recorded distinctly** from an infrastructure failure (a bounded observation that simply elapses is a distinct outcome, not an error, unless a control gate fires);
- the observation duration begins only after required runtime readiness is confirmed;
- the bounded duration **cannot authorize a second attempt** — the attempt count gate is independent of the duration.

### B. Complete cleanup

- the cleanup function is **defined before any Docker resource is created**;
- the `trap` is **installed before the first Docker resource is created**;
- traps are installed for **EXIT, INT, TERM, and HUP**;
- cleanup runs after **success, failure, timeout, or interruption**;
- containers are **stopped and removed in deterministic reverse order** of creation;
- the project-labeled network is **removed**;
- cleanup is **limited strictly to project names and labels** (never foreign resources);
- **no global `docker prune`** of any scope;
- cleanup is **idempotent** (safe to invoke when resources are already gone);
- **pre-existing project-labeled resources cause fail-closed abort before creation** (the attempt must not start over stale resources);
- a **final assertion requires zero project-labeled containers and zero project-labeled networks** after cleanup;
- **cleanup failure overrides a nominal observation result** and classifies the attempt as **invalid infrastructure evidence**.

### C. Evidence safety

- a **fresh evidence root per attempted run** (unique run namespace; no reuse of a prior run's evidence directory);
- immutable-ground and policy-visible roots remain **separate sibling** directories;
- **no overwrite or mutation** of retained evidence (the v2 candidate writes only to the fresh evidence root);
- witness timing data remains **immutable-ground only**;
- policy-visible data contains **no tick, no monotonic timestamp, and no derived timing** (only a non-sensitive scope marker and independent manifest);
- independent manifests are **generated and validated** for both roots;
- evidence **survives cleanup** (cleanup removes only Docker resources, never the evidence root);
- **partial evidence is retained and classified** when execution fails after evidence creation (no evidence destruction on failure);
- **no diagnostic or baseline evidence is created during static verification** (the v2 static gate must not produce runtime/diagnostic/baseline evidence).

### D. Containment

- an **internal project-labeled bridge network only** (`--internal`); no host network;
- no host ports;
- no Docker socket mount;
- no external egress;
- no command source;
- no command transmission;
- no event injection;
- no packet capture;
- no packet payload, packet hash, or IP-address collection.

### E. Entry-point and hash governance

- the v2 candidate must have a **new deterministic SHA-256** (distinct from `0fe76023...`);
- the v2 generator must have a **new SHA-256** (distinct from the accepted generator `e288abc...`);
- a **separate v2 static verifier** must bind its PASS to the **exact v2 generator and generated-candidate hashes** (mirroring the accepted static verifier's binding convention);
- the **v2 candidate itself — not an external wrapper — must become the future accepted runtime entrypoint** (the self-contained fail-closed entrypoint);
- the existing `0fe76023...` candidate **remains historical and unauthorized**;
- `gate.accepted_runtime_entrypoint_sha256` **must not change under D-061**; any change is reserved for a future accepted static gate (D-063) and runtime authorization (D-064).

## Part 5 future phase separation (frozen)

- **D-061**: runtime-control remediation design accepted; no implementation and no runtime authorization.
- **D-062**: implement the versioned v2 generator and candidate (self-contained bounded observation + complete fail-closed cleanup); runtime remains unauthorized.
- **D-063**: execute and review a separate fail-closed static verification gate for v2 that binds PASS to the exact v2 generator and candidate hashes; runtime remains unauthorized.
- **D-064**: consider authorization for exactly one bounded passive telemetry attempt **only after D-063 is accepted**.

No runtime result or scientific conclusion is reserved.

## Part 6 interpretation limits

The future bounded attempt may establish only:
- whether authoritative NOS Engine ticks progressed;
- whether at least one authoritative tick followed the first UDP `5011` ingress;
- whether a post-ingress callback opportunity existed.

It may **not** establish:
- generic-radio callback invocation;
- callback queue visibility;
- due-time evaluation;
- a generic-radio source defect;
- mission impact;
- scientific outcome;
- CryptoLib or SDLS behavior.

## Authorization state (unchanged by D-061)

- Diagnostic runtime authorized: false
- Authorized diagnostic attempts: zero
- Baseline run 1 authorized: false
- Baseline run 2 authorized: false
- Command transmission allowed: false
- Event injection authorized: false
- Scientific outcome allowed: false
- CryptoLib/SDLS interpretation allowed: false
- Accepted runtime entrypoint recorded for identity only, not authorized for execution

No result recorded here authorizes runtime execution, a telemetry diagnostic, a benign baseline, command transmission, event injection, or any scientific-outcome classification. The next acceptance gate is: implement the versioned bounded runtime candidate and cleanup controls under D-062 without authorizing runtime.

## D-062 implementation addendum

Recorded: 2026-07-29

Disposition: `ACCEPTED_IMPLEMENTATION_ONLY`

Contract target reached: `0.4.8` (`PASSIVE_TIME_WITNESS_RUNTIME_CONTROL_V2_IMPLEMENTED_STATIC_GATE_PENDING`)

D-062 implemented the versioned generator named by the D-061 design:

- `scripts/prepare_passive_time_witness_runtime_candidate_v2.sh`
- generator SHA-256 `504069a6fa6889a998c1b98ea5211c78c2a12006f7f6ead0bc4a060175e22a3b`
- deterministic generated-candidate SHA-256 `b541d22ecd7a94b2acb1f85bb9478453b090ab11e19fb5b667eed1b588a27322`

The candidate incorporates the actual accepted v3 topology, a single passive NOS Engine time witness, a hard-locked 70-second observation, candidate self-hash authorization, bounded readiness and Docker operations, all four cleanup traps, reverse-order container teardown, exact labeled-network removal, ten zero-resource cleanup assertions, and separate fresh immutable-ground and policy-visible evidence roots.

### D-061 unresolved duration closed by D-062

D-062 freezes the observation at 70 seconds. The derivation uses the retained `49.880617419`-second successful UDP `5011` trace span plus one configured `0.010`-second tick (`49.890617419` seconds), applies the conservative factor `1.25` (`62.363271774` seconds), and rounds upward to the next 10-second boundary. The value is not environment-overridable.

### Governance boundary

- `gate.passive_time_witness_runtime_candidate_v2_static_verification=PENDING`
- `gate.accepted_runtime_entrypoint_v2_sha256=""`
- `gate.diagnostic_runtime_authorized=false`
- `gate.diagnostic_runtime_attempts_authorized=0`
- historical `gate.accepted_runtime_entrypoint_sha256=0fe76023ccc968f0aa12fa27db0a5ae21597b03e53066cebb5cf56bc29572259` unchanged
- candidate executed: false
- real Docker invoked during D-062: false
- retained evidence modified: false

The D-062 implementation and deterministic-emission checks do not constitute the D-063 static gate. D-063 must separately bind a fail-closed PASS to the exact v2 generator and candidate hashes. D-064 remains the sole phase that may consider one bounded passive telemetry attempt after D-063 acceptance.
