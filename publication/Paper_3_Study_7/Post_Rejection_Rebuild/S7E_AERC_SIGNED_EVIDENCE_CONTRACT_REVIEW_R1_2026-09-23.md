# S7E-AERC-001 Signed-Evidence Contract Technical Review R1 — 2026-09-23

**Experiment:** `S7E-AERC-001`  
**Reviewed artifact:** `study7e/configs/signed_evidence_contract_draft.json`  
**Disposition:** **REVISE BEFORE AUTHOR APPROVAL**  
**Protocol freeze:** NO  
**Policy binding:** NO  
**Canonical scientific execution:** NOT AUTHORIZED

## Executive finding

The first draft is directionally sound but should not be approved or frozen as written.

Its strongest properties are explicit fixed-width serialization, signed source/authority/key identifiers, a domain separator, controlled logical-time fields, and a public-key-only verifier boundary.

Three items block approval:

1. the signed body does not bind scenario/context identity;
2. signing-key placement is inconsistent across the current design artifacts;
3. T4's separate authority/keying provenance remains unspecified.

## R1-F1 — scenario/context binding is required

The current 56-byte candidate excludes `scenario_id` from the signed body. That leaves a splice/replay ambiguity if the same signed evidence can be transported into another scenario with compatible epoch/time/sequence metadata.

Recommendation: sign an **opaque** scenario/context ID. The value must not encode topology or fault identity and must remain policy-invisible metadata.

A revised candidate can remain within the already-qualified verifier capacity by using a 64-byte body.

## Recommended candidate v2 layout

| Offset | Bytes | Field |
|---:|---:|---|
| 0 | 16 | domain separator `S7E-AERC-AUTH-V1` |
| 16 | 1 | schema version |
| 17 | 1 | producer role |
| 18 | 1 | authorization value |
| 19 | 1 | reserved8 = 0 |
| 20 | 4 | opaque scenario ID |
| 24 | 4 | opaque source ID |
| 28 | 4 | opaque authority ID |
| 32 | 4 | opaque key ID |
| 36 | 4 | reserved32 = 0 |
| 40 | 8 | evidence epoch |
| 48 | 8 | issued controlled logical time |
| 56 | 8 | evidence sequence |

Total: **64 bytes**.

This layout is a recommendation, not a frozen protocol.

## R1-F2 — preserve feature independence

The policy contract exposes `signature_valid` and `authorization` as separate features. Automatically zeroing authorization whenever signature verification fails would collapse those dimensions in preprocessing.

Recommendation:

- if a message is structurally complete, preserve its parsed signed authorization claim as the authorization feature even when `signature_valid=0`;
- if evidence is absent or structurally invalid, use `authorization=0` and `complete=0`;
- policy safety remains fail-closed because D0/D1 separately require the quality predicates.

This preserves the equal-information comparison and avoids hidden feature engineering.

## R1-F3 — completeness should be structural only

`complete` should not duplicate signature, source trust, freshness, or epoch validity.

Recommended structural conditions include exact canonical length, correct domain separator/version/role, binary authorization value, zero reserved fields, and parseable mandatory identifiers/timestamps.

An unknown source/key may still be structurally complete while failing the dedicated trust/signature feature.

## R1-F4 — contradiction should be path-local

Primary/corroborator disagreement is already visible through their separate authorization features. The contradiction feature should not silently collapse cross-path disagreement.

Recommended path-local rule:

- byte-identical duplicate: not a contradiction;
- two different structurally complete evidence bodies with the same signed scenario, producer role, source, epoch, and evidence sequence: contradiction;
- absence of usable evidence: `noncontradictory=0` because consistency was not established.

Exact state-reset behavior still needs freeze review.

## R1-F5 — freshness thresholds belong to qualifier configuration

The producer should not choose its own acceptance window.

Recommendation: sign `issued_logical_time` and `evidence_epoch`, but keep freshness threshold/unit in frozen qualifier configuration.

This is consistent with the existing requirement for controlled experiment time and prevents a compromised producer from widening its own freshness window.

## R1-F6 — domain IDs must be opaque

Source/key/authority IDs should be stable nonzero numeric identifiers but must not encode topology or fault class in their bit patterns.

Topology manifests may implement sharing by aliasing IDs. Policies receive only derived booleans, not those identifiers.

## R1-F7 — signing-key placement requires an explicit design choice

There is a current design tension:

- the implementation plan says authorization producer apps construct and emit signed evidence;
- the current verifier/dependency guardrails prohibit secret keys in flight software.

Two coherent options exist:

**Option A — external deterministic test signing service/harness.**  
Private test keys stay outside cFS FSW. Producer cFS components emit or transport pre-signed evidence. Key-domain compromise is modeled by the controlled harness selecting the affected test key.

**Option B — isolated producer-only signing components.**  
Private test keys exist only in dedicated producer-signing components, while verifier/qualifier/policy/sink FSW remains public-key-only. This requires explicitly narrowing the current no-secret-key guardrail and documenting why.

Do not implement either implicitly.

## R1-F8 — T4 authority provenance remains blocking

The implementation plan states that T4 separates authorization authority/keying provenance but does not freeze the mechanism.

Before producer implementation, decide whether signed `authority_id` plus controlled harness provenance is sufficient or whether an additional authority assertion/signature/key layer is required.

## Remaining freeze blockers

The review keeps these items unresolved:

- scenario/context binding approval;
- key-generation/public-key registry procedure;
- logical-time units and freshness thresholds;
- epoch semantics;
- replay/sequence rule;
- final contradiction/completeness rules;
- authorization behavior on failed qualification;
- T4 authority representation;
- F3/F4/F9/F10/F11/F12 byte-level transforms;
- final test key pairs/public-key hashes.

## Conclusion

R1 does not authorize producer signing, verifier-to-policy binding, protocol freeze, model training/freeze, or canonical execution.

The next safe step is to revise the draft to the proposed v2 form while keeping every freeze/approval gate false.
