# P2X Phase A — FortyTwo build-variance diagnosis (3 October 2026)

**Status:** HISTORICAL_FORTYTWO_BYTE_REPRODUCTION_HOLD; no new science executed. This record belongs only to draft Phase A PR #215.

## Operator evidence already observed

- NOS3 source `5a3bdee6be9a2c67fdf994ae6db56d5c60395302`, recursive source locks and exact OCI digest were verified in the prior host check.
- FortyTwo upstream source was freshly restored at pinned commit `eda252bf31f27850e867e698cfdd963e143ead1f`, clean.
- October's pinned-image, offline `make GUIFLAG= SHADERFLAG= 42` successfully compiled/linked unmodified source. The new `external/fortytwo/42` is a 64-bit x86-64 ELF PIE.
- October SHA256: `b4d054bdd8a95dd429201466833fba8403efec4bdef09a9ed7040131dda3006d`; original July lock SHA256: `9c0062d2a447a6340e7c191850ff952d3f8768dd307e3e7fb141e777961e60c7`. They differ.
- July compiler log named by the historical lock (`logs/wp4/fortytwo-build-20260725T042102Z.log`) returned `LOG_NOT_AVAILABLE` on the research host. Source/image hashes survived, but the exact historical Make invocation did not.
- Pinned FortyTwo Makefile defaults include GUIFLAG = `-D _ENABLE_GUI_` and SHADERFLAG = `-D _USE_SHADERS_`; the October reconstruction disabled both. This **could** explain some difference, but no cause is established without a controlled comparison.
- All five generated NOS3 build artifacts are missing in the fresh source clone. Historical Git-tracked locks remain unchanged. No runtime, NOOP, ground telemetry or primary science was executed.

## Isolated two-candidate build-recipe comparison

`scripts/probe_paper2x_fortytwo_build_recipe.sh` uses `git archive` of the exact FortyTwo commit to create two distinct clean sources only under ignored `artifacts/runtime/p2xa-42-recipe-probe-*/`. Both use the same locked OCI, Linux/amd64, disabled networking and internal compiler path `/work/fortytwo`.

1. October control: `make GUIFLAG= SHADERFLAG= 42`. Its checksum **must** repeat the observed October `b4d054bd...` or the probe fails closed before other inference.
2. One-variable comparison: in a **separate clean source**, use `make GUIFLAG= 42`, preserving pinned Makefile's shader default. Compare exact SHA256 against both October and July. A July byte match corroborates a candidate recipe; it does **not** prove which command was run in July because that source log is unavailable.
3. Source checkout, existing October executable and historical FortyTwo/NOS3 locks are checked for zero mutation; new logs and source archives remain in the ignored sidecar. No output is auto-promoted into the original FortyTwo checkout.

## Scientific-method consequence

July belongs to historical work. Matching its binary is useful provenance but a new Paper-2 integrated experiment can instead establish a prospective **separate P2X environment baseline** through two independent deterministic builds, explicit compiler flags, pinned source and OCI, artifact identities, functional and command/telemetry smoke tests and author-approved protocol amendment. That prospective path must not quietly relabel new executable bytes as a recovered July freeze. No runtime, fault injection, manuscript insertion, source change or scientific observation is authorized by this diagnostic.

**Current gate:** fresh author-host recipe-probe output pending; NOS3 compiled build and A1 remain blocked.
