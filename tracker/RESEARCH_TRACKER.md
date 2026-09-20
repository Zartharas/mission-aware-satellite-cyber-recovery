# Research Tracker

Last updated: 2026-09-19

## Current focus

The repository now contains four submitted publication lines:

1. **Paper 1:** Studies 1 + 2, submitted to AIAA Journal of Aerospace Information Systems as manuscript `2026-09-I012066` on 2026-09-05.
2. **Paper 4:** Study 8, submitted to Acta Astronautica as manuscript `AA-D-26-02872` on 2026-09-06; rejected by editorial decision recorded 2026-09-19, with no external reviewer reports supplied and no specific methodological defect enumerated.
3. **Paper 2:** Studies 3 + 4 + 6, submitted to IEEE Transactions on Aerospace and Electronic Systems on 2026-09-07, Research Exchange UUID `cd1dfa89-4a24-4451-bdd4-af31ce3367f4`.
4. **Paper 3:** Study 7, submitted to CEAS Space Journal on 2026-09-13 as submission `6db04a31-8223-4aaf-af02-e4bafe06ef89`; current recorded portal state is `Technical check`.

Papers 1, 2, and 3 remain frozen pending journal action. The rejected Paper-4 Acta package remains frozen as provenance, while a controlled post-rejection manuscript-quality, literature/novelty, and venue-retargeting audit is authorized. No new scientific execution or statistical reanalysis is authorized by the rejection.

This is a journal/research publication workflow, not a dissertation-revision workflow.

## Current authorities

Use these current-state records before older preparation or work-package documents:

1. `docs/CURRENT_PUBLICATION_STATE.md`
2. `tracker/PUBLICATION_STATE.csv`
3. this `tracker/RESEARCH_TRACKER.md`
4. `docs/PUBLICATION_PHASE_MAP.md`
5. `publication/README.md`

For scientific facts, per-study freeze/provenance records remain authoritative. For submitted papers, exact submitted-state packages and publisher-status records take precedence over older venue-development material.

## Submitted publication state

### Paper 1 - Studies 1 + 2

- Journal: AIAA Journal of Aerospace Information Systems
- Manuscript ID: `2026-09-I012066`
- Submitted: 2026-09-05
- State: `SUBMITTED__EDITORIAL_AND_PEER_REVIEW_WORKFLOW`
- Authority: `publication/Paper_1_Studies_1_2/Journal_of_Aerospace_Information_Systems/`

Study 1 and Study 2 remain separate frozen populations.

### Paper 4 - Study 8

- Journal: Acta Astronautica
- Manuscript ID: `AA-D-26-02872`
- Submitted: 2026-09-06
- Current recorded state: `REJECTED__EDITORIAL_DECISION`
- Decision recorded: 2026-09-19
- Decision detail: no external reviewer reports were included in the supplied letter; the editor stated that the topic was potentially of interest but the manuscript did not meet the journal's required quality standard
- Authority: `publication/Paper_4_Study_8/Acta_Astronautica/ACTA_SUBMISSION_STATUS.json`
- Decision provenance: `publication/Paper_4_Study_8/Acta_Astronautica/EDITORIAL_DECISION_REJECTED_2026-09-19.md`

Study 8 remains a separate deterministic finite modeled population of 3,456 positions. Its frozen primary result remains `P3 - P1 = 0/1 = 0.000000 percentage points`. The editorial rejection does not alter the frozen scientific record.

The next Study 8 gate is a controlled forensic manuscript/venue audit before retargeting. No fallback venue is automatically selected, and no scientific rerun or statistical reanalysis is authorized by the editorial decision.

### Paper 2 - Studies 3 + 4 + 6

- Journal: IEEE Transactions on Aerospace and Electronic Systems
- Submitted: 2026-09-07
- Research Exchange UUID: `cd1dfa89-4a24-4451-bdd4-af31ce3367f4`
- State: `R10_INITIAL_SUBMISSION_COMPLETE__UNDER_EDITORIAL_PROCESSING`
- Authority: `publication/Paper_2_Studies_3_4_6/IEEE_Transactions_on_Aerospace_and_Electronic_Systems/TAES_PACKAGE_STATUS.json`

Paper 2 uses Studies 3, 4, and 6 only and keeps all three frozen populations separate.

### Paper 3 - Study 7

