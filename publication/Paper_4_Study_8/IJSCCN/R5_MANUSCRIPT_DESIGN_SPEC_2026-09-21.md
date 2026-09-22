# Paper 4 IJSCCN R5 Manuscript Design Specification

**Design date:** 2026-09-21  
**Depends on:** R5_LIVE_POLICY_REQUIREMENT_MATRIX_2026-09-21.md  
**Target:** International Journal of Satellite Communications and Networking, Wiley  
**Article type:** Original Paper  
**Status:** DESIGN LOCK FOR SOURCE REBUILD  
**Scientific effect:** None

## 1. Why R5 is a rebuild rather than another R4.x patch

The existing IJSCCN source is scientifically mature but visually and structurally over-fragmented for a professional reviewer manuscript.

Current source audit on 2026-09-21:

- approximately 7,011 words;
- 71 section/subsection headings;
- 69 Markdown bullet-list lines;
- 9 em-dash characters;
- Methods and Results are distributed across Study 1 and Study 2 sections rather than being presented under explicit top-level Methods and Results headings;
- the strict-before-horizon bound is present, but B and d_min are not defined self-containedly at the point of use;
- the AI disclosure is currently in Declarations rather than Methods.

These issues are presentation and manuscript-architecture defects. They do not require or authorize any change to frozen Study 8 or Study 8E science.

## 2. R5 visible title-page design

The visible R5 manuscript should open like a conventional scholarly article, not a repository status document.

Keep:

- manuscript title;
- Aman Kumar Singh, MS, PhD;
- affiliation;
- corresponding-author marker and local-only contact block as required;
- ORCID in the local personalized version;
- short title where appropriate.

Remove from the visible front page:

- "IJSCCN Submission Manuscript";
- "Target journal:";
- internal experiment identifiers presented as title-page metadata;
- repository-governance labels;
- package version labels;
- technical build information.

Experiment identifiers remain in Methods where they support reproducibility.

Private author metadata stays under the ignored local-only submission path and must never be committed to the public repository.

## 3. Word style system

R5 is a professional single-column reviewer manuscript.

### Page and body

- standard Word page size;
- approximately 1-inch / 2.54 cm margins;
- Times New Roman 12 pt body;
- 1.15 to 1.2 line spacing;
- restrained 4 to 6 pt paragraph spacing;
- no double-line spacing unless later required by the portal;
- no decorative page borders, colored heading bands, WordArt, text boxes, or production-style columns;
- no manually simulated Wiley headers, issue metadata, DOI blocks, or copyright footers.

### Title

- Times New Roman;
- 16 to 18 pt;
- bold;
- left aligned or centered based on final visual QA;
- compact spacing;
- no oversized title-page whitespace.

### Author line and affiliation

- 11 to 12 pt;
- professional compact spacing;
- corresponding-author indicator handled conventionally;
- private contact details only in the local personalized copy.

### Headings

Use no more than three visible heading levels.

- Level 1: 13 to 14 pt bold.
- Level 2: 12 pt bold.
- Level 3 only when scientifically necessary: 12 pt italic or bold italic.

Avoid a heading for every small result or limitation. Prefer coherent paragraphs.

### Paragraphs

- scholarly prose rather than slide-style fragments;
- first paragraph after a heading unindented;
- subsequent body paragraphs may use a small first-line indent or consistent block spacing, but not both heavily;
- widow/orphan control enabled;
- headings kept with following paragraph.

### Punctuation

- zero em dashes in every publisher-facing document;
- prefer commas, semicolons, parentheses, or sentence breaks;
- use standard hyphens only where linguistically appropriate.

## 4. R5 manuscript architecture

The R5 article will use explicit venue-compatible top-level sections.

### Front matter

1. Title
2. Author and affiliation
3. Corresponding-author information in local personalized copy
4. ORCID in local personalized copy as appropriate
5. Short title
6. Abstract, maximum 250 words
7. Keywords, maximum 8

### 1. Introduction

Purpose:

- establish the satellite cybersecurity and post-quantum transition problem;
- position the work against current space/NTN PQC, crypto-agility, and satellite-cybersecurity literature;
- state the narrow gap;
- state the two-study architecture and non-pooling rule;
- summarize contributions without turning them into a bullet-heavy list unless a very short list is clearly superior.

Related-work material from the current Section 2 should be integrated into the Introduction or retained as a compact 1.x subsection only if this improves readability.

### 2. Methods

#### 2.1 Two-study architecture and evidence separation

State explicitly:

- Study 8 = S8-PQC-ICR-001;
- Study 8E = S8E-ECTV-001;
- populations are separate;
- no pooled denominator, statistic, or physical timescale is used;
- Paper 5 / Study 9 evidence is not part of this paper.

#### 2.2 Shared trusted-recovery model

Concise description of:

- state machine;
- cryptographic profiles and exact transition-object burdens;
- policies P0 through P3;
- disruption schedules;
- shared interpretation boundary.

Current large lists should be converted to concise prose and Table 1 where appropriate.

#### 2.3 Study 8 deterministic experiment

Include:

