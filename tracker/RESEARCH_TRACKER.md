# Research Tracker

Last updated: 2026-07-25

## Status legend

- Not started
- In progress
- Blocked
- Ready for review
- Complete

## Work packages

| ID | Work package | Status | Current output | Next acceptance gate |
|---|---|---|---|---|
| WP0 | Research governance and workspace | Complete | Private GitHub repository, initial commit, data and legal controls | Maintain clean synchronized repository |
| WP1 | Literature and novelty validation | Ready for review | Two gap reviews, reviewer challenge, final novelty statement, and 30-source matrix | Citation/metadata audit and approval of final gap statement |
| WP2 | Theoretical and conceptual model | Ready for review | Mission Aware + FDIR + cyber-resilience/RMF/SPARTA structure; traceability and deterministic metric contract | Approve Gate 2 traceability and metric definitions |
| WP3 | Threat and mission model | Ready for review | Frozen boundaries, machine-readable model and run schema, red-team review, and Docker-specific ROE controls | Approve Gate 2 threat/mission model and ROE controls |
| WP4 | Testbed selection and architecture | In progress | Exact NOS3, cFE/OSAL/PSP, 42, and image locks; successful network-disabled builds; scoped project-labeled headless runtime preflight under validation | Pass the scoped runtime preflight, then reproduce the complete benign command/telemetry baseline twice |
| WP5 | Event-injection library | Not started | — | Each event deterministic and contained |
| WP6 | Response-policy implementation | Not started | — | Baseline policies pass unit and integration tests |
| WP7 | Trusted-recovery implementation | Not started | — | Recovery evidence checklist verified |
| WP8 | Pilot experiment | Not started | — | Variability and final design established |
| WP9 | Final experiment | Not started | — | Pre-registered campaign completed |
| WP10 | Analysis and manuscript | Not started | — | Reproducible tables, figures, and paper draft |
| WP11 | Artifact and responsible release | Not started | — | License, secrets, misuse, and reproducibility review passed |

## Completed setup and WP1 tasks

- [x] Create private GitHub repository
- [x] Push initial scaffold
- [x] Create research, legal, data, risk, and decision records
- [x] Complete first focused novelty review
- [x] Expand literature matrix from 12 to 22 sources
- [x] Flag CuCD-ID license discrepancy and place it on conditional hold
- [x] Expand literature matrix to 30 sources
- [x] Search adjacent cyber-physical attack-recovery and spacecraft fault-management literature
- [x] Conduct reviewer-style challenge of the novelty claim
- [x] Produce final defensible gap and falsification criteria
- [x] Finalize initial mission objectives and unacceptable losses
- [x] Freeze safety/trust invariants and trusted-recovery criteria
- [x] Freeze the minimum viable pilot boundary

## Completed WP2/WP3 tasks

- [x] Build proposition-to-variable-to-metric traceability table
- [x] Define a falsification condition for every proposition
- [x] Define deterministic primary metrics, raw inputs, zero-denominator rules, censoring, and terminal-state precedence
- [x] Create machine-readable mission/event/policy/contact/evidence catalog
- [x] Create JSON Schema for experiment-run records
- [x] Conduct independent red-team review of the threat and mission model
- [x] Separate immutable ground truth from policy-visible state
- [x] Treat safe mode as both a response and an adversarially inducible condition
- [x] Draft software-only laboratory Rules of Engagement
- [x] Add Docker-specific network-isolation and emergency-shutdown controls
- [x] Record Gate 2 decisions in the decision log

## Completed WP4 design and validation tasks

