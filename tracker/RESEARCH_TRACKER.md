# Research Tracker

Last updated: 2026-07-29

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
| WP4 | Testbed selection and architecture | In progress | Exact toolchain locks; successful runtime preflight; retained diagnostics and metadata audit complete; D-060 static baseline accepted; D-061 runtime-control design accepted; D-062 implemented the versioned v2 generator (`504069a6fa68...`) and deterministic candidate (`b541d22ecd7a...`) with a frozen 70-second observation, fail-closed self-hash authorization gate, bounded reverse-order cleanup, fresh separated evidence roots, and no runtime authorization | Execute and review the separate fail-closed v2 static gate under D-063 without authorizing runtime |
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

- [x] Implement the versioned v2 passive time-witness runtime-candidate generator under D-062 without executing the candidate
- [x] Freeze the passive observation duration at exactly 70 seconds using the retained UDP span, configured 10-ms tick interval, 1.25 safety factor, and ceiling-to-next-10-seconds rule
- [x] Add fail-closed candidate self-hash authorization, all four signal/exit traps, bounded reverse-order cleanup, exact labeled-network removal, and ten post-cleanup zero-resource assertions
- [x] Validate deterministic double emission, Bash syntax, current-contract rc=1 closed-gate behavior, zero fake-Docker invocation, and unchanged retained evidence
- [x] Record D-062 as implementation-only acceptance; retain D-063 as the separate v2 static gate and D-064 as the sole future runtime-authorization disposition

## Immediate tasks

- [x] Review and disposition the passive time-witness static-verifier result under D-060 (D-060 governance-accepted the remediated static gate on 2026-07-28 and locked the implementation and deterministic runtime-candidate hashes; the static gate is accepted and the runtime remains unauthorized)
- [x] Keep all diagnostic runtime, baseline, command, event-injection, scientific-outcome, and CryptoLib/SDLS authorizations closed until the static-gate result is reviewed and separately accepted under D-060 (D-060 accepted the static gate; all runtime/scientific authorizations remain false or zero)
- [x] Lock the bounded runtime-control remediation design under D-061 (D-061 accepted the design requiring a versioned replacement candidate with an internally enforced deterministic observation bound and complete fail-closed cleanup; the current candidate 0fe76023... is a static-baseline identity only and is runtime-authorization-ineligible; contract advanced to 0.4.7)
- [x] Implement the versioned bounded runtime candidate (`prepare_passive_time_witness_runtime_candidate_v2.sh`) and cleanup controls under D-062 without authorizing runtime (completed under contract 0.4.8; observation duration frozen at 70 seconds; generator 504069a6fa68...; candidate b541d22ecd7a...)
- [x] Execute and review the separate fail-closed v2 static gate under D-063, binding any PASS to the exact generator and candidate hashes; runtime remains unauthorized (D-063 executed on 2026-07-29: verifier 879dcac2... rc=1; frozen v2 candidate b541d22ecd7a... FAILED at step 6 because it permits a write-capable bind of pinned $NOS3 -> /work/nos3 that is not explicitly read-only; no real Docker, no runtime, no evidence mutation; contract advanced to 0.4.9)
- [ ] Separately governed generator remediation: modify the generator, emit a new deterministic candidate, establish new generator/candidate hashes, and rerun static verification before D-064 may consider one bounded passive telemetry attempt (runtime remains unauthorized)
- [x] Lock the v3 manifest-seed design under D-063R1 (PINNED_IMAGE_BASE_PLUS_CANONICAL_MANIFEST_BOUND_PRIVATE_HOST_WORKSPACES): design and governance record only; no implementation, no runtime; contract advanced to 0.4.10; D-064 BLOCKED (D-063R1 governance_date=2026-07-29; design record SHA-256 c089ffac...; design lock SHA-256 cebd5933...; pre-write audit simulator 27/25, cFS 1370/1365, config 36/36, 0 unsupported/escaping/hardlink/unclassified; 18 private workspaces; image-owned files remain in-image; the canonical manifest model binds the host seed; stale state MUST_BE_ABSENT_AT_START; runtime compatibility UNPROVEN and the design requires every runtime write to be contained within a private run-scoped workspace; implementation, runtime containment, and runtime compatibility remain UNPROVEN; historical v2/D-060 identities unchanged)
- [ ] Separately governed v3 implementation: create a new versioned generator, deterministic candidate, canonical runtime-material manifest, and versioned static verifier; pass separate static verification before D-064 may consider one bounded passive telemetry attempt; runtime remains unauthorized
- [ ] Design a separate compatible CryptoLib/SDLS integration gate without conflating it with the nominal cFS packet baseline
- [ ] Audit author, venue, DOI, publication status, and access terms for all 30 literature entries
- [ ] Complete license verification for CuCD-ID and AegisSat
- [ ] Obtain institutional determination before any interview-data reanalysis or human study

## Blocked

