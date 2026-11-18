# Current Publication State

**Current-state date:** 2026-10-20 (Paper 2 reconciled; other papers retain their last independently recorded updates)

**Study 8E extension update:** 2026-09-20

**Paper 4 IJSCCN package-freeze update:** 2026-09-21

**Paper 4 IJSCCN privacy-hardening update:** 2026-09-21

**Paper 4 IJSCCN R5 rebuild-gate update:** 2026-09-21

**Paper 3 Study 7E / IJCIP draft continuity update:** 2026-10-20 (original CEAS decision: 2026-09-22)

**Paper 4 IJSCCN editorial decision update:** 2026-09-24

**Paper 2 CEAS submission status update:** 2026-10-19 (prior TAES decision: 2026-09-26)

This is the canonical cross-publication handoff for the `mission-aware-satellite-cyber-recovery` repository. Historical preparation, venue-fit, freeze, and handoff records retain the wording that was true when they were created; this file records the actual current publisher state.

## Current publication portfolio

The repository has **four publication lines that have been submitted historically**. Paper 1 remains active with its publisher. Paper 2 was rejected at TAES editorial pre-screening 2026-09-26 without external review, then submitted in rebuilt RevB form to CEAS Space Journal on 2026-10-19; the confirmed portal status is Technical Check. Study 3/4/6 and S3X/S6X separately frozen evidence remain scientifically distinct. Paper 3 was rejected by CEAS Space Journal on 2026-09-22 after handling-editor assessment. The original Paper 4 / Study 8 submission was rejected by Acta Astronautica. Rebuilt Paper 4 integrates separately frozen Study 8 and Study 8E evidence and was submitted to the International Journal of Satellite Communications and Networking (IJSCCN) on 2026-09-22 as manuscript `4920969`. IJSCCN declined it at editorial screening on 2026-09-24 with the stated reason `out of scope`; no external reviewer reports were supplied and no scientific change follows from that decision. Paper 3's originally rejected Study-7-only CEAS package remains frozen. The separate Study 7E extension has since completed qualified cFS/NOS3 engineering gates, a standalone-cFS stack decision, a sealed canonical scientific execution, and a formal result freeze. Rebuilt Paper 3 (Study 7 + Study 7E, unpooled) is in an IJCIP-specific R3 preparation draft PR #168; it has not been submitted or merged.

### Paper 1 - Studies 1 + 2

- **Journal:** AIAA Journal of Aerospace Information Systems
- **Title:** Satellite Cyber Response and Trusted Recovery Under Contact and Adversarial Evidence Constraints
- **Manuscript ID:** `2026-09-I012066`
- **Submitted:** 2026-09-05
- **State:** `SUBMITTED__EDITORIAL_AND_PEER_REVIEW_WORKFLOW`
- **Authority:** `publication/Paper_1_Studies_1_2/Journal_of_Aerospace_Information_Systems/`

Study 1 and Study 2 remain separately frozen and must never be reported as one pooled statistical population.

### Paper 4 - Study 8

- **Journal:** Acta Astronautica
- **Title:** Contact-Aware Cryptographic Agility for Trusted Post-Compromise Recovery in Intermittently Connected Space Systems
- **Manuscript ID:** `AA-D-26-02872`
- **Submitted:** 2026-09-06
- **State:** `REJECTED__EDITORIAL_DECISION`
- **Decision recorded:** 2026-09-19
- **Decision detail:** no external reviewer reports were included; the editor stated that the topic was potentially of interest but the manuscript did not meet the journal's required quality standard
- **Authority:** `publication/Paper_4_Study_8/Acta_Astronautica/ACTA_SUBMISSION_STATUS.json`

Study 8 remains a separate deterministic finite modeled population of 3,456 positions. The frozen primary result remains `P3 - P1 = 0/1 = 0.000000 percentage points`. The editorial rejection does not change the frozen scientific record and does not identify a specific methodological defect. Study 8E is separately governed and formally frozen under `S8E-CANON-RESULTS-002-FREEZE-001`. The author selected **Study 8 + Study 8E -> rebuilt Paper 4** as the manuscript architecture; the two study populations remain separate and unpooled. Venue-neutral manuscript integration was executed in `publication/Paper_4_Study_8/Rebuilt_Study8_8E/` under explicit author authorization, with frozen science unchanged. IJSCCN was the locked retarget venue for the submitted R5 cycle; that venue lock is now historical because manuscript `4920969` was rejected at editorial screening on 2026-09-24 as `out of scope`.

