# Study 2 — Security-Assurance Foundation

**Status:** `ASSURANCE_FOUNDATION_CI_VALIDATED_NOT_RUNTIME_AUTHORIZED_NOT_FROZEN`

This directory starts a new, isolated research track for **adversarial evidence-aware cyber response and trusted recovery**. It is intentionally separate from the frozen Study-1 campaign and its Zenodo evidence-of-record.

## Scientific boundary

This foundation does **not**:

- alter the 720 VALID / 9 retained INVALID Study-1 observations;
- consume Study-1 or Study-2 campaign seeds;
- execute NOS3/cFS campaign runtime;
- modify frozen Study-1 policy P7, event T1 semantics, results, ledgers, or statistical artifacts;
- authorize a Study-2 empirical campaign;
- claim operational-spacecraft, RF, flight, hardware-root-of-trust, or standards-conformance validation.

The Study-1 T1 treatment remains exactly what it was: omission/reduction of selected policy-visible evidence. Study-2 evidence states V2-V5 are prospective new mechanisms and must never be retroactively attributed to Study 1.

## Validated foundation checkpoint

The first Dockerized assurance checkpoint was validated on implementation commit `e2462edda703f12fac3245a384344ceb50cafc47` by GitHub Actions run `33467447178` / job `99730137920`.

The validated checkpoint established:

- 48/48 frozen Study-1 P7 combinations conformed to the independent baseline;
- the policy remained unchanged after synthetic mutation of experiment ground truth;
- 9 evidence-verification tests and 4 trusted-recovery-gate tests passed;
- 5 explicitly discovered Hypothesis property tests passed;
- the Study-1 P7 TLA+ abstraction completed with 48 distinct states and no error;
- the trusted-recovery TLA+ model completed with 385 distinct states and no error;
- validation produced zero tracked-file drift.

These are assurance-validation results, not Study-2 empirical campaign observations.

## First security milestone

The initial implementation adds four assurance layers before any new campaign is allowed:

1. **Authenticated evidence claims** — canonical synthetic evidence claims signed with Ed25519 and verified against an explicit source-key registry.
2. **Decision eligibility checks** — source trust, signature integrity, wall-clock freshness, expected recovery epoch, and strictly increasing per-source/per-epoch sequence state must all pass.
3. **Evidence-qualified trusted recovery** — applicable recovery criteria must be current, authenticated, trusted, non-contradictory, and satisfied; residual unauthorized state blocks trusted recovery.
4. **Independent conformance/formal checks** — the finite frozen Study-1 P7 state space is checked against an independently encoded baseline, while TLA+ models check control-plane invariants.

This is a researcher-controlled security prototype. The signature layer is **inspired by** the separation of evidence, verification, and relying-party decisions in remote-attestation architectures such as RFC 9334, but it is not an implementation of a hardware attester, EAT, TPM, or a claim of RFC conformance.

## Prospective Study-2 evidence treatments

These identifiers are design vocabulary only until a later protocol freeze:

| ID | Meaning |
|---|---|
| `V0` | complete/current evidence |
| `V1` | omitted evidence |
| `V2` | stale or replayed evidence |
| `V3` | contradictory independent evidence |
| `V4` | deliberately manipulated policy-visible value |
| `V5` | partial evidence-plane compromise with an independent trust source retained |

The implementation deliberately distinguishes **authenticity**, **trust**, **freshness**, **epoch membership**, **sequence monotonicity**, **consistency**, and **criterion satisfaction**. A valid signature by itself does not make evidence suitable for a recovery decision.

## Prospective bounded adversary budgets

These are not runtime treatments yet:

- `A0`: no evidence-plane compromise;
- `A1`: one policy-visible evidence producer controlled;
- `A2`: one evidence producer controlled plus modeled contact unavailability;
- `A3`: multiple policy-visible producers controlled while an independently designated verifier/trust anchor remains outside the adversary budget.

Exact capabilities, knowledge, timing, and exclusions must be frozen before empirical use.

## Trust architecture

```text
Synthetic evidence producer / future attester
        |
        v
canonical claim + signature + epoch + sequence + provenance
        |
        v
Study-2 verifier
  - source key known?
  - source trusted?
  - signature valid?
  - claim current?
  - expected epoch?
  - sequence newer?
  - independent-source contradiction?
        |
        v
AttestationResult / verified policy-visible evidence
        |
        v
Trusted-recovery relying gate
        |
        +----> allow only when all applicable criteria are verified
        |
        +----> fail closed otherwise

Independent experiment ground truth / adjudication oracle
        X  (must remain unavailable to the runtime policy)
```

## Docker validation

From the repository root:

```bash
docker build --file study2/Dockerfile --tag satellite-study2-assurance .
docker run --rm satellite-study2-assurance
```

The image performs only assurance validation:

- Python compilation;
- frozen Study-1 P7 conformance enumeration;
- deterministic and property-based Study-2 security tests;
- TLA+ parsing/model checking of the Study-1 P7 abstraction and trusted-recovery control plane.

It contains no command that launches a Study-1 or Study-2 NOS3/cFS campaign.

## Formal models

`formal/Study1P7.tla` independently encodes the finite Study-1 P7 decision semantics and checks:

- type safety;
- oracle isolation;
- evidence-assessment conformance;
- delegated-policy/action conformance.

`formal/TrustedRecovery.tla` checks:

- oracle isolation;
- immutable ground-truth token;
- evidence-sufficient versus fallback branch integrity;
- trusted-recovery soundness: qualified evidence, authorization, no residual unauthorized state, and the evidence-sufficient path are all required.

The models are assurance artifacts, not empirical outcomes. Any later Study-2 extension must be implementation-traced and receive new identifiers rather than silently redefining Study-1 semantics.

## Next gates before Study-2 runtime

The next work packages are deliberately sequential:

1. implement V0-V5 treatment generation and bounded adversary budgets;
2. implement new Study-2 baselines and selector ablations under new identifiers;
3. add matched benign-fault/adversarial ambiguity fixtures;
4. add mutation testing that must detect weakened evidence/authentication/recovery gates;
5. freeze RQs, estimands, exact cells, seed count, adversary knowledge, validity/INVALID rules, censoring, and analysis plan;
6. record source/config hashes and explicit runtime authorization;
7. only then execute a new Study-2 campaign in a separate experiment ID, seed namespace, ledger, evidence tree, analysis package, and archive.

HIL remains a later engineering-transfer study after the SIL cybersecurity analysis is frozen.
