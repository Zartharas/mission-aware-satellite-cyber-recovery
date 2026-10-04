# Paper 2 P2X Phase A — verified new-chat handoff (4 October 2026)

**Repository authority:** PRIVATE `Zartharas/mission-aware-satellite-cyber-recovery`; use live `main` as the historical/portfolio authority and the separately versioned **draft/unmerged PR #215** for prospective Paper-2-only work. This is the only GitHub repository with a relevant change in this handoff. Do not touch OmniRoute, Paper 1/P7, Papers 3/4/5 or unrelated repositories. Sole independent author. Do not infer an author-host experiment from green GitHub Actions.

## Exact last checked authority

- Last verified `main`: `4cd0c30a276b3c5a0494736b93a8d08dc1ed8df4` (check live refs afresh in the next chat; never assume it remains unchanged).
- Working branch: `research/paper2x-nos3-phase-a-20261003`; draft PR [#215](https://github.com/Zartharas/mission-aware-satellite-cyber-recovery/pull/215), UNMERGED. Last verified **implementation** head: `22404f78ecfb73b57d56a6a6817c96232e9ef653` (commit `Paper 2 P2X: require independent staged submodule worktree roots in v2e`). The GitHub handoff-record commit that introduces this Markdown file will be a fast-forward child; verify the actual new head rather than assuming this recorded predecessor is current.
- Exact-head Actions `Validate research configurations`: run **#1338**, ID `37176565708`, commit `22404f78ecfb73b57d56a6a6817c96232e9ef653`, terminal **SUCCESS**, including `Audit historical Paper 2 P2X design at exact approved head`, `Audit authorized P2X Phase A host runner scope (static only)` and tracked shell syntax. Earlier runs #1337 / #1336 were also successful on their own earlier heads. Code/static CI does NOT run Docker or create experimental observations.

## Experiment/claims firewall

Experiment ID: `P2X-NOS3-RG-001`; independent prospective October NOS3/FortyTwo/COSMOS environmental qualification for Paper 2. Do not relabel any July historic freeze or extend Paper 1/P7 inference. No A1 cFS benign NOOP, A2 COSMOS telemetry/command proof, F1/F2/G0/G1, faults, manuscript claims, final environment acceptance or PR merge have occurred or are authorized by this handoff. Earlier author permission only covered implementing and static-validating new v2e scripts, **not running a second full NOS3 build**.

## Original Phase A Environment v2 — immutable failed-evidence population

- Pinned NOS3 source `5a3bdee6be9a2c67fdf994ae6db56d5c60395302`; LC gitlink `5daef363c95d71c1ff3c5e9dcd4dddab560e8b39`; HWLIB gitlink `d65f77dea94467b7cb71053eb2f58f7a0cde3b02`.
- OCI `ivvitc/nos3-64@sha256:06aa945988a7770b759022c2e1f6f2531818c087fe41a4739d3a3a7f2a9dcce2` (Linux/amd64); offline `--network none`; both builds used `/work/nos3`.
- Distinct October FortyTwo candidate: revision `eda252bf31f27850e867e698cfdd963e143ead1f`, executable SHA-256 `b4d054bdd8a95dd429201466833fba8403efec4bdef09a9ed7040131dda3006d`. Historical July reference `9c0062d2a447a6340e7c191850ff952d3f8768dd307e3e7fb141e777961e60c7` was NOT byte-reproduced and must not be silently replaced.
- Original ignored author-host evidence: `artifacts/runtime/p2xa-nos3-v2-build-20261003T192146Z-99065/`. Both full initial offline builds reached `[100%] Built target standalone`. The original finalizer was repaired for historical checksum paths containing spaces, and it wrote `p2x-v2-build-manifest.json` and `artifact-hash-comparison.tsv`. Classification **`BUILD_BYTE_REPRODUCTION_HOLD`**: eight of nine required files byte-identical, sole differing ELF `fsw/build/exe/cpu1/core-cpu1`, both 1,339,248 bytes; primary SHA `db64bf080232d64d5c39301e2f712885cf85e86d93c33c94fb46325fda1533fb`; repeat SHA `5a0d746a01eeac38ee555d664673ae68f0b4f4b1b96c38e06923109867ea296b`.
- Exhaustive ELF comparison found exactly 49 differing bytes: GNU Build ID 20; cFE build environment `.rodata` 14 (`BUILDDATE` `202610031922` versus `202610031930`; different ephemeral container hostnames `2158a3b1be11` versus `a3ba0b0eaa5b`); five GCC coverage-generation stamps `.data` 15 in `nos_link.c`, `libcan.c`, `libi2c.c`, `libspi.c`, `libuart.c`. All 10 embedded stamps matched their respective existing `.gcno` files. `.text` identical, but raw overall bytes not identical. Do not strip, zero, patch, normalize, downgrade policy or claim functional equivalence merely from code-section identity.
- Original four July lock files repeatedly passed SHA-256 integrity checks: `fortytwo-lock.txt`, `nominal-build-lock.txt`, `nominal-runtime-preflight-lock.txt`, `nos3-submodule-lock.txt`. Existing canonical `external/nos3` now contains ignored generated build directories; NEVER rerun the original v2 builder or `scripts/build_nominal_nos3.sh`, run `make clean`, overwrite old build directories or remove this evidence.

## Isolated determinism investigation — actual host results

- GCC 11.4 disposable single-TU test: fixed seeded `.gcno` stamps `4294967295` and `4294967295` after delay; unseeded `83379182` and `83381227`. Pinned primary/repeat `noslink.dir/flags.make` matched; `-fprofile-arcs -ftest-coverage` were enabled without a fixed seed.
- The first tracked two-source CMake pilot at commit `7b296313...` was a **FALSE POSITIVE**: `docker run` lacked `-i`; only the outer PASS printed. The next attempt `6db69c50...` was stopped at Mac `bash -n` due to nested heredoc quoting before Docker. Neither is positive evidence.
- The corrected pilot at exact commit `08276523efeea57fe0278be9942783bd03de28a7` **genuinely passed on author's Mac**: `MAC_BASH_SYNTAX=PASS`, two actual disposable pinned offline CMake builds, distinct repeatable per-source/object seed strings `P2X-NOS3-RG-001:v2d:alpha.c:alpha.c.o` and `...:beta.c:beta.c.o`, observed `.gcno` numeric stamp `4294967295` for BOTH different source files in BOTH copies. Unique *strings*, NOT unique numeric stamps. Markers `P2X_V2D_SOURCE_UNIQUE_SEED_STRINGS=PASS`, `P2X_V2D_CMAKE_COMPILER_LAUNCHER_REPEATABILITY=PASS`, `P2X_V2D_GCNO_HEADER_REPRODUCIBILITY=PASS`, `P2X_V2D_FULL_NOS3_BYTE_REPRODUCIBILITY=NOT_TESTED`, `P2X_V2D_INNER_GATE=PASS`, `P2X_V2D_PROBE=PASS`. No NOS3 full rebuild or runtime; worktree clean.

## Authorized v2e implementation — already versioned and CI static PASS

Read these exact records **from current live PR branch head** before working:

1. `paper2x/phase_a/DETERMINISTIC_V2E_REBUILD_PROPOSAL_2026-10-03.md` — prospective experiment design, synthetic reproducibility labels, fresh two-source staging, strict nine raw bytes.
2. `paper2x/phase_a/GCOV_DETERMINISM_DIAGNOSIS_2026-10-03.md` and `paper2x/phase_a/RUNBOOK_2026-10-03.md` — failure/pilot evidence and staged next steps.
3. `paper2x/phase_a/V2E_OFFLINE_BUILD_EXECUTION_GATE_2026-10-03.json` — **CLOSED:** `decision=DESIGN_AND_STATIC_VALIDATION_ONLY`, `execution_authorized=false`, `authorization_scope.offline_full_build=false`, all runtime/COSMOS/fault/merge permissions false.
4. `scripts/p2x_v2e_seed_launcher.py` — source AND object relative-path hashed `-frandom-seed` identity; no global one-seed substitution.
5. `scripts/build_paper2x_phase_a_nos3_v2e.py` — default `--inspect`, `--self-test`, explicitly blocked `--build`. Hard authorization test occurs BEFORE host evidence reads, Docker calls or source staging. Future new evidence root would be `artifacts/runtime/p2xa-nos3-v2e-build-<fresh-id>/{primary,repeat}/source`, with existing generated directories excluded from copied clean source, independent staged-submodule gitdirs/worktrees inside each candidate, fixed container `/work/nos3`, synthetic labels `BUILDDATE=202610030000`, `HOSTNAME=p2x-v2e-builder`, `USER=p2x-builder`, separately recorded true provenance, two offline sequential original recipe builds.
6. `scripts/verify_paper2x_phase_a_v2e.py` — separately authored independent hash/seed/log/source/old-HOLD/July-lock reader; must require nine of nine raw identical SHA-256 + size and actual generated synthetic CFE fields; cannot inherit old v2 verifier's primary-root assumptions.
7. `scripts/audit_paper2x_phase_a_design.py` — exact PR change whitelist, scope and v2e static/negative authorization tests, including separate staged LC/HWLIB gitdir/show-toplevel containment. Exact-head CI #1338 was SUCCESS.

**No v2e full candidate trees, dual NOS3 builds, v2e PASS manifest, nominal runtime or science data exist yet.** Earlier v2 and new v2e are distinct candidate populations; never promote or replace one with the other.

## Safe next action and required separate author approval

First query live GitHub main, PR #215 status and exact head, Actions terminal status on that exact head. Read the gate and the v2e scripts. Perform only approved STATIC/read-only work. When author-host commands are needed, the following are the planned safe commands on a clean checkout of the exact current PR head:

```bash
python3 scripts/p2x_v2e_seed_launcher.py --self-test
python3 scripts/build_paper2x_phase_a_nos3_v2e.py --self-test
python3 scripts/verify_paper2x_phase_a_v2e.py --self-test
python3 scripts/build_paper2x_phase_a_nos3_v2e.py --inspect
```

**Negative authorization proof:** `python3 scripts/build_paper2x_phase_a_nos3_v2e.py --build` MUST currently exit nonzero with `P2X_V2E_BUILDER_HOLD=separate_v2e_authorization_absent__no_build`, before Docker or staging; do not bypass/flip its gate while merely testing. Avoid repeating tests that would mutate preserved source or experiments. Check for any new failures in static tests and address them in a new draft commit, keeping the gate closed.

Only after author explicitly and separately approves a prospective P2X-only full OFFLINE v2e rebuild should the specific execution gate be revised in a reviewed, versioned PR. Newly built primary/repeat files must remain under a NEW ignored evidence ID; raw 9/9 SHA identity and independent actual-byte read-back must pass. That would still be `V2E_DUAL_OFFLINE_BUILD_BYTE_IDENTITY_PASS__RUNTIME_UNTESTED` — not final Environment acceptance. Benign internal cFS A1 must be gated separately from A2 COSMOS radio/downlink; no faults/F1/F2/G0/G1 or manuscript scientific claims at this point.

## Reporting instructions for next chat

- Use connected GitHub app for this PRIVATE repository and compare live main/ref/pr/CI rather than trusting this handoff as the live head. Preserve sole independent-author metadata and evidence-first/fail-closed research claims.
- Avoid edits to anything outside this Paper 2 PR scope, avoid unneeded new PRs/PRMs; PR #215 is the active project-management vehicle, already draft/unmerged. No PR merge unless the author gives separate explicit permission.
- Report exact head, CI run ID/status, gate state, concrete passing/failed tests and next safe command. Do not invent local Docker outcomes from CI. Stop before any irreversible or experimental action until explicitly authorized.
