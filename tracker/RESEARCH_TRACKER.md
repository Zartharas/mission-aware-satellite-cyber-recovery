# Research Tracker

Last updated: 2026-07-27

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
| WP4 | Testbed selection and architecture | In progress | Exact toolchain locks; successful runtime preflight; four invalid baseline attempts, two invalid telemetry-only diagnostics, and one completed metadata-only diagnostic retained; TO_LAB `5013` bridge, radio socket metadata wrapper, retained audit, and D-056 parser correction complete; passive time-witness design locked; D-059 implementation candidate (subscriber, trace validator, emit-only candidate generator, network-disabled static verifier) created; the original Part 5 technical static verifier returned PASS but was later found to permit a deferred compile/self-test PASS path, Part 7D remediated that fail-closed defect, and the current remediated verifier returned PASS in Part 7D; D-060 (2026-07-28) governance-accepted the remediated static gate and locked the implementation and deterministic runtime-candidate hashes while retaining a closed runtime gate | Propose a separately governed decision for one passive telemetry runtime attempt |
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
- [x] Pass the plaintext-relay host and pinned-image network-disabled static verification gate
- [x] Record the plaintext-relay static gate lock and decision D-038
- [x] Execute plaintext-relay attempt `20260726T001052Z` and classify it `RUN_INVALID`
- [x] Identify the generic-radio hostname-resolution log as a logger-only readiness heuristic rather than proof of functional telemetry flow
- [x] Replace the logger-only marker with an observed `PLAINTEXT_RELAY_TELEMETRY_FORWARDED` event after TO_LAB activation
- [x] Pass and accept the contract-0.6.1 functional-readiness static verification gate
- [x] Execute corrected plaintext-relay rerun `20260726T005937Z` and classify it `RUN_INVALID`
- [x] Fail-close benign-baseline contract version `0.6.2` and block every further baseline execution
- [x] Add a telemetry-only proxy/sink diagnostic with no command source
- [x] Pass host and network-disabled static verification for the diagnostic witness and wrappers
- [x] Execute telemetry-only diagnostic `20260726T021807Z` and classify it `DOWNLINK_DIAGNOSTIC_INVALID`
- [x] Confirm both witnesses and all runtime components remained live and zero commands were possible or transmitted
- [x] Confirm the active-gs witness on UDP `5011` received zero packets and the radio queue was not evaluated
- [x] Identify and retain the empty policy-visible manifest defect without retroactively changing the run
- [x] Run the retained diagnostic analyzer and close the one-run authorization
- [x] Audit the pinned TO_LAB source, subscription table, schedule table, and built table artifact without launching Docker
- [x] Confirm TO_LAB was compiled to UDP `5013` while generic-radio listens for FSW telemetry on UDP `5011`
- [x] Reclassify the prior witness result as a wrong-port observation rather than evidence that TO_LAB produced no packets
- [x] Record the direct port mismatch in audit lock and decision D-045
- [x] Define contract `0.2.0` for an `active-gs:5013` byte-preserving proxy to `radio-sim:5011`
- [x] Add a non-sensitive policy-visible `scope.json` requirement and zero-entry manifest rejection
- [x] Add the corrected overlay and dedicated static verifier without authorizing runtime
- [x] Pass the corrected port-correction static verification gate
- [x] Seal the static gate in `artifacts/downlink-port-correction-static-gate-lock.txt`
- [x] Accept decision D-047 and authorize exactly one telemetry-only port-correction runtime
- [x] Execute corrected telemetry-only run `20260726T165332Z` and classify it `DOWNLINK_DIAGNOSTIC_INVALID`
- [x] Confirm the `5013` proxy received and byte-preservingly forwarded 1,452 unique packets totaling 314,985 bytes to radio-sim UDP `5011`
- [x] Confirm the UDP `8011` egress witness remained empty at the final retained observation
- [x] Verify zero commands, clean teardown, valid evidence trees, and non-empty policy-visible scope evidence
- [x] Close the consumed corrected-runtime authorization in contract `0.3.0`
- [x] Record compact run lock and decisions D-048 and D-049
- [x] Add and run the read-only retained radio-queue and static observability audits
- [x] Distinguish the header-only liveness checkpoint CSV from the 22-container final Docker-inspect snapshot
- [x] Confirm metadata-only `LD_PRELOAD` interposition is feasible without source edits, packet capture, host networking, Docker-socket access, or commands
- [x] Implement the filtered radio socket metadata shim and deterministic loopback self-test
- [x] Pass the pinned-image, network-disabled shim static verification gate
- [x] Seal the shim gate in `artifacts/radio-socket-metadata-shim-static-gate-lock.txt`
- [x] Accept decision D-050 while keeping all NOS3 runtime integration blocked
- [x] Retain the v2 metadata-runtime invocation as a consumed fail-closed pre-runtime assertion failure with no Docker or NOS3 launch
- [x] Pass and accept the v3 mode-aware metadata-runtime wrapper static gate
- [x] Execute the single authorized v3 telemetry-only metadata diagnostic in run `20260726T192902Z`
- [x] Accept the retained metadata audit with 1,061 UDP `5011` receives, zero UDP `8011` send attempts, zero commands, valid evidence trees, and clean teardown
- [x] Separate the confirmed post-ingress/pre-egress transport observation from causal claims about time progression or callback behavior
- [x] Complete the D-055 read-only eligibility and callback-path audit
- [x] Correct the D-056 time-tick parser false positive and confirm that the retained log contains only authoritative tick `0`
- [x] Record that retained NOS Engine time progression and callback invocation after ingress remain unproven
- [x] Reconcile the primary tracker, work-package register, decision log, and contract through D-058
- [x] Lock the passive NOS Engine time-witness design without implementing or executing it
- [x] Accept decision D-059 and record the passive time-witness implementation candidate (script set and SHA-256 hashes) while retaining a closed runtime gate
- [x] Produce the Part 5 technical static-verifier result PASS for the passive time-witness static gate
- [x] Hold the technical static-verifier PASS for governance review under D-060 without accepting it
- [x] Identify the original Part 5 verifier's deferred pinned-image compile/C++ witness --self-test PASS path as a fail-closed defect (Part 7)
- [x] Remediate the verifier to fail closed unless the pinned-image compile and witness --self-test execute and pass (Part 7D, current hash 947961bfcbee386553c472fef1b2f9b25fa5cf03f1120e750085c9dd6e96ad9f)
- [x] Execute the remediated verifier in Part 7D and produce PASSIVE_NOS_ENGINE_TIME_WITNESS_SELF_TEST=PASS, PASSIVE_TIME_WITNESS_TRACE_VALIDATOR_SELF_TEST=PASS, PASSIVE_TIME_WITNESS_STATIC_VERIFICATION_STATUS=PASS, VERIFIER_RC=0
- [x] Hold both the original Part 5 technical PASS and the Part 7D remediated-verifier technical PASS for governance review under D-060 without accepting either

