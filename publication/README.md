# Publication Package

This directory is the human-facing publication layer for the **journal article**. The active manuscript reports **two separately frozen empirical studies**. Historical Study-1 publication artifacts retain stable paths for provenance, while Study 2 is integrated without pooling or rewriting the Study-1 population.

## 1. Authoritative manuscript order

Read the target-neutral journal manuscript components in this sequence:

1. [`manuscript/00-title-abstract.md`](manuscript/00-title-abstract.md) — combined title, abstract, keywords, running-title candidate
2. [`manuscript/01-introduction.md`](manuscript/01-introduction.md) — two-study problem framing, contributions, and scope
3. [`manuscript/02-background-and-related-work.md`](manuscript/02-background-and-related-work.md) — related literature and novelty boundary
4. [`manuscript/03-methods.md`](manuscript/03-methods.md) — frozen Study-1 methods and provenance
5. [`manuscript/03-study2-methods-extension.md`](manuscript/03-study2-methods-extension.md) — separately frozen Study-2 design, runtime/evidence boundary, endpoints, and analysis
6. [`manuscript/04-results.md`](manuscript/04-results.md) — frozen Study-1 results
7. [`manuscript/04-study2-results-extension.md`](manuscript/04-study2-results-extension.md) — frozen Study-2 RQ1–RQ5 results and interpretation limits
8. [`manuscript/05-discussion.md`](manuscript/05-discussion.md) — cross-study interpretation, limitations, and implications
9. [`manuscript/06-conclusion.md`](manuscript/06-conclusion.md) — combined bounded conclusions and remaining research path
10. [`manuscript/07-declarations-and-availability.md`](manuscript/07-declarations-and-availability.md) — ethics, responsible-research boundary, data/code availability, funding, and declarations

Assembly and submission controls:

- [`manuscript/MANUSCRIPT-ASSEMBLY.md`](manuscript/MANUSCRIPT-ASSEMBLY.md)
- [`manuscript/claim-traceability.csv`](manuscript/claim-traceability.csv) — historical/frozen Study-1 claim traceability
- [`manuscript/study2-claim-traceability.csv`](manuscript/study2-claim-traceability.csv) — Study-2 claim-to-evidence boundaries
- [`manuscript/citation-readiness.csv`](manuscript/citation-readiness.csv)
- [`manuscript/submission-inputs.csv`](manuscript/submission-inputs.csv)

**Current journal state:** the two-study journal integration and target-package reconciliation were merged through PR #72 at `6f9a1a5d26287120278913d453b26c78f267870f`. Study-1 and Study-2 statistics remain frozen. The exact Study-2 Phase-6 source evidence has passed responsible-release review with disposition `APPROVED_FOR_PUBLIC_DURABLE_ARCHIVE_WITH_PROVENANCE_WRAPPER`. The remaining pre-submission archive object is the **responsible-release-reviewed DOI archive**: the review portion is complete, while durable Study-2 DOI publication, public checksum verification, and DOI insertion remain pending. Submission-day live-policy/portal verification and exact-export citation/DOI/frozen-claim/scope audits follow.

## 2. Frozen study boundaries

### Study 1

- 24 frozen cells × 30 repetitions
- 720 VALID statistical observations
- 9 retained INVALID attempts outside statistical membership
- 696-observation final-commit complete-block analysis is sensitivity only
- DOI-bearing public evidence-of-record: Zenodo v1.0.0, `10.5281/zenodo.22181540`

### Study 2

- 85 frozen cells
- 3,872 VALID observations
- 0 INVALID attempts
- 162 primary paired contrasts
- 432 prespecified secondary contrasts
- Phase-7 independent reproduction: 0 mismatches
- canonical freeze: `study2/PHASE7_RESULTS_FREEZE.json`
- canonical provenance: `study2/PHASE7_PROVENANCE.json`
- Phase-7 result ZIP retained durably in Git history
- exact Phase-6 source ZIP passed responsible-release review; release record and DOI-deposit metadata are under `study2/release/phase6/`
- remaining archive requirement: publish the exact approved ZIP to a durable DOI-bearing Study-2 dataset and verify the public checksum before submission

