# P2X-NOS3-RG-001 — prospective Phase A environment v2 amendment (draft)

**Disposition:** `DRAFT_NOT_ADOPTED`; author approval required for substitution of the Phase-A binary identity. No runtime and no primary research data exist under v2. Date: 2026-10-03.

## Observed evidence and non-recoverable historical gap

Operator report: exact pinned FortyTwo source `eda252bf31f27850e867e698cfdd963e143ead1f`, OCI `ivvitc/nos3-64@sha256:06aa945988a7770b759022c2e1f6f2531818c087fe41a4739d3a3a7f2a9dcce2` (linux/amd64) and explicit headless `make GUIFLAG= SHADERFLAG= 42` built a binary with SHA256 `b4d054bdd8a95dd429201466833fba8403efec4bdef09a9ed7040131dda3006d`. A fresh clean `git archive` **October control** under identical image/path independently reproduced this byte hash. An independent clean **shader-default** case `make GUIFLAG= 42` also produced exactly the same binary. Thus the tested shader override is not the missing July explanation.

July historical FortyTwo executable SHA256 `9c0062d2a447a6340e7c191850ff952d3f8768dd307e3e7fb141e777961e60c7` is retained, immutable, and `NOT_BYTE_REPRODUCED`; July's named compiler log `logs/wp4/fortytwo-build-20260725T042102Z.log` was not available on the author host. The operator's source-level probe passed, but the raw ignored sidecar has not been independently downloaded and reviewed in this chat. Do not infer that the 2026-07-25 original command was recovered, that the historical executable was defective, or that the two binaries are behaviourally equivalent.

Evidence root reported by author (ignored, not deposited): `artifacts/runtime/p2xa-42-recipe-probe-20261003T181834Z-91386/`. Control and shader-default both equal `b4d054...`. Existing author-host `external/fortytwo/42` remained unchanged; no NOS3 compilation or runtime was triggered by the probe.

## Purpose of a new baseline

P2X is a new Paper-2 hands-on software-in-the-loop experiment, not a reproduction of Paper-1 July observations. A defensible new experiment can freeze its own environment *before* fault fixtures or treatment outcomes are generated, provided its new binary and functional identity are prospectively qualified. We should stop trying random flags to manufacture July byte identity.

## Proposed environment identity (NOT YET ACCEPTED)

| Element | Candidate identity / qualification |
|---|---|
| Scientific study | `P2X-NOS3-RG-001`; separate population, no historical data migration |
| FortyTwo upstream | `nasa-itc/42` at `eda252bf31f27850e867e698cfdd963e143ead1f` |
| FortyTwo candidate recipe | `make GUIFLAG= SHADERFLAG= 42`, `linux/amd64`, same pinned OCI, compiler workdir `/work/fortytwo`, `--network none`, clean source archive |
| FortyTwo candidate executable | `b4d054bdd8a95dd429201466833fba8403efec4bdef09a9ed7040131dda3006d`, October control reproduction reported, independent artifact review pending |
| July reference | `9c0062d2a447a6340e7c191850ff952d3f8768dd307e3e7fb141e777961e60c7`; keep frozen and exclude as v2 acceptance criterion, labelled `NOT_BYTE_REPRODUCED` |
| NOS3 source | `nasa/nos3` at `5a3bdee6be9a2c67fdf994ae6db56d5c60395302`, recursive gitlinks unchanged (including LC `5daef363...` and HWLIB `d65f77de...`) |
| Build image | `ivvitc/nos3-64@sha256:06aa945988a7770b759022c2e1f6f2531818c087fe41a4739d3a3a7f2a9dcce2`; no network on build |
| NOS3 compiled outputs | Missing. Candidate-only reconstruction with distinct ignored Phase-A sidecar; record five hashes and metadata; compare to July descriptively, not silently demand equality or replace original lock |
| Ground/flight proof | Actual pinned NOS3/COSMOS radio command -> cFS receipt -> returned telemetry/counter, independently checked from fresh raw trace; internal UDP-only NOOP is partial |

## Required acceptance gates, ordered

1. Verify exact PR/source/image and inspect the full FortyTwo recipe-probe sidecar and its two candidate build logs. Preserve unchanged original October executable and exact two candidate hashes.
2. Freeze recipe, actual compiler/linker version (capture `gcc --version`, `ld --version`), work directory and env flags; create a new **P2X-only** lock under ignored Phase-A evidence. Clearly identify the July study separately. Repeat the frozen recipe from an independent clean source and match the same candidate SHA256. A compiler path variation causing different bytes is a HOLD, not waived.
3. Prepare a no-overwrite offline NOS3 candidate build: only if the generated directories are wholly absent, invoke the original pinned build order (`bash ./scripts/cfg/config.sh`, `make build-fsw`, `make build-sim`, `make build-cryptolib`) inside the exact OCI with `--network none`. Do not run the historical `scripts/build_nominal_nos3.sh`: it deletes build trees and overwrites `artifacts/nominal-build-lock.txt`. Generate separate P2X sidecar and five artifact digests, and report historical differences honestly.
4. Independently verify the new NOS3 cFS executable and simulator outputs (source pins, build recipe and hashes); where byte-for-byte repeats fail, investigate build nondeterminism before adopting. No dynamic runtime before this step.
5. Before runtime, update the Phase-A runner/nominal launcher to consume P2X-specific sidecar and prove actual P2X FortyTwo/NOS3 binaries, **not just** the old July lock's `PASS` strings. Do not alter the existing shared historic WP4 runtime script or smuggle a mismatching binary under the July identity.
6. Restrict preflight to the expressly authorized benign simulated source/host readiness and one internal SAMPLE NOOP (partial result). Separately demonstrate a real pinned COSMOS `CFS_RADIO` radio NOOP and returned telemetry, including prior/after counters and read-only independent trace review.
7. Freeze a new environment acceptance record *before* starting F1/F2 or primary G0/G1 trials, together with negative outcomes and failed attempts. A distinct later runtime/fault-campaign gate remains necessary.

**Portfolio firewall:** Study3/4/6, S3X/S6X, Paper1/P7, Papers3/4/5 and all prior outcome populations unchanged. NO manuscript insertion, PR merge, Zenodo upload, publisher submission, fault injection or scientific observations authorized by this DRAFT_NOT_ADOPTED amendment.

**Decision request:** approve a distinctly labelled *new P2X environment baseline* rather than insisting on unrecoverable July executable byte identity. Until accepted, all Phase A host runtime remains on HOLD.