## Immediate tasks

- [x] Review and disposition the passive time-witness static-verifier result under D-060 (D-060 governance-accepted the remediated static gate on 2026-07-28 and locked the implementation and deterministic runtime-candidate hashes; the static gate is accepted and the runtime remains unauthorized)
- [x] Keep all diagnostic runtime, baseline, command, event-injection, scientific-outcome, and CryptoLib/SDLS authorizations closed until the static-gate result is reviewed and separately accepted under D-060 (D-060 accepted the static gate; all runtime/scientific authorizations remain false or zero)
- [ ] Propose a separately governed decision for exactly one passive telemetry runtime attempt (the D-060 static-gate acceptance does not authorize a runtime)
- [ ] Design a separate compatible CryptoLib/SDLS integration gate without conflating it with the nominal cFS packet baseline
- [ ] Audit author, venue, DOI, publication status, and access terms for all 30 literature entries
- [ ] Complete license verification for CuCD-ID and AegisSat
- [ ] Obtain institutional determination before any interview-data reanalysis or human study

## Blocked

D-060 (2026-07-28) governance-accepted the passive time-witness static gate and locked the implementation and runtime-candidate hashes while retaining a closed runtime-authorization gate. The following remain blocked pending a separately governed decision that explicitly authorizes a single passive telemetry runtime attempt:

- Runtime execution
- Telemetry diagnostic
- Benign baseline
- Command transmission
- Event injection
- Scientific outcome classification
- CryptoLib/SDLS conclusions

## Final candidate novelty statement

This study introduces a reproducible software-in-the-loop experimental method for comparing satellite cyber-containment and trusted-recovery policies across mission states, telemetry-evidence conditions, and intermittent ground contact, while measuring adversary containment, mission continuity, safety-invariant preservation, and time to verified trusted recovery.

## Gate 3 status

WP4 has passed the host-runtime, schema, NOS3 source, recursive-submodule, cFE/OSAL/PSP, 42 source/build, container-digest, network-disabled compilation, scoped runtime-preflight, ground-probe, runtime-configuration, historical runner, plaintext-relay, functional-readiness, telemetry-only diagnostic, retained-run-analysis, TO_LAB static-audit, corrected port-bridge, radio-observability, retained-liveness, metadata-shim component, metadata-runtime wrapper, retained metadata-audit, and corrected time-tick-parser controls. Four benign baseline attempts and two telemetry-only diagnostics remain invalid infrastructure runs; one bounded metadata-only diagnostic completed as infrastructure evidence, and none produced a measured command or scientific outcome. Run `20260726T192902Z` confirms 1,061 generic-radio UDP `5011` receives and zero successful or failed UDP `8011` send attempts, but retained evidence contains only authoritative TimeDriver tick `0` and therefore does not prove time progression or callback invocation after ingress. Decision D-059 and contract `0.4.5` recorded a passive NOS Engine time-witness implementation candidate (script set and SHA-256 hashes). The original Part 5 technical static verifier (superseded hash 0f4db49582d8cacab1fefe7919af7a104bda5360ae1d82d4901d5396a13a52d3) returned PASS but was later found to permit a deferred pinned-image compile and C++ witness --self-test PASS path; Part 7D remediated that fail-closed defect and the current remediated verifier (hash 947961bfcbee386553c472fef1b2f9b25fa5cf03f1120e750085c9dd6e96ad9f) returned PASS in Part 7D. D-060 (2026-07-28) governance-accepted that remediated static gate, locked the reviewed implementation and deterministic runtime-candidate hashes, and advanced the contract to `0.4.6` (`PASSIVE_TIME_WITNESS_STATIC_GATE_ACCEPTED_RUNTIME_NOT_AUTHORIZED`). Every runtime, baseline, command, event-injection, scientific-outcome, and CryptoLib/SDLS gate remains closed; the next task is a separately governed proposal for one passive telemetry runtime attempt.
