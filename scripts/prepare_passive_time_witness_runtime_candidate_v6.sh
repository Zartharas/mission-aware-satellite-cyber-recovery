#!/usr/bin/env bash
# WP4 V6 privilege-separated passive time-witness candidate generator.
# EMIT ONLY. Does not invoke candidate, transaction-v4, receiver, or Docker.
set -Eeuo pipefail

readonly ACCEPTED_V5_GENERATOR_SHA256="9f006bc7e13e73b9702d2f63c5d97413a77151af0a9d63e3ed88d3cba121bed7"
readonly ACCEPTED_TRANSACTION_V4_SHA256="aa96c912a2311ee8c2edec2d5bbfbaf90f0387f78476f9fe80a83773c10c2d1d"
readonly ACCEPTED_RECEIVER_SHA256="64ecadbd0c8c8d69e5509bb7bbe9115bfe8ebc812961eaf77f8ec3331168726c"
readonly DESIGN_LOCK_SHA256="a7774fc5f0ccb23ef84fe02d6f802b3b199a870b96dfc3d01fcd76616e9f0a2c"
readonly DESIGN_LOCK_AMENDMENT_1_SHA256="df9c737269d39baeb87affef9c6ac5d848cf7e8ef5b395ca4cd852071caac139"
readonly FORTYTWO_SOURCE_COMMIT="eda252bf31f27850e867e698cfdd963e143ead1f"
readonly FORTYTWO_SOURCE_TREE="541dbc9c3c3d42887b9c668a218ffc3726d24346"
readonly FORTYTWO_42_SHA256="9c0062d2a447a6340e7c191850ff952d3f8768dd307e3e7fb141e777961e60c7"
readonly FORTYTWO_42_BYTES="2250376"
readonly FORTYTWO_42_MODE="0755"
readonly FORTYTWO_HANDOFF_DEST="fortytwo-runtime/42"

fail() { echo "[ERROR] $*" >&2; exit 2; }

physical_tmp_root() {
  python3 - <<'PYTMP'
import os, tempfile
print(os.path.realpath(tempfile.gettempdir()))
PYTMP
}

emit_path="${PASSIVE_TIME_WITNESS_V6_EMIT_PATH:-}"
[[ -n "$emit_path" ]] || fail "PASSIVE_TIME_WITNESS_V6_EMIT_PATH is required"

ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" ||
  fail "Run generator from governed repository"
ROOT="$(cd "$ROOT" && pwd -P)"
V5_GENERATOR="$ROOT/scripts/prepare_passive_time_witness_runtime_candidate_v5.sh"
TRANSACTION_V4="$ROOT/scripts/nos3_runtime_transaction_v4.py"
HANDOFF_RECEIVER="$ROOT/scripts/receive_runtime_material_handoff_v1.py"

[[ "$(shasum -a 256 "$V5_GENERATOR" | awk '{print $1}')" == "$ACCEPTED_V5_GENERATOR_SHA256" ]] ||
  fail "V5 generator identity mismatch"
[[ "$(shasum -a 256 "$TRANSACTION_V4" | awk '{print $1}')" == "$ACCEPTED_TRANSACTION_V4_SHA256" ]] ||
  fail "transaction-v4 identity mismatch"
[[ "$(shasum -a 256 "$HANDOFF_RECEIVER" | awk '{print $1}')" == "$ACCEPTED_RECEIVER_SHA256" ]] ||
  fail "handoff receiver identity mismatch"

