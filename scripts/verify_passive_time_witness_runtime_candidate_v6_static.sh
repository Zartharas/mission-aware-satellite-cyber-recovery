#!/usr/bin/env bash
# WP4 D-064 V6 formal static verifier.
#
# --selftest:
#   source-only negative-suite validation; NOT the formal verification event.
#
# --verify:
#   reserved for separately authorized formal V6 static verification.
set -Eeuo pipefail

readonly EXPECTED_TRANSACTION_V4_SHA256="aa96c912a2311ee8c2edec2d5bbfbaf90f0387f78476f9fe80a83773c10c2d1d"
readonly EXPECTED_RECEIVER_SHA256="64ecadbd0c8c8d69e5509bb7bbe9115bfe8ebc812961eaf77f8ec3331168726c"
readonly EXPECTED_GENERATOR_V6_SHA256="2a2b7a5a1438831908af27b9c9cb6d4a0d4cd633ceb964c4f71a5df2a1beda83"
readonly EXPECTED_V5_GENERATOR_SHA256="9f006bc7e13e73b9702d2f63c5d97413a77151af0a9d63e3ed88d3cba121bed7"
readonly EXPECTED_TRANSACTION_V3_SHA256="ce1f1f3ad3ba50373e57f36c6490c4ece67f028994155015ed536ce4832fec9e"
readonly EXPECTED_V5_VERIFIER_SHA256="a688ba002b243a07ddb95a7819b19875a7020132812c6fccfc65c01c93eda5c5"
readonly DESIGN_LOCK_SHA256="a7774fc5f0ccb23ef84fe02d6f802b3b199a870b96dfc3d01fcd76616e9f0a2c"
readonly DESIGN_LOCK_AMENDMENT_1_SHA256="df9c737269d39baeb87affef9c6ac5d848cf7e8ef5b395ca4cd852071caac139"
readonly EXPECTED_CANONICAL_MANIFEST_SHA256="5026176de3084c8015fd7f84827ce8a4e5d44df7e986bc142815eb0d649e81cd"

mode="${1:-}"
case "$mode" in
  --selftest|--verify) ;;
  *)
    echo "usage: $0 --selftest|--verify" >&2
    exit 2
    ;;
esac

ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || {
  echo "V6_STATIC_VERIFICATION=FAIL" >&2
  exit 1
}
ROOT="$(cd "$ROOT" && pwd -P)"

TX="$ROOT/scripts/nos3_runtime_transaction_v4.py"
RX="$ROOT/scripts/receive_runtime_material_handoff_v1.py"
GEN="$ROOT/scripts/prepare_passive_time_witness_runtime_candidate_v6.sh"
V3="$ROOT/scripts/nos3_runtime_transaction_v3.py"
V5GEN="$ROOT/scripts/prepare_passive_time_witness_runtime_candidate_v5.sh"
V5VER="$ROOT/scripts/verify_passive_time_witness_runtime_candidate_v5_static.sh"
MANIFEST="$ROOT/manifests/nos3-runtime-material-manifest.json"

check_sha() {
  [[ "$(shasum -a 256 "$1" | awk '{print $1}')" == "$2" ]]
}

check_sha "$TX" "$EXPECTED_TRANSACTION_V4_SHA256"
check_sha "$RX" "$EXPECTED_RECEIVER_SHA256"
check_sha "$GEN" "$EXPECTED_GENERATOR_V6_SHA256"
check_sha "$V3" "$EXPECTED_TRANSACTION_V3_SHA256"
check_sha "$V5GEN" "$EXPECTED_V5_GENERATOR_SHA256"
check_sha "$V5VER" "$EXPECTED_V5_VERIFIER_SHA256"
check_sha "$MANIFEST" "$EXPECTED_CANONICAL_MANIFEST_SHA256"

python3 -m py_compile "$TX" "$RX"
bash -n "$GEN"

TX_SELFTEST="$(
  python3 "$TX" --v6-stream-selftest
)"
for marker in \
  "V6_TRANSACTION_CONTRACT_POLICY_SELFTEST=PASS" \
  "v6_contract_negative_v5_candidate_identity=PASS" \
  "v6_contract_negative_candidate_mismatch=PASS" \
  "v6_contract_negative_schema1_host_evidence=PASS" \
  "v6_contract_negative_supplemental_fortytwo_binding=PASS" \
  "V6_TRANSACTION_STREAM_SELFTEST=PASS" \
  "v6_lock_held_through_stream_cleanup=PASS" \
  "v6_terminal_frame_after_cleanup=PASS"
do
  [[ "$(printf '%s\n' "$TX_SELFTEST" | grep -Fxc "$marker")" == 1 ]] || {
    echo "[FAIL] missing transaction selftest marker: $marker" >&2
    exit 1
  }
done

