# Research Tracker

Last updated: 2026-08-08

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
| WP4 | Testbed selection and architecture | In progress | VR6 T063 source correction `89e34a6ae35e...` is independently accepted, published through PR #8, and merged on clean main at `c130306f37b6...`; aggregate complete production verifier executions remain `5`, and the active verifier remains at `0` production executions. A post-merge pre-production audit found one governance-only binding defect: production `IDC_VERIFIER_SELF` resolves the nested implementation `static_verifier.sha256`, which still held superseded `1a7db020a08b...` instead of active `89e34a6ae35e...`; therefore execution #6 was not started. VR7 repairs only that authoritative binding and records authorization for exactly one later production `--verify`; static verification remains PENDING, runtime false/0, D-064 BLOCKED, and verifier/generator/candidate bytes remain unchanged. | Independently review and publish the exact four-file VR7 governance binding repair before consuming the one authorized production static-verifier execution; no runtime authorization |
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

D-063R2 (2026-07-29) amends the D-063R1 v3 manifest-seed design as a governance-only correction, advancing contract to 0.4.11 (PASSIVE_TIME_WITNESS_RUNTIME_CANDIDATE_V3_MANIFEST_SEED_DESIGN_AMENDED_IMPLEMENTATION_PENDING). The historical D-063R1 record (SHA-256 c089ffacac68694de2d446acbd301d0a96bc270fa9d1042e7e4c2c6f5bdf2f14) and lock (SHA-256 cebd5933d2bea7246f2a4d14d0f1efacafcb4f20afa5b901ba505a9c2512263d) remain immutable and unchanged; D-063R2 does not erase or rewrite D-063R1. The amendment record is tracker/WP4_PASSIVE_TIME_WITNESS_RUNTIME_CANDIDATE_V3_MANIFEST_SEED_DESIGN_AMENDMENT_1_20260729.md (SHA-256 a6c6e158842dc1c9fac28570adef9501cdb611eb0217468e674a9d2efb1c84e8) and the amendment lock is artifacts/wp4-passive-time-witness-runtime-candidate-v3-manifest-seed-design-amendment-1-lock.txt (SHA-256 1d4d16c422f1dcf3a9162ae4535a2836c3edd46a5aa8ba3ee318915abb100bff). Corrected counts: simulator 27 raw / 25 included / 2 excluded / 54427517 bytes; cFS 1370 raw / 1361 included / 9 excluded / 45877946 bytes (the four data/owls/bundle/.goutputstream-* stale temporary files are exact exclusions based on exact byte duplication, no repository references, hidden temporary-style naming, and the presence of the intended duplicate file); configuration 36 raw / 36 included / 0 excluded / 190651 bytes; aggregate 1433 raw / 1422 manifest regular-file entries / 89 directory entries / 11 exact exclusions; 0 unsupported, 0 escaping symlinks, 0 hard-link aliases, 0 unclassified. Corrected byte calculations: 18 private workspaces = 971145735 bytes; Fortytwo scratch = 190651 bytes (separate, not inside private-workspace bytes); optional staging seed = 100496114 bytes; prelaunch without staging = 971336386; prelaunch with staging = 1071832500; recommended free space = 3215497500 (3 * max(prelaunch_without_staging, prelaunch_with_staging)). The canonical manifest model uses ensure_ascii=True, sort_keys=True, separators=(",", ":"), exactly one final LF, byte-encoded sort keys, str.casefold() with NFC/NFD collision guards, no internal manifest self-hash, and a detached manifest SHA-256 recorded in contract and lock. Eleven logical candidate dependencies, fourteen implementation/runtime identity controls (including baseline-contract SHA-256 86d365fe... and Fortytwo executable SHA-256 9c0062d2...), and seven governance-artifact identity categories are locked. The contract schema field passive_time_witness_runtime_candidate_v3_contract_schema=1 provides candidate compatibility independent of the mutable governance revision. The proposed_runtime_entrypoint_v3_sha256 field is distinct from and does not authorize the accepted_runtime_entrypoint_v3_sha256 field (empty until a separately governed static gate passes). Host-side authorization checks precede materialization; the runtime-material tool executes on the host; static verification invokes no real Docker; under the closed contract the candidate exits before materializer execution and fake Docker. A combined v3 implementation phase (contract 0.4.12, 11 files) with internal stop gates is required before a separately governed static-verification disposition (contract 0.4.13, 8 files). Implementation remains NOT_STARTED and unauthorized; static verification remains PENDING and unauthorized; runtime authorization remains false with zero authorized attempts; D-064 remains BLOCKED; all top-level permissions remain false; the next decision is SEPARATELY_GOVERNED_COMBINED_V3_IMPLEMENTATION_REQUIRED_BEFORE_STATIC_VERIFICATION. This amendment makes no scientific, mission-impact, generic-radio-defect, CryptoLib, or SDLS claim. A future static PASS may set D-064 to READY_FOR_SEPARATE_D064_CONSIDERATION but does not authorize D-064, runtime, or attempts; a separate explicit D-064 governance decision is required; runtime_authorized_after_static_pass=false and runtime_attempts_after_static_pass=0; a static FAIL keeps D-064 BLOCKED. Inventory raw counts (1433 aggregate) are 2026-07-29 amendment-time snapshots, not unconditional future gates; included entry count (1422), included bytes (100496114), and exact exclusion-record count (11) are future invariants; present exclusion count may range 0 to 11; future raw count = included manifest entries + present exact exclusions.

