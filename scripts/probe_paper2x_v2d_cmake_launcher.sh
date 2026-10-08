#!/usr/bin/env bash
# P2X v2d: disposable TWO-source CMake compiler launcher microprobe.
# No host bind mount, NOS3 build, runtime, data modification, or network.
set -Eeuo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
IMAGE="ivvitc/nos3-64@sha256:06aa945988a7770b759022c2e1f6f2531818c087fe41a4739d3a3a7f2a9dcce2"
fail() { echo "P2X_V2D_LAUNCHER_PROBE_HOLD=$*" >&2; exit 1; }

test "$(basename "$ROOT")" = "mission-aware-satellite-cyber-recovery" || fail wrong_project_root
case "$(git -C "$ROOT" remote get-url origin 2>/dev/null || true)" in
  https://github.com/Zartharas/mission-aware-satellite-cyber-recovery|https://github.com/Zartharas/mission-aware-satellite-cyber-recovery.git|git@github.com:Zartharas/mission-aware-satellite-cyber-recovery|git@github.com:Zartharas/mission-aware-satellite-cyber-recovery.git|ssh://git@github.com/Zartharas/mission-aware-satellite-cyber-recovery|ssh://git@github.com/Zartharas/mission-aware-satellite-cyber-recovery.git) ;;
  *) fail wrong_research_origin;;
esac
test -z "$(git -C "$ROOT" status --porcelain)" || fail research_tree_dirty
command -v docker >/dev/null 2>&1 || fail docker_unavailable
test "$(docker image inspect "$IMAGE" --format '{{.Os}}/{{.Architecture}}' 2>/dev/null)" = "linux/amd64" || fail locked_image_wrong_arch

# Attach the heredoc to the container stdin. Docker without -i silently delivered EOF
# to bash -s in the original pilot, causing a false outer PASS with no inner run.
# Write to an ephemeral HOST /tmp log to avoid heredoc within a quoted $(...)
# expression, whose parsing differs in macOS Bash 3.2. Never stage in NOS3.
PROBE_LOG="$(mktemp "${TMPDIR:-/tmp}/p2x-v2d-inner.XXXXXX")" || fail temporary_probe_log_unavailable
trap 'rm -f -- "$PROBE_LOG"' EXIT
if docker run --rm -i --read-only --platform linux/amd64 --network none \
  --tmpfs /tmp:rw,exec,mode=1777,size=128m \
  --user "$(id -u):$(id -g)" -e HOME=/tmp "$IMAGE" bash -s >"$PROBE_LOG" 2>&1 <<'IN_CONTAINER'
set -Eeuo pipefail
DIR=/tmp/p2x-v2d-cmake-launcher
trap 'rc=$?; echo "P2X_V2D_INNER_FAILURE=rc:$rc line:$LINENO"; for log in "$DIR/config-a.log" "$DIR/compile-a.log" "$DIR/config-b.log" "$DIR/compile-b.log"; do if [ -f "$log" ]; then echo "P2X_V2D_DIAGNOSTIC_LOG=$log"; tail -n 14 "$log"; fi; done' ERR
mkdir -p "$DIR/source"
cat > "$DIR/source/CMakeLists.txt" <<'CMAKE'
cmake_minimum_required(VERSION 3.17)
project(P2X_V2D_LAUNCHER_PROBE LANGUAGES C)
add_library(p2x_two_source STATIC alpha.c beta.c)
target_compile_options(p2x_two_source PRIVATE -g -O0 -fprofile-arcs -ftest-coverage)
CMAKE
printf '%s\n' 'int p2x_alpha(int n) { return n > 0 ? n + 1 : 0; }' > "$DIR/source/alpha.c"
printf '%s\n' 'int p2x_beta(int n) { return n < 0 ? n - 1 : 0; }' > "$DIR/source/beta.c"

cat > "$DIR/seed_launcher.py" <<'PY'
#!/usr/bin/env python3
import os
from pathlib import Path
import sys
require_root = Path("/tmp/p2x-v2d-cmake-launcher/source").resolve()
if len(sys.argv) < 3:
    raise SystemExit("P2X_LAUNCHER_INVALID_INVOCATION")
compiler, args = sys.argv[1], sys.argv[2:]
sources = [x for x in args if x.endswith(".c") and not x.startswith("-")]
if len(sources) != 1 or "-c" not in args:
    os.execvp(compiler, [compiler, *args])
source = Path(sources[0])
source = (source if source.is_absolute() else Path.cwd() / source).resolve()
try:
    relative_source = source.relative_to(require_root).as_posix()
except ValueError:
    # CMake's own compiler-detection sources may be outside this probe's source root.
    os.execvp(compiler, [compiler, *args])
if "-o" not in args or args.index("-o") + 1 >= len(args):
    raise SystemExit("P2X_LAUNCHER_MISSING_COMPILE_OUTPUT")
