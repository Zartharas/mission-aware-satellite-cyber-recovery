# Rebuilt Paper 4 — Live Venue Assessment R1

**Assessment date:** 2026-09-21  
**Scope:** reviewed venue-neutral rebuilt Paper 4 / Study 8 + Study 8E  
**Assessment status:** `LIVE_VENUE_ASSESSMENT_COMPLETE__VENUE_NOT_LOCKED`  
**Source main commit:** `2ca92b67c40f2b559e4d917dcfc5b8fe966a5746`

## 1. Purpose

This record implements the explicitly authorized live venue/scope/author-guideline assessment for the scientifically reviewed venue-neutral rebuilt Paper 4.

It does **not**:

- lock a venue;
- change frozen Study 8 or Study 8E science;
- modify the manuscript;
- create a venue-specific package;
- authorize publisher submission.

The decision standard is venue fit, not predicted acceptance.

The rebuilt manuscript is a two-study systems/security paper centered on:

- post-compromise post-quantum cryptographic-state transition;
- intermittent satellite communication opportunity;
- fixed-capacity feasibility;
- minimum modeled payload-rate thresholds under external observation-opportunity timing;
- recovery-state and availability tradeoffs;
- reproducible deterministic modeling;
- explicit non-operational claim boundaries.

## 2. Current manuscript characteristics relevant to venue fit

Current working title:

**Post-Quantum Trusted Recovery Under Intermittent Connectivity: Feasibility Across Modeled Contact Budgets and Public Observation-Opportunity Timing**

Current venue-neutral manuscript:

- approximately 6,967 words;
- abstract approximately 319 words;
- 10 keywords;
- two separately governed evidence layers;
- extensive public repository/data availability;
- no physical-layer or hardware-performance claim;
- no operational-command-contact claim from SatNOGS;
- no new scientific execution required before retargeting.

## 3. Ranked current venue shortlist

### Rank 1 — International Journal of Satellite Communications and Networking

**Publisher:** Wiley  
**Current assessment:** strongest direct topical and manuscript-architecture fit  
**Venue lock:** NOT AUTHORIZED

Official scope:
https://onlinelibrary.wiley.com/page/journal/15420981/homepage/productinformation.html

Current author guidelines:
https://onlinelibrary.wiley.com/page/journal/15420981/homepage/forauthors.html

Current submission portal:
https://authors.wiley.com/journal/SAT

#### Why the rebuilt paper fits

The journal explicitly covers:

- satellite communications and broadcast systems;
- satellite networks and networking;
- performance analysis;
- interoperability;
- standards/regulation;
- network protocols;
- system-oriented research.

This maps directly onto the rebuilt paper's strongest contribution:

> a satellite-network/security systems analysis of whether and under what modeled communication conditions a successor cryptographic epoch can be restored after compromise.

Study 8 supplies controlled network/contact-budget feasibility.

Study 8E adds independently sourced public satellite observation-opportunity timing without claiming operational command-contact measurement.

That second evidence layer makes the current manuscript substantially better aligned with this journal than the earlier Study-8-only Acta submission.

#### Direct current topical precedent

The journal published:

T. Ghosh and I. Nath, "Secure Satellite Communication in the Post-Quantum Era: A Lattice-Based Cryptographic Approach," *International Journal of Satellite Communications and Networking*, 44(5), 524–543, 2026, DOI 10.1002/sat.70041.

That paper focuses on lattice-based PQC algorithm/performance/security comparison and implementation constraints.

The rebuilt Paper 4 remains distinct because it focuses on:

- post-compromise trusted-state transition;
- explicit predecessor/successor epoch semantics;
- finite intermittent opportunity;
- fixed-capacity recovery feasibility;
- minimum modeled rate under external observation timing;
- policy-state cost rather than algorithm ranking.

The journal's current 2026 issue stream also contains satellite routing/resource-allocation, optical-link, edge-intelligence, and satellite-security papers, supporting a systems/networking interpretation.

#### Current author requirements that affect this manuscript

The live Wiley guidance states:

