# S6X-EAP-001 cFS Environment Screening R1

**Status:** `ENVIRONMENT_SCREENING_COMPLETE__IMPLEMENTATION_NOT_AUTHORIZED`  
**Screening date:** 2026-09-26  
**Scientific execution:** none

## cFS suitability

NASA's open-source cFS bundle is a reusable flight-software framework with a Linux development/test configuration. The official repository explicitly states that the open bundle is a demo/development bundle and is not itself a flight distribution. This boundary is useful for S6X because the proposed work is a researcher-controlled software-assurance experiment, not flight qualification.

The official cFS build system supports:
- a native Linux development configuration;
- unit-test execution through the documented `runtest` goal;
- isolated build directories for different configurations.

## Version candidate

The NASA cFS release list shows `v7.0.1` as a non-prerelease open-source release published in May 2026.

The repository README also discusses a later `v7.0.2rc1` release candidate.

Recommended prospective freeze candidate: **cFS v7.0.1**, not the release candidate, unless a later pre-freeze review identifies a specific reason to use a different version.

No source revision is frozen yet.

## Candidate application substrate

### Preferred: Limit Checker (LC)

NASA describes LC as monitoring telemetry values, comparing them with threshold limits, issuing events, and optionally initiating a command script when threshold conditions occur.

Why it is attractive:
- spacecraft/vehicle-management relevance is concrete;
- behavior admits prospectively defined functional invariants;
- the official repository contains a `unit-test/` tree;
- an approved-but-semantically-wrong source fixture can be benign, e.g. an intentionally altered threshold/comparison behavior that is caught only by an external functional adjudicator.

Risk:
- S6X must avoid turning into a new fault-management or control-policy study. The artifact-assurance question remains primary.

### Secondary: Stored Command (SC)

SC autonomously releases absolute- and relative-time command sequences.

Why it is attractive:
- direct onboard/autonomy relevance;
- deterministic command-release behavior supports functional tests.

Risk:
- more complex timing/configuration semantics than needed for the core observability result.

### Fallback only: sample_app

The cFS sample application is easy to build and test but NASA explicitly describes it as a non-flight example with minimal functionality and limited testing. It is therefore weaker for addressing the prior aerospace-relevance criticism.

## Recommended S6X direction

Use **cFS v7.0.1 + Limit Checker** as the primary design candidate, subject to a dedicated invariant review.

The independent objective-correctness adjudication should test a documented LC functional property and remain completely outside the assurance gate.

Example structure:

`pinned source -> build -> artifact -> hashes/provenance/rebuild/review/approval -> gate decision`

separately from:

`artifact -> independent functional invariant -> research-only correctness adjudication`.

The experiment should never claim that passing the S6X test establishes mission readiness, flightworthiness, NASA certification, or cFS-wide security.

## Current decision

`CONDITIONAL_GO_FOR_INVARIANT_AND_FIXTURE_DESIGN_AFTER_AUTHOR_APPROVAL`

No cFS checkout, build, artifact mutation, signing, or experiment execution is authorized by this record.
