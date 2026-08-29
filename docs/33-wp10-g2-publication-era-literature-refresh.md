# WP10-G2 Publication-Era Literature Refresh

**Date:** 2026-08-29  
**Status:** Targeted publication-era novelty refresh complete  
**Purpose:** Revalidate the WP1 novelty boundary after the empirical P1–P5 findings were locked.

## Scope and method

This is a targeted August 2026 refresh of the focused WP1 search, not a claim of exhaustive systematic-review coverage. The existing `docs/06-literature-matrix.csv` already contains 30 directly relevant sources spanning Mission Aware cybersecurity, spacecraft FDIR/autonomy, satellite cyber testbeds/datasets, cyber-safe mode, cyber-resilience, attack recovery, and mission assurance.

The refresh specifically searched for newer or adjacent work that could invalidate the remaining contribution by already providing a controlled comparative satellite cyber-response/recovery experiment with the same combination of:

- multiple response/recovery policies;
- spacecraft mission context;
- intermittent/limited contact;
- degraded or manipulated policy-visible evidence;
- separate cyber, mission, safety, rejection, and trusted-recovery outcomes;
- condition-specific multi-objective/Pareto comparison;
- negative cases where adaptive response is equivalent or worse.

No directly equivalent study was identified in this targeted refresh. This is evidence supporting a **narrow novelty claim**, not proof that no such work exists anywhere.

## Publication-era adjacency review

### 1. Mission Aware cybersecurity is current prior art

Bakirtzis et al., *Mission Aware Cyber-Physical Security*, Systems Engineering (2026), DOI `10.1002/sys.70018`, reiterates Mission Aware as a systems-theoretic, mission-centric analysis that traces cyberattack evidence to mission requirements and critical system elements.

**Implication:** The manuscript must treat Mission Aware as the theoretical/design foundation. It cannot claim that mission-centric cyber analysis is new, and the P1 null result must not be hidden to preserve the framework narrative.

### 2. Cyber-safe recovery and adaptive response concepts are already explicit in SPARTA

Current SPARTA/NASA best-practice mappings include cyber-safe mode, recovery/reconstitution to known state, integrity-protected gold images, recovery timelines, automated safeguards, and adaptive response concepts including reinforcement-learning agents constrained by trusted safety mechanisms.

Relevant public resources include:

- `https://sparta.aerospace.org/countermeasures/CM0044`
- `https://sparta.aerospace.org/countermeasures/nasabpg/MI-MA-02`

**Implication:** Cyber-safe mode, trusted-image recovery, autonomous response, and adaptive policy concepts are not novel contributions. The paper contributes controlled comparative evidence about when response choices help or hurt under the frozen conditions.

### 3. Satellite incident-response practice now explicitly recognizes contact-window and mission/security trade-offs

AWS Public Sector published *An incident response playbook for satellite operations on AWS (Part-2): Automated response and recovery* in 2026. It explicitly discusses containment actions that may wait for orbital passes, mission-continuity/security trade-offs, recovery of remotely inaccessible endpoints, automated runbooks, and human approval gates for high-impact satellite actions.

Source: `https://aws.amazon.com/blogs/publicsector/an-incident-response-playbook-for-satellite-operations-on-aws-part-2-automated-response-and-recovery/`

**Implication:** The paper cannot claim that contact-constrained satellite incident response or mission/security trade-offs are newly recognized operational problems. Its differentiator is the reproducible experiment with predeclared policies, endpoints, repeated seeds, evidence degradation, and observed conditional outcomes.

### 4. Time/mission context is an active satellite-security research direction

Liu and Sun, *Temporal Risk on Satellites* (arXiv:2608.20575, August 2026), argues that the same exploit can have different consequences across operationally meaningful mission time windows and proposes time-indexed risk matrices rather than one static score.

**Implication:** Time/mission context itself is not unique. However, that work is risk assessment, not a controlled response-policy/recovery comparison with the outcome structure used here. The P1 null finding also means this paper must not claim that mission context necessarily changes response outcomes.

### 5. Onboard autonomous cyber detection is advancing rapidly

Le, Tran, and Le, *TinyML-Driven Cybersecurity for Autonomous Spacecraft: Latency-Accuracy Analysis for SPARTA RF and Cyber Threat Detection* (arXiv:2606.05779, June 2026), evaluates lightweight onboard models for cyber/RF threat detection and focuses on detection accuracy and inference latency.