- satellite component is mandatory;
- free-format initial submission is supported;
- abstract maximum = 250 words;
- keywords maximum = 8;
- ORCID required;
- data availability statement required;
- scripts/analysis artifacts should be publicly archived when possible;
- Graphical Table of Contents entry required;
- GTOC text <= 80 words / 3 sentences;
- short biography <= 200 words and recent photograph requested;
- numbered reference style for final journal style;
- high-resolution figures required;
- no page charge for ordinary publication.

Current Wiley journal page displays:

- acceptance rate: 8%;
- median submission-to-first-decision: 3 days.

These are publisher-reported journal metrics and must not be used as acceptance predictions.

#### Current manuscript delta

Before submission:

1. reduce abstract from ~319 words to <=250;
2. reduce keywords from 10 to <=8;
3. create required GTOC figure/text;
4. generate reader-facing figures from the already approved figure plan;
5. create short title <=70 characters;
6. create biography/photo package;
7. convert references to numbered Wiley style for final package;
8. tighten title/abstract around satellite network recovery feasibility;
9. preserve exact negative policy result and Study-8E claim boundary;
10. ensure data-availability statement points to the public frozen repository evidence.

**Scientific change required:** none.

**Primary editorial risk:** selectivity and the possibility that reviewers expect more operational network realism despite the external timing extension.

---

### Rank 2 — Computer Networks

**Publisher:** Elsevier  
**Current assessment:** strong networking/security alternative; broader than IJSCCN  
**Venue lock:** NOT AUTHORIZED

Official journal description/scope:
https://shop.elsevier.com/journals/computer-networks/1389-1286

Current journal page:
https://www.sciencedirect.com/journal/computer-networks

#### Why it fits

Current scope explicitly includes:

- communication network protocols;
- protocol specification/testing/verification;
- network security and privacy;
- authentication;
- key management;
- denial of service;
- network reliability;
- performance measurement;
- network modeling and analysis;
- discrete modeling in networking.

This aligns closely with the rebuilt manuscript's:

- deterministic transition state machine;
- contact-schedule modeling;
- cryptographic transfer burden;
- authentication/trust restoration;
- deadline/horizon-constrained feasibility;
- recovery-policy comparison.

The 2026 publication stream includes directly relevant satellite-network security work, including:

- a September 2026 survey on authentication schemes for satellite communication systems;
- LEO satellite anti-jamming routing;
- satellite network resilience/security papers.

#### Why it is not ranked first

The manuscript is satellite-specific and does not introduce a new general networking protocol deployed or benchmarked on an operational/testbed network.

Computer Networks may therefore expect a stronger general-networking contribution, implementation, or practical performance-validation story than IJSCCN.

The Study 8E timing layer improves the case substantially, but its endpoint remains modeled rate rather than measured network throughput.

#### Current manuscript delta

Likely package work:

- emphasize network protocol/state-machine contribution over broad space cybersecurity;
- add article highlights;
- add final figures;
- make network-model verification/reproducibility prominent;
- use the public frozen data/code package as a reproducibility strength;
- sharpen closest comparison to satellite authentication/network-security work.

**Scientific change required:** none for scope eligibility.

**Primary editorial risk:** reviewers may view the work as too satellite-domain-specific or insufficiently protocol-implementation-oriented.

---

### Rank 3 — International Journal of Information Security

**Publisher:** Springer Nature  
**Current assessment:** strong security/cryptography alternative; less satellite-network-specific  
**Venue lock:** NOT AUTHORIZED

Official aims and scope:
https://link.springer.com/journal/10207/aims-and-scope

Current submission guidelines:
https://link.springer.com/journal/10207/submission-guidelines

#### Why it fits

The journal's scope is:

- theory;
- applications;
- implementations of information security;
- computer security;
- applied cryptography.

It published a 2026 regular contribution on a resilient multi-layered security framework for satellite communications, demonstrating that satellite-security applications are within editorial scope.

The rebuilt manuscript contributes an applied-security systems model with:

- post-compromise trust restoration;
- cryptographic epoch-transition semantics;
- replay/stale-state controls;
- PQC transition-object burden;
- availability/exposure tradeoffs;
- reproducible finite-population evaluation.

#### Current requirements relevant to this manuscript

The current guidelines state:

- abstract = 150–250 words;
- keywords = 4–6;
- manuscript should be submitted in Springer LaTeX two-column format;
- data availability statement required for original research;
- single-blind peer review;
- source files required;
- author contribution and competing-interest information required;
- LLM use that goes beyond copy-editing should be documented in Methods or a suitable alternative section.

