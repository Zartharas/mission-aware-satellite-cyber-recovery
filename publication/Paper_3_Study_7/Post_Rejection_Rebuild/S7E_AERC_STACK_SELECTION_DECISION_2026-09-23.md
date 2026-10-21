# S7E-AERC-001 Stack Selection Decision — 2026-09-23

**Decision ID:** `S7E-AERC-STACK-SELECT-003`  
**State:** `PRE_FREEZE_IMPLEMENTATION_BASELINE_SELECTED__NOT_CANONICAL_FREEZE`  
**Scientific execution:** NOT AUTHORIZED

## Decision

Select **standalone NASA cFS v7.0.1** at commit `088b2fa828db9ff7e00733f1908e0eeb59f66ce3` as the pre-freeze implementation baseline for the remaining non-canonical Study-7E architecture.

NOS3 v1.7.5 remains bounded feasibility/reference evidence and is not part of the selected runtime baseline.

## Evidence comparison

| Criterion | standalone cFS v7.0.1 | NOS3 v1.7.5 |
|---|---|---|
| Exact release/dependency provenance | established | established |
| Reproducible build/test | established | established |
| Live Study-7E custom cFE app | established | not established in bounded NOS3 gate |
| Direct cFE/SB transport | established | available in stack; Study-7E seam not demonstrated |
| T3/T4 two-instance/SBN path | established live | pinned baseline is single-CPU; documented multi-spacecraft path is external/proof-of-concept |
| Deterministic scenario-ID survival | established | not established for Study 7E |
| Sink/trace capture | established | not established for Study 7E |
| HS/readiness-source observation | established | not established for Study 7E |
| Ground/dynamics/hardware-model breadth | outside baseline | broader integrated capability |
| Dependency/runtime surface | smaller and sufficient for current RQs | broader; required topology expansion adds an external repository |

## Rationale

Study 7E tests equal-information policy behavior, trust-domain separation, common-cause propagation, and held-out topology/fault transfer. Those questions require cFE/SB/SBN, controlled trust separation, deterministic scenario propagation, HS observability, and deterministic capture; they do not require orbital dynamics or hardware-performance realism.

Standalone cFS now demonstrates those required implementation seams directly.

The bounded NOS3 v1.7.5 build is green at `5a3bdee6be9a2c67fdf994ae6db56d5c60395302`, but its pinned generated target baseline declares one CPU and its mission file declares one spacecraft while describing multiple-spacecraft use as experimental/proof-of-concept. Its documented multiple-spacecraft walkthrough requires the separate repository `nasa-itc/nos3-multiple-spacecraft`, referenced at commit `dae7e75709f963f15e9297a0b92926bae767f302`.

Adding that repository would expand the dependency graph beyond the declared pinned NOS3 candidate and violate the existing no-mixing principle unless a separate compatibility study were authorized.

## Evidence IDs

- cFS Gate 1: run `35868263684`, job `107205320338`
- cFS preselection seams: run `35873580570`, job `107223637303`, artifact `10756545870`
- NOS3 bounded Gate 2: run `35870689230`, job `107213663081`, artifact `10755347006`

## Boundary

This selection is not a protocol/environment freeze, model freeze, flight qualification, certification result, or canonical-execution authorization. It does not claim cFS is globally superior to NOS3.

Use the selected standalone cFS v7.0.1 candidate family for the remaining pre-freeze architecture unless a new compatibility decision explicitly authorizes another runtime/dependency stack.
