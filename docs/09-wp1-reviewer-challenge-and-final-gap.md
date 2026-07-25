# WP1 Reviewer Challenge and Final Gap Statement

## Purpose

This review tests whether the proposed paper remains novel after considering adjacent spacecraft fault-management, cyber-resilience, cyber-physical recovery, and autonomous recovery research.

## Reviewer challenge

A skeptical reviewer could argue that the proposed work is only a combination of already-established ideas:

- Mission Aware cybersecurity already links mission objectives, system functions, architecture, and cyber loss.
- Spacecraft fault management already selects responses according to mission phase, power, thermal state, and communication availability.
- Cyber-safe mode and restoration from trusted images already appear in space-security guidance.
- Cyber-physical systems research already studies attack recovery controllers and restoration to a target physical state.
- NOS3/cFS and other satellite testbeds already support command, telemetry, fault, and attack injection.

That criticism is valid unless the experiment contributes a distinct comparison problem and measurable outcome model.

## What prior work establishes

### Mission and resilience concepts

NIST cyber-resilience engineering defines the objectives of anticipating, withstanding, recovering from, and adapting to cyber-enabled adversity while reducing mission risk. Mission Aware research provides a systems-theoretic process for tracing mission requirements to system functions and attack consequences.

These concepts should be treated as foundations rather than new contributions.

### Spacecraft fault management

NASA and peer-reviewed spacecraft FDIR literature already establishes that recovery behavior can depend on mission phase, resource condition, thermal safety, and communication delay. Spacecraft safe mode normally preserves essential functions and creates a condition from which ground operators can diagnose and recover the mission.

The proposed work therefore cannot claim that state-dependent recovery or safe mode is new.

### Cyber-physical attack recovery

The cyber-physical systems literature distinguishes detection and containment from recovery of the physical process. It includes shallow recovery, dedicated recovery controllers, real-time attack recovery, predictive response selection, and self-healing approaches.

The proposed paper must therefore explain why intermittent-contact spacecraft create a distinct evaluation problem rather than simply applying a generic recovery controller.

## Remaining defensible gap

The literature reviewed in WP1 did not identify a controlled small-satellite experiment that simultaneously:

1. Compares multiple cyber-response policies rather than evaluating one detector or recovery mechanism.
2. Varies spacecraft mission state and ground-contact availability.
3. Includes adversarial degradation or manipulation of the evidence used to choose a response.
4. Reports both cyber-containment and mission-continuity outcomes.
5. Requires verifiable trusted-state evidence before declaring recovery.
6. Reports conditions in which aggressive or autonomous containment performs worse than a simpler baseline.

This is a narrower and more defensible gap than autonomous recovery, safe mode, or satellite cyber-range construction alone.

## Final novelty statement

> This study introduces a reproducible software-in-the-loop experimental method for comparing satellite cyber-containment and trusted-recovery policies across mission states, telemetry-evidence conditions, and intermittent ground contact, while measuring adversary containment, mission continuity, safety-invariant preservation, and time to verified trusted recovery.

## Contribution boundaries

The paper will not claim:

- A new general theory of mission-aware cybersecurity
- A new spacecraft FDIR architecture
- A new anomaly-detection algorithm
- A production-ready flight recovery system
- Formal safety certification
- Operational effectiveness against every satellite architecture
- Human operator performance or trust findings

## Falsification criteria

The central claim will be weakened or rejected if:

- The mission-aware policy does not materially differ from a static baseline.
- Results depend entirely on one arbitrary weighting scheme.
- Trusted-recovery evidence does not change recovery conclusions.
- Contact delay and mission state do not alter policy outcomes.
- The same conclusions arise without spacecraft-specific constraints.
- Trial results cannot be reproduced from pinned snapshots and seeds.

## Recommended paper framing

### Problem

Cyber containment can protect a spacecraft while also interrupting mission-critical operation. Intermittent communication and incomplete evidence complicate the decision to isolate, suspend, safe, roll back, or continue operating.

### Method

Theory-informed design-science research with controlled software-in-the-loop experiments.

### Primary comparison

Observe-only, static containment, ground-authorized response, safe-mode/rollback recovery, and mission-aware policy selection.

### Primary result form

A multi-objective comparison rather than a single universal winner.

## WP1 decision

**Proceed.** The gap is sufficiently distinct for the next phase, provided the experiment preserves the six differentiating elements above and does not revert to a generic testbed or anomaly-detection paper.