#### Rebuilt Paper 4 - Study 8 + Study 8E

- **Journal:** International Journal of Satellite Communications and Networking
- **Publisher:** Wiley
- **Title:** Post-Quantum Trusted Recovery Under Intermittent Connectivity: Feasibility Across Modeled Contact Budgets and Public Observation-Opportunity Timing
- **Article type:** Original Paper
- **Manuscript ID:** `4920969`
- **Submitted:** 2026-09-22
- **Decision date:** 2026-09-24
- **State:** `REJECTED__EDITORIAL_SCREENING__OUT_OF_SCOPE__NO_EXTERNAL_REVIEW`
- **Decision detail:** the journal stated `out of scope`; no external reviewer reports or specific technical/methodological defects were supplied
- **Authority:** `publication/Paper_4_Study_8/IJSCCN/PACKAGE_STATUS.json`
- **Decision record:** `publication/Paper_4_Study_8/IJSCCN/R5_IJSCCN_EDITORIAL_DECISION_2026-09-24.md`

The IJSCCN decision does not alter Study 8, Study 8E, Results-002, TRACE-002, or any frozen scientific artifact. The submitted R5 package remains historical provenance. Wiley Transfer Desk suggestions may be reviewed as candidates only; no automatic transfer is authorized. The fresh venue-fit audit is recorded at `publication/Paper_4_Study_8/NEXT_VENUE_AUDIT_2026-09-24.md`; no new venue is locked.

### Paper 2 - Studies 3 + 4 + 6 (separate S3X/S6X qualification work)

**CURRENT: CEAS Space Journal RevB submission**

