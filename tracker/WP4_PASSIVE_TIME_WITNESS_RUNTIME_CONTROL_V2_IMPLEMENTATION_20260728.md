# WP4 Passive Time-Witness Runtime-Control v2 Implementation (D-062)

Implementation disposition date: 2026-07-29

Phase initiated: 2026-07-28

Decision: D-062

Disposition: `ACCEPTED_IMPLEMENTATION_ONLY`

Contract version: `0.4.8`

Contract status: `PASSIVE_TIME_WITNESS_RUNTIME_CONTROL_V2_IMPLEMENTED_STATIC_GATE_PENDING`

Required next decision: D-063

Runtime-authorization decision: D-064 only after D-063 acceptance

## Scope

D-062 implements the versioned passive time-witness runtime-candidate generator and records its deterministic generated-candidate identity. It does not create the D-063 static verifier, accept a v2 static gate, authorize runtime, execute the candidate, invoke real Docker, create diagnostic or baseline evidence, or modify retained evidence.

## Starting state

- Branch: `wp4-d062-runtime-control-implementation`
- HEAD: `948f405581eb3909ae65d9393f98640fe616058e`
- D-061 contract: `0.4.7`
- D-061 status: `PASSIVE_TIME_WITNESS_RUNTIME_CONTROL_DESIGN_LOCKED_IMPLEMENTATION_PENDING`
- Historical D-060 candidate identity: `0fe76023ccc968f0aa12fa27db0a5ae21597b03e53066cebb5cf56bc29572259`
- Historical identity remains accepted for static-baseline provenance only and remains runtime-authorization-ineligible.

## Implemented files and identities

- Generator: `scripts/prepare_passive_time_witness_runtime_candidate_v2.sh`
- Generator SHA-256: `504069a6fa6889a998c1b98ea5211c78c2a12006f7f6ead0bc4a060175e22a3b`
- Deterministic generated candidate SHA-256: `b541d22ecd7a94b2acb1f85bb9478453b090ab11e19fb5b667eed1b588a27322`
- Actual-v3 materialized topology review artifact SHA-256: `3fb6b0bf6a542a5dbbc2046fa01f062afe71e127160f4555715f6d7a6e28bd3e`

The generated candidate is emitted only to an approved temporary or explicit review directory. It is not committed as a runtime artifact.

## Actual-v3 topology retained

The v2 candidate preserves the validated telemetry-only topology used by the materialized v3 runtime:

- `active-gs` byte-preserving UDP proxy bound to `5013`, forwarding to `radio-sim:5011`;
- metadata-only generic-radio socket interposition for UDP `5011` ingress and UDP `8011` egress;
- UDP `8011` egress sink;
- NOS Engine server, TimeDriver, 42, truth sink, fourteen hardware simulators, command-bus bridge, and cFS;
- one passive NOS Engine time witness using the already accepted witness source and exact-schema validator;
- project-labeled Docker internal bridge only, with no host ports or external egress.

The proxy/sink records counters and readiness only. It does not retain packet payload, packet hashes, or source IP addresses.

## Observation-duration resolution

D-061 intentionally left the exact duration unresolved. D-062 freezes it at exactly **70 seconds**.

| Derivation element | Value |
|---|---:|
| Retained successful UDP `5011` metadata span | 49.880617419 s |
| Configured time-tick interval | 0.010 s |
| Span plus one tick | 49.890617419 s |
| Historical metadata observation lower bound | 30 s |
| Selected maximum basis | 49.890617419 s |
| Conservative multiplier | 1.25 |
| Multiplied duration | 62.363271774 s |
| Rounding rule | ceiling to next 10 s |
| Frozen observation | **70 s** |

The observation begins only after required readiness, including successful UDP `5011` `recvfrom` metadata and passive-witness connection. There is no duration environment override.

## Cleanup and containment controls

- `set -Eeuo pipefail`;
- fail-closed contract and candidate-self-hash gate before Docker-capable functions;
- cleanup defined before Docker resource creation;
- `EXIT`, `INT`, `TERM`, and `HUP` traps installed before the first Docker invocation;
- Python `subprocess.run(..., timeout=...)` for bounded Docker operations;
- 60-second readiness timeout;
- 10-second container stop grace;
- 15-second cleanup-command timeout;
- 15-second network-removal timeout;
- reverse-creation-order container stop and removal;
- exact same-run project/phase/run-labeled network removal;
- idempotent cleanup and no global Docker prune;
- ten post-cleanup zero-resource checks at one-second intervals;
- cleanup failure overrides nominal completion and classifies invalid infrastructure evidence;
- fresh evidence root rejection if the run namespace already exists;
- no host network, host ports, Docker socket, external egress, command source, command transmission, event injection, packet capture, packet hash collection, IP-address retention, or scientific-outcome authorization.

## Evidence boundary

- immutable-ground and policy-visible are separate sibling roots;
- socket and time-witness monotonic records remain immutable-ground only;
- policy-visible output contains no tick values, monotonic timestamps, UDP timing relationship, or derived timing value;
- independent SHA-256 manifests are generated for each evidence root;
- partial evidence is retained after post-creation failure;
- cleanup removes Docker resources only and never deletes evidence.

## D-062 validation result

The D-062A non-runtime validation established:

- generator SHA-256 `504069a6fa6889a998c1b98ea5211c78c2a12006f7f6ead0bc4a060175e22a3b`;
- deterministic candidate SHA-256 `b541d22ecd7a94b2acb1f85bb9478453b090ab11e19fb5b667eed1b588a27322`;
- double emission `IDENTICAL`;
- authorization gate before cleanup definition and before every Docker invocation;
- all four traps before the first Docker invocation;
- fixed 70-second observation loop;
- current-contract candidate result rc=`1`;
- closed-gate marker `CLOSED_GATE_NOT_AUTHORIZED`;
- fake Docker invoked: false;
- retained evidence modified: false;
- real Docker invoked: false;
- candidate runtime executed: false;
- expected one-file implementation scope before governance updates: PASS;
- nothing staged: PASS.

This validation is an implementation check only. It does not replace or pre-accept the D-063 static gate.

## Contract state after D-062

- `gate.passive_time_witness_runtime_candidate_v2_static_verification=PENDING`
- `gate.accepted_runtime_entrypoint_v2_sha256=""`
- `gate.accepted_runtime_entrypoint_sha256=0fe76023ccc968f0aa12fa27db0a5ae21597b03e53066cebb5cf56bc29572259` unchanged
- `gate.diagnostic_runtime_authorized=false`
- `gate.diagnostic_runtime_attempts_authorized=0`
- baseline authorizations false
- command transmission false
- event injection false
- scientific outcome false
- cryptographic semantics claims false

## Next gate

D-063 must implement, execute, and review a separate fail-closed v2 static verifier that binds PASS to the exact generator and generated-candidate hashes. Runtime remains unauthorized throughout D-063. D-064 is the only later disposition that may consider exactly one bounded passive telemetry attempt after D-063 is accepted.