The current derivative already contains a generative-AI assistance statement, but it would need to be reconciled exactly with the final Springer wording if this venue were selected.

#### Why it ranks below the networking venues

The strongest novelty is not cryptographic primitive design or security proof. It is a systems/network feasibility analysis with satellite timing.

At IJIS, editors/reviewers may expect deeper information-security theory, protocol security proof, implementation benchmarking, or attack evaluation.

The manuscript is still in scope, but the center of gravity is more naturally satellite networking/systems than general information security.

**Scientific change required:** none for basic scope fit.

**Primary editorial risk:** security contribution may be judged too model/system-specific relative to the journal's broad applied-cryptography/security audience.

---

### Rank 4 — IEEE Systems Journal

**Publisher:** IEEE  
**Current assessment:** credible systems fallback; less direct topical home  
**Venue lock:** NOT AUTHORIZED

Official scope:
https://ieeesystemscouncil.org/publication/ieee-systems-journal

Current author instructions:
https://ieeesystemscouncil.org/publication/ieee-systems-journal/instructions-for-authors

#### Why it fits

The journal seeks systems-level application-oriented work on complex systems and systems-of-systems.

The rebuilt manuscript can be framed as a systems result about:

- trusted-state recovery;
- resilience;
- mission assurance;
- communications constraints;
- model-based system feasibility;
- security-state/availability tradeoffs.

#### Current format constraints

Current IEEE instructions state:

- regular paper <=12 pages at every review round;
- standard IEEE double-column format;
- at least five keywords/index terms;
- ORCID required;
- traditional publication available without mandatory OA charge;
- final pages beyond eight can incur extra-page charges up to the allowed maximum.

#### Why it ranks fourth

The manuscript would need to make its transferable systems-engineering contribution much more prominent and compress the current ~6,967-word two-study narrative into the IEEE page limit.

The paper may otherwise be seen as a specialized satellite/PQC application rather than a general systems contribution.

**Scientific change required:** none, but substantial editorial compression/reframing would be needed.

**Primary editorial risk:** desk rejection for insufficiently broad systems-level significance.

---

### Rank 5 — AIAA Journal of Aerospace Information Systems

**Publisher:** AIAA  
**Current assessment:** technically good scope fit but strategically not preferred while Paper 1 is active there  
**Venue lock:** NOT AUTHORIZED

Official scope:
https://aiaa.org/publications/journals/journal-scopes-and-content/

Current author resources:
https://aiaa.org/publications/journals/journal-author/

#### Why it fits

JAIS explicitly covers:

- aerospace computing;
- information systems;
- networks and communication systems;
- systems engineering;
- safety and mission assurance;
- aerospace-specific applications.

The rebuilt paper is within scope and avoids the physical-layer/basic-networking-hardware area JAIS excludes.

#### Current author constraints

AIAA currently states:

- full-length papers are typically ~10,000–12,000 words including figure/table-equivalent space;
- abstract = 100–200 words;
- title maximum = 12 words;
- manuscript formatting is single-column, double-spaced, 10-point type at initial preparation.

#### Strategic reason not to target it first

Paper 1 from the same research program is already active at JAIS.

Paper 4 is scientifically independent, but submitting another closely related satellite cybersecurity paper to the same journal while Paper 1 remains active creates avoidable:

- portfolio concentration;
- self-overlap scrutiny;
- editor/reviewer familiarity/confusion risk.

This is a strategic publication-management concern, not a scope defect.

---

## 4. Explicitly not recommended

### Computers & Security

Despite publishing current satellite-security articles, the journal's current scope states that cryptology has been explicitly excluded since 2006 and submissions where cryptology is a principal component will not be considered.

Because rebuilt Paper 4 is centered on post-quantum cryptographic transition objects and cryptographic epoch recovery, the desk-rejection risk is unnecessary.

**Disposition:** `NOT_RECOMMENDED__CURRENT_SCOPE_CONFLICT`

### Acta Astronautica

The prior Paper 4 manuscript was editorially rejected there.

The rebuilt paper is scientifically stronger, but immediate resubmission of the same publication line to the same venue is strategically unattractive, especially when more directly aligned satellite-network/security venues exist.

