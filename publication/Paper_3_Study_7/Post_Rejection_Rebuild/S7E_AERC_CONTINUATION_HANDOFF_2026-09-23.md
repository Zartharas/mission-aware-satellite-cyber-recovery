# Study 7E AERC Continuation Handoff — 2026-09-23

## Scope and authority

This record preserves the continuation state for the pre-freeze, non-canonical Study 7E AERC implementation lane (`S7E-AERC-001`). It is a governance/status handoff only. It does not modify, replace, freeze, or promote the native deterministic Study 7E experiment or any submitted/frozen publication evidence.

Active pull request: **#167**  
Active branch: `paper3/s7e-aerc-implementation-feasibility-20260922`  
Gate-1 qualification head: `bef6fe920277d378ba857d280633f48b2b25cffc`  
Base: `main`

PR #167 remains an active implementation/qualification PR. **No merge is authorized by this handoff.**

## Gate 1 — corrected cFS runtime smoke: GREEN

The corrected cFS feasibility gate is green at exact head `bef6fe920277d378ba857d280633f48b2b25cffc`.

Authoritative GitHub Actions evidence:

- Study 7E pre-canonical qualification:
  - workflow ID: `364617426`
  - run ID: `35868263684`
  - conclusion: `success`
- cFS custom-app smoke:
  - job ID: `107205320338`
  - conclusion: `success`
- repository-wide validation:
  - run ID: `35868263952`
  - conclusion: `success`
- pinned standalone cFS:
  - tag: `v7.0.1`
  - commit: `088b2fa828db9ff7e00733f1908e0eeb59f66ce3`

The runtime job:

1. built the custom `aerc_bus_probe`;
2. installed it under the cFS cpu1/cpu2 `cf/` application directories;
3. loaded `AERC_PROBE` under live cFE;
4. created/subscribed a Software Bus pipe;
5. transmitted the fixed probe message on experimental MID `0x0EE0`;
6. received and validated the same message;
7. emitted the exact PASS marker:

`AERC_BUS_PROBE PASS scenario=0x53374531 marker=0xA37C0DE1`

The workflow also recorded:

- `aerc_bus_probe_runtime=PASS`;
- `study7e_scientific_scenarios_executed=0`;
- `scientific_results_generated=false`.

This is engineering/runtime feasibility evidence only.

## Gate-1 defect corrections

Two concrete harness defects were corrected without changing Study 7E scientific behavior.

### Entry-point mismatch

At handoff head `9c4ad55bf14ed7de62e4d4e586ccf6ece3683398`, run `35824429121`, job `107062970996` failed because cFE attempted the configured `AERC_BUS_PROBE_AppMain` symbol, which did not match the probe's exported `AERC_BUS_PROBE_Main`.

Correction commit:

`0884b397b3b8e2c67d9b699dc6f2d9f4f801b887`

### Message-layout mismatch

After the entry-point correction, run `35867546996`, job `107202887028` loaded the probe but failed its payload check because the probe used the generic `CFE_MSG_Message_t` base header while MID `0x0EE0` carries the cFE telemetry secondary-header semantics. The secondary-header bytes therefore overlapped the first payload field.

Correction commit:

`bef6fe920277d378ba857d280633f48b2b25cffc`

The probe now uses `CFE_MSG_TelemetryHeader_t` and passes the embedded `.Msg` to the cFE message/Software Bus APIs. The fixed scenario and marker are preserved through transmit/receive.

## Provenance correction to the prior handoff

The earlier version of this handoff and `IMPLEMENTATION_STATE.json` stated that a prior cFS runtime had demonstrated:

- a NOOP on command MID `0x1886`;
- housekeeping on MID `0x0886`;
- `cmd_count=1`;
- `AERC bus probe PASS: HK MID 0x0886 cmd_count=1`.

That claim is **retracted as unsupported**.

