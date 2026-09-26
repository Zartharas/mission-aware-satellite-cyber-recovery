# Research Tracker

Last updated: 2026-09-26

## Current focus

The repository now contains four submitted publication lines:

1. **Paper 1:** Studies 1 + 2, submitted to AIAA Journal of Aerospace Information Systems as manuscript `2026-09-I012066` on 2026-09-05.
2. **Paper 4:** rebuilt Study 8 + Study 8E manuscript, submitted to IJSCCN as manuscript `4920969` on 2026-09-22; rejected at editorial screening on 2026-09-24 as `out of scope`, with no external reviewer reports supplied. The earlier Acta rejection remains historical provenance.
3. **Paper 2:** Studies 3 + 4 + 6, submitted to IEEE Transactions on Aerospace and Electronic Systems on 2026-09-07; manuscript `TAES-2026-4182` was rejected at editorial pre-screening on 2026-09-26 without external peer review.
4. **Paper 3:** Study 7, submitted to CEAS Space Journal on 2026-09-13 as submission `6db04a31-8223-4aaf-af02-e4bafe06ef89`; rejected by handling-editor editorial assessment on 2026-09-22.

Paper 1 remains frozen pending journal action. Paper 2's rejected R10 package and Studies 3/4/6 remain frozen; only a separate Phase-1 post-rejection design/formal-analysis workspace is authorized. The rejected Paper-3 CEAS, Paper-4 Acta, and Paper-4 IJSCCN packages remain frozen as provenance. Paper 3 now has an explicitly authorized rejection-to-research-requirements workstream; its completed audit proposes a new prospective extension but does not authorize scientific execution. Paper 4 is now in a fresh venue-fit phase after the IJSCCN scope rejection; no scientific rerun or automatic Wiley transfer is authorized.

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

### Paper 4 - Study 8 + Study 8E

- Latest journal: International Journal of Satellite Communications and Networking
- Manuscript ID: `4920969`
- Submitted: 2026-09-22
- Decision date: 2026-09-24
- Current recorded state: `REJECTED__EDITORIAL_SCREENING__OUT_OF_SCOPE__NO_EXTERNAL_REVIEW`
- Decision detail: IJSCCN stated `out of scope`; no external reviewer reports or specific technical/methodological defects were supplied
- Authority: `publication/Paper_4_Study_8/IJSCCN/PACKAGE_STATUS.json`
- Decision provenance: `publication/Paper_4_Study_8/IJSCCN/R5_IJSCCN_EDITORIAL_DECISION_2026-09-24.md`
- Prior Acta submission: `AA-D-26-02872`, rejected 2026-09-19 and retained as historical provenance

Study 8 remains a separate deterministic finite modeled population of 3,456 positions. Study 8E remains separately frozen under `S8E-CANON-RESULTS-002-FREEZE-001`. The two populations remain unpooled. The IJSCCN scope rejection does not alter either scientific record.

The next Paper 4 gate is a fresh venue-fit audit plus optional review of Wiley Transfer Desk suggestions. No fallback venue is automatically selected, no automatic transfer is authorized, and no scientific rerun or statistical reanalysis is authorized by the decision.

### Paper 2 - Studies 3 + 4 + 6

- Journal: IEEE Transactions on Aerospace and Electronic Systems
- Submitted: 2026-09-07
- Research Exchange UUID: `cd1dfa89-4a24-4451-bdd4-af31ce3367f4`
- Manuscript ID: `TAES-2026-4182`
- Decision date: 2026-09-26
- State: `REJECTED__EDITORIAL_PRESCREEN__NO_EXTERNAL_REVIEW`
- Authority: `publication/Paper_2_Studies_3_4_6/IEEE_Transactions_on_Aerospace_and_Electronic_Systems/TAES_PACKAGE_STATUS.json`
- Decision record: `publication/Paper_2_Studies_3_4_6/IEEE_Transactions_on_Aerospace_and_Electronic_Systems/TAES_EDITORIAL_DECISION_2026-09-26.md`
- Rebuild state: `PHASE1_AUTHORIZED__DESIGN_AND_FORMAL_ANALYSIS_ONLY__NO_NEW_EXECUTION`
- Rebuild workspace: `publication/Paper_2_Studies_3_4_6/Post_Rejection_Rebuild/`

Paper 2 retains Studies 3, 4, and 6 as three immutable, unpooled frozen populations. The rejection does not authorize rerunning them.

Phase 1 derives the Study-4 threshold formulas, Study-6 observational-equivalence result, and Study-3 freshness/semantic-truth distinction from existing frozen artifacts; it also drafts separate S3X/S4X/S6X validation protocols. No new extension is authorized for implementation or execution.

### Paper 3 - Study 7

