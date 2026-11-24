# P2X pre-execution approval and cross-paper evidence firewall (2026-10-03)

## Distinctness
- Paper 1 Studies1+2 and historic NOS3 P7: reuse the **pinned simulator infrastructure only**, not its policy code, outcomes, table results, traces or experimental populations. Implement a new ground qualification gate, evidence adapter and scenario controller with unique output root `paper2x/results/P2X-NOS3-RG-001/` (ignored/protected until release authorization).
- Paper 2 frozen Studies3/4/6 plus S3X/S6X: retain all old IDs, source records, findings and campaign directories as immutable. CAL1's old S6X fault *type* can sanity-check integration but its observations/hashes do not enter the primary estimand.
- Paper 3 Studies7+7E: no learned-selector benchmark or migration.
- Paper 4 Studies8+8E: no PQC/SatNOGS or OPS-SAT trace rows.
- Paper 5 Study9 / Study5 CuCD-ID: no dataset row migration. Published CuCD-ID/NOS3 may demonstrate methodological precedent only.

## Phase A — source and transport baseline (requires separate bounded approval)
1. Verify precise existing source lock with `scripts/verify_nos3_source_lock.sh`, local checkout `5a3bdee6be9a2c67fdf994ae6db56d5c60395302`, recursive cFE/OSAL/PSP submodules, and image digest `ivvitc/nos3-64@sha256:06aa945988a7770b759022c2e1f6f2531818c087fe41a4739d3a3a7f2a9dcce2`. Fail rather than silently switch to current main/another image.
2. Confirm actual version and readiness of NOS3's cFS/LC components, command-ingest/telemetry-output apps and selected COSMOS adapter. S6X's separate cFS v7.0.1/LC source pin is **not presumed identical** to the NOS3 source tree. Any compatibility change gets a new hash and amendment before runtime.
3. Record a harmless simulated command from ground to cFS, cFS reception and actual telemetry confirmation, each with timestamp, raw packet identity, source/build hashes and no NASA operational endpoints.
4. Extract/freeze applicable LC functional requirements and two independent implementations of a black-box behavioural oracle from test specifications **before** primary fault outcomes. The adjudication oracle sees scenario truth and post-command simulator state; the process gate never does.
5. Produce first-phase readiness status. An inability to observe cFS command/telemetry or to demonstrate oracle separation is a failed preflight, not a result.

## Phase B — prespecified benchmark and controls (requires independent author protocol/fault freeze)
- Lock F1/F2 fault-family source manifests; use requirement deviations unrelated to the historic S6X equality fixture. Include correctly approved clean controls and benign missing-evidence cases.
- Define gate input set, the seventh conformance signal, signers/approval provenance, protocol timings, fallback/hold semantics, timeouts and seeds in advance. Record and hash order-balancing and trial/repetition assignments before collecting outcomes.
- Explicitly show two-way actual simulated command packet flow for **each** scenario under both G0/G1, resetting the simulator between attempts; otherwise only report a lower-level component test.
- Primary paired endpoints: unsafe command dispatch and correct-case hold/deferral; secondary evidence-collection and confirmation latencies. Report results by scenario first, not pooled percentage across repetitions.
- If the added signal is absent in C2, a fail-closed gate may defer legitimate recovery. That cost is a primary outcome, not an exclusion.
- Independent adjudication/reconstruction uses separate implementation, with a read-set test proving no hidden truth reaches decision gate; sole-author separation should not be described as external human replication.

## Phase C — validation, interpretation and manuscript gate
- Preserve all attempts (including failures), source/result manifests, logs and clean/bad artifact identities.
- New primary quantitative findings must be derived only from P2X itself, never mathematically appended to frozen Study6/S6X denominators.
- Compare findings against the preregistered hypothesis; do not tune the enhancement against primary scenario failures, and report cases where G1 does not outperform G0.
- No CEAS R3/R4 claims or new numerical tables from P2X until audit + author review approve claim scope. “Software-in-the-loop” is the ceiling absent real hardware. Flight readiness, field attack detection and real ground-link probabilities remain out of scope.

**Current gate:** `P2X_DESIGN_ONLY__NO_RUNTIME_OR_SCIENTIFIC_EXECUTION_AUTHORIZED`.