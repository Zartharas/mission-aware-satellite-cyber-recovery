# Post-Publication WP10 Reproducibility Hardening Record

**Date:** 2026-08-30
**Status:** post-publication statistical reproduction package prepared for pre-journal review
**Scientific work-package state:** WP0–WP11 remain closed; this record does not create WP12
**Zenodo evidence-of-record:** v1.0.0 — <https://doi.org/10.5281/zenodo.22181540>

## Purpose

A post-publication repository review identified a reproducibility gap: the frozen WP10 statistical outputs, methods, and cryptographic identities were preserved, but the executable source that originally generated the local WP10 analysis outputs was not tracked in GitHub or included in Zenodo v1.0.0.

This hardening pass closes that gap without reopening the experiment or rewriting the historical analysis record. It adds an independently reconstructed statistical implementation that starts from the frozen derived analysis inputs and is regression-tested against the preserved authoritative WP10 outputs.

## Recovery finding

Before reconstruction, the private preservation package was re-verified and the authoritative WP10 output directories were selectively recovered. The recovered output manifests passed their original SHA-256 checks. The locked 720-row extraction retained SHA-256:

`bf219d71162df708343f4be85bb258a083f5012e696c23619d0a46b7a2f2f265`

The locked P4 240-row analysis table retained SHA-256:

`f848a448cc75818d37a7827df9e8936ff7a4bf60075ca25b102e858df7f56af3`

A source-code search over the recovered WP10 analysis directories found zero Python, R, shell, or notebook analysis-source candidates. Therefore the public implementation added after publication is explicitly classified as a **post-publication reconstruction**, not recovered original WP10 source.

## Pre-commit environment correction

During local pre-commit validation, the host's unqualified `python3` resolved to CPython 3.14. The reconstruction dependency pins target Python 3.11, so pip had no compatible SciPy 1.11.4 wheel and attempted an unsupported source build that stopped during package metadata/build preparation. No statistical reconstruction, experiment runtime, campaign-seed consumption, or scientific-evidence mutation occurred before that failure.

The setup was therefore hardened before commit to require CPython 3.11.x explicitly and to install the pinned statistical dependencies from binary wheels. GitHub Actions uses the same Python 3.11 interpreter line.

## Pre-commit Python 3.11 parser correction

After the Python 3.11 environment was established, the first reconstruction invocation stopped during source parsing before statistical execution. Two validation-only f-strings used quote-reuse syntax accepted by Python 3.12 and later but not by Python 3.11. The expressions were changed to equivalent Python-3.11-compatible quoting and the complete reconstruction source was then syntax-checked with CPython 3.11 before analysis resumed.

This parser failure occurred before any statistical reconstruction, experiment runtime, campaign-seed consumption, scientific-evidence mutation, staging, commit, or push.

## Source-faithful reference-file whitespace

Selected historical WP10 reference TSV files are retained byte-for-byte so their recovered SHA-256 identities remain independently verifiable. The preserved P4 locked-analysis reference contains trailing whitespace in some rows originating in the authoritative recovered artifact. That whitespace is intentionally retained rather than normalized because normalization would change the reference-file identity.

Whitespace hygiene is enforced strictly on executable code, workflows, manuscript text, documentation, and other non-reference files. Files under `analysis/reference/` are instead governed by their SHA-256 manifest and byte-exact provenance contract.

## Reconstruction validation

The reconstruction preserves the frozen 720-VALID analysis population, 24 cells, 30 campaign seeds, M05 event/censor binding, and all proposition boundaries. It does not read or mutate the raw WP9 campaign during normal execution.

Regression validation against the preserved WP10 references includes:

- P1 predeclared-primary null/structural results;
- P2 M04/M05 RMST point estimates and exact reconstructed seed-block percentile intervals;
- P2/P3 exact trusted-recovery counts and intervals;
- P3 verification-discordance result;
- P2/P3 M07 mixed-model estimates;
- exact C2 raw seed-block bootstrap intervals;
- exact C2 rank and quantile sensitivity values/intervals;
- C2 cross-method direction classifications;
- P4 actual-selection distributions and evidence-driven selection switching;
- P4 downstream blocked consequence contrasts;
- P5 cell primary estimates and point-estimate Pareto fronts;
- P5 pairwise point-estimate relations;
- P5 final-commit 29-seed / 696-observation sensitivity.

The reconstructed validation reports PASS against those retained reference contracts.

## Bootstrap provenance and one retained limitation

The recovered records preserve the C1 and C2 bootstrap settings, including 20,000 paired campaign-seed replicates and their RNG seeds. The reconstruction therefore reproduces the retained C1 and C2 Monte Carlo interval endpoints numerically.

The original P5 bootstrap RNG seed was not preserved. No seed is invented and described as historical. Instead, the reconstruction uses a deterministic new validation seed derived from the frozen input SHA and a documented namespace. The independent bootstrap reproduces the same marginal P7/comparator dominance-versus-uncertainty classification for every pair. The original P5 interval endpoints remain historical reference values; the reconstruction does not claim byte-for-byte Monte Carlo replay for those endpoints.

## Scientific boundary

This hardening pass does not:

- run a new campaign observation;
- consume a campaign seed;
- change the 720 VALID statistical population;
- change the nine retained INVALID attempts;
- modify `results/wp9/campaign/`;
- relabel A16/A17 from P6 to P5;
- introduce M07 as a P1 rescue endpoint;
- manufacture a P4 correctness oracle;
- create a weighted P5 score or global policy rank;
- make a simultaneous 95% Pareto-dominance claim;
- change the 696-observation sensitivity into the primary population;
- change Zenodo v1.0.0.

## Publication relationship

Zenodo v1.0.0 remains the immutable DOI-bearing evidence-of-record for the completed study phase. The post-publication reconstruction is repository software added later for peer-review reproducibility. If it is later archived with a DOI, it must be deposited as a new Zenodo version or a separate software record rather than silently changing v1.0.0.