D-063R2-TM1 (2026-07-31) was approved as the WP4 Checkpoint 1 cleanup threat-model amendment (tracker/WP4_CHECKPOINT1_CLEANUP_THREAT_MODEL_AMENDMENT_20260731.md). Under D-063R2-TM1, cleanup assurance is now evaluated under an exclusive-writer operational precondition: during workspace materialization and failure cleanup, the retained authorized-root directory and every staging directory are required to be exclusively writable by the materializer's operating-system identity for the duration of the transaction. An impossible portable guarantee against same-authority concurrent basename replacement is not claimed; Checkpoint 1 does not claim protection against a concurrent hostile process that already possesses the same effective filesystem write authority and mutates a cleanup basename during the final unlink() or rmdir() syscall window, and that same-authority concurrent-mutation case is outside the Checkpoint 1 cleanup guarantee and applies only to cleanup-name removal. Descriptor-relative traversal, O_NOFOLLOW opens, device/inode continuity checks, retained directory descriptors, destination audits, and atomic no-replace publication remain required defense-in-depth and protect against symlink substitution, stale pathname use, accidental object replacement, unsupported destination objects, changes detected before the final removal or publication operation, and overwrite of a pre-existing final workspace. This limitation must not weaken source identity verification, manifest verification, destination completeness auditing, exclusion and deny-pattern enforcement, per-file no-replace publication, final workspace no-replace publication, or runtime authorization gates. D-064 must not authorize runtime until the operational environment proves the exclusive-writer prerequisite (the eight D-064 evidence requirements are recorded in the amendment), and a failure of any exclusive-writer prerequisite keeps runtime authorization false and D-064 BLOCKED. Implementation acceptance still requires a final bounded test-integrity review; the implementation tool identity remains 9c1b1e0abcb7e30df40df8c91c4ce9ec600571a575c68a26b978b5778075c15f and the manifest identity remains 5026176de3084c8015fd7f84827ce8a4e5d44df7e986bc142815eb0d649e81cd; this amendment does not accept Checkpoint 1 implementation by itself; Checkpoint 2, staging, commit, and runtime remain unauthorized; runtime authorization remains false; runtime attempts remain zero; D-064 remains BLOCKED. Assurance classifications are exact: cleanup_concurrency_model=EXCLUSIVE_WRITER_OPERATIONAL_PRECONDITION, same_authority_concurrent_mutation=OUTSIDE_CHECKPOINT_1_GUARANTEE, descriptor_relative_identity_controls=REQUIRED_DEFENSE_IN_DEPTH, atomic_final_publication=REQUIRED_NO_REPLACE, d064_runtime_authorization_dependency=EXCLUSIVE_WRITER_EVIDENCE_REQUIRED. This amendment makes no scientific, mission-impact, generic-radio-defect, CryptoLib, or SDLS claim.