- frozen research question;
- deterministic finite population;
- logical contact model;
- endpoint and prespecified P3 minus P1 contrast;
- finite-population reporting rationale;
- reproducibility checks.

Logical slots must be explicitly identified as ordering units without physical duration.

#### 2.4 Study 8E external observation-opportunity timing evaluation

Include:

- source and frozen population governance;
- observation-opportunity mapping;
- eligible anchors and case construction;
- 6 h, 12 h, 24 h extension-only horizons;
- minimum hypothetical uniform effective payload-rate endpoint;
- strict sufficient upper-bound definition;
- corrected canonical runner and result freeze;
- SatNOGS proxy limitations.

The bound must be defined self-containedly as follows:

For a case with at least one positive-duration future window,

- B = sum(profile_object_bytes) + max(profile_object_bytes), representing the complete nominal profile-object bundle plus one largest-object retransmission;
- d_min = the shortest positive future-window duration in exact seconds;
- U_strict = floor(8B/d_min) + 1 integer bit/s.

U_strict is a model-search sufficiency construction only. It is not measured physical link capacity or SatNOGS throughput.

#### 2.5 Reproducibility, research integrity, and AI-assisted manuscript preparation

Keep scientific reproducibility statements distinct from manuscript-preparation tooling.

The AI disclosure will state truthfully that OpenAI ChatGPT / GPT-5.6 Sol assisted with drafting, restructuring, language editing, literature navigation, claim-boundary checking, and submission preparation, while the author independently verified all scientific claims, citations, numerical values, and interpretations.

It must explicitly state that the AI tool did not generate or alter:

- Study 8 data;
- Study 8E data;
- study protocols;
- canonical results;
- evidence hashes;
- scientific endpoints.

The author retains full responsibility.

### 3. Results

Keep Study 8 and Study 8E numerically separate.

#### 3.1 Study 8 fixed-capacity feasibility

Required headline values:

- total positions: 3,456;
- each policy: 635/864 = 73.4954%;
- P3 minus P1: 0.000000 percentage points;
- profile success: 93.7500%, 64.9306%, 61.8056%.

Report logical-time findings without conversion to seconds, minutes, hours, or orbital time.

#### 3.2 Study 8E observation-opportunity timing evaluation

Required corrected anchors:

- 20 satellite-station pairs;
- 476 frozen observations;
- 454 eligible anchors;
- 65,376 cases;
- 17,640 finite;
- 47,736 non-finite;
- finite fraction 26.9824%;
- finite threshold min/median/max: 48 / 345 / 57,727 modeled bit/s;
- P3 versus P1 matched: 16,344;
- both finite: 4,410;
- both non-finite: 11,934;
- all finite P3 minus P1 differences: 0 bit/s;
- profile-burden ordering violations: 0;
- rollback violations: 0;
- stale-acceptance violations: 0.

Any horizon or disruption summaries must use only already frozen values.

#### 3.3 Cross-study synthesis without pooling

This subsection may compare qualitative structural findings only.

It must not:

- pool counts;
- construct a combined sample size;
- perform new statistical tests;
- reinterpret Study 8 logical slots as elapsed time;
- describe Study 8E as operational validation or empirical spacecraft recovery validation.

### 4. Discussion

Recommended compact structure:

#### 4.1 What the null policy contrast means

Explain that a contact-aware guard did not create additional communication opportunity or capacity in the tested frozen populations.

Do not convert the null result into a claim of universal policy equivalence.

#### 4.2 Fixed-capacity feasibility versus required-rate burden

Clarify the different estimands without merging them.

#### 4.3 Implications for post-quantum satellite recovery engineering

Bound implications to modeled communication opportunity, recovery horizon, transition-object burden, and state progression.

Do not infer CPU, PQC execution latency, memory, energy, thermal behavior, RF throughput, BER, coding, link margin, mission availability, or operational recovery time.

#### 4.4 Limitations and external-validity boundary

Consolidate the current twelve limitation subsections into a smaller number of coherent paragraphs covering:

- separate finite populations;
- logical versus elapsed time;
- observation opportunity is not command contact;
- modeled rate is not measured throughput;
- cryptographic-object-only accounting;
- no execution benchmarking;
- restricted adversary;
- source-selection boundary;
- corrected-result metadata discrepancy;
- no external experimental replication;
- no universal policy-superiority conclusion.

### 5. Conclusions

Keep concise and evidence bounded.

The conclusion should:

- state the fixed-capacity Study 8 finding;
- state the Study 8E modeled-rate finding;
- emphasize communication opportunity, horizon, and transition-object burden;
- preserve the negative policy result;
- avoid operational spacecraft performance claims;
- avoid novelty overclaiming.

## 5. Tables

### Table 1. Study 8 deterministic experimental design

Purpose: replace large factor bullet lists.

Columns:

- Factor
- Levels
- Values / interpretation

Rows may include:

- cryptographic profile;
- recovery policy;
- logical contact regime;
- disruption schedule;
- compromise offset;
- logical deadline.

Footer or note: complete deterministic population = 3,456 modeled positions.

No new calculation is authorized.

### Table 2. Study 8E canonical evaluation summary

Purpose: consolidate existing frozen values.

Candidate rows:

