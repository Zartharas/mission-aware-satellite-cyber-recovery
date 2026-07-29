# WP4 Passive NOS Engine Time-Witness Plan

Date: 2026-07-26
Decisions: D-057, D-058, D-059, D-060, D-061, D-062, and D-063
Additional decision: D-063R1
Status: Historical static baseline accepted under D-060 (2026-07-28); runtime-control design accepted under D-061 (2026-07-28); versioned v2 implementation accepted under D-062 (2026-07-29); D-063 v2 static gate EXECUTED and FAILED on 2026-07-29 (write-capable bind of pinned $NOS3 -> /work/nos3 not explicitly read-only); D-064 BLOCKED; runtime remains unauthorized
D-063R1 status: Design locked under D-063R1 on 2026-07-29 as DESIGN_LOCKED_IMPLEMENTATION_NOT_AUTHORIZED; design and governance record only; no implementation, no runtime, no candidate emission or execution, no verifier execution; implementation_status=NOT_STARTED; static_verification=PENDING; runtime_authorized=false; runtime_attempts=0; D-064=BLOCKED; next decision SEPARATELY_GOVERNED_V3_IMPLEMENTATION_REQUIRED_BEFORE_D064

## Purpose

The next WP4 observability step is a passive NOS Engine time witness that can establish whether authoritative simulation ticks progressed during a bounded telemetry-only observation and whether at least one tick occurred after generic-radio UDP `5011` ingress. This design does not authorize implementation execution or runtime activity.

## Accepted evidence boundary

Retained run `20260726T192902Z` proves 1,061 successful generic-radio `recvfrom` records on UDP `5011` and zero successful or failed `sendto` records to UDP `8011`. The corrected authoritative TimeDriver parser finds only tick `0`; retained time progression and callback invocation after ingress are therefore unproven.

## Permitted future witness record

Each witness record may contain only:

- sequence number;
- Linux `CLOCK_MONOTONIC` timestamp in nanoseconds;
- authoritative NOS Engine tick value;
- connection or disconnect state required to establish evidence validity.

The future implementation must emit no packet payload, packet hash, IP address, command data, policy state, or unrelated process metadata.

## Shared-clock requirement

The passive time witness and the accepted generic-radio socket metadata shim must use the same Linux `CLOCK_MONOTONIC` basis. A later static verifier must prove the clock source in both implementations and reject any wrapper that cannot establish a common monotonic ordering basis.

The shared clock may support ordering between authoritative time ticks and socket calls. It does not by itself prove that generic-radio received a callback.

## Prohibited capabilities and changes

The future witness, wrapper, and static gate must forbid:

- command sources and command transmission;
- event injection;
- packet payload capture;
- packet hashes;
- IP-address collection;
- packet-capture capabilities;
- host networking;
- host port publication;
- Docker-socket mounts;
- external network egress;
- policy access to immutable-ground time evidence;
- modification of pinned NOS3, generic-radio, sim-common, or nos-time-driver sources.

## Evidence placement

Authoritative time-witness records belong only in immutable-ground evidence. Policy-visible evidence may contain a non-sensitive scope marker and independent manifest information, but must not expose tick values, monotonic timestamps, or derived timing relationships.

No retained evidence from prior runs may be modified or reclassified through file replacement.

## Future static-verification gate

Before any new telemetry-only runtime can be considered, a separate static gate must prove at minimum:

1. the witness accepts time data passively and exposes no command or event-injection path;
2. its output schema is limited to the four permitted field classes;
3. its monotonic timestamp uses Linux `CLOCK_MONOTONIC` and matches the radio socket metadata shim clock basis;
4. the generated wrapper uses only a project-labeled internal network, no host networking, no host ports, no Docker socket, and no external egress;
5. the witness writes only to immutable-ground evidence;
6. policy-visible output contains no authoritative tick or monotonic-time data;
7. pinned source trees remain unchanged;
8. syntax, deterministic self-tests, generated-wrapper inspection, cleanup checks, and evidence-manifest controls pass with networking disabled where applicable.

Static-gate completion alone must not automatically authorize runtime. Any bounded runtime requires a separate decision and explicit attempt count.

## Future diagnostic acceptance evidence

