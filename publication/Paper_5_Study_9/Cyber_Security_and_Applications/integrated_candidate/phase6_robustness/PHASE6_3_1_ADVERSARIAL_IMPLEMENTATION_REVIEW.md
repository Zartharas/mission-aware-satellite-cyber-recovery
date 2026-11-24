# Phase 6.3.1 adversarial implementation audit and qualification hold

Baseline 3b23072449aa7e0b9454976fe0072dfaa3c78139: exact-head engineering 45299374092, LaTeX 45299373896 and repository 45299373902 all SUCCESS. Review inspected actual evaluator, oracle, state model, runner, integrity, worker, writer and tests. No canonical evaluation or domain enumeration executed.

| ID | Risk / finding | Disposition |
|---|---|---|
| IQ01 | Python bool/int equality can mask wrong literal value | Recursive type-strict comparison for scientific and metamorphic outputs; engineering probes |
| IQ02 | Constrained-domain membership checked by size/nesting only | Independent integer-decoded domain oracle; exact set comparison prepared, no enumeration now |
| IQ03 | Policy/sidecar/monotonicity exception lacked offending tuple | Capture offending state, model, policy and reference; enforce full logical row count |
| IQ04 | Duplicate JSON keys and nonfinite constants silently parsed | Strict worker decoder and response validation; malformed JSON probes |
| IQ05 | Container timeout may leave container running | Unique container name and bounded cleanup attempt |
| IQ06 | Candidate read path isolation not actually qualified | Local-digest-only Docker qualifier with non-study inputs, read-only/no-network/nonroot checks; actual environment pending |
| IQ07 | Integrity manifest mutable in same directory | Exact-commit code/input manifest needed before execution; separate receipt to avoid self-reference |
| IQ08 | Failure preservation not crash-proof | Exclusive private directory and KeyboardInterrupt capture; no guarantee under abrupt process death, disk failure or host crash |
| IQ09 | Controlled vocabulary authored from public contract | Not blinded or external validation; no broad semantic-generalization claim |
| IQ10 | Existing runner functions callable by a programmer | CLI remains hard-blocked; governance hold, not tamper-proof security; future explicitly authorized launcher needed |
| IQ11 | Host subprocess buffering and Docker daemon trust | Fixed input caps and bounded container memory/time; trusted local daemon/image, abrupt termination remain operational risks |
| IQ12 | Source-schema qualification vs real evidence | Synthetic premises only, no flight or cryptographic assurance |

Qualification program never imports scientific runner, reads canonical fixtures/gold, or enumerates models. Requires a trusted already-local Python image by repo digest and a local Unix Docker endpoint. The chat runtime has neither Docker nor Podman. No actual daemon qualification performed here. Before readiness, verify exact code and input hashes, successful real runtime qualification, latest CI and separate author execution approval. No new source access, experiment, merge or release. 

**Disposition:** corrections committed; runtime and final execution manifest pending. No change to frozen design.
