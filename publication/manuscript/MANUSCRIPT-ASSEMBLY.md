# Target-Neutral Manuscript Assembly

**Assembly status:** cybersecurity framing integrated; reproducibility hardening complete; author attestations complete  
**Scientific evidence audit:** `docs/35-wp10-g5-manuscript-evidence-audit.md` — PASS  
**Quantitative authority:** `docs/28`–`docs/34`, `publication/tables/`, and the reconstructed `analysis/` regression package  
**Primary target journal:** Computers & Security (Elsevier), Full Length Article  
**Backup targets:** AIAA Journal of Aerospace Information Systems; IEEE Transactions on Aerospace and Electronic Systems  
**Author-attestation gate: PASS**  
**Current submission state:** **final submission-export gate**

## Authoritative manuscript order

1. `00-title-abstract.md` — title, abstract, keywords
2. `01-introduction.md` — cybersecurity problem, post-detection gap, contributions, scope
3. `02-background-and-related-work.md` — Mission Aware, FDIR/autonomy, cyber resilience, trusted recovery, venue-adjacent peer work, SPARTA correspondence, NIST incident-response positioning, targeted gap
4. `03-methods.md` — post-access adversary model, defender-knowledge model, TB0–TB5 trust boundaries, security/dependability properties, testbed boundary, frozen design, policies, outcomes, validity, statistical analysis, provenance, reproducibility
5. `04-results.md` — evidence-locked proposition results
6. `05-discussion.md` — bounded interpretation, cybersecurity design implications, limitations, and separately scoped follow-on research program
7. `06-conclusion.md` — conclusions and future work
8. `07-declarations-and-availability.md` — ethics, responsible-research boundary, data/code availability, reproducibility, submission declarations

The temporary `02a`, `03a`, and `05a` upgrade modules have been integrated into conventional Sections 2, 3, and 5 and removed to avoid duplicate prose drift.

## Bibliography source

- `../../references/references.bib` — canonical, deduplicated manuscript bibliography, including NIST SP 800-61 Rev. 3, the frozen-event SPARTA references, and verified venue-adjacent cybersecurity literature.

A journal export must format this single canonical bibliography to the target journal style without changing citation meaning.

## Main publication displays

- Table R1: `../tables/table-r1-proposition-summary.csv`
- Table R2: `../tables/table-r2-p2-contact-effects.csv`
- Table R3: `../tables/table-r3-p3-p4-evidence-pathways.csv`
- Table R4: `../tables/table-r4-p5-pareto-status.csv`
- Table R5: `../tables/table-r5-cybersecurity-positioning.csv`
- Table R6: `../tables/table-r6-security-property-mapping.csv`
- Figure R1: `../figures/figure-r1-p2-contact-effects.svg`
- Figure R2: `../figures/figure-r2-p3-trusted-recovery.svg`
- Figure R3: `../figures/figure-r3-p4-selection-pathway.svg`
- Figure R4: `../figures/figure-r4-p5-pareto-status.svg`

Supplementary provenance table:

- Table S1: `../tables/table-s1-execution-provenance-sensitivity.csv`

## Scientific non-negotiables for any journal export

Any combined DOCX/LaTeX/PDF or journal-specific rewrite must preserve:

- exactly 720 VALID primary analysis observations;
- P1 unsupported on predeclared M01/M02/M03/M06 outcomes;
- C1 described as synthetic/modelled contact only;
- A16/A17 retained as P6, with post-authorization delegation to the P5 rollback mechanism;
- M05 explicit event/censor representation and 30-s horizon;
- P3 broader evidence-dependent finding while the narrower restoration-without-verification mechanism remains absent;
- P4 as actual selection/action/consequence, with no objective correctness oracle;
- Study 1 T1 as omission/reduction of selected policy-visible evidence fields, not a separate stale/contradictory/forged-evidence experiment;
- P7 as a frozen deterministic rule-based selector, not a learned or AI/ML scientific method;
- `ENTER_SAFE_MODE` as an experimental modeled action;
- M03 structural zero as an observed result, not proof of universal safety;
- P5 as condition-specific, with no 5/9 success-rate language, no weighted score, and no global policy rank;
- execution provenance 1/9/710 across commits A/B/C and the 29-seed/696-observation final-C sensitivity as sensitivity only;
- no operational spacecraft, real RF, real operator timing, flightworthiness, or certification claim;
- SPARTA mappings described as frozen behavioral/experimental correspondence rather than proof that complete operational attack chains were reproduced;
- NIST SP 800-61 Rev. 3 mapping described as lifecycle positioning rather than organizational compliance;
- Study 2/Study 3 proposals kept scientifically separate from the frozen Study 1 population.

## Submission metadata resolved

- single author: Aman Kumar Singh;
- affiliation: Independent Researcher, The Woodlands, Texas, United States;
- corresponding-author email and ORCID are recorded in `submission-inputs.csv`;
- funding: independent research, no external funding;
- competing interests: no competing financial or non-financial interests declared;
- acknowledgments: none to add for this manuscript;
- final CRediT role statement: author approved;
- generative-AI declaration: author approved, with live publisher-policy recheck retained;
- simultaneous consideration: author confirmed the manuscript is not simultaneously under consideration elsewhere;
- Zenodo v1.0.0 version DOI and concept DOI are fixed;
- Code Availability is intentionally bound to the reproducibility-hardened `main` snapshot `99892bd9bb0828bdb3d0a28caf40dbc18fcbc4dc`, which contains the validated WP10 reconstruction; later submission-only commits do not redefine that scientific/reproducibility snapshot;
- primary target: Computers & Security, Full Length Article.

## Submission-state controls

The current Computers & Security scope/policy review and cybersecurity fit audit have been completed during this preparation cycle. Because publisher portals and policies can change, a final live Guide for Authors/Aims & Scope/Editorial Manager check remains mandatory on the actual submission date.

The author-owned factual declarations are closed. The remaining final-export decisions/checks are deliberately different in kind:

- decide whether to adopt the concise Computers & Security abstract candidate or retain the authoritative target-neutral abstract;
- confirm current article-type naming, length/reference/display/file requirements, and portal fields;
- recheck current AI/ML scope, generative-AI disclosure, and competing-interest workflows;
- provide an institutional IRB/HRPP determination identifier **only if** the portal specifically requires an applicable identifier for this no-human-participant software experiment; none is invented;
- run the final citation/DOI/reference audit, frozen-results claim audit, and scope-fit audit against the exact submission export.

## Assembly rule

The component files above are the manuscript source of truth. Do not maintain a second manually copied full-text file before target-journal export, because duplicate prose copies can drift. A journal-specific export should be generated from these components only after the final pre-submission audit passes.
