# Paper 4 IJSCCN R5 Manuscript Design Specification

**Design reconciled:** 2026-09-22 UTC / 2026-09-21 America/Chicago  
**Evidence authority:** `R5_WILEY_IJSCCN_EVIDENCE_AUDIT_2026-09-22.md`  
**Target:** International Journal of Satellite Communications and Networking, Wiley  
**Article type:** Original Paper  
**Status:** EVIDENCE-RECONCILED DESIGN LOCK FOR R5 SOURCE REBUILD  
**Scientific effect:** None

## 1. Design objective

R5 is a controlled publisher-facing rebuild, not a new study.

The existing IJSCCN manuscript source is scientifically mature but over-fragmented as a journal document. The R5 objective is to improve manuscript architecture, prose density, typography, table/figure presentation, and submission packaging while preserving every frozen Study 8 and Study 8E scientific authority.

The historical Acta Astronautica manuscript remains immutable. It may be used only as a visual-quality benchmark where that does not conflict with IJSCCN/Wiley requirements.

## 2. Evidence corrections to the earlier design assumptions

The final web audit changes three earlier assumptions:

1. IJSCCN requires clear method and result content but does **not** prove that literal top-level headings named “Methods” and “Results” are mandatory.
2. Initial Free Format permits figures and tables in the editable manuscript or separately. Separate-page tables and separate figures are explicitly mandatory at revision and strongly preferred by the journal style guidance.
3. A dedicated Figure Legends section after References is Wiley-preferred and professionally useful, but it is not an IJSCCN-specific absolute initial-submission requirement.

R5 will still adopt the stricter, revision-ready presentation because it improves professionalism, but the repository must label these items correctly as design choices rather than false initial-submission mandates.

## 3. Visible title-page design

The visible manuscript title page should look like a scholarly article, not a repository status document.

Keep:

- full manuscript title;
- Aman Kumar Singh, MS, PhD;
- affiliation;
- corresponding-author marker;
- ORCID where appropriate;
- short title.

Remove from the visible title page:

- target-journal labels;
- package/build identifiers;
- internal study governance labels;
- repository workflow information;
- internal authorization language.

Scientific experiment identifiers remain in the body where they support reproducibility.

Private address, email, telephone, ORCID if treated as private in the local workflow, and author photograph remain only in ignored local-private/local-submission paths.

## 4. Word style system

### Body

- single-column Word manuscript;
- Times New Roman 12 pt;
- approximately 1-inch / 2.54 cm margins;
- restrained line spacing around 1.15 to 1.2;
- compact scholarly paragraph spacing;
- no simulated Wiley two-column production layout;
- no decorative borders, colored heading bands, text boxes, WordArt, faux DOI blocks, or copyright footers.

### Title

- Times New Roman;
- approximately 16 to 18 pt;
- bold;
- compact scholarly spacing;
- final alignment selected after rendered-page comparison.

### Author and affiliation

- approximately 11 to 12 pt;
- compact;
- corresponding-author notation conventional;
- identifying block removable if the live portal requires double-anonymized review.

### Headings

Use no more than three visible levels.

- Level 1: approximately 13 to 14 pt bold.
- Level 2: 12 pt bold.
- Level 3: 12 pt italic or bold italic only when necessary.

Avoid one-heading-per-paragraph fragmentation.

### Body prose

- prose-first scholarly narrative;
- lists only when they genuinely improve technical clarity;
- factor lattices and result summaries should use concise tables when superior to long bullet lists;
- consistent paragraph treatment;
- widow/orphan control;
- keep headings with following text.

### Punctuation

Author requirement: **zero em dashes** in every publisher-facing document.

Use commas, semicolons, parentheses, colons, or separate sentences instead.

## 5. Manuscript architecture

IJSCCN does not require literal IMRaD heading names. R5 nevertheless uses a conventional evidence-friendly architecture because it fits this paper and makes the two-study boundary easy to review.

### Front matter

1. Title.
2. Sole author and affiliation.
3. Corresponding-author information in the identified/local version.
4. ORCID as appropriate.
5. Short title.
6. Abstract, maximum 250 words.
7. Keywords, maximum 8.

### 1. Introduction

The Introduction should:

- establish trusted cryptographic recovery as a satellite systems problem;
- position the work against current PQC, crypto-agility, satellite security, NTN, and recovery literature;
- state the narrow research gap;
- explain that Study 8 and Study 8E are separately governed and never statistically pooled;
- distinguish Paper 4 from Paper 5 / Study 9;
- state contributions without marketing language or unsupported novelty claims.

A compact related-work subsection may be retained if it improves flow. It should not become a detached literature catalogue.

### 2. Recovery Model and Methods

The exact heading may be “Recovery Model and Methods,” “Methodology,” or another clear technical equivalent. The content must make the study design unmistakable.

#### 2.1 Two-study evidence architecture

State explicitly:

- Study 8 = `S8-PQC-ICR-001`;
- Study 8E = `S8E-ECTV-001`;
- separate finite populations;
- no pooled denominator or statistic;
- no physical-time conversion of Study 8 logical slots;
- Study 9 / Paper 5 evidence excluded.

