# WP10 Statistical Reproduction Package

## Status and provenance

This directory is a **post-publication reproduction implementation** of the frozen WP10 statistical analysis. It is **not** the original WP10 analysis source code.

The original WP10 executable analysis source was not preserved in the recovered analysis-output directories. Before this package was written, the private preservation archive was re-verified, the authoritative WP10 output directories were selectively recovered, their output manifests were re-verified, and a source-code search over those recovered directories found zero `.py`, `.R`, `.sh`, or notebook analysis candidates. The reconstruction therefore starts from the frozen analysis inputs and validates its results against the preserved authoritative outputs.

No experiment is run by this package. It does not start NOS3/cFS, read or modify `results/wp9/campaign/`, consume a campaign seed, create a new scientific observation, change the 720-VALID statistical population, or alter Zenodo v1.0.0.

## Frozen inputs

The public reproduction inputs are small derived tables rather than the raw campaign tree:

- `reference/locked-analysis-extraction-720.tsv`
  - 720 VALID observations;
  - SHA-256 `bf219d71162df708343f4be85bb258a083f5012e696c23619d0a46b7a2f2f265`.
- `reference/p4-locked-analysis-240.tsv`
  - the P4 execution-selection/consequence subset containing actual selected action and execution provenance;
  - SHA-256 `f848a448cc75818d37a7827df9e8936ff7a4bf60075ca25b102e858df7f56af3`.

The statistical-membership identity remains:

`a2bf0c8f352f4386e74a500d97ea8f73e0c39d03bfe10ac0ebcf02470af9f70e`

The DOI-bearing raw evidence-of-record remains Zenodo v1.0.0: <https://doi.org/10.5281/zenodo.22181540>.

## What is reproduced

`reproduce_wp10.py` reconstructs and validates the manuscript-facing analysis logic for:

- P1 structural/direct and interaction conclusions on the predeclared primary outcomes;
- P2 M04/M05 RMST contrasts through 30 s with the recovered 20,000-replicate paired seed-block bootstrap;
- P2/P3 exact trusted-recovery counts and Clopper-Pearson intervals;
- M03 structural-zero bounds without manufacturing a count model;
- P2/P3 M07 linear mixed models, seed-block bootstrap, rank sensitivity, quantile sensitivity, and cross-method direction audit;
- P4 actual selected-action/effective-policy switching and downstream consequence contrasts from the locked 240-row P4 table;
- P5 five-dimensional condition-specific Pareto fronts and the 696-observation final-commit complete-block sensitivity.

It never introduces a P1 M07 rescue analysis, P4 correctness oracle, P5 weighted score, global policy rank, p-value layer, or simultaneous Pareto-confidence claim.

## Bootstrap provenance

The original WP10 records preserve the exact C1 and C2 Monte Carlo settings:

- C1 bootstrap seed: `13772462244504663816`;
- C2 bootstrap seed: `7873538898909399172`;
- bootstrap unit: campaign seed;
- replicates: 20,000;
- interval: marginal percentile 95%.

The reconstruction recovers the deterministic Python `random.Random` seed-block resampling behavior and reproduces the preserved C1 and C2 bootstrap endpoints numerically.

The original **P5 bootstrap RNG seed was not preserved** in the authoritative P5 output summary or recovered analysis material. This package therefore does not pretend to replay those Monte Carlo endpoints byte-for-byte. Instead, it:

1. reproduces the exact P5 point estimates and Pareto relations;
2. uses a new deterministic reconstruction-validation seed derived from the frozen input SHA and a documented namespace;
3. confirms that the independent 20,000-replicate paired seed-block bootstrap produces the same marginal dominance/uncertainty classification for every P7-comparator pair;
4. retains the original published P5 confidence intervals as historical reference outputs, not as regenerated values.

This distinction is deliberate and prevents a missing RNG detail from being silently invented.

## Python environment

This statistical reconstruction requires **CPython 3.11.x**. Do not create its virtual environment with a newer default `python3` interpreter. The pinned scientific dependencies predate Python 3.14, and the pre-commit validation deliberately fails closed rather than compiling unsupported source builds. GitHub Actions also validates this reconstruction on Python 3.11.

Recovered historical WP10-C2 execution evidence records:

- NumPy `1.26.4`;
- statsmodels `0.14.0`.

Those two versions are preserved in `requirements.txt`. The SciPy and pandas versions used by the original WP10 scripts were not recovered; this reproduction package pins compatible Python 3.11 versions for a stable executable environment and labels them as reconstruction pins rather than historical identities.

## Run

From the repository root:

```bash
python3.11 -m venv .venv-analysis
source .venv-analysis/bin/activate
python -m pip install --upgrade pip
python -m pip install --only-binary=:all: -r analysis/requirements.txt
python analysis/reproduce_wp10.py --validate
```

A successful validation ends with JSON containing:

```json
{
  "overall": "PASS"
}
```

To write regenerated diagnostic tables and the complete validation record outside the tracked reference tree:

```bash
python analysis/reproduce_wp10.py \
  --validate \
  --output-dir /tmp/mission-aware-wp10-reproduction
```

## Interpretation of PASS

A PASS means the reconstructed procedure reproduces the frozen numerical/statistical contracts covered by the included regression references, including exact C1/C2 seed-block bootstrap values and P5 point/classification results. It does **not** mean that the original WP10 source was recovered, that Zenodo v1.0.0 changed, or that a new experiment was performed.

The preserved WP10 outputs remain the authority for the historical 2026 analysis. This package supplies an executable, independently reconstructed path from the frozen derived inputs to the reported analysis quantities for peer-review reproducibility.
