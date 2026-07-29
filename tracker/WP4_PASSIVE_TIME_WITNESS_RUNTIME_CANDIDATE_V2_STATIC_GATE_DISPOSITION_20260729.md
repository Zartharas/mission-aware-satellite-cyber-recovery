# WP4 Passive Time-Witness Runtime-Candidate v2 Static-Gate Disposition (D-063)

Governance date: 2026-07-29

Decision: D-063

Disposition: `V2_STATIC_GATE_FAILED_CANDIDATE_REMEDIATION_REQUIRED`

Activity status: COMPLETE

Candidate result: FAIL

D-064 status: BLOCKED

## Controlled-execution context

- Branch: `wp4-d063-v2-static-gate`
- Starting HEAD: `0559af9841a80f9b3168d9de9dfa96cae8da9cc7`
- Contract version after this disposition: `0.4.9`
- Contract status after this disposition: `PASSIVE_TIME_WITNESS_RUNTIME_CANDIDATE_V2_STATIC_GATE_FAILED_REMEDIATION_REQUIRED`

## Verifier

- Path: `scripts/verify_passive_time_witness_runtime_candidate_v2_static.sh`
- SHA-256: `879dcac237717e84043cac5cdcd89c8c546f568c48e4ec7c897dc5c15cfbf87f`
- Mode: `755`
- Bash syntax (`bash -n`): PASS

## Frozen identities tested and rejected

- Generator path: `scripts/prepare_passive_time_witness_runtime_candidate_v2.sh`
- Generator SHA-256: `504069a6fa6889a998c1b98ea5211c78c2a12006f7f6ead0bc4a060175e22a3b`
- Candidate SHA-256: `b541d22ecd7a94b2acb1f85bb9478453b090ab11e19fb5b667eed1b588a27322`
- Observation window: 70 seconds (frozen under D-062)

These are the identities that were tested and rejected. They remain the frozen D-062 identities and are not authorized for runtime.

## Retained evidence

- Retained log path: `artifacts/wp4-passive-time-witness-runtime-candidate-v2-static-gate-failure-20260729T051122Z.log`
- Retained log SHA-256: `753bcc17a6b3cda9686f76b7120edc588da6b22cdc28757d8af942aba6fab87f`
- Retained log is byte-identical to the raw source `/tmp/d063c-static-gate-20260729T051122Z.log`.
- The raw source was not rewritten or normalized.

## Exact controlled-execution metrics

- verifier execution completed as designed
- verifier rc: 1
- Docker guard log bytes: 0
- final PASS marker count: 0
- step 8 reached count: 0
- writable NOS3 rejection count: 1
- failure occurred at step: 6
- no real Docker invocation occurred
- no pinned-image compile was attempted
- no NOS3 runtime was launched
- no runtime candidate post-gate path was executed
- no diagnostic or baseline was executed
- no retained evidence was modified
- runtime authorization remains: false
- authorized runtime attempts remain: 0

## Checks that passed through step 5

- [1/14] Required files + contract JSON: contract JSON valid; required files present.
- [2/14] Fail-closed contract pre-gate validation: CONTRACT_PRE_GATE_OK; contract pre-gate state exactly matches required D-063A inputs.
- [3/14] Exact frozen source/artifact binding: generator/witness/validator/shim SHA-256 match frozen identities; contract D-062 generator/candidate/duration binding matches frozen values; CONTRACT_D062_BINDING_OK.
- [4/14] Syntax + deterministic double emission: syntax valid (verifier, generator, validator); double emission byte-identical; both candidate SHA match frozen b541d22e....
- [5/14] Candidate structural validation: CANDIDATE_STRUCTURE_OK; candidate structure validated (70s lock, gate-before-docker, cleanup/trap ordering, no prune, 10x retries, sibling roots, no policy timing).

## Exact step-6 failure

- Step: [6/14] Topology + containment + claim validation.
- Failure reason: write-capable mount of pinned NOS3 source (source=$NOS3 -> /work/nos3) is prohibited; must be explicitly read-only: `--mount "type=bind,source=$NOS3,target=/work/nos3"`.
- Verifier emitted: `V2_STATIC_VERIFICATION_FAILED: topology/containment/claim validation failed`.

## Why writable pinned-source capability is rejected

The static gate rejects any write-capable bind of the pinned NOS3 source tree regardless of whether any observed command expressly writes through the mount. The capability itself is the hazard: a write-capable bind of `$NOS3` onto `/work/nos3` permits mutation of the pinned source under a future or altered command path that the static verifier cannot exhaustively enumerate. Static verification can only reject the capability, not rely on the absence of an explicit write observed in the current candidate command set. Therefore the gate fails closed on capability, not on observed behavior, and the candidate is rejected even though no command in the current candidate explicitly writes through the mount.

## No runtime execution

- No real Docker invocation occurred (Docker guard log bytes=0).
- No NOS3 runtime was launched.
- No runtime candidate post-gate path was executed.
- No diagnostic or baseline was executed.
- The runtime candidate was emitted only to temporary `mktemp` review directories and was not executed; its frozen SHA-256 remained unchanged.

## No retained-evidence mutation

- No retained evidence was modified during this disposition.
- The only new artifact is the byte-identical retained copy of the raw verifier log.

## No scientific outcome

- This disposition records a static-gate failure and governance disposition only. It makes no scientific, mission-impact, generic-radio-defect, CryptoLib, or SDLS claim.

## D-064 blocked

D-064 remains blocked. D-064 may only consider one bounded passive telemetry attempt after a separately governed remediated candidate passes a separate static verification. This disposition does not authorize D-064, does not authorize any runtime attempt, and does not authorize any diagnostic or baseline.

## Remediation required in a separate future phase

The frozen v2 candidate failed its static gate. A later separately governed remediation phase must modify the generator, emit a new deterministic candidate, establish new generator/candidate hashes, and rerun static verification. That remediation is not performed in this disposition. A remediation phase identifier is not invented here because existing project conventions do not define one for this remediation step.

## Contract gate fields after this disposition

- `gate.passive_time_witness_runtime_candidate_v2_static_verification`: `FAIL`
- `gate.accepted_runtime_entrypoint_v2_sha256`: `""` (unchanged, empty)
- `gate.diagnostic_runtime_authorized`: `false`
- `gate.diagnostic_runtime_attempts_authorized`: `0`
- `gate.baseline_run_1_authorized`: `false`
- `gate.baseline_run_2_authorized`: `false`
- `gate.event_injection_authorized`: `false`
- Historical D-060 accepted entrypoint hash `gate.accepted_runtime_entrypoint_sha256` preserved unchanged: `0fe76023ccc968f0aa12fa27db0a5ae21597b03e53066cebb5cf56bc29572259`
- Frozen D-062 generator and candidate identities preserved as the identities that were tested and rejected.
- All top-level scientific, command-transmission, baseline, event-injection, and cryptographic-semantics permissions remain `false`.
