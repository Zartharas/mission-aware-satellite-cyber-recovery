# S7E-AERC-001 Candidate Environment Baseline

**Date:** 2026-09-22  
**State:** `CANDIDATE_ONLY__NOT_PINNED__FEASIBILITY_NOT_EXECUTED`

This record identifies current upstream release candidates for the prospective Study-7E implementation. It does not authorize installation, build, execution, or scientific data generation.

## cFS candidate

- Upstream: `nasa/cFS`
- Candidate release: `v7.0.1`
- Release name: cFS Bundle - v7.0.1
- Published: 2026-05-14
- Release status: official, non-prerelease
- License stated by upstream release: Apache 2.0 for the cFS framework bundle
- Includes cFE/OSAL 7.0.1 according to upstream release documentation

Candidate rationale:

- current official release at design time;
- stable tag preferable to a floating branch;
- compatible release family across cFS components.

Before protocol freeze, resolve and record:

- exact cFS tag object/commit;
- every submodule commit;
- exact HS and SBN release/commit;
- compiler and CMake versions;
- PSP/OSAL configuration.

## NOS3 candidate

- Upstream: `nasa/nos3`
- Candidate release: `v1_07_05` / Release 1.7.5
- Published: 2026-06-30
- Release status: non-prerelease
- License: NASA Open Source Agreement 1.3

Release notes relevant to the proposed study include:

- SBN command/telemetry work;
- multiple GDS support;
- updated 42 integration with RF communications capability;
- RF inview and delay support.

These release-note items do not make RF behavior an endpoint of Study 7E. They only support feasibility of a contemporary NOS3 integration baseline.

Before protocol freeze, resolve and record:

- exact NOS3 tag commit;
- all recursive submodule commits;
- VM/container/base-image identity;
- selected ground system and version;
- whether the release can be reproduced without unpinned network fetches.

## Selection rule

The canonical environment will use these candidate releases only if a separate local feasibility qualification demonstrates:

1. deterministic build from pinned revisions;
2. required cFS custom-app integration;
3. HS access;
4. SBN two-instance communication;
5. deterministic scenario control and telemetry capture;
6. acceptable license/provenance handling;
7. no uncontrolled network dependency during canonical execution.

If NOS3 fails this gate, the fallback is a pinned cFS-only multi-instance research simulation, subject to author approval before protocol freeze.

No scientific execution is authorized by this record.
