# Concise Abstract Candidate — Computers & Security

**Status:** target-specific candidate. The authoritative abstract remains `../../manuscript/00-title-abstract.md`; adopt this shorter version only if preferred by the live submission guide/portal.

Satellite cyber response must balance containment with mission continuity, command availability, and recovery supported by current trust evidence. We evaluate that post-detection trade-off in a controlled NOS3/Fortytwo/cFS software-in-the-loop experiment. A frozen 24-cell design compared fixed, ground-authorized, recovery, and deterministic rule-based mission-aware policies across synthetic cyber events, mission states, evidence conditions, and modeled contact availability. Thirty reproducible seed blocks produced 720 VALID observations.

Mission-state dependence was not supported on the predeclared P1 primary outcomes. Under modeled missed contact, the ground-authorized P6 path showed approximately 10 s increases in containment, verified-recovery, and ground/spacecraft state-divergence timing, while corresponding P7 contact contrasts were near zero. Evidence sufficiency also changed P7 behavior: in the retained compromised-update block, full evidence produced 30/30 trusted recoveries, whereas T1 omission/reduction of selected policy-visible fields produced 0/30 trusted recoveries and 30/30 recovery failures; fixed P5 retained 30/30 trusted recovery in both conditions. P4 analysis showed that the evidence reduction changed actual P7 selection/action pathways and downstream outcomes without introducing a post-hoc correctness oracle.

Condition-specific Pareto analysis across five security, mission, safety, recovery, and command-availability dimensions found that P7 could improve, match, or underperform simpler alternatives depending on conditions. A 696-observation final-commit complete-block sensitivity preserved group-level Pareto relations and primary-metric directions. The contribution is a reproducible post-detection response/recovery evaluation method and integrity-frozen outcome record, not a claim of universal autonomous-policy superiority or operational flight readiness.

Approximate word count: 229 words.
