# Study 7E AERC Continuation Handoff — 2026-09-23

## Scope and authority

This record preserves the continuation state for the pre-freeze, non-canonical Study 7E AERC implementation lane (`S7E-AERC-001`). It is a governance/status handoff only. It does not modify, replace, freeze, or promote the native deterministic Study 7E experiment or any submitted/frozen publication evidence.

Active pull request: **#167**  
Active branch: `paper3/s7e-aerc-implementation-feasibility-20260922`  
Gate-1 qualification head: `bef6fe920277d378ba857d280633f48b2b25cffc`  
Base: `main`

PR #167 remains an active implementation/qualification PR. **No merge is authorized by this handoff.**

## Gate 1 — corrected cFS runtime smoke: GREEN

The corrected cFS feasibility gate is green at exact head `bef6fe920277d378ba857d280633f48b2b25cffc`.

Authoritative GitHub Actions evidence:

- Study 7E pre-canonical qualification:
  - workflow ID: `364617426`
  - run ID: `35868263684`
  - conclusion: `success`
- cFS custom-app smoke:
  - job ID: `107205320338`
  - conclusion: `success`
- repository-wide validation:
  - run ID: `35868263952`
  - conclusion: `success`
- pinned standalone cFS:
  - tag: `v7.0.1`
  - commit: `088b2fa828db9ff7e00733f1908e0eeb59f66ce3`

The runtime job:

1. built the custom `aerc_bus_probe`;
2. installed it under the cFS cpu1/cpu2 `cf/` application directories;
3. loaded `AERC_PROBE` under live cFE;
4. created/subscribed a Software Bus pipe;
5. transmitted the fixed probe message on experimental MID `0x0EE0`;
6. received and validated the same message;
7. emitted the exact PASS marker:

`AERC_BUS_PROBE PASS scenario=0x53374531 marker=0xA37C0DE1`

The workflow also recorded:

- `aerc_bus_probe_runtime=PASS`;
- `study7e_scientific_scenarios_executed=0`;
- `scientific_results_generated=false`.

This is engineering/runtime feasibility evidence only.

## Gate-1 defect corrections

Two concrete harness defects were corrected without changing Study 7E scientific behavior.

### Entry-point mismatch

At handoff head `9c4ad55bf14ed7de62e4d4e586ccf6ece3683398`, run `35824429121`, job `107062970996` failed because cFE attempted the configured `AERC_BUS_PROBE_AppMain` symbol, which did not match the probe's exported `AERC_BUS_PROBE_Main`.

Correction commit:

`0884b397b3b8e2c67d9b699dc6f2d9f4f801b887`

### Message-layout mismatch

After the entry-point correction, run `35867546996`, job `107202887028` loaded the probe but failed its payload check because the probe used the generic `CFE_MSG_Message_t` base header while MID `0x0EE0` carries the cFE telemetry secondary-header semantics. The secondary-header bytes therefore overlapped the first payload field.

Correction commit:

`bef6fe920277d378ba857d280633f48b2b25cffc`

The probe now uses `CFE_MSG_TelemetryHeader_t` and passes the embedded `.Msg` to the cFE message/Software Bus APIs. The fixed scenario and marker are preserved through transmit/receive.

## Provenance correction to the prior handoff

The earlier version of this handoff and `IMPLEMENTATION_STATE.json` stated that a prior cFS runtime had demonstrated:

- a NOOP on command MID `0x1886`;
- housekeeping on MID `0x0886`;
- `cmd_count=1`;
- `AERC bus probe PASS: HK MID 0x0886 cmd_count=1`.

That claim is **retracted as unsupported**.

The referenced prior Study-7E run `35807192091`, cFS custom-app job `107010550970`, was inspected directly. Its log shows the `aerc_bus_probe` failing at application entry-symbol resolution; it does not establish the claimed NOOP/HK interaction. Inspection of PR #167 also shows that the cFS flight-software surface currently contains the non-canonical `aerc_bus_probe`, not a full AERC policy application.

The corrected, supported runtime evidence is the green Software Bus self-loop probe described above. Historical commits are preserved; no history was rewritten.

