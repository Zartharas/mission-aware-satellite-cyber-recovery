# Paper 3 CEAS Rejection-to-Research-Requirements Audit

**Audit date:** 2026-09-22  
**Status:** `COMPLETE__NEW_PROSPECTIVE_EVIDENCE_REQUIRED`  
**Rejected submission:** CEAS Space Journal / `6db04a31-8223-4aaf-af02-e4bafe06ef89`  
**Frozen foundation:** Study 7 / `S7-LSO-001`  
**Proposed extension:** `S7E-AERC-001`  
**Execution authorization:** NOT GRANTED BY THIS AUDIT

## 1. Purpose

This audit converts the CEAS handling-editor decision into explicit, testable research requirements. It does not revise the rejected manuscript and does not alter any frozen Study-7 evidence.

Authoritative Study-7 sources used:

- `study7/STUDY7_PROTOCOL.json`
- `study7/results/RESULTS_FREEZE.json`
- rejected Paper-3 manuscript package under `publication/Paper_3_Study_7/CEAS_Space_Journal/PORTAL_UPLOAD_PACKAGE/`
- historical full manuscript source `publication/Paper_3_Study_7/Journal_of_Aerospace_Information_Systems/PAPER3_TECHNICAL_NOTE_DRAFT_R3_FULL.md`

## 2. Handling-editor requirements

The handling editor stated that the manuscript addresses a relevant assurance concern and has a transparent, reproducible setup, but identified four deficiencies that limit scientific contribution and application-specific insight.

| Editor concern | Repository evidence | Audit finding | Can prose alone fix it? | Required response |
|---|---|---|---|---|
| Central finding follows directly from the problem formulation | Block C deliberately holds the eight visible inputs constant while changing research-only authorization truth | **Supported / high severity.** The indistinguishability result is exact, but the visible-only failure is structurally expected once decisive truth is excluded from the input | No | Add architecture-generated scenarios and endpoints whose outcomes are not merely a direct restatement of hidden-variable indistinguishability |
| No concrete spacecraft recovery architecture | S7 uses abstract binary policy-visible features and no flight-software component/message/authority topology | **Supported / high severity** | No | Implement a concrete reference spacecraft recovery architecture and bind each observable to a component, message path, authority, and recovery action |
| Trust assumptions not validated | `independent_corroboration` is a stipulated binary feature; the rejected manuscript explicitly says operational independence is an assumption | **Supported / high severity** | No | Replace the independence bit as an assumption with explicit trust-domain topology and fault/compromise injection across source, key, execution, transport, and authority domains |
| Missing deterministic policy with the same corroborating information | `D0_S1_VISIBLE_ONLY` and `L0_ERM_VISIBLE_ONLY` share eight inputs, but only `L1_ERM_WITH_INDEPENDENT_CORROBORATION` receives the ninth corroboration input | **Supported / high severity** | No | Add an equal-information deterministic corroboration-aware comparator and evaluate it against the learned selector on exactly the same observable state |

## 3. What remains scientifically valid

The CEAS rejection does **not** invalidate the following frozen Study-7 facts:

- exact modeled population = 1,033 observations;
- Block A = 512 observations;
- Block B = 512 observations;
- Block C = 9 observations;
- L0 training errors = 0;
- L1 training errors = 0;
- visible-only lattice errors = 0;
- corroboration lattice errors = 2;
- independent-disagreement unsafe proceed: D0 = 1, L0 = 1, L1 = 0;
- correlated-false-corroboration unsafe proceed: D0 = 1, L0 = 1, L1 = 1;
- independent repository audit = PASS.

These claims remain exact for the frozen model. They must not be reinterpreted as operational spacecraft performance, general ML superiority, or empirically validated corroboration independence.

## 4. Why a manuscript-only retarget is not sufficient

A manuscript-only retarget could improve explanation, diagrams, literature placement, and venue formatting. It cannot honestly create:

- a concrete implemented spacecraft recovery architecture;
- validated trust-domain separation;
- a deterministic corroboration-aware comparator receiving the same information as the learned comparator; or
- new architecture-level safety/recovery observations.

Therefore the minimum defensible recovery path requires a separate prospective extension study.

## 5. New scientific requirement

The new study must separate **information availability**, **policy class**, and **trust architecture**.

At minimum, the experiment must contain equal-information pairs:

| Information set | Deterministic policy | Learned policy |
|---|---|---|
| Base recovery evidence | yes | yes |
| Base evidence + corroboration | yes | yes |

This resolves the principal comparator asymmetry in Study 7. Any performance difference between deterministic and learned policies must then be attributable to policy behavior under identical observables, not to one policy receiving extra information.

## 6. Architecture-grounding requirement

A strong implementation path is a NASA core Flight System (cFS)-grounded reference architecture.

NASA describes cFS as a platform-independent, component-based flight-software framework built around the core Flight Executive and a publish/subscribe Software Bus. NASA also provides Health and Safety, command-ingest, telemetry, and Software Bus Network components. NOS3 provides a spacecraft software development, integration/test, V&V, ground-station, dynamics/environment, and hardware-model simulation environment.

Useful official references reviewed 2026-09-22:

