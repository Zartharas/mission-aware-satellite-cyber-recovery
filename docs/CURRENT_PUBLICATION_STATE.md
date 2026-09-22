# Current Publication State

**Current-state date:** 2026-09-19

**Study 8E extension update:** 2026-09-20

**Paper 4 IJSCCN package-freeze update:** 2026-09-21

**Paper 4 IJSCCN privacy-hardening update:** 2026-09-21

**Paper 4 IJSCCN R5 rebuild-gate update:** 2026-09-21

**Paper 3 CEAS decision/recovery update:** 2026-09-22

This is the canonical cross-publication handoff for the `mission-aware-satellite-cyber-recovery` repository. Historical preparation, venue-fit, freeze, and handoff records retain the wording that was true when they were created; this file records the actual current publisher state.

## Current publication portfolio

The repository has **four publication lines that have been submitted historically**. Papers 1 and 2 remain active with their publishers. Paper 3 was rejected by CEAS Space Journal on 2026-09-22 after handling-editor assessment. The original Paper 4 / Study 8 submission was rejected by Acta Astronautica. Rebuilt Paper 4 now integrates separately frozen Study 8 and Study 8E evidence, is locked to the International Journal of Satellite Communications and Networking (IJSCCN), and has a frozen repository-generated core submission package. Publisher submission is not authorized. Paper 3 has entered a separately authorized post-rejection research-requirements phase; no Study-7 rerun or Study-7E execution is authorized.

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

Study 8 remains a separate deterministic finite modeled population of 3,456 positions. The frozen primary result remains `P3 - P1 = 0/1 = 0.000000 percentage points`. The editorial rejection does not change the frozen scientific record and does not identify a specific methodological defect. Study 8E is separately governed and formally frozen under `S8E-CANON-RESULTS-002-FREEZE-001`. The author selected **Study 8 + Study 8E -> rebuilt Paper 4** as the manuscript architecture; the two study populations remain separate and unpooled. Venue-neutral manuscript integration was executed in `publication/Paper_4_Study_8/Rebuilt_Study8_8E/` under explicit author authorization, with frozen science unchanged. IJSCCN is now the locked retarget venue, and the repository-generated core IJSCCN package is frozen under `P4-IJSCCN-PKG-R1-FREEZE-001`.

### Paper 2 - Studies 3 + 4 + 6

- **Journal:** IEEE Transactions on Aerospace and Electronic Systems
- **Title:** Residual Trust Boundaries in Satellite Cyber Recovery: Temporal Evidence, Producer Composition, and Artifact Assurance
- **Article type:** Regular Paper
- **Submitted:** 2026-09-07
- **Research Exchange UUID:** `cd1dfa89-4a24-4451-bdd4-af31ce3367f4`
- **State:** `R10_INITIAL_SUBMISSION_COMPLETE__UNDER_EDITORIAL_PROCESSING`
- **Authority:** `publication/Paper_2_Studies_3_4_6/IEEE_Transactions_on_Aerospace_and_Electronic_Systems/TAES_PACKAGE_STATUS.json`

Paper 2 keeps three separate frozen populations: Study 3 = 1,380 deterministic trajectories; Study 4 = 4,608 exact rule-by-subset observations; Study 6 = 420 exact observations. There is no pooled Paper-2 sample size.

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

## Paper 3 post-rejection recovery gate

The author explicitly authorized a rejection-to-research-requirements audit on 2026-09-22.

Audit result: `NEW_PROSPECTIVE_EXTENSION_REQUIRED`.

Proposed extension:

- **Experiment ID:** `S7E-AERC-001`
- **Working title:** Architecture-Grounded Equal-Information Recovery Comparators Under Correlated Trust Failures
- **Status:** `PROTOCOL_DRAFT_COMPLETE__AUTHOR_REVIEW_REQUIRED__EXECUTION_NOT_AUTHORIZED`
- **Proposal:** `publication/Paper_3_Study_7/Post_Rejection_Rebuild/STUDY7E_AERC_PROSPECTIVE_EXTENSION_PROPOSAL_2026-09-22.md`

The extension now has a draft prospective protocol, implementation plan, test/audit plan, architecture source ledger, and candidate environment baseline. The design uses a cFS-grounded reference architecture, five explicit trust-domain topologies, twelve fault/compromise profiles, and equal-information deterministic/learned policy pairs.

Prospective design quantities are 84 training architecture scenarios and 176 canonical evaluation/control scenarios, producing 704 canonical evaluation policy-decision observations. The complete manifest remains 260 scenarios. These are planned counts, not scientific results.

No `study7e/` execution workspace, canonical run, or new scientific result is authorized yet. Study 7 and any future Study 7E remain separate populations and must not be pooled.

