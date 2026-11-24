# Paper 2 — R5 publication readiness and concise abstract candidate

**Date:** 2026-10-08. **Repository basis:** live `main` `4cd0c30a276b3c5a0494736b93a8d08dc1ed8df4`. **Scope:** pre-venue editorial review and **unapproved** abstract draft only; no changes to the authoritative R4 source, study results, manuscript claim-source mapping, publisher records, or PR #215.

## Immutable scientific and editorial basis

- Historical TAES prescreened submission `TAES-2026-4182` (submitted 2026-09-07, editorial rejection 2026-09-26, no external peer review) is preserved and not resubmitted as-is. The editorial criticism addressed contribution narrowness, relevance, readability, limitations-forward narrative, unclear question/gap and experiment-centered contributions; it did **not** allege a numerical or data-integrity defect.
- Venue-neutral R4 manuscript `PAPER2_REBUILD_MANUSCRIPT_R4_2026-10-01.md`, Git blob `069e319864b1f5c1ee201b31872e68572fea1923`, is present on live main; its status is **pre-venue candidate, not publisher package**.
- Frozen Study 3 (1,380 trajectories and 67,620 epoch states), Study 4 (4,608 rule-by-subset observations), Study 6 (420 finite assurance observations) remain separate; S3X uses 1,919 ESA timing-proxy intervals and S6X comprises two separately governed 396-observation repetitions and eight builds. No populations are pooled and no trial claims operational spacecraft recovery.
- R4 currently has five numbered tables, one original Figure 1 and approximately 7,863 word-like tokens (as recorded in the R4 status). Direct count of the R4 abstract using whitespace-delimited tokens: **287** (editorial diagnostic, not an official publisher word count).
- **P2X is not an R4 study population.** Its v2f qualification remains at nine reproduced offline artifacts plus an independently reviewed full-tree inventory with 55 byte-hash variances; its runtime is untested. PR #215 remains a separate draft and cannot be imported as operational or S6X claim evidence.
- Sole author: Independent Researcher; no coauthors should be added. Verify final author metadata, ORCID, disclosures and affiliations against approved author records at venue-specific preparation.

## Condensed abstract candidate — editorial draft only

A satellite cyber-recovery qualification decision relies on observable evidence rather than hidden system correctness. We ask which trust failures remain undetectable when temporal freshness, producer composition, and recovery-artifact assurance are evaluated as distinct evidence layers. Three frozen deterministic studies and two separately governed stress tests address this question. Study 3 distinguishes bounded truthful-cache exposure from false but validly signed evidence created within a trusted producer boundary. S3X uses 1,919 extreme inter-sample intervals from ESA telemetry as timing proxies, showing that refresh hiatus changes when a false-but-valid boundary appears but does not repair the underlying semantic trust failure. Study 4 evaluates 4,608 rule-by-subset observations across 18 rules and shows that provenance constraints can alter systematic qualification failure while also reducing tolerance of benign unavailability. Study 6 reduces modeled incorrectly qualified states from four of five under signature-only checks to one of five under a six-signal composite gate. S6X separately tests the residual with pinned cFS/Limit Checker source: two repetitions of 396 observations across eight governed builds distinguish controlled correctness states, while six qualification signals remain true and independent gate evaluators agree. These results locate residual qualification failure in the difference between decision-visible evidence and underlying correctness. They characterize finite models and a controlled executable fixture, not operational spacecraft recovery or external replication of the core studies.

**Draft abstract whitespace-word count:** 215. This wording is not adopted into R4 or any publisher package; verify every clause against `PAPER2_REBUILD_R3_CLAIM_SOURCE_MAP_2026-09-30.md`, S6X frozen claim-use status, and the exact finite-study evidence before adopting it. Preserve study-specific units and avoid implying a joint experiment.

## Live venue screen (not a venue lock)

| Venue | Current authoritative guidance consulted | Relevance and gating issue |
|---|---|---|
| Journal of Information Security and Applications (Elsevier) | Official journal scope: https://shop.elsevier.com/journals/journal-of-information-security-and-applications/2214-2126 | Strong thematic match for evidence qualification and information-security applications; the official full Guide for Authors could not be fetched during this review (publisher access restriction). Formatting, length, ethics, data and article categories remain **UNVERIFIED**. Also recheck any Paper-4 venue allocation before selecting JISA. |
| IEEE Systems Journal | Official instructions: https://ieeesystemscouncil.org/publication/ieee-systems-journal/instructions-for-authors | Application-oriented systems interpretation is plausible; up to **12 review pages**, IEEE double-column format and approximately **150–250 abstract words**. Must typeset R4 and count actual PDF pages. The source instructions contain inconsistent stated open-access charges in different sections; verify fees directly if selected. |
| Aerospace (MDPI) | Official instructions: https://www.mdpi.com/journal/aerospace/instructions | Satellite-domain fit, but fully open access with APC; the guide requires reproducible experimental detail and data-availability statements and offers free-format initial submission. Confirm precise APC, dataset-release/embargo policy and aerospace audience fit before lock. |

**Nonbinding editorial priority:** evaluate JISA first **for thematic fit**, while keeping IEEE Systems Journal and Aerospace under comparative review. This does not choose a journal and makes no acceptance forecast. Choosing a venue requires a separate explicit author decision and a current complete policy audit.

## Publication-critical gates and completion criteria

| Gate | Status and completion rule |
|---|---|
| Scientific evidence integrity | **FOUNDATION PRESERVED.** Re-audit R4 claims against frozen Study-3/4/6 and S3X/S6X source maps; no extra result claims or pooling. |
| Contribution/readability remedy | **OPEN.** Lead with the cross-layer qualification observation-set finding and specific engineering decisions, not merely experiments performed; remove unnecessary convoluted sentences without altering claims. |
| Author metadata/declarations | **OPEN FOR FINAL CONFIRMATION.** Single independent author; no invented coauthors, funding, grants, ethics exemptions, contact details or affiliations. |
| Venue selection | **OPEN.** Verify full current official guide, scope, length, artwork, references, conflict/AI disclosures, code/data availability and APC or page fees, then obtain author's choice. |
| Manuscript R5 editorial derivative | **CANDIDATE ABSTRACT ONLY.** Create a separately versioned derivative after claim-level and venue review; leave R4, historical TAES R10 and original Figure 1 immutable. |
| Tables/figure/reference QA | **OPEN.** Check five tables and canonical Figure 1 for labels, unit consistency, accessibility, copyright, reference validity, figure export and visual legibility. |
| Rendered submission file | **NOT PREPARED.** Format in selected journal template, compile and audit PDF/pages/figures/links and exact source-to-output checksums. |
| Submission package and author approval | **NOT AUTHORIZED.** Prepare cover letter, appropriate data statement and separate upload manifest only after venue choice; no portal action or submission without author confirmation. |
| P2X workspace/runtime | **OPTIONAL SEPARATE TRACK; NOT AN R4 SUBMISSION GATE.** Nine offline build outputs reproduce, but no runtime was executed; 55 exact file-hash variances are conditional omissions only, zero applied. |

## Controlled next action

Perform a claim-by-claim editorial audit on R4, then produce a versioned R5 derivative proposal—not an unapproved submission. Independently investigate the venue's full instructions and confirm the venue, then render the publisher-specific package and obtain final author authorization before any submission. Continue optional P2X source-consumer/dependency review separately without changing Paper-2 manuscript claim populations.

**Current outcome:** `PUBLICATION_R5_PREVENUE_READINESS_REVIEW_PREPARED__NO_VENUE_LOCK__NO_SUBMISSION`. No venue lock and no submission are authorized by this review.
