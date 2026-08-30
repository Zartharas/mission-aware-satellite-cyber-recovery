# Contributing

Contributions are welcome when they improve the repository's reproducibility, clarity, testing, defensive research quality, or publication readiness without weakening the study's scientific and safety boundaries.

## Good contribution areas

Examples include:

- documentation corrections and clearer reproduction instructions;
- unit, contract, and regression tests;
- portability fixes that preserve the frozen scientific semantics;
- accessibility and readability improvements to figures/tables;
- non-destructive tooling for validating archived evidence;
- citation/reference metadata corrections;
- security hardening for project isolation and cleanup;
- journal-formatting support that does not change scientific claims.

## Contributions that do not belong here

Do not submit:

- real spacecraft or ground-system credentials;
- proprietary/classified mission telemetry or infrastructure data;
- operational TT&C endpoints or mission schedules;
- live RF interference, jamming, or spoofing procedures;
- unauthorized access instructions for real systems;
- exploit payloads targeting operational spacecraft/ground infrastructure;
- new campaign results presented as if they were part of the frozen 720-observation WP9 population;
- silent rewrites of historical evidence, checksums, run IDs, or publication claims.

Sensitive security concerns should follow [`SECURITY.md`](SECURITY.md), not a public pull request.

## Scientific-integrity rule

The completed study has an evidence-of-record:

- 720 VALID statistical observations;
- 9 ledgered INVALID attempts retained as provenance;
- one quarantined never-ledgered interruption;
- frozen campaign/integrity identities;
- Zenodo v1.0.0 at <https://doi.org/10.5281/zenodo.22181540>.

A contribution may improve code, tests, documentation, or future replication support, but it must not retroactively change what happened in the historical campaign. New experiments are new replications and require their own provenance boundary.

## Development setup

Use the safe repository validation path first:

```bash
git clone https://github.com/Zartharas/mission-aware-satellite-cyber-recovery.git
cd mission-aware-satellite-cyber-recovery

python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt

python scripts/validate_experiment_schema.py
python -m unittest discover -s tests -p 'test_*.py'
```

For Docker/NOS3/Fortytwo setup and bounded runtime preflight, follow [`docs/REPRODUCIBILITY_GUIDE.md`](docs/REPRODUCIBILITY_GUIDE.md).

Do not use the historical WP9 one-position campaign operator as a smoke test.

## Pull-request expectations

A focused pull request should:

1. explain the problem and why the change is needed;
2. list the files/behavior intentionally changed;
3. state whether scientific claims, experiment semantics, frozen evidence, or release artifacts are affected;
4. include or update tests when executable behavior changes;
5. run the applicable local validation before submission;
6. avoid unrelated formatting or generated-file churn;
7. preserve historical paths/hashes unless the change explicitly documents why a new version is required.

For ordinary code/configuration changes, run at least:

```bash
python scripts/validate_experiment_schema.py
python -m unittest discover -s tests -p 'test_*.py'
```

For shell changes, also run `bash -n` against the modified scripts.

## Commit and branch hygiene

- Work on a branch rather than directly on `main`.
- Keep commits reviewable and scoped.
- Do not commit local `external/` clones, simulator build output, credentials, or raw campaign directories that are intentionally ignored.
- Do not force-update historical evidence branches/tags to hide provenance.

## Licensing of contributions

By submitting an original contribution, you agree that it may be distributed under the license applicable to that content class in [`LICENSE`](LICENSE):

- MIT for original software/code and software-like configuration;
- CC BY 4.0 for original research documentation, figures/tables, and author-generated research data.

Do not submit third-party material unless you have verified that redistribution is permitted and the original license/attribution is preserved.

## Citation and attribution

If a contribution relies on external research, standards, or software, cite the authoritative source and avoid implying that third-party projects endorse this work.

For scientific reuse of the published dataset, cite the version-specific DOI: <https://doi.org/10.5281/zenodo.22181540>.