tmp_root="$(physical_tmp_root)"
emit_parent="$(cd "$(dirname "$emit_path")" && pwd -P)"
emit_leaf="$(basename "$emit_path")"
case "$emit_parent/$emit_leaf" in
  "$tmp_root"/*) ;;
  *) fail "V6 emission restricted to physical system temp tree" ;;
esac
case "$emit_parent/$emit_leaf" in
  "$ROOT"|"$ROOT"/*) fail "V6 emission must not target repository" ;;
esac
[[ ! -e "$emit_parent/$emit_leaf" && ! -L "$emit_parent/$emit_leaf" ]] ||
  fail "V6 emit destination already exists"

umask 077
workdir="$(mktemp -d "$tmp_root/.wp4-v6-generator.XXXXXX")"
v5_candidate="$workdir/candidate-v5.sh"
tmp_emit="$(mktemp "$emit_parent/.${emit_leaf}.v6.XXXXXX")"

cleanup() {
  rc=$?
  rm -f -- "$v5_candidate" "$tmp_emit"
  rmdir "$workdir" 2>/dev/null || true
  trap - EXIT
  exit "$rc"
}
trap cleanup EXIT

PASSIVE_TIME_WITNESS_V5_EMIT_PATH="$v5_candidate" \
  bash "$V5_GENERATOR" >/dev/null

python3 - "$v5_candidate" "$tmp_emit" <<'PYTRANSFORM'
from pathlib import Path
import sys

source = Path(sys.argv[1]).read_text(encoding="utf-8")
output = Path(sys.argv[2])

source = source.replace("V5", "V6").replace("v5", "v6")

def one(old, new, label):
    global source
    count = source.count(old)
    if count != 1:
        raise SystemExit("%s anchor count=%d" % (label, count))
    source = source.replace(old, new, 1)

source = source.replace(
    "nos3_runtime_transaction_v3.py",
    "nos3_runtime_transaction_v4.py",
)
source = source.replace(
    "--materialize-v5-transaction",
    "--materialize-v6-stream",
)

one(
    'TRANSACTION_TOOL="$ROOT/scripts/nos3_runtime_transaction_v4.py"\n',
    'TRANSACTION_TOOL="$ROOT/scripts/nos3_runtime_transaction_v4.py"\n'
    'HANDOFF_RECEIVER="$ROOT/scripts/receive_runtime_material_handoff_v1.py"\n'
    'MATERIALIZER_USER="wp4d064mat"\n'
    'PINNED_PYTHON="/usr/local/bin/python3"\n',
    "V6 receiver prelude",
)

start = source.index(
    'AUTHORIZED_TRANSACTION_ROOT="${PASSIVE_TIME_WITNESS_V6_AUTHORIZED_ROOT:-}"'
)
end = source.index("\nHARDWARE_SIMS=(\n", start)

handoff = r'''AUTHORIZED_TRANSACTION_ROOT="${PASSIVE_TIME_WITNESS_V6_AUTHORIZED_ROOT:-}"
[[ -n "$AUTHORIZED_TRANSACTION_ROOT" ]] || {
  echo "[FAIL-CLOSED] PASSIVE_TIME_WITNESS_V6_AUTHORIZED_ROOT is required." >&2
  exit 1
}

readonly FORTYTWO_SOURCE_COMMIT="eda252bf31f27850e867e698cfdd963e143ead1f"
readonly FORTYTWO_SOURCE_TREE="541dbc9c3c3d42887b9c668a218ffc3726d24346"
readonly FORTYTWO_42_SHA256="9c0062d2a447a6340e7c191850ff952d3f8768dd307e3e7fb141e777961e60c7"
readonly FORTYTWO_42_BYTES="2250376"
readonly FORTYTWO_42_MODE="0755"
readonly FORTYTWO_HANDOFF_DEST="fortytwo-runtime/42"

command -v sudo >/dev/null 2>&1 || {
  echo "[FAIL-CLOSED] sudo is required for UID599 materialization." >&2
  exit 1
}
sudo -n -u "$MATERIALIZER_USER" /usr/bin/true >/dev/null 2>&1 || {
  echo "[FAIL-CLOSED] noninteractive UID599 materialization unavailable." >&2
  exit 1
}

FORTYTWO_SOURCE_REPO="$ROOT/external/fortytwo"
FORTYTWO_SOURCE_BINARY="$FORTYTWO_SOURCE_REPO/42"

[[ "$(git -C "$FORTYTWO_SOURCE_REPO" rev-parse HEAD)" == "eda252bf31f27850e867e698cfdd963e143ead1f" ]] || {
  echo "[FAIL-CLOSED] Fortytwo source commit mismatch." >&2
  exit 1
}
[[ "$(git -C "$FORTYTWO_SOURCE_REPO" rev-parse 'HEAD^{tree}')" == "541dbc9c3c3d42887b9c668a218ffc3726d24346" ]] || {
  echo "[FAIL-CLOSED] Fortytwo source tree mismatch." >&2
  exit 1
}
[[ -z "$(git -C "$FORTYTWO_SOURCE_REPO" status --porcelain)" ]] || {
  echo "[FAIL-CLOSED] Fortytwo source repository not clean." >&2
  exit 1
}

"$PINNED_PYTHON" - "$FORTYTWO_SOURCE_BINARY" <<'PYV6FORTYTWO_SOURCE'
import hashlib
import os
import stat
import sys

path = os.path.realpath(sys.argv[1])
st1 = os.stat(path, follow_symlinks=False)
if (
    not stat.S_ISREG(st1.st_mode)
    or stat.S_ISLNK(st1.st_mode)
    or st1.st_nlink != 1
    or st1.st_size != 2250376
    or stat.S_IMODE(st1.st_mode) != 0o755
):
    raise SystemExit("Fortytwo source executable identity mismatch")
h = hashlib.sha256()
with open(path, "rb") as stream:
    for chunk in iter(lambda: stream.read(1024 * 1024), b""):
        h.update(chunk)
st2 = os.stat(path, follow_symlinks=False)
if (
    st1.st_dev, st1.st_ino, st1.st_mode, st1.st_nlink, st1.st_size
) != (
    st2.st_dev, st2.st_ino, st2.st_mode, st2.st_nlink, st2.st_size
):
    raise SystemExit("Fortytwo source executable identity drift")
if h.hexdigest() != "9c0062d2a447a6340e7c191850ff952d3f8768dd307e3e7fb141e777961e60c7":
    raise SystemExit("Fortytwo source executable SHA mismatch")
print("V6_FRESH_FORTYTWO_SOURCE_IDENTITY=PASS")
PYV6FORTYTWO_SOURCE

UID599_PROCESS_COUNT="$(
  /bin/ps -axo uid= |
  /usr/bin/awk '$1 == 599 { count += 1 } END { print count + 0 }'
)"
[[ "$UID599_PROCESS_COUNT" == "0" ]] || {
  echo "[FAIL-CLOSED] fresh host gate observed an existing UID599 process." >&2
  exit 1
}

sudo -n -u "$MATERIALIZER_USER" /usr/bin/env \
  "HOME=/var/empty" \
  "$PINNED_PYTHON" - \
    "$ROOT" \
    "$CONTRACT_PATH" \
    "$AUTHORIZED_TRANSACTION_ROOT" <<'PYV6HOST'
import ctypes
import ctypes.util
import hashlib
import json
import os
import stat
import subprocess
import sys

repo, contract_path, authorized_root = sys.argv[1:]
repo = os.path.realpath(repo)
authorized_root = os.path.realpath(authorized_root)

def fail(msg):
    raise SystemExit(msg)

def read_regular(path):
    st1 = os.stat(path, follow_symlinks=False)
    if (
        not stat.S_ISREG(st1.st_mode)
        or stat.S_ISLNK(st1.st_mode)
        or st1.st_nlink != 1
    ):
        fail("governance file object invalid")
    with open(path, "rb") as stream:
        raw = stream.read()
    st2 = os.stat(path, follow_symlinks=False)
    if (
        st1.st_dev, st1.st_ino, st1.st_mode, st1.st_nlink, st1.st_size
    ) != (
        st2.st_dev, st2.st_ino, st2.st_mode, st2.st_nlink, st2.st_size
    ):
        fail("governance file identity drift")
    if len(raw) != st1.st_size:
        fail("governance file size drift")
    return raw, hashlib.sha256(raw).hexdigest()

contract_raw, _ = read_regular(contract_path)
contract = json.loads(contract_raw.decode("utf-8"))
amendment = contract.get(
    "passive_time_witness_runtime_candidate_v6_design_amendment_1"
)
if not isinstance(amendment, dict):
    fail("V6 amendment missing")
impl = amendment.get(
    "passive_time_witness_runtime_candidate_v6_implementation"
)
if not isinstance(impl, dict):
    fail("V6 implementation missing")
supplemental = impl.get("supplemental_runtime_artifact_fortytwo_42")
expected_supplemental = {
    "source_path": "external/fortytwo/42",
    "source_commit": "eda252bf31f27850e867e698cfdd963e143ead1f",
    "source_tree": "541dbc9c3c3d42887b9c668a218ffc3726d24346",
    "sha256": "9c0062d2a447a6340e7c191850ff952d3f8768dd307e3e7fb141e777961e60c7",
    "bytes": 2250376,
    "mode": 0o755,
    "nlink": 1,
    "handoff_destination": "fortytwo-runtime/42",
    "canonical_manifest_member": False,
}
if supplemental != expected_supplemental:
    fail("V6 supplemental Fortytwo contract binding mismatch")
binding = impl.get("active_host_exclusive_writer_evidence_v3")
if not isinstance(binding, dict):
    fail("V6 host-evidence binding missing")
if binding.get("schema") != 2:
    fail("schema-2 host evidence required")

evidence_rel = binding.get("path")
if (
    not isinstance(evidence_rel, str)
    or evidence_rel.startswith("/")
    or ".." in evidence_rel.split("/")
):
    fail("host-evidence relative path invalid")
evidence_path = os.path.join(repo, evidence_rel)
evidence_raw, evidence_sha = read_regular(evidence_path)
if evidence_sha != binding.get("sha256"):
    fail("host-evidence SHA binding mismatch")
evidence = json.loads(evidence_raw.decode("utf-8"))
if evidence.get("schema") != 2:
    fail("host-evidence schema mismatch")
concurrent = evidence.get("concurrent_writer_observation")
serialization = evidence.get("serialization_readiness")
if not isinstance(concurrent, dict) or not isinstance(serialization, dict):
    fail("host-evidence concurrent-writer/serialization blocks missing")
if concurrent.get("external_noncooperating_writer_absence_proven") is not False:
    fail("concurrent-writer claim must remain false")
if serialization.get("external_noncooperating_writer_absence_proven") is not False:
    fail("serialization external-writer claim must remain false")

root_expected = evidence.get("authorized_root")
if not isinstance(root_expected, dict):
    fail("authorized-root evidence missing")
if root_expected.get("absolute_path") != authorized_root:
    fail("authorized-root path mismatch")

current = "/"
for component in authorized_root.strip("/").split("/"):
    current = os.path.join(current, component)
    lst = os.lstat(current)
    if stat.S_ISLNK(lst.st_mode):
        fail("authorized-root path component symlink")

root_st = os.lstat(authorized_root)
if not stat.S_ISDIR(root_st.st_mode) or stat.S_ISLNK(root_st.st_mode):
    fail("authorized root not plain directory")
expected_root = (
    root_expected.get("device"),
    root_expected.get("inode"),
    root_expected.get("uid"),
    root_expected.get("gid"),
    int(root_expected.get("mode"), 8),
    root_expected.get("nlink"),
)
current_root = (
    root_st.st_dev,
    root_st.st_ino,
    root_st.st_uid,
    root_st.st_gid,
    stat.S_IMODE(root_st.st_mode),
    root_st.st_nlink,
)
if current_root != expected_root:
    fail("authorized-root identity drift")
if root_st.st_uid != os.geteuid() or os.geteuid() != 599:
    fail("authorized-root owner/EUID mismatch")
if os.listdir(authorized_root):
    fail("authorized root not empty")

least = evidence.get("least_privilege_limitation")
parent = evidence.get("parent_traversal_remediation")
if not isinstance(least, dict) or not isinstance(parent, dict):
    fail("parent evidence missing")
home_path = least.get("authorized_root_parent_path")
documents_path = parent.get("parent_path")
for obj, path, fields in (
    (least, home_path, (
        "authorized_root_parent_device",
        "authorized_root_parent_inode",
        "authorized_root_parent_uid",
        "authorized_root_parent_gid",
        "authorized_root_parent_mode",
    )),
    (parent, documents_path, ("device", "inode", "uid", "gid", "mode")),
):
    if not isinstance(path, str):
        fail("parent path invalid")
    st = os.lstat(path)
    if not stat.S_ISDIR(st.st_mode) or stat.S_ISLNK(st.st_mode):
        fail("parent path type drift")
    if obj is least:
        expected = (
            obj[fields[0]], obj[fields[1]], obj[fields[2]], obj[fields[3]],
            int(obj[fields[4]], 8),
        )
    else:
        expected = (
            obj[fields[0]], obj[fields[1]], obj[fields[2]], obj[fields[3]],
            int(obj[fields[4]], 8),
        )
    current_tuple = (
        st.st_dev, st.st_ino, st.st_uid, st.st_gid, stat.S_IMODE(st.st_mode)
    )
    if current_tuple != expected:
        fail("parent identity drift: " + path)

xattrs = parent.get("xattrs")
if not isinstance(xattrs, dict):
    fail("Documents xattr evidence missing")
expected_names = xattrs.get("sorted_name_set")
if expected_names != ["com.apple.macl", "com.apple.provenance"]:
    fail("Documents xattr expected name set drift")

if sys.platform != "darwin":
    fail("fresh xattr observation requires Darwin")
libc_name = ctypes.util.find_library("c")
if not libc_name:
    fail("libc unavailable")
libc = ctypes.CDLL(libc_name, use_errno=True)
listxattr = libc.listxattr
listxattr.argtypes = [
    ctypes.c_char_p, ctypes.c_char_p, ctypes.c_size_t, ctypes.c_int
]
listxattr.restype = ctypes.c_ssize_t
getxattr = libc.getxattr
getxattr.argtypes = [
    ctypes.c_char_p, ctypes.c_char_p, ctypes.c_void_p, ctypes.c_size_t,
    ctypes.c_uint32, ctypes.c_int,
]
getxattr.restype = ctypes.c_ssize_t
XATTR_NOFOLLOW = 0x0001
path_b = os.fsencode(documents_path)
needed = listxattr(path_b, None, 0, XATTR_NOFOLLOW)
if needed < 0:
    fail("listxattr size query failed")
buf = ctypes.create_string_buffer(needed if needed else 1)
got = listxattr(path_b, buf, needed, XATTR_NOFOLLOW)
if got < 0:
    fail("listxattr data query failed")
names = sorted(
    os.fsdecode(v)
    for v in bytes(buf.raw[:got]).split(b"\x00")
    if v
)
if names != expected_names:
    fail("Documents xattr name set drift")

for name in names:
    rec = xattrs.get(name.replace(".", "_"))
    if rec is None:
        rec = xattrs.get(name)
    if not isinstance(rec, dict):
        fail("xattr identity record missing: " + name)
    name_b = os.fsencode(name)
    size = getxattr(path_b, name_b, None, 0, 0, XATTR_NOFOLLOW)
    if size < 0:
        fail("getxattr size query failed: " + name)
    value = ctypes.create_string_buffer(size if size else 1)
    got = getxattr(path_b, name_b, value, size, 0, XATTR_NOFOLLOW)
    if got < 0:
        fail("getxattr data query failed: " + name)
    raw = bytes(value.raw[:got])
    if got != rec.get("capture_length"):
        fail("xattr length drift: " + name)
    if hashlib.sha256(raw).hexdigest() != rec.get("capture_sha256"):
        fail("xattr SHA drift: " + name)

acl = subprocess.run(
    ["/bin/ls", "-lde", documents_path],
    check=True,
    capture_output=True,
    text=True,
).stdout
if "user:wp4d064mat allow search" not in acl:
    fail("Documents materializer search-only ACL missing")
for forbidden in (" allow write", " allow delete", " allow add_file"):
    if forbidden in acl:
        fail("Documents materializer ACL grants unexpected write capability")

tm = subprocess.run(
    ["/usr/bin/tmutil", "status"],
    check=False,
    capture_output=True,
    text=True,
)
if tm.returncode not in (0, 1):
    fail("Time Machine status query failed")
tm_text = (tm.stdout + "\n" + tm.stderr).lower()
if "running = 1" in tm_text or '"running":1' in tm_text:
    fail("Time Machine is running")

print("V6_FRESH_EXECUTION_TIME_HOST_RECHECK=PASS")
print("external_noncooperating_writer_absence_proven=false")
PYV6HOST

sudo -n -u "$MATERIALIZER_USER" /usr/bin/env \
  "HOME=/var/empty" \
  "$PINNED_PYTHON" - "$AUTHORIZED_TRANSACTION_ROOT" <<'PYV6LOCK'
import errno
import fcntl
import os
import stat
import sys

root = os.path.realpath(sys.argv[1])
root_fd = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
lock_fd = None
lock_name = ".wp4-d064-v4-transaction.lock"
try:
    rst = os.fstat(root_fd)
    if rst.st_uid != os.geteuid() or os.geteuid() != 599:
        raise SystemExit("contention probe root owner/EUID mismatch")
    if os.listdir(root_fd):
        raise SystemExit("contention probe root not empty")
    lock_fd = os.open(
        lock_name,
        os.O_RDWR | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
        0o600,
        dir_fd=root_fd,
    )
    os.fchmod(lock_fd, 0o600)
    fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    fst = os.fstat(lock_fd)
    lst = os.lstat(lock_name, dir_fd=root_fd)
    if (
        not stat.S_ISREG(fst.st_mode)
        or fst.st_nlink != 1
        or fst.st_uid != 599
        or stat.S_IMODE(fst.st_mode) != 0o600
        or fst.st_dev != rst.st_dev
        or (fst.st_dev, fst.st_ino) != (lst.st_dev, lst.st_ino)
    ):
        raise SystemExit("contention probe lock identity invalid")
    os.unlink(lock_name, dir_fd=root_fd)
    os.fsync(root_fd)
    if os.listdir(root_fd):
        raise SystemExit("contention probe root not empty after cleanup")
    print("V6_PREINVOCATION_CONTENTION_PROBE=PASS")
    print("V6_PREINVOCATION_FLOCK_PROBE=PASS")
finally:
    if lock_fd is not None:
        try:
            fcntl.flock(lock_fd, fcntl.LOCK_UN)
        except OSError:
            pass
        os.close(lock_fd)
    os.close(root_fd)
PYV6LOCK

SOURCE_COMMIT="$(git rev-parse HEAD)"
SOURCE_TREE="$(git rev-parse 'HEAD^{tree}')"
[[ "$SOURCE_COMMIT" =~ ^[0-9a-f]{40}$ && "$SOURCE_TREE" =~ ^[0-9a-f]{40}$ ]] || {
  echo "[FAIL-CLOSED] V6 governed source Git identities invalid." >&2
  exit 1
}

TRANSACTION_BASENAME="wp4-passive-time-witness-v6-$SAFE_ID"
RUNTIME_MATERIAL_PARENT="$(mktemp -d "$(python3 - <<'PYTMP'
import os, tempfile
print(os.path.realpath(tempfile.gettempdir()))
PYTMP
)/wp4-d064-v6-runtime-$SAFE_ID.XXXXXX")"
chmod 700 "$RUNTIME_MATERIAL_PARENT"
RUNTIME_MATERIAL_BASENAME="runtime-material"
RUNTIME_MATERIAL_ROOT="$RUNTIME_MATERIAL_PARENT/$RUNTIME_MATERIAL_BASENAME"
RUNTIME_MATERIAL_PUBLISHED=0

cleanup_v6_runtime_material_only() {
  local rc=$?
  trap - EXIT INT TERM HUP
  set +e
  python3 - "$RUNTIME_MATERIAL_PARENT" <<'PYCLEANV6'
import os,shutil,stat,sys,tempfile
path=sys.argv[1]
if not path or not os.path.lexists(path):
    raise SystemExit(0)
root=os.path.realpath(tempfile.gettempdir())
real=os.path.realpath(path)
st=os.lstat(path)
if (
    real != path
    or os.path.dirname(real) != root
    or not os.path.basename(real).startswith("wp4-d064-v6-runtime-")
    or stat.S_ISLNK(st.st_mode)
    or not stat.S_ISDIR(st.st_mode)
    or st.st_uid != os.geteuid()
    or stat.S_IMODE(st.st_mode) != 0o700
):
    raise SystemExit(2)
shutil.rmtree(path)
PYCLEANV6
  local cleanup_rc=$?
  if (( cleanup_rc != 0 && rc == 0 )); then
    rc=1
  fi
  exit "$rc"
}
trap cleanup_v6_runtime_material_only EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
trap 'exit 129' HUP

ATTEMPT_SENTINEL_REL="$(
  python3 - "$CONTRACT_PATH" <<'PYSENT'
import json,sys
c=json.load(open(sys.argv[1],encoding="utf-8"))
a=c.get("passive_time_witness_runtime_candidate_v6_design_amendment_1",{})
i=a.get("passive_time_witness_runtime_candidate_v6_implementation",{})
v=i.get("attempt_consumption_sentinel_relpath")
if not isinstance(v,str) or not v.startswith("artifacts/downlink-diagnostics/"):
    raise SystemExit(1)
if v.startswith("/") or ".." in v.split("/"):
    raise SystemExit(1)
print(v)
PYSENT
)" || {
  echo "[FAIL-CLOSED] V6 attempt-consumption sentinel governance absent." >&2
  exit 1
}
ATTEMPT_SENTINEL="$ROOT/$ATTEMPT_SENTINEL_REL"

python3 - "$ROOT" "$ATTEMPT_SENTINEL" "$RUN_ID" <<'PYCONSUME'
import json,os,stat,sys
root,path,run_id=sys.argv[1:]
root=os.path.realpath(root)
parent=os.path.dirname(path)
leaf=os.path.basename(path)
if os.path.realpath(parent) != parent:
    raise SystemExit("attempt sentinel parent canonical drift")
if os.path.commonpath((root,parent)) != root:
    raise SystemExit("attempt sentinel parent escapes repository")
if not leaf or leaf in (".","..") or "/" in leaf or "\\" in leaf:
    raise SystemExit("attempt sentinel basename invalid")
pfd=os.open(parent,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
try:
    pst=os.fstat(pfd)
    if not stat.S_ISDIR(pst.st_mode) or pst.st_uid != os.geteuid():
        raise SystemExit("attempt sentinel parent identity invalid")
    raw=(json.dumps({
      "schema":1,
      "status":"D064_V6_ATTEMPT_CONSUMED_BEFORE_PRODUCTION_TRANSACTION",
      "run_id":run_id,
      "automatic_retry_authorized":False,
    },ensure_ascii=True,sort_keys=True,separators=(",",":"))+"\n").encode()
    fd=os.open(
        leaf,
        os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,
        0o600,
        dir_fd=pfd,
    )
    try:
        off=0
        while off < len(raw):
            n=os.write(fd,raw[off:])
            if n <= 0:
                raise SystemExit("attempt sentinel short write")
            off += n
        os.fsync(fd)
        fst=os.fstat(fd)
        if (
            not stat.S_ISREG(fst.st_mode)
            or fst.st_nlink != 1
            or fst.st_uid != os.geteuid()
            or fst.st_size != len(raw)
        ):
            raise SystemExit("attempt sentinel identity invalid")
    finally:
        os.close(fd)
    os.fsync(pfd)
finally:
    os.close(pfd)
PYCONSUME

HANDOFF_STATUS_FILE="$RUNTIME_MATERIAL_PARENT/receiver-status.txt"
: > "$HANDOFF_STATUS_FILE"
chmod 600 "$HANDOFF_STATUS_FILE"

set +e
sudo -n -u "$MATERIALIZER_USER" /usr/bin/env \
  "HOME=/var/empty" \
  "$PINNED_PYTHON" "$TRANSACTION_TOOL" \
    --materialize-v6-stream \
    --repo-root "$ROOT" \
    --contract "$CONTRACT_PATH" \
    --manifest "$CANONICAL_MANIFEST" \
    --candidate "$CANDIDATE_SELF" \
    --receiver "$HANDOFF_RECEIVER" \
    --authorized-root "$AUTHORIZED_TRANSACTION_ROOT" \
    --final-basename "$TRANSACTION_BASENAME" |
"$PINNED_PYTHON" "$HANDOFF_RECEIVER" \
    --receive \
    --output-parent "$RUNTIME_MATERIAL_PARENT" \
    --final-basename "$RUNTIME_MATERIAL_BASENAME" \
    --expected-candidate-sha256 "$(shasum -a 256 "$CANDIDATE_SELF" | awk '{print $1}')" \
    --expected-transaction-sha256 "$(shasum -a 256 "$TRANSACTION_TOOL" | awk '{print $1}')" \
    --expected-contract-sha256 "$(shasum -a 256 "$CONTRACT_PATH" | awk '{print $1}')" \
    --expected-manifest-sha256 "$(shasum -a 256 "$CANONICAL_MANIFEST" | awk '{print $1}')" \
    --expected-host-evidence-sha256 "c4783f95de24ae309c6fd1c79ea2bc0d27e1dfdb319259351338d0f75c62de9a" \
    --expected-receiver-sha256 "$(shasum -a 256 "$HANDOFF_RECEIVER" | awk '{print $1}')" \
    --expected-source-commit "$SOURCE_COMMIT" \
    --expected-source-tree "$SOURCE_TREE" \
    --expected-fortytwo-source-path "external/fortytwo/42" \
    --expected-fortytwo-source-commit "eda252bf31f27850e867e698cfdd963e143ead1f" \
    --expected-fortytwo-source-tree "541dbc9c3c3d42887b9c668a218ffc3726d24346" \
    --expected-fortytwo-destination "fortytwo-runtime/42" \
    --expected-fortytwo-sha256 "9c0062d2a447a6340e7c191850ff952d3f8768dd307e3e7fb141e777961e60c7" \
    --expected-fortytwo-bytes "2250376" \
    --expected-fortytwo-mode "0755" \
    > "$HANDOFF_STATUS_FILE"
pipe_rc=( "${PIPESTATUS[@]}" )
set -e

(( ${#pipe_rc[@]} == 2 )) || {
  echo "[FAIL-CLOSED] V6 handoff pipeline status cardinality invalid." >&2
  exit 1
}
sender_rc="${pipe_rc[0]}"
receiver_rc="${pipe_rc[1]}"
handoff_output="$(cat "$HANDOFF_STATUS_FILE")"
rm -f -- "$HANDOFF_STATUS_FILE"

[[ "$sender_rc" == 0 && "$receiver_rc" == 0 ]] || {
  echo "[FAIL-CLOSED] V6 privilege-separated material handoff failed." >&2
  exit 1
}
[[ "$(printf '%s\n' "$handoff_output" | grep -Fxc 'V6_RUNTIME_MATERIAL_HANDOFF=PASS')" == 1 ]] || {
  echo "[FAIL-CLOSED] V6 receiver success marker invalid." >&2
  exit 1
}
reported_root="$(printf '%s\n' "$handoff_output" | awk -F= '$1=="V6_RUNTIME_MATERIAL_ROOT"{print substr($0,index($0,"=")+1)}')"
reported_receiver_receipt_sha="$(printf '%s\n' "$handoff_output" | awk -F= '$1=="V6_HANDOFF_RECEIVER_RECEIPT_SHA256"{print substr($0,index($0,"=")+1)}')"
[[ "$reported_root" == "$RUNTIME_MATERIAL_ROOT" && -d "$RUNTIME_MATERIAL_ROOT" && ! -L "$RUNTIME_MATERIAL_ROOT" ]] || {
  echo "[FAIL-CLOSED] V6 runtime-material root mismatch." >&2
  exit 1
}
[[ "$reported_receiver_receipt_sha" =~ ^[0-9a-f]{64}$ ]] || {
  echo "[FAIL-CLOSED] V6 receiver receipt SHA marker invalid." >&2
  exit 1
}

"$PINNED_PYTHON" - \
  "$RUNTIME_MATERIAL_ROOT/.wp4-d064-v6-handoff-receipt.json" \
  "$reported_receiver_receipt_sha" \
  "$SOURCE_COMMIT" \
  "$SOURCE_TREE" \
  "$CANDIDATE_SELF" \
  "$TRANSACTION_TOOL" \
  "$CONTRACT_PATH" \
  "$CANONICAL_MANIFEST" \
  "$HANDOFF_RECEIVER" <<'PYV6RECEIPT'
import hashlib
import json
import os
import stat
import sys

(
    receipt_path,
    expected_receipt_sha,
    source_commit,
    source_tree,
    candidate_path,
    transaction_path,
    contract_path,
    manifest_path,
    receiver_path,
) = sys.argv[1:]

def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

st1 = os.stat(receipt_path, follow_symlinks=False)
if (
    not stat.S_ISREG(st1.st_mode)
    or stat.S_ISLNK(st1.st_mode)
    or st1.st_nlink != 1
    or st1.st_uid != os.geteuid()
    or stat.S_IMODE(st1.st_mode) != 0o600
):
    raise SystemExit("receiver receipt object invalid")
raw = open(receipt_path, "rb").read()
st2 = os.stat(receipt_path, follow_symlinks=False)
if (
    st1.st_dev, st1.st_ino, st1.st_mode, st1.st_nlink, st1.st_size
) != (
    st2.st_dev, st2.st_ino, st2.st_mode, st2.st_nlink, st2.st_size
):
    raise SystemExit("receiver receipt identity drift")
if hashlib.sha256(raw).hexdigest() != expected_receipt_sha:
    raise SystemExit("receiver receipt SHA mismatch")
receipt = json.loads(raw.decode("utf-8"))
canonical = (
    json.dumps(
        receipt,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ) + "\n"
).encode("utf-8")
if raw != canonical:
    raise SystemExit("receiver receipt not canonical")

expected_keys = {
    "receipt_schema",
    "status",
    "handoff_schema",
    "source_commit",
    "source_tree",
    "candidate_sha256",
    "transaction_v4_sha256",
    "contract_sha256",
    "manifest_sha256",
    "host_evidence_sha256",
    "receiver_sha256",
    "supplemental_runtime_artifact",
    "transaction_receipt_sha256",
    "stream_digest_sha256",
    "file_count",
    "byte_count",
    "runtime_owner_uid",
    "source_owner_uid",
    "source_inode_alias_count",
    "terminal_frame_verified",
    "private_transaction_cleanup",
    "authorized_root_posthandoff_empty",
    "lock_held_through_handoff",
    "lock_unlinked_identity_bound",
    "external_noncooperating_writer_absence_proven",
    "docker_invoked",
}
if set(receipt) != expected_keys:
    raise SystemExit("receiver receipt field set mismatch")

expected = {
    "receipt_schema": 1,
    "status": "V6_RUNTIME_MATERIAL_HANDOFF_ACCEPTED",
    "handoff_schema": "WP4_D064_V6_HANDOFF_SCHEMA_1",
    "source_commit": source_commit,
    "source_tree": source_tree,
    "candidate_sha256": sha(candidate_path),
    "transaction_v4_sha256": sha(transaction_path),
    "contract_sha256": sha(contract_path),
    "manifest_sha256": sha(manifest_path),
    "host_evidence_sha256":
        "c4783f95de24ae309c6fd1c79ea2bc0d27e1dfdb319259351338d0f75c62de9a",
    "receiver_sha256": sha(receiver_path),
    "supplemental_runtime_artifact": {
        "source_path": "external/fortytwo/42",
        "source_commit": "eda252bf31f27850e867e698cfdd963e143ead1f",
        "source_tree": "541dbc9c3c3d42887b9c668a218ffc3726d24346",
        "handoff_destination": "fortytwo-runtime/42",
        "sha256": "9c0062d2a447a6340e7c191850ff952d3f8768dd307e3e7fb141e777961e60c7",
        "bytes": 2250376,
        "mode": 0o755,
        "nlink": 1,
        "canonical_manifest_member": False,
    },
    "runtime_owner_uid": os.geteuid(),
    "source_owner_uid": 599,
    "source_inode_alias_count": 0,
    "terminal_frame_verified": True,
    "private_transaction_cleanup": True,
    "authorized_root_posthandoff_empty": True,
    "lock_held_through_handoff": True,
    "lock_unlinked_identity_bound": True,
    "external_noncooperating_writer_absence_proven": False,
    "docker_invoked": False,
}
for key, value in expected.items():
    if receipt.get(key) != value:
        raise SystemExit("receiver receipt field mismatch: " + key)
for key in (
    "transaction_receipt_sha256",
    "stream_digest_sha256",
    "file_count",
    "byte_count",
):
    if key not in receipt:
        raise SystemExit("receiver receipt field missing: " + key)
def hex64(value):
    return (
        isinstance(value, str)
        and len(value) == 64
        and value == value.lower()
        and all(c in "0123456789abcdef" for c in value)
    )
if not hex64(receipt["transaction_receipt_sha256"]):
    raise SystemExit("receiver transaction receipt SHA invalid")
if not hex64(receipt["stream_digest_sha256"]):
    raise SystemExit("receiver stream digest invalid")
if not isinstance(receipt["file_count"], int) or receipt["file_count"] <= 0:
    raise SystemExit("receiver file count invalid")
if not isinstance(receipt["byte_count"], int) or receipt["byte_count"] <= 0:
    raise SystemExit("receiver byte count invalid")
print("V6_HANDOFF_RECEIVER_RECEIPT_VERIFICATION=PASS")
PYV6RECEIPT

FORTYTWO_RUNTIME="$RUNTIME_MATERIAL_ROOT/fortytwo-runtime"
FORTYTWO_IMPORTED_BINARY="$FORTYTWO_RUNTIME/42"

"$PINNED_PYTHON" - "$FORTYTWO_IMPORTED_BINARY" <<'PYV6FORTYTWO_IMPORTED'
import hashlib
import os
import stat
import sys

path = os.path.realpath(sys.argv[1])
st1 = os.stat(path, follow_symlinks=False)
if (
    not stat.S_ISREG(st1.st_mode)
    or stat.S_ISLNK(st1.st_mode)
    or st1.st_nlink != 1
    or st1.st_uid != os.geteuid()
    or st1.st_size != 2250376
    or stat.S_IMODE(st1.st_mode) != 0o755
):
    raise SystemExit("imported Fortytwo executable identity mismatch")
h = hashlib.sha256()
with open(path, "rb") as stream:
    for chunk in iter(lambda: stream.read(1024 * 1024), b""):
        h.update(chunk)
st2 = os.stat(path, follow_symlinks=False)
if (
    st1.st_dev, st1.st_ino, st1.st_mode, st1.st_nlink, st1.st_size
) != (
    st2.st_dev, st2.st_ino, st2.st_mode, st2.st_nlink, st2.st_size
):
    raise SystemExit("imported Fortytwo executable identity drift")
if h.hexdigest() != "9c0062d2a447a6340e7c191850ff952d3f8768dd307e3e7fb141e777961e60c7":
    raise SystemExit("imported Fortytwo executable SHA mismatch")
print("V6_SUPPLEMENTAL_FORTYTWO_HANDOFF_VERIFICATION=PASS")
PYV6FORTYTWO_IMPORTED

RUNTIME_MATERIAL_PUBLISHED=1

WS_NOS_ENGINE="$RUNTIME_MATERIAL_ROOT/workspaces/nos_engine/work/nos3"
WS_TIME_DRIVER="$RUNTIME_MATERIAL_ROOT/workspaces/time_driver/work/nos3"
WS_CMD_BUS_BRIDGE="$RUNTIME_MATERIAL_ROOT/workspaces/cmd_bus_bridge/work/nos3"
WS_CFS="$RUNTIME_MATERIAL_ROOT/workspaces/cfs/work/nos3"
INOUT="$RUNTIME_MATERIAL_ROOT/fortytwo-config/cfg/build/InOut"
'''

source = source[:start] + handoff + source[end:]

source = source.replace(
    '$TRANSACTION_DIR/workspaces/$hw_component/work/nos3',
    '$RUNTIME_MATERIAL_ROOT/workspaces/$hw_component/work/nos3',
)

one(
    'source=$FORTYTWO,target=/work/fortytwo',
    'source=$FORTYTWO_RUNTIME,target=/work/fortytwo',
    "V6 imported Fortytwo runtime mount",
)

old_cleanup = '''  if (( TRANSACTION_PUBLISHED == 1 )) && [[ "$TRANSACTION_DIR" == "$AUTHORIZED_TRANSACTION_ROOT/$TRANSACTION_BASENAME" ]]; then
    rm -rf -- "$TRANSACTION_DIR" || cleanup_failed=1
    TRANSACTION_PUBLISHED=0
  fi
'''
new_cleanup = '''  if (( RUNTIME_MATERIAL_PUBLISHED == 1 )) && [[ "$RUNTIME_MATERIAL_ROOT" == "$RUNTIME_MATERIAL_PARENT/$RUNTIME_MATERIAL_BASENAME" ]]; then
    rm -rf -- "$RUNTIME_MATERIAL_ROOT" || cleanup_failed=1
    RUNTIME_MATERIAL_PUBLISHED=0
  fi
  if [[ -d "$RUNTIME_MATERIAL_PARENT" ]]; then
    rmdir "$RUNTIME_MATERIAL_PARENT" 2>/dev/null || cleanup_failed=1
  fi
'''
if old_cleanup not in source:
    raise SystemExit("V6 inherited private transaction cleanup anchor missing")
source = source.replace(old_cleanup, new_cleanup, 1)

for forbidden in (
    'source=$' + 'NOS3,target=/work/nos3',
    'source=$' + 'FORTYTWO,target=/work/fortytwo',
    'TRANSACTION_DIR/workspaces/',
    '--materialize-v5-transaction',
    'nos3_runtime_transaction_v3.py',
):
    if forbidden in source:
        raise SystemExit("V6 forbidden runtime/source token remains: " + forbidden)

required = (
    "PASSIVE_TIME_WITNESS_V6_RUNTIME_CANDIDATE",
    "nos3_runtime_transaction_v4.py",
    "receive_runtime_material_handoff_v1.py",
    "--materialize-v6-stream",
    'MATERIALIZER_USER="wp4d064mat"',
    "RUNTIME_MATERIAL_ROOT",
    "D064_V6_ATTEMPT_CONSUMED_BEFORE_PRODUCTION_TRANSACTION",
    "V6_FRESH_EXECUTION_TIME_HOST_RECHECK=PASS",
    "V6_PREINVOCATION_CONTENTION_PROBE=PASS",
    "V6_HANDOFF_RECEIVER_RECEIPT_VERIFICATION=PASS",
    "V6_FRESH_FORTYTWO_SOURCE_IDENTITY=PASS",
    "V6_SUPPLEMENTAL_FORTYTWO_HANDOFF_VERIFICATION=PASS",
    "--expected-source-commit",
    "--expected-source-tree",
    'pipe_rc=( "${' + 'PIPESTATUS[@]}" )',
    'source=$WS_NOS_ENGINE,target=/work/nos3',
    'source=$WS_TIME_DRIVER,target=/work/nos3',
    'source=$WS_CMD_BUS_BRIDGE,target=/work/nos3',
    'source=$WS_CFS,target=/work/nos3',
    'source=$FORTYTWO_RUNTIME,target=/work/fortytwo',
)
for token in required:
    if token not in source:
        raise SystemExit("V6 required source token missing: " + token)

output.write_text(source, encoding="utf-8", newline="\n")
PYTRANSFORM

bash -n "$tmp_emit" || fail "Generated V6 candidate Bash syntax invalid"

python3 - "$tmp_emit" "$emit_parent/$emit_leaf" <<'PYPUBLISH'
import os,sys
src,dst=sys.argv[1:]
os.link(src,dst,follow_symlinks=False)
os.chmod(dst,0o700)
os.unlink(src)
PYPUBLISH

trap - EXIT
rm -f -- "$v5_candidate"
rmdir "$workdir"
echo "PASSIVE_TIME_WITNESS_V6_CANDIDATE_EMITTED=$emit_parent/$emit_leaf"
