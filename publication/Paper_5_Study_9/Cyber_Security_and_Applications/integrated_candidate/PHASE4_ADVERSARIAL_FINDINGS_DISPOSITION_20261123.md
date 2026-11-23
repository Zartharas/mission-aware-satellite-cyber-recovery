# Paper 5 Phase 4: adversarial assessment finding-by-finding disposition

**Date:** 2026-11-23  
**Scope:** Every issue AR-01 through AR-12 in `PHASE2_ADVERSARIAL_REREVIEW_20261123.md`, evaluated against the author-only editorial remediation of draft PR #255.  
**Integrity constraint:** Never mutate frozen Study 2/9/10 results or reinterpret `NOT_EVALUABLE` as a zero operational outcome.  
**Final reviewer status:** **AI-assisted/internal**, not independent human peer review. External unfunded *pre-submission* human review is not a private project requirement (author decision 2026-11-23); journal-appointed peer review begins only after submission and editorial screening.  
**Global publication decision:** `NOT_AUTHOR_APPROVED__NOT_SUBMITTED__PR_DRAFT_UNMERGED`.

## Disposition legend

- **EDITORIALLY_RESOLVED:** the source wording, factual attribution or publication control identified in the review was corrected and can be validated without changing the underlying experiment.
- **RESOLVED_AS_BOUNDED_DISCLOSURE:** the original broader scientific question cannot be proved from frozen sources, but the accepted scope, honest limitation and cited evidence now make the publication-facing claim accurate. This **does not** assert the unmeasured scientific endpoint was experimentally resolved.
- **ASSISTANT_QA_COMPLETE_AUTHOR_PENDING:** model-led source/visual checks were done, but author-side personal acceptance has not been provided.
- **AUTHOR_OR_PUBLISHER_PENDING:** an unresolved personal declaration, legal/rights decision, final author approval or journal editorial decision cannot be made by the assistant.
- **NOT_A_PRIVATE_GATE:** a constraint/requirement was removed because it was not imposed by the target journal, without claiming its function was performed.

## All 12 adversarial findings