The two statistical populations are **not pooled**. Study 2 is a separately frozen empirical extension and does not change Study-1 observations, statistical estimates, or historical Zenodo v1.0.0.

## 3. Main publication displays

### Study-1 frozen displays

1. [`tables/table-r1-proposition-summary.csv`](tables/table-r1-proposition-summary.csv)
2. [`tables/table-r2-p2-contact-effects.csv`](tables/table-r2-p2-contact-effects.csv)
3. [`tables/table-r3-p3-p4-evidence-pathways.csv`](tables/table-r3-p3-p4-evidence-pathways.csv)
4. [`tables/table-r4-p5-pareto-status.csv`](tables/table-r4-p5-pareto-status.csv)
5. [`tables/table-r5-cybersecurity-positioning.csv`](tables/table-r5-cybersecurity-positioning.csv)
6. [`tables/table-r6-security-property-mapping.csv`](tables/table-r6-security-property-mapping.csv)
7. [`tables/table-s1-execution-provenance-sensitivity.csv`](tables/table-s1-execution-provenance-sensitivity.csv)

Tracked Study-1 figures remain under [`figures/`](figures/).

### Study-2 journal displays

- [`tables/table-r7-study2-prespecified-findings.csv`](tables/table-r7-study2-prespecified-findings.csv) — compact RQ1–RQ5 evidence summary
- [`tables/table-s2-study2-secondary-holm.csv`](tables/table-s2-study2-secondary-holm.csv) — prespecified secondary-family Holm counts

These Study-2 tables summarize the frozen Phase-7 record; they do not replace the authoritative machine-readable results/provenance under `../study2/`.

## 4. Data and reproducibility status

**Study 1:** the public source-evidence archive is Zenodo v1.0.0, version DOI `10.5281/zenodo.22181540`, concept DOI `10.5281/zenodo.22181539`.

**Study 2:** the exact Phase-7 statistical result ZIP is durably retained in repository history with SHA-256 `0136123a53d150437fefc8ace342af63b11d980cf8cab32ef7a4f03b78267417`. The underlying Phase-6 source ZIP is cryptographically bound and has completed responsible-release review without any source-evidence or frozen-science modification. It is not yet represented as a DOI-bearing public evidence release. A DOI must be recorded only after the exact approved ZIP is published and the public checksum is independently verified.

See [`../docs/REPRODUCIBILITY_GUIDE.md`](../docs/REPRODUCIBILITY_GUIDE.md) for the distinction between Study-1 reproduction, Study-2 independent audit, safe repository validation, and any future new replication.

## 5. Journal interpretation boundaries

Any reuse or export must preserve all of the following:

- Study 1 = exactly 720 VALID observations; Study 2 = exactly 3,872 VALID observations; never report a pooled statistical population.
- Study-1 P1 remains unsupported on its predeclared primary outcomes.
- Study-1 C1 timing is modeled contact, not operational ground-contact timing.
- Study-1 T1 is omission/reduction of selected policy-visible evidence, not stale/contradictory/forged evidence.
- Study-1 P7 is deterministic rule-based, not AI/ML.
- Study-2 V5 shows that evidence can remain policy-qualified while being false relative to the research-only adjudication truth under the bounded compromise model.
- Study-2 Block-C BENIGN/ADVERSARIAL contrasts are a structural label-invariance/control result only; they do not establish empirical benign-versus-adversarial causal discrimination.
- Study-2 K4 is separate intermittent/flapping contact, not ordinal severity 4.
- Study-2 A2/K2 is a coupled producer-compromise/contact-loss profile.
- Study-2 secondary n=32 blocks are estimation/sensitivity evidence, not prospectively powered small-effect confirmatory evidence.
- No weighted global score, global policy rank, operational spacecraft claim, RF claim, real-link latency claim, flightworthiness claim, or certification claim is supported.

## 6. Submission package

The primary venue package is under [`submission/computers-and-security/`](submission/computers-and-security/). Its two-study reconciliation and Study-2 responsible-release review are complete; remaining work is the Study-2 DOI publication/public-checksum/DOI-insertion gate plus live publisher-policy/portal checks and exact-export validation on the actual submission date.

The manuscript source remains target-neutral. Do not maintain a second manually copied full manuscript in the submission directory.