## Exact interpretation boundary

Gate 1 now supports:

**standalone cFS v7.0.1 can build, load, and execute the Study-7E non-canonical custom probe, and the probe can publish/receive and validate a fixed message through cFE Software Bus in CI.**

Gate 1 does **not** establish:

- a full AERC policy application running in cFS;
- AERC command/HK interfaces at `0x1886`/`0x0886`;
- recovery-policy behavior;
- fault-injection behavior;
- Study-7E scientific observations;
- flight qualification;
- certification/certifiability;
- production or deployment readiness;
- operational-spacecraft validation.

## Current scientific/governance state

- Study: `Study7E`
- Experiment: `S7E-AERC-001`
- Lane: pre-freeze, non-canonical implementation/technology-demo feasibility
- Program token: `AERC`
- ITOS token: `aerc`
- Native deterministic Study 7E experiment remains the prospective canonical execution surface.
- Canonical scientific execution remains prohibited.
- No production L0/L1 model is trained or frozen.
- No Study-7E canonical results exist.
- No Study-7E dataset/Zenodo freeze exists.
- No runtime stack has yet been selected for the remaining non-canonical architecture.

Prospective protocol quantities remain unchanged:

- TR1 = 72
- TR0 = 12
- training = 84
- E1 = 84
- E2 = 104
- C0 = 8
- evaluation/control = 196
- four policies per evaluation scenario = 784 planned policy-decision observations
- complete prospective manifest = 280

These are protocol-design quantities, not scientific results.

## Next authorized gates

Proceed in this order only:

1. **Bounded NOS3 feasibility**
   - Gate 1 is green, so this may now begin.
   - Use current authoritative NOS3/cFS documentation and upstream repository evidence.
   - Capture exact versions, tags, commits, submodules, platform/runtime assumptions, build/dependency burden, cFE/SB integration, telemetry/command visibility, simulated hardware/device integration, NOS Engine dependencies, CI/repeatability/provenance, and scientific benefit/complexity.
   - Do not expand this into a full NOS3 implementation.

2. **cFS-vs-NOS3 stack decision**
   - Compare both with the same factual criteria.
   - Do not use arbitrary numerical scores or popularity.
   - Select only for this pre-defined Study 7E architecture/question.
   - Record the decision durably.

3. **Remaining non-canonical architecture**
   - Continue only after the stack decision is documented.
   - Keep all architecture work outside canonical scientific evidence until separately authorized/adjudicated.

## Guardrails

- Explain exact repository changes before writes.
- Work only on the active Study 7E branch/PR unless explicitly authorized otherwise.
- No PR merge, force push, rebase, destructive branch deletion, base change, or history rewrite without explicit authorization.
- Preserve exact commit SHAs, workflow/run/job identifiers, logs, and provenance.
- Do not promote cFS/NOS3 technology-demo evidence into scientific findings.
- Do not modify Papers 1, 2, 4, the submitted/frozen Study 7 CEAS package, Study 5, or the separate JSSE study.
- Preserve the equal-information/truth-separation controls and training/evaluation leakage guards.

## Durable records

Machine-readable state:

`study7e/IMPLEMENTATION_STATE.json`

Gate-1 checkpoint:

`publication/Paper_3_Study_7/Post_Rejection_Rebuild/S7E_AERC_CFS_GATE1_CHECKPOINT_2026-09-23.md`

Earlier implementation checkpoint retained as historical provenance:

`publication/Paper_3_Study_7/Post_Rejection_Rebuild/S7E_AERC_IMPLEMENTATION_CHECKPOINT_2026-09-22.md`

## Gate 2 — bounded NOS3 feasibility: GREEN

At head `178fdbd4871c2f6f89b62a8f4f0d2ce826853188`, workflow `Study 7E bounded NOS3 feasibility` (workflow ID `365185951`, run `35870689230`, job `107213663081`) completed successfully.

The bounded gate confirmed the exact NOS3 1.7.5 revision and key recursive gitlinks, then completed `config`, `build-test`, `test-fsw`, and `build-sim`. Artifact `10755347006` was produced with digest `sha256:28397de31e1eed3a37304f9e552ba936222a1a6d53555c28585c817485d4ef38`.