D-063R2-PB1 (2026-07-31) was approved as the WP4 Checkpoint 2PB1 process-boundary authorization pivot (tracker/WP4_CHECKPOINT2_PROCESS_BOUNDARY_AUTHORIZATION_PIVOT_20260731.md, SHA-256 04adc8c9123a5e4e872b742a33d5672a03c2a65f752a19eaac4145633185874d). D-063R2-PB1 accepts the Checkpoint 2B1R2 self-test isolation correction as retained evidence (temporary regular-file manifest copy, no write to the canonical manifest, temporary-manifest drift invalidating authorization, canonical-manifest identity guard, and removal of the misleading duplicate stale_or_unregistered_bearer_rejected test) and thus keeps the Checkpoint 1 materialization core accepted (canonical manifest generation and verification, VerifiedManifest registry boundary, descriptor-bound source traversal, descriptor-relative destination mutation, exact workspace-policy validation, source and destination identity checks, exclusion and deny-pattern enforcement, no-replace file and workspace publication, complete destination audit, and cleanup under D-063R2-TM1). D-063R2-PB1 rejects the Checkpoint 2B1 in-process authorization layer as a production security boundary: MaterializationAuthorized, authorize_v3_materialization(), the closure-contained _issue function, the in-process authorization registry, bearer-based _require_auth(), and --authorize-v3-check as the proposed production authorization boundary are rejected because Python closure cells, function objects, class methods, registries, and mutable objects inside the same interpreter are not a security boundary against code executing in that interpreter. The current tool SHA-256 37c2a033f8b0fb0de17d1940c1cc12c13c52de4ec415a0e4afa16cb7dbc9e51c must not be treated as an accepted production runtime-material tool identity; it is retained as the experimental source for the accepted Checkpoint 1 core, the accepted 2B1R2 self-test isolation evidence, and the rejected 2B1 authorization experiment (CURRENT_TOOL_PRODUCTION_IDENTITY_ACCEPTED=false, CURRENT_TOOL_RETAINED_AS_EXPERIMENTAL_SOURCE=true). The pivot requires the host v3 candidate to invoke the runtime-material tool as a separate operating-system process, not import the runtime-material Python module, and perform all authorization and materialization in one tool process; no authorization bearer, registry object, issuer, token, secret, receipt object, or capability is returned to or shared with the candidate, and a successful authorization decision is retained only as internal process-local transaction state destroyed on process exit. Docker remains outside the materialization process and may be invoked by the host candidate only after the runtime-material process exits successfully and the published transaction receipt is validated; under contract 0.4.11 the future production CLI must fail before authorized-root inspection, staging creation, workspace creation, source copying, Fortytwo scratch creation, materialization, Docker, fake Docker, and retained-runtime evidence creation. The subsequent code checkpoint must replace the rejected authorization layer with a process-boundary transaction CLI conceptually --materialize-v3-transaction, receiving or deriving repository root, contract path, canonical manifest path, candidate path, authorized transaction root, and final transaction basename; the tool must identify itself from __file__ and must not trust a caller-supplied tool hash or alternate tool path as authority. One outer run-scoped staging directory beneath the authorized root holds workspaces (nos_engine, time_driver, hw_sim_01 through hw_sim_14, cmd_bus_bridge, cfs), fortytwo/configuration, and transaction-receipt.json; all 18 workspaces remain private physical writable copies; the separate Fortytwo configuration scratch is not counted as one of the 18 workspaces; no live external/nos3 path may be mounted into runtime containers; individual workspaces are not published separately; the complete outer transaction directory is published through one atomic no-replace rename (<final-run-basename>.staging-... -> <final-run-basename>); a failure before outer publication removes the complete staging transaction under the D-063R2-TM1 exclusive-writer prerequisite; no partially published final transaction may remain. The canonical transaction receipt must include schema, repository device and inode, contract relative path/device/inode/SHA-256, candidate relative path/device/inode/SHA-256, executing-tool relative path/device/inode/SHA-256, canonical-manifest relative path/device/inode/SHA-256, authorized-root device and inode, final transaction basename, all 18 component IDs, Fortytwo scratch identity, per-workspace verification disposition, aggregate workspace count, aggregate included file count, aggregate copied byte count, no-replace publication disposition, exclusive-writer evidence references, and runtime attempt value; no timestamp, random identifier, or host-dependent value is an implementation identity. The future production CLI must technically validate authorized-root type, owner, mode, no group/world write unless separately reviewed and explicitly permitted, no unexpected ACL grants, staging mode 0700, authorized-root device/inode binding, serialized transaction lock, no existing final basename, no existing staging basename collision, and no symlinked path components; the dedicated materializer operating identity, no concurrent maintenance/indexing/backup/orchestration writer, mount/shared-volume access review, ACL review, serialization evidence, and retained pre-runtime device/inode/owner/mode/ACL capture remain D-064 retained operational evidence. The host candidate must calculate its own SHA-256, validate it equals gate.accepted_runtime_entrypoint_v3_sha256, verify schema 1 structured authorization, invoke the runtime-material tool as a separate process, pass explicit canonical paths and transaction destination, require one exact successful completion marker, validate the published transaction receipt, and invoke Docker only after materialization success; it must not import the runtime-material Python module, access Python closures or registries, mint an authorization capability, pass a parsed contract dictionary, pass proposed identity as authorization, materialize workspaces itself, mount external/nos3 directly, or invoke Docker before transaction publication. The tool, canonical manifest, and downlink-diagnostic contract identities remain 37c2a033..., 5026176de3084c8015fd7f84827ce8a4e5d44df7e986bc142815eb0d649e81cd, and 8ccca310... (all unchanged); external/nos3 remains 5a3bdee6be9a2c67fdf994ae6db56d5c60395302 (clean, unchanged); nothing was staged. No source code, manifest, contract, generator, candidate, transaction, workspace, Fortytwo scratch, materialization, Docker, fake Docker, verifier, compilation, retained runtime evidence, staging, commit, push, or PR was performed; Checkpoint 2PB2 and Checkpoint 3 were not started. D063R2_PB1_DECISION=APPROVED, CHECKPOINT_1_MATERIALIZATION_CORE=ACCEPTED, CHECKPOINT_2B1R2_SELFTEST_ISOLATION=ACCEPTED, CHECKPOINT_2B1_IN_PROCESS_AUTHORIZATION=REJECTED, PROCESS_BOUNDARY_ARCHITECTURE=REQUIRED, CHECKPOINT_2PB2_IMPLEMENTATION_AUTHORIZED=false, GENERATOR_IMPLEMENTATION_AUTHORIZED=false, CHECKPOINT_3_AUTHORIZED=false, STAGING_AUTHORIZED=false, COMMIT_AUTHORIZED=false, RUNTIME_AUTHORIZED=false, RUNTIME_ATTEMPTS=0, D064_STATUS=BLOCKED. This decision makes no scientific, mission-impact, generic-radio-defect, CryptoLib, or SDLS claim.

