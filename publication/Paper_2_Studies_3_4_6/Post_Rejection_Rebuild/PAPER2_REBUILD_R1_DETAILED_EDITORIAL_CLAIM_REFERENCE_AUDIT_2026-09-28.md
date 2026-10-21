# Paper 2 Rebuild R1 — Detailed Editorial, Claim, Citation, and Manuscript-Quality Audit

**Audit date:** 2026-09-28  
**Authoritative manuscript:** `PAPER2_REBUILD_MANUSCRIPT_R1_2026-09-28.md`  
**Authoritative manuscript blob:** `822aa4257f15b76f16fed35c1131b2063923b0c8`  
**Authoritative main:** `0e94e5eee412645c5a039a5295f88db01fdd6d68`  
**Audit mode:** read-only manuscript review; no scientific execution; no manuscript mutation; no venue lock.

## 1. Executive verdict

`PASS_SCIENTIFIC_INTEGRITY__EDITORIAL_AND_REFERENCE_CORRECTIONS_REQUIRED_BEFORE_VENUE_LOCK`

The findings-first R1 rebuild materially corrects the central communication problems identified after the TAES prescreen decision: the research question is visible early, the contributions are phrased as findings, the limitations are consolidated, and S3X is integrated under RQ1 without pooling it with Study 3.

The audit found **no frozen-result numerical correction** required for the quantitative claims checked against Studies 3, 4, 6, and the effective Phase-7F claim-use authority.

The remaining rejection risk is concentrated in four areas:

1. endpoint precision: the title and some high-level prose say "recovery" where the evaluated endpoint is recovery **qualification**;
2. literature-gap proof: the bibliography does not yet confront several close 2025–2026 spacecraft-security papers, especially legitimate-looking false telemetry produced by compromised onboard components;
3. S3X selection/independence wording: the P99_X10 selection history and the phrase "independently sourced" should be made more exact;
4. display balance: RQ1 currently carries the largest and newest result set but lacks the compact numerical display that RQ2 and RQ3 receive.

These are manuscript-development findings. They do not reopen the frozen science.

## 2. Quantitative and scientific claim audit

### Study 3

The R1 values checked against the frozen Study-3 authority are consistent:

- 1,380 trajectories;
- 67,620 epoch states;
- persistent V5/K0 B0 and S1: 46/46 trajectories, mean 122.500 logical seconds;
- persistent V5/K4 B0: 46/46, mean 55.326 logical seconds;
- persistent V5/K4 S1: 46/46, mean 49.022 logical seconds;
- B2 structural-zero cells reported as 0/46;
- truthful V0/K4/B0: 3/46 trajectories, mean 0.326 logical seconds.

No Study-3 numerical correction is required.

### Study 4

The 4,608-observation population and complete 18-rule first/systematic threshold map agree with the frozen Study-4 authority. Spot checks covering the main provenance result all match, including:

- `Q3_D3`: unsafe 3/6, benign 2/5;
- `Q4_D3`: unsafe 4/6, benign 2/4;
- `Q5_D3`: unsafe 5/6, benign 2/3;
- null/equal-threshold examples retained in the manuscript.

No Study-4 numerical correction is required.

### Study 6

The 420-observation population and the principal finite-state counts agree with the frozen Study-6 authority:

- G0: 4/5 incorrect states remain qualified; 32/64 benign unavailable-signal subsets rejected;
- G1/G2: 3/5; 48/64;
- G3/G4: 2/5; 56/64;
- G5: 1/5; 63/64;
- `APPROVED_BAD_SOURCE` is the remaining G5 incorrect state.

No Study-6 numerical correction is required.

### S3X Phase 7

The R1 S3X structural counts agree with the effective Phase-7F claim-use record:

