#!/usr/bin/env python3
"""P2X v2e CMake C compiler launcher: stable per-source AND per-object GCC seed.

This only wraps a CMake compile command. It does not edit source files, artifacts,
compiler output, or existing research locks. GCC's own output remains unmodified.
"""
from __future__ import annotations

import hashlib
import os
from pathlib import Path
import sys

CONTAINER_ROOT = Path("/work/nos3")
PREFIX = "P2X-NOS3-RG-001:v2e:"


def require(ok: bool, why: str) -> None:
    if not ok:
        raise SystemExit("P2X_V2E_SEED_LAUNCHER_HOLD=" + why)


def relative(path: str, cwd: Path) -> str:
    p = Path(path)
    p = (p if p.is_absolute() else cwd / p).resolve()
    try:
        rel = p.relative_to(CONTAINER_ROOT).as_posix()
    except ValueError:
        raise SystemExit("P2X_V2E_SEED_LAUNCHER_HOLD=path_outside_fixed_container_root")
    require(rel and rel != ".", "empty_relative_path")
    return rel


def seed_for(source: str, obj: str) -> str:
    require(source.endswith(".c") and obj.endswith(".o"), "not_c_source_or_object")
    return PREFIX + hashlib.sha256(
        ("P2X-v2e\x00" + source + "\x00" + obj).encode("utf-8")
    ).hexdigest()


def self_test() -> None:
    a = seed_for("fsw/apps/hwlib/sim/src/libcan.c", "fsw/build/obj/libcan.c.o")
    b = seed_for("fsw/apps/hwlib/sim/src/libspi.c", "fsw/build/obj/libspi.c.o")
    require(a == seed_for("fsw/apps/hwlib/sim/src/libcan.c",
                         "fsw/build/obj/libcan.c.o"), "unstable_seed")
    require(a != b, "same_seed_distinct_unit")
    require(a != seed_for("fsw/apps/hwlib/sim/src/libcan.c",
                          "fsw/build/other/libcan.c.o"), "object_path_omitted")
    require(relative("/work/nos3/fsw/apps/test.c", CONTAINER_ROOT)
            == "fsw/apps/test.c", "root_normalization")
    print("P2X_V2E_SOURCE_OBJECT_SEED_SELF_TEST=PASS")


def main() -> None:
    if sys.argv[1:] == ["--self-test"]:
        self_test()
        return
    require(len(sys.argv) >= 2, "missing_compiler")
    compiler, args = sys.argv[1], sys.argv[2:]
    require(Path(compiler).name in ("cc", "gcc") and
            Path(compiler).parent == Path("/usr/bin"), "unexpected_compiler")
    if "-c" not in args:
        # CMake compiler identity / link-only checks do not generate TU coverage.
        os.execv(compiler, [compiler, *args])
    require(args.count("-c") == 1 and args.index("-c") + 1 < len(args),
            "ambiguous_compile_source")
    require(args.count("-o") == 1 and args.index("-o") + 1 < len(args),
            "missing_or_ambiguous_object")
    require(not any(x.startswith("-frandom-seed") for x in args),
            "preexisting_random_seed_override")
    src_arg = args[args.index("-c") + 1]
    out_arg = args[args.index("-o") + 1]
    src = relative(src_arg, Path.cwd())
    obj = relative(out_arg, Path.cwd())
    require(src.endswith(".c") and obj.endswith(".o"), "unexpected_compile_unit")
    seed = seed_for(src, obj)
    print("P2X_V2E_SEED_SOURCE=" + src + " OBJECT=" + obj +
          " SEED=" + seed, flush=True, file=sys.stderr)
    os.execv(compiler, [compiler, "-frandom-seed=" + seed, *args])


if __name__ == "__main__":
    main()