RX_SELFTEST="$(
  python3 "$RX" --selftest
)"
for marker in \
  "V6_RECEIVER_SELFTEST=PASS" \
  "receiver_negative_truncated=PASS" \
  "receiver_negative_duplicate_path=PASS" \
  "receiver_negative_path_traversal=PASS" \
  "receiver_negative_prefix_collision=PASS" \
  "receiver_negative_hash_mismatch=PASS" \
  "receiver_negative_file_count_mismatch=PASS" \
  "receiver_negative_byte_count_mismatch=PASS" \
  "receiver_negative_stream_digest_mismatch=PASS" \
  "receiver_negative_cleanup_flag_false=PASS" \
  "receiver_negative_trailing_bytes=PASS" \
  "receiver_negative_special_semantic=PASS" \
  "receiver_negative_source_hardlink_alias=PASS" \
  "receiver_negative_source_commit_mismatch=PASS" \
  "receiver_negative_source_tree_mismatch=PASS" \
  "receiver_negative_receiver_sha_mismatch=PASS" \
  "receiver_negative_supplemental_binding_mismatch=PASS" \
  "receiver_negative_supplemental_record_mismatch=PASS" \
  "receiver_negative_case_count=17"
do
  [[ "$(printf '%s\n' "$RX_SELFTEST" | grep -Fxc "$marker")" == 1 ]] || {
    echo "[FAIL] missing receiver selftest marker: $marker" >&2
    exit 1
  }
done

tmp_root="$(
  python3 - <<'PYTMP'
import os,tempfile
print(os.path.realpath(tempfile.gettempdir()))
PYTMP
)"
tmp="$(mktemp -d "$tmp_root/wp4-v6-static-review.XXXXXX")"
candidate="$tmp/candidate-v6.sh"
cleanup() {
  rc=$?
  rm -f -- "$candidate"
  rmdir "$tmp" 2>/dev/null || true
  trap - EXIT
  exit "$rc"
}
trap cleanup EXIT

PASSIVE_TIME_WITNESS_V6_EMIT_PATH="$candidate" bash "$GEN" >/dev/null
bash -n "$candidate"

python3 - "$TX" "$RX" "$GEN" "$candidate" <<'PYSTATIC'
import ast
import pathlib
import re
import sys

tx, rx, gen, candidate = map(pathlib.Path, sys.argv[1:])
tx_text = tx.read_text(encoding="utf-8")
rx_text = rx.read_text(encoding="utf-8")
gen_text = gen.read_text(encoding="utf-8")
cand = candidate.read_text(encoding="utf-8")


def fail(msg):
    raise SystemExit(msg)


def no_process_or_docker(path, label):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            if any(
                alias.name.split(".")[0] in ("subprocess", "docker")
                for alias in node.names
            ):
                fail(label + " imports forbidden process/docker module")
        if isinstance(node, ast.ImportFrom):
            if (node.module or "").split(".")[0] in ("subprocess", "docker"):
                fail(label + " imports forbidden process/docker module")
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            cur = node.func
            while isinstance(cur, ast.Attribute):
                cur = cur.value
            if isinstance(cur, ast.Name) and cur.id in ("subprocess", "docker"):
                fail(label + " calls forbidden process/docker module")


no_process_or_docker(tx, "transaction-v4")
no_process_or_docker(rx, "receiver-v1")

# 1, 2, 4 are behaviorally exercised above by transaction
# --v6-stream-selftest. Source review independently requires the exact
# must_close() labels rather than impossible dynamically constructed PASS
# marker literals.
tx_tree = ast.parse(tx_text)
must_close_labels = set()
for node in ast.walk(tx_tree):
    if (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "must_close"
        and node.args
        and isinstance(node.args[0], ast.Constant)
        and isinstance(node.args[0].value, str)
    ):
        must_close_labels.add(node.args[0].value)

for label in (
    "v5_candidate_identity",
    "candidate_mismatch",
    "schema1_host_evidence",
):
    if label not in must_close_labels:
        fail("transaction negative-suite must_close label missing: " + label)

# 3. Executable V6 parser exposes no V5 production operation.
try:
    parser = tx_text.split("def _v6_build_argparser", 1)[1].split(
        "def _v6_main", 1
    )[0]
except IndexError:
    fail("V6 parser source unavailable")
if "--materialize-v5-transaction" in parser:
    fail("V5 production fallback exposed by V6 parser")
if parser.count("--materialize-v6-stream") != 1:
    fail("V6 stream production operation cardinality invalid")

# 5. UID599 transaction side contains no subprocess/Docker execution.
for token in (
    "subprocess.run(",
    "subprocess.Popen(",
    "docker run",
    "docker create",
    "docker start",
):
    if token in tx_text:
        fail("transaction-v4 process/Docker token present: " + token)

# Amendment 1 exact supplemental Fortytwo binding.
for token in (
    '_V6_FORTYTWO_SOURCE_REL = "external/fortytwo/42"',
    '_V6_FORTYTWO_SOURCE_COMMIT = "eda252bf31f27850e867e698cfdd963e143ead1f"',
    '_V6_FORTYTWO_SOURCE_TREE = "541dbc9c3c3d42887b9c668a218ffc3726d24346"',
    '_V6_FORTYTWO_SHA256 = "9c0062d2a447a6340e7c191850ff952d3f8768dd307e3e7fb141e777961e60c7"',
    "_V6_FORTYTWO_BYTES = 2250376",
    "_V6_FORTYTWO_MODE = 0o755",
    "_V6_FORTYTWO_NLINK = 1",
    '_V6_FORTYTWO_HANDOFF_DEST = "fortytwo-runtime/42"',
    '"canonical_manifest_member": False',
    "V6 supplemental Fortytwo source/destination inode alias",
):
    if token not in tx_text:
        fail("transaction supplemental Fortytwo token missing: " + token)

