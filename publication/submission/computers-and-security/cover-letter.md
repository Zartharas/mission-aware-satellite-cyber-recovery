# Cover Letter Draft — Computers & Security

Dear Editors of *Computers & Security*,

I am submitting the manuscript **“Mission-Aware Satellite Cyber Response and Trusted Recovery Under Contact and Adversarial Evidence Constraints: Two Controlled Software-in-the-Loop Studies”** for consideration as a **Full Length Article**.

The paper addresses a practical cyber-resilience problem for satellite systems: a defensive action can suppress unauthorized activity yet impose mission, command-availability, or recovery costs, while evidence that appears authenticated and current may still be insufficient to establish objective correctness under bounded compromise. Rather than propose another detector or a universal autonomy claim, the article evaluates deterministic response/recovery policies under explicit mission, contact, authorization, evidence, and adversary assumptions.

The manuscript reports two **separately frozen** empirical studies whose observations are not pooled. Study 1 contains 720 VALID observations across 24 frozen cells and evaluates mission-state, modeled-contact, evidence-sufficiency, trusted-recovery, and condition-specific multi-objective policy effects. Its findings include a retained null mission-state result, modeled authorization/contact delay, evidence-dependent selection/recovery behavior, and mixed Pareto relations rather than universal mission-aware superiority.

Study 2 prospectively generalizes the evidence and contact problem. Its 85-cell campaign contains 3,872 VALID observations with 0 INVALID attempts and evaluates omission, stale/replay evidence, contradiction, post-signature manipulation, bounded producer compromise, multiple modeled contact regimes, context ablations, and adversary-budget stress. One important result is that policy-visible evidence can remain authenticated/current enough for evidence-qualified recovery while being false relative to research-only adjudication truth under the bounded compromise model. The Study-2 analysis produced 162 primary paired contrasts and 432 prespecified secondary contrasts, and an independent implementation recomputed the frozen result tables with zero mismatches.

The Study-2 Block-C benign/adversarial contrasts are reported conservatively. The cause label does not change hidden truth or generated policy-visible evidence within each frozen ambiguity family, so the 54 zero contrasts are a **structural label-invariance/control result**, not empirical evidence that the policies can or cannot distinguish genuinely different benign and adversarial causal mechanisms.

Both studies use **deterministic rule-based response mechanisms**, not AI/ML decision models. This distinction is material to the journal's current scope. OpenAI ChatGPT use in manuscript preparation, source checking, consistency review, and reproducibility/code work is disclosed separately under Elsevier policy and is not represented as an experimental security mechanism.

I believe the article fits *Computers & Security* because its center of gravity is the post-detection security response/recovery decision problem: how authorization/contact dependencies, evidence integrity, and bounded compromise change containment, recovery, mission availability, and command availability. The satellite environment supplies meaningful cyber-physical constraints, while the method and limitations remain relevant to broader cyber-resilience and CPS-security readers.

The Study-1 raw campaign and integrity package are publicly archived on Zenodo (version DOI **10.5281/zenodo.22181540**; concept DOI **10.5281/zenodo.22181539**). That record is explicitly the Study-1 evidence-of-record. The Study-2 Phase-7 statistical result artifact and cryptographic provenance are retained in the public repository; before actual submission, the underlying Study-2 source-evidence package will complete responsible-release review and receive its own durable DOI-bearing archive. The manuscript will not claim a Study-2 DOI until that publication exists.

The public repository is https://github.com/Zartharas/mission-aware-satellite-cyber-recovery. Study-1 reproducibility retains the explicitly reconstructed WP10 statistical implementation and its historical-source limitation. Study-2 retains the frozen analyzer identity, canonical Phase-7 result/provenance records, and a separate independent reproduction audit.

The research used no human participants, no operational spacecraft or ground station, no RF transmission or interference, no operational credentials, and no classified or proprietary mission telemetry. Modeled contact and logical SIL timing are not presented as real ground-station, network, or operator latency. The paper makes no flightworthiness or certification claim and reports no weighted global policy score or global policy ranking.

For prior-dissemination transparency, the broader research program developed from doctoral work whose dissertation manuscript is archived through ProQuest. This submission is a journal research article built around the controlled empirical studies, frozen evidence, additional Study-2 experimentation, and journal-specific analysis described in the manuscript. The dissertation relationship is disclosed rather than treated as undisclosed prior dissemination.

I confirm that the manuscript is not simultaneously under consideration elsewhere and that I have no competing financial or non-financial interests to declare. The CRediT statement and generative-AI declaration have been reviewed and approved, and I have no acknowledgments to add.

Thank you for considering this work.

Sincerely,

**Aman Kumar Singh, MS, DSc**  
Independent Researcher  
The Woodlands, Texas, United States  
ORCID: 0009-0008-9752-3743  
asingh65430@ucumberlands.edu
