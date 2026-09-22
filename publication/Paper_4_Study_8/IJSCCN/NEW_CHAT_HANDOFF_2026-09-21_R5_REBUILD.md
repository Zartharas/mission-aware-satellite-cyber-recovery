# Paper 4 IJSCCN R5 Rebuild — New Chat Handoff

**Handoff date:** 2026-09-21  
**Repository:** `Zartharas/mission-aware-satellite-cyber-recovery`  
**Base main at handoff start:** `c4888f969545a17f06979aae26e30ed4afbad5c7`  
**Working branch:** `paper4/ijsccn-r5-rebuild-handoff-20260921`  
**Target journal:** *International Journal of Satellite Communications and Networking* (IJSCCN, Wiley)  
**Publisher submission:** **NOT AUTHORIZED**  
**New scientific execution:** **NOT AUTHORIZED**

## 1. Immediate objective

Pause Wiley portal upload work and rebuild the Paper 4 publisher-facing documentation as **R5** only after a fresh, comprehensive live-policy audit.

The author rejected the local R4.3 manuscript as a submission candidate because its visual presentation did not meet the required professional journal standard. The obvious broken-bullet defect was repaired in R4.3, but the broader manuscript design remained unsatisfactory.

R5 must be a fresh publication-format rebuild, not another incremental patch.

## 2. Required live-policy research before editing

Start by researching the current journal and Wiley submission guidance. Follow every submission-relevant link from these pages rather than relying on prior notes:

1. IJSCCN Author Guidelines  
   https://onlinelibrary.wiley.com/page/journal/15420981/homepage/forauthors.html

2. Wiley Prepare hub  
   https://authors.wiley.com/author-resources/Journal-Authors/Prepare/index.html

3. Wiley Manuscript Preparation Guidelines  
   https://authors.wiley.com/author-resources/Journal-Authors/Prepare/manuscript-preparation-guidelines.html/index.html

4. Wiley Submission and Peer Review  
   https://authors.wiley.com/author-resources/Journal-Authors/submission-peer-review/index.html

At minimum inspect and verify all linked guidance relevant to:

- Free Format initial submission;
- manuscript components and title page;
- figures and figure legends;
- tables;
- supporting information;
- graphical table of contents;
- biographies and author photographs;
- author/contact/ORCID requirements;
- Data Availability Statements;
- data citation and repository practices;
- funding;
- competing interests;
- ethics and consent;
- authorship;
- AI/LLM disclosure;
- permissions/copyright;
- licensing;
- color/artwork rules;
- file types and upload limits;
- cover letters;
- peer-review workflow;
- revision requirements;
- portal file categories.

Create a requirement matrix that distinguishes:

1. mandatory IJSCCN-specific rules;
2. mandatory requirements shown by the live Wiley portal;
3. generic Wiley requirements;
4. generic Wiley recommendations;
5. production-stage guidance that does not need to be imitated in the initial Word manuscript.

**Conflict rule:** current journal-specific IJSCCN instructions control over generic Wiley guidance when they conflict. Live portal requirements control for fields/certifications actually shown during submission.

## 3. Author workflow requested for R5

Use this workflow for the academic manuscript:

### Primary skills/workflows

- academic-research-suite
- evidence-first-execution
- academic-manuscript-copyedit

### Conditional

- multi-expert-analysis for consequential or ambiguous methodological, interpretive, ethical, or publication decisions;
- research-novelty-prior-art for research gap, originality, prior work, patents, standards, repositories, or competing approaches;
- anti-ai-tells **only for non-academic material** such as general-audience text, website copy, presentation copy, or other prose outside the scholarly manuscript;
- model-efficiency-router before a distinct phase when model/reasoning selection materially matters.

Do not claim a named skill was invoked unless it is actually exposed to the chat runtime. If a named skill is unavailable, apply the requested methodology directly and say so accurately.

### Author formatting requirement

**No em dashes in any publisher-facing document.**

## 4. Paper identity

**Working title:**  
*Post-Quantum Trusted Recovery Under Intermittent Connectivity: Feasibility Across Modeled Contact Budgets and Public Observation-Opportunity Timing*

**Short title:**  
*Post-Quantum Satellite Recovery Under Intermittent Connectivity*

**Author:** Aman Kumar Singh, MS, PhD  
**Authorship:** sole independent author; do not add or imply coauthors.