if tx_text.count("supplemental_runtime_artifact_fortytwo_42") < 2:
    fail("transaction supplemental contract binding cardinality too low")

# Receiver protocol exactness and negative-suite implementation.
for token in (
    "header field set mismatch",
    "header file record field set mismatch",
    "stream file record field set mismatch",
    "source/destination inode alias",
    "unexpected EOF",
    "terminal frame fields mismatch",
    "expected_source_commit",
    "expected_source_tree",
    "supplemental Fortytwo binding mismatch",
    "supplemental Fortytwo file record mismatch",
    "expected_fortytwo_source_commit",
    "expected_fortytwo_source_tree",
    "expected_fortytwo_sha256",
    "expected_fortytwo_bytes",
    "expected_fortytwo_mode",
    "transaction receipt file SHA binding mismatch",
):
    if token not in rx_text:
        fail("receiver hardening token missing: " + token)

# 6, 22. Runtime mounts must originate only from handoff-imported roots.
for forbidden in (
    "source=$NOS3,target=/work/nos3",
    "source=$FORTYTWO,target=/work/fortytwo",
    "TRANSACTION_DIR/workspaces/",
):
    if forbidden in cand:
        fail("live/private source runtime mount remains: " + forbidden)
for token, count in (
    ("source=$WS_NOS_ENGINE,target=/work/nos3", 1),
    ("source=$WS_TIME_DRIVER,target=/work/nos3", 1),
    ("source=$WS_CMD_BUS_BRIDGE,target=/work/nos3", 1),
    ("source=$WS_CFS,target=/work/nos3", 1),
    ("source=$hw_workspace,target=/work/nos3", 2),
    ("source=$FORTYTWO_RUNTIME,target=/work/fortytwo", 1),
):
    if cand.count(token) != count:
        fail("runtime handoff mount cardinality invalid: " + token)

# 7-14 and Amendment-1 receiver negatives are behaviorally exercised above
# by receiver --selftest. Source review independently requires exactly the
# intended _expect_reject() literal labels rather than impossible dynamically
# constructed full PASS-marker literals.
expected_receiver_negative_labels = {
    "truncated",
    "duplicate_path",
    "path_traversal",
    "prefix_collision",
    "hash_mismatch",
    "file_count_mismatch",
    "byte_count_mismatch",
    "stream_digest_mismatch",
    "cleanup_flag_false",
    "trailing_bytes",
    "special_semantic",
    "source_hardlink_alias",
    "source_commit_mismatch",
    "source_tree_mismatch",
    "receiver_sha_mismatch",
    "supplemental_binding_mismatch",
    "supplemental_record_mismatch",
}

rx_tree = ast.parse(rx_text)
receiver_negative_labels = []
for node in ast.walk(rx_tree):
    if (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "_expect_reject"
    ):
        if (
            len(node.args) < 2
            or not isinstance(node.args[1], ast.Constant)
            or not isinstance(node.args[1].value, str)
        ):
            fail("receiver _expect_reject label is not an exact string literal")
        receiver_negative_labels.append(node.args[1].value)

if len(receiver_negative_labels) != 17:
    fail(
        "receiver _expect_reject call count invalid: %d"
        % len(receiver_negative_labels)
    )
if len(set(receiver_negative_labels)) != 17:
    fail("receiver _expect_reject labels are not unique")
if set(receiver_negative_labels) != expected_receiver_negative_labels:
    missing = sorted(
        expected_receiver_negative_labels - set(receiver_negative_labels)
    )
    extra = sorted(
        set(receiver_negative_labels) - expected_receiver_negative_labels
    )
    fail(
        "receiver negative label set mismatch missing=%r extra=%r"
        % (missing, extra)
    )

if rx_text.count(
    'print("receiver_negative_" + name + "=PASS")'
) != 1:
    fail("receiver dynamic negative PASS emitter cardinality invalid")

# Finding 2: fresh host + contention gate precede attempt consumption and
# production transaction invocation.
host_marker = cand.find("V6_FRESH_EXECUTION_TIME_HOST_RECHECK=PASS")
fortytwo_source_marker = cand.find("V6_FRESH_FORTYTWO_SOURCE_IDENTITY=PASS")
contention_marker = cand.find("V6_PREINVOCATION_CONTENTION_PROBE=PASS")
sentinel_marker = cand.find(
    "D064_V6_ATTEMPT_CONSUMED_BEFORE_PRODUCTION_TRANSACTION"
)
materialize_marker = cand.find("--materialize-v6-stream")
if min(
    host_marker,
    fortytwo_source_marker,
    contention_marker,
    sentinel_marker,
    materialize_marker,
) < 0:
    fail("candidate execution-boundary marker missing")
if not (
    host_marker < sentinel_marker
    and fortytwo_source_marker < sentinel_marker
    and contention_marker < sentinel_marker
    and sentinel_marker < materialize_marker
):
    fail("fresh-gate / sentinel / production ordering invalid")

for token in (
    "fcntl.LOCK_EX | fcntl.LOCK_NB",
    "os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW",
    "external_noncooperating_writer_absence_proven=false",
):
    if token not in cand:
        fail("fresh gate/contention token missing: " + token)

