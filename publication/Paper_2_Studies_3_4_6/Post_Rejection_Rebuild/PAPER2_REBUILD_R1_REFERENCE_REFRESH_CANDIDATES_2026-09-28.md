# Paper 2 Rebuild R1 — Reference Refresh Candidates

**Status:** audit evidence only; no manuscript-reference changes authorized by this file.  
**Cutoff:** checked through 2026-09-28.

## 1. Existing-reference correction

### ESA Anomaly Dataset

**DOI:** `10.5281/zenodo.15237121`

DOI-resolved metadata:

> G. De Canio, K. Kotowski, and C. Haskamp, "ESA Anomaly Dataset," 2025. doi: 10.5281/zenodo.15237121.

Current R1 source identity/version remains scientifically correct: the frozen experiment uses ESA Anomaly Dataset **v2**, Missions 1 and 2. The bibliographic author/title metadata should be corrected during the next authorized manuscript edit.

## 2. Priority literature candidates

### L1 — closest trusted-source / legitimate-looking false-telemetry comparison

**DOI:** `10.1109/AERO66936.2026.11519913`

J. Vanlyssel, G.-C. Roman, and A. Anwar, "Silent Subversion: Sensor Spoofing Attacks via Supply Chain Implants in Satellite Systems," 2026 IEEE Aerospace Conference, pp. 1–10, 2026.

**Why evaluate for inclusion:** demonstrates an onboard compromised vendor component producing telemetry in expected format/cadence that ground tooling accepts as legitimate. This is close to Paper 2's semantic trusted-producer motivation.

**Required distinction:** Paper 2 does not claim discovery of legitimate-looking false telemetry. Its contribution is the finite recovery-qualification boundary under explicit freshness/contact/policy semantics, source-origin separation, and the separately frozen S3X timing stress test.

### L2 — contemporary satellite cybersecurity survey

**DOI:** `10.1109/COMST.2024.3408277`

S. Salim, N. Moustafa, and M. Reisslein, "Cybersecurity of Satellite Communications Systems: A Comprehensive Survey of the Space, Ground, and Links Segments," IEEE Communications Surveys & Tutorials, vol. 27, no. 1, pp. 372–425, 2025.

**Why evaluate for inclusion:** high-value field-level review for current threat/defense positioning.

### L3 — 2026 satellite-network cybersecurity literature review

**DOI:** `10.3390/aerospace13030249`

B. Wang et al., "A Comprehensive Literature Review of Cybersecurity in Satellite Networks," Aerospace, vol. 13, no. 3, p. 249, 2026.

**Why evaluate for inclusion:** recent broad/systematic literature coverage; consult before making a literature-gap statement.

### L4 — authoritative satellite-operations cybersecurity context

**DOI:** `10.6028/NIST.IR.8270`

M. Scholl and T. Suloway, "Introduction to Cybersecurity for Commercial Satellite Operations," NIST IR 8270, 2023.

**Why evaluate for inclusion:** official satellite-specific cyber-risk context that can strengthen aerospace significance.

## 3. Strong secondary candidates

### Zero-trust satellite experiment

**DOI:** `10.5220/0013103200003899`

M. Utsash, G. Kavallieratos, K. Antonakopoulos, and S. K. Katsikas, "Investigating the Effectiveness of Zero-Trust Architecture for Satellite Cybersecurity," Proc. ICISSP, pp. 133–140, 2025.

### Cybersecurity-in-space research-gap paper

**DOI:** `10.1109/AICCSA66935.2025.11315201`

C. Mattar et al., "What is Cybersecurity in Space?," 2025 IEEE/ACS AICCSA, pp. 1–6, 2025.

### Space-forensic evidence visibility

**DOI:** `10.1109/ACCESS.2026.3686372`

B. G. Cho et al., "Space-Forensic Tool Coverage Derivation Through Satellite System Profiling," IEEE Access, vol. 14, pp. 72313–72330, 2026.

### Current CubeSat cybersecurity overview

**DOI:** `10.1109/ACCESS.2026.3705697`

J. P. C. M. Oliveira, F. J. T. Vidal, and F. Mattiello-Francisco, "CubeSat Cybersecurity: An Overview," IEEE Access, vol. 14, pp. 108539–108547, 2026.

## 4. Existing standards/web references requiring source-specific retention

These were not resolved by the scholarly batch checker because they are standards/web resources rather than ordinary scholarly records:

- The Aerospace Corporation SPARTA — replace generic-homepage support with the specific **CM0044 Cyber-safe Mode** page if it directly supports the recovery-baseline sentence.
- IETF `draft-ietf-rats-multi-verifier-00` — retain as work in progress if still current at submission.
- TUF Specification v1.0.36 — retain direct official version/release URL and access date.
- SLSA v1.2 source requirements — retain official URL and access date.
- SLSA v1.2 threats/mitigations — retain official URL and access date.

## 5. Reference-integration rule

No candidate is added merely to increase bibliography size. A reference should enter R2 only if it does at least one of the following:

1. supports a material aerospace-context claim;
2. constrains the novelty boundary;
3. provides the closest prior mechanism/result comparison;
4. supports an interpretation or limitation that is otherwise under-sourced.

The final literature-gap statement should be made only after these close candidates are read and compared against the exact Paper-2 contribution.
