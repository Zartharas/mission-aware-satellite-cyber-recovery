# Study 3 — Temporal Trust Qualification Under Intermittent Contact

**Experiment ID:** `S3-K4E-001`  
**Status:** `DESIGN_AND_IMPLEMENTATION_CANDIDATE_NO_CAMPAIGN_RESULT_YET`  
**Relationship to prior work:** separate follow-on study; Study 1 and Study 2 remain frozen and are never pooled with this population.

## Research question

Study 2 established two separate boundaries: intermittent/flapping contact (`K4`) changes response timing/authorization behavior, and bounded producer compromise (`V5`) can make authenticated/current policy-visible evidence false relative to research-only adjudication truth. Study 3 asks the temporal interaction question that Study 2 did not instantiate:

> When contact repeatedly disappears and returns, how long and how often can post-signature manipulation (`V4`) or a compromised evidence producer (`V5`) create unsafe permissive action or false evidence-qualified recovery, and how do the frozen B0/B2/S1 policy semantics differ across those repeated contact transitions?

This is not an appended Study-2 block. It is a separately identified finite-state trajectory study using Study-2 semantics as hash-bound design inputs.

## Why a new temporal model is required

The frozen Study-2 runtime re-evaluates future-contact recovery only for Block B and regenerates clean current evidence at the next modeled contact. Merely assigning `K4` to a `V4`/`V5` Study-2 cell would therefore not instantiate persistent or one-shot adversarial evidence across repeated contact transitions. Study 3 introduces a stateful evidence cache/transport layer while preserving the frozen Study-2 definitions themselves unchanged.

## Frozen candidate design

- logical horizon: 0–240 s;
- decision epochs: every 5 logical seconds;
- evidence validity: 5 logical seconds;
- contact regimes:
  - `K0`: continuously available `[0,240]`;
  - `K4`: `[25,35]`, `[75,90]`, `[145,165]`, `[220,240]`;
- evidence conditions:
  - `V0`: truthful current authorization evidence;
  - `V4`: authorization claim value changed after signing, producing an invalid signature;
  - `V5`: compromised producer signs the false authorization value with its valid key;
- attack persistence:
  - `ONE_SHOT`: only the first received authorization claim at/after onset is affected;
  - `PERSISTENT`: every received authorization claim at/after onset is affected;
- policies: frozen semantic copies of `S2_B0_FAIL_CLOSED`, `S2_B2_RISK_THRESHOLD`, and `S2_S1_EVIDENCE_AWARE`;
- onset phases: every 5 s from 10 through 235 inclusive (46 phases).

The underlying authorization prerequisite is true before the onset phase and false from onset through the end of the trajectory. `V0` reports that change truthfully; `V4` and `V5` alter only the policy-visible authorization evidence according to the treatment definitions. The research-only hidden truth is never a selector input.

### Exact trajectory population

`V0` has no persistence dimension: `2 contacts × 1 evidence × 3 policies × 46 onset phases = 276 trajectories`.

`V4`/`V5`: `2 contacts × 2 evidence conditions × 2 persistence modes × 3 policies × 46 onset phases = 1,104 trajectories`.

**Total planned finite population: 1,380 trajectories.**

There are no random campaign seeds. The onset-phase grid is exhaustively enumerated; repeating deterministic trajectories under arbitrary seed labels would create pseudo-replication. Decision epochs inside one trajectory are repeated states, not independent observations.

## Primary endpoints

1. `unsafe_permissive_epoch_rate` — fraction of post-onset decision epochs where the selected action is permissive while hidden authorization is false.
2. `unsafe_qualified_epoch_rate` — fraction of post-onset epochs where the recovery gate is policy-visible qualified while hidden authorization is false.
3. `unsafe_qualified_exposure_s` — logical exposure duration represented by unsafe-qualified epochs × 5 s.
4. `unsafe_qualified_episode_count` — number of distinct false-qualification episodes after onset.
5. `protective_epoch_rate` — post-onset fraction in `HOLD_AND_REQUIRE_EVIDENCE` or `RESTRICT_AND_REQUEST_AUTHORIZATION`.
6. `action_transition_count` — number of post-onset policy-action transitions.

The second endpoint is intentionally distinct from Study-2 unsafe-permissive classification. It measures false trust qualification at the recovery gate rather than merely selection of a permissive action.

## Analysis

The 46 onset phases are an exhaustive finite grid under the frozen 5-second model, not a random sample of real orbital timing. Primary summaries are exact finite-grid means/proportions and paired phase-wise differences. No p-value is needed to describe this finite model population and no weighted global policy score/rank is allowed.

## Assurance properties

The implementation validator must exhaustively establish:

1. hidden authorization truth is never used by the selector;
2. no unsafe-qualified epoch occurs before the onset phase;
3. truthful `V0` cannot produce an unsafe-qualified epoch after onset;
4. an affected `V4` record cannot qualify because its signature is invalid;
5. a `V5` affected record can qualify only when it is present, fresh, and signed by the compromised-but-still-trusted producer;
6. `K4` never receives a new record outside its frozen contact windows;
7. one-shot treatment affects exactly one received post-onset record when such a record exists;
8. every declared cell × onset phase produces exactly one terminal trajectory summary;
9. the selector receives only policy-visible evidence/contact/security state;
10. Study-1/Study-2 files are read-only dependencies and are not modified by Study-3 execution.

## Responsible-research boundary

Study 3 is a deterministic software model. It uses no operational spacecraft, ground station, RF transmission, real credential, intercepted telemetry, proprietary data, production signing key, or third-party system. Its cryptographic states are abstract booleans reproducing the already frozen Study-2 distinction between detectable post-signature tampering and a compromised trusted producer.

## Interpretation limits

Logical seconds are not orbital-access, network, operator, or spacecraft latency. `K4` is the frozen synthetic flapping profile reused as an experimental schedule, not a claim about a particular orbit. `V5` assumes producer-key control and does not identify how that compromise occurred. A finite phase sweep establishes behavior of this model only; it does not estimate the frequency of these conditions in operational missions.
