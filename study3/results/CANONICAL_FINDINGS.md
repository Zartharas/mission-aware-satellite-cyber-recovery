# Study 3 canonical findings — S3-K4E-001

**Status:** `CANONICAL_RESULTS_FROZEN_PENDING_REPOSITORY_MERGE`  
**Design merge:** `577d0a0d1f8eb603cc836ded40cb7e795af7d001`  
**Canonical execution:** `c2372c5fab598ecec1070b1bc76b9ff5237f9c99`  
**Workflow / job:** `33650631676` / `100316425605`  
**Artifact:** `9854607159`  
**Artifact ZIP SHA-256:** `2cae36a016fd899ef921085fabbbc3599f75847417eb88ea47ec9860c26a683e`

The canonical campaign contains 30 cells, 46 onset phases per cell, 1,380 deterministic temporal trajectories, and 67,620 epoch states. The independent auditor reported zero trajectory mismatches, zero epoch-rule mismatches, zero false-qualification-origin mismatches, and zero SHA mismatches.

## Findings

1. **Persistent V5 creates a sustained false-qualification regime for gate-entering B0/S1 semantics under continuous contact.** Across the complete K0 onset grid, B0 and S1 each had unsafe-qualified recovery in 46/46 trajectories with mean exposure 122.5 logical seconds. B2 had 0/46 and mean exposure 0.

2. **Intermittent K4 contact reduces, but does not eliminate, persistent V5 false qualification.** Under K4, persistent V5 produced unsafe qualification in 46/46 B0 trajectories and 46/46 S1 trajectories. Mean exposure was 55.326 logical seconds for B0 and 49.022 for S1. Relative to their truthful V0 controls, the V5-attributable increments were 55.0 and 49.022 logical seconds, respectively. B2 remained 0/46.

3. **S1's contact-aware restriction provides an additional K4 boundary relative to B0, but not immunity.** Under persistent V5/K4, S1's mean unsafe-qualified exposure was about 6.304 logical seconds lower than B0. Both remained vulnerable during contact windows because V5 evidence is fresh, validly signed, and false relative to hidden truth.

4. **Persistent V4 is detectably different from V5.** The affected V4 records never qualified because post-signature manipulation invalidated the signature. Persistent V4 therefore did not add V4-attributable false qualification. Any B0 K4 false qualification observed in V4/V0 was attributable only to a still-fresh record received before the hidden authorization state changed.

5. **Freshness is not instantaneous truth synchronization.** Under truthful V0/K4, B0 had a short cache boundary in 3/46 onset phases, with mean unsafe-qualified exposure 0.326 logical seconds across the complete grid. The prespecified origin decomposition attributed these epochs to `PRE_ONSET_CACHE`, not adversarial evidence. S1 and B2 had no truthful-V0 false qualification under K4.

6. **One-shot V5 is transient but universal across the modeled onset grid for B0/S1.** Under K0, one-shot V5 gave B0 and S1 mean unsafe-qualified exposure of 5 logical seconds and affected all 46 onset phases. Under K4, it affected all 46 B0/S1 onset trajectories that eventually received the one-shot compromised record; B0's mean includes the separate cache boundary, while S1's mean V5 exposure remained 5 logical seconds.

## Interpretation boundary

`unsafe_permissive_epoch_rate` is a selector/gate-entry action metric. It must not be described as actual trusted recovery. The stronger endpoint is `unsafe_qualified`: the recovery gate is policy-visible qualified while research-only hidden authorization truth is false.

The study is a deterministic software model. Logical seconds are not spacecraft, orbital-access, network, or operator latency. K4 is a synthetic flapping-contact schedule, not an orbital-availability estimate. The 46 onset phases exhaust the frozen model grid; they do not estimate how often these conditions occur in operational missions. Study 1 and Study 2 remain frozen and are not pooled with Study 3.
