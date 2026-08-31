# Mission-Aware Satellite Cyber Response and Trusted Recovery Under Contact and Evidence Constraints: A Controlled Software-in-the-Loop Study

## Abstract

Satellite cyber response must balance containment of unauthorized activity against continued mission service, command availability, and recovery to a state that can be supported by current trust evidence. This study evaluates that trade-off using a controlled software-in-the-loop experiment built on a NOS3/Fortytwo and cFS-based research environment. A frozen 24-cell design compared fixed, ground-authorized, recovery, and **deterministic rule-based mission-aware** response policies across synthetic cyber events, mission states, evidence conditions, and a modeled missed-contact condition. Thirty reproducible seed blocks produced 720 VALID observations; nine additional INVALID attempts were retained as provenance but excluded from statistical membership under predeclared validity rules. Primary outcomes were analyzed separately rather than collapsed into a weighted score.

Mission-state dependence was not demonstrated on the predeclared P1 primary outcomes. In contrast, one modeled missed-contact window increased ground-authorized P6 containment RMST by 10.0831 s (95% seed-block bootstrap interval 9.8304–10.3735), verified-recovery RMST by 10.4246 s (9.6567–11.3598), and ground/spacecraft state-divergence duration by 10.0676 s (9.8438–10.3260), while the corresponding P7 contact contrasts were approximately zero. Evidence quality was also consequential: in the retained compromised-update block, P7 changed from 30/30 trusted recoveries under full evidence to 0/30 trusted recoveries and 30/30 recovery failures under degraded policy-visible evidence, whereas fixed P5 retained 30/30 trusted recovery in both evidence conditions. Semantic analysis showed that degraded evidence changed actual P7 effective-policy/action pathways and downstream mission/recovery outcomes without requiring a post-hoc correctness oracle.

Condition-specific Pareto analysis across unauthorized-effect completion, mission completion, safety-invariant violations, verified-recovery RMST, and legitimate-command rejection found P7 on the point-estimate Pareto front in five of nine matched groups, but three were principally equivalence/delegation cases and P7 was point-dominated in four groups. A final-commit complete-block sensitivity using 29 seeds and 696 observations preserved all group-level Pareto relations and primary-metric directions. These findings support a bounded conclusion: mission-aware response can improve, match, or underperform simpler alternatives depending on contact and evidence conditions. The contribution is therefore a reproducible comparative evaluation method and integrity-frozen outcome record, not a claim of universal autonomous-policy superiority or operational flight readiness.

## Keywords

satellite cybersecurity; mission-aware cybersecurity; cyber resilience; trusted recovery; spacecraft autonomy; software-in-the-loop; NOS3; cFS; cyber incident response; Pareto analysis; evidence-aware response

## Running-title candidate

Mission-Aware Satellite Cyber Response and Trusted Recovery

## Manuscript-status note

This title/abstract is target-neutral. Journal-specific length, structured-abstract headings, keyword count, author information, funding declarations, and graphical-abstract requirements remain submission-format tasks rather than scientific-analysis tasks.
