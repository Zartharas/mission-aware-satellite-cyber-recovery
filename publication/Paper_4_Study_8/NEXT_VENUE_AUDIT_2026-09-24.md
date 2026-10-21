# Paper 4 Fresh Venue-Fit Audit After IJSCCN Scope Rejection

**Audit date:** 2026-09-24  
**Manuscript:** Rebuilt Paper 4 / Study 8 + Study 8E  
**IJSCCN manuscript ID:** `4920969`  
**Trigger:** IJSCCN editorial-screening rejection with stated reason `out of scope`  
**Scientific effect:** None  
**Venue lock:** None

## Governing evidence boundary

The venue must fit the manuscript as it actually exists:

- satellite/space-system cybersecurity;
- post-quantum cryptographic transition and crypto-agility;
- trusted post-compromise recovery/key-state transition;
- intermittent connectivity and contact/opportunity constraints;
- deterministic modeled feasibility and exact finite-population analysis;
- separately governed Study 8 and Study 8E populations;
- SatNOGS observation timing used only as an opportunity proxy.

The venue must **not** require unsupported claims about measured RF throughput, BER/coding, link margin, physical PQC execution latency, spacecraft CPU/energy/thermal performance, authenticated command-contact availability, mission availability, or operational recovery time.

## Live candidate review

### Candidate A: International Journal of Information Security (Springer Nature)

**Current fit evidence**

- The journal publishes information-security work spanning system/network security, authentication, and applied cryptography.
- It has published satellite-focused security work, including:
  - *Cyber security in New Space*;
  - *Enhancing the hypatia simulator for LEO satellite networks with integrated DoS and DDoS attack capabilities* (2026);
  - *Design of a resilient multi-layered security framework for satellite communications* (2026).
- The 2026 satellite-security framework paper explicitly discusses cryptographic protection and future post-quantum integration.
- The journal also publishes cryptography and quantum-security work outside the space domain.

**Paper-4 fit**

Strong topical alignment because the manuscript can be framed primarily as an information-security/recovery-feasibility contribution with satellite systems as the constrained application domain. The journal's recent satellite-security record reduces the scope uncertainty encountered at IJSCCN.

**Main adaptation risk**

The manuscript should foreground security/recovery semantics, cryptographic transition requirements, threat/recovery assumptions, and evidence boundaries rather than communications-network performance.

**Publishing-model note**

IJIS is currently fully open access. Springer Nature lists the current APC as USD 3,690 (also GBP 2,690 / EUR 2,990), with taxes where applicable. Springer states that discretionary waiver or discount requests must be made at submission.

**Status:** `PRIMARY_CANDIDATE_FOR_AUTHOR_REVIEW__NOT_LOCKED`

### Candidate B: IEEE Systems Journal

**Current fit evidence**

- The journal's regular-issue scope is systems-level, application-oriented research on complex systems and systems-of-systems.
- It explicitly covers systems thinking, systems engineering, complex cyber-physical systems, reliability/resilience, and multi-domain applications.
- The IEEE Systems Council now has a Technical Committee on System Security with working groups for **Quantum & Post-Quantum System Security** and system-level assurance/verification.
- Regular papers may be up to 12 pages during review.

**Paper-4 fit**

Strong systems-engineering alignment if the contribution is framed as a constrained trusted-recovery system problem across cryptographic state, contact opportunities, disruption, and recovery horizons rather than as a new cryptographic primitive.

**Main adaptation risk**

The paper would need a clear systems-level architecture/problem formulation and substantial IEEE-format compression. It must avoid appearing as a component-level cryptography paper.

**Status:** `STRONG_ALTERNATIVE__NOT_LOCKED`

### Candidate C: Journal of Information Security and Applications (Elsevier)

**Current fit evidence**

- JISA focuses on original research and practice-driven applications relevant to information security.
- Its published scope includes authentication/access control and cryptographic protection in systems/applications.
- It has recent post-quantum work, including quantum-safe authenticated key agreement and 2026 work combining post-quantum cryptography with applied secure systems.

**Paper-4 fit**

Good fit for the paper's applied security and cryptographic-transition aspects, especially if the manuscript emphasizes recovery mechanisms and modeled application constraints.

**Main adaptation risk**

The satellite-specific contribution must remain technically meaningful rather than appearing as a generic PQC application with a space label.

**Status:** `STRONG_ALTERNATIVE__NOT_LOCKED`

### Candidate D: Aerospace (MDPI), Astronautics & Space Science section

**Current fit evidence**

- Aerospace covers spacecraft design, operations, control, risk/reliability, software engineering, and multidisciplinary space engineering.
- Its Astronautics & Space Science section explicitly includes satellite technology and spacecraft operations.
- The journal published *A Comprehensive Literature Review of Cybersecurity in Satellite Networks* in 2026.

