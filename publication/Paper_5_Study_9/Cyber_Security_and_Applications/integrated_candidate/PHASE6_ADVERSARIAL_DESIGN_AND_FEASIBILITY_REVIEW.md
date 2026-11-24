# Phase 6 adversarial design and feasibility assessment — Paper 5

Status: STATIC_DESIGN_REVIEW_CONDITIONAL; NO EXPERIMENTS. Review uses exact pinned source, historical CI and authoritative public guidance. Not independent human peer review.

## Strongest objections and corrections

| ID | Severity | Adversarial challenge | Design response / remaining gate |
|---|---|---|---|
| P6-A01 | MAJOR | Duplicates G3's 18 controls/1,024 selector comparisons and calls it new science. | New target is documented source schema discrimination, extension-only derivations, complete/incomplete observation separation and constrained completions; old parity is baseline only. Final fixtures must demonstrate distinct targets. |
| P6-A02 | MAJOR | Historical G3 completeness equality conflates M_present and Q_satisfied. | Static confirmed mismatch in G3 helper/expected negative value case vs S2 runtime presence and S9 semantics. Preserve historical PASS, no numerical correction inferred; test presence and satisfaction separately. RQ-E5 manuscript claim requires bounded clarification before submission. |
| P6-A03 | MAJOR | Rejected extra rows can make aggregate signature/trust/fresh/epoch false while accepted required keys remain present. | Do not impose implication universally; F2 is named atomic publication hypothesis; explicit counterexample outside model. |
| P6-A04 | MAJOR | A contradiction on nonrequired key can coexist with all ten required keys. | F1 limits scope to required keys, same subject/epoch; no general M -> not C claim. |
| P6-A05 | MAJOR | Nonempty Boolean subset does not establish realizable mission states. | Model-specific logical restrictions only; witness proof and characterization before freeze; no claim of all-state concrete reachability or physics. |
| P6-A06 | MAJOR | Semantic control expected outputs constructed by same evaluator; circular validation. | Distinct specification, alternate oracle, held-out fixture file/manifest, leakage audit, trivial baselines; no blind independent human review. Exact fixture plan remains pending. |
| P6-A07 | MAJOR | DIRECT schema and invalid/null row incorrectly collapsed; false is missing. | Separate schema class, row admission, nullable value and invalid-domain population flag. Preserve S9 historical deviation. |
| P6-A08 | MAJOR | Empty feasible slice yields spurious singleton or zero metric. | Explicit INCONSISTENT_OBSERVATION and compare common feasible slices only. All tied minima, no vacuous success. |
| P6-A09 | MODERATE | Time-only mutations reuse stale ledger; context provenance guessed. | All full observations require coherent same decision snapshot; isolated boundary tests labeled, no selector endpoint when insufficient. |
| P6-A10 | MAJOR | Rule derives from IDs, labels, clocks or undocumented expected epoch. | D_FRESH/D_EPOCH are proposed only in new synthetic registry with strict scope and authoritative inputs; missing context remains unknown; old registries empty. |
| P6-A11 | MODERATE | Designed cases or 3^8 patterns misrepresented as independent experiments. | Deterministic family denominators, exhaustive model counts not mission trials, no p-values or acceptance probability. |
| P6-A12 | MAJOR | Favorable reduction or novel constraints chosen post hoc. | F0/F1/F2 declared before execution; reduction not required; counterexamples and negative results retained; no tuning. |
| P6-A13 | MAJOR | Model conclusions overclaim RATS/NIST conformance and live recovery. | RATS and NIST are motivating role/context guidance only; no universal predicates or physical constraints from standards. |
| P6-A14 | MAJOR | Author asked design only; implementation or execution sneaks in. | No harness, synthetic fixtures, new scientific run, data download, protocol freeze or publication. Only review documents committed. |

## Feasibility

- Model size: eight Boolean variables, finite subset search, candidate 72 synthetic instances, and planned 3^8 partial patterns; computationally modest in principle, no runtime benchmark executed. Exact memory/runtime/implementation behavior unverified. A local standard-library harness should suffice given frozen selector uses only dataclasses/enums. No real-data or paid service needed for design; no expense committed.
- New independent architecture evidence: not established. F1/F2 are explicitly conditional reference architectures, not validated mission constraints. To claim physical feasibility would require new architecture/mission documentation and separate approval.
- Technical independence: alternate implementation and expected specification separation feasible for sole author, but inter-rater agreement and independent human adjudication not established.
- Standards: RFC 9334, NIST IR 8401 motivate verifier/decision authority and ground-segment recovery. TRACE shows feasibility constraints are prior art. These sources do not justify a universal relation between the eight predicates.
- Tools: GitHub MCP for read-only exact source inspection, workflow metadata/logs and authorized documentation commits; Acumen for a narrow recent-literature screen, public web primary source verification; no unpublished manuscript sent to external scholarly services in this phase. Prior citation checks retained, not rerun gratuitously.

## Exact prior Phase 5 validation checkpoint

Source head 442a59b3319c9c2dd3224609e2169c87f83cac35; LaTeX 45294627270 SUCCESS and research configurations 45294627295 SUCCESS. Logs show 34 main pages, five S1 pages, zero overfull boxes each, 32 main underfull warnings; frozen-science and 56-mapping checks PASS and packaged manifest PASS. Artifact ID 14875821712, GitHub reported ZIP digest sha256:4ee1a114b2822b92b0ced5d8b76ef18f994aa62ba761e4bfb63cc1a5484f608f. Main runner digest 9e753ca6961d0bef98eb37c71c9dd1febe7a602d13e219f383a9a2310c6fd26a; S1 fa6dbaade6227e86b490c7f08b87e5f830082de4f626d7b9cf36535d53fc4a31. This checkpoint rechecked runner logs and metadata; did not download/rehash/render the revised PDFs. Fresh visual proof remains pending.

## Verdict

DESIGN_FEASIBLE_IN_PRINCIPLE__STATIC_REVIEW_CONDITIONAL__NOT_FREEZE_READY. Main remaining blockers: exact serialized fixture and expected-class/value/error tables, independent oracle and comparator specification, constraint witness/proof or explicit abstraction bounds, author agreement on M/Q distinction and claim scope, and exact protocol/input/code freeze authorization. Design-only approval does not close these gates. No score upgrade. No frozen science edits, merge or submission.
