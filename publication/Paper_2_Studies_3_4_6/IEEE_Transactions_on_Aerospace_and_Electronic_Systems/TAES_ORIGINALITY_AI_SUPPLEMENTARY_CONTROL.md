# TAES Originality, AI, and Supplementary-Material Control

**Status:** `ACTIVE_DEVELOPMENT_CONTROL`  
**Target:** IEEE Transactions on Aerospace and Electronic Systems  
**Paper:** Studies 3 + 4 + 6 only

## 1. Originality and self-overlap control

TAES publishes original material that is not simultaneously under review elsewhere. The final Paper-2 manuscript must be scientifically distinct from the two active submitted publication lines in this repository.

### Paper 1 boundary

Paper 1 is submitted to AIAA Journal of Aerospace Information Systems as manuscript `2026-09-I012066` and uses Studies 1 + 2 only.

Paper 2 must not reuse Study-1 or Study-2 observations as if they were new Paper-2 evidence. If a published Paper-1 article later becomes relevant background before Paper-2 submission, it must be cited and the difference between the papers made explicit.

### Paper 4 boundary

Paper 4 is submitted to Acta Astronautica as manuscript `AA-D-26-02872` and uses Study 8 only.

Paper 2 must not import Study-8 observations, cryptographic-agility findings, or submitted manuscript text as Paper-2 evidence.

### Study 5 boundary

Study 5 is deferred from the Paper-2 core. Its external-dataset result may be discussed only if it has a clearly identified background/limitation role. It must not be presented as external empirical validation of Studies 3, 4, or 6.

### Text-recycling control

Before submission:

1. compare the final TAES manuscript against submitted/published author manuscripts available in the repository;
2. inspect any repeated phrases, paragraph structures, tables, and figures;
3. cite prior author work where scientifically relevant;
4. rewrite generic framing rather than copying prior manuscript language;
5. preserve necessary technical terminology where exact terminology is required.

## 2. Previously rejected manuscript disclosure

TAES requires disclosure if the same or a substantially similar manuscript was previously reviewed and rejected by any journal. If that occurs before TAES submission:

- record the prior journal and decision;
- retain all editorial/reviewer correspondence;
- prepare a concise explanation of why the manuscript is being resubmitted;
- provide prior correspondence to TAES if the submission workflow requires it.

As of this file's creation, Paper 2 has not been submitted or rejected by another journal.

## 3. IEEE AI-use policy

Current IEEE/AESS guidance allows AI-generated content when disclosed in the article Acknowledgments section. The disclosure must identify:

- the AI system used;
- the section(s) or content types in which AI-generated content was used;
- the level of assistance.

Editing and grammar enhancement alone generally do not require disclosure, though IEEE recommends disclosure. Paper 2 should use the stronger disclosure path because ChatGPT is assisting with organization, drafting, source checking, and manuscript preparation after the science was frozen.

### Working disclosure candidate

The exact wording is not frozen, but the final disclosure should accurately state that OpenAI ChatGPT was used after the Study 3, Study 4, and Study 6 designs/results were frozen to assist with manuscript organization and drafting, literature/source checking, terminology consistency, reproducibility documentation, and submission preparation. It should also state that the author designed and conducted the research, generated and analyzed the experimental/model outputs, selected the frozen study conditions, verified all numerical results and citations, and remains solely responsible for the final article.

Do not state that AI had no role in drafting if AI-generated prose remains in the submitted manuscript.

## 4. Citation integrity control

Because AI-assisted drafting can create citation risk:

- every external factual claim must be traced to a verified source;
- primary/authoritative sources should be preferred where possible;
- bibliographic metadata must be checked independently;
- references must not be accepted solely because an AI system produced them;
- reference-list formatting may be automated only after source identity is verified;
- no fabricated DOI, title, author, volume, issue, page, or publication-year value may enter the final manuscript.

## 5. Supplementary-material decision

TAES allows supplementary data, code, images, multimedia, and supporting PDF documents. Supplementary material intended to accompany the article must be provided at initial submission for peer review and referenced in the main manuscript.

### Current Paper-2 plan

The public GitHub repository remains the primary reproducibility record. A supplementary snapshot is **not yet locked**.

Potential submission-time supplementary package:

- a README explaining the three frozen study records and how to reproduce/audit them;
- exact source/result files required to recreate the reported tables;
- independent-audit outputs;
- a machine-readable manifest with file hashes.

### Supplementary-package safeguards

- do not copy Study 1, Study 2, Study 5, Study 7, or Study 8 into a Paper-2 supplementary population;
- do not alter Study 3, 4, or 6 files for manuscript convenience;
- do not create post-hoc observations or analyses and label them as frozen evidence;
- if a derived publication table is generated from frozen evidence, preserve the derivation script and source identity;
- include a README with description, environment, setup/run instructions where applicable, expected outputs, and contact information.

## 6. Data and code availability statement

A final statement will be drafted only after deciding whether TAES supplementary material will be used. At minimum, it should direct readers to the public repository and identify the exact frozen Study 3, 4, and 6 records used by the article.

Do not imply that repository access constitutes external replication or operational validation.

## 7. Final pre-submission originality gate

Before final authorization:

- [ ] no concurrent submission exists;
- [ ] prior-rejection disclosure status reviewed;
- [ ] self-overlap comparison completed;
- [ ] AI disclosure present and accurate;
- [ ] citation ledger fully verified;
- [ ] supplementary-material decision frozen;
- [ ] data/code availability statement matches actual released material;
- [ ] final author explicitly approves all disclosures.
