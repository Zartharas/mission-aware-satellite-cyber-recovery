# Study 8 Post-Rejection Forensic Manuscript Audit

**Audit date:** 2026-09-19  
**Study:** `S8-PQC-ICR-001`  
**Roadmap publication label:** Paper 4  
**Rejected venue:** Acta Astronautica  
**Acta manuscript ID:** `AA-D-26-02872`  
**Audit disposition:** `REVISION_RECOMMENDED_NO_SCIENCE_REOPENING_REQUIRED`

## Scope and authority

This is a publication-layer forensic audit performed after the Acta Astronautica editorial rejection recorded on 2026-09-19. It evaluates the exact frozen Study 8 science, target-neutral manuscript, Acta editorial projection, current literature position, and live venue fit.

**Scope disambiguation:** this audit concerns **roadmap Paper 4 / Study 8**. It does not reopen scientific **Study 4 / `S4-MPQ-001`**, which is already consumed by the submitted Paper 2 manuscript at IEEE Transactions on Aerospace and Electronic Systems and remains frozen.

This audit does not rerun the Study 8 model, recompute the statistical analysis, change the frozen population, change any endpoint, rescue the null primary result, or modify the rejected `S8-ACTA-PKGFREEZE-002` package.

Frozen scientific authorities remain:

- canonical observations SHA-256: `cfc65b6663be4e9f17a00ed102730f8642efcbbd844045acce032ff09a0bcabf`
- primary/independent findings SHA-256: `26a8ac4d1039917323e75a294775dd14a2b563adb12a5d2fcdb47ce8f15c992e`
- interpretation-audit SHA-256: `620827f83fb566ff6ceae1b66c8f51f61ef8e5bbdabbb1c4b5a48b5187a82413`
- frozen primary contrast: `P3 - P1 = 0/1 = 0.000000 percentage points`

## Editorial-decision evidence

The Acta decision states only that the problems addressed were potentially interesting to its readership but that the manuscript did not meet the journal's required quality standard.

No external reviewer report was supplied. No specific methodological, statistical, reproducibility, ethics, data, or scope defect was enumerated. No revision was invited.

Therefore this audit does not attribute any specific weakness below to the Acta editor. The items below are independent publication-quality and venue-fit findings intended to reduce avoidable risk in the next submission.

## Forensic findings

### F1. Contribution hierarchy is weaker than the underlying result structure

The submitted title and abstract foreground contact-aware cryptographic agility and the P3-versus-P1 comparison. That comparison is important because it was prespecified, but it is exactly null overall and in every prespecified stratum.

The stronger publication thesis is broader and more informative:

1. the frozen common object bundle and scheduler define a deadline/contact feasibility envelope;
2. standardized object burden, temporal contact placement, and deadline materially change which modeled positions are feasible;
3. within that common feasibility envelope, policy semantics do not change the terminal success proportion;
4. policy still changes predecessor exposure, control unavailability, overlap, attempts, transfer use, and failure classification.

**Revision action:** move from a "contact-aware policy" headline to a "feasibility versus transition-state cost" headline. Preserve the null result prominently, but do not make the null policy comparison the only apparent reason the paper exists.

### F2. The mechanism behind the null result needs earlier explanation

All four policies use the same required object bundle and the same deterministic priority scheduler. P3 changes commit gating rather than creating new contact capacity or reducing the cryptographic material required for trust restoration.

The manuscript explains this in the Discussion, but an editor can encounter the exact-zero policy result before the mechanism is made sufficiently explicit.

**Revision action:** state near the end of the Introduction and at the start of Results/Discussion that the design intentionally isolates acceptance/revocation semantics while holding the transferred object bundle and scheduler constant. The exact null then becomes an interpretable systems result: state-management semantics can redistribute costs without enlarging the frozen terminal feasible set.

This is a restatement of the frozen design and observed findings, not a new statistical analysis.

### F3. Novelty is defensible but currently too diffuse

The current manuscript correctly refuses novelty claims for PQC in satellites, crypto agility, hybrid migration, or large PQ artifacts by themselves. However, the novelty signal is spread across several paragraphs and is partly expressed as a list of what the work is not.

The current field moved quickly in 2025-2026:

- NIST CSWP 39-upd1 formalizes crypto agility as replacing/adapting cryptography while preserving security and ongoing operations.
- GSMA PQ.07 treats PQC migration in non-terrestrial networks as an active systems problem.
- Mähn, Müller, and Zielinski define crypto agility for space systems.
- Ghosh and Nath analyze lattice-based PQC for satellite communication.
- Kim surveys PQC algorithms, implementation, protocol adaptation, hybrid migration, and crypto agility for space systems.
- Recent experimental work evaluates post-quantum WireGuard/IPsec over LEO-like satellite conditions.
- Eichen et al. discuss PQ authentication and key-management pressure in bandwidth-constrained and non-terrestrial networks.
- Earlier DTN literature already identifies key management and key exchange under intermittent connectivity as a distinct problem.