D-060 (2026-07-28) accepted the historical passive time-witness static baseline; D-061 (2026-07-28) accepted the bounded runtime-control design; D-062 (2026-07-29) accepted the versioned v2 implementation only; and D-063 (2026-07-29) executed the fail-closed v2 static gate and recorded a CANDIDATE FAIL. Contract 0.4.9 records that the frozen v2 candidate b541d22ecd7a... failed the static gate at step 6 because it permits a write-capable bind of the pinned NOS3 source (source=$NOS3 -> /work/nos3) that is not explicitly read-only; the gate rejects the write capability even though no observed command explicitly writes through the mount. Verifier 879dcac2... returned rc=1, Docker guard log bytes=0, no real Docker invocation occurred, no pinned-image compile was attempted, no NOS3 runtime was launched, no runtime candidate post-gate path was executed, no diagnostic or baseline was executed, and no retained evidence was modified. Runtime authorization remains false with zero authorized attempts; both baseline authorizations remain false; event injection authorization remains false; all top-level scientific, command-transmission, baseline, event-injection, and cryptographic-semantics permissions remain false; the historical D-060 accepted entrypoint hash is preserved unchanged; and the frozen D-062 generator and candidate identities are preserved as the identities that were tested and rejected. D-064 is BLOCKED: a separately governed remediation phase must modify the generator, emit a new deterministic candidate, establish new generator/candidate hashes, and pass a separate static verification before D-064 may consider one bounded passive telemetry attempt. The following remain blocked pending that separate remediation and a future D-064 authorization:

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

WP4 has passed the host-runtime, schema, NOS3 source, recursive-submodule, cFE/OSAL/PSP, 42 source/build, container-digest, network-disabled compilation, scoped runtime-preflight, ground-probe, runtime-configuration, historical runner, plaintext-relay, functional-readiness, telemetry-only diagnostic, retained-run-analysis, TO_LAB static-audit, corrected port-bridge, radio-observability, retained-liveness, metadata-shim component, metadata-runtime wrapper, retained metadata-audit, and corrected time-tick-parser controls. Four benign baseline attempts and two telemetry-only diagnostics remain invalid infrastructure runs; one bounded metadata-only diagnostic completed as infrastructure evidence, and none produced a measured command or scientific outcome. Run `20260726T192902Z` confirms 1,061 generic-radio UDP `5011` receives and zero successful or failed UDP `8011` send attempts, but retained evidence contains only authoritative TimeDriver tick `0` and therefore does not prove time progression or callback invocation after ingress. Decision D-059 and contract `0.4.5` recorded a passive NOS Engine time-witness implementation candidate (script set and SHA-256 hashes). The original Part 5 technical static verifier (superseded hash 0f4db49582d8cacab1fefe7919af7a104bda5360ae1d82d4901d5396a13a52d3) returned PASS but was later found to permit a deferred pinned-image compile and C++ witness --self-test PASS path; Part 7D remediated that fail-closed defect and the current remediated verifier (hash 947961bfcbee386553c472fef1b2f9b25fa5cf03f1120e750085c9dd6e96ad9f) returned PASS in Part 7D. D-060 (2026-07-28) governance-accepted that remediated static gate, locked the reviewed implementation and deterministic runtime-candidate hashes, and advanced the contract to `0.4.6` (`PASSIVE_TIME_WITNESS_STATIC_GATE_ACCEPTED_RUNTIME_NOT_AUTHORIZED`). Every runtime, baseline, command, event-injection, scientific-outcome, and CryptoLib/SDLS gate remains closed. D-061 (2026-07-28) accepted the runtime-control remediation design and advanced the contract to `0.4.7` (`PASSIVE_TIME_WITNESS_RUNTIME_CONTROL_DESIGN_LOCKED_IMPLEMENTATION_PENDING`): the current candidate `0fe76023...` is a D-060 static-baseline identity only, is runtime-authorization-ineligible in its present form (no deterministic observation duration, no internal teardown path), and must be replaced by a versioned v2 candidate and generator. The phase separation is frozen as D-062 (implement v2; runtime unauthorized), D-063 (fail-closed static gate for v2; runtime unauthorized), and D-064 (sole authorization disposition, only after D-063 is accepted). D-062 (2026-07-29) implemented the versioned v2 generator and deterministic candidate, froze the observation at 70 seconds, and recorded complete fail-closed cleanup and evidence controls in contract `0.4.8` (`PASSIVE_TIME_WITNESS_RUNTIME_CONTROL_V2_IMPLEMENTED_STATIC_GATE_PENDING`). The generator SHA-256 is `504069a6fa6889a998c1b98ea5211c78c2a12006f7f6ead0bc4a060175e22a3b` and the proposed candidate SHA-256 is `b541d22ecd7a94b2acb1f85bb9478453b090ab11e19fb5b667eed1b588a27322`. The historical D-060 identity `0fe76023ccc968f0aa12fa27db0a5ae21597b03e53066cebb5cf56bc29572259` remains unchanged in `gate.accepted_runtime_entrypoint_sha256`; the new `gate.accepted_runtime_entrypoint_v2_sha256` is empty and the v2 static gate is PENDING. No runtime, Docker activity, candidate execution, or retained-evidence mutation occurred during D-062. D-063 (2026-07-29) executed the fail-closed v2 static gate. The static verifier (SHA-256 879dcac237717e84043cac5cdcd89c8c546f568c48e4ec7c897dc5c15cfbf87f) returned rc=1. The frozen v2 candidate b541d22ecd7a94b2acb1f85bb9478453b090ab11e19fb5b667eed1b588a27322 FAILED at step 6 because it permits a write-capable bind of the pinned NOS3 source (source=$NOS3 -> /work/nos3) that is not explicitly read-only; the gate rejects the write capability even though no observed command explicitly writes through the mount. Docker guard log bytes=0; no real Docker invocation occurred; no pinned-image compile was attempted; no NOS3 runtime was launched; no runtime candidate post-gate path was executed; no diagnostic or baseline was executed; no retained evidence was modified. Contract 0.4.9 records V2_STATIC_GATE_FAILED_REMEDIATION_REQUIRED; gate.passive_time_witness_runtime_candidate_v2_static_verification=FAIL; gate.accepted_runtime_entrypoint_v2_sha256 remains empty; diagnostic runtime authorization remains false with zero authorized attempts; both baseline authorizations remain false; event injection authorization remains false; all top-level scientific, command-transmission, baseline, event-injection, and cryptographic-semantics permissions remain false; the historical D-060 accepted entrypoint hash 0fe76023... is preserved unchanged; and the frozen D-062 generator (504069a6fa68...) and candidate (b541d22ecd7a...) identities are preserved as the identities that were tested and rejected. The retained log is artifacts/wp4-passive-time-witness-runtime-candidate-v2-static-gate-failure-20260729T051122Z.log (SHA-256 753bcc17a6b3cda9686f76b7120edc588da6b22cdc28757d8af942aba6fab87f). D-064 is BLOCKED. The next acceptance gate is: a separately governed generator remediation that modifies the generator, emits a new deterministic candidate, establishes new generator/candidate hashes, and passes a separate static verification, after which D-064 alone may consider one bounded passive telemetry attempt; runtime remains unauthorized.