- **Title:** Residual Trust Boundaries in Satellite Cyber-Recovery Qualification: Temporal Evidence, Producer Composition, and Artifact Assurance
- **Sole corresponding author:** Aman Kumar Singh
- **Received:** 2026-10-19; portal version v1.0
- **Portal tracking ID:** `38cc76f5-ab6b-4b8e-b6ba-24727db86b48` (not independently verified as a journal-assigned manuscript number)
- **Status:** `SUBMISSION_RECEIVED__TECHNICAL_CHECK`; neither external peer review nor acceptance verified
- **Publisher manuscript:** `CEAS_Paper2_Manuscript_Final_2026-10-19_RevB.docx`
- **Seven-file author-local RevB ZIP SHA-256:** `cd58668c183cbfdf9a14be85159435d2d4224e25d353365a5f608d2c4f6ab64f`
- **Receipt authority:** [Issue #217](https://github.com/Zartharas/mission-aware-satellite-cyber-recovery/issues/217#issuecomment-6275866467)
- **Current handoff:** `publication/Paper_2_Studies_3_4_6/Post_Rejection_Rebuild/CEAS_REVB_SUBMISSION_HANDOFF_2026-10-19.md`
- **Publication source:** PR #216 OPEN/DRAFT/UNMERGED; not part of `main`

Publisher DOCX/PDF/ZIP and private evidence are deliberately Mac-local, not publicly committed. Optional Research Square In Review was selected; no posted preprint/DOI is verified. Preserve scientific limits: original Study 3 (1,380 deterministic trajectories), Study 4 (4,608 exact observations), Study 6 (420 observations) are frozen and **unpooled**. S3X comprises 1,919 ESA v2 timestamp **inter-sample timing proxies**, not observed RF outages. S6X provides separately frozen controlled-build research-fixture evidence, **two repetitions of 396 observations**, not spacecraft flight validation. The Study 3 accepted-original ZIP differs from the tracked auxiliary CSV; neither can be silently changed. Source/derivative rights and restricted evidence reviewer-access remain unresolved.

**HISTORICAL: rejected TAES initial submission**

- **Journal:** IEEE Transactions on Aerospace and Electronic Systems
- **Submitted:** 2026-09-07; `TAES-2026-4182`
- **Research Exchange UUID:** `cd1dfa89-4a24-4451-bdd4-af31ce3367f4`
- **Decision:** `REJECTED__EDITORIAL_PRESCREEN__NO_EXTERNAL_REVIEW` on 2026-09-26
- **Decision record:** `publication/Paper_2_Studies_3_4_6/IEEE_Transactions_on_Aerospace_and_Electronic_Systems/TAES_EDITORIAL_DECISION_2026-09-26.md`
- **Frozen source:** TAES R10 publisher package and core-study evidence preserved

Earlier Phase-1 through Phase-7F authorization and pre-execution gates were historical milestones that led to the submitted CEAS RevB cycle; they are **not current** permission restrictions. P2X draft PRs #214/#215 are separate prospective NOS3 work and not supporting evidence in the submitted article. Any later manuscript revision, public data release or new scientific experiment needs distinct authorization.

### Paper 3 - Study 7

- **Journal:** CEAS Space Journal
- **Title:** Observability Limits of Learned Satellite Cyber-Recovery Decisions Under Compromised Evidence
- **Article type:** Research
- **Topic:** Artificial Intelligence in Space
- **Peer review setting:** Single anonymous
- **Submission ID:** `6db04a31-8223-4aaf-af02-e4bafe06ef89`
- **Submission version:** `v.1.0`
- **Submitted:** 2026-09-13
- **Decision date:** 2026-09-22
- **State:** `REJECTED__EDITORIAL_ASSESSMENT`
- **Current authority:** `publication/Paper_3_Study_7/CEAS_Space_Journal/CEAS_SUBMISSION_STATUS.json`
- **Decision record:** `publication/Paper_3_Study_7/CEAS_Space_Journal/CEAS_EDITORIAL_DECISION_2026-09-22.md`
- **Recovery audit:** `publication/Paper_3_Study_7/Post_Rejection_Rebuild/PAPER3_CEAS_REJECTION_TO_RESEARCH_REQUIREMENTS_AUDIT_2026-09-22.md`

The handling editor recognized a relevant assurance concern and transparent, reproducible setup, but found the scientific contribution insufficiently developed. The decision specifically identified the directness of the central finding, absence of a concrete spacecraft recovery architecture, unvalidated trust assumptions, and lack of a deterministic policy receiving the same corroborating information as the learned policy.

Paper 3's rejected CEAS submission uses Study 7 only. The frozen Study-7 population remains exactly 1,033 modeled observations. The rejection does not alter or invalidate the frozen Study-7 scientific record.

Durable Study-7 evidence:

- Zenodo version DOI: `10.5281/zenodo.22732060`
- Zenodo concept DOI: `10.5281/zenodo.22732059`

The earlier `publication/Paper_3_Study_7/Journal_of_Aerospace_Information_Systems/` directory remains historical, unsubmitted Paper-3 development provenance only.

## Paper 3 post-rejection recovery — current Study 7E and IJCIP state

**Current as of 2026-10-20:** Study 7E is formally frozen and PR #167 was merged. The earlier 2026-09-22 protocol-draft/implementation-only gates below this branch's historical review files are not current execution restrictions. Read the exact-state [2026-10-20 Paper-3 handoff](../publication/Paper_3_Study_7/Post_Rejection_Rebuild/PAPER3_STUDY7E_CURRENT_HANDOFF_2026-10-20.md) before resuming.

- **Experiment:** `S7E-AERC-001`; architecture-grounded equal-information recovery comparators under correlated trust failures.
- **Corrected cFS Gate 1:** `PASS`, workflow run `35868263684`. Standalone cFS `v7.0.1` / `088b2fa828db9ff7e00733f1908e0eeb59f66ce3`. This proves limited cFE custom-app/Software Bus smoke, not complete recovery policy runtime.
- **Bounded NOS3 Gate 2:** `PASS`, workflow run `35870689230`. NOS3 `v1_07_05` / `5a3bdee6be9a2c67fdf994ae6db56d5c60395302`; no integrated Study 7E NOS3 runtime established.
- **Stack selected:** standalone NASA cFS v7.0.1 for the study; NOS3 retained as build-feasible reference, with no mixed dependency pins.
- **Protocol/environment/model/result:** frozen under `S7E-AERC-FREEZE-001`, `S7E-AERC-MODEL-FREEZE-001`, and `S7E-AERC-RESULT-FREEZE-001`.
- **Held-out scientific execution:** `S7E-AERC-HELDOUT-EXEC-001` sealed. E1 = 84, E2 = 104, C0 = 8, total **196 scenarios / 784 policy decisions**, 0 invalid, 0 independent-audit mismatches. Durable original archive SHA-256 `cc436ee98e20bb13643f58af738f42885b499a81bddad2766cb90f3e0860da35`.
- **PR #167:** merged as `740cc4984387b2c4f14b337b76d66198406f22c4` on 2026-09-24.
- **Rebuilt manuscript:** [PR #168](https://github.com/Zartharas/mission-aware-satellite-cyber-recovery/pull/168) **OPEN/DRAFT/UNMERGED** at `375aa5bc5808ddace8bb124df73eb184a61b9765`; head CI run `36012450683` SUCCESS.
- **Working venue:** International Journal of Critical Infrastructure Protection (IJCIP), targeted for preparation only. R3 path on PR #168: `publication/Paper_3_Study_7/Rebuilt_Study7_7E/IJCIP/PAPER3_IJCIP_MANUSCRIPT_R3.md`; preservation audit PASS. Journal-specific requirements still require live Guide/portal reconciliation after an earlier HTTP 403.
- **Next managed gate:** [Issue #221](https://github.com/Zartharas/mission-aware-satellite-cyber-recovery/issues/221), source/venue compliance and final DOCX/PDF/visual QA. Explicit separate author decisions required for PR #168 merge and publisher submission.

The original Study 7 uses 1,033 frozen modeled observations. It must **not** be pooled with Study 7E or silently amended. Neither study supports universal policy ranking, operational spacecraft performance, certification, or probabilistic reliability claims. No retraining, re-execution under the sealed ID, new evidence epoch or result edit is authorized by this status reconciliation.

## Current post-rejection Study 8 gate and Study 8E extension

**Immediate active publication-development priority:** for Paper 4, preserve the rejected IJSCCN R5 submission as immutable historical provenance, review any Wiley Transfer Desk suggestions without authorizing automatic transfer, and perform a fresh venue-fit audit against the actual Study 8 + Study 8E evidence boundaries. No scientific rerun or result modification is authorized by the IJSCCN scope decision.

The original frozen Study 8 science remains unchanged. The post-rejection forensic audit found no demonstrated defect in the original 3,456-position deterministic population. Study 8E was therefore developed as a separate external observation-opportunity timing extension rather than as a rewrite of the original experiment.

Historical post-rejection Study 8 audit records remain authoritative provenance for the original manuscript-only forensic and venue analysis:

- `publication/Paper_4_Study_8/POST_REJECTION_RESUBMISSION_HANDOFF_2026-09-19.md`
- `publication/Paper_4_Study_8/POST_REJECTION_FORENSIC_AUDIT_2026-09-19.md`
- `publication/Paper_4_Study_8/NEXT_VENUE_SHORTLIST_2026-09-19.md`

Current Paper-4 architecture/originality authority:

- `publication/Paper_4_Study_8/PAPER4_STUDY8_8E_ARCHITECTURE_AND_NONOVERLAP_GATE_2026-09-20.md`

This gate confirms publication independence from Paper 5 / Study 9 and protects Paper 5's semantic-interoperability/action-identifiability lane from Paper-4 manuscript drift.

Current Study 8E authority:

- `study8e/CURRENT_EXTENSION_STATE.md`
- `study8e/CANONICAL_RESULTS_002_FREEZE.json`
- `study8e/CANONICAL_RESULTS_002_AUDIT_HANDOFF.json`
- `study8e/NEW_CHAT_HANDOFF_20260920.md`

Corrected Study 8E evidence state:

- corrected population: `S8E-SATNOGS-POP-002`
- frozen external trace: `S8E-SATNOGS-TRACE-002`
- 20 satellite-station trace pairs
- 476 frozen SatNOGS observation rows
- canonical protocol: `S8E-CANON-EXEC-001`
- corrected runner: `S8E-CANON-RUNNER-004`
- corrected canonical workflow run: `35536583594`
- corrected result artifact: `10613372166`
- artifact ZIP SHA-256: `3e9c6c7899a9853682d29fa92ea37589c4684db49b16a0a289be054a3553bfee`
- corrected canonical cases: 65,376
- finite minimum-rate cases: 17,640
- non-finite cases: 47,736
- independent case mismatches: 0
- profile-burden ordering violations: 0

The first canonical result package from workflow run `35529423881` is invalidated and must not be used. A strict-before-horizon upper-bound defect misclassified 24 exact-divisibility cases. The corrected runner uses `floor(8B/d_min)+1` and independently audits that bound.

The corrected result package is **formally frozen** under `S8E-CANON-RESULTS-002-FREEZE-001`. One non-scientific package metadata inconsistency remains documented: the corrected `CANONICAL_FINDINGS.json` identifies `S8E-CANON-RESULTS-002`, while the immutable corrected artifact's `RESULTS_HASH_MANIFEST.json` retains the stale label `S8E-CANON-RESULTS-001`. The immutable artifact is not rewritten; exact corrected file hashes are bound by the pre-freeze audit and formal freeze records. No TRACE-002 rerun is authorized for metadata cleanup.

Current manuscript-integration plan authority:

- `publication/Paper_4_Study_8/REBUILT_STUDY8_8E_MANUSCRIPT_INTEGRATION_PLAN_2026-09-20.md`

Current integrated-manuscript authority:

- `publication/Paper_4_Study_8/Rebuilt_Study8_8E/MANUSCRIPT.md`
- `publication/Paper_4_Study_8/Rebuilt_Study8_8E/MANUSCRIPT_STATUS.json`
- `publication/Paper_4_Study_8/Rebuilt_Study8_8E/CLAIM_LEDGER.csv`
- `publication/Paper_4_Study_8/Rebuilt_Study8_8E/LITERATURE_REFRESH_2026-09-21.md`

Current author/scientific review authority:

- `publication/Paper_4_Study_8/Rebuilt_Study8_8E/AUTHOR_SCIENTIFIC_REVIEW_R1_2026-09-21.md`

Review decision: `AUTHOR_SCIENTIFIC_REVIEW_R1_PASS__READY_FOR_SEPARATE_LIVE_VENUE_ASSESSMENT_GATE`.

Current live venue assessment authority:

- `publication/Paper_4_Study_8/Rebuilt_Study8_8E/LIVE_VENUE_ASSESSMENT_R1_2026-09-21.md`

Assessment result: `LIVE_VENUE_ASSESSMENT_COMPLETE__IJSCCN_PREFERRED__VENUE_NOT_LOCKED`.

Historical IJSCCN venue-lock authority:

- `publication/Paper_4_Study_8/Rebuilt_Study8_8E/IJSCCN_VENUE_LOCK_2026-09-21.md`

Historical venue decision: `IJSCCN_LOCKED__CORE_PACKAGE_FROZEN__PUBLISHER_SUBMISSION_NOT_AUTHORIZED`.

Current IJSCCN submission/decision authority:

- `publication/Paper_4_Study_8/IJSCCN/README.md`
- `publication/Paper_4_Study_8/IJSCCN/PACKAGE_STATUS.json`
- `publication/Paper_4_Study_8/IJSCCN/R5_FINAL_SUBMISSION_RECORD_2026-09-22.md`
- `publication/Paper_4_Study_8/IJSCCN/R5_IJSCCN_EDITORIAL_DECISION_2026-09-24.md`

Current IJSCCN state: `IJSCCN_R5_REJECTED__OUT_OF_SCOPE__NO_EXTERNAL_REVIEW__NO_SCIENTIFIC_CHANGE`.

The repository-generated R1 package freeze, R5 preparation records, and local-private submission package remain immutable historical provenance. The final personalized R5 package remains local-only under ignored paths and must not be rewritten to simulate a different venue.

Current Paper 4 retarget state:

- no active venue is locked;
- the IJSCCN R5 submission is closed by editorial scope rejection;
- no external reviewer reports or specific technical/methodological defects were supplied;
- Study 8 and Study 8E remain frozen and unpooled;
- no scientific rerun or statistical reanalysis is authorized by the decision;
- Wiley Transfer Desk suggestions may be reviewed as candidates only;
- no automatic transfer is authorized;
- any future venue-specific derivative must be created as a new versioned Paper 4 cycle from current `main`.

Historical R5 continuity/provenance authority:

- `publication/Paper_4_Study_8/IJSCCN/NEW_CHAT_HANDOFF_2026-09-21_R5_REBUILD.md`
- `publication/Paper_4_Study_8/IJSCCN/SUBMISSION_CHECKLIST.md`
- `publication/Paper_4_Study_8/Rebuilt_Study8_8E/IJSCCN_PACKAGE_R1_FREEZE_2026-09-21.md`
- `publication/Paper_4_Study_8/Rebuilt_Study8_8E/IJSCCN_LOCAL_PRIVATE_SUBMISSION_PRIVACY_GATE_2026-09-21.md`

Current next gate:

1. preserve the submitted IJSCCN R5 manuscript and local publisher package unchanged as historical provenance;
2. inspect Wiley Transfer Desk recommendations if/when received, but do not authorize transfer automatically;
3. run a fresh live venue-fit audit centered on satellite/space systems, cybersecurity, post-quantum cryptography, trusted recovery/key-state transition, intermittent connectivity, and contact/opportunity modeling;
4. reject candidate venues that would require unsupported claims about RF throughput, link margin, BER/coding, CPU/PQC execution latency, energy, thermal behavior, operational spacecraft recovery time, or authenticated command-contact availability;
5. select a new venue only after scope and author-guideline verification;
6. create any new publisher-facing derivative on a fresh Paper 4 branch from current `main`;
7. require separate explicit author authorization before any new publisher submission or Wiley transfer.

Do not rerun TRACE-002 merely to clean the stale metadata label without a new explicit scientific-execution authorization. Do not modify the rejected Acta package or frozen original Study 8 evidence.

## Deferred independent publication work

Paper 3 already contains independently frozen Study 7 and Study 7E evidence; they remain separately scoped and must never be pooled or repurposed as fresh experimental observations. The current next gate concerns the draft IJCIP R3 publication package, not new Paper-3 science.

The remaining-study candidate audit remains separate while the Paper 4 / Study 8 + Study 8E fresh venue-fit audit is active, unless the author explicitly reprioritizes it. When resumed, it is a **read-only candidate audit** over the remaining eligible research lines. Known remaining work includes:

- Study 5 / `S5-CUCD-001`, a separately frozen portability/external-validity boundary study;
- any other demonstrably complete repository experiment not already consumed by Papers 1, 2, 3, or 4.

No next venue or manuscript package is currently locked. Candidate selection must verify scientific coherence, novelty, reproducibility, self-overlap risk, claim boundaries, and live venue fit before a new publication branch is created.

## Authority hierarchy

When records disagree, use this order:

1. per-study scientific freeze/provenance records for scientific facts;
2. exact submitted-state package and publisher-status record for a submitted paper;
3. this `docs/CURRENT_PUBLICATION_STATE.md` cross-publication handoff;
4. `tracker/PUBLICATION_STATE.csv`;
5. `tracker/RESEARCH_TRACKER.md`;
6. `docs/PUBLICATION_PHASE_MAP.md`;
7. `publication/README.md`;
8. historical preparation, venue-fit, freeze, work-package, and handoff records.

## Global safeguards

- Never silently pool separately frozen populations.
- Never rerun a frozen study merely to improve publication optics.
- Never modify submitted publisher-facing files unless the corresponding journal requests a technical correction or revision.
- Never convert logical model time into operational spacecraft time without new evidence.
- Never infer RF, flight, CPU, energy, ground-station, certification, or operational performance from modeled quantities.
- Same-repository separately implemented reproduction is reproducibility, not external empirical replication.
- Every future publisher submission requires separate explicit final author authorization.
- Before the next publication branch is created, verify `main` is clean and perform the candidate audit read-only.
