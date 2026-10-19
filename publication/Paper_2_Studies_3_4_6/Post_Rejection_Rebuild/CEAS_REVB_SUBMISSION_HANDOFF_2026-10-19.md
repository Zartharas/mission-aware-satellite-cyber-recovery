# Paper 2 — CEAS Space Journal RevB submission handoff (2026-10-19)

**Status:** Submission package prepared and verified on the sole author's Mac. **NOT submitted to CEAS.** This record is metadata-only: do **not** commit the publisher DOCX/PDF/ZIP, ignored evidence archives, ESA v2 inputs, or other third-party material to GitHub.

## Authorities and version boundaries

- Canonical research repository: `Zartharas/mission-aware-satellite-cyber-recovery` (<https://github.com/Zartharas/mission-aware-satellite-cyber-recovery>). The only research repository relevant to this Paper-2 handoff.
- Last independently verified `main` before this handoff branch: `4cd0c30a276b3c5a0494736b93a8d08dc1ed8df4`. This branch starts **from main** and adds this documentation file only.
- Publication PR [#216](https://github.com/Zartharas/mission-aware-satellite-cyber-recovery/pull/216): **OPEN / DRAFT / UNMERGED**, head `b63ab1eb64378e3bdde7a89a217c49c4eb5717bc`. Post-PR workflow **#1481 SUCCESS**. Do not merge, close or mark ready automatically.
- Publication governance [Issue #217](https://github.com/Zartharas/mission-aware-satellite-cyber-recovery/issues/217) remains the existing issue; no duplicate new issue necessary.
- Other draft work (e.g. #213–#215, Paper 3, Papers 4/5) is unrelated and must not be modified by this submission handoff.

## Sole-author submission identity and title

- Manuscript title: **Residual Trust Boundaries in Satellite Cyber-Recovery Qualification: Temporal Evidence, Producer Composition, and Artifact Assurance**.
- Sole independent researcher and corresponding author: **Aman Kumar Singh**. No coauthors.
- Venue: **CEAS Space Journal (Springer Nature)**, **Original Research Article**, single-blind review.
- Submission portal (confirm live page before action): <https://submission.springernature.com/new-submission/12567/3>.
- No publisher-generated proof, submission receipt, or manuscript ID has been received. **CEAS submission = NOT COMPLETED.**

## Author-host verified publisher package

- ZIP filename: `CEAS_Paper2_Submission_Ready_2026-10-19_RevB.zip`
- **Whole ZIP SHA-256:** `cd58668c183cbfdf9a14be85159435d2d4224e25d353365a5f608d2c4f6ab64f`. The sole author executed `shasum -a 256` on the copied Mac ZIP and reported this exact SHA; the assistant separately verified the bytes of the uploaded ZIP at this SHA and `unzip -t` passed.
- Stored on the author's Mac **outside the Git repository** at the sibling `Paper2_CEAS_Submission_2026-10-19/` directory beneath `Satellite-Cybersecurity-Research/`.
- ZIP contains exactly seven files:
  1. `CEAS_Paper2_Manuscript_Final_2026-10-19_RevB.docx`
  2. `CEAS_Paper2_Manuscript_Final_2026-10-19_RevB.pdf`
  3. `CEAS_Paper2_Cover_Letter_2026-10-19.docx`
  4. `CEAS_Paper2_Cover_Letter_2026-10-19.pdf`
  5. `CEAS_Paper2_Portal_Fields_2026-10-19.md` (**local entry aid, NOT a journal attachment**)
  6. `Fig1_Residual_Trust_Boundaries.svg` (source artwork; upload separately only if the portal asks)
  7. `START_HERE.txt` (local instructions, NOT a journal attachment).
- **Important filename mismatch:** The older text in `CEAS_Paper2_Portal_Fields_2026-10-19.md` says `CEAS_Paper2_Manuscript_Final_2026-10-19.docx/.pdf`. These *examples are stale*. Use the **actual RevB names inside the ZIP** shown above.
- Earlier RevA ZIP SHA-256: `684dc4d3c317d870fa6be1793fb13729347c8fd279cb37e0a93fc3e14a4e5bbf`. RevA and pre-RevA are superseded and retained on the author's Mac.

## RevB manuscript validation, limitations, and editorial status

The latest author-facing independent review report is `CEAS_Paper2_RevB_Editorial_Rejection_Comparison_2026-10-19.md` (off-repository; **do not upload to publisher**). Previously confirmed:
- 30 PDF pages, automatic Word PAGE fields visible as page 1–30 in the PDF, Figure 1 caption without terminal punctuation;
- 228-word abstract, six keywords, 17 numbered references, five editable tables, four editable OMML equations, original vector Figure 1 retained;
- Word accessibility review high=0, medium=0, low=0; rendered layout manually reviewed;
- RevB from RevA: only the terminal punctuation of the figure caption changed in body text; automatic page numbering added; scientific results unchanged;
- AI assistance disclosed accurately and without double authorship; single independent human author has full responsibility.

**Do not overclaim:** these are formatting and source-consistency checks, **not** a guarantee of CEAS acceptance, full independent 17-reference passage/retraction validation, operational spacecraft validation, or actual reviewer access to ignored research outputs. The code availability points to a retrievable exact source revision in draft PR #216, **not** already merged into `main`. Data access restrictions must be stated truthfully.

## Scientific populations and non-negotiable claims

- Study 3: **1,380** deterministic trajectories / **67,620** logical-epoch states. V5 means a compromised trusted producer signs false evidence; V4 means post-signature manipulation invalidates the signature. K4 is synthetic intermittent contact. Unsafe qualified recovery-gate classification must not be equated with actual spacecraft recovery.
- Study 4: **4,608** rule-by-subset observations. Synthetic producer/provenance memberships are **not empirically verified hardware/organizational independence**.
- Study 6: **420** finite assurance observations. G0 signature-only incorrectly qualifies **4/5** modeled incorrect states, G5 six-signal composite **1/5**, not an operational bypass claim.
- S3X: **1,919 ESA v2 inter-sample timing proxies**, **not measured RF outages/attack labels**. ESA source DOI <https://doi.org/10.5281/zenodo.15237121>. Redistributing version-specific derived intervals/reconstructive outputs is **not independently rights-cleared**.
- S6X: pinned cFS/Limit Checker research fixture, **396 observations per deterministic repetition**, two matching runs and eight controlled builds. **Not** flight validation.
- **Study 3 provenance discrepancy must remain transparent:** accepted original artifact member `cell_summary.csv` SHA-256 `dc653561333d48f90b1917f5c29863e1cded4d5a8b13ce11b0b5935fa6fe0322`; separate tracked auxiliary `study3/results/canonical/cell_summary.csv` SHA-256 `e588d1034894d40f72cfdb3c630d43e42e7e2ebcf7fe38014629120d70c4a394`; historical comparison observed 25 differing numbers across 13 cells. The manuscript's Study 3 Table 2 should be understood as grounded in the **accepted primary frozen findings**. **Do not silently reconcile, rewrite or replace either CSV.**
- No pooling study populations, no reruns, no reinterpreted hidden-truth or third-party timing as observed spacecraft cyberattack data.

## Prior editorial decisions considered (not promises of acceptance)

**Paper 2, TAES `TAES-2026-4182`, 2026-09-26:** editorial **prescreen** rejection, **no external peer review**. Six concerns: narrow contribution, unclear aerospace significance, difficult/convoluted writing, excessive limitations-forward narration, unclear RQ-to-gap linkage, experiments instead of findings in the contribution bullets. Exact source:
`publication/Paper_2_Studies_3_4_6/IEEE_Transactions_on_Aerospace_and_Electronic_Systems/TAES_EDITORIAL_DECISION_2026-09-26.md`.

**Paper 3, separate Study 7, CEAS, 2026-09-22:** handling-editor rejection. Central result was too directly implied by model formulation; no concrete spacecraft recovery architecture; trust/independence assumptions not validated; missing equal-information deterministic comparator for the learned-corrob comparison. Exact source:
`publication/Paper_3_Study_7/CEAS_Space_Journal/CEAS_EDITORIAL_DECISION_2026-09-22.md`.

**Assessment of RevB:** TAES communication flaws **materially improved**. Paper 3's special unequal-information ML comparator problem **does not directly apply** to Paper 2; Paper 2 gives finite quantified comparisons and an executable cFS fixture. The risk of a theoretical/expected result, incomplete integrated spacecraft architecture, and unvalidated real trust-domain independence **still exists**; **do not** claim all rejection objections are “fixed” or that CEAS editorial prescreen success is guaranteed.

## Remaining user-facing submission sequence (no further research-audit scripts)

1. Sole author reviews the final RevB PDF/Word and cover letter and confirms exact authorship, originality, no concurrent journal submission, funding/conflicts/AI disclosures, and rights.
2. Use RevB-named manuscript DOCX, RevB PDF, and cover letter from the seven-file ZIP. Populate portal's mandatory author contributions, competing interests, funding, data availability and code availability fields truthfully. If file category for the accompanying PDF differs, follow the live portal's labels.
3. Do not upload `START_HERE.txt`, this handoff, any internal audit or rejection report, or `CEAS_Paper2_Portal_Fields_2026-10-19.md`.
4. Inspect CEAS-generated submission proof for equations, tables, Figure 1 and all references. **Only after author approval, press Submit and capture manuscript ID + receipt.**
5. When receipt exists, record actual date, journal submission ID and exact uploaded ZIP SHA in Issue #217; do not invent a submission date/ID or close PR #216 as though publication occurred.

## Detailed prompt for the next chat

> Continue **Paper 2 CEAS Space Journal submission** from the live GitHub repository `Zartharas/mission-aware-satellite-cyber-recovery`. Read this exact `CEAS_REVB_SUBMISSION_HANDOFF_2026-10-19.md` on live `main` (or its separate handoff PR if not yet merged), inspect the current `main`, PR #216 and Issue #217 first. The sole author has a **Mac-local, SHA-verified RevB publisher package** `CEAS_Paper2_Submission_Ready_2026-10-19_RevB.zip` SHA `cd58668c183cbfdf9a14be85159435d2d4224e25d353365a5f608d2c4f6ab64f`, outside the Git checkout. Manuscript 30 pages, 228-word abstract, six keywords, 17 numbered references, 5 editable tables, 4 equations; RevB page numbers/caption formatting checked; untouched frozen study evidence. The publication **has not been submitted**, and draft PR #216 must not be merged/closed without authorization. Compare TAES Paper 2 and CEAS Paper 3 prior editorial concerns exactly as sourced here; do not claim guaranteed acceptance. **Do not repeat old ZIP/evidence scans, rerun science, invent journal approvals, or rewrite more prose without a concrete defect.** Next assist directly with CEAS portal fields and proof, after sole-author confirmation. Important: the portal worksheet still carries **older manuscript filenames**; select the actual `_RevB` files from the ZIP. After genuine receipt, record exact submission ID/date in Issue #217. The evidence/code availability and ESA v2 reuse rights must remain truthful. Keep original research, PR #216, unrelated studies and repositories unchanged.

**Release/merge guard:** This document is a continuation record only, not scientific evidence and not a request to merge PR #216, publish data, or submit the paper.