- 1,919 frozen intervals;
- 34,542 cases;
- 30,704 matched comparisons;
- 5,757 B0-versus-S1 cache comparisons;
- 11,514 V4 first-refresh cases;
- 7,676 B0/S1 V5 interval-arm cases;
- 3,838 B2 V5 cases;
- 5,757 V5 gap-versus-control first-refresh classification comparisons.

The manuscript also preserves zero case-level and zero matched-comparison mismatch claims and the two-run byte-identical result statement. No S3X result correction is required.

## 3. Abstract-to-results consistency

**Verdict: PASS with one wording refinement recommended.**

The abstract's numerical claims map to the body:

- S3X 1,919 intervals and 7,676/3,838 V5 counts;
- Study 4 18 rules and 4,608 observations;
- Study 6 four-of-five to one-of-five residual incorrect-state progression.

The abstract appropriately avoids pooled sample size, p-values, operational probabilities, and global policy ranking.

Recommended refinement: the abstract begins with "Satellite cyber recovery depends on decisions..." but the measured endpoint throughout the paper is **qualification**, not completed recovery. The abstract should consistently use "cyber-recovery qualification" when referring to what is actually evaluated.

## 4. Research-question and endpoint precision

### High-priority finding A1 — title overbreadth

Current title:

> Residual Trust Boundaries in Satellite Cyber Recovery: Temporal Evidence, Producer Composition, and Artifact Assurance

The experiments do not execute or measure completed recovery. They evaluate qualification decisions. A reviewer can reasonably read the current title as broader than the endpoint.

**Recommended candidate title for the next manuscript-edit phase:**

> **Residual Trust Boundaries in Satellite Cyber-Recovery Qualification: Temporal Evidence, Producer Composition, and Artifact Assurance**

This is a manuscript correction recommendation, not an authorized edit in this audit phase.

### High-priority finding A2 — central question can imply one integrated architecture

Current central question joins fresh evidence, multiple trusted producers, and an approved recovery artifact in one sentence. The manuscript later explains that the studies are separate, but the question can initially imply that one integrated end-to-end system was experimentally tested.

**Recommended candidate wording:**

> Across separately evaluated temporal, producer-composition, and artifact-assurance layers, which trust failures remain invisible to a satellite cyber-recovery qualification decision?

This keeps the systems synthesis while making study separation explicit at the question itself.

## 5. RQ1 / Study-3 + S3X audit

**Scientific answer strength: strong.** The manuscript now distinguishes:

- freshness-origin exposure from truthful cached evidence;
- post-signature alteration with invalid signature;
- false-but-valid evidence produced within the trusted-producer boundary;
- external timing delay versus first-refresh classification.

### High-priority finding A3 — P99_X10 selection wording

Current R1 states:

> "A prespecified cadence-sensitivity process selected the P99_X10 rule..."

That sentence is directionally correct but can be read as though P99_X10 itself was prospectively fixed before inspecting the sensitivity results.

The repository authority is more precise:

- the **eight-rule sensitivity analysis was prespecified**;
- P99_X10 was selected **after** that sensitivity analysis;
- P99_X10 was then frozen before timestamp-trace extraction and Phase-7 replay;
- retuning after freeze is prohibited.

**Recommended replacement concept for the next edit phase:**

> A prespecified eight-rule cadence-sensitivity analysis was performed; P99_X10 was selected after that analysis and then frozen before timestamp-trace extraction and recovery replay.

This disclosure is important against a cherry-picking/post-hoc-selection objection.

### Moderate finding A4 — "independently sourced"

The phrase "independently sourced telemetry interval population" may be read as independent validation or replication. The repository governance expressly limits that claim.

Prefer:

> "externally sourced, separately frozen telemetry interval population"

and retain the existing statement that S3X is not an external empirical replication of Study 3.

### Moderate finding A5 — "portability test"

"Strengthens the portability test" is broader than the evidence establishes. Prefer:

> "provides an external-source timing stress test of the frozen Study-3 decision semantics."

### Moderate finding A6 — V4 heading

