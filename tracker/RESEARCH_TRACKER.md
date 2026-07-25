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
| WP4 | Testbed selection and architecture | In progress | Exact toolchain locks; successful 21-component runtime preflight; three invalid baseline attempts retained; CI_LAB/TO_LAB interface mapped; standalone CryptoLib packet-layer incompatibility identified; allowlisted plaintext-relay baseline implemented | Pass the plaintext-relay static gate, then obtain the first accepted benign baseline pass |
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

- [x] Build proposition-to-variable-to-metric-falsification traceability table
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
- [x] Select `SAMPLE_NOOP_CC` as the single measured benign command
- [x] Lock the measured-command message ID, function code, telemetry packet, counters, and 30-second assertion window
- [x] Define immutable-ground and policy-visible evidence boundaries
- [x] Commit the machine-readable benign-baseline contract
- [x] Implement the pinned cFE XOR checksum and fixed `SAMPLE_NOOP_CC` packet vector
- [x] Implement deterministic `SAMPLE_HK_TLM` parsing using the pinned 12-byte cFE telemetry header layout
- [x] Implement separate immutable-ground and policy-visible evidence files with independent SHA-256 manifests
- [x] Add and pass host and network-disabled pinned-container probe self-tests
- [x] Implement the bounded 22-component benign-baseline runner with no event-injection path
- [x] Add and pass the initial static runner verification gate
- [x] Execute full baseline attempt `20260725T212156Z` and classify it `RUN_INVALID`
- [x] Execute setup-gated attempt `20260725T215659Z` and classify it `RUN_INVALID`
- [x] Verify both early invalid attempts preserved runtime health, cleanup, evidence hashing, and zero measured-command transmissions
- [x] Run read-only hop analysis on retained run `20260725T215659Z`
- [x] Confirm the runtime loads `CI_LAB_APP` and `TO_LAB_APP`, not the assumed CFS_CI/CFS_TO interface
- [x] Confirm `CI_LAB` listens on UDP port `5012`
- [x] Confirm `SC_RTS001` automatically enables `TO_LAB` to destination `active-gs`
- [x] Supersede the explicit ground `TO_ENABLE_OUTPUT` setup-command design
- [x] Add a measurement-only ground probe with exactly one possible ground transmission
- [x] Add a hashed runtime configuration copy that changes only the radio CI destination from `5010` to `5012`
- [x] Treat the pinned NOS3 simulator configuration as opaque XML-like text and prove a one-character runtime diff
- [x] Assign the internal `active-gs` alias to the radio container for the TO_LAB downlink
- [x] Pass the interface-corrected text-safe static verification gate
- [x] Execute interface-corrected attempt `20260725T230542Z` and classify it `RUN_INVALID`
- [x] Verify run `20260725T230542Z` applied the 5012 correction, resolved `active-gs`, initialized CI_LAB/TO_LAB and radio paths, retained full liveness, cleaned up, and validated both evidence trees
- [x] Confirm SAMPLE housekeeping is scheduled every five seconds and included in the TO_LAB subscription table
- [x] Confirm TO_LAB emits plain cFS telemetry packets while the pinned standalone CryptoLib TM path requires transfer-frame security processing
- [x] Confirm the pinned standalone CryptoLib TC path produces a protected transfer frame while CI_LAB expects a plain cFS command packet
- [x] Record that the standalone CryptoLib program is not a transparent packet relay for this nominal CI_LAB/TO_LAB gate
- [x] Defer CryptoLib and SDLS semantics to a separate compatible flight-side integration gate
- [x] Implement an internal plaintext UDP relay that allowlists only the frozen eight-byte `SAMPLE_NOOP_CC` and permits at most one command
- [x] Require independent relay evidence of one command receive, one matching command forward, telemetry forwarding, and zero relay-invalid events
- [x] Preserve the existing radio aliases and ports through a compatibility alias explicitly labeled as not CryptoLib
- [x] Add the plaintext-relay runner, contract version `0.6.0`, transport addendum, invalid-run lock, and network-disabled verification gate

## Immediate tasks

- [ ] Pull the plaintext-relay baseline revision
- [ ] Validate `configs/benign-baseline-contract.json`
- [ ] Compile `benign_ground_probe_measurement.py`, `prepare_runtime_radio_config.py`, and `benign_plaintext_transport_relay.py`
- [ ] Syntax-check `run_benign_baseline_plaintext_relay.sh` and `verify_benign_baseline_plaintext_relay.sh`
- [ ] Run `bash scripts/verify_benign_baseline_plaintext_relay.sh`
- [ ] Confirm all host and network-disabled self-tests and `BENIGN_BASELINE_PLAINTEXT_RELAY_VERIFICATION_STATUS=PASS`
- [ ] Execute the first plaintext-relay benign baseline only after the complete static gate passes
- [ ] Review relay command/telemetry accounting, counter transition, liveness, cleanup, runtime configuration hash, and separated evidence hashes
- [ ] Accept or reject the first clean baseline run before attempting run 2
- [ ] Execute the second clean benign baseline run only after run 1 acceptance
- [ ] Compare the two clean-run manifests and reject unexplained variation before event work
- [ ] Design a separate compatible CryptoLib/SDLS integration gate without conflating it with the nominal cFS packet baseline
- [ ] Audit author, venue, DOI, publication status, and access terms for all 30 literature entries
- [ ] Complete license verification for CuCD-ID and AegisSat
- [ ] Obtain institutional determination before any interview-data reanalysis or human study

## Final candidate novelty statement

This study introduces a reproducible software-in-the-loop experimental method for comparing satellite cyber-containment and trusted-recovery policies across mission states, telemetry-evidence conditions, and intermittent ground contact, while measuring adversary containment, mission continuity, safety-invariant preservation, and time to verified trusted recovery.

## Gate 3 status

WP4 has passed the host-runtime, schema, NOS3 source, recursive-submodule, cFE/OSAL/PSP, 42 source/build, container-digest, network-disabled compilation, scoped runtime-preflight, ground-probe, runtime-configuration, and prior runner static controls. Three full baseline attempts are retained as `RUN_INVALID`; run `20260725T230542Z` proved the corrected CI_LAB/TO_LAB and radio interface was active, but zero telemetry reached the probe and zero measured commands were transmitted. Source-level review established that the plain cFS packets used by CI_LAB/TO_LAB are incompatible with the pinned standalone CryptoLib transfer-frame processing path. Contract version 0.6.0 therefore uses an allowlisted internal plaintext UDP relay for the nominal two-run command/telemetry gate and explicitly defers all CryptoLib/SDLS claims to a separate compatible integration gate. Event injection remains blocked until the plaintext-relay static gate passes, two benign baselines are accepted, cross-run structural comparison is approved, and immutable-ground evidence remains demonstrably separate from policy-visible evidence.
