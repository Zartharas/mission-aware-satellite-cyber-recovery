# Studies 3–8 Assurance Coverage Audit

**Audit date:** 2026-09-03  
**Scope:** repository assurance structure only; no scientific re-execution and no frozen-result modification.

## Question

Repository Review v3 correctly observed that Studies 3–7 each use one relatively small unit-test module. Line count alone, however, is not a sufficient measure of assurance for these deterministic finite-population studies. This audit therefore evaluates the layered assurance actually used:

1. targeted unit invariants;
2. exhaustive finite-population construction/evaluation where applicable;
3. independently written evidence/result reproduction or audit;
4. canonical workflow integrity/hash checks;
5. frozen result identities and interpretation guards;
6. repository-wide regression/no-drift validation.

No new test is added unless this layered review identifies a concrete uncovered invariant or boundary condition.

## Summary matrix

| Study | Targeted unit tests | Exhaustive / exact population check | Independent reproduction/audit | Hash/freeze gate | Audit disposition |
|---|---:|---|---|---|---|
| Study 3 | 9 test methods in `test_temporal_model.py` | exact 30 cells, 46 onset phases, 1,380 trajectories; canonical 67,620 epoch rows | `RESULTS_FREEZE.json`: PASS with 0 trajectory, epoch-rule, qualification-origin, and SHA mismatches | canonical artifact and three output SHA-256 identities frozen | **adequate for current frozen claim boundary; no extra test justified** |
| Study 4 | 6 test methods in `test_quorum_model.py` | exact 18 rules × 2 blocks × 128 subsets = 4,608 observations | accepted run `33658900540`: `study4_independent_audit=PASS`, observation mismatches = 0, threshold mismatches = 0 | canonical artifact + four output SHA-256 identities frozen | **adequate for current finite combinatorial claim boundary; no extra test justified** |
| Study 5 | 6 test methods in `test_bridge_model.py` | exact 80 label × context × policy decisions; explicit 8-row input sufficiency and 5-row transferability structures | canonical validation records independent audit mismatches = 0 | dedicated and repository validation PASS; selector dependency SHA frozen | **adequate for portability/input-sufficiency claim boundary; no extra test justified** |
| Study 6 | 8 test methods in `test_artifact_trust_model.py` | exact 36 adversarial + 384 benign-unavailability = 420 observations | `independent_audit = PASS` | canonical artifact + four output SHA-256 identities frozen | **adequate for finite Boolean artifact-trust model; no extra test justified** |
| Study 7 | 7 test methods in `test_learned_selector_model.py` | exact 512 + 512 + 9 = 1,033 observations | `independent_audit = PASS` | canonical artifact + four output SHA-256 identities frozen | **adequate for the frozen transparent linear-threshold learner; no extra test justified** |
| Study 8 | 6 implementation test methods in `test_phase8_models.py` | exact 3,456-factor population plus development fixture parity | separately written implementation-level reproduction of all 3,456 rows; 3,456 exact matches / 0 mismatches | Phase-8.6 findings hash freeze + technical-close + 11-file publication freeze | **strong layered assurance; no extra test justified** |

## Study 3

`study3/tests/test_temporal_model.py` checks more than population size. It verifies:

- exact cells, onset phases, and trajectory count;
- truthful V0 false qualification can only arise from the pre-onset-cache boundary;
- affected V4 records cannot qualify;
- every false qualification has one of the declared origins;
- persistent V5 produces exposure for gate-entering policies;
- one-shot treatment affects exactly one received post-onset record;
- no false qualification/permissive event occurs before onset;
- K4 contact never appears outside the frozen windows;
- B2 remains protective after a security signal when evidence is qualified.

The canonical freeze adds full-population result auditing with zero recorded mismatches. This is stronger evidence than raw test-file line count suggests.

## Study 4

`study4/tests/test_quorum_model.py` checks:

- exact 4,608-observation population;
- exact 18-rule set;
- zero-compromise safety;
- zero-loss availability;
- provenance diversity blocking a same-domain pair;
- absolute quorum fail-closed behavior under unavailability.

