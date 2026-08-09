# WP4 Passive Time-Witness Runtime-Candidate v3 Combined Implementation

Decision: D-063R2-C3B-I2C
Predeclared record path date: 2026-08-03
Governance reconciliation date: 2026-08-07
Status: IMPLEMENTED_PENDING_STATIC_VERIFICATION

## Scope

This record reconciles the already-reviewed and merged v3 combined implementation into the separately governed contract 0.4.12 implementation state required by D-063R2. It does not execute the complete v3 static verifier, does not create a static PASS or FAIL disposition, does not authorize D-064, and does not authorize or execute runtime.

Merged main identity: `6fa928108ac744ab5b2acd56dc6c39fbb861c2a2`

The eight existing implementation artifacts listed below remain byte-identical to the reviewed merged state. This reconciliation creates this implementation record and its lock and advances governance state only.

## Frozen combined implementation package

| # | Path | Role | SHA-256 / disposition |
|---|---|---|---|
| 1 | `configs/downlink-diagnostic-contract.json` | governed contract | `FINAL_0_4_12_BYTES_BOUND_BY_GOVERNANCE` |
| 2 | `manifests/nos3-runtime-material-manifest.json` | canonical runtime-material manifest | `5026176de3084c8015fd7f84827ce8a4e5d44df7e986bc142815eb0d649e81cd` |
| 3 | `scripts/nos3_runtime_material.py` | retained materialization core | `37c2a033f8b0fb0de17d1940c1cc12c13c52de4ec415a0e4afa16cb7dbc9e51c` |
| 4 | `scripts/nos3_runtime_transaction_v1.py` | process-boundary transaction tool | `0d2e76aab5b9e604b632f19caf2f2c9b584b191c9b7fafaff9bd1ae0d9ecff83` |
| 5 | `scripts/passive_nos_engine_time_witness.cpp` | passive time witness source | `830cd1a3e336c7ed2fe5c6755a30ee24b5bbc04106d3c14f2a9d26995adaaf7e` |
| 6 | `scripts/validate_passive_time_witness_trace.py` | trace validator | `f75131770ab9020c8c2dfb41102121e12ffd664c02a8a2e03bd8aa8c7b8d9027` |
| 7 | `scripts/radio_socket_metadata_shim.c` | socket metadata shim source | `d15ede657230560178b5648ef5d4e15b1965837a1c384790d9cbd3dc8f01ee1b` |
| 8 | `scripts/prepare_passive_time_witness_runtime_candidate_v3.sh` | v3 generator | `e3b1f8922161116e3ecfc1355900b72311d2834f5617b7a4956ccae4f6e50153` |
| 9 | `scripts/verify_passive_time_witness_runtime_candidate_v3_static.sh` | v3 static verifier implementation (retry source-corrected binding plus generator-stage deterministic failure observability) | `da7d16d75d962d19997834d0c526298e7de74ef2250143667602fedaac932dca` |
| 10 | `tracker/WP4_PASSIVE_TIME_WITNESS_RUNTIME_CANDIDATE_V3_COMBINED_IMPLEMENTATION_20260803.md` | combined implementation record | `SELF_GOVERNED_BELOW` |
| 11 | `artifacts/wp4-passive-time-witness-runtime-candidate-v3-combined-implementation-lock.txt` | combined implementation lock | `SELF_GOVERNED_BELOW` |

Combined implementation package file-set count: 11.

## Governed implementation identities