A future bounded telemetry-only diagnostic may establish usable time ordering only if retained evidence shows:

- at least two distinct authoritative ticks in monotonically increasing order;
- at least one authoritative tick after the first successful UDP `5011` `recvfrom`;
- preferably at least one authoritative tick after the final successful UDP `5011` `recvfrom`, or an explicit censored classification when the observation ends first;
- zero command sources and zero command transmissions;
- no event injection;
- no retained-evidence mutation;
- valid independent immutable-ground and policy-visible manifests;
- complete project-scoped cleanup;
- no scientific-outcome classification.

## Interpretation limits

An independent witness may prove NOS Engine time progression and a post-ingress callback opportunity. It cannot prove that generic-radio's registered callback was invoked, that the callback observed the queued message, or that the due-time comparison evaluated as expected.

If advancing post-ingress ticks are proven while UDP `8011` remains absent, the remaining infrastructure boundary is callback delivery, callback queue visibility, or due-time evaluation. No source-code defect or scientific result may be claimed without additional evidence and a separately governed phase.

## Current authorization state

- Diagnostic runtime authorized: false
- Authorized diagnostic attempts: zero
- Baseline run 1 authorized: false
- Baseline run 2 authorized: false
- Command transmission allowed: false
- Event injection authorized: false
- Scientific outcome allowed: false
- CryptoLib/SDLS interpretation allowed: false

## Implementation candidate (Part 6 governance record)

Decision D-059 accepted the passive NOS Engine time-tick subscriber, exact-schema trace validator, emit-only telemetry-runtime candidate generator, and network-disabled static verifier described in this plan while retaining a closed runtime gate. This section records the implementation files produced under that decision. Recording these files and their hashes does not accept the static-gate result and does not authorize any runtime.

### Implementation files

- scripts/passive_nos_engine_time_witness.cpp
  - SHA-256: 830cd1a3e336c7ed2fe5c6755a30ee24b5bbc04106d3c14f2a9d26995adaaf7e
- scripts/validate_passive_time_witness_trace.py
  - SHA-256: f75131770ab9020c8c2dfb41102121e12ffd664c02a8a2e03bd8aa8c7b8d9027
- scripts/prepare_passive_time_witness_runtime_candidate.sh
  - SHA-256: e288abc456fb15cdfd5b3ab33198ee6ed2c48e3489e0c05aa6e0b61ff5db1890
- scripts/verify_passive_time_witness_static.sh
  - SHA-256: 947961bfcbee386553c472fef1b2f9b25fa5cf03f1120e750085c9dd6e96ad9f

### Static-gate result and governance status

- The original technical static verifier (scripts/verify_passive_time_witness_static.sh, superseded SHA-256 0f4db49582d8cacab1fefe7919af7a104bda5360ae1d82d4901d5396a13a52d3) produced the result PASSIVE_TIME_WITNESS_STATIC_VERIFICATION_STATUS=PASS during Part 5.
- The original Part 5 verifier was later found to permit a deferred pinned-image compile and C++ witness --self-test PASS path; it could print PASS without executing those mandatory network-disabled requirements.
- Part 7D remediated that fail-closed defect. The current remediated verifier (scripts/verify_passive_time_witness_static.sh, current SHA-256 947961bfcbee386553c472fef1b2f9b25fa5cf03f1120e750085c9dd6e96ad9f) fails closed unless Docker, the exact pinned image, the strict --network none C++14 compile, and the C++ witness --self-test all execute and pass.
- The remediated verifier was successfully executed in Part 7D and produced PASSIVE_NOS_ENGINE_TIME_WITNESS_SELF_TEST=PASS, PASSIVE_TIME_WITNESS_TRACE_VALIDATOR_SELF_TEST=PASS, PASSIVE_TIME_WITNESS_STATIC_VERIFICATION_STATUS=PASS, VERIFIER_RC=0.
- D-060 (governance_date=2026-07-28) governance-accepted the remediated static-gate result and locked the reviewed implementation and deterministic runtime-candidate hashes in artifacts/wp4-passive-time-witness-static-gate-lock.txt. The final read-only review confirmed exact pinned-image compilation, the C++ witness self-test, the trace-validator self-test, deterministic candidate generation, fail-closed candidate execution, zero fake-Docker invocation, zero project-labeled containers and networks before and after verification, and unchanged retained evidence.
- An isolated post-whitespace recheck at commit `eca23aee777dff8f523aad485e074dc62c1983f8` re-established the technical PASS for witness SHA-256 `830cd1a3e336c7ed2fe5c6755a30ee24b5bbc04106d3c14f2a9d26995adaaf7e` and generated candidate SHA-256 `0fe76023ccc968f0aa12fa27db0a5ae21597b03e53066cebb5cf56bc29572259`; runtime remained unauthorized.
- The static gate is accepted. Contract version advanced to 0.4.6 (PASSIVE_TIME_WITNESS_STATIC_GATE_ACCEPTED_RUNTIME_NOT_AUTHORIZED); gate.passive_time_witness_static_verification=PASS.
- No runtime is authorized. The accepted runtime entrypoint SHA-256 (gate.accepted_runtime_entrypoint_sha256) records candidate identity only and does not authorize execution.
- No diagnostic or baseline may run.
- Commands and event injection remain blocked.
- No scientific outcome may be claimed.
- D-062 implemented the versioned bounded runtime candidate generator and cleanup controls without authorizing runtime. The next task is the separate D-063 static gate.

