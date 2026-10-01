# Paper 3 — Live Venue-Fit Assessment — 2026-09-24

**Assessment ID:** `PAPER3-S7-S7E-LIVE-VENUE-AUDIT-001`  
**Manuscript:** rebuilt Paper 3 / Study 7 + Study 7E  
**Basis:** venue-neutral R1 scientific audit PASS plus 2026-09-24 live literature audit  
**State:** `COMPLETE__PRIMARY_CANDIDATE_IDENTIFIED__VENUE_NOT_LOCKED`  
**Submission authorization:** NOT GRANTED

## 1. Evaluation criteria

Venues were assessed on:

- direct topical fit to satellite cyber-recovery and mission/safety assurance;
- fit to ML assurance without requiring algorithmic novelty;
- fit to cFS-grounded systems/software architecture;
- ability to accommodate finite modeled experiments and adverse/null results;
- conflict/overlap risk with the author's other active publication lines;
- need for reframing beyond what the frozen evidence supports.

This is a decision aid, not a venue lock.

## 2. Primary candidate — Journal of Space Safety Engineering (JSSE)

**Assessment:** `PRIMARY_CANDIDATE__STRONG_DIRECT_FIT__LOW_PORTFOLIO_CONFLICT`

JSSE states that it publishes space-safety design, research, development, science, technology, and practice. The rebuilt paper's central outcomes—unsafe recovery, false-conservative hold, common-cause failure, trust architecture, and mission-assurance implications—fit that safety orientation directly.

Recent journal content confirms that cybersecurity and AI/ML are within the active editorial neighborhood:

- Kuba and Babiceanu, "Space mission safety assurance: Cybersecurity attack scenarios and risk assessment," JSSE 12(3), 2025, DOI 10.1016/j.jsse.2025.07.005;
- "Cybersecurity internal audit framework of the European Space Agency's navigation satellite systems," JSSE 13(2), 2026, DOI 10.1016/j.jsse.2026.03.007;
- "An extended review on cyber vulnerabilities of AI technologies in space applications," JSSE 10(4), 2023, DOI 10.1016/j.jsse.2023.08.003;
- satellite-telemetry ML anomaly detection has also appeared in JSSE.

### Why it fits

- Paper 3 is an assurance/safety paper more than an ML-algorithm paper.
- Unsafe-proceed versus false-conservative outcomes are naturally interpretable as safety/availability trade-offs.
- The cFS-grounded architecture gives application-specific spacecraft context.
- No current Paper-1/Paper-2 journal collision exists in this publication program.

### Required adaptation if later locked

- foreground mission/safety assurance rather than classifier mechanics;
- preserve exact finite-population language;
- keep operational-probability disclaimers prominent;
- emphasize common-cause failure and architecture/decision interaction;
- perform a dedicated current JSSE Guide-for-Authors audit after venue lock.

## 3. Secondary candidate — AIAA Journal of Aerospace Information Systems (JAIS)

**Assessment:** `SECONDARY_CANDIDATE__VERY_STRONG_TECHNICAL_SCOPE__PORTFOLIO_OVERLAP_CAUTION`

AIAA explicitly includes aerospace systems/software engineering, verification and validation of embedded systems, machine learning, autonomous systems, systems engineering, and safety/mission assurance.

This is arguably the strongest pure technical-scope match.

AIAA's current length guidance recommends approximately 10,000-12,000 words/equivalent space for regular/full articles and 2,500-3,500 for Technical Notes. The current Paper-3 R1/R2 is between those ranges before planned figures/tables. This is guidance rather than an absolute scientific reason to pad the paper.

### Main caution

Paper 1 is already active at JAIS and Study 2/V5 is antecedent specification lineage for Paper 3. The evidence populations are separate and the repository has a strong originality boundary, but another manuscript at the same journal may create avoidable editorial/self-overlap scrutiny.

**Disposition:** retain as a strong alternative, not the preferred first target at this stage.