| Finding | Disposition | Evidence, remediation, non-negotiable limitation |
|---|---|---|
| **AR-01: scientific novelty** | **RESOLVED_AS_BOUNDED_DISCLOSURE; journal significance undecided** | The revised Introduction, related-work section and Discussion expressly separate the field-level empirical audit from the deterministic all-unknown selector consequences. The [Phase 4 closest-work/construct-validity matrix](PHASE4_CLOSEST_WORK_CONSTRUCT_VALIDITY_MATRIX_20261123.md) includes the strongest predicted-negative-result objection and a falsifiability condition. Novelty and eventual editorial suitability cannot be scientifically certified by an internal checklist. |
| **AR-02: historical RQ-E2 and Hack-A-Sat scope** | **EDITORIALLY_RESOLVED** | G2 exact four-stratum ESA-v2/OPS-SAT primary comparison is complete; original Hack-A-Sat competition arm was secondary and unpooled and remains **unexecuted**. The manuscript explicitly identifies the historical wider contrast as not addressed without labeling primary G2 as violated. |
| **AR-03: RQ-E3 metadata vs recovery-class mapping** | **RESOLVED_AS_BOUNDED_DISCLOSURE; original mapping-class question unanswered** | The optional ESA v1/v2 result is precisely 224 matched channels, 842/896 equal shared metadata cells, 54 changed `Physical Unit` annotations and 224 v2-only `Categorical` field occurrences. No semantic class transition or physical unit conversion is inferred. **A complete frozen v1 semantic re-adjudication did not occur.** A new study needs separately approved protocol and rights. |
| **AR-04: scope of real-flight data inspection** | **EDITORIALLY_RESOLVED** | Abstract, source-scope table, methods, RQ table and conclusion identify 12 ESA metadata tables, OPS-SAT first-line headers and bounded archive directories. `ABSENT` is relative to inspected published representation, not operational spacecraft capabilities; the 16 `NOT_EVALUABLE` actions do not represent failures. |
| **AR-05: strict contract predicts negative result** | **RESOLVED_AS_BOUNDED_DISCLOSURE** | Manuscript acknowledges selection of a demanding, eight-predicate operationally qualified interface and the expected mismatch with detection-oriented data. It does not grade benchmark quality, claim interface universality or present a sensitivity run against an untested alternative contract. |
| **AR-06: source-to-result reproducibility** | **RESOLVED_AS_BOUNDED_DISCLOSURE** | The [Phase 4 source-to-result map](PHASE4_SOURCE_TO_RESULT_REPRODUCIBILITY_MAP_20261123.md) pins exact baseline, G2 receipt, G3 code branch, three derived JSON content SHA-256s, 56 field mapping markers and public source DOIs. It explicitly identifies the nonuploaded author-terminal layout report and local ESA matched-detail CSV as not independently reproducible from PR #255; no source bytes were released. |
| **AR-07: closest work 2026** | **EDITORIALLY_RESOLVED for a targeted review; not exhaustive** | Four additional date-verified 2026 references in `references.bib`: CCSDS firewall (publisher abstract only), Stargate (Nov 2026 preprint full text), SAFE satellite IoT trust admission (publisher article/abstract), and EBAW authorization contract (publisher full text). They are compared by actual object/measurement rather than superiority; see [matrix](PHASE4_CLOSEST_WORK_CONSTRUCT_VALIDITY_MATRIX_20261123.md). Full CCSDS methods and systematic-review uniqueness are not claimed. |
| **AR-08: AI-assisted diagram attribution** | **ASSISTANT_QA_COMPLETE_AUTHOR_PENDING** | Figure 1 was revised with the currently identifiable OpenAI ChatGPT **GPT-6 on 2026-11-23**, and the caption/general declaration record how it was used. The earlier draft's precise model was **not recorded and is disclosed as unknown**, rather than guessed. The final figure is an editable schematic, not fabricated research imagery. Author must visually verify the content and approve disclosure; editor may clarify documentation if needed. |
| **AR-09: stale manuscript and gate metadata** | **EDITORIALLY_RESOLVED** | The older 23-page/15-item gate was marked historical without changing earlier attestations. README and Phase 3 gate distinguish the compiled 33-page + four-page supplement / 24-citation revised candidate from older Phase 2 build. The latest workflow check is attached to the current PR source, not assumed from old run IDs. |
| **AR-10: PDF visual/typesetting quality** | **ASSISTANT_QA_COMPLETE_AUTHOR_PENDING** | LaTeX build and PDF render checks performed for 33 main and four S1 pages; no text blocks outside page coordinates, no unexpected replacement/null characters, and no reported overfull LaTeX boxes. The formerly stand-alone figure page was reflowed with `[H]` placement and the Results text. Dense closest-work and S1 tables merit author normal-zoom inspection; 129 underfull-line warnings are diagnostic, not an automatic compile failure. Separate author publication proof remains pending. |
| **AR-11: author-only legal/publisher declarations** | **AUTHOR_OR_PUBLISHER_PENDING** | [Private-use sole-author worksheet](PHASE4_SOLE_AUTHOR_FINAL_ATTESTATION_WORKSHEET_20261123.md) explicitly requests current byline, email, postal address, funding/consultancy and other three-year actual/perceived conflicts, original/exclusive submission, AI figure approval, source-specific rights and Elsevier-generated `.doc`/`.docx` interests declaration. No unsupported “nothing to declare”, license clearance, affiliation, or upload has been certified. |
| **AR-12: independent human review independence** | **NOT_A_PRIVATE_GATE** | The author confirms no funds/resources for an outside pre-submission methods reviewer. Under the [CSA Guide for Authors](https://www.keaipublishing.com/en/journals/cyber-security-and-applications/guide-for-authors/), peer review is arranged by the journal after initial editorial assessment. AI-assisted adversarial QA remains explicitly internal; it is never described as external referee endorsement. |

## Retained scientific numerical baseline

- **Study 9:** 25,000 CuCD-ID v3, 137,965 AegisSat 2025, 404,798 UNSW-IoTSAT 2026 original rows; each dataset has 0/8 qualified direct-or-derived variables; selector unique-action rate 0 within all four policy-specific mathematical evaluations, guaranteed minimum sidecar sizes **6/7/7/8**. These are **not** 567,763 flight recovery trials.
- **Study 10:** 32 schema slots in four descriptive strata, **14 AMBIGUOUS / 18 ABSENT**, all **16** operational policy/stratum combinations `NOT_EVALUABLE`; 224 matched ESA channels / **54 changed annotations**, not 54 operational changes.
- **Synthetic:** 18 cases, 22 tests, 1,024 exact oracle comparisons. No new G5, no original telemetry, no new policy, no third-party source redistribution.
- **Evidence boundary:** Some derived JSON was independently hashed, not independently recreated from all original local files.

## PDF artifact transport integrity clarification

A GitHub Actions ZIP downloaded through the connected GitHub app matched GitHub's published ZIP SHA-256 digest. After a separate tool exported the embedded PDF files as local user-facing attachments, those **transformed local copies** differed in size and SHA-256 from the CI originals. Re-extracting the untouched ZIP directly to a separate temporary directory reproduced the exact **main and supplementary PDF SHA-256 values printed by GitHub Actions**. Thus no upstream GitHub artifact integrity discrepancy remains. Do not treat a post-export transformed local PDF as the byte-identical CI artifact. The workflow now also records a post-build `PDF_REVIEW_SHA256SUMS.txt` file inside the artifact ZIP for straightforward verification.

## Remaining genuinely necessary actions before any submission

The *publication-facing factual discrepancies* and technical review objections have been corrected or explicitly bounded. But the manuscript **cannot honestly be designated submission-ready** by assistant action until the following are personally approved or independently resolved:

1. **Sole-author signed scientific decision** accepting the narrow audit contribution and explicit unanswered secondary/sensitivity research aspects.
2. **Author final PDF proof and correspondence details**, including figure accuracy and the AI creation/revision disclosure.
3. **Publisher-generated competing-interest Word declaration**, plus truthful funding, relevant outside relationships, exclusivity and institutional/third-party rights assessments.
4. **Publication use of the derived-only research archive**, the source-specific ESA/OPS-SAT attribution/notice qualification, and choice of how to present nonredistributed data.
5. **Explicit separate authorization for submission**. Any future external editor/reviewer evaluation belongs to the journal, not this internal review.

**Phase 4 disposition:** `AR01_TO_AR12_ADDRESSED_AS_FAR_AS_FROZEN_EVIDENCE_ALLOWS__AUTHOR_GATES_OPEN__NO_SUBMISSION`.  
**No merge, no data release, no journal upload, no new experiment.**