object_name = Path(args[args.index("-o") + 1]).name
seed = "P2X-NOS3-RG-001:v2d:" + relative_source + ":" + object_name
print("P2X_LAUNCHER_SOURCE=" + relative_source + " SEED=" + seed, flush=True)
os.execvp(compiler, [compiler, "-frandom-seed=" + seed, *args])
PY
chmod 755 "$DIR/seed_launcher.py"

# CMake 3.26 initializes its target's C compiler launcher from this environment
# variable on FIRST configure. Every source/target gets its own stable seed string.
export CMAKE_C_COMPILER_LAUNCHER="/usr/bin/python3;$DIR/seed_launcher.py"
echo "===== FIRST DISPOSABLE CMAKE BUILD ====="
cmake -S "$DIR/source" -B "$DIR/build-a" -DCMAKE_BUILD_TYPE=Debug > "$DIR/config-a.log" 2>&1
cmake --build "$DIR/build-a" --verbose > "$DIR/compile-a.log" 2>&1
echo "===== SECOND INDEPENDENT DISPOSABLE CMAKE BUILD ====="
cmake -S "$DIR/source" -B "$DIR/build-b" -DCMAKE_BUILD_TYPE=Debug > "$DIR/config-b.log" 2>&1
cmake --build "$DIR/build-b" --verbose > "$DIR/compile-b.log" 2>&1

python3 - "$DIR" <<'PY'
from pathlib import Path
import re
import struct
import sys
root=Path(sys.argv[1])
results={}
for build in ("a", "b"):
    log=(root/("compile-"+build+".log")).read_text(errors="replace")
    pairs=re.findall(r"P2X_LAUNCHER_SOURCE=(alpha\.c|beta\.c) SEED=(\S+)",log)
    assert len(pairs)==2, "COMPILER_LAUNCHER_DID_NOT_RUN_TWICE:"+build
    assert {x for x,_ in pairs}=={"alpha.c","beta.c"}, "LAUNCHER_SOURCE_COVERAGE:"+build
    assert len({seed for _,seed in pairs})==2, "NON_UNIQUE_SOURCE_SEEDS:"+build
    results[build] = dict(pairs)
    print("CMAKE_LAUNCHER_BUILD="+build)
    for source,seed in sorted(pairs):
        files=list((root/("build-"+build)).rglob(source+".gcno"))
        assert len(files)==1, "GCNO_MISSING_OR_AMBIGUOUS:"+build+":"+source
        h=files[0].read_bytes()[:12]
        assert h[:4] in (b"oncg",b"gcno") and len(h)==12,"INVALID_GCNO_HEADER"
        stamp=struct.unpack_from("<I",h,8)[0]
        print("SOURCE="+source+" SEED="+seed+" GCOV_STAMP="+str(stamp))
        results[build][source]=(seed,stamp)
assert results["a"]==results["b"],"SAME_SOURCE_NOT_REPRODUCIBLE"
assert results["a"]["alpha.c"][0] != results["a"]["beta.c"][0],"SOURCE_SEEDS_NOT_UNIQUE"
print("P2X_V2D_SOURCE_UNIQUE_SEED_STRINGS=PASS")
print("P2X_V2D_CMAKE_COMPILER_LAUNCHER_REPEATABILITY=PASS")
print("P2X_V2D_GCNO_HEADER_REPRODUCIBILITY=PASS")
print("P2X_V2D_FULL_NOS3_BYTE_REPRODUCIBILITY=NOT_TESTED")
PY
IN_CONTAINER
then
  cat "$PROBE_LOG"
else
  cat "$PROBE_LOG"
  fail "container_execution_or_inner_assertion_failed"
fi

# Inner result markers must be emitted by ACTUAL executed fixture, not merely
# occur in the unexecuted source text. Exactly one each; missing/duplicate fails.
for marker in \
  "P2X_V2D_SOURCE_UNIQUE_SEED_STRINGS=PASS" \
  "P2X_V2D_CMAKE_COMPILER_LAUNCHER_REPEATABILITY=PASS" \
  "P2X_V2D_GCNO_HEADER_REPRODUCIBILITY=PASS" \
  "P2X_V2D_FULL_NOS3_BYTE_REPRODUCIBILITY=NOT_TESTED"
do
  count="$(grep -Fxc -- "$marker" "$PROBE_LOG" || true)"
  test "$count" = "1" || fail "missing_or_duplicate_inner_marker:$marker:count=$count"
done

test -z "$(git -C "$ROOT" status --porcelain)" || fail host_repo_changed
echo "P2X_V2D_INNER_GATE=PASS"
echo "P2X_V2D_PROBE=PASS"
echo "HOST_NOS3_SOURCE_MUTATION=NO"
echo "NEW_NOS3_BUILD_EXECUTED=NO"
echo "NOS3_RUNTIME_EXECUTED=NO"