- NASA cFS: https://etd.gsfc.nasa.gov/capabilities/core-flight-system
- NASA cFS software catalog: https://software.nasa.gov/software/GSC-18719-1
- NASA cFE: https://software.nasa.gov/software/GSC-16232-1
- NASA Software Bus Network: https://software.nasa.gov/software/GSC-16917-1
- NASA small-spacecraft design tools / NOS3: https://www.nasa.gov/smallsat-institute/space-mission-design-tools/

The extension should use these only as an open reference architecture/test environment. It must not claim NASA endorsement, flight qualification, or operational mission validation.

## 7. Trust-validation requirement

The new study should replace the single stipulated independence bit with explicit trust domains, for example:

1. evidence-source provenance domain;
2. cryptographic/key authority domain;
3. execution/process or processor domain;
4. message-transport domain;
5. ground/mission-authorization domain.

Corroboration independence must be derived from the architecture and tested by controlled compromise/fault injection. At least these topology classes should be evaluated:

- shared-domain corroboration;
- source/key-separated corroboration;
- process/processor-separated corroboration;
- common-cause compromise that defeats both paths.

The study must state precisely what "independent" means in the implemented architecture. Sharing a common Software Bus or authority must not be silently described as full independence.

## 8. Non-tautological outcome requirement

The extension should not merely recreate a hidden bit that no policy can observe. Architecture-level component failures/compromises should generate the observables seen by the policies.

Primary endpoints should include:

- unsafe recovery authorization / unsafe proceed;
- false-conservative hold;
- objective decision error;
- deterministic-versus-learned decision disagreement under identical information;
- change in safety outcome attributable to trust-domain separation;
- collapse of corroboration benefit under common-cause compromise.

The experiment should use a prospectively frozen finite scenario matrix or a separately justified stochastic design. If a finite matrix is used, report exact finite-population counts rather than operational probabilities.

## 9. Paper-3 scientific architecture after recovery

A rebuilt Paper 3 may use:

- **Study 7 / S7-LSO-001** as the frozen information-sufficiency foundation; and
- **Study 7E / S7E-AERC-001** as a separately designed architecture-grounded extension.

The two studies must remain separate populations. No pooled sample size, pooled error rate, or retroactive protocol change is permitted.

## 10. Conditional live venue fit after strengthening

No venue is locked by this audit. The following venues become scientifically plausible **only if** the new architecture-grounded extension is completed successfully.

### AIAA Journal of Aerospace Information Systems — strong conditional fit

AIAA states that JAIS publishes original work on aerospace computing, information, networks and communication systems, including aerospace systems/software engineering, V&V of embedded systems, machine learning, systems health management, autonomous systems, systems engineering, and safety/mission assurance.

Official scope: https://aiaa.org/publications/journals/journal-scopes-and-content/

**Condition:** the rebuilt paper must clearly exceed the rejected abstract information example and demonstrate architecture-specific aerospace insight. Existing Paper-1 activity at JAIS creates portfolio/overlap-management considerations that must be checked before any venue lock.

### IEEE Transactions on Aerospace and Electronic Systems — strong scientific fit, high bar

TAES covers organization, design, development, integration, and operation of complex space/aerospace systems. Its technical-area descriptions explicitly include cyber-physical security of space systems and AI in avionics.

Official sources:
- https://ieee-aess.org/publications/taes
- https://ieee-aess.org/publications/transactions-aes/technical-areas-editors/descriptions

**Condition:** substantial architecture-level novelty and systems evidence are required. Paper 2 is already active at TAES, so self-overlap and portfolio concentration must be reviewed before considering this venue.

### IEEE Open Journal of Systems Engineering — strong if framed as systems-engineering method

OJSE focuses on systems-engineering science, methods, V&V, integration/test, requirements and life-cycle support for complex systems.

Official scope: https://ieee-aess.org/publication/ieee-open-journal-system-engineering

**Condition:** the paper should emphasize a reusable trust-domain/equal-information assurance methodology rather than only an application result. It is fully open access and requires an APC after acceptance.

### ACM Transactions on Cyber-Physical Systems — conditional fit

ACM TCPS publishes high-quality work on interactions among information processing, networking, and physical processes, including avionics.

Current call/scope reference reviewed: https://tcps.acm.org/

**Condition:** the extension must include meaningful cyber-physical interaction or recovery effects through a realistic simulation/testbed. A software-only selector comparison would likely remain too narrow.

### Reliability Engineering & System Safety — conditional/high-bar fit

RESS explicitly includes space systems, software reliability, operator decision support, fault detection/diagnosis, and methods for safety/reliability of complex technological systems.

Official description: https://shop.elsevier.com/journals/reliability-engineering-and-system-safety/0951-8320

**Condition:** the extension must become a substantive safety/reliability analysis of a real or realistically modeled architecture, not simply a cyber decision-policy comparison.

## 11. Audit decision

**Decision:** `NEW_PROSPECTIVE_EXTENSION_REQUIRED`

**Proposed experiment:** `S7E-AERC-001`

**Do not:**

- alter `S7-LSO-001`;
- rerun Study 7 to obtain a different result;
- add a deterministic comparator retroactively to the frozen Study-7 population;
- claim that the CEAS rejection invalidates Study 7;
- create operational spacecraft or certification claims;
- select a new journal before extension evidence exists.

## 12. Next gate

Prepare and author-review the prospective `S7E-AERC-001` protocol and implementation plan. Do not execute the new study until its research questions, architecture, trust domains, comparator semantics, scenario population, endpoints, validation tests, audit method, and claim boundaries are prospectively frozen.