# Findings 3 and 4: source commit/tree are independently expected-bound and
# receiver receipt is revalidated before any Docker creation.
for token in (
    "--expected-source-commit",
    "--expected-source-tree",
    "V6_HANDOFF_RECEIVER_RECEIPT_SHA256",
    "V6_HANDOFF_RECEIVER_RECEIPT_VERIFICATION=PASS",
    ".wp4-d064-v6-handoff-receipt.json",
    "--expected-fortytwo-source-path",
    "--expected-fortytwo-source-commit",
    "--expected-fortytwo-source-tree",
    "--expected-fortytwo-destination",
    "--expected-fortytwo-sha256",
    "--expected-fortytwo-bytes",
    "--expected-fortytwo-mode",
    "V6_SUPPLEMENTAL_FORTYTWO_HANDOFF_VERIFICATION=PASS",
):
    if token not in cand:
        fail("candidate handoff/receipt binding token missing: " + token)

receipt_marker = cand.find("V6_HANDOFF_RECEIVER_RECEIPT_VERIFICATION=PASS")
fortytwo_import_marker = cand.find(
    "V6_SUPPLEMENTAL_FORTYTWO_HANDOFF_VERIFICATION=PASS"
)
sender_check = cand.find(
    '[[ "$sender_rc" == 0 && "$receiver_rc" == 0 ]]'
)
docker_marker = cand.find('"$DOCKER_BIN" network create')
if docker_marker < 0:
    fail("candidate first Docker network-create token absent")
if not (
    sender_check >= 0
    and sender_check < receipt_marker < fortytwo_import_marker < docker_marker
):
    fail(
        "sender/receiver/receipt/supplemental acceptance does not precede Docker"
    )

# 15,16,17. Sender/receiver failure and pipeline truncation cannot fall through
# to Docker. The sender->receiver pipeline must execute directly in the current
# shell, PIPESTATUS must be captured immediately after the receiver redirection,
# and only then may the receiver status file be read with command substitution.
if cand.count('pipe_rc=( "${PIPESTATUS[@]}" )') != 1:
    fail("PIPESTATUS capture cardinality invalid")

handoff_status_decl_token = (
    'HANDOFF_STATUS_FILE="$RUNTIME_MATERIAL_PARENT/receiver-status.txt"'
)
handoff_status_decl_i = cand.rfind(
    handoff_status_decl_token,
    sentinel_marker,
    materialize_marker,
)
if handoff_status_decl_i < 0:
    fail("handoff status-file declaration absent before production pipeline")

segment = cand[handoff_status_decl_i:docker_marker]

pipeline_start_token = 'sudo -n -u "$MATERIALIZER_USER" /usr/bin/env \\\n'
receiver_pipe_token = '|\n"$PINNED_PYTHON" "$HANDOFF_RECEIVER" \\\n'
pipeline_end_token = '    > "$HANDOFF_STATUS_FILE"\n'
pipe_capture_token = 'pipe_rc=( "${PIPESTATUS[@]}" )\n'
status_cardinality_token = '(( ${#pipe_rc[@]} == 2 )) || {'
sender_assign_token = 'sender_rc="${pipe_rc[0]}"'
receiver_assign_token = 'receiver_rc="${pipe_rc[1]}"'
status_read_token = 'handoff_output="$(cat "$HANDOFF_STATUS_FILE")"'
sender_gate_token = '[[ "$sender_rc" == 0 && "$receiver_rc" == 0 ]]'

for label, token, expected_count in (
    ("handoff status-file declaration", handoff_status_decl_token, 1),
    ("sender pipeline start", pipeline_start_token, 1),
    ("receiver pipeline leg", receiver_pipe_token, 1),
    ("receiver status redirection", pipeline_end_token, 1),
    ("PIPESTATUS capture", pipe_capture_token, 1),
    ("PIPESTATUS cardinality gate", status_cardinality_token, 1),
    ("sender rc assignment", sender_assign_token, 1),
    ("receiver rc assignment", receiver_assign_token, 1),
    ("handoff status-file read", status_read_token, 1),
    ("sender receiver acceptance gate", sender_gate_token, 1),
):
    if segment.count(token) != expected_count:
        fail(
            "handoff pipeline structural token cardinality invalid: "
            + label
        )

pipeline_start_i = segment.find(pipeline_start_token)
receiver_pipe_i = segment.find(receiver_pipe_token, pipeline_start_i)
pipeline_end_i = segment.find(pipeline_end_token, receiver_pipe_i)
pipe_capture_i = segment.find(pipe_capture_token, pipeline_end_i)
status_cardinality_i = segment.find(
    status_cardinality_token, pipe_capture_i
)
sender_assign_i = segment.find(sender_assign_token, status_cardinality_i)
receiver_assign_i = segment.find(receiver_assign_token, sender_assign_i)
status_read_i = segment.find(status_read_token, receiver_assign_i)
sender_gate_i = segment.find(sender_gate_token, status_read_i)

if min(
    pipeline_start_i,
    receiver_pipe_i,
    pipeline_end_i,
    pipe_capture_i,
    status_cardinality_i,
    sender_assign_i,
    receiver_assign_i,
    status_read_i,
    sender_gate_i,
) < 0:
    fail("handoff pipeline structural ordering marker absent")

# Direct current-shell pipeline: the sender starts as a standalone command,
# not inside assignment/command substitution. Permit only leading whitespace.
line_start_i = segment.rfind("\n", 0, pipeline_start_i) + 1
if segment[line_start_i:pipeline_start_i].strip() != "":
    fail("handoff sender pipeline is not a direct current-shell command")

