# Testbed and Reproducibility

## Role in the study

The testbed is infrastructure used to create controlled, repeatable observations. It is not itself the paper's principal contribution.

The selected environment is a Docker-first headless NOS3/cFS software-in-the-loop testbed with Fortytwo retained as a pinned dependency.

## Retained reproducibility evidence

- `configs/toolchain-lock.json`
- `artifacts/nos3-submodule-lock.txt`
- `artifacts/fortytwo-lock.txt`
- `artifacts/nominal-build-lock.txt`
- `artifacts/nominal-runtime-preflight-lock.txt`

Reusable tooling:

- `scripts/prepare_nos3_candidate.sh`
- `scripts/prepare_42_candidate.sh`
- `scripts/build_nominal_nos3.sh`
- `scripts/run_nominal_runtime_preflight.sh`
- `scripts/cleanup_nominal_runtime.sh`
- `scripts/verify_testbed_runtime.sh`

## Accepted infrastructure result

The retained bounded runtime preflight established sufficient component liveness, internal-network isolation, host-port controls, Docker-socket exclusion, and cleanup behavior to proceed with event and policy development.

That result is infrastructure evidence only; it is not a cyber-response scientific outcome.

## Discontinued diagnostic branch

A later passive downlink/time-witness branch attempted to resolve a narrow NOS3 radio-observability question. The question is not necessary to evaluate the paper's mission-aware response and trusted-recovery hypotheses.

The final single-use V6 attempt was consumed on 2026-08-13 and failed closed before production runtime materialization because the dedicated materializer identity could not open its transaction executable. Docker/NOS3/Fortytwo scientific runtime did not begin and no scientific result was produced.

No successor D-064 attempt is required.

## WP4 disposition

**WP4 complete.**

Future work will modify testbed infrastructure only when a concrete WP5-WP9 experiment requires it.

## Limitations

- software simulation is not flight hardware;
- modeled contact and subsystem behavior simplify real missions;
- conclusions are bounded to tested event/policy classes;
- synthetic scenarios do not estimate real-world attack prevalence;
- no live RF or operational satellite system is involved.
