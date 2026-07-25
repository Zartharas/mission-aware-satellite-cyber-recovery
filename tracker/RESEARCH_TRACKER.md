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
| WP4 | Testbed selection and architecture | In progress | Exact toolchain locks; successful isolated 21-component runtime preflight; locked SAMPLE no-op command, transport, telemetry assertion, and evidence-separation design | Implement and reproduce the complete benign command/telemetry baseline twice |
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
- [x] Isolate the remaining CryptoLib exit to its radio transport-readiness interval
- [x] Add explicit TCP selection, radio port-8010 readiness verification, interactive CryptoLib stdin, and recorded loopback ground destination
- [x] Confirm the radio constructor remained blocked on the unavailable 42 port-4286 truth provider path
- [x] Identify the omitted port-9999 truth client as an earlier pinned 42 IPC dependency
- [x] Add an internal byte-count-only truth sink without COSMOS, host ports, event injection, or policy visibility
- [x] Create the liveness CSV before startup so readiness-gate failures retain a valid evidence structure
- [x] Pass the scoped 21-component runtime preflight in run `20260725T201918Z`
- [x] Verify truth-sink readiness, radio port-8010 readiness, radio-to-42 connectivity, and radio/CryptoLib TCP establishment
- [x] Verify all startup and observation liveness rows remained `running:0`
- [x] Verify no host ports, Docker-socket mounts, residual labeled containers, or residual labeled networks
- [x] Commit the compact runtime-preflight lock without committing large runtime logs
- [x] Select `SAMPLE_NOOP_CC` as the single benign baseline command
- [x] Lock the command message ID, function code, telemetry packet, required counters, and 30-second assertion window
- [x] Lock the internal ground-probe transport path over CryptoLib UDP 6010/6011 and radio TCP 8010/8011
- [x] Define immutable ground-evidence and policy-visible evidence boundaries
- [x] Commit the machine-readable benign-baseline contract

## Immediate tasks

- [x] Pull the internal truth-stream compatibility revision
- [x] Run `bash -n scripts/run_nominal_runtime_preflight.sh`
- [x] Run `DURATION_SECONDS=60 STARTUP_GRACE_SECONDS=30 bash scripts/run_nominal_runtime_preflight.sh`
- [x] Verify `truth_sink_connection=ready` and `radio_tcp_8010_listener=ready` in the manifest
- [x] Review the 21-component liveness record, truth-sink byte counts, 42/radio/CryptoLib logs, network inspection, and cleanup evidence
- [x] Define the controlled ground command and telemetry endpoint for the complete nominal baseline
- [x] Select the exact benign cFE command and deterministic command-acceptance assertion
- [x] Define required telemetry fields, source identities, and timing tolerances
- [x] Define the evidence-separation contract
- [ ] Implement and self-test the cFS command checksum and packet builder
- [ ] Implement the internal ground probe with UDP 6010 transmit and UDP 6011 receive
- [ ] Implement deterministic `SAMPLE_HK_TLM` parsing and pre-command stability checks
- [ ] Implement independent immutable-ground and policy-visible evidence files and hashes
- [ ] Implement a bounded benign-baseline runner with no event-injection capability
- [ ] Execute the first clean benign baseline run
- [ ] Execute the second clean benign baseline run
- [ ] Compare the two clean-run manifests and reject unexplained variation before event work
- [ ] Audit author, venue, DOI, publication status, and access terms for all 30 literature entries
- [ ] Complete license verification for CuCD-ID and AegisSat
- [ ] Obtain institutional determination before any interview-data reanalysis or human study

## Final candidate novelty statement

This study introduces a reproducible software-in-the-loop experimental method for comparing satellite cyber-containment and trusted-recovery policies across mission states, telemetry-evidence conditions, and intermittent ground contact, while measuring adversary containment, mission continuity, safety-invariant preservation, and time to verified trusted recovery.

## Gate 3 status

WP4 has passed the host-runtime, schema, NOS3 source, recursive-submodule, cFE/OSAL/PSP, 42 source/build, container-digest, network-disabled compilation, and scoped runtime-preflight controls. Gate 3B Phase 1 is complete, and the Phase 2 benign-baseline design is locked. Phase 2 implementation and two clean passes remain pending. Event injection remains blocked until both baseline runs pass and immutable ground-truth evidence is demonstrably separated from policy-visible evidence.
