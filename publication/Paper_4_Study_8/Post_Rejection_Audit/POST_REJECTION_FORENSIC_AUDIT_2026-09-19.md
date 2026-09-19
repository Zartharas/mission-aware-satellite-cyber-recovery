# Study 8 / Paper 4 Post-Rejection Forensic Manuscript Audit

**Date:** 2026-09-19  
**Study:** `S8-PQC-ICR-001`  
**Rejected venue:** Acta Astronautica  
**Rejected manuscript ID:** `AA-D-26-02872`  
**Audit type:** read-only scientific/editorial forensic review  
**Scientific reexecution performed:** no  
**Statistical reanalysis performed:** no  
**Frozen science modified:** no  
**Rejected Acta package modified:** no

## Decision boundary

The Acta Astronautica decision supplied by the author is an editorial rejection with no external reviewer reports and no enumerated methodological, statistical, reproducibility, ethics, or data defect. This audit therefore does not infer an unstated scientific flaw. It examines the submitted manuscript for presentation, contribution-signaling, venue-fit, and model-significance weaknesses that could plausibly reduce editorial confidence.

## Frozen scientific facts that must remain unchanged

- Complete deterministic finite population: 3,456 modeled positions.
- All four policies: 635/864 trusted-recovery success = 73.4954%.
- Prespecified primary contrast P3 minus P1: exactly 0.000000 percentage points.
- All prespecified P3-versus-P1 strata: zero.
- Profile success: 93.7500%, 64.9306%, and 61.8056% for the three exact ML-KEM/ML-DSA pairs.
- Matched non-profile positions: success non-increasing with frozen object burden in all 1,152 positions.
- Logical slots have no physical-time conversion.
- Modeled bytes are not measured RF throughput, CPU, energy, thermal load, or flight performance.
- Same-repository separately implemented reproduction is reproducibility, not external replication.

## Forensic findings

### F1. The main policy result is scientifically valid but editorially difficult to sell

The paper's prespecified headline comparison is an exact null result. The manuscript preserves this correctly, but the contribution signal is split between the null policy finding and the much stronger profile/contact/deadline patterns. An editor can therefore read the paper as a study whose named treatment, contact-aware staging, fails to change the primary endpoint.

**Revision implication:** lead with the systems question and the separation between recovery feasibility and transition-state cost. Treat the null policy contrast as the falsification of a plausible design intuition, not as the entire contribution.

### F2. The strongest profile result can look mechanically inevitable without a sharper systems argument

The manuscript shows that larger standardized object bundles reduce deadline-feasible recovery positions under finite byte budgets. This is a real frozen result, including the 1,152-position monotonic matched check, but without a stronger explanatory frame an editor may see the result as "larger messages need more capacity."

**Revision implication:** emphasize the non-obvious part that total-cycle contact capacity was controlled while timing/partitioning changed feasibility, and that policy semantics changed state exposure without changing terminal success. The revised paper should foreground the interaction among object burden, temporal contact structure, and recovery deadline rather than object size alone.

### F3. Space relevance is carefully bounded but consequently abstract

The manuscript correctly avoids unsupported orbital, RF, ground-station, processor, energy, and flight claims. That rigor also leaves the paper with synthetic contact schedules and no physical mission trace. For a broad astronautics journal, this can make the work appear insufficiently tied to actual space-system operation.

**Revision implication:** do not fabricate operational realism. Retarget toward a venue that explicitly values systems modeling, systems engineering, security, resilience, or satellite-network analysis. In the manuscript, make the abstraction an intentional controlled experiment rather than an incomplete mission simulation.

### F4. Contribution hierarchy is too diffuse

The current manuscript contains several defensible contributions: exact finite factorial evaluation, controlled equal-total-capacity contact regimes, a negative contact-aware-policy result, profile burden effects, transition-state tradeoffs, and same-repository independent reconstruction. These are dispersed across the introduction and discussion rather than presented as a compact ranked contribution set.