# Explicitly reject the historical unsafe wrapper while allowing the later
# single-command status-file read.
unsafe_wrapper = re.compile(
    r'handoff_output="\$\(\s*'
    r'sudo -n -u "\$MATERIALIZER_USER" /usr/bin/env',
    re.MULTILINE,
)
if unsafe_wrapper.search(segment):
    fail("handoff sender/receiver pipeline wrapped in command substitution")

# The first non-whitespace source text after the receiver's status-file
# redirection must be the PIPESTATUS capture. This is the immediate-capture
# invariant needed before any other command can overwrite PIPESTATUS.
pipeline_end_after = pipeline_end_i + len(pipeline_end_token)
between_pipeline_and_capture = segment[
    pipeline_end_after:pipe_capture_i
]
if between_pipeline_and_capture.strip() != "":
    fail("PIPESTATUS capture is not immediate after handoff pipeline")

if not (
    pipeline_start_i
    < receiver_pipe_i
    < pipeline_end_i
    < pipe_capture_i
    < status_cardinality_i
    < sender_assign_i
    < receiver_assign_i
    < status_read_i
    < sender_gate_i
):
    fail("handoff pipeline / PIPESTATUS / status-read ordering invalid")

# The safe status-file command substitution is required exactly once and only
# after the two pipeline return codes have been captured into scalar variables.
if segment.count('handoff_output="$(cat "$HANDOFF_STATUS_FILE")"') != 1:
    fail("handoff status-file command substitution cardinality invalid")

if 'exit 1' not in cand[sender_check:receipt_marker]:
    fail("sender/receiver failure block does not fail closed")

# 18-20. Sender cleanup, terminal-frame eligibility, and production lock
# lifetime. Prove the actual inherited transaction-v3 finalizer rather than a
# nonexistent helper token.
tx_ast = ast.parse(tx_text)
tx_lines = tx_text.splitlines()

def function_node(name):
    nodes = [
        n for n in tx_ast.body
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
        and n.name == name
    ]
    if len(nodes) != 1:
        fail("transaction function cardinality invalid: " + name)
    return nodes[0]

def function_source(name):
    node = function_node(name)
    return "\n".join(tx_lines[node.lineno - 1:node.end_lineno])

def call_qname(node):
    if not isinstance(node, ast.Call):
        return None
    fn = node.func
    if isinstance(fn, ast.Name):
        return fn.id
    if (
        isinstance(fn, ast.Attribute)
        and isinstance(fn.value, ast.Name)
    ):
        return fn.value.id + "." + fn.attr
    return None

def is_name(node, value):
    return isinstance(node, ast.Name) and node.id == value

def is_lock_un_call(node):
    return (
        isinstance(node, ast.Call)
        and call_qname(node) == "fcntl.flock"
        and len(node.args) >= 2
        and is_name(node.args[0], "lock_fd")
        and isinstance(node.args[1], ast.Attribute)
        and isinstance(node.args[1].value, ast.Name)
        and node.args[1].value.id == "fcntl"
        and node.args[1].attr == "LOCK_UN"
    )

def is_lock_close_call(node):
    return (
        isinstance(node, ast.Call)
        and call_qname(node) == "os.close"
        and len(node.args) == 1
        and is_name(node.args[0], "lock_fd")
    )

def is_lock_guard(test):
    return (
        isinstance(test, ast.Compare)
        and is_name(test.left, "lock_fd")
        and len(test.ops) == 1
        and isinstance(test.ops[0], ast.IsNot)
        and len(test.comparators) == 1
        and isinstance(test.comparators[0], ast.Constant)
        and test.comparators[0].value is None
    )

def subtree_contains(nodes, target):
    for root in nodes:
        if root is target:
            return True
        if any(n is target for n in ast.walk(root)):
            return True
    return False

stream_node = function_node("_v6_stream_published_transaction")
stream_fn = function_source("_v6_stream_published_transaction")

# The streaming function must not release or close the retained lock FD.
stream_unlocks = [
    n for n in ast.walk(stream_node)
    if is_lock_un_call(n)
]
stream_lock_closes = [
    n for n in ast.walk(stream_node)
    if is_lock_close_call(n)
]
if stream_unlocks or stream_lock_closes:
    fail("V6 stream function releases/closes lock before handoff completion")

# Preserve exact successful cleanup order:
# private transaction cleanup -> lock identity revalidation ->
# identity-bound lock-path unlink -> root-empty proof -> terminal footer.
cleanup_calls = [
    n for n in ast.walk(stream_node)
    if isinstance(n, ast.Call)
    and call_qname(n) == "_desc_rmtree"
    and len(n.args) >= 2
    and is_name(n.args[0], "root_fd")
    and is_name(n.args[1], "final_basename")
]
revalidate_calls = [
    n for n in ast.walk(stream_node)
    if isinstance(n, ast.Call)
    and call_qname(n) == "_revalidate_serialization_lock"
]
unlink_calls = [
    n for n in ast.walk(stream_node)
    if isinstance(n, ast.Call)
    and call_qname(n) == "os.unlink"
    and len(n.args) >= 1
    and is_name(n.args[0], "_D064_LOCK_BASENAME")
]
listdir_calls = [
    n for n in ast.walk(stream_node)
    if isinstance(n, ast.Call)
    and call_qname(n) == "_fd_listdir"
    and len(n.args) == 1
    and is_name(n.args[0], "root_fd")
]
root_empty_guards = [
    n for n in ast.walk(stream_node)
    if isinstance(n, ast.If)
    and is_name(n.test, "names")
    and any(isinstance(x, ast.Raise) for x in n.body)
]
footer_assigns = [
    n for n in ast.walk(stream_node)
    if isinstance(n, ast.Assign)
    and any(is_name(t, "footer") for t in n.targets)
    and isinstance(n.value, ast.Dict)
]
terminal_magic_calls = [
    n for n in ast.walk(stream_node)
    if isinstance(n, ast.Call)
    and call_qname(n) == "_v6_write_all"
    and len(n.args) >= 2
    and is_name(n.args[1], "_V6_HANDOFF_END_MAGIC")
]