- Journal: CEAS Space Journal
- Title: **Observability Limits of Learned Satellite Cyber-Recovery Decisions Under Compromised Evidence**
- Article type: Research
- Topic: Artificial Intelligence in Space
- Submission ID: `6db04a31-8223-4aaf-af02-e4bafe06ef89`
- Submission version: `v.1.0`
- Submitted: 2026-09-13
- Decision date: 2026-09-22
- Current recorded state: `REJECTED__EDITORIAL_ASSESSMENT`
- Current authority: `publication/Paper_3_Study_7/CEAS_Space_Journal/CEAS_SUBMISSION_STATUS.json`
- Decision record: `publication/Paper_3_Study_7/CEAS_Space_Journal/CEAS_EDITORIAL_DECISION_2026-09-22.md`

The handling editor recognized the assurance concern as relevant and the setup as transparent and reproducible, but found the scientific contribution insufficiently developed. The identified gaps were: a central result too directly implied by the formulation, no concrete spacecraft recovery architecture, unvalidated trust assumptions, and no deterministic corroboration-aware comparator receiving the same information as the learned policy.

Study 7 / `S7-LSO-001` remains a frozen exact finite modeled population of 1,033 observations. The rejected CEAS package and the Study-7 evidence are immutable provenance.

Durable archive:

- Zenodo version DOI: `10.5281/zenodo.22732060`
- Zenodo concept DOI: `10.5281/zenodo.22732059`

Post-rejection recovery authority:

- `publication/Paper_3_Study_7/Post_Rejection_Rebuild/PAPER3_CEAS_REJECTION_TO_RESEARCH_REQUIREMENTS_AUDIT_2026-09-22.md`
- `publication/Paper_3_Study_7/Post_Rejection_Rebuild/STUDY7E_AERC_PROSPECTIVE_EXTENSION_PROPOSAL_2026-09-22.md`

Audit result: `NEW_PROSPECTIVE_EXTENSION_REQUIRED`.

Proposed extension: `S7E-AERC-001` / Architecture-Grounded Equal-Information Recovery Comparators Under Correlated Trust Failures.

The prospective protocol and implementation/test plans are now drafted for author review. The design specifies equal-information policy pairs, five trust-domain topologies, thirteen fault/compromise profiles, 84 training architecture scenarios, and 196 canonical evaluation/control scenarios yielding 784 planned evaluation decisions. These are prospective design quantities, not results. No implementation workspace or scientific execution is authorized.

## Paper 2 post-rejection Phase-1 gate

Author authorization on 2026-09-26 establishes a separate Paper-2 workstream:

`PHASE1_DESIGN_REVIEW_REQUIRED_BEFORE_ANY_EXTENSION_EXECUTION`

The current tasks are editorial diagnosis, theory/generalization audit, non-overlap control, and review of draft S3X/S4X/S6X protocols. This workstream does not alter Study 5, Paper 3, or Paper 4.

## Remaining eligible publication candidates

### Study 5 / S5-CUCD-001

Study 5 remains a portability/external-validity boundary study. Its publication vehicle remains deferred. It must not be represented as external empirical validation of Studies 3, 4, 6, or 7, and it must not be reported as measuring IDS accuracy, recall, false-positive rate, or packet-level recovery effectiveness because those outcomes were not measured.

### Other remaining studies

Any other repository study or experiment may enter the next-paper candidate audit only if it is demonstrably complete, provenance-bound, scientifically independent, and not already consumed as experimental evidence by Papers 1, 2, 3, or 4.

## Current exact action

Paper 3 recovery is an additionally authorized workstream following the 2026-09-22 CEAS decision. Its immediate gate is author review of the drafted `S7E-AERC-001` protocol and implementation plan. This does not cancel or overwrite the separately governed Paper-4 workstream.

The active Paper-4 publication gate is:

`IJSCCN_OUT_OF_SCOPE_CLOSEOUT__FRESH_VENUE_FIT_AUDIT`

Decision authority:

`publication/Paper_4_Study_8/IJSCCN/R5_IJSCCN_EDITORIAL_DECISION_2026-09-24.md`

Required sequence:

1. preserve the exact rejected IJSCCN R5 submission and private local publisher package as historical provenance;
2. inspect Wiley Transfer Desk suggestions if received, but treat them as candidates only;
3. conduct a fresh live venue review against the actual Study 8 + Study 8E scope;
4. reject venues that would require unsupported operational RF, throughput, CPU, energy, thermal, or mission-performance claims;
5. preserve Study 8 / Study 8E non-pooling and Paper-5 independence;
6. select and lock a new venue only after live scope and author-guideline verification;
7. create any new publisher-facing derivative on a fresh Paper-4 branch from current `main`;
8. retain any transfer or publisher submission as a separate explicit author-authorization gate.

**Terminology safeguard:** Paper 4 is the Study 8 publication. Study 4 / `S4-MPQ-001` is a different frozen experiment already included in submitted Paper 2 / TAES. Do not modify or rerun Study 4 as part of this Paper-4 resubmission workflow.

The remaining-study publication-candidate audit, including Study 5, remains separate from the Paper-4 retargeting workstream unless the author explicitly reprioritizes it.

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
