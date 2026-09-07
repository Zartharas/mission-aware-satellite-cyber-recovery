# Research Tracker

Last updated: 2026-09-07

## Current focus

The repository now contains three submitted publication lines:

1. Paper 1: Studies 1 + 2, submitted to the AIAA Journal of Aerospace Information Systems as manuscript `2026-09-I012066` on 2026-09-05.
2. Roadmap Paper 4: Study 8, submitted to Acta Astronautica as manuscript `AA-D-26-02872` on 2026-09-06; current recorded publisher state is `With Editor`.
3. Paper 2: Studies 3 + 4 + 6, submitted to IEEE Transactions on Aerospace and Electronic Systems on 2026-09-07 as initial-submission revision R10, Research Exchange UUID `cd1dfa89-4a24-4451-bdd4-af31ce3367f4`.

All three submitted publication lines are frozen pending journal action. No new scientific execution, result substitution, manuscript modification, or publisher-facing package modification is authorized for those papers unless the corresponding journal requests a revision.

The next repository publication action is **not** automatic Paper-3 manuscript drafting. It is a read-only candidate audit over the remaining eligible studies and experiments from clean `main`.

This is a journal/research publication workflow, not a dissertation-revision workflow.

## Canonical current-state authorities

Use these current-state records before older preparation or work-package documents:

1. `docs/CURRENT_PUBLICATION_STATE.md`
2. `tracker/PUBLICATION_STATE.csv`
3. this `tracker/RESEARCH_TRACKER.md`
4. `docs/PUBLICATION_PHASE_MAP.md`
5. `publication/README.md`

For scientific facts, per-study freeze/provenance records remain authoritative. For submitted papers, exact submitted-state packages and publisher-status records take precedence over older venue-preparation files.

## Submitted publication state

### Paper 1 - Studies 1 + 2

**Journal:** AIAA Journal of Aerospace Information Systems  
**Title:** Satellite Cyber Response and Trusted Recovery Under Contact and Adversarial Evidence Constraints  
**Manuscript ID:** `2026-09-I012066`  
**Submitted:** 2026-09-05  
**State:** `SUBMITTED__EDITORIAL_AND_PEER_REVIEW_WORKFLOW`

Canonical submitted-state package:

`publication/Paper_1_Studies_1_2/Journal_of_Aerospace_Information_Systems/`

Paper-1 scientific populations remain separate:

- Study 1: 720 VALID observations across 24 frozen cells; 9 retained INVALID attempts outside statistical membership.
- Study 2 / `S2-AEATR-001`: 3,872 VALID observations across 85 cells; 0 INVALID attempts; 162 primary paired contrasts; 432 prespecified secondary contrasts; independent reproduction with 0 mismatches.

Study-1 Zenodo version DOI: `10.5281/zenodo.22181540`.
Study-2 Zenodo version DOI: `10.5281/zenodo.22289114`.

No pooled Paper-1 statistical population is defined.

### Roadmap Paper 4 - Study 8

**Journal:** Acta Astronautica  
**Title:** Contact-Aware Cryptographic Agility for Trusted Post-Compromise Recovery in Intermittently Connected Space Systems  
**Manuscript ID:** `AA-D-26-02872`  
**Submitted:** 2026-09-06  
**Current recorded publisher state:** `With Editor`

Canonical submitted-state authority:

- `publication/Paper_4_Study_8/Acta_Astronautica/README_CURRENT.md`
- `publication/Paper_4_Study_8/Acta_Astronautica/ACTA_SUBMISSION_STATUS.json`

Study 8 / `S8-PQC-ICR-001` remains a deterministic finite modeled population of 3,456 positions. Same-repository independently written reproduction matched 3,456/3,456 rows with 0 mismatches.

Frozen primary policy result:

`P3 - P1 = 0/1 = 0.000000 percentage points`

The negative primary result is immutable and must not be rescued or reframed as policy superiority.

### Paper 2 - Studies 3 + 4 + 6

**Journal:** IEEE Transactions on Aerospace and Electronic Systems  
**Article type:** Regular Paper  
**Primary Technical Area:** Aerospace Information Systems  
**Title:** Residual Trust Boundaries in Satellite Cyber Recovery: Temporal Evidence, Producer Composition, and Artifact Assurance  
**Submitted:** 2026-09-07  
**Research Exchange submission UUID:** `cd1dfa89-4a24-4451-bdd4-af31ce3367f4`  
**Formal TAES manuscript ID:** pending / not yet shown in the captured post-submission state  
**State:** `R10_INITIAL_SUBMISSION_COMPLETE__UNDER_EDITORIAL_PROCESSING`

Canonical submitted-state package:

`publication/Paper_2_Studies_3_4_6/IEEE_Transactions_on_Aerospace_and_Electronic_Systems/`

Current state authority:

