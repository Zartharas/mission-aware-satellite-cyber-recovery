# WP4 D-064 V4 Source Implementation — 2026-08-10

**Decision:** `D-063R2-C3B-I2D-D064-V4-IMPL`
**Authorization:** `D-063R2-C3B-I2D-D064-SIA1`
**State:** `SOURCE_IMPLEMENTED_PENDING_INDEPENDENT_REVIEW_AND_PUBLICATION`

## Frozen implementation identities

- transaction-v2: `7419fa18b891ddc7525fa237b12323a092b9ece0f44d5b6fa4069c614322ce29`
- generator-v4: `5e7cec82032b16edc30a7c0f5d4bfe0a5ddb567ed6a13f6c3075f4db3c97f2a7`
- proposed deterministic candidate-v4: `b67ad4d03e04ca1e01d32b7869668c2d2be04c76f51017ec72a36f130527b7d7`
- verifier-v4: `ccc364c24a11092c2f11aed45636daaca813630745268ce0695d0b89184286f6`
- canonical manifest: `5026176de3084c8015fd7f84827ce8a4e5d44df7e986bc142815eb0d649e81cd`
- implementation-only contract `0.4.14`: `b1a4d16a22de4ee8420b23121ad17fa0a6a287b2dfbbc27ec931d001aedd4fe6`

## Validation performed within SIA1

- reviewed transaction-v2 identity preserved unchanged;
- generator-v4 Bash syntax passed;
- generator-v4 deterministic double emission matched byte-for-byte;
- candidate-v4 Bash syntax passed;
- candidate-v4 source-only V4/transaction-v2/receipt-control review passed;
- verifier-v4 Bash syntax passed;
- verifier-v4 synthetic selftest passed `10/0/0`;
- transaction-v2 synthetic selftest replayed `205/0/0` before the `0.4.13` → `0.4.14` contract transition;
- verifier-v4 selftest binds the exact reviewed transaction-v2 SHA plus V4 ACL/lock/evidence source semantics after the transition;
- no production candidate execution occurred;
- no production verifier `--verify` / Execution #11 occurred.

## Closed gates

- production candidate execution: **not authorized**
- production static verifier Execution #11: **not authorized**
- authorized-root selection/creation: **not authorized**
- retained host-exclusive-writer evidence creation: **not authorized**
- D-064: **not authorized**
- runtime: **not authorized**
- runtime attempts: **0**
- event injection / baseline / WP5 execution: **not authorized**

This record is an implementation-state artifact only. It makes no scientific,
mission-impact, generic-radio-defect, CryptoLib, SDLS, exclusive-host-writer,
or successful-runtime claim. Static verification for V4 remains `PENDING`.
