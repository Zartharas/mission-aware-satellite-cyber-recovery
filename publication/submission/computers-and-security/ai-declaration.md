# Generative-AI Disclosure — Elsevier / Computers & Security

**Status:** author-approved; reconciled to the two-study journal manuscript on 2026-09-01. Recheck the live Elsevier policy and exact portal wording on the actual submission date.

## Declaration of generative AI and AI-assisted technologies in manuscript preparation

During preparation of this journal work, the author used **OpenAI ChatGPT** to assist with manuscript organization, literature/source checking, editorial refinement, consistency checking, reproducibility documentation, repository/audit workflow support, and preparation of journal-submission materials. The author reviewed and edited the resulting content, checked scientific quantities and source claims against the frozen research record and cited sources, and takes responsibility for the publication.

## Research-process / reproducibility disclosure

### Study 1

After the Study-1 campaign and historical WP10 statistical findings were frozen—and after the Study-1 data package was published as Zenodo v1.0.0—OpenAI ChatGPT was used to assist with reconstructing, reviewing, and testing a public statistical reproducibility implementation from preserved derived inputs, outputs, and provenance records. The original executable WP10 analysis source was not recovered. This reconstruction did **not** generate campaign observations, consume campaign seeds, modify the 720-VALID statistical population, alter frozen WP9 evidence, or change historical statistical outputs. The implementation was human-reviewed, regression-validated against preserved reference artifacts, tested for reference-tamper rejection, and identified as an independently reconstructed reproducibility implementation rather than the original analysis code.

### Study 2

After the Study-2 Phase-6 campaign evidence and the prospective Phase-7 analysis implementation were frozen, ChatGPT-assisted workflow support was used to help execute and review the hash-bound analysis process, independently audit/reproduce the generated statistical tables, review claim boundaries, and integrate the frozen results into the journal manuscript. The independent reproduction operated on the immutable 3,872-observation artifact and did not generate or replace observations, alter campaign seeds, change exclusion rules, modify the frozen primary analyzer, or provide input to the experimental response policies.

The frozen Phase-7 result tables were separately recomputed with an independent standard-library auditor, producing zero mismatches across the frozen cell summaries, primary contrasts, secondary contrasts, Holm adjustments/rejection flags, and terminal-state distributions.

## Scientific-mechanism boundary

The Study-1 P7 selector and all Study-2 response policies are **frozen deterministic rule-based mechanisms**. They do not use generative AI or machine learning as a scientific response mechanism. AI assistance belongs only to research/manuscript tooling and is disclosed separately from the experimental treatments.

## Placement implemented

- The manuscript-preparation declaration and two-study research-process disclosure are included in `publication/manuscript/07-declarations-and-availability.md`.
- Study-1 reproducibility-code reconstruction remains described in `publication/manuscript/03-methods.md`.
- Study-2 protocol/analysis/reproduction boundaries are described in `publication/manuscript/03-study2-methods-extension.md` and the canonical Phase-7 provenance/freeze records.
- No AI tool is listed or cited as an author.

## Policy authority checked during preparation

https://www.elsevier.com/about/policies-and-standards/generative-ai-policies-for-journals

The policy snapshot was rechecked in the 2026 submission-preparation cycle. The live policy and portal language remain authoritative at submission time.