for label, nodes in (
    ("cleanup", cleanup_calls),
    ("lock revalidation", revalidate_calls),
    ("identity-bound lock unlink", unlink_calls),
    ("root listdir", listdir_calls),
    ("root-empty guard", root_empty_guards),
    ("footer", footer_assigns),
    ("terminal magic", terminal_magic_calls),
):
    if len(nodes) != 1:
        fail("V6 stream ordering %s cardinality invalid: %d" % (label, len(nodes)))

cleanup_node = cleanup_calls[0]
revalidate_node = revalidate_calls[0]
unlink_node = unlink_calls[0]
listdir_node = listdir_calls[0]
root_empty_node = root_empty_guards[0]
footer_node = footer_assigns[0]
terminal_node = terminal_magic_calls[0]

if not (
    cleanup_node.lineno
    < revalidate_node.lineno
    < unlink_node.lineno
    < listdir_node.lineno
    < root_empty_node.lineno
    < footer_node.lineno
    < terminal_node.lineno
):
    fail("V6 sender cleanup/lock/root-empty/terminal ordering invalid")

# The lock-path unlink must be descriptor-relative to the retained root.
unlink_root_keywords = [
    kw for kw in unlink_node.keywords if kw.arg == "dir_fd"
]
if (
    len(unlink_root_keywords) != 1
    or not is_name(unlink_root_keywords[0].value, "root_fd")
):
    fail("V6 lock-path unlink is not identity/root-descriptor bound")

b2_node = function_node("_b2_materialize")

# Exactly one production stream call exists in _b2_materialize.
b2_stream_calls = [
    n for n in ast.walk(b2_node)
    if isinstance(n, ast.Call)
    and call_qname(n) == "_v6_stream_published_transaction"
]
if len(b2_stream_calls) != 1:
    fail("V6 production stream call cardinality invalid")
b2_stream_call = b2_stream_calls[0]

# Find the one outer try/finally whose immediate finalbody owns lock_fd release.
candidate_outer_tries = []
for node in b2_node.body:
    if not isinstance(node, ast.Try):
        continue
    lock_guards = [
        x for x in node.finalbody
        if isinstance(x, ast.If) and is_lock_guard(x.test)
    ]
    if len(lock_guards) == 1:
        candidate_outer_tries.append((node, lock_guards[0]))

if len(candidate_outer_tries) != 1:
    fail("V6 _b2_materialize outer lock-finalizer cardinality invalid")

outer_try, lock_guard = candidate_outer_tries[0]

# The stream call must execute inside the outer try body, not its handlers,
# orelse, or finalbody. Python then necessarily runs finalbody only after the
# stream call returns or raises.
if not subtree_contains(outer_try.body, b2_stream_call):
    fail("V6 production stream call not inside outer transaction try body")
if (
    subtree_contains(outer_try.finalbody, b2_stream_call)
    or subtree_contains(outer_try.orelse, b2_stream_call)
    or any(subtree_contains(h.body, b2_stream_call) for h in outer_try.handlers)
):
    fail("V6 production stream call incorrectly placed outside outer try body")

guard_unlocks = [
    n for n in ast.walk(lock_guard)
    if is_lock_un_call(n)
]
guard_closes = [
    n for n in ast.walk(lock_guard)
    if is_lock_close_call(n)
]
if len(guard_unlocks) != 1 or len(guard_closes) != 1:
    fail("V6 inherited lock finalizer release/close cardinality invalid")

unlock_node = guard_unlocks[0]
close_node = guard_closes[0]
if not (
    b2_stream_call.lineno
    < unlock_node.lineno
    < close_node.lineno
):
    fail("V6 production stream/finalizer lock-release ordering invalid")

# No alternative early LOCK_UN or lock_fd close is allowed anywhere in
# _b2_materialize.
all_b2_unlocks = [
    n for n in ast.walk(b2_node)
    if is_lock_un_call(n)
]
all_b2_lock_closes = [
    n for n in ast.walk(b2_node)
    if is_lock_close_call(n)
]
if len(all_b2_unlocks) != 1 or all_b2_unlocks[0] is not unlock_node:
    fail("V6 unexpected additional/early LOCK_UN in _b2_materialize")
if len(all_b2_lock_closes) != 1 or all_b2_lock_closes[0] is not close_node:
    fail("V6 unexpected additional/early lock_fd close in _b2_materialize")

