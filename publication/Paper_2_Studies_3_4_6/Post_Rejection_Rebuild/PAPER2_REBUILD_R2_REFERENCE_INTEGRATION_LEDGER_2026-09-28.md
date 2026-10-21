# Paper 2 Rebuild R2 — Reference Integration Ledger

**Date:** 2026-09-28  
**Purpose:** document the reference changes applied to R2 without changing frozen scientific results.

## Existing-reference corrections

- **[4] SPARTA:** replaced the generic SPARTA homepage citation with the specific official `CM0044 Cyber-safe Mode` page because R2 makes a concrete integrity-protected validated-baseline recovery claim.
- **[12]–[13] SLSA:** retained v1.2 and added the exact official Source Requirements and Threats & Mitigations URLs with an updated access date.
- **[14] ESA Anomaly Dataset:** corrected bibliographic authors to G. De Canio, K. Kotowski, and C. Haskamp while retaining the frozen experiment's scientific use of ESA Anomaly Dataset v2, Missions 1 and 2.

## Added close/current literature

### [15] Silent Subversion

J. Vanlyssel, G.-C. Roman, and A. Anwar, 2026 IEEE Aerospace Conference, doi: `10.1109/AERO66936.2026.11519913`.

**R2 use:** closest mechanism comparison for legitimate-looking false telemetry produced by a compromised onboard supply-chain component.

**Novelty boundary:** R2 explicitly does not claim that legitimate-looking false telemetry is new. Paper 2's contribution is the qualification-boundary analysis under explicit timing, evidence, producer-composition, and artifact-assurance semantics.

### [16] Satellite communications cybersecurity survey

S. Salim, N. Moustafa, and M. Reisslein, IEEE Communications Surveys & Tutorials, 2025, doi: `10.1109/COMST.2024.3408277`.

**R2 use:** contemporary field-level threat/defense context.

### [17] 2026 satellite-network literature review

B. Wang et al., Aerospace, 2026, doi: `10.3390/aerospace13030249`.

**R2 use:** current broad literature coverage used to bound claims about the research landscape.

### [18] NIST IR 8270

M. Scholl and T. Suloway, 2023, doi: `10.6028/NIST.IR.8270`.

**R2 use:** authoritative commercial-satellite cybersecurity and risk-management context.

### [19] Satellite zero-trust experiment

M. M. Utsash et al., ICISSP 2025, doi: `10.5220/0013103200003899`.

**R2 use:** distinguishes implementation-level attack mitigation from Paper 2's qualification-boundary analysis.

### [20] NASA Space Security Best Practices Guide

NASA, Rev. B.

**R2 use:** space-mission security context spanning prevention, mitigation, and recovery.

## Source-state checks

As of 2026-09-28:

- SPARTA CM0044 is available as the direct cyber-safe-mode countermeasure page.
- IETF `draft-ietf-rats-multi-verifier-00` remains the cited work-in-progress version dated 5 May 2026.
- SLSA v1.2 is the current specification version used by R2.
- NIST IR 8270 remains the official published satellite-operations cybersecurity introduction.

## Non-effect on frozen science

These reference changes alter literature positioning and citation precision only. They do not modify Study 3, Study 4, Study 6, S3X, any result count, any policy result, or any frozen artifact.