## 4. Third candidate — International Journal of Critical Infrastructure Protection (IJCIP)

**Assessment:** `STRONG_CYBERSECURITY_FIT__FRAMING_RISK`

IJCIP publishes practical science/engineering work for critical-infrastructure security. It has published space-cybersecurity work and, in 2026, S-LARF for adversarial resilience in spaceborne anomaly detection.

Paper 3 could fit if framed around continuity and protection of critical space infrastructure. However, the manuscript should not overstate its bounded spacecraft reference experiment as evidence about societal infrastructure-scale resilience.

**Disposition:** credible third option if a cybersecurity-first framing is desired.

## 5. Additional candidates

### IEEE Transactions on Aerospace and Electronic Systems

**Fit:** strong systems/aerospace scope. TAES covers organization, design, integration, and operation of complex systems including spacecraft, telemetry, and command/control.

**Caution:** Paper 2 is already active at TAES. Paper 2 also contains provenance/composition assurance concepts that would require careful overlap management.

**Disposition:** technically credible backup; portfolio risk makes it less attractive than JSSE/JAIS for Paper 3.

### IEEE Systems Journal

**Fit:** moderate. Its scope includes complex systems, cyber-physical systems, mission assurance, safety, risk, security, architectures, and systems engineering. Regular papers permit up to 12 pages during review.

**Caution:** Paper 3 is a bounded spacecraft recovery architecture, not a broad system-of-systems study. A systems-level reframing could invite claims beyond the frozen evidence.

**Disposition:** backup venue.

### Acta Astronautica

**Fit:** broad space-system scope and demonstrated satellite-ML publication activity.

**Caution:** the paper's core identity is cyber-recovery assurance rather than general astronautics; a separate Paper-4 line was also recently rejected by Acta, creating no scientific prohibition but an avoidable portfolio/process consideration.

**Disposition:** backup rather than first target.

### Aerospace Science and Technology

**Fit:** moderate; scope includes complex-system engineering, information processing, robotics/intelligent systems, and satellite engineering.

**Caution:** cybersecurity/recovery assurance is less central to the journal's identity than at JSSE/JAIS/IJCIP.

**Disposition:** secondary backup.

## 6. No-go / defer venues

### Computers & Security

**Disposition:** `NO_GO_CURRENT_SCOPE`

The journal states that since early 2024 it has a moratorium on submissions featuring AI/ML as a significant component. Study 7 and Study 7E contain ML as a significant scientific component. Paper 3 therefore conflicts with the current stated scope.

### CEAS Space Journal

**Disposition:** `DEFER__DO_NOT_IMMEDIATELY_RESUBMIT_WITHOUT_SEPARATE_PROCESS_REVIEW`

The strengthened Study-7E extension directly addresses the four limitations identified in the 2026-09-22 CEAS handling-editor decision, but the same Paper-3 line was just rejected and no invitation to resubmit is recorded.

This assessment does not infer a formal CEAS prohibition. It simply does not recommend an immediate return to the same journal without a separate current process/editorial review or explicit invitation.

## 7. Comparative recommendation

Current recommended order for author consideration:

1. **Journal of Space Safety Engineering — primary candidate**
2. **AIAA Journal of Aerospace Information Systems — strongest technical alternative**
3. **International Journal of Critical Infrastructure Protection — cybersecurity-first alternative**
4. IEEE Transactions on Aerospace and Electronic Systems
5. IEEE Systems Journal
6. Acta Astronautica
7. Aerospace Science and Technology

No venue is locked.

## 8. Next gate

Before any venue lock:

1. create venue-neutral R2 with the live literature corrections;
2. validate R2 scientific claims against the frozen claim ledger;
3. keep PR #168 draft/unmerged until review and CI are green;
4. obtain explicit author choice/authorization for a target venue;
5. only then perform the selected journal's full current Guide-for-Authors and submission-package audit.

Publisher submission remains separately prohibited.
