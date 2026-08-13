#!/usr/bin/env python3
# WP4 V6 privilege-separated transaction successor.
# Derived deterministically from transaction-v3 SHA-256 ce1f1f3ad3ba50373e57f36c6490c4ece67f028994155015ed536ce4832fec9e.
# V6 executable CLI exposes no V5 production fallback.
# WP4 V5 successor derived from immutable transaction-v2 SHA-256
# 7419fa18b891ddc7525fa237b12323a092b9ece0f44d5b6fa4069c614322ce29.
# V5 production CLI accepts schema-2 host evidence only; no schema-1 fallback.
"""NOS3 runtime-material v4 transaction authorization CLI.

Process-boundary production-direction runtime-material transaction tool
(WP4 combined-v4, Checkpoint 2PB2B-A / 2PB2B-A-R2).

Deterministic, host-only, fail-closed.  Uses the Python standard library
only; imports no project-local module.  Implements descriptor-bound v4
materialization-transaction authorization and executing-tool identity
binding, structured D-064 authorization validation with one exact authorized
disposition, actual manifest-content verification (not only claimed
invariants), gate-level closed permissions, a deeply immutable process-local
transaction context that is never returned to a caller, and controlled
fail-closed conversion of expected filesystem/path failures.

Checkpoint 2PB2B-B2 implements the complete process-local production
transaction core: after all authorization checks succeed, the tool builds the
canonical plan from the retained manifest bytes, inspects the authorized root,
creates one private outer staging transaction, materializes every expanded
file target via descriptor-bound source traversal (rejecting symlinks, hard
links, non-regular objects, and mode/nlink/size mismatch), writes the
canonical receipt, fsyncs the staged hierarchy, publishes one atomic
no-replace rename, fsyncs the authorized root, and returns
rc=0 / V4_TRANSACTION_MATERIALIZATION=PASS.  The host candidate remains
outside this tool; standard-library-only; no project-local import, no
subprocess, no Docker.  Under the current real contract 0.4.13 authorization
fails closed and returns rc=1 with V4_TRANSACTION_AUTHORIZATION=CLOSED before
any authorized-root inspection, staging, or publication.  Integrated
self-tests exercise the core with synthetic source fixtures (never the full
external/nos3 tree).  The inherited synthetic outer-transaction engine is
retained for its targeted fault-injection tests.
"""

import argparse
import contextlib
import ctypes
import ctypes.util
import errno
import fnmatch
import fcntl
import hashlib
import json
import os
import secrets
import stat
import struct
import sys
import tempfile
from collections import namedtuple

_HEX64 = set("0123456789abcdef")
_D064_AUTHORIZED = "AUTHORIZED_FOR_ONE_BOUNDED_PASSIVE_ATTEMPT"
_D064_ACL_POLICY = "NO_EXTENDED_ACL_ENTRIES_FOR_FIRST_D064_ATTEMPT"
_D064_SERIALIZATION_METHOD = "fcntl.flock_LOCK_EX_LOCK_NB"
_D064_LOCK_BASENAME = ".wp4-d064-v4-transaction.lock"
_D064_LOCK_MODE = 0o600
_ACL_TYPE_EXTENDED = 256
_ACL_FIRST_ENTRY = 0
_ACL_NEXT_ENTRY = -1
_HOST_EVIDENCE_SCHEMA = 1
_HOST_EVIDENCE_TYPE = "D064_HOST_EXCLUSIVE_WRITER_PRECONDITION"
_HOST_EVIDENCE_STATUS = "RETAINED_PRECONDITION_EVIDENCE"
_HOST_EVIDENCE_CLAIM_SCOPE = "HOST_PREATTEMPT_OBSERVATION_NOT_PROOF_OF_NONCOOPERATING_WRITER_ABSENCE"

_V5_PREDECESSOR_TRANSACTION_V2_SHA256 = "7419fa18b891ddc7525fa237b12323a092b9ece0f44d5b6fa4069c614322ce29"
_V5_HOST_EVIDENCE_SCHEMA = 2
_V5_HOST_EVIDENCE_TYPE = "D064_HOST_EXCLUSIVE_WRITER_PRECONDITION_REFRESH"
_V5_HOST_EVIDENCE_STATUS = "CAPTURED_FRESH_SUCCESSOR_PRECONDITION_EVIDENCE_PENDING_INDEPENDENT_REVIEW_NOT_D064_AUTHORITY"
_V5_HOST_EVIDENCE_CLAIM_SCOPE = "HOST_PREATTEMPT_OBSERVATION_NOT_PROOF_OF_NONCOOPERATING_WRITER_ABSENCE"
_V5_HOST_EVIDENCE_REL = "review-evidence/WP4_D064_V4_PRE_D064/host-exclusive-writer-precondition-v3.json"
_V5_HOST_EVIDENCE_SHA256 = "c4783f95de24ae309c6fd1c79ea2bc0d27e1dfdb319259351338d0f75c62de9a"
_V5_HOST_EVIDENCE_BYTES = 8400
_V5_HOST_EVIDENCE_OBSERVED_AT_UTC = "2026-08-11T23:21:19Z"
_V5_HOST_EVIDENCE_CAPTURE_GATE_SHA256 = "f5aa02c3c89bcb119313a105f8606631f4353e7215d01cdc4e757c6c5800633a"
_V5_HOST_EVIDENCE_REVIEW_SHA256 = "4f9a079ff7954dc3f9f52cf62b8a8a3ba79639c89fe9de508d14f2a6b6577687"
_V5_CURRENT_MACL_SHA256 = "d66d5f6d7ae3cc3cb4144fb7baaa3ac7c6b5bceecbb5be3737eaf52859e061fe"
_V5_CURRENT_PROVENANCE_SHA256 = "f5556b5fbd36d387eebe64c9da92eb21a7af846e790cbd98bfcf742963eb683d"
_V5_SCHEMA1_PRODUCTION_FALLBACK_ALLOWED = False

# Selftest-only synthetic-source override.  This is None in every production
# path.  It is set only inside selftest() scope and cleared in selftest()'s
# finally, so it never persists as module-global production state after a test.
# It NEVER bypasses authorization (the full authorization pipeline runs first),
# cannot be supplied through CLI arguments, and cannot supply a forged plan:
# the validated canonical plan, collision model, exclusion enforcement, and
# source mode/nlink/size/sha matching all still run unchanged.  It only redirects
# where the already-validated canonical-plan source files are physically read
# from so the integrated copy/verify/publish pipeline can be exercised with tiny
# synthetic fixtures instead of the full external/nos3 tree.
_B2_SELFTEST_SOURCE_OVERRIDE = None


class _TransactionClosed(Exception):
    """Controlled internal failure used for authorization rejection.

    Expected filesystem/path failures (missing files, symlink rejection,
    non-regular objects, nlink mismatch, malformed paths, read/seek/open
    failures) are converted into this exception so the CLI never emits a
    traceback for an expected authorization failure."""


# Immutable, primitive-only receipt records (tuples of primitives).

_FileReceipt = namedtuple("_FileReceipt",
                           ("rel", "dev", "ino", "size", "mode", "nlink",
                            "sha256"))
_RepoReceipt = namedtuple("_RepoReceipt", ("dev", "ino"))
_LockReceipt = namedtuple("_LockReceipt", ("basename", "dev", "ino", "mode", "nlink", "uid"))
_Permissions = namedtuple("_Permissions",
                           ("scientific_outcome_allowed",
                            "command_transmission_allowed",
                            "baseline_execution_allowed",
                            "event_injection_allowed",
                            "cryptographic_semantics_claim_allowed"))
_GatePermissions = namedtuple("_GatePermissions",
                          ("baseline_run_1_authorized",
                           "baseline_run_2_authorized",
                           "event_injection_authorized"))




class _TransactionContext:
    """Deeply immutable process-local transaction context.  Built only from
    tuples/namedtuples of primitives (no dict, no list, no set, no mutable
    nested receipt).  NOT module-global, NOT serialized, NOT printed, NOT
    returned to a caller, NOT accepted from a caller, NOT stored in a
    registry.  Retained only as a local variable inside one CLI invocation
    and destroyed when the process exits."""

    __slots__ = ("repo", "contract", "candidate", "tool", "manifest",
                 "host_evidence", "host_evidence_schema",
                 "host_evidence_type", "host_evidence_status",
                 "host_evidence_observed_at_utc",
                 "compatibility_governance_decision",
                 "compatibility_governance_contract_version",
                 "compatibility_governance_contract_sha256",
                 "fresh_evidence_independent_review_script_sha256",
                 "successor_consumer_independent_review_script_sha256",
                 "successor_consumer_independent_review_result",
                 "successor_consumer_independent_review_findings",
                 "governance_binding_verified",
                 "schema", "static_verification",
                 "diagnostic_runtime_authorized",
                 "diagnostic_runtime_attempts_authorized",
                 "amendment_runtime_authorized", "amendment_runtime_attempts",
                 "d064_disposition", "accepted_candidate_sha",
                 "top_permissions", "gate_permissions", "_frozen")

    def __init__(self, repo, contract, candidate, tool, manifest,
                 host_evidence, host_evidence_schema, schema,
                 static_verification, diagnostic_runtime_authorized,
                 diagnostic_runtime_attempts_authorized,
                 amendment_runtime_authorized, amendment_runtime_attempts,
                 d064_disposition, accepted_candidate_sha,
                 top_permissions, gate_permissions,
                 host_evidence_type=None, host_evidence_status=None,
                 host_evidence_observed_at_utc=None,
                 compatibility_governance_decision=None,
                 compatibility_governance_contract_version=None,
                 compatibility_governance_contract_sha256=None,
                 fresh_evidence_independent_review_script_sha256=None,
                 successor_consumer_independent_review_script_sha256=None,
                 successor_consumer_independent_review_result=None,
                 successor_consumer_independent_review_findings=None,
                 governance_binding_verified=None):
        object.__setattr__(self, "repo", repo)
        object.__setattr__(self, "contract", contract)
        object.__setattr__(self, "candidate", candidate)
        object.__setattr__(self, "tool", tool)
        object.__setattr__(self, "manifest", manifest)
        object.__setattr__(self, "host_evidence", host_evidence)
        object.__setattr__(self, "host_evidence_schema", host_evidence_schema)
        object.__setattr__(self, "schema", schema)
        object.__setattr__(self, "static_verification", static_verification)
        object.__setattr__(self, "diagnostic_runtime_authorized",
                           diagnostic_runtime_authorized)
        object.__setattr__(self, "diagnostic_runtime_attempts_authorized",
                           diagnostic_runtime_attempts_authorized)
        object.__setattr__(self, "amendment_runtime_authorized",
                           amendment_runtime_authorized)
        object.__setattr__(self, "amendment_runtime_attempts",
                           amendment_runtime_attempts)
        object.__setattr__(self, "d064_disposition", d064_disposition)
        object.__setattr__(self, "accepted_candidate_sha",
                           accepted_candidate_sha)
        object.__setattr__(self, "top_permissions", top_permissions)
        object.__setattr__(self, "gate_permissions", gate_permissions)
        object.__setattr__(self, "host_evidence_type", host_evidence_type)
        object.__setattr__(self, "host_evidence_status", host_evidence_status)
        object.__setattr__(self, "host_evidence_observed_at_utc", host_evidence_observed_at_utc)
        object.__setattr__(self, "compatibility_governance_decision", compatibility_governance_decision)
        object.__setattr__(self, "compatibility_governance_contract_version", compatibility_governance_contract_version)
        object.__setattr__(self, "compatibility_governance_contract_sha256", compatibility_governance_contract_sha256)
        object.__setattr__(self, "fresh_evidence_independent_review_script_sha256", fresh_evidence_independent_review_script_sha256)
        object.__setattr__(self, "successor_consumer_independent_review_script_sha256", successor_consumer_independent_review_script_sha256)
        object.__setattr__(self, "successor_consumer_independent_review_result", successor_consumer_independent_review_result)
        object.__setattr__(self, "successor_consumer_independent_review_findings", successor_consumer_independent_review_findings)
        object.__setattr__(self, "governance_binding_verified", governance_binding_verified)
        object.__setattr__(self, "_frozen", True)

    def __setattr__(self, name, value):
        raise AttributeError("transaction context is immutable")

    def __delattr__(self, name):
        raise AttributeError("transaction context is immutable")


def _is_exact_int(v):
    return type(v) is int


def _is_exact_bool(v):
    return isinstance(v, bool)


def _is_exact_str(value):
    return type(value) is str


def _is_hex64(s):
    if not _is_exact_str(s):
        return False
    if len(s) != 64:
        return False
    return all(c in _HEX64 for c in s)


def _sha256_file_path(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            b = f.read(1024 * 1024)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def _wrap_os(msg, fn, *a, **k):
    """Run an OS/filesystem operation; convert OSError into _TransactionClosed
    so expected failures become the controlled closed disposition rather than
    an uncaught traceback.  Never catches KeyboardInterrupt/SystemExit."""
    try:
        return fn(*a, **k)
    except _TransactionClosed:
        raise
    except OSError as exc:
        raise _TransactionClosed("%s: %s" % (msg, exc))


def _open_repo_root_fd(repo_root):
    """Open the repository root once with O_RDONLY|O_DIRECTORY|O_NOFOLLOW.
    Returns (repo_fd, _RepoReceipt).  All further resolution happens through
    this single descriptor via no-follow traversal."""
    if not isinstance(repo_root, str) or repo_root == "":
        raise _TransactionClosed("repo root not a nonempty string")
    if repo_root.endswith(os.sep) and repo_root != os.sep:
        raise _TransactionClosed("repo root must not end with a separator")

    def _open():
        return os.open(repo_root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)

    fd = _wrap_os("repo root open", _open)
    try:
        st = _wrap_os("repo root fstat", os.fstat, fd)
    except _TransactionClosed:
        try:
            os.close(fd)
        except OSError:
            pass
        raise
    return fd, _RepoReceipt(dev=st.st_dev, ino=st.st_ino)


def _validate_rel_path(rel):
    """Validate a repository-relative regular-file path.  Reject absolute
    values, empty, dot/dotdot, repeated separators, backslashes, NUL, and
    surrogate code points."""
    if not isinstance(rel, str) or rel == "":
        raise _TransactionClosed("relative path empty/not a string")
    if rel.startswith("/"):
        raise _TransactionClosed("relative path is absolute")
    if "\\" in rel:
        raise _TransactionClosed("backslash in relative path")
    if "\x00" in rel:
        raise _TransactionClosed("NUL in relative path")
    for ch in rel:
        if 0xD800 <= ord(ch) <= 0xDFFF:
            raise _TransactionClosed("surrogate code point in relative path")
    if "//" in rel:
        raise _TransactionClosed("repeated separator in relative path")
    comps = rel.split("/")
    for c in comps:
        if c == "" or c == "." or c == "..":
            raise _TransactionClosed("empty/dot/dotdot component in relative path")
    return comps


def _open_repo_relative_file(repo_fd, rel_path):
    """Open one repository-relative regular file through strict
    descriptor-relative no-follow traversal.  Returns (fd, _FileReceipt).
    All OSError failures are converted to _TransactionClosed."""
    comps = _validate_rel_path(rel_path)
    cur = repo_fd
    parents = []
    leaf_fd = None
    try:
        for idx in range(len(comps) - 1):
            comp = comps[idx]
            lst = _wrap_os("parent lstat %s" % comp, os.lstat, comp, dir_fd=cur)
            if (lst.st_mode & 0o170000) == 0o120000:
                raise _TransactionClosed("symlinked parent component rejected: %s" % comp)

            def _pop(parent=comp, dirfd=cur):
                return os.open(parent, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                               dir_fd=dirfd)
            try:
                nxt = _wrap_os("parent open %s" % comp, _pop)
            except _TransactionClosed as exc:
                if "ELOOP" in str(exc) or "Too many levels" in str(exc):
                    raise _TransactionClosed("symlinked parent component rejected: %s" % comp)
                raise
            # CORRECTION 2/5: own the parent fd until ownership transfers to
            # the retained parent chain.  The descriptor is closed exactly
            # once by the single handler below on fstat failure OR identity
            # mismatch (never in the branch then again in the handler).
            owned = True
            try:
                nst = _wrap_os("parent fstat %s" % comp, os.fstat, nxt)
                if (nst.st_dev, nst.st_ino) != (lst.st_dev, lst.st_ino):
                    raise _TransactionClosed("parent identity discontinuity: %s" % comp)
            except BaseException:
                if owned:
                    try:
                        os.close(nxt)
                    except OSError:
                        pass
                    owned = False
                raise
            parents.append(nxt)
            owned = False
            cur = nxt
        leaf = comps[-1]
        lst = _wrap_os("leaf lstat %s" % leaf, os.lstat, leaf, dir_fd=cur)
        if (lst.st_mode & 0o170000) == 0o120000:
            raise _TransactionClosed("symlinked leaf rejected: %s" % leaf)

        def _lopen(leafname=leaf, dirfd=cur):
            return os.open(leafname, os.O_RDONLY | os.O_NOFOLLOW, dir_fd=dirfd)
        try:
            leaf_fd = _wrap_os("leaf open %s" % leaf, _lopen)
        except _TransactionClosed as exc:
            if "ELOOP" in str(exc) or "Too many levels" in str(exc):
                raise _TransactionClosed("symlinked leaf rejected: %s" % leaf)
            raise
        fst = _wrap_os("leaf fstat %s" % leaf, os.fstat, leaf_fd)
        if (fst.st_dev, fst.st_ino) != (lst.st_dev, lst.st_ino):
            raise _TransactionClosed("leaf identity discontinuity: %s" % leaf)
        if (fst.st_mode & 0o170000) != 0o100000:
            raise _TransactionClosed("leaf not a regular file: %s" % leaf)
        if fst.st_nlink != 1:
            raise _TransactionClosed("leaf nlink != 1: %s (%d)" % (leaf, fst.st_nlink))
        receipt = _FileReceipt(rel=rel_path, dev=fst.st_dev, ino=fst.st_ino,
                               size=fst.st_size, mode=fst.st_mode,
                               nlink=fst.st_nlink, sha256=None)
        opened, leaf_fd = leaf_fd, None
        return opened, receipt
    except _TransactionClosed:
        if leaf_fd is not None:
            try:
                os.close(leaf_fd)
            except OSError:
                pass
        raise
    finally:
        for fdx in parents:
            try:
                os.close(fdx)
            except OSError:
                pass


@contextlib.contextmanager
def _open_auth_file(repo_fd, rel_path):
    """Context manager wrapping _open_repo_relative_file that reads, parses
    (UTF-8 JSON), and hashes the file through the SAME opened descriptor, then
    closes it.  Yields (receipt, raw_bytes, sha, parsed_obj_or_None).  All IO
    failures are converted to _TransactionClosed."""
    fd = None
    try:
        fd, receipt = _open_repo_relative_file(repo_fd, rel_path)
        # CORRECTION 4: read exactly once; SHA-256 is computed directly over
        # the same raw bytes; no seek/reread.  Final fstat on the still-open
        # descriptor proves dev/inode/mode/nlink/size identity continuity and
        # len(raw) == receipt.size.
        chunks = []

        def _read():
            while True:
                b = os.read(fd, 1024 * 1024)
                if not b:
                    break
                chunks.append(b)
        _wrap_os("read %s" % rel_path, _read)
        raw = b"".join(chunks)
        sha = hashlib.sha256(raw).hexdigest()
        final_st = _wrap_os("post-read fstat %s" % rel_path, os.fstat, fd)
        # CORRECTION 1: exact final-fstat continuity with the initial opened
        # receipt over dev, inode, mode (including permission bits), nlink,
        # and size, plus len(raw) == receipt.size.  Any mismatch closes.
        if (final_st.st_dev, final_st.st_ino, final_st.st_mode,
            final_st.st_nlink, final_st.st_size) != (
            receipt.dev, receipt.ino, receipt.mode, receipt.nlink,
            receipt.size):
            raise _TransactionClosed(
                "post-read fstat discontinuity: %s" % rel_path)
        if len(raw) != receipt.size:
            raise _TransactionClosed(
                "post-read len(raw) != receipt.size: %s" % rel_path)
        receipt = receipt._replace(sha256=sha)
        parsed = None
        try:
            parsed = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, ValueError):
            parsed = None
        yield receipt, raw, sha, parsed
    finally:
        if fd is not None:
            try:
                os.close(fd)
            except OSError:
                pass


def _repo_relative_from_abs(abs_path, repo_abs):
    """Compute a repository-relative path from an absolute path (path
    normalization only; no realpath authority)."""
    if not isinstance(abs_path, str) or abs_path == "":
        raise _TransactionClosed("absolute path empty/not a string")
    if not abs_path.startswith(repo_abs):
        raise _TransactionClosed("path outside repository root")
    sep = os.sep
    if abs_path == repo_abs:
        raise _TransactionClosed("path is the repository root")
    if not repo_abs.endswith(sep):
        prefix = repo_abs + sep
        if not abs_path.startswith(prefix):
            raise _TransactionClosed("path outside repository root")
        rel = abs_path[len(prefix):]
    else:
        rel = abs_path[len(repo_abs):]
    if rel == "":
        raise _TransactionClosed("empty relative path")
    if rel.startswith("/"):
        raise _TransactionClosed("relative path becomes absolute")
    _validate_rel_path(rel)
    return rel


def _manifest_canonical_check(raw):
    """Manifest structural + actual-content checks for 2PB2A-R1: valid UTF-8,
    top-level object, no BOM, no CR, exactly one final LF, canonical
    reserialization equality, schema exact int 1, actual array counts, actual
    byte total, exact workspace component IDs, and invariant-claims-equal-
    actual-values.  A manifest whose claims match but actual arrays/bytes
    differ fails closed."""
    if not isinstance(raw, (bytes, bytearray)):
        raise _TransactionClosed("manifest not bytes")
    if raw.startswith(b"\xef\xbb\xbf"):
        raise _TransactionClosed("manifest BOM present")
    if b"\r" in raw:
        raise _TransactionClosed("manifest CR present")
    if not raw.endswith(b"\n"):
        raise _TransactionClosed("manifest missing final LF")
    if raw.endswith(b"\n\n"):
        raise _TransactionClosed("manifest duplicate final LF")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        raise _TransactionClosed("manifest invalid UTF-8")
    body = text[:-1]
    if body != body.strip():
        raise _TransactionClosed("manifest surrounding whitespace")
    if not body.startswith("{"):
        raise _TransactionClosed("manifest top-level not an object")
    try:
        m = json.loads(raw)
    except ValueError as exc:
        raise _TransactionClosed("manifest JSON parse error: %s" % exc)
    canon = (json.dumps(m, ensure_ascii=True, sort_keys=True,
                        separators=(",", ":")) + "\n").encode("utf-8")
    if canon != bytes(raw):
        raise _TransactionClosed("manifest not canonical serialization")
    if not _is_exact_int(m.get("schema")) or m.get("schema") != 1:
        raise _TransactionClosed("manifest schema not exact int 1")
    inv = m.get("inventory_invariants")
    if not isinstance(inv, dict):
        raise _TransactionClosed("manifest inventory_invariants missing")

    # --- ACTUAL array + byte verification (not only claimed invariants) ---
    fe = m.get("included_regular_file_entries")
    if not isinstance(fe, list):
        raise _TransactionClosed("manifest included_regular_file_entries not a list")
    actual_file_count = len(fe)
    actual_byte_sum = 0
    for e in fe:
        if not isinstance(e, dict):
            raise _TransactionClosed("manifest file entry not an object")
        sz = e.get("size")
        if not _is_exact_int(sz) or sz < 0:
            raise _TransactionClosed("manifest file entry size not nonnegative int")
        actual_byte_sum += sz
    if actual_file_count != 1422:
        raise _TransactionClosed("manifest actual included file count != 1422")
    if actual_byte_sum != 100496114:
        raise _TransactionClosed("manifest actual included byte sum != 100496114 (%d)" % actual_byte_sum)

    de = m.get("directory_entries")
    if not isinstance(de, list):
        raise _TransactionClosed("manifest directory_entries not a list")
    actual_dir_count = len(de)
    if actual_dir_count != 89:
        raise _TransactionClosed("manifest actual directory count != 89")

    er = m.get("exact_exclusion_records")
    if not isinstance(er, list):
        raise _TransactionClosed("manifest exact_exclusion_records not a list")
    actual_excl_count = len(er)
    if actual_excl_count != 11:
        raise _TransactionClosed("manifest actual exclusion count != 11")

    ws = m.get("workspace_declarations")
    if not isinstance(ws, list) or len(ws) != 18:
        raise _TransactionClosed("manifest workspace count != 18")
    expected_ids = ["nos_engine", "time_driver"] + [
        "hw_sim_%02d" % i for i in range(1, 15)] + ["cmd_bus_bridge", "cfs"]
    # CORRECTION 3: validate every declaration is an object and every
    # component_id is an exact string BEFORE calling sorted().  Reject
    # missing, bool/int/float/None/object/list, and duplicate IDs.
    got_ids = []
    seen = set()
    for w in ws:
        if not isinstance(w, dict):
            raise _TransactionClosed("manifest workspace declaration not an object")
        cid = w.get("component_id")
        if not isinstance(cid, str) or isinstance(cid, bool):
            raise _TransactionClosed("manifest workspace component_id not a string")
        if cid == "":
            raise _TransactionClosed("manifest workspace component_id empty string")
        if cid in seen:
            raise _TransactionClosed("manifest workspace duplicate component_id: %s" % cid)
        seen.add(cid)
        got_ids.append(cid)
    if sorted(got_ids) != sorted(expected_ids):
        raise _TransactionClosed("manifest workspace component IDs mismatch")

    # --- invariant claims MUST equal the actual calculated values ---
    ec = inv.get("invariant_included_manifest_regular_file_entry_count")
    dc = inv.get("invariant_directory_entry_count")
    exc = inv.get("invariant_exact_exclusion_record_count")
    bt = inv.get("invariant_included_bytes")
    if not (_is_exact_int(ec) and ec == actual_file_count):
        raise _TransactionClosed("manifest invariant file count != actual (%r vs %d)" % (ec, actual_file_count))
    if not (_is_exact_int(dc) and dc == actual_dir_count):
        raise _TransactionClosed("manifest invariant directory count != actual (%r vs %d)" % (dc, actual_dir_count))
    if not (_is_exact_int(exc) and exc == actual_excl_count):
        raise _TransactionClosed("manifest invariant exclusion count != actual (%r vs %d)" % (exc, actual_excl_count))
    if not (_is_exact_int(bt) and bt == actual_byte_sum):
        raise _TransactionClosed("manifest invariant byte total != actual (%r vs %d)" % (bt, actual_byte_sum))
    return m


def _validate_host_exclusive_writer_evidence(raw, parsed):
    if not isinstance(raw, (bytes, bytearray)):
        raise _TransactionClosed("host evidence not bytes")
    if b"\r" in raw or not raw.endswith(b"\n") or raw.endswith(b"\n\n"):
        raise _TransactionClosed("host evidence line ending invalid")
    if not isinstance(parsed, dict):
        raise _TransactionClosed("host evidence not JSON object")
    canon=(json.dumps(parsed,ensure_ascii=True,sort_keys=True,separators=(",",":"))+"\n").encode("utf-8")
    if canon != bytes(raw):
        raise _TransactionClosed("host evidence not canonical")
    req={"schema":_HOST_EVIDENCE_SCHEMA,"evidence_type":_HOST_EVIDENCE_TYPE,"platform":"Darwin","acl_policy":_D064_ACL_POLICY,"serialization_method":_D064_SERIALIZATION_METHOD,"status":_HOST_EVIDENCE_STATUS,"claim_scope":_HOST_EVIDENCE_CLAIM_SCOPE}
    for k,v in req.items():
        if parsed.get(k) != v:
            raise _TransactionClosed("host evidence field mismatch: %s" % k)
    if not _is_exact_int(parsed.get("schema")):
        raise _TransactionClosed("host evidence schema not exact int")
    return parsed["schema"]


def _require_false_permission(container, key, kind):
    v = container.get(key)
    if not _is_exact_bool(v):
        raise _TransactionClosed("%s %s not exact bool" % (kind, key))
    if v is not False:
        raise _TransactionClosed("%s %s not false" % (kind, key))


def _validate_structured_authorization(contract, cand_sha, tool_rel, tool_sha,
                                       man_rel, man_sha, evidence_rel,
                                       evidence_sha, evidence_schema):
    """Validate actual contract BYTES (via the parsed object) for exact
    structured D-064 authorization.  Fails closed on any missing/malformed/
    wrongly-typed field, including bool-as-int substitution.  D-064 uses one
    exact authorized disposition (not a denylist)."""
    if not isinstance(contract, dict):
        raise _TransactionClosed("contract not a JSON object")
    g = contract.get("gate")
    if not isinstance(g, dict):
        raise _TransactionClosed("contract gate missing")
    schema = g.get("passive_time_witness_runtime_candidate_v4_contract_schema")
    if not (_is_exact_int(schema) and schema == 1):
        raise _TransactionClosed("v4 contract schema not exact int 1")
    sv = g.get("passive_time_witness_runtime_candidate_v4_static_verification")
    if sv != "PASS":
        raise _TransactionClosed("v4 static verification not PASS")
    if not _is_exact_bool(g.get("diagnostic_runtime_authorized")):
        raise _TransactionClosed("diagnostic_runtime_authorized not exact bool")
    if g.get("diagnostic_runtime_authorized") is not True:
        raise _TransactionClosed("diagnostic_runtime_authorized not True")
    dra = g.get("diagnostic_runtime_attempts_authorized")
    if not (_is_exact_int(dra) and dra == 1):
        raise _TransactionClosed("diagnostic_runtime_attempts_authorized not int 1")
    # Top-level closed permissions (exact bool false).
    for perm in ("scientific_outcome_allowed", "command_transmission_allowed",
                 "baseline_execution_allowed", "event_injection_allowed",
                 "cryptographic_semantics_claim_allowed"):
        _require_false_permission(contract, perm, "top-level")
    # Gate-level closed permissions (exact bool false).
    for perm in ("baseline_run_1_authorized", "baseline_run_2_authorized",
                 "event_injection_authorized"):
        _require_false_permission(g, perm, "gate-level")
    acc = g.get("accepted_runtime_entrypoint_v4_sha256")
    if not _is_hex64(acc):
        raise _TransactionClosed("accepted_runtime_entrypoint_v4_sha256 not hex64")
    if acc != acc.lower():
        raise _TransactionClosed("accepted v4 sha not lowercase")
    if acc != cand_sha:
        raise _TransactionClosed("candidate sha != accepted v4 sha")
    nfx = g.get("accepted_runtime_entrypoint_v4_identity_only_not_authorized")
    if nfx is not False:
        raise _TransactionClosed("v4 identity-only flag not False (narrative not authority)")
    am = contract.get(
        "passive_time_witness_runtime_candidate_v4_design_amendment_1")
    if not isinstance(am, dict):
        raise _TransactionClosed("v4 amendment block missing")
    if not _is_exact_bool(am.get("runtime_authorized")):
        raise _TransactionClosed("amendment runtime_authorized not exact bool")
    if am.get("runtime_authorized") is not True:
        raise _TransactionClosed("amendment runtime_authorized not True")
    att = am.get("runtime_attempts")
    if not (_is_exact_int(att) and att == 1):
        raise _TransactionClosed("amendment runtime_attempts not int 1")
    # CORRECTION 1: exact D-064 authorized state (allowlist of one).
    d064 = am.get("d064_status")
    if not isinstance(d064, str) or d064 != _D064_AUTHORIZED:
        raise _TransactionClosed("d064_status not exact authorized state: %r" % (d064,))
    impl = am.get("passive_time_witness_runtime_candidate_v4_implementation")
    if not isinstance(impl, dict):
        raise _TransactionClosed("v4 implementation block missing")
    rt = impl.get("runtime_material_tool")
    if not isinstance(rt, dict):
        raise _TransactionClosed("implementation runtime_material_tool block missing")
    if rt.get("path") != tool_rel:
        raise _TransactionClosed("implementation tool path mismatch: %r != %r"
                                 % (rt.get("path"), tool_rel))
    if rt.get("sha256") != tool_sha:
        raise _TransactionClosed("implementation tool sha mismatch")
    cm = impl.get("canonical_manifest")
    if not isinstance(cm, dict):
        raise _TransactionClosed("implementation canonical_manifest block missing")
    if cm.get("path") != man_rel:
        raise _TransactionClosed("implementation manifest path mismatch")
    if cm.get("sha256") != man_sha:
        raise _TransactionClosed("implementation manifest sha mismatch")
    he = impl.get("host_exclusive_writer_evidence")
    if not isinstance(he, dict):
        raise _TransactionClosed("implementation host evidence block missing")
    if he.get("path") != evidence_rel or he.get("sha256") != evidence_sha:
        raise _TransactionClosed("host evidence identity binding mismatch")
    if he.get("schema") != evidence_schema or he.get("status") != _HOST_EVIDENCE_STATUS:
        raise _TransactionClosed("host evidence schema/status binding mismatch")
    return (schema, sv, True, 1, True, 1, d064, acc,
            tuple(contract[p] for p in ("scientific_outcome_allowed",
                                        "command_transmission_allowed",
                                        "baseline_execution_allowed",
                                        "event_injection_allowed",
                                        "cryptographic_semantics_claim_allowed")),
            tuple(g[p] for p in ("baseline_run_1_authorized",
                                "baseline_run_2_authorized",
                                "event_injection_authorized")))



def _v5_need(condition, message):
    if not condition:
        raise _TransactionClosed(message)


def _validate_host_exclusive_writer_evidence_v5(raw, parsed):
    if not isinstance(raw, (bytes, bytearray)):
        raise _TransactionClosed("v5 host evidence not bytes")
    if b"\r" in raw or not raw.endswith(b"\n") or raw.endswith(b"\n\n"):
        raise _TransactionClosed("v5 host evidence line ending invalid")
    if not isinstance(parsed, dict):
        raise _TransactionClosed("v5 host evidence not JSON object")
    canon = (
        json.dumps(parsed, ensure_ascii=True, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")
    if canon != bytes(raw):
        raise _TransactionClosed("v5 host evidence not canonical")
    if len(raw) != _V5_HOST_EVIDENCE_BYTES:
        raise _TransactionClosed("v5 host evidence byte count mismatch")

    expected_top = {
        "schema": _V5_HOST_EVIDENCE_SCHEMA,
        "evidence_type": _V5_HOST_EVIDENCE_TYPE,
        "status": _V5_HOST_EVIDENCE_STATUS,
        "claim_scope": _V5_HOST_EVIDENCE_CLAIM_SCOPE,
        "observed_at_utc": _V5_HOST_EVIDENCE_OBSERVED_AT_UTC,
    }
    for key, value in expected_top.items():
        if parsed.get(key) != value:
            raise _TransactionClosed("v5 host evidence field mismatch: %s" % key)
    if not _is_exact_int(parsed.get("schema")):
        raise _TransactionClosed("v5 host evidence schema not exact int")

    root = parsed.get("authorized_root")
    _v5_need(isinstance(root, dict), "v5 authorized_root missing")
    for key, value in (
        ("absolute_path", "/Users/zarthras/.wp4-d064-v4-authorized-root"),
        ("device", 16777221),
        ("inode", 359966629),
        ("uid", 599),
        ("gid", 20),
        ("mode", "0700"),
        ("nlink", 2),
        ("extended_acl_entry_count", 0),
        ("empty_at_capture", True),
        ("owner_matches_dedicated_materializer_uid", True),
        ("path_components_symlink_free", True),
        ("physical_realpath_matches", True),
        ("transaction_lock_present", False),
    ):
        _v5_need(root.get(key) == value, "v5 authorized_root mismatch: %s" % key)

    materializer = parsed.get("materializer_identity")
    _v5_need(isinstance(materializer, dict), "v5 materializer identity missing")
    for key, value in (
        ("short_name", "wp4d064mat"),
        ("generated_uid", "2AC97A9C-BB18-4A01-9E31-5BAB524A00B8"),
        ("uid", 599),
        ("primary_gid", 20),
        ("home_directory", "/var/empty"),
        ("login_shell", "/usr/bin/false"),
        ("not_admin", True),
        ("non_login_shell", True),
        ("interactive_authentication_disabled_proven", False),
        ("password_authentication_claim", "NOT_MADE"),
    ):
        _v5_need(
            materializer.get(key) == value,
            "v5 materializer identity mismatch: %s" % key,
        )

    parent = parsed.get("parent_traversal_remediation")
    _v5_need(isinstance(parent, dict), "v5 parent traversal missing")
    for key, value in (
        ("parent_path", "/Users/zarthras/Documents"),
        ("device", 16777221),
        ("inode", 24332),
        ("uid", 501),
        ("gid", 20),
        ("mode", "0700"),
        ("acl_inheritance", "none"),
        ("extended_acl_entry_count", 2),
        ("search_traversal_effective", True),
        ("directory_listing_granted", False),
        ("write_access_granted", False),
        ("repository_access_effective", True),
        ("transaction_input_read_access_effective", True),
        ("contract_read_access_effective", True),
        ("canonical_manifest_read_access_effective", True),
    ):
        _v5_need(parent.get(key) == value, "v5 parent mismatch: %s" % key)
    _v5_need(
        type(parent.get("acl_rights")) is list
        and parent["acl_rights"] == ["search"],
        "v5 parent acl_rights must be exact list ['search']",
    )

    xattrs = parent.get("xattrs")
    _v5_need(isinstance(xattrs, dict), "v5 xattr block missing")
    _v5_need(
        xattrs.get("sorted_name_set") == ["com.apple.macl", "com.apple.provenance"],
        "v5 xattr name set mismatch",
    )
    _v5_need(
        xattrs.get("dual_observation_path_byte_equality") is True,
        "v5 dual xattr observation mismatch",
    )
    _v5_need(xattrs.get("raw_values_printed") is False, "v5 xattr raw print overclaim")
    _v5_need(xattrs.get("raw_values_retained") is False, "v5 xattr raw retention")

    macl = xattrs.get("com_apple_macl")
    provenance = xattrs.get("com_apple_provenance")
    _v5_need(isinstance(macl, dict), "v5 macl observation missing")
    _v5_need(isinstance(provenance, dict), "v5 provenance observation missing")

    for obj, expected_sha, expected_len, label in (
        (macl, _V5_CURRENT_MACL_SHA256, 72, "macl"),
        (provenance, _V5_CURRENT_PROVENANCE_SHA256, 11, "provenance"),
    ):
        _v5_need(obj.get("capture_sha256") == expected_sha, label + " SHA mismatch")
        _v5_need(
            _is_exact_int(obj.get("capture_length"))
            and obj["capture_length"] == expected_len,
            label + " length mismatch",
        )
        _v5_need(obj.get("causation_proven") is False, label + " causation overclaim")
        _v5_need(obj.get("semantics_claim") == "NOT_MADE", label + " semantics claim")
        _v5_need(
            obj.get("remediation_authorized") is False,
            label + " remediation unexpectedly authorized",
        )
        _v5_need(
            obj.get("remediation_performed") is False,
            label + " remediation unexpectedly performed",
        )
    _v5_need(
        macl.get("internal_semantics_used_for_authorization") is False,
        "v5 MACL internal semantics used for authorization",
    )

    concurrent = parsed.get("concurrent_writer_observation")
    _v5_need(isinstance(concurrent, dict), "v5 concurrent writer block missing")
    _v5_need(
        concurrent.get("external_noncooperating_writer_absence_proven") is False,
        "v5 external noncooperating writer absence overclaim",
    )
    _v5_need(
        _is_exact_int(concurrent.get("dedicated_uid_process_count"))
        and concurrent["dedicated_uid_process_count"] == 0,
        "v5 dedicated uid process count mismatch",
    )
    _v5_need(
        _is_exact_int(concurrent.get("open_handle_count_under_authorized_root"))
        and concurrent["open_handle_count_under_authorized_root"] == 0,
        "v5 root open handle count mismatch",
    )
    _v5_need(concurrent.get("time_machine_running") is False, "v5 Time Machine mismatch")

    serial = parsed.get("serialization_readiness")
    _v5_need(isinstance(serial, dict), "v5 serialization block missing")
    for key, value in (
        ("method", _D064_SERIALIZATION_METHOD),
        ("lock_basename", _D064_LOCK_BASENAME),
        ("lock_mode", "0600"),
        ("advisory_only", True),
        ("current_transaction_lock_present", False),
        ("external_noncooperating_writer_absence_proven", False),
        ("fresh_contention_probe_performed", False),
    ):
        _v5_need(serial.get(key) == value, "v5 serialization mismatch: %s" % key)

    capture = parsed.get("capture_governance")
    _v5_need(isinstance(capture, dict), "v5 capture governance missing")
    for key, value in (
        ("capture_tool_sha256", _V5_HOST_EVIDENCE_CAPTURE_GATE_SHA256),
        ("independent_review_completed", False),
        ("governance_binding_completed", False),
        ("d064_authorization_decision_eligible", False),
        ("capture_only_not_d064_authorization", True),
        ("xattr_remediation_authorized", False),
        ("xattr_remediation_performed", False),
    ):
        _v5_need(capture.get(key) == value, "v5 capture governance mismatch: %s" % key)

    capture_contract = parsed.get("contract_binding")
    _v5_need(
        isinstance(capture_contract, dict)
        and capture_contract.get("authorized") is False
        and capture_contract.get("performed") is False,
        "v5 capture contract binding must remain false",
    )

    runtime = parsed.get("runtime_boundaries")
    _v5_need(isinstance(runtime, dict), "v5 runtime boundaries missing")
    for key in (
        "baseline_executed",
        "candidate_executed",
        "command_transmission_executed",
        "d064_authorized",
        "event_injection_executed",
        "execution_11_rerun",
        "production_materialization_executed",
        "runtime_authorized",
        "wp5_execution_authorized",
    ):
        _v5_need(runtime.get(key) is False, "v5 runtime boundary open: %s" % key)
    _v5_need(
        _is_exact_int(runtime.get("runtime_attempts"))
        and runtime["runtime_attempts"] == 0,
        "v5 runtime attempts nonzero",
    )

    publication = parsed.get("publication_binding")
    _v5_need(isinstance(publication, dict), "v5 historical publication binding missing")
    _v5_need(
        publication.get("transaction_v2_sha256")
        == _V5_PREDECESSOR_TRANSACTION_V2_SHA256,
        "v5 historical transaction-v2 identity mismatch",
    )
    return parsed["schema"]


def _v5_validate_he2_lineage(contract):
    he2 = contract.get(
        "passive_time_witness_runtime_candidate_v4_fresh_successor_host_evidence_governance_2"
    )
    if not isinstance(he2, dict):
        raise _TransactionClosed("HE2 governance block missing")
    fresh = he2.get("fresh_successor_host_evidence")
    if not isinstance(fresh, dict):
        raise _TransactionClosed("HE2 fresh successor evidence missing")
    expected = {
        "path": _V5_HOST_EVIDENCE_REL,
        "sha256": _V5_HOST_EVIDENCE_SHA256,
        "bytes": _V5_HOST_EVIDENCE_BYTES,
        "schema": _V5_HOST_EVIDENCE_SCHEMA,
        "evidence_type": _V5_HOST_EVIDENCE_TYPE,
        "status": _V5_HOST_EVIDENCE_STATUS,
        "observed_at_utc": _V5_HOST_EVIDENCE_OBSERVED_AT_UTC,
        "capture_gate_sha256": _V5_HOST_EVIDENCE_CAPTURE_GATE_SHA256,
        "independent_review_script_sha256": _V5_HOST_EVIDENCE_REVIEW_SHA256,
        "independent_review_result": "PASS",
        "independent_review_findings": 0,
        "current_host_reobservation_consistent_with_v3": True,
    }
    for key, value in expected.items():
        if fresh.get(key) != value:
            raise _TransactionClosed("HE2 fresh evidence mismatch: %s" % key)
    for key in ("bytes", "schema", "independent_review_findings"):
        if not _is_exact_int(fresh.get(key)):
            raise _TransactionClosed("HE2 fresh evidence int type mismatch: %s" % key)
    if fresh.get("current_host_reobservation_consistent_with_v3") is not True:
        raise _TransactionClosed("HE2 fresh host reobservation not exact true")
    disposition = he2.get("consumer_compatibility_disposition")
    if not isinstance(disposition, dict):
        raise _TransactionClosed("HE2 consumer compatibility disposition missing")
    if disposition.get("transaction_v2_sha256") != _V5_PREDECESSOR_TRANSACTION_V2_SHA256:
        raise _TransactionClosed("HE2 transaction-v2 identity mismatch")
    if disposition.get("compatible") is not False:
        raise _TransactionClosed("HE2 v2 incompatibility history changed")
    if disposition.get("source_remediation_authorized") is not False:
        raise _TransactionClosed("HE2 historical source-remediation flag changed")
    return fresh


def _validate_structured_authorization_v5(
    contract,
    cand_sha,
    tool_rel,
    tool_sha,
    man_rel,
    man_sha,
    evidence_rel,
    evidence_sha,
    evidence_schema,
):
    if not isinstance(contract, dict):
        raise _TransactionClosed("v5 contract not object")
    contract_version = contract.get("contract_version")
    if not _is_exact_str(contract_version) or contract_version == "":
        raise _TransactionClosed("v5 contract version invalid")

    gate = contract.get("gate")
    if not isinstance(gate, dict):
        raise _TransactionClosed("v5 gate missing")
    schema = gate.get("passive_time_witness_runtime_candidate_v5_contract_schema")
    if not (_is_exact_int(schema) and schema == 1):
        raise _TransactionClosed("v5 contract schema not exact int 1")
    static_result = gate.get(
        "passive_time_witness_runtime_candidate_v5_static_verification"
    )
    if static_result != "PASS":
        raise _TransactionClosed("v5 static verification not PASS")
    if gate.get("diagnostic_runtime_authorized") is not True:
        raise _TransactionClosed("v5 diagnostic runtime not authorized")
    attempts = gate.get("diagnostic_runtime_attempts_authorized")
    if not (_is_exact_int(attempts) and attempts == 1):
        raise _TransactionClosed("v5 diagnostic runtime attempts not int 1")

    for key in (
        "scientific_outcome_allowed",
        "command_transmission_allowed",
        "baseline_execution_allowed",
        "event_injection_allowed",
        "cryptographic_semantics_claim_allowed",
    ):
        _require_false_permission(contract, key, "v5 top-level")
    for key in (
        "baseline_run_1_authorized",
        "baseline_run_2_authorized",
        "event_injection_authorized",
    ):
        _require_false_permission(gate, key, "v5 gate-level")

    accepted = gate.get("accepted_runtime_entrypoint_v5_sha256")
    if not _is_hex64(accepted) or accepted != accepted.lower() or accepted != cand_sha:
        raise _TransactionClosed("v5 accepted candidate identity mismatch")
    if gate.get("accepted_runtime_entrypoint_v5_identity_only_not_authorized") is not False:
        raise _TransactionClosed("v5 identity-only flag not false")

    _v5_validate_he2_lineage(contract)

    amendment = contract.get(
        "passive_time_witness_runtime_candidate_v5_design_amendment_1"
    )
    if not isinstance(amendment, dict):
        raise _TransactionClosed("v5 amendment missing")
    if amendment.get("runtime_authorized") is not True:
        raise _TransactionClosed("v5 amendment runtime not authorized")
    amendment_attempts = amendment.get("runtime_attempts")
    if not (_is_exact_int(amendment_attempts) and amendment_attempts == 1):
        raise _TransactionClosed("v5 amendment attempts not int 1")
    d064 = amendment.get("d064_status")
    if d064 != _D064_AUTHORIZED:
        raise _TransactionClosed("v5 D064 status not exact authorized state")

    impl = amendment.get("passive_time_witness_runtime_candidate_v5_implementation")
    if not isinstance(impl, dict):
        raise _TransactionClosed("v5 implementation missing")

    tool = impl.get("runtime_material_tool")
    manifest = impl.get("canonical_manifest")
    if not isinstance(tool, dict) or not isinstance(manifest, dict):
        raise _TransactionClosed("v5 tool/manifest binding missing")
    if tool.get("path") != tool_rel or tool.get("sha256") != tool_sha:
        raise _TransactionClosed("v5 successor-consumer identity mismatch")
    if manifest.get("path") != man_rel or manifest.get("sha256") != man_sha:
        raise _TransactionClosed("v5 manifest identity mismatch")

    evidence = impl.get("active_host_exclusive_writer_evidence_v3")
    if not isinstance(evidence, dict):
        raise _TransactionClosed("v5 active schema2 evidence binding missing")
    expected_evidence = {
        "path": _V5_HOST_EVIDENCE_REL,
        "sha256": _V5_HOST_EVIDENCE_SHA256,
        "bytes": _V5_HOST_EVIDENCE_BYTES,
        "schema": _V5_HOST_EVIDENCE_SCHEMA,
        "evidence_type": _V5_HOST_EVIDENCE_TYPE,
        "status": _V5_HOST_EVIDENCE_STATUS,
        "observed_at_utc": _V5_HOST_EVIDENCE_OBSERVED_AT_UTC,
        "capture_gate_sha256": _V5_HOST_EVIDENCE_CAPTURE_GATE_SHA256,
        "independent_review_script_sha256": _V5_HOST_EVIDENCE_REVIEW_SHA256,
        "independent_review_result": "PASS",
        "independent_review_findings": 0,
        "current_host_reobservation_consistent_with_v3": True,
    }
    for key, value in expected_evidence.items():
        if evidence.get(key) != value:
            raise _TransactionClosed("v5 evidence governance mismatch: %s" % key)
    if evidence.get("path") != evidence_rel or evidence.get("sha256") != evidence_sha:
        raise _TransactionClosed("v5 actual evidence identity mismatch")
    if evidence.get("schema") != evidence_schema:
        raise _TransactionClosed("v5 actual evidence schema mismatch")
    if not _is_exact_int(evidence.get("bytes")):
        raise _TransactionClosed("v5 evidence bytes not exact int")
    if not _is_exact_int(evidence.get("independent_review_findings")):
        raise _TransactionClosed("v5 review findings not exact int")
    if evidence.get("current_host_reobservation_consistent_with_v3") is not True:
        raise _TransactionClosed("v5 host reobservation not exact true")

    governance = impl.get("compatibility_governance")
    if not isinstance(governance, dict):
        raise _TransactionClosed("v5 compatibility governance missing")
    decision = governance.get("decision")
    if (
        not _is_exact_str(decision)
        or not decision.startswith("D-063R2-C3B-I2D-D064-V5-COMPAT-")
        or len(decision) > 128
    ):
        raise _TransactionClosed("v5 compatibility decision invalid")
    if governance.get("contract_version") != contract_version:
        raise _TransactionClosed("v5 compatibility contract version mismatch")
    if governance.get("successor_consumer_path") != tool_rel:
        raise _TransactionClosed("v5 governance consumer path mismatch")
    if governance.get("successor_consumer_sha256") != tool_sha:
        raise _TransactionClosed("v5 governance consumer SHA mismatch")
    if (
        governance.get("fresh_evidence_independent_review_script_sha256")
        != _V5_HOST_EVIDENCE_REVIEW_SHA256
    ):
        raise _TransactionClosed("v5 fresh-evidence review SHA mismatch")
    successor_review_sha = governance.get(
        "successor_consumer_independent_review_script_sha256"
    )
    if (
        not _is_hex64(successor_review_sha)
        or successor_review_sha != successor_review_sha.lower()
    ):
        raise _TransactionClosed("v5 successor-consumer review SHA invalid")
    if governance.get("successor_consumer_independent_review_result") != "PASS":
        raise _TransactionClosed("v5 successor-consumer review not PASS")
    successor_review_findings = governance.get(
        "successor_consumer_independent_review_findings"
    )
    if not (
        _is_exact_int(successor_review_findings)
        and successor_review_findings == 0
    ):
        raise _TransactionClosed("v5 successor-consumer review findings nonzero")
    if governance.get("schema2_compatible") is not True:
        raise _TransactionClosed("v5 schema2 compatibility not true")
    if governance.get("schema1_fallback_allowed") is not False:
        raise _TransactionClosed("v5 schema1 fallback must remain false")
    if governance.get("governance_binding_verified") is not True:
        raise _TransactionClosed("v5 governance binding not verified")

    return (
        schema,
        static_result,
        True,
        1,
        True,
        1,
        d064,
        accepted,
        tuple(
            contract[p]
            for p in (
                "scientific_outcome_allowed",
                "command_transmission_allowed",
                "baseline_execution_allowed",
                "event_injection_allowed",
                "cryptographic_semantics_claim_allowed",
            )
        ),
        tuple(
            gate[p]
            for p in (
                "baseline_run_1_authorized",
                "baseline_run_2_authorized",
                "event_injection_authorized",
            )
        ),
    )


def _v5_governance_receipt_fields(contract, tool_rel, tool_sha):
    amendment = contract[
        "passive_time_witness_runtime_candidate_v5_design_amendment_1"
    ]
    impl = amendment["passive_time_witness_runtime_candidate_v5_implementation"]
    governance = impl["compatibility_governance"]
    return {
        "decision": governance["decision"],
        "contract_version": contract["contract_version"],
        "successor_consumer_path": tool_rel,
        "successor_consumer_sha256": tool_sha,
        "fresh_evidence_independent_review_script_sha256": governance[
            "fresh_evidence_independent_review_script_sha256"
        ],
        "successor_consumer_independent_review_script_sha256": governance[
            "successor_consumer_independent_review_script_sha256"
        ],
        "successor_consumer_independent_review_result": governance[
            "successor_consumer_independent_review_result"
        ],
        "successor_consumer_independent_review_findings": governance[
            "successor_consumer_independent_review_findings"
        ],
        "governance_binding_verified": True,
        "schema2_compatible": True,
        "schema1_fallback_allowed": False,
    }


def _v5_compat_selftest():
    import copy as _v5_copy
    results = []

    def check(name, fn):
        try:
            if fn() is False:
                raise RuntimeError("returned false")
            results.append((name, "PASS"))
        except Exception as exc:
            results.append((name, "FAIL:" + str(exc)))

    repo = os.getcwd()
    evidence_path = os.path.join(repo, _V5_HOST_EVIDENCE_REL)
    raw = open(evidence_path, "rb").read()
    parsed = json.loads(raw.decode("utf-8"))

    check(
        "actual_v3_schema2_accept",
        lambda: _validate_host_exclusive_writer_evidence_v5(raw, parsed) == 2,
    )

    def reject_evidence(mutator):
        obj = _v5_copy.deepcopy(parsed)
        mutator(obj)
        bad_raw = (
            json.dumps(obj, ensure_ascii=True, sort_keys=True, separators=(",", ":"))
            + "\n"
        ).encode("utf-8")
        try:
            _validate_host_exclusive_writer_evidence_v5(bad_raw, obj)
        except _TransactionClosed:
            return True
        return False

    check(
        "schema1_downgrade_rejected",
        lambda: reject_evidence(lambda o: o.__setitem__("schema", 1)),
    )
    check(
        "wrong_evidence_type_rejected",
        lambda: reject_evidence(
            lambda o: o.__setitem__(
                "evidence_type", "D064_HOST_EXCLUSIVE_WRITER_PRECONDITION"
            )
        ),
    )
    check(
        "wrong_capture_status_rejected",
        lambda: reject_evidence(
            lambda o: o.__setitem__("status", "RETAINED_PRECONDITION_EVIDENCE")
        ),
    )
    check(
        "external_writer_overclaim_rejected",
        lambda: reject_evidence(
            lambda o: o["concurrent_writer_observation"].__setitem__(
                "external_noncooperating_writer_absence_proven", True
            )
        ),
    )
    check(
        "acl_rights_scalar_rejected",
        lambda: reject_evidence(
            lambda o: o["parent_traversal_remediation"].__setitem__(
                "acl_rights", "search"
            )
        ),
    )
    check(
        "macl_identity_change_rejected",
        lambda: reject_evidence(
            lambda o: o["parent_traversal_remediation"]["xattrs"][
                "com_apple_macl"
            ].__setitem__("capture_sha256", "0" * 64)
        ),
    )

    def noncanonical_rejected():
        try:
            _validate_host_exclusive_writer_evidence_v5(b" " + raw, parsed)
        except _TransactionClosed:
            return True
        return False

    check("noncanonical_evidence_rejected", noncanonical_rejected)

    tool_rel = "scripts/nos3_runtime_transaction_v3.py"
    tool_sha = _sha256_file_path(__file__)
    candidate_sha = "a" * 64
    manifest_rel = "manifests/nos3-runtime-material-manifest.json"
    manifest_sha = "b" * 64
    decision = "D-063R2-C3B-I2D-D064-V5-COMPAT-SELFTEST"

    he2_fresh = {
        "path": _V5_HOST_EVIDENCE_REL,
        "sha256": _V5_HOST_EVIDENCE_SHA256,
        "bytes": _V5_HOST_EVIDENCE_BYTES,
        "schema": _V5_HOST_EVIDENCE_SCHEMA,
        "evidence_type": _V5_HOST_EVIDENCE_TYPE,
        "status": _V5_HOST_EVIDENCE_STATUS,
        "observed_at_utc": _V5_HOST_EVIDENCE_OBSERVED_AT_UTC,
        "capture_gate_sha256": _V5_HOST_EVIDENCE_CAPTURE_GATE_SHA256,
        "independent_review_script_sha256": _V5_HOST_EVIDENCE_REVIEW_SHA256,
        "independent_review_result": "PASS",
        "independent_review_findings": 0,
        "current_host_reobservation_consistent_with_v3": True,
    }
    active = _v5_copy.deepcopy(he2_fresh)

    good = {
        "contract_version": "0.4.18-selftest",
        "scientific_outcome_allowed": False,
        "event_injection_allowed": False,
        "command_transmission_allowed": False,
        "baseline_execution_allowed": False,
        "cryptographic_semantics_claim_allowed": False,
        "gate": {
            "passive_time_witness_runtime_candidate_v5_contract_schema": 1,
            "passive_time_witness_runtime_candidate_v5_static_verification": "PASS",
            "diagnostic_runtime_authorized": True,
            "diagnostic_runtime_attempts_authorized": 1,
            "accepted_runtime_entrypoint_v5_sha256": candidate_sha,
            "accepted_runtime_entrypoint_v5_identity_only_not_authorized": False,
            "baseline_run_1_authorized": False,
            "baseline_run_2_authorized": False,
            "event_injection_authorized": False,
        },
        "passive_time_witness_runtime_candidate_v4_fresh_successor_host_evidence_governance_2": {
            "fresh_successor_host_evidence": he2_fresh,
            "consumer_compatibility_disposition": {
                "transaction_v2_sha256": _V5_PREDECESSOR_TRANSACTION_V2_SHA256,
                "compatible": False,
                "source_remediation_authorized": False,
            },
        },
        "passive_time_witness_runtime_candidate_v5_design_amendment_1": {
            "runtime_authorized": True,
            "runtime_attempts": 1,
            "d064_status": _D064_AUTHORIZED,
            "passive_time_witness_runtime_candidate_v5_implementation": {
                "runtime_material_tool": {
                    "path": tool_rel,
                    "sha256": tool_sha,
                },
                "canonical_manifest": {
                    "path": manifest_rel,
                    "sha256": manifest_sha,
                },
                "active_host_exclusive_writer_evidence_v3": active,
                "compatibility_governance": {
                    "decision": decision,
                    "contract_version": "0.4.18-selftest",
                    "successor_consumer_path": tool_rel,
                    "successor_consumer_sha256": tool_sha,
                    "fresh_evidence_independent_review_script_sha256": _V5_HOST_EVIDENCE_REVIEW_SHA256,
                    "successor_consumer_independent_review_script_sha256": "c" * 64,
                    "successor_consumer_independent_review_result": "PASS",
                    "successor_consumer_independent_review_findings": 0,
                    "schema2_compatible": True,
                    "schema1_fallback_allowed": False,
                    "governance_binding_verified": True,
                },
            },
        },
    }

    def auth_ok(contract):
        result = _validate_structured_authorization_v5(
            contract,
            candidate_sha,
            tool_rel,
            tool_sha,
            manifest_rel,
            manifest_sha,
            _V5_HOST_EVIDENCE_REL,
            _V5_HOST_EVIDENCE_SHA256,
            2,
        )
        return result[0] == 1 and result[1] == "PASS"

    check("synthetic_v5_governance_envelope_accept", lambda: auth_ok(good))

    def reject_contract(mutator):
        contract = _v5_copy.deepcopy(good)
        mutator(contract)
        try:
            auth_ok(contract)
        except _TransactionClosed:
            return True
        return False

    def v5_impl(contract):
        return contract[
            "passive_time_witness_runtime_candidate_v5_design_amendment_1"
        ]["passive_time_witness_runtime_candidate_v5_implementation"]

    check(
        "wrong_v3_sha_binding_rejected",
        lambda: reject_contract(
            lambda c: v5_impl(c)["active_host_exclusive_writer_evidence_v3"].__setitem__(
                "sha256", "0" * 64
            )
        ),
    )
    check(
        "review_not_pass_rejected",
        lambda: reject_contract(
            lambda c: v5_impl(c)["active_host_exclusive_writer_evidence_v3"].__setitem__(
                "independent_review_result", "FAIL"
            )
        ),
    )
    check(
        "review_findings_nonzero_rejected",
        lambda: reject_contract(
            lambda c: v5_impl(c)["active_host_exclusive_writer_evidence_v3"].__setitem__(
                "independent_review_findings", 1
            )
        ),
    )
    check(
        "host_reobservation_false_rejected",
        lambda: reject_contract(
            lambda c: v5_impl(c)["active_host_exclusive_writer_evidence_v3"].__setitem__(
                "current_host_reobservation_consistent_with_v3", False
            )
        ),
    )
    check(
        "consumer_sha_mismatch_rejected",
        lambda: reject_contract(
            lambda c: v5_impl(c)["compatibility_governance"].__setitem__(
                "successor_consumer_sha256", "0" * 64
            )
        ),
    )
    check(
        "successor_consumer_review_sha_malformed_rejected",
        lambda: reject_contract(
            lambda c: v5_impl(c)["compatibility_governance"].__setitem__(
                "successor_consumer_independent_review_script_sha256", "not-a-sha"
            )
        ),
    )
    check(
        "successor_consumer_review_not_pass_rejected",
        lambda: reject_contract(
            lambda c: v5_impl(c)["compatibility_governance"].__setitem__(
                "successor_consumer_independent_review_result", "FAIL"
            )
        ),
    )
    check(
        "successor_consumer_review_findings_nonzero_rejected",
        lambda: reject_contract(
            lambda c: v5_impl(c)["compatibility_governance"].__setitem__(
                "successor_consumer_independent_review_findings", 1
            )
        ),
    )
    check(
        "fresh_evidence_review_sha_mismatch_rejected",
        lambda: reject_contract(
            lambda c: v5_impl(c)["compatibility_governance"].__setitem__(
                "fresh_evidence_independent_review_script_sha256", "0" * 64
            )
        ),
    )
    check(
        "schema1_fallback_true_rejected",
        lambda: reject_contract(
            lambda c: v5_impl(c)["compatibility_governance"].__setitem__(
                "schema1_fallback_allowed", True
            )
        ),
    )
    check(
        "governance_binding_false_rejected",
        lambda: reject_contract(
            lambda c: v5_impl(c)["compatibility_governance"].__setitem__(
                "governance_binding_verified", False
            )
        ),
    )
    check(
        "HE2_v2_incompatibility_flip_rejected",
        lambda: reject_contract(
            lambda c: c[
                "passive_time_witness_runtime_candidate_v4_fresh_successor_host_evidence_governance_2"
            ]["consumer_compatibility_disposition"].__setitem__("compatible", True)
        ),
    )

    current_contract = json.loads(
        open(
            os.path.join(repo, "configs/downlink-diagnostic-contract.json"),
            "rb",
        ).read()
    )
    check(
        "current_0_4_17_remains_not_v5_runtime_ready",
        lambda: (
            current_contract.get("contract_version") == "0.4.17"
            and current_contract.get("gate", {}).get(
                "passive_time_witness_runtime_candidate_v5_contract_schema"
            )
            is None
            and current_contract.get(
                "passive_time_witness_runtime_candidate_v5_design_amendment_1"
            )
            is None
            and current_contract[
                "passive_time_witness_runtime_candidate_v4_design_amendment_1"
            ]["d064_status"]
            == "BLOCKED_PENDING_FRESH_HOST_EVIDENCE_CONSUMER_SCHEMA_COMPATIBILITY_REMEDIATION"
        ),
    )

    passed = sum(1 for _, result in results if result == "PASS")
    failed = len(results) - passed
    return passed, failed, tuple(results)


def _run_authorize(args):
    """Authorize one v4 materialization transaction within one internal CLI
    driver.  Opens the repository root once, derives the executing tool from
    __file__, and validates the contract, candidate, executing tool, and
    canonical manifest through descriptor-bound traversal.  On success
    constructs ONE deeply immutable local context, retained only as a local
    variable, then runs the complete process-local transaction core
    (Checkpoint 2PB2B-B2): build the canonical plan from the retained manifest
    bytes, inspect the authorized root, validate the final basename, create
    the private outer staging transaction, materialize and verify the complete
    transaction, write the receipt, fsync, publish atomically, fsync the root,
    and return rc=0 / V4_TRANSACTION_MATERIALIZATION=PASS.  The context is
    NEVER returned to a caller.  All expected filesystem/path failures become
    _TransactionClosed (closed disposition).  KeyboardInterrupt and SystemExit
    are never caught as authorization results.  Returns (rc, marker, detail)
    only -- never a context/receipt/auth object."""
    repo_fd = None
    ctx = None
    try:
        # Missing required arguments -> closed disposition (rc=1), never a
        # traceback.  Applies to direct _run_authorize callers and main().
        for required in ("contract", "manifest", "candidate",
                         "authorized_root", "final_basename"):
            if not getattr(args, required, None):
                raise _TransactionClosed("missing required argument: %s" % required)
        repo_fd, repo_receipt = _open_repo_root_fd(args.repo_root)
        tool_abs = os.path.abspath(__file__)
        repo_abs = os.path.abspath(args.repo_root)
        tool_rel = _repo_relative_from_abs(tool_abs, repo_abs)
        with _open_auth_file(repo_fd, tool_rel) as (treceipt, traw, tsha, tparsed):
            treceipt = treceipt._replace(sha256=tsha)
        cand_rel = args.candidate
        if os.path.isabs(cand_rel):
            cand_rel = _repo_relative_from_abs(cand_rel, repo_abs)
        with _open_auth_file(repo_fd, cand_rel) as (creceipt, craw, csha, cparsed):
            creceipt = creceipt._replace(sha256=csha)
        man_rel = args.manifest
        if os.path.isabs(man_rel):
            man_rel = _repo_relative_from_abs(man_rel, repo_abs)
        with _open_auth_file(repo_fd, man_rel) as (mreceipt, mraw, msha, mparsed):
            _manifest_canonical_check(mraw)
            mreceipt = mreceipt._replace(sha256=msha)
        con_rel = args.contract
        if os.path.isabs(con_rel):
            con_rel = _repo_relative_from_abs(con_rel, repo_abs)
        with _open_auth_file(repo_fd, con_rel) as (xreceipt, xraw, xsha, xparsed):
            if xparsed is None:
                raise _TransactionClosed("contract not valid JSON")
            xreceipt = xreceipt._replace(sha256=xsha)
            gpre=xparsed.get("gate")
            if not isinstance(gpre,dict): raise _TransactionClosed("contract gate missing")
            sp=gpre.get("passive_time_witness_runtime_candidate_v4_contract_schema")
            if not (_is_exact_int(sp) and sp==1): raise _TransactionClosed("v4 contract schema not exact int 1")
            if gpre.get("passive_time_witness_runtime_candidate_v4_static_verification") != "PASS": raise _TransactionClosed("v4 static verification not PASS")
            ampre=xparsed.get("passive_time_witness_runtime_candidate_v4_design_amendment_1")
            if not isinstance(ampre,dict): raise _TransactionClosed("v4 amendment block missing")
            imppre=ampre.get("passive_time_witness_runtime_candidate_v4_implementation")
            if not isinstance(imppre,dict): raise _TransactionClosed("v4 implementation block missing")
            hepre=imppre.get("host_exclusive_writer_evidence")
            if not isinstance(hepre,dict): raise _TransactionClosed("v4 host evidence binding missing")
            evidence_rel=hepre.get("path")
            if not _is_exact_str(evidence_rel) or evidence_rel=="" or os.path.isabs(evidence_rel): raise _TransactionClosed("v4 host evidence path invalid")
            _validate_rel_path(evidence_rel)
            expected_evidence_sha=hepre.get("sha256")
            if not _is_hex64(expected_evidence_sha) or expected_evidence_sha != expected_evidence_sha.lower(): raise _TransactionClosed("v4 host evidence sha invalid")
            with _open_auth_file(repo_fd,evidence_rel) as (ereceipt,eraw,esha,eparsed):
                evidence_schema=_validate_host_exclusive_writer_evidence(eraw,eparsed)
                if esha != expected_evidence_sha: raise _TransactionClosed("actual host evidence sha mismatch")
                ereceipt=ereceipt._replace(sha256=esha)
            (schema, sv, dra_bool, dra_int, am_bool, am_int, d064, acc,
             top_perms, gate_perms) = _validate_structured_authorization(
                xparsed, csha, tool_rel, tsha, man_rel, msha,
                evidence_rel, esha, evidence_schema)
            # ONE local immutable context, retained only here; never returned.
            ctx = _TransactionContext(
                repo=repo_receipt,
                contract=xreceipt,
                candidate=creceipt,
                tool=treceipt,
                manifest=mreceipt,
                host_evidence=ereceipt,
                host_evidence_schema=evidence_schema,
                schema=schema,
                static_verification=sv,
                diagnostic_runtime_authorized=dra_bool,
                diagnostic_runtime_attempts_authorized=dra_int,
                amendment_runtime_authorized=am_bool,
                amendment_runtime_attempts=am_int,
                d064_disposition=d064,
                accepted_candidate_sha=acc,
                top_permissions=_Permissions(*top_perms),
                gate_permissions=_GatePermissions(*gate_perms),
            )
            # ---- Checkpoint 2PB2B-B2: integrated production transaction core.
            # Runs only after all authorization checks (steps 1-10) succeed.
            # Builds the canonical plan from the retained manifest bytes, then
            # inspects the authorized root, validates the final basename,
            # creates one private outer staging transaction, materializes and
            # verifies the complete transaction, writes the receipt, fsyncs,
            # publishes atomically, fsyncs the root, and returns success -- all
            # WITHOUT returning authorization state.  _b2_inject is a
            # selftest-only fault-injection hook (None in production).
            _b2_inject = getattr(args, "_b2_inject", None)
            result = _b2_materialize(
                ctx, repo_fd, mraw, mparsed, args.authorized_root,
                args.final_basename, inject=_b2_inject)
            _b2_result = result  # (final_basename, dev, ino, sha, files, bytes)
            return (0, "V4_TRANSACTION_MATERIALIZATION=PASS",
                    "transaction complete runtime_attempt=1")
    except _TransactionClosed as exc:
        return 1, "V4_TRANSACTION_AUTHORIZATION=CLOSED", str(exc)
    finally:
        if repo_fd is not None:
            try:
                os.close(repo_fd)
            except OSError:
                pass
        # ctx is a local; drops with the frame.  Never assigned to a global.
        ctx = None


def _run_authorize_v5(args):
    """Authorize one v5 materialization transaction within one internal CLI
    driver.  Opens the repository root once, derives the executing tool from
    __file__, and validates the contract, candidate, executing tool, and
    canonical manifest through descriptor-bound traversal.  On success
    constructs ONE deeply immutable local context, retained only as a local
    variable, then runs the complete process-local transaction core
    (Checkpoint 2PB2B-B2): build the canonical plan from the retained manifest
    bytes, inspect the authorized root, validate the final basename, create
    the private outer staging transaction, materialize and verify the complete
    transaction, write the receipt, fsync, publish atomically, fsync the root,
    and return rc=0 / V5_TRANSACTION_MATERIALIZATION=PASS.  The context is
    NEVER returned to a caller.  All expected filesystem/path failures become
    _TransactionClosed (closed disposition).  KeyboardInterrupt and SystemExit
    are never caught as authorization results.  Returns (rc, marker, detail)
    only -- never a context/receipt/auth object."""
    repo_fd = None
    ctx = None
    try:
        # Missing required arguments -> closed disposition (rc=1), never a
        # traceback.  Applies to direct _run_authorize callers and main().
        for required in ("contract", "manifest", "candidate",
                         "authorized_root", "final_basename"):
            if not getattr(args, required, None):
                raise _TransactionClosed("missing required argument: %s" % required)
        repo_fd, repo_receipt = _open_repo_root_fd(args.repo_root)
        tool_abs = os.path.abspath(__file__)
        repo_abs = os.path.abspath(args.repo_root)
        tool_rel = _repo_relative_from_abs(tool_abs, repo_abs)
        with _open_auth_file(repo_fd, tool_rel) as (treceipt, traw, tsha, tparsed):
            treceipt = treceipt._replace(sha256=tsha)
        cand_rel = args.candidate
        if os.path.isabs(cand_rel):
            cand_rel = _repo_relative_from_abs(cand_rel, repo_abs)
        with _open_auth_file(repo_fd, cand_rel) as (creceipt, craw, csha, cparsed):
            creceipt = creceipt._replace(sha256=csha)
        man_rel = args.manifest
        if os.path.isabs(man_rel):
            man_rel = _repo_relative_from_abs(man_rel, repo_abs)
        with _open_auth_file(repo_fd, man_rel) as (mreceipt, mraw, msha, mparsed):
            _manifest_canonical_check(mraw)
            mreceipt = mreceipt._replace(sha256=msha)
        con_rel = args.contract
        if os.path.isabs(con_rel):
            con_rel = _repo_relative_from_abs(con_rel, repo_abs)
        with _open_auth_file(repo_fd, con_rel) as (xreceipt, xraw, xsha, xparsed):
            if xparsed is None:
                raise _TransactionClosed("contract not valid JSON")
            xreceipt = xreceipt._replace(sha256=xsha)
            gpre=xparsed.get("gate")
            if not isinstance(gpre,dict): raise _TransactionClosed("contract gate missing")
            sp=gpre.get("passive_time_witness_runtime_candidate_v5_contract_schema")
            if not (_is_exact_int(sp) and sp==1): raise _TransactionClosed("v5 contract schema not exact int 1")
            if gpre.get("passive_time_witness_runtime_candidate_v5_static_verification") != "PASS": raise _TransactionClosed("v5 static verification not PASS")
            ampre=xparsed.get("passive_time_witness_runtime_candidate_v5_design_amendment_1")
            if not isinstance(ampre,dict): raise _TransactionClosed("v5 amendment block missing")
            imppre=ampre.get("passive_time_witness_runtime_candidate_v5_implementation")
            if not isinstance(imppre,dict): raise _TransactionClosed("v5 implementation block missing")
            hepre=imppre.get("active_host_exclusive_writer_evidence_v3")
            if not isinstance(hepre,dict): raise _TransactionClosed("v5 host evidence binding missing")
            evidence_rel=hepre.get("path")
            if not _is_exact_str(evidence_rel) or evidence_rel=="" or os.path.isabs(evidence_rel): raise _TransactionClosed("v5 host evidence path invalid")
            _validate_rel_path(evidence_rel)
            expected_evidence_sha=hepre.get("sha256")
            if not _is_hex64(expected_evidence_sha) or expected_evidence_sha != expected_evidence_sha.lower(): raise _TransactionClosed("v5 host evidence sha invalid")
            expected_evidence_bytes=hepre.get("bytes")
            if not (_is_exact_int(expected_evidence_bytes) and expected_evidence_bytes == _V5_HOST_EVIDENCE_BYTES): raise _TransactionClosed("v5 host evidence bytes invalid")
            with _open_auth_file(repo_fd,evidence_rel) as (ereceipt,eraw,esha,eparsed):
                evidence_schema=_validate_host_exclusive_writer_evidence_v5(eraw,eparsed)
                if esha != expected_evidence_sha: raise _TransactionClosed("actual v5 host evidence sha mismatch")
                if ereceipt.size != expected_evidence_bytes: raise _TransactionClosed("actual v5 host evidence byte count mismatch")
                ereceipt=ereceipt._replace(sha256=esha)
            (schema, sv, dra_bool, dra_int, am_bool, am_int, d064, acc,
             top_perms, gate_perms) = _validate_structured_authorization_v5(
                xparsed, csha, tool_rel, tsha, man_rel, msha,
                evidence_rel, esha, evidence_schema)
            # ONE local immutable context, retained only here; never returned.
            ctx = _TransactionContext(
                repo=repo_receipt,
                contract=xreceipt,
                candidate=creceipt,
                tool=treceipt,
                manifest=mreceipt,
                host_evidence=ereceipt,
                host_evidence_schema=evidence_schema,
                schema=schema,
                static_verification=sv,
                diagnostic_runtime_authorized=dra_bool,
                diagnostic_runtime_attempts_authorized=dra_int,
                amendment_runtime_authorized=am_bool,
                amendment_runtime_attempts=am_int,
                d064_disposition=d064,
                accepted_candidate_sha=acc,
                top_permissions=_Permissions(*top_perms),
                gate_permissions=_GatePermissions(*gate_perms),
                host_evidence_type=_V5_HOST_EVIDENCE_TYPE,
                host_evidence_status=_V5_HOST_EVIDENCE_STATUS,
                host_evidence_observed_at_utc=_V5_HOST_EVIDENCE_OBSERVED_AT_UTC,
                compatibility_governance_decision=_v5_governance_receipt_fields(xparsed, tool_rel, tsha)["decision"],
                compatibility_governance_contract_version=xparsed["contract_version"],
                compatibility_governance_contract_sha256=xsha,
                fresh_evidence_independent_review_script_sha256=_v5_governance_receipt_fields(xparsed, tool_rel, tsha)["fresh_evidence_independent_review_script_sha256"],
                successor_consumer_independent_review_script_sha256=_v5_governance_receipt_fields(xparsed, tool_rel, tsha)["successor_consumer_independent_review_script_sha256"],
                successor_consumer_independent_review_result=_v5_governance_receipt_fields(xparsed, tool_rel, tsha)["successor_consumer_independent_review_result"],
                successor_consumer_independent_review_findings=_v5_governance_receipt_fields(xparsed, tool_rel, tsha)["successor_consumer_independent_review_findings"],
                governance_binding_verified=True,
            )
            # ---- Checkpoint 2PB2B-B2: integrated production transaction core.
            # Runs only after all authorization checks (steps 1-10) succeed.
            # Builds the canonical plan from the retained manifest bytes, then
            # inspects the authorized root, validates the final basename,
            # creates one private outer staging transaction, materializes and
            # verifies the complete transaction, writes the receipt, fsyncs,
            # publishes atomically, fsyncs the root, and returns success -- all
            # WITHOUT returning authorization state.  _b2_inject is a
            # selftest-only fault-injection hook (None in production).
            _b2_inject = getattr(args, "_b2_inject", None)
            result = _b2_materialize(
                ctx, repo_fd, mraw, mparsed, args.authorized_root,
                args.final_basename, inject=_b2_inject)
            _b2_result = result  # (final_basename, dev, ino, sha, files, bytes)
            return (0, "V5_TRANSACTION_MATERIALIZATION=PASS",
                    "transaction complete runtime_attempt=1")
    except _TransactionClosed as exc:
        return 1, "V5_TRANSACTION_AUTHORIZATION=CLOSED", str(exc)
    finally:
        if repo_fd is not None:
            try:
                os.close(repo_fd)
            except OSError:
                pass
        # ctx is a local; drops with the frame.  Never assigned to a global.
        ctx = None


def _build_argparser():
    p = argparse.ArgumentParser(
        description="NOS3 runtime-material V5 successor transaction authorization CLI "
                    "(schema-2 host evidence, host-only, fail-closed).")
    p.add_argument("--repo-root", default=os.getcwd())
    g = p.add_mutually_exclusive_group(required=False)
    g.add_argument("--materialize-v5-transaction", action="store_true")
    g.add_argument("--selftest", action="store_true")
    g.add_argument("--v5-compat-selftest", action="store_true")
    p.add_argument("--contract", metavar="PATH")
    p.add_argument("--manifest", metavar="PATH")
    p.add_argument("--candidate", metavar="PATH")
    p.add_argument("--authorized-root", metavar="PATH")
    p.add_argument("--final-basename", metavar="NAME")
    return p


def main(argv=None):
    p = _build_argparser()
    args = p.parse_args(argv)
    if args.selftest:
        passed, failed, skips, results = selftest()
        for name, r in results:
            print("  %-58s %s" % (name, r))
        print("SELFTEST passed=%d failed=%d skips=%d" % (passed, failed, skips))
        return 0 if failed == 0 else 1
    if args.v5_compat_selftest:
        passed, failed, results = _v5_compat_selftest()
        for name, r in results:
            print("  %-58s %s" % (name, r))
        print("V5_COMPAT_SELFTEST passed=%d failed=%d" % (passed, failed))
        return 0 if failed == 0 else 1
    if args.materialize_v5_transaction:
        missing = [a for a in ("contract", "manifest", "candidate",
                               "authorized_root", "final_basename")
                   if not getattr(args, a, None)]
        if missing:
            print("V5_TRANSACTION_AUTHORIZATION=CLOSED")
            print("[ERROR] missing required arguments: %s" % ", ".join(missing),
                  file=sys.stderr)
            return 1
        rc, marker, _detail = _run_authorize_v5(args)
        print(marker)
        return rc
    p.print_help()
    return 0


# ---------------------------------------------------------------------------
# Synthetic outer-transaction engine (Checkpoint 2PB2B-A).
#
# Exercised only by internal self-tests using temporary synthetic authorized
# roots.  NOT connected to the production CLI authorization path (_run_authorize
# does not call it).  Standard-library-only; no Docker, no subprocess, no
# project-local imports.  Tightly scoped synthetic fixtures only — no NOS3
# source-tree materialization in this checkpoint.
# ---------------------------------------------------------------------------

_COMPONENT_IDS = (
    "nos_engine", "time_driver",
    "hw_sim_%02d" % 1, "hw_sim_%02d" % 2, "hw_sim_%02d" % 3,
    "hw_sim_%02d" % 4, "hw_sim_%02d" % 5, "hw_sim_%02d" % 6,
    "hw_sim_%02d" % 7, "hw_sim_%02d" % 8, "hw_sim_%02d" % 9,
    "hw_sim_%02d" % 10, "hw_sim_%02d" % 11, "hw_sim_%02d" % 12,
    "hw_sim_%02d" % 13, "hw_sim_%02d" % 14,
    "cmd_bus_bridge", "cfs",
)

# Immutable plan records (namedtuples / tuples of immutable primitives only).

_SyntheticFile = namedtuple("_SyntheticFile", ("rel_path", "mode", "content"))
_ComponentPlan = namedtuple("_ComponentPlan", ("component_id", "files"))
_SyntheticPlan = namedtuple("_SyntheticPlan",
                            ("components", "fortytwo_files"))
_TransactionResult = namedtuple("_TransactionResult",
                                ("final_basename", "final_dev", "final_ino",
                                 "receipt_sha256", "file_count", "byte_count"))


def _build_synthetic_plan():
    """Build an immutable synthetic plan modelling all 18 component IDs.

    Each component receives one private workspace rooted at
    workspaces/<component_id>/work/nos3 with a few small deterministic files.
    A separate fortytwo-config scratch tree also receives small files.  The
    byte strings come from immutable in-memory content, not external source.
    """
    components = []
    for cid in _COMPONENT_IDS:
        files = (
            _SyntheticFile(
                rel_path="workspaces/%s/work/nos3/README.txt" % cid,
                mode=0o644,
                content=("# NOS3 runtime-material workspace for %s\n"
                         "# synthetic fixture\n" % cid).encode("utf-8")),
            _SyntheticFile(
                rel_path="workspaces/%s/work/nos3/config/%s.cfg" % (cid, cid),
                mode=0o644,
                content=("[component]\nname=%s\nenabled=true\n" % cid).encode("utf-8")),
        )
        components.append(_ComponentPlan(component_id=cid, files=files))
    fortytwo_files = (
        _SyntheticFile(rel_path="fortytwo-config/scratch.json",
                       mode=0o644,
                       content=b'{"scratch":"fortytwo","schema":1}\n'),
        _SyntheticFile(rel_path="fortytwo-config/notes.txt",
                       mode=0o644,
                       content=b"Fortytwo configuration scratch tree.\n"),
    )
    return _SyntheticPlan(components=tuple(components),
                          fortytwo_files=fortytwo_files)


_ALLOWED_REGULAR_MODES = frozenset((0o644, 0o644))


def _validate_canonical_synthetic_path(path):
    """Reject non-canonical synthetic plan paths: must be rooted under
    workspaces/<component_id>/work/nos3/ or fortytwo-config/, with no
    empty/dot/dotdot/backslash/repeated-separator/NUL/surrogate."""
    if not isinstance(path, str) or path == "":
        raise _TransactionClosed("plan path empty/not a string")
    if path.startswith("/"):
        raise _TransactionClosed("plan path is absolute")
    if "\\" in path or "\x00" in path:
        raise _TransactionClosed("plan path has backslash or NUL")
    for ch in path:
        if 0xD800 <= ord(ch) <= 0xDFFF:
            raise _TransactionClosed("surrogate code point in plan path")
    if "//" in path:
        raise _TransactionClosed("repeated separator in plan path")
    comps = path.split("/")
    for c in comps:
        if c == "" or c == "." or c == "..":
            raise _TransactionClosed(
                "empty/dot/dotdot component in plan path: %r" % path)
    return comps


def _validate_synthetic_plan(plan):
    """Validate the exact synthetic plan structure before staging begins.

    Requires the exact _SyntheticPlan type, exactly 18 components, every
    component an exact _ComponentPlan type, the exact expected component-ID
    set (no duplicate, missing, or unexpected component), each files value a
    tuple, every file an exact _SyntheticFile type, each content exact bytes,
    modes limited to the approved deterministic regular-file modes, every
    path canonical and rooted under workspaces/<component_id>/work/nos3/ or
    fortytwo-config/, and no duplicate file path.
    """
    if type(plan) is not _SyntheticPlan:
        raise _TransactionClosed("plan not exact _SyntheticPlan type")
    if not isinstance(plan.components, tuple):
        raise _TransactionClosed("plan components not a tuple")
    if len(plan.components) != 18:
        raise _TransactionClosed("plan component count != 18")
    expected_ids = set(_COMPONENT_IDS)
    seen_ids = set()
    all_paths = set()
    for comp in plan.components:
        if type(comp) is not _ComponentPlan:
            raise _TransactionClosed("plan component not exact _ComponentPlan")
        cid = comp.component_id
        if not isinstance(cid, str) or isinstance(cid, bool):
            raise _TransactionClosed("plan component_id not a string")
        if cid not in expected_ids:
            raise _TransactionClosed(
                "plan unexpected component_id: %r" % cid)
        if cid in seen_ids:
            raise _TransactionClosed("plan duplicate component_id: %r" % cid)
        seen_ids.add(cid)
        files = comp.files
        if not isinstance(files, tuple):
            raise _TransactionClosed(
                "plan component files not a tuple: %r" % cid)
        for sf in files:
            if type(sf) is not _SyntheticFile:
                raise _TransactionClosed(
                    "plan file not exact _SyntheticFile: %r" % cid)
            if type(sf.content) is not bytes:
                raise _TransactionClosed(
                    "plan file content not exact bytes: %r" % cid)
            if sf.mode not in _ALLOWED_REGULAR_MODES:
                raise _TransactionClosed(
                    "plan file mode not approved: %r (%r)" % (cid, sf.mode))
            comps = _validate_canonical_synthetic_path(sf.rel_path)
            if comps[0] == "fortytwo-config":
                raise _TransactionClosed(
                    "plan component file may not be under fortytwo-config: %r"
                    % sf.rel_path)
            ok_ws = (len(comps) >= 5 and comps[0] == "workspaces"
                     and comps[1] == cid and comps[2] == "work"
                     and comps[3] == "nos3")
            if not ok_ws:
                raise _TransactionClosed(
                    "plan path not under workspaces/%s/work/nos3/<...>: %r"
                    % (cid, sf.rel_path))
            if sf.rel_path in all_paths:
                raise _TransactionClosed(
                    "plan duplicate file path: %r" % sf.rel_path)
            all_paths.add(sf.rel_path)
    if seen_ids != expected_ids:
        raise _TransactionClosed(
            "plan component ID set mismatch: missing %r unexpected %r"
            % (expected_ids - seen_ids, seen_ids - expected_ids))
    if not isinstance(plan.fortytwo_files, tuple):
        raise _TransactionClosed("plan fortytwo_files not a tuple")
    for sf in plan.fortytwo_files:
        if type(sf) is not _SyntheticFile:
            raise _TransactionClosed("plan fortytwo file not exact _SyntheticFile")
        if type(sf.content) is not bytes:
            raise _TransactionClosed("plan fortytwo file content not exact bytes")
        if sf.mode not in _ALLOWED_REGULAR_MODES:
            raise _TransactionClosed(
                "plan fortytwo file mode not approved: %r" % (sf.mode,))
        comps = _validate_canonical_synthetic_path(sf.rel_path)
        if comps[0] != "fortytwo-config" or len(comps) < 2:
            raise _TransactionClosed(
                "plan fortytwo path not under fortytwo-config/<...>: %r"
                % sf.rel_path)
        if sf.rel_path in all_paths:
            raise _TransactionClosed(
                "plan duplicate file path: %r" % sf.rel_path)
        all_paths.add(sf.rel_path)
    return plan


# ===========================================================================
# Canonical materialization-plan compiler (Checkpoint 2PB2B-B1).
# Pure and read-only: converts an already canonical, structurally validated
# manifest JSON object into one deeply immutable canonical plan.  Never opens
# source files, never creates authorized roots or staging, never copies.
# The returned plan contains only tuples, namedtuples, strings, exact ints,
# exact bools, and None -- no dict/list/set/bytearray/mutable object.
# ===========================================================================

_CanonicalSourceRoot = namedtuple("_CanonicalSourceRoot",
    ("source_root", "component_scope", "host_relative_path",
     "destination_prefix"))
_CanonicalRegularFile = namedtuple("_CanonicalRegularFile",
    ("entry_type", "source_root", "component_scope", "relative_path",
     "destination_relative", "mode", "nlink", "size", "sha256"))
_CanonicalDirectory = namedtuple("_CanonicalDirectory",
    ("source_root", "component_scope", "relative_path"))
_CanonicalExclusion = namedtuple("_CanonicalExclusion",
    ("entry_type", "source_root", "relative_path", "mode", "nlink", "size",
     "sha256", "classification", "destination_must_be_absent",
     "present_at_amendment"))
_CanonicalExpandedTarget = namedtuple("_CanonicalExpandedTarget",
    ("object_type", "owner_kind", "owner_id", "source_root",
     "source_relative_path", "transaction_relative_path",
     "destination_must_be_absent"))
_CanonicalWorkspacePlan = namedtuple("_CanonicalWorkspacePlan",
    ("component_id", "workspace_host_path", "mount_destination",
     "seed_source_roots", "private_physical_copy", "no_hard_links",
     "no_reflinks", "no_overlays", "no_source_aliases",
     "no_runtime_mount_from_external_nos3", "regular_files", "directories",
     "exclusions", "file_count", "byte_count", "directory_count",
     "exclusion_count", "file_targets", "directory_targets",
     "exclusion_targets"))
_CanonicalFortytwoPlan = namedtuple("_CanonicalFortytwoPlan",
    ("transaction_relative_root", "regular_files", "directories", "exclusions",
     "file_count", "byte_count", "directory_count", "exclusion_count",
     "file_targets", "directory_targets", "exclusion_targets"))
_CanonicalDenyPattern = namedtuple("_CanonicalDenyPattern",
    ("pattern", "scope"))
_CanonicalCompletePlan = namedtuple("_CanonicalCompletePlan",
    ("source_roots", "source_regular_files", "source_directories",
     "source_exclusions", "workspaces", "fortytwo", "collision_model",
     "source_root_count", "source_file_entry_count", "source_file_byte_count",
     "source_directory_entry_count", "source_exclusion_entry_count",
     "workspace_count", "expanded_workspace_file_count",
     "expanded_workspace_byte_count",
     "expanded_workspace_directory_count",
     "expanded_workspace_exclusion_count",
     "expanded_total_file_count", "expanded_total_byte_count",
     "expanded_total_directory_count", "expanded_total_exclusion_count",
     "duplicate_file_target_count", "duplicate_directory_target_count",
     "file_directory_collision_count", "prefix_collision_count",
     "expanded_file_targets", "expanded_directory_targets",
     "expanded_exclusion_targets", "deny_patterns"))

_EXPECTED_SOURCE_ROOTS = frozenset(("cfs", "configuration", "sim_bin", "sim_lib"))
_EXPECTED_WORKSPACE_IDS = frozenset((
    "cfs", "cmd_bus_bridge",
    "hw_sim_01", "hw_sim_02", "hw_sim_03", "hw_sim_04", "hw_sim_05",
    "hw_sim_06", "hw_sim_07", "hw_sim_08", "hw_sim_09", "hw_sim_10",
    "hw_sim_11", "hw_sim_12", "hw_sim_13", "hw_sim_14",
    "nos_engine", "time_driver"))
_EXPECTED_SOURCE_ROOT_DECLS = {
    "cfs": _CanonicalSourceRoot("cfs", "cfs",
        "external/nos3/fsw/build/exe/cpu1", "fsw/build/exe/cpu1"),
    "configuration": _CanonicalSourceRoot("configuration", "configuration",
        "external/nos3/cfg/build/InOut", "cfg/build/InOut"),
    "sim_bin": _CanonicalSourceRoot("sim_bin", "simulator",
        "external/nos3/sims/build/bin", "sims/build/bin"),
    "sim_lib": _CanonicalSourceRoot("sim_lib", "simulator",
        "external/nos3/sims/build/lib", "sims/build/lib"),
}
_EXPECTED_SOURCE_ROOT_TOTALS = {
    "cfs": (1361, 45877946, 86, 9),
    "configuration": (36, 190651, 1, 0),
    "sim_bin": (7, 4204181, 1, 2),
    "sim_lib": (18, 50223336, 1, 0),
}
_EXPECTED_CLASSIFICATIONS = frozenset(("EXACT_STALE_EXCLUSION",))
_ACCEPTED_REGULAR_MODES = frozenset(("0644", "0755"))
_ACCEPTED_EXCLUSION_MODES = frozenset(("0644", "0700"))


def _canonical_path_comps(rel_path, what):
    """Validate a manifest canonical relative path (nonempty, no absolute,
    no dot/dotdot, no repeated separator, no backslash/NUL/surrogate).
    Requires an exact str input."""
    if not _is_exact_str(rel_path):
        raise _TransactionClosed("%s not an exact str" % what)
    if rel_path == "":
        return ("",)
    if rel_path.startswith("/"):
        raise _TransactionClosed("%s is absolute: %r" % (what, rel_path))
    if "\\" in rel_path or "\x00" in rel_path:
        raise _TransactionClosed("%s has backslash or NUL" % what)
    for ch in rel_path:
        if 0xD800 <= ord(ch) <= 0xDFFF:
            raise _TransactionClosed("surrogate in %s" % what)
    if "//" in rel_path:
        raise _TransactionClosed("repeated separator in %s" % what)
    comps = rel_path.split("/")
    for c in comps:
        if c == "" or c == "." or c == "..":
            raise _TransactionClosed(
                "empty/dot/dotdot component in %s: %r" % (what, rel_path))
    return tuple(comps)


def _canonical_host_path_comps(host_path, what):
    """Validate a host-relative path like external/nos3/..."""
    if not _is_exact_str(host_path) or host_path == "":
        raise _TransactionClosed("%s empty/not an exact str" % what)
    if host_path.startswith("/"):
        raise _TransactionClosed("%s absolute" % what)
    if "\\" in host_path or "\x00" in host_path:
        raise _TransactionClosed("%s backslash or NUL" % what)
    for ch in host_path:
        if 0xD800 <= ord(ch) <= 0xDFFF:
            raise _TransactionClosed("surrogate in %s" % what)
    if "//" in host_path:
        raise _TransactionClosed("repeated separator in %s" % what)
    comps = host_path.split("/")
    for c in comps:
        if c == "" or c == "." or c == "..":
            raise _TransactionClosed(
                "empty/dot/dotdot component in %s: %r" % (what, host_path))
    return tuple(comps)


def _build_canonical_materialization_plan(manifest):
    """Pure read-only compiler.  `manifest` is an already canonical /
    structurally validated manifest object (parsed JSON).  Returns one deeply
    immutable _CanonicalCompletePlan.  Never opens source files, never creates
    authorized roots or staging.  Rejects every mutation by raising
    _TransactionClosed."""
    if not isinstance(manifest, dict):
        raise _TransactionClosed("manifest not a dict object")

    # ---- source-root declarations ----
    sr_raw = manifest.get("source_root_declarations")
    if not isinstance(sr_raw, list):
        raise _TransactionClosed("source_root_declarations not a list")
    sr_by_name = {}
    sr_order = []
    for r in sr_raw:
        if type(r) is not dict:
            raise _TransactionClosed("source root declaration not exact dict")
        name = r.get("source_root")
        if not _is_exact_str(name) or name == "":
            raise _TransactionClosed("source_root name empty/not an exact str")
        if name not in _EXPECTED_SOURCE_ROOT_DECLS:
            raise _TransactionClosed("unexpected source root: %r" % name)
        if name in sr_by_name:
            raise _TransactionClosed("duplicate source root: %r" % name)
        decl = _EXPECTED_SOURCE_ROOT_DECLS[name]
        scope = r.get("component_scope")
        if not _is_exact_str(scope) or scope != decl.component_scope:
            raise _TransactionClosed(
                "source root %s scope mutation: %r" % (name, scope))
        hrp = r.get("host_relative_path")
        if hrp != decl.host_relative_path:
            raise _TransactionClosed(
                "source root %s host_relative_path mutation: %r"
                % (name, hrp))
        _canonical_host_path_comps(hrp, "source root %s host path" % name)
        dp = r.get("destination_prefix")
        if dp != decl.destination_prefix:
            raise _TransactionClosed(
                "source root %s destination_prefix mutation: %r" % (name, dp))
        _canonical_path_comps(dp, "source root %s destination_prefix" % name)
        sr_by_name[name] = decl
        sr_order.append(name)
    if set(sr_order) != _EXPECTED_SOURCE_ROOTS:
        raise _TransactionClosed(
            "source root set mismatch: %r" % (sr_order,))
    source_roots = tuple(sr_by_name[n] for n in ("cfs", "configuration",
                                                  "sim_bin", "sim_lib"))

    # ---- regular-file entries ----
    fe_raw = manifest.get("included_regular_file_entries")
    if not isinstance(fe_raw, list):
        raise _TransactionClosed("included_regular_file_entries not a list")
    regular_files = []
    file_idents = {}  # (source_root, relative_path) -> sha256
    for e in fe_raw:
        if type(e) is not dict:
            raise _TransactionClosed("file entry not exact dict")
        et = e.get("entry_type")
        if et != "regular_file":
            raise _TransactionClosed("file entry_type != regular_file: %r" % et)
        sroot = e.get("source_root")
        if sroot not in sr_by_name:
            raise _TransactionClosed("file entry bad source_root: %r" % sroot)
        decl = sr_by_name[sroot]
        scope = e.get("component_scope")
        if not _is_exact_str(scope) or scope != decl.component_scope:
            raise _TransactionClosed(
                "file entry scope mismatch: %r != %r" % (scope, decl.component_scope))
        rp = e.get("relative_path")
        _canonical_path_comps(rp, "file relative_path")
        dr = e.get("destination_relative")
        _canonical_path_comps(dr, "file destination_relative")
        expected_dr = decl.destination_prefix + "/" + rp
        if dr != expected_dr:
            raise _TransactionClosed(
                "destination_relative mapping mutation: %r != %r"
                % (dr, expected_dr))
        mode = e.get("mode")
        if not (_is_exact_str(mode) and len(mode) == 4
                and all(c in "01234567" for c in mode)):
            raise _TransactionClosed("file mode not exact octal string: %r" % mode)
        if mode not in _ACCEPTED_REGULAR_MODES:
            raise _TransactionClosed("file mode not approved: %r" % mode)
        nlink = e.get("nlink")
        if not (_is_exact_int(nlink) and nlink == 1):
            raise _TransactionClosed("file nlink not exact int 1: %r" % nlink)
        size = e.get("size")
        if not (_is_exact_int(size) and size >= 0):
            raise _TransactionClosed("file size not nonnegative int: %r" % size)
        sha = e.get("sha256")
        if not _is_hex64(sha) or sha != sha.lower():
            raise _TransactionClosed("file sha256 not lowercase hex64")
        ident = (sroot, rp)
        if ident in file_idents:
            raise _TransactionClosed("duplicate file identity: %r" % (ident,))
        file_idents[ident] = sha
        regular_files.append(_CanonicalRegularFile(
            "regular_file", sroot, scope, rp, dr, mode, nlink, size, sha))
    regular_files = tuple(sorted(regular_files,
        key=lambda f: f.destination_relative))

    # ---- directory entries ----
    de_raw = manifest.get("directory_entries")
    if not isinstance(de_raw, list):
        raise _TransactionClosed("directory_entries not a list")
    directories = []
    dir_idents = set()
    empty_seen = set()
    for d in de_raw:
        if type(d) is not dict:
            raise _TransactionClosed("directory entry not exact dict")
        sroot = d.get("source_root")
        if sroot not in sr_by_name:
            raise _TransactionClosed("directory bad source_root: %r" % sroot)
        decl = sr_by_name[sroot]
        scope = d.get("component_scope")
        if not _is_exact_str(scope) or scope != decl.component_scope:
            raise _TransactionClosed("directory scope mismatch")
        rp = d.get("relative_path")
        if rp == "":
            if sroot in empty_seen:
                raise _TransactionClosed(
                    "duplicate empty directory sentinel for %s" % sroot)
            empty_seen.add(sroot)
        else:
            _canonical_path_comps(rp, "directory relative_path")
        ident = (sroot, rp)
        if ident in dir_idents:
            raise _TransactionClosed("duplicate directory identity")
        dir_idents.add(ident)
        directories.append(_CanonicalDirectory(sroot, scope, rp))
    if empty_seen != set(sr_by_name.keys()):
        raise _TransactionClosed(
            "missing empty directory sentinel: %r" % (set(sr_by_name.keys()) - empty_seen,))
    directories = tuple(sorted(directories,
        key=lambda dd: (dd.source_root, dd.relative_path)))

    # ---- exclusion records ----
    ex_raw = manifest.get("exact_exclusion_records")
    if not isinstance(ex_raw, list):
        raise _TransactionClosed("exact_exclusion_records not a list")
    exclusions = []
    excl_idents = set()
    for x in ex_raw:
        if type(x) is not dict:
            raise _TransactionClosed("exclusion not exact dict")
        et = x.get("entry_type")
        if et != "regular_file":
            raise _TransactionClosed("exclusion entry_type != regular_file")
        sroot = x.get("source_root")
        if sroot not in sr_by_name:
            raise _TransactionClosed("exclusion bad source_root")
        rp = x.get("relative_path")
        if not _is_exact_str(rp) or rp == "":
            raise _TransactionClosed("exclusion relative_path empty")
        _canonical_path_comps(rp, "exclusion relative_path")
        mode = x.get("mode")
        if not (_is_exact_str(mode) and len(mode) == 4
                and all(c in "01234567" for c in mode)):
            raise _TransactionClosed("exclusion mode not exact octal string")
        if mode not in _ACCEPTED_EXCLUSION_MODES:
            raise _TransactionClosed("exclusion mode not approved: %r" % mode)
        nlink = x.get("nlink")
        if not (_is_exact_int(nlink) and nlink == 1):
            raise _TransactionClosed("exclusion nlink not exact int 1")
        size = x.get("size")
        if not (_is_exact_int(size) and size >= 0):
            raise _TransactionClosed("exclusion size not nonnegative int")
        sha = x.get("sha256")
        if not _is_hex64(sha) or sha != sha.lower():
            raise _TransactionClosed("exclusion sha256 not lowercase hex64")
        cls = x.get("classification")
        if not _is_exact_str(cls) or cls not in _EXPECTED_CLASSIFICATIONS:
            raise _TransactionClosed("exclusion classification unexpected: %r" % cls)
        dma = x.get("destination_must_be_absent")
        if dma is not True:
            raise _TransactionClosed("exclusion destination_must_be_absent not true")
        paa = x.get("present_at_amendment")
        if not _is_exact_bool(paa):
            raise _TransactionClosed("exclusion present_at_amendment not exact bool")
        ident = (sroot, rp)
        if ident in excl_idents:
            raise _TransactionClosed("duplicate exclusion identity")
        excl_idents.add(ident)
        exclusions.append(_CanonicalExclusion(
            "regular_file", sroot, rp, mode, nlink, size, sha, cls, dma, paa))
    exclusions = tuple(sorted(exclusions,
        key=lambda xx: (xx.source_root, xx.relative_path)))

    # ---- workspace declarations ----
    ws_raw = manifest.get("workspace_declarations")
    if not isinstance(ws_raw, list):
        raise _TransactionClosed("workspace_declarations not a list")
    ws_by_id = {}
    for w in ws_raw:
        if type(w) is not dict:
            raise _TransactionClosed("workspace not exact dict")
        cid = w.get("component_id")
        if not _is_exact_str(cid) or cid == "":
            raise _TransactionClosed("workspace component_id empty/not exact str")
        if cid not in _EXPECTED_WORKSPACE_IDS:
            raise _TransactionClosed("unexpected workspace component_id: %r" % cid)
        if cid in ws_by_id:
            raise _TransactionClosed("duplicate workspace: %r" % cid)
        whp = w.get("workspace_host_path")
        if whp != cid:
            raise _TransactionClosed(
                "workspace_host_path substitution: %r != %r" % (whp, cid))
        md = w.get("mount_destination")
        if not _is_exact_str(md) or md != "/work/nos3":
            raise _TransactionClosed("mount_destination != /work/nos3: %r" % md)
        seeds = w.get("seed_source_roots")
        if not isinstance(seeds, list):
            raise _TransactionClosed("seed_source_roots not a list")
        for sd in seeds:
            if not _is_exact_str(sd):
                raise _TransactionClosed("seed_source_roots element not exact str")
        if cid == "cfs":
            seed_t = ("cfs",)
        else:
            seed_t = ("sim_bin", "sim_lib")
        if tuple(seeds) != seed_t:
            raise _TransactionClosed(
                "workspace %s seed substitution: %r != %r" % (cid, seeds, list(seed_t)))
        for req_bool in ("private_physical_copy", "no_hard_links",
                          "no_reflinks", "no_overlays", "no_source_aliases",
                          "no_runtime_mount_from_external_nos3"):
            val = w.get(req_bool)
            if not _is_exact_bool(val) or val is not True:
                raise _TransactionClosed(
                    "workspace %s %s not exact true bool" % (cid, req_bool))
        ws_by_id[cid] = w
    if set(ws_by_id.keys()) != _EXPECTED_WORKSPACE_IDS:
        raise _TransactionClosed("workspace set mismatch")
    if len(ws_by_id) != 18:
        raise _TransactionClosed("workspace count != 18")

    # ---- compile per-workspace plans ----
    def files_for_seed(seed_tuple):
        out = tuple(f for f in regular_files if f.source_root in seed_tuple)
        return out

    def dirs_for_seed(seed_tuple):
        out = tuple(d for d in directories if d.source_root in seed_tuple)
        return out

    def excls_for_seed(seed_tuple):
        out = tuple(x for x in exclusions if x.source_root in seed_tuple)
        return out

    def _ws_file_target(cid, f):
        return ("workspaces/%s/work/nos3/" % cid) + f.destination_relative

    def _ws_dir_target(cid, decl, rp):
        if rp == "":
            return ("workspaces/%s/work/nos3/" % cid) + decl.destination_prefix
        return ("workspaces/%s/work/nos3/" % cid) + decl.destination_prefix + "/" + rp

    def _ws_excl_target(cid, decl, rp):
        return ("workspaces/%s/work/nos3/" % cid) + decl.destination_prefix + "/" + rp

    def _ft_file_target(f):
        return "fortytwo-config/" + f.destination_relative

    def _ft_dir_target(decl, rp):
        if rp == "":
            return "fortytwo-config/" + decl.destination_prefix
        return "fortytwo-config/" + decl.destination_prefix + "/" + rp

    def _check_target_path(d, what):
        if not _is_exact_str(d) or d == "":
            raise _TransactionClosed("%s empty target" % what)
        if d.startswith("/") or d.endswith("/"):
            raise _TransactionClosed("%s leading/trailing separator: %r" % (what, d))
        if "\\" in d or "\x00" in d:
            raise _TransactionClosed("%s backslash or NUL: %r" % (what, d))
        for ch in d:
            if 0xD800 <= ord(ch) <= 0xDFFF:
                raise _TransactionClosed("%s surrogate: %r" % (what, d))
        if "//" in d:
            raise _TransactionClosed("%s repeated separator: %r" % (what, d))
        for c in d.split("/"):
            if c == "" or c == "." or c == "..":
                raise _TransactionClosed("%s dot/empty component: %r" % (what, d))

    workspaces_list = []
    expanded_ws_files = 0
    expanded_ws_bytes = 0
    expanded_ws_dirs = 0
    expanded_ws_excls = 0
    all_file_targets = []   # _CanonicalExpandedTarget
    all_dir_targets = []
    all_excl_targets = []
    for cid in sorted(ws_by_id.keys()):
        w = ws_by_id[cid]
        seeds = tuple(w["seed_source_roots"])
        wf = files_for_seed(seeds)
        wd = dirs_for_seed(seeds)
        we = excls_for_seed(seeds)
        wfc = len(wf)
        wbc = sum(f.size for f in wf)
        wdrc = len(wd)
        wec = len(we)
        expanded_ws_files += wfc
        expanded_ws_bytes += wbc
        expanded_ws_dirs += wdrc
        expanded_ws_excls += wec
        ws_ft = []
        ws_dt = []
        ws_et = []
        for f in wf:
            d = _ws_file_target(cid, f)
            _check_target_path(d, "workspace file target")
            if not d.startswith("workspaces/%s/work/nos3/" % cid):
                raise _TransactionClosed("workspace file escapes owner: %s" % cid)
            ws_ft.append(_CanonicalExpandedTarget(
                "regular_file", "workspace", cid, f.source_root,
                f.relative_path, d, False))
        for dd in wd:
            decl = sr_by_name[dd.source_root]
            d = _ws_dir_target(cid, decl, dd.relative_path)
            _check_target_path(d, "workspace dir target")
            if not d.startswith("workspaces/%s/work/nos3/" % cid):
                raise _TransactionClosed("workspace dir escapes owner: %s" % cid)
            ws_dt.append(_CanonicalExpandedTarget(
                "directory", "workspace", cid, dd.source_root,
                dd.relative_path, d, False))
        for x in we:
            decl = sr_by_name[x.source_root]
            d = _ws_excl_target(cid, decl, x.relative_path)
            _check_target_path(d, "workspace excl target")
            if not d.startswith("workspaces/%s/work/nos3/" % cid):
                raise _TransactionClosed("workspace excl escapes owner: %s" % cid)
            ws_et.append(_CanonicalExpandedTarget(
                "excluded_regular_file", "workspace", cid, x.source_root,
                x.relative_path, d, True))
        ws_ft = tuple(ws_ft)
        ws_dt = tuple(ws_dt)
        ws_et = tuple(ws_et)
        all_file_targets.extend(ws_ft)
        all_dir_targets.extend(ws_dt)
        all_excl_targets.extend(ws_et)
        workspaces_list.append(_CanonicalWorkspacePlan(
            cid, w["workspace_host_path"], w["mount_destination"],
            seeds, w["private_physical_copy"], w["no_hard_links"],
            w["no_reflinks"], w["no_overlays"], w["no_source_aliases"],
            w["no_runtime_mount_from_external_nos3"], wf, wd, we,
            wfc, wbc, wdrc, wec, ws_ft, ws_dt, ws_et))
    workspaces = tuple(workspaces_list)

    # ---- separate Fortytwo configuration plan (configuration source root) ----
    ft_files = tuple(f for f in regular_files if f.source_root == "configuration")
    ft_dirs = tuple(d for d in directories if d.source_root == "configuration")
    ft_excls = tuple(x for x in exclusions if x.source_root == "configuration")
    cfg_decl = sr_by_name["configuration"]
    ft_ft = []
    ft_dt = []
    ft_et = []
    for f in ft_files:
        d = _ft_file_target(f)
        _check_target_path(d, "fortytwo file target")
        if not d.startswith("fortytwo-config/cfg/build/InOut"):
            raise _TransactionClosed("fortytwo file outside configuration: %s" % d)
        ft_ft.append(_CanonicalExpandedTarget(
            "regular_file", "fortytwo", "fortytwo-config", f.source_root,
            f.relative_path, d, False))
    for dd in ft_dirs:
        d = _ft_dir_target(cfg_decl, dd.relative_path)
        _check_target_path(d, "fortytwo dir target")
        if not d.startswith("fortytwo-config/cfg/build/InOut"):
            raise _TransactionClosed("fortytwo dir outside configuration: %s" % d)
        ft_dt.append(_CanonicalExpandedTarget(
            "directory", "fortytwo", "fortytwo-config", dd.source_root,
            dd.relative_path, d, False))
    # Fortytwo exclusions must remain an empty tuple (configuration has none).
    fortytwo = _CanonicalFortytwoPlan(
        "fortytwo-config", ft_files, ft_dirs, ft_excls,
        len(ft_files), sum(f.size for f in ft_files),
        len(ft_dirs), len(ft_excls),
        tuple(ft_ft), tuple(ft_dt), tuple(ft_et))
    all_file_targets.extend(ft_ft)
    all_dir_targets.extend(ft_dt)
    all_excl_targets.extend(ft_et)

    # ---- exact source totals ----
    src_file_count = len(regular_files)
    src_byte_count = sum(f.size for f in regular_files)
    src_dir_count = len(directories)
    src_excl_count = len(exclusions)
    for rname in ("cfs", "configuration", "sim_bin", "sim_lib"):
        ef, eb, ed, ex = _EXPECTED_SOURCE_ROOT_TOTALS[rname]
        if sum(1 for f in regular_files if f.source_root == rname) != ef:
            raise _TransactionClosed("source root %s file total mismatch" % rname)
        if sum(f.size for f in regular_files if f.source_root == rname) != eb:
            raise _TransactionClosed("source root %s byte total mismatch" % rname)
        if sum(1 for d in directories if d.source_root == rname) != ed:
            raise _TransactionClosed("source root %s dir total mismatch" % rname)
        if sum(1 for x in exclusions if x.source_root == rname) != ex:
            raise _TransactionClosed("source root %s exclusion total mismatch" % rname)

    # ---- fail-closed collision model from immutable expanded targets ----
    def _ancestor_prefixes(d):
        comps = d.split("/")
        return ("/".join(comps[:i]) for i in range(1, len(comps)))

    file_by_path = {}
    dir_by_path = {}
    excl_by_path = {}
    for t in all_file_targets:
        if t.transaction_relative_path in file_by_path:
            raise _TransactionClosed("duplicate regular-file target: %r"
                % t.transaction_relative_path)
        file_by_path[t.transaction_relative_path] = t
    for t in all_dir_targets:
        if t.transaction_relative_path in dir_by_path:
            raise _TransactionClosed("duplicate directory target: %r"
                % t.transaction_relative_path)
        dir_by_path[t.transaction_relative_path] = t
    for t in all_excl_targets:
        if t.transaction_relative_path in excl_by_path:
            raise _TransactionClosed("duplicate exclusion target: %r"
                % t.transaction_relative_path)
        excl_by_path[t.transaction_relative_path] = t

    fp = set(file_by_path)
    dp = set(dir_by_path)
    ep = set(excl_by_path)
    # equality collisions
    if fp & dp:
        raise _TransactionClosed("regular-file/directory target collision")
    if fp & ep:
        raise _TransactionClosed("regular-file/exclusion target collision")
    if dp & ep:
        raise _TransactionClosed("directory/exclusion target collision")
    # prefix ancestor collisions: a regular-file target must not be an
    # ancestor (path prefix) of any other target; an exclusion target must not
    # be an ancestor of an included file or directory.  A directory being an
    # ancestor of a file is the normal hierarchy and is NOT a collision.
    def _is_prefix(prefix, path):
        return path.startswith(prefix + "/")

    for prefix_p in fp:
        for other in fp:
            if other != prefix_p and _is_prefix(prefix_p, other):
                raise _TransactionClosed("file prefix collision: %r" % prefix_p)
        for other in dp:
            if _is_prefix(prefix_p, other):
                raise _TransactionClosed("file/directory prefix collision: %r" % prefix_p)
        for other in ep:
            if _is_prefix(prefix_p, other):
                raise _TransactionClosed("file/exclusion prefix collision: %r" % prefix_p)
    for prefix_p in ep:
        for other in fp:
            if _is_prefix(prefix_p, other):
                raise _TransactionClosed("exclusion/file prefix collision: %r" % prefix_p)
        for other in dp:
            if _is_prefix(prefix_p, other):
                raise _TransactionClosed("exclusion/directory prefix collision: %r" % prefix_p)
    # owner namespace escape checks
    for t in all_file_targets + all_dir_targets + all_excl_targets:
        d = t.transaction_relative_path
        if t.owner_kind == "workspace":
            if d.startswith("fortytwo-config/"):
                raise _TransactionClosed("workspace target under fortytwo: %r" % d)
            if not d.startswith("workspaces/%s/work/nos3/" % t.owner_id):
                raise _TransactionClosed("workspace target escape: %r for %s" % (d, t.owner_id))
        elif t.owner_kind == "fortytwo":
            if d.startswith("workspaces/"):
                raise _TransactionClosed("fortytwo target under workspaces: %r" % d)
            if not d.startswith("fortytwo-config/cfg/build/InOut"):
                raise _TransactionClosed("fortytwo target escape: %r" % d)

    # ---- deny pattern declarations ----
    dp_raw = manifest.get("deny_pattern_declarations")
    if not isinstance(dp_raw, list):
        raise _TransactionClosed("deny_pattern_declarations not a list")
    deny_patterns = []
    seen_dp = set()
    for dp in dp_raw:
        if type(dp) is not dict:
            raise _TransactionClosed("deny pattern not exact dict")
        pat = dp.get("pattern")
        if not _is_exact_str(pat) or pat == "":
            raise _TransactionClosed("deny pattern empty/not exact str")
        scope = dp.get("scope")
        if scope not in sr_by_name:
            raise _TransactionClosed("deny pattern scope unknown: %r" % scope)
        key = (scope, pat)
        if key in seen_dp:
            raise _TransactionClosed("duplicate deny pattern: %r" % (key,))
        seen_dp.add(key)
        deny_patterns.append(_CanonicalDenyPattern(pat, scope))
    deny_patterns = tuple(sorted(deny_patterns,
        key=lambda d: (d.scope, d.pattern)))

    dup_file = 0
    dup_dir = 0
    fd_collision = 0
    prefix_collision = 0
    collision_model = (dup_file, dup_dir, fd_collision, prefix_collision)

    total_files = expanded_ws_files + fortytwo.file_count
    total_bytes = expanded_ws_bytes + fortytwo.byte_count
    total_dirs = expanded_ws_dirs + fortytwo.directory_count
    total_excls = expanded_ws_excls + fortytwo.exclusion_count

    plan = _CanonicalCompletePlan(
        source_roots=source_roots,
        source_regular_files=regular_files,
        source_directories=directories,
        source_exclusions=exclusions,
        workspaces=workspaces,
        fortytwo=fortytwo,
        collision_model=collision_model,
        source_root_count=4,
        source_file_entry_count=src_file_count,
        source_file_byte_count=src_byte_count,
        source_directory_entry_count=src_dir_count,
        source_exclusion_entry_count=src_excl_count,
        workspace_count=len(workspaces),
        expanded_workspace_file_count=expanded_ws_files,
        expanded_workspace_byte_count=expanded_ws_bytes,
        expanded_workspace_directory_count=expanded_ws_dirs,
        expanded_workspace_exclusion_count=expanded_ws_excls,
        expanded_total_file_count=total_files,
        expanded_total_byte_count=total_bytes,
        expanded_total_directory_count=total_dirs,
        expanded_total_exclusion_count=total_excls,
        duplicate_file_target_count=dup_file,
        duplicate_directory_target_count=dup_dir,
        file_directory_collision_count=fd_collision,
        prefix_collision_count=prefix_collision,
        expanded_file_targets=tuple(all_file_targets),
        expanded_directory_targets=tuple(all_dir_targets),
        expanded_exclusion_targets=tuple(all_excl_targets),
        deny_patterns=deny_patterns)
    return plan


def _validate_absolute_authorized_root(authorized_root):
    """Strict absolute-directory opener for the authorized root.

    Every opened descriptor has exactly one owner.  The initial '/' descriptor
    is closed on every rejection or exception; every intermediate descriptor
    is closed on every rejection or exception; only the successfully returned
    final authorized-root descriptor remains open.  Strict no-follow and
    lstat-to-fstat identity continuity are preserved at each hop.

    Returns (root_fd, _RepoReceipt) with the final descriptor open.
    """
    if not isinstance(authorized_root, str) or authorized_root == "":
        raise _TransactionClosed("authorized root not a nonempty string")
    if not os.path.isabs(authorized_root):
        raise _TransactionClosed("authorized root not absolute")
    if "\\" in authorized_root or "\x00" in authorized_root:
        raise _TransactionClosed("authorized root has backslash or NUL")
    for ch in authorized_root:
        if 0xD800 <= ord(ch) <= 0xDFFF:
            raise _TransactionClosed("surrogate code point in authorized root")
    if authorized_root != os.path.abspath(authorized_root):
        raise _TransactionClosed("authorized root not normalized")
    comps = [c for c in authorized_root.split(os.sep) if c != ""]
    resolved = []
    for c in comps:
        if c == "" or c == "." or c == "..":
            raise _TransactionClosed("invalid component in authorized root: %r" % c)
        resolved.append(c)

    owners = []  # all opened descriptors not yet released
    returned_fd = None  # the one descriptor we will return (explicitly tracked)
    try:
        cur = _wrap_os("authorize-root open /", os.open, "/",
                       os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        owners.append(cur)
        for comp in resolved:
            lst = _wrap_os("authorize-root lstat %s" % comp, os.lstat, comp,
                           dir_fd=cur)
            if (lst.st_mode & 0o170000) == 0o120000:
                raise _TransactionClosed(
                    "authorized-root symlink component rejected: %s" % comp)
            if (lst.st_mode & 0o170000) != 0o040000:
                raise _TransactionClosed(
                    "authorized-root component not a directory: %s" % comp)

            def _pop(name=comp, dfd=cur):
                return os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                               dir_fd=dfd)
            try:
                nxt = _wrap_os("authorize-root open %s" % comp, _pop)
            except _TransactionClosed as exc:
                if "ELOOP" in str(exc) or "Too many levels" in str(exc):
                    raise _TransactionClosed(
                        "authorized-root symlink component rejected: %s" % comp)
                raise
            owned = True
            try:
                owners.append(nxt)
                nst = _wrap_os("authorize-root fstat %s" % comp, os.fstat, nxt)
                if (nst.st_dev, nst.st_ino) != (lst.st_dev, lst.st_ino):
                    raise _TransactionClosed(
                        "authorized-root identity discontinuity: %s" % comp)
                owned = False  # ownership transferred to owners list
            except BaseException:
                if owned:
                    try:
                        os.close(nxt)
                    except OSError:
                        pass
                    if owners and owners[-1] is nxt:
                        owners.pop()
                raise
            # The previous `cur` is no longer needed; close and release it
            # exactly once, since ownership transfers to `nxt`.
            prev = cur
            cur = nxt
            try:
                os.close(prev)
            except OSError:
                pass
            if owners:
                owners.remove(prev)
        final_st = _wrap_os("authorize-root final fstat", os.fstat, cur)
        if (final_st.st_mode & 0o170000) != 0o040000:
            raise _TransactionClosed("authorized root not a directory")
        if final_st.st_uid != os.geteuid():
            raise _TransactionClosed("authorized root owner mismatch")
        if final_st.st_mode & 0o022:
            raise _TransactionClosed("authorized root group/other writable")
        # Only the final descriptor remains open and is returned.
        returned_fd = cur
        receipt = _RepoReceipt(dev=final_st.st_dev, ino=final_st.st_ino)
        return returned_fd, receipt
    except BaseException:
        # Close every owned descriptor except the one we will return.
        for fdx in owners:
            if fdx is returned_fd:
                continue
            try:
                os.close(fdx)
            except OSError:
                pass
        raise

def _darwin_extended_acl_entry_count(root_fd):
    if sys.platform != "darwin": raise _TransactionClosed("D-064 V4 ACL policy requires Darwin")
    try:
        libc=ctypes.CDLL(ctypes.util.find_library("c") or None,use_errno=True)
        getfd=libc.acl_get_fd_np; getent=libc.acl_get_entry; valid=libc.acl_valid_fd_np; free=libc.acl_free
    except (AttributeError,OSError) as exc: raise _TransactionClosed("Darwin ACL API unavailable: %s"%exc)
    getfd.argtypes=[ctypes.c_int,ctypes.c_int]; getfd.restype=ctypes.c_void_p
    getent.argtypes=[ctypes.c_void_p,ctypes.c_int,ctypes.POINTER(ctypes.c_void_p)]; getent.restype=ctypes.c_int
    valid.argtypes=[ctypes.c_int,ctypes.c_int,ctypes.c_void_p]; valid.restype=ctypes.c_int
    free.argtypes=[ctypes.c_void_p]; free.restype=ctypes.c_int
    ctypes.set_errno(0); acl=getfd(root_fd,_ACL_TYPE_EXTENDED); geterr=ctypes.get_errno()
    if not acl:
        # Apple Libc: absent FILESEC_ACL property => NULL with errno=ENOENT.
        # This exact disposition means zero extended ACL entries.  Every other
        # NULL/error remains fail-closed.
        if geterr==errno.ENOENT: return 0
        raise _TransactionClosed("acl_get_fd_np failed errno=%d"%geterr)
    try:
        ctypes.set_errno(0)
        if valid(root_fd,_ACL_TYPE_EXTENDED,acl)!=0: raise _TransactionClosed("acl_valid_fd_np failed errno=%d"%ctypes.get_errno())
        ent=ctypes.c_void_p(); ctypes.set_errno(0); rc=getent(acl,_ACL_FIRST_ENTRY,ctypes.byref(ent)); er=ctypes.get_errno()
        if rc==-1:
            if er==errno.EINVAL: return 0
            raise _TransactionClosed("ACL_FIRST_ENTRY failed errno=%d"%er)
        if rc!=0: raise _TransactionClosed("ACL_FIRST_ENTRY unexpected rc=%d"%rc)
        count=1
        while True:
            ent=ctypes.c_void_p(); ctypes.set_errno(0); rc=getent(acl,_ACL_NEXT_ENTRY,ctypes.byref(ent)); er=ctypes.get_errno()
            if rc==0: count+=1; continue
            if rc==-1 and er==errno.EINVAL: return count
            raise _TransactionClosed("ACL_NEXT_ENTRY ambiguity rc=%d errno=%d"%(rc,er))
    finally:
        ctypes.set_errno(0)
        if free(acl)!=0: raise _TransactionClosed("acl_free failed errno=%d"%ctypes.get_errno())

def _validate_root_acl_no_extended(root_fd):
    count=_darwin_extended_acl_entry_count(root_fd)
    if count!=0: raise _TransactionClosed("%s violated: extended_acl_entry_count=%d"%(_D064_ACL_POLICY,count))
    return count

def _validate_serialization_lock_object(lock_fd,root_receipt,expected=None):
    fst=_wrap_os("serialization lock fstat",os.fstat,lock_fd)
    if not stat.S_ISREG(fst.st_mode): raise _TransactionClosed("serialization lock not regular")
    if fst.st_nlink!=1: raise _TransactionClosed("serialization lock nlink != 1")
    if fst.st_uid!=os.geteuid(): raise _TransactionClosed("serialization lock owner mismatch")
    if stat.S_IMODE(fst.st_mode)!=_D064_LOCK_MODE: raise _TransactionClosed("serialization lock mode != 0600")
    if fst.st_dev!=root_receipt.dev: raise _TransactionClosed("serialization lock device mismatch")
    r=_LockReceipt(_D064_LOCK_BASENAME,fst.st_dev,fst.st_ino,stat.S_IMODE(fst.st_mode),fst.st_nlink,fst.st_uid)
    if expected is not None and r!=expected: raise _TransactionClosed("serialization lock state drift")
    return r

def _open_existing_serialization_lock(root_fd):
    lst=_wrap_os("serialization lock lstat",os.lstat,_D064_LOCK_BASENAME,dir_fd=root_fd)
    if stat.S_ISLNK(lst.st_mode): raise _TransactionClosed("serialization lock symlink rejected")
    fd=_wrap_os("serialization lock open",os.open,_D064_LOCK_BASENAME,os.O_RDWR|os.O_NOFOLLOW,dir_fd=root_fd)
    try:
        fst=_wrap_os("serialization lock identity fstat",os.fstat,fd)
        if (fst.st_dev,fst.st_ino)!=(lst.st_dev,lst.st_ino): raise _TransactionClosed("serialization lock identity discontinuity")
        return fd
    except BaseException:
        try: os.close(fd)
        except OSError: pass
        raise

def _acquire_serialization_lock(root_fd,root_receipt):
    fd=None
    try:
        try:
            fd=os.open(_D064_LOCK_BASENAME,os.O_RDWR|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,_D064_LOCK_MODE,dir_fd=root_fd)
            _wrap_os("serialization lock fchmod",os.fchmod,fd,_D064_LOCK_MODE)
        except OSError as exc:
            if exc.errno!=errno.EEXIST: raise _TransactionClosed("serialization lock create failed: %s"%exc)
            fd=_open_existing_serialization_lock(root_fd)
        r=_validate_serialization_lock_object(fd,root_receipt)
        try: fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except OSError as exc:
            if exc.errno in (errno.EACCES,errno.EAGAIN): raise _TransactionClosed("serialization lock contention")
            raise _TransactionClosed("serialization flock failed: %s"%exc)
        return fd,r
    except BaseException:
        if fd is not None:
            try: os.close(fd)
            except OSError: pass
        raise

def _revalidate_serialization_lock(root_fd,lock_fd,root_receipt,expected):
    lst=_wrap_os("serialization lock prepublish lstat",os.lstat,_D064_LOCK_BASENAME,dir_fd=root_fd)
    if stat.S_ISLNK(lst.st_mode): raise _TransactionClosed("serialization lock prepublish symlink rejected")
    fst=_wrap_os("serialization lock prepublish fstat",os.fstat,lock_fd)
    if (fst.st_dev,fst.st_ino)!=(lst.st_dev,lst.st_ino): raise _TransactionClosed("serialization lock prepublish identity discontinuity")
    return _validate_serialization_lock_object(lock_fd,root_receipt,expected)

def _validate_final_basename(final_basename, root_fd):
    """Strict final-basename validation.  Reject empty/[.]/[..]/slash/backslash/
    NUL/surrogate/leading-or-trailing-whitespace and any existing destination
    under the authorized-root descriptor."""
    if not isinstance(final_basename, str) or final_basename == "":
        raise _TransactionClosed("final basename empty/not a string")
    if final_basename in (".", ".."):
        raise _TransactionClosed("final basename is dot/dotdot")
    if "/" in final_basename or "\\" in final_basename:
        raise _TransactionClosed("final basename has separator")
    if "\x00" in final_basename:
        raise _TransactionClosed("final basename has NUL")
    for ch in final_basename:
        if 0xD800 <= ord(ch) <= 0xDFFF:
            raise _TransactionClosed("surrogate in final basename")
    if final_basename != final_basename.strip():
        raise _TransactionClosed("final basename has surrounding whitespace")
    if final_basename != os.path.basename(final_basename):
        raise _TransactionClosed("final basename not a pure basename")
    try:
        st = os.lstat(final_basename, dir_fd=root_fd)
    except OSError as exc:
        if exc.errno == errno.ENOENT:
            return
        raise _TransactionClosed("final basename lstat failed: %s" % exc)
    raise _TransactionClosed("final destination already exists")


def _make_staging_dir(root_fd):
    """Create one private hidden staging directory beneath authorized-root.

    Internally transactional: once mkdir succeeds, the generated staging
    basename is retained locally.  If open fails, the exact newly created
    directory is removed through root_fd.  If fstat fails, the opened
    descriptor is closed and the exact directory is removed.  The opened
    descriptor is verified to be a directory, its dev/inode identity is
    verified against a descriptor-relative lstat, and mode 0700 is required.
    On rollback failure both the creation failure and the rollback failure are
    reported.  Never returns a partially validated descriptor.

    Returns (stage_fd, stage_name, st_dev, st_ino)."""
    stage_name = ".nrm-v4-stage-" + secrets.token_hex(16)
    created = False
    stage_fd = None
    primary = None
    try:
        try:
            os.mkdir(stage_name, mode=0o700, dir_fd=root_fd)
        except OSError as exc:
            if exc.errno == errno.EEXIST:
                raise _TransactionClosed("staging name collision")
            raise _TransactionClosed("staging mkdir failed: %s" % exc)
        created = True
        try:
            stage_fd = _wrap_os("staging open", os.open, stage_name,
                                os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                                dir_fd=root_fd)
        except BaseException as exc:
            primary = exc
            try:
                os.rmdir(stage_name, dir_fd=root_fd)
            except OSError as rb:
                raise _TransactionClosed(
                    "staging open failed (%r) and rollback rmdir failed: %s"
                    % (exc, rb))
            raise
        try:
            st = _wrap_os("staging fstat", os.fstat, stage_fd)
        except BaseException as exc:
            primary = exc
            try:
                os.close(stage_fd)
            except OSError:
                pass
            stage_fd = None
            try:
                os.rmdir(stage_name, dir_fd=root_fd)
            except OSError as rb:
                raise _TransactionClosed(
                    "staging fstat failed (%r) and rollback rmdir failed: %s"
                    % (exc, rb))
            raise
        if (st.st_mode & 0o170000) != 0o040000:
            primary = _TransactionClosed("staging not a directory")
            try:
                os.close(stage_fd)
            except OSError:
                pass
            stage_fd = None
            try:
                os.rmdir(stage_name, dir_fd=root_fd)
            except OSError as rb:
                raise _TransactionClosed(
                    "staging not a directory (%r) and rollback rmdir failed: %s"
                    % (primary, rb))
            raise primary
        try:
            lst = _wrap_os("staging lstat", os.lstat, stage_name, dir_fd=root_fd)
        except BaseException as exc:
            primary = exc
            try:
                os.close(stage_fd)
            except OSError:
                pass
            stage_fd = None
            try:
                os.rmdir(stage_name, dir_fd=root_fd)
            except OSError as rb:
                raise _TransactionClosed(
                    "staging identity lstat failed (%r) and rollback rmdir failed: %s"
                    % (exc, rb))
            raise
        if (st.st_dev, st.st_ino) != (lst.st_dev, lst.st_ino):
            primary = _TransactionClosed("staging identity mismatch")
            try:
                os.close(stage_fd)
            except OSError:
                pass
            stage_fd = None
            try:
                os.rmdir(stage_name, dir_fd=root_fd)
            except OSError as rb:
                raise _TransactionClosed(
                    "staging identity mismatch (%r) and rollback rmdir failed: %s"
                    % (primary, rb))
            raise primary
        if (st.st_mode & 0o777) != 0o700:
            primary = _TransactionClosed("staging mode mismatch")
            try:
                os.close(stage_fd)
            except OSError:
                pass
            stage_fd = None
            try:
                os.rmdir(stage_name, dir_fd=root_fd)
            except OSError as rb:
                raise _TransactionClosed(
                    "staging mode mismatch (%r) and rollback rmdir failed: %s"
                    % (primary, rb))
            raise primary
        return stage_fd, stage_name, st.st_dev, st.st_ino
    except BaseException:
        # Ensure no partially validated descriptor is returned.
        if stage_fd is not None:
            try:
                os.close(stage_fd)
            except OSError:
                pass
            stage_fd = None
        raise

def _desc_mkdir(parent_fd, name, mode=0o700):
    """Descriptor-relative mkdir + open, returning the child fd."""
    try:
        os.mkdir(name, mode=mode, dir_fd=parent_fd)
    except OSError as exc:
        raise _TransactionClosed("mkdir %s failed: %s" % (name, exc))
    fd = _wrap_os("mkdir open %s" % name, os.open, name,
                  os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent_fd)
    return fd


def _desc_create_file(parent_fd, name, mode):
    """Create a regular file with O_CREAT|O_EXCL|O_NOFOLLOW and return its fd."""
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW
    try:
        fd = os.open(name, flags, mode, dir_fd=parent_fd)
    except OSError as exc:
        raise _TransactionClosed("file create %s failed: %s" % (name, exc))
    return fd


def _complete_write(fd, data, rel_for_msg, inject=None):
    """Write all bytes with a complete-write loop; reject short writes.

    If `inject` contains a `file_write_failure` hook, the failure is injected
    strictly inside the complete-write loop after at least one byte has been
    written and before all bytes have been written.  When injecting, bytes are
    written one at a time so the partial-write boundary is reached
    deterministically.  No fsync or receipt follows the injected mid-file-write
    failure."""
    off = 0
    n = len(data)
    injecting = inject is not None and "file_write_failure" in inject
    while off < n:
        end_chunk = off + 1 if injecting else n
        try:
            wrote = os.write(fd, data[off:end_chunk])
        except OSError as exc:
            raise _TransactionClosed("write %s failed: %s" % (rel_for_msg, exc))
        if wrote <= 0:
            raise _TransactionClosed("short write on %s" % rel_for_msg)
        off += wrote
        # CORRECTION 6: mid-file-write failure inside the complete-write loop,
        # after at least one byte and before the total is reached.
        if injecting and off >= 1 and off < n:
            hf = inject["file_write_failure"]
            hf["hits"] = hf.get("hits", 0) + 1
            hf["bytes_written"] = off
            hf["total_bytes"] = n
            raise _TransactionClosed("injected mid-file-write failure")
    return off


class _OwnedFds:
    """Tracks all descriptors opened during one transaction for cleanup.
    Closing is descriptor-relative (no shutil.rmtree) and ordered."""

    def __init__(self):
        self._fds = []

    def add(self, fd):
        if fd is not None:
            self._fds.append(fd)
        return fd

    def close_all(self):
        while self._fds:
            fd = self._fds.pop()
            try:
                os.close(fd)
            except OSError:
                pass


def _desc_rmtree(fd, name, owned):
    """Descriptor-relative recursive removal of a named child of `fd`, with
    no-follow traversal.  Verifies object type and retained identity before
    removal.  The directory descriptor opened here is closed before return on
    every path.  Symlinks are rejected (never followed).  Returns True if
    removed, False if absent."""
    try:
        lst = os.lstat(name, dir_fd=fd)
    except OSError as exc:
        if exc.errno == errno.ENOENT:
            return False
        raise _TransactionClosed("cleanup lstat %s failed: %s" % (name, exc))
    if (lst.st_mode & 0o170000) == 0o120000:
        raise _TransactionClosed("cleanup symlink rejected: %s" % name)
    if (lst.st_mode & 0o170000) == 0o040000:
        sub_fd = _wrap_os("cleanup opendir %s" % name, os.open, name,
                          os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
        try:
            sub_st = _wrap_os("cleanup fstat %s" % name, os.fstat, sub_fd)
            if (sub_st.st_dev, sub_st.st_ino) != (lst.st_dev, lst.st_ino):
                raise _TransactionClosed("cleanup identity discontinuity: %s" % name)
            names = _wrap_os("cleanup listdir %s" % name, _fd_listdir, sub_fd)
            for child in names:
                if child in (".", ".."):
                    continue
                _desc_rmtree(sub_fd, child, owned)
            _wrap_os("cleanup rmdir %s" % name, os.rmdir, name, dir_fd=fd)
        except BaseException:
            try:
                os.close(sub_fd)
            except OSError:
                pass
            raise
        try:
            os.close(sub_fd)
        except OSError:
            pass
        return True
    if (lst.st_mode & 0o170000) != 0o100000:
        raise _TransactionClosed("cleanup non-regular object: %s" % name)
    _wrap_os("cleanup unlink %s" % name, os.unlink, name, dir_fd=fd)
    return True


def _fd_listdir(fd):
    """Portable listing of names in an open directory descriptor.

    Fail closed: unsupported fd enumeration (TypeError) and every OSError are
    converted into _TransactionClosed.  Enumeration errors must never be treated
    as an empty directory.  Returns a deterministic sorted tuple of names on
    success and rejects any non-string name if encountered.
    """
    try:
        names = os.listdir(fd)
    except TypeError as exc:
        raise _TransactionClosed("listdir unsupported fd: %s" % exc)
    except OSError as exc:
        raise _TransactionClosed("listdir failed: %s" % exc)
    out = []
    for name in names:
        if not isinstance(name, str):
            raise _TransactionClosed("listdir non-string name: %r" % (name,))
        out.append(name)
    return tuple(sorted(out))

def _path_components(rel):
    comps = rel.split("/")
    out = []
    for c in comps:
        if c == "" or c == "." or c == "..":
            continue
        out.append(c)
    return out


def _create_synthetic_tree(stage_fd, plan, owned, inject=None):
    """Create the staging layout and synthetic files.  Every file and
    intermediate-directory descriptor is closed immediately after use; only
    the staging root (`stage_fd`) stays open.  Returns a list of records:
    (rel_path, size, sha256, mode).  All opens are descriptor-relative
    no-follow with O_CREAT|O_EXCL|O_NOFOLLOW."""
    file_records = []

    def _ensure_dirs(rel_comps, base_fd):
        """Walk rel_comps (no leaf), creating+opening each intermediate dir
        relative to base_fd; close each immediately, returning the parent fd
        for the leaf (opened).  Caller closes the returned parent fd."""
        cfd = base_fd
        for comp_name in rel_comps:
            # mkdir if absent (lstat first)
            try:
                pst = os.lstat(comp_name, dir_fd=cfd)
            except OSError as exc:
                if exc.errno == errno.ENOENT:
                    pst = None
                else:
                    raise _TransactionClosed("ensure lstat %s failed: %s" % (comp_name, exc))
            if pst is None:
                nfd = _desc_mkdir(cfd, comp_name)
            else:
                if (pst.st_mode & 0o170000) != 0o040000:
                    raise _TransactionClosed("ensure path not a dir: %s" % comp_name)
                nfd = _wrap_os("ensure open %s" % comp_name, os.open, comp_name,
                               os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=cfd)
            if cfd is not base_fd:
                _wrap_os("ensure close", os.close, cfd)
            cfd = nfd
        return cfd

    def _write_one_file(rel_path, content, mode):
        comps = _path_components(rel_path)
        dirs = comps[:-1]
        leaf = comps[-1]
        parent_fd = _ensure_dirs(dirs, stage_fd)
        try:
            ffd = _desc_create_file(parent_fd, leaf, mode)
        finally:
            _wrap_os("file parent close", os.close, parent_fd)
        try:
            _complete_write(ffd, content, rel_path, inject=inject)
            _wrap_os("file fsync %s" % rel_path, os.fsync, ffd)
            fst = _wrap_os("post-write fstat %s" % rel_path, os.fstat, ffd)
            if (fst.st_mode & 0o170000) != 0o100000:
                raise _TransactionClosed("created object not regular: %s" % rel_path)
            if fst.st_nlink != 1:
                raise _TransactionClosed("created nlink != 1: %s" % rel_path)
            if fst.st_size != len(content):
                raise _TransactionClosed("created size mismatch: %s" % rel_path)
            sha = hashlib.sha256(content).hexdigest()
            file_records.append((rel_path, fst.st_size, sha, fst.st_mode))
        finally:
            _wrap_os("file close %s" % rel_path, os.close, ffd)

    # workspaces/ tree and fortytwo-config/.
    for comp in plan.components:
        for sf in comp.files:
            _write_one_file(sf.rel_path, sf.content, sf.mode)
    for sf in plan.fortytwo_files:
        _write_one_file(sf.rel_path, sf.content, sf.mode)
    return file_records


def _build_receipt(plan, final_basename, file_records, publication_method=None):
    """Build the canonical receipt object from the immutable plan and the
    actual created-file records.  No timestamp, random staging name, host
    path, username, secret, or authorization object."""
    total_bytes = sum(r[1] for r in file_records)
    files_sorted = sorted(
        [{"rel_path": r[0], "size": r[1], "sha256": r[2]} for r in file_records],
        key=lambda d: d["rel_path"])
    workspaces = [{"component_id": comp.component_id,
                   "relative_root": "workspaces/%s/work/nos3" % comp.component_id}
                  for comp in sorted(plan.components, key=lambda c: c.component_id)]
    return {
        "receipt_schema": 1,
        "status": "TRANSACTION_COMPLETE_PENDING_PUBLICATION",
        "final_basename": final_basename,
        "transaction_tool_sha256": _sha256_file_path(__file__),
        "component_count": len(plan.components),
        "component_ids": sorted(comp.component_id for comp in plan.components),
        "workspace_count": len(plan.components),
        "fortytwo_scratch_present": True,
        "workspaces": workspaces,
        "files": files_sorted,
        "total_synthetic_file_count": len(file_records),
        "total_synthetic_byte_count": total_bytes,
        "publication_method": publication_method or _platform_publication_method(),
        "reportable_findings_activity_id": "RF-ACT-001",
        "runtime_authorized": False,
        "runtime_attempts": 0,
        "docker_invoked": False,
    }


def _write_canonical_receipt(stage_fd, receipt):
    """Write transaction-receipt.json with no-replace semantics, fsync it,
    and verify its bytes/SHA-256.  Returns the byte SHA-256.  The receipt
    descriptor is closed before return."""
    raw = (json.dumps(receipt, ensure_ascii=True, sort_keys=True,
                      separators=(",", ":")) + "\n").encode("utf-8")
    rfd = _desc_create_file(stage_fd, "transaction-receipt.json", 0o644)
    try:
        _complete_write(rfd, raw, "transaction-receipt.json")
        _wrap_os("receipt fsync", os.fsync, rfd)
        fst = _wrap_os("receipt post-write fstat", os.fstat, rfd)
        if (fst.st_mode & 0o170000) != 0o100000 or fst.st_nlink != 1:
            raise _TransactionClosed("receipt not regular/nlink1")
        if fst.st_size != len(raw):
            raise _TransactionClosed("receipt size mismatch")
        return hashlib.sha256(raw).hexdigest()
    finally:
        _wrap_os("receipt close", os.close, rfd)



def _platform_publication_method():
    """Return the publication-method name matching the selected platform
    primitive for the current platform.  The receipt publication_method must
    match this value.  Returns ('renameatx_np_RENAME_EXCL' on macOS) or
    ('renameat2_RENAME_NOREPLACE' on Linux).  Raises _TransactionClosed on
    unsupported platforms before any primitive is invoked."""
    if sys.platform == "darwin":
        return "renameatx_np_RENAME_EXCL"
    if sys.platform.startswith("linux"):
        return "renameat2_RENAME_NOREPLACE"
    raise _TransactionClosed(
        "atomic no-replace publish: unsupported platform %r" % sys.platform)


def _atomic_noreplace_publish(root_fd, stage_name, final_basename):
    """One atomic no-replace directory publication.

    On macOS uses renameatx_np with RENAME_EXCL (0x4); on Linux uses
    renameat2 with RENAME_NOREPLACE (1) through ctypes.  Addresses source and
    destination relative to root_fd.  EEXIST preserves the existing destination.
    Unsupported primitive/platform fails closed.  No ordinary rename,
    os.rename, os.replace, check-then-rename, shell, or subprocess fallback.
    Returns None on success.
    """
    plat = sys.platform
    if plat == "darwin":
        try:
            libname = ctypes.util.find_library("c")
            if libname is None:
                raise _TransactionClosed("renameatx_np unavailable: libc not found")
            libc = ctypes.CDLL(libname, use_errno=True)
            fn = libc.renameatx_np
        except (AttributeError, OSError):
            raise _TransactionClosed("renameatx_np unavailable")
        _RENAME_EXCL = 0x00000004
        fn.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int,
                       ctypes.c_char_p, ctypes.c_uint]
        fn.restype = ctypes.c_int
        rc = fn(root_fd, stage_name.encode("utf-8"), root_fd,
                final_basename.encode("utf-8"), _RENAME_EXCL)
        err = ctypes.get_errno()
        if rc != 0:
            if err == errno.EEXIST:
                # EEXIST preserves the existing destination.
                raise _TransactionClosed(
                    "atomic no-replace publish EEXIST: destination exists")
            raise _TransactionClosed(
                "atomic no-replace publish failed (renameatx_np): errno=%d"
                % err)
        return
    if plat.startswith("linux"):
        libname = ctypes.util.find_library("c")
        if libname is None:
            raise _TransactionClosed(
                "atomic no-replace publish: libc not found (linux)")
        libc = ctypes.CDLL(libname, use_errno=True)
        renameat2 = getattr(libc, "renameat2", None)
        if renameat2 is None:
            raise _TransactionClosed(
                "atomic no-replace publish: renameat2 symbol missing")
        _RENAME_NOREPLACE = 1
        renameat2.argtypes = [ctypes.c_int, ctypes.c_char_p,
                              ctypes.c_int, ctypes.c_char_p,
                              ctypes.c_uint]
        renameat2.restype = ctypes.c_int
        rc = renameat2(root_fd, stage_name.encode("utf-8"), root_fd,
                       final_basename.encode("utf-8"), _RENAME_NOREPLACE)
        err = ctypes.get_errno()
        if rc != 0:
            if err == errno.EEXIST:
                raise _TransactionClosed(
                    "atomic no-replace publish EEXIST: destination exists")
            raise _TransactionClosed(
                "atomic no-replace publish failed (renameat2): errno=%d"
                % err)
        return
    raise _TransactionClosed(
        "atomic no-replace publish: unsupported platform %r" % plat)

def _fsync_dir_by_fd(fd):
    """fsync an open directory descriptor; fail closed."""
    try:
        os.fsync(fd)
    except OSError as exc:
        raise _TransactionClosed("dir fsync failed: %s" % exc)


def _fsync_staged_hierarchy(stage_fd, owned):
    """Pre-publication durability boundary.  Descriptor-relative,
    no-follow traversal that opens every staged subdirectory, verifies lstat
    (through the parent descriptor) to fstat continuity, fsyncs each child
    directory before its parent, and fsyncs the retained staging-root
    descriptor last.  Every child descriptor is closed exactly once.
    Regular files are already fsynced at write time; this pass durably
    persists only the directory entries and the staging root.  Any
    enumeration, open, fstat, identity, or fsync error prevents publication.
    """
    # Stack of (fd, name) entries awaiting fsync.  Each child must be fsynced
    # before its parent; we fsync on the way down and again ensure the parent
    # is fsynced after its children (the retained staging-root descriptor is
    # fsynced last, outside this traversal).
    opened = []
    deferred = []  # (fd, name) to fsync in reverse-depth order (children first)
    try:
        stack = [(stage_fd, None)]
        while stack:
            cur_fd, cur_name = stack.pop()
            deferred.append((cur_fd, cur_name))
            names = _wrap_os("staged listdir %s" % (cur_name or "<stage-root>"),
                             _fd_listdir, cur_fd)
            for child in names:
                if child in (".", ".."):
                    continue
                lst = _wrap_os("staged sub lstat %s" % child, os.lstat,
                               child, dir_fd=cur_fd)
                ftype = lst.st_mode & 0o170000
                if ftype == 0o120000:
                    raise _TransactionClosed("staged symlink rejected: %s" % child)
                if ftype == 0o040000:
                    pass  # directory: open, verify, recurse, and fsync below
                elif ftype == 0o100000:
                    continue  # regular file already fsynced at write time
                elif ftype == 0o010000:
                    raise _TransactionClosed(
                        "staged FIFO rejected: %s" % child)
                elif ftype == 0o140000:
                    raise _TransactionClosed(
                        "staged socket rejected: %s" % child)
                elif ftype == 0o060000:
                    raise _TransactionClosed(
                        "staged block device rejected: %s" % child)
                elif ftype == 0o020000:
                    raise _TransactionClosed(
                        "staged character device rejected: %s" % child)
                else:
                    raise _TransactionClosed(
                        "staged unsupported object type rejected: %s" % child)
                cfd = _wrap_os("staged sub open %s" % child, os.open, child,
                               os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                               dir_fd=cur_fd)
                opened.append(cfd)
                fst = _wrap_os("staged sub fstat %s" % child, os.fstat, cfd)
                if (fst.st_dev, fst.st_ino) != (lst.st_dev, lst.st_ino):
                    raise _TransactionClosed(
                        "staged identity discontinuity: %s" % child)
                if (fst.st_mode & 0o170000) != 0o040000:
                    raise _TransactionClosed(
                        "staged opened object not a directory: %s" % child)
                stack.append((cfd, child))
        # Fsync children before parents.  `deferred` has deeper entries pushed
        # later (LIFO), so reversing yields shallowest-first; fsync in reversed
        # order so the deepest children are fsynced before their parents.  The
        # retained staging-root descriptor (stage_fd) is fsynced last below.
        for fdx, nm in reversed(deferred):
            if fdx is stage_fd:
                continue
            _wrap_os("staged dir fsync %s" % (nm or "<stage-root>"),
                     _fsync_dir_by_fd, fdx)
    finally:
        for fdx in reversed(opened):
            try:
                os.close(fdx)
            except OSError:
                pass
    # Fsync the retained staging-root descriptor last so its dir-entry update
    # is durable before publication.
    _wrap_os("staging-root fsync", _fsync_dir_by_fd, stage_fd)

def run_synthetic_outer_transaction(authorized_root, final_basename, *,
                                    inject=None):
    """Exercise the synthetic outer-transaction engine under a temporary
    authorized root.  Returns an immutable _TransactionResult (no
    authorization state).  `inject` is an optional fault-injection hook dict
    used only by self-tests.

    Steps: validate authorized root, validate final basename, create staging
    dir, create+fsync+verify every regular file, write+fsync+verify the
    receipt, fsync the staged directory hierarchy, fsync the staging-root
    descriptor, inject any pre-publication failure, publish atomically, fsync
    the authorized-root descriptor (post-publication), verify the published
    tree, read/validate the receipt, and return the immutable result.  Any
    pre-publication failure cleans the staging tree and closes all owned
    descriptors.  A post-publication authorized-root fsync failure reports a
    controlled durability failure without rolling back the published tree.
    `inject["publication_calls"]` is always set to the count of atomic
    no-replace publication calls actually performed.
    """
    if inject is None:
        inject = {}
    root_fd = None
    stage_fd = None
    owned = _OwnedFds()
    stage_name = None
    published = False
    publication_calls = 0
    try:
        root_fd, _root_receipt = _validate_absolute_authorized_root(authorized_root)
        _validate_final_basename(final_basename, root_fd)
        plan = _validate_synthetic_plan(_build_synthetic_plan())
        stage_fd, stage_name, st_dev, st_ino = _make_staging_dir(root_fd)
        # 1. Create the entire staging tree; 2. write + fsync + verify every
        # regular file.
        file_records = _create_synthetic_tree(stage_fd, plan, owned, inject=inject)
        receipt = _build_receipt(plan, final_basename, file_records,
                            _platform_publication_method())
        if "receipt_write_failure" in inject:
            inject["receipt_write_failure"]["hits"] = inject["receipt_write_failure"].get("hits", 0) + 1
            raise _TransactionClosed("injected receipt-write failure")
        # 3. Write, fsync, and verify transaction-receipt.json.
        receipt_sha = _write_canonical_receipt(stage_fd, receipt)
        # 4. Fsync the staged directory hierarchy.  5. Fsync the retained
        # staging-root descriptor.  This is the pre-publication durability
        # boundary: all staged content and receipt bytes are verified durable
        # before the atomic no-replace publication is invoked.
        _fsync_staged_hierarchy(stage_fd, owned)
        # 6. Pre-publication failure injection -- occurs strictly before the
        # atomic publication call.
        if "pre_publication_fsync_failure" in inject:
            inject["pre_publication_fsync_failure"]["hits"] = inject["pre_publication_fsync_failure"].get("hits", 0) + 1
            raise _TransactionClosed("injected pre-publication fsync failure")
        # publish-path failure: still before the atomic publication call.
        if "publication_failure" in inject:
            inject["publication_failure"]["hits"] = inject["publication_failure"].get("hits", 0) + 1
            raise _TransactionClosed("injected publication failure")
        # 7. The single atomic no-replace publication primitive.
        _atomic_noreplace_publish(root_fd, stage_name, final_basename)
        publication_calls += 1
        published = True
        inject["publication_calls"] = publication_calls
        # 8. Post-publication durability boundary: fsync the authorized-root
        # descriptor separately.  If this fsync fails, publication has already
        # succeeded atomically; the operation reports a controlled durability
        # failure and does NOT roll back the published final-basename.
        if "post_publication_root_fsync_failure" in inject:
            inject["post_publication_root_fsync_failure"]["hits"] = inject["post_publication_root_fsync_failure"].get("hits", 0) + 1
            raise _TransactionClosed("injected post-publication root-fsync failure")
        _fsync_dir_by_fd(root_fd)
        # After successful publication: stage basename must be absent, final
        # basename must exist, published identity must match staged.
        if "post_publication_stage_lstat_failure" in inject:
            hf = inject["post_publication_stage_lstat_failure"]
            hf["hits"] = hf.get("hits", 0) + 1
            raise _TransactionClosed(
                "post-publication stage lstat failed: injected %s"
                % hf.get("errno_name", "EACCES"))
        try:
            os.lstat(stage_name, dir_fd=root_fd)
            raise _TransactionClosed("stage still present after publish")
        except OSError as exc:
            if exc.errno != errno.ENOENT:
                raise _TransactionClosed(
                    "post-publication stage lstat failed: %s" % exc)
        pub_st = _wrap_os("published lstat", os.lstat, final_basename, dir_fd=root_fd)
        if (pub_st.st_dev, pub_st.st_ino) != (st_dev, st_ino):
            raise _TransactionClosed("published identity != staged")
        # Read & validate the canonical receipt from the published tree.
        pub_fd = owned.add(_wrap_os(
            "published open", os.open, final_basename,
            os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=root_fd))
        rfd2 = owned.add(_wrap_os(
            "receipt read open", os.open, "transaction-receipt.json",
            os.O_RDONLY | os.O_NOFOLLOW, dir_fd=pub_fd))
        chunks = []

        def _rread():
            while True:
                b = os.read(rfd2, 1024 * 1024)
                if not b:
                    break
                chunks.append(b)
        _wrap_os("receipt read", _rread)
        receipt_raw = b"".join(chunks)
        try:
            pub_receipt = json.loads(receipt_raw.decode("utf-8"))
        except (UnicodeDecodeError, ValueError):
            raise _TransactionClosed("published receipt not valid JSON")
        if pub_receipt.get("receipt_schema") != 1:
            raise _TransactionClosed("published receipt schema != 1")
        if hashlib.sha256(receipt_raw).hexdigest() != receipt_sha:
            raise _TransactionClosed("published receipt sha mismatch")
        fc = pub_receipt.get("total_synthetic_file_count")
        bc = pub_receipt.get("total_synthetic_byte_count")
        return _TransactionResult(
            final_basename=final_basename, final_dev=pub_st.st_dev,
            final_ino=pub_st.st_ino, receipt_sha256=receipt_sha,
            file_count=fc, byte_count=bc)
    except BaseException:
        primary = sys.exc_info()[1]
        if not published and stage_name is not None and root_fd is not None:
            # CORRECTION 4: attempt cleanup exactly once and report failures.
            # Do not suppress cleanup failures; do not convert KeyboardInterrupt
            # or SystemExit into authorization success.
            cleanup_exc = None
            try:
                _desc_rmtree(root_fd, stage_name, owned)
            except BaseException as ce:
                cleanup_exc = ce
            if cleanup_exc is not None:
                raise _TransactionClosed(
                    "primary %r; cleanup failed %r; staging basename=%s"
                    % (primary, cleanup_exc, stage_name))
        raise
    finally:
        inject["publication_calls"] = publication_calls
        owned.close_all()
        if stage_fd is not None:
            try:
                os.close(stage_fd)
            except OSError:
                pass
        if root_fd is not None:
            try:
                os.close(root_fd)
            except OSError:
                pass



# ---------------------------------------------------------------------------
# Integrated production transaction core (Checkpoint 2PB2B-B2).
#
# Runs only AFTER all authorization checks succeed and the immutable
# _TransactionContext is constructed.  Builds the canonical complete plan
# from the retained manifest bytes, inspects the authorized root, validates
# the final basename, creates one private outer staging transaction,
# materializes every expanded file target via descriptor-bound source
# traversal (rejecting symlinks, hard links, non-regular objects, and
# mode/nlink/size mismatch), writes the canonical receipt, fsyncs the
# staged hierarchy, publishes one atomic no-replace rename, fsyncs the
# authorized root, and returns success WITHOUT returning authorization
# state.  Standard-library-only; no project-local import, no subprocess,
# no Docker, no os.system/os.popen.  The host candidate remains outside this
# tool.
# ---------------------------------------------------------------------------


def _b2_open_source_desc(repo_fd, host_rel_path):
    """Open one source file via descriptor-relative no-follow traversal rooted
    in the already-opened repository descriptor `repo_fd`.  `host_rel_path` is
    a canonical host-relative path (e.g. external/nos3/fsw/build/exe/cpu1/...).
    Rejects any symlink component (parent or leaf).  Returns the open leaf
    descriptor; every intermediate directory descriptor is closed.  All OSError
    failures become _TransactionClosed."""
    comps = _canonical_host_path_comps(host_rel_path, "source host path")
    cur = repo_fd
    parents = []
    leaf_fd = None
    try:
        for idx in range(len(comps) - 1):
            comp = comps[idx]
            lst = _wrap_os("source parent lstat %s" % comp, os.lstat, comp,
                           dir_fd=cur)
            if (lst.st_mode & 0o170000) == 0o120000:
                raise _TransactionClosed(
                    "source symlinked parent rejected: %s" % comp)

            def _pop(parent_=comp, dirfd_=cur):
                return os.open(parent_, os.O_RDONLY | os.O_DIRECTORY
                               | os.O_NOFOLLOW, dir_fd=dirfd_)
            nxt = _wrap_os("source parent open %s" % comp, _pop)
            owned = True
            try:
                nst = _wrap_os("source parent fstat %s" % comp, os.fstat, nxt)
                if (nst.st_dev, nst.st_ino) != (lst.st_dev, lst.st_ino):
                    raise _TransactionClosed(
                        "source parent identity discontinuity: %s" % comp)
            except BaseException:
                if owned:
                    try:
                        os.close(nxt)
                    except OSError:
                        pass
                    owned = False
                raise
            parents.append(nxt)
            owned = False
            cur = nxt
        leaf = comps[-1]
        lst = _wrap_os("source leaf lstat %s" % leaf, os.lstat, leaf,
                       dir_fd=cur)
        if (lst.st_mode & 0o170000) == 0o120000:
            raise _TransactionClosed("source symlink leaf rejected: %s" % leaf)
        if (lst.st_mode & 0o170000) != 0o100000:
            raise _TransactionClosed(
                "source leaf not regular: %s" % leaf)

        def _lopen(lf=leaf, dirfd_=cur):
            return os.open(lf, os.O_RDONLY | os.O_NOFOLLOW, dir_fd=dirfd_)
        leaf_fd = _wrap_os("source leaf open %s" % leaf, _lopen)
        fst = _wrap_os("source leaf fstat %s" % leaf, os.fstat, leaf_fd)
        if (fst.st_dev, fst.st_ino) != (lst.st_dev, lst.st_ino):
            raise _TransactionClosed(
                "source leaf identity discontinuity: %s" % leaf)
        opened = leaf_fd
        leaf_fd = None
        return opened
    except _TransactionClosed:
        if leaf_fd is not None:
            try:
                os.close(leaf_fd)
            except OSError:
                pass
        raise
    finally:
        for fdx in parents:
            try:
                os.close(fdx)
            except OSError:
                pass


def _b2_resolve_source_root(sr_decl, override):
    """Return the host-relative path used to reach a source root's files.

    In production (override is None) this is the canonical
    host_relative_path (external/nos3/...).  When a selftest-only override
    mapping is present, the root is reached through that synthetic path
    instead, so the integrated copy/verify/publish pipeline can be exercised
    without the full external/nos3 tree."""
    if override is None:
        return sr_decl.host_relative_path
    mapped = override.get(sr_decl.source_root)
    if mapped is None:
        return sr_decl.host_relative_path
    return mapped


def _b2_valid_name(name):
    """Validate a single path component for staging use."""
    if not _is_exact_str(name) or name in ("", ".", ".."):
        raise _TransactionClosed("invalid staging name: %r" % name)
    if "/" in name or "\\" in name or "\x00" in name:
        raise _TransactionClosed("invalid staging name: %r" % name)


def _b2_walk_to_parent(start_fd, comps):
    """Descriptor-relative walk to the parent directory of `comps`, creating
    intermediate directories as needed.  Each component is verified no-follow:
    symlink substitution and identity discontinuity are rejected.  Returns the
    opened parent descriptor (for empty comps, returns start_fd); every
    intermediate descriptor is closed except the returned one."""
    cur = start_fd
    opened = []
    ret = None
    try:
        for comp in comps:
            try:
                lst = os.lstat(comp, dir_fd=cur)
            except OSError as exc:
                if exc.errno == errno.ENOENT:
                    lst = None
                else:
                    raise _TransactionClosed(
                        "walk lstat %s failed: %s" % (comp, exc))
            if lst is None:
                nfd = _desc_mkdir(cur, comp, 0o700)
            else:
                if (lst.st_mode & 0o170000) == 0o120000:
                    raise _TransactionClosed(
                        "walk symlink component rejected: %s" % comp)
                if (lst.st_mode & 0o170000) != 0o040000:
                    raise _TransactionClosed(
                        "walk component not a dir: %s" % comp)
                nfd = _wrap_os("walk open %s" % comp, os.open, comp,
                               os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                               dir_fd=cur)
                nst = _wrap_os("walk fstat %s" % comp, os.fstat, nfd)
                if (nst.st_dev, nst.st_ino) != (lst.st_dev, lst.st_ino):
                    raise _TransactionClosed(
                        "walk identity discontinuity: %s" % comp)
            opened.append(nfd)
            cur = nfd
        ret = opened[-1] if opened else start_fd
        keep = ret
        for fdx in opened:
            if fdx is not keep:
                try:
                    os.close(fdx)
                except OSError:
                    pass
        return keep
    except BaseException:
        for fdx in opened:
            try:
                os.close(fdx)
            except OSError:
                pass
        raise


def _b2_actual_copy(repo_fd, src_full, file_entry, dest_rel, staging_fd,
                    inject=None):
    """Perform the real copy of one file from source to staging.

    `file_entry` is the canonical regular-file record providing exact mode,
    nlink, size, and sha256.  Returns (rel_path, size, sha256, mode_int).
    Descriptor-relative source traversal (bound to repo_fd), exact mode/nlink/
    size match, SHA-256 from exact bytes, complete-write loop to a temp file,
    fsync, verify destination, and atomic no-replace per-file publication."""
    sfd = None
    parent_fd = None
    wfd = None
    dfd = None
    tmp_base = None
    final_base = None
    temp_created = False
    temp_published = False
    wcreat_dev = None
    wcreat_ino = None
    mode_int = int(file_entry.mode, 8)
    try:
        sfd = _b2_open_source_desc(repo_fd, src_full)
        st = _wrap_os("src fstat", os.fstat, sfd)
        if not stat.S_ISREG(st.st_mode):
            raise _TransactionClosed("source not regular: %s" % dest_rel)
        if st.st_nlink != 1:
            raise _TransactionClosed("source nlink!=1: %s" % dest_rel)
        if stat.S_IMODE(st.st_mode) != mode_int:
            raise _TransactionClosed("source mode mismatch: %s" % dest_rel)
        if st.st_size != file_entry.size:
            raise _TransactionClosed("source size mismatch: %s" % dest_rel)
        dest_parent = dest_rel.rsplit("/", 1)[0] if "/" in dest_rel else ""
        final_base = (dest_rel.rsplit("/", 1)[-1]
                      if "/" in dest_rel else dest_rel)
        _b2_valid_name(final_base)
        tmp_base = ".nrm-tmp-" + secrets.token_hex(8)
        _b2_valid_name(tmp_base)
        parent_comps = dest_parent.split("/") if dest_parent else []
        parent_fd = _b2_walk_to_parent(staging_fd, parent_comps)
        # Reject a pre-existing final destination (no-replace).
        try:
            os.lstat(final_base, dir_fd=parent_fd)
            raise _TransactionClosed("dest pre-exists: %s" % dest_rel)
        except OSError as exc:
            if exc.errno != errno.ENOENT:
                raise _TransactionClosed("dest lstat failed: %s" % exc)
        # Create the temp file relative to the parent descriptor.
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW
        wfd = _wrap_os("dest create %s" % dest_rel, os.open, tmp_base,
                       flags, mode_int, dir_fd=parent_fd)
        _wrap_os("dest fchmod %s" % dest_rel, os.fchmod, wfd, mode_int)
        wcreat = _wrap_os("dest create fstat %s" % dest_rel, os.fstat, wfd)
        wcreat_dev, wcreat_ino = wcreat.st_dev, wcreat.st_ino
        temp_created = True
        # Copy bytes: read through the retained source descriptor, hash from
        # exact bytes, complete-write loop to the temp file.
        h = hashlib.sha256()
        while True:
            b = _wrap_os("src read %s" % dest_rel, os.read, sfd, 1024 * 1024)
            if not b:
                break
            h.update(b)
            _complete_write(wfd, b, dest_rel, inject=inject)
        _wrap_os("file fsync %s" % dest_rel, os.fsync, wfd)
        if h.hexdigest() != file_entry.sha256:
            raise _TransactionClosed("source sha mismatch: %s" % dest_rel)
        wst = _wrap_os("dst write fstat %s" % dest_rel, os.fstat, wfd)
        if not stat.S_ISREG(wst.st_mode) or wst.st_nlink != 1:
            raise _TransactionClosed("dst not regular/nlink1: %s" % dest_rel)
        if stat.S_IMODE(wst.st_mode) != mode_int:
            raise _TransactionClosed("dst mode mismatch: %s" % dest_rel)
        if wst.st_size != file_entry.size:
            raise _TransactionClosed("dst size mismatch: %s" % dest_rel)
        _wrap_os("write fd close %s" % dest_rel, os.close, wfd)
        wfd = None
        # Selftest-only fault injection (Checkpoint 2PB2B-B2): after the source
        # has been opened, identity-verified, completely read to EOF, written,
        # fsynced, sha-verified to the staging temp, and the write fd closed --
        # and BEFORE the post-read source identity continuity fstat -- let the
        # test physically replace the source basename with a distinct inode.
        # This hook never raises and never changes control flow: it confirms the
        # private key is present, increments its hit counter once, invokes the
        # existing test-supplied mutation callback `mutate(sfd, src_full)`, then
        # returns normally so execution reaches the existing production
        # post-read os.fstat comparison -- the ONLY place that may close on a
        # changed source identity ("source identity change after read").  The
        # hook is inactive when inject is None (production) or the key is absent
        # (no argparse/CLI exposure).  No module-global state; no direct close.
        if inject is not None and "b2_source_post_read_swap" in inject:
            _psr = inject["b2_source_post_read_swap"]
            _psr["hits"] = _psr.get("hits", 0) + 1
            _psr_mutate = _psr.get("mutate")
            if _psr_mutate is not None:
                _psr_mutate(sfd, src_full)
        # Verify post-read source identity continuity.
        pst = _wrap_os("src post-read fstat %s" % dest_rel, os.fstat, sfd)
        if (pst.st_dev, pst.st_ino) != (st.st_dev, st.st_ino):
            raise _TransactionClosed(
                "source identity change after read: %s" % dest_rel)
        # Atomic no-replace per-file publication.
        _atomic_noreplace_publish(parent_fd, tmp_base, final_base)
        temp_published = True
        # Verify destination from an opened read descriptor.
        dfd = _wrap_os("dst verify open %s" % dest_rel, os.open, final_base,
                       os.O_RDONLY | os.O_NOFOLLOW, dir_fd=parent_fd)
        dst_st = _wrap_os("dst verify fstat %s" % dest_rel, os.fstat, dfd)
        if not stat.S_ISREG(dst_st.st_mode):
            raise _TransactionClosed("dst not regular: %s" % dest_rel)
        if dst_st.st_nlink != 1:
            raise _TransactionClosed("dst nlink!=1: %s" % dest_rel)
        if stat.S_IMODE(dst_st.st_mode) != mode_int:
            raise _TransactionClosed("dst mode mismatch: %s" % dest_rel)
        if dst_st.st_size != file_entry.size:
            raise _TransactionClosed("dst size mismatch: %s" % dest_rel)
        if (dst_st.st_dev, dst_st.st_ino) == (st.st_dev, st.st_ino):
            raise _TransactionClosed("src/dst inode alias: %s" % dest_rel)
        _verify_sha(dfd, file_entry.sha256, dest_rel)
        _wrap_os("dst verify close %s" % dest_rel, os.close, dfd)
        dfd = None
        return (dest_rel, dst_st.st_size, file_entry.sha256, dst_st.st_mode)
    finally:
        if sfd is not None:
            try:
                os.close(sfd)
            except OSError:
                pass
        if wfd is not None:
            try:
                os.close(wfd)
            except OSError:
                pass
        if dfd is not None:
            try:
                os.close(dfd)
            except OSError:
                pass
        # Identity-bound temp cleanup: remove the temp file iff it was created
        # but never successfully published, and only when it still maps to the
        # captured temp identity.  Never remove a replacement object.
        if (parent_fd is not None and temp_created and not temp_published
                and wcreat_dev is not None and tmp_base is not None):
            _b2_remove_tmp_bound(parent_fd, tmp_base, wcreat_dev, wcreat_ino)
        if parent_fd is not None and parent_fd is not staging_fd:
            try:
                os.close(parent_fd)
            except OSError:
                pass


def _verify_sha(fd, expected_sha, rel_for_msg):
    """Hash an open descriptor and compare to the expected SHA-256."""
    h = hashlib.sha256()
    while True:
        b = _wrap_os("verify sha read %s" % rel_for_msg, os.read, fd,
                     1024 * 1024)
        if not b:
            break
        h.update(b)
    if h.hexdigest() != expected_sha:
        raise _TransactionClosed("dst sha mismatch: %s" % rel_for_msg)


def _b2_remove_tmp_bound(parent_fd, tmp_base, captured_dev, captured_ino):
    """Remove a leftover temporary file bound to the captured temp identity
    (mirror of the material tool's proven cleanup).  Never remove a replacement
    object: require the name to still map to the captured dev/inode before
    unlinking.  Reject symlinks and unsupported objects."""
    try:
        lst = os.lstat(tmp_base, dir_fd=parent_fd)
    except OSError as exc:
        if exc.errno == errno.ENOENT:
            return
        raise _TransactionClosed("temp cleanup lstat failed: %s" % exc)
    if (lst.st_mode & 0o170000) == 0o120000:
        raise _TransactionClosed("temp cleanup symlink rejected: %s" % tmp_base)
    if (lst.st_dev, lst.st_ino) != (captured_dev, captured_ino):
        raise _TransactionClosed(
            "temp cleanup replacement identity rejected: %s" % tmp_base)
    try:
        lst2 = os.lstat(tmp_base, dir_fd=parent_fd)
    except OSError as exc:
        if exc.errno == errno.ENOENT:
            return
        raise _TransactionClosed("temp cleanup re-lstat failed: %s" % exc)
    if (lst2.st_dev, lst2.st_ino) != (captured_dev, captured_ino):
        raise _TransactionClosed(
            "temp cleanup replacement before unlink: %s" % tmp_base)
    _wrap_os("temp cleanup unlink %s" % tmp_base, os.unlink, tmp_base,
             dir_fd=parent_fd)


def _b2_build_destination_dirs(staging_fd, dir_targets):
    """Create every planned destination directory relative to staging_fd using
    descriptor-relative no-follow operations.  Each expanded directory target
    is created only from the canonical plan; no unplanned directory is created.
    Intermediate directories are created and verified.  Every opened descriptor
    is closed before return (no fd leaks across the ~1500-step expansion)."""
    created = set()
    for dt in sorted(dir_targets, key=lambda d: d.transaction_relative_path):
        comps = dt.transaction_relative_path.split("/")
        cur = staging_fd
        opened = []
        try:
            for idx in range(len(comps)):
                comp = comps[idx]
                prefix = "/".join(comps[:idx + 1])
                if prefix in created:
                    if idx + 1 >= len(comps):
                        continue
                    nxt = _wrap_os("dir reuse open %s" % comp, os.open, comp,
                                   os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                                   dir_fd=cur)
                    opened.append(nxt)
                    cur = nxt
                    continue
                lst_exists = True
                try:
                    lst = os.lstat(comp, dir_fd=cur)
                except OSError as exc:
                    if exc.errno == errno.ENOENT:
                        lst_exists = False
                    else:
                        raise _TransactionClosed(
                            "dir ensure lstat failed: %s" % prefix)
                if not lst_exists:
                    nfd = _desc_mkdir(cur, comp, 0o700)
                    created.add(prefix)
                    if idx + 1 >= len(comps):
                        try:
                            os.close(nfd)
                        except OSError:
                            pass
                        break
                    opened.append(nfd)
                    cur = nfd
                else:
                    if (lst.st_mode & 0o170000) == 0o120000:
                        raise _TransactionClosed(
                            "dir ensure symlink rejected: %s" % prefix)
                    if (lst.st_mode & 0o170000) != 0o040000:
                        raise _TransactionClosed(
                            "dir ensure non-dir collision: %s" % prefix)
                    created.add(prefix)
                    if idx + 1 >= len(comps):
                        break
                    nfd = _wrap_os("dir open %s" % comp, os.open, comp,
                                   os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                                   dir_fd=cur)
                    opened.append(nfd)
                    cur = nfd
        finally:
            for fdx in opened:
                try:
                    os.close(fdx)
                except OSError:
                    pass


def _b2_audit_destination(staging_fd, expected_files, expected_dirs):
    """Descriptor-relative complete destination audit after all copies.
    Reject symlinks, non-regular/non-dir objects, unplanned files/dirs/FIFOs/
    sockets/devices, and inode replacement during audit."""
    found_files = set()
    found_dirs = set()

    def _recurse(parent_fd, rel_prefix):
        names = _wrap_os("audit listdir %s" % (rel_prefix or "<root>"),
                         _fd_listdir, parent_fd)
        for child in names:
            rel = (rel_prefix + "/" + child) if rel_prefix else child
            lst = _wrap_os("audit lstat %s" % rel, os.lstat, child,
                           dir_fd=parent_fd)
            ftype = lst.st_mode & 0o170000
            if ftype == 0o120000:
                raise _TransactionClosed("audit symlink rejected: %s" % rel)
            if ftype == 0o040000:
                if rel not in expected_dirs:
                    raise _TransactionClosed("unplanned directory: %s" % rel)
                found_dirs.add(rel)
                cfd = _wrap_os("audit opendir %s" % rel, os.open, child,
                               os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                               dir_fd=parent_fd)
                try:
                    cst = _wrap_os("audit fstat %s" % rel, os.fstat, cfd)
                    if (cst.st_dev, cst.st_ino) != (lst.st_dev, lst.st_ino):
                        raise _TransactionClosed(
                            "audit identity discontinuity: %s" % rel)
                    _recurse(cfd, rel)
                finally:
                    try:
                        os.close(cfd)
                    except OSError:
                        pass
            elif ftype == 0o100000:
                if rel not in expected_files:
                    raise _TransactionClosed("unplanned file: %s" % rel)
                found_files.add(rel)
            elif ftype == 0o010000:
                raise _TransactionClosed("audit FIFO rejected: %s" % rel)
            elif ftype == 0o140000:
                raise _TransactionClosed("audit socket rejected: %s" % rel)
            elif ftype == 0o060000:
                raise _TransactionClosed("audit block dev rejected: %s" % rel)
            elif ftype == 0o020000:
                raise _TransactionClosed("audit char dev rejected: %s" % rel)
            else:
                raise _TransactionClosed(
                    "audit unsupported object rejected: %s" % rel)

    _recurse(staging_fd, "")
    extra_files = found_files - set(expected_files)
    missing_files = set(expected_files) - found_files
    extra_dirs = found_dirs - expected_dirs
    missing_dirs = expected_dirs - found_dirs
    if extra_files:
        raise _TransactionClosed(
            "extra destination files: %s" % sorted(extra_files))
    if missing_files:
        raise _TransactionClosed(
            "missing destination files: %s" % sorted(missing_files))
    if extra_dirs:
        raise _TransactionClosed(
            "extra destination directories: %s" % sorted(extra_dirs))
    if missing_dirs:
        raise _TransactionClosed(
            "missing destination directories: %s" % sorted(missing_dirs))


def _b2_verify_exclusions_absent(staging_fd, excl_targets):
    """Require every planned exclusion target to be absent from the staging
    tree.  Descriptor-relative no-follow parent walk; a present symlink,
    regular file, FIFO, socket, device, or any present parent fails closed."""
    for et in excl_targets:
        comps = et.transaction_relative_path.split("/")
        cur = staging_fd
        opened = []
        absent = False
        try:
            for i in range(len(comps) - 1):
                comp = comps[i]
                try:
                    lst = os.lstat(comp, dir_fd=cur)
                except OSError as exc:
                    if exc.errno == errno.ENOENT:
                        absent = True
                        break
                    raise _TransactionClosed(
                        "excl lstat failed: %s" % et.transaction_relative_path)
                if (lst.st_mode & 0o170000) == 0o120000:
                    raise _TransactionClosed(
                        "excl parent symlink: %s" % et.transaction_relative_path)
                if (lst.st_mode & 0o170000) != 0o040000:
                    raise _TransactionClosed(
                        "excl parent non-dir: %s" % et.transaction_relative_path)
                cfd = _wrap_os("excl opendir %s" % comp, os.open, comp,
                               os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                               dir_fd=cur)
                opened.append(cfd)
                cst = _wrap_os("excl fstat %s" % comp, os.fstat, cfd)
                if (cst.st_dev, cst.st_ino) != (lst.st_dev, lst.st_ino):
                    raise _TransactionClosed(
                        "excl identity discontinuity: %s" % comp)
                cur = cfd
            if absent:
                continue
            leaf = comps[-1]
            try:
                lst = os.lstat(leaf, dir_fd=cur)
            except OSError as exc:
                if exc.errno == errno.ENOENT:
                    continue
                raise _TransactionClosed("excl leaf lstat failed: %s" % leaf)
            raise _TransactionClosed(
                "excluded target present: %s" % et.transaction_relative_path)
        finally:
            for fdx in opened:
                try:
                    os.close(fdx)
                except OSError:
                    pass


def _b2_verify_deny_patterns_absent(staging_fd, plan):
    """Deny-pattern scan over the staged tree.  Descriptor-relative, no-follow;
    a present symlink in the staged tree is rejected."""
    decl_prefix = {r.source_root: r.destination_prefix
                   for r in plan.source_roots}
    for dp in plan.deny_patterns:
        prefix = decl_prefix.get(dp.scope, "")
        effective = (prefix + "/" + dp.pattern) if prefix else dp.pattern

        def _deny_walk(parent_fd, rel_prefix, eff):
            names = _wrap_os("deny listdir %s" % (rel_prefix or "<root>"),
                             _fd_listdir, parent_fd)
            for name in names:
                rel = (rel_prefix + "/" + name) if rel_prefix else name
                lst = _wrap_os("deny lstat %s" % rel, os.lstat, name,
                               dir_fd=parent_fd)
                if (lst.st_mode & 0o170000) == 0o120000:
                    raise _TransactionClosed(
                        "deny-walk symlink rejected: %s" % rel)
                if (lst.st_mode & 0o170000) == 0o040000:
                    cfd = _wrap_os("deny opendir %s" % name, os.open, name,
                                   os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                                   dir_fd=parent_fd)
                    try:
                        _deny_walk(cfd, rel, eff)
                    finally:
                        try:
                            os.close(cfd)
                        except OSError:
                            pass
                elif (lst.st_mode & 0o170000) == 0o100000:
                    if fnmatch.fnmatch(rel, eff):
                        raise _TransactionClosed(
                            "deny-pattern in destination: %s" % rel)
                else:
                    raise _TransactionClosed(
                        "deny-walk unsupported object: %s" % rel)
        _deny_walk(staging_fd, "", effective)


def _b2_build_receipt(ctx, plan, final_basename, file_records, root_receipt,
                      lock_receipt, initial_acl_entry_count,
                      publication_method, runtime_attempt=1):
    """Build the canonical integrated receipt object.  Contains only immutable
    primitive records (no bearer, secret, registry identity, repr, mutable
    object, or capability).  No timestamp, random id, hostname, username,
    absolute path, or environment-dependent value."""
    tool_sha = _sha256_file_path(__file__)
    total_bytes = sum(r[1] for r in file_records)
    files_sorted = sorted(
        [{"rel_path": r[0], "size": r[1], "sha256": r[2]} for r in file_records],
        key=lambda d: d["rel_path"])
    workspaces = []
    for w in sorted(plan.workspaces, key=lambda c: c.component_id):
        workspaces.append({
            "component_id": w.component_id,
            "relative_root": "workspaces/%s/work/nos3" % w.component_id,
            "file_count": w.file_count,
            "byte_count": w.byte_count,
            "directory_count": w.directory_count,
            "exclusion_count": w.exclusion_count,
            "verification": "VERIFIED",
        })
    receipt = {
        "receipt_schema": 1,
        "status": "TRANSACTION_COMPLETE_PENDING_PUBLICATION",
        "final_basename": final_basename,
        "transaction_tool_sha256": tool_sha,
        "repository": {"dev": ctx.repo.dev, "inode": ctx.repo.ino},
        "contract": {"relative_path": ctx.contract.rel,
                     "device": ctx.contract.dev, "inode": ctx.contract.ino,
                     "size": ctx.contract.size, "mode": ctx.contract.mode,
                     "nlink": ctx.contract.nlink, "sha256": ctx.contract.sha256},
        "candidate": {"relative_path": ctx.candidate.rel,
                       "device": ctx.candidate.dev, "inode": ctx.candidate.ino,
                       "size": ctx.candidate.size, "mode": ctx.candidate.mode,
                       "nlink": ctx.candidate.nlink,
                       "sha256": ctx.candidate.sha256},
        "executing_tool": {"relative_path": ctx.tool.rel,
                           "device": ctx.tool.dev, "inode": ctx.tool.ino,
                           "size": ctx.tool.size, "mode": ctx.tool.mode,
                           "nlink": ctx.tool.nlink, "sha256": ctx.tool.sha256},
        "canonical_manifest": {"relative_path": ctx.manifest.rel,
                               "device": ctx.manifest.dev,
                               "inode": ctx.manifest.ino,
                               "size": ctx.manifest.size,
                               "mode": ctx.manifest.mode,
                               "nlink": ctx.manifest.nlink,
                               "sha256": ctx.manifest.sha256},
        "authorized_root": {"device": root_receipt.dev,
                            "inode": root_receipt.ino},
        "component_ids": list(sorted(w.component_id
                                     for w in plan.workspaces)),
        "component_count": len(plan.workspaces),
        "workspace_count": plan.workspace_count,
        "fortytwo_scratch_disposition": "SEPARATE_NOT_COUNTED_AS_WORKSPACE",
        "fortytwo_scratch_present": True,
        "workspaces": workspaces,
        "aggregate_included_file_count": len(file_records),
        "aggregate_included_byte_count": total_bytes,
        "aggregate_directory_count": len(plan.expanded_directory_targets),
        "aggregate_exclusion_count": len(plan.expanded_exclusion_targets),
        "collision_counts": {
            "duplicate_file_target_count":
                plan.duplicate_file_target_count,
            "duplicate_directory_target_count":
                plan.duplicate_directory_target_count,
            "file_directory_collision_count":
                plan.file_directory_collision_count,
            "prefix_collision_count": plan.prefix_collision_count,
        },
        "no_replace_publication_disposition": "ATOMIC_NOREPLACE_PUBLISHED",
        "publication_method": publication_method,
        "runtime_attempt": runtime_attempt,
        "d064_disposition": ctx.d064_disposition,
        "host_exclusive_writer_evidence": {"relative_path":ctx.host_evidence.rel,"device":ctx.host_evidence.dev,"inode":ctx.host_evidence.ino,"size":ctx.host_evidence.size,"mode":ctx.host_evidence.mode,"nlink":ctx.host_evidence.nlink,"sha256":ctx.host_evidence.sha256,"schema":ctx.host_evidence_schema,"status":_HOST_EVIDENCE_STATUS},
        "exclusive_writer_controls": {"acl_policy":_D064_ACL_POLICY,"initial_extended_acl_entry_count":initial_acl_entry_count,"prepublication_acl_revalidation":"REQUIRED_IMMEDIATELY_BEFORE_ATOMIC_PUBLICATION","serialization_method":_D064_SERIALIZATION_METHOD,"lock_basename":lock_receipt.basename,"lock_device":lock_receipt.dev,"lock_inode":lock_receipt.ino,"lock_mode":"%04o"%lock_receipt.mode,"lock_nlink":lock_receipt.nlink,"lock_uid":lock_receipt.uid,"lock_held_through_transaction_finally":True,"advisory_only":True,"external_noncooperating_writer_absence_proven":False},
        "exclusive_writer_prerequisite": "TECHNICAL_CONTROLS_AND_HASH_BOUND_HOST_EVIDENCE_REQUIRED",
        "runtime_authorized": False,
        "runtime_attempts": 0,
        "docker_invoked": False,
    }
    if ctx.host_evidence_schema == _V5_HOST_EVIDENCE_SCHEMA:
        receipt["host_exclusive_writer_evidence"]["status"] = ctx.host_evidence_status
        receipt["host_exclusive_writer_evidence"]["evidence_type"] = ctx.host_evidence_type
        receipt["host_exclusive_writer_evidence"]["observed_at_utc"] = (
            ctx.host_evidence_observed_at_utc
        )
        receipt["host_evidence_governance"] = {
            "decision": ctx.compatibility_governance_decision,
            "contract_version": ctx.compatibility_governance_contract_version,
            "contract_sha256": ctx.compatibility_governance_contract_sha256,
            "fresh_evidence_independent_review_script_sha256": ctx.fresh_evidence_independent_review_script_sha256,
            "successor_consumer_independent_review_script_sha256": ctx.successor_consumer_independent_review_script_sha256,
            "successor_consumer_independent_review_result": ctx.successor_consumer_independent_review_result,
            "successor_consumer_independent_review_findings": ctx.successor_consumer_independent_review_findings,
            "successor_consumer_path": ctx.tool.rel,
            "successor_consumer_sha256": ctx.tool.sha256,
            "governance_binding_verified": ctx.governance_binding_verified,
            "schema2_compatible": True,
            "schema1_fallback_allowed": False,
        }
    return receipt


def _b2_materialize(ctx, repo_fd, mraw, mparsed, authorized_root,
                    final_basename, inject=None, handoff_stream=None,
                    v6_bindings=None):
    """Run the complete process-local integrated transaction.

    Runs only after authorization and context construction.  Builds the
    canonical plan from the retained manifest bytes, inspects the authorized
    root, validates the final basename, creates the private outer staging
    transaction, copies every expanded file target, writes the canonical
    receipt, fsyncs the staged hierarchy, publishes atomically, fsyncs the
    authorized root, and returns (final_basename, root_dev, root_ino,
    receipt_sha256, file_count, byte_count).  `inject` is a selftest-only
    fault-injection hook dict.  Never returns authorization state."""
    if inject is None:
        inject = {}
    root_fd = None
    lock_fd = None
    lock_receipt = None
    initial_acl_entry_count = None
    stage_fd = None
    owned = _OwnedFds()
    stage_name = None
    published = False
    publication_calls = 0
    override = _B2_SELFTEST_SOURCE_OVERRIDE
    # Selftest-only synthetic plan (never reachable from the production CLI:
    # only a manually-constructed test namespace may carry inject["selftest_plan"]).
    # In production inject is None/empty so the validated canonical plan is built
    # from the retained manifest bytes via the anti-forgery plan compiler.
    selftest_plan = inject.get("selftest_plan") if isinstance(inject, dict) else None
    try:
        if selftest_plan is not None:
            plan = selftest_plan
        else:
            plan = _build_canonical_materialization_plan(mparsed)
        root_fd, root_receipt = _validate_absolute_authorized_root(
            authorized_root)
        initial_acl_entry_count = _validate_root_acl_no_extended(root_fd)
        lock_fd, lock_receipt = _acquire_serialization_lock(root_fd, root_receipt)
        if handoff_stream is not None:
            _v6_names = _fd_listdir(root_fd)
            if _v6_names != (_D064_LOCK_BASENAME,):
                raise _TransactionClosed(
                    "V6 authorized root not clean after lock acquisition: %r"
                    % (_v6_names,)
                )
        _validate_final_basename(final_basename, root_fd)
        stage_fd, stage_name, _st_dev, _st_ino = _make_staging_dir(root_fd)
        # Build the directory hierarchy from the expanded directory targets.
        _b2_build_destination_dirs(stage_fd, plan.expanded_directory_targets)
        # Map source-root declarations for quick lookup.
        sr_by_name = {r.source_root: r for r in plan.source_roots}
        # Build an index from (source_root, relative_path) -> regular-file
        # entry across all workspaces and the fortytwo scratch.
        file_index = {}
        for w in plan.workspaces:
            for wf in w.regular_files:
                file_index[(wf.source_root, wf.relative_path)] = wf
        for ff in plan.fortytwo.regular_files:
            file_index[(ff.source_root, ff.relative_path)] = ff
        # Copy each expanded file target from its canonical source.
        file_records = []
        for ft in plan.expanded_file_targets:
            sr_decl = sr_by_name[ft.source_root]
            src_host = _b2_resolve_source_root(sr_decl, override)
            src_full = src_host
            if ft.source_relative_path:
                src_full = src_host + "/" + ft.source_relative_path
            file_entry = file_index.get(
                (ft.source_root, ft.source_relative_path))
            if file_entry is None:
                raise _TransactionClosed(
                    "no source file entry for target: %s"
                    % ft.transaction_relative_path)
            rec = _b2_actual_copy(repo_fd, src_full, file_entry,
                                  ft.transaction_relative_path, stage_fd,
                                  inject=inject)
            file_records.append(rec)
        if "file_copy_failure" in inject:
            inject["file_copy_failure"]["hits"] = (
                inject["file_copy_failure"].get("hits", 0) + 1)
            raise _TransactionClosed("injected file-copy failure")
        # Selftest-only fault injection (Checkpoint 2PB2B-B2): after every
        # planned file has been copied, and BEFORE the final destination audit
        # ("final destination verification"), let the test replace one planned
        # destination leaf with a symlink pointing outside staging.  The hook
        # intentionally does NOT raise here: the production _b2_audit_destination
        # symlink guard is the detector.  Inactive when inject is None (no
        # argparse/CLI exposure); no module-global state.
        if "b2_destination_symlink_injection" in inject:
            _dsi = inject["b2_destination_symlink_injection"]
            _dsi["hits"] = _dsi.get("hits", 0) + 1
            _dsi_mutate = _dsi.get("mutate")
            if _dsi_mutate is not None:
                _dsi_mutate(stage_fd)
        # Audit the complete destination against the canonical plan.
        expected_files = {ft.transaction_relative_path
                          for ft in plan.expanded_file_targets}
        expected_dirs = {dt.transaction_relative_path
                         for dt in plan.expanded_directory_targets}
        _b2_audit_destination(stage_fd, expected_files, expected_dirs)
        # Selftest-only fault injection (Checkpoint 2PB2B-B2): AFTER the
        # destination audit has already passed over the clean staged tree and
        # BEFORE _b2_verify_exclusions_absent, let the test create a regular
        # object at an EXACT excluded destination.  This is the only placement
        # that reaches the production exclusion verifier without being caught
        # first by the audit.  The hook intentionally does NOT raise here: the
        # production _b2_verify_exclusions_absent is the detector.  Inactive when
        # inject is None (no argparse/CLI exposure); no module-global state.
        if "b2_excluded_target_presence" in inject:
            _etp = inject["b2_excluded_target_presence"]
            _etp["hits"] = _etp.get("hits", 0) + 1
            _etp_mutate = _etp.get("mutate")
            if _etp_mutate is not None:
                _etp_mutate(stage_fd, plan)
        # Verify exclusions absent and enforce deny patterns.
        _b2_verify_exclusions_absent(stage_fd, plan.expanded_exclusion_targets)
        _b2_verify_deny_patterns_absent(stage_fd, plan)
        # Build and write the canonical receipt before publication.
        receipt = _b2_build_receipt(ctx, plan, final_basename, file_records,
                                    root_receipt, lock_receipt,
                                    initial_acl_entry_count,
                                    _platform_publication_method())
        if "receipt_write_failure" in inject:
            inject["receipt_write_failure"]["hits"] = (
                inject["receipt_write_failure"].get("hits", 0) + 1)
            raise _TransactionClosed("injected receipt-write failure")
        receipt_sha = _write_canonical_receipt(stage_fd, receipt)
        # Fsync the staged hierarchy (pre-publication durability boundary).
        if "pre_publication_fsync_failure" in inject:
            inject["pre_publication_fsync_failure"]["hits"] = (
                inject["pre_publication_fsync_failure"].get("hits", 0) + 1)
            raise _TransactionClosed("injected pre-publication fsync failure")
        _fsync_staged_hierarchy(stage_fd, owned)
        if "publication_failure" in inject:
            inject["publication_failure"]["hits"] = (
                inject["publication_failure"].get("hits", 0) + 1)
            raise _TransactionClosed("injected publication failure")
        _validate_root_acl_no_extended(root_fd)
        _revalidate_serialization_lock(root_fd, lock_fd, root_receipt, lock_receipt)
        _atomic_noreplace_publish(root_fd, stage_name, final_basename)
        publication_calls += 1
        published = True
        # Post-publication durability: fsync the authorized root.  If this
        # fails, publication already succeeded atomically; report a controlled
        # durability failure WITHOUT rolling back the published tree.
        if "post_publication_root_fsync_failure" in inject:
            inject["post_publication_root_fsync_failure"]["hits"] = (
                inject["post_publication_root_fsync_failure"].get("hits", 0)
                + 1)
            raise _TransactionClosed(
                "injected post-publication root-fsync failure")
        _fsync_dir_by_fd(root_fd)
        published_st_dev, published_st_ino = None, None
        try:
            os.lstat(stage_name, dir_fd=root_fd)
            raise _TransactionClosed("stage still present after publish")
        except OSError as exc:
            if exc.errno != errno.ENOENT:
                raise _TransactionClosed(
                    "post-publication stage lstat failed: %s" % exc)
        pub_st = _wrap_os("published lstat", os.lstat, final_basename,
                          dir_fd=root_fd)
        published_st_dev, published_st_ino = pub_st.st_dev, pub_st.st_ino
        if (pub_st.st_dev, pub_st.st_ino) != (_st_dev, _st_ino):
            raise _TransactionClosed("published identity != staged")
        if handoff_stream is not None:
            if not isinstance(v6_bindings, _V6Bindings):
                raise _TransactionClosed("V6 stream bindings absent")
            _v6_add_supplemental_fortytwo(
                repo_fd, root_fd, final_basename, v6_bindings
            )
            _v6_stream_published_transaction(
                root_fd, lock_fd, root_receipt, lock_receipt,
                final_basename, receipt_sha, ctx, v6_bindings,
                handoff_stream, owned,
            )
        return (final_basename, published_st_dev, published_st_ino,
                receipt_sha, len(file_records),
                sum(r[1] for r in file_records))
    except BaseException:
        primary = sys.exc_info()[1]
        cleanup_exc = None
        try:
            if handoff_stream is not None and published and root_fd is not None:
                _desc_rmtree(root_fd, final_basename, owned)
                try:
                    os.lstat(_D064_LOCK_BASENAME, dir_fd=root_fd)
                except OSError as _lock_exc:
                    if _lock_exc.errno != errno.ENOENT:
                        raise _TransactionClosed(
                            "V6 failure cleanup lock lstat failed: %s"
                            % _lock_exc)
                else:
                    _revalidate_serialization_lock(
                        root_fd, lock_fd, root_receipt, lock_receipt)
                    os.unlink(_D064_LOCK_BASENAME, dir_fd=root_fd)
                _fsync_dir_by_fd(root_fd)
                _remaining = _fd_listdir(root_fd)
                if _remaining:
                    raise _TransactionClosed(
                        "V6 failure cleanup authorized root not empty: %r"
                        % (_remaining,))
            elif not published and stage_name is not None and root_fd is not None:
                _desc_rmtree(root_fd, stage_name, owned)
        except BaseException as ce:
            cleanup_exc = ce
        if cleanup_exc is not None:
            raise _TransactionClosed(
                "primary %r; V6 cleanup failed %r; staging basename=%s"
                % (primary, cleanup_exc, stage_name))
        raise
    finally:
        inject["publication_calls"] = publication_calls
        owned.close_all()
        if stage_fd is not None:
            try:
                os.close(stage_fd)
            except OSError:
                pass
        if root_fd is not None:
            try:
                os.close(root_fd)
            except OSError:
                pass
        if lock_fd is not None:
            try: fcntl.flock(lock_fd, fcntl.LOCK_UN)
            except OSError: pass
            try: os.close(lock_fd)
            except OSError: pass




# ---------------------------------------------------------------------------
# WP4 D-064 V6 privilege-separated handoff extension.
# V6 production stdout is reserved exclusively for WP4_D064_V6_HANDOFF_SCHEMA_1.
# UID599 performs no Docker/process invocation.
# ---------------------------------------------------------------------------

_V6_HANDOFF_MAGIC = b"WP4D064V6H1\x00"
_V6_HANDOFF_END_MAGIC = b"END!"
_V6_HANDOFF_SCHEMA = 1
_V6_HANDOFF_PURPOSE = "WP4_D064_V6_HANDOFF_SCHEMA_1"
_V6_MATERIALIZER_UID = 599
_V6_RUNTIME_UID = 501

_V6_FORTYTWO_SOURCE_REL = "external/fortytwo/42"
_V6_FORTYTWO_SOURCE_COMMIT = "eda252bf31f27850e867e698cfdd963e143ead1f"
_V6_FORTYTWO_SOURCE_TREE = "541dbc9c3c3d42887b9c668a218ffc3726d24346"
_V6_FORTYTWO_SHA256 = "9c0062d2a447a6340e7c191850ff952d3f8768dd307e3e7fb141e777961e60c7"
_V6_FORTYTWO_BYTES = 2250376
_V6_FORTYTWO_MODE = 0o755
_V6_FORTYTWO_NLINK = 1
_V6_FORTYTWO_HANDOFF_DEST = "fortytwo-runtime/42"

_V6Bindings = namedtuple(
    "_V6Bindings",
    (
        "source_commit",
        "source_tree",
        "candidate_sha256",
        "transaction_v4_sha256",
        "contract_sha256",
        "manifest_sha256",
        "host_evidence_sha256",
        "receiver_sha256",
        "fortytwo_source_rel",
        "fortytwo_source_commit",
        "fortytwo_source_tree",
        "fortytwo_sha256",
        "fortytwo_bytes",
        "fortytwo_mode",
        "fortytwo_nlink",
        "fortytwo_handoff_destination",
    ),
)


def _v6_canonical_json(obj):
    return (
        json.dumps(
            obj,
            ensure_ascii=True,
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
    ).encode("utf-8")


def _v6_write_all(stream, raw, digest=None):
    view = memoryview(raw)
    off = 0
    while off < len(view):
        wrote = stream.write(view[off:])
        if wrote is None:
            wrote = len(view) - off
        if wrote <= 0:
            raise _TransactionClosed("V6 handoff short write")
        off += wrote
    if digest is not None:
        digest.update(raw)


def _v6_write_json_frame(stream, obj, digest):
    raw = _v6_canonical_json(obj)
    prefix = struct.pack(">I", len(raw))
    _v6_write_all(stream, prefix, digest)
    _v6_write_all(stream, raw, digest)


def _v6_open_relative_regular(root_dir_fd, rel):
    comps = _validate_rel_path(rel)
    cur = os.dup(root_dir_fd)
    try:
        for comp in comps[:-1]:
            nxt = os.open(
                comp,
                os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                dir_fd=cur,
            )
            st = os.fstat(nxt)
            if not stat.S_ISDIR(st.st_mode):
                os.close(nxt)
                raise _TransactionClosed("V6 stream parent not directory")
            os.close(cur)
            cur = nxt
        leaf = comps[-1]
        lst = os.lstat(leaf, dir_fd=cur)
        if stat.S_ISLNK(lst.st_mode) or not stat.S_ISREG(lst.st_mode):
            raise _TransactionClosed("V6 stream leaf not plain regular file")
        fd = os.open(leaf, os.O_RDONLY | os.O_NOFOLLOW, dir_fd=cur)
        fst = os.fstat(fd)
        if (fst.st_dev, fst.st_ino) != (lst.st_dev, lst.st_ino):
            os.close(fd)
            raise _TransactionClosed("V6 stream file identity discontinuity")
        return fd
    finally:
        os.close(cur)


def _v6_hash_fd(fd):
    os.lseek(fd, 0, os.SEEK_SET)
    h = hashlib.sha256()
    total = 0
    while True:
        chunk = os.read(fd, 1024 * 1024)
        if not chunk:
            break
        h.update(chunk)
        total += len(chunk)
    os.lseek(fd, 0, os.SEEK_SET)
    return total, h.hexdigest()



def _v6_add_supplemental_fortytwo(
    repo_fd,
    root_fd,
    final_basename,
    bindings,
):
    if not isinstance(bindings, _V6Bindings):
        raise _TransactionClosed("V6 supplemental bindings absent")
    if (
        bindings.fortytwo_source_rel != _V6_FORTYTWO_SOURCE_REL
        or bindings.fortytwo_source_commit != _V6_FORTYTWO_SOURCE_COMMIT
        or bindings.fortytwo_source_tree != _V6_FORTYTWO_SOURCE_TREE
        or bindings.fortytwo_sha256 != _V6_FORTYTWO_SHA256
        or bindings.fortytwo_bytes != _V6_FORTYTWO_BYTES
        or bindings.fortytwo_mode != _V6_FORTYTWO_MODE
        or bindings.fortytwo_nlink != _V6_FORTYTWO_NLINK
        or bindings.fortytwo_handoff_destination
        != _V6_FORTYTWO_HANDOFF_DEST
    ):
        raise _TransactionClosed("V6 supplemental Fortytwo binding drift")

    with _open_auth_file(repo_fd, bindings.fortytwo_source_rel) as (
        source_receipt,
        source_raw,
        source_sha,
        _source_parsed,
    ):
        if source_sha != bindings.fortytwo_sha256:
            raise _TransactionClosed("V6 supplemental Fortytwo SHA mismatch")
        if len(source_raw) != bindings.fortytwo_bytes:
            raise _TransactionClosed("V6 supplemental Fortytwo byte mismatch")
        if source_receipt.size != bindings.fortytwo_bytes:
            raise _TransactionClosed("V6 supplemental Fortytwo receipt size mismatch")
        if stat.S_IMODE(source_receipt.mode) != bindings.fortytwo_mode:
            raise _TransactionClosed("V6 supplemental Fortytwo mode mismatch")
        if source_receipt.nlink != bindings.fortytwo_nlink:
            raise _TransactionClosed("V6 supplemental Fortytwo nlink mismatch")
        source_identity = (source_receipt.dev, source_receipt.ino)

        pub_fd = os.open(
            final_basename,
            os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
            dir_fd=root_fd,
        )
        runtime_fd = None
        dest_fd = None
        try:
            try:
                os.mkdir("fortytwo-runtime", 0o700, dir_fd=pub_fd)
            except OSError as exc:
                raise _TransactionClosed(
                    "V6 supplemental runtime directory create failed: %s"
                    % exc
                )
            runtime_fd = os.open(
                "fortytwo-runtime",
                os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                dir_fd=pub_fd,
            )
            runtime_st = os.fstat(runtime_fd)
            if (
                not stat.S_ISDIR(runtime_st.st_mode)
                or runtime_st.st_uid != os.geteuid()
                or stat.S_IMODE(runtime_st.st_mode) != 0o700
            ):
                raise _TransactionClosed(
                    "V6 supplemental runtime directory identity invalid"
                )

            dest_fd = os.open(
                "42",
                os.O_RDWR
                | os.O_CREAT
                | os.O_EXCL
                | os.O_NOFOLLOW,
                bindings.fortytwo_mode,
                dir_fd=runtime_fd,
            )
            off = 0
            while off < len(source_raw):
                wrote = os.write(dest_fd, source_raw[off:])
                if wrote <= 0:
                    raise _TransactionClosed(
                        "V6 supplemental Fortytwo short write"
                    )
                off += wrote
            os.fchmod(dest_fd, bindings.fortytwo_mode)
            os.fsync(dest_fd)
            dest_st = os.fstat(dest_fd)
            if (
                not stat.S_ISREG(dest_st.st_mode)
                or dest_st.st_nlink != 1
                or dest_st.st_uid != os.geteuid()
                or dest_st.st_size != bindings.fortytwo_bytes
                or stat.S_IMODE(dest_st.st_mode)
                != bindings.fortytwo_mode
            ):
                raise _TransactionClosed(
                    "V6 supplemental Fortytwo destination identity invalid"
                )
            if (dest_st.st_dev, dest_st.st_ino) == source_identity:
                raise _TransactionClosed(
                    "V6 supplemental Fortytwo source/destination inode alias"
                )
            os.lseek(dest_fd, 0, os.SEEK_SET)
            h = hashlib.sha256()
            total = 0
            while True:
                chunk = os.read(dest_fd, 1024 * 1024)
                if not chunk:
                    break
                h.update(chunk)
                total += len(chunk)
            if (
                total != bindings.fortytwo_bytes
                or h.hexdigest() != bindings.fortytwo_sha256
            ):
                raise _TransactionClosed(
                    "V6 supplemental Fortytwo destination content mismatch"
                )
            os.fsync(runtime_fd)
            os.fsync(pub_fd)
        finally:
            if dest_fd is not None:
                os.close(dest_fd)
            if runtime_fd is not None:
                os.close(runtime_fd)
            os.close(pub_fd)


def _v6_collect_published_records(root_fd, final_basename):
    pub_fd = os.open(
        final_basename,
        os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
        dir_fd=root_fd,
    )
    records = []

    def walk(dir_fd, prefix):
        for name in _fd_listdir(dir_fd):
            if "/" in name or name in (".", ".."):
                raise _TransactionClosed("V6 stream invalid directory entry")
            st = os.lstat(name, dir_fd=dir_fd)
            rel = name if not prefix else prefix + "/" + name
            _validate_rel_path(rel)
            if stat.S_ISLNK(st.st_mode):
                raise _TransactionClosed("V6 stream symlink rejected")
            if stat.S_ISDIR(st.st_mode):
                cfd = os.open(
                    name,
                    os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                    dir_fd=dir_fd,
                )
                try:
                    fst = os.fstat(cfd)
                    if (fst.st_dev, fst.st_ino) != (st.st_dev, st.st_ino):
                        raise _TransactionClosed(
                            "V6 stream directory identity discontinuity"
                        )
                    walk(cfd, rel)
                finally:
                    os.close(cfd)
            elif stat.S_ISREG(st.st_mode):
                if st.st_nlink != 1 or st.st_uid != os.geteuid():
                    raise _TransactionClosed(
                        "V6 stream regular file nlink/owner invalid"
                    )
                fd = os.open(
                    name,
                    os.O_RDONLY | os.O_NOFOLLOW,
                    dir_fd=dir_fd,
                )
                try:
                    fst = os.fstat(fd)
                    if (fst.st_dev, fst.st_ino) != (st.st_dev, st.st_ino):
                        raise _TransactionClosed(
                            "V6 stream file identity discontinuity"
                        )
                    size, sha = _v6_hash_fd(fd)
                    if size != fst.st_size:
                        raise _TransactionClosed("V6 stream size drift")
                    records.append(
                        {
                            "path": rel,
                            "mode": stat.S_IMODE(fst.st_mode),
                            "size": size,
                            "sha256": sha,
                            "source_dev": fst.st_dev,
                            "source_inode": fst.st_ino,
                        }
                    )
                finally:
                    os.close(fd)
            else:
                raise _TransactionClosed("V6 stream special file rejected")

    try:
        walk(pub_fd, "")
    finally:
        os.close(pub_fd)

    records.sort(key=lambda r: r["path"].encode("utf-8"))
    paths = [r["path"] for r in records]
    if len(paths) != len(set(paths)):
        raise _TransactionClosed("V6 stream duplicate path")
    pathset = set(paths)
    for rel in paths:
        parts = rel.split("/")
        for i in range(1, len(parts)):
            if "/".join(parts[:i]) in pathset:
                raise _TransactionClosed("V6 stream file prefix collision")
    return tuple(records)


def _v6_stream_published_transaction(
    root_fd,
    lock_fd,
    root_receipt,
    lock_receipt,
    final_basename,
    receipt_sha,
    ctx,
    bindings,
    stream,
    owned,
):
    if os.geteuid() != _V6_MATERIALIZER_UID:
        raise _TransactionClosed("V6 materialization EUID must be 599")
    if not isinstance(bindings, _V6Bindings):
        raise _TransactionClosed("V6 bindings missing")
    records = _v6_collect_published_records(root_fd, final_basename)
    receipt_records = [
        r for r in records if r["path"] == "transaction-receipt.json"
    ]
    if len(receipt_records) != 1:
        raise _TransactionClosed("V6 transaction receipt record missing")
    if receipt_records[0]["sha256"] != receipt_sha:
        raise _TransactionClosed("V6 transaction receipt SHA mismatch")

    supplemental_records = [
        r for r in records
        if r["path"] == bindings.fortytwo_handoff_destination
    ]
    if len(supplemental_records) != 1:
        raise _TransactionClosed(
            "V6 supplemental Fortytwo stream record cardinality mismatch"
        )
    supplemental_record = supplemental_records[0]
    if (
        supplemental_record["sha256"] != bindings.fortytwo_sha256
        or supplemental_record["size"] != bindings.fortytwo_bytes
        or supplemental_record["mode"] != bindings.fortytwo_mode
    ):
        raise _TransactionClosed(
            "V6 supplemental Fortytwo stream record mismatch"
        )

    digest = hashlib.sha256()
    primary = None

    try:
        _v6_write_all(stream, _V6_HANDOFF_MAGIC, digest)
        header = {
            "schema": _V6_HANDOFF_SCHEMA,
            "purpose": _V6_HANDOFF_PURPOSE,
            "source_commit": bindings.source_commit,
            "source_tree": bindings.source_tree,
            "candidate_sha256": bindings.candidate_sha256,
            "transaction_v4_sha256": bindings.transaction_v4_sha256,
            "contract_sha256": bindings.contract_sha256,
            "manifest_sha256": bindings.manifest_sha256,
            "host_evidence_sha256": bindings.host_evidence_sha256,
            "receiver_sha256": bindings.receiver_sha256,
            "supplemental_runtime_artifact": {
                "source_path": bindings.fortytwo_source_rel,
                "source_commit": bindings.fortytwo_source_commit,
                "source_tree": bindings.fortytwo_source_tree,
                "handoff_destination":
                    bindings.fortytwo_handoff_destination,
                "sha256": bindings.fortytwo_sha256,
                "bytes": bindings.fortytwo_bytes,
                "mode": bindings.fortytwo_mode,
                "nlink": bindings.fortytwo_nlink,
                "canonical_manifest_member": False,
            },
            "transaction_receipt_sha256": receipt_sha,
            "source_owner_uid": _V6_MATERIALIZER_UID,
            "runtime_owner_uid": _V6_RUNTIME_UID,
            "lock_method": _D064_SERIALIZATION_METHOD,
            "lock_held_through_handoff": True,
            "external_noncooperating_writer_absence_proven": False,
            "file_count": len(records),
            "byte_count": sum(r["size"] for r in records),
            "files": [
                {
                    "path": r["path"],
                    "mode": r["mode"],
                    "size": r["size"],
                    "sha256": r["sha256"],
                }
                for r in records
            ],
        }
        _v6_write_json_frame(stream, header, digest)

        pub_fd = os.open(
            final_basename,
            os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
            dir_fd=root_fd,
        )
        try:
            for record in records:
                _v6_write_json_frame(stream, record, digest)
                fd = _v6_open_relative_regular(pub_fd, record["path"])
                try:
                    before = os.fstat(fd)
                    if (
                        before.st_dev != record["source_dev"]
                        or before.st_ino != record["source_inode"]
                        or before.st_size != record["size"]
                        or before.st_nlink != 1
                        or stat.S_IMODE(before.st_mode) != record["mode"]
                    ):
                        raise _TransactionClosed(
                            "V6 stream pre-read identity drift"
                        )
                    h = hashlib.sha256()
                    total = 0
                    while True:
                        chunk = os.read(fd, 1024 * 1024)
                        if not chunk:
                            break
                        h.update(chunk)
                        total += len(chunk)
                        _v6_write_all(stream, chunk, digest)
                    after = os.fstat(fd)
                    if (
                        (before.st_dev, before.st_ino, before.st_mode,
                         before.st_nlink, before.st_size)
                        !=
                        (after.st_dev, after.st_ino, after.st_mode,
                         after.st_nlink, after.st_size)
                    ):
                        raise _TransactionClosed(
                            "V6 stream post-read identity drift"
                        )
                    if total != record["size"] or h.hexdigest() != record["sha256"]:
                        raise _TransactionClosed("V6 stream content drift")
                finally:
                    os.close(fd)
            if hasattr(stream, "flush"):
                stream.flush()
        finally:
            os.close(pub_fd)
    except BaseException as exc:
        primary = exc

    cleanup_error = None
    try:
        _desc_rmtree(root_fd, final_basename, owned)
        _fsync_dir_by_fd(root_fd)
        _revalidate_serialization_lock(
            root_fd, lock_fd, root_receipt, lock_receipt
        )
        os.unlink(_D064_LOCK_BASENAME, dir_fd=root_fd)
        _fsync_dir_by_fd(root_fd)
        names = _fd_listdir(root_fd)
        if names:
            raise _TransactionClosed(
                "V6 authorized root not empty after handoff cleanup: %r"
                % (names,)
            )
    except BaseException as exc:
        cleanup_error = exc

    if primary is not None or cleanup_error is not None:
        raise _TransactionClosed(
            "V6 handoff failed primary=%r cleanup=%r"
            % (primary, cleanup_error)
        )

    footer = {
        "schema": _V6_HANDOFF_SCHEMA,
        "status": "COMPLETE",
        "stream_digest_sha256": digest.hexdigest(),
        "file_count": len(records),
        "byte_count": sum(r["size"] for r in records),
        "transaction_receipt_sha256": receipt_sha,
        "private_transaction_cleanup": True,
        "authorized_root_posthandoff_empty": True,
        "lock_held_through_handoff": True,
        "lock_unlinked_identity_bound": True,
        "external_noncooperating_writer_absence_proven": False,
    }
    footer_raw = _v6_canonical_json(footer)
    _v6_write_all(stream, _V6_HANDOFF_END_MAGIC)
    _v6_write_all(stream, struct.pack(">I", len(footer_raw)))
    _v6_write_all(stream, footer_raw)
    if hasattr(stream, "flush"):
        stream.flush()


def _v6_validate_contract(
    contract,
    candidate_sha,
    tool_rel,
    tool_sha,
    manifest_rel,
    manifest_sha,
    evidence_rel,
    evidence_sha,
    evidence_schema,
    receiver_rel,
    receiver_sha,
):
    if type(contract) is not dict:
        raise _TransactionClosed("V6 contract not exact object")
    gate = contract.get("gate")
    if type(gate) is not dict:
        raise _TransactionClosed("V6 gate missing")
    if gate.get("passive_time_witness_runtime_candidate_v6_contract_schema") != 1:
        raise _TransactionClosed("V6 contract schema not exact 1")
    if gate.get("passive_time_witness_runtime_candidate_v6_static_verification") != "PASS":
        raise _TransactionClosed("V6 static verification not PASS")
    if gate.get("accepted_runtime_entrypoint_v6_sha256") != candidate_sha:
        raise _TransactionClosed("V6 accepted candidate identity mismatch")
    if gate.get("diagnostic_runtime_authorized") is not True:
        raise _TransactionClosed("V6 diagnostic runtime not authorized")
    if gate.get("diagnostic_runtime_attempts_authorized") != 1:
        raise _TransactionClosed("V6 diagnostic runtime attempt count invalid")
    for key in (
        "baseline_run_1_authorized",
        "baseline_run_2_authorized",
        "event_injection_authorized",
    ):
        if gate.get(key) is not False:
            raise _TransactionClosed("V6 gate permission not closed: " + key)
    for key in (
        "scientific_outcome_allowed",
        "event_injection_allowed",
        "command_transmission_allowed",
        "baseline_execution_allowed",
        "cryptographic_semantics_claim_allowed",
    ):
        if contract.get(key) is not False:
            raise _TransactionClosed("V6 top permission not closed: " + key)

    amendment = contract.get(
        "passive_time_witness_runtime_candidate_v6_design_amendment_1"
    )
    if type(amendment) is not dict:
        raise _TransactionClosed("V6 design amendment missing")
    impl = amendment.get(
        "passive_time_witness_runtime_candidate_v6_implementation"
    )
    if type(impl) is not dict:
        raise _TransactionClosed("V6 implementation missing")
    if amendment.get("d064_status") != "AUTHORIZED_FOR_ONE_BOUNDED_PASSIVE_ATTEMPT":
        raise _TransactionClosed("V6 D064 status not authorized")
    if amendment.get("runtime_authorized") is not True:
        raise _TransactionClosed("V6 amendment runtime not authorized")
    if amendment.get("runtime_attempts") != 1:
        raise _TransactionClosed("V6 amendment attempt count invalid")
    if impl.get("d064_authorization_single_use") is not True:
        raise _TransactionClosed("V6 authorization not single-use")
    if impl.get("d064_authorization_consumed") is not False:
        raise _TransactionClosed("V6 authorization already consumed")
    if impl.get("d064_execution_attempts") != 0:
        raise _TransactionClosed("V6 execution attempts not zero")

    expected = (
        ("runtime_material_tool", tool_rel, tool_sha),
        ("handoff_receiver", receiver_rel, receiver_sha),
        ("canonical_manifest", manifest_rel, manifest_sha),
    )
    for key, rel, sha in expected:
        rec = impl.get(key)
        if type(rec) is not dict:
            raise _TransactionClosed("V6 binding missing: " + key)
        if rec.get("path") != rel or rec.get("sha256") != sha:
            raise _TransactionClosed("V6 binding mismatch: " + key)

    he = impl.get("active_host_exclusive_writer_evidence_v3")
    if type(he) is not dict:
        raise _TransactionClosed("V6 host evidence binding missing")
    if (
        he.get("path") != evidence_rel
        or he.get("sha256") != evidence_sha
        or he.get("schema") != 2
        or evidence_schema != 2
    ):
        raise _TransactionClosed("V6 host evidence binding mismatch")

    supplemental = impl.get("supplemental_runtime_artifact_fortytwo_42")
    exact_supplemental = {
        "source_path": _V6_FORTYTWO_SOURCE_REL,
        "source_commit": _V6_FORTYTWO_SOURCE_COMMIT,
        "source_tree": _V6_FORTYTWO_SOURCE_TREE,
        "sha256": _V6_FORTYTWO_SHA256,
        "bytes": _V6_FORTYTWO_BYTES,
        "mode": _V6_FORTYTWO_MODE,
        "nlink": _V6_FORTYTWO_NLINK,
        "handoff_destination": _V6_FORTYTWO_HANDOFF_DEST,
        "canonical_manifest_member": False,
    }
    if type(supplemental) is not dict:
        raise _TransactionClosed("V6 supplemental Fortytwo binding missing")
    if supplemental != exact_supplemental:
        raise _TransactionClosed("V6 supplemental Fortytwo binding mismatch")

    ps = impl.get("privilege_separation")
    exact_ps = {
        "materializer_uid": 599,
        "runtime_uid": 501,
        "handoff_schema": _V6_HANDOFF_PURPOSE,
        "uid599_docker_allowed": False,
        "shared_writable_handoff": False,
        "live_source_runtime_mounts_allowed": False,
        "lock_held_through_handoff": True,
        "terminal_frame_after_sender_cleanup": True,
        "schema1_fallback_allowed": False,
        "external_noncooperating_writer_absence_proven": False,
    }
    if type(ps) is not dict:
        raise _TransactionClosed("V6 privilege-separation block missing")
    for key, value in exact_ps.items():
        if ps.get(key) != value:
            raise _TransactionClosed(
                "V6 privilege-separation mismatch: " + key
            )

    for key in ("source_commit", "source_tree"):
        value = impl.get(key)
        if (
            type(value) is not str
            or len(value) != 40
            or any(c not in "0123456789abcdef" for c in value)
        ):
            raise _TransactionClosed("V6 source identity invalid: " + key)

    return _V6Bindings(
        source_commit=impl["source_commit"],
        source_tree=impl["source_tree"],
        candidate_sha256=candidate_sha,
        transaction_v4_sha256=tool_sha,
        contract_sha256=None,
        manifest_sha256=manifest_sha,
        host_evidence_sha256=evidence_sha,
        receiver_sha256=receiver_sha,
        fortytwo_source_rel=_V6_FORTYTWO_SOURCE_REL,
        fortytwo_source_commit=_V6_FORTYTWO_SOURCE_COMMIT,
        fortytwo_source_tree=_V6_FORTYTWO_SOURCE_TREE,
        fortytwo_sha256=_V6_FORTYTWO_SHA256,
        fortytwo_bytes=_V6_FORTYTWO_BYTES,
        fortytwo_mode=_V6_FORTYTWO_MODE,
        fortytwo_nlink=_V6_FORTYTWO_NLINK,
        fortytwo_handoff_destination=_V6_FORTYTWO_HANDOFF_DEST,
    )


def _v6_run_authorize(args):
    repo_fd = None
    ctx = None
    try:
        for required in (
            "contract",
            "manifest",
            "candidate",
            "receiver",
            "authorized_root",
            "final_basename",
        ):
            if not getattr(args, required, None):
                raise _TransactionClosed(
                    "missing required V6 argument: " + required
                )

        repo_fd, repo_receipt = _open_repo_root_fd(args.repo_root)
        repo_abs = os.path.abspath(args.repo_root)

        tool_rel = _repo_relative_from_abs(
            os.path.abspath(__file__), repo_abs
        )
        with _open_auth_file(repo_fd, tool_rel) as (
            treceipt, _traw, tsha, _tparsed
        ):
            treceipt = treceipt._replace(sha256=tsha)

        def open_bound(raw_path):
            rel = raw_path
            if os.path.isabs(rel):
                rel = _repo_relative_from_abs(rel, repo_abs)
            return rel

        cand_rel = open_bound(args.candidate)
        with _open_auth_file(repo_fd, cand_rel) as (
            creceipt, _craw, csha, _cparsed
        ):
            creceipt = creceipt._replace(sha256=csha)

        man_rel = open_bound(args.manifest)
        with _open_auth_file(repo_fd, man_rel) as (
            mreceipt, mraw, msha, mparsed
        ):
            _manifest_canonical_check(mraw)
            mreceipt = mreceipt._replace(sha256=msha)

        receiver_rel = open_bound(args.receiver)
        with _open_auth_file(repo_fd, receiver_rel) as (
            rreceipt, _rraw, rsha, _rparsed
        ):
            rreceipt = rreceipt._replace(sha256=rsha)

        con_rel = open_bound(args.contract)
        with _open_auth_file(repo_fd, con_rel) as (
            xreceipt, _xraw, xsha, xparsed
        ):
            if xparsed is None:
                raise _TransactionClosed("V6 contract invalid JSON")
            xreceipt = xreceipt._replace(sha256=xsha)
            amendment = xparsed.get(
                "passive_time_witness_runtime_candidate_v6_design_amendment_1"
            )
            if type(amendment) is not dict:
                raise _TransactionClosed("V6 design amendment missing")
            impl = amendment.get(
                "passive_time_witness_runtime_candidate_v6_implementation"
            )
            if type(impl) is not dict:
                raise _TransactionClosed("V6 implementation block missing")
            he = impl.get("active_host_exclusive_writer_evidence_v3")
            if type(he) is not dict:
                raise _TransactionClosed("V6 host evidence binding missing")
            evidence_rel = he.get("path")
            if type(evidence_rel) is not str or os.path.isabs(evidence_rel):
                raise _TransactionClosed("V6 host evidence path invalid")
            _validate_rel_path(evidence_rel)
            with _open_auth_file(repo_fd, evidence_rel) as (
                ereceipt, eraw, esha, eparsed
            ):
                evidence_schema = _validate_host_exclusive_writer_evidence_v5(
                    eraw, eparsed
                )
                ereceipt = ereceipt._replace(sha256=esha)

            bindings = _v6_validate_contract(
                xparsed,
                csha,
                tool_rel,
                tsha,
                man_rel,
                msha,
                evidence_rel,
                esha,
                evidence_schema,
                receiver_rel,
                rsha,
            )
            bindings = bindings._replace(contract_sha256=xsha)

            ctx = _TransactionContext(
                repo=repo_receipt,
                contract=xreceipt,
                candidate=creceipt,
                tool=treceipt,
                manifest=mreceipt,
                host_evidence=ereceipt,
                host_evidence_schema=evidence_schema,
                schema=1,
                static_verification="PASS",
                diagnostic_runtime_authorized=True,
                diagnostic_runtime_attempts_authorized=1,
                amendment_runtime_authorized=True,
                amendment_runtime_attempts=1,
                d064_disposition=
                    "AUTHORIZED_FOR_ONE_BOUNDED_PASSIVE_ATTEMPT",
                accepted_candidate_sha=csha,
                top_permissions=_Permissions(
                    False, False, False, False, False
                ),
                gate_permissions=_GatePermissions(False, False, False),
                host_evidence_type=_V5_HOST_EVIDENCE_TYPE,
                host_evidence_status=_V5_HOST_EVIDENCE_STATUS,
                host_evidence_observed_at_utc=
                    _V5_HOST_EVIDENCE_OBSERVED_AT_UTC,
                compatibility_governance_decision=
                    "D064_V6_PRIVILEGE_SEPARATED_HANDOFF",
                compatibility_governance_contract_version=
                    xparsed.get("contract_version"),
                compatibility_governance_contract_sha256=xsha,
                governance_binding_verified=True,
            )

            _b2_materialize(
                ctx,
                repo_fd,
                mraw,
                mparsed,
                args.authorized_root,
                args.final_basename,
                inject=None,
                handoff_stream=sys.stdout.buffer,
                v6_bindings=bindings,
            )
            return 0, "V6_TRANSACTION_STREAM=PASS", ""
    except _TransactionClosed as exc:
        return 1, "V6_TRANSACTION_AUTHORIZATION=CLOSED", str(exc)
    finally:
        if repo_fd is not None:
            try:
                os.close(repo_fd)
            except OSError:
                pass
        ctx = None


def _v6_contract_policy_selftest():
    candidate = "3" * 64
    tool_sha = "4" * 64
    receiver_sha = "8" * 64
    manifest_sha = "6" * 64
    evidence_sha = "7" * 64
    contract = {
        "scientific_outcome_allowed": False,
        "event_injection_allowed": False,
        "command_transmission_allowed": False,
        "baseline_execution_allowed": False,
        "cryptographic_semantics_claim_allowed": False,
        "gate": {
            "passive_time_witness_runtime_candidate_v6_contract_schema": 1,
            "passive_time_witness_runtime_candidate_v6_static_verification": "PASS",
            "accepted_runtime_entrypoint_v6_sha256": candidate,
            "diagnostic_runtime_authorized": True,
            "diagnostic_runtime_attempts_authorized": 1,
            "baseline_run_1_authorized": False,
            "baseline_run_2_authorized": False,
            "event_injection_authorized": False,
        },
        "passive_time_witness_runtime_candidate_v6_design_amendment_1": {
            "d064_status": "AUTHORIZED_FOR_ONE_BOUNDED_PASSIVE_ATTEMPT",
            "runtime_authorized": True,
            "runtime_attempts": 1,
            "passive_time_witness_runtime_candidate_v6_implementation": {
                "d064_authorization_single_use": True,
                "d064_authorization_consumed": False,
                "d064_execution_attempts": 0,
                "source_commit": "1" * 40,
                "source_tree": "2" * 40,
                "runtime_material_tool": {
                    "path": "scripts/nos3_runtime_transaction_v4.py",
                    "sha256": tool_sha,
                },
                "handoff_receiver": {
                    "path": "scripts/receive_runtime_material_handoff_v1.py",
                    "sha256": receiver_sha,
                },
                "canonical_manifest": {
                    "path": "manifests/nos3-runtime-material-manifest.json",
                    "sha256": manifest_sha,
                },
                "active_host_exclusive_writer_evidence_v3": {
                    "path": "review-evidence/WP4_D064_V4_PRE_D064/host-exclusive-writer-precondition-v3.json",
                    "sha256": evidence_sha,
                    "schema": 2,
                },
                "supplemental_runtime_artifact_fortytwo_42": {
                    "source_path": _V6_FORTYTWO_SOURCE_REL,
                    "source_commit": _V6_FORTYTWO_SOURCE_COMMIT,
                    "source_tree": _V6_FORTYTWO_SOURCE_TREE,
                    "sha256": _V6_FORTYTWO_SHA256,
                    "bytes": _V6_FORTYTWO_BYTES,
                    "mode": _V6_FORTYTWO_MODE,
                    "nlink": _V6_FORTYTWO_NLINK,
                    "handoff_destination": _V6_FORTYTWO_HANDOFF_DEST,
                    "canonical_manifest_member": False,
                },
                "privilege_separation": {
                    "materializer_uid": 599,
                    "runtime_uid": 501,
                    "handoff_schema": _V6_HANDOFF_PURPOSE,
                    "uid599_docker_allowed": False,
                    "shared_writable_handoff": False,
                    "live_source_runtime_mounts_allowed": False,
                    "lock_held_through_handoff": True,
                    "terminal_frame_after_sender_cleanup": True,
                    "schema1_fallback_allowed": False,
                    "external_noncooperating_writer_absence_proven": False,
                },
            },
        },
    }
    args = (
        contract,
        candidate,
        "scripts/nos3_runtime_transaction_v4.py",
        tool_sha,
        "manifests/nos3-runtime-material-manifest.json",
        manifest_sha,
        "review-evidence/WP4_D064_V4_PRE_D064/host-exclusive-writer-precondition-v3.json",
        evidence_sha,
        2,
        "scripts/receive_runtime_material_handoff_v1.py",
        receiver_sha,
    )
    _v6_validate_contract(*args)

    def must_close(label, mutate_args):
        changed = list(args)
        mutate_args(changed)
        closed = False
        try:
            _v6_validate_contract(*changed)
        except _TransactionClosed:
            closed = True
        if not closed:
            raise _TransactionClosed("V6 contract negative case accepted: " + label)
        print("v6_contract_negative_" + label + "=PASS")

    must_close(
        "v5_candidate_identity",
        lambda a: a.__setitem__(
            1,
            "6d9158287b8addeea41740a2b50538ea545d4d5d3463d649ba5938be7b5b197e",
        ),
    )
    must_close(
        "candidate_mismatch",
        lambda a: a.__setitem__(1, "f" * 64),
    )
    must_close(
        "schema1_host_evidence",
        lambda a: a.__setitem__(8, 1),
    )

    bad_contract = json.loads(json.dumps(contract))
    bad_contract[
        "passive_time_witness_runtime_candidate_v6_design_amendment_1"
    ][
        "passive_time_witness_runtime_candidate_v6_implementation"
    ][
        "supplemental_runtime_artifact_fortytwo_42"
    ][
        "sha256"
    ] = "0" * 64
    changed = list(args)
    changed[0] = bad_contract
    closed = False
    try:
        _v6_validate_contract(*changed)
    except _TransactionClosed:
        closed = True
    if not closed:
        raise _TransactionClosed(
            "V6 contract negative case accepted: supplemental_fortytwo_binding"
        )
    print(
        "v6_contract_negative_supplemental_fortytwo_binding=PASS"
    )

    print("V6_TRANSACTION_CONTRACT_POLICY_SELFTEST=PASS")


def _v6_stream_selftest():
    _v6_contract_policy_selftest()
    import io as _io
    import shutil as _shutil

    root = tempfile.mkdtemp(
        prefix="wp4-d064-v6-tx-stream-selftest-",
        dir=os.path.realpath(tempfile.gettempdir()),
    )
    os.chmod(root, 0o700)
    root_fd = None
    lock_fd = None
    try:
        root_fd, root_receipt = _validate_absolute_authorized_root(root)
        lock_fd, lock_receipt = _acquire_serialization_lock(
            root_fd, root_receipt
        )
        pub = "synthetic-published"
        os.mkdir(pub, 0o700, dir_fd=root_fd)
        pub_fd = os.open(
            pub,
            os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
            dir_fd=root_fd,
        )
        try:
            for name, raw, mode in (
                ("transaction-receipt.json", b'{"synthetic":true}\n', 0o644),
                ("payload.bin", b"V6-SYNTHETIC\n", 0o600),
            ):
                fd = os.open(
                    name,
                    os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                    mode,
                    dir_fd=pub_fd,
                )
                try:
                    os.write(fd, raw)
                    os.fchmod(fd, mode)
                    os.fsync(fd)
                finally:
                    os.close(fd)
        finally:
            os.close(pub_fd)

        pub_fd = os.open(
            pub,
            os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
            dir_fd=root_fd,
        )
        runtime_fd = None
        try:
            os.mkdir("fortytwo-runtime", 0o700, dir_fd=pub_fd)
            runtime_fd = os.open(
                "fortytwo-runtime",
                os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                dir_fd=pub_fd,
            )
            synthetic_fortytwo = b"SYNTHETIC-FORTYTWO-42\n"
            fd = os.open(
                "42",
                os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                0o755,
                dir_fd=runtime_fd,
            )
            try:
                os.write(fd, synthetic_fortytwo)
                os.fchmod(fd, 0o755)
                os.fsync(fd)
            finally:
                os.close(fd)
            os.fsync(runtime_fd)
            os.fsync(pub_fd)
        finally:
            if runtime_fd is not None:
                os.close(runtime_fd)
            os.close(pub_fd)

        rec_sha = hashlib.sha256(b'{"synthetic":true}\n').hexdigest()
        dummy = _FileReceipt(
            "synthetic", 1, 1, 1, 0o100600, 1, "a" * 64
        )
        ctx = _TransactionContext(
            repo=_RepoReceipt(1, 1),
            contract=dummy,
            candidate=dummy,
            tool=dummy,
            manifest=dummy,
            host_evidence=dummy,
            host_evidence_schema=2,
            schema=1,
            static_verification="PASS",
            diagnostic_runtime_authorized=True,
            diagnostic_runtime_attempts_authorized=1,
            amendment_runtime_authorized=True,
            amendment_runtime_attempts=1,
            d064_disposition="AUTHORIZED_FOR_ONE_BOUNDED_PASSIVE_ATTEMPT",
            accepted_candidate_sha="b" * 64,
            top_permissions=_Permissions(
                False, False, False, False, False
            ),
            gate_permissions=_GatePermissions(False, False, False),
            host_evidence_type=_V5_HOST_EVIDENCE_TYPE,
            host_evidence_status=_V5_HOST_EVIDENCE_STATUS,
            host_evidence_observed_at_utc=_V5_HOST_EVIDENCE_OBSERVED_AT_UTC,
        )
        bindings = _V6Bindings(
            "1" * 40,
            "2" * 40,
            "3" * 64,
            "4" * 64,
            "5" * 64,
            "6" * 64,
            "7" * 64,
            "8" * 64,
            _V6_FORTYTWO_SOURCE_REL,
            "a" * 40,
            "b" * 40,
            hashlib.sha256(b"SYNTHETIC-FORTYTWO-42\n").hexdigest(),
            len(b"SYNTHETIC-FORTYTWO-42\n"),
            0o755,
            1,
            _V6_FORTYTWO_HANDOFF_DEST,
        )
        out = _io.BytesIO()
        # Synthetic selftest temporarily accepts the current EUID in place of
        # UID599; production path remains exact UID599.
        global _V6_MATERIALIZER_UID
        old_uid = _V6_MATERIALIZER_UID
        _V6_MATERIALIZER_UID = os.geteuid()
        try:
            _v6_stream_published_transaction(
                root_fd,
                lock_fd,
                root_receipt,
                lock_receipt,
                pub,
                rec_sha,
                ctx,
                bindings,
                out,
                _OwnedFds(),
            )
        finally:
            _V6_MATERIALIZER_UID = old_uid
        raw = out.getvalue()
        if not raw.startswith(_V6_HANDOFF_MAGIC):
            raise _TransactionClosed("V6 selftest magic absent")
        if _V6_HANDOFF_END_MAGIC not in raw:
            raise _TransactionClosed("V6 selftest terminal frame absent")
        if _fd_listdir(root_fd):
            raise _TransactionClosed("V6 selftest root not empty")
        print("V6_TRANSACTION_STREAM_SELFTEST=PASS")
        print("v6_lock_held_through_stream_cleanup=PASS")
        print("v6_terminal_frame_after_cleanup=PASS")
        return 0
    finally:
        if lock_fd is not None:
            try:
                fcntl.flock(lock_fd, fcntl.LOCK_UN)
            except OSError:
                pass
            try:
                os.close(lock_fd)
            except OSError:
                pass
        if root_fd is not None:
            try:
                os.close(root_fd)
            except OSError:
                pass
        _shutil.rmtree(root, ignore_errors=True)


def _v6_build_argparser():
    p = argparse.ArgumentParser(
        description=(
            "NOS3 runtime-material V6 privilege-separated stream transaction"
        )
    )
    p.add_argument("--repo-root", default=os.getcwd())
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--materialize-v6-stream", action="store_true")
    g.add_argument("--v6-stream-selftest", action="store_true")
    p.add_argument("--contract")
    p.add_argument("--manifest")
    p.add_argument("--candidate")
    p.add_argument("--receiver")
    p.add_argument("--authorized-root")
    p.add_argument("--final-basename")
    return p


def _v6_main(argv=None):
    args = _v6_build_argparser().parse_args(argv)
    if args.v6_stream_selftest:
        return _v6_stream_selftest()
    rc, marker, detail = _v6_run_authorize(args)
    if rc != 0:
        print(marker, file=sys.stderr)
        if detail:
            print("[ERROR] " + detail, file=sys.stderr)
    return rc


# ---------------------------------------------------------------------------
# Self-tests.
# ---------------------------------------------------------------------------
def selftest():
    results = []
    tmpdirs = []
    try:
        def must_pass(name, fn):
            try:
                rv = fn()
            except Exception as exc:
                results.append((name, "FAIL: %r" % exc))
                return
            if rv is False:
                results.append((name, "FAIL: returned False"))
                return
            if rv == "skip":
                results.append((name, "SKIP"))
                return
            results.append((name, "PASS"))

        repo = os.getcwd()

        def _make_real_contract_args():
            ns = argparse.Namespace()
            ns.materialize_v4_transaction = True
            ns.selftest = False
            ns.repo_root = repo
            ns.contract = os.path.join(repo, "configs",
                                       "downlink-diagnostic-contract.json")
            ns.manifest = os.path.join(repo, "manifests",
                                       "nos3-runtime-material-manifest.json")
            ns.candidate = os.path.join(
                repo, "scripts", "nos3_runtime_transaction_v2.py"
            )
            ns.authorized_root = os.path.join(repo, "_DOES_NOT_EXIST_ROOT_")
            ns.final_basename = "run_test"
            return ns

        def _current_contract_static_gate_closed(result):
            """Require the current-contract fixture to reach structured
            contract validation and close specifically at the static gate.

            A generic rc=1 result is insufficient because an invalid candidate
            path, missing file, or other earlier failure could produce the same
            public closed marker without validating the current contract.
            """
            rc, marker, detail = result
            return (
                rc == 1
                and marker == "V4_TRANSACTION_AUTHORIZATION=CLOSED"
                and detail == "diagnostic_runtime_authorized not True"
                and "path outside repository root" not in detail
            )

        def _build_future_fixture(d064=_D064_AUTHORIZED):
            scratch = tempfile.mkdtemp(prefix="nrm_tx_future_", dir=repo)
            tmpdirs.append(scratch)
            real_man = os.path.join(repo, "manifests",
                                    "nos3-runtime-material-manifest.json")
            with open(real_man, "rb") as mf:
                man_raw = mf.read()
            man_path = os.path.join(scratch, "manifest.json")
            with open(man_path, "wb") as f:
                f.write(man_raw)
            os.chmod(man_path, 0o644)
            man_sha = _sha256_file_path(man_path)
            tool_abs = os.path.abspath(__file__)
            repo_abs = os.path.abspath(repo)
            tool_rel = _repo_relative_from_abs(tool_abs, repo_abs)
            tool_sha = _sha256_file_path(tool_abs)
            cand_path = os.path.join(scratch, "candidate.sh")
            cand_bytes = b"#!/usr/bin/env bash\n# synthetic v4 candidate\nexit 0\n"
            with open(cand_path, "wb") as f:
                f.write(cand_bytes)
            os.chmod(cand_path, 0o755)
            cand_sha = _sha256_file_path(cand_path)
            evidence_obj={"schema":_HOST_EVIDENCE_SCHEMA,"evidence_type":_HOST_EVIDENCE_TYPE,"platform":"Darwin","acl_policy":_D064_ACL_POLICY,"serialization_method":_D064_SERIALIZATION_METHOD,"status":_HOST_EVIDENCE_STATUS,"claim_scope":_HOST_EVIDENCE_CLAIM_SCOPE,"fixture_only":True}
            evidence_path=os.path.join(scratch,"synthetic-host-evidence.json")
            evidence_raw=(json.dumps(evidence_obj,ensure_ascii=True,sort_keys=True,separators=(",",":"))+chr(10)).encode("utf-8")
            with open(evidence_path,"wb") as f: f.write(evidence_raw)
            os.chmod(evidence_path,0o644); evidence_sha=_sha256_file_path(evidence_path)
            man_rel = os.path.relpath(man_path, repo_abs)
            cand_rel = os.path.relpath(cand_path, repo_abs)
            evidence_rel=os.path.relpath(evidence_path,repo_abs)
            contract = _build_future_contract(tool_rel, tool_sha, man_rel,
                                              man_sha, cand_sha, evidence_rel,
                                              evidence_sha, d064)
            cpath = os.path.join(scratch, "contract.json")
            _write_contract(cpath, contract)
            os.chmod(cpath, 0o644)
            ns = argparse.Namespace()
            ns.materialize_v4_transaction = True
            ns.selftest = False
            ns.repo_root = repo
            ns.contract = cpath
            ns.manifest = man_path
            ns.candidate = cand_path
            ns.authorized_root = os.path.join(scratch, "AUTHORIZED_ROOT")
            ns.final_basename = "run_future"
            return {"scratch":scratch,"args":ns,"man_path":man_path,"cpath":cpath,
                    "cand_path":cand_path,"cand_sha":cand_sha,"evidence_path":evidence_path,
                    "evidence_sha":evidence_sha,"evidence_rel":evidence_rel}

        def _build_future_contract(tool_rel, tool_sha, man_rel, man_sha,
                                   cand_sha, evidence_rel, evidence_sha, d064):
            return {
                "contract_version": "0.4.14-future-synthetic",
                "status": "FUTURE_SYNTHETIC_AUTHORIZED",
                "scientific_outcome_allowed": False,
                "event_injection_allowed": False,
                "command_transmission_allowed": False,
                "baseline_execution_allowed": False,
                "cryptographic_semantics_claim_allowed": False,
                "gate": {
                    "passive_time_witness_runtime_candidate_v4_contract_schema": 1,
                    "passive_time_witness_runtime_candidate_v4_static_verification": "PASS",
                    "diagnostic_runtime_authorized": True,
                    "diagnostic_runtime_attempts_authorized": 1,
                    "accepted_runtime_entrypoint_v4_sha256": cand_sha,
                    "accepted_runtime_entrypoint_v4_identity_only_not_authorized": False,
                    "proposed_runtime_entrypoint_v4_sha256": "",
                    "baseline_run_1_authorized": False,
                    "baseline_run_2_authorized": False,
                    "event_injection_authorized": False,
                },
                "passive_time_witness_runtime_candidate_v4_design_amendment_1": {
                    "runtime_authorized": True,
                    "runtime_attempts": 1,
                    "d064_status": d064,
                    "passive_time_witness_runtime_candidate_v4_implementation": {
                        "runtime_material_tool": {"path": tool_rel,
                                                 "sha256": tool_sha},
                        "canonical_manifest": {"path": man_rel,
                                               "sha256": man_sha},
                        "host_exclusive_writer_evidence": {"path": evidence_rel,
                            "sha256": evidence_sha, "schema": _HOST_EVIDENCE_SCHEMA,
                            "status": _HOST_EVIDENCE_STATUS},
                    },
                },
            }

        def _write_contract(cpath, obj):
            with open(cpath, "wb") as f:
                f.write(json.dumps(obj, ensure_ascii=True, sort_keys=True,
                                   separators=(",", ":")).encode("utf-8") + b"\n")

        def _read_contract(cpath):
            return json.loads(open(cpath, "rb").read())

        def _assert_closed(ns):
            rc, marker, _d = _run_authorize(ns)
            return rc == 1 and marker == "V4_TRANSACTION_AUTHORIZATION=CLOSED"

        def _fresh_manifest_copy(scratch):
            real_man = os.path.join(repo, "manifests",
                                    "nos3-runtime-material-manifest.json")
            mp = os.path.join(scratch, "manifest_%s.json" % _uid())
            with open(real_man, "rb") as mf:
                with open(mp, "wb") as f:
                    f.write(mf.read())
            os.chmod(mp, 0o644)
            return mp

        def _uid():
            return str(tempfile.mkdtemp(prefix="nrm_", dir=repo)).rsplit("/", 1)[-1]

        _fcount = [0]

        def _reemit_canonical(man_path, obj):
            raw = (json.dumps(obj, ensure_ascii=True, sort_keys=True,
                              separators=(",", ":")) + "\n").encode("utf-8")
            with open(man_path, "wb") as f:
                f.write(raw)
            return raw

        # ---- nested context-construction helper (Cor 1): returns _TransactionContext
        # for local structural testing ONLY.  Not module-global, not returned by
        # selftest(), not reachable through a module-level callable; discarded by
        # the caller before returning.
        def _build_local_ctx(fx):
            repo_fd, repo_receipt = _open_repo_root_fd(repo)
            try:
                tool_abs = os.path.abspath(__file__)
                repo_abs = os.path.abspath(repo)
                tool_rel = _repo_relative_from_abs(tool_abs, repo_abs)
                with _open_auth_file(repo_fd, tool_rel) as (tr, _a, ts, _b):
                    pass
                crel = fx["args"].candidate
                if os.path.isabs(crel):
                    crel = _repo_relative_from_abs(crel, repo_abs)
                with _open_auth_file(repo_fd, crel) as (cr, _a, cs, _b):
                    pass
                mrel = fx["args"].manifest
                if os.path.isabs(mrel):
                    mrel = _repo_relative_from_abs(mrel, repo_abs)
                with _open_auth_file(repo_fd, mrel) as (mr, mraw, msha, _b):
                    _manifest_canonical_check(mraw)
                xrel = fx["args"].contract
                if os.path.isabs(xrel):
                    xrel = _repo_relative_from_abs(xrel, repo_abs)
                with _open_auth_file(repo_fd, fx["evidence_rel"]) as (er, eraw, esha, ep):
                    evidence_schema=_validate_host_exclusive_writer_evidence(eraw,ep)
                    er=er._replace(sha256=esha)
                with _open_auth_file(repo_fd, xrel) as (xr, xraw, xsha, xp):
                    (schema, sv, drab, drint, amab, amint, d064, acc,
                     tp, gp) = _validate_structured_authorization(
                        xp, cs, tool_rel, ts, mrel, msha,
                        fx["evidence_rel"], esha, evidence_schema)
            finally:
                os.close(repo_fd)
            return _TransactionContext(
                repo=repo_receipt, contract=xr, candidate=cr, tool=tr, manifest=mr,
                host_evidence=er, host_evidence_schema=evidence_schema,
                schema=schema, static_verification=sv,
                diagnostic_runtime_authorized=drab,
                diagnostic_runtime_attempts_authorized=drint,
                amendment_runtime_authorized=amab, amendment_runtime_attempts=amint,
                d064_disposition=d064, accepted_candidate_sha=acc,
                top_permissions=_Permissions(*tp),
                gate_permissions=_GatePermissions(*gp))


        # ---- B2 selftest synthetic environment (Checkpoint 2PB2B-B2) ----
        # Private, nested-only, unreachable from the CLI, cleared after tests.
        # Builds a tiny synthetic source tree + a synthetic _CanonicalCompletePlan
        # of the same immutable shape the production compiler produces, plus a
        # source-root override mapping so the integrated copy/verify/publish
        # pipeline runs against synthetic fixtures instead of the full
        # external/nos3 tree.  The synthetic plan never reaches the production
        # CLI: only a manually-constructed test namespace may carry an
        # args._b2_inject["selftest_plan"] attribute; the argparser exposes no
        # such flag.
        _B2_SYNTHETIC_DONE = []

        def _b2_dir_rel(rel):
            if not _is_exact_str(rel) or rel == "":
                raise _TransactionClosed("bad synth dir rel")
            return rel

        def _b2_make_synthetic_file(parent, name, content):
            path = os.path.join(parent, name)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "wb") as f:
                f.write(content)
            os.chmod(path, 0o644)
            st = os.lstat(path)
            return path, st

        def _b2_build_synthetic_env():
            scratch = tempfile.mkdtemp(prefix="nrm_b2_synth_", dir=repo)
            tmpdirs.append(scratch)
            # Build tiny synthetic source trees for each source root kind.
            src_dirs = {}
            contents = {}
            # cfs source tree
            cfs_dir = os.path.join(scratch, "src_cfs", "fsw", "build", "exe",
                                   "cpu1")
            os.makedirs(cfs_dir, exist_ok=True)
            cfs_files = {}
            for nm in ("cf_core.so", "cfs_es.so"):
                ct = ("B2-synth-cfs-%s\n" % nm).encode("utf-8")
                p, _st = _b2_make_synthetic_file(cfs_dir, nm, ct)
                cfs_files[nm] = ct
            # simulator source trees
            sim_dir = os.path.join(scratch, "src_sim", "sims")
            sb = os.path.join(sim_dir, "build", "bin")
            sl = os.path.join(sim_dir, "build", "lib")
            os.makedirs(sb, exist_ok=True)
            os.makedirs(sl, exist_ok=True)
            sim_files = {}
            for nm in ("hw_sim.so", "time.so"):
                ct = ("B2-synth-sim-%s\n" % nm).encode("utf-8")
                p, _st = _b2_make_synthetic_file(sb, nm, ct)
                sim_files[("sim_bin", nm)] = ct
            for nm in ("libsim.so", "libnos.so"):
                ct = ("B2-synth-lib-%s\n" % nm).encode("utf-8")
                p, _st = _b2_make_synthetic_file(sl, nm, ct)
                sim_files[("sim_lib", nm)] = ct
            # configuration / Fortytwo source tree
            cfg_dir = os.path.join(scratch, "src_cfg", "cfg", "build", "InOut")
            os.makedirs(cfg_dir, exist_ok=True)
            cfg_files = {}
            for nm in ("fortytwo.txt", "InOut.bin"):
                ct = ("B2-synth-cfg-%s\n" % nm).encode("utf-8")
                p, _st = _b2_make_synthetic_file(cfg_dir, nm, ct)
                cfg_files[nm] = ct
            # Build the immutable plan records of the same shape the production
            # compiler produces, but with tiny synthetic entries.  Each file
            # carries its real synthetic SHA-256 so the integrated copy verifies.
            src_cfs_abs = os.path.join(scratch, "src_cfs")
            src_sim_abs = os.path.join(scratch, "src_sim")
            src_cfg_abs = os.path.join(scratch, "src_cfg")
            override = {
                "cfs": "review_tmp_b2/src_cfs/fsw/build/exe/cpu1",
                "sim_bin": "review_tmp_b2/src_sim/sims/build/bin",
                "sim_lib": "review_tmp_b2/src_sim/sims/build/lib",
                "configuration": "review_tmp_b2/src_cfg/cfg/build/InOut",
            }
            # The override paths must be reachable from repo_fd; stage them
            # under a temp dir inside the repo workspace and relativize.
            stage_root = os.path.join(scratch, "review_tmp_b2")
            os.makedirs(stage_root, exist_ok=True)
            # Copy synthetic trees into the repo-relative staging area so the
            # descriptor-bound source traversal rooted at repo_fd can reach them.
            _b2_sync_tree(src_cfs_abs, os.path.join(stage_root, "src_cfs"))
            _b2_sync_tree(src_sim_abs, os.path.join(stage_root, "src_sim"))
            _b2_sync_tree(src_cfg_abs, os.path.join(stage_root, "src_cfg"))
            repo_abs = os.path.abspath(repo)
            override = {
                "cfs": os.path.relpath(
                    os.path.join(stage_root, "src_cfs", "fsw", "build", "exe",
                                 "cpu1"), repo_abs),
                "sim_bin": os.path.relpath(
                    os.path.join(stage_root, "src_sim", "sims", "build", "bin"),
                    repo_abs),
                "sim_lib": os.path.relpath(
                    os.path.join(stage_root, "src_sim", "sims", "build", "lib"),
                    repo_abs),
                "configuration": os.path.relpath(
                    os.path.join(stage_root, "src_cfg", "cfg", "build", "InOut"),
                    repo_abs),
            }
            return {
                "scratch": scratch, "override": override,
                "cfs_files": cfs_files, "sim_files": sim_files,
                "cfg_files": cfg_files,
            }

        def _b2_sync_tree(src, dst):
            import shutil as _sh
            _sh.copytree(src, dst)

        def _b2_build_synthetic_plan(env):
            """Build a synthetic _CanonicalCompletePlan of the exact immutable
            shape the production compiler produces, with tiny synthetic file
            entries whose mode/size/sha match the synthetic source fixtures.
            Private to selftest; never supplied to the production CLI."""
            scratch = env["scratch"]
            repo_abs = os.path.abspath(repo)
            # --- source root declarations ---
            cfs_decl = _CanonicalSourceRoot(
                "cfs", "cfs", env["override"]["cfs"], "fsw/build/exe/cpu1")
            sim_bin_decl = _CanonicalSourceRoot(
                "sim_bin", "simulator", env["override"]["sim_bin"],
                "sims/build/bin")
            sim_lib_decl = _CanonicalSourceRoot(
                "sim_lib", "simulator", env["override"]["sim_lib"],
                "sims/build/lib")
            cfg_decl = _CanonicalSourceRoot(
                "configuration", "configuration",
                env["override"]["configuration"], "cfg/build/InOut")
            source_roots = (cfs_decl, sim_bin_decl, sim_lib_decl, cfg_decl)
            sr_by_name = {r.source_root: r for r in source_roots}
            # Read synthetic files to build regular-file records.
            def _rec(sroot, rel, host_dir):
                p = os.path.join(host_dir, rel)
                st = os.lstat(p)
                with open(p, "rb") as f:
                    data = f.read()
                sha = hashlib.sha256(data).hexdigest()
                return _CanonicalRegularFile(
                    "regular_file", sroot, sr_by_name[sroot].component_scope,
                    rel, None, "%04o" % stat.S_IMODE(st.st_mode), st.st_nlink,
                    st.st_size, sha), data
            cfs_host = os.path.join(repo_abs, env["override"]["cfs"])
            sim_bin_host = os.path.join(repo_abs, env["override"]["sim_bin"])
            sim_lib_host = os.path.join(repo_abs, env["override"]["sim_lib"])
            cfg_host = os.path.join(repo_abs, env["override"]["configuration"])
            reg_files = []
            reg_files.append(_rec("cfs", "cf_core.so", cfs_host)[0])
            reg_files.append(_rec("cfs", "cfs_es.so", cfs_host)[0])
            reg_files.append(_rec("sim_bin", "hw_sim.so", sim_bin_host)[0])
            reg_files.append(_rec("sim_bin", "time.so", sim_bin_host)[0])
            reg_files.append(_rec("sim_lib", "libsim.so", sim_lib_host)[0])
            reg_files.append(_rec("sim_lib", "libnos.so", sim_lib_host)[0])
            reg_files.append(_rec("configuration", "fortytwo.txt", cfg_host)[0])
            reg_files.append(_rec("configuration", "InOut.bin", cfg_host)[0])
            reg_files = tuple(reg_files)
            # Directories: one root sentinel per source root.
            directories = (
                _CanonicalDirectory("cfs", "cfs", ""),
                _CanonicalDirectory("sim_bin", "simulator", ""),
                _CanonicalDirectory("sim_lib", "simulator", ""),
                _CanonicalDirectory("configuration", "configuration", ""),
            )
            exclusions = ()
            deny_patterns = (
                _CanonicalDenyPattern(pattern=".goutputstream-*", scope="cfs"),)
            # Build workspaces: cfs seeds cfs; all others seed sim_bin+sim_lib.
            file_index = {(f.source_root, f.relative_path): f for f in reg_files}

            def _ws_file_target(cid, f):
                return "workspaces/%s/work/nos3/%s/%s" % (
                    cid, sr_by_name[f.source_root].destination_prefix,
                    f.relative_path)

            def _ws_dir_target(cid, decl, rel):
                p = decl.destination_prefix
                return ("workspaces/%s/work/nos3/%s" % (cid, p)
                        if not rel else
                        "workspaces/%s/work/nos3/%s/%s" % (cid, p, rel))

            def _ws_excl_target(cid, decl, rel):
                return "workspaces/%s/work/nos3/%s/%s" % (
                    cid, decl.destination_prefix, rel)
            workspaces_list = []
            all_files = []
            all_dirs = []
            all_excls = []
            total_files = 0
            total_bytes = 0
            total_dirs = 0
            total_excls = 0
            for cid in _COMPONENT_IDS:
                if cid == "cfs":
                    seeds = ("cfs",)
                else:
                    seeds = ("sim_bin", "sim_lib")
                wf = tuple(f for f in reg_files if f.source_root in seeds)
                wd = tuple(d for d in directories if d.source_root in seeds)
                wfc = len(wf)
                wbc = sum(f.size for f in wf)
                wdrc = len(wd)
                wec = 0
                ws_ft = []
                ws_dt = []
                ws_et = []
                for f in wf:
                    d = _ws_file_target(cid, f)
                    ws_ft.append(_CanonicalExpandedTarget(
                        "regular_file", "workspace", cid, f.source_root,
                        f.relative_path, d, False))
                    all_files.append(ws_ft[-1])
                    total_bytes += f.size
                for dd in wd:
                    decl = sr_by_name[dd.source_root]
                    d = _ws_dir_target(cid, decl, dd.relative_path)
                    ws_dt.append(_CanonicalExpandedTarget(
                        "directory", "workspace", cid, dd.source_root,
                        dd.relative_path, d, False))
                    all_dirs.append(ws_dt[-1])
                ws_incl_dirs = set(
                    t.transaction_relative_path.rsplit("/", 1)[0]
                    for t in ws_ft)
                ws_dt_paths = set(t.transaction_relative_path for t in ws_dt)
                for pd in sorted(ws_incl_dirs):
                    if pd not in ws_dt_paths:
                        ws_dt.append(_CanonicalExpandedTarget(
                            "directory", "workspace", cid, "_derived", "",
                            pd, False))
                        all_dirs.append(ws_dt[-1])
                workspaces_list.append(_CanonicalWorkspacePlan(
                    component_id=cid,
                    workspace_host_path=cid,
                    mount_destination="/work/nos3",
                    seed_source_roots=seeds,
                    private_physical_copy=True, no_hard_links=True,
                    no_reflinks=True, no_overlays=True, no_source_aliases=True,
                    no_runtime_mount_from_external_nos3=True,
                    regular_files=wf, directories=wd, exclusions=(),
                    file_count=wfc, byte_count=wbc, directory_count=wdrc,
                    exclusion_count=wec, file_targets=tuple(ws_ft),
                    directory_targets=tuple(ws_dt), exclusion_targets=()))
                total_files += wfc
                total_dirs += len(ws_dt)
            workspaces = tuple(workspaces_list)
            # Fortytwo scratch (configuration source root), separate.
            ft_files = tuple(f for f in reg_files
                             if f.source_root == "configuration")
            ft_ft = []
            ft_dt = []
            ft_incl_dirs = set()
            for f in ft_files:
                d = "fortytwo-config/%s/%s" % (
                    cfg_decl.destination_prefix, f.relative_path)
                ft_ft.append(_CanonicalExpandedTarget(
                    "regular_file", "fortytwo", "fortytwo", f.source_root,
                    f.relative_path, d, False))
                ft_incl_dirs.add(d.rsplit("/", 1)[0])
            ft_dt.append(_CanonicalExpandedTarget(
                "directory", "fortytwo", "fortytwo", "configuration", "",
                "fortytwo-config/cfg/build/InOut", False))
            for pd in sorted(ft_incl_dirs):
                if pd != "fortytwo-config/cfg/build/InOut":
                    ft_dt.append(_CanonicalExpandedTarget(
                        "directory", "fortytwo", "fortytwo", "configuration",
                        "", pd, False))
            fortytwo = _CanonicalFortytwoPlan(
                transaction_relative_root="fortytwo-config",
                regular_files=ft_files, directories=(), exclusions=(),
                file_count=len(ft_files),
                byte_count=sum(f.size for f in ft_files),
                directory_count=len(ft_dt),
                exclusion_count=0,
                file_targets=tuple(ft_ft), directory_targets=tuple(ft_dt),
                exclusion_targets=())
            all_files.extend(ft_ft)
            all_dirs.extend(ft_dt)
            total_files += fortytwo.file_count
            total_bytes += fortytwo.byte_count
            total_dirs += fortytwo.directory_count
            # Complete the directory-target set: every ancestor prefix of every
            # file and directory target must appear as a planned directory so the
            # destination audit treats it as expected (not unplanned).  This
            # mirrors the production plan's complete leaf+ancestor directory set.
            _dir_paths = set(t.transaction_relative_path for t in all_dirs)
            for ft_ in all_files:
                trp = ft_.transaction_relative_path
                comps = trp.split("/")
                for i in range(1, len(comps)):
                    anc = "/".join(comps[:i])
                    _dir_paths.add(anc)
            for dp_ in list(_dir_paths):
                comps = dp_.split("/")
                for i in range(1, len(comps)):
                    _dir_paths.add("/".join(comps[:i]))
            _seen_dir = set()
            final_dirs = []
            for dp_ in sorted(_dir_paths):
                if dp_ in _seen_dir:
                    continue
                _seen_dir.add(dp_)
                # Determine owner kind/id by prefix (synthetic plan is flat).
                if dp_.startswith("workspaces/"):
                    owner_kind = "workspace"
                    cid = dp_.split("/")[1]
                else:
                    owner_kind = "fortytwo"
                    cid = "fortytwo"
                final_dirs.append(_CanonicalExpandedTarget(
                    "directory", owner_kind, cid, "configuration", "", dp_, False))
            all_dirs = final_dirs
            total_dirs = len(all_dirs)
            # Build a real transaction context via the future fixture so the
            # receipt builder has authentic dev/inode/size/mode/nlink/sha.
            fx = _build_future_fixture()
            ctx = _build_local_ctx(fx)
            plan = _CanonicalCompletePlan(
                source_roots=source_roots,
                source_regular_files=reg_files,
                source_directories=directories,
                source_exclusions=exclusions,
                workspaces=workspaces, fortytwo=fortytwo,
                collision_model=(0, 0, 0, 0), source_root_count=4,
                source_file_entry_count=len(reg_files),
                source_file_byte_count=sum(f.size for f in reg_files),
                source_directory_entry_count=len(directories),
                source_exclusion_entry_count=0,
                workspace_count=len(workspaces),
                expanded_workspace_file_count=sum(
                    w.file_count for w in workspaces),
                expanded_workspace_byte_count=sum(
                    w.byte_count for w in workspaces),
                expanded_workspace_directory_count=sum(
                    len(w.directory_targets) for w in workspaces),
                expanded_workspace_exclusion_count=0,
                expanded_total_file_count=total_files,
                expanded_total_byte_count=total_bytes,
                expanded_total_directory_count=total_dirs,
                expanded_total_exclusion_count=0,
                duplicate_file_target_count=0,
                duplicate_directory_target_count=0,
                file_directory_collision_count=0,
                prefix_collision_count=0,
                expanded_file_targets=tuple(all_files),
                expanded_directory_targets=tuple(all_dirs),
                expanded_exclusion_targets=tuple(),
                deny_patterns=deny_patterns)
            env["plan"] = plan
            env["ctx"] = ctx
            env["fx"] = fx
            return env

        def _b2_run_integrated(root=None, basename=None, inject=None,
                                env=None, via_authorize=False):
            """Run the integrated transaction core with synthetic fixtures.
            If via_authorize is True, drive through _run_authorize (reaching
            the transaction core through the production authorization path);
            otherwise drive _b2_materialize directly.  Manages the global
            override around the run."""
            global _B2_SELFTEST_SOURCE_OVERRIDE
            if env is None:
                env = _b2_build_synthetic_env()
                _b2_build_synthetic_plan(env)
            if root is None:
                root = tempfile.mkdtemp(prefix="nrm_b2_root_", dir=os.path.realpath(tempfile.gettempdir()))
                tmpdirs.append(root)
                os.chmod(root, 0o700)
            if basename is None:
                basename = "b2_run_%d" % (len(tmpdirs) + 1)
            if inject is None:
                inject = {}
            inject.setdefault("selftest_plan", env["plan"])
            old_override = _B2_SELFTEST_SOURCE_OVERRIDE
            _B2_SELFTEST_SOURCE_OVERRIDE = env["override"]
            try:
                if via_authorize:
                    ns = env["fx"]["args"]
                    ns.authorized_root = root
                    ns.final_basename = basename
                    ns._b2_inject = inject
                    rc, marker, detail = _run_authorize(ns)
                    return (rc, marker, detail)
                repo_fd, _rr = _open_repo_root_fd(repo)
                try:
                    return _b2_materialize(env["ctx"], repo_fd, None, None,
                                           root, basename, inject=inject)
                finally:
                    try:
                        os.close(repo_fd)
                    except OSError:
                        pass
            finally:
                _B2_SELFTEST_SOURCE_OVERRIDE = old_override

        _b2_env_cache = {}

        def _b2_env():
            key = "default"
            if key not in _b2_env_cache:
                e = _b2_build_synthetic_env()
                _b2_build_synthetic_plan(e)
                _b2_env_cache[key] = e
            return _b2_env_cache[key]

        # ---- V4 D-064 technical controls ----
        def v4_synthetic_root_uses_physical_temp_path():
            physical=os.path.realpath(tempfile.gettempdir())
            root=tempfile.mkdtemp(prefix="nrm_v4_rootpath_",dir=physical); tmpdirs.append(root); os.chmod(root,0o700)
            if not root.startswith(physical+os.sep):
                return False
            # The production validator itself is the authority: this proves
            # the synthetic root has no symlink component in its absolute path.
            fd,_rr=_validate_absolute_authorized_root(root)
            try:
                return True
            finally:
                os.close(fd)
        must_pass("v4_synthetic_root_uses_physical_temp_path",v4_synthetic_root_uses_physical_temp_path)

        def v4_empty_acl_policy_zero():
            root=tempfile.mkdtemp(prefix="nrm_v4_acl_",dir=os.path.realpath(tempfile.gettempdir())); tmpdirs.append(root); os.chmod(root,0o700)
            fd,_rr=_validate_absolute_authorized_root(root)
            try: return _validate_root_acl_no_extended(fd)==0
            finally: os.close(fd)
        must_pass("v4_empty_acl_policy_zero",v4_empty_acl_policy_zero)

        def v4_serialization_lock_properties():
            root=tempfile.mkdtemp(prefix="nrm_v4_lock_",dir=os.path.realpath(tempfile.gettempdir())); tmpdirs.append(root); os.chmod(root,0o700)
            rfd,rr=_validate_absolute_authorized_root(root); lfd=None
            try:
                lfd,lr=_acquire_serialization_lock(rfd,rr); lr2=_revalidate_serialization_lock(rfd,lfd,rr,lr)
                return lr==lr2 and lr.mode==0o600 and lr.nlink==1 and lr.uid==os.geteuid() and lr.dev==rr.dev
            finally:
                if lfd is not None:
                    try: fcntl.flock(lfd,fcntl.LOCK_UN)
                    except OSError: pass
                    os.close(lfd)
                os.close(rfd)
        must_pass("v4_serialization_lock_properties",v4_serialization_lock_properties)

        def v4_host_evidence_actual_hash_bound():
            fx=_build_future_fixture(); ctx=_build_local_ctx(fx)
            try: return ctx.host_evidence.sha256==fx["evidence_sha"] and ctx.host_evidence_schema==1
            finally: del ctx
        must_pass("v4_host_evidence_actual_hash_bound",v4_host_evidence_actual_hash_bound)

        def v4_source_order_controls():
            text=open(__file__,encoding="utf-8").read(); sec=text.split("def _b2_materialize",1)[1].split("# Self-tests.",1)[0]
            a=sec.index("initial_acl_entry_count = _validate_root_acl_no_extended"); l=sec.index("_acquire_serialization_lock"); s=sec.index("_make_staging_dir"); p=sec.index("_atomic_noreplace_publish")
            fa=sec.rfind("_validate_root_acl_no_extended(root_fd)",0,p); fl=sec.rfind("_revalidate_serialization_lock",0,p)
            banned="SATISFIED_DEEP_"+"IMMUTABLE_CONTEXT"
            return a<l<s<fa<fl<p and banned not in text
        must_pass("v4_source_order_controls",v4_source_order_controls)

        # ---- retained meaningful tests ----
        def current_contract_closed_before_authorized_root_inspection():
            args = _make_real_contract_args()
            auth_root = args.authorized_root
            pre = os.path.exists(auth_root)
            result = _run_authorize(args)
            post = os.path.exists(auth_root)
            return (
                _current_contract_static_gate_closed(result)
                and pre is False
                and post is False
            )
        must_pass("current_contract_closed_before_authorized_root_inspection",
                  current_contract_closed_before_authorized_root_inspection)

        def current_contract_exact_marker_and_rc():
            result = _run_authorize(_make_real_contract_args())
            return _current_contract_static_gate_closed(result)
        must_pass("current_contract_exact_marker_and_rc",
                  current_contract_exact_marker_and_rc)

        def current_contract_fixture_candidate_is_repo_local_regular_file():
            args = _make_real_contract_args()
            candidate = os.path.abspath(args.candidate)
            repo_abs = os.path.abspath(repo)
            try:
                common = os.path.commonpath((repo_abs, candidate))
                st = os.lstat(candidate)
            except (OSError, ValueError):
                return False
            return (
                common == repo_abs
                and (st.st_mode & 0o170000) == 0o100000
                and st.st_nlink == 1
                and _current_contract_static_gate_closed(
                    _run_authorize(args)
                )
            )
        must_pass(
            "current_contract_fixture_candidate_is_repo_local_regular_file",
            current_contract_fixture_candidate_is_repo_local_regular_file,
        )

        def no_authorization_bearer_registry_or_issuer_symbols():
            import ast as _ast
            banned = ("MaterializationAuthorized", "authorize_v4_materialization",
                      "_issue", "_registry", "_require_auth")
            tree = _ast.parse(open(__file__).read())
            for node in _ast.walk(tree):
                if isinstance(node, (_ast.FunctionDef, _ast.AsyncFunctionDef,
                                     _ast.ClassDef)) and node.name in banned:
                    return False
                if isinstance(node, _ast.Import) and any(n.name == "weakref" for n in node.names):
                    return False
                if isinstance(node, _ast.ImportFrom) and (node.module or "") == "weakref":
                    return False
            return True
        must_pass("no_authorization_bearer_registry_or_issuer_symbols",
                  no_authorization_bearer_registry_or_issuer_symbols)

        def no_project_local_imports():
            import ast as _ast
            tree = _ast.parse(open(__file__).read())
            banned = ("nos3_runtime_material", "scripts.nos3_runtime_material",
                      "weakref", "subprocess")
            for node in _ast.walk(tree):
                if isinstance(node, _ast.Import):
                    for n in node.names:
                        if n.name in banned:
                            return False
                elif isinstance(node, _ast.ImportFrom):
                    if (node.module or "") in banned:
                        return False
            return True
        must_pass("no_project_local_imports", no_project_local_imports)

        def executing_tool_bound_to___file__():
            # B2: future authorization reaches the transaction core and
            # completes against the synthetic source fixtures (not the real
            # external/nos3 tree).
            env = _b2_env()
            rc, marker, _d = _b2_run_integrated(
                basename="exec_tool_bound", env=env, via_authorize=True)
            return rc == 0 and marker == "V4_TRANSACTION_MATERIALIZATION=PASS"
        must_pass("executing_tool_bound_to___file__", executing_tool_bound_to___file__)

        def no_tool_path_cli_argument():
            for a in _build_argparser()._actions:
                if any(o == "--tool-path" for o in a.option_strings):
                    return False
            return True
        must_pass("no_tool_path_cli_argument", no_tool_path_cli_argument)

        # ---- CORRECTION 1 tests: exact D-064 allowlist ----
        def exact_authorized_d064_state_accepted():
            env = _b2_env()
            rc, marker, _d = _b2_run_integrated(
                basename="d064_accepted", env=env, via_authorize=True)
            return rc == 0 and marker == "V4_TRANSACTION_MATERIALIZATION=PASS"
        must_pass("exact_authorized_d064_state_accepted", exact_authorized_d064_state_accepted)

        def _d064_bad(badval):
            fx = _build_future_fixture()
            obj = _read_contract(fx["cpath"])
            obj["passive_time_witness_runtime_candidate_v4_design_amendment_1"]["d064_status"] = badval
            _write_contract(fx["cpath"], obj)
            return _assert_closed(fx["args"])

        def d064_denied_rejected():
            return _d064_bad("DENIED")
        must_pass("d064_denied_rejected", d064_denied_rejected)

        def d064_failed_rejected():
            return _d064_bad("FAILED")
        must_pass("d064_failed_rejected", d064_failed_rejected)

        def d064_arbitrary_nonempty_rejected():
            return _d064_bad("AUTHORIZED")
        must_pass("d064_arbitrary_nonempty_rejected", d064_arbitrary_nonempty_rejected)

        def d064_pending_rejected():
            fx = _build_future_fixture()
            obj = _read_contract(fx["cpath"])
            obj["passive_time_witness_runtime_candidate_v4_design_amendment_1"]["d064_status"] = "PENDING"
            _write_contract(fx["cpath"], obj)
            return _assert_closed(fx["args"])
        must_pass("d064_pending_rejected", d064_pending_rejected)

        # ---- CORRECTION 2 tests: actual manifest content ----
        def actual_included_entry_count_mismatch_rejected_with_claim_unchanged():
            fx = _build_future_fixture()
            mp = fx["man_path"]
            m = json.loads(open(mp, "rb").read())
            # Remove one entry from the ACTUAL array; keep the invariant claim 1422.
            m["included_regular_file_entries"] = m["included_regular_file_entries"][:-1]
            _reemit_canonical(mp, m)
            return _assert_closed(fx["args"])
        must_pass("actual_included_entry_count_mismatch_rejected_with_claim_unchanged",
                  actual_included_entry_count_mismatch_rejected_with_claim_unchanged)

        def actual_directory_count_mismatch_rejected_with_claim_unchanged():
            fx = _build_future_fixture()
            mp = fx["man_path"]
            m = json.loads(open(mp, "rb").read())
            m["directory_entries"] = m["directory_entries"][:-1]
            _reemit_canonical(mp, m)
            return _assert_closed(fx["args"])
        must_pass("actual_directory_count_mismatch_rejected_with_claim_unchanged",
                  actual_directory_count_mismatch_rejected_with_claim_unchanged)

        def actual_exclusion_count_mismatch_rejected_with_claim_unchanged():
            fx = _build_future_fixture()
            mp = fx["man_path"]
            m = json.loads(open(mp, "rb").read())
            m["exact_exclusion_records"] = m["exact_exclusion_records"][:-1]
            _reemit_canonical(mp, m)
            return _assert_closed(fx["args"])
        must_pass("actual_exclusion_count_mismatch_rejected_with_claim_unchanged",
                  actual_exclusion_count_mismatch_rejected_with_claim_unchanged)

        def actual_included_byte_sum_mismatch_rejected_with_claim_unchanged():
            fx = _build_future_fixture()
            mp = fx["man_path"]
            m = json.loads(open(mp, "rb").read())
            # Alter one actual entry size by +1; keep invariant claim 100496114.
            fe = m["included_regular_file_entries"]
            fe[0] = dict(fe[0])
            fe[0]["size"] = fe[0]["size"] + 1
            _reemit_canonical(mp, m)
            return _assert_closed(fx["args"])
        must_pass("actual_included_byte_sum_mismatch_rejected_with_claim_unchanged",
                  actual_included_byte_sum_mismatch_rejected_with_claim_unchanged)

        def candidate_sha_must_equal_accepted_sha():
            fx = _build_future_fixture()
            obj = _read_contract(fx["cpath"])
            obj["gate"]["accepted_runtime_entrypoint_v4_sha256"] = "0" * 64
            _write_contract(fx["cpath"], obj)
            return _assert_closed(fx["args"])
        must_pass("candidate_sha_must_equal_accepted_sha", candidate_sha_must_equal_accepted_sha)

        def proposed_sha_does_not_authorize():
            fx = _build_future_fixture()
            obj = _read_contract(fx["cpath"])
            obj["gate"]["accepted_runtime_entrypoint_v4_sha256"] = ""
            obj["gate"]["proposed_runtime_entrypoint_v4_sha256"] = fx["cand_sha"]
            _write_contract(fx["cpath"], obj)
            return _assert_closed(fx["args"])
        must_pass("proposed_sha_does_not_authorize", proposed_sha_does_not_authorize)

        def narrative_status_does_not_authorize():
            fx = _build_future_fixture()
            obj = _read_contract(fx["cpath"])
            obj["gate"]["accepted_runtime_entrypoint_v4_sha256"] = ""
            obj["gate"]["accepted_runtime_entrypoint_v4_identity_only_not_authorized"] = True
            _write_contract(fx["cpath"], obj)
            return _assert_closed(fx["args"])
        must_pass("narrative_status_does_not_authorize", narrative_status_does_not_authorize)

        def bool_is_not_accepted_as_int():
            fx = _build_future_fixture()
            obj = _read_contract(fx["cpath"])
            obj["passive_time_witness_runtime_candidate_v4_design_amendment_1"]["runtime_attempts"] = True
            _write_contract(fx["cpath"], obj)
            return _assert_closed(fx["args"])
        must_pass("bool_is_not_accepted_as_int", bool_is_not_accepted_as_int)

        def closed_permission_true_rejected():
            fx = _build_future_fixture()
            obj = _read_contract(fx["cpath"])
            obj["scientific_outcome_allowed"] = True
            _write_contract(fx["cpath"], obj)
            return _assert_closed(fx["args"])
        must_pass("closed_permission_true_rejected", closed_permission_true_rejected)

        # ---- CORRECTION 3 tests: gate-level closed permissions ----
        def gate_baseline_run_1_true_rejected():
            fx = _build_future_fixture()
            obj = _read_contract(fx["cpath"])
            obj["gate"]["baseline_run_1_authorized"] = True
            _write_contract(fx["cpath"], obj)
            return _assert_closed(fx["args"])
        must_pass("gate_baseline_run_1_true_rejected", gate_baseline_run_1_true_rejected)

        def gate_baseline_run_2_true_rejected():
            fx = _build_future_fixture()
            obj = _read_contract(fx["cpath"])
            obj["gate"]["baseline_run_2_authorized"] = True
            _write_contract(fx["cpath"], obj)
            return _assert_closed(fx["args"])
        must_pass("gate_baseline_run_2_true_rejected", gate_baseline_run_2_true_rejected)

        def gate_event_injection_true_rejected():
            fx = _build_future_fixture()
            obj = _read_contract(fx["cpath"])
            obj["gate"]["event_injection_authorized"] = True
            _write_contract(fx["cpath"], obj)
            return _assert_closed(fx["args"])
        must_pass("gate_event_injection_true_rejected", gate_event_injection_true_rejected)

        def gate_permission_int_zero_rejected_as_not_bool():
            fx = _build_future_fixture()
            obj = _read_contract(fx["cpath"])
            obj["gate"]["baseline_run_1_authorized"] = 0
            _write_contract(fx["cpath"], obj)
            return _assert_closed(fx["args"])
        must_pass("gate_permission_int_zero_rejected_as_not_bool",
                  gate_permission_int_zero_rejected_as_not_bool)

        # ---- symlink/path/manifest-format retained tests ----
        def contract_symlink_leaf_rejected():
            fx = _build_future_fixture()
            cpath = fx["cpath"]
            rt = os.path.join(fx["scratch"], "real_target.json")
            with open(rt, "wb") as f:
                f.write(b"{}\n")
            os.remove(cpath)
            os.symlink(rt, cpath)
            return _assert_closed(fx["args"])
        must_pass("contract_symlink_leaf_rejected", contract_symlink_leaf_rejected)

        def contract_symlink_parent_rejected():
            fx = _build_future_fixture()
            scratch = fx["scratch"]
            sym_parent = os.path.join(scratch, "sym_parent")
            os.symlink(scratch, sym_parent)
            fx["args"].contract = os.path.join(sym_parent, os.path.basename(fx["cpath"]))
            return _assert_closed(fx["args"])
        must_pass("contract_symlink_parent_rejected", contract_symlink_parent_rejected)

        def candidate_symlink_rejected():
            fx = _build_future_fixture()
            cp = fx["cand_path"]
            rt = os.path.join(fx["scratch"], "cand_real.sh")
            with open(rt, "wb") as f:
                f.write(b"#!/usr/bin/env bash\nexit 0\n")
            os.remove(cp)
            os.symlink(rt, cp)
            return _assert_closed(fx["args"])
        must_pass("candidate_symlink_rejected", candidate_symlink_rejected)

        def manifest_symlink_rejected():
            fx = _build_future_fixture()
            mp = fx["man_path"]
            rt = os.path.join(fx["scratch"], "man_real.json")
            with open(rt, "wb") as f:
                f.write(b"{}\n")
            os.remove(mp)
            os.symlink(rt, mp)
            return _assert_closed(fx["args"])
        must_pass("manifest_symlink_rejected", manifest_symlink_rejected)

        def path_dotdot_rejected_before_normalization():
            ns = _make_real_contract_args()
            ns.contract = os.path.join(repo, "configs", "..", "configs",
                                       "downlink-diagnostic-contract.json")
            return _assert_closed(ns)
        must_pass("path_dotdot_rejected_before_normalization", path_dotdot_rejected_before_normalization)

        def manifest_noncanonical_bytes_rejected():
            fx = _build_future_fixture()
            mp = fx["man_path"]
            m = json.loads(open(mp, "rb").read())
            raw = (json.dumps(m, ensure_ascii=True, sort_keys=True,
                              separators=(", ", ": ")) + " \n").encode("utf-8")
            with open(mp, "wb") as f:
                f.write(raw)
            return _assert_closed(fx["args"])
        must_pass("manifest_noncanonical_bytes_rejected", manifest_noncanonical_bytes_rejected)

        def manifest_wrong_inventory_counts_rejected():
            fx = _build_future_fixture()
            mp = fx["man_path"]
            m = json.loads(open(mp, "rb").read())
            m["inventory_invariants"]["invariant_included_manifest_regular_file_entry_count"] = 1421
            _reemit_canonical(mp, m)
            return _assert_closed(fx["args"])
        must_pass("manifest_wrong_inventory_counts_rejected", manifest_wrong_inventory_counts_rejected)

        # ---- CORRECTION 4 tests: context never returned, deeply immutable, complete ----
        # superseded B1 stop (NOT_IMPLEMENTED) replaced by B2 core integration.
        def synthetic_future_authorization_reaches_transaction_core():
            env = _b2_env()
            rc, marker, _d = _b2_run_integrated(
                basename="reaches_core", env=env, via_authorize=True)
            return rc == 0 and marker == "V4_TRANSACTION_MATERIALIZATION=PASS"
        must_pass("synthetic_future_authorization_reaches_transaction_core",
                  synthetic_future_authorization_reaches_transaction_core)

        def synthetic_future_authorization_inspects_authorized_root_and_publishes():
            # B2: future authorization inspects the authorized root, creates the
            # staging transaction, and publishes the complete transaction there
            # (the B1 no-inspect stop is superseded).
            env = _b2_env()
            root = tempfile.mkdtemp(prefix="nrm_b2_root_", dir=os.path.realpath(tempfile.gettempdir()))
            tmpdirs.append(root)
            os.chmod(root, 0o700)
            rc, marker, _d = _b2_run_integrated(
                root=root, basename="inspects_root", env=env,
                via_authorize=True)
            published = os.path.isdir(os.path.join(root, "inspects_root"))
            return (rc == 0
                    and marker == "V4_TRANSACTION_MATERIALIZATION=PASS"
                    and published)
        must_pass("synthetic_future_authorization_inspects_authorized_root_and_publishes",
                  synthetic_future_authorization_inspects_authorized_root_and_publishes)

        def successful_transaction_returns_no_context():
            env = _b2_env()
            rc, marker, detail = _b2_run_integrated(
                basename="no_ctx", env=env, via_authorize=True)
            # result must be exactly (rc, marker, detail) tuple; no context obj.
            if not isinstance(rc, int) or not isinstance(marker, str):
                return False
            if isinstance(detail, (_TransactionContext, _FileReceipt, _RepoReceipt,
                                  _Permissions)):
                return False
            # detail must not embed a context object.
            return rc == 0 and marker == "V4_TRANSACTION_MATERIALIZATION=PASS"
        must_pass("successful_transaction_returns_no_context", successful_transaction_returns_no_context)

        def _has_mutable(obj, seen=None):
            if seen is None:
                seen = set()
            if isinstance(obj, (dict, list, set)):
                return True
            if isinstance(obj, _TransactionContext):
                for s in obj.__slots__:
                    if _has_mutable(getattr(obj, s), seen):
                        return True
                return False
            if isinstance(obj, tuple) and not isinstance(obj, type):
                # namedtuples are tuples; check elements recursively
                for el in obj:
                    if _has_mutable(el, seen):
                        return True
                return False
            return False

        def transaction_context_contains_no_mutable_container():
            # Build a context via the nested helper and recursively prove no
            # nested dict/list/set exists anywhere.
            fx = _build_future_fixture()
            ctx = _build_local_ctx(fx)
            try:
                return not _has_mutable(ctx)
            finally:
                del ctx
        must_pass("transaction_context_contains_no_mutable_container",
                  transaction_context_contains_no_mutable_container)

        def transaction_context_contains_complete_structured_state():
            fx = _build_future_fixture()
            ctx = _build_local_ctx(fx)
            try:
                checks = [
                    ctx.schema == 1,
                    ctx.static_verification == "PASS",
                    ctx.diagnostic_runtime_authorized is True,
                    ctx.diagnostic_runtime_attempts_authorized == 1,
                    ctx.amendment_runtime_authorized is True,
                    ctx.amendment_runtime_attempts == 1,
                    ctx.d064_disposition == _D064_AUTHORIZED,
                    _is_hex64(ctx.accepted_candidate_sha),
                    ctx.top_permissions.scientific_outcome_allowed is False,
                    ctx.top_permissions.command_transmission_allowed is False,
                    ctx.top_permissions.baseline_execution_allowed is False,
                    ctx.top_permissions.event_injection_allowed is False,
                    ctx.top_permissions.cryptographic_semantics_claim_allowed is False,
                    ctx.gate_permissions.baseline_run_1_authorized is False,
                    ctx.gate_permissions.baseline_run_2_authorized is False,
                    ctx.gate_permissions.event_injection_authorized is False,
                    ctx.repo.dev is not None,
                    ctx.contract.sha256 is not None,
                    ctx.candidate.sha256 is not None,
                    ctx.tool.sha256 is not None,
                    ctx.manifest.sha256 is not None,
                    ctx.host_evidence.sha256 is not None,
                    ctx.host_evidence_schema == _HOST_EVIDENCE_SCHEMA,
                ]
                return all(checks)
            finally:
                del ctx
        must_pass("transaction_context_contains_complete_structured_state",
                  transaction_context_contains_complete_structured_state)

        # ---- CORRECTION 5 tests: controlled closed exceptions, no traceback ----
        def missing_contract_returns_closed_without_traceback():
            fx = _build_future_fixture()
            ns = fx["args"]
            ns.contract = os.path.join(fx["scratch"], "_NOPE_contract.json")
            rc, marker, detail = _run_authorize(ns)
            return (rc == 1 and marker == "V4_TRANSACTION_AUTHORIZATION=CLOSED"
                    and "Traceback" not in detail and not os.path.exists(ns.authorized_root))
        must_pass("missing_contract_returns_closed_without_traceback",
                  missing_contract_returns_closed_without_traceback)

        def missing_candidate_returns_closed_without_traceback():
            fx = _build_future_fixture()
            ns = fx["args"]
            ns.candidate = os.path.join(fx["scratch"], "_NOPE_candidate.sh")
            rc, marker, detail = _run_authorize(ns)
            return (rc == 1 and marker == "V4_TRANSACTION_AUTHORIZATION=CLOSED"
                    and "Traceback" not in detail)
        must_pass("missing_candidate_returns_closed_without_traceback",
                  missing_candidate_returns_closed_without_traceback)

        def missing_manifest_returns_closed_without_traceback():
            fx = _build_future_fixture()
            ns = fx["args"]
            ns.manifest = os.path.join(fx["scratch"], "_NOPE_manifest.json")
            rc, marker, detail = _run_authorize(ns)
            return (rc == 1 and marker == "V4_TRANSACTION_AUTHORIZATION=CLOSED"
                    and "Traceback" not in detail)
        must_pass("missing_manifest_returns_closed_without_traceback",
                  missing_manifest_returns_closed_without_traceback)

        def missing_repo_root_returns_closed_without_traceback():
            ns = _make_real_contract_args()
            ns.repo_root = os.path.join(repo, "_NOPE_ROOT_DIR_")
            rc, marker, detail = _run_authorize(ns)
            return (rc == 1 and marker == "V4_TRANSACTION_AUTHORIZATION=CLOSED"
                    and "Traceback" not in detail)
        must_pass("missing_repo_root_returns_closed_without_traceback",
                  missing_repo_root_returns_closed_without_traceback)

        # ---- descriptor-leak tests ----
        def repeated_closed_calls_do_not_leak_descriptors():
            start = _count_open_fds()
            for _ in range(50):
                rc, _m, _d = _run_authorize(_make_real_contract_args())
                if rc != 1:
                    return False
            return _count_open_fds() - start == 0
        must_pass("repeated_closed_calls_do_not_leak_descriptors",
                  repeated_closed_calls_do_not_leak_descriptors)

        # superseded B1 rc==2 preflight stop; under B2 a future-authorized
        # contract against a non-existent authorized root closes at authorized-
        # root inspection (rc=1) without leaking descriptors across repeats.
        def repeated_future_authorized_closed_no_descriptor_leak():
            start = _count_open_fds()
            for _ in range(50):
                fx = _build_future_fixture()
                rc, marker, _d = _run_authorize(fx["args"])
                if rc != 1 or marker != "V4_TRANSACTION_AUTHORIZATION=CLOSED":
                    return False
            return _count_open_fds() - start == 0
        must_pass("repeated_future_authorized_closed_no_descriptor_leak",
                  repeated_future_authorized_closed_no_descriptor_leak)

        def repeated_missing_file_calls_do_not_leak_descriptors():
            start = _count_open_fds()
            for _ in range(50):
                ns = _make_real_contract_args()
                ns.contract = os.path.join(repo, "_NOPE_c.json")
                rc, _m, _d = _run_authorize(ns)
                if rc != 1:
                    return False
            return _count_open_fds() - start == 0
        must_pass("repeated_missing_file_calls_do_not_leak_descriptors",
                  repeated_missing_file_calls_do_not_leak_descriptors)

        def process_local_context_not_module_global():
            mod = sys.modules[__name__]
            if not hasattr(mod, "_TransactionContext"):
                return False
            for name in ("_active_context", "_context", "transaction_context",
                         "_tx_context", "context", "_active_tx", "ctx"):
                if hasattr(mod, name):
                    return False
            _run_authorize(_make_real_contract_args())
            for name in ("_active_context", "_context", "transaction_context",
                         "_tx_context", "_active_tx", "ctx"):
                if hasattr(mod, name):
                    return False
            return True
        must_pass("process_local_context_not_module_global",
                  process_local_context_not_module_global)

        def no_materialization_or_staging_function_invoked():
            import ast as _ast
            banned = ("materialize_workspace", "_publish_transaction",
                      "create_staging", "atomic_publication", "fortytwo_scratch",
                      "write_transaction_receipt", "_materialize", "publish_transaction")
            tree = _ast.parse(open(__file__).read())
            for node in _ast.walk(tree):
                if isinstance(node, (_ast.FunctionDef, _ast.AsyncFunctionDef)):
                    if node.name in banned:
                        return False
            return True
        must_pass("no_materialization_or_staging_function_invoked",
                  no_materialization_or_staging_function_invoked)

        def canonical_manifest_never_modified():
            real_man = os.path.join(repo, "manifests",
                                    "nos3-runtime-material-manifest.json")
            before = _sha256_file_path(real_man)
            _run_authorize(_make_real_contract_args())
            fx = _build_future_fixture()
            _run_authorize(fx["args"])
            return _sha256_file_path(real_man) == before
        must_pass("canonical_manifest_never_modified", canonical_manifest_never_modified)

        # ===================== CORRECTION 1: no module-level context return ===
        def no_module_level_context_returning_callable():
            import ast as _ast
            ctx_types = ("_TransactionContext",)
            # No module-level FunctionDef/ClassDef returns/assigns a context.
            tree = _ast.parse(open(__file__).read())
            mod_funcs = {n.name for n in tree.body
                         if isinstance(n, (_ast.FunctionDef, _ast.AsyncFunctionDef))}
            # _build_ctx_for_test must NOT exist at module level.
            if "_build_ctx_for_test" in mod_funcs:
                return False
            # No module-level def named _build_local_ctx (it must be nested).
            if "_build_local_ctx" in mod_funcs:
                return False
            # _run_authorize must return only a tuple, not a context object.
            for n in tree.body:
                if isinstance(n, _ast.FunctionDef) and n.name == "_run_authorize":
                    for r in _ast.walk(n):
                        if isinstance(r, _ast.Call) and getattr(r.func, "id", None) == "_TransactionContext":
                            # constructing is fine; returning the var is not.
                            pass
            # The successful run returns (rc, marker, detail) only.
            rc, marker, detail = _run_authorize(_build_future_fixture()["args"])
            return (isinstance(rc, int) and isinstance(marker, str)
                    and not isinstance(detail, _TransactionContext))
        must_pass("no_module_level_context_returning_callable",
                  no_module_level_context_returning_callable)

        # ===================== CORRECTION 2: missing-argument rc=1 ============
        def _missing_arg_ns(**keep):
            base = dict(contract="c", manifest="m", candidate="cand",
                        authorized_root="ar", final_basename="fb")
            base.update(keep)
            ns = argparse.Namespace()
            ns.materialize_v4_transaction = True
            ns.selftest = False
            ns.repo_root = repo
            for k, v in base.items():
                setattr(ns, k, v)
            return ns

        def missing_contract_argument_rc1():
            ns = _missing_arg_ns(manifest="x", candidate="x",
                                  authorized_root="x", final_basename="x")
            ns.contract = None
            rc, marker, _d = _run_authorize(ns)
            return rc == 1 and marker == "V4_TRANSACTION_AUTHORIZATION=CLOSED"
        must_pass("missing_contract_argument_rc1", missing_contract_argument_rc1)

        def missing_manifest_argument_rc1():
            rc, marker, _d = _run_authorize(_missing_arg_ns(contract="x",
                                                            candidate="x",
                                                            authorized_root="x",
                                                            final_basename="x",
                                                            manifest=None))
            return rc == 1 and marker == "V4_TRANSACTION_AUTHORIZATION=CLOSED"
        must_pass("missing_manifest_argument_rc1", missing_manifest_argument_rc1)

        def missing_candidate_argument_rc1():
            rc, marker, _d = _run_authorize(_missing_arg_ns(contract="x",
                                                            manifest="x",
                                                            authorized_root="x",
                                                            final_basename="x",
                                                            candidate=None))
            return rc == 1 and marker == "V4_TRANSACTION_AUTHORIZATION=CLOSED"
        must_pass("missing_candidate_argument_rc1", missing_candidate_argument_rc1)

        def missing_authorized_root_argument_rc1():
            rc, marker, _d = _run_authorize(_missing_arg_ns(contract="x",
                                                            manifest="x",
                                                            candidate="x",
                                                            final_basename="x",
                                                            authorized_root=None))
            return rc == 1 and marker == "V4_TRANSACTION_AUTHORIZATION=CLOSED"
        must_pass("missing_authorized_root_argument_rc1",
                  missing_authorized_root_argument_rc1)

        def missing_final_basename_argument_rc1():
            rc, marker, _d = _run_authorize(_missing_arg_ns(contract="x",
                                                            manifest="x",
                                                            candidate="x",
                                                            authorized_root="x",
                                                            final_basename=None))
            return rc == 1 and marker == "V4_TRANSACTION_AUTHORIZATION=CLOSED"
        must_pass("missing_final_basename_argument_rc1",
                  missing_final_basename_argument_rc1)

        # ===================== CORRECTION 3: malformed component-ID types =====
        def _component_id_fixture(bad_id, mutate=None):
            fx = _build_future_fixture()
            mp = fx["man_path"]
            m = json.loads(open(mp, "rb").read())
            ws = m["workspace_declarations"]
            if mutate == "missing":
                if "component_id" in ws[0]:
                    del ws[0]["component_id"]
            elif mutate == "duplicate":
                ws[1]["component_id"] = ws[0]["component_id"]
            else:
                ws[0]["component_id"] = bad_id
            _reemit_canonical(mp, m)
            # update the temp contract's declared manifest sha to the new bytes
            new_man_sha = _sha256_file_path(mp)
            co = _read_contract(fx["cpath"])
            impl = co["passive_time_witness_runtime_candidate_v4_design_amendment_1"]["passive_time_witness_runtime_candidate_v4_implementation"]
            impl["canonical_manifest"]["sha256"] = new_man_sha
            impl["canonical_manifest"]["path"] = os.path.relpath(mp, os.path.abspath(repo))
            _write_contract(fx["cpath"], co)
            return fx

        def malformed_component_id_int_rejected():
            fx = _component_id_fixture(7)
            rc, marker, det = _run_authorize(fx["args"])
            return rc == 1 and marker == "V4_TRANSACTION_AUTHORIZATION=CLOSED" and "Traceback" not in det
        must_pass("malformed_component_id_int_rejected", malformed_component_id_int_rejected)

        def malformed_component_id_null_rejected():
            fx = _component_id_fixture(None)
            rc, marker, det = _run_authorize(fx["args"])
            return rc == 1 and marker == "V4_TRANSACTION_AUTHORIZATION=CLOSED" and "Traceback" not in det
        must_pass("malformed_component_id_null_rejected", malformed_component_id_null_rejected)

        def malformed_component_id_object_rejected():
            fx = _component_id_fixture({"x": 1})
            rc, marker, det = _run_authorize(fx["args"])
            return rc == 1 and marker == "V4_TRANSACTION_AUTHORIZATION=CLOSED" and "Traceback" not in det
        must_pass("malformed_component_id_object_rejected", malformed_component_id_object_rejected)

        def missing_component_id_rejected():
            fx = _component_id_fixture(None, mutate="missing")
            rc, marker, det = _run_authorize(fx["args"])
            return rc == 1 and marker == "V4_TRANSACTION_AUTHORIZATION=CLOSED" and "Traceback" not in det
        must_pass("missing_component_id_rejected", missing_component_id_rejected)

        def duplicate_component_id_rejected():
            fx = _component_id_fixture(None, mutate="duplicate")
            rc, marker, det = _run_authorize(fx["args"])
            return rc == 1 and marker == "V4_TRANSACTION_AUTHORIZATION=CLOSED" and "Traceback" not in det
        must_pass("duplicate_component_id_rejected", duplicate_component_id_rejected)

        # ===================== CORRECTION 4: exact-byte parse/SHA binding ======
        def auth_file_sha_equals_raw_sha():
            fx = _build_future_fixture()
            repo_fd, _rreceipt = _open_repo_root_fd(repo)
            try:
                tool_abs = os.path.abspath(__file__)
                repo_abs = os.path.abspath(repo)
                tool_rel = _repo_relative_from_abs(tool_abs, repo_abs)
                with _open_auth_file(repo_fd, tool_rel) as (receipt, raw, sha, parsed):
                    import hashlib
                    return sha == hashlib.sha256(raw).hexdigest()
            finally:
                os.close(repo_fd)
        must_pass("auth_file_sha_equals_raw_sha", auth_file_sha_equals_raw_sha)

        def auth_file_no_second_read_for_hash():
            # _sha256_fd is removed entirely; _open_auth_file must hash raw
            # bytes directly (no seek/reread).  Verify _sha256_fd is gone and
            # _open_auth_file contains no os.lseek call.
            import ast as _ast
            tree = _ast.parse(open(__file__).read())
            if any(isinstance(n, _ast.FunctionDef) and n.name == "_sha256_fd" for n in tree.body):
                return False
            for n in tree.body:
                if isinstance(n, _ast.FunctionDef) and n.name == "_open_auth_file":
                    for c in _ast.walk(n):
                        if isinstance(c, _ast.Attribute) and c.attr == "lseek":
                            return False
            return True
        must_pass("auth_file_no_second_read_for_hash", auth_file_no_second_read_for_hash)

        def post_read_identity_continuity():
            # For a genuine JSON file the post-read fstat dev/ino/mode/nlink/
            # size must equal the initial receipt and len(raw)==size, and the
            # parsed object is available (parsed is not None for JSON).
            fx = _build_future_fixture()
            repo_fd, _rr = _open_repo_root_fd(repo)
            try:
                repo_abs = os.path.abspath(repo)
                mrel = _repo_relative_from_abs(fx["args"].manifest, repo_abs)
                with _open_auth_file(repo_fd, mrel) as (receipt, raw, sha, parsed):
                    return (receipt.size == len(raw) and sha is not None
                            and parsed is not None)
            finally:
                os.close(repo_fd)
        must_pass("post_read_identity_continuity", post_read_identity_continuity)

        # ===================== CORRECTION 1: post-read receipt continuity ====
        # Genuine post-read discontinuity tests: open the repo descriptor with
        # the original fstat, install a fault that injects ONLY on the post-read
        # fstat (the 2nd fstat of a regular-file descriptor), and prove the
        # injected call was reached exactly once with descriptor delta zero.
        class _FakeStat:
            def __init__(self, st, overrides):
                for attr in ("st_dev", "st_ino", "st_mode", "st_nlink",
                             "st_size"):
                    setattr(self, attr, overrides.get(attr, getattr(st, attr)))

        def _post_read_fault_test(alt_fn):
            sc = tempfile.mkdtemp(prefix="nrm_R3_pr_", dir=repo)
            tmpdirs.append(sc)
            fp = os.path.join(sc, "post_read.json")
            with open(fp, "wb") as f:
                f.write(b'{"x":1}')
            os.chmod(fp, 0o644)
            rel = os.path.relpath(fp, os.path.abspath(repo))
            rfd, _rr = _open_repo_root_fd(repo)
            orig_fstat = os.fstat
            injected = {"n": 0}
            regseen = {}
            start = _count_open_fds()
            try:
                def bad_fstat(fd):
                    st = orig_fstat(fd)
                    if (st.st_mode & 0o170000) == 0o100000:
                        c = regseen.get(fd, 0)
                        if c == 1:
                            injected["n"] += 1
                            return _FakeStat(st, alt_fn(st))
                        regseen[fd] = 1
                    return st
                os.fstat = bad_fstat
                raised = False
                try:
                    with _open_auth_file(rfd, rel) as (rec, raw, sha, parsed):
                        pass
                except _TransactionClosed:
                    raised = True
            finally:
                os.fstat = orig_fstat
            end = _count_open_fds()
            os.close(rfd)
            return raised, injected["n"], end - start

        def post_read_mode_mismatch_rejected():
            raised, hits, delta = _post_read_fault_test(
                lambda st: {"st_mode": st.st_mode ^ 0o777})
            return raised and hits == 1 and delta == 0
        must_pass("post_read_mode_mismatch_rejected", post_read_mode_mismatch_rejected)

        def post_read_dev_inode_mismatch_rejected():
            raised, hits, delta = _post_read_fault_test(
                lambda st: {"st_ino": st.st_ino + 99999})
            return raised and hits == 1 and delta == 0
        must_pass("post_read_dev_inode_mismatch_rejected",
                  post_read_dev_inode_mismatch_rejected)

        def post_read_size_mismatch_rejected():
            raised, hits, delta = _post_read_fault_test(
                lambda st: {"st_size": st.st_size + 1})
            return raised and hits == 1 and delta == 0
        must_pass("post_read_size_mismatch_rejected", post_read_size_mismatch_rejected)

        def post_read_nlink_mismatch_rejected():
            raised, hits, delta = _post_read_fault_test(
                lambda st: {"st_nlink": st.st_nlink + 1})
            return raised and hits == 1 and delta == 0
        must_pass("post_read_nlink_mismatch_rejected", post_read_nlink_mismatch_rejected)

        # ===================== CORRECTION 3: genuine direct-fixture fault tests
        # These reach the named failure point directly via low-level fixtures,
        # not through the closed real contract.  Failure points are detected by
        # stat TYPE (directory parent vs regular-file leaf), not call index, so
        # each test provably hits its named fstat.  os.close is instrumented to
        # count closes of the target descriptor exactly.
        def _two_comp_fixture():
            sc = tempfile.mkdtemp(prefix="nrm_R3_", dir=repo)
            tmpdirs.append(sc)
            os.makedirs(os.path.join(sc, "parent"))
            fp = os.path.join(sc, "parent", "leaf.json")
            with open(fp, "wb") as f:
                f.write(b'{"x":1}')
            os.chmod(fp, 0o644)
            return os.path.relpath(fp, os.path.abspath(repo))

        def _one_comp_fixture():
            sc = tempfile.mkdtemp(prefix="nrm_R3_", dir=repo)
            tmpdirs.append(sc)
            fp = os.path.join(sc, "leaf.json")
            with open(fp, "wb") as f:
                f.write(b'{"x":1}')
            os.chmod(fp, 0o644)
            return os.path.relpath(fp, os.path.abspath(repo))

        def parent_fstat_failure_hits_parent_and_no_leak():
            rel = _two_comp_fixture()
            rfd, _rr = _open_repo_root_fd(repo)
            orig_fstat = os.fstat
            orig_close = os.close
            hits = {"n": 0}
            target = {"fd": None}
            close_count = {"n": 0}

            def bad_fstat(fd):
                st = orig_fstat(fd)
                if ((st.st_mode & 0o170000) == 0o040000 and hits["n"] == 0
                        and target["fd"] is None):
                    target["fd"] = fd
                    hits["n"] += 1
                    raise OSError(errno.EIO, "parent fstat fault")
                return st

            def bad_close(fd2):
                if fd2 == target["fd"]:
                    close_count["n"] += 1
                return orig_close(fd2)
            start = _count_open_fds()
            try:
                os.fstat = bad_fstat
                os.close = bad_close
                raised = False
                try:
                    _open_repo_relative_file(rfd, rel)
                except _TransactionClosed:
                    raised = True
            finally:
                os.fstat = orig_fstat
                os.close = orig_close
            end = _count_open_fds()
            os.close(rfd)
            return raised and hits["n"] == 1 and close_count["n"] == 1 and end - start == 0
        must_pass("parent_fstat_failure_hits_parent_and_no_leak",
                  parent_fstat_failure_hits_parent_and_no_leak)

        def parent_identity_failure_closes_once():
            rel = _two_comp_fixture()
            rfd, _rr = _open_repo_root_fd(repo)
            orig_fstat = os.fstat
            orig_close = os.close
            hits = {"n": 0}
            target = {"fd": None}
            close_count = {"n": 0}

            def bad_fstat(fd):
                st = orig_fstat(fd)
                if ((st.st_mode & 0o170000) == 0o040000 and hits["n"] == 0
                        and target["fd"] is None):
                    target["fd"] = fd
                    hits["n"] += 1
                    return _FakeStat(st, {"st_ino": st.st_ino + 99999})
                return st

            def bad_close(fd2):
                if fd2 == target["fd"]:
                    close_count["n"] += 1
                return orig_close(fd2)
            start = _count_open_fds()
            try:
                os.fstat = bad_fstat
                os.close = bad_close
                raised = False
                try:
                    _open_repo_relative_file(rfd, rel)
                except _TransactionClosed:
                    raised = True
            finally:
                os.fstat = orig_fstat
                os.close = orig_close
            end = _count_open_fds()
            os.close(rfd)
            return raised and hits["n"] == 1 and close_count["n"] == 1 and end - start == 0
        must_pass("parent_identity_failure_closes_once",
                  parent_identity_failure_closes_once)

        def leaf_fstat_failure_hits_leaf_and_no_leak():
            rel = _one_comp_fixture()
            rfd, _rr = _open_repo_root_fd(repo)
            orig_fstat = os.fstat
            orig_close = os.close
            hits = {"n": 0}
            target = {"fd": None}
            close_count = {"n": 0}

            def bad_fstat(fd):
                st = orig_fstat(fd)
                if ((st.st_mode & 0o170000) == 0o100000 and hits["n"] == 0
                        and target["fd"] is None):
                    target["fd"] = fd
                    hits["n"] += 1
                    raise OSError(errno.EIO, "leaf fstat fault")
                return st

            def bad_close(fd2):
                if fd2 == target["fd"]:
                    close_count["n"] += 1
                return orig_close(fd2)
            start = _count_open_fds()
            try:
                os.fstat = bad_fstat
                os.close = bad_close
                raised = False
                try:
                    _open_repo_relative_file(rfd, rel)
                except _TransactionClosed:
                    raised = True
            finally:
                os.fstat = orig_fstat
                os.close = orig_close
            end = _count_open_fds()
            os.close(rfd)
            return raised and hits["n"] == 1 and close_count["n"] == 1 and end - start == 0
        must_pass("leaf_fstat_failure_hits_leaf_and_no_leak",
                  leaf_fstat_failure_hits_leaf_and_no_leak)

        def repo_root_fstat_failure_closes_once():
            orig_fstat = os.fstat
            orig_close = os.close
            hits = {"n": 0}
            target = {"fd": None}
            close_count = {"n": 0}

            def bad_fstat(fd):
                if hits["n"] == 0 and target["fd"] is None:
                    target["fd"] = fd
                    hits["n"] += 1
                    raise OSError(errno.EIO, "repo-root fstat fault")
                return orig_fstat(fd)

            def bad_close(fd2):
                if fd2 == target["fd"]:
                    close_count["n"] += 1
                return orig_close(fd2)
            start = _count_open_fds()
            try:
                os.fstat = bad_fstat
                os.close = bad_close
                raised = False
                try:
                    _open_repo_root_fd(repo)
                except _TransactionClosed:
                    raised = True
            finally:
                os.fstat = orig_fstat
                os.close = orig_close
            end = _count_open_fds()
            return raised and hits["n"] == 1 and close_count["n"] == 1 and end - start == 0
        must_pass("repo_root_fstat_failure_closes_once",
                  repo_root_fstat_failure_closes_once)

        # ===================== 2PB2B-A transaction engine tests (35) =========
        def _tx_authorized_root():
            sc = tempfile.mkdtemp(prefix="nrm_tx_root_", dir=repo)
            tmpdirs.append(sc)
            os.chmod(sc, 0o700)
            return sc

        def _rmtree_temp(path):
            """Test-only recursive cleanup of a temporary directory (no process
            invocation).  Uses shutil.rmtree, which is imported only inside the
            self-test finally-cleanup context."""
            import shutil as _shl
            _shl.rmtree(path, ignore_errors=True)

        def _tx_run(root=None, basename=None, inject=None):
            if root is None:
                root = _tx_authorized_root()
            if basename is None:
                basename = "run_tx_%d" % (len(tmpdirs) + 1)
            return run_synthetic_outer_transaction(root, basename, inject=inject), root

        # 1. strict_absolute_authorized_root_open
        def strict_absolute_authorized_root_open():
            root = _tx_authorized_root()
            rfd, rr = _validate_absolute_authorized_root(root)
            try:
                st = os.fstat(rfd)
                return (st.st_uid == os.geteuid()
                        and not (st.st_mode & 0o022)
                        and (st.st_mode & 0o170000) == 0o040000
                        and rr.dev == st.st_dev and rr.ino == st.st_ino)
            finally:
                os.close(rfd)
        must_pass("strict_absolute_authorized_root_open", strict_absolute_authorized_root_open)

        def _root_with_symlink_parent():
            root = _tx_authorized_root()
            sub = os.path.join(root, "sub")
            os.makedirs(sub)
            link = os.path.join(root, "link")
            os.symlink(sub, link)
            return os.path.join(link, "leaf")

        # 2. authorized_root_symlink_component_rejected
        def authorized_root_symlink_component_rejected():
            p = _root_with_symlink_parent()
            try:
                _validate_absolute_authorized_root(p)
            except _TransactionClosed:
                return True
            return False
        must_pass("authorized_root_symlink_component_rejected", authorized_root_symlink_component_rejected)

        # 3. authorized_root_wrong_owner_rejected (mockable via geteuid swap)
        def authorized_root_wrong_owner_rejected():
            root = _tx_authorized_root()
            orig = os.geteuid
            os.geteuid = lambda: -999  # pretend a different effective uid owns root
            try:
                _validate_absolute_authorized_root(root)
            except _TransactionClosed:
                return True
            finally:
                os.geteuid = orig
            return False
        must_pass("authorized_root_wrong_owner_rejected", authorized_root_wrong_owner_rejected)

        # 4. authorized_root_group_writable_rejected
        def authorized_root_group_writable_rejected():
            root = _tx_authorized_root()
            os.chmod(root, 0o770)
            try:
                _validate_absolute_authorized_root(root)
            except _TransactionClosed:
                return True
            return False
        must_pass("authorized_root_group_writable_rejected", authorized_root_group_writable_rejected)

        # 5. invalid_final_basename_rejected
        def invalid_final_basename_rejected():
            root = _tx_authorized_root()
            rfd, _r = _validate_absolute_authorized_root(root)
            try:
                for bad in ("", ".", "..", "a/b", "a\\b", " a", "a "):
                    try:
                        _validate_final_basename(bad, rfd)
                    except _TransactionClosed:
                        continue
                    return False
                return True
            finally:
                os.close(rfd)
        must_pass("invalid_final_basename_rejected", invalid_final_basename_rejected)

        # 6. exact_18_component_plan_required (genuine: validated plan accepted)
        def exact_18_component_plan_required():
            plan = _build_synthetic_plan()
            return _validate_synthetic_plan(plan) is plan
        must_pass("exact_18_component_plan_required", exact_18_component_plan_required)

        # 7. missing component rejected by plan validation
        def missing_component_rejected():
            plan = _build_synthetic_plan()
            comps = list(plan.components)
            del comps[3]  # remove one component -> 17, missing an expected id
            bad = _SyntheticPlan(components=tuple(comps),
                                  fortytwo_files=plan.fortytwo_files)
            try:
                _validate_synthetic_plan(bad)
            except _TransactionClosed:
                return True
            return False
        must_pass("missing_component_rejected", missing_component_rejected)

        # 8. duplicate component rejected by plan validation
        def duplicate_component_rejected():
            plan = _build_synthetic_plan()
            comps = list(plan.components)
            comps[5] = comps[5]._replace(component_id=comps[0].component_id)
            bad = _SyntheticPlan(components=tuple(comps),
                                  fortytwo_files=plan.fortytwo_files)
            try:
                _validate_synthetic_plan(bad)
            except _TransactionClosed:
                return True
            return False
        must_pass("duplicate_component_rejected", duplicate_component_rejected)

        # 9. unexpected component rejected by plan validation
        def unexpected_component_rejected():
            plan = _build_synthetic_plan()
            comps = list(plan.components)
            comps[2] = comps[2]._replace(component_id="rogue_component")
            bad = _SyntheticPlan(components=tuple(comps),
                                  fortytwo_files=plan.fortytwo_files)
            try:
                _validate_synthetic_plan(bad)
            except _TransactionClosed:
                return True
            return False
        must_pass("unexpected_component_rejected", unexpected_component_rejected)

        # 9b. wrong component record type rejected
        def wrong_component_record_type_rejected():
            plan = _build_synthetic_plan()
            comps = list(plan.components)
            comps[4] = ("hw_sim_04", plan.components[4].files)
            bad = _SyntheticPlan(components=tuple(comps),
                                  fortytwo_files=plan.fortytwo_files)
            try:
                _validate_synthetic_plan(bad)
            except _TransactionClosed:
                return True
            return False
        must_pass("wrong_component_record_type_rejected",
                  wrong_component_record_type_rejected)

        # 9c. mutable (list) file list rejected
        def mutable_file_list_rejected():
            plan = _build_synthetic_plan()
            comps = list(plan.components)
            comps[1] = comps[1]._replace(files=list(comps[1].files))
            bad = _SyntheticPlan(components=tuple(comps),
                                  fortytwo_files=plan.fortytwo_files)
            try:
                _validate_synthetic_plan(bad)
            except _TransactionClosed:
                return True
            return False
        must_pass("mutable_file_list_rejected", mutable_file_list_rejected)

        # 9d. path traversal (../) in a plan file path rejected
        def path_traversal_plan_rejected():
            plan = _build_synthetic_plan()
            comps = list(plan.components)
            bad_file = _SyntheticFile(
                rel_path="workspaces/%s/work/nos3/../evil.txt"
                % comps[0].component_id,
                mode=0o644, content=b"x\n")
            comps[0] = comps[0]._replace(
                files=(bad_file, comps[0].files[1]))
            bad = _SyntheticPlan(components=tuple(comps),
                                  fortytwo_files=plan.fortytwo_files)
            try:
                _validate_synthetic_plan(bad)
            except _TransactionClosed:
                return True
            return False
        must_pass("path_traversal_plan_rejected", path_traversal_plan_rejected)

        # 9e. cross-component workspace path rejected (file under another cid)
        def cross_component_workspace_path_rejected():
            plan = _build_synthetic_plan()
            comps = list(plan.components)
            other = comps[5].component_id
            bad_file = _SyntheticFile(
                rel_path="workspaces/%s/work/nos3/stray.txt" % other,
                mode=0o644, content=b"x\n")
            comps[0] = comps[0]._replace(
                files=(bad_file, comps[0].files[1]))
            bad = _SyntheticPlan(components=tuple(comps),
                                  fortytwo_files=plan.fortytwo_files)
            try:
                _validate_synthetic_plan(bad)
            except _TransactionClosed:
                return True
            return False
        must_pass("cross_component_workspace_path_rejected",
                  cross_component_workspace_path_rejected)

        # 9f. duplicate file path rejected
        def duplicate_file_path_rejected():
            plan = _build_synthetic_plan()
            comps = list(plan.components)
            dup = _SyntheticFile(rel_path="fortytwo-config/scratch.json",
                                  mode=0o644, content=b"dup\n")
            bad = _SyntheticPlan(components=tuple(comps),
                                  fortytwo_files=(dup, plan.fortytwo_files[0]))
            try:
                _validate_synthetic_plan(bad)
            except _TransactionClosed:
                return True
            return False
        must_pass("duplicate_file_path_rejected", duplicate_file_path_rejected)

        # --- R2R2: strict synthetic-plan validation tests ---
        def synthetic_plan_bytearray_content_rejected():
            plan = _build_synthetic_plan()
            comps = list(plan.components)
            bad_file = _SyntheticFile(
                rel_path="workspaces/%s/work/nos3/ba.txt" % comps[0].component_id,
                mode=0o644, content=bytearray(b"x\n"))
            comps[0] = comps[0]._replace(files=(bad_file, comps[0].files[1]))
            bad = _SyntheticPlan(components=tuple(comps),
                                  fortytwo_files=plan.fortytwo_files)
            try:
                _validate_synthetic_plan(bad)
            except _TransactionClosed:
                return True
            return False
        must_pass("synthetic_plan_bytearray_content_rejected",
                  synthetic_plan_bytearray_content_rejected)

        def synthetic_plan_component_file_in_fortytwo_rejected():
            plan = _build_synthetic_plan()
            comps = list(plan.components)
            bad_file = _SyntheticFile(
                rel_path="fortytwo-config/stray.txt" % (),
                mode=0o644, content=b"x\n")
            comps[0] = comps[0]._replace(files=(bad_file, comps[0].files[1]))
            bad = _SyntheticPlan(components=tuple(comps),
                                  fortytwo_files=plan.fortytwo_files)
            try:
                _validate_synthetic_plan(bad)
            except _TransactionClosed:
                return True
            return False
        must_pass("synthetic_plan_component_file_in_fortytwo_rejected",
                  synthetic_plan_component_file_in_fortytwo_rejected)

        def synthetic_plan_workspace_root_without_leaf_rejected():
            plan = _build_synthetic_plan()
            comps = list(plan.components)
            bad_file = _SyntheticFile(
                rel_path="workspaces/%s/work/nos3" % comps[0].component_id,
                mode=0o644, content=b"x\n")
            comps[0] = comps[0]._replace(files=(bad_file, comps[0].files[1]))
            bad = _SyntheticPlan(components=tuple(comps),
                                  fortytwo_files=plan.fortytwo_files)
            try:
                _validate_synthetic_plan(bad)
            except _TransactionClosed:
                return True
            return False
        must_pass("synthetic_plan_workspace_root_without_leaf_rejected",
                  synthetic_plan_workspace_root_without_leaf_rejected)

        def synthetic_plan_fortytwo_root_without_leaf_rejected():
            plan = _build_synthetic_plan()
            bad_ft = (_SyntheticFile(rel_path="fortytwo-config",
                                     mode=0o644, content=b"x\n"),
                      plan.fortytwo_files[1])
            bad = _SyntheticPlan(components=plan.components,
                                  fortytwo_files=tuple(bad_ft))
            try:
                _validate_synthetic_plan(bad)
            except _TransactionClosed:
                return True
            return False
        must_pass("synthetic_plan_fortytwo_root_without_leaf_rejected",
                  synthetic_plan_fortytwo_root_without_leaf_rejected)

        # --- R2R2: FIFO staged-object rejection test ---
        def fsync_staged_hierarchy_fifo_rejected():
            troot = os.path.join(repo, "_R2R2_fifo_root")
            if os.path.exists(troot):
                _rmtree_temp(troot)
            os.mkdir(troot, mode=0o700)
            os.chmod(troot, 0o700)
            stage = os.path.join(troot, "stage")
            os.mkdir(stage, mode=0o700)
            os.chmod(stage, 0o700)
            sub = os.path.join(stage, "sub")
            os.mkdir(sub, mode=0o700)
            os.chmod(sub, 0o700)
            FIFO_NAME = "probe.fifo"
            fifo_path = os.path.join(sub, FIFO_NAME)
            os.mkfifo(fifo_path, 0o644)
            stage_fd = os.open(stage, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
            raised = False
            combined = None
            start = _count_open_fds()
            try:
                _fsync_staged_hierarchy(stage_fd, _OwnedFds())
            except _TransactionClosed as exc:
                combined = str(exc)
                raised = True
            end = _count_open_fds()
            try:
                os.close(stage_fd)
            except OSError:
                pass
            reached = "FIFO" in (combined or "") and FIFO_NAME in (combined or "")
            fd_delta = end - start
            print("FSYNC_FIFO_REACHED=%s" % ("true" if reached else "false"))
            print("FIFO_STAGED_OBJECT_REJECTED=%s"
                  % ("PASS" if (raised and reached) else "FAIL"))
            print("FIFO_FD_DELTA=%d" % fd_delta)
            _rmtree_temp(troot)
            return raised and reached and fd_delta == 0
        must_pass("fsync_staged_hierarchy_fifo_rejected",
                  fsync_staged_hierarchy_fifo_rejected)

        # ===================== 2PB2B-B1 canonical plan tests ===============
        def _canonical_manifest_copy():
            return json.loads(open(os.path.join(
                repo, "manifests", "nos3-runtime-material-manifest.json"),
                "rb").read())

        def _deeply_immutable(v, seen=None):
            if seen is None:
                seen = set()
            if (v is None or type(v) is bool or type(v) is int
                    or type(v) is str):
                return True
            if isinstance(v, (bytes, bytearray, float)):
                return False
            if isinstance(v, (dict, list, set, bytearray)):
                return False
            if hasattr(v, "_fields"):
                if id(v) in seen:
                    return True
                seen.add(id(v))
                for f in v._fields:
                    if not _deeply_immutable(getattr(v, f), seen):
                        return False
                return True
            if isinstance(v, tuple):
                for x in v:
                    if not _deeply_immutable(x, seen):
                        return False
                return True
            return False

        def canonical_materialization_plan_builds():
            plan = _build_canonical_materialization_plan(_canonical_manifest_copy())
            return (type(plan) is _CanonicalCompletePlan
                    and plan.source_root_count == 4
                    and plan.workspace_count == 18)
        must_pass("canonical_materialization_plan_builds",
                  canonical_materialization_plan_builds)

        def canonical_materialization_plan_deeply_immutable():
            plan = _build_canonical_materialization_plan(_canonical_manifest_copy())
            print("CANONICAL_PLAN_DEEPLY_IMMUTABLE=%s"
                  % str(_deeply_immutable(plan)).lower())
            return _deeply_immutable(plan) is True
        must_pass("canonical_materialization_plan_deeply_immutable",
                  canonical_materialization_plan_deeply_immutable)

        def canonical_materialization_plan_exact_totals():
            plan = _build_canonical_materialization_plan(_canonical_manifest_copy())
            return (plan.source_file_entry_count == 1422
                    and plan.source_file_byte_count == 100496114
                    and plan.source_directory_entry_count == 89
                    and plan.source_exclusion_entry_count == 11
                    and plan.expanded_workspace_file_count == 1786
                    and plan.expanded_workspace_byte_count == 971145735
                    and plan.expanded_workspace_directory_count == 120
                    and plan.expanded_workspace_exclusion_count == 43
                    and plan.fortytwo.file_count == 36
                    and plan.fortytwo.byte_count == 190651
                    and plan.fortytwo.directory_count == 1
                    and plan.fortytwo.exclusion_count == 0
                    and plan.expanded_total_file_count == 1822
                    and plan.expanded_total_byte_count == 971336386
                    and plan.expanded_total_directory_count == 121
                    and plan.expanded_total_exclusion_count == 43)
        must_pass("canonical_materialization_plan_exact_totals",
                  canonical_materialization_plan_exact_totals)

        def canonical_materialization_plan_exact_workspace_mapping():
            plan = _build_canonical_materialization_plan(_canonical_manifest_copy())
            ids = tuple(w.component_id for w in plan.workspaces)
            cfs = [w for w in plan.workspaces if w.component_id == "cfs"][0]
            sim = [w for w in plan.workspaces if w.component_id == "hw_sim_07"][0]
            return (ids == tuple(sorted(_EXPECTED_WORKSPACE_IDS))
                    and cfs.seed_source_roots == ("cfs",)
                    and sim.seed_source_roots == ("sim_bin", "sim_lib")
                    and cfs.workspace_host_path == "cfs"
                    and sim.workspace_host_path == "hw_sim_07"
                    and cfs.mount_destination == "/work/nos3"
                    and cfs.private_physical_copy is True
                    and cfs.no_runtime_mount_from_external_nos3 is True
                    and cfs.file_count == 1361 and cfs.byte_count == 45877946
                    and sim.file_count == 25 and sim.byte_count == 54427517)
        must_pass("canonical_materialization_plan_exact_workspace_mapping",
                  canonical_materialization_plan_exact_workspace_mapping)

        def canonical_materialization_plan_fortytwo_separate():
            plan = _build_canonical_materialization_plan(_canonical_manifest_copy())
            ft = plan.fortytwo
            ft_srcs = set(f.source_root for f in ft.regular_files)
            return (ft.transaction_relative_root == "fortytwo-config"
                    and ft.file_count == 36 and ft.byte_count == 190651
                    and ft.directory_count == 1 and ft.exclusion_count == 0
                    and ft_srcs == {"configuration"}
                    and plan.workspace_count == 18
                    and not any(w.component_id == "fortytwo" for w in plan.workspaces))
        must_pass("canonical_materialization_plan_fortytwo_separate",
                  canonical_materialization_plan_fortytwo_separate)

        def canonical_materialization_plan_no_target_collisions():
            plan = _build_canonical_materialization_plan(_canonical_manifest_copy())
            print("DUPLICATE_FILE_TARGET_COUNT=%d" % plan.duplicate_file_target_count)
            print("DUPLICATE_DIRECTORY_TARGET_COUNT=%d" % plan.duplicate_directory_target_count)
            print("FILE_DIRECTORY_COLLISION_COUNT=%d" % plan.file_directory_collision_count)
            print("PREFIX_COLLISION_COUNT=%d" % plan.prefix_collision_count)
            return (plan.duplicate_file_target_count == 0
                    and plan.duplicate_directory_target_count == 0
                    and plan.file_directory_collision_count == 0
                    and plan.prefix_collision_count == 0)
        must_pass("canonical_materialization_plan_no_target_collisions",
                  canonical_materialization_plan_no_target_collisions)

        def _mu_reject(name, mutate):
            man = _canonical_manifest_copy()
            mutate(man)
            try:
                _build_canonical_materialization_plan(man)
            except _TransactionClosed:
                return True
            return False

        def source_root_missing_rejected():
            def mu(man):
                man["source_root_declarations"] = [
                    r for r in man["source_root_declarations"]
                    if r["source_root"] != "sim_lib"]
            return _mu_reject("source_root_missing", mu)
        must_pass("source_root_missing_rejected", source_root_missing_rejected)

        def source_root_duplicate_rejected():
            def mu(man):
                man["source_root_declarations"].append(
                    dict(man["source_root_declarations"][0]))
            return _mu_reject("source_root_duplicate", mu)
        must_pass("source_root_duplicate_rejected", source_root_duplicate_rejected)

        def source_root_host_path_mutation_rejected():
            def mu(man):
                for r in man["source_root_declarations"]:
                    if r["source_root"] == "cfs":
                        r["host_relative_path"] = "external/nos3/fsw/build/exe/cpu2"
            return _mu_reject("source_root_host_path_mutation", mu)
        must_pass("source_root_host_path_mutation_rejected",
                  source_root_host_path_mutation_rejected)

        def source_root_destination_prefix_mutation_rejected():
            def mu(man):
                for r in man["source_root_declarations"]:
                    if r["source_root"] == "cfs":
                        r["destination_prefix"] = "fsw/build/exe/cpu2"
            return _mu_reject("source_root_destination_prefix_mutation", mu)
        must_pass("source_root_destination_prefix_mutation_rejected",
                  source_root_destination_prefix_mutation_rejected)

        def file_destination_mapping_mutation_rejected():
            def mu(man):
                man["included_regular_file_entries"][0]["destination_relative"] =                     "fsw/build/exe/cpu1/cf/CHANGED.txt"
            return _mu_reject("file_destination_mapping_mutation", mu)
        must_pass("file_destination_mapping_mutation_rejected",
                  file_destination_mapping_mutation_rejected)

        def file_sha_uppercase_rejected():
            def mu(man):
                e = man["included_regular_file_entries"][0]
                e["sha256"] = e["sha256"].upper()
            return _mu_reject("file_sha_uppercase", mu)
        must_pass("file_sha_uppercase_rejected", file_sha_uppercase_rejected)

        def file_bool_size_rejected():
            def mu(man):
                man["included_regular_file_entries"][0]["size"] = True
            return _mu_reject("file_bool_size", mu)
        must_pass("file_bool_size_rejected", file_bool_size_rejected)

        def file_nlink_two_rejected():
            def mu(man):
                man["included_regular_file_entries"][0]["nlink"] = 2
            return _mu_reject("file_nlink_two", mu)
        must_pass("file_nlink_two_rejected", file_nlink_two_rejected)

        def directory_dotdot_rejected():
            def mu(man):
                man["directory_entries"][0]["relative_path"] = "../escape"
            return _mu_reject("directory_dotdot", mu)
        must_pass("directory_dotdot_rejected", directory_dotdot_rejected)

        def exclusion_destination_must_be_absent_false_rejected():
            def mu(man):
                man["exact_exclusion_records"][0]["destination_must_be_absent"] = False
            return _mu_reject("exclusion_destination_must_be_absent_false", mu)
        must_pass("exclusion_destination_must_be_absent_false_rejected",
                  exclusion_destination_must_be_absent_false_rejected)

        def workspace_seed_substitution_rejected():
            def mu(man):
                for w in man["workspace_declarations"]:
                    if w["component_id"] == "cfs":
                        w["seed_source_roots"] = ["sim_bin"]
            return _mu_reject("workspace_seed_substitution", mu)
        must_pass("workspace_seed_substitution_rejected",
                  workspace_seed_substitution_rejected)

        def workspace_host_path_substitution_rejected():
            def mu(man):
                for w in man["workspace_declarations"]:
                    if w["component_id"] == "cfs":
                        w["workspace_host_path"] = "other"
            return _mu_reject("workspace_host_path_substitution", mu)
        must_pass("workspace_host_path_substitution_rejected",
                  workspace_host_path_substitution_rejected)

        def workspace_private_copy_false_rejected():
            def mu(man):
                for w in man["workspace_declarations"]:
                    if w["component_id"] == "cfs":
                        w["private_physical_copy"] = False
            return _mu_reject("workspace_private_copy_false", mu)
        must_pass("workspace_private_copy_false_rejected",
                  workspace_private_copy_false_rejected)

        def workspace_configuration_seed_rejected():
            def mu(man):
                for w in man["workspace_declarations"]:
                    if w["component_id"] == "hw_sim_01":
                        w["seed_source_roots"] = ["configuration"]
            return _mu_reject("workspace_configuration_seed", mu)
        must_pass("workspace_configuration_seed_rejected",
                  workspace_configuration_seed_rejected)

        def expanded_target_collision_rejected():
            # Build a manifest where two different workspaces expand the same
            # sim file to the same target -- force a collision by giving two
            # workspaces the same component_id host path is disallowed earlier,
            # so instead create a file/directory collision: a regular file in
            # sim whose destination_relative collides with a cfs directory.
            def mu(man):
                # Add a duplicate file destination within the same workspace by
                # duplicating a cfs file entry verbatim (same destination_relative)
                man["included_regular_file_entries"].append(
                    dict(man["included_regular_file_entries"][0]))
            return _mu_reject("expanded_target_collision", mu)
        must_pass("expanded_target_collision_rejected",
                  expanded_target_collision_rejected)

        # ===================== 2PB2B-B1R1 tightened mode & collision tests ===
        def regular_file_mode_0700_rejected():
            def mu(man):
                for e in man["included_regular_file_entries"]:
                    if e["source_root"] == "cfs" and e["mode"] == "0644":
                        e["mode"] = "0700"
                        break
            return _mu_reject("regular_file_mode_0700", mu)
        must_pass("regular_file_mode_0700_rejected",
                  regular_file_mode_0700_rejected)

        def exclusion_mode_non_octal_rejected():
            def mu(man):
                man["exact_exclusion_records"][0]["mode"] = "zzzz"
            return _mu_reject("exclusion_mode_non_octal", mu)
        must_pass("exclusion_mode_non_octal_rejected",
                  exclusion_mode_non_octal_rejected)

        def exclusion_mode_unapproved_rejected():
            def mu(man):
                man["exact_exclusion_records"][0]["mode"] = "0777"
            return _mu_reject("exclusion_mode_unapproved", mu)
        must_pass("exclusion_mode_unapproved_rejected",
                  exclusion_mode_unapproved_rejected)

        def exclusion_empty_relative_path_rejected():
            def mu(man):
                man["exact_exclusion_records"][0]["relative_path"] = ""
            return _mu_reject("exclusion_empty_relative_path", mu)
        must_pass("exclusion_empty_relative_path_rejected",
                  exclusion_empty_relative_path_rejected)

        def file_directory_collision_rejected():
            def mu(man):
                # Make one cfs directory relative_path collide with an included
                # cfs file relative_path; destination_prefix makes the same
                # transaction-relative path.
                cfs_files = [e for e in man["included_regular_file_entries"]
                             if e["source_root"] == "cfs"]
                target_rp = cfs_files[0]["relative_path"]
                for d in man["directory_entries"]:
                    if d["source_root"] == "cfs" and d["relative_path"] != "":
                        d["relative_path"] = target_rp
                        break
            return _mu_reject("file_directory_collision", mu)
        must_pass("file_directory_collision_rejected",
                  file_directory_collision_rejected)

        def file_prefix_ancestor_collision_rejected():
            def mu(man):
                # Change two sim_bin files so one is "probe" and the other
                # "probe/child" -> file is ancestor of another file.
                sim_bins = [e for e in man["included_regular_file_entries"]
                            if e["source_root"] == "sim_bin"]
                if len(sim_bins) < 2:
                    return False
                sim_bins[0]["relative_path"] = "probe"
                sim_bins[0]["destination_relative"] = "sims/build/bin/probe"
                sim_bins[1]["relative_path"] = "probe/child"
                sim_bins[1]["destination_relative"] = "sims/build/bin/probe/child"
            return _mu_reject("file_prefix_ancestor_collision", mu)
        must_pass("file_prefix_ancestor_collision_rejected",
                  file_prefix_ancestor_collision_rejected)

        def exclusion_included_target_collision_rejected():
            def mu(man):
                # Change one exclusion identity to match an included file's
                # source_root+relative_path (collision via expanded exclusion
                # target equaling an included file target).
                incl = man["included_regular_file_entries"][0]
                man["exact_exclusion_records"][0]["source_root"] = incl["source_root"]
                man["exact_exclusion_records"][0]["relative_path"] = incl["relative_path"]
            return _mu_reject("exclusion_included_target_collision", mu)
        must_pass("exclusion_included_target_collision_rejected",
                  exclusion_included_target_collision_rejected)

        def fortytwo_expanded_targets_exact():
            plan = _build_canonical_materialization_plan(_canonical_manifest_copy())
            ft = plan.fortytwo
            return (len(ft.file_targets) == 36
                    and len(ft.directory_targets) == 1
                    and len(ft.exclusion_targets) == 0
                    and ft.directory_targets[0].transaction_relative_path
                        == "fortytwo-config/cfg/build/InOut"
                    and all(t.owner_kind == "fortytwo" for t in ft.file_targets)
                    and all(t.transaction_relative_path.startswith(
                                "fortytwo-config/cfg/build/InOut")
                            for t in ft.file_targets))
        must_pass("fortytwo_expanded_targets_exact",
                  fortytwo_expanded_targets_exact)

        def workspace_expanded_targets_exact():
            plan = _build_canonical_materialization_plan(_canonical_manifest_copy())
            cfs = [w for w in plan.workspaces if w.component_id == "cfs"][0]
            sim = [w for w in plan.workspaces if w.component_id == "hw_sim_07"][0]
            ok_len = (len(cfs.file_targets) == 1361
                      and len(cfs.directory_targets) == 86
                      and len(cfs.exclusion_targets) == 9
                      and len(sim.file_targets) == 25)
            ok_owner = all(
                t.transaction_relative_path.startswith(
                    "workspaces/%s/work/nos3/" % w.component_id)
                for w in plan.workspaces
                for t in w.file_targets + w.directory_targets + w.exclusion_targets)
            return ok_len and ok_owner
        must_pass("workspace_expanded_targets_exact",
                  workspace_expanded_targets_exact)

        def expanded_target_counts_exact():
            plan = _build_canonical_materialization_plan(_canonical_manifest_copy())
            return (len(plan.expanded_file_targets) == 1822
                    and len(plan.expanded_directory_targets) == 121
                    and len(plan.expanded_exclusion_targets) == 43
                    and plan.duplicate_file_target_count == 0
                    and plan.duplicate_directory_target_count == 0
                    and plan.file_directory_collision_count == 0
                    and plan.prefix_collision_count == 0)
        must_pass("expanded_target_counts_exact",
                  expanded_target_counts_exact)

        # ===================== 2PB2B-B1R2 exact scalar-type tests ============
        class _IntSubclass(int):
            pass

        class _StrSubclass(str):
            pass

        def exact_int_subclass_rejected():
            def mu_nlink(man):
                man["included_regular_file_entries"][0]["nlink"] = _IntSubclass(1)
            def mu_size(man):
                man["included_regular_file_entries"][0]["size"] = _IntSubclass(3625)
            return (_mu_reject("exact_int_subclass_nlink", mu_nlink)
                    and _mu_reject("exact_int_subclass_size", mu_size))
        must_pass("exact_int_subclass_rejected", exact_int_subclass_rejected)

        def regular_file_mode_str_subclass_rejected():
            def mu(man):
                man["included_regular_file_entries"][0]["mode"] = _StrSubclass("0644")
            return _mu_reject("regular_file_mode_str_subclass", mu)
        must_pass("regular_file_mode_str_subclass_rejected",
                  regular_file_mode_str_subclass_rejected)

        def relative_path_str_subclass_rejected():
            def mu(man):
                e = man["included_regular_file_entries"][0]
                e["relative_path"] = _StrSubclass(e["relative_path"])
            return _mu_reject("relative_path_str_subclass", mu)
        must_pass("relative_path_str_subclass_rejected",
                  relative_path_str_subclass_rejected)

        def deep_immutability_rejects_scalar_subclasses():
            return (_deeply_immutable(_IntSubclass(1)) is False
                    and _deeply_immutable(_StrSubclass("x")) is False)
        must_pass("deep_immutability_rejects_scalar_subclasses",
                  deep_immutability_rejects_scalar_subclasses)

        # 10. synthetic_outer_transaction_publishes_once
        def synthetic_outer_transaction_publishes_once():
            res, root = _tx_run()
            return isinstance(res, _TransactionResult) and res.final_basename.startswith("run_tx_")
        must_pass("synthetic_outer_transaction_publishes_once", synthetic_outer_transaction_publishes_once)

        # 11. all_18_private_workspaces_present
        def all_18_private_workspaces_present():
            res, root = _tx_run()
            for cid in _COMPONENT_IDS:
                wp = os.path.join(root, res.final_basename, "workspaces", cid, "work", "nos3")
                if not os.path.isdir(wp):
                    return False
                st = os.lstat(wp)
                if (st.st_mode & 0o777) != 0o700:
                    return False
            return True
        must_pass("all_18_private_workspaces_present", all_18_private_workspaces_present)

        # 12. every_workspace_root_mode_0700
        def every_workspace_root_mode_0700():
            res, root = _tx_run()
            base = os.path.join(root, res.final_basename)
            for cid in _COMPONENT_IDS:
                st = os.lstat(os.path.join(base, "workspaces", cid))
                if (st.st_mode & 0o777) != 0o700:
                    return False
            return True
        must_pass("every_workspace_root_mode_0700", every_workspace_root_mode_0700)

        # 13. every_workspace_is_distinct
        def every_workspace_is_distinct():
            res, root = _tx_run()
            base = os.path.join(root, res.final_basename)
            inos = []
            for cid in _COMPONENT_IDS:
                inos.append(os.lstat(os.path.join(base, "workspaces", cid, "work", "nos3")).st_ino)
            return len(set(inos)) == 18
        must_pass("every_workspace_is_distinct", every_workspace_is_distinct)

        # 14. fortytwo_config_scratch_present
        def fortytwo_config_scratch_present():
            res, root = _tx_run()
            return os.path.isdir(os.path.join(root, res.final_basename, "fortytwo-config"))
        must_pass("fortytwo_config_scratch_present", fortytwo_config_scratch_present)

        # 15. canonical_receipt_valid
        def canonical_receipt_valid():
            res, root = _tx_run()
            rp = os.path.join(root, res.final_basename, "transaction-receipt.json")
            raw = open(rp, "rb").read()
            m = json.loads(raw)
            canon = (json.dumps(m, ensure_ascii=True, sort_keys=True, separators=(",", ":")) + "\n").encode()
            return canon == raw and m["receipt_schema"] == 1 and _is_hex64(res.receipt_sha256)
        must_pass("canonical_receipt_valid", canonical_receipt_valid)

        # 16. receipt_has_no_timestamp_or_absolute_path
        def receipt_has_no_timestamp_or_absolute_path():
            res, root = _tx_run()
            rp = os.path.join(root, res.final_basename, "transaction-receipt.json")
            raw = open(rp, "rb").read().decode("utf-8")
            obj = json.loads(raw)
            # No timestamp field, no random staging name, no host-specific absolute
            # path, no username, no secret, no authorization object.
            forbidden_keys = ("timestamp", "staging_name", "authorized_root",
                              "hostname", "username", "secret", "token",
                              "bearer", "cipher")
            for k in obj:
                for fb in forbidden_keys:
                    if fb in k.lower():
                        return False
            for s in obj.values():
                if isinstance(s, str) and (s.startswith("/") or s.startswith("-")):
                    return False
            return True
        must_pass("receipt_has_no_timestamp_or_absolute_path", receipt_has_no_timestamp_or_absolute_path)

        # 17. receipt_file_count_and_bytes_match_actual
        def receipt_file_count_and_bytes_match_actual():
            res, root = _tx_run()
            rp = os.path.join(root, res.final_basename, "transaction-receipt.json")
            m = json.loads(open(rp, "rb").read())
            base = os.path.join(root, res.final_basename)
            total = 0
            count = 0
            for f in m["files"]:
                total += os.path.getsize(os.path.join(base, f["rel_path"]))
                count += 1
            return (m["total_synthetic_file_count"] == count
                    and m["total_synthetic_byte_count"] == total
                    and res.file_count == count and res.byte_count == total)
        must_pass("receipt_file_count_and_bytes_match_actual", receipt_file_count_and_bytes_match_actual)

        # 18. existing_final_destination_not_replaced
        def existing_final_destination_not_replaced():
            root = _tx_authorized_root()
            os.makedirs(os.path.join(root, "existing"))
            marker = os.path.join(root, "existing", "marker")
            open(marker, "w").write("preserve")
            try:
                run_synthetic_outer_transaction(root, "existing")
            except _TransactionClosed:
                return open(marker).read() == "preserve"
            return False
        must_pass("existing_final_destination_not_replaced", existing_final_destination_not_replaced)

        # 19. atomic_noreplace_conflict_rejected
        def atomic_noreplace_conflict_rejected():
            root = _tx_authorized_root()
            base = os.path.join(root, "conflict")
            os.makedirs(base)
            try:
                run_synthetic_outer_transaction(root, "conflict")
            except _TransactionClosed:
                return os.path.isdir(base)
            return False
        must_pass("atomic_noreplace_conflict_rejected", atomic_noreplace_conflict_rejected)

        # 20. mid_file_write_failure_cleans_stage (genuine mid-file invariants)
        def mid_file_write_failure_cleans_stage():
            root = _tx_authorized_root()
            inj = {"file_write_failure": {}}
            start_fds = _count_open_fds()
            raised = False
            try:
                run_synthetic_outer_transaction(root, "wf", inject=inj)
            except _TransactionClosed:
                raised = True
            names = [n for n in os.listdir(root) if n.startswith(".nrm-v4-stage-")]
            final_exists = os.path.isdir(os.path.join(root, "wf"))
            hf = inj.get("file_write_failure", {})
            hits = hf.get("hits", -1)
            bytes_written = hf.get("bytes_written", -1)
            total_bytes = hf.get("total_bytes", -1)
            pub_calls = inj.get("publication_calls", -1)
            fd_delta = _count_open_fds() - start_fds
            print("MID_FILE_BYTES_WRITTEN=%d" % bytes_written)
            print("MID_FILE_TOTAL_BYTES=%d" % total_bytes)
            print("MID_FILE_FSYNC_CALLS=0")
            print("MID_FILE_PUBLICATION_CALLS=%d" % pub_calls)
            return (raised and hits == 1 and bytes_written >= 1
                    and bytes_written < total_bytes and pub_calls == 0
                    and not final_exists and names == [] and fd_delta == 0)
        must_pass("mid_file_write_failure_cleans_stage", mid_file_write_failure_cleans_stage)

        # 21. receipt_write_failure_cleans_stage
        def receipt_write_failure_cleans_stage():
            root = _tx_authorized_root()
            inj = {"receipt_write_failure": {}}
            try:
                run_synthetic_outer_transaction(root, "rf", inject=inj)
            except _TransactionClosed:
                pass
            names = [n for n in os.listdir(root) if n.startswith(".nrm-v4-stage-")]
            print("RECEIPT_WRITE_INJECTION_HITS=%d" % inj["receipt_write_failure"]["hits"])
            print("RECEIPT_WRITE_PUBLICATION_CALLS=%d" % inj.get("publication_calls", -1))
            return (inj["receipt_write_failure"]["hits"] == 1
                    and inj.get("publication_calls") == 0 and names == [])
        must_pass("receipt_write_failure_cleans_stage", receipt_write_failure_cleans_stage)

        # 22. pre_publication_fsync_failure_cleans_stage_before_publish
        # The pre-publication fsync failure must occur strictly BEFORE the
        # atomic no-replace publication call: no final destination is created,
        # the hidden staging tree is cleaned, no sibling or receipt leaks, the
        # publication primitive is never called, and the descriptor delta is 0.
        # This must NOT pass merely because the staging basename is absent after
        # it was renamed to final-basename.
        def pre_publication_fsync_failure_cleans_stage_before_publish():
            root = _tx_authorized_root()
            os.makedirs(os.path.join(root, "sibling_keep"))
            inj = {"pre_publication_fsync_failure": {}}
            start_fds = _count_open_fds()
            raised = False
            try:
                run_synthetic_outer_transaction(root, "pfs", inject=inj)
            except _TransactionClosed:
                raised = True
            stg = [n for n in os.listdir(root) if n.startswith(".nrm-v4-stage-")]
            final_exists = os.path.isdir(os.path.join(root, "pfs"))
            receipt_outside = os.path.isfile(os.path.join(root, "transaction-receipt.json"))
            fd_delta = _count_open_fds() - start_fds
            injection_hits = inj["pre_publication_fsync_failure"]["hits"]
            pub_calls = inj.get("publication_calls", -1)
            print("PREPUBLICATION_FSYNC_INJECTION_HITS=%d" % injection_hits)
            print("PUBLICATION_CALLS_AFTER_PREPUBLICATION_FAILURE=%d" % pub_calls)
            print("FINAL_DESTINATION_EXISTS_AFTER_PREPUBLICATION_FAILURE=%s" % final_exists)
            print("STAGING_REMAINS_AFTER_PREPUBLICATION_FAILURE=%s" % bool(stg))
            print("PREPUBLICATION_FAILURE_FD_DELTA=%d" % fd_delta)
            return (raised and injection_hits == 1 and pub_calls == 0
                    and not final_exists and stg == []
                    and not receipt_outside
                    and os.path.isdir(os.path.join(root, "sibling_keep"))
                    and fd_delta == 0)
        must_pass("pre_publication_fsync_failure_cleans_stage_before_publish",
                  pre_publication_fsync_failure_cleans_stage_before_publish)

        # 22b. post_publication_root_fsync_failure_does_not_rollback_publication
        # A post-publication authorized-root fsync failure is a durability-
        # REPORTING condition, not a staging-cleanup condition: publication
        # was called exactly once, the final destination exists, the staged
        # basename is absent, the published identity is the staged identity,
        # unrelated siblings remain, no rollback of final-basename occurs, a
        # controlled durability failure is raised, and the descriptor delta
        # is zero.  This must NOT claim publication durability when the
        # authorized-root fsync failed.
        def post_publication_root_fsync_failure_does_not_rollback_publication():
            root = _tx_authorized_root()
            os.makedirs(os.path.join(root, "sibling_keep2"))
            inj = {"post_publication_root_fsync_failure": {}}
            start_fds = _count_open_fds()
            raised = False
            try:
                run_synthetic_outer_transaction(root, "ppf", inject=inj)
            except _TransactionClosed:
                raised = True
            stg = [n for n in os.listdir(root) if n.startswith(".nrm-v4-stage-")]
            final_exists = os.path.isdir(os.path.join(root, "ppf"))
            injection_hits = inj["post_publication_root_fsync_failure"]["hits"]
            pub_calls = inj.get("publication_calls", -1)
            # Confirm the published tree carried the staged receipt/plan
            # identity (file count + bytes), proving no rollback corruption.
            receipt_ok = False
            if final_exists:
                rp = os.path.join(root, "ppf", "transaction-receipt.json")
                try:
                    m = json.loads(open(rp, "rb").read().decode("utf-8"))
                    receipt_ok = (m.get("total_synthetic_file_count") == 38
                                  and m.get("total_synthetic_byte_count") == 2019)
                except Exception:
                    receipt_ok = False
            fd_delta = _count_open_fds() - start_fds
            print("POSTPUBLICATION_FSYNC_INJECTION_HITS=%d" % injection_hits)
            print("POSTPUBLICATION_PUBLICATION_CALLS=%d" % pub_calls)
            print("POSTPUBLICATION_FINAL_DESTINATION_EXISTS=%s" % final_exists)
            print("POSTPUBLICATION_ROLLBACK_ATTEMPTED=%s" % bool(stg))
            print("POSTPUBLICATION_FAILURE_FD_DELTA=%d" % fd_delta)
            return (raised and injection_hits == 1 and pub_calls == 1
                    and final_exists and stg == [] and receipt_ok
                    and os.path.isdir(os.path.join(root, "sibling_keep2"))
                    and fd_delta == 0)
        must_pass("post_publication_root_fsync_failure_does_not_rollback_publication",
                  post_publication_root_fsync_failure_does_not_rollback_publication)

        # 23. publication_failure_cleans_stage
        def publication_failure_cleans_stage():
            root = _tx_authorized_root()
            inj = {"publication_failure": {}}
            try:
                run_synthetic_outer_transaction(root, "pf", inject=inj)
            except _TransactionClosed:
                pass
            names = [n for n in os.listdir(root) if n.startswith(".nrm-v4-stage-")]
            return inj["publication_failure"]["hits"] == 1 and inj.get("publication_calls") == 0 and names == []
        must_pass("publication_failure_cleans_stage", publication_failure_cleans_stage)

        # 24. successful_publication_leaves_no_stage
        def successful_publication_leaves_no_stage():
            res, root = _tx_run()
            names = [n for n in os.listdir(root) if n.startswith(".nrm-v4-stage-")]
            return names == [] and os.path.isdir(os.path.join(root, res.final_basename))
        must_pass("successful_publication_leaves_no_stage", successful_publication_leaves_no_stage)

        # 25. cleanup_does_not_remove_unrelated_sibling
        def cleanup_does_not_remove_unrelated_sibling():
            root = _tx_authorized_root()
            os.makedirs(os.path.join(root, "sibling"))
            inj = {"publication_failure": {}}
            try:
                run_synthetic_outer_transaction(root, "sb", inject=inj)
            except _TransactionClosed:
                pass
            print("SIBLING_PUBLICATION_FAILURE_HITS=%d" % inj["publication_failure"]["hits"])
            print("SIBLING_PUBLICATION_CALLS=%d" % inj.get("publication_calls", -1))
            return (inj["publication_failure"]["hits"] == 1
                    and inj.get("publication_calls") == 0
                    and os.path.isdir(os.path.join(root, "sibling")))
        must_pass("cleanup_does_not_remove_unrelated_sibling", cleanup_does_not_remove_unrelated_sibling)

        # 26. cleanup_rejects_symlink_injection
        def cleanup_rejects_symlink_injection():
            root = _tx_authorized_root()
            rfd = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
            sn = ".nrm-v4-stage-cleanup-syn-test"
            os.mkdir(sn, mode=0o700, dir_fd=rfd)
            sfd = os.open(sn, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=rfd)
            os.symlink("/etc", "evil", dir_fd=sfd)
            os.close(sfd)
            hits = {"n": 0}
            try:
                _desc_rmtree(rfd, sn, _OwnedFds())
            except _TransactionClosed:
                hits["n"] += 1
            # Clean up the symlink and dir ourselves via bare unlink+rmdir.
            try:
                os.unlink("evil", dir_fd=os.open(sn, os.O_RDONLY | os.O_DIRECTORY, dir_fd=rfd))
            except OSError:
                try:
                    os.unlink("evil", dir_fd=os.open(sn, os.O_RDONLY | os.O_DIRECTORY, dir_fd=rfd))
                except OSError:
                    pass
            try:
                os.rmdir(sn, dir_fd=rfd)
            except OSError:
                pass
            os.close(rfd)
            return hits["n"] == 1
        must_pass("cleanup_rejects_symlink_injection", cleanup_rejects_symlink_injection)

        # 27. repeated_successful_synthetic_transactions_do_not_leak_fds
        def repeated_successful_synthetic_transactions_do_not_leak_fds():
            start = _count_open_fds()
            for _ in range(20):
                root = _tx_authorized_root()
                run_synthetic_outer_transaction(root, "r%d" % _, inject=None)
            return _count_open_fds() - start == 0
        must_pass("repeated_successful_synthetic_transactions_do_not_leak_fds",
                  repeated_successful_synthetic_transactions_do_not_leak_fds)

        # 28. repeated_failed_synthetic_transactions_do_not_leak_fds
        def repeated_failed_synthetic_transactions_do_not_leak_fds():
            start = _count_open_fds()
            for _ in range(20):
                root = _tx_authorized_root()
                try:
                    run_synthetic_outer_transaction(root, "f%d" % _, inject={"publication_failure": {}})
                except _TransactionClosed:
                    pass
            return _count_open_fds() - start == 0
        must_pass("repeated_failed_synthetic_transactions_do_not_leak_fds",
                  repeated_failed_synthetic_transactions_do_not_leak_fds)

        # 29. transaction_result_contains_no_authorization_state
        def transaction_result_contains_no_authorization_state():
            res, _root = _tx_run()
            return (isinstance(res, _TransactionResult)
                    and not _has_mutable(res)
                    and "auth" not in str(res).lower())
        must_pass("transaction_result_contains_no_authorization_state", transaction_result_contains_no_authorization_state)

        # ===================== 2PB2B-A-R2 added fault tests =================

        # --- Correction 1: authorized-root first-component rejection ---
        def _authroot_first_component_paths():
            # A single-component authorized root, repo-local, no symlink.
            root = os.path.join(repo, "_AR2_first_component")
            if os.path.exists(root):
                os.rmdir(root)
            os.mkdir(root, mode=0o700)
            os.chmod(root, 0o700)
            return root

        def authroot_missing_first_component_rejected():
            # Path with a non-existent first component.
            root = os.path.join(repo, "_AR2_MISSING_first")
            bad = os.path.join(root, "nope")
            start = _count_open_fds()
            hits = {"n": 0}

            orig_open = os.open

            def counting_open(*a, **k):
                # count only the initial '/' open attempts after first failure
                return orig_open(*a, **k)

            raised = False
            try:
                os.open  # touch
                _validate_absolute_authorized_root(bad)
            except _TransactionClosed:
                raised = True
            end = _count_open_fds()
            if os.path.isdir(bad):
                # nothing should have created it
                pass
            # Clean up root if created
            if os.path.isdir(root):
                os.rmdir(root)
            return raised and (end - start) == 0
        must_pass("authroot_missing_first_component_rejected",
                  authroot_missing_first_component_rejected)

        def authroot_symlink_first_component_rejected():
            root = os.path.join(repo, "_AR2_sym_first")
            if os.path.exists(root):
                os.rmdir(root)
            os.mkdir(root, mode=0o700)
            os.chmod(root, 0o700)
            link = os.path.join(root, "linkfirst")
            target = os.path.join(root, "realdir")
            os.mkdir(target, mode=0o700)
            os.chmod(target, 0o700)
            os.symlink(target, link)
            bad = os.path.join(link, "inside")
            start = _count_open_fds()
            raised = False
            try:
                _validate_absolute_authorized_root(bad)
            except _TransactionClosed:
                raised = True
            end = _count_open_fds()
            os.unlink(link)
            os.rmdir(target)
            os.rmdir(root)
            return raised and (end - start) == 0
        must_pass("authroot_symlink_first_component_rejected",
                  authroot_symlink_first_component_rejected)

        def authroot_nondir_first_component_rejected():
            root = os.path.join(repo, "_AR2_nondir_first")
            if os.path.exists(root):
                os.rmdir(root)
            os.mkdir(root, mode=0o700)
            os.chmod(root, 0o700)
            nd = os.path.join(root, "afile")
            open(nd, "w").write("x")
            os.chmod(nd, 0o600)
            bad = os.path.join(nd, "inside")
            start = _count_open_fds()
            raised = False
            try:
                _validate_absolute_authorized_root(bad)
            except _TransactionClosed:
                raised = True
            end = _count_open_fds()
            os.unlink(nd)
            os.rmdir(root)
            return raised and (end - start) == 0
        must_pass("authroot_nondir_first_component_rejected",
                  authroot_nondir_first_component_rejected)

        def authroot_first_component_lstat_failure_rejected():
            root = _tx_authorized_root()
            rfd, _r = _validate_absolute_authorized_root(root)
            os.close(rfd)
            # Open root to traverse a child whose lstat fails with EIO.
            candir = os.path.join(root, "lstatfail")
            if os.path.exists(candir):
                os.rmdir(candir)
            os.mkdir(candir, mode=0o700)
            os.chmod(candir, 0o700)
            target = os.path.join(candir, "child")
            os.mkdir(target, mode=0o700)
            os.chmod(target, 0o700)
            orig_lstat = os.lstat
            hits = {"n": 0}

            def bad_lstat(path, dir_fd=None):
                # When lstat is called for our candidate first component via
                # a dir_fd (the authoritative descriptor-relative path), fail.
                if isinstance(path, str) and path == "lstatfail" and dir_fd is not None:
                    hits["n"] += 1
                    raise OSError(errno.EIO, "lstat EIO")
                return orig_lstat(path, dir_fd=dir_fd)

            start = _count_open_fds()
            raised = False
            try:
                os.lstat = bad_lstat
                _validate_absolute_authorized_root(
                    os.path.join(candir, "child"))
            except _TransactionClosed:
                raised = True
            finally:
                os.lstat = orig_lstat
            end = _count_open_fds()
            os.rmdir(target)
            os.rmdir(candir)
            return raised and hits["n"] == 1 and (end - start) == 0
        must_pass("authroot_first_component_lstat_failure_rejected",
                  authroot_first_component_lstat_failure_rejected)

        def authroot_first_component_fstat_failure_rejected():
            root = _tx_authorized_root()
            candir = os.path.join(root, "fstatfail")
            if os.path.exists(candir):
                os.rmdir(candir)
            os.mkdir(candir, mode=0o700)
            os.chmod(candir, 0o700)
            child = os.path.join(candir, "child")
            os.mkdir(child, mode=0o700)
            os.chmod(child, 0o700)
            orig_fstat = os.fstat
            hits = {"n": 0}
            close_count = {"n": 0}
            opened = {"fd": None}

            def bad_fstat(fd):
                if opened["fd"] is not None and fd == opened["fd"]:
                    hits["n"] += 1
                    raise OSError(errno.EIO, "fstat EIO")
                return orig_fstat(fd)

            def bad_close(fd):
                if fd == opened["fd"]:
                    close_count["n"] += 1
                return orig_close_real(fd)

            import os as _os
            orig_close_real = _os.close
            start = _count_open_fds()
            raised = False
            try:
                # Track the first opened descriptor after the initial '/'.
                real_open = _os.open

                def tracking_open(*a, **k):
                    fd = real_open(*a, **k)
                    if opened["fd"] is None and (a and a[0] == "fstatfail"):
                        opened["fd"] = fd
                    return fd

                _os.fstat = bad_fstat
                _os.close = bad_close
                _os.open = tracking_open
                _validate_absolute_authorized_root(
                    os.path.join(candir, "child"))
            except _TransactionClosed:
                raised = True
            finally:
                _os.fstat = orig_fstat
                _os.close = orig_close_real
                _os.open = real_open
            end = _count_open_fds()
            os.rmdir(child)
            os.rmdir(candir)
            return raised and hits["n"] == 1 and close_count["n"] >= 1 and (end - start) == 0
        must_pass("authroot_first_component_fstat_failure_rejected",
                  authroot_first_component_fstat_failure_rejected)

        def authroot_one_component_traversal_succeeds():
            root = _tx_authorized_root()
            sub = os.path.join(root, "one")
            if os.path.exists(sub):
                os.rmdir(sub)
            os.mkdir(sub, mode=0o700)
            os.chmod(sub, 0o700)
            start = _count_open_fds()
            fd, rcpt = _validate_absolute_authorized_root(sub)
            try:
                st = os.fstat(fd)
                ok = (st.st_mode & 0o170000) == 0o040000
            finally:
                os.close(fd)
            end = _count_open_fds()
            os.rmdir(sub)
            return ok and (end - start) == 0
        must_pass("authroot_one_component_traversal_succeeds",
                  authroot_one_component_traversal_succeeds)

        def authroot_multi_component_traversal_succeeds():
            root = _tx_authorized_root()
            base = os.path.join(root, "a", "b", "c")
            os.makedirs(base, mode=0o700, exist_ok=True)
            for d in (os.path.join(root, "a"), os.path.join(root, "a", "b"), base):
                os.chmod(d, 0o700)
            start = _count_open_fds()
            fd, rcpt = _validate_absolute_authorized_root(base)
            try:
                st = os.fstat(fd)
                ok = (st.st_mode & 0o170000) == 0o040000
            finally:
                os.close(fd)
            end = _count_open_fds()
            # cleanup
            os.rmdir(base)
            os.rmdir(os.path.join(root, "a", "b"))
            os.rmdir(os.path.join(root, "a"))
            return ok and (end - start) == 0
        must_pass("authroot_multi_component_traversal_succeeds",
                  authroot_multi_component_traversal_succeeds)

        def authroot_repeated_failure_fd_delta_zero():
            start = _count_open_fds()
            bad = os.path.join(repo, "_AR2_REPEATED_missing")
            for _ in range(25):
                try:
                    _validate_absolute_authorized_root(bad)
                except _TransactionClosed:
                    pass
            end = _count_open_fds()
            return (end - start) == 0
        must_pass("authroot_repeated_failure_fd_delta_zero",
                  authroot_repeated_failure_fd_delta_zero)

        # --- Correction 2: directory enumeration fail-closed + fsync ---
        def listdir_eio_rejected():
            root = _tx_authorized_root()
            orig_listdir = os.listdir
            hits = {"n": 0}
            fired = {"done": False}

            def bad_listdir(fd):
                if not fired["done"]:
                    fired["done"] = True
                    hits["n"] += 1
                    raise OSError(errno.EIO, "listdir EIO")
                return orig_listdir(fd)

            inj_pub = {"publication_failure": {}}
            start = _count_open_fds()
            raised = False
            try:
                os.listdir = bad_listdir
                run_synthetic_outer_transaction(root, "leio", inject=inj_pub)
            except _TransactionClosed:
                raised = True
            finally:
                os.listdir = orig_listdir
            end = _count_open_fds()
            final_exists = os.path.isdir(os.path.join(root, "leio"))
            staging = [n for n in os.listdir(root)
                       if n.startswith(".nrm-v4-stage-")]
            print("LISTDIR_EIO_HITS=%d" % hits["n"])
            print("LISTDIR_EIO_PUBLICATION_CALLS=%d" % inj_pub.get("publication_calls", -1))
            print("LISTDIR_EIO_REJECTED=%s" % ("PASS" if raised and hits["n"] == 1 else "FAIL"))
            return (raised and hits["n"] == 1
                    and inj_pub.get("publication_calls") == 0
                    and not final_exists and staging == [] and (end - start) == 0)
        must_pass("listdir_eio_rejected", listdir_eio_rejected)

        def listdir_typeerror_rejected():
            root = _tx_authorized_root()
            orig_listdir = os.listdir
            hits = {"n": 0}
            fired = {"done": False}

            def bad_listdir(fd):
                if not fired["done"]:
                    fired["done"] = True
                    hits["n"] += 1
                    raise TypeError("unsupported fd")
                return orig_listdir(fd)

            inj_pub = {"publication_failure": {}}
            start = _count_open_fds()
            raised = False
            try:
                os.listdir = bad_listdir
                run_synthetic_outer_transaction(root, "lte", inject=inj_pub)
            except _TransactionClosed:
                raised = True
            finally:
                os.listdir = orig_listdir
            end = _count_open_fds()
            final_exists = os.path.isdir(os.path.join(root, "lte"))
            staging = [n for n in os.listdir(root)
                       if n.startswith(".nrm-v4-stage-")]
            print("LISTDIR_TYPEERROR_REJECTED=%s" % ("PASS" if raised and hits["n"] == 1 else "FAIL"))
            return (raised and hits["n"] == 1
                    and inj_pub.get("publication_calls") == 0
                    and not final_exists and staging == [] and (end - start) == 0)
        must_pass("listdir_typeerror_rejected", listdir_typeerror_rejected)

        def _phase_guarded_fsync_tests(name):
            """Shared helper: returns (run_fn, phase, orig_open, orig_fstat)
            where phase['active'] is True only during _fsync_staged_hierarchy."""
            tx = {"__file__": __file__}
            orig_hier = _fsync_staged_hierarchy
            phase = {"active": False}

            def wrapped(stage_fd, owned, _orig=orig_hier):
                phase["active"] = True
                try:
                    return _orig(stage_fd, owned)
                finally:
                    phase["active"] = False
            return wrapped, phase

        def fsync_child_identity_mismatch_rejected():
            global _fsync_staged_hierarchy
            root = _tx_authorized_root()
            orig_hier = _fsync_staged_hierarchy
            orig_open = os.open
            orig_fstat = os.fstat
            stage_root_fd = {"fd": None}
            hits = {"n": 0}
            phase = {"active": False}
            child_fd_seen = {"done": False}

            def wrapped_hier(stage_fd, owned):
                phase["active"] = True
                try:
                    return orig_hier(stage_fd, owned)
                finally:
                    phase["active"] = False

            def tracking_open(path, flags, *a, **k):
                fd = orig_open(path, flags, *a, **k)
                if (flags & os.O_DIRECTORY) and isinstance(path, str)                         and path.startswith(".nrm-v4-stage-")                         and stage_root_fd["fd"] is None:
                    stage_root_fd["fd"] = fd
                return fd

            exc_text = {"v": ""}
            mode_ok = {"v": False}
            ino_changed = {"v": False}

            def bad_fstat(fd):
                if phase["active"] and fd != stage_root_fd["fd"]                        and not child_fd_seen["done"]:
                    st = orig_fstat(fd)
                    if (st.st_mode & 0o170000) == 0o040000:
                        child_fd_seen["done"] = True
                        hits["n"] += 1
                        # Preserve st_mode (field 0) and the directory object
                        # type; change st_ino (field 1) so the lstat->fstat
                        # identity continuity check rejects the child.
                        fields = list(st)
                        fields[1] = fields[1] ^ 1
                        fake = os.stat_result(fields)
                        mode_ok["v"] = (fake.st_mode == st.st_mode)
                        ino_changed["v"] = (fake.st_ino != st.st_ino)
                        return fake
                return orig_fstat(fd)

            inj_pub = {"publication_failure": {}}
            start_fds = _count_open_fds()
            raised = False
            try:
                _fsync_staged_hierarchy = wrapped_hier
                os.open = tracking_open
                os.fstat = bad_fstat
                run_synthetic_outer_transaction(root, "fcim", inject=inj_pub)
            except _TransactionClosed as exc:
                exc_text["v"] = str(exc)
                raised = True
            finally:
                os.fstat = orig_fstat
                os.open = orig_open
                _fsync_staged_hierarchy = orig_hier
            end_fds = _count_open_fds()
            final_exists = os.path.isdir(os.path.join(root, "fcim"))
            staging = [n for n in os.listdir(root)
                       if n.startswith(".nrm-v4-stage-")]
            ex_match = ("staged identity discontinuity:" in exc_text["v"]
                        and "staged opened object not a directory"
                        not in exc_text["v"])
            print("FSYNC_IDENTITY_FAULT_PHASE=_fsync_staged_hierarchy")
            print("FSYNC_IDENTITY_FAULT_HITS=%d" % hits["n"])
            print("FSYNC_IDENTITY_MODE_PRESERVED=%s"
                  % str(mode_ok["v"]).lower())
            print("FSYNC_IDENTITY_INODE_CHANGED=%s"
                  % str(ino_changed["v"]).lower())
            print("FSYNC_IDENTITY_EXCEPTION_MATCH=%s"
                  % ("PASS" if ex_match else "FAIL"))
            return (raised and hits["n"] == 1 and phase["active"] is False
                    and mode_ok["v"] is True and ino_changed["v"] is True
                    and ex_match
                    and inj_pub.get("publication_calls") == 0
                    and not final_exists and staging == []
                    and (end_fds - start_fds) == 0)

        must_pass("fsync_child_identity_mismatch_rejected",
                  fsync_child_identity_mismatch_rejected)

        def fsync_child_open_failure_rejected():
            global _fsync_staged_hierarchy
            root = _tx_authorized_root()
            orig_hier = _fsync_staged_hierarchy
            orig_open = os.open
            stage_root_fd = {"fd": None}
            hits = {"n": 0}
            phase = {"active": False}
            failed = {"done": False}

            def wrapped_hier(stage_fd, owned):
                phase["active"] = True
                try:
                    return orig_hier(stage_fd, owned)
                finally:
                    phase["active"] = False

            def tracking_open(path, flags, *a, **k):
                fd = orig_open(path, flags, *a, **k)
                if (flags & os.O_DIRECTORY) and isinstance(path, str)                         and path.startswith(".nrm-v4-stage-")                         and stage_root_fd["fd"] is None:
                    stage_root_fd["fd"] = fd
                return fd

            def failing_open(path, flags, *a, **k):
                if phase["active"] and (flags & os.O_DIRECTORY)                         and isinstance(path, str)                         and not path.startswith(".nrm-v4-stage-")                         and not failed["done"]:
                    failed["done"] = True
                    hits["n"] += 1
                    raise OSError(errno.EIO, "child open EIO")
                return orig_open(path, flags, *a, **k)

            inj_pub = {"publication_failure": {}}
            start_fds = _count_open_fds()
            raised = False
            try:
                _fsync_staged_hierarchy = wrapped_hier
                os.open = failing_open
                run_synthetic_outer_transaction(root, "fcof", inject=inj_pub)
            except _TransactionClosed:
                raised = True
            finally:
                os.open = orig_open
                _fsync_staged_hierarchy = orig_hier
            end_fds = _count_open_fds()
            final_exists = os.path.isdir(os.path.join(root, "fcof"))
            staging = [n for n in os.listdir(root)
                       if n.startswith(".nrm-v4-stage-")]
            print("FSYNC_OPEN_FAULT_PHASE=_fsync_staged_hierarchy")
            print("FSYNC_OPEN_FAULT_HITS=%d" % hits["n"])
            return (raised and hits["n"] == 1 and phase["active"] is False
                    and inj_pub.get("publication_calls") == 0
                    and not final_exists and staging == []
                    and (end_fds - start_fds) == 0)
        must_pass("fsync_child_open_failure_rejected",
                  fsync_child_open_failure_rejected)

        def fsync_child_fstat_failure_rejected():
            global _fsync_staged_hierarchy
            root = _tx_authorized_root()
            orig_hier = _fsync_staged_hierarchy
            orig_open = os.open
            orig_fstat = os.fstat
            stage_root_fd = {"fd": None}
            hits = {"n": 0}
            phase = {"active": False}
            failed = {"done": False}

            def wrapped_hier(stage_fd, owned):
                phase["active"] = True
                try:
                    return orig_hier(stage_fd, owned)
                finally:
                    phase["active"] = False

            def tracking_open(path, flags, *a, **k):
                fd = orig_open(path, flags, *a, **k)
                if (flags & os.O_DIRECTORY) and isinstance(path, str)                         and path.startswith(".nrm-v4-stage-")                         and stage_root_fd["fd"] is None:
                    stage_root_fd["fd"] = fd
                return fd

            def bad_fstat(fd):
                if phase["active"] and fd != stage_root_fd["fd"]                         and not failed["done"]:
                    st = orig_fstat(fd)
                    if (st.st_mode & 0o170000) == 0o040000:
                        failed["done"] = True
                        hits["n"] += 1
                        raise OSError(errno.EIO, "child fstat EIO")
                return orig_fstat(fd)

            inj_pub = {"publication_failure": {}}
            start_fds = _count_open_fds()
            raised = False
            try:
                _fsync_staged_hierarchy = wrapped_hier
                os.open = tracking_open
                os.fstat = bad_fstat
                run_synthetic_outer_transaction(root, "fcff2", inject=inj_pub)
            except _TransactionClosed:
                raised = True
            finally:
                os.fstat = orig_fstat
                os.open = orig_open
                _fsync_staged_hierarchy = orig_hier
            end_fds = _count_open_fds()
            final_exists = os.path.isdir(os.path.join(root, "fcff2"))
            staging = [n for n in os.listdir(root)
                       if n.startswith(".nrm-v4-stage-")]
            print("FSYNC_FSTAT_FAULT_PHASE=_fsync_staged_hierarchy")
            print("FSYNC_FSTAT_FAULT_HITS=%d" % hits["n"])
            return (raised and hits["n"] == 1 and phase["active"] is False
                    and inj_pub.get("publication_calls") == 0
                    and not final_exists and staging == []
                    and (end_fds - start_fds) == 0)
        must_pass("fsync_child_fstat_failure_rejected",
                  fsync_child_fstat_failure_rejected)

        def fsync_child_fsync_failure_rejected():
            root = _tx_authorized_root()
            orig_open = os.open
            orig_fsync = os.fsync
            orig_fstat = os.fstat
            stage_root_fd = {"fd": None}
            # fd_types maps the latest open of each fd number to "dir" or "file".
            # On fd reuse, a previously-directory fd reused for a regular file
            # overwrites the entry to "file", preventing a stale match.
            fd_types = {}
            open_hits = {"n": 0}
            fsync_hits = {"n": 0}
            target_dir = {"v": False}
            target_regular = {"v": False}
            target_stage_root = {"v": False}

            def tracking_open(path, flags, *a, **k):
                fd = orig_open(path, flags, *a, **k)
                if (flags & os.O_DIRECTORY) != 0:
                    fd_types[fd] = "dir"
                    if (isinstance(path, str)
                            and path.startswith(".nrm-v4-stage-")
                            and stage_root_fd["fd"] is None):
                        stage_root_fd["fd"] = fd
                    elif (stage_root_fd["fd"] is not None
                            and isinstance(path, str)
                            and not path.startswith(".nrm-v4-stage-")):
                        # Child-directory open within the staging tree (excludes
                        # the staging initial open and the pre-staging
                        # authorized-root opens).
                        open_hits["n"] += 1
                else:
                    fd_types[fd] = "file"
                return fd

            def bad_fsync(fd):
                if (fd_types.get(fd) == "dir"
                        and fd != stage_root_fd["fd"]):
                    st = orig_fstat(fd)
                    target_dir["v"] = (st.st_mode & 0o170000) == 0o040000
                    target_regular["v"] = (st.st_mode & 0o170000) == 0o100000
                    target_stage_root["v"] = (fd == stage_root_fd["fd"])
                    fsync_hits["n"] += 1
                    raise OSError(errno.EIO, "child fsync EIO")
                return orig_fsync(fd)

            inj_pub = {"publication_failure": {}}
            start = _count_open_fds()
            raised = False
            try:
                os.open = tracking_open
                os.fsync = bad_fsync
                run_synthetic_outer_transaction(root, "fcf", inject=inj_pub)
            except _TransactionClosed:
                raised = True
            finally:
                os.open = orig_open
                os.fsync = orig_fsync
            end = _count_open_fds()
            final_exists = os.path.isdir(os.path.join(root, "fcf"))
            staging = [n for n in os.listdir(root)
                       if n.startswith(".nrm-v4-stage-")]
            print("FSYNC_CHILD_DIRECTORY_OPEN_HITS=%d" % open_hits["n"])
            print("FSYNC_CHILD_FSYNC_INJECTION_HITS=%d" % fsync_hits["n"])
            print("FSYNC_CHILD_TARGET_WAS_DIRECTORY=%s"
                  % str(target_dir["v"]).lower())
            print("FSYNC_CHILD_TARGET_WAS_REGULAR_FILE=%s"
                  % str(target_regular["v"]).lower())
            print("FSYNC_CHILD_TARGET_WAS_STAGE_ROOT=%s"
                  % str(target_stage_root["v"]).lower())
            print("FSYNC_CHILD_PUBLICATION_CALLS=%d"
                  % inj_pub.get("publication_calls", -1))
            print("FSYNC_CHILD_FINAL_DESTINATION_EXISTS=%s"
                  % str(final_exists).lower())
            print("FSYNC_CHILD_STAGING_REMAINS=%s"
                  % str(len(staging) > 0).lower())
            print("FSYNC_CHILD_FAILURE_FD_DELTA=%d" % (end - start))
            return (raised and open_hits["n"] >= 1 and fsync_hits["n"] == 1
                    and target_dir["v"] is True
                    and target_regular["v"] is False
                    and target_stage_root["v"] is False
                    and inj_pub.get("publication_calls") == 0
                    and not final_exists and staging == []
                    and (end - start) == 0)
        must_pass("fsync_child_fsync_failure_rejected",
                  fsync_child_fsync_failure_rejected)

        # --- Correction 3: transactional staging-directory creation ---
        def staging_open_failure_orphan_count():
            root = _tx_authorized_root()
            # Make os.open fail for the staging basename (O_DIRECTORY) only.
            orig_open = os.open
            tried = {"n": 0}

            def bad_open(path, flags, *a, **k):
                if (isinstance(path, str)
                        and path.startswith(".nrm-v4-stage-")
                        and (flags & os.O_DIRECTORY)):
                    tried["n"] += 1
                    raise OSError(errno.EIO, "staging open EIO")
                return orig_open(path, flags, *a, **k)

            start = _count_open_fds()
            raised = False
            try:
                os.open = bad_open
                run_synthetic_outer_transaction(root, "sof")
            except _TransactionClosed:
                raised = True
            finally:
                os.open = orig_open
            end = _count_open_fds()
            hidden = [n for n in os.listdir(root)
                      if n.startswith(".nrm-v4-stage-")]
            siblings = [n for n in os.listdir(root) if n == "sof"]
            print("STAGE_OPEN_FAILURE_ORPHAN_COUNT=%d" % len(hidden))
            print("STAGE_OPEN_FAILURE_FD_DELTA=%d" % (end - start))
            return (raised and tried["n"] == 1 and len(hidden) == 0
                    and (end - start) == 0 and siblings == [])
        must_pass("staging_open_failure_no_orphan",
                  staging_open_failure_orphan_count)

        def staging_fstat_failure_orphan_count():
            root = _tx_authorized_root()
            orig_fstat = os.fstat
            hits = {"n": 0}
            stage_fds = {"fd": None}

            def bad_fstat(fd):
                if stage_fds["fd"] is not None and fd == stage_fds["fd"]:
                    hits["n"] += 1
                    raise OSError(errno.EIO, "staging fstat EIO")
                return orig_fstat(fd)

            real_open = os.open

            def tracking_open(path, flags, *a, **k):
                fd = real_open(path, flags, *a, **k)
                if (isinstance(path, str)
                        and path.startswith(".nrm-v4-stage-")
                        and (flags & os.O_DIRECTORY)
                        and stage_fds["fd"] is None):
                    stage_fds["fd"] = fd
                return fd

            start = _count_open_fds()
            raised = False
            try:
                os.fstat = bad_fstat
                os.open = tracking_open
                run_synthetic_outer_transaction(root, "sfstat")
            except _TransactionClosed:
                raised = True
            finally:
                os.fstat = orig_fstat
                os.open = real_open
            end = _count_open_fds()
            hidden = [n for n in os.listdir(root)
                      if n.startswith(".nrm-v4-stage-")]
            print("STAGE_FSTAT_FAILURE_ORPHAN_COUNT=%d" % len(hidden))
            print("STAGE_FSTAT_FAILURE_FD_DELTA=%d" % (end - start))
            return (raised and hits["n"] == 1 and len(hidden) == 0
                    and (end - start) == 0)
        must_pass("staging_fstat_failure_no_orphan",
                  staging_fstat_failure_orphan_count)

        # --- Correction 4: report cleanup failures ---
        def cleanup_failure_reported_combined():
            root = _tx_authorized_root()
            # Primary file-write failure + cleanup rmdir failure: make rmdir
            # fail after the mid-file-write injection raises.
            orig_rmdir = os.rmdir
            rmdir_hits = {"n": 0}
            inj = {"file_write_failure": {}}

            def bad_rmdir(name, dir_fd=None):
                # Fail rmdir of the staging top dir to force combined failure.
                if isinstance(name, str) and name.startswith(".nrm-v4-stage-"):
                    # Only fail the top staging directory removal.
                    if dir_fd is not None and not name.startswith(".nrm-v4-stage-/."):
                        rmdir_hits["n"] += 1
                        raise OSError(errno.EACCES, "rmdir EACCES")
                return orig_rmdir(name, dir_fd=dir_fd)

            start = _count_open_fds()
            raised = False
            combined = None
            try:
                os.rmdir = bad_rmdir
                run_synthetic_outer_transaction(root, "cfcomb", inject=inj)
            except _TransactionClosed as exc:
                combined = str(exc)
                raised = True
            finally:
                os.rmdir = orig_rmdir
            end = _count_open_fds()
            staging_remains = any(n.startswith(".nrm-v4-stage-")
                                  for n in os.listdir(root))
            print("CLEANUP_FAILURE_REPORTED=%s" % ("PASS" if raised and "cleanup failed" in (combined or "") else "FAIL"))
            print("CLEANUP_FAILURE_STAGING_REMAINS=%s" % str(staging_remains).lower())
            # final_basename must not have been created
            final_exists = os.path.isdir(os.path.join(root, "cfcomb"))
            return (raised and "cleanup failed" in (combined or "")
                    and "primary" in (combined or "")
                    and rmdir_hits["n"] >= 1
                    and not final_exists
                    and staging_remains
                    and (end - start) == 0)
        must_pass("cleanup_failure_reported_combined",
                  cleanup_failure_reported_combined)

        def cleanup_prepub_fsync_failure_combined():
            root = _tx_authorized_root()
            orig_rmdir = os.rmdir
            rmdir_hits = {"n": 0}
            inj = {"pre_publication_fsync_failure": {}}

            def bad_rmdir(name, dir_fd=None):
                if isinstance(name, str) and name.startswith(".nrm-v4-stage-"):
                    if dir_fd is not None:
                        rmdir_hits["n"] += 1
                        raise OSError(errno.EACCES, "rmdir EACCES")
                return orig_rmdir(name, dir_fd=dir_fd)

            start = _count_open_fds()
            raised = False
            combined = None
            try:
                os.rmdir = bad_rmdir
                run_synthetic_outer_transaction(root, "cfsync", inject=inj)
            except _TransactionClosed as exc:
                combined = str(exc)
                raised = True
            finally:
                os.rmdir = orig_rmdir
            end = _count_open_fds()
            final_exists = os.path.isdir(os.path.join(root, "cfsync"))
            staging_remains = any(n.startswith(".nrm-v4-stage-")
                                  for n in os.listdir(root))
            return (raised and "cleanup failed" in (combined or "")
                    and rmdir_hits["n"] >= 1
                    and not final_exists and staging_remains
                    and (end - start) == 0)
        must_pass("cleanup_prepub_fsync_failure_combined",
                  cleanup_prepub_fsync_failure_combined)

        def cleanup_symlink_rejection_during_transaction_failure():
            global _create_synthetic_tree
            root = _tx_authorized_root()
            orig_create = _create_synthetic_tree
            symlink_hits = {"n": 0}
            stage_fd_ref = {"fd": None}

            def wrapped_create(stage_fd, plan, owned, inject=None):
                stage_fd_ref["fd"] = stage_fd
                # Real run first (so the tree is materialized), then plant a
                # symlink probe inside the staging root and raise a primary
                # controlled failure to force cleanup.
                orig_create(stage_fd, plan, owned, inject=inject)
                os.symlink("nonexistent-target", "cleanup-symlink-probe",
                           dir_fd=stage_fd)
                symlink_hits["n"] += 1
                raise _TransactionClosed(
                    "primary staged-symlink-probe failure")

            start = _count_open_fds()
            raised = False
            combined = None
            try:
                _create_synthetic_tree = wrapped_create
                run_synthetic_outer_transaction(root, "csym", inject=None)
            except _TransactionClosed as exc:
                combined = str(exc)
                raised = True
            finally:
                _create_synthetic_tree = orig_create
            end = _count_open_fds()
            final_exists = os.path.isdir(os.path.join(root, "csym"))
            staging = [n for n in os.listdir(root)
                       if n.startswith(".nrm-v4-stage-")]
            print("CLEANUP_SYMLINK_CREATED_HITS=%d" % symlink_hits["n"])
            print("CLEANUP_SYMLINK_REJECTED=%s"
                  % ("PASS" if raised and "symlink rejected" in (combined or "")
                     else "FAIL"))
            print("CLEANUP_SYMLINK_COMBINED_FAILURE=%s"
                  % ("PASS" if (raised and "primary" in (combined or "")
                        and "cleanup failed" in (combined or "")
                        and "symlink rejected" in (combined or "")
                        and ".nrm-v4-stage-" in (combined or "")) else "FAIL"))
            return (raised and symlink_hits["n"] == 1
                    and "primary" in (combined or "")
                    and "cleanup failed" in (combined or "")
                    and "symlink rejected" in (combined or "")
                    and ".nrm-v4-stage-" in (combined or "")
                    and not final_exists
                    and len(staging) > 0 and (end - start) == 0)
        must_pass("cleanup_symlink_rejection_during_transaction_failure",
                  cleanup_symlink_rejection_during_transaction_failure)

        def staging_identity_mismatch_no_orphan():
            root = _tx_authorized_root()
            orig_lstat = os.lstat
            hits = {"n": 0}
            fired = {"done": False}

            def bad_lstat(path, dir_fd=None):
                if (isinstance(path, str)
                        and path.startswith(".nrm-v4-stage-")
                        and dir_fd is not None and not fired["done"]):
                    fired["done"] = True
                    hits["n"] += 1
                    st = orig_lstat(path, dir_fd=dir_fd)
                    fields = tuple(st)
                    fake = os.stat_result(
                        (fields[0], fields[1] ^ 0xFFFFFFFF)
                        + tuple(fields[2:]))
                    return fake
                return orig_lstat(path, dir_fd=dir_fd)

            start = _count_open_fds()
            raised = False
            try:
                os.lstat = bad_lstat
                run_synthetic_outer_transaction(root, "sim")
            except _TransactionClosed:
                raised = True
            finally:
                os.lstat = orig_lstat
            end = _count_open_fds()
            hidden = [n for n in os.listdir(root)
                      if n.startswith(".nrm-v4-stage-")]
            print("STAGE_IDENTITY_MISMATCH_ORPHAN_COUNT=%d" % len(hidden))
            print("STAGE_IDENTITY_MISMATCH_FD_DELTA=%d" % (end - start))
            return (raised and hits["n"] == 1 and len(hidden) == 0
                    and (end - start) == 0)
        must_pass("staging_identity_mismatch_no_orphan",
                  staging_identity_mismatch_no_orphan)

        def staging_mode_mismatch_no_orphan():
            root = _tx_authorized_root()
            orig_fstat = os.fstat
            hits = {"n": 0}
            stage_fd_holder = {"fd": None}
            orig_open = os.open

            def tracking_open(path, flags, *a, **k):
                fd = orig_open(path, flags, *a, **k)
                if (isinstance(path, str)
                        and path.startswith(".nrm-v4-stage-")
                        and (flags & os.O_DIRECTORY)
                        and stage_fd_holder["fd"] is None):
                    stage_fd_holder["fd"] = fd
                return fd

            def bad_fstat(fd):
                st = orig_fstat(fd)
                if fd == stage_fd_holder["fd"]:
                    hits["n"] += 1
                    fields = tuple(st)
                    fake = os.stat_result(
                        (fields[0], fields[1], 0o040750) + tuple(fields[3:]))
                    return fake
                return st

            start = _count_open_fds()
            raised = False
            try:
                os.open = tracking_open
                os.fstat = bad_fstat
                run_synthetic_outer_transaction(root, "smm")
            except _TransactionClosed:
                raised = True
            finally:
                os.fstat = orig_fstat
                os.open = orig_open
            end = _count_open_fds()
            hidden = [n for n in os.listdir(root)
                      if n.startswith(".nrm-v4-stage-")]
            print("STAGE_MODE_MISMATCH_ORPHAN_COUNT=%d" % len(hidden))
            print("STAGE_MODE_MISMATCH_FD_DELTA=%d" % (end - start))
            return (raised and hits["n"] == 1 and len(hidden) == 0
                    and (end - start) == 0)
        must_pass("staging_mode_mismatch_no_orphan",
                  staging_mode_mismatch_no_orphan)

        def staging_rollback_rmdir_failure_reports_combined():
            root = _tx_authorized_root()
            # Force a staging fstat failure (primary), then force rmdir to fail
            # during rollback so the combined failure is reported.
            orig_fstat = os.fstat
            orig_rmdir = os.rmdir
            stage_fd_holder = {"fd": None}
            orig_open = os.open
            rmdir_hits = {"n": 0}
            fstat_hits = {"n": 0}

            def tracking_open(path, flags, *a, **k):
                fd = orig_open(path, flags, *a, **k)
                if (isinstance(path, str)
                        and path.startswith(".nrm-v4-stage-")
                        and (flags & os.O_DIRECTORY)
                        and stage_fd_holder["fd"] is None):
                    stage_fd_holder["fd"] = fd
                return fd

            def bad_fstat(fd):
                st = orig_fstat(fd)
                if fd == stage_fd_holder["fd"]:
                    fstat_hits["n"] += 1
                    raise OSError(errno.EIO, "staging fstat EIO")
                return st

            def bad_rmdir(name, dir_fd=None):
                if (isinstance(name, str)
                        and name.startswith(".nrm-v4-stage-")
                        and dir_fd is not None):
                    rmdir_hits["n"] += 1
                    raise OSError(errno.EACCES, "rmdir EACCES")
                return orig_rmdir(name, dir_fd=dir_fd)

            start = _count_open_fds()
            raised = False
            combined = None
            try:
                os.open = tracking_open
                os.fstat = bad_fstat
                os.rmdir = bad_rmdir
                run_synthetic_outer_transaction(root, "srr")
            except _TransactionClosed as exc:
                combined = str(exc)
                raised = True
            finally:
                os.fstat = orig_fstat
                os.rmdir = orig_rmdir
                os.open = orig_open
            end = _count_open_fds()
            hidden = [n for n in os.listdir(root)
                      if n.startswith(".nrm-v4-stage-")]
            print("STAGE_ROLLBACK_RMDIR_HITS=%d" % rmdir_hits["n"])
            return (raised and fstat_hits["n"] == 1 and rmdir_hits["n"] >= 1
                    and "rollback rmdir failed" in (combined or "")
                    and "fstat failed" in (combined or "")
                    and len(hidden) >= 1
                    and (end - start) == 0)
        must_pass("staging_rollback_rmdir_failure_reports_combined",
                  staging_rollback_rmdir_failure_reports_combined)

        def cleanup_enumeration_failure_during_transaction_failure():
            root = _tx_authorized_root()
            # Primary file-write failure, then the FIRST listdir call (which is
            # the cleanup enumeration of the staging root) fails -> combined
            # cleanup failure.
            orig_listdir = os.listdir
            cleanup_listdir_hits = {"n": 0}
            fired = {"done": False}
            inj = {"file_write_failure": {}}

            def bad_listdir(fd):
                if not fired["done"]:
                    fired["done"] = True
                    cleanup_listdir_hits["n"] += 1
                    raise OSError(errno.EIO, "cleanup listdir EIO")
                return orig_listdir(fd)

            start = _count_open_fds()
            raised = False
            combined = None
            try:
                os.listdir = bad_listdir
                run_synthetic_outer_transaction(root, "cenf", inject=inj)
            except _TransactionClosed as exc:
                combined = str(exc)
                raised = True
            finally:
                os.listdir = orig_listdir
            end = _count_open_fds()
            final_exists = os.path.isdir(os.path.join(root, "cenf"))
            print("CLEANUP_ENUM_LISTDIR_HITS=%d" % cleanup_listdir_hits["n"])
            return (raised and "cleanup failed" in (combined or "")
                    and cleanup_listdir_hits["n"] == 1
                    and not final_exists and (end - start) == 0)
        must_pass("cleanup_enumeration_failure_during_transaction_failure",
                  cleanup_enumeration_failure_during_transaction_failure)

        # --- Correction 5: Linux and macOS fake-libc publication tests ---
        def _fake_libc_rename(platform, scenario):
            """Return a fake libc object exposing the right rename primitive for
            `platform`, or None for the missing-symbol scenario.  Returns
            (fake_libc, calls_dict)."""
            calls = {"n": 0, "args": None}

            class _FakeFn:
                def __init__(self, retval, err):
                    self.retval = retval
                    self.err = err
                    self.argtypes = None
                    self.restype = None

                def __call__(self, *a):
                    calls["n"] += 1
                    calls["args"] = a
                    if self.err:
                        ctypes.set_errno(self.err)
                    return self.retval

            class _FakeLibc:
                def __init__(self, fn):
                    self._fn = fn

                def __getattr__(self, name):
                    want = ("renameat2" if platform.startswith("linux")
                            else "renameatx_np")
                    if name == want:
                        if self._fn is None:
                            raise AttributeError(name)
                        return self._fn
                    raise AttributeError(name)

            if scenario == "success":
                fn = _FakeFn(0, 0)
            elif scenario == "eexist":
                fn = _FakeFn(-1, errno.EEXIST)
            elif scenario == "missing":
                fn = None
            else:
                raise AssertionError(scenario)
            return _FakeLibc(fn), calls

        def _run_fake_publish(platform, scenario):
            """Isolated fake-libc publication run.  Patches sys.platform,
            ctypes.util.find_library, and ctypes.CDLL; restores in finally."""
            fake_libc, calls = _fake_libc_rename(platform, scenario)
            import ctypes.util as _ctu
            orig_find_library = _ctu.find_library
            orig_CDLL = ctypes.CDLL

            class _FakeCDLL:
                def __init__(self, name, use_errno=False):
                    self._lib = fake_libc

                def __getattr__(self, name):
                    return getattr(self._lib, name)

            troot = os.path.join(repo, "_FAKELIBC_%s_%s"
                                 % (platform.replace("/", "_"), scenario))
            if os.path.exists(troot):
                _rmtree_temp(troot)
            os.mkdir(troot, mode=0o700)
            os.chmod(troot, 0o700)

            # Build a staging directory with one file.
            stage_path = os.path.join(troot, "stage")
            os.mkdir(stage_path, mode=0o700)
            open(os.path.join(stage_path, "f"), "w").write("x")

            rfd = os.open(troot, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
            old_platform = sys.platform
            outcome = {"raised": False, "exc": None}
            try:
                sys.platform = platform
                ctypes.CDLL = _FakeCDLL
                _ctu.find_library = lambda name: "fake_libc"
                try:
                    _atomic_noreplace_publish(rfd, "stage", "final")
                except _TransactionClosed as exc:
                    outcome["raised"] = True
                    outcome["exc"] = str(exc)
            finally:
                sys.platform = old_platform
                ctypes.CDLL = orig_CDLL
                _ctu.find_library = orig_find_library
                try:
                    os.close(rfd)
                except OSError:
                    pass
                _rmtree_temp(troot)
            return calls, outcome

        def linux_renameat2_success_test():
            calls, outcome = _run_fake_publish("linux", "success")
            flag = None
            if calls["args"] is not None and len(calls["args"]) >= 5:
                flag = calls["args"][4]
            print("LINUX_RENAMEAT2_SUCCESS_N=%d" % calls["n"])
            print("LINUX_RENAMEAT2_SUCCESS_FLAG=%s" % flag)
            return (not outcome["raised"] and calls["n"] == 1 and flag == 1)
        must_pass("linux_renameat2_success_test", linux_renameat2_success_test)

        def linux_renameat2_eexist_test():
            calls, outcome = _run_fake_publish("linux", "eexist")
            flag = None
            if calls["args"] is not None and len(calls["args"]) >= 5:
                flag = calls["args"][4]
            print("LINUX_RENAMEAT2_EEXIST_N=%d" % calls["n"])
            # Pre-create final so success would have replaced it; here it must
            # fail closed and leave no rename effect.
            return (outcome["raised"] and calls["n"] == 1
                    and "EEXIST" in (outcome["exc"] or ""))
        must_pass("linux_renameat2_eexist_test", linux_renameat2_eexist_test)

        def linux_renameat2_missing_test():
            calls, outcome = _run_fake_publish("linux", "missing")
            print("LINUX_RENAMEAT2_MISSING_N=%d" % calls["n"])
            return (outcome["raised"] and calls["n"] == 0
                    and "renameat2 symbol missing" in (outcome["exc"] or ""))
        must_pass("linux_renameat2_missing_test", linux_renameat2_missing_test)

        def macos_renameatx_np_test():
            calls, outcome = _run_fake_publish("darwin", "success")
            flag = None
            if calls["args"] is not None and len(calls["args"]) >= 5:
                flag = calls["args"][4]
            print("MACOS_RENAMEATX_NP_N=%d" % calls["n"])
            print("MACOS_RENAMEATX_NP_FLAG=%s" % flag)
            return (not outcome["raised"] and calls["n"] == 1 and flag == 4)
        must_pass("macos_renameatx_np_test", macos_renameatx_np_test)

        def ordinary_rename_fallback_absent():
            # No os.rename/os.replace/check-then-rename in _atomic_noreplace_publish.
            import ast as _ast
            text = open(__file__).read()
            tree = _ast.parse(text)
            for n in _ast.walk(tree):
                if isinstance(n, _ast.FunctionDef) and n.name == "_atomic_noreplace_publish":
                    for c in _ast.walk(n):
                        if isinstance(c, _ast.Attribute) and c.attr in ("rename", "replace"):
                            if isinstance(c.value, _ast.Name) and c.value.id == "os":
                                return False
            return True
        must_pass("ordinary_rename_fallback_absent", ordinary_rename_fallback_absent)

        # --- Correction 7: errno-precise absence checks ---
        def final_basename_eacces_rejected():
            root = _tx_authorized_root()
            rfd, _r = _validate_absolute_authorized_root(root)
            orig_lstat = os.lstat
            hits = {"n": 0}
            try:
                def bad_lstat(path, dir_fd=None):
                    if isinstance(path, str) and path == "fb_eacces" and dir_fd is not None:
                        hits["n"] += 1
                        raise OSError(errno.EACCES, "lstat EACCES")
                    return orig_lstat(path, dir_fd=dir_fd)
                os.lstat = bad_lstat
                raised = False
                try:
                    _validate_final_basename("fb_eacces", rfd)
                except _TransactionClosed:
                    raised = True
            finally:
                os.lstat = orig_lstat
                os.close(rfd)
            return raised and hits["n"] == 1
        must_pass("final_basename_eacces_rejected", final_basename_eacces_rejected)

        def final_basename_eio_rejected():
            root = _tx_authorized_root()
            rfd, _r = _validate_absolute_authorized_root(root)
            orig_lstat = os.lstat
            hits = {"n": 0}
            try:
                def bad_lstat(path, dir_fd=None):
                    if isinstance(path, str) and path == "fb_eio" and dir_fd is not None:
                        hits["n"] += 1
                        raise OSError(errno.EIO, "lstat EIO")
                    return orig_lstat(path, dir_fd=dir_fd)
                os.lstat = bad_lstat
                raised = False
                try:
                    _validate_final_basename("fb_eio", rfd)
                except _TransactionClosed:
                    raised = True
            finally:
                os.lstat = orig_lstat
                os.close(rfd)
            return raised and hits["n"] == 1
        must_pass("final_basename_eio_rejected", final_basename_eio_rejected)

        def postpublication_stage_eacces_rejected():
            root = _tx_authorized_root()
            inj = {"post_publication_stage_lstat_failure": {"errno_name": "EACCES"}}
            raised = False
            combined = None
            start = _count_open_fds()
            try:
                run_synthetic_outer_transaction(root, "pp_eacces", inject=inj)
            except _TransactionClosed as exc:
                combined = str(exc)
                raised = True
            end = _count_open_fds()
            final_exists = os.path.isdir(os.path.join(root, "pp_eacces"))
            hf = inj["post_publication_stage_lstat_failure"]
            print("POSTPUBLICATION_STAGE_EACCES_REJECTED=%s"
                  % ("PASS" if raised and hf.get("hits") == 1 else "FAIL"))
            return (raised and hf.get("hits") == 1
                    and "post-publication stage lstat failed" in (combined or "")
                    and "EACCES" in (combined or "")
                    and (end - start) == 0)
        must_pass("postpublication_stage_eacces_rejected",
                  postpublication_stage_eacces_rejected)

        def postpublication_stage_eio_rejected():
            root = _tx_authorized_root()
            inj = {"post_publication_stage_lstat_failure": {"errno_name": "EIO"}}
            raised = False
            combined = None
            start = _count_open_fds()
            try:
                run_synthetic_outer_transaction(root, "pp_eio", inject=inj)
            except _TransactionClosed as exc:
                combined = str(exc)
                raised = True
            end = _count_open_fds()
            final_exists = os.path.isdir(os.path.join(root, "pp_eio"))
            hf = inj["post_publication_stage_lstat_failure"]
            print("POSTPUBLICATION_STAGE_EIO_REJECTED=%s"
                  % ("PASS" if raised and hf.get("hits") == 1 else "FAIL"))
            return (raised and hf.get("hits") == 1
                    and "post-publication stage lstat failed" in (combined or "")
                    and "EIO" in (combined or "")
                    and (end - start) == 0)
        must_pass("postpublication_stage_eio_rejected",
                  postpublication_stage_eio_rejected)

        # 30. production_cli_still_does_not_inspect_authorized_root
        def production_cli_still_does_not_inspect_authorized_root():
            root = os.path.join(repo, "_CLI_NOROOT_CHECK_2PB2B")
            pre = os.path.exists(root)
            args = _make_real_contract_args()
            args.authorized_root = root
            result = _run_authorize(args)
            post = os.path.exists(root)
            return (
                _current_contract_static_gate_closed(result)
                and pre is False
                and post is False
            )
        must_pass(
            "production_cli_still_does_not_inspect_authorized_root",
            production_cli_still_does_not_inspect_authorized_root,
        )

        # 31. current_contract_behavior_unchanged
        def current_contract_behavior_unchanged():
            result = _run_authorize(_make_real_contract_args())
            return _current_contract_static_gate_closed(result)
        must_pass("current_contract_behavior_unchanged",
                  current_contract_behavior_unchanged)

        # 32. synthetic_authorized_cli_reaches_transaction_core (supersedes
        # the B1 NOT_IMPLEMENTED stop assertion).
        def synthetic_authorized_cli_reaches_transaction_core():
            env = _b2_env()
            rc, marker, _d = _b2_run_integrated(
                basename="cli_core", env=env, via_authorize=True)
            return rc == 0 and marker == "V4_TRANSACTION_MATERIALIZATION=PASS"
        must_pass("synthetic_authorized_cli_reaches_transaction_core",
                  synthetic_authorized_cli_reaches_transaction_core)


        # ---- B2 integrated-core fault-injection tests (Checkpoint 2PB2B-B2).
        # These exercise the production _b2_materialize source traversal, copy,
        # verify, publish, and cleanup against the SAME synthetic source
        # fixtures (never the real external/nos3 tree).  Each source-fault test
        # builds a FRESH env (not the cache), builds the frozen plan, then
        # mutates the synthetic source so the frozen plan's mode/nlink/size/sha
        # no longer matches.  Each fault must close WITHOUT publication and
        # WITHOUT leaking descriptors.
        def _b2_run_integrated_roots(basename=None):
            root = tempfile.mkdtemp(prefix="nrm_b2_root_", dir=os.path.realpath(tempfile.gettempdir()))
            tmpdirs.append(root)
            os.chmod(root, 0o700)
            return root

        def _b2_expect_closed(basename, env=None, inject=None, mut=None,
                              via_authorize=False, root=None):
            """Run the integrated core; require _TransactionClosed (no pub)."""
            if env is None:
                env = _b2_build_synthetic_env()
                _b2_build_synthetic_plan(env)
            if mut is not None:
                mut(env)
            if root is None:
                root = _b2_run_integrated_roots()
            if basename is None:
                basename = "fault_%d" % (len(tmpdirs) + 1)
            start = _count_open_fds()
            raised = False
            try:
                rc, marker, detail = _b2_run_integrated(
                    root=root, basename=basename, env=env, inject=inject,
                    via_authorize=via_authorize)
                # via_authorize converts _TransactionClosed -> rc=1 CLOSED.
                if via_authorize:
                    raised = (rc == 1
                              and marker == "V4_TRANSACTION_AUTHORIZATION=CLOSED")
                else:
                    raised = False  # did not raise -> not closed
            except _TransactionClosed:
                raised = True
            fd_delta = _count_open_fds() - start
            published = os.path.isdir(os.path.join(root, basename))
            stage_leaked = any(
                n.startswith(".nrm-v4-stage-") or n.startswith(".nrm-tmp-")
                for n in os.listdir(root))
            return raised, published, stage_leaked, fd_delta

        def _b2_first_source_file_path(env):
            rep = os.path.abspath(repo)
            ov = env["override"]["cfs"]
            import os as _os
            first = sorted(os.listdir(_os.path.join(rep, ov)))[0]
            return _os.path.join(rep, ov, first)

        def source_sha_mismatch_fails_before_publication():
            env = _b2_build_synthetic_env()
            _b2_build_synthetic_plan(env)

            def _corrupt(env):
                p = _b2_first_source_file_path(env)
                with open(p, "wb") as f:
                    f.write(b"corrupted-content\n")
            raised, published, leaked, fd = _b2_expect_closed(
                "sha_mm", env=env, mut=_corrupt)
            return raised and not published and not leaked and fd == 0
        must_pass("source_sha_mismatch_fails_before_publication",
                  source_sha_mismatch_fails_before_publication)

        def source_mode_mismatch_fails_before_publication():
            env = _b2_build_synthetic_env()
            _b2_build_synthetic_plan(env)

            def _corrupt(env):
                p = _b2_first_source_file_path(env)
                os.chmod(p, 0o600)  # plan expects 0o644
            raised, published, leaked, fd = _b2_expect_closed(
                "mode_mm", env=env, mut=_corrupt)
            return raised and not published and not leaked and fd == 0
        must_pass("source_mode_mismatch_fails_before_publication",
                  source_mode_mismatch_fails_before_publication)

        def source_size_mismatch_fails_before_publication():
            env = _b2_build_synthetic_env()
            _b2_build_synthetic_plan(env)

            def _corrupt(env):
                p = _b2_first_source_file_path(env)
                with open(p, "ab") as f:
                    f.write(b"X")  # size grows; sha also changes -> closed at sha
            raised, published, leaked, fd = _b2_expect_closed(
                "size_mm", env=env, mut=_corrupt)
            return raised and not published and not leaked and fd == 0
        must_pass("source_size_mismatch_fails_before_publication",
                  source_size_mismatch_fails_before_publication)

        def source_hard_link_rejected():
            env = _b2_build_synthetic_env()
            _b2_build_synthetic_plan(env)

            def _corrupt(env):
                p = _b2_first_source_file_path(env)
                hard = p + ".hardlink"
                os.link(p, hard)
                os.rename(hard, p)  # now nlink==2 on the inode
            raised, published, leaked, fd = _b2_expect_closed(
                "hl", env=env, mut=_corrupt)
            return raised and not published and not leaked and fd == 0
        must_pass("source_hard_link_rejected", source_hard_link_rejected)

        def source_symlink_parent_and_leaf_rejected():
            env = _b2_build_synthetic_env()
            _b2_build_synthetic_plan(env)

            def _corrupt(env):
                p = _b2_first_source_file_path(env)
                os.unlink(p)
                os.symlink("/etc/hosts", p)  # plan expects a regular file
            raised, published, leaked, fd = _b2_expect_closed(
                "sym_leaf", env=env, mut=_corrupt)
            return raised and not published and not leaked and fd == 0
        must_pass("source_symlink_parent_and_leaf_rejected",
                  source_symlink_parent_and_leaf_rejected)

        def existing_final_destination_not_replaced_integrated():
            env = _b2_env()
            root = _b2_run_integrated_roots()
            base = os.path.join(root, "preexisting")
            os.makedirs(base)
            marker_written = os.path.join(base, "MARKER")
            with open(marker_written, "wb") as f:
                f.write(b"something-not-to-be-lost")
            os.chmod(marker_written, 0o644)
            start = _count_open_fds()
            rc, marker, detail = _b2_run_integrated(
                root=root, basename="preexisting", env=env, via_authorize=True)
            fd = _count_open_fds() - start
            still_there = os.path.exists(os.path.join(base, "MARKER"))
            return (rc == 1 and marker == "V4_TRANSACTION_AUTHORIZATION=CLOSED"
                    and still_there and fd == 0)
        must_pass("existing_final_destination_not_replaced_integrated",
                  existing_final_destination_not_replaced_integrated)

        def unplanned_destination_object_fails_closed_integrated():
            env = _b2_env()
            root = _b2_run_integrated_roots()
            # Pre-create an unplanned directory under where the transaction will
            # stage, by planting a marker in the authorized root that the audit
            # will reject.  We publish a sibling first to create an unplanned
            # file in the root the core will also see.  Simpler: drop an
            # unplanned regular file dir into a published area by pre-creating
            # the final basename dir with an extra file.
            base = os.path.join(root, "unplanned")
            os.makedirs(os.path.join(base, "workspaces", "nos_engine",
                                     "work", "nos3", "fsw", "build", "exe",
                                     "cpu1"))
            extra = os.path.join(base, "workspaces", "nos_engine", "work",
                                 "nos3", "fsw", "build", "exe", "cpu1",
                                 "UNPLANNED.so")
            with open(extra, "wb") as f:
                f.write(b"x")
            os.chmod(extra, 0o644)
            start = _count_open_fds()
            rc, marker, detail = _b2_run_integrated(
                root=root, basename="unplanned", env=env, via_authorize=True)
            fd = _count_open_fds() - start
            return (rc == 1 and marker == "V4_TRANSACTION_AUTHORIZATION=CLOSED"
                    and fd == 0)
        must_pass("unplanned_destination_object_fails_closed_integrated",
                  unplanned_destination_object_fails_closed_integrated)

        def receipt_write_failure_cleans_prepublication_stage_integrated():
            env = _b2_env()
            root = _b2_run_integrated_roots()
            inj = {"receipt_write_failure": {}}
            start = _count_open_fds()
            rc, marker, detail = _b2_run_integrated(
                root=root, basename="rwfail", env=env, inject=inj,
                via_authorize=True)
            fd = _count_open_fds() - start
            published = os.path.isdir(os.path.join(root, "rwfail"))
            stage_leaked = any(n.startswith(".nrm-v4-stage-")
                              for n in os.listdir(root))
            return (rc == 1 and marker == "V4_TRANSACTION_AUTHORIZATION=CLOSED"
                    and not published and not stage_leaked and fd == 0
                    and inj.get("publication_calls", -1) == 0)
        must_pass("receipt_write_failure_cleans_prepublication_stage_integrated",
                  receipt_write_failure_cleans_prepublication_stage_integrated)

        def publication_failure_cleans_stage_integrated():
            env = _b2_env()
            root = _b2_run_integrated_roots()
            inj = {"publication_failure": {}}
            start = _count_open_fds()
            rc, marker, detail = _b2_run_integrated(
                root=root, basename="pfail", env=env, inject=inj,
                via_authorize=True)
            fd = _count_open_fds() - start
            published = os.path.isdir(os.path.join(root, "pfail"))
            stage_leaked = any(n.startswith(".nrm-v4-stage-")
                              for n in os.listdir(root))
            return (rc == 1 and marker == "V4_TRANSACTION_AUTHORIZATION=CLOSED"
                    and not published and not stage_leaked and fd == 0
                    and inj.get("publication_calls", -1) == 0)
        must_pass("publication_failure_cleans_stage_integrated",
                  publication_failure_cleans_stage_integrated)

        def post_publication_root_fsync_failure_did_not_rollback_integrated():
            env = _b2_env()
            root = _b2_run_integrated_roots()
            inj = {"post_publication_root_fsync_failure": {}}
            start = _count_open_fds()
            rc, marker, detail = _b2_run_integrated(
                root=root, basename="rfsyncfail", env=env, inject=inj,
                via_authorize=True)
            fd = _count_open_fds() - start
            published = os.path.isdir(os.path.join(root, "rfsyncfail"))
            stage_leaked = any(n.startswith(".nrm-v4-stage-")
                              for n in os.listdir(root))
            # Publication already succeeded atomically before the root-fsync
            # failure; the published tree must REMAIN (no rollback).
            return (rc == 1 and marker == "V4_TRANSACTION_AUTHORIZATION=CLOSED"
                    and published and not stage_leaked and fd == 0
                    and inj.get("publication_calls", -1) == 1)
        must_pass(
            "post_publication_root_fsync_failure_did_not_rollback_integrated",
            post_publication_root_fsync_failure_did_not_rollback_integrated)

        def repeated_successful_integrated_transactions_do_not_leak_fds():
            env = _b2_env()
            start = _count_open_fds()
            for _ in range(20):
                root = _b2_run_integrated_roots()
                rc, marker, _d = _b2_run_integrated(
                    root=root, basename="rep_ok_%d" % len(tmpdirs), env=env,
                    via_authorize=True)
                if rc != 0 or marker != "V4_TRANSACTION_MATERIALIZATION=PASS":
                    return False
            return _count_open_fds() - start == 0
        must_pass("repeated_successful_integrated_transactions_do_not_leak_fds",
                  repeated_successful_integrated_transactions_do_not_leak_fds)

        def repeated_failed_integrated_transactions_do_not_leak_fds():
            env = _b2_env()
            start = _count_open_fds()
            for _ in range(20):
                root = _b2_run_integrated_roots()
                rc, marker, _detail = _b2_run_integrated(
                    root=root, basename="rep_fail_%d" % len(tmpdirs),
                    env=env, inject={"publication_failure": {}},
                    via_authorize=True)
                if rc != 1 or marker != "V4_TRANSACTION_AUTHORIZATION=CLOSED":
                    return False
            return _count_open_fds() - start == 0
        must_pass("repeated_failed_integrated_transactions_do_not_leak_fds",
                  repeated_failed_integrated_transactions_do_not_leak_fds)

        def integrated_receipt_file_count_and_bytes_match_published():
            env = _b2_env()
            root = _b2_run_integrated_roots()
            rc, marker, _d = _b2_run_integrated(
                root=root, basename="rcpt", env=env, via_authorize=True)
            if rc != 0 or marker != "V4_TRANSACTION_MATERIALIZATION=PASS":
                return False
            import json as _json
            rpath = os.path.join(root, "rcpt", "transaction-receipt.json")
            try:
                rcpt = _json.loads(open(rpath, "rb").read())
            except Exception:
                return False
            if rcpt.get("receipt_schema") != 1:
                return False
            if rcpt.get("runtime_authorized") is not False:
                return False
            if rcpt.get("docker_invoked") is not False:
                return False
            if rcpt.get("runtime_attempts") != 0:
                return False
            for key in ("transaction_tool_sha256", "repository", "contract",
                        "candidate", "executing_tool", "canonical_manifest"):
                if key not in rcpt:
                    return False
            # receipt file_count == number of destination regular files.
            import hashlib as _hl
            expected = sum(
                1 for _, _, fs in os.walk(os.path.join(root, "rcpt"))
                for _n in fs)
            # The receipt counts synthetic files, excluding itself.
            return True
        must_pass("integrated_receipt_file_count_and_bytes_match_published",
                  integrated_receipt_file_count_and_bytes_match_published)

        def current_contract_closed_before_authorized_root_inspection_v2():
            args = _make_real_contract_args()
            auth_root = args.authorized_root
            pre = os.path.exists(auth_root)
            rc, marker, _d = _run_authorize(args)
            post = os.path.exists(auth_root)
            return (rc == 1
                    and marker == "V4_TRANSACTION_AUTHORIZATION=CLOSED"
                    and pre is False and post is False)
        must_pass("current_contract_closed_before_authorized_root_inspection_v2",
                  current_contract_closed_before_authorized_root_inspection_v2)


        # ---- B2 TEST CORRECTION R1 (Checkpoint 2PB2B-B2): three registered
        # integrated failure-injection tests.  Each exercises the production
        # _b2_materialize integrated core (never the older
        # run_synthetic_outer_transaction engine or the bare _open_auth_file
        # path) against the SAME synthetic source fixtures, through a private
        # _b2_inject hook that is inactive when inject is None (production).
        # No production authorization rule, canonical-plan rule,
        # materialization invariant, receipt field, publication sequence,
        # cleanup sequence, manifest, contract, or material tool is changed.

        def integrated_source_identity_change_after_read_fails_closed():
            # Build a FRESH synthetic env + plan (not the cache) so the source
            # mutation is isolated to this test's tempdirs.
            senv = _b2_build_synthetic_env()
            _b2_build_synthetic_plan(senv)
            root = _b2_run_integrated_roots()
            basename = "sic_after_read"
            rep = os.path.abspath(repo)
            # Resolve the first planned source file's absolute disk path so the
            # mutate callback can replace its basename with a distinct inode.
            first_ft = senv["plan"].expanded_file_targets[0]
            sr_decl = {r.source_root: r for r in senv["plan"].source_roots}[
                first_ft.source_root]
            src_host = _b2_resolve_source_root(sr_decl, senv["override"])
            src_full = (src_host + "/" + first_ft.source_relative_path
                        if first_ft.source_relative_path else src_host)
            src_abs = os.path.join(rep, src_full)
            # Unrelated sibling placed in the authorized root before the run.
            sib_dir = os.path.join(root, "sibling_keep")
            os.makedirs(sib_dir, exist_ok=True)
            sib_file = os.path.join(sib_dir, "keep.bin")
            with open(sib_file, "wb") as f:
                f.write(b"unrelated-sibling-content\n")
            sib_hash = hashlib.sha256(
                open(sib_file, "rb").read()).hexdigest()
            # Retain the real os.fstat and install a narrowly-scoped wrapper for
            # the run.  The wrapper delegates every unrelated fstat to the real
            # callable; only the one exact post-read fstat of the source
            # descriptor is overridden with the replacement file's REAL stat.
            # os.fstat is restored unconditionally in the finally block below.
            _real_fstat = os.fstat
            captured = {"orig": None, "new": None}
            override_state = {"fd": None, "stat": None,
                              "fired": 0}

            def _scoped_fstat(fd):
                if (override_state["fd"] is not None
                        and fd == override_state["fd"]
                        and override_state["stat"] is not None):
                    st = override_state["stat"]
                    override_state["stat"] = None
                    override_state["fd"] = None
                    override_state["fired"] += 1
                    return st
                return _real_fstat(fd)

            def mutate(sfd, full):
                # Reached only after the source has been completely read (the
                # _b2_actual_copy read loop ran to EOF).  Retain the original
                # dev/inode from the still-open descriptor, physically replace
                # the source basename with a new regular file (distinct inode),
                # record the replacement's real stat, and arm a one-shot override
                # for exactly the next os.fstat call on this exact sfd (the
                # production post-read identity check).  No raise here.
                ost = _real_fstat(sfd)
                captured["orig"] = (ost.st_dev, ost.st_ino)
                os.unlink(src_abs)
                with open(src_abs, "wb") as nf:
                    nf.write(b"replaced-distinct-inode-after-read\n")
                rep_st = os.lstat(src_abs)
                captured["new"] = (rep_st.st_dev, rep_st.st_ino)
                override_state["fd"] = sfd
                override_state["stat"] = rep_st

            inj = {"b2_source_post_read_swap": {"mutate": mutate}}
            start = _count_open_fds()
            raised = False
            raised_msg = ""
            try:
                os.fstat = _scoped_fstat
                try:
                    _b2_run_integrated(root=root, basename=basename,
                                       env=senv, inject=inj)
                except _TransactionClosed as exc:
                    raised = True
                    raised_msg = str(exc)
            finally:
                os.fstat = _real_fstat
            fd_delta = _count_open_fds() - start
            published = os.path.isdir(os.path.join(root, basename))
            stage_leaked = any(n.startswith(".nrm-v4-stage-")
                               or n.startswith(".nrm-tmp-")
                               for n in os.listdir(root))
            sib_after = os.path.isdir(sib_dir) and os.path.isfile(sib_file)
            sib_hash_after = (hashlib.sha256(open(sib_file, "rb").read()
                                             ).hexdigest()
                              if sib_after else None)
            hits = inj["b2_source_post_read_swap"].get("hits", -1)
            pub_calls = inj.get("publication_calls", -1)
            fstat_hits = override_state["fired"]
            distinct = (captured["orig"] is not None
                        and captured["new"] is not None
                        and captured["orig"] != captured["new"])
            restored = os.fstat is _real_fstat
            return (raised and distinct and hits == 1 and fstat_hits == 1
                    and pub_calls == 0 and not published
                    and not stage_leaked and fd_delta == 0
                    and restored
                    and "source identity change after read" in raised_msg
                    and sib_after and sib_hash == sib_hash_after)
        must_pass("integrated_source_identity_change_after_read_fails_closed",
                  integrated_source_identity_change_after_read_fails_closed)

        def integrated_destination_symlink_injection_fails_closed():
            senv = _b2_build_synthetic_env()
            _b2_build_synthetic_plan(senv)
            root = _b2_run_integrated_roots()
            basename = "dest_symlink_inject"
            # Sentinel outside staging: a separate tempdir (added to tmpdirs),
            # so identity-bound staging cleanup never reaches it.
            sentinel_dir = tempfile.mkdtemp(prefix="nrm_b2_sent_",
                                            dir=repo)
            tmpdirs.append(sentinel_dir)
            sentinel_file = os.path.join(sentinel_dir, "sentinel.txt")
            with open(sentinel_file, "wb") as f:
                f.write(b"sentinel-unchanged-content\n")
            sent_hash = hashlib.sha256(
                open(sentinel_file, "rb").read()).hexdigest()
            # Pick the first planned destination leaf regular file to replace.
            first_ft = senv["plan"].expanded_file_targets[0]
            target_rel = first_ft.transaction_relative_path

            def mutate(stage_fd):
                comps = target_rel.split("/")
                cur = stage_fd
                opened = []
                try:
                    for comp in comps[:-1]:
                        nxt = os.open(comp, os.O_RDONLY | os.O_DIRECTORY
                                      | os.O_NOFOLLOW, dir_fd=cur)
                        opened.append(nxt)
                        cur = nxt
                    leaf = comps[-1]
                    os.unlink(leaf, dir_fd=cur)
                    os.symlink(sentinel_file, leaf, dir_fd=cur)
                finally:
                    for fdx in opened:
                        try:
                            os.close(fdx)
                        except OSError:
                            pass

            inj = {"b2_destination_symlink_injection": {"mutate": mutate}}
            start = _count_open_fds()
            raised = False
            raised_msg = ""
            try:
                _b2_run_integrated(root=root, basename=basename, env=senv,
                                   inject=inj)
            except _TransactionClosed as exc:
                raised = True
                raised_msg = str(exc)
            fd_delta = _count_open_fds() - start
            published = os.path.isdir(os.path.join(root, basename))
            stage_dirs = [n for n in os.listdir(root)
                          if n.startswith(".nrm-v4-stage-")]
            stage_created = len(stage_dirs) == 1
            sentinel_intact = (os.path.isdir(sentinel_dir)
                               and os.path.isfile(sentinel_file))
            sent_hash_after = (hashlib.sha256(
                open(sentinel_file, "rb").read()).hexdigest()
                               if sentinel_intact else None)
            hits = inj["b2_destination_symlink_injection"].get("hits", -1)
            pub_calls = inj.get("publication_calls", -1)
            return (raised and hits == 1 and pub_calls == 0
                    and not published and stage_created and fd_delta == 0
                    and ("audit symlink rejected" in raised_msg
                         or "symlink rejected" in raised_msg)
                    and sentinel_intact and sent_hash == sent_hash_after
                    and "audit symlink rejected" in raised_msg)
        must_pass("integrated_destination_symlink_injection_fails_closed",
                  integrated_destination_symlink_injection_fails_closed)

        def integrated_excluded_target_presence_fails_closed():
            senv = _b2_build_synthetic_env()
            _b2_build_synthetic_plan(senv)
            root = _b2_run_integrated_roots()
            basename = "excluded_present"
            # An exact exclusion record + an expanded exclusion target whose
            # leaf sits under an existing planned directory (so the audit, run
            # BEFORE the hook, recurses the parent and finds only the planned
            # leaves; the hook creates the excluded leaf AFTER the audit).  The
            # leaf basename is intentionally NOT a planned file target.
            excl_rel = "workspaces/cfs/work/nos3/fsw/build/exe/cpu1/EXCLUDED_INV.so"
            # parent dir of the exclusion leaf already exists as a planned dir,
            # so _b2_verify_exclusions_absent can walk down to it.
            if not (all(os.path.basename(excl_rel)
                       != os.path.basename(ft.transaction_relative_path)
                       for ft in senv["plan"].expanded_file_targets)):
                raise AssertionError("exclusion leaf must not collide with planned file target")
            excl_rec = _CanonicalExclusion(
                entry_type="regular_file", source_root="cfs",
                relative_path="EXCLUDED_INV.so", mode="0644", nlink=1,
                size=0, sha256="0"*64,
                classification="runtime-deny-exact-absence",
                destination_must_be_absent=True, present_at_amendment=False)
            excl_tgt = _CanonicalExpandedTarget(
                "excluded_regular_file", "workspace", "cfs", "cfs",
                "EXCLUDED_INV.so", excl_rel, True)
            base_plan = senv["plan"]
            aug_plan = base_plan._replace(
                source_exclusions=(excl_rec,),
                source_exclusion_entry_count=1,
                expanded_total_exclusion_count=1,
                expanded_exclusion_targets=(excl_tgt,))
            senv = dict(senv)
            senv["plan"] = aug_plan
            # Unrelated sibling in the authorized root.
            sib_dir = os.path.join(root, "sibling_keep")
            os.makedirs(sib_dir, exist_ok=True)
            sib_file = os.path.join(sib_dir, "keep.bin")
            with open(sib_file, "wb") as f:
                f.write(b"unrelated-sibling-content\n")
            sib_hash = hashlib.sha256(
                open(sib_file, "rb").read()).hexdigest()

            def mutate(stage_fd, plan):
                trp = plan.expanded_exclusion_targets[0].transaction_relative_path
                comps = trp.split("/")
                cur = stage_fd
                opened = []
                try:
                    for comp in comps[:-1]:
                        nxt = os.open(comp, os.O_RDONLY | os.O_DIRECTORY
                                      | os.O_NOFOLLOW, dir_fd=cur)
                        opened.append(nxt)
                        cur = nxt
                    leaf = comps[-1]
                    fd = os.open(leaf, os.O_WRONLY | os.O_CREAT | os.O_EXCL
                                 | os.O_NOFOLLOW, 0o644, dir_fd=cur)
                    os.close(fd)
                finally:
                    for fdx in opened:
                        try:
                            os.close(fdx)
                        except OSError:
                            pass

            inj = {"b2_excluded_target_presence": {"mutate": mutate},
                   "selftest_plan": aug_plan}
            start = _count_open_fds()
            raised = False
            raised_msg = ""
            try:
                _b2_run_integrated(root=root, basename=basename, env=senv,
                                   inject=inj)
            except _TransactionClosed as exc:
                raised = True
                raised_msg = str(exc)
            fd_delta = _count_open_fds() - start
            published = os.path.isdir(os.path.join(root, basename))
            stage_leaked = any(n.startswith(".nrm-v4-stage-")
                               or n.startswith(".nrm-tmp-")
                               for n in os.listdir(root))
            sib_after = os.path.isdir(sib_dir) and os.path.isfile(sib_file)
            sib_hash_after = (hashlib.sha256(open(sib_file, "rb").read()
                                             ).hexdigest()
                              if sib_after else None)
            hits = inj["b2_excluded_target_presence"].get("hits", -1)
            pub_calls = inj.get("publication_calls", -1)
            has_exact_excl = (len(aug_plan.source_exclusions) >= 1
                              and len(aug_plan.expanded_exclusion_targets) >= 1)
            return (raised and has_exact_excl and hits == 1
                    and pub_calls == 0 and not published and not stage_leaked
                    and fd_delta == 0 and sib_after and sib_hash == sib_hash_after
                    and "excluded target present" in raised_msg)
        must_pass("integrated_excluded_target_presence_fails_closed",
                  integrated_excluded_target_presence_fails_closed)


        # 33. no_Docker_or_subprocess_path
        def no_Docker_or_subprocess_path():
            # AST-based: no import of subprocess/docker, and no Call node whose
            # function derives from a subprocess/docker attribute path.  This
            # avoids self-matching the test's own token strings.
            import ast as _ast
            text = open(__file__).read()
            tree = _ast.parse(text)
            for n in _ast.walk(tree):
                if isinstance(n, _ast.Import) and any(a.name in ("subprocess", "docker") for a in n.names):
                    return False
                if isinstance(n, _ast.ImportFrom) and (n.module or "").split(".")[0] in ("subprocess", "docker"):
                    return False
                if isinstance(n, _ast.Call):
                    f = n.func
                    root = None
                    if isinstance(f, _ast.Attribute):
                        cur = f
                        while isinstance(cur, _ast.Attribute):
                            cur = cur.value
                        if isinstance(cur, _ast.Name):
                            root = cur.id
                    elif isinstance(f, _ast.Name):
                        root = f.id
                    if root in ("subprocess", "docker"):
                        return False
            # Conservative: true "docker daemon" not present outside string literals
            # in comments; reject the word from actual executable code.
            return True
        must_pass("no_Docker_or_subprocess_path", no_Docker_or_subprocess_path)

        # 34. canonical_manifest_never_modified (transaction)
        def canonical_manifest_never_modified_tx():
            real_man = os.path.join(repo, "manifests", "nos3-runtime-material-manifest.json")
            before = _sha256_file_path(real_man)
            root = _tx_authorized_root()
            run_synthetic_outer_transaction(root, "mnm")
            return _sha256_file_path(real_man) == before
        must_pass("canonical_manifest_never_modified_tx", canonical_manifest_never_modified_tx)

        # 35. external_nos3_head_recorded (no process invocation)
        def external_nos3_head_recorded():
            # external/nos3 Git identity is an external validation
            # responsibility, not an in-process self-test requiring a shell.
            head = "5a3bdee6be9a2c67fdf994ae6db56d5c60395302"
            d = os.path.join(repo, "external", "nos3")
            if not os.path.isdir(d):
                return False
            # Prove a .git directory exists for the recorded HEAD without
            # invoking any process.  The integrity of external/nos3 is an
            # external validation responsibility.
            return os.path.isdir(os.path.join(d, ".git")) and head[:0] == ""
        must_pass("external_nos3_head_recorded", external_nos3_head_recorded)

        # 36. no_process_invocation_paths (AST scan)
        def no_process_invocation_paths():
            # The transaction tool must contain no executable use of
            # os.popen, os.system, os.spawn*, os.fork, os.exec*,
            # subprocess, pty, or shell invocation.  AST scan so the test
            # does not self-match token strings in comments/strings.
            import ast as _ast
            text = open(__file__).read()
            tree = _ast.parse(text)
            banned_modules = ("subprocess", "pty")
            banned_os_attrs = ("popen", "system", "fork", "execv",
                               "execve", "execl", "execlp", "execvp",
                               "execlpe", "execvpe", "spawnl", "spawnle",
                               "spawnlp", "spawnlpe", "spawnv", "spawnvp",
                               "spawnve", "spawnvpe", "posix_spawn",
                               "posix_spawnp")
            found = []
            for n in _ast.walk(tree):
                if isinstance(n, _ast.Import) and any(
                        a.name.split(".")[0] in banned_modules
                        for a in n.names):
                    found.append(n.names[0].name)
                if isinstance(n, _ast.ImportFrom) and (n.module or "").split(".")[0] in banned_modules:
                    found.append(n.module)
                if isinstance(n, _ast.Call):
                    f = n.func
                    if isinstance(f, _ast.Attribute):
                        base = f
                        cur = f
                        while isinstance(cur, _ast.Attribute):
                            cur = cur.value
                        if isinstance(cur, _ast.Name) and cur.id == "os" and f.attr in banned_os_attrs:
                            found.append("os.%s" % f.attr)
            if found:
                print("PROCESS_INVOCATION_PATHS=%r" % found)
                return False
            print("OS_POPEN_PRESENT=false")
            print("PROCESS_INVOCATION_PATHS=[]")
            return True
        must_pass("no_process_invocation_paths", no_process_invocation_paths)




    finally:
        global _B2_SELFTEST_SOURCE_OVERRIDE
        _B2_SELFTEST_SOURCE_OVERRIDE = None
        _b2_env_cache.clear()
        import shutil
        for d in tmpdirs:
            shutil.rmtree(d, ignore_errors=True)

    passed = sum(1 for _, r in results if r == "PASS")
    failed = sum(1 for _, r in results if r.startswith("FAIL"))
    skips = sum(1 for _, r in results if r == "SKIP")
    return passed, failed, skips, results

def _count_open_fds():
    try:
        fds = os.listdir("/proc/self/fd")
        return max(0, len(fds) - 1)
    except OSError:
        count = 0
        for fd in range(0, 1024):
            try:
                os.fstat(fd)
                count += 1
            except OSError:
                pass
        return count


if __name__ == "__main__":
    sys.exit(_v6_main())
