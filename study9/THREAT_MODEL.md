# Study 9 Threat Model

**Study:** `S9-RTSI-001`  
**Phase:** 9.0 prospective design  
**Status:** `THREAT_MODEL_DRAFT_BEFORE_SCHEMA_LOCK`

## Scope

Study 9 studies a semantic boundary between public space-cyber telemetry and a bounded mission-aware recovery-decision interface. The threat model therefore focuses on decision-relevant information loss, ambiguity, provenance weakness, and unsafe inference rather than on reproducing a specific spacecraft attack campaign.

The study does not assume that any included dataset was designed for recovery control. A dataset may be excellent for intrusion detection and still lack the state needed to justify a recovery action.

## Protected decision property

The protected property is **decision identifiability under explicit evidence semantics**.

For a native dataset record or state representation, the downstream action is identifiable only when every admissible assignment of unresolved required recovery variables produces the same action under the frozen downstream interface.

If two or more actions remain possible, the correct Study 9 result is ambiguity. The analysis must not choose the action that appears most reasonable to the analyst.

## Decision-relevant state

The bounded interface requires:

- `signature_valid`
- `source_trusted`
- `fresh`
- `epoch_valid`
- `contradictory`
- `minimum_evidence_complete`
- `security_signal`
- `authorization_available`

These are semantic decision variables. A native feature counts only when its meaning satisfies the preregistered mapping rubric.

## Threats to semantic validity

### Missing decision state

The dataset may omit one or more required variables entirely. Missing state remains unknown and can create multiple admissible downstream actions.

### Proxy substitution

A convenient feature may correlate with a recovery variable without establishing it. Examples include treating a source identifier as trust, a timestamp as freshness, a checksum/error field as signature validity, or an attack label as an operational alarm.

Study 9 treats such substitution as a threat to scientific validity.

### Ground-truth leakage

Attack/scenario labels are typically assigned by the experimenter after or during controlled data generation. Using those labels as if they were available to the deployed recovery mechanism would leak offline ground truth into the decision path.

Primary Study 9 endpoints prohibit this use.

### Temporal mismatch

A field may have the right name but the wrong temporal meaning. A timestamp does not establish freshness unless it can be compared with a decision-time reference under a frozen freshness rule. A sequence or version field does not establish epoch validity unless the accepted epoch relation is represented.

### Provenance and trust ambiguity

A record can identify a packet, host, process, or source without establishing that the source is trusted. Dataset provenance also does not imply per-record source trust.

### Evidence-completeness ambiguity

Presence of telemetry is not equivalent to evidence completeness. Completeness requires an explicit criterion defining which evidence is required before the decision.

### Contradiction ambiguity

Different native fields may appear inconsistent without proving the decision variable `contradictory=true`. A contradiction requires a predeclared semantic relation and comparison rule.

### Dataset dependency masquerading as replication

Two publications may share a testbed, simulator, collection campaign, or derived dataset. Counting them as independent sources can overstate cross-testbed support.

Study 9 records source dependencies and excludes shared-provenance derivatives from the primary independent comparison unless dependence is modeled explicitly.

### Analyst degrees of freedom

Post-result changes to mappings, derivation rules, candidate datasets, or action-completion logic can create narrative bias. The protocol therefore freezes source selection, schema identity, mapping rubric, and derivation rules before endpoint inspection.

## Adversary boundary

Study 9 does not model an adaptive attacker optimizing against the recovery selector.

Included source datasets may contain attacks created by their original authors, but Study 9 does not claim to reproduce those attacks, measure attacker success, or estimate real-world adversary prevalence.

The semantic analysis allows the conceptual possibility that evidence is stale, untrusted, incomplete, contradictory, unauthorized, or otherwise insufficient. It does not create forged signatures, compromise cryptographic keys, interact with operational spacecraft, or target external systems.

## Failure-safe interpretation

When a native source cannot establish a required value, Study 9 preserves uncertainty rather than silently assigning a value.

The analysis may therefore produce large admissible action sets, persistent ambiguity, or no meaningful direct coverage. Those outcomes are scientifically acceptable and must not be converted into synthetic certainty for publication convenience.

## Out of scope

The following are outside this phase and outside the primary Study 9 threat model:

- intrusion-detector training or benchmarking;
- adversarial machine learning;
- RF attack execution;
- spacecraft command transmission;
- credential use or authentication against third-party infrastructure;
- cryptographic attack implementation;
- on-orbit validation;
- mission-specific safety certification;
- operational response automation.

## Current execution boundary

This document defines design assumptions only. No dataset ingestion, executable mapping implementation, row-level analysis, or canonical experiment is authorized yet.
