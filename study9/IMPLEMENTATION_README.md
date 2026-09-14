# Study 9 synthetic implementation phase

This directory documents the implementation-only phase for **S9-RTSI-001** after the primary population and semantic-adjudication contracts were frozen.

## Scope

The implementation under `study9/src/study9_semantic/` is deliberately **synthetic-only**. It may load frozen Study 9 governance metadata and the frozen Study 2 selector implementation, but it must not open or process the real CuCD-ID, AegisSat, or UNSW-IoTSAT row populations during this phase.

The code provides:

- fail-closed validation of the frozen population, semantic freeze, rubric, schema manifest, and Study 2 selector hash;
- materialization of the frozen 3-dataset x 8-variable semantic mapping contract;
- deterministic enumeration of admissible binary completions for unresolved state;
- a thin adapter to the frozen Study 2 selector;
- generic action-set and minimal-sidecar combinatorics for synthetic fixtures;
- an independently implemented audit path for completion/action-set reconstruction.

It does **not** produce Study 9 scientific results.

## Run the synthetic test suite

From the repository root:

```bash
PYTHONPATH="study9/src:study2/src" \
python3 -m unittest discover -s study9/tests -p 'test_*.py' -v
```

The test suite includes exhaustive adapter equivalence over all 256 binary eight-variable states and every `Study2Policy` enum value. It also verifies the frozen 24-record semantic matrix, label exclusions, fail-closed governance bindings, completion enumeration, minimal-sidecar tie retention, and canonical-versus-independent synthetic reconstruction.

## Fail-closed behavior

`contracts.py` rejects execution if, among other things:

- any of the three frozen population members changes;
- the required eight-variable interface changes;
- dataset artifact/population/schema locks are not all active;
- the semantic freeze and schema manifest disagree about a mapping;
- a deterministic derivation rule appears in the currently empty frozen registry;
- the frozen Study 2 selector byte hash changes;
- any real-data, row-level, canonical-execution, results, manuscript, or submission authorization becomes true without a later protocol phase.

## Policy-scope boundary

This implementation intentionally has **no default Study 2 policy**. The adapter and combinatorial functions require a policy argument.

Study 9 has not yet frozen which Study 2 policy or policy set is canonical for real action-identifiability endpoints. Synthetic tests may exercise all selector enum values solely to verify adapter equivalence. Before any real row-level execution, the canonical policy scope must be prospectively frozen or amended in the Study 9 protocol.

## Not authorized in this phase

This phase does not authorize:

- reading or processing real dataset rows;
- dataset ingestion into the repository;
- per-dataset coverage calculations as scientific results;
- real admissible-action-set computation;
- real unique-action-identifiability computation;
- real minimal-sidecar computation;
- creation of `study9/results/`;
- modification of Study 2;
- modification of submitted Papers 1 through 4;
- manuscript drafting or journal submission.

Those remain separate governance gates.
