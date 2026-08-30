# Scripts Guide

This directory contains both current reproducibility entry points and historical experiment tooling retained for provenance. The presence of a script does not mean it should be run as a casual smoke test.

## Recommended entry points for readers

Use these first when validating or reconstructing the published environment:

| Script | Purpose |
|---|---|
| `verify_environment.sh` | Report the local host/tool prerequisites used by the project. |
| `validate_experiment_schema.py` | Validate the experiment schema and committed fixtures. |
| `prepare_nos3_candidate.sh` | Obtain the pinned NOS3 source tree into the ignored `external/` directory and record the source lock. |
| `prepare_42_candidate.sh` | Obtain/build the pinned Fortytwo/42 dependency under the frozen container environment. |
| `build_nominal_nos3.sh` | Build the pinned nominal NOS3 environment with network-disabled container execution. |
| `run_nominal_runtime_preflight.sh` | Run the bounded, non-campaign nominal runtime preflight used to validate component liveness and isolation. |
| `cleanup_nominal_runtime.sh` | Remove project-labeled runtime containers/networks after a bounded preflight. |
| `verify_nos3_source_lock.sh` | Verify the pinned NOS3 source identity. |
| `verify_testbed_runtime.sh` | Verify the retained testbed/runtime evidence contract. |

The end-to-end setup order, expected PASS markers, platform notes, and safety boundaries are documented in [`../docs/REPRODUCIBILITY_GUIDE.md`](../docs/REPRODUCIBILITY_GUIDE.md).

## Release tooling

The following scripts are retained because they generated and audited the publication candidate that became Zenodo v1.0.0:

- `prepare_wp11_release_candidate.py`
- `audit_wp11_release_candidate.py`

They are useful when creating a deliberately new archive version. They are not needed merely to download or verify the already-published Zenodo v1.0.0 record.

## Historical scientific/runtime tooling

Scripts beginning with the following prefixes are retained as part of the research provenance and implementation record:

- `run_wp5_`
- `run_wp6_`
- `run_wp7_`
- `run_wp8_`
- `run_wp9_`
- `run_wp9b2_`

These files document and implement the mechanisms that were developed, validated, piloted, or used to produce the frozen study. They are intentionally retained even though the published campaign is complete.

Do **not** use the historical WP9 campaign operator as a generic test command. A new execution is not a member of the published 720-observation population and must be treated as a separate replication with its own provenance.

`nos3_runtime_material.py` is retained as historical runtime support material used by the experiment tooling and should not be removed merely because it is not a user-facing entry point.

## Removed obsolete helpers

The post-publication repository cleanup removed four files from the active branch because they were obsolete/orphaned and not part of the current reproducibility path:

- `bootstrap_macos.sh` — contained an old researcher-specific local path/repository bootstrap workflow superseded by the public clone/setup instructions.
- `benign_plaintext_transport_relay.py` — WP4 benign diagnostic helper from the discontinued transport-observability branch.
- `prepare_runtime_radio_config.py` — WP4 runtime-radio diagnostic helper from the discontinued branch.
- `verify_benign_ground_probe.sh` — orphaned verifier that referenced `scripts/benign_ground_probe.py`, which is not present in the publication baseline.

The exact pre-cleanup repository state remains recoverable from Git history and the backup branch `archive/pre-journal-cleanup-eab939b` at commit `eab939b1ff440899853a04d80e31a6abf011c6ea`.

## Safety and scientific-integrity boundary

This repository supports controlled software-in-the-loop defensive research. Do not adapt the scripts for unauthorized access to operational spacecraft, ground systems, production credentials, proprietary telemetry, or live RF interference. See [`../SECURITY.md`](../SECURITY.md) and [`../docs/13-laboratory-rules-of-engagement.md`](../docs/13-laboratory-rules-of-engagement.md).
