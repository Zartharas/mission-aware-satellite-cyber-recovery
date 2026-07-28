# WP4 Passive NOS Engine Time-Witness Plan

Date: 2026-07-26
Decisions: D-057, D-058, and D-059
Status: Implementation candidate created; static-gate review pending

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
  - SHA-256: 8b3c1061b910c75e75a828101d74243f5b7e4f344dda3e2fc6ce0dda2dd4091e
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
- Neither the original Part 5 technical PASS nor the Part 7D remediated-verifier technical PASS has been governance-accepted.
- The static gate is not accepted.
- No runtime is authorized.
- No diagnostic or baseline may run.
- Commands and event injection remain blocked.
- No scientific outcome may be claimed.
- D-060 is reserved for a later decision to accept or reject the static-gate result.

### Provenance note (Part 7E.1)

- The current implementation manifest above records the remediated verifier hash 947961bfcbee386553c472fef1b2f9b25fa5cf03f1120e750085c9dd6e96ad9f. The superseded original Part 5 verifier hash 0f4db49582d8cacab1fefe7919af7a104bda5360ae1d82d4901d5396a13a52d3 is retained here only as clearly labeled historical provenance of the superseded original; it is not the current verifier.
- D-060 remains reserved for the disposition of the current remediated verifier result; it has not been created as a decision.

No result recorded here authorizes runtime execution, a telemetry diagnostic, a benign baseline, command transmission, event injection, or any scientific-outcome classification.
