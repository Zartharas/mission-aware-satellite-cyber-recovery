# Cover Letter Draft — Journal of Aerospace Information Systems

Dear Editors of the *Journal of Aerospace Information Systems*,

I am submitting the manuscript **“Mission-Aware Satellite Cyber Response and Trusted Recovery Under Contact and Adversarial Evidence Constraints: Two Controlled Software-in-the-Loop Studies”** for consideration as a **Regular/Full Article**.

The article addresses an aerospace information-systems and mission-assurance problem: after a cyber event has been established, a satellite response mechanism must contain unauthorized activity while preserving mission and command availability and permitting recovery only when available evidence supports a trusted state. Intermittent contact, command authority, evidence integrity, and recovery timing are therefore treated as explicit system constraints rather than background assumptions.

The manuscript reports two separately frozen controlled software-in-the-loop studies whose observations are analyzed as distinct statistical populations. Study 1 contains 720 VALID observations across 24 frozen cells and evaluates mission state, modeled contact, evidence sufficiency, trusted recovery, and condition-specific policy trade-offs. Its findings retain a null mission-state result on the predeclared primary outcomes, modeled authorization/contact delay, evidence-dependent selection and recovery behavior, and mixed Pareto relations rather than a universal policy-superiority claim.

Study 2 prospectively extends the design to omission, stale or replayed evidence, contradictory evidence, post-signature manipulation, bounded producer compromise, multiple modeled contact regimes, context ablations, and adversary-budget stress. The frozen Study-2 campaign contains 3,872 VALID observations across 85 cells with 0 INVALID attempts. Under bounded producer compromise, policy-visible evidence can remain sufficiently authenticated and current for evidence-qualified recovery while still being false relative to research-only adjudication truth. Contact and authorization conditions also expose policy-specific safety and recovery trade-offs. A separate independent implementation recomputed the frozen Study-2 numerical result families with zero mismatches.

The article is intended to fit the journal's interest in aerospace systems and software engineering, verification and validation of embedded systems, systems engineering, and safety and mission assurance. The satellite setting is materially necessary to the research question because intermittent contact, command authority, mission continuity, and constrained recovery opportunities directly shape the evaluated response behavior. The manuscript does not claim operational flight validation, radio-frequency performance, certification, or universal policy superiority.

The Study-2 benign/adversarial ambiguity block is reported conservatively. Within each frozen ambiguity family, the cause label does not change hidden truth or generated policy-visible evidence, so the resulting zero contrasts are interpreted as a structural label-invariance control rather than empirical evidence that genuinely different benign and adversarial causes are distinguishable or indistinguishable.

Both studies evaluate deterministic rule-based response mechanisms. Artificial-intelligence assistance used in manuscript preparation, source checking, documentation, and post-freeze reproducibility/audit workflow support is disclosed separately in accordance with AIAA policy. It did not generate experimental observations, select experimental treatments, or operate the evaluated response policies.

The supporting research record is publicly documented. Study 1 is archived on Zenodo as version DOI **10.5281/zenodo.22181540** and concept DOI **10.5281/zenodo.22181539**. Study 2 has a separate responsible-release-reviewed source-evidence archive on Zenodo as version DOI **10.5281/zenodo.22289114** and concept DOI **10.5281/zenodo.22289113**. The public Study-2 source ZIP was independently re-downloaded after publication and its SHA-256 matched the frozen source-evidence identity. The public research repository is https://github.com/Zartharas/mission-aware-satellite-cyber-recovery.

The research used no human participants, operational spacecraft, operational ground stations, radio-frequency transmission or interference, stolen or operational credentials, classified data, or proprietary mission telemetry. The software-in-the-loop contact and timing variables are logical research constructs and are not represented as real spacecraft, network, ground-station, or operator latency.

For dissemination transparency, the broader research program developed from doctoral work whose dissertation manuscript is archived through ProQuest. This journal article reports the separately frozen empirical studies and the additional Study-2 experimentation and analysis described in the manuscript. The dissertation relationship is disclosed rather than concealed.

I confirm that the manuscript is not simultaneously under consideration elsewhere, the work is unclassified and cleared for public release because no external classification review is required, the research received no external funding, and I have no competing financial or non-financial interests to declare.

Thank you for considering this work for the *Journal of Aerospace Information Systems*.

Sincerely,

**Aman Kumar Singh, MS, DSc**  
Independent Researcher  
The Woodlands, Texas, United States  
ORCID: 0009-0008-9752-3743  
asingh65430@ucumberlands.edu