Private email, telephone, postal address, and author photograph must remain local-only. Do not commit them to the public repository.

## 5. Scientific architecture — immutable

Paper 4 combines two separately frozen evidence layers:

- Study 8: `S8-PQC-ICR-001`
- Study 8E: `S8E-ECTV-001`

They are presented in one manuscript but remain **separate populations and must never be statistically pooled**.

Safe framing:

> We first characterize post-compromise cryptographic recovery under a fully controlled deterministic intermittent-contact model, then independently evaluate the resulting recovery requirements against prospectively governed public satellite observation-opportunity timing traces.

Study 8E may be described as an external observation-opportunity timing evaluation/stress test using independently sourced public timing. Do not call it operational validation, real-world command-contact validation, or empirical spacecraft recovery replication.

## 6. Frozen Study 8 anchors

Study 8 is deterministic and finite:

- 3 cryptographic profiles;
- 4 recovery policies;
- 4 contact regimes;
- 4 disruption schedules;
- 6 compromise offsets;
- 3 logical recovery deadlines;
- total population: **3,456 positions**.

Profiles:

- `PROFILE_512_44`
- `PROFILE_768_65`
- `PROFILE_1024_87`

Object budgets:

- 12,560 bytes
- 17,460 bytes
- 24,236 bytes

Policies:

- `P0_HARD_CUTOVER`
- `P1_STAGED_CUTOVER`
- `P2_HYBRID_OVERLAP`
- `P3_CONTACT_AWARE_STAGED`

Primary frozen result:

- each policy: **635/864 = 73.4954%**
- P3 minus P1: **0.000000 percentage points**

Profile success proportions:

- 93.7500%
- 64.9306%
- 61.8056%

Time is logical-slot model time only. Never convert it to physical seconds/hours or operational spacecraft time.

Do not infer CPU, PQC execution latency, memory, energy, thermal, RF throughput, BER, coding, link margin, real contact duration, ground-station processing, CCSDS overhead, mission availability, or operational recovery time.

`TRUST_RESTORED` is a modeled terminal state only.

## 7. Frozen Study 8E anchors

Corrected population: `S8E-SATNOGS-POP-002`  
Frozen trace: `S8E-SATNOGS-TRACE-002`

Trace:

- 20 satellite-station pairs;
- 476 frozen observation rows;
- trace SHA-256: `6f80a44fa6cfa63a70df49de3ba447de3d59efe0632208180f26552f37b46a8e`.

Corrected execution:

- protocol: `S8E-CANON-EXEC-001`
- runner: `S8E-CANON-RUNNER-004`
- corrected workflow run: `35536583594`
- corrected artifact: `10613372166`
- artifact ZIP SHA-256: `3e9c6c7899a9853682d29fa92ea37589c4684db49b16a0a289be054a3553bfee`
- freeze: `S8E-CANON-RESULTS-002-FREEZE-001`

Corrected population results:

- total cases: **65,376**
- finite: **17,640**
- non-finite: **47,736**
- finite fraction: **26.9824%**
- finite threshold min/median/max: **48 / 345 / 57,727 modeled bit/s**
- horizon finite: 6 h **5.2863%**, 12 h **20.5947%**, 24 h **55.0661%**
- A0/A1 finite fraction: **40.5286%**
- A2/A3 finite fraction: **13.4361%**
- each policy finite classification: **4,410 / 16,344**
- P3 vs P1 matched cases: 16,344
- both finite: 4,410
- both non-finite: 11,934
- finite P3 minus P1 differences: all **0 bit/s**
- profile-burden ordering violations: **0**
- rollback violations: **0**
- stale-acceptance violations: **0**

The first canonical Results-001 package is invalidated and must not be used scientifically.

Correct strict-before-horizon sufficient upper bound:

`floor(8B/d_min) + 1`

The manuscript must define `B` and `d_min` self-containedly from the frozen protocol.

SatNOGS timestamps are timing proxies only:

- observation does not equal authenticated/bidirectional command contact;
- transmitter baud does not equal usable payload throughput;
- station identity does not imply `source_trusted`;
- TLE epoch does not imply cryptographic epoch validity.

`hypothetical_uniform_effective_payload_rate_bps` is a modeled solved threshold, not measured throughput.

## 8. Paper 5 non-overlap

Paper 5 / Study 9 is a separate semantic-interoperability/action-identifiability line. Do not import its data, conclusions, or semantic evidence into Paper 4.