### Provenance note (Part 7E.1)

- The current implementation manifest above records the remediated verifier hash 947961bfcbee386553c472fef1b2f9b25fa5cf03f1120e750085c9dd6e96ad9f. The superseded original Part 5 verifier hash 0f4db49582d8cacab1fefe7919af7a104bda5360ae1d82d4901d5396a13a52d3 is retained here only as clearly labeled historical provenance of the superseded original; it is not the current verifier.
- D-060 has been created and accepted on 2026-07-28: the remediated static-gate result is governance-accepted in artifacts/wp4-passive-time-witness-static-gate-lock.txt, while every runtime, diagnostic, baseline, command, event-injection, and scientific-outcome gate remains closed.
- Note: the witness source SHA-256 is recorded as 830cd1a3e336c7ed2fe5c6755a30ee24b5bbc04106d3c14f2a9d26995adaaf7e (the current on-disk file hash after the eca23ae trailing-whitespace cleanup). Earlier draft references cited 8b3c1061b910c75e75a828101d74243f5b7e4f344dda3e2fc6ce0dda2dd4091e, which was the file hash at commit 54c07aa before that cleanup; that value is now reconciled to the current file so the implementation manifest matches the committed file.

## Runtime-control remediation design (D-061)

Decision D-061 (2026-07-28) accepted the runtime-control remediation design only. The design is recorded in `tracker/WP4_PASSIVE_TIME_WITNESS_RUNTIME_CONTROL_DESIGN_20260728.md` and locked in `artifacts/wp4-passive-time-witness-runtime-control-design-lock.txt`; the contract advanced to `0.4.7` (`PASSIVE_TIME_WITNESS_RUNTIME_CONTROL_DESIGN_LOCKED_IMPLEMENTATION_PENDING`). No implementation script was created or modified; no candidate was emitted or executed; no static verifier ran; no Docker was invoked.

- **Current candidate `0fe76023ccc968f0aa12fa27db0a5ae21597b03e53066cebb5cf56bc29572259` is a D-060 static-baseline identity only and is runtime-authorization-ineligible in its present form.** A read-only inspection found two runtime-control gaps: no deterministic bounded observation duration and no complete internal cleanup path (it launches detached Docker resources with no timeout, no bounded wait, no EXIT trap, no reverse-order teardown, no network removal, and no post-cleanup zero-resource assertion).
- D-061 does **not revoke or rewrite D-060**. The D-060 static gate and lock remain the accepted static baseline. D-061 requires a **versioned replacement** generator and candidate rather than silently editing the accepted historical candidate.
- **Future design references (not created under D-061):** `scripts/prepare_passive_time_witness_runtime_candidate_v2.sh` (v2 generator) and `scripts/verify_passive_time_witness_runtime_candidate_v2_static.sh` (v2 static verifier). These names are design references only; they are not created under D-061.

### Required v2 control architecture (frozen)

