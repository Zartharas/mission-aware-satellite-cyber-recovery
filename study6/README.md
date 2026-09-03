# Study 6 — Supply-Chain-Compromised Trusted Recovery

**Experiment:** `S6-SCTR-001`  
**Current status:** `CANONICAL_RESULTS_FROZEN_MERGED`  
**Canonical results merge:** PR #85 / `0dfe7f4331fc1f8864344c95d39e0d8dcb74c8f4`  
**Accepted execution:** run `33669329819` / commit `f50f4db03e27e223104df96b2dd32bea85fd6319`  
**Frozen population:** 420 exact observations (36 adversarial artifact states + 384 benign assurance-signal unavailability states)  
**Independent audit:** PASS  

## Purpose

Study 6 asks whether a recovery artifact can satisfy increasingly strong artifact-assurance gates while still being objectively incorrect, and what availability cost stronger gates impose when assurance evidence is benignly unavailable.

This is an **abstract artifact-trust study**, not malware development, exploit research, operational spacecraft testing, or a claim of compliance with SLSA, TUF, or SPARTA.

## Scientific progression

- Study 2 showed that authenticated/current runtime evidence can still be false when a trusted producer is compromised.
- Study 3 showed that false-but-qualified runtime evidence can persist or recur over contact windows.
- Study 4 quantified multi-producer evidence quorum safety/availability trade-offs.
- Study 6 moves the trust boundary upstream: a recovery baseline itself can carry apparently valid supply-chain assurance while remaining objectively wrong.

## Frozen candidate design

Block A exhausts six abstract baseline states against six qualification gates (36 observations). Block B starts from the clean/correct baseline and exhausts every subset of six unavailable assurance signals against all six gates (64 × 6 = 384 observations). Total finite population: **420 observations**.

The research-only `objective_baseline_correct` value is used only to adjudicate outcomes after a gate decision. It is never a gate input.

## Claim boundary

The study can establish only exact properties of this finite Boolean assurance model. It cannot establish attack prevalence, real build-system compromise likelihood, spacecraft flightworthiness, operational recovery performance, standards compliance, or a globally best assurance gate.

Studies 1–5 remain frozen and are never pooled into this population.
