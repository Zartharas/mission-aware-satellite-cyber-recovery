# Study 8 Venue Fit — Publication Development

**Verification date:** 2026-09-03  
**Status:** `VENUE_CANDIDATES_EVALUATED_NOT_SUBMISSION_AUTHORIZED`

## Recommended order

### 1. IEEE Systems Journal — primary candidate

Current IEEE Systems Journal scope explicitly includes systems-level modeling, analysis, simulation, mission assurance, robustness, reliability, availability, communications, security, standards, and complex cyber-physical systems. That combination closely matches Study 8's systems-level question: how a finite post-compromise cryptographic transition behaves under interacting contact, byte-budget, deadline, disruption, and policy constraints.

Why the paper fits:

- the contribution is systems-level rather than cryptanalytic;
- the full deterministic factorial model is an analysis/simulation contribution;
- the paper studies availability, security-state, interoperability/transition, and mission-assurance-adjacent design tradeoffs without claiming flight performance;
- a negative primary result plus deterministic resource/state tradeoffs is suitable for a systems-analysis paper when reported transparently;
- the current regular-paper limit is up to 12 pages during review, making a compact manuscript with four main tables and two figures feasible.

Current source: https://ieeesystemscouncil.org/publication/ieee-systems-journal  
Author instructions: https://ieeesystemscouncil.org/publication/ieee-systems-journal/instructions-for-authors

**Development disposition:** primary manuscript-shaping target. Final commitment remains a later author gate.

### 2. Acta Astronautica — strong domain-specific alternative

Acta Astronautica accepts original contributions in space engineering and technology, including satellite technology and communications. It has prior satellite-cybersecurity papers and, in September 2026, published a systematic survey specifically on post-quantum cryptography for space systems (Kim, 2026). That makes the journal highly relevant to the domain and establishes that PQC-for-space is within editorial scope.

Why the paper fits:

- satellite/space-system context is central rather than incidental;
- the study addresses transition architecture and constrained-contact behavior rather than only algorithm benchmarking;
- the deterministic model can be positioned as a space-systems design analysis;
- the claim boundary must be especially explicit because the journal also publishes hardware, flight, and physical-performance work that Study 8 does not provide.

Current scope source: https://shop.elsevier.com/journals/acta-astronautica/0094-5765  
Recent PQC-space precedent: Kim, 2026, DOI `10.1016/j.actaastro.2026.04.041`.

**Development disposition:** strongest aerospace-domain alternative.

### 3. International Journal of Satellite Communications and Networking — direct communications alternative

The journal covers the theory, practice, and operation of satellite systems and networks, including satellite networks, performance analysis, standards/regulation, interoperability, and network protocols. In 2026 it published Ghosh and Nath's lattice-based post-quantum satellite communication paper, providing direct topical precedent.

Why the paper fits:

- contact opportunity, transition objects, protocols, and constrained-network behavior are central;
- the paper can be framed as protocol/system performance analysis using a synthetic finite logical-contact model;
- the results directly complement current satellite PQC migration work by focusing on post-compromise transition feasibility rather than generic deployment feasibility.

Current scope: https://onlinelibrary.wiley.com/page/journal/15420981/homepage/productinformation.html  
Recent topical precedent: Ghosh and Nath, 2026, DOI `10.1002/sat.70041`.

**Development disposition:** direct-scope fallback if systems/aerospace venues reject the modeled abstraction.

## Venue explicitly not recommended for Study 8

### Computers & Security

The existing Study-1/Study-2 paper is separately targeted to Computers & Security, but the current journal scope explicitly states that submissions in which cryptology is a principal component are not considered. Study 8's central treatment object is a cryptographic transition built from ML-KEM/ML-DSA standardized objects. Even though the contribution is systems-level rather than cryptanalytic, routing this companion paper there creates avoidable desk-rejection risk.

Current source: https://shop.elsevier.com/journals/computers-and-security/0167-4048

**Disposition:** do not merge Study 8 into the existing Computers & Security submission package; retain the separate companion-publication line.

## Manuscript-shaping decision

The development draft will use **IEEE Systems Journal as the primary formatting/length target while remaining venue-neutral in scientific claims**. No publisher-specific template, copyright transfer, portal submission, or final venue commitment is authorized in this phase.
