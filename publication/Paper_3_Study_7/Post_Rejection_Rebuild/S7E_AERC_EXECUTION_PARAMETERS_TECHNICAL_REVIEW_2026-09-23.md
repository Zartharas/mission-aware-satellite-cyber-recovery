# S7E-AERC-001 Execution Parameters Technical Review — 2026-09-23

**State:** technical candidate only  
**Protocol/environment freeze:** NO  
**Canonical execution:** NOT AUTHORIZED

## Objective

Resolve the remaining reproducibility parameters before proposing any protocol/environment freeze.

The producer/qualifier cFS path is already runtime-green. The remaining open items are numeric logical-time freshness, epoch mapping, opaque registries, deterministic test-key provenance, and final F0-F12 byte/stage transforms.

## EP-1 — logical time and freshness

**Recommendation:** scenario-local logical ticks with `freshness_max_age_ticks=0`.

Nominal evidence is issued and evaluated at the same logical tick. F5/F6 retain the exact signed body and evaluate it one tick later.

This deliberately avoids choosing an arbitrary number of milliseconds/seconds when Study 7E is not measuring network latency. It makes freshness a controlled semantic factor:

- age 0: fresh;
- age ≥1 logical tick: stale.

This is not an operational spacecraft timing recommendation.

## EP-2 — evidence epoch

**Recommendation:** one constant `evidence_epoch=1` for the protocol/environment/key-registry freeze candidate.

Scenario identity is already signed separately, so a scenario-specific epoch adds no useful protection and could encode experimental structure.

The epoch changes only if the signed-evidence schema, key registry, or frozen execution contract changes before canonical execution.

This also makes F9 deterministic: byte 47 is the least-significant epoch byte; XOR `0x01` maps epoch 1 to 0 after signing, producing both signature invalidity and epoch invalidity.

## EP-3 — opaque numeric registries

**Recommendation:** domain-separated SHA-256 → unsigned 32-bit big-endian IDs with deterministic retry on zero/collision.

Material:

`S7E-AERC-001|<namespace>|<label>|<retry>`

Labels are processed lexicographically within each namespace.

The current 280 prospective scenario labels are collision-free with retry 0. The same holds for the three aliases in each trust-domain namespace.

Example scenario mappings:

- `TR1-001 → 0x408AB824`
- `TR0-001 → 0xAF8B82F8`
- `E1-001 → 0xB80D472F`
- `E2-001 → 0x25165261`
- `C0-001 → 0x71D8655F`

The registry mapping remains research-side provenance. Policies never receive topology/fault labels.

## EP-4 — deterministic test-key provenance

**Recommendation:** reproducible, non-secret Ed25519 research fixtures derived only in the host signing harness.

For each key-domain alias:

`seed = SHA256("S7E-AERC-001|ED25519-TEST-SEED-V1|" + key_domain_alias)`

The three key domains are:

- `shared:key`
- `primary:key`
- `corroborator:key`

No persistent private-key files are required. The host harness derives the seed/key pair on demand and wipes seed/secret-key memory after signing. cFS receives only the public-key registry.

These are **non-secret test fixtures**, not operational key-management material. F3/F4 model controlled signing capability for the affected domain; they do not claim to simulate discovery of a high-entropy operational secret.

## EP-5 — F0-F12 byte/stage transformations

**Recommendation:** carry the currently approved pre-canonical transformations forward unchanged as the final transform-freeze candidate.

In particular:

- F9: post-signature XOR `0x01` at byte 47;
- F11: authority false-output stage first, then F9 transport mutation;
- F12: two separately signed same-sequence bodies with opposite authorization.

The current transform draft has already passed host contract tests and the producer/qualifier cFS runtime gate.

## Adversarial review

The candidate includes these safeguards:

- 32-bit truncation is never accepted without collision/zero detection;
- changing labels or registry inputs after freeze requires a new freeze candidate;
- epoch is constant and therefore cannot encode fault/topology/block;
- freshness does not depend on machine scheduling or wall-clock jitter;
- deterministic test seeds are explicitly non-secret and prohibited for production/operational use;
- no private signing material enters cFS binaries;
- no proposal here authorizes L0/L1 training, protocol freeze, environment freeze, canonical execution, or PR merge.

## Requested author decisions

The next approval package is deliberately compact:

- **EP-1:** approve logical-tick freshness with max age 0;
- **EP-2:** approve constant evidence epoch 1;
- **EP-3:** approve SHA-256-derived opaque registries;
- **EP-4:** approve deterministic non-secret host-only test-key fixtures;
- **EP-5:** approve the current F0-F12 transforms as the final transform-freeze candidate.

Approval of EP-1 through EP-5 would authorize preparation of a protocol/environment **freeze candidate**, not canonical execution.