- `TAES_PACKAGE_STATUS.json`
- `TAES_INITIAL_SUBMISSION_RECORD_2026-09-07.md`
- `TAES_REVIEWER_PDF_INITIAL_SUBMISSION_2026-09-07.pdf`

Exact reviewer PDF SHA-256:

`34c4691381fe521bbd161f34878a33c82799abae18bd62dafab5ac7b2e05327c`

Exact normalized initial-submission record SHA-256:

`3a23567db6c68d4e7541b9d7cfa65acda6f6c4e0f980ca67d7b06c669d7b346d`

Paper-2 populations remain separate:

- Study 3 / `S3-K4E-001`: 1,380 deterministic trajectories.
- Study 4 / `S4-MPQ-001`: 4,608 exact rule-by-subset observations.
- Study 6 / `S6-SCTR-001`: 420 exact observations.

No pooled Paper-2 `N = 6,408` is scientifically defined.

The historical branch `paper2/taes-10-page-compression` is frozen as:

`SUPERSEDED_UNSUBMITTED__R10_INITIAL_SUBMISSION_COMPLETED_2026-09-07`

It is historical publication-development provenance only. It was not the package submitted to TAES.

## Remaining eligible publication candidates

### Study 7 / S7-LSO-001

Study 7 remains a separately frozen learned-selector study with 1,033 observations.

Historical working theme:

**Observability limits of learned recovery selectors under trusted-producer compromise.**

The study is a credible next-paper candidate but is not automatically selected. Before publication development it requires fresh AI/autonomy literature review, novelty and overlap audit, claim-boundary review, reproducibility review, and live venue review.

Do not frame its frozen results as generic ML superiority.

### Study 5 / S5-CUCD-001

Study 5 remains a portability/external-validity boundary study and was not part of Paper 2.

Its final publication vehicle is still deferred. It must not be represented as external empirical validation of Studies 3, 4, or 6 and must not be reported as measuring IDS accuracy, recall, false-positive rate, or packet-level recovery effectiveness because those outcomes were not measured.

### Other remaining studies

Any other repository study or experiment may enter the next-paper candidate audit only if it is demonstrably complete, provenance-bound, scientifically independent, and not already consumed as experimental evidence by Papers 1, 2, or 4.

## Current exact action

The next publication gate is:

`READ_ONLY_REMAINING_STUDY_PUBLICATION_CANDIDATE_AUDIT`

Required steps:

1. verify clean canonical `main` and its HEAD SHA;
2. inventory every remaining study or experiment not consumed by Papers 1, 2, or 4;
3. verify frozen populations, endpoints, null/negative findings, provenance, reproducibility, and validity limits;
4. evaluate scientific coherence and whether any studies can be combined without violating independence;
5. perform fresh literature, novelty, and self-overlap review;
6. rank candidate publication units by evidence strength, aerospace relevance, cybersecurity contribution, methodological defensibility, reviewer risk, and venue fit;
7. identify the strongest candidate plus at least one credible alternative;
8. perform a devil's-advocate review before venue recommendation;
9. create a new publication branch only after the candidate boundary is explicitly selected and the author authorizes the write phase.

No new manuscript drafting, study rerun, new statistics, or venue-specific package creation is authorized by this tracker before that candidate audit.

## Historical Study-1 work-package register

`tracker/work_packages.csv` remains the historical WP0-WP11 Study-1 register. Those work packages are closed and should not be renumbered or rewritten into a publication state machine.

The old WP0-WP11 state remains useful provenance, but it is not the current cross-publication tracker.

Current publication-level machine-readable state is now maintained separately in:

`tracker/PUBLICATION_STATE.csv`

This separation prevents closed Study-1 engineering work packages from being confused with current journal submission state.

## Scientific and responsible-research boundaries

Preserve throughout all future publication and revision work:

- controlled defensive software simulation/modeling only;
- no real spacecraft access;
- no RF transmission/interference claim;
- no real ground-contact, network, or operator timing claim;
- immutable research truth never acts as a runtime policy oracle;
- unexpected treatment-valid outcomes remain evidence rather than being removed for presentation;
- no post-hoc seed replacement, outcome-dependent exclusion, or new campaign execution to improve publication results;
- no weighted global score or universal global policy rank unless prospectively defined by a new study;
- Study 1 and Study 2 remain separate populations;
- Study 8 remains a separate deterministic finite modeled population;
- Paper 2 uses Studies 3, 4, and 6 only and keeps their populations separate;
- only Study 3 directly models intermittent contact in Paper 2;
- Study-4 producer unavailability is not orbital contact loss or mission availability;
- Study-6 assurance-signal unavailability is not contact loss;
- Study-4 provenance domains are synthetic independence classes;
- Study 4 is not a Byzantine-consensus experiment;
- Study 6 is an abstract artifact-trust model, not an operational supply-chain attack experiment;
- same-repository independently written reproduction is reproducibility, not external empirical replication;
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
