# Paper 3 — IJCIP Live Author-Requirement and Adaptation Audit

**Audit ID:** `PAPER3-S7-S7E-IJCIP-COMPLIANCE-001`  
**Date checked:** 2026-09-24  
**Target:** International Journal of Critical Infrastructure Protection (IJCIP)  
**Result:** `PASS_WITH_PORTAL_ITEMS_STILL_TO_VERIFY__SUBMISSION_NOT_AUTHORIZED`

## 1. Source-access note

The official Elsevier journal page confirms IJCIP's aims and scope and links to the ScienceDirect Guide for Authors. During this audit, the journal-specific ScienceDirect Guide-for-Authors endpoint returned HTTP 403 through the research browser. No inaccessible journal-specific rule is inferred or fabricated.

Verified requirements are therefore separated into:

1. current official IJCIP scope;
2. current Elsevier journal-author policy/guidance;
3. formatting/declaration patterns visible in current IJCIP published articles;
4. items that must be rechecked in the live submission portal or accessible Guide for Authors before final submission.

## 2. Scope — PASS

IJCIP explicitly seeks high-quality work in critical-infrastructure protection and specifically includes:

- security challenges across infrastructure sectors;
- core protection principles and techniques;
- dependencies/interdependencies and cascading-failure mitigation;
- sophisticated practical solutions using mathematical, scientific, and engineering methods.

R3 frames spacecraft cyber recovery as a bounded protection/continuity problem for a space-enabled critical-infrastructure asset. It explicitly disclaims measurement of cross-sector cascading failures and national-level outage consequences.

## 3. Critical-infrastructure factual boundary — PASS

R3 does **not** claim a formal CISA "Space Systems Sector."

Instead it uses three supportable statements:

- U.S. space policy describes space systems as an essential component of U.S. critical infrastructure because they provide and enable services;
- CISA's Communications infrastructure description explicitly includes satellite;
- CISA documents Communications dependencies across multiple critical-infrastructure sectors.

The paper uses those sources for contextual relevance, not as experimental evidence.

## 4. Keywords — PASS

Current Elsevier author guidance: maximum 6 keywords.

R3 uses exactly six:

1. satellite cybersecurity
2. cyber recovery
3. critical infrastructure protection
4. trust domains
5. machine-learning assurance
6. common-cause failure

## 5. AI disclosure — PASS WITH TWO-PART DISCLOSURE

Current Elsevier policy requires a separate declaration before References for substantive AI-assisted manuscript preparation.

Elsevier also states that AI used as part of the research process should be described in Methods.

Repository provenance confirms OpenAI ChatGPT assisted pre-freeze protocol refinement, code/test drafting, documentation, and verification-oriented review, while the author controlled all research decisions, repository changes, execution authorization, and frozen-result verification.

R3 therefore uses:

- a concise Methods provenance subsection for research-development assistance; and
- a separate Elsevier-style manuscript-preparation declaration before References.

This is more accurate than deleting all Methods disclosure.

## 6. Highlights — PREPARED

Current IJCIP articles display Highlights, and Elsevier guidance defines highlights as 3-5 bullets of no more than 85 characters each.

Prepared five bullets; character counts excluding the bullet marker are:

- 82
- 76
- 74
- 76
- 78

All are within the 85-character guidance.

## 7. Abstract — PASS, JOURNAL-SPECIFIC LIMIT STILL TO VERIFY

R3 abstract is approximately 242 words and contains problem, study design, key finite-population results, and conclusion.

No IJCIP-specific abstract word limit was independently verified because the journal-specific Guide endpoint was inaccessible. The live portal/Guide must be checked before submission.

## 8. Model-simplicity reviewer risk — MANAGED

R3 now states in Methods that the Study-7 linear-threshold learner is deliberately simple as an experimental control, not an algorithmic contribution. Its purpose is to keep the visible decision boundary inspectable and isolate information sufficiency from model-capacity/optimization confounds.

Study 7E additionally uses frozen scikit-learn decision trees, 84 training scenarios, 196 held-out scenarios, 784 decisions, held-out faults/topologies, cFS grounding, and an independent semantic-tree audit.

R3 does not claim to prove performance of every possible advanced model.

## 9. "Trivial correlated failure" risk — MANAGED

R3 retains Study 7's correlated-false-corroboration case as the information-boundary foundation but relies on Study 7E for nontrivial architecture evidence:

- explicit source/key/execution/transport/authority domains;
- F10-F12 common-cause/adverse-transfer behavior;
- topology-controlled T0-T4 analysis;
- non-monotonic learned behavior.

R3 does **not** claim that operational spacecraft FDIR universally assumes independent failures.

## 10. Operational telemetry objection — MANAGED

R3 explicitly states that OPS-SAT-style telemetry benchmarks address anomaly-detection performance but do not expose the controlled adjudication truth, domain aliasing, fault interventions, and equal-information semantics required by the recovery-authorization experiment.

The manuscript frames finite controlled populations as an isolation step before future noisy-telemetry validation, not as a substitute for all operational validation.

## 11. Declarations — PREPARED

Current IJCIP published articles commonly include:

- CRediT authorship contribution statement;
- Declaration of competing interest;
- Funding where applicable;
- Data availability.

R3 includes these plus Code availability and an Ethics statement.

The funding/no-competing-interest content is inherited from the author's prior Paper-3 submission record:

- no research funding;
- no relevant competing interests;
- sole author.

These values must still be reconfirmed by the author at final portal submission.

## 12. References — PASS FOR NEW CI CONTEXT

R3 adds:

- U.S. Space Priorities Framework;
- CISA Communications Systems / dependency material;
- Office of Space Commerce SPD-5 summary.

These sources support contextual critical-infrastructure relevance. They do not support or create new Paper-3 experimental claims.

## 13. Current published-article patterns

Current IJCIP research articles inspected during the audit show:

- Highlights;
- numbered references;
- CRediT statements;
- competing-interest declarations;
- data-availability statements.

R3 is compatible with those visible patterns.

## 14. Items not yet claimed as verified

Before final submission, recheck in an accessible Guide for Authors or live portal:

- exact portal article-type label;
- any IJCIP-specific abstract word limit;
- whether Highlights are mandatory at first submission versus later files;
- whether a graphical abstract is required, optional, or not requested;
- exact initial file requirements/template;
- any journal-specific manuscript word/page limit;
- required portal classifications/topics;
- reviewer-suggestion fields;
- current open-access/APC choice;
- exact data/declaration portal questions.

## 15. Decision

`GO__IJCIP_R3_VENUE_ADAPTATION_PREPARED__FINAL_PORTAL_AUDIT_REQUIRED`

No publisher submission or PR #168 merge is authorized by this audit.