The run executed zero Study-7E scientific scenarios and generated no scientific results.

Durable Gate-2 checkpoint:

`publication/Paper_3_Study_7/Post_Rejection_Rebuild/S7E_AERC_NOS3_GATE2_CHECKPOINT_2026-09-23.md`

## Stack-selection status — DEFERRED, fail closed

The bounded NOS3 build does not satisfy all preregistered proof-before-selection criteria. The same is true of the standalone-cFS candidate: Gate 1 proves a live custom Software Bus probe but not yet the two-instance/SBN, HS/readiness, end-to-end scenario-ID, and action-sink seams required by the implementation plan.

Accordingly, no stack is selected or frozen yet.

Durable preselection review:

`publication/Paper_3_Study_7/Post_Rejection_Rebuild/S7E_AERC_STACK_PRESELECTION_REVIEW_2026-09-23.md`

### Required next feasibility proofs

Before selecting a stack:

- standalone cFS: HS/readiness observation, two-instance SBN, deterministic scenario-ID survival, and action-sink telemetry/capture;
- NOS3: Study-7E custom-app integration, deterministic non-canonical scenario control, required SBN/multi-instance topology, deterministic trace/capture, and runtime network-dependency containment.

These remain engineering qualification activities only. Canonical Study-7E execution remains prohibited.

## cFS preselection seams — GREEN

At head `f97433b7025a655f21ca97e71618f3aa1fd4b2a3`, workflow `Study 7E cFS preselection seams` (workflow ID `365200358`, run `35873580570`, job `107223637303`) completed successfully.

Evidence:

- artifact `10756545870`;
- digest `sha256:4e3202fc55e853ff8a83de48f32d818f236ab6bfcade9d782d26a336054b6b93`;
- `AERC_SBN_SINK PASS scenario=0x53374532 marker=0xA37C0DE2 sink_cpu=2 receipt=0xBEEF`;
- `AERC_SBN_ROUNDTRIP PASS scenario=0x53374532 marker=0xA37C0DE2 sink_cpu=2 receipt=0xBEEF attempt=1`;
- `AERC_HS_OBSERVER PASS appmon=1 eventmon=0 aliveness=1 cpuhog=1 status=0x1F cmd_count=0 cmd_err=0`;
- `research_truth_derived=false`;
- `study7e_scientific_scenarios_executed=0`;
- `scientific_results_generated=false`.

The HS fields are engineering runtime observations, not the Study-7E adjudicator truth variable.

Checkpoint:

`publication/Paper_3_Study_7/Post_Rejection_Rebuild/S7E_AERC_CFS_PRESELECTION_SEAMS_CHECKPOINT_2026-09-23.md`

## Stack decision — standalone cFS v7.0.1 selected

The remaining non-canonical Study-7E architecture will use standalone cFS v7.0.1 at `088b2fa828db9ff7e00733f1908e0eeb59f66ce3` as the pre-freeze implementation baseline.

NOS3 v1.7.5 remains bounded feasibility/reference evidence and is not mixed into the selected baseline. Its documented multiple-spacecraft path requires a separate proof-of-concept repository/branch outside the pinned NOS3 dependency graph.

Decision:

`publication/Paper_3_Study_7/Post_Rejection_Rebuild/S7E_AERC_STACK_SELECTION_DECISION_2026-09-23.md`

This is **not** a protocol/environment freeze and does not authorize production-model training/freeze or canonical scientific execution.

### Next gate

Continue the remaining non-canonical architecture components on the selected cFS baseline while preserving equal-information, truth-separation, deterministic-control, and fail-closed canonical-execution guards.

## Recovery action sink — GREEN

At head `ec2637b5d1c6710e6ac97b32d45cbde2750c1d42`, the selected standalone cFS baseline successfully compiled and ran the pre-canonical `aerc_sink` plus its engineering-only `aerc_sink_probe`.

GitHub Actions evidence:

- workflow: `Study 7E pre-canonical qualification`
- workflow ID: `364617426`
- run ID: `35882223951`
- job ID: `107253301919`
- job conclusion: `success`

