# WP10-G6 Target-Neutral Full Manuscript Assembly

**Date:** 2026-08-29  
**Status:** Full target-neutral manuscript component set assembled  
**Upstream scientific audit:** `docs/35-wp10-g5-manuscript-evidence-audit.md` — PASS  
**Target journal:** intentionally not required for this stage

## Scope

G6 assembles the manuscript components that can be completed without author/submission metadata or journal-specific formatting. It does not create new analysis or change any frozen scientific finding.

## Manuscript component set

- `publication/manuscript/00-title-abstract.md`
- `publication/manuscript/01-introduction.md`
- `publication/manuscript/02-background-and-related-work.md`
- `publication/manuscript/03-methods.md`
- `publication/manuscript/04-results.md`
- `publication/manuscript/05-discussion.md`
- `publication/manuscript/06-conclusion.md`
- `publication/manuscript/07-declarations-and-availability.md`
- `publication/manuscript/MANUSCRIPT-ASSEMBLY.md`

Results and Discussion are the G4 evidence-locked drafts and were not replaced with stronger prose during G6.

## Bibliography work

`references/references.bib` was expanded with verified/current references required by the assembled Background/Discussion, including:

- NIST SP 800-160 Vol. 2 Rev. 1;
- SPARTA Cyber-safe Mode;
- AWS satellite incident-response practice context;
- Temporal Risk on Satellites;
- TinyML autonomous-spacecraft cyber detection;
- What is Cybersecurity in Space?;
- The JUICE Spacecraft System Design;
- AegisSat;
- HADES;
- cyber-physical attack-recovery survey context.

`publication/manuscript/citation-readiness.csv` records remaining target-style normalization tasks. Metadata was not invented where the repository/source review did not provide a complete author/issue record; such cases remain explicit final-reference tasks.

## Assembly decisions

### Modular source of truth

The manuscript remains a component set rather than a second manually copied monolithic Markdown file. This avoids divergence between duplicate Results/Discussion copies. A target-journal export should concatenate/transform these components after G7 pre-submission review.

### Abstract discipline

The abstract includes the P1 null, P2 contact timing, P3 evidence-dependent recovery result, P5 conditionality, provenance sensitivity, and the controlled software-in-the-loop boundary. It does not present P7 as universally superior.

### Methods discipline

The Methods section follows the actual final analysis behavior rather than the early initial plan. Structural-zero/degenerate outcomes are described with exact counts/contrasts rather than implying that mixed models were successfully fit where they were not. P5 is described with its five frozen dimensions, 20,000 paired seed-block bootstrap replicates, marginal percentile intervals, and no weighted/global rank.

### Data availability discipline

The manuscript does not claim that the complete raw campaign is currently public. It records the frozen SHA-256 identities and says the DOI-bearing Zenodo release is pending WP11. The statement must be updated after archive verification.

## Scientific-boundary check

G6 preserves:

- P1 as unsupported on predeclared primary outcomes;
- modeled/synthetic contact semantics;
- A16/A17 as P6;
- M05 right-censoring;
- P3 narrower anticipated mechanism as absent;
- P4 selection/consequence without an objective correctness oracle;
- experimental safe-mode wording;
- M03 structural zero without universal safety inference;
- P5 conditionality and no weighted/global ranking;
- 1/9/710 execution provenance and 29-seed sensitivity;
- controlled NOS3/Fortytwo SIL, no RF/operational/human claims.

## Items not yet fillable without external decision/input

The following are intentionally left as submission placeholders rather than guessed:

- author list and affiliations;
- corresponding-author information;
- funding declaration;
- competing-interest declaration;
- acknowledgments;
- selected journal/article type and formatting limits;
- target-journal generative-AI disclosure language;
- final Zenodo DOI(s).

These do not block a target-neutral pre-submission manuscript audit.

## G6 disposition

**G6 manuscript assembly: COMPLETE.**

Next phase: **WP10-G7 — target-neutral pre-submission quality audit**, including section coherence, claim consistency, citation coverage, reference-key hygiene, display callouts, abstract-to-results consistency, and unresolved-submission-input register. No new statistical analysis is authorized or required.