- [x] Verify host operating system, architecture, tools, and storage
- [x] Select Docker-first headless execution strategy
- [x] Select exact NOS3 candidate commit and container tag
- [x] Require the cFS revision pinned by NOS3 rather than a moving upstream branch
- [x] Create candidate toolchain lock
- [x] Map red-team requirements to the reference architecture
- [x] Create Docker runtime and internal-network verification script
- [x] Pass Docker daemon, linux/amd64, internal-network, and internet-blocking checks
- [x] Create exact-commit NOS3 checkout and recursive-submodule lock script
- [x] Initialize all recursive NOS3 submodules without drift
- [x] Record cFE, OSAL, PSP, application, simulator, and ground-software commits
- [x] Resolve and commit the NOS3 image digest
- [x] Add positive and negative experiment-schema fixtures
- [x] Pass local JSON Schema validation including rejection of stale trusted-recovery evidence
- [x] Add GitHub Actions validation for research configurations
- [x] Exclude generated runtime and incident evidence from Git
- [x] Define a controlled exact-resolution and build workflow for 42
- [x] Define a network-disabled controlled NOS3/cFS build gate
- [x] Define the two-run nominal baseline protocol
- [x] Resolve 42 to commit `eda252bf31f27850e867e698cfdd963e143ead1f`, build it, and commit its lock
- [x] Complete the clean network-disabled NOS3/cFS/simulator/CryptoLib build and commit its lock
- [x] Add project-scoped runtime cleanup and bounded internal-network preflight scripts
- [x] Document Gate 3B Phase 1 evidence and acceptance boundaries
- [x] Retain and classify failed compatibility runs as `RUN_INVALID`
- [x] Correct the 42 bind-mount layout
- [x] Replace the conflicting aggregate simulator process with individual simulator launches
- [x] Scope the infrastructure-only headless preflight to fourteen frozen-pilot hardware simulators
- [x] Record COSMOS-dependent truth streaming and camera payload validation as separate later dependencies
- [x] Correct the generic-radio hostname alias and normalize the container terminal environment

## Immediate tasks

- [x] Pull the repository changes containing the build-path fix
- [x] Run `bash scripts/prepare_42_candidate.sh`
- [x] Review and commit `artifacts/fortytwo-lock.txt`
- [x] Run `bash scripts/build_nominal_nos3.sh` from clean build state
- [x] Review and commit `artifacts/nominal-build-lock.txt`
- [x] Pull and run the initial Gate 3B Phase 1 runtime-preflight revisions
- [x] Review the retained `RUN_INVALID` manifests, liveness records, logs, network inspection, and cleanup evidence
- [ ] Pull the scoped headless preflight revision
- [ ] Run `bash -n scripts/run_nominal_runtime_preflight.sh`
- [ ] Run `DURATION_SECONDS=60 STARTUP_GRACE_SECONDS=30 bash scripts/run_nominal_runtime_preflight.sh`
- [ ] Review the runtime manifest, liveness record, component logs, network inspection, and cleanup evidence
- [ ] Pin or eliminate the ground-software dependency for the complete nominal baseline
- [ ] Define the exact benign cFE command and command-acceptance assertion
- [ ] Define required telemetry fields and timing tolerances
- [ ] Reproduce the complete nominal command and telemetry baseline twice from clean runtime state
- [ ] Verify separate immutable ground-truth and policy-visible logging paths
- [ ] Audit author, venue, DOI, publication status, and access terms for all 30 literature entries
- [ ] Complete license verification for CuCD-ID and AegisSat
- [ ] Obtain institutional determination before any interview-data reanalysis or human study

## Final candidate novelty statement

This study introduces a reproducible software-in-the-loop experimental method for comparing satellite cyber-containment and trusted-recovery policies across mission states, telemetry-evidence conditions, and intermittent ground contact, while measuring adversary containment, mission continuity, safety-invariant preservation, and time to verified trusted recovery.

## Gate 3 status

WP4 has passed the host-runtime, schema, NOS3 source, recursive-submodule, cFE/OSAL/PSP, 42 source/build, container-digest, and network-disabled compilation controls. Gate 3B Phase 1 remains in runtime compatibility validation. Event injection remains blocked until the scoped runtime preflight passes, the complete benign command/telemetry baseline passes twice, and ground-truth logging is demonstrably separated from policy-visible evidence.
