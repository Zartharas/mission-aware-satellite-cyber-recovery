# Study 5 canonical findings — S5-CUCD-001

**Status:** `CANONICAL_RESULTS_FROZEN_PENDING_REPOSITORY_MERGE`  
**Design/implementation merge:** `872258b87ba016ac059930d110ff06a691246e73`  
**Validated head:** `9149ea900a6681ff55cd5c702f6194d50bb0e89d`  
**Dedicated validation:** `33663897775` / `100360780631` — PASS  
**Repository validation:** `33663897772` / `100360780901` — PASS

## Findings

1. **CuCD-ID does not directly supply the frozen trusted-recovery selector state.** None of the eight selector inputs is directly available from a CuCD-ID packet/telemetry row under the Study-5 mapping (`0/8`, coverage fraction `0.0`). In particular, the published scenario class is not treated as a policy-visible detector feature; it is permitted only as an offline oracle alarm for the bounded portability test.

2. **The original proposal to run P0–P7 or the Study-2 policies directly on CuCD-ID rows is therefore rejected as scientifically unsupported without additional response-state instrumentation.** Imputing authorization, trust, freshness, epoch, contradiction, signature validity, or evidence completeness from packet telemetry would manufacture variables the external dataset does not provide.

3. **CuCD-ID still provides useful external scenario/taxonomy coverage.** Its four attack classes are retained as external threat scenarios with conceptual or assurance-boundary adjacency to the frozen event/evidence taxonomy, but none is asserted to be a direct equivalent of a frozen Study-1 event family or Study-2 evidence treatment.

4. **Frozen response semantics are portable to an external alarm interface without becoming attack-label-specific.** Across all 16 controlled recovery-context × policy groups, the four attack subtype labels produced identical actions when the label was reduced to the same offline `security_signal=true` alarm. Thus attack-subtype action invariance was `16/16` groups.

5. **The finite bridge produced 80 deterministic decisions.** The exact action counts were 20 `HOLD_AND_REQUIRE_EVIDENCE`, 14 `PRESERVE_LIMITED_OPERATION`, 16 `PROCEED_TO_RECOVERY_GATE`, and 30 `RESTRICT_AND_REQUEST_AUTHORIZATION`. These counts describe the frozen balanced bridge grid; they are not weighted by operational attack prevalence and do not define a global policy ranking.

6. **Independent reconstruction found zero mismatches.** The independent auditor did not import the Study-5 bridge or Study-2 selector; it reconstructed the baseline decision rules from emitted fields and reported `0` mismatches over all 80 decisions, eight sufficiency rows, and five transferability rows.

## Interpretation boundary

This study is not an intrusion-detection benchmark. It does not estimate CuCD-ID detector accuracy, recall, precision, false-positive rate, or attack prevalence, and it does not claim that the recovery policies were executed on individual CuCD-ID packet rows. The result is narrower: CuCD-ID expands the external threat-scenario vocabulary, while direct trusted-recovery validation still requires mission, authorization, trust, freshness, contradiction, epoch, signature, and evidence-completeness instrumentation that CuCD-ID does not contain.

Studies 1–4 remain frozen and are not pooled with Study 5. No operational spacecraft, RF, real credentials, or third-party target is involved.
