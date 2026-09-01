# Study 2 — Adversarial Evidence-Aware Security Research

**Status:** `PHASES_0_4_PRE_RUNTIME_PROTOCOL_FROZEN_RUNTIME_NOT_AUTHORIZED`

This directory is an isolated research track for **adversarial evidence-aware cyber response and trusted recovery under intermittent connectivity**. It is separate from the frozen Study-1 campaign and its Zenodo evidence-of-record.

## Scientific boundary

This work does **not** alter the 720 VALID / 9 retained INVALID Study-1 observations, consume Study-1 campaign seeds, rerun frozen Study-1 analyses, or redefine Study-1 T1. It does not execute an operational spacecraft, RF system, real ground station, real credentials, or classified/proprietary mission data. No Study-2 empirical campaign is authorized yet.

Study-1 T1 remains omission/reduction of selected policy-visible evidence only. V2–V5 are new Study-2 mechanisms.

## Phase 0 foundation boundary

The assurance foundation merged to `main` at `d3af5cec7a3862e84021335c5f36a6fe3be154d8`. Both actual post-merge `main` workflows succeeded: repository validation run `33516260188` and Study-2 assurance run `33516260189`.

The foundation retains authenticated Ed25519 synthetic evidence, explicit source trust, freshness, recovery epoch, per-source/per-epoch sequence monotonicity, contradiction detection, trusted-recovery gating, independent Study-1 P7 conformance, Hypothesis tests, TLA+ models, and a digest-pinned Docker assurance environment.

## Frozen Phase 1–4 protocol

Experiment ID: `S2-AEATR-001`

Machine-readable protocol: `STUDY2_PROTOCOL.json`

Canonical cell matrix SHA-256:
`5087e46f9d416fe5b741fedcb4b1a9d848342087c6e317614dec26a56c2dc081`

The pre-runtime design freezes:

- adversary classes A0–A3 and explicit trust/knowledge boundaries;
- evidence treatments V0–V5;
- contact identities K0–K4;
- matched benign/adversarial ambiguity families;
- Study-2-only fail-closed, fail-operational, risk-threshold, and evidence-aware baselines;
- security ablations for freshness, contradiction, epoch, and signature/trust checks;
- an independent research-only adjudication oracle unavailable to selectors;
- 85 exact cells and 3,872 target VALID observations;
- paired seed sets: 96 for the primary block and 32 for secondary blocks;
- invalid-run retention, no hidden retries, no post-hoc seed substitution, no outcome-dependent stopping, prespecified censoring/analysis rules, and no weighted global policy score.

The 96 primary seeds were selected prospectively from a worst-case Wilson 95% Bernoulli half-width <= 0.10 criterion; at n=96 the half-width is approximately 0.0981. The replication count was not copied from Study 1.

## Evidence semantics

| ID | Study-2 meaning |
|---|---|
| `V0` | complete/current evidence |
| `V1` | omitted evidence |
| `V2` | stale or replayed evidence |
| `V3` | contradictory independent evidence |
| `V4` | post-signature manipulation |
| `V5` | bounded partial evidence-plane producer compromise |

A valid signature is not treated as truth. In V5 a compromised producer may validly sign a false value. The research oracle used to adjudicate correctness remains unavailable to runtime policy logic.

## Bounded adversary model

- `A0`: no evidence-plane producer compromise;
- `A1`: exactly one policy-visible evidence producer controlled;
- `A2`: exactly one producer controlled plus modeled contact unavailability; K0 is prohibited;
- `A3`: at least two policy-visible producers controlled while the verifier and independent trust anchor remain outside the adversary budget.

Ground truth, the adjudication oracle, analysis controls, seeds, treatment identity, provenance controls, and verifier compromise are outside the permitted adversary budget.

## Hardened pre-runtime assurance checkpoint

Implementation commit `bfb5ee01ec4c9d0010330a12e3c5f76da6b90d48` passed the dedicated Study-2 GitHub Actions run `33536459043` / job `99951852211`. The same hardened head passed the exhaustive repository run `33536458895` / job `99951851674` with the frozen Study-1 research suite and WP10 reconstruction intact.

The hardened checkpoint establishes:

- 48 Study-1 P7 conformance cases;
- 41 deterministic Study-2 security/protocol tests;
- 8 Hypothesis property tests;
- 7/7 targeted semantic security mutants killed through production `verify_bundle()` and trusted-recovery-gate paths;
- explicit frozen scenario/adversary-budget identity binding;
- guaranteed V2 stale expiry or fail-closed rejection when the requested logical clock cannot represent expiry;
- V3/V5 sequence allocation above the signing source's current maximum in the same recovery epoch;
- Study1P7 TLA+: 48 distinct states;
- TrustedRecovery TLA+: 385 distinct states;
- AdversarialEvidence TLA+: 540 generated / 400 distinct states, depth 3;
- 611/611 frozen Study-1 research tests;
- frozen WP10 reproduction/regression PASS;
- zero tracked-file drift.

All four P1 review findings that prompted the hardening were addressed and resolved before merge eligibility. These are assurance/model-checking results, not empirical Study-2 campaign observations or proof of operational spacecraft security.

## Docker validation

From the repository root:

```bash
docker build --file study2/Dockerfile --tag satellite-study2-assurance .
docker run --rm satellite-study2-assurance
```

The image performs compilation, Study-1 P7 conformance, protocol/hash freeze checks, deterministic security tests, property tests, production-bound semantic mutation checks, and three TLA+ model checks. It contains no command that launches a Study-1 or Study-2 NOS3/cFS campaign.

## Next boundary

Phases 0–4 stop before empirical execution. Phase 5 must calibrate and freeze numerical SIL contact/time horizons, freeze exact runtime/container/configuration hashes, validate the campaign runner using development-only fixtures, and create an explicit runtime-authorization checkpoint. Until then:

`study2_campaign_runtime_authorized = false`

`runtime_gate = CLOSED`