- Journal: CEAS Space Journal
- Title: **Observability Limits of Learned Satellite Cyber-Recovery Decisions Under Compromised Evidence**
- Article type: Research
- Topic: Artificial Intelligence in Space
- Submission ID: `6db04a31-8223-4aaf-af02-e4bafe06ef89`
- Submission version: `v.1.0`
- Submitted: 2026-09-13
- Current recorded state: `SUBMITTED__TECHNICAL_CHECK`
- Current authority: `publication/Paper_3_Study_7/CEAS_Space_Journal/CEAS_SUBMISSION_STATUS.json`
- Initial-submission record: `publication/Paper_3_Study_7/CEAS_Space_Journal/CEAS_INITIAL_SUBMISSION_RECORD_2026-09-13.md`

Study 7 / `S7-LSO-001` remains an exact finite modeled population of 1,033 observations. The submitted manuscript uses Study 7 only.

Durable archive:

- Zenodo version DOI: `10.5281/zenodo.22732060`
- Zenodo concept DOI: `10.5281/zenodo.22732059`

The historical Paper-3 JAIS directory is unsubmitted development provenance only and is superseded by the CEAS submission package.

## Remaining eligible publication candidates

### Study 5 / S5-CUCD-001

Study 5 remains a portability/external-validity boundary study. Its publication vehicle remains deferred. It must not be represented as external empirical validation of Studies 3, 4, 6, or 7, and it must not be reported as measuring IDS accuracy, recall, false-positive rate, or packet-level recovery effectiveness because those outcomes were not measured.

### Other remaining studies

Any other repository study or experiment may enter the next-paper candidate audit only if it is demonstrably complete, provenance-bound, scientifically independent, and not already consumed as experimental evidence by Papers 1, 2, 3, or 4.

## Current exact action

The active publication-development gate is:

`POST_REJECTION_STUDY8_MANUSCRIPT_AND_VENUE_AUDIT`

Canonical handoff:

`publication/Paper_4_Study_8/POST_REJECTION_RESUBMISSION_HANDOFF_2026-09-19.md`

Required sequence:

1. verify clean canonical `main` and record its HEAD SHA;
2. inspect the exact rejected Acta manuscript and package without modifying those provenance files;
3. perform a claim-by-claim forensic manuscript-quality audit against frozen Study 8 evidence;
4. identify presentation, framing, literature, explanatory-depth, figure/table, and discussion improvements that do not require new science;
5. explicitly distinguish audit findings from hypotheses about why Acta rejected the paper, because the editor did not provide a specific technical defect;
6. perform a fresh live literature and novelty review;
7. perform a fresh live venue review and produce a shortlist with fit and reviewer-risk reasoning;
8. determine whether the frozen science is sufficient for controlled resubmission;
9. present the recommended venue and revision plan to the author before locking a new venue-specific package;
10. retain final publisher submission as a separate explicit author-authorization gate.

**Terminology safeguard:** Paper 4 is the Study 8 publication. Study 4 / `S4-MPQ-001` is a different frozen experiment already included in submitted Paper 2 / TAES. Do not modify or rerun Study 4 as part of this Paper-4 resubmission workflow.

The remaining-study publication-candidate audit, including Study 5, is deferred while this Paper-4 retargeting gate is active unless the author explicitly reprioritizes it.

## Scientific and responsible-research boundaries

Preserve throughout all future publication and revision work:

- controlled defensive software simulation/modeling only;
- no real spacecraft access;
- no RF transmission/interference claim;
- immutable research truth never acts as a runtime policy oracle;
- no post-hoc seed replacement, outcome-dependent exclusion, or new campaign execution to improve publication results;
- no weighted global score or universal global policy rank unless prospectively defined by a new study;
- separately frozen study populations remain separate unless a new prospectively authorized analysis explicitly permits pooling;
- same-repository separately implemented reproduction is reproducibility, not external empirical replication;
- logical model time is not operational spacecraft time;
- modeled cryptographic-object bytes are not measured onboard CPU, energy, or RF cost;
- no operational spacecraft, RF, flightworthiness, ground-station, certification, or production claim is supported without new frozen evidence.

## Repository-governance rule after submissions

After each publisher submission gate, update the cross-repository current-state layer in the same closeout cycle:

- `docs/CURRENT_PUBLICATION_STATE.md`
- `docs/PUBLICATION_PHASE_MAP.md`
- `publication/README.md`
- `tracker/RESEARCH_TRACKER.md`
- `tracker/PUBLICATION_STATE.csv`

Venue-package closeout alone is not sufficient if these global current-state surfaces still advertise a superseded publication state.
