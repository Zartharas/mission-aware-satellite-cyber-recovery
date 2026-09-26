# Paper 2 R10 Editorial Diagnosis

**Source decision:** TAES manuscript `TAES-2026-4182`, 2026-09-26  
**Scope:** manuscript diagnosis only; no scientific result is modified.

## Editorial problem to solve

The TAES decision identifies a communication-and-positioning failure at editorial screening: aerospace significance was not sufficiently visible; the research gap and research question were difficult to identify quickly; prose was too complex; limitations occupied too much narrative attention; and contribution statements described experiments rather than findings.

## R10 structural diagnosis

The manuscript contains a defensible scientific boundary, but its narrative foreground is dominated by qualification language: frozen populations, model boundaries, exclusions, and non-claims. Those controls must remain, but most belong in methods/validity rather than the opening argument.

The next manuscript must be findings-first.

### Proposed central question

> Which trust failures remain invisible to a satellite cyber-recovery decision when it relies on fresh evidence, multiple trusted producers, and an approved recovery artifact?

### Proposed study-level questions

- **RQ1:** How does intermittent evidence availability affect exposure to false but validly signed recovery evidence?
- **RQ2:** How does producer diversity change the compromise-versus-availability boundary?
- **RQ3:** Which incorrect recovery artifacts remain indistinguishable from approved artifacts under progressively stronger assurance evidence?

## Findings-first contribution architecture

1. **Temporal finding:** signature validity and freshness reject post-signature alteration but do not reject false evidence freshly signed by a compromised trusted producer; intermittent availability reduces exposure without eliminating the modeled failure.
2. **Composition finding:** provenance diversity can delay systematic unsafe qualification without changing the first unsafe compromise threshold, at an availability cost that can be characterized analytically.
3. **Artifact finding:** assurance composition removes several modeled artifact failure classes, but a deterministic gate cannot distinguish two artifacts that are identical on every gate-visible signal while differing in objective correctness.
4. **Systems finding:** the residual trust boundary is determined by what the decision can observe, not by the nominal number of controls alone.

## Writing controls for the rebuild

- lead each section with the positive finding;
- move complete non-claim inventories to a compact validity section;
- prefer one claim per sentence;
- avoid repeating `frozen`, `model-bounded`, `does not`, and `cannot` in every result paragraph;
- retain all scientific caveats, but consolidate them;
- explain aerospace relevance through concrete recovery-decision constraints rather than generic satellite motivation;
- do not use a larger study count or additional dataset merely as publication optics.