**Revision implication:** add a concise contribution paragraph with three to four contribution claims, each tied to a frozen result and a claim boundary.

### F5. The abstract is information-dense and reads like a technical closeout

The abstract includes extensive factorial detail, multiple exact percentages, methodological caveats, reproduction wording, and several endpoint classes. It is accurate but cognitively expensive before the reader understands the design question.

**Revision implication:** retain the null result and main quantitative findings but reduce setup detail. State the problem, design, central null result, strongest feasibility result, and systems implication in a cleaner sequence.

### F6. The related-work section is responsible but not sufficiently comparative

The manuscript cites current PQC-for-space, crypto-agility, CCSDS, and satellite-security work, but it mostly summarizes adjacent work. It does not provide a compact comparison that makes the paper's exact gap unmistakable.

**Revision implication:** add a prior-work comparison table or tightly structured paragraph comparing dimensions such as post-compromise transition, intermittent contact, exact standardized object sizes, explicit deadline, policy-state semantics, stale-epoch safety, and reproducibility. Do not claim novelty for PQC in satellites, crypto agility, or bandwidth overhead by themselves.

### F7. The paper needs a clearer analytical narrative around equal total capacity

The equal-65,536-byte full-cycle design is one of the paper's strongest controls. It demonstrates that temporal placement and partitioning of capacity matter even when complete-cycle total capacity is identical. This result is currently present, but not elevated enough.

**Revision implication:** make controlled equal-capacity temporal structure a central experiment-design contribution, with a figure or table that makes the contrast immediately visible.

### F8. The policy-tradeoff result is useful but secondary metrics need a stronger systems interpretation

P0, P1, P2, and P3 redistribute predecessor exposure, control unavailability, overlap, resource use, attempts, and failure classification. The paper reports this correctly, but the manuscript could more clearly explain why a systems engineer would evaluate these state costs separately from terminal recovery success.

**Revision implication:** reorganize the discussion around two axes: feasibility and transition-state cost. Avoid any global ranking.

### F9. The conclusion is accurate but somewhat repetitive

The conclusion repeats several numeric results already given in the Results and Discussion.

**Revision implication:** shorten the conclusion and emphasize the general systems lesson and the exact scope boundary.

## Revision architecture

A new retargeted manuscript should be a new venue-specific editorial projection. Do not overwrite:

- `publication/study8/` frozen source package;
- `S8-ACTA-PKGFREEZE-002`;
- the rejected Acta manuscript, figures, cover letter, highlights, or checksums.

Recommended editorial architecture:

1. sharper title centered on trusted rekeying/recovery under intermittent contact;
2. shorter abstract with the null result visible;
3. introduction with explicit gap and compact contributions;
4. related-work comparison matrix;
5. methods that foreground equal-total-capacity timing control and finite-population logic;
6. results organized as:
   - policy null result,
   - object-burden feasibility boundary,
   - equal-capacity temporal-contact effect,
   - transition-state cost redistribution;
7. discussion organized around feasibility versus state cost;
8. limitations retained without apology or unsupported extrapolation;
9. shorter conclusion.

## Scientific changes not authorized by this audit

This audit does not authorize:

- new observations;
- a new factorial population;
- post-hoc endpoint changes;
- new inferential statistics;
- conversion of slots into seconds;
- use of real mission claims without new evidence;
- adding physical RF/orbit/processor measurements as if they belonged to Study 8;
- replacing the exact null primary result;
- altering the rejected Acta package.

If a future analytical extension is desired, it must be separately designed, authorized, executed, and identified as a new evidence layer rather than silently inserted into the frozen Study 8 population.

## Audit disposition

**MANUSCRIPT REVISION IS WARRANTED. FROZEN SCIENCE REOPENING IS NOT WARRANTED BY THE ACTA DECISION.**

The next gate is venue retarget selection followed by a new venue-specific manuscript revision from frozen Study 8 evidence.