D-063R2-PB2B-B1R3 (2026-08-01) accepts WP4 Checkpoint 2PB2B-B1R3 after independent adversarial review of the canonical materialization-plan compiler and the current-contract test-attribution correction. The accepted transaction-tool identity is 2589d40c4f5c300d5b74092f46e3099cadb3b39acab9ac8dc7b67bca2c596351; the accepted reportable-findings-register identity is 606d0389ec0fa83d7ccfb39e8701de4ae7805e9adf6541c2ed5923cef54bad60. The B1R3 review package is retained under review-evidence/WP4_2PB2B_B1R3: final-state SHA-256 2b3a98e08a9783149eaf06871b271c2928d2996261cc5fb83244fe58440e2fdd, self-test SHA-256 530a77657ac9a409c16c5b81da8b5e3a6c10bca1834a3c6ca9ed5e1a7d55ba58, and exact-type-probe SHA-256 859bb5d69447493c35267f4669500847b154b278c8a4f20708c11dc7542c4548. Independent review confirmed that all B1R3 source changes are confined to selftest(), the production and compiler regions are byte-identical to B1R2, all five current-contract tests require the exact contract-derived rejection `v3 static verification not PASS`, and the fixture candidate is a repository-local single-link regular file. The complete suite passed 183 tests with zero failures and zero skips. RF-ACT-002 contains five findings; RF-2026-020 is classified INTERNAL_FIX and is corrected, validated, and CLOSED. The current contract remains V3_TRANSACTION_AUTHORIZATION=CLOSED with rc=1 and no authorized root; the synthetic future-authorized preflight stops at V3_TRANSACTION_CORE=NOT_IMPLEMENTED with rc=2 and creates no synthetic root. Historical B1R2 evidence remains intact, external/nos3 remains clean at 5a3bdee6be9a2c67fdf994ae6db56d5c60395302, and nothing was staged during review. CHECKPOINT_2PB2B_B1R3_ACCEPTED=true. Staging may be considered only for the exact reviewed eight-file checkpoint scope; commit, push, B2, Checkpoint 3, Docker, NOS3 execution, materialization, runtime authorization, and runtime attempts remain unauthorized pending a final staged-diff review. Runtime authorization remains false, runtime attempts remain zero, and D-064 remains BLOCKED. This decision makes no scientific, mission-impact, generic-radio-defect, CryptoLib, or SDLS claim.