**Revision action:** express one narrow novelty statement in the Introduction:

> The contribution is not another algorithm benchmark. It is a complete finite model of post-compromise cryptographic state transition that separates terminal deadline feasibility from the security-state and availability costs incurred while standardized post-quantum transition objects traverse intermittent satellite contact opportunities.

This wording must remain bounded to the modeled design.

### F4. The literature base should be strengthened

The Acta package contained 17 references. Those references were individually relevant, but the retargeted manuscript should better connect three literatures that currently appear only partially integrated:

1. satellite/DTN key management under intermittent connectivity;
2. post-quantum satellite/network protocol overhead and migration;
3. crypto-agility/state-transition and post-compromise recovery semantics.

**Revision action:** add directly relevant sources, especially peer-reviewed or standards sources, without turning the paper into a survey. Candidate additions include established DTN key-management/key-exchange work and 2026 PQ satellite-protocol evaluation. Every added source must be verified before manuscript freeze.

### F5. Space specificity is scientifically bounded but editorially vulnerable

The strict abstraction boundary is a strength for internal validity: logical slots are not physical time, contact capacities are synthetic byte opportunities, and CPU/RF/orbit/energy behavior is intentionally excluded.

For a broad astronautics venue, however, the same abstraction can make the work appear insufficiently tied to a concrete aerospace implementation.

**Revision action:** target a venue where satellite-network protocol modeling and performance analysis are explicitly in scope. Frame the contact process as a satellite-network planning abstraction, not a spacecraft performance model. Do not manufacture orbital realism or physical-link measurements that the study does not contain.

### F6. Results presentation should explain mechanisms before enumerating factors

The exact counts are well preserved, but the reader encounters many factorial details early. The strongest interpretation can be made easier to follow by organizing Results around three questions:

1. **What determines terminal feasibility?** Object burden, contact placement, deadline.
2. **What did policy not change?** The terminal success set under the frozen common-bundle/common-scheduler design.
3. **What did policy change?** Exposure, unavailability, overlap, transfer/attempt burden, and failure classification.

**Revision action:** restructure section headings and transitions around those three questions while retaining every frozen result.

### F7. The manuscript should distinguish model implications from deployment recommendations more visibly

The manuscript already contains strong limitations. The next version should move the deployment boundary closer to each design implication rather than relying primarily on a later limitations section.

**Revision action:** use phrases such as "within this model," "for a transition with the frozen common object bundle," and "this supports modeling X as an input" at the point where implications are discussed.

### F8. No scientific reopening is justified by the rejection

The Acta letter identifies no scientific defect, and this audit found no contradiction with the frozen evidence or claim traceability.

**Decision:** do not rerun the 3,456-position campaign, change endpoints, add post-hoc inference, replace the P3 primary contrast, or alter the frozen statistical findings for publication purposes.

A future physical-contact, protocol-framing, hardware, RF, or independent-laboratory validation effort would be a new study with its own protocol and evidence identity.

## Recommended revision thesis

The retargeted Paper 4 should be built around:

**Post-compromise post-quantum transition under intermittent satellite contact has two separable design questions: whether the required transition material can reach a trusted terminal state before a deadline, and what security-state/availability costs are incurred while attempting that transition. In the frozen model, object burden, contact placement, and deadline change feasibility, while the four tested policy semantics leave terminal success unchanged but redistribute transition-state costs.**

This thesis preserves the exact null primary result rather than minimizing it.

## Candidate retarget title

**Post-Compromise Post-Quantum Cryptographic Transition Under Intermittent Satellite Contact: Feasibility and State-Cost Tradeoffs**

The title is a publication-layer candidate only. It does not rename the scientific experiment.

## Recommended next gate

Proceed to a venue-specific revision only after a named retarget venue is explicitly locked.

The retargeted package may change:

- title and abstract;
- introduction/contribution hierarchy;
- related-work synthesis and verified references;
- results organization and explanatory prose;
- discussion structure;
- publication-layer tables/figures or a new explanatory schematic derived only from already frozen definitions/results;
- journal-specific formatting and declarations.

The retargeted package may not change:

- frozen science;
- population;
- prespecified endpoint or P3-versus-P1 primary contrast;
- canonical counts/proportions;
- claim boundary;
- scientific provenance identities;
- the rejected Acta package retained as historical evidence.