Observed positive records:

- `AERC_RECOVERY_SINK RECORD scenario=0x53374541 policy=1 action=HOLD sequence=1`
- `AERC_RECOVERY_SINK RECORD scenario=0x53374542 policy=3 action=ENTER_RECOVERY_GATE sequence=2`

Observed fail-closed checks:

- `AERC_RECOVERY_SINK REJECT_LENGTH expected=24 actual=20 status=0x00000000`
- `AERC_RECOVERY_SINK REJECT_ACTION scenario=0x5337454F policy=2 action=255`

Engineering probe:

- `AERC_SINK_PROBE PASS hold_scenario=0x53374541 enter_scenario=0x53374542 records=2 negatives=2`

The workflow recorded `study7e_scientific_scenarios_executed=0` and `scientific_results_generated=false`.

The sink makes no claim about whether a requested action is correct. It contains no research-only truth and performs no real hardware actuation.

Durable checkpoint:

`publication/Paper_3_Study_7/Post_Rejection_Rebuild/S7E_AERC_RECOVERY_SINK_CHECKPOINT_2026-09-23.md`

### CI efficiency update

After the selected cFS baseline and sink gate became green, CI was separated by purpose:

- fast pre-canonical contracts/governance remain automatic;
- cFS runtime smoke runs on Study-7E FSW changes or manual dispatch;
- full cFS `native_std.runtest` baseline feasibility is retained as manual-only.

This avoids repeating an already-established full baseline build on documentation/config-only commits.

## Shared B/C snapshot + deterministic D0/D1 — GREEN

At head `b13f0d0cd6db3aa0f6e965e9303e7068544f3184`, the FSW-only runtime-smoke workflow completed the isolated deterministic policy gate successfully.

Evidence:

- workflow: `Study 7E cFS runtime smoke`
- workflow ID: `365269942`
- run ID: `35885631864`
- job ID: `107264993826`
- artifact ID: `10761799281`
- artifact digest: `sha256:0b8ce4878099acad5e06257106f26aaac0cc6db58e1aa258db0312f66f15ee47`
- repository validation run: `35885631683` — success
- pre-canonical qualification run: `35885631522` — success

Positive deterministic decisions:

- `D0_BASE` ENTER on scenario `0x53374551`, sequence 1, 9-feature base snapshot;
- `D0_BASE` HOLD on scenario `0x53374552`, sequence 2;
- `D1_CORROBORATED` ENTER on scenario `0x53374553`, sequence 3, 16-feature corroborated snapshot;
- `D1_CORROBORATED` HOLD on scenario `0x53374554`, sequence 4.

Fail-closed runtime checks:

- malformed snapshot length rejected;
- base/corroborated feature-count mismatch rejected;
- non-binary feature value rejected.

All four accepted decisions produced matching recovery-sink records with the same policy/action ordering.

The workflow also recorded:

- `aerc_policy_runtime=PASS`;
- `aerc_d0_runtime=PASS`;
- `aerc_d1_runtime=PASS`;
- `research_truth_visible_to_policy_runtime=false`;
- `learned_policy_runtime_executed=false`;
- `study7e_scientific_scenarios_executed=0`;
- `scientific_results_generated=false`.

Checkpoint:

`publication/Paper_3_Study_7/Post_Rejection_Rebuild/S7E_AERC_POLICY_SNAPSHOT_D0_D1_CHECKPOINT_2026-09-23.md`

### Next gate

Perform a bounded compatibility/provenance review for the real-signature verification dependency. Ed25519 remains the protocol candidate, but no crypto runtime is selected or added by this checkpoint. L0/L1 learned-policy implementation remains separate and no production model is trained or frozen.

## Ed25519 verification dependency — Monocypher 4.0.3 selected

The bounded dependency gate at head `e5ce0606f23ffbb9c1f80fe6f0f32feda70c3242` completed successfully for both finalists:

- workflow ID: `365298193`
- run ID: `35887743822`
- Monocypher job: `107272117959` — success
- libsodium job: `107272118271` — success