D-063R1 (2026-07-29) locked the v3 manifest-seed design as a design and governance record only, advancing contract to 0.4.10 (PASSIVE_TIME_WITNESS_RUNTIME_CANDIDATE_V3_MANIFEST_SEED_DESIGN_LOCKED_IMPLEMENTATION_PENDING). The architecture is PINNED_IMAGE_BASE_PLUS_CANONICAL_MANIFEST_BOUND_PRIVATE_HOST_WORKSPACES: the pinned image remains the immutable execution base and image-owned files remain in the image (never copied into the host seed); only external/nos3 material is represented by the canonical manifest model (normalized paths, entry types, modes, regular-file sizes and SHA-256 values, directory entries, explicit exclusions, and deterministic serialization) bound by the SHA-256 of the canonical manifest; each of 18 components (NOS Engine 1, TimeDriver 1, 14 hardware simulators, bridge 1, cFS 1) receives a private run-scoped writable workspace mounted at /work/nos3 from a private workspace never external/nos3. Pre-write audit found simulator seed 27 raw / 25 included, cFS seed 1370 raw / 1365 included, config seed 36 raw / 36 included, with 0 symlinks, 0 escaping symlinks, 0 unsupported filesystem objects, 0 hard-link aliases, and 0 unclassified source paths. Plugin mapping: 14 hardware simulator instances, 12 distinct hardware plugin files, 13 distinct simulator plugin files including TimeDriver. Stale runtime state is MUST_BE_ABSENT_AT_START by source evidence. The design creates no v3 generator, candidate, verifier, materializer, or manifest; historical v2 generator (504069a6fa68...), rejected candidate (b541d22ecd7a...), D-063 verifier (879dcac2...), D-063 retained log (753bcc17...), and D-060 accepted entrypoint (0fe76023...) remain unchanged. gate.passive_time_witness_runtime_candidate_v3_static_verification=PENDING; gate.accepted_runtime_entrypoint_v3_sha256 remains empty; runtime authorization remains false with zero authorized attempts; all top-level permissions remain false; D-064 remains BLOCKED; the next decision is SEPARATELY_GOVERNED_V3_IMPLEMENTATION_REQUIRED_BEFORE_D064. Runtime compatibility remains UNPROVEN. The design requires every runtime write to be contained within a private run-scoped workspace; implementation correctness, runtime containment, and runtime compatibility remain UNPROVEN until a separately governed implementation and static verification are completed; no runtime is authorized. This record makes no scientific, mission-impact, generic-radio-defect, CryptoLib, or SDLS claim.