"V4 Remains Integrity-Detectable" can sound broader than the modeled signature condition. Prefer:

> "V4 Remains Non-Qualifying Under Signature Validation."

## 6. RQ2 audit

**Verdict: strong and appropriately bounded.**

The Study-4 section correctly preserves:

- full 18-rule map rather than cherry-picking favorable provenance cells;
- first-versus-systematic failure distinction;
- benign-loss tradeoff;
- null provenance effects;
- synthetic-domain limitation;
- no global ranking.

Primary editorial opportunity: reduce repeated reminders that the map is finite/synthetic in the results subsections and let Section VIII carry more of that burden. The core result is already sufficiently qualified.

## 7. RQ3 audit

**Verdict: strong, with abstraction criticism foreseeable.**

The Study-6 result is clear because residual-state identity is retained rather than collapsed into counts. The G3/G4 equal-count but different-state contrast is especially useful.

Likely reviewer objection: the six-state Boolean model may appear too constructed. The manuscript should answer this by explaining why these states were selected to expose distinct observability assumptions, while preserving the statement that they are not an exhaustive supply-chain taxonomy.

The current `APPROVED_BAD_SOURCE` interpretation is appropriately bounded and should remain.

## 8. Cross-study synthesis audit

The synthesis is substantially stronger than R10. It now has a single mechanism-level answer: the residual boundary depends on the difference between visible evidence and the property the decision actually needs to know.

### Moderate finding A7 — universal-sounding conclusion

Current conclusion:

> "each control can establish only the property represented by the evidence it observes."

The paper supports that statement **within the registered finite models**, not as a general theorem about all security controls.

Recommended wording:

> Within these finite models, each control establishes only properties represented in its policy-visible evidence.

## 9. Literature and citation audit

### Existing 14-reference integrity check

A batch scholarly-identifier audit produced:

- 14 references checked;
- 8 direct scholarly identifier matches;
- 5 entries not resolved by the scholarly database because they are standards/web resources;
- 1 metadata mismatch on the ESA dataset citation;
- 0 retractions detected.

The five unresolved entries are not treated as fabricated. They are web/standards materials requiring source-specific verification: SPARTA, the IETF multi-Verifier Internet-Draft, TUF, and two SLSA pages.

### Required reference correction R1 — ESA dataset

The DOI is correct, but the current author/title metadata should be corrected before submission.

Current manuscript entry:

> European Space Agency, "ESA Anomaly Dataset, v2," ...

DOI resolution identifies:

> G. De Canio, K. Kotowski, and C. Haskamp, "ESA Anomaly Dataset," 2025. doi: 10.5281/zenodo.15237121.

The manuscript can still state that the frozen source is **v2**; the bibliographic author metadata should follow the DOI record.

### Required reference refinement R2 — SPARTA

The manuscript makes a specific recovery-baseline claim but cites the generic SPARTA homepage. Before submission, prefer the specific SPARTA countermeasure **CM0044 Cyber-safe Mode** or the most direct official SPARTA page supporting the exact statement.

### Existing standards freshness

Manual source checks during this audit found:

- RFC 9334 remains appropriate for Evidence/appraisal/freshness framing;
- `draft-ietf-rats-multi-verifier-00` remains the current cited multi-Verifier WG draft as of the audit date and should retain "work in progress";
- TUF v1.0.36 remains the cited current release;
- SLSA v1.2 remains the relevant current source/build/threat-boundary version.

These checks support the existing use of those sources but do not convert them into peer-reviewed evidence.

## 10. Material literature gaps through September 2026

The present 14-reference bibliography is too sparse to make the novelty boundary maximally defensible. The following are high-value candidates for the next manuscript-edit phase.

### Priority L1 — closest spacecraft false-evidence result

J. Vanlyssel, G.-C. Roman, and A. Anwar, "Silent Subversion: Sensor Spoofing Attacks via Supply Chain Implants in Satellite Systems," 2026 IEEE Aerospace Conference, pp. 1–10, doi: **10.1109/AERO66936.2026.11519913**.