#### 2.2 Shared trusted-recovery mechanism

Describe concisely:

- frozen recovery state progression;
- cryptographic profiles and exact transition-object burdens;
- P0 to P3 policy semantics;
- bounded disruption schedules;
- shared interpretation boundary.

Avoid slide-style bullet expansion where Table 1 can carry structured factors.

#### 2.3 Study 8 controlled logical-contact design

Retain only frozen design facts:

- complete deterministic population;
- logical contact regimes;
- disruption schedules;
- compromise offsets;
- logical deadlines;
- primary endpoint;
- P3 minus P1 prespecified contrast;
- exact finite-population reporting rationale.

Logical slots remain ordering units with no physical duration.

#### 2.4 Study 8E observation-opportunity timing design

Retain only frozen extension facts:

- SatNOGS source and population governance;
- 20 satellite-station pairs;
- 476 frozen observation rows;
- 454 eligible anchors;
- 6 h, 12 h, 24 h extension-only horizons;
- minimum hypothetical uniform effective payload-rate endpoint;
- corrected canonical runner/result freeze;
- observation-opportunity proxy restrictions.

Define the strict sufficient bound self-containedly:

- `B = sum(profile_object_bytes) + max(profile_object_bytes)`;
- `d_min` = shortest positive future-window duration in exact seconds;
- `U_strict = floor(8B/d_min) + 1` integer bit/s.

Explain that `U_strict` is a model-search sufficiency construction only, not a physical link measurement.

#### 2.5 Reproducibility and AI-assisted manuscript preparation

Scientific reproducibility must remain separate from manuscript-preparation tooling.

The Methods AI disclosure should identify OpenAI ChatGPT / GPT-5.6 Sol and describe its use for drafting, restructuring, language editing, literature navigation, claim-boundary checking, and submission preparation.

It must state that the author independently verified the final content and that AI did not generate or alter:

- Study 8 data;
- Study 8E data;
- study protocols;
- canonical results;
- evidence hashes;
- scientific endpoints.

## 6. Results architecture

Keep Study 8 and Study 8E separate.

### 3.1 Study 8 fixed-capacity feasibility

Required frozen headline values:

- 3,456 total positions;
- each policy: 635/864 = 73.4954%;
- P3 minus P1: 0.000000 percentage points;
- profile success: 93.7500%, 64.9306%, 61.8056%.

Logical-time results must never be converted to seconds, minutes, hours, orbital periods, or operational recovery time.

### 3.2 Study 8E external timing evaluation

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
- finite P3 minus P1 differences: all 0 bit/s;
- profile-burden ordering violations: 0;
- rollback violations: 0;
- stale-acceptance violations: 0.

Only already frozen horizon/disruption summaries may be reported.

### 3.3 Cross-study synthesis without pooling

Permitted:

- structural comparison;
- qualitative consistency;
- explanation of different estimands.

Forbidden:

- pooled sample sizes;
- combined effects;
- new statistical tests;
- Study 8 logical-slot to elapsed-time mapping;
- calling Study 8E operational validation;
- calling SatNOGS observations authenticated command contacts;
- calling modeled bit/s measured throughput.

## 7. Discussion

Use a small number of substantive subsections.

Recommended topics:

1. why the P3 guard cannot create communication opportunity or capacity;
2. fixed-capacity feasibility versus solved-rate burden;
3. importance of opportunity timing and recovery horizon;
4. policy-state tradeoffs despite a null feasibility contrast;
5. engineering implications bounded to the modeled evidence;
6. limitations and external-validity boundary.

The discussion must not infer:

- CPU performance;
- PQC execution latency;
- memory;
- energy;
- thermal effects;
- RF throughput;
- BER;
- coding efficiency;
- link margin;
- mission availability;
- operational ground-station performance;
- real spacecraft recovery time.

## 8. Conclusion

Keep concise and evidence-bounded.

State:

- the Study 8 fixed-capacity finding;
- the Study 8E modeled-rate finding;
- the role of transition-object burden, opportunity timing, and recovery horizon;
- the exact negative policy result.

Avoid operational deployment claims or unsupported superiority language.

## 9. Tables

### Table 1: Study 8 deterministic experimental design

Use frozen factors only.

Possible columns:

- Factor;
- Levels;
- Values / interpretation.

No new calculation or scientific inference.

### Table 2: Study 8E canonical evaluation summary

Use frozen values only.

Possible rows:

- trace identity;
- selected trace pairs;
- frozen observations;
- eligible anchors;
- canonical cases;
- finite/non-finite counts;
- finite fraction;
- threshold minimum/median/maximum;
- P3/P1 matched comparison counts;
- structural violation counts.

### Initial-submission placement

For R5, each table will appear on a separate page after References.

This is a conservative, journal-preferred, revision-ready design choice. The evidence audit does not classify it as an absolute Free Format initial-submission mandate.

## 10. Figures

Scientific figures:

1. Trusted-recovery state-machine schematic.
2. Study 8 fixed-capacity/profile result.
3. Study 8E finite-threshold/horizon result.