Both candidates passed the same RFC 8032 positive verification and negative mutated-signature, zero-signature, and changed-message checks.

Measured feasibility surfaces:

- Monocypher 4.0.3 selected static subset: `97,982` bytes; test binary: `33,728` bytes;
- libsodium 1.0.22 static archive: `927,808` bytes; test binary: `314,960` bytes.

For this verification-only Study-7E cFS integration, Monocypher 4.0.3 at `ab2b16dd619ad5f6979a4fbe69cfa324a6fcc35f` is selected for the next pre-canonical integration gate. libsodium 1.0.22 remains a green reference alternative.

Mandatory integration guard: Monocypher documents that it does not perform input validation, so the Study-7E wrapper must enforce exact packet, public-key, signature, and canonical-message lengths before calling `crypto_ed25519_check`.

No signing key is permitted in flight software. This selection makes no FIPS, certification, flight-qualification, or scientific-result claim.

Decision record:

`publication/Paper_3_Study_7/Post_Rejection_Rebuild/S7E_AERC_ED25519_DEPENDENCY_DECISION_2026-09-23.md`

## cFE Ed25519 verification boundary — GREEN

At head `2c5725e0c43114a087da1087f7fb1d94814661e0`, the selected cFS baseline successfully compiled and executed the pinned Monocypher 4.0.3 verification-only boundary.

GitHub Actions evidence:

- workflow: `Study 7E cFS runtime smoke`
- workflow ID: `365269942`
- run ID: `35890910760`
- job ID: `107282876318`
- artifact ID: `10765340878`
- artifact digest: `sha256:ef74d724eb61548ad41b59356b77874a4285c34b6fdcab40ce712553576c0496`
- pre-canonical qualification run `35890910817`: success

Observed verification behavior:

- RFC 8032 Test 1 accepted;
- final repeat of the valid vector accepted at verification sequence 5;
- mutated signature rejected cryptographically;
- all-zero signature rejected cryptographically;
- changed message rejected cryptographically;
- short packet, wrong wire version, wrong key ID, message length 65, and nonzero inactive message padding were rejected before cryptographic output;
- malformed requests did not advance the verification sequence.

Exact probe marker:

`AERC_SIGVERIFY_PROBE PASS valid=2 crypto_reject=3 malformed_reject=5 final_sequence=5`

The runtime also recorded:

- `secret_key_in_flight_software=false`;
- `policy_authorization_binding_present=false`;
- `study7e_scientific_scenarios_executed=0`;
- `scientific_results_generated=false`.

Checkpoint:

`publication/Paper_3_Study_7/Post_Rejection_Rebuild/S7E_AERC_ED25519_CFS_BOUNDARY_CHECKPOINT_2026-09-23.md`

### Next design gate

The protocol does not yet define canonical signed-authorization bytes or the final public-key provenance registry. Do not derive `primary_signature_valid`, `corr_signature_valid`, `primary_authorization`, or `corr_authorization` from this engineering verifier until those byte/provenance contracts are separately reviewed and recorded.

## Signed authorization-evidence contract — DRAFT ONLY

A machine-readable and human-readable **candidate** signed-evidence/key-provenance contract has been added for review:

- `study7e/configs/signed_evidence_contract_draft.json`
- `publication/Paper_3_Study_7/Post_Rejection_Rebuild/S7E_AERC_SIGNED_EVIDENCE_CONTRACT_DRAFT_2026-09-23.md`

The draft does not freeze canonical bytes, public keys, signing keys, freshness rules, epoch semantics, or policy binding.

Candidate properties proposed for review include:

- explicit fixed-width big-endian byte serialization rather than native C struct serialization;
- signed domain separator `S7E-AERC-AUTH-V1`;
- signed producer role, authorization value, source ID, authority ID, key ID, epoch, controlled logical time, and evidence sequence;
- a proposed 56-byte signed body that fits within the already-qualified 64-byte engineering verifier capacity;
- public-key IDs mapped to key domains, with no secret key in verifier flight software.

The draft explicitly leaves scenario/context binding, replay semantics, freshness thresholds, contradiction/completeness semantics, T4 authority representation, fault byte transformations, and final test-key registry unresolved.

