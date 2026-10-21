# Paper 4 / Study 8 Live Next-Venue Shortlist

**Date checked:** 2026-09-19  
**Status:** `LIVE_SHORTLIST_COMPLETE__VENUE_NOT_LOCKED`  
**Scope:** retargeting the frozen Study 8 evidence after Acta Astronautica rejection

## Decision standard

The goal is not to find an "easy" journal. Acceptance cannot be predicted.

The goal is to improve the probability of a fair editorial assessment by matching the paper to a venue that naturally publishes:

- satellite communications and networking;
- protocol/system modeling;
- cybersecurity;
- performance or feasibility analysis;
- post-quantum or cryptographic-transition work.

The exact Acta manuscript should not be resubmitted unchanged.

## Recommended primary candidate: International Journal of Satellite Communications and Networking

**Publisher:** Wiley  
**Recommendation:** strongest current topical fit, subject to author venue-lock approval

Official scope states that the journal covers the theory, practice, and operation of satellite systems and networks and explicitly includes satellite networks, performance analysis, interoperability, standards, and network protocols.

Official scope:
https://onlinelibrary.wiley.com/page/journal/15420981/homepage/productinformation.html

Author guidelines:
https://onlinelibrary.wiley.com/page/journal/15420981/homepage/forauthors.html

### Why the fit is stronger than Acta for this paper

Study 8 is fundamentally a satellite-network/system transition model:

- finite contact opportunities;
- protocol-state progression;
- transition-object byte burden;
- deadline-constrained recovery;
- network timing and capacity partitioning;
- security-state tradeoffs.

The work does not depend on propulsion, structures, orbital dynamics, spacecraft hardware benchmarking, or flight validation. A satellite communications/networking journal therefore aligns more directly with what the study actually measures.

### Direct topical precedent

The journal published:

T. Ghosh and I. Nath, "Secure Satellite Communication in the Post-Quantum Era: A Lattice-Based Cryptographic Approach," International Journal of Satellite Communications and Networking, vol. 44, no. 5, pp. 524-543, 2026. DOI: 10.1002/sat.70041.

That paper addresses satellite PQC from an algorithm/performance/security perspective. Study 8 remains distinguishable because it evaluates post-compromise trusted-state transition under finite intermittent contact rather than ranking cryptographic implementations.

The journal has also published satellite security, physical-layer security, routing, resource allocation, and system-level simulation studies.

### Current submission requirements relevant to Paper 4

The live Wiley guidance currently states:

- free-format initial submission is supported;
- the paper must contain a satellite component;
- abstract up to 250 words;
- up to eight keywords;
- ORCID required;
- graphical table-of-contents entry required;
- author biography up to 200 words and recent photograph requested;
- figures must be publication quality;
- data availability, funding, conflicts, and other integrity statements may be required.

The journal page currently displays an 8% acceptance rate and a 3-day median submission-to-first-decision metric. These publisher metrics show that the journal is selective and must not be interpreted as an easy fallback.

### Required manuscript changes before submission

Do not submit the Acta version unchanged.

For this venue:

1. retitle around post-quantum recovery feasibility under intermittent satellite contact;
2. rewrite the abstract to no more than 250 words;
3. use no more than eight keywords;
4. add a state-machine / message-dependency schematic;
5. add a logical contact-regime schematic;
6. add a graphical table-of-contents figure and <=80-word accompanying text;
7. directly compare against Ghosh and Nath 2026 and other NTN/PQC work;
8. foreground network/protocol feasibility rather than astronautics broadly;
9. reduce internal repository/hash detail in the main text;
10. retain the exact negative primary result and all claim boundaries.

## Candidate 2: IEEE Systems Journal

**Publisher:** IEEE  
**Recommendation:** strong systems-oriented fallback

Official scope:
https://ieeesystemscouncil.org/publication/ieee-systems-journal

Author instructions:
https://ieeesystemscouncil.org/publication/ieee-systems-journal/instructions-for-authors

### Fit

IEEE Systems Journal explicitly covers:

- systems and systems-of-systems;
- complex cyber-physical systems;
- modeling, analysis, and simulation;
- mission assurance;
- robustness, reliability, availability, and safety;
- communications;
- security;
- standards.

Study 8 can fit if framed as a systems-engineering result about recovery feasibility and security-state tradeoffs rather than primarily as a satellite-PQC application.

### Current format constraints

The live author instructions currently state:

- regular paper up to 12 pages at every review round;
- standard IEEE double-column journal format;
- ORCID required;
- up to 8 final published pages complimentary;
- up to 4 additional final pages allowed with extra-page charges;
- hybrid publication, with traditional subscription publication available without an open-access charge.

### Main risk

The paper would compete as a general systems contribution. The current frozen model may be viewed as too domain-specific or too synthetic unless the manuscript makes a stronger transferable systems argument.

For that reason, IEEE Systems Journal is a strong fallback but not the first retarget recommendation.

## Candidate 3: AIAA Journal of Aerospace Information Systems

**Recommendation:** technically plausible, but not preferred while Paper 1 is active there

AIAA states that the journal publishes original work on aerospace computing, information, networks and communication systems, systems engineering, verification and validation, and safety and mission assurance.

Scope:
https://aiaa.org/publications/journals/journal-scopes-and-content/

Study 8 is in scope conceptually.

However, Paper 1 from the same research program is already active at JAIS. Although this does not prohibit a separate submission, a new Paper 4 submission would require especially careful differentiation and self-overlap disclosure. A cleaner venue separation is preferable at this stage.

## Not recommended as the immediate next target

### Acta Astronautica

Closed by editorial rejection for manuscript `AA-D-26-02872`. Do not resubmit the same work there.

### IEEE Transactions on Aerospace and Electronic Systems

Paper 2 from the same research program is already active there. Study 8 could be in scope, but simultaneous same-author related submissions create avoidable editorial and self-overlap complexity. It is not the preferred immediate retarget.

### CEAS Space Journal

Paper 3 is already active there. Study 8 could potentially fit the broader space-systems scope, but the satellite-network/PQC topic has a more direct home in IJSCCN.

### Journal of Space Safety Engineering

Its scope centers space safety design, research, and practice. Study 8 is primarily a cryptographic recovery/network feasibility study rather than a space-safety investigation, so the fit is secondary.

## Current recommendation

### Proposed next venue

**International Journal of Satellite Communications and Networking**

This is a recommendation, not a locked venue.

The recommendation is based on:

- direct satellite-network scope;
- explicit network-protocol and performance-analysis coverage;
- recent publication of satellite PQC research;
- compatibility with modeling/simulation studies;
- ability to frame Study 8 around intermittent-contact recovery feasibility without inventing hardware, RF, or orbital evidence.

The publisher's displayed 8% acceptance rate means strong venue fit does not imply high acceptance probability. The manuscript must be substantially improved before submission.

## Novelty positioning for the retarget

Do not claim novelty for satellite PQC, crypto agility, lattice-based cryptography, or PQC communication overhead.

The narrow defensible contribution is:

> an exhaustive deterministic evaluation of post-compromise trusted cryptographic-state transition under finite intermittent satellite contact, separating the feasibility effects of standardized transition-object burden and contact timing from the security-state and availability costs of transition policy.

Closest-work differentiation should emphasize:

- Ghosh and Nath 2026: algorithm/performance/security analysis of lattice-based PQC for satellite communication;
- Eichen et al. 2026: PQ authentication bandwidth/resource pressure and alternative key-management architecture for constrained/NTN environments;
- De Zuane et al. 2026: quantum-safe IKE protocol design and experimental evaluation for satellite communications;
- NIST CSWP 39: environment-specific crypto-agility mechanisms and transition planning.

Study 8 instead focuses on trusted post-compromise epoch restoration under a finite contact schedule.

## Next gate

Before a venue-specific package is created, obtain explicit author approval to lock one venue.

If the author approves IJSCCN, create a new derivative package under a new directory. Preserve the frozen Acta package and target-neutral source package unchanged.