D-063R2-PB2B-B1R4 (2026-08-01) records the narrowly scoped WP4 Checkpoint 2PB2B-B1R4 staged-format correction following the accepted B1R3 independent review. `git diff --cached --check` identified one terminal blank line in tracker/REPORTABLE_FINDINGS_REGISTER.md and one terminal blank line in tracker/WP4_CHECKPOINT1_CLEANUP_THREAT_MODEL_AMENDMENT_20260731.md. Exactly one redundant terminal LF byte was removed from each file; no textual field, finding, classification, disposition, threat-model rule, authorization condition, implementation logic, manifest entry, or runtime behavior changed. The findings-register identity changed from 606d0389ec0fa83d7ccfb39e8701de4ae7805e9adf6541c2ed5923cef54bad60 to 2de89f0227eacac627e0a2b68074cbb18ac90bde2681a700a8e5824108f1d1c1. The cleanup threat-model amendment identity changed from 8a648157a5a0097edc49403e4e63fdf5bba67e43debb97e33d1dc8b531ebc318 to a3cf146913a3bf62cded128f9cb9563a6f55991b0fcadacd31bcd1c868574f05. The transaction-tool identity remains 2589d40c4f5c300d5b74092f46e3099cadb3b39acab9ac8dc7b67bca2c596351. The complete self-test suite was rerun after normalization and passed 183 tests with zero failures and zero skips; the real failure scan passed and the cached diff check returned zero. The exact reviewed eight-file staged scope remains unchanged, no review-evidence file is staged, and there are no unstaged changes. CHECKPOINT_2PB2B_B1R4_FORMAT_CORRECTION=ACCEPTED. This correction supersedes only the normalized file identities for the eventual commit; it does not rewrite or invalidate the historical B1R3 evidence or decision. Commit, push, B2, Checkpoint 3, Docker, NOS3 execution, materialization, runtime authorization, and runtime attempts remain unauthorized pending the final staged-index review. Runtime authorization remains false, runtime attempts remain zero, and D-064 remains BLOCKED. No scientific, mission-impact, generic-radio-defect, CryptoLib, SDLS, or third-party vulnerability claim is made.

## C3B-I2C combined v3 implementation governance reconciliation