Why it matters: this work demonstrates a compromised vendor-supplied onboard component generating telemetry in the correct format and cadence that ground software accepts as legitimate. That is close to the paper's trusted-producer semantic-falsity motivation.

Required differentiation if cited:

- Silent Subversion demonstrates the feasibility and mission consequences of legitimate-looking false telemetry from an onboard supply-chain implant;
- Paper 2 characterizes **recovery-qualification** boundaries under explicit freshness/contact/policy semantics, separates cache-origin exposure from false-but-valid trusted-producer evidence, and stress-tests the temporal mechanism with a separately frozen external timing population.

Failing to discuss this paper would leave an avoidable novelty challenge.

### Priority L2 — major satellite-communications cybersecurity survey

S. Salim, N. Moustafa, and M. Reisslein, "Cybersecurity of Satellite Communications Systems: A Comprehensive Survey of the Space, Ground, and Links Segments," IEEE Communications Surveys & Tutorials, vol. 27, no. 1, pp. 372–425, 2025, doi: **10.1109/COMST.2024.3408277**.

Use: current field-level threat/defense context and evidence that the paper is positioned against the modern satellite cybersecurity literature.

### Priority L3 — 2026 systematic satellite-security review

B. Wang et al., "A Comprehensive Literature Review of Cybersecurity in Satellite Networks," Aerospace, vol. 13, no. 3, p. 249, 2026, doi: **10.3390/aerospace13030249**.

Use: current systematic literature coverage. It should be consulted before making any "not identified in the literature" formulation.

### Priority L4 — official commercial-satellite cybersecurity context

M. Scholl and T. Suloway, "Introduction to Cybersecurity for Commercial Satellite Operations," NIST IR 8270, 2023, doi: **10.6028/NIST.IR.8270**.

Use: satellite-specific cybersecurity context from an authoritative standards body; useful for making aerospace relevance concrete rather than generic.

### Strongly consider

- M. Utsash et al., "Investigating the Effectiveness of Zero-Trust Architecture for Satellite Cybersecurity," ICISSP 2025, pp. 133–140, doi: **10.5220/0013103200003899**.
- C. Mattar et al., "What is Cybersecurity in Space?," AICCSA 2025, pp. 1–6, doi: **10.1109/AICCSA66935.2025.11315201**.
- B. G. Cho et al., "Space-Forensic Tool Coverage Derivation Through Satellite System Profiling," IEEE Access, vol. 14, pp. 72313–72330, 2026, doi: **10.1109/ACCESS.2026.3686372**.
- J. P. C. M. Oliveira et al., "CubeSat Cybersecurity: An Overview," IEEE Access, vol. 14, pp. 108539–108547, 2026, doi: **10.1109/ACCESS.2026.3705697**.
- NASA Space Security: Best Practices Guide / current NASA software-security handbook material for explicit prevent/mitigate/recover operational context.

These candidates are not automatically approved manuscript references. They are audit findings for the next reference-integration gate.

## 11. Figures and tables

R1 currently gives RQ2 and RQ3 compact numerical tables but leaves the expanded RQ1/Study-3+S3X result primarily in prose.

### High-priority finding A8 — restore a compact temporal result display

The prior TAES display review had already determined that exact Study-3 values were better represented as a table than as a trend chart.

For the new R1, create a compact RQ1 table that keeps Study-3 logical-time values and S3X cadence-normalized values visibly separate. Candidate content:

- persistent V5/K0 B0, S1, B2;
- persistent V5/K4 B0, S1, B2;
- truthful V0/K4/B0 cache row;
- S3X B0-vs-S1 cache contrast (+1 cadence unit);
- S3X V4 first-refresh non-qualification;
- S3X V5 B0/S1 versus B2 first-refresh classification.

Do not merge logical seconds with cadence units.