The future v2 candidate must be a self-contained, fail-closed runtime entrypoint containing all runtime controls internally, with no reliance on an undocumented external operator procedure for duration or cleanup.

- **A. Deterministic bounded observation:** exactly one observation-duration value supplied by a governed contract field or hard-locked constant; strict integer validation (reject empty/negative/zero/non-integer/out-of-range); no unlimited or empty duration; no user-controlled expansion outside the accepted value; a bounded wait for the passive observation; the timeout result recorded distinctly from infrastructure failure; the duration begins only after required runtime readiness; the duration cannot authorize a second attempt.
- **B. Complete cleanup:** cleanup function defined before resource creation; `trap` installed before the first Docker resource is created; traps for `EXIT`, `INT`, `TERM`, and `HUP`; cleanup runs after success, failure, timeout, or interruption; containers stopped and removed in deterministic reverse order; project-labeled network removed; cleanup limited strictly to project names and labels; no global `docker prune`; idempotent; pre-existing project resources cause fail-closed abort before creation; a final assertion requires zero project-labeled containers and zero project-labeled networks; cleanup failure overrides a nominal observation result and classifies the attempt as invalid infrastructure evidence.
- **C. Evidence safety:** fresh evidence root per run; immutable-ground and policy-visible roots remain separate siblings; no overwrite or mutation of retained evidence; witness timing data immutable-ground only; policy-visible data contains no tick, monotonic timestamp, or derived timing; independent manifests generated and validated; evidence survives cleanup; partial evidence retained and classified when execution fails after evidence creation; no diagnostic or baseline evidence created during static verification.
- **D. Containment:** internal project-labeled bridge only; no host network; no host ports; no Docker socket; no external egress; no command source; no command transmission; no event injection; no packet capture; no packet payload, packet hash, or IP-address collection.
- **E. Entry-point and hash governance:** the v2 candidate must have a new deterministic SHA-256; the v2 generator must have a new SHA-256; a separate v2 static verifier must bind its PASS to the exact v2 generator and generated-candidate hashes; the v2 candidate (not an external wrapper) must become the future accepted runtime entrypoint; the existing `0fe76023...` candidate remains historical and unauthorized; `gate.accepted_runtime_entrypoint_sha256` does not change under D-061.

### Observation-duration resolution (unresolved)

There is no accepted repository precedent for an exact passive time-witness observation-duration value; the benign-baseline and radio accepted durations are readiness/acceptance timeouts, not a deterministic passive-observation window. D-061 does **not** select an arbitrary observation duration. The exact value is recorded as **unresolved** and must be frozen during the D-062 implementation disposition (via a governed contract field or a hard-locked constant), with its derivation recorded in the D-062 implementation lock.

### Frozen future phase separation

- **D-061**: runtime-control remediation design accepted; no implementation and no runtime authorization.
- **D-062**: implement the versioned v2 generator and candidate; runtime remains unauthorized.
- **D-063**: execute and review a separate fail-closed static verification gate for v2 that binds its PASS to the exact v2 generator and candidate hashes; runtime remains unauthorized. **D-063 EXECUTED 2026-07-29 — v2 candidate FAILED the gate at step 6 (write-capable bind of pinned $NOS3 -> /work/nos3 not explicitly read-only); verifier 879dcac2... rc=1; no runtime; contract 0.4.9.**
- **D-064**: consider authorization for exactly one bounded passive telemetry attempt only after a separately governed remediated candidate passes a separate static verification. **D-064 is BLOCKED pending that remediation; the D-063 candidate was rejected.**

### Interpretation limits

The future bounded attempt may establish only whether authoritative NOS Engine ticks progressed, whether at least one authoritative tick followed the first UDP `5011` ingress, and whether a post-ingress callback opportunity existed. It may not establish generic-radio callback invocation, callback queue visibility, due-time evaluation, a generic-radio source defect, mission impact, a scientific outcome, or CryptoLib/SDLS behavior.

The next acceptance gate is: a separately governed generator remediation (modify the generator, emit a new deterministic candidate, establish new generator/candidate hashes, and pass a separate static verification) before D-064 may consider one bounded passive telemetry attempt; runtime remains unauthorized.