No verifier result is bound to `primary_signature_valid`, `corr_signature_valid`, `primary_authorization`, or `corr_authorization` by this draft.

## Signed-evidence contract technical review R1 — REVISE

The first draft has completed technical/adversarial review. It is **not approved for freeze**.

Review records:

- `study7e/configs/signed_evidence_contract_review_r1.json`
- `publication/Paper_3_Study_7/Post_Rejection_Rebuild/S7E_AERC_SIGNED_EVIDENCE_CONTRACT_REVIEW_R1_2026-09-23.md`

Blocking findings:

1. sign an opaque scenario/context identifier to prevent cross-scenario splice/replay ambiguity;
2. explicitly resolve signing-key placement before producer implementation;
3. explicitly resolve T4 authority representation/keying provenance.

The review recommends a 64-byte candidate body that preserves 64-bit epoch/logical-time/sequence fields while adding a signed opaque `scenario_id`. It also recommends keeping completeness structural-only and preserving a structurally parsed authorization claim independently of signature validity so policy-visible feature meanings are not silently collapsed.

Author approval, protocol freeze, and policy binding remain false.

## Signed-evidence candidate v2 — APPLIED, NOT APPROVED/FROZEN

R1's recommended revision has been applied to the draft contract without author approval or protocol freeze.

Active candidate:

- explicit fixed-width big-endian serialization;
- 64-byte signed body;
- signed opaque `scenario_id` at bytes 20–23;
- opaque source/authority/key IDs;
- 64-bit epoch, controlled logical time, and evidence sequence;
- no topology/fault identity in signed or policy-visible evidence;
- structural-only completeness candidate;
- authorization claim preserved independently of `signature_valid` when evidence is structurally complete.

The original 56-byte candidate remains in the JSON as superseded historical design provenance.

Still blocking:

- signing-key placement;
- T4 separate-authority representation/keying provenance;
- final logical-time/freshness/epoch/replay rules;
- final opaque registries and test-key provenance;
- final fault byte transformations.

All author-approval, protocol-freeze, key-freeze, policy-binding, and canonical-execution gates remain false.

## Signed-evidence architecture blockers — technical draft resolution

Two R1 blockers now have a pre-canonical **technical draft resolution**, not an author-approved freeze:

- signing keys remain outside all cFS FSW in a deterministic local Study-7E test signing harness;
- T4 authority separation uses a signed opaque `authority_id` plus harness provenance/state, without introducing a second authority-signature hierarchy.

This preserves independent key-, execution-, source-, and authority-domain fault semantics:

- F3/F4 key compromise affects controlled harness signing-key access;
- F12 execution compromise can alter/drop producer behavior without automatically exposing the key;
- F10 authority compromise changes authority output before source/producer signing;
- F1 source false changes the claim after authority output but before signing.

No external network signer is permitted for canonical execution. No final key material, registry, or fault transformation is frozen.

Records:

- `study7e/configs/signed_evidence_architecture_resolution_draft.json`
- `publication/Paper_3_Study_7/Post_Rejection_Rebuild/S7E_AERC_SIGNED_EVIDENCE_ARCHITECTURE_RESOLUTION_DRAFT_2026-09-23.md`

## Host-side signed-evidence v2 feasibility — IMPLEMENTED, QUALIFICATION PENDING

A non-canonical host-side implementation now exercises the reviewed 64-byte v2 candidate without adding private keys to cFS FSW.

Files:

- `study7e/feasibility/signed_evidence_v2/aerc_signed_evidence_v2.[ch]`
- `study7e/feasibility/signed_evidence_v2/signed_evidence_v2_monocypher_test.c`
- `.github/workflows/study7e-signed-evidence-v2-feasibility.yml`

The engineering test uses the published RFC 8032 Section 7.1 Test 1 seed/public key only as standard test-vector material. It is not final Study-7E key material.

The gate checks explicit big-endian serialize/parse round-trip, deterministic key derivation, signing/verification of the 64-byte body, signature failure after mutations of protected fields, and malformed/invalid structural rejection.

No final key registry, policy binding, scientific scenario, or result is created.