**Disposition:** `NOT_RECOMMENDED_FOR_IMMEDIATE_RETARGET`

### IEEE Transactions on Aerospace and Electronic Systems

Paper 2 is currently active there.

Scope may be plausible, but another related satellite-cybersecurity manuscript in the same venue would create avoidable overlap/portfolio complexity.

**Disposition:** `DEFER_WHILE_PAPER2_ACTIVE`

### CEAS Space Journal

Paper 3 is currently active there.

The rebuilt Paper 4 has a more direct networking/security home elsewhere.

**Disposition:** `DEFER_WHILE_PAPER3_ACTIVE`

## 5. Current comparative assessment

| Venue | Topical fit | Fit to two-study architecture | External timing layer valued | Editorial rework | Main risk |
| --- | --- | --- | --- | --- | --- |
| IJSCCN | Very high | Very high | High | Moderate | Selective; may still ask for more operational realism |
| Computer Networks | High | High | High | Moderate | May expect broader networking/protocol implementation |
| IJIS | High | Medium-high | Medium | Moderate | Security audience may expect proof/implementation/attack depth |
| IEEE Systems Journal | Medium-high | High if reframed | Medium | High | General systems significance + 12-page limit |
| AIAA JAIS | High | High | High | Moderate | Paper 1 already active there |

This table is a fit assessment, not an acceptance prediction.

## 6. Current recommendation for author decision

### Preferred next venue candidate

**International Journal of Satellite Communications and Networking**

This remains the strongest current fit after adding Study 8E.

The reason is now stronger than in the 2026-09-19 Study-8-only assessment:

1. the paper is explicitly about satellite communication opportunity and recovery feasibility;
2. Study 8E supplies an external public satellite observation-timing layer;
3. the journal explicitly covers performance analysis and network protocols;
4. the journal has current PQC/satellite precedent;
5. free-format initial submission minimizes formatting work before editorial screening;
6. the manuscript's public data/code/reproducibility package aligns well with Wiley's current data-availability expectations.

### Strongest fallback

**Computer Networks**

This is the strongest alternative if the author prefers a broader networking/security audience or if IJSCCN is declined.

### Security-oriented fallback

**International Journal of Information Security**

Use if the manuscript is deliberately reframed around post-compromise trust-state security rather than satellite-network performance.

## 7. Required next gate

This assessment does **not** lock the recommendation.

Next explicit gate:

`EXPLICIT_PAPER4_VENUE_LOCK_DECISION`

Permitted author choices include:

- lock IJSCCN;
- lock Computer Networks;
- lock IJIS;
- request deeper comparison of any two candidates;
- reject the shortlist and request additional live venue search.

After a venue is locked, a separate venue-specific derivative package should be created.

Publisher submission remains separately unauthorized.

## 8. Live sources checked

### IJSCCN

- https://onlinelibrary.wiley.com/page/journal/15420981/homepage/productinformation.html
- https://onlinelibrary.wiley.com/page/journal/15420981/homepage/forauthors.html
- https://onlinelibrary.wiley.com/doi/10.1002/sat.70041
- https://onlinelibrary.wiley.com/journal/15420981

### Computer Networks

- https://shop.elsevier.com/journals/computer-networks/1389-1286
- https://www.sciencedirect.com/journal/computer-networks
- current 2026 satellite authentication/security publications on ScienceDirect

### International Journal of Information Security

- https://link.springer.com/journal/10207/aims-and-scope
- https://link.springer.com/journal/10207/submission-guidelines
- https://link.springer.com/article/10.1007/s10207-025-01184-z

### IEEE Systems Journal

- https://ieeesystemscouncil.org/publication/ieee-systems-journal
- https://ieeesystemscouncil.org/publication/ieee-systems-journal/instructions-for-authors

### AIAA JAIS

- https://aiaa.org/publications/journals/journal-scopes-and-content/
- https://aiaa.org/publications/journals/journal-author/

### Computers & Security exclusion check

- https://shop.elsevier.com/journals/computers-and-security/0167-4048

**Assessment conclusion:** `LIVE_VENUE_ASSESSMENT_COMPLETE__IJSCCN_PREFERRED__VENUE_NOT_LOCKED`