### High-priority finding A9 — update the approved qualitative figure

The historical Figure 1 revision-2 design already passed visual QA as three **parallel** residual-boundary panels with no arrows or experimental data flow.

A new rebuild figure should preserve that architecture but add S3X as an **external timing stress-test inset inside the temporal panel**, not as a fourth sequential layer. Required visible controls should include:

- separately evaluated populations;
- qualitative synthesis only;
- no pooled population;
- no experimental data flow;
- only Study 3 contains the frozen synthetic contact treatment;
- S3X intervals are external timing proxies, not observed contact loss.

The historical figure should not simply be copied into R1 because it predates S3X.

## 12. Prose and readability

The rebuild is substantially less defensive than R10, but governance vocabulary remains visible in the main narrative.

Observed manuscript-level counts include approximately:

- `frozen`: 32 occurrences;
- `does not`: 25 occurrences;
- `separate` / `separately`: more than 30 combined occurrences.

Recommendation: retain formal provenance terminology where it matters—in methods, reproducibility, and validity—but use ordinary scientific phrasing such as "prespecified," "fixed," "finite," or direct positive statements elsewhere.

This is an editorial compression issue, not a scientific problem.

## 13. Reviewer-objection stress test

| Likely objection | Current protection | Remaining action |
|---|---|---|
| "The paper did not execute recovery." | Validity section states qualification is modeled. | Put **qualification** in title, abstract, and central RQ. |
| "This could apply to any CPS; why satellite?" | Space-specific intro and ESA timing extension. | Add NIST/NASA context and closer spacecraft literature. |
| "The three studies are not integrated." | Non-pooling language is strong. | Make separation explicit in the central RQ wording itself. |
| "P99_X10 was chosen after looking at data." | Freeze/audit trail exists. | State the exact eight-rule prespecified-analysis then post-analysis selection/freeze chronology. |
| "ESA gaps are not contact loss." | Current firewall is strong. | Retain unchanged. |
| "B2 appears globally superior." | Current no-ranking language is strong. | Retain; do not rank policies. |
| "The reference evaluator is not independent replication." | Current wording is strong. | Retain unchanged. |
| "Why no inferential statistics?" | Complete finite-population rationale is stated. | Keep concise explanation. |
| "Literature gap is asserted, not demonstrated." | Related-work structure exists. | Add recent survey/systematic review + closest attack papers and a compact prior-work comparison. |
| "Study 6 is too abstract." | State/gate limits are acknowledged. | Add concise rationale for why the selected states expose distinct trust assumptions. |
| "The paper still reads like a governance record." | R1 is much improved. | Reduce repetitive frozen/non-claim wording in the next edit pass. |

## 14. Recommended pre-venue manuscript-edit scope

Before venue selection, a separately authorized R2 edit should:

1. refine title and central RQ to **qualification**;
2. integrate the high-priority literature and explicitly compare the closest 2026 work;
3. correct reference [14] metadata and strengthen the SPARTA citation;
4. clarify P99_X10 selection chronology;
5. replace "independently sourced" / "portability test" with narrower S3X language;
6. add a compact Study-3/S3X RQ1 table;
7. redesign the parallel residual-boundary figure with S3X as a temporal inset;
8. reduce repeated governance/negative phrasing without deleting scientific caveats;
9. preserve all frozen counts and existing non-pooling / non-replication / no-ranking firewalls;
10. conduct a second claim/reference audit before any venue lock.

## 15. Gate decision

This audit does **not** authorize changes to R1.

Current verdict:

`PASS_SCIENTIFIC_INTEGRITY__EDITORIAL_AND_REFERENCE_CORRECTIONS_REQUIRED_BEFORE_VENUE_LOCK`

Next controlled gate:

`AUTHOR_REVIEW_AFTER_REBUILD_R1_DETAILED_AUDIT_PR_AND_PREMERGE_CI_BEFORE_MERGE`