- Proposed v3 candidate SHA-256: `599c534df37b127f7325ad513eecc4b24bdc0d37a56c32b4448a0b0099c13a1f`
- Canonical manifest SHA-256: `5026176de3084c8015fd7f84827ce8a4e5d44df7e986bc142815eb0d649e81cd`
- Runtime material core SHA-256: `37c2a033f8b0fb0de17d1940c1cc12c13c52de4ec415a0e4afa16cb7dbc9e51c`
- Runtime transaction tool SHA-256: `0d2e76aab5b9e604b632f19caf2f2c9b584b191c9b7fafaff9bd1ae0d9ecff83`
- Witness source SHA-256: `830cd1a3e336c7ed2fe5c6755a30ee24b5bbc04106d3c14f2a9d26995adaaf7e`
- Trace validator SHA-256: `f75131770ab9020c8c2dfb41102121e12ffd664c02a8a2e03bd8aa8c7b8d9027`
- Socket shim SHA-256: `d15ede657230560178b5648ef5d4e15b1965837a1c384790d9cbd3dc8f01ee1b`
- Generator SHA-256: `e3b1f8922161116e3ecfc1355900b72311d2834f5617b7a4956ccae4f6e50153`
- Static verifier SHA-256: `da7d16d75d962d19997834d0c526298e7de74ef2250143667602fedaac932dca`
- Baseline contract SHA-256: `86d365fe08d7ee177e74192cead71dc366e9c546e81668261c770350003e37ca`
- NOS3 commit: `5a3bdee6be9a2c67fdf994ae6db56d5c60395302`
- Fortytwo commit: `eda252bf31f27850e867e698cfdd963e143ead1f`
- Fortytwo executable SHA-256: `9c0062d2a447a6340e7c191850ff952d3f8768dd307e3e7fb141e777961e60c7`
- Pinned OCI image: `ivvitc/nos3-64@sha256:06aa945988a7770b759022c2e1f6f2531818c087fe41a4739d3a3a7f2a9dcce2`

## Implementation-phase validation disposition

- Generator Bash syntax: PASS.
- Verifier Bash syntax: PASS.
- Verifier embedded Python syntax compilation: PASS.
- Deterministic double candidate emission: PASS.
- Both emitted candidates matched `599c534df37b127f7325ad513eecc4b24bdc0d37a56c32b4448a0b0099c13a1f`.
- Candidate Bash syntax: PASS.
- Candidate source-only authorization/order review: PASS.
- Candidate execution attempts: 0.
- Complete v3 verifier `--verify` executions: 0.
- Production materialization attempts: 0.
- Real Docker/NOS3/Fortytwo runtime invocations: 0.

## Required post-implementation state

- Contract version: `0.4.12`.
- v3 implementation status: `IMPLEMENTED_PENDING_STATIC_VERIFICATION`.
- v3 static verification: `PENDING`.
- proposed_runtime_entrypoint_v3_sha256: `599c534df37b127f7325ad513eecc4b24bdc0d37a56c32b4448a0b0099c13a1f`.
- accepted_runtime_entrypoint_v3_sha256: empty.
- diagnostic_runtime_authorized: false.
- diagnostic_runtime_attempts_authorized: 0.
- D-064: `BLOCKED`.
- Scientific, baseline, command-transmission, event-injection, and cryptographic-semantics permissions: false.

The next governed phase is the separate v3 static-verification disposition under contract 0.4.13. A future static PASS may only make D-064 ready for separate consideration; it does not itself authorize D-064 or runtime.

## C3B-I2D corrected-verifier identity reconciliation — 2026-08-08

- The C3B-I2C implementation originally bound verifier SHA-256 `6556a4bbd01f46d11dd35abe420b3fbaaaab417339d6aa7d21040ca47f665ad9`.
- That original verifier remains preserved in Git history and in the retained first complete verifier execution, which terminated as `INVALID_EXECUTION` with `verifier_rc=1`; it did not establish static PASS or FAIL.
- Retained invalid raw-log SHA-256: `a4a131c710e894ebdf8e29116ff4a08cb69351102d935c4f9ade1ef7586b06fb`.
- The diagnostic classified the cause as `SOURCE_DEFECT_PRODUCTION_FIXTURE_SCHEMA_GAP` (`base_fixture` omitted `scientific`, `baseline`, `command`, `event`, and `crypto`).
- The corrected verifier was independently reviewed with zero findings and published on `main` at commit `659ad0e3fb9ce79efe9c513279e145840ed9939e`.
- Corrected verifier SHA-256: `49b12d8e8c66441b4d97580ce398dcf943348038ebff42db847c8c0a630a82e2`.
- This reconciliation updates only the verifier identity and associated governance provenance inside the existing contract `0.4.12` implementation state.
- Aggregate complete production `--verify` executions before any corrected retry: `1` (the retained historical invalid execution).
- v3 static verification remains `PENDING`.
- `accepted_runtime_entrypoint_v3_sha256` remains empty.
- Runtime authorization remains false; runtime attempts remain `0`; D-064 remains `BLOCKED`.
- No candidate execution, production materialization, Docker/NOS3/Fortytwo runtime, or scientific outcome is authorized or performed by this reconciliation.

