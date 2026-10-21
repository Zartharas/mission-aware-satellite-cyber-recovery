# S4X-JCU-001 Protocol Draft R1

**Working title:** Joint Compromise and Unavailability Robustness for Recovery-Evidence Quorums  
**Status:** `OPTIONAL_PROTOCOL_DRAFT__HOLD__NO_EXECUTION_AUTHORIZED`

## Motivation

Study 4 evaluates malicious compromise and benign producer unavailability in separate exact blocks. It does not evaluate states in which compromised and unavailable producers coexist.

## Candidate state model

Retain the seven registered producer identities and frozen 3/2/2 synthetic provenance-domain mapping only as a reference configuration.

For an extension safety block, each producer may be:

- `HONEST_AVAILABLE`;
- `COMPROMISED_AVAILABLE`;
- `UNAVAILABLE`.

Under hidden authorization=false:

- honest available producer -> false claim;
- compromised available producer -> false-but-valid `authorization=true` claim;
- unavailable producer -> no claim.

For seven producers, the complete three-state population contains `3^7 = 2,187` producer states per rule. Across the existing 18 rule forms this would yield `39,366` exact rule-state evaluations.

These are planned design quantities, not results.

## Candidate endpoints

- unsafe qualification;
- first unsafe boundary conditional on unavailable count;
- systematic unsafe boundary conditional on unavailable count;
- provenance-domain occupancy of compromised available producers;
- exact rule-state failure maps.

## Design caution

Proceed only if the Study-4 analytical generalization leaves a material unanswered question. Do not run merely to enlarge the observation count.

A hidden-authorization=true adversarial-denial block would require new compromise semantics and is not authorized by this draft.