No result recorded here authorizes runtime execution, a telemetry diagnostic, a benign baseline, command transmission, event injection, or any scientific-outcome classification.

## D-062 versioned runtime-control implementation

Decision D-062 was recorded on 2026-07-29 as **implementation-only acceptance**. It does not accept the future v2 static gate and does not authorize runtime.

### Frozen identities

- Generator: `scripts/prepare_passive_time_witness_runtime_candidate_v2.sh`
- Generator SHA-256: `504069a6fa6889a998c1b98ea5211c78c2a12006f7f6ead0bc4a060175e22a3b`
- Deterministic generated candidate SHA-256: `b541d22ecd7a94b2acb1f85bb9478453b090ab11e19fb5b667eed1b588a27322`
- Historical D-060 candidate identity retained unchanged: `0fe76023ccc968f0aa12fa27db0a5ae21597b03e53066cebb5cf56bc29572259`
- Materialized actual-v3 topology review artifact SHA-256: `3fb6b0bf6a542a5dbbc2046fa01f062afe71e127160f4555715f6d7a6e28bd3e`

The v2 candidate is a deterministic temporary emission, not a committed runtime artifact. `gate.accepted_runtime_entrypoint_v2_sha256` remains empty until a separately accepted D-063 static gate. The historical `gate.accepted_runtime_entrypoint_sha256` remains unchanged and unauthorized.

### Observation-duration resolution

D-062 resolves the D-061 duration placeholder and freezes the observation at exactly **70 seconds**:

1. retained successful UDP `5011` metadata trace span: `49.880617419` seconds;
2. configured simulation and wall tick interval: `0.010` seconds;
3. retained span plus one tick: `49.890617419` seconds;
4. conservative safety multiplier: `1.25`;
5. multiplied value: `62.363271774` seconds;
6. ceiling to the next ten-second boundary: **70 seconds**.

The historical 30-second metadata observation remains a lower-bound precedent only. No environment variable or operator input may expand or replace the frozen 70-second value.

### Implemented runtime controls

- exact fail-closed status, authorization-count, v2-static-PASS, governed-duration, proposed-attempt-count, and candidate-self-hash checks before Docker;
- `EXIT`, `INT`, `TERM`, and `HUP` traps before the first Docker invocation;
- 60-second bounded readiness controls and a 70-second observation that begins only after required readiness, including successful UDP `5011` ingress metadata and passive-witness connection;
- bounded Docker operations using Python `subprocess.run(..., timeout=...)`;
- reverse-creation-order container stop/removal, exact same-run labeled network removal, idempotent cleanup, and ten post-cleanup zero-resource assertions;
- fresh per-run evidence root; separate immutable-ground and policy-visible siblings; independent SHA-256 manifests; no policy-visible tick, monotonic timestamp, or derived timing relationship;
- actual v3 telemetry topology retained: `active-gs:5013` proxy to `radio-sim:5011`, radio egress sink on `8011`, NOS Engine, TimeDriver, 42, hardware simulators, bridge, cFS, socket metadata shim, and one passive time witness;
- no command source, command transmission, event injection, packet capture, packet hash collection, IP-address retention, host networking, host ports, Docker-socket mount, external egress, or scientific-outcome authorization.

### D-062 non-runtime validation

The generator passed Bash syntax validation, emitted byte-identical candidates twice, produced the exact candidate hash above, and the current contract caused candidate rc=`1` with `CLOSED_GATE_NOT_AUTHORIZED` before fake Docker. Retained evidence was unchanged. The candidate runtime path was not executed and real Docker was not invoked.

This D-062 validation is not the D-063 static gate. D-063 must create, execute, and govern a separate fail-closed verifier bound to the exact generator and candidate hashes. D-064 alone may later consider one bounded passive telemetry attempt, and only after D-063 is accepted.


## D-063 v2 static-gate disposition

Decision D-063 was recorded on 2026-07-29. The fail-closed v2 static verification gate was executed and the frozen v2 candidate **FAILED**.

- Disposition: `V2_STATIC_GATE_FAILED_CANDIDATE_REMEDIATION_REQUIRED`
- Activity status: COMPLETE
- Candidate result: FAIL
- D-064: BLOCKED
- Disposition record: `tracker/WP4_PASSIVE_TIME_WITNESS_RUNTIME_CANDIDATE_V2_STATIC_GATE_DISPOSITION_20260729.md`