## C3B-I2D retry-verifier source correction and active identity reconciliation — 2026-08-08

- The previously corrected verifier SHA-256 `49b12d8e8c66441b4d97580ce398dcf943348038ebff42db847c8c0a630a82e2` remains preserved as historical provenance and was the verifier used by the separately authorized corrected complete production retry.
- That corrected retry returned `verifier_rc=4` at the identity-control gate before candidate source scanning; it established neither static PASS nor static FAIL and established no accepted candidate static finding.
- Aggregate complete production `--verify` executions are now `2`: one historical invalid `rc=1` execution plus one corrected retry `rc=4` execution.
- The retained retry-verifier defect root cause is `PRODUCTION_PROPOSED_CANDIDATE_ACTUAL_RESOLVER_USES_SYNTHETIC_FIXTURE_AND_GENERIC_T036_MASKS_FAILED_IDENTITY_CONTROL`.
- The source correction binds production `IDC_PROPOSED_CANDIDATE` to SHA-256 of the exact supplied candidate file bytes and emits control-specific stable identity failure IDs; `T036` remains reserved for unresolved verifier-self placeholder state.
- Corrected source validation retained `SELFTEST passed=78 failed=0 skips=0`.
- The source-correction implementation was independently reviewed with `finding_count=0` and disposition `ACCEPTED`.
- The retry-source-corrected verifier SHA-256 is `238724221f595e81d52283345f3eb6e79404a0e49bfcc56fb463203ac88c6ee7` and was published on `main` at commit `5045d734d876d3e1a6ee2d322fae121d536f7382`.
- This six-file reconciliation updates the active verifier identity and aggregate complete-verifier execution count while preserving the original `6556...` verifier, the first invalid execution, the prior `49b12d8e8c66441b4d97580ce398dcf943348038ebff42db847c8c0a630a82e2` corrected verifier, and the corrected retry `rc=4` as historical evidence.
- Contract version remains `0.4.12`; v3 static verification remains `PENDING`; `accepted_runtime_entrypoint_v3_sha256` remains empty.
- Candidate execution attempts remain `0`; production materialization attempts remain `0`; real Docker invocations remain `0`.
- Runtime authorization remains false; runtime attempts remain `0`; D-064 remains `BLOCKED`.
- No production `--verify`, verifier selftest, candidate execution, materialization, Docker/NOS3/Fortytwo runtime, static disposition, candidate acceptance, or scientific outcome is authorized or performed by this reconciliation.
- Independent review of this six-file governance reconciliation is required before publication or any further production static-verification authorization.

Retained provenance bindings:
- Retry execution state SHA-256: `96cb9329d6f8fd9752de17ae1ac89bd901515b61a01387d280c3c228bbc537ee`.
- Retry-verifier defect diagnostic report SHA-256: `96a9fa602983705ad890e93cbd89bd6bb88036cddd94e3ccd4683803aa488ce2`.
- Source-correction implementation report SHA-256: `30674254b82bcacc37266f9d5ec20dfd727f70c427b579cf31143e0fecab2f0e`.
- Source-correction independent-review report SHA-256: `f64b69f789d0bc1e48d062151b8c377f6b1b44737d1028faaadfe73be80338c6`.
- Source-correction publication report SHA-256: `cee9f932318c33e405bb6ffdb4f70515ac9eea91bc1c20b827d8c46cde7346d2`.
- Governance-reconciliation preparation report SHA-256: `384eb8e316698c2577a73147ddef01394ccab6e3b86b39f3055b5964cd4090a9`.

## C3B-I2D generator-stage observability correction and VR4 governance reconciliation — 2026-08-08