The accepted canonical workflow separately executes `study4/analysis/audit_independent.py`. Run `33658900540` recorded:

- `study4_independent_audit=PASS`;
- `study4_observation_mismatches=0`;
- `study4_threshold_mismatches=0`.

The same run also verified the frozen output hashes and completed with no tracked-file drift. Because the finite population already enumerates all 128 affected-producer subsets for all rules and both blocks, adding numerous example-based unit cases would add limited assurance unless a specific invariant is found missing.

## Study 5

`study5/tests/test_bridge_model.py` checks:

- SHA binding to the frozen Study-2 selector dependency;
- exact 80-row portability population and uniqueness;
- exact external label schema;
- 0/8 direct recovery-input availability and permitted offline-label-oracle treatment;
- attack-subtype action invariance across 16 controlled context-policy groups;
- prohibition on falsely calling non-normal CuCD-ID mappings `DIRECT`.

The result freeze records zero independent-audit mismatches. These tests map directly to Study 5's narrow portability and anti-fabrication claim boundary.

## Study 6

`study6/tests/test_artifact_trust_model.py` checks:

- exact 36 + 384 finite population;
- clean-approved qualification across all gates;
- signature-only handling of tamper versus validly signed bad states;
- reproduced-build and source-review trust boundaries;
- the composite gate still accepting an objectively wrong but fully approved source;
- objective correctness never entering the gate signal set;
- one row per benign-unavailability subset × gate.

The result freeze separately records `independent_audit = PASS`.

## Study 7

`study7/tests/test_learned_selector_model.py` checks:

- deterministic learned weights/thresholds and zero training errors;
- exact 1,033-row population and all three block sizes;
- exact visible-lattice generalization;
- the two-error corroboration-lattice boundary cost;
- inability of visible-only policies to resolve the V5 hidden-truth collision;
- independent corroboration resolving only the independent-disagreement case, not correlated false corroboration;
- hidden truth not being supplied in the policy feature vector.

The result freeze separately records `independent_audit = PASS`.

## Study 8

The Study-8 implementation tests intentionally avoid rerunning the canonical campaign. They check factor-population uniqueness, equal total-cycle contact capacity, primary/independent fixture parity, prohibited direct execution entrypoints, the explicit hybrid-overlap endpoint, and structural-zero safety outputs in fixtures.

Full assurance is provided at the evidence layer by the separately written implementation-level reproduction of all 3,456 frozen cases, exact row identity, Phase-8.6 result hashes, technical-close checks, and publication-package freeze.

## Findings

### No confirmed assurance gap requiring new tests

The reviewer’s observation that each later study has one small test module is factually useful, but conventional file/line-count comparison with Study 1 is not an appropriate assurance metric by itself. The later studies have smaller deterministic implementations and rely heavily on complete finite enumeration plus independent evidence/result auditing.

This audit found **no concrete frozen claim whose required invariant is currently unsupported solely because of missing unit tests**.

### Improvements that are worthwhile without changing science

- Maintain a current status/index surface for each study so unit tests, population size, independent audit, freeze identity, and publication disposition are discoverable.
- Preserve independent auditor implementations separately from primary analyzers.
- Keep canonical workflows fail-closed on exact population/hash identities and no-drift checks.
- For future studies, add a prospective assurance matrix to the design freeze so each claim-critical invariant maps to at least one test, exhaustive check, independent audit, or formal property.

### What not to do

- Do not add tests merely to increase file count or line count.
- Do not rerun frozen canonical campaigns just to improve a coverage metric.
- Do not refactor frozen implementations in place to share test infrastructure.
- Do not interpret successful finite-model tests as operational spacecraft validation.

## Disposition

`ASSURANCE_COVERAGE_REVIEW_PASS_NO_ADDITIONAL_TESTS_REQUIRED_FOR_CURRENT_FROZEN_CLAIMS`

A new test should be added only if a later manuscript/adversarial review identifies a specific claim-critical boundary not already exercised by the layered assurance above.