- trace identity;
- satellite-station pairs;
- frozen observation rows;
- eligible anchors;
- canonical cases;
- finite and non-finite counts;
- finite fraction;
- threshold minimum/median/maximum;
- P3/P1 matched, both-finite, both-non-finite;
- structural violation counts.

Only frozen values may be used.

Placement: each table on its own page after References as required by IJSCCN.

## 6. Figures

Scientific figures remain:

1. Figure 1. Trusted-recovery state-machine schematic.
2. Figure 2. Study 8 fixed-capacity/profile result.
3. Figure 3. Study 8E elapsed-time/finite-threshold result.

GTOC is separate and is not Figure 4.

R5 rules:

- separate TIFF or EPS file for each scientific figure;
- 800 dpi preferred for graphs/drawings, 600 dpi minimum;
- regenerate from source when improving resolution;
- no raster upsampling;
- consistent fonts and line weights;
- readable labels at final reduction;
- no scientific meaning conveyed by color alone;
- legends in a dedicated Figure Legends section after References.

## 7. End matter

Recommended order:

1. Funding
2. Competing Interests
3. Author Contributions
4. Ethics Statement
5. Data Availability Statement
6. References
7. Figure Legends
8. Table 1, separate page
9. Table 2, separate page
10. Author Biography, if retained inside the main manuscript rather than supplied as a dedicated portal file

The substantive AI disclosure remains in Methods to satisfy the live portal requirement. A duplicate declaration should be avoided unless the portal or editor specifically requests one.

## 8. GTOC package

Create as a separate submission item:

- title;
- Aman Kumar Singh with corresponding-author asterisk;
- high-quality abstract figure;
- text not exceeding 80 words or 3 sentences.

The graphic should communicate the two-layer evidence architecture visually:

- controlled Study 8 logical-contact model;
- Study 8E public observation-opportunity timing;
- separate populations;
- common recovery mechanism;
- no pooled statistic.

Do not make the GTOC a decorative duplicate of a scientific figure if a cleaner purpose-built diagram better explains the paper.

## 9. Biography and photograph

Biography:

- maximum 200 words;
- scholarly and concise;
- no unnecessary personal detail;
- no private contact information.

Photograph:

- recent;
- local-only;
- never committed to the public repository.

## 10. Data and reproducibility presentation

The manuscript should identify the repository and frozen evidence in a reviewer-usable way.

R5 should prefer:

- immutable commit or release identity;
- formal reference-list citation for shared research data/code;
- persistent identifier if one is deliberately created later.

A Zenodo DOI would improve archival permanence but is not required by the current policy audit and is not created by this design lock.

## 11. Citation reconciliation

Open PR #156 is not merged.

Before R5 content freeze:

- inspect and deliberately reconcile the De Zuane et al. record;
- use the peer-reviewed IEEE LANMAN 2026 record if verified;
- DOI: 10.1109/LANMAN69841.2026.11623493;
- remove the obsolete preprint-only characterization from final R5 if the peer-reviewed record is used.

No assumption is made that PR #156 is already part of main.

## 12. Visual QA standard

Technical render success is necessary but insufficient.

Before R5 is considered submission-ready:

- render every DOCX;
- inspect every page at normal reading scale and 100 percent zoom;
- inspect every figure separately;
- verify no clipping, overlap, broken glyphs, orphan headings, widows, poor page breaks, or excessive whitespace;
- inspect tables for professional alignment and legibility;
- compare typography, spacing, page rhythm, caption treatment, and overall professionalism with the immutable historical Acta manuscript;
- follow IJSCCN requirements whenever Acta and IJSCCN differ.

The Acta manuscript remains immutable and must never be edited.

## 13. Scientific preservation gate

R5 rebuilding may change:

- section organization;
- paragraph order;
- heading granularity;
- prose clarity;
- typography;
- table presentation;
- figure rendering from existing source;
- submission-document organization.

R5 rebuilding may not change:

- frozen Study 8 or Study 8E data;
- populations;
- protocols;
- endpoint definitions;
- canonical results;
- hashes;
- prespecified contrasts;
- scientific claim boundaries;
- Paper 4 versus Paper 5 independence;
- rejected Acta submitted binaries.

## 14. R5 build sequence

1. Lock live policy matrix. COMPLETE.
2. Lock manuscript design specification. COMPLETE with this record.
3. Rebuild venue-facing manuscript source under the new Methods/Results architecture.
4. Reconcile PR #156 citation before content freeze.
5. Run numerical, equation, hash, citation, and claim-ledger preservation audit.
6. Build public-safe QA DOCX with placeholders only.
7. Render and inspect every page.
8. Compare against Acta visual benchmark.
9. Correct layout until professional acceptance.
10. Build personalized local-only DOCX and submission documents under _local_submission/.
11. Validate GTOC, biography/photo, figures, tables, declarations, DAS, and AI disclosure.
12. Produce exact Research Exchange upload map.
13. Obtain explicit author approval.
14. Obtain separate explicit authorization before final Wiley submission.

**Design gate:** PASS FOR R5 SOURCE-MANUSCRIPT REBUILD.  
**Publisher submission:** NOT AUTHORIZED.