**Paper-4 fit**

The satellite domain is clearly in scope, and the journal has demonstrated willingness to publish satellite-cybersecurity work.

**Main adaptation risk**

Reviewers may expect stronger aerospace-operational or hardware/mission validation than the frozen modeled evidence supports. The manuscript must keep the non-operational claim boundaries explicit.

**Status:** `DOMAIN_FIT_ALTERNATIVE__NOT_LOCKED`

### Candidate E: IEEE Access

**Current fit evidence**

- IEEE Access is explicitly broad and multidisciplinary across IEEE fields.
- Its scope favors application-oriented work that may not fit traditional narrow journals.
- It accepts simulation/model-based research when analyses are technically rigorous.
- It publishes both post-quantum security work and satellite/cybersecurity work.
- IEEE Access uses a binary accept/reject review process and is fully open access.

**Paper-4 fit**

Low scope-rejection risk relative to a narrow communications journal and reasonable alignment with the manuscript's multidisciplinary security + satellite-systems character.

**Main adaptation risk**

Mandatory IEEE Access formatting, biography requirements, open-access APC, and a high technical-merit threshold. Broad scope does not reduce the need to establish novelty and contribution clearly.

**Status:** `BROAD_SCOPE_FALLBACK__NOT_LOCKED`

## Candidate excluded from the active shortlist

### Computers & Security

Computers & Security has published recent satellite-cybersecurity work, including 2026 satellite-system and space-organization security papers. However, its current publisher scope explicitly states that **cryptology has been excluded since 2006** and that submissions with cryptology as a principal component will not be considered for review.

Because post-quantum cryptographic transition/object burden is a principal component of rebuilt Paper 4, this creates a direct scope-risk signal.

**Status:** `EXCLUDED_FROM_ACTIVE_SHORTLIST__CRYPTOLOGY_SCOPE_CONFLICT`

## Provisional ordering for author review

1. **International Journal of Information Security** — strongest direct overlap with satellite cybersecurity + applied cryptography/security systems.
2. **IEEE Systems Journal** — strong system-level security/resilience fit if the paper is compressed and framed as systems engineering.
3. **Journal of Information Security and Applications** — strong applied information-security/PQC fit.
4. **Aerospace** — clear satellite-domain fit, but higher risk of operational-validation expectations.
5. **IEEE Access** — broad multidisciplinary fallback with lower scope risk but mandatory open-access publication model.

This ordering is a venue-fit assessment, not an acceptance prediction.

## Transfer Desk state

As of the 2026-09-24 Outlook check, no separate Wiley Transfer Desk recommendation email has been received. The IJSCCN decision email states only that recommendations may follow.

No transfer is authorized.

## Live sources checked

- Springer Nature, International Journal of Information Security aims and scope: https://link.springer.com/journal/10207/aims-and-scope
- Springer Nature, International Journal of Information Security publishing model / fees: https://link.springer.com/journal/10207/how-to-publish-with-us
- Springer Nature, International Journal of Information Security article record: *Cyber security in New Space*: https://link.springer.com/article/10.1007/s10207-020-00503-w
- Springer Nature, 2026 IJIS satellite-security article: https://link.springer.com/article/10.1007/s10207-025-01184-z
- Springer Nature, 2026 IJIS LEO-satellite security simulation article: https://link.springer.com/article/10.1007/s10207-025-01191-0
- IEEE Systems Council, IEEE Systems Journal regular-issue scope: https://ieeesystemscouncil.org/publication/iEEE-systems-journal/call-papers-regular-issues
- IEEE Systems Council, IEEE Systems Journal instructions: https://ieeesystemscouncil.org/publication/ieee-systems-journal/instructions-for-authors
- IEEE Systems Council, Technical Committee on System Security: https://ieeesystemscouncil.org/technical-committee/technical-committee-system-security
- Elsevier, Journal of Information Security and Applications: https://shop.elsevier.com/journals/journal-of-information-security-and-applications/2214-2126
- MDPI Aerospace aims and scope: https://www.mdpi.com/journal/aerospace/about
- MDPI Aerospace Astronautics & Space Science section: https://www.mdpi.com/journal/aerospace/sections/astronautics_space_science
- IEEE Access scope: https://ieeeaccess.ieee.org/about/
- IEEE Access submission guidelines: https://ieeeaccess.ieee.org/authors/submission-guidelines/
- Elsevier Computers & Security current scope summary: https://shop.elsevier.com/journals/computers-and-security/0167-4048

## Next gate

Author review of the shortlist and selection of the journal for a **full live author-guideline audit**.

Do not create a new venue-specific manuscript derivative and do not authorize any Wiley transfer until the author separately selects a target venue.
