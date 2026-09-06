# I. Introduction

Cyber recovery in satellite systems can require trust decisions under communication gaps, constrained postlaunch access, and mission-continuity pressure [1]. Recovery is therefore not only a restoration problem but also a qualification problem: before a policy permits a recovery path, it must decide whether the available runtime evidence, the producers supplying that evidence, and the recovery artifact are sufficiently trustworthy for the modeled decision.

Prior work already establishes the main mechanisms used here. Satellite research examines internal trust boundaries and testable cyber-resilience requirements [2], [3], while SPARTA describes integrity-protected trusted recovery baselines [4]. RATS distinguishes evidence from appraisal and treats freshness as an explicit concern [5], with current work also considering multiple-Verifier composition [6]. Quorum systems formalize trust and failure assumptions [7], [8], and recent satellite trusted-execution work uses Byzantine-tolerant endorsement quorums [9]. Software-supply-chain systems provide provenance, signed metadata, hashes, controlled build processes, and source assurance [10], [11], [12], while SLSA also documents limits involving intentionally malicious producers [13]. This paper does not claim novelty for those mechanisms.

The narrower question is: **what residual trust boundary remains when a recovery-qualification policy can satisfy its visible checks while a relevant research-only authorization or correctness state differs?** Runtime evidence can be authentic and fresh but semantically false if a trusted producer is compromised. Multiple producers can reduce dependence on one source, but the boundary then depends on vote count, provenance assumptions, and producer availability. Artifact assurance can close several integrity and process failures while still depending on a higher-level assumption about approved source correctness.

Three separately frozen deterministic studies examine those boundaries without forming one integrated experiment or pooled population. Study 3 evaluates 1,380 temporal trajectories under continuous and synthetic intermittent contact. Study 4 evaluates 4,608 exact rule-by-subset observations across 18 vote and synthetic provenance-domain rules. Study 6 evaluates 420 exact observations across six artifact states, six assurance gates, and benign assurance-signal unavailability. Each study retains its own unit, interventions, endpoints, and model boundary.

The research questions are:

**RQ1:** Under the frozen continuous and intermittent-contact schedules, how do truthful evidence, post-signature modification, and false but validly signed claims from a compromised trusted producer affect the duration and recurrence of false recovery qualification across the Study-3 policy semantics?

**RQ2:** When recovery authorization is supported by multiple modeled evidence producers, how do absolute vote thresholds and synthetic provenance-domain requirements change the first and systematic failure boundaries for unsafe qualification under producer compromise and false-conservative qualification under benign producer loss?

**RQ3:** When the recovery artifact is subjected to progressively composed assurance requirements, which prespecified incorrect artifact states remain qualified, and what benign qualification loss results when required assurance signals become unavailable?

A systems-level synthesis then asks how these independently measured boundaries relate across temporal runtime evidence, producer composition, and recovery-artifact assurance. The synthesis is qualitative and mechanism based; it does not estimate a common treatment effect, pooled success rate, or end-to-end recovery probability.

The paper makes four bounded contributions:

1. **Temporal qualification boundary.** Study 3 separates a short truthful pre-onset cache boundary from false qualification caused by a compromised trusted producer that continues to generate fresh and validly signed false evidence, while the post-signature-manipulation control distinguishes semantic producer failure from invalidly signed alteration.
2. **Producer-composition boundary.** Study 4 provides an exhaustive first-versus-systematic failure map across 18 vote and provenance-domain rules, including conditional benefits, benign-loss costs, and null provenance effects.
3. **Artifact-assurance boundary.** Study 6 maps the incorrect artifact states that survive progressively composed assurance gates and the corresponding rejection of the objectively correct baseline under benign signal loss.
4. **Residual-boundary synthesis.** Across the three studies, stronger evidence composition closes or narrows specified failure pathways without automatically making policy-visible evidence equivalent to hidden or objective truth.

The interpretation remains model bounded. Only Study 3 models contact, and logical time is not operational spacecraft time. Study 4's provenance domains are synthetic, and Study 6 is a Boolean assurance model rather than a real supply-chain experiment. The studies do not measure flight safety, mission availability, RF performance, computing cost, or operational recovery probability; Section VIII states the complete validity and aerospace interpretation limits.

Section II positions the work against prior art. Section III defines the common qualification abstraction while preserving study separation. Sections IV through VI present the three studies, Section VII synthesizes their residual boundaries, Section VIII addresses validity and future evaluation, and Section IX concludes.
