# Current Publication State

**Current-state date:** 2026-09-19

This is the canonical cross-publication handoff for the `mission-aware-satellite-cyber-recovery` repository. Historical preparation, venue-fit, freeze, and handoff records retain the wording that was true when they were created; this file records the actual current publisher state.

## Current publication portfolio

The repository has **four publication lines that have been submitted**. Papers 1, 2, and 3 remain active with their publishers. Paper 4 / Study 8 was rejected by Acta Astronautica and is frozen pending a controlled post-rejection audit and retargeting decision.

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

Study 8 remains a separate deterministic finite modeled population of 3,456 positions. The frozen primary result remains `P3 - P1 = 0/1 = 0.000000 percentage points`. The editorial rejection does not change the frozen scientific record and does not identify a specific methodological defect.

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
- **Peer review:** Single anonymous
- **Submission ID:** `6db04a31-8223-4aaf-af02-e4bafe06ef89`
- **Submission version:** `v.1.0`
- **Submitted:** 2026-09-13
- **State:** `SUBMITTED__TECHNICAL_CHECK`
- **Current authority:** `publication/Paper_3_Study_7/CEAS_Space_Journal/CEAS_SUBMISSION_STATUS.json`
- **Initial-submission record:** `publication/Paper_3_Study_7/CEAS_Space_Journal/CEAS_INITIAL_SUBMISSION_RECORD_2026-09-13.md`

Paper 3 uses Study 7 only. The frozen Study-7 population is exactly 1,033 modeled observations. No Study-5 observations or other study populations are part of the CEAS paper.

Durable Study-7 evidence:

- Zenodo version DOI: `10.5281/zenodo.22732060`
- Zenodo concept DOI: `10.5281/zenodo.22732059`

The earlier `publication/Paper_3_Study_7/Journal_of_Aerospace_Information_Systems/` directory is historical, unsubmitted Paper-3 development provenance only. It is superseded by the CEAS package and must not be treated as a current venue package.

## Current post-rejection Study 8 gate

**Immediate active publication-development priority:** Paper 4 / Study 8 post-rejection improvement and retargeting audit.

Paper 4 / Study 8 is eligible for a controlled retargeting audit. No fallback venue is automatically activated. Before a new venue is selected, perform a forensic quality review of the exact submitted manuscript, distinguish presentation/venue-fit issues from scientific limitations, and perform a fresh live literature and venue review. Do not rerun or reanalyze the frozen study merely to improve publication prospects.

Canonical resubmission handoff:

`publication/Paper_4_Study_8/POST_REJECTION_RESUBMISSION_HANDOFF_2026-09-19.md`

The current authorization covers forensic manuscript review, literature/novelty review, manuscript-improvement planning, and venue research/shortlisting. It does not authorize new scientific execution, statistical reanalysis outside the frozen plan, final venue lock, or publisher submission.

**Terminology:** Paper 4 is the Study 8 publication. Study 4 / `S4-MPQ-001` is a different frozen study already included in submitted Paper 2 / TAES and is not part of this resubmission task.

## Deferred independent publication work

Paper 3 is no longer a candidate or development item. Study 7 is consumed by the submitted CEAS paper and must not be reused as new experimental evidence in another publication.

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