The referenced prior Study-7E run `35807192091`, cFS custom-app job `107010550970`, was inspected directly. Its log shows the `aerc_bus_probe` failing at application entry-symbol resolution; it does not establish the claimed NOOP/HK interaction. Inspection of PR #167 also shows that the cFS flight-software surface currently contains the non-canonical `aerc_bus_probe`, not a full AERC policy application.

The corrected, supported runtime evidence is the green Software Bus self-loop probe described above. Historical commits are preserved; no history was rewritten.

## Exact interpretation boundary

Gate 1 now supports:

**standalone cFS v7.0.1 can build, load, and execute the Study-7E non-canonical custom probe, and the probe can publish/receive and validate a fixed message through cFE Software Bus in CI.**

Gate 1 does **not** establish:

- a full AERC policy application running in cFS;
- AERC command/HK interfaces at `0x1886`/`0x0886`;
- recovery-policy behavior;
- fault-injection behavior;
- Study-7E scientific observations;
- flight qualification;
- certification/certifiability;
- production or deployment readiness;
- operational-spacecraft validation.

## Current scientific/governance state

- Study: `Study7E`
- Experiment: `S7E-AERC-001`
- Lane: pre-freeze, non-canonical implementation/technology-demo feasibility
- Program token: `AERC`
- ITOS token: `aerc`
- Native deterministic Study 7E experiment remains the prospective canonical execution surface.
- Canonical scientific execution remains prohibited.
- No production L0/L1 model is trained or frozen.
- No Study-7E canonical results exist.
- No Study-7E dataset/Zenodo freeze exists.
- No runtime stack has yet been selected for the remaining non-canonical architecture.

Prospective protocol quantities remain unchanged:

- TR1 = 72
- TR0 = 12
- training = 84
- E1 = 84
- E2 = 104
- C0 = 8
- evaluation/control = 196
- four policies per evaluation scenario = 784 planned policy-decision observations
- complete prospective manifest = 280

These are protocol-design quantities, not scientific results.

## Next authorized gates

Proceed in this order only:

1. **Bounded NOS3 feasibility**
   - Gate 1 is green, so this may now begin.
   - Use current authoritative NOS3/cFS documentation and upstream repository evidence.
   - Capture exact versions, tags, commits, submodules, platform/runtime assumptions, build/dependency burden, cFE/SB integration, telemetry/command visibility, simulated hardware/device integration, NOS Engine dependencies, CI/repeatability/provenance, and scientific benefit/complexity.
   - Do not expand this into a full NOS3 implementation.

2. **cFS-vs-NOS3 stack decision**
   - Compare both with the same factual criteria.
   - Do not use arbitrary numerical scores or popularity.
   - Select only for this pre-defined Study 7E architecture/question.
   - Record the decision durably.

3. **Remaining non-canonical architecture**
   - Continue only after the stack decision is documented.
   - Keep all architecture work outside canonical scientific evidence until separately authorized/adjudicated.

## Guardrails

- Explain exact repository changes before writes.
- Work only on the active Study 7E branch/PR unless explicitly authorized otherwise.
- No PR merge, force push, rebase, destructive branch deletion, base change, or history rewrite without explicit authorization.
- Preserve exact commit SHAs, workflow/run/job identifiers, logs, and provenance.
- Do not promote cFS/NOS3 technology-demo evidence into scientific findings.
- Do not modify Papers 1, 2, 4, the submitted/frozen Study 7 CEAS package, Study 5, or the separate JSSE study.
- Preserve the equal-information/truth-separation controls and training/evaluation leakage guards.

## Durable records

Machine-readable state:

`study7e/IMPLEMENTATION_STATE.json`

Gate-1 checkpoint:

`publication/Paper_3_Study_7/Post_Rejection_Rebuild/S7E_AERC_CFS_GATE1_CHECKPOINT_2026-09-23.md`

Earlier implementation checkpoint retained as historical provenance:

`publication/Paper_3_Study_7/Post_Rejection_Rebuild/S7E_AERC_IMPLEMENTATION_CHECKPOINT_2026-09-22.md`