- [x] Reconcile the already-reviewed merged v3 implementation to the D-063R2 combined-implementation state under contract `0.4.12`.
- [x] Bind proposed v3 candidate SHA-256 `599c534df37b127f7325ad513eecc4b24bdc0d37a56c32b4448a0b0099c13a1f` while keeping `accepted_runtime_entrypoint_v3_sha256` empty.
- [x] Bind generator SHA-256 `e3b1f8922161116e3ecfc1355900b72311d2834f5617b7a4956ccae4f6e50153` and corrected verifier SHA-256 `6556a4bbd01f46d11dd35abe420b3fbaaaab417339d6aa7d21040ca47f665ad9` without modifying either implementation file.
- [x] Bind transaction SHA-256 `0d2e76aab5b9e604b632f19caf2f2c9b584b191c9b7fafaff9bd1ae0d9ecff83`, material-core SHA-256 `37c2a033f8b0fb0de17d1940c1cc12c13c52de4ec415a0e4afa16cb7dbc9e51c`, and canonical-manifest SHA-256 `5026176de3084c8015fd7f84827ce8a4e5d44df7e986bc142815eb0d649e81cd`.
- [x] Create the predeclared implementation record `tracker/WP4_PASSIVE_TIME_WITNESS_RUNTIME_CANDIDATE_V3_COMBINED_IMPLEMENTATION_20260803.md` and implementation lock `artifacts/wp4-passive-time-witness-runtime-candidate-v3-combined-implementation-lock.txt`.
- [x] Preserve v3 static verification as `PENDING`, runtime authorization as false, runtime attempts as zero, and D-064 as `BLOCKED`.
- [x] Perform no complete verifier `--verify` execution, no candidate execution, no production materialization, no Docker/NOS3/Fortytwo runtime, and no scientific outcome.
- [ ] Separately govern and execute the v3 static-verification disposition under contract `0.4.13`.

## C3B-I2D corrected-verifier identity governance reconciliation

- [x] Preserve the original C3B-I2C verifier SHA-256 `6556a4bbd01f46d11dd35abe420b3fbaaaab417339d6aa7d21040ca47f665ad9` as the historical implementation binding.
- [x] Preserve the first complete verifier execution as `INVALID_EXECUTION` with `verifier_rc=1`; it established neither static PASS nor static FAIL.
- [x] Preserve retained invalid raw-log SHA-256 `a4a131c710e894ebdf8e29116ff4a08cb69351102d935c4f9ade1ef7586b06fb` and the diagnostic classification `SOURCE_DEFECT_PRODUCTION_FIXTURE_SCHEMA_GAP`.
- [x] Bind the independently reviewed corrected verifier published at `659ad0e3fb9ce79efe9c513279e145840ed9939e` with SHA-256 `49b12d8e8c66441b4d97580ce398dcf943348038ebff42db847c8c0a630a82e2`.
- [x] Reconcile the current contract `0.4.12` verifier identity plus implementation-record and implementation-lock hashes without advancing to `0.4.13`.
- [x] Record aggregate complete production verifier executions as `1` before any corrected retry.
- [x] Keep v3 static verification `PENDING`, accepted v3 candidate identity empty, runtime authorization false, runtime attempts `0`, and D-064 `BLOCKED`.
- [x] Perform no corrected complete `--verify`, candidate execution, production materialization, Docker/NOS3/Fortytwo runtime, or scientific outcome in this reconciliation.
- [x] Independently review and publish the six-file corrected-verifier identity governance reconciliation at `e137f4ecd2eebc11670998ee7cf407682aa34571` (independent review `ACCEPTED`, finding_count=`0`).
- [x] After the prior corrected-verifier identity governance publication, separately authorize and consume exactly one corrected complete static-verification retry; retained retry returned `rc=4` before candidate source scanning and established no static PASS or static FAIL.
- [x] Independently classify the retained retry `rc=4` as a verifier source defect rather than a candidate static finding.
- [x] Confirm root cause `PRODUCTION_PROPOSED_CANDIDATE_ACTUAL_RESOLVER_USES_SYNTHETIC_FIXTURE_AND_GENERIC_T036_MASKS_FAILED_IDENTITY_CONTROL`.
- [x] Validate the retry-verifier source correction with retained selftest `78/0/0` and a 14/14 pre-publication function-level identity-control probe.
- [x] Implement and independently review the retry-verifier source correction with finding_count `0`; publish verifier `238724221f595e81d52283345f3eb6e79404a0e49bfcc56fb463203ac88c6ee7` at `5045d734d876d3e1a6ee2d322fae121d536f7382`.
- [x] Prepare the minimum six-file verifier-identity governance reconciliation and prove the active verifier binding plus complete-verifier execution counter are stale.
- [x] Implement the six-file verifier-identity governance reconciliation while preserving contract `0.4.12`, static verification `PENDING`, accepted candidate empty, runtime false/0, and D-064 `BLOCKED`.
- [ ] Independently review the six-file retry-verifier identity governance reconciliation before publication or any further production static-verification authorization.

