## Summary

Describe the change and why it is needed.

## Scope

List the files/components intentionally changed.

## Scientific / evidence impact

Select or explain the applicable statement:

- [ ] No scientific claim, frozen experiment semantic, campaign evidence, or published archive file is changed.
- [ ] The change affects future replication/tooling only and does not rewrite the historical WP9 evidence-of-record.
- [ ] The change intentionally affects publication text/metadata; the claim/evidence impact is described below.
- [ ] The change would require a new archive/release version; rationale is described below.

Impact notes:

## Validation

- [ ] `python scripts/validate_experiment_schema.py`
- [ ] `python -m unittest discover -s tests -p 'test_*.py'`
- [ ] Applicable modified shell scripts pass `bash -n`
- [ ] Documentation links/figures checked if documentation changed
- [ ] No secrets, operational credentials, proprietary telemetry, or sensitive target data added

## Reproducibility / safety boundary

Confirm that the change preserves the controlled software-in-the-loop boundary and does not introduce operational spacecraft/RF testing instructions unless that material is purely defensive, authorized, and separately reviewed.

## Related issue / evidence

Link relevant issue, document, DOI, or evidence record if applicable.