Authority:

`publication/Paper_4_Study_8/PAPER4_STUDY8_8E_ARCHITECTURE_AND_NONOVERLAP_GATE_2026-09-20.md`

## 9. Prior Acta manuscript

Historical submitted manuscript:

`publication/Paper_4_Study_8/Acta_Astronautica/ACTA_ASTRONAUTICA_MANUSCRIPT.docx`

Historical manuscript ID: `AA-D-26-02872`

The Acta package is immutable. Do not edit, replace, or rewrite those submitted binaries.

Use the Acta manuscript only as a visual-quality benchmark for:

- professional scholarly typography;
- compact page rhythm;
- heading hierarchy;
- paragraph spacing;
- list treatment;
- figure/caption balance;
- reference presentation;
- overall manuscript polish.

The R5 IJSCCN manuscript must follow current Wiley/IJSCCN rules, not Acta venue requirements.

## 10. Current formatting decision

Do **not** upload local R4.3.

R4.3 fixed a broken Word list definition but remains rejected as a submission candidate by the author because the overall formatting/design is not publication-quality.

R5 should be a clean rebuild, not another patch.

Expected direction, subject to the live-policy audit:

- professional single-column reviewer manuscript;
- Times New Roman 12 pt if the live IJSCCN preference remains current;
- restrained heading hierarchy;
- compact scholarly paragraph spacing;
- no slide-like giant bullet lists;
- convert lists to prose or true tables where that improves scholarly presentation;
- do not imitate Wiley's final two-column production PDF;
- tables placed as required by the live IJSCCN rule, historically stated as separate pages after References;
- figures treated as required by live IJSCCN instructions, historically stated as separate TIFF/EPS uploads;
- dedicated figure-legends section if required/recommended;
- mandatory GTOC handled exactly as current IJSCCN requires;
- biography/photo supplied in a way that guarantees compliance without misclassifying them as scientific supplementary material.

## 11. Tables and figures planned for R5

Do not invent new scientific findings.

Potential reader-facing tables, if supported by the live rules and existing evidence:

### Table 1 — Study 8 deterministic experimental design

A compact table can replace the ugly six-item factor list. It may include factor, number of levels, values/interpretation, and total population = 3,456.

### Table 2 — Study 8E canonical evaluation summary

May summarize existing frozen trace/case/finite/non-finite/horizon/threshold values only.

No new calculations beyond presentation-preserving summaries unless separately authorized.

Figures:

- Figure 1: state-machine/recovery schematic
- Figure 2: Study 8 fixed-capacity/profile result
- Figure 3: Study 8E elapsed-time/finite-threshold result
- GTOC graphic: separate graphical TOC item, not Figure 4

Where line-art figures are regenerated, render from source at the current preferred journal resolution rather than raster upsampling.

## 12. Current literature/citation issue to resolve

PR #156 remains open and unmerged:

**Paper 4: reconcile De Zuane citation to peer-reviewed IEEE LANMAN record**

It updates the De Zuane et al. citation from the arXiv-only version to the peer-reviewed IEEE LANMAN 2026 proceedings record, DOI:

`10.1109/LANMAN69841.2026.11623493`

Before R5 final content freeze, inspect PR #156 and reconcile the citation deliberately. Do not assume that PR has merged.

## 13. Privacy boundary

Public repository:

- may contain public-safe templates and scientific material;
- must not contain private email, telephone, postal address, or author photograph.

Ignored local paths:

`publication/Paper_4_Study_8/IJSCCN/_local_private/`

`publication/Paper_4_Study_8/IJSCCN/_local_submission/`

The author has already supplied private metadata and a recent photograph locally. Keep them local.

Personalized R5 upload-ready files must be generated only under `_local_submission/`.

## 14. AI disclosure

The live Wiley portal presented a certification requiring AI-generated-content/tool use to be described within the Methods section.

The current manuscript therefore contains a Methods disclosure identifying OpenAI ChatGPT / GPT-5.6 Sol and its role in drafting/restructuring prose, language editing, literature navigation, claim-boundary checking, and submission preparation, while explicitly stating that it did not generate or alter Study 8/8E research data, protocols, canonical results, evidence hashes, or scientific endpoints.

Re-check the current Wiley/IJSCCN AI policy during the live audit. Preserve complete, truthful disclosure and human responsibility.

## 15. Data/reproducibility