## C3B-I2D VR4 generator-stage observability governance reconciliation

- Decision: `D-063R2-C3B-I2D-VR4`.
- Published verifier: `da7d16d75d962d19997834d0c526298e7de74ef2250143667602fedaac932dca` at `main` commit `d4466c2c1a117cdd3354a35f4a5749bbdd61266f`.
- Previous active verifier `238724221f595e81d52283345f3eb6e79404a0e49bfcc56fb463203ac88c6ee7` remains historical and was used by production verifier execution #3.
- Execution #3: `rc=4`, `INVALID_EXECUTION_NO_STATIC_DISPOSITION`; candidate source scan not reached; no candidate static finding; no static PASS/FAIL.
- Aggregate complete production verifier executions: `3`.
- Production executions using `238724221f595e81d52283345f3eb6e79404a0e49bfcc56fb463203ac88c6ee7`: `1`.
- Production executions using `da7d16d75d962d19997834d0c526298e7de74ef2250143667602fedaac932dca`: `0`.
- Observability correction: six stable generator-stage diagnostic IDs, behavioral gate changes `0`, retained selftest `78/0/0`, independent source findings `0`.
- Contract remains `0.4.12`; static verification `PENDING`; accepted v3 candidate empty; runtime authorization false; runtime attempts `0`; D-064 `BLOCKED`.
- VR4 six-file proposal hashes: contract `f572cdbb216c5c11ce82d21f8c2ecf6525ea0be8988129c11d171e211d71fe62`, implementation record `18760a9c5f7809f248014fd23d401e822b13474230b8e335a72af3ded7a50bb7`, implementation lock `f870268ed669ff8cb6ac0b4dfeee650fb2db5e7ccc85f097c0368d823bccb915`.
- No production verifier execution, generator execution, candidate execution, materialization, Docker/NOS3/Fortytwo runtime, staging, commit, or push is performed by this design.
- Next gate: `C3B_I2D_RETRY_VERIFIER_GENERATOR_STAGE_OBSERVABILITY_CORRECTION_GOVERNANCE_RECONCILIATION_IMPLEMENTATION_AUTHORIZATION`.

## C3B-I2D VR5 coordinated generator/verifier correction and execution #4 reconciliation

- Decision: `D-063R2-C3B-I2D-VR5`.
- Corrected active v3 generator SHA-256: `7140b7ff1aa1873ac020bae24d2a921a343f3d1fde86c6bbb4aece45cf229812`.
- Corrected active static verifier SHA-256: `1a7db020a08beca3448c484273595bfa769112ad1fd2a66d73094c37a8d88fa2`.
- Execution #4: `INVALID_EXECUTION_NO_STATIC_DISPOSITION`.
- Execution #4 failure ID: `SVF_C3B_I2D_GEN_001_PROCESS_NONZERO`.
- Accepted root cause: `V3_GENERATOR_SOURCE_API_COMPATIBILITY_DEFECT`.
- Accepted source finding: `SOURCE_DEFECT_V3_GENERATOR_PATHLIB_WRITE_TEXT_NEWLINE_COMPATIBILITY`.
- Aggregate complete production verifier executions: `4`.
- Corrected-verifier production executions represented by execution evidence: `1`.
- Candidate source scan reached: `false`.
- Candidate failure established: `false`.
- Static verification remains: `PENDING`.
- Runtime authorization remains: `false`.
- Runtime attempts remain: `0`.
- D-064 remains: `BLOCKED`.
- Production verifier rerun authorization remains: `false`.