### Controlled-execution context

- Branch: `wp4-d063-v2-static-gate`
- Starting HEAD: `0559af9841a80f9b3168d9de9dfa96cae8da9cc7`
- Contract version: `0.4.9`
- Contract status: `PASSIVE_TIME_WITNESS_RUNTIME_CANDIDATE_V2_STATIC_GATE_FAILED_REMEDIATION_REQUIRED`

### Verifier, identities, and evidence

- Verifier path: `scripts/verify_passive_time_witness_runtime_candidate_v2_static.sh`
- Verifier SHA-256: `879dcac237717e84043cac5cdcd89c8c546f568c48e4ec7c897dc5c15cfbf87f`
- Verifier mode: 755; `bash -n` PASS
- Generator SHA-256 (tested and rejected): `504069a6fa6889a998c1b98ea5211c78c2a12006f7f6ead0bc4a060175e22a3b`
- Candidate SHA-256 (tested and rejected): `b541d22ecd7a94b2acb1f85bb9478453b090ab11e19fb5b667eed1b588a27322`
- Retained log: `artifacts/wp4-passive-time-witness-runtime-candidate-v2-static-gate-failure-20260729T051122Z.log`
- Retained log SHA-256: `753bcc17a6b3cda9686f76b7120edc588da6b22cdc28757d8af942aba6fab87f` (byte-identical to raw source)

### Exact controlled-execution metrics

- verifier rc=1; Docker guard log bytes=0; final PASS marker count=0; step 8 reached count=0; writable NOS3 rejection count=1
- failure occurred at step 6 (Topology + containment + claim validation)
- no real Docker invocation; no pinned-image compile; no NOS3 runtime; no runtime candidate post-gate path; no diagnostic or baseline; no retained-evidence mutation
- runtime authorization remains false; authorized runtime attempts remain 0

### Checks that passed through step 5

Steps 1–5 passed (required files + contract JSON; fail-closed pre-gate; frozen source/artifact binding; syntax + deterministic double emission; candidate structural validation). The candidate double-emission under `mktemp` was byte-identical and matched the frozen SHA-256; the candidate was not executed.

### Exact step-6 failure

The candidate permits a write-capable bind of the pinned NOS3 source (`source=$NOS3 -> /work/nos3`) that is not explicitly read-only. The gate rejects the write capability itself, even though no observed command in the current candidate explicitly writes through the mount, because a future or altered command path could mutate the pinned source under a write-capable bind that the static verifier cannot exhaustively enumerate.

### Contract gate state after D-063

- `gate.passive_time_witness_runtime_candidate_v2_static_verification` = `FAIL`
- `gate.accepted_runtime_entrypoint_v2_sha256` = `""` (unchanged)
- `gate.diagnostic_runtime_authorized` = `false`; `gate.diagnostic_runtime_attempts_authorized` = `0`
- `gate.baseline_run_1_authorized` = `false`; `gate.baseline_run_2_authorized` = `false`; `gate.event_injection_authorized` = `false`
- Historical `gate.accepted_runtime_entrypoint_sha256` preserved unchanged: `0fe76023ccc968f0aa12fa27db0a5ae21597b03e53066cebb5cf56bc29572259`
- All top-level scientific, command-transmission, baseline, event-injection, and cryptographic-semantics permissions remain `false`.

### No runtime execution, no evidence mutation, no scientific outcome

No real Docker invocation occurred; no runtime candidate post-gate path was executed; no diagnostic or baseline was executed; no retained evidence was modified. This disposition records a static-gate failure and governance disposition only and makes no scientific, mission-impact, generic-radio-defect, CryptoLib, or SDLS claim.

### D-064 blocked and remediation required

D-064 is explicitly blocked. A separately governed remediation phase must modify the generator, emit a new deterministic candidate, establish new generator/candidate hashes, and rerun static verification. That remediation is not performed in this disposition; a remediation phase identifier is not invented here because existing project conventions do not define one for this step.

## D-063R1 v3 manifest-seed design lock

