# Paper 5 Phase 3: sole-author methodological challenge, PDF proof and publisher gate

**Prepared:** 2026-11-23  
**Status:** `SOLE_AUTHOR_CRITICAL_REVIEW_AND_AUTHOR_APPROVAL_PENDING`; **not submitted; PR #255 must remain draft and unmerged.**  
**Sole-author resource decision (2026-11-23):** The author confirms that an external pre-submission human methods reviewer cannot be funded or arranged. **External pre-submission review is not a project requirement or submission blocker.** The journal's own independent reviewer selection remains the publisher's responsibility after editorial screening. This decision does not claim that the author has already completed the scientific appraisal or waived journal peer review.  
**Authorizations:** Manuscript-only adversarial-remediation and preparation of human/visual review materials. No experiments, raw-source release, external manuscript transmission, journal upload or merge.  
**Supersedes for current readiness only:** The 2026-11-23 `FINAL_AUTHOR_SUBMISSION_GATE_20261123.md`'s *old* 23-page/15-reference snapshot and corresponding old CI run numbers. Its author attestations remain **unanswered**, not superseded or automatically approved.

## Research and source pins for author-led inspection

| Evidence class | Canonical source, scope and verification boundary |
|---|---|
| Study 9 frozen science | Repo `Zartharas/mission-aware-satellite-cyber-recovery`, baseline `5ee451c2a739cbca7dc948d49239d985c6b4cc07`; study9 protocol/mapping/policy freeze and accepted canonical results. Source populations 25,000, 137,965, 404,798. |
| Study 10 frozen design | G2 receipt on `study10/s10-rsei-001-g2-freeze-receipt-20261122`, pinned protocol payload `8ed6a2b16233b86bf91672f6f15605dcf906c5eb`. Internally frozen after some declared prior metadata exposure, **not** externally preregistered. Four primary ESA-v2/OPS-SAT strata; Hack-A-Sat secondary unpooled and unexecuted. |
| Study 10 synthetic methodology | `study10/s10-rsei-001-g3-post-parity-audit-g4-hold-20261123`: 18 synthetic cases, 22 tests and 1,024 exact oracle comparisons. Not real-flight recovery. |
| Study 10 derived-only observational evidence | `study10_derived/S10_G4_TierA_32Slot_PublishedSchema.json`; `S10_G4_TierC_16_StratumPolicy_NonEvaluable.json`; `S10_RQ_E3_ESA_V1V2_Aggregate_Metadata.json`; hashes/exclusions in `README_MANIFEST.json`. |
| Public inputs | ESA v2 DOI `10.5281/zenodo.15237121`, ESA v1 comparison DOI `10.5281/zenodo.12528696`, OPS-SAT-AD v2 DOI `10.5281/zenodo.15108715`. No original bytes republished. Rights and channel-detail exceptions remain under author control. |
| Integration and prior challenge | Exact Phase 2 assessed source commit `0dd962071b6adb16a9ad572046f9f90c59f922a7`; report added at `e171a2e7225c23539c56864cf7824ca90f9958b8`. See `PHASE2_ADVERSARIAL_REREVIEW_20261123.md`. |
| Revised manuscript and supplement | Use the **current PR head**, not the above historical commits, for author PDF approval; source is `CSA_S9_S10_INTEGRATED_CANDIDATE.tex`, `references.bib`, `PHASE2_FIELD_LEVEL_EVIDENCE_SUPPLEMENT.tex` and `PHASE2_FIELD_LEVEL_EVIDENCE_APPENDIX.tex`. |
| Exact checks | The revised manuscript-bearing head `b844f92019ae3fce661e7308a24f8f5b04915f56` passed exact-head [LaTeX + 56-mapping validation `45279831571`](https://github.com/Zartharas/mission-aware-satellite-cyber-recovery/actions/runs/45279831571), producing the [artifact ZIP with PDF SHA-256 manifest](https://github.com/Zartharas/mission-aware-satellite-cyber-recovery/actions/runs/45279831571/artifacts/14868614567). See `PHASE4_PDF_VISUAL_AND_ARTIFACT_INTEGRITY_QA_20261123.md`. The repository-wide validation at this SHA must be checked separately. Any subsequent manuscript revision requires a new exact-head check. |

## A. Sole-author methods challenge — scientific appraisal, not external peer review

**Resourcing and review model:** This is independent, unfunded, sole-author research. External human pre-submission review is **not obtainable** and **not required** as a private project gate. The author is responsible for final methodological judgments; AI-assisted adversarial analysis (recorded in `PHASE2_ADVERSARIAL_REREVIEW_20261123.md`), frozen source audits, code/tests, source-linked literature review and exact-head CI are inputs to that judgment, **not** outside expert endorsement. The journal's ordinary editor/reviewer assessment occurs only after an eventual submission and is **not** represented as having occurred here.

For each question, the author should provide a brief **evidence-based disposition** in a dated sole-author review note: `supported`, `limited but disclosed`, or `needs correction`, citing exact file/commit/page and identifying the strongest plausible counterargument. The assistant may draft and challenge this record, but must not sign or attest on behalf of the author.

- [ ] **Novelty:** Test this source-sufficiency audit against TRACE, RTEF-IDS, AIRSS, CCSDS firewall, Stargate, SAFE and evidence-bound warrants. Identify the narrow original contribution and the strongest competing interpretation, citing actual published material.
- [ ] **Contract-driven results:** Critique whether a strict eight-predicate operational recovery interface makes zero qualifying coverage predictable for detection-oriented public sources. Acknowledge the selector's mathematically deterministic consequences and why the observational source-field audit remains useful.
- [ ] **Study 9 (RQ1–RQ4):** Verify the 24 frozen source-to-predicate judgments, `Position_Anomaly` entire-field deviation, exhaustive selector completions, non-singleton action sets and 6/7/7/8 sidecar minima using frozen artifacts and checks.
- [ ] **Study 10 (RQ-E1–RQ-E5):** Check the G2-frozen four primary strata, unexecuted Hack-A-Sat secondary arm, 32 Tier A mappings, 16 operational `NOT_EVALUABLE` outcomes, metadata-only E3 limitation (54 differences not semantic transitions), and the separate 18-case/1,024-oracle synthetic tests.
- [ ] **Evidence and reproducibility:** Check hash pins, public DOIs, rights notices, excluded local source bytes and author-terminal-only receipt limits. Distinguish archived-result integrity checks from independently reproducing original source adjudications.
- [ ] **Adversarial counterexamples:** Explicitly challenge any sentence implying flight effectiveness, dataset deficiency, guaranteed mission independence, universal sidecar requirements, general statistical inference or completed semantic-release stability.
- [ ] **Author scientific decision:** Record a date, current commit, evidence ledger and reasoned **proceed with disclosed limitations / revise further / withdraw or change venue** judgment. The author alone must check this item after reviewing evidence. This is a scholarly self-assessment, not independent human peer review.

**AI-assisted internal adversarial review:** `DOCUMENTED_NOT_EXTERNALLY_INDEPENDENT`  
**External pre-submission human review:** `NOT_AVAILABLE_NOT_REQUIRED_FOR_INTERNAL_GATE`  
**Journal peer review:** `NOT_STARTED; EDITORIAL_PROCESS_ONLY_AFTER_SUBMISSION`  
**Sole-author signed scientific appraisal:** `PENDING`

## B. Author visual proof of two current-head PDFs

**Current manuscript-bearing QA basis:** commit `b844f92019ae3fce661e7308a24f8f5b04915f56`, exact-head LaTeX workflow [45279831571](https://github.com/Zartharas/mission-aware-satellite-cyber-recovery/actions/runs/45279831571) **SUCCESS**; main PDF **33 pages**, S1 **4 pages**, **zero overfull boxes** in both, **129 underfull** in the main PDF, **24 cited references**. The ZIP + enclosed SHA-256 manifest verifies both unmodified PDFs. A complete **assistant technical rendered-page review** is recorded in `PHASE4_PDF_VISUAL_AND_ARTIFACT_INTEGRITY_QA_20261123.md`; it does not substitute for **your final author proof**. Subsequent documentation-only commits do not change the verified manuscript bytes, but current-head CI should be checked again before final approval.

- [ ] Retrieve latest run from [PR #255](https://github.com/Zartharas/mission-aware-satellite-cyber-recovery/pull/255), Actions `Paper 5 integrated draft LaTeX validation`, and download its main + S1 PDF artifacts.
- [ ] Record **final SHA, workflow run IDs and actual page counts**; confirm no unresolved citations, overfull boxes, errors or missing figures after edits.
- [ ] Visually inspect **every main PDF page** at normal zoom: title/contact placeholders; abstract; nine-RQ table; closest-work table; diagram, caption and cross-references; ESA/OPS counts; appendix citations; bibliography legibility.
- [ ] Inspect all **four or updated number of S1 pages**: 24 S9 + 32 S10 mappings visible; tables not cropped; source-field names, exclusion judgments and evidence roles readable.
- [ ] Evaluate footnotes, page-break gaps, poor line breaks (especially any underfull warnings), typography and figure rendering. Log page numbers requiring edits, **not** just a technical pass.
- [ ] Verify Figure 1's factual content and updated disclosure: ChatGPT **GPT-6 revised the final LaTeX schematic on 23 Nov 2026**; the exact earlier-draft model is not documented. No observed-data imagery was generated. Approve this accurate provenance statement.
- [ ] Approve or reject the typeset manuscript **with author name/date and exact final SHA**. The assistant must not check these boxes.

**Assistant technical PDF visual QA:** `COMPLETED__NOT_INDEPENDENT_HUMAN_PROOF` (see Phase 4 report).  
**Author PDF visual verification:** `NOT_PERFORMED`  
**Author title/affiliation/correspondence approval:** `NOT_RECORDED`

## C. Publisher / original research gate (author only)

The current [CSA Guide for Authors](https://www.keaipublishing.com/en/journals/cyber-security-and-applications/guide-for-authors/) and [Elsevier journal AI policy](https://www.elsevier.com/about/policies-and-standards/generative-ai-policies-for-journals) were checked on 2026-11-23. They require author accountability, AI text/image disclosures, and publisher forms; only the author can attest to personal information or competing interests.

- [ ] Confirm the exact current byline, independent researcher designation, ORCID, **full postal address** and corresponding email already in title-page source; do not infer or replace them.
- [ ] Recheck research originality/exclusivity, overlapping studies/papers and prior preprint disclosures. No current combined manuscript submitted elsewhere unless expressly disclosed.
- [ ] Independently verify the new four references and their scope: CCSDS 2026 full text was not available; SAFE published online 20 November 2026; Stargate was a 13 November arXiv preprint, not yet cited as a published proceedings paper; EBAW appeared 23 November 2026.
- [ ] Confirm OpenAI ChatGPT and figure/model-version accuracy; revise disclosure only from author-confirmed facts; independently edit and check AI-assisted wording/citation accuracy.
- [ ] Review funding, current employment and consultancies, perceived conflicts, intellectual property, relevant prior three-year relationships, and institutional disclosure duties; the previous sentence stating no competing interests is **proposed** and not a completed declaration.
- [ ] Use [Elsevier declarations tool](https://declarations.elsevier.com/) and supply its generated `.doc`/`.docx` file. Do not fake a form or an author attestation.
- [ ] Confirm specific ESA/OPS-SAT attribution, ESA v2 license limitations, release-specific source notices, no original-data republication; arrange stable supplementary release only if later separately authorized.
- [ ] Check all 3–5 highlights, 3–6 keywords, live journal requirements, sponsor/acknowledgment disclosures, supplement caption and upload plan.
- [ ] Provide specific approval for **final submission candidate at exact SHA**; the present permission to perform editorial work does not approve journal submission or merging.

**Status:** `AUTHOR_CONFIRMATION_PENDING` / `SOLE_AUTHOR_SCIENTIFIC_APPRAISAL_PENDING` / `AUTHOR_VISUAL_PROOF_PENDING` / `PR_DRAFT_NO_SUBMISSION`.

## D. Stopping rule

Passing GitHub CI, presence of this checklist, current source citations, or success of a static validator **does not** establish scientifically sufficient novelty, independent external human review, license clearance, final PDF layout, model-version attribution or author attestations. Lack of external pre-submission review is documented and is **not itself a submission blocker**; the author must still critically assess scientific quality and accept the journal's own peer-review process. Do not merge, upload to publisher, distribute raw data or run a new study without a separate explicit approval.