The GTOC remains separate and is not Figure 4.

R5 figure rules:

- regenerate from source;
- TIFF for upload, with EPS retained if useful;
- 800 dpi target for graphs/drawings, never below the journal's 600 dpi minimum;
- no raster upsampling to simulate resolution;
- consistent labels, type sizes, line weights, and orientation;
- no scientific meaning dependent solely on color;
- each compound figure supplied as one file;
- no tints;
- symbol keys inside artwork when needed.

Figure legends will be collected in a dedicated post-References section as a Wiley-preferred, revision-ready presentation.

## 11. GTOC

Separate submission item.

Must include:

- paper title;
- Aman Kumar Singh*;
- corresponding-author asterisk;
- abstract figure;
- maximum 80 words or 3 sentences.

The graphic should communicate:

- Study 8 controlled logical-contact layer;
- Study 8E public observation-opportunity timing layer;
- common frozen recovery mechanism;
- separate populations;
- no pooled statistic;
- no slot-to-seconds mapping;
- no operational-contact or measured-throughput implication.

## 12. Biography and photograph

Biography:

- maximum 200 words;
- concise and scholarly;
- no unnecessary personal information.

Photo:

- recent;
- local-only;
- never committed.

## 13. Data and repository presentation

The manuscript will include a Data Availability Statement.

The repository/data record will be formally cited in the reference list in Wiley-compatible data-citation form.

Minimum acceptable persistent evidence identity for R5:

- immutable repository commit or release.

A DOI-backed archival snapshot may be created later if deliberately authorized. Zenodo is optional, not mandatory.

## 14. Duplicate/fragmentation gate

Wiley's policy makes Paper 4 / Paper 5 separation a publication-integrity requirement.

Before content freeze, verify:

- no Study 9 / Paper 5 evidence appears in Paper 4;
- Paper 4's research question, population, endpoints, and contribution remain distinct;
- no language suggests one manuscript is merely a fragment of the other;
- overlapping background material is cited or rewritten transparently rather than recycled without attribution.

## 15. End matter

Recommended order before References:

1. Funding.
2. Conflict of Interest.
3. Author Contributions.
4. Ethics Statement.
5. Data Availability Statement.

Then:

6. References.
7. Figure Legends.
8. Table 1, separate page.
9. Table 2, separate page.
10. Biography only if the portal/journal handling indicates it belongs in the main manuscript rather than a separate file.

The substantive AI disclosure remains in Methods because of the previously observed live portal requirement.

## 16. Reviewer-readiness QA

Use Wiley's peer-review criteria as R5 quality gates:

- clear research question;
- originality stated narrowly and supportably;
- contribution distinct from prior literature;
- conclusions directly supported by evidence;
- reproducible methodology;
- related and contradictory work acknowledged;
- figures/tables necessary and readable;
- references balanced and accurate;
- no factual, numerical, unit, equation, or hash errors;
- no exaggerated conclusions;
- no fragmented-publication appearance;
- structure concise enough for reviewers to assess efficiently.

## 17. Visual QA

Technical render success is necessary but not sufficient.

Before any R5 DOCX is called submission-ready:

- render every page;
- inspect at normal reading scale and 100 percent;
- inspect every figure separately;
- inspect every table separately;
- verify no clipping, overlap, broken glyphs, or hidden text;
- verify no orphan headings or unacceptable widows;
- correct excessive whitespace and poor page rhythm;
- compare typography and scholarly page composition with the immutable Acta benchmark;
- follow IJSCCN whenever the benchmark conflicts with current policy.

## 18. Scientific preservation gate

Allowed:

- section organization;
- heading names;
- paragraph order;
- prose clarity;
- typography;
- table presentation;
- figure regeneration from frozen data/source;
- submission-document organization.

Forbidden:

- modifying frozen Study 8 or Study 8E data;
- modifying populations;
- changing protocols;
- changing endpoints;
- changing canonical results;
- changing hashes;
- changing prespecified contrasts;
- pooling populations;
- importing Paper 5 evidence;
- modifying rejected Acta submitted binaries.

## 19. Build sequence

1. Public-policy evidence audit. **COMPLETE / PASS.**
2. Reconciled requirement matrix. **COMPLETE / PASS.**
3. Reconciled design specification. **COMPLETE with this document.**
4. Rebuild the R5 venue-facing manuscript source.
5. Run numerical, equation, hash, citation, non-overlap, and claim-ledger preservation audits.
6. Update the R5 Word build pipeline.
7. Build a public-safe QA DOCX.
8. Render and inspect every page.
9. Regenerate/fix figures and tables until visual QA passes.
10. Build local personalized materials under ignored private paths.
11. Verify GTOC, biography/photo, DAS, funding, COI, ethics, AI disclosure, and submission files.
12. Re-open the live Research Exchange portal and resolve the remaining portal-only questions.
13. Produce the exact upload map.
14. Obtain separate explicit authorization before final publisher submission.

**Design gate: PASS FOR R5 SOURCE REBUILD.**

**R5 submission-ready DOCX gate: NOT YET PASSED.**

**Final Wiley submission: NOT AUTHORIZED.**
