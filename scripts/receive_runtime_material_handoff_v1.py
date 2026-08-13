#!/usr/bin/env python3
"""WP4 D-064 V6 UID-501 runtime-material handoff receiver.

Standard-library-only. Receives WP4_D064_V6_HANDOFF_SCHEMA_1 from stdin,
reconstructs a private runtime copy using descriptor-bound O_EXCL|O_NOFOLLOW,
verifies path/mode/size/hash/count/footer bindings, then atomically publishes
with no replacement. Never invokes Docker or a subprocess.
"""

import argparse
import ctypes
import ctypes.util
import errno
import hashlib
import io
import json
import os
import stat
import struct
import sys
import tempfile

MAGIC = b"WP4D064V6H1\x00"
END_MAGIC = b"END!"
SCHEMA = 1
PURPOSE = "WP4_D064_V6_HANDOFF_SCHEMA_1"
MAX_JSON_FRAME = 64 * 1024 * 1024
MAX_FILE_COUNT = 100000
MAX_FILE_BYTES = 4 * 1024 * 1024 * 1024
RECEIVER_RECEIPT = ".wp4-d064-v6-handoff-receipt.json"


class HandoffClosed(Exception):
    pass


def _canonical_json(obj):
    return (
        json.dumps(
            obj,
            ensure_ascii=True,
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
    ).encode("utf-8")


def _read_exact(stream, count):
    if type(count) is not int or count < 0:
        raise HandoffClosed("invalid read count")
    out = bytearray()
    while len(out) < count:
        chunk = stream.read(count - len(out))
        if not chunk:
            raise HandoffClosed("unexpected EOF")
        out.extend(chunk)
    return bytes(out)


def _read_json_frame(stream, digest):
    prefix = _read_exact(stream, 4)
    digest.update(prefix)
    length = struct.unpack(">I", prefix)[0]
    if length <= 0 or length > MAX_JSON_FRAME:
        raise HandoffClosed("invalid JSON frame length")
    raw = _read_exact(stream, length)
    digest.update(raw)
    try:
        obj = json.loads(raw.decode("utf-8"))
    except Exception as exc:
        raise HandoffClosed("invalid JSON frame: %s" % exc)
    if type(obj) is not dict:
        raise HandoffClosed("JSON frame is not exact object")
    if raw != _canonical_json(obj):
        raise HandoffClosed("JSON frame is not canonical")
    return obj


def _validate_rel(rel):
    if type(rel) is not str or rel == "":
        raise HandoffClosed("path empty/not exact string")
    if rel.startswith("/") or rel.endswith("/"):
        raise HandoffClosed("absolute/trailing-separator path")
    if "\\" in rel or "\x00" in rel or "//" in rel:
        raise HandoffClosed("path backslash/NUL/repeated separator")
    for ch in rel:
        if 0xD800 <= ord(ch) <= 0xDFFF:
            raise HandoffClosed("path surrogate")
    parts = rel.split("/")
    if any(p in ("", ".", "..") for p in parts):
        raise HandoffClosed("path dot/empty component")
    return tuple(parts)


def _hex64(value):
    return (
        type(value) is str
        and len(value) == 64
        and value == value.lower()
        and all(c in "0123456789abcdef" for c in value)
    )


def _open_private_parent(path):
    lexical = os.path.abspath(path)
    real = os.path.realpath(lexical)
    if real != lexical:
        raise HandoffClosed("output parent contains symlink/canonical drift")
    fd = os.open(real, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        st = os.fstat(fd)
        if not stat.S_ISDIR(st.st_mode):
            raise HandoffClosed("output parent not directory")
        if st.st_uid != os.geteuid():
            raise HandoffClosed("output parent owner mismatch")
        if stat.S_IMODE(st.st_mode) & 0o077:
            raise HandoffClosed("output parent must be private")
        return fd, real
    except BaseException:
        os.close(fd)
        raise


def _open_or_create_dir(parent_fd, name):
    try:
        lst = os.lstat(name, dir_fd=parent_fd)
    except OSError as exc:
        if exc.errno != errno.ENOENT:
            raise HandoffClosed("directory lstat failed: %s" % exc)
        os.mkdir(name, 0o700, dir_fd=parent_fd)
        lst = os.lstat(name, dir_fd=parent_fd)
    if stat.S_ISLNK(lst.st_mode) or not stat.S_ISDIR(lst.st_mode):
        raise HandoffClosed("path component not plain directory: %s" % name)
    fd = os.open(
        name,
        os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
        dir_fd=parent_fd,
    )
    fst = os.fstat(fd)
    if (fst.st_dev, fst.st_ino) != (lst.st_dev, lst.st_ino):
        os.close(fd)
        raise HandoffClosed("directory identity discontinuity")
    if fst.st_uid != os.geteuid():
        os.close(fd)
        raise HandoffClosed("directory owner mismatch")
    return fd


def _open_parent_for_file(stage_fd, rel):
    parts = _validate_rel(rel)
    cur = os.dup(stage_fd)
    try:
        for comp in parts[:-1]:
            nxt = _open_or_create_dir(cur, comp)
            os.close(cur)
            cur = nxt
        return cur, parts[-1]
    except BaseException:
        try:
            os.close(cur)
        except OSError:
            pass
        raise


def _write_received_file(stage_fd, meta, stream, digest):
    rel = meta.get("path")
    _validate_rel(rel)
    mode = meta.get("mode")
    size = meta.get("size")
    expected_sha = meta.get("sha256")
    if type(mode) is not int or mode < 0 or mode > 0o777:
        raise HandoffClosed("invalid file mode")
    if type(size) is not int or size < 0 or size > MAX_FILE_BYTES:
        raise HandoffClosed("invalid file size")
    if not _hex64(expected_sha):
        raise HandoffClosed("invalid file SHA")

    pfd, leaf = _open_parent_for_file(stage_fd, rel)
    fd = None
    try:
        fd = os.open(
            leaf,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
            mode,
            dir_fd=pfd,
        )
        h = hashlib.sha256()
        remaining = size
        while remaining:
            chunk = _read_exact(stream, min(1024 * 1024, remaining))
            digest.update(chunk)
            h.update(chunk)
            off = 0
            while off < len(chunk):
                wrote = os.write(fd, chunk[off:])
                if wrote <= 0:
                    raise HandoffClosed("short write")
                off += wrote
            remaining -= len(chunk)
        os.fchmod(fd, mode)
        os.fsync(fd)
        st = os.fstat(fd)
        if (
            not stat.S_ISREG(st.st_mode)
            or st.st_nlink != 1
            or st.st_uid != os.geteuid()
            or st.st_size != size
            or stat.S_IMODE(st.st_mode) != mode
        ):
            raise HandoffClosed("received file identity invalid")
        if h.hexdigest() != expected_sha:
            raise HandoffClosed("received file SHA mismatch")
        if (
            type(meta.get("source_dev")) is int
            and type(meta.get("source_inode")) is int
            and (st.st_dev, st.st_ino)
            == (meta["source_dev"], meta["source_inode"])
        ):
            raise HandoffClosed("source/destination inode alias")
    finally:
        if fd is not None:
            try:
                os.close(fd)
            except OSError:
                pass
        os.close(pfd)


def _fd_walk_fsync(fd):
    for name in sorted(os.listdir(fd)):
        st = os.lstat(name, dir_fd=fd)
        if stat.S_ISLNK(st.st_mode):
            raise HandoffClosed("symlink in receiver tree")
        if stat.S_ISDIR(st.st_mode):
            cfd = os.open(
                name,
                os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                dir_fd=fd,
            )
            try:
                _fd_walk_fsync(cfd)
                os.fsync(cfd)
            finally:
                os.close(cfd)
        elif not stat.S_ISREG(st.st_mode):
            raise HandoffClosed("special file in receiver tree")
    os.fsync(fd)


def _desc_rmtree(fd, name):
    try:
        st = os.lstat(name, dir_fd=fd)
    except OSError as exc:
        if exc.errno == errno.ENOENT:
            return
        raise
    if stat.S_ISLNK(st.st_mode):
        raise HandoffClosed("cleanup symlink rejected")
    if stat.S_ISDIR(st.st_mode):
        cfd = os.open(
            name,
            os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
            dir_fd=fd,
        )
        try:
            for child in sorted(os.listdir(cfd)):
                _desc_rmtree(cfd, child)
        finally:
            os.close(cfd)
        os.rmdir(name, dir_fd=fd)
    elif stat.S_ISREG(st.st_mode):
        os.unlink(name, dir_fd=fd)
    else:
        raise HandoffClosed("cleanup special object rejected")


def _atomic_noreplace(parent_fd, source, destination):
    if sys.platform == "darwin":
        libname = ctypes.util.find_library("c")
        if libname is None:
            raise HandoffClosed("libc unavailable")
        libc = ctypes.CDLL(libname, use_errno=True)
        fn = getattr(libc, "renameatx_np", None)
        if fn is None:
            raise HandoffClosed("renameatx_np unavailable")
        fn.argtypes = [
            ctypes.c_int,
            ctypes.c_char_p,
            ctypes.c_int,
            ctypes.c_char_p,
            ctypes.c_uint,
        ]
        fn.restype = ctypes.c_int
        rc = fn(
            parent_fd,
            source.encode("utf-8"),
            parent_fd,
            destination.encode("utf-8"),
            0x4,
        )
    elif sys.platform.startswith("linux"):
        libname = ctypes.util.find_library("c")
        if libname is None:
            raise HandoffClosed("libc unavailable")
        libc = ctypes.CDLL(libname, use_errno=True)
        fn = getattr(libc, "renameat2", None)
        if fn is None:
            raise HandoffClosed("renameat2 unavailable")
        fn.argtypes = [
            ctypes.c_int,
            ctypes.c_char_p,
            ctypes.c_int,
            ctypes.c_char_p,
            ctypes.c_uint,
        ]
        fn.restype = ctypes.c_int
        rc = fn(
            parent_fd,
            source.encode("utf-8"),
            parent_fd,
            destination.encode("utf-8"),
            1,
        )
    else:
        raise HandoffClosed("unsupported publication platform")
    if rc != 0:
        err = ctypes.get_errno()
        if err == errno.EEXIST:
            raise HandoffClosed("runtime handoff destination already exists")
        raise HandoffClosed("atomic publication failed errno=%d" % err)


def _validate_header(header, args):
    expected_header_keys = {
        "schema", "purpose", "source_commit", "source_tree",
        "candidate_sha256", "transaction_v4_sha256", "contract_sha256",
        "manifest_sha256", "host_evidence_sha256", "receiver_sha256",
        "supplemental_runtime_artifact",
        "transaction_receipt_sha256", "source_owner_uid", "runtime_owner_uid",
        "lock_method", "lock_held_through_handoff",
        "external_noncooperating_writer_absence_proven",
        "file_count", "byte_count", "files",
    }
    if set(header) != expected_header_keys:
        raise HandoffClosed("header field set mismatch")

    exact = {
        "schema": SCHEMA,
        "purpose": PURPOSE,
        "candidate_sha256": args.expected_candidate_sha256,
        "transaction_v4_sha256": args.expected_transaction_sha256,
        "contract_sha256": args.expected_contract_sha256,
        "manifest_sha256": args.expected_manifest_sha256,
        "host_evidence_sha256": args.expected_host_evidence_sha256,
        "receiver_sha256": args.expected_receiver_sha256,
        "source_commit": args.expected_source_commit,
        "source_tree": args.expected_source_tree,
        "source_owner_uid": 599,
        "runtime_owner_uid": 501,
        "lock_method": "fcntl.flock_LOCK_EX_LOCK_NB",
        "lock_held_through_handoff": True,
        "external_noncooperating_writer_absence_proven": False,
    }
    for key, value in exact.items():
        if header.get(key) != value:
            raise HandoffClosed("header mismatch: %s" % key)

    supplemental = header.get("supplemental_runtime_artifact")
    expected_supplemental = {
        "source_path": args.expected_fortytwo_source_path,
        "source_commit": args.expected_fortytwo_source_commit,
        "source_tree": args.expected_fortytwo_source_tree,
        "handoff_destination": args.expected_fortytwo_destination,
        "sha256": args.expected_fortytwo_sha256,
        "bytes": args.expected_fortytwo_bytes,
        "mode": args.expected_fortytwo_mode,
        "nlink": 1,
        "canonical_manifest_member": False,
    }
    if supplemental != expected_supplemental:
        raise HandoffClosed("supplemental Fortytwo binding mismatch")
    for key in ("source_commit", "source_tree"):
        value = header.get(key)
        if (
            type(value) is not str
            or len(value) != 40
            or any(c not in "0123456789abcdef" for c in value)
        ):
            raise HandoffClosed("invalid source identity: %s" % key)
    if not _hex64(header.get("transaction_receipt_sha256")):
        raise HandoffClosed("invalid receipt SHA")
    files = header.get("files")
    if type(files) is not list:
        raise HandoffClosed("header files not list")
    if type(header.get("file_count")) is not int:
        raise HandoffClosed("header file count invalid")
    if header["file_count"] != len(files) or len(files) > MAX_FILE_COUNT:
        raise HandoffClosed("header file count mismatch")
    if type(header.get("byte_count")) is not int or header["byte_count"] < 0:
        raise HandoffClosed("header byte count invalid")

    paths = []
    byte_count = 0
    normalized = []
    expected_header_file_keys = {"path", "mode", "size", "sha256"}
    for item in files:
        if type(item) is not dict:
            raise HandoffClosed("header file record not object")
        if set(item) != expected_header_file_keys:
            raise HandoffClosed("header file record field set mismatch")
        rel = item.get("path")
        _validate_rel(rel)
        if type(item.get("size")) is not int or item["size"] < 0:
            raise HandoffClosed("header file size invalid")
        paths.append(rel)
        byte_count += item["size"]
        normalized.append((rel.encode("utf-8"), item))
    if byte_count != header["byte_count"]:
        raise HandoffClosed("header aggregate byte count mismatch")
    if len(paths) != len(set(paths)):
        raise HandoffClosed("duplicate header path")
    if files != [item for _, item in sorted(normalized, key=lambda x: x[0])]:
        raise HandoffClosed("header file ordering not canonical")

    path_set = set(paths)
    for rel in paths:
        parts = rel.split("/")
        for i in range(1, len(parts)):
            if "/".join(parts[:i]) in path_set:
                raise HandoffClosed("file prefix collision")

    transaction_receipt_records = [
        item for item in files
        if item.get("path") == "transaction-receipt.json"
    ]
    if len(transaction_receipt_records) != 1:
        raise HandoffClosed("transaction receipt file record cardinality mismatch")
    if (
        transaction_receipt_records[0].get("sha256")
        != header["transaction_receipt_sha256"]
    ):
        raise HandoffClosed("transaction receipt file SHA binding mismatch")

    supplemental_records = [
        item for item in files
        if item.get("path") == args.expected_fortytwo_destination
    ]
    if len(supplemental_records) != 1:
        raise HandoffClosed("supplemental Fortytwo file record cardinality mismatch")
    supplemental_record = supplemental_records[0]
    if supplemental_record != {
        "path": args.expected_fortytwo_destination,
        "mode": args.expected_fortytwo_mode,
        "size": args.expected_fortytwo_bytes,
        "sha256": args.expected_fortytwo_sha256,
    }:
        raise HandoffClosed("supplemental Fortytwo file record mismatch")

    return tuple(files)


def receive(args, stream):
    if os.geteuid() != 501:
        raise HandoffClosed("receiver EUID must be 501")

    parent_fd, parent_real = _open_private_parent(args.output_parent)
    stage_name = None
    published = False
    try:
        if (
            not args.final_basename
            or "/" in args.final_basename
            or "\\" in args.final_basename
            or args.final_basename in (".", "..")
        ):
            raise HandoffClosed("invalid final basename")
        try:
            os.lstat(args.final_basename, dir_fd=parent_fd)
        except OSError as exc:
            if exc.errno != errno.ENOENT:
                raise
        else:
            raise HandoffClosed("final destination exists")

        stage_name = ".wp4-v6-recv-%s" % next(tempfile._get_candidate_names())
        os.mkdir(stage_name, 0o700, dir_fd=parent_fd)
        stage_fd = os.open(
            stage_name,
            os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
            dir_fd=parent_fd,
        )
        try:
            digest = hashlib.sha256()
            magic = _read_exact(stream, len(MAGIC))
            if magic != MAGIC:
                raise HandoffClosed("handoff magic mismatch")
            digest.update(magic)

            header = _read_json_frame(stream, digest)
            header_files = _validate_header(header, args)

            seen = set()
            source_identities = set()
            received_bytes = 0
            expected_stream_file_keys = {
                "path", "mode", "size", "sha256", "source_dev", "source_inode"
            }
            for expected in header_files:
                meta = _read_json_frame(stream, digest)
                if set(meta) != expected_stream_file_keys:
                    raise HandoffClosed("stream file record field set mismatch")
                if {
                    k: meta.get(k)
                    for k in ("path", "mode", "size", "sha256")
                } != {
                    k: expected.get(k)
                    for k in ("path", "mode", "size", "sha256")
                }:
                    raise HandoffClosed("stream/header file record mismatch")
                rel = meta["path"]
                if rel in seen:
                    raise HandoffClosed("duplicate stream path")
                seen.add(rel)
                if (
                    type(meta["source_dev"]) is not int
                    or type(meta["source_inode"]) is not int
                    or meta["source_dev"] < 0
                    or meta["source_inode"] <= 0
                ):
                    raise HandoffClosed("source identity metadata invalid")
                source_identity = (meta["source_dev"], meta["source_inode"])
                if source_identity in source_identities:
                    raise HandoffClosed("source hardlink/identity alias")
                source_identities.add(source_identity)
                _write_received_file(stage_fd, meta, stream, digest)
                received_bytes += meta["size"]

            if seen != {x["path"] for x in header_files}:
                raise HandoffClosed("received path set mismatch")
            if received_bytes != header["byte_count"]:
                raise HandoffClosed("received byte total mismatch")

            if _read_exact(stream, 4) != END_MAGIC:
                raise HandoffClosed("terminal frame missing")
            footer_len = struct.unpack(">I", _read_exact(stream, 4))[0]
            if footer_len <= 0 or footer_len > MAX_JSON_FRAME:
                raise HandoffClosed("terminal frame length invalid")
            footer_raw = _read_exact(stream, footer_len)
            try:
                footer = json.loads(footer_raw.decode("utf-8"))
            except Exception as exc:
                raise HandoffClosed("terminal frame JSON invalid: %s" % exc)
            if type(footer) is not dict or footer_raw != _canonical_json(footer):
                raise HandoffClosed("terminal frame not canonical")
            exact_footer = {
                "schema": SCHEMA,
                "status": "COMPLETE",
                "stream_digest_sha256": digest.hexdigest(),
                "file_count": header["file_count"],
                "byte_count": header["byte_count"],
                "transaction_receipt_sha256":
                    header["transaction_receipt_sha256"],
                "private_transaction_cleanup": True,
                "authorized_root_posthandoff_empty": True,
                "lock_held_through_handoff": True,
                "lock_unlinked_identity_bound": True,
                "external_noncooperating_writer_absence_proven": False,
            }
            if footer != exact_footer:
                raise HandoffClosed("terminal frame fields mismatch")
            if stream.read(1) != b"":
                raise HandoffClosed("trailing bytes after terminal frame")

            receipt = {
                "receipt_schema": 1,
                "status": "V6_RUNTIME_MATERIAL_HANDOFF_ACCEPTED",
                "handoff_schema": PURPOSE,
                "source_commit": header["source_commit"],
                "source_tree": header["source_tree"],
                "candidate_sha256": header["candidate_sha256"],
                "transaction_v4_sha256": header["transaction_v4_sha256"],
                "contract_sha256": header["contract_sha256"],
                "manifest_sha256": header["manifest_sha256"],
                "host_evidence_sha256": header["host_evidence_sha256"],
                "receiver_sha256": header["receiver_sha256"],
                "supplemental_runtime_artifact":
                    header["supplemental_runtime_artifact"],
                "transaction_receipt_sha256":
                    header["transaction_receipt_sha256"],
                "stream_digest_sha256": digest.hexdigest(),
                "file_count": header["file_count"],
                "byte_count": header["byte_count"],
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
            receipt_raw = _canonical_json(receipt)
            rfd = os.open(
                RECEIVER_RECEIPT,
                os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                0o600,
                dir_fd=stage_fd,
            )
            try:
                os.write(rfd, receipt_raw)
                os.fsync(rfd)
            finally:
                os.close(rfd)
            receiver_receipt_sha = hashlib.sha256(receipt_raw).hexdigest()
            _fd_walk_fsync(stage_fd)
        finally:
            os.close(stage_fd)

        _atomic_noreplace(parent_fd, stage_name, args.final_basename)
        published = True
        os.fsync(parent_fd)
        stage_name = None

        final_path = os.path.join(parent_real, args.final_basename)
        print("V6_RUNTIME_MATERIAL_HANDOFF=PASS")
        print("V6_RUNTIME_MATERIAL_ROOT=" + final_path)
        print("V6_HANDOFF_RECEIVER_RECEIPT_SHA256=" + receiver_receipt_sha)
        return 0
    finally:
        if not published and stage_name is not None:
            try:
                _desc_rmtree(parent_fd, stage_name)
            except Exception:
                pass
        os.close(parent_fd)


def _build_selftest_stream():
    files = [
        {
            "path": "transaction-receipt.json",
            "mode": 0o644,
            "raw": b'{"synthetic":true}\n',
        },
        {
            "path": "workspaces/cfs/work/nos3/core-cpu1",
            "mode": 0o755,
            "raw": b"SYNTHETIC\n",
        },
        {
            "path": "fortytwo-runtime/42",
            "mode": 0o755,
            "raw": b"SYNTHETIC-FORTYTWO-42\n",
        },
    ]
    for f in files:
        f["size"] = len(f["raw"])
        f["sha256"] = hashlib.sha256(f["raw"]).hexdigest()
        f["source_dev"] = 1
        f["source_inode"] = 100 + len(f["path"])
    files.sort(key=lambda f: f["path"].encode("utf-8"))

    digest = hashlib.sha256()
    out = io.BytesIO()

    def write(raw):
        out.write(raw)
        digest.update(raw)

    def frame(obj):
        raw = _canonical_json(obj)
        write(struct.pack(">I", len(raw)))
        write(raw)

    write(MAGIC)
    receipt_file = next(
        f for f in files if f["path"] == "transaction-receipt.json"
    )
    receipt_sha = hashlib.sha256(receipt_file["raw"]).hexdigest()
    header = {
        "schema": 1,
        "purpose": PURPOSE,
        "source_commit": "1" * 40,
        "source_tree": "2" * 40,
        "candidate_sha256": "3" * 64,
        "transaction_v4_sha256": "4" * 64,
        "contract_sha256": "5" * 64,
        "manifest_sha256": "6" * 64,
        "host_evidence_sha256": "7" * 64,
        "receiver_sha256": "8" * 64,
        "supplemental_runtime_artifact": {
            "source_path": "external/fortytwo/42",
            "source_commit": "a" * 40,
            "source_tree": "b" * 40,
            "handoff_destination": "fortytwo-runtime/42",
            "sha256": hashlib.sha256(
                b"SYNTHETIC-FORTYTWO-42\n"
            ).hexdigest(),
            "bytes": len(b"SYNTHETIC-FORTYTWO-42\n"),
            "mode": 0o755,
            "nlink": 1,
            "canonical_manifest_member": False,
        },
        "transaction_receipt_sha256": receipt_sha,
        "source_owner_uid": 599,
        "runtime_owner_uid": 501,
        "lock_method": "fcntl.flock_LOCK_EX_LOCK_NB",
        "lock_held_through_handoff": True,
        "external_noncooperating_writer_absence_proven": False,
        "file_count": len(files),
        "byte_count": sum(f["size"] for f in files),
        "files": [
            {k: f[k] for k in ("path", "mode", "size", "sha256")}
            for f in files
        ],
    }
    frame(header)
    for f in files:
        frame(
            {
                k: f[k]
                for k in (
                    "path",
                    "mode",
                    "size",
                    "sha256",
                    "source_dev",
                    "source_inode",
                )
            }
        )
        write(f["raw"])
    footer = {
        "schema": 1,
        "status": "COMPLETE",
        "stream_digest_sha256": digest.hexdigest(),
        "file_count": header["file_count"],
        "byte_count": header["byte_count"],
        "transaction_receipt_sha256": receipt_sha,
        "private_transaction_cleanup": True,
        "authorized_root_posthandoff_empty": True,
        "lock_held_through_handoff": True,
        "lock_unlinked_identity_bound": True,
        "external_noncooperating_writer_absence_proven": False,
    }
    raw = _canonical_json(footer)
    out.write(END_MAGIC)
    out.write(struct.pack(">I", len(raw)))
    out.write(raw)
    out.seek(0)
    return out


def _mutate_stream(mutator):
    files = [
        {"path": "transaction-receipt.json", "mode": 0o644,
         "raw": b'{"synthetic":true}\n'},
        {"path": "workspaces/cfs/work/nos3/core-cpu1", "mode": 0o755,
         "raw": b"SYNTHETIC\n"},
        {"path": "fortytwo-runtime/42", "mode": 0o755,
         "raw": b"SYNTHETIC-FORTYTWO-42\n"},
    ]
    state = {
        "files": files,
        "header_overrides": {},
        "meta_overrides": {},
        "wire_raw_overrides": {},
        "footer_overrides": {},
        "omit_footer": False,
        "trailing": b"",
    }
    mutator(state)
    for f in files:
        f["size"] = len(f["raw"])
        f["sha256"] = hashlib.sha256(f["raw"]).hexdigest()
        f.setdefault("source_dev", 1)
        f.setdefault("source_inode", 100 + len(f["path"]))
    files.sort(key=lambda f: f["path"].encode("utf-8"))

    digest = hashlib.sha256()
    out = io.BytesIO()

    def write(raw):
        out.write(raw)
        digest.update(raw)

    def frame(obj):
        raw = _canonical_json(obj)
        write(struct.pack(">I", len(raw)))
        write(raw)

    write(MAGIC)
    receipt = next((f for f in files if f["path"] == "transaction-receipt.json"), None)
    receipt_sha = (
        hashlib.sha256(receipt["raw"]).hexdigest()
        if receipt is not None else "9" * 64
    )
    header = {
        "schema": 1,
        "purpose": PURPOSE,
        "source_commit": "1" * 40,
        "source_tree": "2" * 40,
        "candidate_sha256": "3" * 64,
        "transaction_v4_sha256": "4" * 64,
        "contract_sha256": "5" * 64,
        "manifest_sha256": "6" * 64,
        "host_evidence_sha256": "7" * 64,
        "receiver_sha256": "8" * 64,
        "supplemental_runtime_artifact": {
            "source_path": "external/fortytwo/42",
            "source_commit": "a" * 40,
            "source_tree": "b" * 40,
            "handoff_destination": "fortytwo-runtime/42",
            "sha256": hashlib.sha256(
                b"SYNTHETIC-FORTYTWO-42\n"
            ).hexdigest(),
            "bytes": len(b"SYNTHETIC-FORTYTWO-42\n"),
            "mode": 0o755,
            "nlink": 1,
            "canonical_manifest_member": False,
        },
        "transaction_receipt_sha256": receipt_sha,
        "source_owner_uid": 599,
        "runtime_owner_uid": 501,
        "lock_method": "fcntl.flock_LOCK_EX_LOCK_NB",
        "lock_held_through_handoff": True,
        "external_noncooperating_writer_absence_proven": False,
        "file_count": len(files),
        "byte_count": sum(f["size"] for f in files),
        "files": [
            {k: f[k] for k in ("path", "mode", "size", "sha256")}
            for f in files
        ],
    }
    header.update(state["header_overrides"])
    frame(header)
    for f in files:
        meta = {
            k: f[k] for k in (
                "path", "mode", "size", "sha256", "source_dev", "source_inode"
            )
        }
        meta.update(state["meta_overrides"].get(f["path"], {}))
        frame(meta)
        write(state["wire_raw_overrides"].get(f["path"], f["raw"]))

    if not state["omit_footer"]:
        footer = {
            "schema": 1,
            "status": "COMPLETE",
            "stream_digest_sha256": digest.hexdigest(),
            "file_count": header["file_count"],
            "byte_count": header["byte_count"],
            "transaction_receipt_sha256": header["transaction_receipt_sha256"],
            "private_transaction_cleanup": True,
            "authorized_root_posthandoff_empty": True,
            "lock_held_through_handoff": True,
            "lock_unlinked_identity_bound": True,
            "external_noncooperating_writer_absence_proven": False,
        }
        footer.update(state["footer_overrides"])
        raw = _canonical_json(footer)
        out.write(END_MAGIC)
        out.write(struct.pack(">I", len(raw)))
        out.write(raw)
    out.write(state["trailing"])
    out.seek(0)
    return out


def _selftest_args(parent, final_basename):
    return argparse.Namespace(
        output_parent=parent,
        final_basename=final_basename,
        expected_candidate_sha256="3" * 64,
        expected_transaction_sha256="4" * 64,
        expected_contract_sha256="5" * 64,
        expected_manifest_sha256="6" * 64,
        expected_host_evidence_sha256="7" * 64,
        expected_receiver_sha256="8" * 64,
        expected_source_commit="1" * 40,
        expected_source_tree="2" * 40,
        expected_fortytwo_source_path="external/fortytwo/42",
        expected_fortytwo_source_commit="a" * 40,
        expected_fortytwo_source_tree="b" * 40,
        expected_fortytwo_destination="fortytwo-runtime/42",
        expected_fortytwo_sha256=hashlib.sha256(
            b"SYNTHETIC-FORTYTWO-42\n"
        ).hexdigest(),
        expected_fortytwo_bytes=len(b"SYNTHETIC-FORTYTWO-42\n"),
        expected_fortytwo_mode=0o755,
    )


def _expect_reject(parent, name, stream):
    failed = False
    try:
        receive(_selftest_args(parent, name), stream)
    except HandoffClosed:
        failed = True
    if not failed:
        raise HandoffClosed("negative case accepted: " + name)
    if os.path.exists(os.path.join(parent, name)):
        raise HandoffClosed("negative case published output: " + name)
    print("receiver_negative_" + name + "=PASS")


def selftest():
    if os.geteuid() != 501:
        print("V6_RECEIVER_SELFTEST=SKIP_UID_NOT_501")
        return 0
    parent = tempfile.mkdtemp(
        prefix="wp4-d064-v6-receiver-selftest-",
        dir=os.path.realpath(tempfile.gettempdir()),
    )
    os.chmod(parent, 0o700)
    try:
        rc = receive(_selftest_args(parent, "accepted"), _build_selftest_stream())
        if rc != 0:
            raise HandoffClosed("selftest valid receive failed")
        final = os.path.join(parent, "accepted")
        if not os.path.isfile(os.path.join(final, RECEIVER_RECEIPT)):
            raise HandoffClosed("selftest receiver receipt absent")

        valid = _build_selftest_stream().read()
        _expect_reject(parent, "truncated", io.BytesIO(valid[:-20]))
        _expect_reject(
            parent, "duplicate_path",
            _mutate_stream(lambda s: s["files"].append(
                {"path": "transaction-receipt.json", "mode": 0o644,
                 "raw": b"DUPLICATE\n"})))
        _expect_reject(
            parent, "path_traversal",
            _mutate_stream(lambda s: s["files"].append(
                {"path": "../escape", "mode": 0o600, "raw": b"ESCAPE\n"})))
        _expect_reject(
            parent, "prefix_collision",
            _mutate_stream(lambda s: s["files"].extend([
                {"path": "prefix", "mode": 0o600, "raw": b"A\n"},
                {"path": "prefix/child", "mode": 0o600, "raw": b"B\n"},
            ])))
        def bad_hash(state):
            target = state["files"][1]["path"]
            state["wire_raw_overrides"][target] = b"XXXXXXXXX\n"
        _expect_reject(parent, "hash_mismatch", _mutate_stream(bad_hash))
        _expect_reject(
            parent, "file_count_mismatch",
            _mutate_stream(lambda s: s["header_overrides"].update({"file_count": 99})))
        _expect_reject(
            parent, "byte_count_mismatch",
            _mutate_stream(lambda s: s["header_overrides"].update({"byte_count": 1})))
        _expect_reject(
            parent, "stream_digest_mismatch",
            _mutate_stream(lambda s: s["footer_overrides"].update(
                {"stream_digest_sha256": "0" * 64})))
        _expect_reject(
            parent, "cleanup_flag_false",
            _mutate_stream(lambda s: s["footer_overrides"].update(
                {"private_transaction_cleanup": False})))
        _expect_reject(
            parent, "trailing_bytes",
            _mutate_stream(lambda s: s.update({"trailing": b"X"})))
        def special_semantic(state):
            target = state["files"][1]["path"]
            state["meta_overrides"][target] = {"object_type": "symlink"}
        _expect_reject(parent, "special_semantic", _mutate_stream(special_semantic))
        def hardlink_alias(state):
            first = state["files"][0]
            second = state["files"][1]
            first_inode = 100 + len(first["path"])
            state["meta_overrides"][second["path"]] = {
                "source_dev": 1,
                "source_inode": first_inode,
            }
        _expect_reject(
            parent, "source_hardlink_alias", _mutate_stream(hardlink_alias))
        _expect_reject(
            parent, "source_commit_mismatch",
            _mutate_stream(lambda s: s["header_overrides"].update(
                {"source_commit": "f" * 40})))
        _expect_reject(
            parent, "source_tree_mismatch",
            _mutate_stream(lambda s: s["header_overrides"].update(
                {"source_tree": "e" * 40})))
        _expect_reject(
            parent, "receiver_sha_mismatch",
            _mutate_stream(lambda s: s["header_overrides"].update(
                {"receiver_sha256": "d" * 64})))

        def supplemental_binding_mismatch(state):
            state["header_overrides"]["supplemental_runtime_artifact"] = {
                "source_path": "external/fortytwo/42",
                "source_commit": "a" * 40,
                "source_tree": "b" * 40,
                "handoff_destination": "fortytwo-runtime/42",
                "sha256": "c" * 64,
                "bytes": len(b"SYNTHETIC-FORTYTWO-42\n"),
                "mode": 0o755,
                "nlink": 1,
                "canonical_manifest_member": False,
            }
        _expect_reject(
            parent, "supplemental_binding_mismatch",
            _mutate_stream(supplemental_binding_mismatch))

        def supplemental_record_mismatch(state):
            state["meta_overrides"]["fortytwo-runtime/42"] = {
                "mode": 0o600
            }
        _expect_reject(
            parent, "supplemental_record_mismatch",
            _mutate_stream(supplemental_record_mismatch))

        print("V6_RECEIVER_SELFTEST=PASS")
        print("receiver_negative_case_count=17")
        return 0
    finally:
        pfd = os.open(parent, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        try:
            for name in list(os.listdir(pfd)):
                _desc_rmtree(pfd, name)
        finally:
            os.close(pfd)
        os.rmdir(parent)

def build_parser():
    p = argparse.ArgumentParser()
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--receive", action="store_true")
    g.add_argument("--selftest", action="store_true")
    p.add_argument("--output-parent")
    p.add_argument("--final-basename")
    p.add_argument("--expected-candidate-sha256")
    p.add_argument("--expected-transaction-sha256")
    p.add_argument("--expected-contract-sha256")
    p.add_argument("--expected-manifest-sha256")
    p.add_argument("--expected-host-evidence-sha256")
    p.add_argument("--expected-receiver-sha256")
    p.add_argument("--expected-source-commit")
    p.add_argument("--expected-source-tree")
    p.add_argument("--expected-fortytwo-source-path")
    p.add_argument("--expected-fortytwo-source-commit")
    p.add_argument("--expected-fortytwo-source-tree")
    p.add_argument("--expected-fortytwo-destination")
    p.add_argument("--expected-fortytwo-sha256")
    p.add_argument("--expected-fortytwo-bytes", type=int)
    p.add_argument("--expected-fortytwo-mode", type=lambda x: int(x, 8))
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    if args.selftest:
        return selftest()
    for name in (
        "output_parent",
        "final_basename",
        "expected_candidate_sha256",
        "expected_transaction_sha256",
        "expected_contract_sha256",
        "expected_manifest_sha256",
        "expected_host_evidence_sha256",
        "expected_receiver_sha256",
        "expected_source_commit",
        "expected_source_tree",
        "expected_fortytwo_source_path",
        "expected_fortytwo_source_commit",
        "expected_fortytwo_source_tree",
        "expected_fortytwo_destination",
        "expected_fortytwo_sha256",
        "expected_fortytwo_bytes",
        "expected_fortytwo_mode",
    ):
        if not getattr(args, name):
            print("[ERROR] missing argument: " + name, file=sys.stderr)
            return 1
    for name in (
        "expected_candidate_sha256",
        "expected_transaction_sha256",
        "expected_contract_sha256",
        "expected_manifest_sha256",
        "expected_host_evidence_sha256",
        "expected_receiver_sha256",
        "expected_fortytwo_sha256",
    ):
        if not _hex64(getattr(args, name)):
            print("[ERROR] malformed expected SHA: " + name, file=sys.stderr)
            return 1
    for name in (
        "expected_source_commit",
        "expected_source_tree",
        "expected_fortytwo_source_commit",
        "expected_fortytwo_source_tree",
    ):
        value = getattr(args, name)
        if (
            type(value) is not str
            or len(value) != 40
            or any(c not in "0123456789abcdef" for c in value)
        ):
            print("[ERROR] malformed expected Git identity: " + name, file=sys.stderr)
            return 1
    if args.expected_fortytwo_source_path != "external/fortytwo/42":
        print("[ERROR] supplemental Fortytwo source path mismatch", file=sys.stderr)
        return 1
    if args.expected_fortytwo_destination != "fortytwo-runtime/42":
        print("[ERROR] supplemental Fortytwo destination mismatch", file=sys.stderr)
        return 1
    if (
        type(args.expected_fortytwo_bytes) is not int
        or args.expected_fortytwo_bytes <= 0
        or type(args.expected_fortytwo_mode) is not int
        or args.expected_fortytwo_mode != 0o755
    ):
        print("[ERROR] supplemental Fortytwo size/mode invalid", file=sys.stderr)
        return 1
    try:
        return receive(args, sys.stdin.buffer)
    except HandoffClosed as exc:
        print("V6_RUNTIME_MATERIAL_HANDOFF=CLOSED", file=sys.stderr)
        print("[ERROR] " + str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