Decision D-063R1 was recorded on 2026-07-29 as `DESIGN_LOCKED_IMPLEMENTATION_NOT_AUTHORIZED`. This is a design and governance record only: it creates no v3 generator, candidate, verifier, materializer, or runtime-material manifest, and authorizes no runtime.

- Architecture: `PINNED_IMAGE_BASE_PLUS_CANONICAL_MANIFEST_BOUND_PRIVATE_HOST_WORKSPACES`
- Design record: `tracker/WP4_PASSIVE_TIME_WITNESS_RUNTIME_CANDIDATE_V3_MANIFEST_SEED_DESIGN_20260729.md` (SHA-256 `c089ffacac68694de2d446acbd301d0a96bc270fa9d1042e7e4c2c6f5bdf2f14`)
- Design lock: `artifacts/wp4-passive-time-witness-runtime-candidate-v3-manifest-seed-design-lock.txt` (SHA-256 `cebd5933d2bea7246f2a4d14d0f1efacafcb4f20afa5b901ba505a9c2512263d`)
- Contract: `0.4.10` / `PASSIVE_TIME_WITNESS_RUNTIME_CANDIDATE_V3_MANIFEST_SEED_DESIGN_LOCKED_IMPLEMENTATION_PENDING`

### Pre-write audit

- Simulator seed (`sims/build/bin` + `sims/build/lib`): 27 raw regular files; 25 included (2 ItcLogger rollover archives excluded).
- cFS seed (`fsw/build/exe/cpu1`): 1370 raw; 1365 included (5 stale runtime files excluded).
- Config seed (`cfg/build/InOut`): 36 raw; 36 included.
- 0 symlinks; 0 escaping symlinks; 0 unsupported filesystem objects; 0 hard-link aliases; 0 unclassified source paths.

### Plugin mapping

- 14 hardware simulator instances; 12 distinct hardware plugin files; 13 distinct simulator plugin files including TimeDriver.

### Architecture

- The pinned image remains the immutable execution base; image-owned files remain in the image and are never copied into the host seed.
- The host seed is bound by the canonical manifest model (normalized paths, entry types, modes, regular-file sizes and SHA-256 values, directory entries, explicit exclusions, and deterministic serialization) via the SHA-256 of the canonical manifest; stale runtime state is `MUST_BE_ABSENT_AT_START` by source evidence.
- 18 private run-scoped NOS3 workspaces (NOS Engine 1, TimeDriver 1, 14 hardware simulators, bridge 1, cFS 1), each mounted at `/work/nos3` from a private workspace never `external/nos3`; no cross-container writable log-file alias.
- Private-copy materialization (not an overlay); no hard links/reflinks/aliases to `external/nos3`.

### Governance state

- `gate.passive_time_witness_runtime_candidate_v3_static_verification=PENDING`; `gate.accepted_runtime_entrypoint_v3_sha256=""`; runtime authorization remains false with zero authorized attempts; all top-level permissions remain false.
- Historical v2 generator (`504069a6fa68...`), rejected candidate (`b541d22ecd7a...`), D-063 verifier (`879dcac2...`), D-063 retained log (`753bcc17...`), and D-060 accepted entrypoint (`0fe76023...`) remain unchanged.
- D-064 remains BLOCKED; the next decision is `SEPARATELY_GOVERNED_V3_IMPLEMENTATION_REQUIRED_BEFORE_D064`.
- Runtime compatibility remains UNPROVEN. The design requires every runtime write to be contained within a private run-scoped workspace; implementation correctness, runtime containment, and runtime compatibility remain UNPROVEN until a separately governed implementation and static verification are completed; no runtime is authorized. No scientific, mission-impact, generic-radio-defect, CryptoLib, or SDLS claim is made.

### Future verifier requirements

A future versioned verifier must fail closed unless it proves the exact new generator/candidate/manifest hashes, complete source classification, 18 private workspaces, 14 hardware instances / 12 distinct hardware plugin files / 13 distinct simulator plugin files, no mount source resolving to `external/nos3`, unique run-scoped `/work/nos3` mount sources, no writable path aliasing, workspace files matching manifest entries, unchanged historical hashes, and runtime authorization false with zero attempts.
