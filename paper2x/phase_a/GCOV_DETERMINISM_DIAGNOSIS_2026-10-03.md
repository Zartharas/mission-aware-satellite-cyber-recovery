# P2X A0c — source-specific GCC determinism diagnosis (3 October 2026)

**Status:** `GCOV_STAMP_MICROPROBE_PASS__BUILD_BYTE_REPRODUCTION_HOLD`. No full NOS3 rebuild, runtime, fault or scientific observation was performed. Original nine-artifact primary/repeat manifest remains `BUILD_BYTE_REPRODUCTION_HOLD`, without policy waiver.

## Existing failed build, independently localized

The primary and repeat candidate NOS3 source and pinned container workdir matched; 8/9 prospective artifacts were byte-identical. Only `fsw/build/exe/cpu1/core-cpu1` (both 1,339,248 bytes) differed at exactly 49 bytes across eight contiguous ranges: GNU Build ID 20 bytes, cFE `.rodata` build date (`202610031922` vs `202610031930`) and hostname (`2158a3b1be11` vs `a3ba0b0eaa5b`) 14 bytes, and five `__gcov_` record stamps 15 bytes. GCC version marker `*41B` in each record. Across primary/repeat, all five of those per-tree ELF stamps matched the appropriate generated `.gcno` headers: **10/10**. The affected source translation units are `nos_link.c`, `libcan.c`, `libi2c.c`, `libspi.c`, `libuart.c` under the pinned NOS3 HWLIB noslink simulator. The `.text` section had zero differences, but loaded metadata/data differed, therefore strict byte reproduction was not achieved.

### Pinned-build source evidence

- NOS3 original primary/repeat generated `noslink.dir/flags.make` are identical. Actual flags include `-fprofile-arcs -ftest-coverage`, with no `-frandom-seed`; the build uses GCC in the original pinned OCI.
- Pinned cFE source (`nasa/cFE@87e273743f3d07ed9216462b461e9f398ff96c87:cmake/generate_build_env.cmake`) explicitly accepts the environment variables `BUILDDATE`, `HOSTNAME` (used as `BUILDHOST`), and `USER`, with fallbacks. These must be held constant in any **new** prospective full-build recipe.
- The pinned NOS3 Makefile `nasa/nos3@5a3bdee6be9a2c67fdf994ae6db56d5c60395302` calls CMake for `make build-fsw`. The source `scripts/cfg/config.sh` configures the mission separately. These originals are not to be patched.

### The author's pinned GCC 11.4 single-source microprobe

| Configuration | `.gcno` offset-8 coverage stamp |
|---|---:|
| Same disposable C source + fixed seed, initial (`seed-a`) | 4294967295 (`0xffffffff`) |
| Same source + same fixed seed, after delay (`seed-b`) | 4294967295 (`0xffffffff`) |
| Default/unseeded initial (`default-a`) | 83379182 |
| Default/unseeded after delay (`default-b`) | 83381227 |

Author terminal reports `PINNED_GCC_FIXED_SEED_REPEATABILITY=PASS`, clean source, `NOS3_BUILD_REEXECUTED=NO`, `NOS3_RUNTIME_EXECUTED=NO`. The all-ones value is the **observed stamp for the seeded fixture**, not evidence of unique stamps across source files and not a new accepted NOS3 artifact.

Official GCC 11.4 Developer Options: https://gcc.gnu.org/onlinedocs/gcc-11.4.0/gcc/Developer-Options.html . It documents `-frandom-seed=string` for object-file and coverage stamp reproduction, and states that the seed string should differ for each compiled file. Thus a *global same-seed `CFLAGS` approach is not approved*. Official CMake 3.26 environment launcher reference: https://cmake.org/cmake/help/v3.26/envvar/CMAKE_LANG_COMPILER_LAUNCHER.html . It initializes the `CMAKE_C_COMPILER_LAUNCHER` property at first configure, allowing a source-specific seed to be inserted without editing NOS3 upstream CMake or source files.

### Isolated next hypothesis test (not a NOS3 build)

The tracked `scripts/probe_paper2x_v2d_cmake_launcher.sh` uses the exact pinned Linux/amd64 OCI, disabled network, read-only container with a temporary `/tmp` filesystem and **no host mounts**. It creates two disposable translation units and a CMake compiler launcher. The launcher deterministically derives a separate seed for each source+object basename, holds seeds constant across independent CMake configurations, and verifies repeat `.gcno` stamps. This checks that the CMake 3.26 launcher mechanism actually activates with the pinned image; it does not establish full nine-artifact NOS3 byte reproduction or a science result.

On a successful pilot only, document a prospective replacement P2X v2d build recipe: fixed `BUILDDATE`, `HOSTNAME`, and `USER` in both candidate OCI runs, deterministic **source-specific** seed (stable normalized `/work/nos3`-relative input and output), identical pinned image/workdir, two newly staged independent ignored source trees. Retain the original failed candidate build trees/HOLD manifest and all historical July locks. Require a separate full nine-artifact raw SHA comparison, independent actual-byte verifier and separately gated benign A1/COSMOS validation. **No full NOS3 rebuild** has been executed under this proposed recipe.

## Portfolio disposition

Paper 2 P2X-only exploratory metadata diagnosis. No waiver of `BUILD_BYTE_REPRODUCTION_HOLD`, no binary patch/strip, no old-study changes, no NOOP/COSMOS/fault injection, no manuscript insertion or PR merge.