**Implication:** Onboard cyber autonomy and low-latency detection are active prior art. The present study remains distinct by focusing on response/recovery policy consequences after a modeled event rather than detector performance.

### 6. Broad space-cyber reviews continue to identify recovery and real-time impact gaps

Mattar et al., *What is Cybersecurity in Space?* (arXiv:2509.05496, 2025), maps open research gaps including recovery methods, onboard intrusion detection, trusted supply chains, and real-time impact monitoring.

**Implication:** Recovery remains recognized as an open area, but a broad review does not establish novelty for any particular recovery mechanism. The present contribution should be framed as one controlled empirical method addressing a subset of that gap.

### 7. Spacecraft FDIR under communication delay remains mature prior art

The 2026 JUICE spacecraft-system design literature describes substantial onboard FDIR/autonomy because of long communication delays and periods without contact, including recovery to operational mode and safe-mode fallback until ground intervention.

Reference: *The JUICE Spacecraft System Design*, Space Science Reviews (2026), DOI `10.1007/s11214-026-01289-4`.

**Implication:** Ground-contact delay, autonomous fault response, and safe mode are established spacecraft-engineering concerns. The cyber-specific experimental distinction remains adversarial evidence/authorization conditions plus cyber/mission/trusted-recovery comparative outcomes.

## What the refresh does to the novelty claim

### Claims that are too broad and should not appear

Do not claim that this study is the first to:

- make spacecraft cybersecurity mission-aware;
- use autonomous cyber response on spacecraft;
- consider intermittent contact in spacecraft recovery;
- use safe mode or trusted-image rollback;
- compare mission and security trade-offs in principle;
- use Pareto analysis in satellite engineering;
- build a satellite cybersecurity testbed or NOS3/cFS experiment;
- study onboard cyber detection.

### Defensible remaining contribution

The targeted refresh supports the following narrower contribution statement:

> We present a reproducible controlled software-in-the-loop experiment that compares multiple satellite cyber-response and trusted-recovery policies under frozen event, mission-state, evidence, and contact conditions, reports security and mission outcomes separately, and retains conditions in which the mission-aware policy is beneficial, equivalent, or worse than simpler alternatives.

The distinguishing elements are the **joint experimental design and evidence discipline** rather than any single mechanism.

## Empirical findings that strengthen the literature-facing story

- **P1 null:** Mission-state dependence should be presented as an empirical non-result, which prevents the paper from overfitting its theoretical framing.
- **P2 supported:** A single modeled missed-contact window produces a clear timing penalty for ground-authorized P6 but not P7, giving controlled evidence for a widely discussed operational constraint.
- **P3/P4 supported with boundaries:** Policy-visible evidence quality materially changes P7 recovery and selection pathways, while the narrower restoration-without-verification mechanism and an objective “incorrect action” oracle are absent.
- **P5 conditional:** Adaptive response is neither universally superior nor uniformly poor; dominance, equivalence, and disadvantage are all retained. This satisfies the original requirement for negative cases and multi-objective reporting.

## Publication-strength novelty language

### Abstract/Introduction-safe version

> Prior work establishes mission-centric cybersecurity, spacecraft FDIR/autonomy, cyber-safe recovery, satellite cyber testbeds, and automated incident-response concepts. What remains less developed is reproducible empirical comparison of alternative cyber-response and trusted-recovery policies under spacecraft-specific contact and evidence constraints. This study addresses that narrower gap through a frozen software-in-the-loop experiment with separate security, mission, safety, rejection, and verified-recovery outcomes.

### Stronger wording that should be avoided

Avoid “first,” “first-ever,” “novel mission-aware architecture,” “novel cyber-safe mode,” or “proves mission-aware response is superior” unless a later journal-specific systematic search independently supports such wording.

## Literature-refresh disposition

- Existing literature matrix size: `30` directly relevant entries — prior WP1 minimum met.
- Independent reviewer challenge: present in `docs/09-wp1-reviewer-challenge-and-final-gap.md`.
- Threat-model red-team challenge: present in `docs/12-threat-model-red-team-review.md`.
- Publication-era targeted refresh: **complete as of 2026-08-29**.
- Directly equivalent controlled comparative experiment found in this refresh: **none identified**.
- Novelty confidence: **defensible but deliberately narrow**.
- Final bibliographic metadata/license verification remains required when the manuscript reference list and WP11 release package are assembled.