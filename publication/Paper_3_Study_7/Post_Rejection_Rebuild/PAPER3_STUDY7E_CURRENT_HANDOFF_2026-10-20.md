# Paper 3 / Study 7E — authoritative cross-chat handoff (2026-10-20)

**Scope:** Paper 3 rebuilt from **Study 7 + Study 7E** as separate, independently frozen experimental populations.  
**Source authority:** live `main` verified at `1590fb97c854b4c60aae2fcb105cbc511e10043f`; this is a continuity/status document, **not** a protocol or result amendment.  
**Main CI:** `Validate research configurations` run `39444167182` / #1492, `push`, conclusion `success`, exact head `1590fb97c854b4c60aae2fcb105cbc511e10043f`.  
**New publication-readiness tracker:** [Issue #221](https://github.com/Zartharas/mission-aware-satellite-cyber-recovery/issues/221).

## 1. Essential correction to historical handoffs

The September 22 early design / implementation gates were completed in later September 23–24 work. Do **not** resume at an old "runtime smoke pending", "NOS3 assessment pending", "stack undecided", "protocol not frozen" or "held-out execution not yet authorized" checkpoint.

Historical 2026-09-22/23 records and dated machine-readable checkpoints retain their original authorizations for provenance. Their earlier prospective or prohibited-action statements must not be treated as the latest state after an independently documented authorization/merge. This handoff does not retroactively alter those records.

## 2. Three architecture gates — completed

### Gate 1: corrected standalone cFS smoke — PASS

- Exact upstream NASA cFS: `v7.0.1`, `088b2fa828db9ff7e00733f1908e0eeb59f66ce3`.
- Workflow run `35868263684`, cFS job `107205320338`, success.
- Non-canonical live cFE app `AERC_PROBE` successfully loaded and sent/received a fixed Software Bus telemetry message.
- Marker: `AERC_BUS_PROBE PASS scenario=0x53374531 marker=0xA37C0DE1`; MID `0x0EE0`.
- Correction: the older purported NOOP/HK claim for run `35807192091` is **retracted as unsupported** by its actual job logs. The accepted gate proves an engineering smoke only, not full learned AERC recovery logic.

Authority: `S7E_AERC_CFS_GATE1_CHECKPOINT_2026-09-23.md`.

### Gate 2: bounded NOS3 feasibility — PASS

- Exact NOS3: `v1_07_05` / 1.7.5, `5a3bdee6be9a2c67fdf994ae6db56d5c60395302`.
- Run `35870689230`, job `107213663081`, success.
- Pinned submodules, `make config`, `make build-test`, `make test-fsw` and `make build-sim` passed.
- This did **not** establish Study-7E runtime in NOS3, custom app integration, multi-spacecraft topology, or ground telemetry/fault observation.
- Do not swap NOS3's native cFE/OSAL/PSP/SBN pins with standalone cFS dependencies or silently add the external multi-spacecraft repository.

Authority: `S7E_AERC_NOS3_GATE2_CHECKPOINT_2026-09-23.md`.

### Gate 3: stack decision — COMPLETED

Decision `S7E-AERC-STACK-SELECT-003` selects **standalone NASA cFS v7.0.1** for the pre-freeze implementation baseline because cFE/SB/SBN, two-instance scenario propagation, sink receipt and HS observation were demonstrated without NOS3's additional dynamics/hardware surface. NOS3 is retained as reference feasibility, not the chosen Study-7E execution stack. This is **not** a claim that cFS is universally superior.

Authoritative decision: `S7E_AERC_STACK_SELECTION_DECISION_2026-09-23.md`; extra cFS seam run `35873580570` / job `107223637303`.

## 3. Later Study 7E milestones — frozen; do not repeat

PR [#167](https://github.com/Zartharas/mission-aware-satellite-cyber-recovery/pull/167) was **merged** on 2026-09-24 as `740cc4984387b2c4f14b337b76d66198406f22c4`. Earlier JSON/README flags saying "PR merge not authorized" are historic snapshots, not the live PR state.

- Experiment: `S7E-AERC-001`.
- Protocol/environment freeze: `S7E-AERC-FREEZE-001`.
- Model freeze: `S7E-AERC-MODEL-FREEZE-001`.
- Result freeze: `S7E-AERC-RESULT-FREEZE-001`.
- Sole authorized held-out scientific execution: `S7E-AERC-HELDOUT-EXEC-001`; original run `35948870036`; source `1cbc4be58a99e9add139e73efc9ab42a4f275864`.
- E1: 84 scenarios; E2: 104; C0: 8; **196 held-out scenarios, 784 policy decisions**.
- Invalid scenarios: 0. Independent reconciliation mismatches: 0.
- Original result ZIP SHA-256 `cc436ee98e20bb13643f58af738f42885b499a81bddad2766cb90f3e0860da35`; durable material under `study7e/frozen_results/S7E-AERC-RESULT-FREEZE-001/`.
- Hypotheses: H1 and H5 supported; H2, H3 and H4 partially supported. Preserve adverse/null findings. No universal learned-policy winner, independent-oracle guarantee, general error probability or flight qualification follows.

Do not rerun the sealed execution; change the endpoint/population; refit/retrain frozen models; or overwrite frozen artifacts. Study 7 (`S7-LSO-001`, 1,033 observations) and Study 7E remain separate, **never pooled**.

Authorities: `study7e/RESULT_FREEZE_MANIFEST_001.json`, `study7e/RESULT_FREEZE_STATE.json`, `study7e/README.md`, and `S7E_AERC_RESULT_FREEZE_001_RECORD_2026-09-23.md`.

## 4. Active rebuilt Paper 3 publication branch

- PR [#168](https://github.com/Zartharas/mission-aware-satellite-cyber-recovery/pull/168): **OPEN / DRAFT / UNMERGED** on 2026-10-20.
- Head branch: `paper3/rebuilt-study7-study7e-manuscript-20260924`.
- Verified head: `375aa5bc5808ddace8bb124df73eb184a61b9765`.
- Exact-head `Validate research configurations` run `36012450683` / #1186: `success`.
- Working journal target: **International Journal of Critical Infrastructure Protection (IJCIP)**; target lock is for preparation, **not** publisher submission authorization.
- Manuscript: `publication/Paper_3_Study_7/Rebuilt_Study7_7E/IJCIP/PAPER3_IJCIP_MANUSCRIPT_R3.md`.
- State: `IJCIP_R3_SCIENTIFIC_PRESERVATION_PASS__TARGET_LOCKED_FOR_PREPARATION__FINAL_PORTAL_AUDIT_REQUIRED__SUBMISSION_NOT_AUTHORIZED`.
- R3 preservation audit passes; manuscript at recorded audit: 7,606 words, 24 references, 6 keywords, five prepared highlights.
- IJCIP-specific Guide for Authors previously returned HTTP 403. Exact journal portal requirements, any abstract/graphical-abstract restrictions, and remaining access/rights or file classifications must be verified live; never invent an inaccessible rule.
- Manuscript prepared with honest disclosures distinguishing research-development ChatGPT assistance in Methods and substantive manuscript-preparation AI disclosure before References. Maintain these disclosures.

The rejected CEAS Paper 3 package remains immutable provenance; no publisher submission of rebuilt Paper 3 has been verified or authorized. Do not merge PR #168 without a separate explicit author gate.

## 5. Next substantive gate — publication readiness, not new science

Use [Issue #221](https://github.com/Zartharas/mission-aware-satellite-cyber-recovery/issues/221) to perform:
1. Live main/PR #168 status and file/CI verification before any write.
2. Updated IJCIP scope/Guide/portal requirements audit, separating verified from inaccessible requirements.
3. Manual citation/DOI/metadata/retraction and claim-to-evidence checking, including adverse findings and explicit non-overlap with all other papers.
4. Only after confirmed requirements: final Word/PDF, tables/figures, highlights, cover letter, declarations, AI disclosure, accessibility and visual QA.
5. Independent frozen-science preservation audit and required author-facing metadata confirmation.
6. Explicit authorization **separately** for any PR #168 merge and any publisher portal submission.

Keep PRs #215 and #216 **OPEN/DRAFT/UNMERGED**, as they are separate Paper 2 work. Paper 2 was received at CEAS on 2026-10-19 and is at technical check (Issue #217); these are **not** Study-7E data or permissions. Other publication and repository tracks are out of scope and must not be changed.

## 6. New-chat start sequence

1. Read live `main` (do not assume the SHA in this dated handoff is still head), all open PRs, Issues #221 and #217, PR #168, and the main `docs/CURRENT_PUBLICATION_STATE.md`.
2. Read `study7e/RESULT_FREEZE_MANIFEST_001.json`, `study7e/RESULT_FREEZE_STATE.json`, `study7e/README.md` and the selected cFS and NOS3 qualification/stack-decision checkpoints.
3. Read the IJCIP R3 manuscript, `MANUSCRIPT_INTEGRATION_STATUS.json`, `IJCIP_LIVE_COMPLIANCE_AUDIT_2026-09-24.md`, the claim ledger, and PR #168 check results.
4. Identify only unresolved, supportable next tasks; report exactly what is being proposed before repository writes.
5. Retain a fail-closed boundary on frozen models/results, source pins, CEAS rejected package, submission and PR merge.

**This handoff records verified history and remaining gates; it is not evidence of a new scientific execution or a publisher acceptance.**
