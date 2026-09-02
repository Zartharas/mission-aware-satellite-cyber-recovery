# Study 4 — Multi-Producer Evidence Quorum Thresholds

**Experiment ID:** `S4-MPQ-001`  
**Status:** `DESIGN_AND_IMPLEMENTATION_CANDIDATE_NO_CANONICAL_RESULT_YET`

Study 4 is a separate deterministic assurance study. Studies 1–3 remain frozen and are not pooled.

## Research question

When recovery authorization is supported by several independently signed evidence producers, how do absolute vote count and provenance-domain diversity change the safety threshold under bounded producer compromise and the availability cost under producer loss?

This is not a new Byzantine-consensus algorithm. It is a bounded recovery-evidence qualification study that applies simple q-of-N and provenance-diversity gates to the trusted-recovery problem exposed by Study 2 V5 and the temporal results of Study 3.

## Frozen candidate model

- 7 trusted evidence producers (`P1`–`P7`)
- 3 provenance domains: `D1={P1,P2,P3}`, `D2={P4,P5}`, `D3={P6,P7}`
- 18 rules: total-vote threshold `q=1..7`, with required provenance domains `d=1..min(3,q)`
- absolute thresholds are against the registered producer set, never relative to only the producers that happen to respond

### Safety block

Hidden authorization truth is false. A compromised producer remains trusted and can validly sign the false claim `authorization=true`; uncompromised producers truthfully sign false. Every compromise subset of the seven producers is exhaustively enumerated (128 subsets) for every rule.

Primary safety endpoint: `unsafe_qualified`, meaning the false authorization claim satisfies both the total-vote and provenance-diversity thresholds.

### Availability block

Hidden authorization truth is true. No producer is malicious; an affected producer is unavailable and every available producer truthfully signs true. Every unavailability subset (128) is enumerated for every rule.

Primary availability endpoint: `false_conservative`, meaning valid recovery authorization is rejected solely because the absolute quorum cannot be assembled.

## Population

`18 rules × 2 blocks × 128 subsets = 4,608 exact observations.`

The subset is the analytic unit. There are no random seeds and no Monte Carlo frequency claims.

## Threshold summaries

For each rule and block, the analysis reports:

- first-failure count/fraction: smallest affected-set size for which at least one subset fails;
- systematic-failure count/fraction: smallest affected-set size for which every subset of that size fails;
- exact subset failure rate at every affected count.

No p-value, weighted score, or global policy rank is used.

## Responsible-research boundary

The model is combinatorial and synthetic. It contains no real spacecraft topology, credentials, keys, IPs, ground infrastructure, exploit path, or targeting information. “Compromise” is represented only as a boolean ability of a registered producer to sign a false authorization claim with its modeled trusted identity.