- Decision: `D-063R2-C3B-I2D-VR4`.
- The previously active retry-source-corrected verifier SHA-256 `238724221f595e81d52283345f3eb6e79404a0e49bfcc56fb463203ac88c6ee7` remains preserved as historical provenance.
- Production verifier execution #3 used `238724221f595e81d52283345f3eb6e79404a0e49bfcc56fb463203ac88c6ee7`, returned `rc=4`, and is retained as `INVALID_EXECUTION_NO_STATIC_DISPOSITION`.
- Execution #3 reached neither candidate source scanning nor a candidate static finding; it established neither static PASS nor static FAIL.
- Aggregate complete production `--verify` executions are reconciled from `2` to `3`.
- Production executions using `238724221f595e81d52283345f3eb6e79404a0e49bfcc56fb463203ac88c6ee7` are reconciled from `0` to `1`.
- The generator-stage observability correction adds six stable generator-stage failure identifiers only; behavioral gate change count is `0`.
- The observability-corrected verifier retained `SELFTEST passed=78 failed=0 skips=0`.
- Independent source review reported `source_finding_count=0` and disposition `ACCEPTED`.
- The observability-corrected verifier SHA-256 is `da7d16d75d962d19997834d0c526298e7de74ef2250143667602fedaac932dca` and was published on `main` at commit `d4466c2c1a117cdd3354a35f4a5749bbdd61266f`.
- Production executions using `da7d16d75d962d19997834d0c526298e7de74ef2250143667602fedaac932dca` remain `0`.
- Contract version remains `0.4.12`; static verification remains `PENDING`; `accepted_runtime_entrypoint_v3_sha256` remains empty.
- Candidate execution attempts remain `0`; production materialization attempts remain `0`; real Docker invocations remain `0`.
- Runtime authorization remains false; runtime attempts remain `0`; D-064 remains `BLOCKED`.
- No production `--verify`, verifier selftest, generator execution, candidate execution, materialization, Docker/NOS3/Fortytwo runtime, static disposition, candidate acceptance, or scientific outcome is authorized or performed by this reconciliation.
- Independent review of the six-file VR4 governance reconciliation is required before publication or any later production static-verification authorization.

Retained VR4 provenance bindings:
- Execution #3 result SHA-256: `197dfc9bbedb5ca3df3faa99c71f82966308884ef2772bf46f628bb707962999`.
- Execution #3 independent result-review SHA-256: `58818f25eb7ad4084054e3eae1ca84eb32d933229201e137f3343e1e8c2a3947`.
- Observability-correction implementation R3 report SHA-256: `4b90843aee71ca6c559637d10153c944cd64900ee5f986a66a8d5473adec68d3`.
- Observability-correction independent-review R2 report SHA-256: `6fd3dbce46cd76f10d580f2cfb56f76fe78d20162362b3e6379ca0074eedfd88`.
- Observability-correction publication report SHA-256: `684e676f95ba60d2a662e83469edca8bb7156b448b15b8fba61583de406dba65`.

## C3B-I2D VR5 coordinated generator/verifier correction and execution #4 reconciliation

- Decision: `D-063R2-C3B-I2D-VR5`.
- Corrected active v3 generator SHA-256: `7140b7ff1aa1873ac020bae24d2a921a343f3d1fde86c6bbb4aece45cf229812`.
- Corrected active static verifier SHA-256: `1a7db020a08beca3448c484273595bfa769112ad1fd2a66d73094c37a8d88fa2`.
- Execution #4: `INVALID_EXECUTION_NO_STATIC_DISPOSITION`.
- Execution #4 failure ID: `SVF_C3B_I2D_GEN_001_PROCESS_NONZERO`.
- Accepted root cause: `V3_GENERATOR_SOURCE_API_COMPATIBILITY_DEFECT`.
- Accepted source finding: `SOURCE_DEFECT_V3_GENERATOR_PATHLIB_WRITE_TEXT_NEWLINE_COMPATIBILITY`.
- Aggregate complete production verifier executions: `4`.
- Corrected-verifier production executions represented by execution evidence: `1`.
- Candidate source scan reached: `false`.
- Candidate failure established: `false`.
- Static verification remains: `PENDING`.
- Runtime authorization remains: `false`.
- Runtime attempts remain: `0`.
- D-064 remains: `BLOCKED`.
- Production verifier rerun authorization remains: `false`.
