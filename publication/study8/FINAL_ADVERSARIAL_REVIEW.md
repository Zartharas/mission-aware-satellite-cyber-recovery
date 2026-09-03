# Study 8 Final Manuscript Adversarial Review

**Review ID:** `S8-PUB-AR-001`  
**Freeze authorization:** `S8-PUBFREEZE-001`  
**Trigger commit:** `0c2aab95111abdc9535ec8ab347f6e0a6bbbd71c`  
**Review time (UTC):** `2026-09-03T16:35:11.010936Z`  
**Scope:** publication layer only; frozen Study-8 science remained read-only.

## Disposition

`PASS_PUBLICATION_ONLY_CORRECTIONS_APPLIED_READY_FOR_HASH_FREEZE`

## Adversarial findings corrected

1. **External-replication ambiguity.** Abstract wording was changed from an unqualified “independent statistical implementation” to explicit same-repository, separately implemented reproduction language.
2. **Contact-structure overstatement.** Wording that could imply isolation of timing alone was corrected to describe partitioning of fixed total-cycle capacity among contacts and placement across logical slots.
3. **Dominance wording.** The abstract no longer says the profile/contact/deadline factors “dominate” recovery feasibility; it states that they account for the observed feasibility differences in the frozen model.
4. **Figure denominator clarity.** The profile figure now states that each bar is based on that profile's 1,152 frozen positions rather than ambiguously referring to all 3,456 positions.
5. **Reproduction traceability.** A dedicated claim-traceability row now prohibits external-laboratory or independent-human-replication language.
6. **AI-use provenance.** Development metadata and the manuscript now truthfully record generative-AI language assistance while preserving author responsibility and the frozen-science boundary.

## Claims re-audited and retained

- Negative primary result remains prominent: all four policies `635/864`; P3-P1 exactly `0.000000` percentage points.
- All 14 prespecified P3-versus-P1 strata remain reported as exact zero contrasts.
- Profile results remain `1080/1152`, `748/1152`, and `712/1152`; matched non-increasing ordering remains `1152/1152`.
- Logical slots remain nonphysical ordering units; no conversion to seconds, orbital periods, or real mission recovery time is permitted.
- Modeled cryptographic bytes remain standardized-object budget only; no RF, CPU, energy, certificate/framing, or flight-performance claim is introduced.
- Structural zeros remain invariant checks, not treatment-effect evidence.
- ML-KEM/ML-DSA are not claimed as operational CCSDS-standardized PQC suites.
- Same-repository reproduction is not external replication or empirical validation.
- Studies 1-7 remain unpooled with Study 8.

## Gate boundary

This review authorizes and records the publication-package freeze only. PR #92 merge is **not** authorized by this gate. Publisher submission and publisher-portal actions remain **not authorized**.