# 21. No automatic retry after production boundary.
#
# The V6 handoff block contains multiple embedded Python heredocs.  Bash
# retry-loop analysis must therefore distinguish executable shell source from
# heredoc bodies.  In particular, PYCONSUME intentionally contains a bounded
# complete-write loop:
#
#     while off < len(raw):
#
# That loop writes the single O_EXCL attempt-consumption sentinel and is not
# shell control flow and does not reinvoke the production transaction.
if cand.count("--materialize-v6-stream") != 1:
    fail("production transaction invocation cardinality not one")
if cand.count('"automatic_retry_authorized":False') != 1:
    fail("attempt sentinel no-retry binding cardinality invalid")

handoff_scope_start_token = (
    'AUTHORIZED_TRANSACTION_ROOT="${PASSIVE_TIME_WITNESS_V6_AUTHORIZED_ROOT:-}"'
)
if cand.count(handoff_scope_start_token) != 1:
    fail("V6 handoff source-scope start cardinality invalid")
handoff_scope_start = cand.find(handoff_scope_start_token)

receipt_heredoc_end_token = "\nPYV6RECEIPT\n"
receipt_heredoc_end = cand.find(receipt_heredoc_end_token, receipt_marker)
if receipt_heredoc_end < 0:
    fail("V6 receiver-receipt heredoc terminator absent")
handoff_scope_end = receipt_heredoc_end + len(receipt_heredoc_end_token)

if not (
    0 <= handoff_scope_start
    < sentinel_marker
    < materialize_marker
    < receipt_marker
    < handoff_scope_end
):
    fail("V6 handoff retry-analysis source scope ordering invalid")

handoff_retry_scope = cand[handoff_scope_start:handoff_scope_end]

heredoc_decl_re = re.compile(
    r"<<(?P<dash>-?)(?!<)[ \t]*"
    r"(?:'(?P<sq>[A-Za-z_][A-Za-z0-9_]*)'"
    r'|"(?P<dq>[A-Za-z_][A-Za-z0-9_]*)"'
    r"|(?P<bare>[A-Za-z_][A-Za-z0-9_]*))"
)


def shell_without_heredoc_bodies(source):
    if "\r" in source:
        fail("V6 handoff retry-analysis source contains CR")

    executable = []
    completed = []
    pending = []
    active = None

    for line_no, line in enumerate(source.splitlines(keepends=True), 1):
        raw_line = line[:-1] if line.endswith("\n") else line

        if active is not None:
            delimiter, strip_tabs, body_lines, decl_line = active
            compare = raw_line.lstrip("\t") if strip_tabs else raw_line
            # Preserve source line count while excluding non-shell heredoc body.
            executable.append("\n" if line.endswith("\n") else "")
            if compare == delimiter:
                completed.append(
                    (delimiter, "".join(body_lines), decl_line, line_no)
                )
                if pending:
                    active = pending.pop(0)
                else:
                    active = None
            else:
                body_lines.append(line)
            continue

        executable.append(line)
        matches = list(heredoc_decl_re.finditer(raw_line))

        # Fail closed on an unrecognized << construct in executable Bash.
        masked = list(raw_line)
        for match in matches:
            for pos in range(match.start(), match.end()):
                masked[pos] = " "
        residual = "".join(masked).replace("<<<", "")
        if "<<" in residual:
            fail(
                "V6 handoff retry-analysis unsupported heredoc syntax line %d"
                % line_no
            )

        for match in matches:
            delimiter = (
                match.group("sq")
                or match.group("dq")
                or match.group("bare")
            )
            entry = (
                delimiter,
                match.group("dash") == "-",
                [],
                line_no,
            )
            if active is None:
                active = entry
            else:
                pending.append(entry)

    if active is not None or pending:
        delimiter = active[0] if active is not None else pending[0][0]
        fail(
            "V6 handoff retry-analysis unclosed heredoc: "
            + delimiter
        )

    return "".join(executable), tuple(completed)


handoff_shell, handoff_heredocs = shell_without_heredoc_bodies(
    handoff_retry_scope
)

expected_handoff_heredocs = (
    "PYV6FORTYTWO_SOURCE",
    "PYV6HOST",
    "PYV6LOCK",
    "PYTMP",
    "PYCLEANV6",
    "PYSENT",
    "PYCONSUME",
    "PYV6RECEIPT",
)
actual_handoff_heredocs = tuple(item[0] for item in handoff_heredocs)
if actual_handoff_heredocs != expected_handoff_heredocs:
    fail(
        "V6 handoff heredoc set/order mismatch: %r"
        % (actual_handoff_heredocs,)
    )

heredoc_bodies = {}
for delimiter, body, _decl_line, _end_line in handoff_heredocs:
    if delimiter in heredoc_bodies:
        fail("V6 handoff duplicate heredoc delimiter: " + delimiter)
    heredoc_bodies[delimiter] = body

pyconsume_body = heredoc_bodies.get("PYCONSUME", "")
if pyconsume_body.count("while off < len(raw):") != 1:
    fail("PYCONSUME complete-write loop cardinality invalid")
if pyconsume_body.count('"automatic_retry_authorized":False') != 1:
    fail("PYCONSUME no-retry binding cardinality invalid")
if "while off < len(raw):" in handoff_shell:
    fail("embedded PYCONSUME loop leaked into Bash retry analysis")