IJSCCN historically used Wiley's "expects data" policy. Re-check this live.

Current approach:

- public GitHub repository contains data/code/scripts/frozen protocols/results/audit records;
- manuscript Data Availability Statement links to the repository;
- repository should be cited in the reference list;
- for R5, prefer an immutable commit/release identity rather than only a floating repository homepage;
- a Zenodo DOI may improve archival permanence but is not assumed mandatory unless current guidance says so.

## 16. Portal state

Wiley submission workflow encountered:

- Article Type
- Main Document upload
- Optional Files
- later metadata/author details steps

Article Type: **Original Paper**

The live portal required confirmations for:

- conflict of interest;
- licensing;
- sole submission / not published or in press elsewhere;
- color policy;
- author/contact data processing;
- license authority;
- AI disclosure compliance;
- Wiley internal AI processing of submission data.

Do not resume portal upload until R5 passes the full validation gate.

## 17. R5 validation gate

Before calling R5 submission-ready, require:

1. live-policy requirement matrix complete;
2. all journal/portal conflicts reconciled;
3. manuscript text/evidence preservation audit;
4. citation/reference existence and ordering audit;
5. figure resolution/dimensions/legibility audit;
6. table-format/placement audit;
7. GTOC audit;
8. biography/photo audit;
9. title-page/contact/declaration audit;
10. AI/funding/COI/ethics/data audit;
11. zero em-dash check across all publisher-facing files;
12. DOCX metadata/comments/tracked-changes/hidden-text check;
13. render every DOCX;
14. inspect every page visually at normal reading scale;
15. inspect every figure separately;
16. compare R5 visual quality against the Acta benchmark;
17. confirm local privacy and clean Git state;
18. create exact portal upload map;
19. obtain explicit author approval of final documents;
20. obtain separate explicit authorization before final publisher submission.

A technical "renders without clipping" check alone is insufficient. The visual acceptance question is:

> Would this exact file look professionally prepared if opened by an IJSCCN editor or reviewer?

## 18. Repository authorities to inspect first in the new chat

- `docs/CURRENT_PUBLICATION_STATE.md`
- `publication/Paper_4_Study_8/IJSCCN/README.md`
- `publication/Paper_4_Study_8/IJSCCN/SUBMISSION_CHECKLIST.md`
- `publication/Paper_4_Study_8/IJSCCN/MANUSCRIPT_IJSCCN.md`
- `publication/Paper_4_Study_8/Rebuilt_Study8_8E/MANUSCRIPT.md`
- `publication/Paper_4_Study_8/Rebuilt_Study8_8E/MANUSCRIPT_STATUS.json`
- `publication/Paper_4_Study_8/Rebuilt_Study8_8E/CLAIM_LEDGER.csv`
- `publication/Paper_4_Study_8/Rebuilt_Study8_8E/LITERATURE_REFRESH_2026-09-21.md`
- `publication/Paper_4_Study_8/PAPER4_STUDY8_8E_ARCHITECTURE_AND_NONOVERLAP_GATE_2026-09-20.md`
- `study8/STUDY8_TECHNICAL_CLOSE.json`
- `study8e/CURRENT_EXTENSION_STATE.md`
- `study8e/CANONICAL_RESULTS_002_FREEZE.json`
- `study8e/CANONICAL_RESULTS_002_AUDIT_HANDOFF.json`
- immutable Acta manuscript/package under `publication/Paper_4_Study_8/Acta_Astronautica/`

## 19. Recommended first action in the new chat

Do **not** immediately generate a new DOCX.

First:

1. fetch current `main` and this handoff/PR;
2. inspect the listed repository authorities;
3. browse the four live Wiley/IJSCCN entry pages and every relevant linked page;
4. build a detailed compliance matrix with source URLs and current dates;
5. compare that matrix to the current R4.3 design and the Acta visual benchmark;
6. propose the exact R5 manuscript/document design;
7. get author agreement on the design if any consequential ambiguity remains;
8. then rebuild the manuscript and submission documents;
9. render and inspect every page before any portal upload resumes.

## 20. Authorization boundary

Authorized:

- read-only research;
- current-policy verification;
- R5 manuscript/submission-document preparation;
- formatting/QA;
- public-safe repository documentation.

Not authorized without separate explicit approval:

- new scientific execution;
- alteration of frozen Study 8/Study 8E results;
- modification of the submitted Acta binaries;
- final publisher submission.

