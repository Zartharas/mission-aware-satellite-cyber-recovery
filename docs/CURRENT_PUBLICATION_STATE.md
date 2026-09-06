# Current Publication State

**Current-state date:** 2026-09-06

This is the canonical cross-publication handoff for the `mission-aware-satellite-cyber-recovery` repository. Read this file before using older preparation, freeze, handoff, venue-fit, or submission-control documents.

Historical records remain intentionally preserved with the stage-local wording that was true when they were created. They must not be rewritten merely to look current.

## Submitted publications

### Paper 1 - Studies 1 + 2

**Journal:** AIAA Journal of Aerospace Information Systems  
**Title:** Satellite Cyber Response and Trusted Recovery Under Contact and Adversarial Evidence Constraints  
**Manuscript ID:** `2026-09-I012066`  
**Submission date:** 2026-09-05  
**State:** submitted; editorial/peer-review workflow pending

Canonical submitted-state package:

`publication/Paper_1_Studies_1_2/Journal_of_Aerospace_Information_Systems/`

Study 1 and Study 2 remain separately frozen and are not pooled into one statistical population.

### Paper 4 - Study 8

**Journal:** Acta Astronautica  
**Title:** Contact-Aware Cryptographic Agility for Trusted Post-Compromise Recovery in Intermittently Connected Space Systems  
**Manuscript ID:** `AA-D-26-02872`  
**Article type:** Research paper  
**Submission date:** 2026-09-06  
**Current status:** `With Editor`

Canonical submitted-state authority:

`publication/Paper_4_Study_8/Acta_Astronautica/README_CURRENT.md`

Machine-readable status:

`publication/Paper_4_Study_8/Acta_Astronautica/ACTA_SUBMISSION_STATUS.json`

Exact submitted package freeze:

`S8-ACTA-PKGFREEZE-002`

Submitted package source commit:

`f5e9a1d4553737e534821bf647463abfd44fa0dd`

The five publisher-facing files must not be modified while the submission is active unless Acta explicitly requests a revision.

Study 8 remains a complete deterministic finite modeled population of 3,456 positions. The frozen primary result remains `P3 - P1 = 0/1 = 0.000000 percentage points`. No scientific reexecution or statistical reanalysis was performed for submission.

## Next unsent publication work

The next publication-development priority is **Paper 2: Studies 3 + 4 + 6**.

Working theme:

**Evidence-plane trust composition for intermittent-contact trusted recovery.**

Required starting sequence:

1. verify the frozen scientific state and provenance of Studies 3, 4, and 6 independently;
2. do not pool their statistical populations;
3. perform a fresh literature, novelty, overlap, claim-boundary, and live venue review;
4. decide whether Study 5 belongs as a clearly separated portability/external-validity component or remains deferred;
5. obtain explicit author approval before locking a venue or beginning a venue-specific package;
6. preserve all null, negative, and conditional findings;
7. do not rerun or enlarge frozen studies to improve publication optics.

Candidate venues remain planning inputs only until rechecked live. Historical candidates include IEEE Systems Journal, Acta Astronautica, and AIAA Journal of Aerospace Information Systems.

## Later publication work

### Paper 3 - Study 7

Study 7 / `S7-LSO-001` remains a separate frozen publication line focused on observability limits of learned recovery selectors under trusted-producer compromise.

Before manuscript development, perform a fresh AI/autonomy literature and live venue review. Do not frame the frozen results as generic ML superiority.

### Study 5

Study 5 / `S5-CUCD-001` remains a portability/external-validity boundary study. Its final publication vehicle is not yet locked.

Do not claim IDS accuracy, recall, false-positive rate, or packet-level recovery effectiveness from Study 5 because those outcomes were not measured.

## Authority hierarchy

When documents disagree, use this order:

1. per-study scientific freeze/provenance records;
2. exact submitted-state package for an already submitted paper;
3. this `docs/CURRENT_PUBLICATION_STATE.md` cross-publication handoff;
4. `docs/PUBLICATION_PHASE_MAP.md` for operational sequencing;
5. current repository/publication READMEs;
6. historical preparation, venue-fit, authorization, freeze, and handoff documents.

For Study 8 specifically, `publication/study8/PUBLICATION_DEVELOPMENT_STATUS.json` intentionally remains the historical source-package freeze authority. It is not the live publisher-status authority after Acta submission.

Similarly, `publication/Paper_4_Study_8/Acta_Astronautica/ACTA_PACKAGE_FREEZE_MANIFEST.json`, `ACTA_PACKAGE_STATUS.json`, `README_SUBMISSION.md`, `SUBMISSION_CHECKLIST.md`, `EDITORIAL_MANAGER_SUBMISSION_VALUES.md`, and `UPLOAD_FILES.md` retain the pre-submission freeze-002 state by design. Use `README_CURRENT.md` and `ACTA_SUBMISSION_STATUS.json` for the live Acta state.

## Global safeguards

- Never silently pool separately frozen populations.
- Never rerun a frozen study to obtain a more publishable result.
- Never change submitted publisher-facing files unless the journal requests a revision.
- Never convert logical model time into operational spacecraft time without new evidence.
- Never infer RF, flight, CPU, energy, ground-station, or operational performance from modeled quantities.
- Same-repository independently written reproduction is reproducibility, not external replication.
- Every future publisher submission requires a separate explicit final author authorization.