## Current post-rejection Study 8 gate and Study 8E extension

**Immediate active publication-development priority:** complete a fresh, live IJSCCN/Wiley submission-policy audit and rebuild the publisher-facing Paper 4 package as **R5**. The prior repository R1 package remains frozen historical provenance. The local R4.x personalized derivatives are not tracked; author review rejected R4.3 as a submission candidate because its manuscript presentation did not meet the required professional journal standard. The author photograph has been supplied locally under the privacy boundary. Publisher submission remains unauthorized.

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

Current venue-lock authority:

- `publication/Paper_4_Study_8/Rebuilt_Study8_8E/IJSCCN_VENUE_LOCK_2026-09-21.md`

Venue decision: `IJSCCN_LOCKED__CORE_PACKAGE_FROZEN__PUBLISHER_SUBMISSION_NOT_AUTHORIZED`.

Current IJSCCN package authority:

- `publication/Paper_4_Study_8/IJSCCN/README.md`
- `publication/Paper_4_Study_8/IJSCCN/PACKAGE_STATUS.json`
- `publication/Paper_4_Study_8/IJSCCN/SUBMISSION_CHECKLIST.md`

Current package state: `P4-IJSCCN-PKG-R1-FREEZE-001`. The pre-privacy repository-generated package was bound to workflow run `35632266523`, artifact `10655615285`, digest `sha256:ddc3642d936df1c596cc759ee52c4236b337b52a39aa07410505af88f5713b37`. That artifact is historical package provenance only and is superseded for submission handling by the local-private privacy gate because it was generated before tracked author-contact metadata was removed. Personalized upload-ready materials are now local-only and ignored by Git.

Current R5 rebuild state:

- repository R1 package remains immutable historical/public-safe provenance;
- the rejected Acta Astronautica submitted manuscript remains immutable and may be consulted only as a visual-quality benchmark;
- local R4.3 is explicitly **not approved for Wiley upload**;
- R5 is a new controlled publisher-facing derivative, not a scientific rerun;
- R5 must preserve the current integrated Study 8 + Study 8E scientific text and all frozen evidence boundaries;
- R5 must be validated against the live IJSCCN Author Guidelines, Wiley manuscript-preparation guidance, and Wiley submission/peer-review guidance before document generation;
- journal-specific IJSCCN instructions control over generic Wiley guidance when they conflict;
- the final personalized R5 package must remain under ignored local-private/local-submission paths;
- final Wiley submission still requires separate explicit author authorization.

R5 continuity authority:

- `publication/Paper_4_Study_8/IJSCCN/NEW_CHAT_HANDOFF_2026-09-21_R5_REBUILD.md`
- `publication/Paper_4_Study_8/IJSCCN/SUBMISSION_CHECKLIST.md`

Current package-freeze authority:

- `publication/Paper_4_Study_8/Rebuilt_Study8_8E/IJSCCN_PACKAGE_R1_FREEZE_2026-09-21.md`

Current privacy/local-submission authority:

- `publication/Paper_4_Study_8/Rebuilt_Study8_8E/IJSCCN_LOCAL_PRIVATE_SUBMISSION_PRIVACY_GATE_2026-09-21.md`

Current next gate:

1. perform a fresh live-policy audit of the IJSCCN Author Guidelines and every submission-relevant linked Wiley page, including manuscript preparation and submission/peer review;
2. create a requirement matrix that distinguishes mandatory journal-specific rules, live portal requirements, generic Wiley guidance, and recommendations;
3. rebuild the manuscript and all publisher-facing submission documents as R5 with professional scholarly formatting, using the immutable Acta manuscript only as a visual-quality reference;
4. perform scientific-preservation checks, page-by-page render QA, figure/table QA, data/citation/AI/ethics QA, and privacy validation;
5. generate the final personalized package only under the ignored local-submission directory;
6. map exact R5 files to the Wiley portal only after all gates pass;
7. require separate explicit final author authorization before completing publisher submission.

Do not rerun TRACE-002 merely to clean the stale metadata label without a new explicit scientific-execution authorization. Do not modify the rejected Acta package or frozen original Study 8 evidence.

## Deferred independent publication work

Paper 3 is now a separately authorized post-rejection recovery workstream. Study 7 remains frozen and consumed by the Paper-3 line; it must not be reused as new experimental evidence elsewhere. Any new Paper-3 evidence must come from a separately prospectively designed extension such as proposed `S7E-AERC-001`.

The remaining-study candidate audit is deferred while the Paper 4 / Study 8 post-rejection resubmission audit is active, unless the author explicitly reprioritizes it. When resumed, it is a **read-only candidate audit** over the remaining eligible research lines. Known remaining work includes:

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