# Detect executable Bash while/until reserved words at ordinary command
# boundaries after heredoc bodies have been removed.  Exact-one production
# invocation plus absence of these enclosing/retry constructs preserves the
# single-attempt boundary.
shell_retry_loop_re = re.compile(
    r"(?m)(?:^|[;{}()]|\bthen\b|\bdo\b|\belse\b)"
    r"[ \t]*(while|until)\b"
)
shell_retry_loops = tuple(
    match.group(1)
    for match in shell_retry_loop_re.finditer(handoff_shell)
)
if shell_retry_loops:
    fail(
        "automatic Bash retry loop present around production handoff: %r"
        % (shell_retry_loops,)
    )

# 23. Permission surface remains closed in generated candidate gate.
for token in (
    '"scientific_outcome_allowed"',
    '"event_injection_allowed"',
    '"command_transmission_allowed"',
    '"baseline_execution_allowed"',
    '"cryptographic_semantics_claim_allowed"',
    '"baseline_run_1_authorized"',
    '"baseline_run_2_authorized"',
    '"event_injection_authorized"',
):
    if token not in cand:
        fail("closed permission gate token missing: " + token)

# Amendment 1 additive requirements (25-36).
for token in (
    'FORTYTWO_SOURCE_COMMIT="eda252bf31f27850e867e698cfdd963e143ead1f"',
    'FORTYTWO_SOURCE_TREE="541dbc9c3c3d42887b9c668a218ffc3726d24346"',
    'FORTYTWO_42_SHA256="9c0062d2a447a6340e7c191850ff952d3f8768dd307e3e7fb141e777961e60c7"',
    'FORTYTWO_42_BYTES="2250376"',
    'FORTYTWO_42_MODE="0755"',
    'FORTYTWO_HANDOFF_DEST="fortytwo-runtime/42"',
    'FORTYTWO_RUNTIME="$RUNTIME_MATERIAL_ROOT/fortytwo-runtime"',
    "Fortytwo source executable SHA mismatch",
    "Fortytwo source executable identity mismatch",
    "imported Fortytwo executable SHA mismatch",
    "imported Fortytwo executable identity mismatch",
):
    if token not in cand:
        fail("candidate supplemental Fortytwo token missing: " + token)

if cand.count("source=$FORTYTWO_RUNTIME,target=/work/fortytwo") != 1:
    fail("imported Fortytwo runtime mount cardinality invalid")
if "source=$FORTYTWO,target=/work/fortytwo" in cand:
    fail("live Fortytwo runtime mount remains")

if cand.find("V6_FRESH_FORTYTWO_SOURCE_IDENTITY=PASS") > sentinel_marker:
    fail("Fortytwo source identity check occurs after attempt sentinel")
if cand.find("V6_SUPPLEMENTAL_FORTYTWO_HANDOFF_VERIFICATION=PASS") > docker_marker:
    fail("imported Fortytwo verification occurs after Docker")

# No additional explicitly admitted supplemental runtime artifact identifier.
if tx_text.count("supplemental_runtime_artifact_") != tx_text.count(
    "supplemental_runtime_artifact_fortytwo_42"
):
    fail("additional supplemental runtime artifact identifier admitted")

# 24. External writer absence must never be upgraded into a proof.
for label, source in (
    ("transaction-v4", tx_text),
    ("receiver-v1", rx_text),
    ("candidate-v6", cand),
):
    if "external_noncooperating_writer_absence_proven" not in source:
        fail(label + " external-writer limitation missing")
    if re.search(
        r'external_noncooperating_writer_absence_proven["\']?\s*[:=]\s*True',
        source,
    ):
        fail(label + " improperly claims external writer absence")

print("v6_design_lock_negative_suite_source_review=PASS")
print("v6_negative_suite_item_count=36")
print("v6_fresh_gate_before_sentinel=PASS")
print("v6_receipt_verification_before_docker=PASS")
print("v6_source_commit_tree_expected_binding=PASS")
print("v6_amendment1_supplemental_fortytwo_binding=PASS")
print("v6_imported_fortytwo_runtime_mount=PASS")
print("v6_canonical_manifest_unchanged=PASS")
PYSTATIC

candidate_sha="$(shasum -a 256 "$candidate" | awk '{print $1}')"
candidate_bytes="$(wc -c < "$candidate" | tr -d ' ')"

if [[ "$mode" == "--selftest" ]]; then
  echo "V6_STATIC_VERIFIER_SELFTEST=PASS"
  echo "FORMAL_V6_STATIC_VERIFICATION_PERFORMED=false"
  echo "V6_SELFTEST_CANDIDATE_EMISSION_PERFORMED=true"
  echo "V6_SELFTEST_CANDIDATE_EXECUTION_PERFORMED=false"
  echo "V6_SELFTEST_CANDIDATE_SHA256=$candidate_sha"
  echo "V6_SELFTEST_CANDIDATE_BYTES=$candidate_bytes"
  echo "V6_NEGATIVE_SUITE_ITEM_COUNT=36"
else
  echo "V6_STATIC_VERIFICATION=PASS"
  echo "FORMAL_V6_STATIC_VERIFICATION_PERFORMED=true"
  echo "V6_ACCEPTED_CANDIDATE_SHA256=$candidate_sha"
  echo "V6_ACCEPTED_CANDIDATE_BYTES=$candidate_bytes"
  echo "V6_NEGATIVE_SUITE_ITEM_COUNT=36"
fi
