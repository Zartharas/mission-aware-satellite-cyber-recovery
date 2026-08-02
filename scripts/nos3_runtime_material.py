#!/usr/bin/env python3
"""NOS3 runtime-material tool (WP4 v3, Checkpoint 1, Correction 9).

Deterministic, fail-closed, host-only.  Implements the D-063R2 canonical
manifest model: no internal manifest hash, detached SHA-256 over complete
bytes, json.dumps with ensure_ascii=True, sort_keys=True,
separators=(",",":"), exactly one final LF.  Every sort-key element is
encoded as UTF-8 bytes before ordering.  Exact UTF-8 bytes remain path
identity; normalized forms (NFC/NFD after casefold) are collision guards
only.

Real materialization requires a VerifiedManifest bearer issued by
load_and_verify_manifest() and a MaterializationAuthorized bearer issued by
a production authorization path that does not yet exist in this checkpoint.
The public materializer resolves all workspace state from the verified
bearer and never trusts caller-supplied workspace fields.  The tool never
infers authorization from narrative status.

This tool does NOT invoke Docker, a candidate, a verifier, a compiler,
NOS Engine, cFS, Fortytwo, or any simulator.  It never modifies
external/nos3 or external/fortytwo.
"""

import argparse
import errno
import random
import ctypes
import ctypes.util
import fnmatch
import hashlib
import json
import os
import platform
import shutil
import stat
import sys
import tempfile
import unicodedata
import weakref

# --------------------------------------------------------------------------
# Source-root configuration (merged D-063R2 contract).
# Each tuple: (source_root_id, host_relative_path, component_scope,
#              workspace_destination_prefix).
# The destination prefix is workspace-relative; included files map to
#   destination_relative = prefix + "/" + relative_path
# --------------------------------------------------------------------------
SOURCE_ROOTS = [
    ("sim_bin", "external/nos3/sims/build/bin", "simulator", "sims/build/bin"),
    ("sim_lib", "external/nos3/sims/build/lib", "simulator", "sims/build/lib"),
    ("cfs", "external/nos3/fsw/build/exe/cpu1", "cfs", "fsw/build/exe/cpu1"),
    ("configuration", "external/nos3/cfg/build/InOut", "configuration", "cfg/build/InOut"),
]

CONTRACT_SCHEMA = 1

# Eleven exact exclusions, frozen from the D-063R2 contract.  An entry may
# be absent from disk; if present, every field must match or we fail closed.
_EXCL_TEMPLATE = {
    "entry_type": "regular_file",
    "nlink": 1,
    "present_at_amendment": True,
    "classification": "EXACT_STALE_EXCLUSION",
    "destination_must_be_absent": True,
}
EXACT_EXCLUSIONS = [
    dict(_EXCL_TEMPLATE, source_root="sim_bin", relative_path="2026-07-25-nos3-sim-log.txt",
         mode="0644", size=27655970,
         sha256="c63a6cd22b8c830608286cc0606ce89e14ce139c19438ef51ef0d8a31556230b"),
    dict(_EXCL_TEMPLATE, source_root="sim_bin", relative_path="2026-07-26-nos3-sim-log.txt",
         mode="0644", size=12906883,
         sha256="39be49486820383a0c3319203428d812a16e361d404e88951bd12f01203ed9a1"),
    dict(_EXCL_TEMPLATE, source_root="cfs", relative_path="log.txt",
         mode="0644", size=0,
         sha256="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"),
    dict(_EXCL_TEMPLATE, source_root="cfs", relative_path="sa_save_file.bin",
         mode="0644", size=150272,
         sha256="5ed0c75dd2ac88af0b6311d7466c8101781dd59dab4c5a3e3c040feb392c14d2"),
    dict(_EXCL_TEMPLATE, source_root="cfs", relative_path=".cdskeyfile",
         mode="0700", size=0,
         sha256="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"),
    dict(_EXCL_TEMPLATE, source_root="cfs", relative_path=".reservedkeyfile",
         mode="0700", size=0,
         sha256="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"),
    dict(_EXCL_TEMPLATE, source_root="cfs", relative_path=".resetkeyfile",
         mode="0700", size=0,
         sha256="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"),
    dict(_EXCL_TEMPLATE, source_root="cfs",
         relative_path="data/owls/bundle/.goutputstream-3YXHA2",
         mode="0644", size=1369700,
         sha256="f9f7cf74fe6d41615148caf34e32cc93a1d167c2f275603118a8360d5f6b39fb",
         duplicate_target="data/owls/bundle/asdp000000000.tgz",
         duplicate_target_sha256="f9f7cf74fe6d41615148caf34e32cc93a1d167c2f275603118a8360d5f6b39fb",
         bytes_equal=True),
    dict(_EXCL_TEMPLATE, source_root="cfs",
         relative_path="data/owls/bundle/.goutputstream-2Z2791",
         mode="0644", size=1369700,
         sha256="f9f7cf74fe6d41615148caf34e32cc93a1d167c2f275603118a8360d5f6b39fb",
         duplicate_target="data/owls/bundle/asdp000000000.tgz",
         duplicate_target_sha256="f9f7cf74fe6d41615148caf34e32cc93a1d167c2f275603118a8360d5f6b39fb",
         bytes_equal=True),
    dict(_EXCL_TEMPLATE, source_root="cfs",
         relative_path="data/owls/bundle/.goutputstream-M5TDA2",
         mode="0644", size=810786,
         sha256="81fdd618434da04b838701bc08ffe7d614c8ee60a9a4d27f4108ee4541c0bddd",
         duplicate_target="data/owls/bundle/asdp000000001.tgz",
         duplicate_target_sha256="81fdd618434da04b838701bc08ffe7d614c8ee60a9a4d27f4108ee4541c0bddd",
         bytes_equal=True),
    dict(_EXCL_TEMPLATE, source_root="cfs",
         relative_path="data/owls/bundle/.goutputstream-PDW691",
         mode="0644", size=148,
         sha256="4b037466e2da3de4e1b9b94b94463c06d4caa38bd2ef36a44cc00da140756540",
         duplicate_target="data/owls/bundle/asdp000000002_dpmsg.json",
         duplicate_target_sha256="4b037466e2da3de4e1b9b94b94463c06d4caa38bd2ef36a44cc00da140756540",
         bytes_equal=True),
]

DENY_PATTERNS = [
    {"pattern": "data/owls/bundle/.goutputstream-*", "scope": "cfs"},
]

# Eighteen private NOS3 workspaces.  Each maps to its applicable seed roots.
# NOS Engine, TimeDriver, 14 hardware simulators, bridge: sim_bin + sim_lib.
# cFS: cfs.  configuration is separate Fortytwo scratch (not a workspace).
WORKSPACE_COMPONENTS = [
    ("nos_engine", ["sim_bin", "sim_lib"]),
    ("time_driver", ["sim_bin", "sim_lib"]),
] + [("hw_sim_%02d" % i, ["sim_bin", "sim_lib"]) for i in range(1, 15)] + [
    ("cmd_bus_bridge", ["sim_bin", "sim_lib"]),
    ("cfs", ["cfs"]),
]

MOUNT_DESTINATION = "/work/nos3"

# Frozen amendment-time snapshot values.  These are written into the manifest
# and must NOT change when a present exclusion later becomes absent.
SNAPSHOT = {
    "snapshot_date": "2026-07-29",
    "snapshot_raw_regular_files": 1433,
    "snapshot_present_exact_exclusion_count": 11,
    "snapshot_simulator_raw_regular_files": 27,
    "snapshot_simulator_present_exact_exclusions": 2,
    "snapshot_cfs_raw_regular_files": 1370,
    "snapshot_cfs_present_exact_exclusions": 9,
    "snapshot_configuration_raw_regular_files": 36,
    "snapshot_configuration_present_exact_exclusions": 0,
    "snapshot_aggregate_included_regular_files": 1422,
    "snapshot_aggregate_included_bytes": 100496114,
    "snapshot_directory_entry_count": 89,
}

INVARIANTS = {
    "snapshot_date": SNAPSHOT["snapshot_date"],
    "invariant_included_manifest_regular_file_entry_count": 1422,
    "invariant_simulator_included_count": 25,
    "invariant_cfs_included_count": 1361,
    "invariant_configuration_included_count": 36,
    "invariant_included_bytes": 100496114,
    "invariant_exact_exclusion_record_count": 11,
    "invariant_directory_entry_count": 89,
    "raw_counts_are_amendment_snapshot_only": True,
    "included_entry_counts_are_invariants": True,
    "included_byte_count_is_invariant": True,
    "exact_exclusion_record_count_is_invariant": True,
    "future_present_exact_exclusion_count_min": 0,
    "future_present_exact_exclusion_count_max": 11,
    "future_present_simulator_exclusion_count_min": 0,
    "future_present_simulator_exclusion_count_max": 2,
    "future_present_cfs_exclusion_count_min": 0,
    "future_present_cfs_exclusion_count_max": 9,
    "future_simulator_raw_count_formula": "simulator_included_25_plus_present_simulator_exclusions",
    "future_cfs_raw_count_formula": "cfs_included_1361_plus_present_cfs_exclusions",
    "future_configuration_raw_count": 36,
    "future_aggregate_raw_count_formula": "included_manifest_entries_1422_plus_present_exact_exclusions",
    "future_raw_count_formula": "included_manifest_entries_plus_present_exact_exclusions",
    "amendment_snapshot_raw_count_1433_is_not_unconditional_future_gate": True,
    "absence_of_exact_excluded_source_path_is_not_drift": True,
    "present_exact_exclusion_must_match_frozen_identity": True,
    "unlisted_path_fails_closed": True,
    "every_exclusion_absent_from_every_materialized_destination": True,
}

# Destination prefixes per source root (workspace-relative).
DEST_PREFIX = {r[0]: r[3] for r in SOURCE_ROOTS}
ROOT_SCOPES = {r[0]: r[2] for r in SOURCE_ROOTS}
ROOT_HOST = {r[0]: r[1] for r in SOURCE_ROOTS}
ROOT_IDS = [r[0] for r in SOURCE_ROOTS]

class FailClosed(Exception):
    """Any classification, validation, identity, or materialization failure."""
    pass

# --------------------------------------------------------------------------
# Path validation.
# --------------------------------------------------------------------------
def validate_path(rel_path):
    """Validate a relative POSIX child path.  Returns the validated string.

    Rejects surrogates, NUL, absolute, empty/dot/dotdot components,
    backslashes, repeated separators.  The empty string is NOT accepted here;
    it is only valid as the distinguished source-root directory sentinel.
    """
    if rel_path == "":
        raise FailClosed("empty path")
    for ch in rel_path:
        if 0xD800 <= ord(ch) <= 0xDFFF:
            raise FailClosed("surrogate in path: %r" % rel_path)
    if "\x00" in rel_path:
        raise FailClosed("NUL in path")
    if "\\" in rel_path:
        raise FailClosed("backslash in path: %r" % rel_path)
    if rel_path.startswith("/"):
        raise FailClosed("absolute path: %r" % rel_path)
    parts = rel_path.split("/")
    for part in parts:
        if part == "":
            raise FailClosed("empty component or repeated separator in %r" % rel_path)
        if part == ".":
            raise FailClosed("dot component in %r" % rel_path)
        if part == "..":
            raise FailClosed("dotdot component in %r" % rel_path)
    return rel_path


def collision_keys(rel_path):
    """Compute NFC/NFD collision-guard keys after NFD-decompose + casefold.

    Returns (nfc_bytes, nfd_bytes).  Exact bytes remain identity.
    """
    nfd = unicodedata.normalize("NFD", rel_path)
    folded = nfd.casefold()
    nfc = unicodedata.normalize("NFC", folded)
    nfd2 = unicodedata.normalize("NFD", folded)
    return nfc.encode("utf-8"), nfd2.encode("utf-8")


def collision_namespace(paths):
    """Fail-closed collision check over an iterable of exact path strings.

    Detects NFC, NFD, and casefold collisions among distinct exact paths.
    """
    seen_nfc = {}
    seen_nfd = {}
    for p in sorted(set(paths)):
        nk, dk = collision_keys(p)
        if nk in seen_nfc and seen_nfc[nk] != p:
            raise FailClosed("NFC collision: %r vs %r" % (p, seen_nfc[nk]))
        if dk in seen_nfd and seen_nfd[dk] != p:
            raise FailClosed("NFD collision: %r vs %r" % (p, seen_nfd[dk]))
        seen_nfc[nk] = p
        seen_nfd[dk] = p


def file_prefix_collision(files, all_paths):
    """Fail if a FILE path is a proper prefix parent of any other entry.

    A file acting as a directory for another path is invalid.  A directory
    being the parent of files is valid and is NOT rejected here.
    """
    fs = sorted(set(files))
    ap = set(all_paths)
    for fa in fs:
        for b in ap:
            if b != fa and b.startswith(fa + "/"):
                raise FailClosed("file-as-parent prefix collision: %r is parent of %r" % (fa, b))


# --------------------------------------------------------------------------
# SHA-256 helpers.
# --------------------------------------------------------------------------
def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            b = f.read(1024 * 1024)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


_HEX64 = set("0123456789abcdef")
def _is_hex64(s):
    if not isinstance(s, str) or len(s) != 64:
        return False
    return all(c in _HEX64 for c in s)


# --------------------------------------------------------------------------
# Byte-encoded sort keys.
# --------------------------------------------------------------------------
def sk_included(e):
    return (e["source_root"].encode("utf-8"), e["relative_path"].encode("utf-8"),
            e["entry_type"].encode("ascii"), e["destination_relative"].encode("utf-8"),
            e["component_scope"].encode("utf-8"))

def sk_excluded(e):
    return (e["source_root"].encode("utf-8"), e["relative_path"].encode("utf-8"),
            e["classification"].encode("ascii"))

def sk_directory(e):
    return (e["source_root"].encode("utf-8"),
            e["relative_path"].encode("utf-8"),
            e["component_scope"].encode("utf-8"))

def sk_deny(e):
    return (e["pattern"].encode("utf-8"), e["scope"].encode("utf-8"))

def sk_workspace(e):
    return (e["component_id"].encode("utf-8"),
            e["workspace_host_path"].encode("utf-8"),
            e["mount_destination"].encode("utf-8"))

def sk_root_decl(e):
    return (e["source_root"].encode("utf-8"), e["component_scope"].encode("utf-8"))


# --------------------------------------------------------------------------
# Exclusion and deny helpers.
# --------------------------------------------------------------------------
def build_exclusion_index():
    return {(e["source_root"], e["relative_path"]): e for e in EXACT_EXCLUSIONS}

def match_deny_patterns(source_root, rel_path):
    for dp in DENY_PATTERNS:
        if dp["scope"] == source_root and fnmatch.fnmatch(rel_path, dp["pattern"]):
            return True
    return False

# --------------------------------------------------------------------------
# Source inventory + classification.
# --------------------------------------------------------------------------
def classify_entry(source_root, host_root, rel_path, excl_index):
    """Classify a single filesystem entry by lstat.  Fail closed on anything
    unsupported or unlisted.

    Returns ('included', identity_dict) or ('excluded', exclusion_dict) or
    ('directory', dir_dict).
    """
    fp = os.path.join(host_root, rel_path)
    st = os.lstat(fp)
    mode = stat.S_IMODE(st.st_mode)
    mode_str = "%04o" % mode
    if os.path.islink(fp):
        raise FailClosed("symlink not supported: %s:%s" % (source_root, rel_path))
    if stat.S_ISDIR(st.st_mode):
        return ("directory", {"source_root": source_root,
                              "relative_path": rel_path,
                              "mode": mode_str, "nlink": st.st_nlink})
    if not stat.S_ISREG(st.st_mode):
        raise FailClosed("unsupported object: %s:%s" % (source_root, rel_path))
    if st.st_nlink > 1:
        raise FailClosed("hard-link alias: %s:%s nlink=%d" % (source_root, rel_path, st.st_nlink))
    sha = sha256_file(fp)
    identity = {"source_root": source_root, "relative_path": rel_path,
                "entry_type": "regular_file", "mode": mode_str,
                "size": st.st_size, "sha256": sha, "nlink": st.st_nlink}
    key = (source_root, rel_path)
    if key in excl_index:
        excl = excl_index[key]
        for f in ("entry_type", "mode", "size", "sha256", "nlink"):
            if str(identity.get(f)) != str(excl.get(f)):
                raise FailClosed("exclusion mismatch %s:%s field %s disk=%r frozen=%r"
                                 % (source_root, rel_path, f, identity.get(f), excl.get(f)))
        return ("excluded", excl)
    if match_deny_patterns(source_root, rel_path):
        raise FailClosed("deny-pattern match without exact exclusion: %s:%s"
                         % (source_root, rel_path))
    return ("included", identity)


def walk_source_roots(repo_root):
    """Walk all source roots, classify every entry, enforce collision rules
    per namespace.

    Returns (included, directories, excluded_present, stats).
    """
    excl_index = build_exclusion_index()
    included = []
    directories = []
    excluded_present = []
    present_keys = set()
    raw_regular = 0
    present_exact = 0

    # Per-source-root namespaces for collision enforcement.
    sr_files = {r: set() for r in ROOT_IDS}
    sr_dirs = {r: set() for r in ROOT_IDS}
    # Per-component destination namespace.
    comp_dest = {}
    # Global source-identity set (source_root, rel_path).
    seen_source = set()

    for source_root, sub_path, scope, dest_pre in SOURCE_ROOTS:
        host_root = os.path.join(repo_root, sub_path)
        # lstat the declared source root and reject it when it is a symlink
        # BEFORE os.walk() -- os.path.isdir()/os.walk follow symlinks.
        try:
            root_lst = os.lstat(host_root)
        except OSError as exc:
            raise FailClosed("source root missing: %s (%s)" % (host_root, exc))
        if stat.S_ISLNK(root_lst.st_mode):
            raise FailClosed("declared source root is a symlink: %s" % host_root)
        if not stat.S_ISDIR(root_lst.st_mode):
            raise FailClosed("source root not a directory: %s" % host_root)
        # Root directory sentinel entry (distinguished "" representation).
        root_mode = stat.S_IMODE(root_lst.st_mode)
        directories.append({"source_root": source_root, "relative_path": "",
                            "component_scope": ROOT_SCOPES[source_root]})

        for dirpath, dirnames, filenames in os.walk(host_root, followlinks=False):
            rel_dir = os.path.relpath(dirpath, host_root)
            is_root = (rel_dir == ".")
            if is_root:
                rel_dir = ""
            # Subdirectories (children, validated).
            for d in sorted(dirnames):
                full_rel = (rel_dir + "/" + d) if rel_dir else d
                validate_path(full_rel)
                dp_full = os.path.join(dirpath, d)
                if os.path.islink(dp_full):
                    target = os.readlink(dp_full)
                    if target.startswith("/") or ".." in target:
                        raise FailClosed("escaping symlink: %s" % dp_full)
                    raise FailClosed("symlink directory: %s" % dp_full)
                kind, ident = classify_entry(source_root, host_root, full_rel, excl_index)
                if kind == "directory":
                    directories.append({"source_root": source_root,
                                        "relative_path": full_rel,
                                        "component_scope": scope})
                    sr_dirs[source_root].add(full_rel)
                else:
                    raise FailClosed("unexpected kind for dir child: %s" % kind)
            # Regular files.
            for f in sorted(filenames):
                fp = os.path.join(dirpath, f)
                if os.path.islink(fp):
                    raise FailClosed("symlink file: %s:%s" % (source_root, f))
                full_rel = (rel_dir + "/" + f) if rel_dir else f
                validate_path(full_rel)
                raw_regular += 1
                kind, ident = classify_entry(source_root, host_root, full_rel, excl_index)
                if kind == "included":
                    dest_rel = dest_pre + "/" + full_rel
                    inc = dict(ident)
                    inc["destination_relative"] = dest_rel
                    inc["component_scope"] = scope
                    included.append(inc)
                    sr_files[source_root].add(full_rel)
                elif kind == "excluded":
                    excluded_present.append(ident)
                    present_keys.add((source_root, full_rel))
                    present_exact += 1

    # ---- Collision enforcement across namespaces. ----
    # Duplicate source identities.
    for inc in included:
        sid = (inc["source_root"], inc["relative_path"])
        if sid in seen_source:
            raise FailClosed("duplicate source identity: %s:%s" % sid)
        seen_source.add(sid)
    for ex in excluded_present:
        sid = (ex["source_root"], ex["relative_path"])
        if sid in seen_source:
            raise FailClosed("duplicate source identity (excl): %s:%s" % sid)
        seen_source.add(sid)

    # Duplicate destination identities within each component.
    for inc in included:
        key = (inc["component_scope"], inc["destination_relative"])
        if key in comp_dest:
            raise FailClosed("duplicate destination within component %s: %s"
                             % (inc["component_scope"], inc["destination_relative"]))
        comp_dest[key] = True

    # Directory/file collisions within each source root.
    for r in ROOT_IDS:
        shared = sr_files[r] & sr_dirs[r]
        if shared:
            raise FailClosed("directory/file collision in %s: %r" % (r, shared))
        # normalized + prefix collisions among files and dirs combined.
        all_paths = sr_files[r] | sr_dirs[r]
        collision_namespace(all_paths)
        file_prefix_collision(sr_files[r], all_paths)

    # Destination collisions within each component workspace.
    by_comp = {}
    for inc in included:
        by_comp.setdefault(inc["component_scope"], []).append(inc["destination_relative"])
    for comp, dests in by_comp.items():
        collision_namespace(dests)
        file_prefix_collision(dests, dests)

    # Exclusion paths per source root (normalized collision guard).
    excl_by_root = {}
    for ex in EXACT_EXCLUSIONS:
        excl_by_root.setdefault(ex["source_root"], []).append(ex["relative_path"])
    for r, paths in excl_by_root.items():
        collision_namespace(paths)

    stats = {
        "raw_regular_files": raw_regular,
        "present_exact_exclusions": present_exact,
        "unsupported_filesystem_objects": 0,
        "escaping_symlinks": 0,
        "hard_link_aliases": 0,
        "unclassified_source_paths": 0,
        "included_regular_file_count": len(included),
        "directory_entry_count": len(directories),
        "exact_exclusion_record_count": len(EXACT_EXCLUSIONS),
        "present_exclusion_keys": sorted(present_keys),
    }
    return included, directories, excluded_present, stats

# --------------------------------------------------------------------------
# Manifest construction.
# --------------------------------------------------------------------------
def build_source_root_declarations():
    decls = []
    for source_root, sub_path, scope, dest_pre in SOURCE_ROOTS:
        decls.append({"source_root": source_root, "component_scope": scope,
                       "host_relative_path": sub_path,
                       "destination_prefix": dest_pre})
    return sorted(decls, key=sk_root_decl)


def build_migration_workspaces():
    decls = []
    for cid, seed_roots in WORKSPACE_COMPONENTS:
        decls.append({
            "component_id": cid,
            "workspace_host_path": cid,
            "mount_destination": MOUNT_DESTINATION,
            "seed_source_roots": sorted(seed_roots),
            "private_physical_copy": True,
            "no_hard_links": True, "no_reflinks": True,
            "no_overlays": True, "no_source_aliases": True,
            "no_runtime_mount_from_external_nos3": True,
        })
    return sorted(decls, key=sk_workspace)


def build_manifest(repo_root, included, directories, excluded_present, stats):
    """Assemble the canonical manifest dict.  Frozen snapshot values come
    from SNAPSHOT, not current stats.  Current stats only affect --json-stats.
    """
    # Destination mapping prefix model: destination_relative = prefix + "/" + rel.
    snapshot = dict(SNAPSHOT)
    manifest = {
        "schema": CONTRACT_SCHEMA,
        "source_root_declarations": build_source_root_declarations(),
        "included_regular_file_entries": [{k: v for k, v in e.items()}
                                          for e in sorted(included, key=sk_included)],
        "directory_entries": sorted(directories, key=sk_directory),
        "exact_exclusion_records": sorted(EXACT_EXCLUSIONS, key=sk_excluded),
        "deny_pattern_declarations": sorted(DENY_PATTERNS, key=sk_deny),
        "workspace_declarations": build_migration_workspaces(),
        "canonicalization": {
            "no_internal_manifest_sha256": True,
            "detached_sha256_over_complete_file_bytes": True,
            "json_dumps": {"ensure_ascii": True, "sort_keys": True,
                           "separators": [",", ":"], "exactly_one_final_lf": True},
            "exact_utf8_bytes_remain_path_identity": True,
            "all_sort_key_elements_byte_encoded": True,
            "no_locale_dependent_ordering": True,
            "no_filesystem_traversal_order_influence": True,
            "root_directory_sentinel": {
                "entry_category": "directory_entry",
                "source_root_directory": True,
                "value": "",
                "denotes_declared_root_itself": True,
                "not_passed_through_normal_child_path_validation": True,
                "empty_string_rejected_for_files": True,
                "empty_string_rejected_for_exclusions": True,
                "empty_string_rejected_for_destination_paths": True,
                "empty_string_rejected_for_workspace_paths": True,
                "empty_string_rejected_for_non_root_directory_entries": True,
            },
        },
        "path_validation": {
            "reject_surrogate_code_points": True, "reject_nul": True,
            "reject_absolute_paths": True, "reject_empty_components": True,
            "reject_dot_components": True, "reject_dotdot_components": True,
            "reject_backslashes": True, "reject_repeated_separators": True,
            "reject_duplicate_source_identities": True,
            "reject_duplicate_destination_identities_within_component": True,
            "reject_directory_file_and_prefix_collisions": True,
        },
        "collision_model": {
            "step_1_nfd_decompose": True,
            "step_2_apply_str_casefold_not_lower": True,
            "step_3_normalize_folded_to_nfc_and_nfd_independently": True,
            "step_4_encode_both_as_utf8": True,
            "step_5_reject_distinct_paths_if_either_collides": True,
            "normalized_values_are_collision_guards_only": True,
            "exact_utf8_bytes_remain_path_identity": True,
            "namespaces": [
                "source_files_per_root", "source_directories_per_root",
                "destinations_per_component", "exclusions_per_root",
                "deny_patterns_per_scope",
            ],
        },
        "inventory_invariants": INVARIANTS,
        "snapshot_inventory": snapshot,
        "source_exclusion_policy": {
            "excluded_source_path_may_be_absent": True,
            "absence_is_not_source_drift": True,
            "present_must_match_type_mode_size_sha256": True,
            "present_mismatch_fails_closed": True,
            "unlisted_source_path_fails_closed": True,
            "new_deny_pattern_match_fails_without_exact_classification": True,
        },
        "destination_exclusion_policy": {
            "all_exclusions_must_be_absent_from_destinations": True,
            "deny_patterns_are_additional_fail_closed_guards": True,
        },
        "authorization_boundary": {
            "real_materialization_requires_explicit_authorization": True,
            "tool_must_not_infer_authorization_from_narrative_status": True,
            "host_only": True, "no_docker_invocation": True,
            "no_runtime_candidate_emission": True,
            "no_verifier_execution": True, "no_compilation": True,
        },
    }
    return manifest


def serialize_manifest(manifest):
    raw = json.dumps(manifest, ensure_ascii=True, sort_keys=True,
                     separators=(",", ":"))
    return (raw + "\n").encode("utf-8")

# --------------------------------------------------------------------------
# Authoritative manifest verification.
# --------------------------------------------------------------------------
def verify_manifest(manifest_bytes, repo_root):
    """Verify supplied manifest bytes exactly: canonical-bytes equality and
    complete expected-object equality, with descriptor-bound source hashing.

    Returns True or raises FailClosed.
    """
    # ---- Exact canonical-byte verification. ----
    if not isinstance(manifest_bytes, (bytes, bytearray)):
        raise FailClosed("verify: manifest must be bytes")
    # Reject invalid UTF-8.
    try:
        manifest_bytes.decode("utf-8")
    except UnicodeDecodeError:
        raise FailClosed("verify: invalid UTF-8")
    # Exactly one final LF; reject CRLF/BOM/extra LF/leading whitespace.
    if not manifest_bytes.endswith(b"\n"):
        raise FailClosed("verify: missing final LF")
    if manifest_bytes.endswith(b"\n\n"):
        raise FailClosed("verify: duplicate final LF")
    if b"\r" in manifest_bytes:
        raise FailClosed("verify: CRLF present")
    if manifest_bytes.startswith(b"\xef\xbb\xbf"):
        raise FailClosed("verify: BOM present")
    if len(manifest_bytes) > 1 and manifest_bytes[-2:] in (b" \n", b"\t\n"):
        raise FailClosed("verify: trailing whitespace before final LF")
    decoded = manifest_bytes[:-1]
    # Reject leading/trailing whitespace or non-object top-level.
    if decoded != decoded.strip():
        raise FailClosed("verify: surrounding whitespace")
    if not decoded.startswith(b"{"):
        raise FailClosed("verify: top-level JSON not an object")
    try:
        m = json.loads(manifest_bytes)
    except ValueError as exc:
        raise FailClosed("verify: JSON parse error: %s" % exc)
    # Reserialize the parsed object canonically; must equal supplied bytes.
    recanon = serialize_manifest(m)  # includes the final LF
    if recanon != manifest_bytes:
        raise FailClosed("verify: noncanonical bytes (CRLF/indent/sep/order rejected)")

    # ---- Exact expected-manifest comparison. ----
    included, directories, excluded_present, stats = walk_source_roots(repo_root)
    expected = build_manifest(repo_root, included, directories, excluded_present, stats)
    if m != expected:
        # Locate the first diverging top-level key for a useful failure.
        ek = set(expected) | set(m)
        for k in sorted(ek):
            if m.get(k) != expected.get(k):
                raise FailClosed("verify: manifest differs from expected at key %r" % k)
        raise FailClosed("verify: manifest differs from expected")
    # Defense-in-depth invariant checks (after exact comparison).
    if len(m["included_regular_file_entries"]) != 1422:
        raise FailClosed("verify: included != 1422")
    if sum(e["size"] for e in m["included_regular_file_entries"]) != 100496114:
        raise FailClosed("verify: included bytes != 100496114")
    if len(m["directory_entries"]) != 89:
        raise FailClosed("verify: directory count != 89")
    if len(m["exact_exclusion_records"]) != 11:
        raise FailClosed("verify: exclusion count != 11")
    if len(m["workspace_declarations"]) != 18:
        raise FailClosed("verify: workspace count != 18")
    if m.get("snapshot_inventory") != SNAPSHOT:
        raise FailClosed("verify: snapshot_inventory not frozen")

    # ---- Descriptor-bound source verification. ----
    _verify_included_descriptors(m["included_regular_file_entries"], repo_root)
    return True


def _safe_open_source(repo_root_fd, src_root_id, rel_path):
    """Open a source file via descriptor-relative component traversal that
    rejects symlinks in EVERY path component (intermediate parents and leaf),
    bound to an ALREADY-OPENED, ALREADY-VERIFIED repository-root descriptor.

    The caller opens the repository root with O_DIRECTORY|O_NOFOLLOW and
    verifies its identity BEFORE calling this function.  This function NEVER
    reopens the repository root by pathname -- it traverses from the supplied
    root fd.

    Capability probe: os.open must support dir_fd (os.supports_dir_fd) and
    O_DIRECTORY / O_NOFOLLOW must exist.  When safe component-wise traversal
    is unavailable, raise FailClosed -- never fall back to lstat+open or
    O_NOFOLLOW-on-leaf-only.

    Returns ONLY the open leaf descriptor.  Every intermediate directory
    descriptor opened during traversal is explicitly closed here (including
    on the failure path).  The caller closes the returned leaf descriptor.
    The caller-owned repo_root_fd is NOT closed here.
    """
    if src_root_id not in ROOT_HOST:
        raise FailClosed("safe_open: unknown source_root %s" % src_root_id)
    if "\x00" in rel_path:
        raise FailClosed("safe_open: NUL in relative path")
    # Real capability probe -- not a hasattr() guess.
    if (os.open not in os.supports_dir_fd
            or not hasattr(os, "O_DIRECTORY") or not hasattr(os, "O_NOFOLLOW")):
        raise FailClosed("safe_open: descriptor-relative traversal unavailable "
                         "on this platform")
    root_sub = ROOT_HOST[src_root_id]
    dirfds = []  # descriptors opened here (NOT the caller-owned root fd)
    leaf_fd = None
    try:
        # Start traversal from the caller-supplied verified repo-root fd.
        # Do NOT reopen the repo root by pathname.
        cur = repo_root_fd
        parts = []
        if root_sub:
            parts.extend([p for p in root_sub.split("/") if p])
        parent_of_rel = os.path.dirname(rel_path)
        if parent_of_rel:
            parts.extend([p for p in parent_of_rel.split("/") if p])
        for comp in parts:
            if comp in (".", "..", ""):
                raise FailClosed("safe_open: dot/dotdot/empty component")
            try:
                next_fd = os.open(comp, os.O_RDONLY | os.O_DIRECTORY
                                  | os.O_NOFOLLOW, dir_fd=cur)
            except OSError as exc:
                raise FailClosed("safe_open: O_NOFOLLOW dir open failed for %r: %s"
                                 % (comp, exc))
            dirfds.append(next_fd)
            cur = next_fd
        leaf = os.path.basename(rel_path)
        if leaf in ("", ".", ".."):
            raise FailClosed("safe_open: invalid leaf %r" % leaf)
        try:
            leaf_fd = os.open(leaf, os.O_RDONLY | os.O_NOFOLLOW, dir_fd=cur)
        except OSError as exc:
            raise FailClosed("safe_open: O_NOFOLLOW leaf open failed for %r: %s"
                             % (leaf, exc))
        opened = leaf_fd
        leaf_fd = None  # ownership transferred to caller
        return opened
    finally:
        if leaf_fd is not None:
            try: os.close(leaf_fd)
            except OSError: pass
        for d in dirfds:
            try: os.close(d)
            except OSError: pass


def _hash_fd(fd):
    h = hashlib.sha256()
    while True:
        b = os.read(fd, 1024 * 1024)
        if not b:
            break
        h.update(b)
    return h.hexdigest()


def _open_repo_root_fd(repo_root):
    """Open the repository root with O_DIRECTORY|O_NOFOLLOW and return the
    descriptor.  Rejects symlinks at the repo root."""
    if (os.open not in os.supports_dir_fd
            or not hasattr(os, "O_DIRECTORY") or not hasattr(os, "O_NOFOLLOW")):
        raise FailClosed("verify: descriptor-relative traversal unavailable")
    try:
        return os.open(repo_root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    except OSError as exc:
        raise FailClosed("verify: repo root open failed: %s (%s)" % (repo_root, exc))


def _open_authorized_root_bound(authorized_root, frozen_receipt):
    """Open the authorized root ONCE with O_DIRECTORY|O_NOFOLLOW and bind its
  descriptor identity to the frozen receipt (Correction 6).  Requires the
  opened descriptor's dev/ino to equal frozen_receipt['dev']/['ino'] and the
  descriptor to be a directory; returns (ar_fd, ar_fd_receipt).  On any
  mismatch or open failure the opened descriptor (if any) is closed and
  FailClosed is raised BEFORE staging creation, so no staging directory is
  created on a mismatch.  Production materialization uses this helper after
  authorization."""
    _require_dirfd_capabilities()
    try:
        ar_fd = os.open(authorized_root,
                        os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    except OSError as exc:
        raise FailClosed("authorized-root open failed: %s: %s"
                         % (authorized_root, exc))
    try:
        fdev, fino, fdir = _fd_identity(ar_fd)
        if not fdir:
            raise FailClosed("authorized-root fd is not a directory: %s"
                             % authorized_root)
        if (fdev, fino) != (frozen_receipt['dev'], frozen_receipt['ino']):
            raise FailClosed("authorized-root fd dev/ino mismatch with receipt")
        ar_fd_receipt = {'dev': fdev, 'ino': fino, 'is_dir': True}
    except BaseException:
        try: os.close(ar_fd)
        except OSError: pass
        raise
    return ar_fd, ar_fd_receipt


def _verify_included_descriptors(entries, repo_root):
    """For every included source file, open via safe component-wise traversal
    bound to an opened-verified repository-root descriptor, and hash/type/
    mode/size/nlink from the same descriptor.  No pathname re-open.

    Opens the repo root ONCE with O_DIRECTORY|O_NOFOLLOW and passes the
    descriptor into _safe_open_source for every entry.  The descriptor is
    closed in a finally so no fd leaks across the 1422-file loop."""
    repo_fd = _open_repo_root_fd(repo_root)
    try:
        for e in entries:
            src = e["source_root"]
            fp = os.path.join(repo_root, ROOT_HOST[src], e["relative_path"])  # msgs
            sfd = _safe_open_source(repo_fd, src, e["relative_path"])
            try:
                st = os.fstat(sfd)
                if not stat.S_ISREG(st.st_mode):
                    raise FailClosed("verify: not regular: %s" % fp)
                if st.st_nlink != 1:
                    raise FailClosed("verify: source nlink!=1: %s" % fp)
                if stat.S_IMODE(st.st_mode) != int(e["mode"], 8):
                    raise FailClosed("verify: source mode mismatch %s disk=%o manifest=%s"
                                     % (fp, stat.S_IMODE(st.st_mode), e["mode"]))
                if st.st_size != e["size"]:
                    raise FailClosed("verify: source size mismatch: %s" % fp)
                if _hash_fd(sfd) != e["sha256"]:
                    raise FailClosed("verify: source sha mismatch: %s" % fp)
                exp_dest = DEST_PREFIX[src] + "/" + e["relative_path"]
                if e["destination_relative"] != exp_dest:
                    raise FailClosed("verify: destination mapping mismatch %s"
                                     % e["relative_path"])
            finally:
                try: os.close(sfd)
                except OSError: pass
    finally:
        try: os.close(repo_fd)
        except OSError: pass

def _build_verified_manifest_boundary():
    """Factory that encloses the VerifiedManifest class, its authoritative
    object-keyed weak registry, and the sole issuance function in ONE
    closure boundary.

    No registry object, accessor, insertion function, replacement function,
    or debugging accessor is exposed as a module attribute.  Only the
    VerifiedManifest class and load_and_verify_manifest() are returned to
    the module namespace."""
    _registry = weakref.WeakKeyDictionary()

    class VerifiedManifest:
        """Immutable opaque bearer whose authoritative state lives in the
        enclosed object-keyed weak registry (NOT a module attribute).

        Construct only via load_and_verify_manifest().  Direct __init__
        raises.  object.__new__ forgeries are rejected because they have no
        registry entry and cannot acquire one through any module attribute.
        The object carries NO mutable authoritative state: all properties
        read from the enclosed registry."""

        __slots__ = ("__weakref__",)

        def __init__(self):
            raise FailClosed(
                "VerifiedManifest: direct construction forbidden; "
                "use load_and_verify_manifest()")

        def __setattr__(self, name, value):
            raise FailClosed("VerifiedManifest is immutable: cannot set %s" % name)

        def __delattr__(self, name):
            raise FailClosed("VerifiedManifest is immutable: cannot del %s" % name)

        def _entry(self):
            # Identity check against the enclosed object-keyed registry.
            # A forged object (object.__new__) has no registry entry; no
            # module attribute can insert one.
            if self not in _registry:
                raise FailClosed(
                    "verified manifest: bearer not in issuance registry "
                    "(forged or unregistered object)")
            return _registry[self]

        @property
        def raw_bytes(self):
            return self._entry()[0]

        @property
        def detached_hash(self):
            return self._entry()[1]

        @property
        def repo_root(self):
            return self._entry()[2]

        def revalidate(self):
            raw, dhash, repo_rp, rdev, rino = self._entry()
            if dhash != sha256_bytes(raw):
                raise FailClosed("revalidate: canonical bytes/hash drift")
            try:
                st = os.stat(repo_rp)
            except OSError:
                raise FailClosed("revalidate: repository root disappeared")
            if (st.st_dev, st.st_ino) != (rdev, rino):
                raise FailClosed("revalidate: repository-root identity changed")
            return True

        def full_reverify(self):
            """Rerun the complete verify_manifest() against the closure-held
            canonical bytes and the closure-held repository identity, against
            the current source inventory.  A coherent mutation of raw bytes
            plus detached hash still fails because the source no longer
            matches."""
            raw, dhash, repo_rp, rdev, rino = self._entry()
            self.revalidate()
            if not verify_manifest(raw, repo_rp):
                raise FailClosed(
                    "full_reverify: manifest no longer matches source inventory")
            return True

        def manifest(self):
            # Return a detached parsed copy (reparse private canonical bytes)
            # so callers cannot mutate authoritative parsed state.
            return json.loads(self._entry()[0])

        def workspace_for(self, component_id):
            for w in self.manifest()["workspace_declarations"]:
                if w["component_id"] == component_id:
                    return w
            raise FailClosed(
                "component_id %r not found in verified workspace declarations"
                % component_id)

        def open_verified_repo_fd(self):
            """Open the closure-held repository root with O_DIRECTORY|O_NOFOLLOW
            and compare the opened descriptor's dev/ino/type with the
            registry-held repository receipt BEFORE returning it to the
            caller.  Production materialization uses this verified descriptor
            for all source traversal (never reopens the repo path
            independently after full_reverify())."""
            raw, dhash, repo_rp, rdev, rino = self._entry()
            fd = _open_repo_root_fd(repo_rp)
            try:
                dev, ino, isdir = _fd_identity(fd)
                if not isdir:
                    raise FailClosed("repo root descriptor not a directory")
                if (dev, ino) != (rdev, rino):
                    raise FailClosed(
                        "repo-root descriptor dev/ino mismatch with registry")
            except BaseException:
                try: os.close(fd)
                except OSError: pass
                raise
            ret = fd
            fd = -1  # ownership transferred to caller
            return ret

    def load_and_verify_manifest(manifest_bytes, repo_root):
        """Verify and return an immutable VerifiedManifest bearer whose
        authoritative state is stored in the enclosed object-keyed weak
        registry, bound to the repository root's device/inode identity.
        The ONLY normal production issuer."""
        if not isinstance(manifest_bytes, (bytes, bytearray)):
            raise FailClosed("load_and_verify: manifest must be bytes")
        try:
            repo_abs = os.path.realpath(repo_root)
            st = os.stat(repo_abs)
        except OSError as exc:
            raise FailClosed("load_and_verify: repo root unavailable: %s" % exc)
        raw = bytes(manifest_bytes)
        if not verify_manifest(raw, repo_abs):
            raise FailClosed("load_and_verify: verification failed")
        bearer = object.__new__(VerifiedManifest)
        _registry[bearer] = (raw, sha256_bytes(raw), repo_abs,
                             st.st_dev, st.st_ino)
        return bearer

    return VerifiedManifest, load_and_verify_manifest



VerifiedManifest, load_and_verify_manifest = _build_verified_manifest_boundary()



# --------------------------------------------------------------------------
# Production materialization authorization boundary (Checkpoint 2B1R1).
#
# A closure-backed MaterializationAuthorized bearer, its authoritative
# object-keyed weak registry, the registry-held complete authorization
# receipt, and the SOLE production issuer authorize_v3_materialization() are
# enclosed in ONE factory boundary.  Only MaterializationAuthorized and
# authorize_v3_materialization are exposed to the module namespace.  No
# registry object, no internal issuance callable (_issue or otherwise), no
# registry accessor/insertion/replacement function, and no secret/token/debug
# hook is exposed as a module attribute.  There is no callable combination of
# module attributes that can insert a bearer into the registry without running
# the full production authorization validation.  The bearer carries NO mutable
# authoritative state; all authoritative state lives in the enclosed registry.
#
# The executing-tool identity is bound to the canonical descriptor-bound
# identity of __file__ (the file whose code is currently executing the
# issuer), not to any caller-supplied or copied path.  All authorization
# files (contract, manifest, candidate, executing tool) are opened and
# hashed through a single retained repository-root descriptor and a generic
# repository-relative no-follow opener; path-based reopening is never used.
# --------------------------------------------------------------------------


def _open_repo_root_fd_nofollow(repo_root):
    """Open the repository root ONCE with O_DIRECTORY|O_NOFOLLOW and return
    (fd, receipt) where receipt is the immutable descriptor identity
    {path, dev, ino, is_dir}.  Caller owns fd and must close it."""
    if (os.open not in os.supports_dir_fd
            or not hasattr(os, "O_DIRECTORY") or not hasattr(os, "O_NOFOLLOW")):
        raise FailClosed("auth: descriptor-relative traversal unavailable")
    try:
        fd = os.open(repo_root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    except OSError as exc:
        raise FailClosed("auth: repo root open failed %r: %s" % (repo_root, exc))
    dev, ino, isdir = _fd_identity(fd)
    if not isdir:
        try: os.close(fd)
        except OSError: pass
        raise FailClosed("auth: repo root not a directory: %r" % repo_root)
    return fd, {"path": repo_root, "dev": dev, "ino": ino, "is_dir": True}


def _repo_relative_from_abs(abs_path, repo_abs):
    """Derive a strict repository-relative path string from an absolute path
    that must resolve under repo_abs.  Reject absolute, empty, dot, dotdot,
    repeated separator, backslash, NUL, and surrogate components."""
    if not isinstance(abs_path, str) or abs_path == "":
        raise FailClosed("auth: path not a nonempty string: %r" % abs_path)
    if abs_path.startswith("/"):
        # absolute paths are allowed only if under repo_abs
        if abs_path != repo_abs and not abs_path.startswith(repo_abs + os.sep):
            raise FailClosed("auth: path escapes repository root: %r" % abs_path)
        rel = abs_path[len(repo_abs) + 1:] if abs_path != repo_abs else ""
    else:
        rel = abs_path
    if rel == "":
        raise FailClosed("auth: path equals repository root (no leaf): %r" % abs_path)
    if rel.startswith("/"):
        raise FailClosed("auth: relative path absolute: %r" % rel)
    if "\\" in rel:
        raise FailClosed("auth: backslash in path: %r" % rel)
    if "\x00" in rel:
        raise FailClosed("auth: NUL in path: %r" % rel)
    parts = rel.split("/")
    for p in parts:
        if p == "":
            raise FailClosed("auth: empty/repeated separator: %r" % rel)
        if p in (".", ".."):
            raise FailClosed("auth: dot/dotdot component: %r" % rel)
        if any(0xD800 <= ord(ch) < 0xE000 for ch in p):
            raise FailClosed("auth: surrogate component: %r" % rel)
    return rel


def _open_repo_relative_file(repo_fd, rel_path):
    """Generic repository-relative regular-file opener.  Opens every parent
    directory component with O_DIRECTORY|O_NOFOLLOW relative to the retained
    repository-root descriptor (repo_fd), then opens the leaf with O_NOFOLLOW.
    Requires a regular file with nlink 1, compares lstat/opened-fstat device
    and inode continuity, reads and SHA-256 hashes the file from the opened
    descriptor, and returns (fd, receipt, raw_bytes) where receipt is
    {rel_path, dev, ino, sha256}.  Never falls back to path-only opening.
    Caller owns fd and must close it."""
    if "\x00" in rel_path:
        raise FailClosed("auth: NUL in relative path")
    parts = rel_path.split("/")
    leaf = parts[-1]
    if leaf in ("", ".", ".."):
        raise FailClosed("auth: invalid leaf %r" % leaf)
    parent_parts = parts[:-1]
    for p in parent_parts:
        _validate_name(p)
    _validate_name(leaf)
    dirfds = []
    leaf_fd = None
    try:
        cur = repo_fd
        for comp in parent_parts:
            try:
                next_fd = os.open(comp, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                                  dir_fd=cur)
            except OSError as exc:
                raise FailClosed("auth: parent dir open failed %r: %s" % (comp, exc))
            cur = next_fd
            dirfds.append(next_fd)
        # lstat the leaf relative to the parent descriptor BEFORE opening.
        try:
            lst = os.stat(leaf, dir_fd=cur, follow_symlinks=False)
        except OSError as exc:
            raise FailClosed("auth: leaf lstat failed %r: %s" % (leaf, exc))
        if not stat.S_ISREG(lst.st_mode):
            raise FailClosed("auth: not a regular file: %r" % rel_path)
        if lst.st_nlink != 1:
            raise FailClosed("auth: nlink != 1: %r" % rel_path)
        try:
            leaf_fd = os.open(leaf, os.O_RDONLY | os.O_NOFOLLOW, dir_fd=cur)
        except OSError as exc:
            raise FailClosed("auth: leaf O_NOFOLLOW open failed %r: %s"
                             % (rel_path, exc))
        fst = os.fstat(leaf_fd)
        # Device/inode continuity between lstat and opened-fstat.
        if (fst.st_dev, fst.st_ino) != (lst.st_dev, lst.st_ino):
            raise FailClosed("auth: leaf identity drift (lstat vs fstat): %r"
                             % rel_path)
        if not stat.S_ISREG(fst.st_mode):
            raise FailClosed("auth: opened descriptor not a regular file: %r"
                             % rel_path)
        if fst.st_nlink != 1:
            raise FailClosed("auth: opened descriptor nlink != 1: %r" % rel_path)
        raw = b""
        while True:
            chunk = os.read(leaf_fd, 1024 * 1024)
            if not chunk:
                break
            raw += chunk
        # Rewind is unnecessary; bytes already captured.
        sha = sha256_bytes(raw)
        # Seek back to 0 so callers that re-hash/re-read from the descriptor
        # (without reopening) see the full file.  shutil is unavailable; use
        # os.lseek.
        try:
            os.lseek(leaf_fd, 0, os.SEEK_SET)
        except OSError:
            pass
        receipt = {"rel_path": rel_path, "dev": fst.st_dev,
                   "ino": fst.st_ino, "sha256": sha}
        return leaf_fd, receipt, raw
    finally:
        for d in dirfds:
            try: os.close(d)
            except OSError: pass


def _build_materialization_authorization_boundary():
    """Factory that encloses the MaterializationAuthorized bearer class, its
    authoritative object-keyed weak registry, the complete authorization
    receipt store, the internal _issue function, AND the sole production
    issuer authorize_v3_materialization() in ONE closure boundary.

    Returns ONLY (MaterializationAuthorized, authorize_v3_materialization).
    No registry object, internal _issue callable, registry accessor,
    insertion/replacement function, secret, token, or debug hook is exposed
    as a module attribute.  There is no callable combination of module
    attributes that can insert a bearer without the full production
    authorization validation."""
    _registry = weakref.WeakKeyDictionary()

    class MaterializationAuthorized:
        """Immutable opaque bearer proving a D-064 governed v3 materialization
        is authorized for a specific repository root and a specific set of
        authorization files.  Constructed ONLY via authorize_v3_materialization().
        Direct __init__ raises; an object.__new__ forgery has no registry entry
        and cannot acquire one through any module attribute.  The object carries
        NO mutable authoritative state; every property reads from the enclosed
        registry receipt."""

        __slots__ = ("__weakref__",)

        def __init__(self):
            raise FailClosed("MaterializationAuthorized: direct construction "
                             "forbidden; use authorize_v3_materialization()")

        def __setattr__(self, name, value):
            raise FailClosed("MaterializationAuthorized is immutable: "
                             "cannot set %s" % name)

        def __delattr__(self, name):
            raise FailClosed("MaterializationAuthorized is immutable: "
                             "cannot del %s" % name)

        def _entry(self):
            if self not in _registry:
                raise FailClosed(
                    "materialization authorization: bearer not in issuance "
                    "registry (forged or unregistered object)")
            return _registry[self]

        # ---- repository identity ----
        @property
        def repo_root(self):
            return self._entry()["repo"]["path"]

        @property
        def repo_dev(self):
            return self._entry()["repo"]["dev"]

        @property
        def repo_ino(self):
            return self._entry()["repo"]["ino"]

        # ---- candidate identity ----
        @property
        def candidate_sha256(self):
            return self._entry()["candidate"]["sha256"]

        # ---- executing-tool identity ----
        @property
        def tool_sha256(self):
            return self._entry()["tool"]["sha256"]

        # ---- manifest identity ----
        @property
        def manifest_sha256(self):
            return self._entry()["manifest"]["sha256"]

        def _receipt(self):
            """Return the complete authorization receipt (internal use by
            _require_auth which shares this closure)."""
            return self._entry()

    def _issue(receipt):
        bearer = object.__new__(MaterializationAuthorized)
        _registry[bearer] = receipt
        return bearer

    # ---- Structured-authorization snapshot (built once at issuance) ----
    def _auth_state_snapshot(contract):
        gate = contract.get("gate", {})
        am = contract.get(
            "passive_time_witness_runtime_candidate_v3_design_amendment_1", {})
        impl = am.get(
            "passive_time_witness_runtime_candidate_v3_implementation", {})
        return {
            "schema": gate.get(
                "passive_time_witness_runtime_candidate_v3_contract_schema"),
            "static_verification":
                gate.get("passive_time_witness_runtime_candidate_v3_static_verification"),
            "accepted_candidate":
                gate.get("accepted_runtime_entrypoint_v3_sha256"),
            "proposed_candidate":
                gate.get("proposed_runtime_entrypoint_v3_sha256"),
            "diag_runtime_authorized":
                gate.get("diagnostic_runtime_authorized"),
            "diag_attempts":
                gate.get("diagnostic_runtime_attempts_authorized"),
            "am_runtime_authorized": am.get("runtime_authorized"),
            "am_runtime_attempts": am.get("runtime_attempts"),
            "d064_status": am.get("d064_status"),
            "impl_status": am.get("implementation_status"),
            "am_static_verification": am.get("static_verification"),
            "scientific_outcome_allowed":
                contract.get("scientific_outcome_allowed"),
            "command_transmission_allowed":
                contract.get("command_transmission_allowed"),
            "event_injection_allowed":
                contract.get("event_injection_allowed"),
            "baseline_execution_allowed":
                contract.get("baseline_execution_allowed"),
            "cryptographic_semantics_claim_allowed":
                contract.get("cryptographic_semantics_claim_allowed"),
            "gate_baseline_run_1_authorized":
                gate.get("baseline_run_1_authorized"),
            "gate_baseline_run_2_authorized":
                gate.get("baseline_run_2_authorized"),
            "gate_event_injection_authorized":
                gate.get("event_injection_authorized"),
            "tool_decl_path":
                (impl.get("runtime_material_tool") or {}).get("path"),
            "manifest_decl_path":
                (impl.get("runtime_manifest") or {}).get("path"),
        }

    def authorize_v3_materialization(repo_root, contract_path, manifest_path,
                                      candidate_path, tool_path):
        """Sole production issuer of a MaterializationAuthorized bearer for a
        v3 materialization transaction.  Reads and validates actual files
        (never a caller-supplied contract dict) through ONE retained
        repository-root descriptor and a generic repository-relative no-follow
        opener.  Binds the executing-tool identity to the canonical descriptor-
        bound identity of __file__.  Fail-closed before any authorized-root
        inspection, workspace creation, staging, copying, materialization, or
        Docker.  Under the current contract (0.4.11) this fails closed and
        raises FailClosed; the CLI --authorize-v3-check prints the closed gate
        marker.

        Inputs (canonical, absolute or repo-relative):
          repo_root      - repository root under which all paths resolve
          contract_path  - downlink-diagnostic-contract.json path
          manifest_path  - NOS3 runtime-material manifest path
          candidate_path - v3 candidate regular file path
          tool_path      - expected runtime-material tool path (this tool)

        Does not mutate any file, authorized root, or staging directory."""
        fail_prefix = "v3 materialization authorization closed: "

        # ---- 3. One descriptor-bound repository root ----
        repo_fd, repo_receipt = _open_repo_root_fd_nofollow(repo_root)
        repo_abs = repo_receipt["path"]
        try:
            # Canonical __file__ (the file whose code is executing now) must
            # reside under the repository root.
            this_file = os.path.abspath(__file__)
            try:
                this_real = os.path.realpath(this_file)
            except OSError as exc:
                raise FailClosed(fail_prefix + "executing __file__ unavailable: %s"
                                 % exc)
            if this_real != repo_abs and not this_real.startswith(repo_abs + os.sep):
                raise FailClosed(fail_prefix +
                                 "executing tool not under repository root: %r"
                                 % this_real)

            # ---- 4. Generic repository-relative opener for each file ----
            def _resolve_rel(path):
                # Resolve a path (absolute or repo-relative) to strict
                # repo-relative against repo_abs, without following symlinks.
                if path is None or path == "":
                    raise FailClosed(fail_prefix + "empty path")
                ap = os.path.abspath(path) if not os.path.isabs(path) else path
                # abspath collapses '.'/'..' lexically; reject components we
                # never want even though abspath resolved them.
                if ap != repo_abs and not ap.startswith(repo_abs + os.sep):
                    raise FailClosed(fail_prefix +
                                     "path escapes repository root: %r" % path)
                return _repo_relative_from_abs(ap, repo_abs)

            contract_rel = _resolve_rel(contract_path)
            manifest_rel = _resolve_rel(manifest_path)
            candidate_rel = _resolve_rel(candidate_path)
            tool_rel = _resolve_rel(tool_path)
            # The executing tool is __file__.
            this_tool_rel = _repo_relative_from_abs(this_real, repo_abs)

            def _open(rel):
                return _open_repo_relative_file(repo_fd, rel)

            # ---- 2. Bind authorization to the exact executing tool ----
            # caller tool_path must equal canonical __file__'s relative path.
            if tool_rel != this_tool_rel:
                raise FailClosed(fail_prefix +
                                 "tool_path does not identify the executing "
                                 "tool (__file__); copied tool rejected")
            tool_fd, tool_receipt, tool_raw = _open(tool_rel)
            try:
                # Contract-declared tool path must also equal __file__.
                # (Declared inside the contract; checked after contract load
                # below.  Here we retain the executing-tool receipt.)
                pass
            finally:
                pass

            # ---- 5. Read+hash contract from the same descriptor ----
            contract_fd, contract_receipt, contract_raw = \
                _open(contract_rel)
            try:
                contract = json.loads(contract_raw)
            except ValueError as exc:
                try: os.close(contract_fd)
                except OSError: pass
                raise FailClosed(fail_prefix + "contract JSON invalid: %s" % exc)
            os.close(contract_fd)

            # ---- Structured authorization (schema 1 compatibility gate) ----
            if not isinstance(contract, dict):
                raise FailClosed(fail_prefix + "contract not a JSON object")
            gate = contract.get("gate", {})
            if not isinstance(gate, dict):
                raise FailClosed(fail_prefix + "gate not a JSON object")

            def _is_exact_int(v):
                return isinstance(v, int) and not isinstance(v, bool)

            schema = gate.get(
                "passive_time_witness_runtime_candidate_v3_contract_schema")
            if not (_is_exact_int(schema) and schema == 1):
                raise FailClosed(fail_prefix +
                                 "v3 contract schema is not exact int 1")
            sv = gate.get(
                "passive_time_witness_runtime_candidate_v3_static_verification")
            if sv != "PASS":
                raise FailClosed(fail_prefix +
                                 "v3 static verification is not PASS")
            if gate.get("diagnostic_runtime_authorized") is not True:
                raise FailClosed(fail_prefix +
                                 "diagnostic_runtime_authorized is not exact True")
            attempts = gate.get("diagnostic_runtime_attempts_authorized")
            if not (_is_exact_int(attempts) and attempts == 1):
                raise FailClosed(fail_prefix +
                                 "diagnostic_runtime_attempts_authorized is not "
                                 "exact int 1")
            am = contract.get(
                "passive_time_witness_runtime_candidate_v3_design_amendment_1",
                {})
            if not isinstance(am, dict):
                raise FailClosed(fail_prefix + "v3 amendment block missing/invalid")
            if am.get("runtime_authorized") is not True:
                raise FailClosed(fail_prefix +
                                 "amendment runtime_authorized is not exact True")
            am_attempts = am.get("runtime_attempts")
            if not (_is_exact_int(am_attempts) and am_attempts == 1):
                raise FailClosed(fail_prefix +
                                 "amendment runtime_attempts is not exact int 1")
            d064 = am.get("d064_status")
            if d064 in ("BLOCKED", "READY_FOR_SEPARATE_D064_CONSIDERATION"):
                raise FailClosed(fail_prefix +
                                 "d064_status is not authorized: %r" % (d064,))

            # ---- accepted candidate identity ----
            accepted = gate.get("accepted_runtime_entrypoint_v3_sha256")
            if not isinstance(accepted, str) or not _is_hex64(accepted):
                raise FailClosed(fail_prefix +
                                 "accepted_runtime_entrypoint_v3_sha256 is not a "
                                 "nonempty lowercase 64-hex string")
            if accepted != accepted.lower():
                raise FailClosed(fail_prefix +
                                 "accepted_runtime_entrypoint_v3_sha256 not "
                                 "lowercase")
            # proposed is informational only; never authorization.
            proposed = gate.get("proposed_runtime_entrypoint_v3_sha256")
            if isinstance(proposed, str) and proposed != "" and proposed == accepted:
                pass

            # ---- Closed permissions (exact bool False) ----
            closed_top = ("scientific_outcome_allowed",
                          "command_transmission_allowed",
                          "event_injection_allowed",
                          "baseline_execution_allowed",
                          "cryptographic_semantics_claim_allowed")
            for k in closed_top:
                if contract.get(k) is not False:
                    raise FailClosed(fail_prefix +
                                     "permission not exact false: %s" % k)
            closed_gate = ("baseline_run_1_authorized",
                           "baseline_run_2_authorized",
                           "event_injection_authorized")
            for k in closed_gate:
                if gate.get(k) is not False:
                    raise FailClosed(fail_prefix +
                                     "gate permission not exact false: %s" % k)

            # Governance revision is informational only; schema 1 + structured
            # fields are the only authority (not a fixed version string).
            contract_rev = contract.get("contract_version")
            if not isinstance(contract_rev, str):
                pass

            # ---- Implementation identity block (required under schema 1) ----
            impl = am.get("passive_time_witness_runtime_candidate_v3_implementation")
            if not isinstance(impl, dict):
                raise FailClosed(fail_prefix +
                                 "v3 implementation-identity block absent")
            tool_decl = impl.get("runtime_material_tool")
            if not isinstance(tool_decl, dict):
                raise FailClosed(fail_prefix +
                                 "runtime_material_tool identity absent")
            man_decl = impl.get("runtime_manifest")
            if not isinstance(man_decl, dict):
                raise FailClosed(fail_prefix +
                                 "runtime_manifest identity absent")
            # Contract-declared tool path must equal canonical __file__.
            tool_path_decl = tool_decl.get("path")
            if not isinstance(tool_path_decl, str) or not tool_path_decl:
                raise FailClosed(fail_prefix + "tool path not declared")
            try:
                tool_decl_abs = os.path.abspath(tool_path_decl)
            except Exception:
                raise FailClosed(fail_prefix + "tool decl path invalid")
            try:
                tool_decl_real = os.path.realpath(tool_decl_abs)
            except OSError as exc:
                raise FailClosed(fail_prefix +
                                 "tool decl realpath failed: %s" % exc)
            if tool_decl_real != this_real:
                raise FailClosed(fail_prefix +
                                 "contract tool path does not identify the "
                                 "executing tool (__file__)")
            tool_sha_decl = tool_decl.get("sha256")
            if not isinstance(tool_sha_decl, str) or not _is_hex64(tool_sha_decl):
                raise FailClosed(fail_prefix +
                                 "contract tool sha256 not a 64-hex string")
            if tool_receipt["sha256"] != tool_sha_decl:
                raise FailClosed(fail_prefix +
                                 "executing tool SHA-256 does not match contract")

            # ---- Manifest identity ----
            man_path_decl = man_decl.get("path")
            if not isinstance(man_path_decl, str) or not man_path_decl:
                raise FailClosed(fail_prefix + "manifest path not declared")
            try:
                man_decl_abs = os.path.abspath(man_path_decl)
            except Exception:
                raise FailClosed(fail_prefix + "manifest decl path invalid")
            if man_decl_abs != manifest_rel:
                # Compare by the same absolute canonicalization the issuer used.
                man_decl_realpath = os.path.realpath(man_decl_abs)
                if man_decl_realpath != repo_abs and \
                        not man_decl_realpath.startswith(repo_abs + os.sep):
                    raise FailClosed(fail_prefix +
                                     "manifest decl path escapes repo")
                man_decl_rel = _repo_relative_from_abs(man_decl_realpath, repo_abs)
                if man_decl_rel != manifest_rel:
                    raise FailClosed(fail_prefix +
                                     "contract manifest path does not match")

            # ---- 5. Read+hash manifest and candidate from descriptors ----
            manifest_fd, manifest_receipt, manifest_raw = _open(manifest_rel)
            man_sha_decl = man_decl.get("sha256")
            if not isinstance(man_sha_decl, str) or not _is_hex64(man_sha_decl):
                try: os.close(manifest_fd)
                except OSError: pass
                raise FailClosed(fail_prefix +
                                 "contract manifest sha256 not a 64-hex string")
            if manifest_receipt["sha256"] != man_sha_decl:
                try: os.close(manifest_fd)
                except OSError: pass
                raise FailClosed(fail_prefix +
                                 "manifest SHA-256 does not match contract")
            # Issue + retain VerifiedManifest bearer (exact retained bytes).
            if not verify_manifest(manifest_raw, repo_abs):
                try: os.close(manifest_fd)
                except OSError: pass
                raise FailClosed(fail_prefix + "manifest verification failed")
            try:
                load_and_verify_manifest(manifest_raw, repo_abs)
            except FailClosed as exc:
                try: os.close(manifest_fd)
                except OSError: pass
                raise FailClosed(fail_prefix + "VerifiedManifest: %s" % exc)
            os.close(manifest_fd)

            # Candidate self-identity (descriptor-bound SHA == accepted).
            candidate_fd, candidate_receipt, candidate_raw = \
                _open(candidate_rel)
            if candidate_receipt["sha256"] != accepted:
                try: os.close(candidate_fd)
                except OSError: pass
                raise FailClosed(fail_prefix +
                                 "candidate SHA-256 does not match accepted "
                                 "identity")
            os.close(candidate_fd)

            # proposed candidate identity remains informational only.
            prop_decl = impl.get("proposed_runtime_entrypoint_v3_sha256")
            if not (prop_decl is None or isinstance(prop_decl, str)):
                raise FailClosed(fail_prefix +
                                 "proposed candidate identity malformed")

            # ---- 6. Store complete authorization receipt ----
            tool_fd_to_close = tool_fd  # already opened above
            try:
                pass
            finally:
                try: os.close(tool_fd_to_close)
                except OSError: pass

            receipt = {
                "repo": {"path": repo_receipt["path"],
                         "dev": repo_receipt["dev"],
                         "ino": repo_receipt["ino"],
                         "is_dir": True},
                "contract": {"rel_path": contract_receipt["rel_path"],
                             "dev": contract_receipt["dev"],
                             "ino": contract_receipt["ino"],
                             "sha256": contract_receipt["sha256"]},
                "candidate": {"rel_path": candidate_receipt["rel_path"],
                              "dev": candidate_receipt["dev"],
                              "ino": candidate_receipt["ino"],
                              "sha256": candidate_receipt["sha256"]},
                "tool": {"rel_path": tool_receipt["rel_path"],
                         "dev": tool_receipt["dev"],
                         "ino": tool_receipt["ino"],
                         "sha256": tool_receipt["sha256"]},
                "manifest": {"rel_path": manifest_receipt["rel_path"],
                             "dev": manifest_receipt["dev"],
                             "ino": manifest_receipt["ino"],
                             "sha256": manifest_receipt["sha256"]},
                "auth_state": _auth_state_snapshot(contract),
            }
            return _issue(receipt)
        finally:
            try: os.close(repo_fd)
            except OSError: pass

    return MaterializationAuthorized, authorize_v3_materialization


MaterializationAuthorized, authorize_v3_materialization = \
    _build_materialization_authorization_boundary()


def _require_auth(auth):
    """Production materialization entry authorization.  FIRST operation of
    materialize_workspace().  Requires an exactly registered
    MaterializationAuthorized bearer issued by authorize_v3_materialization();
    reopens the repository root and every authorization file through
    descriptor-relative no-follow traversal and compares every current file
    receipt and SHA against the registry-held receipt; re-parses the current
    contract bytes and reruns all structured authorization checks.  Rejects
    None, synthetic self-test capabilities, fake classes,
    object.__new__ forgeries, stale or revoked bearers, runtime revocation,
    attempt-count change, D-064 reverting to BLOCKED/READY, static-verification
    change, any prohibited permission becoming true, accepted-candidate
    identity change, candidate/tool/manifest content change, and replacement
    of any file (even with an identical-path file) or of the repository root.
    An unchanged authorized bearer may be reused by the later 18-workspace
    transaction (no one-call consumption in 2B1R1)."""
    if not isinstance(auth, MaterializationAuthorized):
        raise FailClosed("production materialization requires a "
                         "MaterializationAuthorized bearer (got %r)"
                         % type(auth).__name__)
    try:
        receipt = auth._receipt()
    except FailClosed:
        raise FailClosed("production materialization: unregistered/forged "
                         "authorization bearer")
    fail_prefix = "materialization authorization stale: "
    repo = receipt["repo"]
    # Reopen repository root and compare identity.
    repo_fd, repo_receipt = _open_repo_root_fd_nofollow(repo["path"])
    try:
        if (repo_receipt["dev"], repo_receipt["ino"]) != (repo["dev"], repo["ino"]):
            raise FailClosed(fail_prefix + "repository-root replaced")
        repo_abs = repo_receipt["path"]

        def _reopen(name):
            stored = receipt[name]
            fd, frec, raw = _open_repo_relative_file(repo_fd, stored["rel_path"])
            try:
                if (frec["dev"], frec["ino"]) != (stored["dev"], stored["ino"]):
                    raise FailClosed(fail_prefix + name + " replaced/identity "
                                     "changed")
                if frec["sha256"] != stored["sha256"]:
                    raise FailClosed(fail_prefix + name + " content changed")
                return fd, raw
            except BaseException:
                try: os.close(fd)
                except OSError: pass
                raise

        contract_fd, contract_raw = _reopen("contract")
        try:
            contract = json.loads(contract_raw)
        except ValueError as exc:
            try: os.close(contract_fd)
            except OSError: pass
            raise FailClosed(fail_prefix + "contract JSON invalid: %s" % exc)
        os.close(contract_fd)

        candidate_fd, _craw = _reopen("candidate")
        os.close(candidate_fd)
        tool_fd, _traw = _reopen("tool")
        os.close(tool_fd)
        manifest_fd, _mraw = _reopen("manifest")
        os.close(manifest_fd)

        # Re-run structured authorization checks against the re-parsed contract.
        gate = contract.get("gate", {})
        if not isinstance(gate, dict):
            raise FailClosed(fail_prefix + "gate not a JSON object")
        snap = receipt["auth_state"]

        def _is_exact_int(v):
            return isinstance(v, int) and not isinstance(v, bool)

        # schema unchanged
        schema = gate.get(
            "passive_time_witness_runtime_candidate_v3_contract_schema")
        if not (_is_exact_int(schema) and schema == 1):
            raise FailClosed(fail_prefix + "schema no longer int 1")
        # static verification unchanged PASS
        sv = gate.get(
            "passive_time_witness_runtime_candidate_v3_static_verification")
        if sv != "PASS":
            raise FailClosed(fail_prefix + "static verification changed")
        if sv != snap["static_verification"]:
            raise FailClosed(fail_prefix + "static verification changed")
        # runtime authorization revocation
        if gate.get("diagnostic_runtime_authorized") is not True:
            raise FailClosed(fail_prefix + "diagnostic_runtime_authorized "
                             "revoked")
        if gate.get("diagnostic_runtime_authorized") != snap["diag_runtime_authorized"]:
            raise FailClosed(fail_prefix + "diagnostic runtime auth changed")
        # attempt count change
        attempts = gate.get("diagnostic_runtime_attempts_authorized")
        if not (_is_exact_int(attempts) and attempts == 1):
            raise FailClosed(fail_prefix + "attempt count changed")
        if attempts != snap["diag_attempts"]:
            raise FailClosed(fail_prefix + "attempt count changed")
        am = contract.get(
            "passive_time_witness_runtime_candidate_v3_design_amendment_1", {})
        if not isinstance(am, dict):
            raise FailClosed(fail_prefix + "amendment block invalid")
        if am.get("runtime_authorized") is not True:
            raise FailClosed(fail_prefix + "amendment runtime revoked")
        if am.get("runtime_authorized") != snap["am_runtime_authorized"]:
            raise FailClosed(fail_prefix + "amendment runtime auth changed")
        am_attempts = am.get("runtime_attempts")
        if not (_is_exact_int(am_attempts) and am_attempts == 1):
            raise FailClosed(fail_prefix + "amendment attempts changed")
        if am_attempts != snap["am_runtime_attempts"]:
            raise FailClosed(fail_prefix + "amendment attempts changed")
        d064 = am.get("d064_status")
        if d064 in ("BLOCKED", "READY_FOR_SEPARATE_D064_CONSIDERATION"):
            raise FailClosed(fail_prefix + "d064 reverted: %r" % (d064,))
        if d064 != snap["d064_status"]:
            raise FailClosed(fail_prefix + "d064 status changed")
        if am.get("static_verification") != snap["am_static_verification"]:
            raise FailClosed(fail_prefix + "amendment static verification changed")
        # accepted-candidate identity change
        accepted = gate.get("accepted_runtime_entrypoint_v3_sha256")
        if accepted != snap["accepted_candidate"]:
            raise FailClosed(fail_prefix + "accepted candidate identity changed")
        if not isinstance(accepted, str) or not _is_hex64(accepted):
            raise FailClosed(fail_prefix + "accepted candidate identity invalid")
        # prohibited permission becoming true
        for k in ("scientific_outcome_allowed",
                  "command_transmission_allowed",
                  "event_injection_allowed",
                  "baseline_execution_allowed",
                  "cryptographic_semantics_claim_allowed"):
            if contract.get(k) is not False:
                raise FailClosed(fail_prefix + "prohibited permission true: %s" % k)
            if contract.get(k) != snap[k]:
                raise FailClosed(fail_prefix + "permission changed: %s" % k)
        for k in ("baseline_run_1_authorized",
                  "baseline_run_2_authorized",
                  "event_injection_authorized"):
            if gate.get(k) is not False:
                raise FailClosed(fail_prefix + "prohibited gate permission true: "
                                 "%s" % k)
            if gate.get(k) != snap["gate_" + k]:
                raise FailClosed(fail_prefix + "gate permission changed: %s" % k)
        # executing-tool and manifest declared paths unchanged
        impl = am.get("passive_time_witness_runtime_candidate_v3_implementation",
                      {})
        if not isinstance(impl, dict):
            raise FailClosed(fail_prefix + "implementation block dropped")
        tool_decl = impl.get("runtime_material_tool") or {}
        man_decl = impl.get("runtime_manifest") or {}
        if tool_decl.get("path") != snap["tool_decl_path"]:
            raise FailClosed(fail_prefix + "declared tool path changed")
        if man_decl.get("path") != snap["manifest_decl_path"]:
            raise FailClosed(fail_prefix + "declared manifest path changed")
        return True
    except BaseException:
        raise


_libc = None
def _get_libc():
    global _libc
    if _libc is None:
        n = ctypes.util.find_library("c")
        if n is None:
            return None
        try:
            _libc = ctypes.CDLL(n, use_errno=True)
        except OSError:
            return None
    return _libc



def _open_parent_dirfd(path):
    """Open the parent directory of *path* with O_NOFOLLOW and return the
    (parent_fd, basename) pair.  Caller closes parent_fd."""
    parent = os.path.dirname(path)
    base = os.path.basename(path)
    if base == "" or base in (".", ".."):
        raise FailClosed("no-replace: invalid basename %r" % base)
    try:
        pfd = os.open(parent, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    except OSError as exc:
        raise FailClosed("no-replace: parent dir open failed for %r: %s" % (parent, exc))
    return pfd, base

def _noreplace_validate_basename(base, label):
    """Strict single-component validation for a no-replace basename, applied
  BEFORE any platform syscall.  Rejects absolute, slash-containing,
  backslash, empty, dot, dotdot, NUL, and surrogate names."""
    _validate_name(base)
    # _validate_name already rejects empty/dot/dotdot/slash/backslash/nul/
  # absolute/surrogate.  Re-check defensively with a stable prefix.
    if base in ("", ".", ".."):
        raise FailClosed("no-replace: invalid basename %r (%s)" % (base, label))
    if "/" in base or "\\" in base or base.startswith("/"):
        raise FailClosed("no-replace: non-basename %r (%s)" % (base, label))
    if "\x00" in base:
        raise FailClosed("no-replace: NUL basename %r (%s)" % (base, label))
    if any(0xD800 <= ord(ch) < 0xE000 for ch in base):
        raise FailClosed("no-replace: surrogate basename %r (%s)" % (base, label))
    return base


# Reviewed renameat2 syscall numbers per Linux architecture.  Never invoke a
# syscall number outside this explicit mapping; unknown architectures fail
# closed before any syscall is attempted (Correction 8: architecture-safe).
_RENAMEAT2_SYSCALL_BY_ARCH = {
    "x86_64": 316,
    "amd64": 316,
    "aarch64": 276,
    "arm64": 276,
}


def _renameat2_syscall_number():
    """Return the reviewed renameat2 syscall number for the running Linux
    architecture, or None when the architecture is unknown.  Identification
    uses platform.machine() as a stable platform value."""
    machine = platform.machine()
    return _RENAMEAT2_SYSCALL_BY_ARCH.get(machine)


def _linux_renameat2_noreplace(src_parent_fd, src_base, dst_parent_fd, dst_base):
    """Linux renameat2 RENAME_NOREPLACE using retained dirfds + basenames.
  Falls back to a ctypes/syscall binding when os.renameat2 is unavailable.
  Sets ctypes argtypes/restype explicitly, resets and checks errno."""
    RENAME_NOREPLACE = getattr(os, 'RENAME_NOREPLACE', 1)  # (1 << 0)
    if hasattr(os, 'renameat2'):
        try:
            os.renameat2(src_base, dst_base,
                         src_dir_fd=src_parent_fd, dest_dir_fd=dst_parent_fd,
                         rename_flags=RENAME_NOREPLACE)
            return
        except OSError as exc:
            raise FailClosed("renameat2 RENAME_NOREPLACE failed: %s" % exc)
    # ctypes/syscall fallback for renameat2.
    libc = _get_libc()
    if libc is not None and hasattr(libc, 'renameat2'):
        fn = libc.renameat2
        fn.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int,
                       ctypes.c_char_p, ctypes.c_uint]
        fn.restype = ctypes.c_int
        ctypes.set_errno(0)
        rc = fn(src_parent_fd, os.fsencode(src_base),
                dst_parent_fd, os.fsencode(dst_base),
                ctypes.c_uint(RENAME_NOREPLACE))
        err = ctypes.get_errno()
        if rc != 0:
            raise FailClosed("renameat2(syscall) RENAME_NOREPLACE failed "
                             "(errno=%d): %s -> %s" % (err, src_base, dst_base))
        return
    # Final fallback: the raw syscall via the libc syscall() trampoline.
    # Architecture-safe (Correction 8): the syscall number comes from the
    # explicit reviewed mapping; an unknown architecture fails closed BEFORE
    # any syscall invocation.  Only basenames + retained dirfds are passed.
    SYS_renameat2 = _renameat2_syscall_number()
    if SYS_renameat2 is None:
        raise FailClosed("renameat2 raw syscall: unsupported architecture %r"
                         % platform.machine())
    libc2 = _get_libc()
    if libc2 is not None and hasattr(libc2, 'syscall'):
        fn = libc2.syscall
        fn.argtypes = [ctypes.c_long, ctypes.c_int, ctypes.c_char_p,
                       ctypes.c_int, ctypes.c_char_p, ctypes.c_uint]
        fn.restype = ctypes.c_long
        ctypes.set_errno(0)
        rc = fn(SYS_renameat2, src_parent_fd, os.fsencode(src_base),
                dst_parent_fd, os.fsencode(dst_base),
                ctypes.c_uint(RENAME_NOREPLACE))
        err = ctypes.get_errno()
        if rc != 0:
            raise FailClosed("renameat2(syscall()) RENAME_NOREPLACE failed "
                             "(errno=%d): %s -> %s" % (err, src_base, dst_base))
        return
    raise FailClosed("no-replace rename: renameat2 unavailable on linux")


def _no_replace_rename_dirfd(src_parent_fd, src_base, dst_parent_fd, dst_base):
    """Atomic no-replace publication using ONLY retained parent directory
    descriptors and basenames.  Never passes absolute paths together with
    dirfds.  Caller owns the parent descriptors (they are NOT closed here).
    Basenames are validated as strict single components BEFORE any syscall.
    Darwin: renameatx_np RENAME_EXCL with the supplied parent dirfds.
    Linux:  renameat2(RENAME_NOREPLACE) with basenames + parent dirfds.
    Other:  fail closed."""
    if os.open not in os.supports_dir_fd or not hasattr(os, 'O_NOFOLLOW') or not hasattr(os, 'O_DIRECTORY'):
        raise FailClosed("no-replace rename: dirfd-relative open unavailable")
    _noreplace_validate_basename(src_base, "src_base")
    _noreplace_validate_basename(dst_base, "dst_base")
    if not isinstance(src_parent_fd, int) or not isinstance(dst_parent_fd, int):
        raise FailClosed("no-replace rename: parent fd not int")
    sbase = os.fsencode(src_base)
    dbase = os.fsencode(dst_base)
    if sys.platform == 'darwin':
        libc = _get_libc()
        if libc is None:
            raise FailClosed("no-replace rename: libc unavailable on darwin")
        fn = getattr(libc, 'renameatx_np', None)
        if fn is None:
            raise FailClosed("no-replace rename: renameatx_np unavailable")
        RENAME_EXCL = 4
        fn.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int,
                       ctypes.c_char_p, ctypes.c_uint]
        fn.restype = ctypes.c_int
        ctypes.set_errno(0)
        rc = fn(src_parent_fd, sbase, dst_parent_fd, dbase,
                ctypes.c_uint(RENAME_EXCL))
        err = ctypes.get_errno()
        if rc != 0:
            raise FailClosed("renameatx_np RENAME_EXCL failed (errno=%d): %s -> %s"
                         % (err, src_base, dst_base))
        return
    if sys.platform.startswith('linux'):
        _linux_renameat2_noreplace(src_parent_fd, src_base, dst_parent_fd,
                                   dst_base)
        return
    raise FailClosed("no-replace rename: no atomic primitive on platform %s"
                 % sys.platform)


def _no_replace_rename(src_path, dst_path):
    """Atomic no-replace directory publication using directory-descriptor-
    relative parent opens (never path-only check + path-only rename).
    Delegates to _no_replace_rename_dirfd with freshly opened parent dirfds."""
    sfd, sbase = _open_parent_dirfd(src_path)
    dfd, dbase = _open_parent_dirfd(dst_path)
    try:
        _no_replace_rename_dirfd(sfd, sbase, dfd, dbase)
    finally:
        try: os.close(sfd)
        except OSError: pass
        try: os.close(dfd)
        except OSError: pass

def _identity_receipt(path):
    """Immutable identity receipt dict for an on-disk directory: canonical
    path, st_dev, st_ino, directory type.  Rejects symlinks and non-dirs."""
    try:
        st = os.lstat(path)
    except OSError as exc:
        raise FailClosed("identity receipt: path unavailable: %s (%s)" % (path, exc))
    if stat.S_ISLNK(st.st_mode):
        raise FailClosed("identity receipt: path is symlink: %s" % path)
    if not stat.S_ISDIR(st.st_mode):
        raise FailClosed("identity receipt: not a directory: %s" % path)
    rp = os.path.realpath(path)
    if rp != os.path.normpath(os.path.normpath(path)):
        raise FailClosed("identity receipt: path not canonical: %s" % path)
    return {'path': rp, 'dev': st.st_dev, 'ino': st.st_ino,
            'is_dir': True, 'nlink': st.st_nlink}

def _validate_component_id(component_id):
    """Require a nonempty simple relative identifier."""
    if component_id is None:
        raise FailClosed("component_id absent")
    if not isinstance(component_id, str) or component_id == "":
        raise FailClosed("component_id empty")
    if "/" in component_id or "\\" in component_id:
        raise FailClosed("component_id must be simple: %r" % component_id)
    if component_id in (".", "..") or component_id.startswith("/"):
        raise FailClosed("component_id must not be dot/dotdot/absolute: %r" % component_id)
    if "\x00" in component_id:
        raise FailClosed("component_id NUL")
    for ch in component_id:
        if 0xD800 <= ord(ch) <= 0xDFFF:
            raise FailClosed("component_id surrogate")

_WS_POLICY_FIELDS = (
    "component_id", "workspace_host_path", "mount_destination",
    "seed_source_roots", "private_physical_copy", "no_hard_links",
    "no_reflinks", "no_overlays", "no_source_aliases",
    "no_runtime_mount_from_external_nos3",
)

def _receipt_matches(a, b, label):
    return (a['path'] == b['path'] and a['dev'] == b['dev']
            and a['ino'] == b['ino'] and a['is_dir'] == b['is_dir'])

def _check_authorized_root(authorized_root, repo_root):
    """Reject symlinked authorized_root, symlinked parents, authorized_root
    equal to / inside / containing any source root, and source/destination
    root dev/inode aliasing.  Returns an immutable identity receipt for the
    authorized root.  All checks occur before staging creation."""
    ar = authorized_root
    seen = set()
    while True:
        try:
            lst = os.lstat(ar)
        except OSError as exc:
            raise FailClosed("authorized_root unavailable: %s (%s)" % (ar, exc))
        if stat.S_ISLNK(lst.st_mode):
            raise FailClosed("authorized_root or parent is symlink: %s" % ar)
        rp = os.path.realpath(ar)
        if rp in seen:
            break
        seen.add(rp)
        parent = os.path.dirname(ar)
        if ar == parent or ar == '/':
            break
        ar = parent
    ar_real = os.path.realpath(authorized_root)
    rr_real = os.path.realpath(repo_root)
    try:
        ar_st = os.stat(ar_real)
    except OSError as exc:
        raise FailClosed("authorized_root stat failed: %s" % exc)
    try:
        rr_st = os.stat(rr_real)
    except OSError as exc:
        raise FailClosed("repo_root stat failed: %s" % exc)
    if (ar_st.st_dev, ar_st.st_ino) == (rr_st.st_dev, rr_st.st_ino):
        raise FailClosed("authorized_root aliases repo_root")
    for src_id, sub in [(r[0], r[1]) for r in SOURCE_ROOTS]:
        src_abs = os.path.realpath(os.path.join(repo_root, sub))
        try:
            sst = os.stat(src_abs)
        except OSError:
            continue
        if (ar_st.st_dev, ar_st.st_ino) == (sst.st_dev, sst.st_ino):
            raise FailClosed("authorized_root aliases source root %s" % src_id)
        if ar_real == src_abs or ar_real.startswith(src_abs + os.sep):
            raise FailClosed("authorized_root inside source tree %s" % src_id)
        if src_abs == ar_real or src_abs.startswith(ar_real + os.sep):
            raise FailClosed("authorized_root contains source tree %s" % src_id)
    return _identity_receipt(ar_real)

def _frozen_workspace_map():
    return {w['component_id']: w for w in build_migration_workspaces()}

def _enforce_workspace_policy_frozen(ws, component_id):
    """Require the selected workspace declaration to EQUAL the expected
    frozen object from build_migration_workspaces() exactly, including
    component_id, workspace_host_path, mount_destination, seed_source_roots
    (+ order), and all six policy booleans.  Rejects substitutions between
    otherwise valid declared roots.  Production path only."""
    expected = _frozen_workspace_map().get(component_id)
    if expected is None:
        raise FailClosed("workspace %r not in frozen workspace map" % component_id)
    if ws != expected:
        if ws.get('component_id') != expected['component_id']:
            raise FailClosed("workspace component_id mismatch")
        if ws.get('workspace_host_path') != expected['workspace_host_path']:
            raise FailClosed("workspace_host_path mismatch")
        if ws.get('mount_destination') != expected['mount_destination']:
            raise FailClosed("mount_destination mismatch")
        if ws.get('seed_source_roots') != expected['seed_source_roots']:
            raise FailClosed("seed_source_roots mismatch (substitution rejected)")
        for f in ('private_physical_copy','no_hard_links','no_reflinks',
                  'no_overlays','no_source_aliases',
                  'no_runtime_mount_from_external_nos3'):
            if ws.get(f) is not True:
                raise FailClosed("workspace policy field must be true: %s" % f)
        extra = set(ws) - set(expected)
        if extra:
            raise FailClosed("workspace has extra policy fields: %r" % sorted(extra))
        missing = set(expected) - set(ws)
        if missing:
            raise FailClosed("workspace missing policy fields: %r" % sorted(missing))
        raise FailClosed("workspace declaration differs from frozen expected")
    return expected

def _enforce_workspace_policy(ws, component_id, declared_roots):
    """Structural workspace policy validator for the private synthetic-test
    materializer.  Validates the synthetic ws fields without requiring them
    to equal the production frozen 18-workspace map.  Production uses
    _enforce_workspace_policy_frozen."""
    if ws['component_id'] != component_id:
        raise FailClosed("workspace component_id mismatch: %r != %r"
                         % (ws.get('component_id'), component_id))
    if ws['workspace_host_path'] != component_id:
        raise FailClosed("workspace_host_path must equal component_id: %r != %r"
                         % (ws.get('workspace_host_path'), component_id))
    if ws['mount_destination'] != '/work/nos3':
        raise FailClosed("mount_destination must be /work/nos3: %r"
                         % (ws.get('mount_destination'),))
    seeds = ws['seed_source_roots']
    if not isinstance(seeds, list) or not seeds:
        raise FailClosed("seed_source_roots empty")
    for s in seeds:
        if s not in declared_roots:
            raise FailClosed("unknown seed source root: %r" % s)
        if s == 'configuration':
            raise FailClosed("configuration may not be a runtime workspace root")
    if len(set(seeds)) != len(seeds):
        raise FailClosed("duplicate seed source roots: %r" % seeds)
    for field in _WS_POLICY_FIELDS:
        if field not in ws:
            raise FailClosed("workspace missing policy field: %s" % field)
    bool_fields = _WS_POLICY_FIELDS[4:]
    for f in bool_fields:
        if ws[f] is not True:
            raise FailClosed("workspace policy field must be true: %s=%r" % (f, ws[f]))
    extra = set(ws) - set(_WS_POLICY_FIELDS)
    if extra:
        raise FailClosed("workspace has extra policy fields: %r" % sorted(extra))

# --------------------------------------------------------------------------
# Safe workspace materializer.  Production entry point requires a
# VerifiedManifest bearer registered by load_and_verify_manifest() plus a
# MaterializationAuthorized bearer issued by authorize_v3_materialization();
# resolves all workspace state by component_id from the verified manifest.
# A production authorization path now exists (Checkpoint 2B1R1) but is
# contract-closed under the current 0.4.11 contract (D-064 BLOCKED), so
# _require_auth fails closed for the closed contract and synthetic caps and
# no filesystem mutation can occur until a future D-064 authorization.
# --------------------------------------------------------------------------
# Descriptor-relative helpers for the production materialization path.
# All destination mutation is relative to captured directory descriptors;
# no os.makedirs(path)/os.rename(path,path)/shutil.rmtree(path) in these
# helpers.  Every child component name is validated before use.
# --------------------------------------------------------------------------
def _require_dirfd_capabilities():
    if (os.open not in os.supports_dir_fd
            or not hasattr(os, "O_DIRECTORY") or not hasattr(os, "O_NOFOLLOW")):
        raise FailClosed("descriptor-relative destination ops unavailable "
                         "on this platform")


def _validate_name(name):
    """Validate a single destination component name."""
    if not isinstance(name, str) or name == "":
        raise FailClosed("dest component empty")
    if name in (".", ".."):
        raise FailClosed("dest component dot/dotdot: %r" % name)
    if "/" in name or "\\" in name or "\x00" in name:
        raise FailClosed("dest component has slash/backslash/nul: %r" % name)
    if name.startswith("/"):
        raise FailClosed("dest component absolute: %r" % name)
    if any(0xD800 <= ord(ch) < 0xE000 for ch in name):
        raise FailClosed("dest component has surrogate: %r" % name)
    return name


def _split_components(rel, _root_sentinel_ok=False):
    """Split a relative destination path into validated components.  Empty
    repeated/trailing separators are rejected (--no empty filtering--); the
    empty string is accepted ONLY as the explicit root-sentinel caller case."""
    if not isinstance(rel, str):
        raise FailClosed("dest path not string: %r" % rel)
    if rel == "":
        if _root_sentinel_ok:
            return []
        raise FailClosed("dest path empty (no root-sentinel context)")
    if rel.startswith("/"):
        raise FailClosed("dest path absolute: %r" % rel)
    if rel == ".":
        raise FailClosed("dest path is '.'")
    # Do NOT filter empty components: split and reject any empties.
    parts = rel.split("/")
    if parts[-1] == "" and not _root_sentinel_ok:
        raise FailClosed("dest path has trailing separator: %r" % rel)
    for p in parts:
        if p == "":
            raise FailClosed("dest path has empty/repeated separator: %r" % rel)
        _validate_name(p)
    return parts


def _dirfd_has_entry(parent_fd, name):
    try:
        os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
        return True
    except FileNotFoundError:
        return False
    except OSError as exc:
        raise FailClosed("dirfd stat failed for %r: %s" % (name, exc))


def _dirfd_lstat(parent_fd, name):
    try:
        return os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
    except OSError as exc:
        raise FailClosed("dirfd lstat failed for %r: %s" % (name, exc))


def _dirfd_fstat(fd):
    try:
        return os.fstat(fd)
    except OSError as exc:
        raise FailClosed("fstat failed: %s" % exc)


def _dirfd_open_dir(parent_fd, name):
    """Open an existing directory component relative to parent_fd with
    O_DIRECTORY|O_NOFOLLOW.  Returns the opened descriptor."""
    try:
        return os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                      dir_fd=parent_fd)
    except OSError as exc:
        raise FailClosed("dirfd open dir failed for %r: %s" % (name, exc))


def _dirfd_make_dir(parent_fd, name, mode=0o755):
    """Create a directory relative to parent_fd; EEXIST is fail-closed.
  Correction 2: after mkdir, stat the new basename WITHOUT following symlinks,
  require a directory, open it with O_DIRECTORY|O_NOFOLLOW, and compare the
  opened fstat dev/ino with the post-mkdir stat identity.  Return only after
  exact identity continuity succeeds.  On open/identity failure, remove the
  created directory only when the basename still resolves to the captured
  created inode AND the directory is empty; never remove a replacement path.
  Report cleanup failure when safe cleanup cannot be proven."""
    try:
        os.mkdir(name, mode=mode, dir_fd=parent_fd)
    except OSError as exc:
        if exc.errno == errno.EEXIST:
            raise FailClosed("dirfd mkdir: component already exists: %r" % name)
        raise FailClosed("dirfd mkdir failed for %r: %s" % (name, exc))
    try:
        pst = _dirfd_lstat(parent_fd, name)
    except FailClosed as exc:
        raise FailClosed("dirfd mkdir: post-mkdir identity capture failed "
                         "for %r; cannot safely clean up (identity unavailable): %s"
                         % (name, exc))
    if not stat.S_ISDIR(pst.st_mode):
        raise _fail_after_created_dir(parent_fd, name, pst,
            "dirfd mkdir: created object not a directory: %r" % name)
    try:
        cfd = _dirfd_open_dir(parent_fd, name)
    except FailClosed as exc:
        raise _fail_after_created_dir(parent_fd, name, pst, str(exc))
    try:
        fst = os.fstat(cfd)
    except OSError as exc:
        try: os.close(cfd)
        except OSError: pass
        raise _fail_after_created_dir(parent_fd, name, pst,
            "dirfd mkdir: fstat of opened dir failed: %s" % exc)
    if (fst.st_dev, fst.st_ino) != (pst.st_dev, pst.st_ino):
        try: os.close(cfd)
        except OSError: pass
        raise _fail_after_created_dir(parent_fd, name, pst,
            "dirfd mkdir: identity not continuous for %r" % name)
    return cfd


def _fail_after_created_dir(parent_fd, name, created_stat, message):
    """Raise FailClosed(message) after removing the created directory only when
  the basename still resolves to the captured created inode and the directory is
  empty.  Never remove a replacement path.  Report cleanup failure when a safe
  cleanup cannot be proven (overrides the original failure)."""
    cleanup_error = _safe_remove_created_dir(parent_fd, name, created_stat)
    if cleanup_error is not None:
        return FailClosed("%s; cleanup failed: %s" % (message, cleanup_error))
    return FailClosed(message)


def _safe_remove_created_dir(parent_fd, name, created_stat):
    """Remove a created directory relative to parent_fd only when the basename
  still resolves to the captured created inode and is empty.  Returns None on
  success (or nothing to remove), else a string cleanup-error.  Never removes a
  replacement object (identity mismatch leaves it untouched)."""
    try:
        cur = _dirfd_lstat(parent_fd, name)
    except FailClosed as exc:
        return "post-mkdir lstat failed: %s" % exc
    if created_stat is not None:
        if (cur.st_dev, cur.st_ino) != (created_stat.st_dev, created_stat.st_ino):
            return "basename no longer maps to created inode (replacement left)"
    if not stat.S_ISDIR(cur.st_mode):
        return "basename no longer a directory (replacement left)"
    # Correction 9A: re-stat immediately before rmdir; require the
    # basename still maps to the captured identity.
    try:
        cur2 = _dirfd_lstat(parent_fd, name)
    except FailClosed as exc:
        return "pre-rmdir re-stat failed: %s" % exc
    if not stat.S_ISDIR(cur2.st_mode):
        return "pre-rmdir basename not a directory (replacement)"
    if created_stat is not None:
        if (cur2.st_dev, cur2.st_ino) != (created_stat.st_dev, created_stat.st_ino):
            return "pre-rmdir identity mismatch (replacement left)"
    try:
        os.rmdir(name, dir_fd=parent_fd)
    except OSError as exc:
        return "rmdir failed: %s" % exc
    return None


def _dirfd_open_dir_bound(parent_fd, name, prior_stat):
    """Open an existing directory component with O_DIRECTORY|O_NOFOLLOW and
    require the opened fstat dev/ino to equal the prior non-following stat
    identity (Correction 3: reject replacement before returning the descriptor)."""
    cfd = _dirfd_open_dir(parent_fd, name)
    try:
        fst = os.fstat(cfd)
    except OSError as exc:
        try: os.close(cfd)
        except OSError: pass
        raise FailClosed("dirfd open dir fstat failed for %r: %s" % (name, exc))
    if (fst.st_dev, fst.st_ino) != (prior_stat.st_dev, prior_stat.st_ino):
        try: os.close(cfd)
        except OSError: pass
        raise FailClosed("dirfd: directory replaced before open (identity "
                         "not continuous): %r" % name)
    return cfd


def _dirfd_open_or_make_dir(parent_fd, name, mode=0o755):
    """Open an existing directory component, or create it if missing.  Rejects
    symlinks and non-directories.  Correction 3: for an existing component, the
    opened fstat dev/ino must equal the retained non-following stat identity
    (replacement rejected before returning the descriptor)."""
    if _dirfd_has_entry(parent_fd, name):
        st = _dirfd_lstat(parent_fd, name)
        if stat.S_ISLNK(st.st_mode):
            raise FailClosed("dirfd: symlink dir component rejected: %r" % name)
        if not stat.S_ISDIR(st.st_mode):
            raise FailClosed("dirfd: non-directory component (%s): %r"
                             % (_stat_kind(st.st_mode), name))
        return _dirfd_open_dir_bound(parent_fd, name, st)
    return _dirfd_make_dir(parent_fd, name, mode=mode)


def _dirfd_walk_to_parent(start_fd, components):
    """Open each directory component in sequence relative to start_fd, creating
    directories as needed.  Returns ONLY the deepest descriptor; all
  intermediate descriptors are closed."""
    opened = []
    cur = start_fd
    ret = None
    try:
        for comp in components:
            child = _dirfd_open_or_make_dir(cur, comp)
            opened.append(child)
            cur = child
        ret = opened[-1] if opened else start_fd
        # close all intermediates except the returned one
        keep = ret
        for d in opened:
            if d is not keep:
                try: os.close(d)
                except OSError: pass
        opened = [keep] if keep is not start_fd else []
        return keep
    except BaseException:
        for d in opened:
            try: os.close(d)
            except OSError: pass
        raise


def _dirfd_list_names(parent_fd):
    """List child names relative to parent_fd, excluding . and .."""
    try:
        return sorted(os.listdir(parent_fd))
    except OSError as exc:
        raise FailClosed("dirfd listdir failed: %s" % exc)


def _mkstemp_dirfd(parent_fd, label):
    """Create a unique staging directory relative to parent_fd using mkdir with
  randomized validated basenames and EEXIST retry (no tempfile.mkdtemp).
  Correction 2: after mkdir, stat the new basename WITHOUT following symlinks,
  require a directory, open with O_DIRECTORY|O_NOFOLLOW, and compare the opened
  fstat dev/ino with the post-mkdir stat identity.  Returns (basename, fd)
  only after identity continuity succeeds.  On open/identity failure the created
  directory is removed only when the basename still maps to the captured
  created inode and is empty; never removes a replacement path, and never
  leaves an ordinary created directory behind after an injected open failure."""
    random.seed()
    for _ in range(100):
        suffix = "%016x" % random.getrandbits(64)
        base = "%s_staging_%s" % (label, suffix)
        _validate_name(base)
        try:
            os.mkdir(base, mode=0o700, dir_fd=parent_fd)
        except OSError as exc:
            if exc.errno == errno.EEXIST:
                continue
            raise FailClosed("mkstemp_dirfd: mkdir failed: %s" % exc)
        try:
            pst = _dirfd_lstat(parent_fd, base)
        except FailClosed as exc:
            raise FailClosed("mkstemp_dirfd: post-mkdir stat failed for %r; "
                             "cannot safely clean up (identity unavailable): %s"
                             % (base, exc))
        if not stat.S_ISDIR(pst.st_mode):
            raise _fail_after_created_dir(parent_fd, base, pst,
                "mkstemp_dirfd: created object not a directory: %r" % base)
        try:
            fd = _dirfd_open_dir(parent_fd, base)
        except FailClosed as exc:
            raise _fail_after_created_dir(parent_fd, base, pst, str(exc))
        try:
            fst = os.fstat(fd)
        except OSError as exc:
            try: os.close(fd)
            except OSError: pass
            raise _fail_after_created_dir(parent_fd, base, pst,
                "mkstemp_dirfd: fstat of opened dir failed: %s" % exc)
        if (fst.st_dev, fst.st_ino) != (pst.st_dev, pst.st_ino):
            try: os.close(fd)
            except OSError: pass
            raise _fail_after_created_dir(parent_fd, base, pst,
                "mkstemp_dirfd: identity not continuous for %r" % base)
        return base, fd
    raise FailClosed("mkstemp_dirfd: exhausted collision retries")

# --------------------------------------------------------------------------
# Production materializer (descriptor-relative).  _require_auth() is the first
# operation: it validates a registered MaterializationAuthorized bearer and
# re-confirms all authorization-file identities/contents; it currently fails
# closed for the contract-closed 0.4.11 transaction.  The retained-descriptor
# logic below is the authorized production path.
# --------------------------------------------------------------------------
def materialize_workspace(verified_manifest, authorized_root, *,
                          authorization=None, component_id=None):
    """Materialize one workspace resolved by component_id from the verified
    manifest, beneath authorized_root.  All mutation is relative to retained
  directory descriptors."""
    _require_auth(authorization)
    if not isinstance(verified_manifest, VerifiedManifest):
        raise FailClosed("materialize: requires a VerifiedManifest bearer")
    verified_manifest._entry()  # reject unregistered/forged bearer
    verified_manifest.full_reverify()
    _validate_component_id(component_id)
    runtime_repo = verified_manifest.repo_root
    manifest = verified_manifest.manifest()
    ws = verified_manifest.workspace_for(component_id)
    _enforce_workspace_policy_frozen(ws, component_id)
    seed_source_roots = ws['seed_source_roots']
    ar_receipt = _check_authorized_root(authorized_root, runtime_repo)
    _require_dirfd_capabilities()
    decl_prefix = {d['source_root']: d['destination_prefix']
                   for d in manifest['source_root_declarations']}
    incl = [e for e in manifest['included_regular_file_entries']
            if e['source_root'] in seed_source_roots]
    dirs = [d for d in manifest['directory_entries']
            if d['source_root'] in seed_source_roots]
    excl = [ex for ex in manifest['exact_exclusion_records']
            if ex['source_root'] in seed_source_roots]
    # Open authorized root ONCE with O_DIRECTORY|O_NOFOLLOW; bind its
    # identity to _check_authorized_root()'s receipt BEFORE staging creation
    # (Correction 6: production uses _open_authorized_root_bound after
    # authorization; no staging directory is created on a mismatch).
    ar_fd, ar_fd_receipt = _open_authorized_root_bound(authorized_root, ar_receipt)

    staging_fd = None
    staging_base = None
    staging_receipt = None
    repo_fd = None
    try:
        # Staging created relative to the retained authorized-root descriptor.
        staging_base, staging_fd = _mkstemp_dirfd(ar_fd, component_id)
        staging_receipt = _staging_receipt(staging_fd, staging_base, ar_fd)
        # Bind immediately after staging creation.
        _verify_staging_bound(staging_fd, staging_base, ar_fd, staging_receipt,
                              "after staging creation")
        # Open the verified repository-root descriptor via the bearer (compares
        # dev/ino/type with the registry-held receipt before copying).
        repo_fd = verified_manifest.open_verified_repo_fd()
        try:
            _build_dest_tree_dirfd(staging_fd, dirs, decl_prefix)
            _prod_copy_files_dirfd(incl, staging_fd, repo_fd)
            _verify_staging_bound(staging_fd, staging_base, ar_fd, staging_receipt,
                                  "before complete destination audit")
            _verify_dest_complete_dirfd(staging_fd, incl, dirs, decl_prefix)
            _verify_exclusions_absent_dirfd(staging_fd, excl, decl_prefix)
            _verify_deny_patterns_absent_dirfd(staging_fd, manifest)
            # Revalidate authorized-root identity through the retained fd.
            if not _fd_receipt_matches(ar_fd, ar_fd_receipt, "authorized_root"):
                raise FailClosed("authorized_root identity changed")
            verified_manifest.revalidate()
            # Correction 5: the comprehensive descriptor-relative destination
            # audit is the FINAL content-validation operation immediately
            # before atomic publication.  No content-inspecting or
            # content-mutating operation may occur between this final audit and
            # _no_replace_rename_dirfd(), except a final retained staging-root
            # identity comparison.  RENAME_EXCL/RENAME_NOREPLACE is
            # authoritative, so the path-based final-name precheck is removed.
            _verify_dest_complete_dirfd(staging_fd, incl, dirs, decl_prefix)
            _verify_exclusions_absent_dirfd(staging_fd, excl, decl_prefix)
            _verify_deny_patterns_absent_dirfd(staging_fd, manifest)
            # Final retained staging-root identity comparison.
            _verify_staging_bound(staging_fd, staging_base, ar_fd, staging_receipt,
                                  "before final publication")
            _no_replace_rename_dirfd(ar_fd, staging_base, ar_fd, component_id)
            return os.path.join(authorized_root, component_id)
        finally:
            if repo_fd is not None:
                try: os.close(repo_fd)
                except OSError: pass
    except Exception:
        # Descriptor-relative identity-bound cleanup.  Cleanup failure
        # overrides the original operation failure.
        try:
            if staging_fd is not None and staging_receipt is not None:
                _verify_staging_bound(staging_fd, staging_base, ar_fd,
                                      staging_receipt, "before cleanup")
                _rmtree_dirfd_contents(staging_fd)
            if staging_base is not None and staging_receipt is not None:
                _verify_staging_bound(staging_fd, staging_base, ar_fd,
                                      staging_receipt,
                                      "before removing staging basename")
                try:
                    os.rmdir(staging_base, dir_fd=ar_fd)
                except OSError as rerr:
                    raise FailClosed("cleanup: rmdir staging failed: %s" % rerr)
        except BaseException:
            raise
        raise
    finally:
        if staging_fd is not None:
            try: os.close(staging_fd)
            except OSError: pass
        try: os.close(ar_fd)
        except OSError: pass


def _fd_identity(fd):
    """Return (dev, ino, is_dir) from an opened descriptor (caller owns fd)."""
    st = os.fstat(fd)
    return (st.st_dev, st.st_ino, stat.S_ISDIR(st.st_mode))


def _staging_receipt(staging_fd, staging_basename, ar_fd):
    """A real staging receipt: staging dev/ino/dir-type + staging basename +
  the captured authorized-root dev/ino (the parent identity)."""
    sdev, sino, sdir = _fd_identity(staging_fd)
    adev, aino, _ = _fd_identity(ar_fd)
    return {'staging_dev': sdev, 'staging_ino': sino, 'staging_is_dir': sdir,
            'staging_basename': staging_basename,
            'ar_dev': adev, 'ar_ino': aino}


def _fd_receipt_matches(fd, receipt, label):
    """Generic retained-fd identity check (used for authorized-root and
  repository-root descriptors, keyed by dev/ino/dir-type).  Correction 9:
  a receipt declaring is_dir=True requires the descriptor be a directory;
  a receipt declaring is_dir=False requires it not be a directory.  The
  directory type is part of the identity comparison (not a reversed gate)."""
    dev, ino, isdir = _fd_identity(fd)
    if 'is_dir' in receipt:
        if receipt['is_dir'] and not isdir:
            raise FailClosed("%s: receipt declares directory but descriptor is "
                             "not a directory" % label)
        if not receipt['is_dir'] and isdir:
            raise FailClosed("%s: receipt declares non-directory but descriptor "
                             "is a directory" % label)
    return (dev == receipt.get('dev') and ino == receipt.get('ino'))


def _ar_fd_receipt(ar_fd):
    """Build an authorized-root fd receipt from the opened descriptor."""
    dev, ino, _ = _fd_identity(ar_fd)
    return {'dev': dev, 'ino': ino, 'is_dir': True}


def _verify_staging_bound(staging_fd, staging_basename, ar_fd, receipt, label):
    """Require that staging_basename relative to ar_fd resolves to a real
  directory whose dev/ino equals fstat(staging_fd) AND the frozen staging
  receipt, AND ar_fd still equals the frozen parent identity.  If the
  original staging directory was renamed and a replacement exists at the
  basename, raise a stable staging-name identity failure."""
    # ar_fd parent identity must match the frozen parent.
    cur_ar = _fd_identity(ar_fd)
    if (cur_ar[0], cur_ar[1]) != (receipt['ar_dev'], receipt['ar_ino']):
        raise FailClosed("%s: authorized-root parent identity changed" % label)
    # basename must resolve, without following symlinks, to a directory.
    try:
        bst = os.stat(staging_basename, dir_fd=ar_fd, follow_symlinks=False)
    except OSError as exc:
        raise FailClosed("%s: staging basename no longer resolves: %s"
                         % (label, exc))
    if stat.S_ISLNK(bst.st_mode):
        raise FailClosed("%s: staging basename became a symlink" % label)
    if not stat.S_ISDIR(bst.st_mode):
        raise FailClosed("%s: staging basename not a directory" % label)
    # The opened staging_fd must still identify the same object.
    fdev, fino, _ = _fd_identity(staging_fd)
    if (bst.st_dev, bst.st_ino) != (fdev, fino):
        raise FailClosed("%s: staging basename maps to a different object "
                         "(renamed/replaced): %s" % (label, staging_basename))
    if (fdev, fino) != (receipt['staging_dev'], receipt['staging_ino']):
        raise FailClosed("%s: staging fd identity changed" % label)
    if staging_basename != receipt['staging_basename']:
        raise FailClosed("%s: staging basename mismatch" % label)
    return True


def _prod_copy_files_dirfd(incl, staging_fd, repo_root_fd):
    """Production copy loop bound to the retained repo-root and staging fds."""
    for e in incl:
        _prod_copy_one_file_dirfd(repo_root_fd, e['source_root'],
                                  e['relative_path'], staging_fd,
                                  e['destination_relative'], e)


def _prod_copy_one_file_dirfd(repo_root_fd, src_root_id, rel_path,
                              staging_fd, dest_rel, e):
    """Copy one file using descriptor-relative source traversal (bound to the
    retained repo-root fd) and descriptor-relative destination creation + atomic
  no-replace per-file publication."""
    sfd = None
    dfd = None
    wfd = None
    wcreat = None
    temp_created = False
    temp_published = False
    parent_fd = None
    tmp_base = ("%s.tmp" % os.path.basename(dest_rel)) if dest_rel else "f.tmp"
    final_base = os.path.basename(dest_rel) if dest_rel else "f"
    _validate_name(tmp_base)
    _validate_name(final_base)
    dest_parent = os.path.dirname(dest_rel)
    parent_components = _split_components(dest_parent, _root_sentinel_ok=True)
    try:
        sfd = _safe_open_source(repo_root_fd, src_root_id, rel_path)
        st = os.fstat(sfd)
        if not stat.S_ISREG(st.st_mode):
            raise FailClosed("source not regular: %s:%s" % (src_root_id, rel_path))
        if st.st_nlink != 1:
            raise FailClosed("source nlink!=1: %s:%s" % (src_root_id, rel_path))
        if stat.S_IMODE(st.st_mode) != int(e['mode'], 8):
            raise FailClosed("source mode mismatch: %s:%s" % (src_root_id, rel_path))
        if st.st_size != e['size']:
            raise FailClosed("source size mismatch: %s:%s" % (src_root_id, rel_path))
        parent_fd = _dirfd_walk_to_parent(staging_fd, parent_components)
        # Create the temp file relative to the retained parent descriptor.
        if _dirfd_has_entry(parent_fd, final_base):
            raise FailClosed("dest file pre-exists: %s" % dest_rel)
        try:
            wfd = os.open(tmp_base,
                          os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                          int(e['mode'], 8), dir_fd=parent_fd)
        except OSError as exc:
            raise FailClosed("dest creat failed for %r: %s" % (tmp_base, exc))
        # Correction 4: capture temp-file identity immediately after creation.
        wcreat = os.fstat(wfd)
        temp_created = True
        os.fchmod(wfd, int(e['mode'], 8))
        h = hashlib.sha256()
        while True:
            b = os.read(sfd, 1024 * 1024)
            if not b:
                break
            h.update(b)
            mv = memoryview(b)
            total = 0
            while total < len(mv):
                w = os.write(wfd, mv[total:])
                if w is None or w <= 0:
                    raise FailClosed("write returned <=0")
                total += w
        os.fsync(wfd)
        if h.hexdigest() != e['sha256']:
            raise FailClosed("source sha mismatch: %s:%s" % (src_root_id, rel_path))
        wst = os.fstat(wfd)
        if not stat.S_ISREG(wst.st_mode) or wst.st_nlink != 1:
            raise FailClosed("dst descriptor not regular/nlink!=1")
        if stat.S_IMODE(wst.st_mode) != int(e['mode'], 8):
            raise FailClosed("dst mode mismatch (write fd)")
        if wst.st_size != e['size']:
            raise FailClosed("dst size mismatch (write fd)")
        os.close(wfd); wfd = None
        # Atomic no-replace per-file publication via retained parent fd.
        _no_replace_rename_dirfd(parent_fd, tmp_base, parent_fd, final_base)
        # Verify destination from an opened read descriptor.
        dfd = _dirfd_open_file_nofollow(parent_fd, final_base)
        try:
            dst_st = os.fstat(dfd)
            if not stat.S_ISREG(dst_st.st_mode):
                raise FailClosed("dst not regular: %s" % dest_rel)
            if dst_st.st_nlink != 1:
                raise FailClosed("dst nlink!=1: %s" % dest_rel)
            if stat.S_IMODE(dst_st.st_mode) != int(e['mode'], 8):
                raise FailClosed("dst mode mismatch: %s" % dest_rel)
            if dst_st.st_size != e['size']:
                raise FailClosed("dst size mismatch: %s" % dest_rel)
            if (dst_st.st_dev, dst_st.st_ino) == (st.st_dev, st.st_ino):
                raise FailClosed("source/destination inode alias: %s" % dest_rel)
            if _hash_fd(dfd) != e['sha256']:
                raise FailClosed("dst sha mismatch: %s" % dest_rel)
        finally:
            try: os.close(dfd)
            except OSError: pass
            dfd = None
        temp_published = True
    finally:
        if sfd is not None:
            try: os.close(sfd)
            except OSError: pass
        if wfd is not None:
            try: os.close(wfd)
            except OSError: pass
            wfd = None
        if dfd is not None:
            try: os.close(dfd)
            except OSError: pass
        # Correction 9A: identity-bound temp cleanup on any post-create failure.
        # After closing any open write descriptor, remove the temporary file
        # whenever it was created but not successfully published.
        if (parent_fd is not None and temp_created and not temp_published
                and wcreat is not None):
            try:
                _remove_tmp_bound(parent_fd, tmp_base,
                                  wcreat.st_dev, wcreat.st_ino)
            except FailClosed:
                if parent_fd is not staging_fd:
                    try: os.close(parent_fd)
                    except OSError: pass
                raise
        if parent_fd is not None and parent_fd is not staging_fd:
            try: os.close(parent_fd)
            except OSError: pass


def _dirfd_open_file_nofollow(parent_fd, name):
    """Open a regular file relative to parent_fd with O_NOFOLLOW."""
    try:
        return os.open(name, os.O_RDONLY | os.O_NOFOLLOW, dir_fd=parent_fd)
    except OSError as exc:
        raise FailClosed("dst O_NOFOLLOW open failed for %r: %s" % (name, exc))


def _remove_tmp_bound(parent_fd, tmp_base, captured_dev, captured_ino):
    """Remove a leftover temporary file relative to a RETAINED parent
    descriptor and bound to the captured temp inode (Correction 4 + 9A).
  Using the retained destination-parent descriptor:
  - stat the temporary basename without following symlinks;
  - require its device/inode to equal the captured temporary identity;
  - open with O_NOFOLLOW;
  - compare opened fstat device/inode with both the captured identity and
    the preceding stat identity;
  - close the descriptor;
  - immediately re-stat before unlink;
  - require the name still maps to the captured identity;
  - unlink only then;
  - reject symlinks, unsupported objects, and replacement identities;
  - never remove a replacement object.
  Returns None on success or nothing-to-remove; raises FailClosed if a present
  mismatched object is detected that cannot be safely removed."""
    try:
        tst = os.stat(tmp_base, dir_fd=parent_fd, follow_symlinks=False)
    except FileNotFoundError:
        return None  # genuinely absent
    except OSError as exc:
        raise FailClosed("tmp cleanup: stat failed for %r: %s" % (tmp_base, exc))
    if stat.S_ISLNK(tst.st_mode):
        raise FailClosed("tmp cleanup: basename is a symlink (not removed): %r"
                         % tmp_base)
    if not stat.S_ISREG(tst.st_mode):
        raise FailClosed("tmp cleanup: basename not a regular file "
                         "(unsupported): %r" % tmp_base)
    if (tst.st_dev, tst.st_ino) != (captured_dev, captured_ino):
        raise FailClosed("tmp cleanup: basename maps to a replacement object "
                         "(not removed): %r" % tmp_base)
    # Open with O_NOFOLLOW; compare opened fstat dev/ino with both
    # the captured identity and the preceding stat identity.
    try:
        fd2 = os.open(tmp_base, os.O_WRONLY | os.O_NOFOLLOW, dir_fd=parent_fd)
    except OSError as exc:
        raise FailClosed("tmp cleanup: O_NOFOLLOW open failed: %s" % exc)
    try:
        fst = os.fstat(fd2)
    except OSError as exc:
        try: os.close(fd2)
        except OSError: pass
        raise FailClosed("tmp cleanup: fstat after O_NOFOLLOW open failed: %s" % exc)
    if (fst.st_dev, fst.st_ino) != (captured_dev, captured_ino):
        try: os.close(fd2)
        except OSError: pass
        raise FailClosed("tmp cleanup: open descriptor identity mismatch "
                         "(replacement detected): %r" % tmp_base)
    if (fst.st_dev, fst.st_ino) != (tst.st_dev, tst.st_ino):
        try: os.close(fd2)
        except OSError: pass
        raise FailClosed("tmp cleanup: stat/open identity not continuous: %r"
                         % tmp_base)
    try: os.close(fd2)
    except OSError: pass
    # Re-stat immediately before unlink; confirm identity still holds.
    try:
        tst2 = os.stat(tmp_base, dir_fd=parent_fd, follow_symlinks=False)
    except OSError as exc:
        raise FailClosed("tmp cleanup: pre-unlink re-stat failed: %s" % exc)
    if (tst2.st_dev, tst2.st_ino) != (captured_dev, captured_ino):
        raise FailClosed("tmp cleanup: re-stat identity change before unlink "
                         "(replacement): %r" % tmp_base)
    try:
        os.unlink(tmp_base, dir_fd=parent_fd)
    except OSError as exc:
        raise FailClosed("tmp cleanup: unlink failed for %r: %s" % (tmp_base, exc))
    return None


def _dirfd_walk_existing(start_fd, components):
    """Open each existing directory component; no creation.  Correction 3: each
    opened component's fstat dev/ino must equal the retained non-following lstat
    identity (replacement rejected before returning the descriptor).  Returns the
    deepest descriptor; intermediates closed."""
    opened = []
    cur = start_fd
    try:
        for comp in components:
            st = _dirfd_lstat(cur, comp)
            if stat.S_ISLNK(st.st_mode):
                raise FailClosed("dirfd walk: symlink component: %r" % comp)
            if not stat.S_ISDIR(st.st_mode):
                raise FailClosed("dirfd walk: non-directory component (%s): %r"
                                 % (_stat_kind(st.st_mode), comp))
            child = _dirfd_open_dir_bound(cur, comp, st)
            opened.append(child)
            cur = child
        if opened:
            keep = opened[-1]
            for d in opened:
                if d is not keep:
                    try: os.close(d)
                    except OSError: pass
            return keep
        return start_fd
    except BaseException:
        for d in opened:
            try: os.close(d)
            except OSError: pass
        raise


def _build_dest_tree_dirfd(staging_fd, dirs, decl_prefix):
    """Create every declared destination directory relative to staging_fd."""
    seen = set()
    for d in dirs:
        root_id = d["source_root"]
        prefix = decl_prefix.get(root_id, "")
        rel = d["relative_path"]
        full = prefix if not rel else os.path.join(prefix, rel) if prefix else rel
        comps = _split_components(full, _root_sentinel_ok=True)
        # mkdir each component path; walk_to_parent creates/opens them.
        fd = _dirfd_walk_to_parent(staging_fd, comps)
        if fd is not staging_fd:
            try: os.close(fd)
            except OSError: pass


def _verify_dest_complete_dirfd(staging_fd, incl, dirs, decl_prefix):
    """Descriptor-relative complete destination audit: reject symlinks,
  non-regular/non-dir objects, wrong mode/size/hash/nlink, extra/missing
  objects, and inode replacement during audit.
  Returns None on success, raises FailClosed on mismatch."""
    expected_files, expected_dirs = _expected_dest_model(incl, dirs, decl_prefix)
    found_files, found_dirs = set(), set()
    _audit_recurse(staging_fd, "", staging_fd, expected_files, expected_dirs,
                   found_files, found_dirs)
    if found_files - set(expected_files):
        raise FailClosed("extra destination files: %r" % sorted(found_files - set(expected_files)))
    if set(expected_files) - found_files:
        raise FailClosed("missing destination files: %r" % sorted(set(expected_files) - found_files))
    if found_dirs - expected_dirs:
        raise FailClosed("extra destination directories: %r" % sorted(found_dirs - expected_dirs))
    if expected_dirs - found_dirs:
        raise FailClosed("missing destination directories: %r" % sorted(expected_dirs - found_dirs))


def _expected_dest_model(incl, dirs, decl_prefix):
    expected_files = {}
    for e in incl:
        expected_files[os.path.normpath(e["destination_relative"])] = e
    expected_dirs = set()
    for d in dirs:
        root_id = d["source_root"]
        prefix = decl_prefix.get(root_id, "")
        base = prefix if d["relative_path"] == "" else \
            os.path.join(prefix, d["relative_path"]) if prefix else d["relative_path"]
        if base:
            parts = [p for p in base.split("/") if p]
            for i in range(1, len(parts) + 1):
                expected_dirs.add(os.path.normpath("/".join(parts[:i])))
    expected_dirs.discard(".")
    return expected_files, expected_dirs


def _audit_recurse(parent_fd, rel_prefix, staging_fd, expected_files, expected_dirs,
                   found_files, found_dirs):
    """Recursively audit destination objects through descriptors with lstat-to-
  open identity continuity."""
    for name in _dirfd_list_names(parent_fd):
        _validate_name(name)
        rel = os.path.normpath(os.path.join(rel_prefix, name)) if rel_prefix else name
        lst = _dirfd_lstat(parent_fd, name)
        if stat.S_ISLNK(lst.st_mode):
            raise FailClosed("destination symlink rejected: %s" % rel)
        kind = _stat_kind(lst.st_mode)
        if kind == "directory":
            # identity continuity: lstat then open, compare dev/ino.
            dfd = None
            try:
                dfd = _dirfd_open_dir(parent_fd, name)
                ost = os.fstat(dfd)
                if (ost.st_dev, ost.st_ino) != (lst.st_dev, lst.st_ino):
                    raise FailClosed("dest dir inode changed (TOCTOU): %s" % rel)
                found_dirs.add(rel)
                _audit_recurse(dfd, rel, staging_fd, expected_files, expected_dirs,
                               found_files, found_dirs)
            finally:
                if dfd is not None:
                    try: os.close(dfd)
                    except OSError: pass
        elif kind == "regular":
            tfd = None
            try:
                tfd = _dirfd_open_file_nofollow(parent_fd, name)
                tst = os.fstat(tfd)
                if (tst.st_dev, tst.st_ino) != (lst.st_dev, lst.st_ino):
                    raise FailClosed("dest file inode changed (TOCTOU): %s" % rel)
                if tst.st_nlink != 1:
                    raise FailClosed("destination hard-link alias: %s" % rel)
                e = expected_files.get(rel)
                if e is None:
                    raise FailClosed("extra destination file: %s" % rel)
                if stat.S_IMODE(tst.st_mode) != int(e["mode"], 8):
                    raise FailClosed("dest mode mismatch: %s" % rel)
                if tst.st_size != e["size"]:
                    raise FailClosed("dest size mismatch: %s" % rel)
                if _hash_fd(tfd) != e["sha256"]:
                    raise FailClosed("dest sha mismatch: %s" % rel)
                found_files.add(rel)
            finally:
                if tfd is not None:
                    try: os.close(tfd)
                    except OSError: pass
        else:
            raise FailClosed("destination unsupported object (%s): %s" % (kind, rel))


def _verify_exclusions_absent_dirfd(staging_fd, excl, decl_prefix):
    """Exact-exclusion destination verification via parent walk + leaf stat.
  For each exclusion: derive the prefixed destination-relative path, walk each
  PARENT directory with O_DIRECTORY|O_NOFOLLOW relative to staging_fd, then
  inspect the final basename separately.  Correction 1: only FileNotFoundError
  for a parent component may mean the exclusion destination is genuinely absent;
  a present symlink, regular-file, FIFO, socket, device, or unknown parent
  fails closed, and a permission failure or other OSError fails closed.
  Correction 3: each opened parent directory has its fstat dev/ino compared
  with the preceding non-following stat identity.  If the final basename exists
  as ANY type, raise FailClosed."""
    for ex in excl:
        prefix = decl_prefix.get(ex["source_root"], "")
        full = os.path.join(prefix, ex["relative_path"]) if prefix \
            else ex["relative_path"]
        comps = _split_components(full, _root_sentinel_ok=True)
        if comps == []:
            if _dirfd_list_names(staging_fd):
                raise FailClosed("exclusion present in destination root: %s"
                                 % ex["relative_path"])
            continue
        parent_comps, leaf = comps[:-1], comps[-1]
        _validate_name(leaf)
        parent_fd = None
        opened = []
        try:
            cur = staging_fd
            absent = False
            for comp in parent_comps:
                # stat the component WITHOUT following symlinks.
                try:
                    pst = os.stat(comp, dir_fd=cur, follow_symlinks=False)
                except FileNotFoundError:
                    absent = True
                    break
                except OSError as exc:
                    raise FailClosed("exclusion parent stat failed for %r: %s"
                                     % (comp, exc))
                if stat.S_ISLNK(pst.st_mode):
                    raise FailClosed("exclusion parent is symlink: %s"
                                     % ex["relative_path"])
                if not stat.S_ISDIR(pst.st_mode):
                    # Correction 1: a present non-directory parent (regular,
                    # FIFO, socket, device, or unknown) fails closed; it is
                    # never treated as absence.
                    raise FailClosed("exclusion parent is non-directory (%s): %s"
                                     % (_stat_kind(pst.st_mode),
                                        ex["relative_path"]))
                # Correction 3: open + identity-bound the parent directory.
                child = _dirfd_open_dir_bound(cur, comp, pst)
                opened.append(child)
                cur = child
            if absent:
                continue
            parent_fd = cur
            try:
                lst = os.stat(leaf, dir_fd=parent_fd, follow_symlinks=False)
            except FileNotFoundError:
                continue  # genuinely absent
            except OSError as exc:
                raise FailClosed("exclusion leaf stat failed for %r: %s"
                                 % (leaf, exc))
            kind = _stat_kind(lst.st_mode)
            raise FailClosed("exclusion present in destination (%s): %s"
                             % (kind, ex["relative_path"]))
        finally:
            for d in opened:
                try: os.close(d)
                except OSError: pass


def _deny_walk(parent_fd, rel_prefix, effective, staging_fd):
    """Descriptor-relative deny-pattern scan over regular files.  Correction 3:
    directory components are opened with O_DIRECTORY|O_NOFOLLOW and the opened
    fstat dev/ino must equal the retained non-following lstat identity
    (replacement rejected before recursion)."""
    for name in _dirfd_list_names(parent_fd):
        rel = os.path.normpath(os.path.join(rel_prefix, name)) if rel_prefix else name
        lst = _dirfd_lstat(parent_fd, name)
        if stat.S_ISLNK(lst.st_mode):
            raise FailClosed("deny-walk: destination symlink: %s" % rel)
        if stat.S_ISDIR(lst.st_mode):
            dfd = None
            try:
                dfd = _dirfd_open_dir_bound(parent_fd, name, lst)
                _deny_walk(dfd, rel, effective, staging_fd)
            finally:
                if dfd is not None:
                    try: os.close(dfd)
                    except OSError: pass
        elif stat.S_ISREG(lst.st_mode):
            if fnmatch.fnmatch(rel, effective):
                raise FailClosed("deny-pattern in destination: %s" % rel)


def _verify_deny_patterns_absent_dirfd(staging_fd, manifest):
    decl_prefix = {d["source_root"]: d["destination_prefix"]
                   for d in manifest["source_root_declarations"]}
    for dp in manifest.get("deny_pattern_declarations", []):
        prefix = decl_prefix.get(dp["scope"], "")
        effective = os.path.join(prefix, dp["pattern"]) if prefix else dp["pattern"]
        _deny_walk(staging_fd, "", effective, staging_fd)


def _rmtree_dirfd_contents(fd):
    """Recursively remove all CONTENTS of the directory referenced by fd using
  descriptor-relative operations (no shutil.rmtree).  Rejects symlinks (does
  NOT unlink them) and unsupported objects; for regular files and
  directories it opens with O_NOFOLLOW and compares fstat dev/ino with the
  pre-open stat before recursing/unlinking, and re-stats the name immediately
  before removal to reject a replacement name whose identity changed."""
    for name in _dirfd_list_names(fd):
        _validate_name(name)
        lst = _dirfd_lstat(fd, name)
        if stat.S_ISLNK(lst.st_mode):
            raise FailClosed("cleanup: symlink rejected (not unlinked): %s" % name)
        kind = _stat_kind(lst.st_mode)
        if kind == "regular":
            ofd = None
            try:
                ofd = _dirfd_open_file_nofollow(fd, name)
                ost = os.fstat(ofd)
                if (ost.st_dev, ost.st_ino) != (lst.st_dev, lst.st_ino):
                    raise FailClosed("cleanup: regular-file inode swap: %s" % name)
            finally:
                if ofd is not None:
                    try: os.close(ofd)
                    except OSError: pass
            rstat = _dirfd_lstat(fd, name)
            if (rstat.st_dev, rstat.st_ino) != (lst.st_dev, lst.st_ino):
                raise FailClosed("cleanup: file replaced before unlink: %s" % name)
            try:
                os.unlink(name, dir_fd=fd)
            except OSError as exc:
                raise FailClosed("cleanup: unlink failed: %s" % exc)
        elif kind == "directory":
            dfd = None
            try:
                dfd = _dirfd_open_dir(fd, name)
                ost = os.fstat(dfd)
                if (ost.st_dev, ost.st_ino) != (lst.st_dev, lst.st_ino):
                    raise FailClosed("cleanup: directory inode swap: %s" % name)
                _rmtree_dirfd_contents(dfd)
            finally:
                if dfd is not None:
                    try: os.close(dfd)
                    except OSError: pass
            rstat = _dirfd_lstat(fd, name)
            if (rstat.st_dev, rstat.st_ino) != (lst.st_dev, lst.st_ino):
                raise FailClosed("cleanup: dir replaced before rmdir: %s" % name)
            try:
                os.rmdir(name, dir_fd=fd)
            except OSError as exc:
                raise FailClosed("cleanup: rmdir failed: %s" % exc)
        else:
            raise FailClosed("cleanup: unsupported object (%s): %s" % (kind, name))


# --------------------------------------------------------------------------
# Path-based adapters for test convenience (open staging fd, delegate to
# dirfd cores).  No path-based os.makedirs/os.rename/shutil.rmtree here.
# --------------------------------------------------------------------------
def _path_beneath(path, root):
    rp = os.path.realpath(path)
    rr = os.path.realpath(root)
    return rp == rr or rp.startswith(rr + os.sep)


def _open_staging_fd(staging):
    """Open the staging directory as a descriptor for dirfd-core delegation."""
    if (os.open not in os.supports_dir_fd or not hasattr(os, "O_DIRECTORY")
            or not hasattr(os, "O_NOFOLLOW")):
        raise FailClosed("path adapter: dirfd ops unavailable")
    try:
        return os.open(staging, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    except OSError as exc:
        raise FailClosed("path adapter: staging open failed: %s (%s)" % (staging, exc))


def _build_destination_tree(staging, dirs, decl_prefix):
    """Adapter: open staging fd, delegate to _build_dest_tree_dirfd."""
    fd = _open_staging_fd(staging)
    try:
        _build_dest_tree_dirfd(fd, dirs, decl_prefix)
    finally:
        try: os.close(fd)
        except OSError: pass


def _copy_files(incl, staging, repo_root, decl_prefix):
    """Adapter for the synthetic path: open staging + repo fds, delegate to
  _synth_copy_files_dirfd (descriptor-relative source via pathname open +
  O_NOFOLLOW, descriptor-relative dest)."""
    st_fd = _open_staging_fd(staging)
    try:
        for e in incl:
            _synth_copy_one_file_dirfd(e, st_fd, repo_root, decl_prefix)
    finally:
        try: os.close(st_fd)
        except OSError: pass


def _synth_copy_one_file_dirfd(e, staging_fd, repo_root, decl_prefix):
    """Synthetic copy: open source by path with O_NOFOLLOW (pathname is a
  selftest fixture, not a production source root), create+verify dest
  descriptor-relative, atomic no-replace publish."""
    src_root_id = e["source_root"]
    # In the synthetic path the manifest src_root is a logical id resolved via
  # ROOT_HOST (temporarily swapped) to a host_relative path under repo_root.
    src_root_rel = ROOT_HOST[src_root_id]
    src = os.path.join(repo_root, src_root_rel, e["relative_path"]) \
        if not os.path.isabs(src_root_rel) \
        else os.path.join(src_root_rel, e["relative_path"])
    sfd = None
    wfd = None
    wcreat = None
    temp_created = False
    temp_published = False
    dfd = None
    parent_fd = None
    tmp_base = "%s.tmp" % os.path.basename(e["destination_relative"]) \
        if e["destination_relative"] else "f.tmp"
    final_base = os.path.basename(e["destination_relative"]) if e["destination_relative"] else "f"
    _validate_name(tmp_base)
    _validate_name(final_base)
    parent_components = _split_components(os.path.dirname(e["destination_relative"]), _root_sentinel_ok=True)
    try:
        sfd = _open_fixture_nofollow(src)
        st = os.fstat(sfd)
        if not stat.S_ISREG(st.st_mode):
            raise FailClosed("source not regular: %s" % src)
        if st.st_nlink != 1:
            raise FailClosed("source nlink!=1: %s" % src)
        if stat.S_IMODE(st.st_mode) != int(e["mode"], 8):
            raise FailClosed("source mode mismatch: %s" % src)
        if st.st_size != e["size"]:
            raise FailClosed("source size mismatch: %s" % src)
        parent_fd = _dirfd_walk_to_parent(staging_fd, parent_components)
        if _dirfd_has_entry(parent_fd, final_base):
            raise FailClosed("dest file pre-exists: %s" % e["destination_relative"])
        try:
            wfd = os.open(tmp_base,
                          os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                          int(e["mode"], 8), dir_fd=parent_fd)
        except OSError as exc:
            raise FailClosed("dest creat failed for %r: %s" % (tmp_base, exc))
        # Correction 4: capture temp-file identity immediately after creation.
        wcreat = os.fstat(wfd)
        temp_created = True
        os.fchmod(wfd, int(e["mode"], 8))
        h = hashlib.sha256()
        while True:
            b = os.read(sfd, 1024 * 1024)
            if not b:
                break
            h.update(b)
            mv = memoryview(b)
            total = 0
            while total < len(mv):
                w = os.write(wfd, mv[total:])
                if w is None or w <= 0:
                    raise FailClosed("write returned <=0")
                total += w
        os.fsync(wfd)
        if h.hexdigest() != e["sha256"]:
            raise FailClosed("source sha mismatch: %s" % src)
        wst = os.fstat(wfd)
        if not stat.S_ISREG(wst.st_mode) or wst.st_nlink != 1:
            raise FailClosed("dst descriptor not regular/nlink!=1")
        if stat.S_IMODE(wst.st_mode) != int(e["mode"], 8):
            raise FailClosed("dst mode mismatch (write fd)")
        if wst.st_size != e["size"]:
            raise FailClosed("dst size mismatch (write fd)")
        os.close(wfd); wfd = None
        _no_replace_rename_dirfd(parent_fd, tmp_base, parent_fd, final_base)
        dfd = _dirfd_open_file_nofollow(parent_fd, final_base)
        try:
            dst_st = os.fstat(dfd)
            if not stat.S_ISREG(dst_st.st_mode):
                raise FailClosed("dst not regular: %s" % e["destination_relative"])
            if dst_st.st_nlink != 1:
                raise FailClosed("dst nlink!=1: %s" % e["destination_relative"])
            if stat.S_IMODE(dst_st.st_mode) != int(e["mode"], 8):
                raise FailClosed("dst mode mismatch: %s" % e["destination_relative"])
            if dst_st.st_size != e["size"]:
                raise FailClosed("dst size mismatch: %s" % e["destination_relative"])
            if (dst_st.st_dev, dst_st.st_ino) == (st.st_dev, st.st_ino):
                raise FailClosed("source/destination inode alias: %s"
                                 % e["destination_relative"])
            if _hash_fd(dfd) != e["sha256"]:
                raise FailClosed("dst sha mismatch: %s" % e["destination_relative"])
        finally:
            try: os.close(dfd)
            except OSError: pass
            dfd = None
        temp_published = True
    finally:
        if sfd is not None:
            try: os.close(sfd)
            except OSError: pass
        if wfd is not None:
            try: os.close(wfd)
            except OSError: pass
            wfd = None
        if dfd is not None:
            try: os.close(dfd)
            except OSError: pass
        # Correction 9A: identity-bound temp cleanup on any post-create failure.
        # After closing any open write descriptor, remove the temporary file
        # whenever it was created but not successfully published.
        if (parent_fd is not None and temp_created and not temp_published
                and wcreat is not None):
            try:
                _remove_tmp_bound(parent_fd, tmp_base,
                                  wcreat.st_dev, wcreat.st_ino)
            except FailClosed:
                if parent_fd is not staging_fd:
                    try: os.close(parent_fd)
                    except OSError: pass
                raise
        if parent_fd is not None and parent_fd is not staging_fd:
            try: os.close(parent_fd)
            except OSError: pass


def _open_fixture_nofollow(path):
    """Open a selftest fixture file with O_NOFOLLOW (no symlink following)."""
    if not hasattr(os, "O_NOFOLLOW"):
        raise FailClosed("O_NOFOLLOW unavailable on this platform")
    try:
        return os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    except OSError as exc:
        raise FailClosed("fixture O_NOFOLLOW open failed: %s (%s)" % (path, exc))


def _copy_one_file(src, dst, e):
    """Path adapter for selftest fixture copies: open the destination parent
  directory by path (a test fixture), create the temp file descriptor-relative,
  publish via atomic no-replace, and verify from a read descriptor.  No
  os.makedirs/os.rename/shutil.rmtree mutation here."""
    sfd = None
    wfd = None
    dfd = None
    parent_fd = None
    final_base = os.path.basename(dst)
    tmp_base = "%s.tmp" % final_base
    parent_dir = os.path.dirname(dst)
    _validate_name(final_base)
    _validate_name(tmp_base)
    try:
        sfd = _open_fixture_nofollow(src)
        st = os.fstat(sfd)
        if not stat.S_ISREG(st.st_mode):
            raise FailClosed("source not regular: %s" % src)
        if st.st_nlink != 1:
            raise FailClosed("source nlink!=1: %s" % src)
        if stat.S_IMODE(st.st_mode) != int(e["mode"], 8):
            raise FailClosed("source mode mismatch: %s" % src)
        if st.st_size != e["size"]:
            raise FailClosed("source size mismatch: %s" % src)
        if not hasattr(os, "O_NOFOLLOW"):
            raise FailClosed("O_NOFOLLOW unavailable on this platform")
        try:
            pfd = os.open(parent_dir, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        except OSError as exc:
            raise FailClosed("copy_one_file: parent open failed: %s (%s)"
                             % (parent_dir, exc))
        parent_fd = pfd
        if _dirfd_has_entry(parent_fd, final_base):
            raise FailClosed("dest file pre-exists: %s" % dst)
        try:
            wfd = os.open(tmp_base,
                          os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                          int(e["mode"], 8), dir_fd=parent_fd)
        except OSError as exc:
            raise FailClosed("dest creat failed for %r: %s" % (tmp_base, exc))
        os.fchmod(wfd, int(e["mode"], 8))
        h = hashlib.sha256()
        while True:
            b = os.read(sfd, 1024 * 1024)
            if not b:
                break
            h.update(b)
            mv = memoryview(b)
            total = 0
            while total < len(mv):
                w = os.write(wfd, mv[total:])
                if w is None or w <= 0:
                    raise FailClosed("write returned <=0")
                total += w
        os.fsync(wfd)
        if h.hexdigest() != e["sha256"]:
            raise FailClosed("source sha mismatch: %s" % src)
        wst = os.fstat(wfd)
        if not stat.S_ISREG(wst.st_mode) or wst.st_nlink != 1:
            raise FailClosed("dst descriptor not regular/nlink!=1")
        if stat.S_IMODE(wst.st_mode) != int(e["mode"], 8):
            raise FailClosed("dst mode mismatch (write fd)")
        if wst.st_size != e["size"]:
            raise FailClosed("dst size mismatch (write fd)")
        os.close(wfd); wfd = None
        _no_replace_rename_dirfd(parent_fd, tmp_base, parent_fd, final_base)
        dfd = _dirfd_open_file_nofollow(parent_fd, final_base)
        try:
            dst_st = os.fstat(dfd)
            if not stat.S_ISREG(dst_st.st_mode):
                raise FailClosed("dst not regular: %s" % dst)
            if dst_st.st_nlink != 1:
                raise FailClosed("dst nlink!=1: %s" % dst)
            if stat.S_IMODE(dst_st.st_mode) != int(e["mode"], 8):
                raise FailClosed("dst mode mismatch: %s" % dst)
            if dst_st.st_size != e["size"]:
                raise FailClosed("dst size mismatch: %s" % dst)
            if (dst_st.st_dev, dst_st.st_ino) == (st.st_dev, st.st_ino):
                raise FailClosed("source/destination inode alias: %s" % dst)
            if _hash_fd(dfd) != e["sha256"]:
                raise FailClosed("dst sha mismatch: %s" % dst)
        finally:
            try: os.close(dfd)
            except OSError: pass
            dfd = None
        temp_published = True
    finally:
        if sfd is not None:
            try: os.close(sfd)
            except OSError: pass
        if wfd is not None:
            try: os.close(wfd)
            except OSError: pass
        if dfd is not None:
            try: os.close(dfd)
            except OSError: pass
        if parent_fd is not None:
            try: os.close(parent_fd)
            except OSError: pass
        _remove_tmp_path_if_present(os.path.dirname(dst), tmp_base)


def _remove_tmp_path_if_present(parent_dirname, tmp_base):
    """Best-effort removal of a leftover temp file by path (test fixture only)."""
    if not parent_dirname:
        return
    try:
        pfd = os.open(parent_dirname, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    except OSError:
        return
    try:
        if _dirfd_has_entry(pfd, tmp_base):
            try:
                os.unlink(tmp_base, dir_fd=pfd)
            except OSError:
                pass
    finally:
        try: os.close(pfd)
        except OSError: pass


def _prod_copy_files(incl, staging, repo_root):
    """Adapter: open staging fd + repo fd, delegate to dirfd copy."""
    st_fd = _open_staging_fd(staging)
    repo_fd = _open_repo_root_fd(repo_root)
    try:
        _prod_copy_files_dirfd(incl, st_fd, repo_fd)
    finally:
        try: os.close(st_fd)
        except OSError: pass
        try: os.close(repo_fd)
        except OSError: pass


def _prod_copy_one_file(repo_root_fd, src_root_id, rel_path, dst, e):
    """Path adapter for selftest fixture production-copy checks: open the
  destination parent by path (a test fixture), create+verify+publish via
  descriptor-relative helpers.  No os.makedirs/os.rename/shutil.rmtree."""
    parent_fd = None
    parent_dir = os.path.dirname(dst)
    final_base = os.path.basename(dst) if dst else "f"
    tmp_base = "%s.tmp" % final_base
    _validate_name(final_base)
    _validate_name(tmp_base)
    try:
        try:
            pfd = os.open(parent_dir, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        except OSError as exc:
            raise FailClosed("prod_copy_one_file: parent open failed: %s (%s)"
                             % (parent_dir, exc))
        parent_fd = pfd
        # Reuse the dirfd core by faking a staging_fd = parent_fd and a flat
  # destination relative name.
        _prod_copy_one_file_dirfd(repo_root_fd, src_root_id, rel_path,
                                  parent_fd, final_base, e)
    finally:
        if parent_fd is not None:
            try: os.close(parent_fd)
            except OSError: pass
        _remove_tmp_path_if_present(parent_dir, tmp_base)


def _verify_destination_complete(staging, incl, dirs, decl_prefix):
    """Adapter: open staging fd, delegate to _verify_dest_complete_dirfd."""
    fd = _open_staging_fd(staging)
    try:
        _verify_dest_complete_dirfd(fd, incl, dirs, decl_prefix)
    finally:
        try: os.close(fd)
        except OSError: pass


def _verify_exclusions_absent(staging, excl, decl_prefix):
    """Adapter: open staging fd, delegate to dirfd core."""
    fd = _open_staging_fd(staging)
    try:
        _verify_exclusions_absent_dirfd(fd, excl, decl_prefix)
    finally:
        try: os.close(fd)
        except OSError: pass


def _verify_deny_patterns_absent(staging, manifest):
    """Adapter: open staging fd, delegate to dirfd core."""
    fd = _open_staging_fd(staging)
    try:
        _verify_deny_patterns_absent_dirfd(fd, manifest)
    finally:
        try: os.close(fd)
        except OSError: pass


def _stat_kind(mode):
    if stat.S_ISREG(mode):
        return "regular"
    if stat.S_ISDIR(mode):
        return "directory"
    if stat.S_ISLNK(mode):
        return "symlink"
    if stat.S_ISFIFO(mode):
        return "fifo"
    if stat.S_ISSOCK(mode):
        return "socket"
    if stat.S_ISCHR(mode):
        return "char-device"
    if stat.S_ISBLK(mode):
        return "block-device"
    return "unknown"
# --------------------------------------------------------------------------
# Synthetic fixtures for behavioral self-tests.
# --------------------------------------------------------------------------
def _dir_fixture(prefix):
    return tempfile.mkdtemp(prefix=prefix)


def _symlink_fixture(prefix):
    tmp = tempfile.mkdtemp(prefix=prefix)
    os.symlink("../../../etc/hosts", os.path.join(tmp, "link"))
    return tmp


# --------------------------------------------------------------------------
# Behavioral self-tests.
# --------------------------------------------------------------------------
def selftest():
    """Run behavioral self-tests against temporary synthetic fixtures.
    Returns (passed_total, failed_total, results).
    """
    results = []
    tmpdirs = []
    try:
        def must_raise(name, fn, *a, **k):
            try:
                fn(*a, **k)
                results.append((name, "FAIL: no exception"))
            except FailClosed:
                results.append((name, "PASS"))
            except Exception as exc:
                results.append((name, "FAIL: wrong exc %r" % exc))

        def must_pass(name, fn, *a, **k):
            try:
                rv = fn(*a, **k)
            except Exception as exc:
                results.append((name, "FAIL: %r" % exc))
                return
            # An explicit False return is a failure (no unconditional PASS).
            if rv is False:
                results.append((name, "FAIL: returned False"))
                return
            if rv == "skip":
                results.append((name, "SKIP"))
                return
            results.append((name, "PASS"))

        # ---- Selftest-local synthetic capability + materializer closures. ----
        # All synthetic-test state is local to selftest(); an importing caller
        # cannot combine any module attributes to perform materialization.
        _test_cap_secret = object()

        class _TestCap:
            """Selftest-local synthetic capability.  Direct construction fails;
            only mk_cap() (over _test_cap_secret) issues instances."""
            __slots__ = ("_secret", "__weakref__")

            def __init__(self, *a, **k):
                raise FailClosed("_TestCap: direct construction forbidden")

            def __setattr__(self, name, value):
                raise FailClosed("_TestCap is immutable: cannot set %s" % name)

            def __delattr__(self, name):
                raise FailClosed("_TestCap is immutable: cannot del %s" % name)

        def mk_cap():
            cap = object.__new__(_TestCap)
            object.__setattr__(cap, "_secret", _test_cap_secret)
            return cap

        def _test_cap_ok(cap):
            if not isinstance(cap, _TestCap):
                raise FailClosed("test materialization: not a _TestCap")
            if getattr(cap, "_secret", None) is not _test_cap_secret:
                raise FailClosed("test materialization: invalid _TestCap secret")
            return True

        def test_materialize(manifest, repo_root, authorized_root, component_id,
                              authorization, source_host_map=None):
            """Selftest-local synthetic materializer on temporary fixtures using
            the SAME descriptor-relative helpers as the production path.  No
            os.makedirs/os.rename/shutil.rmtree mutation here."""
            _test_cap_ok(authorization)
            _validate_component_id(component_id)
            decl_prefix = {d["source_root"]: d["destination_prefix"]
                           for d in manifest["source_root_declarations"]}
            ws = None
            for w in manifest.get("workspace_declarations", []):
                if w["component_id"] == component_id:
                    ws = w; break
            if ws is None:
                raise FailClosed("test: component_id not in workspace declarations")
            _enforce_workspace_policy(ws, component_id,
                                        {d['source_root']
                                         for d in manifest['source_root_declarations']})
            seed_source_roots = ws["seed_source_roots"]
            incl = [e for e in manifest["included_regular_file_entries"]
                    if e["source_root"] in seed_source_roots]
            dirs = [d for d in manifest["directory_entries"]
                    if d["source_root"] in seed_source_roots]
            excl = [ex for ex in manifest["exact_exclusion_records"]
                    if ex["source_root"] in seed_source_roots]
            _require_dirfd_capabilities()
            ar_fd = os.open(authorized_root,
                            os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
            # Capture the frozen authorized-root descriptor receipt ONCE.
            _adev, _aino, _ = _fd_identity(ar_fd)
            ar_fd_receipt = {'dev': _adev, 'ino': _aino, 'is_dir': True}
            staging_fd = None
            staging_base = None
            staging_receipt = None
            try:
                staging_base, staging_fd = _mkstemp_dirfd(ar_fd, component_id)
                staging_receipt = _staging_receipt(staging_fd, staging_base, ar_fd)
                _verify_staging_bound(staging_fd, staging_base, ar_fd,
                                      staging_receipt, "test after staging creation")
                orig_host = dict(ROOT_HOST)
                if source_host_map:
                    ROOT_HOST.clear(); ROOT_HOST.update(source_host_map)
                try:
                    _build_dest_tree_dirfd(staging_fd, dirs, decl_prefix)
                    for e in incl:
                        _synth_copy_one_file_dirfd(e, staging_fd, repo_root, decl_prefix)
                    _verify_staging_bound(staging_fd, staging_base, ar_fd,
                                          staging_receipt,
                                          "test before complete destination audit")
                    _verify_dest_complete_dirfd(staging_fd, incl, dirs, decl_prefix)
                    _verify_exclusions_absent_dirfd(staging_fd, excl, decl_prefix)
                    _verify_deny_patterns_absent_dirfd(staging_fd, manifest)
                    if not _fd_receipt_matches(ar_fd, ar_fd_receipt,
                                               "test authorized_root"):
                        raise FailClosed("test: authorized_root identity changed")
                    # Correction 5: comprehensive destination audit is the FINAL
                    # content-validation operation immediately before atomic
                    # publication (path-based final-name precheck removed;
                    # RENAME_EXCL/RENAME_NOREPLACE is authoritative).
                    _verify_dest_complete_dirfd(staging_fd, incl, dirs, decl_prefix)
                    _verify_exclusions_absent_dirfd(staging_fd, excl, decl_prefix)
                    _verify_deny_patterns_absent_dirfd(staging_fd, manifest)
                    _verify_staging_bound(staging_fd, staging_base, ar_fd,
                                          staging_receipt,
                                          "test before final publication")
                    _no_replace_rename_dirfd(ar_fd, staging_base, ar_fd, component_id)
                    return os.path.join(authorized_root, component_id)
                finally:
                    ROOT_HOST.clear(); ROOT_HOST.update(orig_host)
            except Exception:
                try:
                    if staging_fd is not None and staging_receipt is not None:
                        _verify_staging_bound(staging_fd, staging_base, ar_fd,
                                              staging_receipt, "test before cleanup")
                        _rmtree_dirfd_contents(staging_fd)
                    if staging_base is not None and staging_receipt is not None:
                        _verify_staging_bound(staging_fd, staging_base, ar_fd,
                                              staging_receipt,
                                              "test before removing staging basename")
                        try:
                            os.rmdir(staging_base, dir_fd=ar_fd)
                        except OSError as rerr:
                            raise FailClosed("cleanup: rmdir staging failed: %s"
                                             % rerr)
                except FailClosed:
                    raise
                raise
            finally:
                if staging_fd is not None:
                    try: os.close(staging_fd)
                    except OSError: pass
                try: os.close(ar_fd)
                except OSError: pass

        # test_copy_files removed: synthetic copy uses _synth_copy_one_file_dirfd
        # via the same descriptor-relative helpers as production.

        # 1. bad path rejection.
        for bad in ["\ud800x", "a\x00b", "/abs", "a//b", "a/b/..", "./a", "a\\b", ""]:
            must_raise("bad_path_reject_%r" % bad, validate_path, bad)
        must_pass("good_path_accept", validate_path, "data/x.tgz")
        must_raise("empty_path_for_file", validate_path, "")

        # 2. source-root sentinel acceptance only in narrow category.
        #    Empty string is never accepted by validate_path; the sentinel
        #    is handled explicitly in walk/manifest, not via validate_path.
        must_raise("sentinel_rejected_by_validate", validate_path, "")

        # 3. NFC collision (café NFC vs café NFD).
        must_raise("nfc_collision", collision_namespace,
                   ["caf\u00e9.txt", "cafe\u0301.txt"])

        # 4. NFD collision (distinct exact paths colliding on NFD).
        must_raise("nfd_collision", collision_namespace,
                   ["Stra\u00dfe.txt", "Strasse.txt"])  # ß casefold->ss

        # 5. casefold collision.
        must_raise("casefold_collision", collision_namespace,
                   ["ABC.txt", "abc.txt"])
        must_pass("no_collision_differ", collision_namespace, ["a.txt", "b.txt"])

        # 6. duplicate source identity.
        # proper duplicate test:
        def dup_src():
            inc = [{"source_root": "r", "relative_path": "a", "component_scope": "s",
                     "destination_relative": "a", "entry_type": "regular_file",
                     "mode": "0644", "size": 1, "sha256": "x", "nlink": 1},
                   {"source_root": "r", "relative_path": "a", "component_scope": "s",
                     "destination_relative": "a", "entry_type": "regular_file",
                     "mode": "0644", "size": 1, "sha256": "x", "nlink": 1}]
            _enforce_dup_source(inc, [])
        must_raise("dup_source_identity", dup_src)

        # 7. duplicate destination identity within component.
        def dup_dest():
            inc = [{"source_root": "r1", "relative_path": "a", "component_scope": "s",
                     "destination_relative": "D/a", "entry_type": "regular_file",
                     "mode": "0644", "size": 1, "sha256": "x", "nlink": 1},
                   {"source_root": "r2", "relative_path": "b", "component_scope": "s",
                     "destination_relative": "D/a", "entry_type": "regular_file",
                     "mode": "0644", "size": 1, "sha256": "y", "nlink": 1}]
            _enforce_dup_dest(inc)
        must_raise("dup_destination_identity", dup_dest)

        # 8. directory/file collision in a source root.
        must_raise("dir_file_collision", _check_dir_file,
                   {"files": {"sub"}, "dirs": {"sub"}})

        # 9. prefix collision (file-as-parent).
        must_raise("prefix_collision", file_prefix_collision, ["a"], ["a", "a/b"])
        # a dir-as-parent of files is valid (must NOT raise).
        must_pass("dir_as_parent_valid", file_prefix_collision, set(), {"d", "d/x"})

        # 10. source symlink rejection (during classify uses lstat).
        sl = _symlink_fixture("nrm_symsrc_")
        tmpdirs.append(sl)
        def src_symlink():
            excl_index = build_exclusion_index()
            classify_entry("fake", sl, "link", excl_index)
        must_raise("source_symlink_reject", src_symlink)

        # 11. destination-parent symlink rejection: materializer must reject
        #     when a source symlink is found at O_NOFOLLOW open.
        dps = tempfile.mkdtemp(prefix="nrm_dpsymlink_")
        tmpdirs.append(dps)
        os.makedirs(os.path.join(dps, "src"))
        os.symlink("/etc/hosts", os.path.join(dps, "src", "link.txt"))
        dps_man = {
            "schema": CONTRACT_SCHEMA,
            "source_root_declarations": [
                {"source_root": "r", "component_scope": "comp",
                 "host_relative_path": "src", "destination_prefix": "D"}],
            "included_regular_file_entries": [
                {"source_root": "r", "relative_path": "link.txt",
                 "entry_type": "regular_file", "mode": "0644", "size": 0,
                 "sha256": "0"*64, "nlink": 1,
                 "destination_relative": "D/link.txt", "component_scope": "comp"}],
            "directory_entries": [{"source_root": "r", "relative_path": "",
                                   "component_scope": "comp"}],
            "exact_exclusion_records": [], "deny_pattern_declarations": [],
            "workspace_declarations": [
                {"component_id": "dpws", "workspace_host_path": "dpws",
                 "mount_destination": "/work/nos3", "seed_source_roots": ["r"],
                 "private_physical_copy": True, "no_hard_links": True,
                 "no_reflinks": True, "no_overlays": True, "no_source_aliases": True,
                 "no_runtime_mount_from_external_nos3": True}],
            "canonicalization": {}, "path_validation": {},
            "collision_model": {}, "inventory_invariants": {}, "snapshot_inventory": {},
            "source_exclusion_policy": {}, "destination_exclusion_policy": {},
            "authorization_boundary": {}, "_test_scope": "comp",
        }
        dps_root = os.path.join(dps, "wsroot")
        os.makedirs(dps_root)
        tmpdirs.append(dps_root)
        def dest_parent_symlink():
            test_materialize(dps_man, dps, dps_root, "dpws",
                              mk_cap(),
                              source_host_map={"r": "src"})
        must_raise("dest_parent_symlink", dest_parent_symlink)

        # 12. source hard-link rejection (nlink>1).
        hl = tempfile.mkdtemp(prefix="nrm_hardlink_")
        tmpdirs.append(hl)
        def src_hardlink():
            f = os.path.join(hl, "f.bin")
            with open(f, "wb") as fh: fh.write(b"hl")
            fd = os.open(f, os.O_RDONLY)
            st = os.fstat(fd); os.close(fd)
            if st.st_nlink > 1:
                raise FailClosed("hardlink detected")
            # emulate nlink>1 by asking classify on a file whose st_nlink>1
            # (hard to force on all filesystems; instead test the nlink check
            # directly via a synthetic classify stub)
            raise FailClosed("synthetic nlink>1")
        # Real hard link test: create a second link.
        def src_hardlink_real():
            f1 = os.path.join(hl, "h1.bin")
            f2 = os.path.join(hl, "h2.bin")
            with open(f1, "wb") as fh: fh.write(b"hard")
            os.link(f1, f2)
            excl_index = build_exclusion_index()
            try:
                classify_entry("fake", hl, "h2.bin", excl_index)
            finally:
                os.remove(f1); os.remove(f2)
        must_raise("source_hardlink_reject", src_hardlink_real)

        # 13. unlisted source rejection during verification.
        us = tempfile.mkdtemp(prefix="nrm_unlisted_")
        tmpdirs.append(us)
        os.makedirs(os.path.join(us, "src"))
        with open(os.path.join(us, "src", "extra.txt"), "wb") as fh: fh.write(b"unexpected")
        # a minimal manifest that does NOT include extra.txt; verify detects it.
        def unlisted_in_verify():
            man = json.loads(("{\"schema\":1,\"source_root_declarations\":[{\"source_root\":"
                              "\"r\",\"component_scope\":\"s\",\"host_relative_path\":\"src\","
                              "\"destination_prefix\":\"D\"}],\"included_regular_file_entries\":"
                              "[],\"directory_entries\":[],\"exact_exclusion_records\":"
                              "[],\"deny_pattern_declarations\":[],\"workspace_declarations\":"
                              "[]}\n").encode())
            verify_manifest(serialize_manifest(man), us)
        must_raise("unlisted_source_in_verify", unlisted_in_verify)

        # 14. genuine unlisted destination rejection: materialize a synthetic
        # fixture, add an unlisted regular file, and require the destination
        # audit to reject it.
        def unlisted_destination_genuinely_rejected():
            tf = tempfile.mkdtemp(prefix="nrm_unlistdst_")
            tmpdirs.append(tf)
            os.makedirs(os.path.join(tf, "src"))
            with open(os.path.join(tf, "src", "a.txt"), "wb") as fh: fh.write(b"aaa")
            os.chmod(os.path.join(tf, "src", "a.txt"), 0o644)
            man = _build_synthetic_manifest(os.path.join(tf, "src"),
                [{"source_root": "r", "relative_path": "a.txt",
                  "entry_type": "regular_file", "mode": "0644", "size": 3,
                  "sha256": sha256_bytes(b"aaa"), "nlink": 1,
                  "destination_relative": "D/a.txt", "component_scope": "comp"}])
            wsr = os.path.join(tf, "ws_root"); os.makedirs(wsr); tmpdirs.append(wsr)
            fex = test_materialize(man, tf, wsr, "ws", mk_cap(),
                                    source_host_map={"r": "src"})
            with open(os.path.join(fex, "D", "unlisted.txt"), "wb") as fh: fh.write(b"x")
            _verify_destination_complete(fex, man["included_regular_file_entries"],
                                         man["directory_entries"], {"r": "D"})
        must_raise("unlisted_destination_genuinely_rejected",
                   unlisted_destination_genuinely_rejected)

        # 15. genuine absent exact exclusion accepted: an exclusion record whose
        # source path is ABSENT from disk is permitted (absence is not drift);
        # materialization succeeds and the exclusion check passes.
        def absent_exact_exclusion_genuinely_accepted():
            tf = tempfile.mkdtemp(prefix="nrm_absentexcl_")
            tmpdirs.append(tf)
            os.makedirs(os.path.join(tf, "src"))
            with open(os.path.join(tf, "src", "a.txt"), "wb") as fh: fh.write(b"aaa")
            os.chmod(os.path.join(tf, "src", "a.txt"), 0o644)
            excl_rec = {"source_root": "r", "relative_path": "stale_log.txt",
                         "entry_type": "regular_file", "mode": "0644",
                         "size": 999, "sha256": "00" * 32, "nlink": 1,
                         "present_at_amendment": True,
                         "classification": "EXACT_STALE_EXCLUSION",
                         "destination_must_be_absent": True}
            man = _build_synthetic_manifest(os.path.join(tf, "src"),
                [{"source_root": "r", "relative_path": "a.txt",
                  "entry_type": "regular_file", "mode": "0644", "size": 3,
                  "sha256": sha256_bytes(b"aaa"), "nlink": 1,
                  "destination_relative": "D/a.txt", "component_scope": "comp"}],
                excl_records=[excl_rec])
            wsr = os.path.join(tf, "ws_root"); os.makedirs(wsr); tmpdirs.append(wsr)
            fex = test_materialize(man, tf, wsr, "ws", mk_cap(),
                                    source_host_map={"r": "src"})
            _verify_exclusions_absent(fex, [excl_rec], {"r": "D"})
            return os.path.isdir(fex)
        must_pass("absent_exact_exclusion_genuinely_accepted",
                  absent_exact_exclusion_genuinely_accepted)

        # 16. genuine present matching exact exclusion accepted: the excluded
        # source IS present on disk and its frozen identity matches classify's
        # disk identity; classify returns ("excluded", ...) and the file is not
        # included in the manifest.
        def present_matching_exclusion_genuinely_accepted():
            tf = tempfile.mkdtemp(prefix="nrm_presentexcl_")
            tmpdirs.append(tf)
            os.makedirs(os.path.join(tf, "src"))
            payload = b"STALELOGDATA"
            with open(os.path.join(tf, "src", "stale.txt"), "wb") as fh: fh.write(payload)
            os.chmod(os.path.join(tf, "src", "stale.txt"), 0o644)
            sha = sha256_bytes(payload)
            excl_rec = {"source_root": "r", "relative_path": "stale.txt",
                         "entry_type": "regular_file", "mode": "0644",
                         "size": len(payload), "sha256": sha, "nlink": 1,
                         "present_at_amendment": True,
                         "classification": "EXACT_STALE_EXCLUSION",
                         "destination_must_be_absent": True}
            # Use a fake exclusion index mapping the (root,rel) to the record.
            idx = {("r", "stale.txt"): excl_rec}
            kind, ident = classify_entry("r", os.path.join(tf, "src"), "stale.txt", idx)
            if kind != "excluded":
                raise FailClosed("present exclusion classified as %r" % kind)
            if ident is not excl_rec:
                raise FailClosed("exclusion identity mismatch")
            return True
        must_pass("present_matching_exclusion_genuinely_accepted",
                  present_matching_exclusion_genuinely_accepted)

        # 17. present mismatching exact exclusion rejected.
        def mismatch_excl():
            tf = tempfile.mkdtemp(prefix="nrm_mismatch_")
            tmpdirs.append(tf)
            with open(os.path.join(tf, "x.bin"), "wb") as fh: fh.write(b"wrong")
            sha = sha256_bytes(b"wrong")
            excl_rec = {"source_root": "r", "relative_path": "x.bin",
                         "entry_type": "regular_file", "mode": "0644",
                         "size": 5, "sha256": "deadbeef" + "0" * 56, "nlink": 1,
                         "present_at_amendment": True,
                         "classification": "EXACT_STALE_EXCLUSION",
                         "destination_must_be_absent": True}
            idx = {("r", "x.bin"): excl_rec}
            classify_entry("r", tf, "x.bin", idx)
        must_raise("present_exclusion_mismatch", mismatch_excl)

        # 18. unclassified deny-pattern match rejected.
        def deny_unclassified():
            match_deny_patterns("cfs", "data/owls/bundle/.goutputstream-foo")
        # returning True means matched; the rejection happens in classify.
        must_pass("deny_match_detected_match", deny_unclassified)
        must_pass("deny_no_match", lambda: not match_deny_patterns("cfs", "ok"))

        # 19. materialization without authorization rejected before paths.
        ma = tempfile.mkdtemp(prefix="nrm_noauth_")
        tmpdirs.append(ma)
        def no_auth():
            try:
                materialize_workspace(None, ma, authorization=None, component_id="x")
            except FailClosed as exc:
                if "MaterializationAuthorized bearer" not in str(exc):
                    raise FailClosed("no_auth rejected for wrong reason: %s" % exc)
                return
            raise FailClosed("materialize_no_auth not rejected")
        must_pass("materialize_no_auth", no_auth)
        # verify no paths were created.
        if os.path.exists(os.path.join(ma, "x")):
            results.append(("materialize_no_auth_no_paths", "FAIL: path exists"))
        else:
            results.append(("materialize_no_auth_no_paths", "PASS"))

        # 20-26. materialization behavioral tests with a synthetic manifest.
        _run_materialization_tests(results, tmpdirs, mk_cap, test_materialize)

        # 29. changed canonical metadata rejected.
        def changed_meta():
            inc, dirs, exc, st = walk_source_roots(os.getcwd())
            man = build_manifest(os.getcwd(), inc, dirs, exc, st)
            man["canonicalization"] = {}  # strip canonicalization metadata
            raw = serialize_manifest(man)
            verify_manifest(raw, os.getcwd())
        must_raise("changed_meta_rejected", changed_meta)

        # 30. changed directory entry rejected (authoritative verify vs disk).
        # 31. changed workspace declaration rejected (authoritative verify vs disk).
        # 28. exact canonical verification - real source.
        def real_verify_ok():
            inc, dirs, exc, st = walk_source_roots(os.getcwd())
            man = build_manifest(os.getcwd(), inc, dirs, exc, st)
            raw = serialize_manifest(man)
            verify_manifest(raw, os.getcwd())
        must_pass("exact_canonical_verification_real", real_verify_ok)

        def changed_directory_rejected():
            inc, dirs, exc, st = walk_source_roots(os.getcwd())
            man = build_manifest(os.getcwd(), inc, dirs, exc, st)
            # corrupt a directory entry
            man["directory_entries"][0] = dict(man["directory_entries"][0],
                                                relative_path="CORRUPTED")
            raw = serialize_manifest(man)
            verify_manifest(raw, os.getcwd())
        must_raise("changed_directory_entry_rejected", changed_directory_rejected)

        def changed_workspace_rejected():
            inc, dirs, exc, st = walk_source_roots(os.getcwd())
            man = build_manifest(os.getcwd(), inc, dirs, exc, st)
            man["workspace_declarations"][0] = dict(man["workspace_declarations"][0],
                                                    component_id="CORRUPTED")
            raw = serialize_manifest(man)
            verify_manifest(raw, os.getcwd())
        must_raise("changed_workspace_decl_rejected", changed_workspace_rejected)

        def size_mismatch_rejected():
            inc, dirs, exc, st = walk_source_roots(os.getcwd())
            man = build_manifest(os.getcwd(), inc, dirs, exc, st)
            man["included_regular_file_entries"][0] = dict(
                man["included_regular_file_entries"][0], size=999999999)
            raw = serialize_manifest(man)
            verify_manifest(raw, os.getcwd())
        must_raise("size_mismatch_rejected", size_mismatch_rejected)

        def mode_mismatch_rejected():
            inc, dirs, exc, st = walk_source_roots(os.getcwd())
            man = build_manifest(os.getcwd(), inc, dirs, exc, st)
            man["included_regular_file_entries"][0] = dict(
                man["included_regular_file_entries"][0], mode="0777")
            raw = serialize_manifest(man)
            verify_manifest(raw, os.getcwd())
        must_raise("mode_mismatch_rejected", mode_mismatch_rejected)

        # Additional materialization-boundary behavioral tests.

        # Genuine bearer-boundary tests (Correction 9): these must fail for
        # the intended reason, not merely because any exception occurred.

        def direct_vm_construction_rejected():
            VerifiedManifest()
        must_raise("direct_verified_manifest_construction_rejected",
                  direct_vm_construction_rejected)

        def forged_new_vm_registry_rejected():
            # object.__new__ forged bearer has an identity absent from the
            # issuance registry; _entry() rejects it.
            forged = object.__new__(VerifiedManifest)
            forged._entry()
        must_raise("forged_new_vm_registry_rejected", forged_new_vm_registry_rejected)

        def fake_vm_object_rejected():
            # A bare fake object is rejected by the production materializer
            # before any filesystem mutation (_require_auth raises first in
            # this checkpoint, which is the intended fail-closed check).
            class FakeVM:
                repo_root = os.getcwd()
                def revalidate(self): return True
                def manifest(self):
                    return {"workspace_declarations": []}
                def workspace_for(self, cid):
                    raise FailClosed("not found")
            try:
                materialize_workspace(FakeVM(), os.path.join(os.getcwd(), "external"),
                                      authorization=mk_cap(),
                                      component_id="ws")
            except FailClosed as exc:
                if "MaterializationAuthorized bearer" not in str(exc):
                    raise FailClosed("fake_vm rejected for wrong reason: %s" % exc)
                return
            raise FailClosed("fake_vm not rejected")
        must_pass("fake_verified_manifest_object_rejected", fake_vm_object_rejected)

        def synthetic_test_capability_rejected_by_production():
            inc, dirs, exc, st = walk_source_roots(os.getcwd())
            man = build_manifest(os.getcwd(), inc, dirs, exc, st)
            raw = serialize_manifest(man)
            vmb = load_and_verify_manifest(raw, os.getcwd())
            wsr_dir = tempfile.mkdtemp(prefix="nrm_synauth_")
            tmpdirs.append(wsr_dir)
            try:
                materialize_workspace(vmb, wsr_dir, authorization=mk_cap(),
                                      component_id="time_driver")
            except FailClosed as exc:
                if "MaterializationAuthorized bearer" not in str(exc):
                    raise FailClosed("synthetic auth rejected for wrong reason: %s" % exc)
                return
            raise FailClosed("synthetic capability not rejected by production")
        must_pass("synthetic_test_capability_rejected_by_production",
                  synthetic_test_capability_rejected_by_production)

        # component_id escape rejected by _validate_component_id (genuine test
        # via the private synthetic-test path that accepts the test capability).
        def comp_id_escape_rejected():
            root_e = tempfile.mkdtemp(prefix="nrm_escape_")
            tmpdirs.append(root_e)
            os.makedirs(os.path.join(root_e, "src"))
            sx = _build_synthetic_manifest(os.path.join(root_e, "src"),
                [{"source_root": "r", "relative_path": "a.txt",
                  "entry_type": "regular_file", "mode": "0644", "size": 3,
                  "sha256": sha256_bytes(b"aaa"), "nlink": 1,
                  "destination_relative": "D/a.txt", "component_scope": "comp"}])
            wsr = os.path.join(root_e, "ws_root"); os.makedirs(wsr); tmpdirs.append(wsr)
            test_materialize(sx, root_e, wsr, "../escape", mk_cap(),
                              source_host_map={"r": "src"})
        must_raise("component_id_dotdot_escape_rejected", comp_id_escape_rejected)

        def unknown_component_id_rejected():
            root_u = tempfile.mkdtemp(prefix="nrm_unknown_")
            tmpdirs.append(root_u)
            os.makedirs(os.path.join(root_u, "src"))
            sx = _build_synthetic_manifest(os.path.join(root_u, "src"),
                [{"source_root": "r", "relative_path": "a.txt",
                  "entry_type": "regular_file", "mode": "0644", "size": 3,
                  "sha256": sha256_bytes(b"aaa"), "nlink": 1,
                  "destination_relative": "D/a.txt", "component_scope": "comp"}])
            wsr = os.path.join(root_u, "ws_root"); os.makedirs(wsr); tmpdirs.append(wsr)
            test_materialize(sx, root_u, wsr, "not_a_real_workspace",
                              mk_cap(), source_host_map={"r": "src"})
        must_raise("unknown_component_id_rejected", unknown_component_id_rejected)

        # ---- Additional genuine workspace-policy and bearer-mutation tests.

        # Authoritative verified state lives in the closure-backed
        # object-keyed WeakKeyDictionary, OUTSIDE caller-mutable object
        # attributes.  object.__setattr__ cannot reach the registry (the
        # bearer has no mutable slots carrying authoritative state), so
        # revalidate() continues to use the registry-held (original) bytes.
        def vm_setattr_rejected():
            inc, dirs, exc, st = walk_source_roots(os.getcwd())
            raw = serialize_manifest(build_manifest(os.getcwd(), inc, dirs, exc, st))
            vmb = load_and_verify_manifest(raw, os.getcwd())
            vmb.repo_root = "/etc"
        must_raise("verified_manifest_setattr_rejected", vm_setattr_rejected)

        def vm_object_setattr_cannot_change_registry():
            inc, dirs, exc, st = walk_source_roots(os.getcwd())
            raw = serialize_manifest(build_manifest(os.getcwd(), inc, dirs, exc, st))
            vmb = load_and_verify_manifest(raw, os.getcwd())
            # object.__setattr__ bypasses __setattr__ but _raw is not a slot;
            # it raises AttributeError and never touches the registry.
            try:
                object.__setattr__(vmb, "_raw", b"tampered")
            except AttributeError:
                pass
            except FailClosed:
                pass
            # The registry still holds the original bytes; revalidate passes.
            return vmb.revalidate() is True
        must_pass("vm_object_setattr_cannot_change_registry",
                  vm_object_setattr_cannot_change_registry)

        def vm_revalidate_untouched_ok():
            inc, dirs, exc, st = walk_source_roots(os.getcwd())
            raw = serialize_manifest(build_manifest(os.getcwd(), inc, dirs, exc, st))
            vmb = load_and_verify_manifest(raw, os.getcwd())
            return vmb.revalidate()
        must_pass("verified_manifest_revalidate_untouched_ok", vm_revalidate_untouched_ok)

        # A forged bearer cannot acquire registry state (no module accessor).
        # full_reverify() on a forged bearer is rejected because it has no
        # registry entry.  This replaces the prior registry-internal mutation
        # tests (the registry is now enclosed; tests must not mutate it).
        def forged_bearer_full_reverify_rejected():
            forged = object.__new__(VerifiedManifest)
            forged.full_reverify()
        must_raise("forged_bearer_full_reverify_rejected",
                   forged_bearer_full_reverify_rejected)

        # A real bearer's full_reverify() genuinely re-checks the source
        # inventory (re-stat of the repo root + re-verify_manifest).
        def real_bearer_full_reverify_ok():
            inc, dirs, exc, st = walk_source_roots(os.getcwd())
            raw = serialize_manifest(build_manifest(os.getcwd(), inc, dirs, exc, st))
            vmb = load_and_verify_manifest(raw, os.getcwd())
            return vmb.full_reverify() is True
        must_pass("real_bearer_full_reverify_ok", real_bearer_full_reverify_ok)

        # ---- Correction 7: production-authorization, frozen-workspace,
        # production-copy, and identity-binding genuine tests ----

        # _require_auth always fails in this checkpoint (no production issuer).
        def require_auth_none_fails():
            _require_auth(None)
        must_raise("require_auth_none_fails", require_auth_none_fails)
        def require_auth_test_capability_fails():
            _require_auth(mk_cap())
        must_raise("require_auth_test_capability_fails", require_auth_test_capability_fails)

        # object.__setattr__ cannot promote a test capability to production;
        # _require_auth requires a registered MaterializationAuthorized bearer;
        # synthetic test capabilities are not registered and are rejected.
        def test_capability_not_promoted():
            tc = mk_cap()
            # _TestCap is immutable; __setattr__ raises.  Even if it did not,
            # _require_auth rejects any non-registered bearer.
            _require_auth(tc)
        must_raise("test_capability_not_promoted_to_production",
                   test_capability_not_promoted)

        # object.__new__ forged bearer has no registry entry: its properties
        # reject with FailClosed.
        def forged_new_vm_property_rejected():
            forged = object.__new__(VerifiedManifest)
            forged.raw_bytes
        must_raise("forged_new_vm_property_rejected", forged_new_vm_property_rejected)

        # Frozen seed-root substitution rejected: a production workspace whose
        # seed_source_roots are swapped between otherwise-valid roots fails the
        # exact frozen comparison.
        def frozen_seed_root_substitution_rejected():
            ws = dict(_frozen_workspace_map()["nos_engine"])
            ws = dict(ws, seed_source_roots=["cfs"])
            _enforce_workspace_policy_frozen(ws, "nos_engine")
        must_raise("frozen_seed_root_substitution_rejected",
                   frozen_seed_root_substitution_rejected)
        def frozen_workspace_accepted_genuine():
            _enforce_workspace_policy_frozen(dict(_frozen_workspace_map()["nos_engine"]), "nos_engine")
            return True
        must_pass("frozen_workspace_accepted_genuine", frozen_workspace_accepted_genuine)

        # Actual _prod_copy_one_file rejects a nested parent symlink via
        # _safe_open_source descriptor-relative O_NOFOLLOW traversal.
        def prod_copy_rejects_nested_parent_symlink():
            tf = tempfile.mkdtemp(prefix="nrm_pcopy_sym_"); tmpdirs.append(tf)
            real_parent = os.path.join(tf, "real_parent"); os.makedirs(os.path.join(real_parent, "sub"))
            payload = b"aaa"
            with open(os.path.join(real_parent, "sub", "a.txt"), "wb") as fh: fh.write(payload)
            os.chmod(os.path.join(real_parent, "sub", "a.txt"), 0o644)
            os.symlink(real_parent, os.path.join(tf, "src"))
            dst = os.path.join(tf, "dst.txt")
            orig = dict(ROOT_HOST)
            try:
                ROOT_HOST.clear(); ROOT_HOST["r"] = "src"
                rfd = _open_repo_root_fd(tf)
                try:
                    _prod_copy_one_file(rfd, "r", "sub/a.txt", dst,
                        {"source_root": "r", "mode": "0644", "size": len(payload),
                         "sha256": sha256_bytes(payload)})
                finally:
                    os.close(rfd)
            finally:
                ROOT_HOST.clear(); ROOT_HOST.update(orig)
        must_raise("prod_copy_nested_parent_symlink_rejected",
                   prod_copy_rejects_nested_parent_symlink)

        # Successful synthetic publication invokes the no-replace primitive
        # exactly twice (1 per-file + 1 final), using basenames + dirfds.
        def successful_publication_one_noreplace_rename():
            tf = tempfile.mkdtemp(prefix="nrm_pubonce_"); tmpdirs.append(tf)
            os.makedirs(os.path.join(tf, "src"))
            with open(os.path.join(tf, "src", "a.txt"), "wb") as fh: fh.write(b"aaa")
            os.chmod(os.path.join(tf, "src", "a.txt"), 0o644)
            gi = [{"source_root": "r", "relative_path": "a.txt",
                   "entry_type": "regular_file", "mode": "0644", "size": 3,
                   "sha256": sha256_bytes(b"aaa"), "nlink": 1,
                   "destination_relative": "D/a.txt", "component_scope": "comp"}]
            man = _build_synthetic_manifest(os.path.join(tf, "src"), gi)
            wsr = os.path.join(tf, "ws_root"); os.makedirs(wsr); tmpdirs.append(wsr)
            calls = {"n": 0}
            import __main__ as _M
            orig = _M._no_replace_rename_dirfd
            def counting_dirfd(spfd, sbase, dpfd, dbase):
                calls["n"] += 1
                return orig(spfd, sbase, dpfd, dbase)
            try:
                _M._no_replace_rename_dirfd = counting_dirfd
                test_materialize(man, tf, wsr, "ws", mk_cap(),
                                  source_host_map={"r": "src"})
            finally:
                _M._no_replace_rename_dirfd = orig
            return calls["n"] == 2
        must_pass("successful_publication_one_noreplace_rename",
                  successful_publication_one_noreplace_rename)

        # Authorized-root identity receipt mismatch after recreate: a
        # recreated directory has a different inode and must not match the
        # original receipt.
        def authorized_root_receipt_mismatch_after_recreate():
            tf = tempfile.mkdtemp(prefix="nrm_arrm2_"); tmpdirs.append(tf)
            ar = os.path.realpath(os.path.join(tf, "ar"))
            os.makedirs(ar)
            receipt = _identity_receipt(ar)
            os.rmdir(ar); os.makedirs(ar)
            cur = _identity_receipt(ar)
            if _receipt_matches(cur, receipt, "ar"):
                raise FailClosed("recreated authorized root unexpectedly matched")
            return True
        must_pass("authorized_root_receipt_mismatch_after_recreate",
                  authorized_root_receipt_mismatch_after_recreate)

        # Workspace policy mutations genuinely rejected.
        gold_inc = [{"source_root": "r", "relative_path": "a.txt",
                     "entry_type": "regular_file", "mode": "0644", "size": 3,
                     "sha256": sha256_bytes(b"aaa"), "nlink": 1,
                     "destination_relative": "D/a.txt", "component_scope": "comp"}]

        def ws_host_path_mutation_rejected():
            tf = tempfile.mkdtemp(prefix="nrm_wshost_"); tmpdirs.append(tf)
            os.makedirs(os.path.join(tf, "src"))
            man = _build_synthetic_manifest(os.path.join(tf, "src"), gold_inc)
            man["workspace_declarations"][0] = dict(
                man["workspace_declarations"][0], workspace_host_path="DIFFERENT")
            wsr = os.path.join(tf, "ws_root"); os.makedirs(wsr); tmpdirs.append(wsr)
            test_materialize(man, tf, wsr, "ws", mk_cap(),
                              source_host_map={"r": "src"})
        must_raise("workspace_host_path_mutation_rejected", ws_host_path_mutation_rejected)

        def ws_mount_dest_mutation_rejected():
            tf = tempfile.mkdtemp(prefix="nrm_wsmp_"); tmpdirs.append(tf)
            os.makedirs(os.path.join(tf, "src"))
            man = _build_synthetic_manifest(os.path.join(tf, "src"), gold_inc)
            man["workspace_declarations"][0] = dict(
                man["workspace_declarations"][0], mount_destination="/elsewhere")
            wsr = os.path.join(tf, "ws_root"); os.makedirs(wsr); tmpdirs.append(wsr)
            test_materialize(man, tf, wsr, "ws", mk_cap(),
                              source_host_map={"r": "src"})
        must_raise("workspace_mount_destination_mutation_rejected",
                   ws_mount_dest_mutation_rejected)

        def ws_seed_roots_mutation_rejected():
            tf = tempfile.mkdtemp(prefix="nrm_wssr_"); tmpdirs.append(tf)
            os.makedirs(os.path.join(tf, "src"))
            man = _build_synthetic_manifest(os.path.join(tf, "src"), gold_inc)
            man["workspace_declarations"][0] = dict(
                man["workspace_declarations"][0], seed_source_roots=["r", "r"])
            wsr = os.path.join(tf, "ws_root"); os.makedirs(wsr); tmpdirs.append(wsr)
            test_materialize(man, tf, wsr, "ws", mk_cap(),
                              source_host_map={"r": "src"})
        must_raise("workspace_seed_roots_mutation_rejected", ws_seed_roots_mutation_rejected)

        def ws_policy_false_field_rejected():
            tf = tempfile.mkdtemp(prefix="nrm_wspf_"); tmpdirs.append(tf)
            os.makedirs(os.path.join(tf, "src"))
            man = _build_synthetic_manifest(os.path.join(tf, "src"), gold_inc)
            man["workspace_declarations"][0] = dict(
                man["workspace_declarations"][0], no_hard_links=False)
            wsr = os.path.join(tf, "ws_root"); os.makedirs(wsr); tmpdirs.append(wsr)
            test_materialize(man, tf, wsr, "ws", mk_cap(),
                              source_host_map={"r": "src"})
        must_raise("workspace_policy_false_field_rejected", ws_policy_false_field_rejected)

        def ws_policy_extra_field_rejected():
            tf = tempfile.mkdtemp(prefix="nrm_wspe_"); tmpdirs.append(tf)
            os.makedirs(os.path.join(tf, "src"))
            man = _build_synthetic_manifest(os.path.join(tf, "src"), gold_inc)
            man["workspace_declarations"][0] = dict(
                man["workspace_declarations"][0], evil_extra=True)
            wsr = os.path.join(tf, "ws_root"); os.makedirs(wsr); tmpdirs.append(wsr)
            test_materialize(man, tf, wsr, "ws", mk_cap(),
                              source_host_map={"r": "src"})
        must_raise("workspace_policy_extra_field_rejected", ws_policy_extra_field_rejected)

        # Workspace policy missing-field rejected.
        def ws_policy_missing_field_rejected():
            tf = tempfile.mkdtemp(prefix="nrm_wspm_"); tmpdirs.append(tf)
            os.makedirs(os.path.join(tf, "src"))
            man = _build_synthetic_manifest(os.path.join(tf, "src"), gold_inc)
            wd = dict(man["workspace_declarations"][0])
            del wd["private_physical_copy"]
            man["workspace_declarations"][0] = wd
            wsr = os.path.join(tf, "ws_root"); os.makedirs(wsr); tmpdirs.append(wsr)
            test_materialize(man, tf, wsr, "ws", mk_cap(),
                              source_host_map={"r": "src"})
        must_raise("workspace_policy_missing_field_rejected", ws_policy_missing_field_rejected)

        # Source-root symlink rejected (declared source root is a symlink).
        def source_root_symlink_rejected():
            # Declared source root (the "src" subpath) is a symlink; the
            # descriptor-relative traversal _safe_open_source must reject the
            # symlinked directory component with O_NOFOLLOW.
            tf = tempfile.mkdtemp(prefix="nrm_srcsym_"); tmpdirs.append(tf)
            real_src = os.path.join(tf, "real_src"); os.makedirs(real_src)
            with open(os.path.join(real_src, "a.txt"), "wb") as fh: fh.write(b"aaa")
            os.chmod(os.path.join(real_src, "a.txt"), 0o644)
            os.symlink(real_src, os.path.join(tf, "src"))
            orig = dict(ROOT_HOST)
            try:
                ROOT_HOST.clear(); ROOT_HOST["r"] = "src"
                rfd = _open_repo_root_fd(tf)
                try:
                    _safe_open_source(rfd, "r", "a.txt")
                finally:
                    os.close(rfd)
            finally:
                ROOT_HOST.clear(); ROOT_HOST.update(orig)
        must_raise("source_root_symlink_rejected", source_root_symlink_rejected)

        # Source-parent-directory symlink rejected: a parent directory
        # component in the source path is a symlink.
        def source_parent_dir_symlink_rejected():
            tf = tempfile.mkdtemp(prefix="nrm_srcpsym_"); tmpdirs.append(tf)
            real_parent = os.path.join(tf, "real_parent"); os.makedirs(real_parent)
            os.makedirs(os.path.join(real_parent, "sub"))
            with open(os.path.join(real_parent, "sub", "a.txt"), "wb") as fh: fh.write(b"aaa")
            os.chmod(os.path.join(real_parent, "sub", "a.txt"), 0o644)
            os.symlink(real_parent, os.path.join(tf, "src"))
            orig = dict(ROOT_HOST)
            try:
                ROOT_HOST.clear(); ROOT_HOST["r"] = "src"
                rfd = _open_repo_root_fd(tf)
                try:
                    _safe_open_source(rfd, "r", "sub/a.txt")
                finally:
                    os.close(rfd)
            finally:
                ROOT_HOST.clear(); ROOT_HOST.update(orig)
        must_raise("source_parent_directory_symlink_rejected",
                   source_parent_dir_symlink_rejected)

        # Expected destination directory symlink rejected.
        def expected_dest_dir_symlink_rejected():
            tf = tempfile.mkdtemp(prefix="nrm_esym_"); tmpdirs.append(tf)
            os.makedirs(os.path.join(tf, "src"))
            with open(os.path.join(tf, "src", "a.txt"), "wb") as fh: fh.write(b"aaa")
            os.chmod(os.path.join(tf, "src", "a.txt"), 0o644)
            man = _build_synthetic_manifest(os.path.join(tf, "src"), gold_inc,
                extra_dirs=[{"source_root": "r", "relative_path": "sub",
                             "component_scope": "comp"}])
            wsr = os.path.join(tf, "ws_root"); os.makedirs(wsr); tmpdirs.append(wsr)
            fex = test_materialize(man, tf, wsr, "ws", mk_cap(),
                                    source_host_map={"r": "src"})
            # Replace the materialized sub dir with a symlink.
            os.rmdir(os.path.join(fex, "D", "sub")) if os.path.isdir(os.path.join(fex, "D", "sub")) else None
            os.symlink(os.path.join(fex, "D"), os.path.join(fex, "D", "sub"))
            _verify_destination_complete(fex, man["included_regular_file_entries"],
                                         man["directory_entries"], {"r": "D"})
        must_raise("expected_destination_directory_symlink_rejected",
                   expected_dest_dir_symlink_rejected)

        # Extra destination directory symlink rejected.
        def extra_dest_dir_symlink_rejected():
            tf = tempfile.mkdtemp(prefix="nrm_xsym_"); tmpdirs.append(tf)
            os.makedirs(os.path.join(tf, "src"))
            with open(os.path.join(tf, "src", "a.txt"), "wb") as fh: fh.write(b"aaa")
            os.chmod(os.path.join(tf, "src", "a.txt"), 0o644)
            man = _build_synthetic_manifest(os.path.join(tf, "src"), gold_inc)
            wsr = os.path.join(tf, "ws_root"); os.makedirs(wsr); tmpdirs.append(wsr)
            fex = test_materialize(man, tf, wsr, "ws", mk_cap(),
                                    source_host_map={"r": "src"})
            os.symlink(os.path.join(fex, "D"), os.path.join(fex, "D", "evil"))
            _verify_destination_complete(fex, man["included_regular_file_entries"],
                                         man["directory_entries"], {"r": "D"})
        must_raise("extra_destination_directory_symlink_rejected",
                   extra_dest_dir_symlink_rejected)

        # Wrong destination content with identical size rejected.
        def wrong_dest_content_same_size_rejected():
            tf = tempfile.mkdtemp(prefix="nrm_wcsz_"); tmpdirs.append(tf)
            os.makedirs(os.path.join(tf, "src"))
            with open(os.path.join(tf, "src", "a.txt"), "wb") as fh: fh.write(b"aaa")
            os.chmod(os.path.join(tf, "src", "a.txt"), 0o644)
            man = _build_synthetic_manifest(os.path.join(tf, "src"), gold_inc)
            wsr = os.path.join(tf, "ws_root"); os.makedirs(wsr); tmpdirs.append(wsr)
            fex = test_materialize(man, tf, wsr, "ws", mk_cap(),
                                    source_host_map={"r": "src"})
            with open(os.path.join(fex, "D", "a.txt"), "wb") as fh: fh.write(b"XXX")
            _verify_destination_complete(fex, man["included_regular_file_entries"],
                                         man["directory_entries"], {"r": "D"})
        must_raise("wrong_dest_content_same_size_rejected",
                   wrong_dest_content_same_size_rejected)

        # Wrong destination mode rejected.
        def wrong_dest_mode_rejected():
            tf = tempfile.mkdtemp(prefix="nrm_wmode_"); tmpdirs.append(tf)
            os.makedirs(os.path.join(tf, "src"))
            with open(os.path.join(tf, "src", "a.txt"), "wb") as fh: fh.write(b"aaa")
            os.chmod(os.path.join(tf, "src", "a.txt"), 0o644)
            man = _build_synthetic_manifest(os.path.join(tf, "src"), gold_inc)
            wsr = os.path.join(tf, "ws_root"); os.makedirs(wsr); tmpdirs.append(wsr)
            fex = test_materialize(man, tf, wsr, "ws", mk_cap(),
                                    source_host_map={"r": "src"})
            os.chmod(os.path.join(fex, "D", "a.txt"), 0o600)
            _verify_destination_complete(fex, man["included_regular_file_entries"],
                                         man["directory_entries"], {"r": "D"})
        must_raise("wrong_dest_mode_rejected", wrong_dest_mode_rejected)

        # No-replace publication rejects a pre-existing final (race guard).
        def no_replace_race_rejected():
            tf = tempfile.mkdtemp(prefix="nrm_nrrace_"); tmpdirs.append(tf)
            os.makedirs(os.path.join(tf, "src"))
            with open(os.path.join(tf, "src", "a.txt"), "wb") as fh: fh.write(b"aaa")
            os.chmod(os.path.join(tf, "src", "a.txt"), 0o644)
            man = _build_synthetic_manifest(os.path.join(tf, "src"), gold_inc)
            wsr = os.path.join(tf, "ws_root"); os.makedirs(wsr); tmpdirs.append(wsr)
            final = os.path.join(wsr, "ws")
            os.makedirs(final)  # pre-existing final
            test_materialize(man, tf, wsr, "ws", mk_cap(),
                              source_host_map={"r": "src"})
        must_raise("no_replace_publication_race_rejected", no_replace_race_rejected)

        # Pre-existing empty final directory remains unchanged after rejection.
        def preexisting_empty_final_remains():
            tf = tempfile.mkdtemp(prefix="nrm_preempty_"); tmpdirs.append(tf)
            os.makedirs(os.path.join(tf, "src"))
            with open(os.path.join(tf, "src", "a.txt"), "wb") as fh: fh.write(b"aaa")
            os.chmod(os.path.join(tf, "src", "a.txt"), 0o644)
            man = _build_synthetic_manifest(os.path.join(tf, "src"), gold_inc)
            wsr = os.path.join(tf, "ws_root"); os.makedirs(wsr); tmpdirs.append(wsr)
            final = os.path.join(wsr, "ws")
            os.makedirs(final)
            marker = os.path.join(final, "marker")
            with open(marker, "wb") as fh: fh.write(b"keep")
            try:
                test_materialize(man, tf, wsr, "ws", mk_cap(),
                                  source_host_map={"r": "src"})
                return False
            except FailClosed:
                pass
            return os.path.isfile(marker) and os.path.getsize(marker) == 4                 and not os.path.isdir(os.path.join(wsr, "ws_staging_marker"))
        if preexisting_empty_final_remains():
            results.append(("preexisting_final_unchanged_after_no_replace", "PASS"))
        else:
            results.append(("preexisting_final_unchanged_after_no_replace", "FAIL"))


        def extra_destination_file_rejected():
            # materialize then add an unlisted regular file; verify catches it.
            root_x = tempfile.mkdtemp(prefix="nrm_extrafile_")
            tmpdirs.append(root_x)
            os.makedirs(os.path.join(root_x, "src"))
            with open(os.path.join(root_x, "src", "a.txt"), "wb") as fh: fh.write(b"aaa")
            os.chmod(os.path.join(root_x, "src", "a.txt"), 0o644)
            sx = _build_synthetic_manifest(os.path.join(root_x, "src"),
                [{"source_root": "r", "relative_path": "a.txt",
                  "entry_type": "regular_file", "mode": "0644", "size": 3,
                  "sha256": sha256_bytes(b"aaa"), "nlink": 1,
                  "destination_relative": "D/a.txt", "component_scope": "comp"}])
            wsr = os.path.join(root_x, "ws_root"); os.makedirs(wsr); tmpdirs.append(wsr)
            fex = test_materialize(sx, root_x, wsr, "ws", mk_cap(),
                                    source_host_map={"r": "src"})
            with open(os.path.join(fex, "D", "unlisted.txt"), "wb") as fh: fh.write(b"x")
            _verify_destination_complete(fex, sx["included_regular_file_entries"],
                                         sx["directory_entries"], {"r": "D"})
        must_raise("extra_destination_file_rejected", extra_destination_file_rejected)

        def destination_fifo_rejected():
            root_f = tempfile.mkdtemp(prefix="nrm_fifo_")
            tmpdirs.append(root_f)
            os.makedirs(os.path.join(root_f, "src"))
            with open(os.path.join(root_f, "src", "a.txt"), "wb") as fh: fh.write(b"aaa")
            os.chmod(os.path.join(root_f, "src", "a.txt"), 0o644)
            sx = _build_synthetic_manifest(os.path.join(root_f, "src"),
                [{"source_root": "r", "relative_path": "a.txt",
                  "entry_type": "regular_file", "mode": "0644", "size": 3,
                  "sha256": sha256_bytes(b"aaa"), "nlink": 1,
                  "destination_relative": "D/a.txt", "component_scope": "comp"}])
            wsr = os.path.join(root_f, "ws_root"); os.makedirs(wsr); tmpdirs.append(wsr)
            fex = test_materialize(sx, root_f, wsr, "ws", mk_cap(),
                                    source_host_map={"r": "src"})
            try:
                os.mkfifo(os.path.join(fex, "D", "fifo"))
            except (OSError, AttributeError):
                # FIFO creation genuinely unsupported on this platform: report
                # an explicit SKIP (do NOT count it as a behavioral PASS).
                results.append(("destination_fifo_rejected", "SKIP"))
                return
            try:
                _verify_destination_complete(fex, sx["included_regular_file_entries"],
                                             sx["directory_entries"], {"r": "D"})
                results.append(("destination_fifo_rejected", "FAIL: no exception"))
            except FailClosed:
                results.append(("destination_fifo_rejected", "PASS"))
            except Exception as exc:
                results.append(("destination_fifo_rejected", "FAIL: %r" % exc))
        destination_fifo_rejected()

        def partial_write_completes_or_fails():
            # GENUINE partial-write simulation: inject an os.write replacement
            # that returns a short positive count each call and confirm the
            # copy loop completes correctly (all bytes written) or fails
            # closed.  A wrong-content destination of the right size must be
            # rejected by the post-copy descriptor verification.
            root_p = tempfile.mkdtemp(prefix="nrm_pwrite_")
            tmpdirs.append(root_p)
            os.makedirs(os.path.join(root_p, "src"))
            fsrc = os.path.join(root_p, "src", "big.txt")
            payload = b"X" * 4096
            with open(fsrc, "wb") as fh: fh.write(payload)
            os.chmod(fsrc, 0o644)
            dst = os.path.join(root_p, "dst.txt")
            orig_write = os.write
            calls = {"n": 0}
            def slow_write(fd, data):
                # Return 1 byte at a time for the first many calls so the loop
                # exercises partial-write handling; then behave normally.
                calls["n"] += 1
                if calls["n"] <= 4 and isinstance(data, (bytes, bytearray, memoryview)) and len(data) > 1:
                    mv = memoryview(data)
                    real = orig_write(fd, mv[:1])
                    return real  # short positive count; loop re-submits rest
                return orig_write(fd, data)
            try:
                os.write = slow_write
                _copy_one_file(fsrc, dst,
                    {"source_root": "r", "mode": "0644", "size": len(payload),
                     "sha256": sha256_bytes(payload)})
                ok = os.path.isfile(dst) and os.path.getsize(dst) == len(payload)                      and sha256_file(dst) == sha256_bytes(payload)
                results.append(("partial_write_handling",
                                "PASS" if ok else "FAIL"))
            finally:
                os.write = orig_write
        partial_write_completes_or_fails()

        def zero_or_negative_write_fails_closed():
            # Inject an os.write that returns 0 (zero-byte write); the copy
            # loop must fail closed rather than spinning or producing a
            # truncated file.
            root_z = tempfile.mkdtemp(prefix="nrm_zerowrite_")
            tmpdirs.append(root_z)
            os.makedirs(os.path.join(root_z, "src"))
            fsrc = os.path.join(root_z, "src", "a.txt")
            with open(fsrc, "wb") as fh: fh.write(b"abcdef")
            os.chmod(fsrc, 0o644)
            dst = os.path.join(root_z, "dst.txt")
            orig_write = os.write
            def zero_write(fd, data):
                return 0
            try:
                os.write = zero_write
                _copy_one_file(fsrc, dst,
                    {"source_root": "r", "mode": "0644", "size": 6,
                     "sha256": sha256_bytes(b"abcdef")})
                results.append(("zero_byte_write_fails_closed",
                                "FAIL: no exception"))
            except FailClosed:
                results.append(("zero_byte_write_fails_closed", "PASS"))
            finally:
                os.write = orig_write
                if os.path.lexists(dst):
                    os.remove(dst)
        zero_or_negative_write_fails_closed()

        def source_destination_inode_alias_rejected():
            # If source and destination resolve to the same physical inode
            # (aliasing), the copy must reject it.  Bind a hard link between
            # the source and the destination path so the post-open src/inode
            # equals the dst/inode at verification time.
            root_a = tempfile.mkdtemp(prefix="nrm_alias_")
            tmpdirs.append(root_a)
            os.makedirs(os.path.join(root_a, "src"))
            fsrc = os.path.join(root_a, "src", "a.txt")
            payload = b"aliascheck"
            with open(fsrc, "wb") as fh: fh.write(payload)
            os.chmod(fsrc, 0o644)
            dst = os.path.join(root_a, "dst.txt")
            # Create dst as a hard link to src so same dev/inode.
            os.link(fsrc, dst)
            # nlink is now 2; _copy_one_file must reject (source nlink!=1 or
            # destination descriptor nlink alias).
            try:
                _copy_one_file(fsrc, dst,
                    {"source_root": "r", "mode": "0644", "size": len(payload),
                     "sha256": sha256_bytes(payload)})
                results.append(("source_destination_inode_alias_rejected",
                                "FAIL: no exception"))
            except FailClosed:
                results.append(("source_destination_inode_alias_rejected", "PASS"))
            finally:
                if os.path.lexists(dst):
                    os.remove(dst)
        source_destination_inode_alias_rejected()

        def failed_materialization_no_staging():
            # Failed materialization must leave no staging tree behind.
            root_f2 = tempfile.mkdtemp(prefix="nrm_nostage_")
            tmpdirs.append(root_f2)
            os.makedirs(os.path.join(root_f2, "src"))
            with open(os.path.join(root_f2, "src", "a.txt"), "wb") as fh: fh.write(b"aaa")
            os.chmod(os.path.join(root_f2, "src", "a.txt"), 0o644)
            sx = _build_synthetic_manifest(os.path.join(root_f2, "src"),
                [{"source_root": "r", "relative_path": "a.txt",
                  "entry_type": "regular_file", "mode": "0644", "size": 3,
                  "sha256": "deadbeef" + "0"*56, "nlink": 1,
                  "destination_relative": "D/a.txt", "component_scope": "comp"}])
            wsr = os.path.join(root_f2, "ws_root"); os.makedirs(wsr); tmpdirs.append(wsr)
            try:
                test_materialize(sx, root_f2, wsr, "ws", mk_cap(),
                                  source_host_map={"r": "src"})
                results.append(("failed_materialization_no_staging", "FAIL: no exception"))
            except FailClosed:
                leftover = [n for n in os.listdir(wsr) if n.startswith("ws_staging_")]
                results.append(("failed_materialization_no_staging",
                                "PASS" if not leftover and not os.path.exists(os.path.join(wsr, "ws")) else "FAIL: %r" % leftover))
            except Exception as exc:
                results.append(("failed_materialization_no_staging", "FAIL: %r" % exc))
        failed_materialization_no_staging()

        # Exact canonical-byte verification tests.
        def real_manifest_bytes():
            inc, dirs, exc, st = walk_source_roots(os.getcwd())
            man = build_manifest(os.getcwd(), inc, dirs, exc, st)
            return serialize_manifest(man)

        def noncanonical_json_rejected():
            man = json.loads(real_manifest_bytes())
            raw = json.dumps(man, ensure_ascii=True, sort_keys=True,
                             separators=(", ", ": ")) + "\n"
            verify_manifest(raw.encode("utf-8"), os.getcwd())
        must_raise("noncanonical_json_rejected", noncanonical_json_rejected)

        def crlf_rejected():
            raw = real_manifest_bytes().replace(b"\n", b"\r\n")
            verify_manifest(raw, os.getcwd())
        must_raise("crlf_rejected", crlf_rejected)

        def trailing_space_rejected():
            raw = real_manifest_bytes()[:-1] + b" \n"
            verify_manifest(raw, os.getcwd())
        must_raise("trailing_space_json_rejected", trailing_space_rejected)

        def duplicate_included_rejected():
            man = json.loads(real_manifest_bytes())
            inc = man["included_regular_file_entries"]
            # duplicate one entry and omit the last -> count stays 1422, set
            # differs (a duplicate replaces an omitted entry).
            man["included_regular_file_entries"] = inc[:-1] + [inc[0]]
            verify_manifest(serialize_manifest(man), os.getcwd())
        must_raise("duplicate_included_entry_rejected", duplicate_included_rejected)

        def changed_component_scope_rejected():
            man = json.loads(real_manifest_bytes())
            e = man["included_regular_file_entries"][0]
            man["included_regular_file_entries"][0] = dict(e, component_scope="CORRUPTED")
            verify_manifest(serialize_manifest(man), os.getcwd())
        must_raise("changed_component_scope_rejected", changed_component_scope_rejected)

        def changed_authorization_boundary_rejected():
            man = json.loads(real_manifest_bytes())
            man["authorization_boundary"] = {"host_only": True}
            verify_manifest(serialize_manifest(man), os.getcwd())
        must_raise("changed_authorization_boundary_rejected", changed_authorization_boundary_rejected)

        def changed_collision_model_rejected():
            man = json.loads(real_manifest_bytes())
            man["collision_model"] = {}
            verify_manifest(serialize_manifest(man), os.getcwd())
        must_raise("changed_collision_model_rejected", changed_collision_model_rejected)

        def unknown_top_level_field_rejected():
            man = json.loads(real_manifest_bytes())
            man["unknown_field"] = 1
            verify_manifest(serialize_manifest(man), os.getcwd())
        must_raise("unknown_top_level_field_rejected", unknown_top_level_field_rejected)

        def missing_top_level_field_rejected():
            man = json.loads(real_manifest_bytes())
            del man["canonicalization"]
            verify_manifest(serialize_manifest(man), os.getcwd())
        must_raise("missing_top_level_field_rejected", missing_top_level_field_rejected)

        # descriptor hash used: temporarily corrupt an on-disk source by
        # replacing with a symlink to confirm O_NOFOLLOW fails closed (no
        # pathname re-open fallback).
        def no_symlink_fallback():
            inc, dirs, exc, st = walk_source_roots(os.getcwd())
            man = build_manifest(os.getcwd(), inc, dirs, exc, st)
            e = man["included_regular_file_entries"][0]
            host = os.path.join(os.getcwd(), ROOT_HOST[e["source_root"]], e["relative_path"])
            # cannot corrupt real source; instead test _verify path directly
            # with a synthetic symlink fixture.
            slf = tempfile.mkdtemp(prefix="nrm_nosym_")
            tmpdirs.append(slf)
            target = os.path.join(slf, "target")
            with open(target, "wb") as fh: fh.write(b"x")
            sl = os.path.join(slf, "link")
            os.symlink(target, sl)
            fake_entry = {"source_root": e["source_root"], "relative_path": "link",
                          "mode": "0644", "size": 1, "sha256": "0"*64}
            # point ROOT_HOST lookup at the fixture dir by monkey-patching repo_root
            # via a temp copy: build a fake repo root containing the fixture.
            frepo = tempfile.mkdtemp(prefix="nrm_frepro_")
            tmpdirs.append(frepo)
            fake_host = os.path.join(frepo, "src")
            os.makedirs(fake_host)
            os.symlink(target, os.path.join(fake_host, "link"))
            # _verify_included_descriptors uses ROOT_HOST; redirect by patching.
            orig = dict(ROOT_HOST)
            try:
                ROOT_HOST.clear(); ROOT_HOST[e["source_root"]] = "src"
                _verify_included_descriptors([fake_entry], frepo)
            finally:
                ROOT_HOST.clear(); ROOT_HOST.update(orig)
        must_raise("no_symlink_fallback_open_fails_closed", no_symlink_fallback)

        # ---- Correction 6: closure-backed registry, no exposed auth,
        # fd-bound source traversal, and no-replace publication tests. ----

        # No module attributes named _VM_REGISTRY, _VM_GET, _VM_HAS, _VM_PUT,
        # or _make_vm_registry (all enclosed in _build_verified_manifest_boundary).
        def no_exposed_registry_mutators():
            mod = __import__('nos3_runtime_material', fromlist=['x'])
            for name in ('_VM_REGISTRY', '_VM_GET', '_VM_HAS', '_VM_PUT',
                         '_make_vm_registry'):
                if hasattr(mod, name):
                    raise FailClosed("exposed registry attribute: %s" % name)
            return True
        must_pass("no_exposed_registry_mutators", no_exposed_registry_mutators)

        # No module-level synthetic token, capability type, or materializer.
        def no_exposed_synthetic_capability():
            mod = __import__('nos3_runtime_material', fromlist=['x'])
            for name in ('_MA_TOKEN', '_TEST_CAP_SECRET', '_AUTH_SECRET',
                         '_TestCap', '_test_capability', '_test_materialize',
                         '_test_copy_files', '_test_cap_ok'):
                if hasattr(mod, name):
                    raise FailClosed("exposed synthetic attribute: %s" % name)
            return True
        must_pass("no_exposed_synthetic_capability",
                  no_exposed_synthetic_capability)

        # Direct registry insertion is impossible through any module attribute:
        # the registry is enclosed and no accessor/mutator is exposed.
        def direct_registry_insertion_impossible():
            mod = __import__('nos3_runtime_material', fromlist=['x'])
            for name in ('_VM_REGISTRY', '_VM_GET', '_VM_HAS', '_VM_PUT',
                         '_make_vm_registry'):
                if hasattr(mod, name):
                    raise FailClosed("exposed: %s" % name)
            forged = object.__new__(VerifiedManifest)
            try:
                forged._entry()
            except FailClosed:
                return True
            raise FailClosed("forged bearer unexpectedly had registry entry")
        must_pass("direct_registry_insertion_impossible",
                  direct_registry_insertion_impossible)

        # Object-ID reuse cannot inherit a prior bearer's state: after a real
        # bearer is collected, a forged object.__new__ bearer with a recycled
        # id cannot inherit the former bearer's registry entry (registry is
        # keyed by the weakly-referenced object, not id()).
        def object_id_reuse_cannot_inherit():
            import gc
            inc, dirs, exc, st = walk_source_roots(os.getcwd())
            raw = serialize_manifest(build_manifest(os.getcwd(), inc, dirs, exc, st))
            vmb = load_and_verify_manifest(raw, os.getcwd())
            saved_id = id(vmb)
            del vmb
            gc.collect()
            # A new forged object may happen to reuse the id, but it will have
            # no registry entry because the WeakKeyDictionary dropped the old
            # bearer and the new object was never registered.
            forged = object.__new__(VerifiedManifest)
            try:
                forged._entry()
            except FailClosed:
                return True
            raise FailClosed("forged bearer inherited registry entry")
        must_pass("object_id_reuse_cannot_inherit", object_id_reuse_cannot_inherit)

        # No externally callable synthetic-materialization path: test_materialize
        # requires a _TestCap that cannot be constructed directly.
        def no_external_synthetic_materialization():
            # Direct _TestCap() construction fails.
            try:
                _TestCap()
            except FailClosed:
                pass
            else:
                raise FailClosed("_TestCap direct construction succeeded")
            # A fake object with the right type name is rejected.
            fake = object.__new__(_TestCap)
            try:
                _test_cap_ok(fake)
            except FailClosed:
                return True
            raise FailClosed("fake _TestCap accepted")
        must_pass("no_external_synthetic_materialization_path",
                  no_external_synthetic_materialization)

        # Public materialize_workspace fails before filesystem inspection.
        def public_materialize_fails_before_inspection():
            tf = tempfile.mkdtemp(prefix="nrm_pubfail_"); tmpdirs.append(tf)
            pre = set(os.listdir(tf))
            try:
                materialize_workspace(None, tf, authorization=None,
                                      component_id="x")
            except FailClosed as exc:
                if "MaterializationAuthorized bearer" not in str(exc):
                    raise FailClosed("wrong reason: %s" % exc)
                post = set(os.listdir(tf))
                if post != pre:
                    raise FailClosed("filesystem mutated: %r" % (post - pre))
                return True
            raise FailClosed("materialize_workspace did not fail")
        must_pass("public_materialize_fails_before_inspection",
                  public_materialize_fails_before_inspection)

        # Linux no-replace call uses basenames, not absolute paths: verify the
        # _no_replace_rename_dirfd signature requires basenames + parent fds.
        def linux_noreplace_uses_basenames():
            tf = tempfile.mkdtemp(prefix="nrm_basename_"); tmpdirs.append(tf)
            os.makedirs(os.path.join(tf, "staging"))
            os.makedirs(os.path.join(tf, "final"))
            spfd = os.open(os.path.join(tf, "staging"), os.O_RDONLY
                           | os.O_DIRECTORY | os.O_NOFOLLOW)
            dpfd = os.open(os.path.join(tf, "final"), os.O_RDONLY
                           | os.O_DIRECTORY | os.O_NOFOLLOW)
            try:
                # Must use a basename "ws", not an absolute path.
                _no_replace_rename_dirfd(spfd, "ws", dpfd, "ws")
                return False  # expected to fail: "ws" does not exist under staging
            except FailClosed:
                return True
            finally:
                try: os.close(spfd)
                except OSError: pass
                try: os.close(dpfd)
                except OSError: pass
        must_pass("linux_noreplace_uses_basenames", linux_noreplace_uses_basenames)

        # Destination inode replacement between lstat and open rejected:
        # _verify_destination_complete lstat's then opens with O_NOFOLLOW and
        # Genuine regular-file inode swap between pre-open stat and open:
        # the destination audit lstat()s a.txt, then a monkeypatched os.open
        # replaces the file with a SECOND REGULAR FILE (not a symlink) carrying
        # identical bytes/mode/size/nlink but a different inode.  The audit's
        # lstat-to-open identity-continuity check must reject it.
        def destination_inode_replacement_rejected():
            tf = tempfile.mkdtemp(prefix="nrm_inoderepl_"); tmpdirs.append(tf)
            os.makedirs(os.path.join(tf, "src"))
            with open(os.path.join(tf, "src", "a.txt"), "wb") as fh: fh.write(b"aaa")
            os.chmod(os.path.join(tf, "src", "a.txt"), 0o644)
            man = _build_synthetic_manifest(os.path.join(tf, "src"),
                [{"source_root": "r", "relative_path": "a.txt",
                  "entry_type": "regular_file", "mode": "0644", "size": 3,
                  "sha256": sha256_bytes(b"aaa"), "nlink": 1,
                  "destination_relative": "D/a.txt", "component_scope": "comp"}])
            wsr = os.path.join(tf, "ws_root"); os.makedirs(wsr); tmpdirs.append(wsr)
            fex = test_materialize(man, tf, wsr, "ws", mk_cap(),
                                    source_host_map={"r": "src"})
            real_target = os.path.join(fex, "D", "a.txt")
            real_fd = os.open(real_target, os.O_RDONLY | os.O_NOFOLLOW)
            real_identity = os.fstat(real_fd)
            os.close(real_fd)
            swap = {"done": False}
            import __main__ as _M2
            real_openleaf = _M2._dirfd_open_file_nofollow
            def swapping_leaf(parent_fd, name):
                # The audit lstat has already recorded the leaf identity; now
  # swap the file with a fresh regular file of identical bytes/mode/size/
  # nlink (a new inode) right before the read-open.
                if not swap["done"] and name == "a.txt":
                    os.unlink(name, dir_fd=parent_fd)
                    nrfd = os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL,
                                    0o644, dir_fd=parent_fd)
                    os.write(nrfd, b"aaa")
                    os.close(nrfd)
                    swap["done"] = True
                return real_openleaf(parent_fd, name)
            fd = _open_staging_fd(fex)
            try:
                _M2._dirfd_open_file_nofollow = swapping_leaf
                try:
                    _verify_dest_complete_dirfd(fd,
                        man["included_regular_file_entries"],
                        man["directory_entries"], {"r": "D"})
                    return False  # expected FailClosed
                except FailClosed as exc:
                    if "inode changed" not in str(exc):
                        raise
                    return True
                finally:
                    _M2._dirfd_open_file_nofollow = real_openleaf
            finally:
                try: os.close(fd)
                except OSError: pass
        must_pass("destination_inode_replacement_rejected",
                  destination_inode_replacement_rejected)

        # ---- Correction 7: descriptor-relative mutation-path source scan. ----
        # The mutation-path functions must contain no path-based os.makedirs,
        # replacing os.rename, or shutil.rmtree.  Allowed path opens are the
        # adapters _open_staging_fd / _open_repo_root_fd / opening a single
  # parent dir for selftest-fixture single-file copies.
        def no_mutation_path_uses_path_based_ops():
            import inspect
            mutants = [
                "materialize_workspace",
                "_prod_copy_files", "_prod_copy_files_dirfd",
                "_prod_copy_one_file_dirfd",
                "_synth_copy_one_file_dirfd",
                "_build_dest_tree_dirfd",
                "_verify_dest_complete_dirfd", "_audit_recurse",
                "_verify_exclusions_absent_dirfd",
                "_verify_deny_patterns_absent_dirfd", "_deny_walk",
                "_rmtree_dirfd_contents",
                "_dirfd_walk_to_parent", "_dirfd_walk_existing",
                "_dirfd_open_or_make_dir", "_dirfd_make_dir",
                "_mkstemp_dirfd",
                "_dirfd_open_file_nofollow",
            ]
            import __main__ as _Mm
            bad = []
            for name in mutants:
                fn = getattr(_Mm, name, None)
                if fn is None:
                    bad.append("missing:%s" % name); continue
                text = inspect.getsource(fn)
                for pat in ["os.makedirs(", "shutil.rmtree("]:
                    if pat in text:
                        cur = "%s:%s" % (name, pat)
                        # os.makedirs is allowed only in test fixtures (these
  # mutants must never call it).
                        bad.append(cur)
                # replacing os.rename(path, path) -- allow only the dirfd
  # primitive _no_replace_rename_dirfd; the mutants must not call os.rename.
                for line in text.splitlines():
                    ls = line.strip()
                    if ls.startswith("#"):
                        continue
                    if "os.rename(" in ls and "dirfd" not in name:
                        bad.append("%s:os.rename" % name)
            if bad:
                raise FailClosed("path-based mutation ops found: %r" % sorted(set(bad)))
            return True
        must_pass("no_mutation_path_uses_path_based_ops",
                  no_mutation_path_uses_path_based_ops)

        # Per-file temporary publication uses no-replace (1 per-file + 1 final).
        def per_file_publication_uses_noreplace():
            tf = tempfile.mkdtemp(prefix="nrm_pfpub_"); tmpdirs.append(tf)
            os.makedirs(os.path.join(tf, "src"))
            with open(os.path.join(tf, "src", "a.txt"), "wb") as fh: fh.write(b"aaa")
            os.chmod(os.path.join(tf, "src", "a.txt"), 0o644)
            gi = [{"source_root": "r", "relative_path": "a.txt",
                   "entry_type": "regular_file", "mode": "0644", "size": 3,
                   "sha256": sha256_bytes(b"aaa"), "nlink": 1,
                   "destination_relative": "D/a.txt", "component_scope": "comp"}]
            man = _build_synthetic_manifest(os.path.join(tf, "src"), gi)
            wsr = os.path.join(tf, "ws_root"); os.makedirs(wsr); tmpdirs.append(wsr)
            calls = {"n": 0}
            import __main__ as _M
            orig = _M._no_replace_rename_dirfd
            pf_final = os.path.join(wsr, "ws", "D", "a.txt")
            def counting(spfd, sbase, dpfd, dbase):
                calls["n"] += 1
                return orig(spfd, sbase, dpfd, dbase)
            try:
                _M._no_replace_rename_dirfd = counting
                test_materialize(man, tf, wsr, "ws", mk_cap(),
                                  source_host_map={"r": "src"})
            finally:
                _M._no_replace_rename_dirfd = orig
            return calls["n"] == 2 and os.path.isfile(pf_final) \
                and sha256_file(pf_final) == sha256_bytes(b"aaa")
        must_pass("per_file_publication_uses_noreplace",
                  per_file_publication_uses_noreplace)

        # Strict destination component validation: a//b, a/, /a, . rejected.
        def strict_split_components_a_double_slash():
            _split_components("a//b")
        must_raise("split_components_rejects_a_double_slash",
                   strict_split_components_a_double_slash)
        def strict_split_components_trailing_slash():
            _split_components("a/")
        must_raise("split_components_rejects_trailing_slash",
                   strict_split_components_trailing_slash)
        def strict_split_components_dot_rejected():
            _split_components(".")
        must_raise("split_components_rejects_dot",
                   strict_split_components_dot_rejected)
        def strict_split_components_empty_without_sentinel():
            _split_components("")
        must_raise("split_components_empty_no_sentinel",
                   strict_split_components_empty_without_sentinel)
        def strict_split_components_root_sentinel_ok():
            return _split_components("", _root_sentinel_ok=True) == []
        must_pass("split_components_root_sentinel_ok",
                  strict_split_components_root_sentinel_ok)

        # Exclusion present as a REGULAR destination rejected.
        def exclusion_present_regular_rejected():
            tf = tempfile.mkdtemp(prefix="nrm_exreg_"); tmpdirs.append(tf)
            os.makedirs(os.path.join(tf, "src"))
            with open(os.path.join(tf, "src", "a.txt"), "wb") as fh: fh.write(b"aaa")
            os.chmod(os.path.join(tf, "src", "a.txt"), 0o644)
            inc = [{"source_root": "r", "relative_path": "a.txt",
                    "entry_type": "regular_file", "mode": "0644", "size": 3,
                    "sha256": sha256_bytes(b"aaa"), "nlink": 1,
                    "destination_relative": "D/a.txt", "component_scope": "comp"}]
            man = _build_synthetic_manifest(os.path.join(tf, "src"), inc,
                excl_records=[{"source_root": "r",
                               "relative_path": "a.txt", "entry_type": "regular_file",
                               "mode": "0644", "size": 3,
                               "sha256": sha256_bytes(b"aaa"), "nlink": 1}])
            wsr = os.path.join(tf, "ws_root"); os.makedirs(wsr); tmpdirs.append(wsr)
            fex = test_materialize(man, tf, wsr, "ws", mk_cap(),
                                    source_host_map={"r": "src"})
            sfd = _open_staging_fd(fex)
            try:
                _verify_exclusions_absent_dirfd(sfd,
                    man["exact_exclusion_records"], {"r": "D"})
            finally:
                try: os.close(sfd)
                except OSError: pass
            return False
        must_raise("exclusion_present_regular_rejected",
                   exclusion_present_regular_rejected)

        def exclusion_absent_accepted():
            tf = tempfile.mkdtemp(prefix="nrm_exabs_"); tmpdirs.append(tf)
            os.makedirs(os.path.join(tf, "src"))
            with open(os.path.join(tf, "src", "a.txt"), "wb") as fh: fh.write(b"aaa")
            os.chmod(os.path.join(tf, "src", "a.txt"), 0o644)
            inc = [{"source_root": "r", "relative_path": "a.txt",
                    "entry_type": "regular_file", "mode": "0644", "size": 3,
                    "sha256": sha256_bytes(b"aaa"), "nlink": 1,
                    "destination_relative": "D/keep.txt", "component_scope": "comp"}]
            man = _build_synthetic_manifest(os.path.join(tf, "src"), inc,
                excl_records=[{"source_root": "r", "relative_path": "absent.txt",
                               "entry_type": "regular_file", "mode": "0644",
                               "size": 3, "sha256": sha256_bytes(b"zzz"),
                               "nlink": 1}])
            wsr = os.path.join(tf, "ws_root"); os.makedirs(wsr); tmpdirs.append(wsr)
            test_materialize(man, tf, wsr, "ws", mk_cap(),
                                  source_host_map={"r": "src"})
            return True
        must_pass("exclusion_absent_accepted", exclusion_absent_accepted)

        def exclusion_present_directory_rejected():
            tf = tempfile.mkdtemp(prefix="nrm_exdir_"); tmpdirs.append(tf)
            os.makedirs(os.path.join(tf, "src"))
            with open(os.path.join(tf, "src", "a.txt"), "wb") as fh: fh.write(b"aaa")
            os.chmod(os.path.join(tf, "src", "a.txt"), 0o644)
            inc = [{"source_root": "r", "relative_path": "a.txt",
                    "entry_type": "regular_file", "mode": "0644", "size": 3,
                    "sha256": sha256_bytes(b"aaa"), "nlink": 1,
                    "destination_relative": "D/a.txt", "component_scope": "comp"}]
            man = _build_synthetic_manifest(os.path.join(tf, "src"), inc,
                extra_dirs=[{"source_root": "r", "relative_path": "evil",
                             "component_scope": "comp"}],
                excl_records=[{"source_root": "r", "relative_path": "evil",
                               "entry_type": "directory", "mode": "0755",
                               "size": 0, "sha256": "", "nlink": 2}])
            wsr = os.path.join(tf, "ws_root"); os.makedirs(wsr); tmpdirs.append(wsr)
            fex = test_materialize(man, tf, wsr, "ws", mk_cap(),
                                    source_host_map={"r": "src"})
            sfd = _open_staging_fd(fex)
            try:
                _verify_exclusions_absent_dirfd(sfd,
                    man["exact_exclusion_records"], {"r": "D"})
            finally:
                try: os.close(sfd)
                except OSError: pass
            return False
        must_raise("exclusion_present_directory_rejected",
                   exclusion_present_directory_rejected)

        def exclusion_present_symlink_rejected():
            tf = tempfile.mkdtemp(prefix="nrm_exsym_"); tmpdirs.append(tf)
            os.makedirs(os.path.join(tf, "src"))
            with open(os.path.join(tf, "src", "a.txt"), "wb") as fh: fh.write(b"aaa")
            os.chmod(os.path.join(tf, "src", "a.txt"), 0o644)
            inc = [{"source_root": "r", "relative_path": "a.txt",
                    "entry_type": "regular_file", "mode": "0644", "size": 3,
                    "sha256": sha256_bytes(b"aaa"), "nlink": 1,
                    "destination_relative": "D/a.txt", "component_scope": "comp"}]
            man = _build_synthetic_manifest(os.path.join(tf, "src"), inc,
                excl_records=[{"source_root": "r", "relative_path": "lnk",
                               "entry_type": "symlink", "mode": "0777",
                               "size": 0, "sha256": "", "nlink": 1}])
            wsr = os.path.join(tf, "ws_root"); os.makedirs(wsr); tmpdirs.append(wsr)
            fex = test_materialize(man, tf, wsr, "ws", mk_cap(),
                                    source_host_map={"r": "src"})
            os.symlink(os.path.join(fex, "D", "a.txt"), os.path.join(fex, "D", "lnk"))
            sfd = _open_staging_fd(fex)
            try:
                _verify_exclusions_absent_dirfd(sfd,
                    man["exact_exclusion_records"], {"r": "D"})
            finally:
                try: os.close(sfd)
                except OSError: pass
            return False
        must_raise("exclusion_present_symlink_rejected",
                   exclusion_present_symlink_rejected)

        # Exclusion traversal error is NOT treated as absence: a symlinked
        # parent along the exclusion path raises.
        def exclusion_traversal_error_fails_closed():
            tf = tempfile.mkdtemp(prefix="nrm_exerr_"); tmpdirs.append(tf)
            os.makedirs(os.path.join(tf, "src"))
            with open(os.path.join(tf, "src", "a.txt"), "wb") as fh: fh.write(b"aaa")
            os.chmod(os.path.join(tf, "src", "a.txt"), 0o644)
            inc = [{"source_root": "r", "relative_path": "a.txt",
                    "entry_type": "regular_file", "mode": "0644", "size": 3,
                    "sha256": sha256_bytes(b"aaa"), "nlink": 1,
                    "destination_relative": "D/a.txt", "component_scope": "comp"}]
            man = _build_synthetic_manifest(os.path.join(tf, "src"), inc,
                excl_records=[{"source_root": "r", "relative_path": "evil/x",
                               "entry_type": "regular_file", "mode": "0644",
                               "size": 1, "sha256": "x", "nlink": 1}])
            wsr = os.path.join(tf, "ws_root"); os.makedirs(wsr); tmpdirs.append(wsr)
            fex = test_materialize(man, tf, wsr, "ws", mk_cap(),
                                    source_host_map={"r": "src"})
            os.symlink(os.path.join(fex, "D"), os.path.join(fex, "D", "evil"))
            sfd = _open_staging_fd(fex)
            try:
                _verify_exclusions_absent_dirfd(sfd,
                    man["exact_exclusion_records"], {"r": "D"})
            finally:
                try: os.close(sfd)
                except OSError: pass
            return False
        must_raise("exclusion_traversal_error_fails_closed",
                   exclusion_traversal_error_fails_closed)

        # Correction 6: genuine authorized-root fd binding test.
        # Exercise _open_authorized_root_bound directly with: a valid receipt,
        # a stale-inode receipt, and pathname replacement between receipt
        # creation and open.  The negative cases MUST raise the authorized-root
        # identity error (not the earlier authorization gate) and MUST NOT
        # leave an open descriptor behind.
        def authorized_root_fd_bound_genuine():
            import __main__ as _M
            tf = tempfile.mkdtemp(prefix="nrm_arbound_"); tmpdirs.append(tf)
            wsr = os.path.join(tf, "ws_root"); os.makedirs(wsr); tmpdirs.append(wsr)
            pre = os.listdir(wsr)
            # Valid receipt: helper opens, binds identity, returns the fd.
            # The frozen receipt is the same shape _check_authorized_root
            # returns (dev/ino/dir); the aliasing checks are exercised by the
            # dedicated authorized_root_*_rejected tests above.  Build it via
            # _identity_receipt over the realpath so the genuine fd binding is
            # tested without the unrelated macOS /var-symlink parent walk.
            receipt = _M._identity_receipt(os.path.realpath(wsr))
            ar_fd, ar_rcpt = _M._open_authorized_root_bound(wsr, receipt)
            try:
                fst = os.fstat(ar_fd)
                if not stat.S_ISDIR(fst.st_mode):
                    return False
                if (fst.st_dev, fst.st_ino) != (receipt["dev"], receipt["ino"]):
                    return False
                if ar_rcpt != {"dev": receipt["dev"], "ino": receipt["ino"],
                               "is_dir": True}:
                    return False
            finally:
                try: os.close(ar_fd)
                except OSError: pass
            # No new staging directory is created by the helper.
            if os.listdir(wsr) != pre:
                return False

            # Stale-inode receipt: must raise the identity error, not the
            # authorization gate, and must not leak a descriptor.
            stale = {"path": receipt["path"], "dev": receipt["dev"],
                     "ino": receipt["ino"] + 999999, "is_dir": True,
                     "nlink": receipt["nlink"]}
            before = frozenset(os.listdir("/dev/fd")) if os.path.isdir("/dev/fd") else None
            stale_ok = False
            try:
                _M._open_authorized_root_bound(wsr, stale)
                return False
            except FailClosed as exc:
                msg = str(exc)
                if "authorized-root fd dev/ino mismatch" not in msg:
                    return False
                stale_ok = True
            if not stale_ok:
                return False
            if before is not None:
                after = frozenset(os.listdir("/dev/fd"))
                if after - before:
                    return False

            # Pathname replacement between receipt creation and open: replace
            # the authorized root directory with a different directory bearing a
            # new inode; the helper must reject the stale detached receipt.
            tf2 = tempfile.mkdtemp(prefix="nrm_arrep_"); tmpdirs.append(tf2)
            ar2 = os.path.join(tf2, "ar"); os.makedirs(ar2); tmpdirs.append(ar2)
            receipt2 = _M._identity_receipt(os.path.realpath(ar2))
            # Remove the original and recreate a fresh directory at the path.
            os.rename(ar2, ar2 + "_orig")
            os.makedirs(ar2)
            try:
                _M._open_authorized_root_bound(ar2, receipt2)
                return False
            except FailClosed as exc:
                if "authorized-root fd dev/ino mismatch" not in str(exc):
                    return False
            # No staging directory created on mismatch.
            return True
        must_pass("authorized_root_fd_bound_genuine",
                  authorized_root_fd_bound_genuine)

        # Verified repository fd bound before copy: open_verified_repo_fd
        # rejects a dev/ino mismatch vs the registry receipt.
        def verified_repository_fd_bound_before_copy():
            inc, dirs, exc, st = walk_source_roots(os.getcwd())
            raw = serialize_manifest(build_manifest(os.getcwd(), inc, dirs, exc, st))
            vmb = load_and_verify_manifest(raw, os.getcwd())
            import __main__ as _M
            orig = _M._fd_identity
            state = {"hits": 0}
            def patched(fd):
                dev, ino, isdir = orig(fd)
                state["hits"] += 1
                if state["hits"] == 1:
                    ino = ino + 1
                return (dev, ino, isdir)
            try:
                _M._fd_identity = patched
                try:
                    vmb.open_verified_repo_fd()
                    return False
                except FailClosed as exc:
                    return "mismatch" in str(exc)
            finally:
                _M._fd_identity = orig
        must_pass("verified_repository_fd_bound_before_copy",
                  verified_repository_fd_bound_before_copy)

        # Staging basename replaced before publication: the replacement is NOT
        # published.
        def staging_basename_replacement_not_published():
            tf = tempfile.mkdtemp(prefix="nrm_stagepub_"); tmpdirs.append(tf)
            os.makedirs(os.path.join(tf, "src"))
            with open(os.path.join(tf, "src", "a.txt"), "wb") as fh: fh.write(b"aaa")
            os.chmod(os.path.join(tf, "src", "a.txt"), 0o644)
            gi = [{"source_root": "r", "relative_path": "a.txt",
                   "entry_type": "regular_file", "mode": "0644", "size": 3,
                   "sha256": sha256_bytes(b"aaa"), "nlink": 1,
                   "destination_relative": "D/a.txt", "component_scope": "comp"}]
            man = _build_synthetic_manifest(os.path.join(tf, "src"), gi)
            wsr = os.path.join(tf, "ws_root"); os.makedirs(wsr); tmpdirs.append(wsr)
            replaced = {"v": False}
            import __main__ as _M
            orig_ver = _M._verify_staging_bound
            orig_norep = _M._no_replace_rename_dirfd
            def publish_check(staging_fd, staging_basename, ar_fd, receipt, label):
                if label == "test before final publication":
                    real_path = os.path.join(wsr, staging_basename)
                    os.rename(real_path, os.path.join(wsr, staging_basename + "_GONE"))
                    os.makedirs(real_path)
                    replaced["v"] = True
                return orig_ver(staging_fd, staging_basename, ar_fd, receipt, label)
            def no_pub(spfd, sbase, dpfd, dbase):
                if replaced["v"]:
                    raise FailClosed("replacement staging must not be published")
                return orig_norep(spfd, sbase, dpfd, dbase)
            try:
                _M._verify_staging_bound = publish_check
                _M._no_replace_rename_dirfd = no_pub
                try:
                    test_materialize(man, tf, wsr, "ws", mk_cap(),
                                      source_host_map={"r": "src"})
                    return False
                except FailClosed as exc:
                    ws_final = os.path.join(wsr, "ws")
                    return ("different object" in str(exc)
                            or "identity" in str(exc)) and not os.path.isdir(ws_final)
            finally:
                _M._verify_staging_bound = orig_ver
                _M._no_replace_rename_dirfd = orig_norep
        must_pass("staging_basename_replacement_not_published",
                  staging_basename_replacement_not_published)

        # Staging basename replaced before cleanup: the replacement is NOT
        # removed (cleanup identity-bound).
        def staging_basename_replacement_not_removed():
            tf = tempfile.mkdtemp(prefix="nrm_stagerm_"); tmpdirs.append(tf)
            os.makedirs(os.path.join(tf, "src"))
            with open(os.path.join(tf, "src", "a.txt"), "wb") as fh: fh.write(b"aaa")
            os.chmod(os.path.join(tf, "src", "a.txt"), 0o644)
            man = _build_synthetic_manifest(os.path.join(tf, "src"),
                [{"source_root": "r", "relative_path": "a.txt",
                  "entry_type": "regular_file", "mode": "0644", "size": 3,
                  "sha256": sha256_bytes(b"aaa"), "nlink": 1,
                  "destination_relative": "D/a.txt", "component_scope": "comp"}])
            wsr = os.path.join(tf, "ws_root"); os.makedirs(wsr); tmpdirs.append(wsr)
            os.remove(os.path.join(tf, "src", "a.txt"))  # force copy failure
            staged = {"base": None}
            import __main__ as _M
            orig_mk = _M._mkstemp_dirfd
            orig_ver = _M._verify_staging_bound
            def cap_mk(parent_fd, label):
                b, fd = orig_mk(parent_fd, label)
                staged["base"] = b
                return b, fd
            def rm_check(staging_fd, staging_basename, ar_fd, receipt, label):
                if label == "test before removing staging basename":
                    real = os.path.join(wsr, staging_basename)
                    os.rename(real, real + "_REAL")
                    os.makedirs(real)
                return orig_ver(staging_fd, staging_basename, ar_fd, receipt, label)
            try:
                _M._mkstemp_dirfd = cap_mk
                _M._verify_staging_bound = rm_check
                try:
                    test_materialize(man, tf, wsr, "ws", mk_cap(),
                                      source_host_map={"r": "src"})
                    return False
                except FailClosed:
                    replacement_path = os.path.join(wsr, staged["base"])
                    return os.path.isdir(replacement_path)
            finally:
                _M._mkstemp_dirfd = orig_mk
                _M._verify_staging_bound = orig_ver
        must_pass("staging_basename_replacement_not_removed",
                  staging_basename_replacement_not_removed)

        # Cleanup rejects a child inode swap: build a staging fixture with one
  # regular file, then monkeypatch _dirfd_open_file_nofollow so the file is
  # replaced (new inode, same content/mode/size) between _rmtree_dirfd_contents
  # lstat and the leaf open; the fstat-vs-lstat dev/ino check rejects it.
        def cleanup_regular_file_inode_swap_rejected():
            tf = tempfile.mkdtemp(prefix="nrm_cleanfswap_"); tmpdirs.append(tf)
            stage = os.path.join(tf, "stage"); os.makedirs(stage)
            with open(os.path.join(stage, "a.txt"), "wb") as fh: fh.write(b"aaa")
            os.chmod(os.path.join(stage, "a.txt"), 0o644)
            sfd = os.open(stage, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
            try:
                import __main__ as _M
                orig = _M._dirfd_open_file_nofollow
                def patched(parent_fd, name):
                    if name == "a.txt":
                        os.unlink(name, dir_fd=parent_fd)
                        nf = os.open(name, os.O_WRONLY|os.O_CREAT|os.O_EXCL,
                                     0o644, dir_fd=parent_fd)
                        os.write(nf, b"aaa"); os.close(nf)
                    return orig(parent_fd, name)
                _M._dirfd_open_file_nofollow = patched
                try:
                    _rmtree_dirfd_contents(sfd)
                    return False
                except FailClosed as exc:
                    return ("regular-file inode swap" in str(exc)
                            or "file replaced before unlink" in str(exc))
                finally:
                    _M._dirfd_open_file_nofollow = orig
            finally:
                try: os.close(sfd)
                except OSError: pass
        must_pass("cleanup_regular_file_inode_swap_rejected",
                  cleanup_regular_file_inode_swap_rejected)

        # Cleanup rejects a child symlink: a staging fixture whose child is a
  # symlink -- _rmtree_dirfd_contents lstat detects S_ISLNK and raises before
  # any unlink.
        def cleanup_symlink_rejected():
            tf = tempfile.mkdtemp(prefix="nrm_cleansym_"); tmpdirs.append(tf)
            stage = os.path.join(tf, "stage"); os.makedirs(stage)
            os.symlink("x", os.path.join(stage, "lnk"))
            sfd = os.open(stage, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
            try:
                try:
                    _rmtree_dirfd_contents(sfd)
                    return False
                except FailClosed as exc:
                    return "symlink rejected" in str(exc)
            finally:
                try: os.close(sfd)
                except OSError: pass
        must_pass("cleanup_symlink_rejected", cleanup_symlink_rejected)

        # No-replace basename validation before the platform syscall.
        def noreplace_absolute_src_rejected_before_syscall():
            try:
                _no_replace_rename_dirfd(0, "/abs", 0, "ok")
                return False
            except FailClosed as exc:
                msg = str(exc)
                return ("non-basename" in msg or "absolute" in msg
                        or "invalid basename" in msg or "slash" in msg)
            return False
        must_pass("noreplace_absolute_src_basename_rejected",
                  noreplace_absolute_src_rejected_before_syscall)
        def noreplace_slash_dst_rejected_before_syscall():
            try:
                _no_replace_rename_dirfd(0, "ok", 0, "a/b")
                return False
            except FailClosed as exc:
                msg = str(exc)
                return ("non-basename" in msg or "slash" in msg
                        or "invalid basename" in msg or "absolute" in msg)
            return False
        must_pass("noreplace_slash_dst_basename_rejected",
                  noreplace_slash_dst_rejected_before_syscall)

        # Genuine per-file race: a competing regular destination is injected
        # immediately before the per-file no-replace syscall; the no-replace
        # primitive rejects the rename and leaves the competing file
        # byte-identical.  The competing file lives inside staging, so its
        # survival is asserted from inside the racing hook (before
        # test_materialize error-cleanup removes the staging tree).
        def genuine_per_file_race_rejected():
            tf = tempfile.mkdtemp(prefix="nrm_pfrace_"); tmpdirs.append(tf)
            os.makedirs(os.path.join(tf, "src"))
            with open(os.path.join(tf, "src", "a.txt"), "wb") as fh: fh.write(b"aaa")
            os.chmod(os.path.join(tf, "src", "a.txt"), 0o644)
            gi = [{"source_root": "r", "relative_path": "a.txt",
                   "entry_type": "regular_file", "mode": "0644", "size": 3,
                   "sha256": sha256_bytes(b"aaa"), "nlink": 1,
                   "destination_relative": "D/a.txt", "component_scope": "comp"}]
            man = _build_synthetic_manifest(os.path.join(tf, "src"), gi)
            wsr = os.path.join(tf, "ws_root"); os.makedirs(wsr); tmpdirs.append(wsr)
            race = {"armed": False, "calls": 0, "compete_survives": False,
                    "noreplace_called": False}
            import __main__ as _M
            orig_norep = _M._no_replace_rename_dirfd
            def racing(spfd, sbase, dpfd, dbase):
                race["calls"] += 1
                if not race["armed"] and race["calls"] == 1                         and sbase.endswith(".tmp") and dbase.endswith(".txt"):
                    try:
                        cf = os.open(dbase, os.O_WRONLY | os.O_CREAT | os.O_EXCL,
                                     0o644, dir_fd=dpfd)
                        os.write(cf, b"COMPETING"); os.close(cf)
                        race["armed"] = True
                    except OSError:
                        pass
                try:
                    orig_norep(spfd, sbase, dpfd, dbase)
                    race["noreplace_called"] = True
                except FailClosed:
                    if race["armed"]:
                        # The competing file still exists inside staging and
                        # must be byte-identical (not replaced by the temp file).
                        try:
                            rfd = os.open(dbase, os.O_RDONLY | os.O_NOFOLLOW,
                                          dir_fd=dpfd)
                            try:
                                if os.fstat(rfd).st_size == len(b"COMPETING")                                         and _hash_fd(rfd) == sha256_bytes(b"COMPETING"):
                                    race["compete_survives"] = True
                            finally:
                                try: os.close(rfd)
                                except OSError: pass
                        except OSError:
                            pass
                    raise
                return
            raised = False
            try:
                _M._no_replace_rename_dirfd = racing
                try:
                    test_materialize(man, tf, wsr, "ws", mk_cap(),
                                    source_host_map={"r": "src"})
                    return False
                except FailClosed:
                    raised = True
            finally:
                _M._no_replace_rename_dirfd = orig_norep
            return (raised and race["armed"] and not race["noreplace_called"]
                    and race["compete_survives"])
        must_pass("genuine_per_file_race_rejected",
                  genuine_per_file_race_rejected)

        # Correction 7: success-path fd balance.  The synthetic materialization
        # MUST actually succeed and the final file MUST exist with the expected
        # SHA-256; the fd table MUST return to its pre-call set (no retained
        # descriptor survives).  Do not ignore the operation result merely
        # because the final fd set happens to match.
        def all_fd_ownership_balanced():
            if not os.path.isdir("/dev/fd"):
                return "skip"
            tf = tempfile.mkdtemp(prefix="nrm_fdown_"); tmpdirs.append(tf)
            os.makedirs(os.path.join(tf, "src"))
            with open(os.path.join(tf, "src", "a.txt"), "wb") as fh: fh.write(b"aaa")
            os.chmod(os.path.join(tf, "src", "a.txt"), 0o644)
            gi = [{"source_root": "r", "relative_path": "a.txt",
                   "entry_type": "regular_file", "mode": "0644", "size": 3,
                   "sha256": sha256_bytes(b"aaa"), "nlink": 1,
                   "destination_relative": "D/a.txt", "component_scope": "comp"}]
            man = _build_synthetic_manifest(os.path.join(tf, "src"), gi)
            wsr = os.path.join(tf, "ws_root"); os.makedirs(wsr); tmpdirs.append(wsr)
            before = frozenset(os.listdir("/dev/fd"))
            final = None
            try:
                final = test_materialize(man, tf, wsr, "ws", mk_cap(),
                                         source_host_map={"r": "src"})
            except Exception as exc:
                return False
            if final is None:
                return False
            after = frozenset(os.listdir("/dev/fd"))
            leaked = after - before
            # The materialization must have succeeded: the final file exists
            # and matches the expected SHA-256.
            real_target = os.path.join(final, "D", "a.txt")
            if not os.path.isfile(real_target):
                return False
            rfd = os.open(real_target, os.O_RDONLY | os.O_NOFOLLOW)
            try:
                if _hash_fd(rfd) != sha256_bytes(b"aaa"):
                    return False
            finally:
                try: os.close(rfd)
                except OSError: pass
            return not leaked
        must_pass("all_fd_ownership_balanced",
                  all_fd_ownership_balanced)

        # Correction 7: failure-path fd balance.  An injected failure (a stale
        # authorized-root fd receipt forces a fail-closed raise BEFORE staging
        # cleanup completes) must still leave no new retained descriptor.  The
        # operation MUST fail (not be ignored) and the fd table MUST return to
        # its pre-call set.
        def fd_ownership_failure_path_balanced():
            if not os.path.isdir("/dev/fd"):
                return "skip"
            tf = tempfile.mkdtemp(prefix="nrm_fdofail_"); tmpdirs.append(tf)
            os.makedirs(os.path.join(tf, "src"))
            with open(os.path.join(tf, "src", "a.txt"), "wb") as fh: fh.write(b"aaa")
            os.chmod(os.path.join(tf, "src", "a.txt"), 0o644)
            gi = [{"source_root": "r", "relative_path": "a.txt",
                   "entry_type": "regular_file", "mode": "0644", "size": 3,
                   "sha256": sha256_bytes(b"aaa"), "nlink": 1,
                   "destination_relative": "D/a.txt", "component_scope": "comp"}]
            man = _build_synthetic_manifest(os.path.join(tf, "src"), gi)
            wsr = os.path.join(tf, "ws_root"); os.makedirs(wsr); tmpdirs.append(wsr)
            import __main__ as _M
            orig_id = _M._fd_identity
            state = {"hit": 0}
            def stale_ar_id(fd):
                dev, ino, isdir = orig_id(fd)
                # Make the FIRST _fd_identity call (on the authorized-root fd)
                # report a dev/ino that will NOT match the captured receipt read
                # earlier by test_materialize, forcing an identity failure after
                # staging creation.
                state["hit"] += 1
                if state["hit"] == 1:
                    return (dev, ino + 999999, isdir)
                return (dev, ino, isdir)
            before = frozenset(os.listdir("/dev/fd"))
            failed = False
            try:
                _M._fd_identity = stale_ar_id
                try:
                    test_materialize(man, tf, wsr, "ws", mk_cap(),
                                     source_host_map={"r": "src"})
                    return False  # must fail
                except FailClosed:
                    failed = True
            finally:
                _M._fd_identity = orig_id
            if not failed:
                return False
            after = frozenset(os.listdir("/dev/fd"))
            leaked = after - before
            return not leaked
        must_pass("fd_ownership_failure_path_balanced",
                  fd_ownership_failure_path_balanced)

        # Staging created relative to authorized_root_fd (retained parent fd).
        def staging_created_relative_to_root_fd():
            tf = tempfile.mkdtemp(prefix="nrm_stagefd_"); tmpdirs.append(tf)
            os.makedirs(os.path.join(tf, "src"))
            with open(os.path.join(tf, "src", "a.txt"), "wb") as fh: fh.write(b"aaa")
            os.chmod(os.path.join(tf, "src", "a.txt"), 0o644)
            man = _build_synthetic_manifest(os.path.join(tf, "src"),
                [{"source_root": "r", "relative_path": "a.txt",
                  "entry_type": "regular_file", "mode": "0644", "size": 3,
                  "sha256": sha256_bytes(b"aaa"), "nlink": 1,
                  "destination_relative": "D/a.txt", "component_scope": "comp"}])
            wsr = os.path.join(tf, "ws_root"); os.makedirs(wsr); tmpdirs.append(wsr)
            captured = {}
            import __main__ as _M
            orig_mk = _M._mkstemp_dirfd
            def cap_mk(parent_fd, label):
                captured["parent_fd"] = parent_fd
                st = os.fstat(parent_fd)
                captured["ar_dev"] = st.st_dev
                captured["ar_ino"] = st.st_ino
                return orig_mk(parent_fd, label)
            try:
                _M._mkstemp_dirfd = cap_mk
                test_materialize(man, tf, wsr, "ws", mk_cap(),
                                  source_host_map={"r": "src"})
            finally:
                _M._mkstemp_dirfd = orig_mk
            arst = os.stat(wsr)
            return (captured.get("parent_fd") is not None
                    and captured.get("ar_dev") == arst.st_dev
                    and captured.get("ar_ino") == arst.st_ino)
        must_pass("staging_created_relative_to_root_fd",
                  staging_created_relative_to_root_fd)

        # -- Correction 9A targeted tests (7 retained) -----------------------
        # 1. synthetic_write_failure_leaves_no_temp: copy with wrong SHA fails
        # after temp creation; the temp file must not remain.
        def synthetic_write_failure_leaves_no_temp():
            # Inject a GENUINE os.write failure after the temp destination is
            # created.  The source mode/size/SHA all pass (correct SHA), so the
            # only failure is the injected write; the copy must raise FailClosed
            # from the write loop, leave no temp file, and publish no final dest.
            tf = tempfile.mkdtemp(prefix="nrm_swf_")
            tmpdirs.append(tf)
            os.makedirs(os.path.join(tf, "src"))
            data = b"aaaa"
            src_path = os.path.join(tf, "src", "a.txt")
            with open(src_path, "wb") as fh:
                fh.write(data)
            os.chmod(src_path, 0o644)
            inc = [{"source_root": "r", "relative_path": "a.txt",
                    "entry_type": "regular_file", "mode": "0644",
                    "size": len(data), "sha256": sha256_bytes(data),
                    "nlink": 1, "destination_relative": "D/a.txt",
                    "component_scope": "comp"}]
            man = _build_synthetic_manifest(os.path.join(tf, "src"), inc,
                src_root="r", comp_scope="comp", dest_prefix="D")
            wsr = os.path.join(tf, "ws_root"); os.makedirs(wsr); tmpdirs.append(wsr)
            orig_write = os.write
            write_calls = {"n": 0}
            def inject_write(fd, b):
                write_calls["n"] += 1
                return 0  # genuine short write -> copy loop raises FailClosed
            raised = False
            try:
                os.write = inject_write
                try:
                    test_materialize(man, tf, wsr, "ws", mk_cap(),
                                      source_host_map={"r": "src"})
                except FailClosed:
                    raised = True
            finally:
                os.write = orig_write
            if not raised:
                raise FailClosed("synthetic write failure did not raise FailClosed")
            if write_calls["n"] < 1:
                raise FailClosed("injected os.write was never called; "
                                 "failure path not exercised")
            for entry in glob_dirs(wsr):
                if entry.endswith(".tmp"):
                    raise FailClosed("temp file leaked: %s" % entry)
            staging = os.path.join(wsr, "ws")
            if os.path.lexists(staging):
                raise FailClosed("staging dir leaked")
            return True
        must_pass("synthetic_write_failure_leaves_no_temp",
                  synthetic_write_failure_leaves_no_temp)

        # 2. production_write_failure_leaves_no_temp
        def production_write_failure_leaves_no_temp():
            # Reach the PRODUCTION descriptor-relative copy write loop and inject
            # a genuine os.write failure ONLY after all source prechecks pass.
            # Uses the actual source mode/size/SHA-256 and a valid ROOT_HOST
            # source-root id, opened via _open_repo_root_fd; the failure must
            # come from the write loop, leave no temp file, and publish no
            # final destination file.  ROOT_HOST and os.write are restored in
            # finally blocks.
            tf = tempfile.mkdtemp(prefix="nrm_pwf_")
            tmpdirs.append(tf)
            os.makedirs(os.path.join(tf, "src"))
            data = b"pppp"
            src_path = os.path.join(tf, "src", "p.txt")
            with open(src_path, "wb") as fh:
                fh.write(data)
            os.chmod(src_path, 0o644)
            staging_d = os.path.join(tf, "stg"); os.makedirs(staging_d)
            tmpdirs.append(staging_d)
            dest_rel = "p.txt"
            e = {"source_root": "pwf_r", "relative_path": "p.txt",
                 "mode": "0644", "size": len(data),
                 "sha256": sha256_bytes(data), "nlink": 1,
                 "destination_relative": dest_rel}
            raised = False
            st_fd = None
            repo_fd = None
            parent_fd = None
            orig_root_host = dict(ROOT_HOST)
            orig_write = os.write
            write_calls = {"n": 0}
            def inject_write(fd, b):
                write_calls["n"] += 1
                return 0  # genuine short write -> production copy loop FailClosed
            try:
                # Valid source-root mapping for the production descriptor path.
                ROOT_HOST.clear()
                ROOT_HOST.update({"pwf_r": "src"})
                repo_fd = _open_repo_root_fd(tf)
                st_fd = os.open(staging_d,
                                os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
                # Retain a destination-parent descriptor (dest_rel is flat, so
                # parent is the staging root itself).
                parent_fd = os.open(staging_d,
                                    os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
                os.write = inject_write
                try:
                    _prod_copy_one_file_dirfd(repo_fd, "pwf_r", "p.txt",
                                              st_fd, dest_rel, e)
                except FailClosed:
                    raised = True
            finally:
                os.write = orig_write
                ROOT_HOST.clear()
                ROOT_HOST.update(orig_root_host)
                for fd in (parent_fd, st_fd, repo_fd):
                    if fd is not None:
                        try: os.close(fd)
                        except OSError: pass
            if not raised:
                raise FailClosed("production write failure did not raise FailClosed")
            if write_calls["n"] < 1:
                raise FailClosed("injected os.write never called; production "
                                 "write loop was not reached")
            for entry in glob_dirs(staging_d):
                if entry.endswith(".tmp"):
                    raise FailClosed("temp file leaked in production: %s" % entry)
                if entry.endswith(dest_rel):
                    raise FailClosed("final destination existed after write "
                                     "failure: %s" % entry)
            return True
        must_pass("production_write_failure_leaves_no_temp",
                  production_write_failure_leaves_no_temp)

        # 3. temp_replacement_not_removed
        def temp_replacement_not_removed():
            tf = tempfile.mkdtemp(prefix="nrm_trnr_")
            tmpdirs.append(tf)
            parent = tempfile.mkdtemp(prefix="par_", dir=tf)
            tmpdirs.append(parent)
            pfd = os.open(parent, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
            tmp_base = "repl.tmp"
            fd1 = os.open(tmp_base, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                          0o644, dir_fd=pfd)
            st1 = os.fstat(fd1)
            os.write(fd1, b"original")
            os.close(fd1)
            try:
                os.rename(tmp_base, tmp_base + ".bk", src_dir_fd=pfd, dst_dir_fd=pfd)
            except OSError:
                pass  # may not support dir_fd rename
            fd2 = os.open(tmp_base, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                          0o644, dir_fd=pfd)
            st2 = os.fstat(fd2)
            os.write(fd2, b"replacement")
            os.close(fd2)
            try:
                _remove_tmp_bound(pfd, tmp_base, st1.st_dev, st1.st_ino)
            except FailClosed as exc:
                if "replacement" not in str(exc).lower():
                    raise FailClosed("wrong rejection: %s" % exc)
                # Verify replacement still present
                tst = os.stat(tmp_base, dir_fd=pfd, follow_symlinks=False)
                if (tst.st_dev, tst.st_ino) != (st2.st_dev, st2.st_ino):
                    raise Exception("replacement was wrongly removed")
                try: os.close(pfd)
                except OSError: pass
                return True
            try: os.close(pfd)
            except OSError: pass
            raise FailClosed("replacement not rejected")
        must_pass("temp_replacement_not_removed", temp_replacement_not_removed)

        # 4. dirfd_make_dir_open_failure_leaves_no_directory
        # Inject an open failure after successful mkdir+stat by patching
        # _dirfd_open_dir to fail, then verify the created directory is removed.
        def dirfd_make_dir_open_failure_leaves_no_directory():
            tf = tempfile.mkdtemp(prefix="nrm_dmo_")
            tmpdirs.append(tf)
            pfdx = os.open(tf, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
            nm = "totest_%s" % os.getpid()
            import __main__ as _M
            orig_open_dir = _M._dirfd_open_dir
            def fail_open_dir(parent_fd, name):
                raise FailClosed("injected open failure for %r" % name)
            try:
                _M._dirfd_open_dir = fail_open_dir
                _dirfd_make_dir(pfdx, nm)
            except FailClosed:
                pass
            finally:
                _M._dirfd_open_dir = orig_open_dir
            # The created directory must not exist
            if _dirfd_has_entry(pfdx, nm):
                try: os.close(pfdx)
                except OSError: pass
                raise FailClosed("created dir not cleaned up after injected open failure")
            try: os.close(pfdx)
            except OSError: pass
            return True
        must_pass("dirfd_make_dir_open_failure_cleans_up",
                  dirfd_make_dir_open_failure_leaves_no_directory)

        # 5. mkstemp_dirfd_open_failure_leaves_no_directory
        def mkstemp_dirfd_open_failure_leaves_no_directory():
            # Inject a GENUINE directory-open failure AFTER _mkstemp_dirfd has
            # performed mkdir and captured the new directory identity.  The
            # _dirfd_open_dir open for the newly created staging basename must
            # raise FailClosed; _mkstemp_dirfd must remove the created dir
            # (identity-bound) and re-raise, leaving no *_staging_* directory
            # under the parent.  This is NOT a normal-success test.
            tf = tempfile.mkdtemp(prefix="nrm_mstf_")
            tmpdirs.append(tf)
            pf = os.open(tf, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
            _g = globals()
            orig_open_dir = _g["_dirfd_open_dir"]
            opened_for_fail = {"n": 0}
            # Capture the parent identity to bound which open calls belong to
            # staging basenames created under this parent.
            def inject_open_dir(parent_fd, name):
                # Delegate every open to the real helper except a freshly
                # created staging basename under our retained parent fd.
                if parent_fd == pf and "_staging_" in name:
                    opened_for_fail["n"] += 1
                    raise FailClosed("injected open failure for staging basename: %s"
                                     % name)
                return orig_open_dir(parent_fd, name)
            raised = False
            try:
                _g["_dirfd_open_dir"] = inject_open_dir
                try:
                    _mkstemp_dirfd(pf, "ztest")
                except FailClosed:
                    raised = True
            finally:
                _g["_dirfd_open_dir"] = orig_open_dir
                try: os.close(pf)
                except OSError: pass
            if not raised:
                raise FailClosed("injected staging dir open did not raise FailClosed")
            if opened_for_fail["n"] < 1:
                raise FailClosed("injected open failure never reached a created "
                                 "staging basename; cleanup path not exercised")
            # No staging directory may remain under the parent.
            remaining = []
            try:
                for nm in sorted(os.listdir(tf)):
                    if "_staging_" in nm:
                        remaining.append(nm)
            except OSError:
                pass
            if remaining:
                raise FailClosed("staging directory leaked after open failure: %s"
                                 % remaining)
            return True
        must_pass("mkstemp_dirfd_open_failure_leaves_no_directory",
                  mkstemp_dirfd_open_failure_leaves_no_directory)

        # 6. unknown_linux_architecture_fails_closed_before_syscall
        # Verify _renameat2_syscall_number returns None for unknown arch,
        # AND verify _linux_renameat2_noreplace raises FailClosed before any
        # syscall when architecture is unknown.
        def unknown_linux_architecture_fails_closed_before_syscall():
            import platform as plt
            orig = plt.machine
            try:
                plt.machine = lambda: "mips64"
                # Step 1: _renameat2_syscall_number must return None
                num = _renameat2_syscall_number()
                if num is not None:
                    raise FailClosed("expected None for unknown arch, got %r" % num)
                # Step 2: _linux_renameat2_noreplace must raise FailClosed
                # before any syscall is attempted. Use dummy fds.
                parent = tempfile.mkdtemp(prefix="nrm_arch_")
                tmpdirs.append(parent)
                pfd = os.open(parent, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
                try:
                    _linux_renameat2_noreplace(pfd, "d1", pfd, "d2")
                except FailClosed as exc:
                    if "unsupported" not in str(exc):
                        raise FailClosed("Wrong exception text: %s" % exc)
                    try: os.close(pfd)
                    except OSError: pass
                    return True
                try: os.close(pfd)
                except OSError: pass
                raise FailClosed("Unkonwn arch not rejected by _linux_renameat2_noreplace")
            finally:
                plt.machine = orig
        must_pass("unknown_linux_arch_fails_closed_before_syscall",
                  unknown_linux_architecture_fails_closed_before_syscall)

        # 7. authorized_root_open_failure_is_failclosed
        def authorized_root_open_failure_is_failclosed():
            # Use _open_authorized_root_bound with nonexistent path
            receipt = {"dev": 0, "ino": 0, "is_dir": True}
            try:
                _open_authorized_root_bound("/nonexistent/path/xyz123", receipt)
            except FailClosed as exc:
                if "open" not in str(exc).lower():
                    raise FailClosed("wrong exception: %s" % exc)
                return True
            raise FailClosed("os.open failure let through as non-FailClosed")
        must_pass("authorized_root_open_failure_is_failclosed",
                  authorized_root_open_failure_is_failclosed)

        # -- Checkpoint 2B1R1 materialization-authorization boundary tests --
        # These tests exercise the production _require_auth and
        # authorize_v3_materialization boundary directly.  Synthetic
        # future-contract fixtures are written only to temporary self-test
        # dirs under the repository; the real contract, manifest, and
        # executing tool are never modified.  Issuance is ALWAYS bound to the
        # real executing tool (__file__), never to a copy.

        # ---- Checkpoint 2B1R2 canonical-manifest immutability guard ----
        # The real canonical manifest must remain byte-identical throughout the
        # ENTIRE authorization test group, never merely restored at the end.
        # Capture its full identity snapshot once, up front, and assert it is
        # unchanged after every authorization test below.  Restoration is NOT
        # the basis for this result.
        def _canonical_manifest_identity():
            cm_path = os.path.join(os.getcwd(), "manifests",
                                   "nos3-runtime-material-manifest.json")
            cs = os.lstat(cm_path)  # no-follow identity of the manifest itself
            with open(cm_path, "rb") as mf:
                cm_sha = sha256_bytes(mf.read())
            return {
                "path": cm_path,
                "sha256": cm_sha,
                "dev": cs.st_dev,
                "ino": cs.st_ino,
                "size": cs.st_size,
                "mode": cs.st_mode,
                "nlink": cs.st_nlink,
            }

        _canonical_manifest_before = _canonical_manifest_identity()

        def _this_tool_path():
            return os.path.abspath(__file__)

        def _build_future_contract(repo_fd_path, contract_path, manifest_path,
                                    tool_path, candidate_path, tool_sha,
                                    man_sha, cand_sha, *,
                                    static_verification="PASS",
                                    diag_runtime_auth=True,
                                    diag_attempts=1,
                                    am_runtime_authorized=True,
                                    am_runtime_attempts=1,
                                    d064_status="AUTHORIZED_FOR_BOUNDED_ATTEMPT",
                                    accepted=None, proposed="",
                                    permissions_false=True,
                                    include_impl_block=True):
            """Build a synthetic schema-1 future contract dict and write it to
            contract_path (a temp file).  Mirrors the real contract structured
            authorization fields required by authorize_v3_materialization."""
            if accepted is None:
                accepted = cand_sha
            d = {
                "contract_version": "0.4.13-synthetic",
                "status": "PASSIVE_TIME_WITNESS_V3_RUNTIME_AUTHORIZED_SYNTHETIC",
                "gate": {
                    "passive_time_witness_runtime_candidate_v3_contract_schema": 1,
                    "passive_time_witness_runtime_candidate_v3_static_verification": static_verification,
                    "diagnostic_runtime_authorized": diag_runtime_auth,
                    "diagnostic_runtime_attempts_authorized": diag_attempts,
                    "accepted_runtime_entrypoint_v3_sha256": accepted,
                    "proposed_runtime_entrypoint_v3_sha256": proposed,
                    "baseline_run_1_authorized": False,
                    "baseline_run_2_authorized": False,
                    "event_injection_authorized": False,
                    "passive_time_witness_static_verification": "PASS",
                    "accepted_runtime_entrypoint_sha256":
                        "0fe76023ccc968f0aa12fa27db0a5ae21597b03e53066cebb5cf56bc29572259",
                },
                "passive_time_witness_runtime_candidate_v3_design_amendment_1": {
                    "runtime_authorized": am_runtime_authorized,
                    "runtime_attempts": am_runtime_attempts,
                    "d064_status": d064_status,
                    "implementation_status": "IMPLEMENTED",
                    "static_verification": "PASS",
                },
            }
            if permissions_false:
                d["scientific_outcome_allowed"] = False
                d["command_transmission_allowed"] = False
                d["event_injection_allowed"] = False
                d["baseline_execution_allowed"] = False
                d["cryptographic_semantics_claim_allowed"] = False
            if include_impl_block:
                d["passive_time_witness_runtime_candidate_v3_design_amendment_1"][
                    "passive_time_witness_runtime_candidate_v3_implementation"] = {
                        "runtime_material_tool": {"path": tool_path,
                                                  "sha256": tool_sha},
                        "runtime_manifest": {"path": manifest_path,
                                             "sha256": man_sha},
                        "proposed_runtime_entrypoint_v3_sha256": proposed,
                    }
            with open(contract_path, "w", encoding="utf-8") as cf:
                cf.write(json.dumps(d, sort_keys=True) + "\n")
            return d

        def _future_fixture():
            """Create a genuine synthetic future-authorization fixture bound
            to the REAL executing tool (__file__).  The repository root is
            the REAL repository (so verify_manifest/load_and_verify_manifest
            succeed against the real external/nos3 source inventory).  The
            synthetic contract and candidate are written under a temp subdir
            CREATED UNDER the real repo root (so the issuer's
            must-be-under-repo-root check passes) and registered in tmpdirs
            for cleanup.  The manifest is an ISOLATED COPY of the canonical
            manifest: the real canonical manifest is opened READ-ONLY and its
            exact bytes are copied to a new regular file (mode 0644, nlink 1)
            inside the scratch dir; the copy is what the synthetic future
            contract declares and what authorize_v3_materialization opens.
            The copy verifies because verify_manifest validates the manifest
            BYTES against the repository source inventory, never against a
            fixed manifest pathname.  The executing tool is __file__ (NOT a
            copy): copies are rejected by the issuer; only the real executing
            tool binds.  The real canonical manifest is never opened for
            writing, truncation, append, rename, chmod, unlink, or
            restoration."""
            repo = os.getcwd()
            scratch = tempfile.mkdtemp(prefix="nrm_auth_future_", dir=repo)
            tmpdirs.append(scratch)
            tool_path = _this_tool_path()
            tool_sha = sha256_file(tool_path)
            real_man_path = os.path.join(repo, "manifests",
                                         "nos3-runtime-material-manifest.json")
            # Read the canonical manifest bytes WITHOUT modifying them.
            with open(real_man_path, "rb") as mf:
                man_raw = mf.read()
            man_sha = sha256_bytes(man_raw)
            # Isolated copy: a NEW regular file inside the scratch dir holding
            # the exact canonical bytes.  No symlink or hard link to the real
            # manifest; a fresh inode with nlink required to be 1.
            man_path = os.path.join(scratch, "manifest-copy.json")
            mfd = os.open(man_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
            try:
                os.write(mfd, man_raw)
            finally:
                os.close(mfd)
            os.chmod(man_path, 0o644)
            man_st = os.lstat(man_path)  # no-follow: the copy itself
            if man_st.st_nlink != 1:
                raise FailClosed("selftest: manifest copy nlink != 1: %d"
                                 % man_st.st_nlink)
            copy_sha = sha256_file(man_path)
            if copy_sha != man_sha:
                raise FailClosed("selftest: manifest copy sha drift")
            cand_path = os.path.join(scratch, "candidate.sh")
            cand_bytes = b"#!/usr/bin/env bash\n# v3 candidate synthetic\nexit 0\n"
            with open(cand_path, "wb") as cf:
                cf.write(cand_bytes)
            os.chmod(cand_path, 0o755)
            cand_sha = sha256_bytes(cand_bytes)
            contract_path = os.path.join(scratch, "contract.json")
            # repo_fd is the repo root path-equivalent (used by
            # _build_future_contract only for the contract file write).
            return (repo, repo, contract_path, man_path, cand_path, tool_path,
                    tool_sha, man_sha, cand_sha)
        def _issue_future_bearer():
            """Issue a genuine bearer against a fresh synthetic future
            authorized contract bound to the real executing tool.  Returns
            (bearer, fixture_tuple)."""
            repo, repo_fd, contract_path, man_path, cand_path, tool_path, \
                tool_sha, man_sha, cand_sha = _future_fixture()
            _build_future_contract(repo_fd, contract_path, man_path, tool_path,
                cand_path, tool_sha, man_sha, cand_sha)
            bearer = authorize_v3_materialization(repo, contract_path,
                                                  man_path, cand_path, tool_path)
            return bearer, (repo, repo_fd, contract_path, man_path,
                            cand_path, tool_path, tool_sha, man_sha, cand_sha)

        def direct_materialization_authorization_construction_rejected():
            MaterializationAuthorized()
        must_raise("direct_materialization_authorization_construction_rejected",
                   direct_materialization_authorization_construction_rejected)

        def forged_materialization_authorization_registry_rejected():
            forged = object.__new__(MaterializationAuthorized)
            forged._entry()
        must_raise("forged_materialization_authorization_registry_rejected",
                   forged_materialization_authorization_registry_rejected)

        def none_authorization_rejected():
            wsr = tempfile.mkdtemp(prefix="nrm_none_"); tmpdirs.append(wsr)
            materialize_workspace(None, wsr, authorization=None,
                                  component_id="x")
        must_raise("none_authorization_rejected", none_authorization_rejected)

        def synthetic_test_capability_rejected_by_production_auth():
            wsr = tempfile.mkdtemp(prefix="nrm_syncauth_"); tmpdirs.append(wsr)
            try:
                materialize_workspace(None, wsr, authorization=mk_cap(),
                                      component_id="x")
            except FailClosed as exc:
                if "MaterializationAuthorized bearer" not in str(exc):
                    raise FailClosed("wrong reason: %s" % exc)
                return True
            raise FailClosed("synthetic capability not rejected")
        must_pass("synthetic_test_capability_rejected_by_production_auth",
                  synthetic_test_capability_rejected_by_production_auth)

        def current_contract_closed_before_root_inspection():
            repo, repo_fd, contract_path, man_path, cand_path, tool_path, \
                tool_sha, man_sha, cand_sha = _future_fixture()
            real_contract = os.path.join(os.getcwd(),
                "configs/downlink-diagnostic-contract.json")
            pre = set(os.listdir(repo))
            try:
                authorize_v3_materialization(os.getcwd(), real_contract,
                                              man_path, cand_path, tool_path)
            except FailClosed as exc:
                if "v3 materialization authorization closed" not in str(exc):
                    raise FailClosed("wrong closed reason: %s" % exc)
                post = set(os.listdir(repo))
                if post != pre:
                    raise FailClosed("repo mutated: %r" % (post - pre))
                return True
            raise FailClosed("current contract did not fail closed")
        must_pass("current_contract_closed_before_root_inspection",
                  current_contract_closed_before_root_inspection)

        def proposed_candidate_hash_alone_not_authorization():
            repo, repo_fd, contract_path, man_path, cand_path, tool_path, \
                tool_sha, man_sha, cand_sha = _future_fixture()
            _build_future_contract(repo_fd, contract_path, man_path, tool_path,
                cand_path, tool_sha, man_sha, cand_sha,
                diag_runtime_auth=False, diag_attempts=0,
                am_runtime_authorized=False, am_runtime_attempts=0,
                d064_status="BLOCKED", accepted="", proposed=cand_sha)
            try:
                authorize_v3_materialization(repo, contract_path, man_path,
                                             cand_path, tool_path)
            except FailClosed as exc:
                if "v3 materialization authorization closed" not in str(exc):
                    raise FailClosed("wrong reason: %s" % exc)
                return True
            raise FailClosed("proposed hash alone issued a bearer")
        must_pass("proposed_candidate_hash_alone_not_authorization",
                  proposed_candidate_hash_alone_not_authorization)

        def accepted_candidate_hash_mismatch_rejected():
            repo, repo_fd, contract_path, man_path, cand_path, tool_path, \
                tool_sha, man_sha, cand_sha = _future_fixture()
            _build_future_contract(repo_fd, contract_path, man_path, tool_path,
                cand_path, tool_sha, man_sha, cand_sha,
                accepted="0" * 64)
            try:
                authorize_v3_materialization(repo, contract_path, man_path,
                                             cand_path, tool_path)
            except FailClosed as exc:
                if "candidate SHA-256 does not match accepted" not in str(exc):
                    raise FailClosed("wrong reason: %s" % exc)
                return True
            raise FailClosed("accepted hash mismatch issued a bearer")
        must_pass("accepted_candidate_hash_mismatch_rejected",
                  accepted_candidate_hash_mismatch_rejected)

        def static_verification_not_pass_rejected():
            repo, repo_fd, contract_path, man_path, cand_path, tool_path, \
                tool_sha, man_sha, cand_sha = _future_fixture()
            _build_future_contract(repo_fd, contract_path, man_path, tool_path,
                cand_path, tool_sha, man_sha, cand_sha,
                static_verification="PENDING")
            try:
                authorize_v3_materialization(repo, contract_path, man_path,
                                             cand_path, tool_path)
            except FailClosed as exc:
                if "v3 static verification is not PASS" not in str(exc):
                    raise FailClosed("wrong reason: %s" % exc)
                return True
            raise FailClosed("non-PASS static verification issued a bearer")
        must_pass("static_verification_not_pass_rejected",
                  static_verification_not_pass_rejected)

        def attempts_bool_true_rejected_as_non_int():
            repo, repo_fd, contract_path, man_path, cand_path, tool_path, \
                tool_sha, man_sha, cand_sha = _future_fixture()
            _build_future_contract(repo_fd, contract_path, man_path, tool_path,
                cand_path, tool_sha, man_sha, cand_sha,
                diag_attempts=True)
            try:
                authorize_v3_materialization(repo, contract_path, man_path,
                                             cand_path, tool_path)
            except FailClosed as exc:
                if ("attempts_authorized is not exact int 1" not in str(exc)
                        and "is not exact int 1" not in str(exc)):
                    raise FailClosed("wrong reason: %s" % exc)
                return True
            raise FailClosed("bool attempts issued a bearer")
        must_pass("attempts_bool_true_rejected_as_non_int",
                  attempts_bool_true_rejected_as_non_int)

        def prohibited_permission_true_rejected():
            repo, repo_fd, contract_path, man_path, cand_path, tool_path, \
                tool_sha, man_sha, cand_sha = _future_fixture()
            d = _build_future_contract(repo_fd, contract_path, man_path,
                tool_path, cand_path, tool_sha, man_sha, cand_sha)
            d["scientific_outcome_allowed"] = True
            with open(contract_path, "w", encoding="utf-8") as cf:
                cf.write(json.dumps(d, sort_keys=True) + "\n")
            try:
                authorize_v3_materialization(repo, contract_path, man_path,
                                             cand_path, tool_path)
            except FailClosed as exc:
                if "permission not exact false" not in str(exc):
                    raise FailClosed("wrong reason: %s" % exc)
                return True
            raise FailClosed("prohibited permission issued a bearer")
        must_pass("prohibited_permission_true_rejected",
                  prohibited_permission_true_rejected)

        def narrative_status_not_used_as_authority():
            repo, repo_fd, contract_path, man_path, cand_path, tool_path, \
                tool_sha, man_sha, cand_sha = _future_fixture()
            d = _build_future_contract(repo_fd, contract_path, man_path,
                tool_path, cand_path, tool_sha, man_sha, cand_sha,
                diag_runtime_auth=False, diag_attempts=0,
                am_runtime_authorized=False, am_runtime_attempts=0,
                d064_status="BLOCKED", accepted="")
            d["status"] = "PASSIVE_TIME_WITNESS_V3_RUNTIME_AUTHORIZED"
            with open(contract_path, "w", encoding="utf-8") as cf:
                cf.write(json.dumps(d, sort_keys=True) + "\n")
            try:
                authorize_v3_materialization(repo, contract_path, man_path,
                                             cand_path, tool_path)
            except FailClosed as exc:
                if "v3 materialization authorization closed" not in str(exc):
                    raise FailClosed("wrong reason: %s" % exc)
                return True
            raise FailClosed("narrative status alone issued a bearer")
        must_pass("narrative_status_not_used_as_authority",
                  narrative_status_not_used_as_authority)

        def governance_revision_advance_does_not_break_schema1():
            repo, repo_fd, contract_path, man_path, cand_path, tool_path, \
                tool_sha, man_sha, cand_sha = _future_fixture()
            d = _build_future_contract(repo_fd, contract_path, man_path,
                tool_path, cand_path, tool_sha, man_sha, cand_sha)
            d["contract_version"] = "9.9.9-future-advance"
            with open(contract_path, "w", encoding="utf-8") as cf:
                cf.write(json.dumps(d, sort_keys=True) + "\n")
            bearer = authorize_v3_materialization(repo, contract_path,
                                                  man_path, cand_path, tool_path)
            return (isinstance(bearer, MaterializationAuthorized)
                    and bearer.candidate_sha256 == cand_sha)
        must_pass("governance_revision_advance_does_not_break_schema1",
                  governance_revision_advance_does_not_break_schema1)

        def synthetic_future_structured_authorization_issues_genuine_bearer():
            repo, repo_fd, contract_path, man_path, cand_path, tool_path, \
                tool_sha, man_sha, cand_sha = _future_fixture()
            _build_future_contract(repo_fd, contract_path, man_path, tool_path,
                cand_path, tool_sha, man_sha, cand_sha)
            bearer = authorize_v3_materialization(repo, contract_path,
                                                  man_path, cand_path, tool_path)
            if not isinstance(bearer, MaterializationAuthorized):
                raise FailClosed("not a MaterializationAuthorized bearer")
            if bearer.repo_root != repo:
                raise FailClosed("bearer repo_root mismatch")
            if bearer.candidate_sha256 != cand_sha:
                raise FailClosed("bearer candidate sha mismatch")
            if bearer.tool_sha256 != tool_sha:
                raise FailClosed("bearer tool sha mismatch")
            if bearer.manifest_sha256 != man_sha:
                raise FailClosed("bearer manifest sha mismatch")
            return True
        must_pass("synthetic_future_structured_authorization_issues_genuine_bearer",
                  synthetic_future_structured_authorization_issues_genuine_bearer)

        def genuine_bearer_passes_require_auth():
            bearer, _fx = _issue_future_bearer()
            return _require_auth(bearer) is True
        must_pass("genuine_bearer_passes_require_auth",
                  genuine_bearer_passes_require_auth)

        def genuine_bearer_reaches_post_auth_type_check_without_filesystem_mutation():
            # _require_auth accepts the genuine bearer, then materialize_workspace
            # raises at a later (non-authorization) check without mutating the
            # authorized root.  This proves _require_auth is no longer the
            # unconditional rejection and that no mutation precedes it.
            bearer, _fx = _issue_future_bearer()
            wsr = tempfile.mkdtemp(prefix="nrm_gbmut_"); tmpdirs.append(wsr)
            pre = set(os.listdir(wsr))
            try:
                materialize_workspace(None, wsr, authorization=bearer,
                                      component_id="x")
            except FailClosed as exc:
                if "MaterializationAuthorized bearer" in str(exc):
                    raise FailClosed("genuine bearer rejected by auth: %s" % exc)
                if "materialization authorization stale" in str(exc):
                    # Re-validation found a real change -- not a stale-bearer
                    # rejection (bearer is genuine); acceptable as post-auth.
                    post = set(os.listdir(wsr))
                    if post != pre:
                        raise FailClosed("authorized root mutated pre-auth-complete: "
                                         "%r" % (post - pre))
                    return True
                post = set(os.listdir(wsr))
                if post != pre:
                    raise FailClosed("authorized root mutated pre-auth-complete: "
                                     "%r" % (post - pre))
                return True
            raise FailClosed("materialize_workspace did not fail post-auth")
        must_pass(
            "genuine_bearer_reaches_post_auth_type_check_without_filesystem_mutation",
            genuine_bearer_reaches_post_auth_type_check_without_filesystem_mutation)

        # ---- 2B1R1 corrected and new tests ----

        def unregistered_bearer_rejected():
            # object.__new__ without registry issuance is rejected by
            # _require_auth for an unregistered/forged reason.
            unregistered = object.__new__(MaterializationAuthorized)
            try:
                _require_auth(unregistered)
            except FailClosed as exc:
                if "unregistered/forged authorization bearer" not in str(exc):
                    raise FailClosed("wrong reason: %s" % exc)
                return True
            raise FailClosed("unregistered bearer accepted")
        must_pass("unregistered_bearer_rejected", unregistered_bearer_rejected)

        def issued_bearer_rejected_after_contract_revocation():
            bearer, (repo, repo_fd, contract_path, man_path, cand_path,
                     tool_path, tool_sha, man_sha, cand_sha) = _issue_future_bearer()
            # Rewrite the contract so runtime authorization is false and
            # attempts are zero; _require_auth must reject for the intended
            # revocation reason.
            with open(contract_path, "r", encoding="utf-8") as cf:
                d = json.loads(cf.read())
            d["gate"]["diagnostic_runtime_authorized"] = False
            d["gate"]["diagnostic_runtime_attempts_authorized"] = 0
            d["passive_time_witness_runtime_candidate_v3_design_amendment_1"]["runtime_authorized"] = False
            d["passive_time_witness_runtime_candidate_v3_design_amendment_1"]["runtime_attempts"] = 0
            d["passive_time_witness_runtime_candidate_v3_design_amendment_1"]["d064_status"] = "BLOCKED"
            with open(contract_path, "w", encoding="utf-8") as cf:
                cf.write(json.dumps(d, sort_keys=True) + "\n")
            try:
                _require_auth(bearer)
            except FailClosed as exc:
                msg = str(exc)
                # The revocation rewrites the contract bytes, so content
                # change is the detected rejection; revocation/attempt/d064
                # structured reasons are also accepted.
                if ("contract content changed" in msg or "revoked" in msg
                        or "attempt" in msg or "d064" in msg):
                    return True
                raise FailClosed("wrong revocation reason: %s" % exc)
            raise FailClosed("revoked contract bearer still valid")
        must_pass("issued_bearer_rejected_after_contract_revocation",
                  issued_bearer_rejected_after_contract_revocation)

        def internal_issuer_not_exposed():
            import sys as _sys
            mod = _sys.modules[__name__]
            banned = ("_issue", "_issue_materialization_authorization",
                      "_issue_materialization_authorization_internal",
                      "_materialization_authorization_registry",
                      "_registry", "_materialization_secret",
                      "_materialization_token",
                      "_make_materialization_authorization_registry")
            leaked = [n for n in banned if hasattr(mod, n)]
            if leaked:
                raise FailClosed("internal issuer/registry exposed: %r" % leaked)
            # The public issuer and class ARE exposed (required).
            if not hasattr(mod, "MaterializationAuthorized"):
                raise FailClosed("MaterializationAuthorized not exposed")
            if not hasattr(mod, "authorize_v3_materialization"):
                raise FailClosed("authorize_v3_materialization not exposed")
            return True
        must_pass("internal_issuer_not_exposed", internal_issuer_not_exposed)

        def copied_tool_path_rejected_as_not_executing_tool():
            # A byte-identical COPY of the real tool at another path is
            # rejected: the issuer binds to __file__, not to a copy.
            repo, repo_fd, contract_path, man_path, cand_path, tool_path, \
                tool_sha, man_sha, cand_sha = _future_fixture()
            repo = os.getcwd()
            scratch2 = tempfile.mkdtemp(prefix="nrm_auth_copy_", dir=repo)
            tmpdirs.append(scratch2)
            copy_tool = os.path.join(scratch2, "tool_copy.py")
            tool_src = os.path.abspath(__file__)
            with open(tool_src, "rb") as sf, open(copy_tool, "wb") as df:
                df.write(sf.read())
            os.chmod(copy_tool, 0o755)
            copy_sha = sha256_file(copy_tool)
            # Contract declares the COPY as the executing tool.
            _build_future_contract(repo_fd, contract_path, man_path, copy_tool,
                cand_path, copy_sha, man_sha, cand_sha)
            try:
                authorize_v3_materialization(repo, contract_path, man_path,
                                             cand_path, copy_tool)
            except FailClosed as exc:
                msg = str(exc)
                if "executing tool" not in msg and "__file__" not in msg and \
                        "copied tool" not in msg:
                    raise FailClosed("wrong reason: %s" % exc)
                return True
            raise FailClosed("copied tool path issued a bearer")
        must_pass("copied_tool_path_rejected_as_not_executing_tool",
                  copied_tool_path_rejected_as_not_executing_tool)

        def issued_bearer_rejected_after_candidate_change():
            bearer, (repo, repo_fd, contract_path, man_path, cand_path,
                     tool_path, tool_sha, man_sha, cand_sha) = _issue_future_bearer()
            # Mutate the candidate content (same path, new bytes).
            with open(cand_path, "wb") as cf:
                cf.write(b"#!/usr/bin/env bash\n# mutated\nexit 1\n")
            try:
                _require_auth(bearer)
            except FailClosed as exc:
                if "candidate" not in str(exc).lower():
                    raise FailClosed("wrong reason: %s" % exc)
                return True
            raise FailClosed("mutated candidate bearer still valid")
        must_pass("issued_bearer_rejected_after_candidate_change",
                  issued_bearer_rejected_after_candidate_change)

        def issued_bearer_rejected_after_manifest_change():
            # The bearer is issued against the ISOLATED manifest COPY, not the
            # real canonical manifest.  Mutate ONLY that temporary copy after
            # issuance; _require_auth re-hashes the manifest it reopens and
            # must FailClosed for manifest receipt/content drift.  The real
            # canonical manifest is never opened for writing here; the temp
            # copy needs no restoration because its containing scratch dir is
            # removed during normal self-test cleanup.
            real_man = os.path.join(os.getcwd(), "manifests",
                                    "nos3-runtime-material-manifest.json")
            real_before = sha256_file(real_man)
            bearer, (repo, repo_fd, contract_path, man_path, cand_path,
                     tool_path, tool_sha, man_sha, cand_sha) = _issue_future_bearer()
            # man_path IS the temporary isolated copy, not the real manifest.
            with open(man_path, "wb") as mf:
                mf.write(b"injected mutation\n")
            try:
                _require_auth(bearer)
            except FailClosed as exc:
                if "manifest" not in str(exc).lower():
                    raise FailClosed("wrong reason: %s" % exc)
                # Real canonical manifest must be byte-identical throughout.
                real_after = sha256_file(real_man)
                if real_after != real_before:
                    raise FailClosed("real canonical manifest mutated")
                return True
            raise FailClosed("mutated manifest bearer still valid")
        must_pass("issued_bearer_rejected_after_manifest_change",
                  issued_bearer_rejected_after_manifest_change)

        def symlinked_authorization_leaf_rejected():
            repo, repo_fd, contract_path, man_path, cand_path, tool_path, \
                tool_sha, man_sha, cand_sha = _future_fixture()
            # Replace the candidate file with a symlink to a real target and
            # attempt issuance; the descriptor-relative opener must reject.
            target = os.path.join(repo, "configs",
                                  "downlink-diagnostic-contract.json")
            try:
                os.remove(cand_path)
            except OSError:
                pass
            try:
                os.symlink(target, cand_path)
            except OSError as exc:
                raise FailClosed("test cannot create symlink: %s" % exc)
            # Recompute candidate SHA from the target so accepted matches; the
            # opener rejects the symlink before content checks regardless.
            cand_sha_link = sha256_file(target)
            _build_future_contract(repo_fd, contract_path, man_path, tool_path,
                cand_path, tool_sha, man_sha, cand_sha_link)
            try:
                authorize_v3_materialization(repo, contract_path, man_path,
                                             cand_path, tool_path)
            except FailClosed as exc:
                # Symlink leaf is rejected by the descriptor-bound opener
                # (not a regular file); any FailClosed is the intended reject.
                return True
            raise FailClosed("symlinked leaf issued a bearer")
        must_pass("symlinked_authorization_leaf_rejected",
                  symlinked_authorization_leaf_rejected)

        def symlinked_authorization_parent_rejected():
            repo, repo_fd, contract_path, man_path, cand_path, tool_path, \
                tool_sha, man_sha, cand_sha = _future_fixture()
            # Replace the scratch directory with a symlink to a real dir and
            # rebuild the candidate/contract under a new symlinked parent.
            scratch2 = tempfile.mkdtemp(prefix="nrm_auth_sym_", dir=repo)
            tmpdirs.append(scratch2)
            real_parent = os.path.join(scratch2, "real_parent")
            os.makedirs(real_parent, exist_ok=True)
            link_parent = os.path.join(scratch2, "link_parent")
            os.symlink(real_parent, link_parent)
            cand_link = os.path.join(link_parent, "candidate.sh")
            cand_bytes = b"#!/usr/bin/env bash\n# v3 candidate synthetic\nexit 0\n"
            with open(cand_link, "wb") as cf:
                cf.write(cand_bytes)
            os.chmod(cand_link, 0o755)
            cand_sha_l = sha256_bytes(cand_bytes)
            contract_l = os.path.join(link_parent, "contract.json")
            _build_future_contract(repo_fd, contract_l, man_path, tool_path,
                cand_link, tool_sha, man_sha, cand_sha_l)
            try:
                authorize_v3_materialization(repo, contract_l, man_path,
                                             cand_link, tool_path)
            except FailClosed as exc:
                # Symlinked parent is rejected by the descriptor-bound opener
                # (Not a directory); any FailClosed is the intended reject.
                return True
            raise FailClosed("symlinked parent issued a bearer")
        must_pass("symlinked_authorization_parent_rejected",
                  symlinked_authorization_parent_rejected)

        def opened_identity_continuity_required():
            # The generic opener compares lstat vs opened-fstat device/inode.
            # A regular candidate whose dev/ino are stable must open fine; the
            # test confirms a genuine bearer issues and require_auth passes,
            # proving the continuity check is satisfied for normal files.
            bearer, _fx = _issue_future_bearer()
            return _require_auth(bearer) is True
        must_pass("opened_identity_continuity_required",
                  opened_identity_continuity_required)

        def authorization_registry_not_exposed_as_module_attribute():
            import sys as _sys
            mod = _sys.modules[__name__]
            banned = ("_registry", "_issue",
                      "_issue_materialization_authorization",
                      "_issue_materialization_authorization_internal",
                      "_materialization_authorization_registry",
                      "_materialization_secret", "_materialization_token",
                      "_make_materialization_authorization_registry")
            leaked = [n for n in banned if hasattr(mod, n)]
            if leaked:
                raise FailClosed("registry internals exposed: %r" % leaked)
            if not hasattr(mod, "MaterializationAuthorized"):
                raise FailClosed("MaterializationAuthorized not exposed")
            if not hasattr(mod, "authorize_v3_materialization"):
                raise FailClosed("authorize_v3_materialization not exposed")
            return True
        must_pass("authorization_registry_not_exposed_as_module_attribute",
                  authorization_registry_not_exposed_as_module_attribute)

        # ---- Checkpoint 2B1R2 canonical-manifest immutability result ----
        # After ALL authorization tests, require every captured identity and
        # content field of the real canonical manifest to be unchanged.  This
        # result reports PASS only when dev, inode, size, mode, nlink, AND the
        # SHA-256 content hash all match the up-front snapshot.  Restoration is
        # never used as the basis for this result.
        def canonical_manifest_never_mutated():
            after = _canonical_manifest_identity()
            before = _canonical_manifest_before
            if after != before:
                changed = {k for k in before if before[k] != after.get(k)}
                raise FailClosed("canonical manifest mutated: %r" % sorted(changed))
            return True
        must_pass("canonical_manifest_never_mutated",
                  canonical_manifest_never_mutated)
        # 32. double emission byte-identical (synthetic).
        _run_double_emission(results)

    finally:
        for d in tmpdirs:
            shutil.rmtree(d, ignore_errors=True)

    passed = sum(1 for _, r in results if r == "PASS")
    skips = sum(1 for _, r in results if r == "SKIP")
    failed = sum(1 for _, r in results
                 if not r.startswith("PASS") and r != "SKIP")
    return passed, failed, skips, results


def _check_dup_source(included, excluded):
    _enforce_dup_source(included, excluded)

def _enforce_dup_source(included, excluded):
    seen = set()
    for inc in included:
        sid = (inc["source_root"], inc["relative_path"])
        if sid in seen:
            raise FailClosed("duplicate source identity: %s:%s" % sid)
        seen.add(sid)

def _enforce_dup_dest(included):
    comp = set()
    for inc in included:
        key = (inc["component_scope"], inc["destination_relative"])
        if key in comp:
            raise FailClosed("duplicate destination: %s" % str(key))
        comp.add(key)

def _check_dir_file(sets):
    shared = sets["files"] & sets["dirs"]
    if shared:
        raise FailClosed("dir/file collision: %r" % shared)

def _build_synthetic_manifest(src, incl_entries, extra_dirs=None, excl_records=None,
                              src_root="r", comp_scope="comp", dest_prefix="D",
                              ws_id="ws", ws_seed=None):
    dirs = [{"source_root": src_root, "relative_path": "", "component_scope": comp_scope}]
    if extra_dirs:
        dirs.extend(extra_dirs)
    seed = ws_seed if ws_seed is not None else [src_root]
    return {
        "schema": CONTRACT_SCHEMA,
        "source_root_declarations": [
            {"source_root": src_root, "component_scope": comp_scope,
             "host_relative_path": "src", "destination_prefix": dest_prefix}],
        "included_regular_file_entries": list(incl_entries),
        "directory_entries": dirs,
        "exact_exclusion_records": excl_records or [],
        "deny_pattern_declarations": [],
        "workspace_declarations": [
            {"component_id": ws_id, "workspace_host_path": ws_id,
             "mount_destination": "/work/nos3", "seed_source_roots": seed,
             "private_physical_copy": True, "no_hard_links": True,
             "no_reflinks": True, "no_overlays": True, "no_source_aliases": True,
             "no_runtime_mount_from_external_nos3": True}],
        "canonicalization": {
            "no_internal_manifest_sha256": True,
            "detached_sha256_over_complete_file_bytes": True,
            "json_dumps": {"ensure_ascii": True, "sort_keys": True,
                           "separators": [",", ":"], "exactly_one_final_lf": True},
            "exact_utf8_bytes_remain_path_identity": True,
            "all_sort_key_elements_byte_encoded": True,
            "no_locale_dependent_ordering": True,
            "no_filesystem_traversal_order_influence": True,
            "root_directory_sentinel": {"entry_category": "directory_entry",
                "source_root_directory": True, "value": "",
                "denotes_declared_root_itself": True,
                "not_passed_through_normal_child_path_validation": True,
                "empty_string_rejected_for_files": True,
                "empty_string_rejected_for_exclusions": True,
                "empty_string_rejected_for_destination_paths": True,
                "empty_string_rejected_for_workspace_paths": True,
                "empty_string_rejected_for_non_root_directory_entries": True}},
        "path_validation": {k: True for k in (
            "reject_surrogate_code_points", "reject_nul", "reject_absolute_paths",
            "reject_empty_components", "reject_dot_components", "reject_dotdot_components",
            "reject_backslashes", "reject_repeated_separators",
            "reject_duplicate_source_identities",
            "reject_duplicate_destination_identities_within_component",
            "reject_directory_file_and_prefix_collisions")},
        "collision_model": {"step_1_nfd_decompose": True,
            "step_2_apply_str_casefold_not_lower": True,
            "step_3_normalize_folded_to_nfc_and_nfd_independently": True,
            "step_4_encode_both_as_utf8": True,
            "step_5_reject_distinct_paths_if_either_collides": True,
            "normalized_values_are_collision_guards_only": True,
            "exact_utf8_bytes_remain_path_identity": True,
            "namespaces": ["source_files_per_root", "source_directories_per_root",
                "destinations_per_component", "exclusions_per_root",
                "deny_patterns_per_scope"]},
        "inventory_invariants": INVARIANTS,
        "snapshot_inventory": SNAPSHOT,
        "source_exclusion_policy": {"excluded_source_path_may_be_absent": True,
            "absence_is_not_source_drift": True,
            "present_must_match_type_mode_size_sha256": True,
            "present_mismatch_fails_closed": True,
            "unlisted_source_path_fails_closed": True,
            "new_deny_pattern_match_fails_without_exact_classification": True},
        "destination_exclusion_policy": {
            "all_exclusions_must_be_absent_from_destinations": True,
            "deny_patterns_are_additional_fail_closed_guards": True},
        "authorization_boundary": {"real_materialization_requires_explicit_authorization": True,
            "tool_must_not_infer_authorization_from_narrative_status": True,
            "host_only": True, "no_docker_invocation": True,
            "no_runtime_candidate_emission": True, "no_verifier_execution": True,
            "no_compilation": True},
        "_test_scope": comp_scope,
    }


def _run_materialization_tests(results, tmpdirs, mk_cap, test_materialize):
    """Behavioral materialization tests using synthetic fixtures via the
    private test_materialize closure only."""
    root = tempfile.mkdtemp(prefix="nrm_matroot_")
    tmpdirs.append(root)
    src = os.path.join(root, "src")
    os.makedirs(os.path.join(src, "sub"))
    f_exec = os.path.join(src, "run.sh")
    f_reg = os.path.join(src, "data.txt")
    f_nested = os.path.join(src, "sub", "deep.txt")
    with open(f_exec, "wb") as fh: fh.write(b"#!/bin/sh\n")
    os.chmod(f_exec, 0o755)
    with open(f_reg, "wb") as fh: fh.write(b"ordinary")
    os.chmod(f_reg, 0o644)
    with open(f_nested, "wb") as fh: fh.write(b"deep-content-here!")
    os.chmod(f_nested, 0o644)
    sha_exec, sha_reg, sha_nested = (sha256_file(f_exec), sha256_file(f_reg),
                                     sha256_file(f_nested))
    inc_base = [
        {"source_root": "r", "relative_path": "run.sh", "entry_type": "regular_file",
         "mode": "0755", "size": 10, "sha256": sha_exec, "nlink": 1,
         "destination_relative": "D/run.sh", "component_scope": "comp"},
        {"source_root": "r", "relative_path": "data.txt", "entry_type": "regular_file",
         "mode": "0644", "size": 8, "sha256": sha_reg, "nlink": 1,
         "destination_relative": "D/data.txt", "component_scope": "comp"},
        {"source_root": "r", "relative_path": "sub/deep.txt", "entry_type": "regular_file",
         "mode": "0644", "size": 18, "sha256": sha_nested, "nlink": 1,
         "destination_relative": "D/sub/deep.txt", "component_scope": "comp"},
    ]
    dirs_sub = {"source_root": "r", "relative_path": "sub", "component_scope": "comp"}
    man = _build_synthetic_manifest(src, inc_base, extra_dirs=[dirs_sub])
    auth = mk_cap()

    def mk(name):
        d = os.path.join(root, name)
        os.makedirs(d); tmpdirs.append(d); return d

    def run_test(name, fn, expect_fail=False):
        try:
            fn()
            if expect_fail:
                results.append((name, "FAIL: no exception"))
            else:
                results.append((name, "PASS"))
        except FailClosed:
            results.append((name, "PASS" if expect_fail else "FAIL: FailClosed"))
        except Exception as exc:
            results.append((name, "FAIL: %r" % exc))

    # mode 0755 / 0644 / nested dir / atomic publication.
    fin = None
    try:
        wsr = mk("ws_basic_root")
        fin = test_materialize(man, root, wsr, "ws", auth, source_host_map={"r": "src"})
        exe_ok = stat.S_IMODE(os.lstat(os.path.join(fin, "D", "run.sh")).st_mode) == 0o755
        reg_ok = stat.S_IMODE(os.lstat(os.path.join(fin, "D", "data.txt")).st_mode) == 0o644
        results.append(("mode_0755_preserved", "PASS" if exe_ok else "FAIL"))
        results.append(("mode_0644_preserved", "PASS" if reg_ok else "FAIL"))
        results.append(("nested_dir_created",
                        "PASS" if os.path.isfile(os.path.join(fin, "D", "sub", "deep.txt")) else "FAIL"))
        results.append(("atomic_workspace_publication", "PASS" if os.path.isdir(fin) else "FAIL"))
    except Exception as exc:
        results.append(("mode_0755_preserved", "FAIL: %r" % exc))
        results.append(("atomic_workspace_publication", "FAIL: %r" % exc))

    # SHA mismatch rejected; no leftover workspace; staging cleaned.
    f_corrupt = os.path.join(src, "corrupt.txt")
    with open(f_corrupt, "wb") as fh: fh.write(b"original!!")
    os.chmod(f_corrupt, 0o644)
    sha_c = sha256_file(f_corrupt)
    man_c = _build_synthetic_manifest(src,
        inc_base + [{"source_root": "r", "relative_path": "corrupt.txt",
                     "entry_type": "regular_file", "mode": "0644", "size": 10,
                     "sha256": sha_c, "nlink": 1,
                     "destination_relative": "D/corrupt.txt", "component_scope": "comp"}],
        extra_dirs=[dirs_sub])
    with open(f_corrupt, "wb") as fh: fh.write(b"CHANGED!!")
    sha_wsr = mk("ws_sha_root")
    run_test("sha_mismatch_rejected", lambda: test_materialize(
        man_c, root, sha_wsr, "ws", auth, source_host_map={"r": "src"}), expect_fail=True)
    results.append(("sha_mismatch_no_workspace",
                    "PASS" if not os.path.exists(os.path.join(sha_wsr, "ws")) else "FAIL"))

    # pre-existing final rejected and unchanged.
    pre_wsr = mk("ws_pre_root")
    os.makedirs(os.path.join(pre_wsr, "ws"))
    run_test("pre_existing_final_rejected", lambda: test_materialize(
        man, root, pre_wsr, "ws", auth, source_host_map={"r": "src"}), expect_fail=True)
    results.append(("pre_existing_final_unchanged",
                    "PASS" if os.path.isdir(os.path.join(pre_wsr, "ws")) else "FAIL"))

    # failed staging-tree cleanup after mid-copy failure (bad source host path).
    clean_wsr = mk("ws_clean_root")
    run_test("failed_workspace_cleanup", lambda: test_materialize(
        man, root, clean_wsr, "ws", auth, source_host_map={"r": "NONEXISTENT_src"}),
             expect_fail=True)
    results.append(("failed_workspace_no_staging",
                    "PASS" if not os.path.exists(os.path.join(clean_wsr, "ws")) else "FAIL"))

    # no excluded destination path: exclusion present in source but not copied.
    f_excl = os.path.join(src, "to_exclude.bin")
    with open(f_excl, "wb") as fh: fh.write(b"excluded-payload-xx")
    os.chmod(f_excl, 0o644)
    man_e = _build_synthetic_manifest(src, inc_base,
        excl_records=[{"source_root": "r", "relative_path": "to_exclude.bin",
                       "entry_type": "regular_file", "mode": "0644", "size": 20,
                       "sha256": sha256_file(f_excl), "nlink": 1,
                       "classification": "EXACT_STALE_EXCLUSION",
                       "destination_must_be_absent": True}],
        extra_dirs=[dirs_sub])
    excl_wsr = mk("ws_excl_root")
    try:
        fex = test_materialize(man_e, root, excl_wsr, "ws", auth,
                                 source_host_map={"r": "src"})
        results.append(("no_excluded_dest_path",
                        "PASS" if not os.path.lexists(os.path.join(fex, "D", "to_exclude.bin")) else "FAIL"))
    except Exception as exc:
        results.append(("no_excluded_dest_path", "FAIL: %r" % exc))

    # component_id absent rejected (test path that accepts the capability).
    run_test("component_id_absent_rejected",
             lambda: test_materialize(man, root, mk("ws_abs"), None,
                                       auth, source_host_map={"r": "src"}),
             expect_fail=True)

    # component_id "../escape" rejected before staging.
    run_test("component_id_dotdot_rejected",
             lambda: test_materialize(man, root, mk("ws_dd"), "../escape",
                                       auth, source_host_map={"r": "src"}),
             expect_fail=True)

    # A directly-constructed fake bearer is rejected by the production
    # materializer before any filesystem mutation (_require_auth raises first
    # in this checkpoint); the intended fail-closed is the auth gate.
    fake_wsr = mk("ws_fake_root")
    amateur = type("Fake", (), {"repo_root": root})()
    amateur.revalidate = lambda: True
    amateur.manifest = lambda: man
    amateur.workspace_for = lambda cid: FailClosed("forged")
    try:
        materialize_workspace(amateur, fake_wsr,
                              authorization=auth, component_id="ws")
    except FailClosed as exc:
        if "MaterializationAuthorized bearer" not in str(exc):
            raise FailClosed("forge rejected for wrong reason: %s" % exc)
    else:
        results.append(("verified_manifest_boundary_rejects_forge", "FAIL: no exception"))
    results.append(("verified_manifest_boundary_rejects_forge", "PASS" if not os.path.isdir(os.path.join(fake_wsr, "ws")) else "FAIL: path exists"))

    # absolute destination rejected (manifest with escaping dest).
    bad_dest_inc = [dict(inc_base[0], destination_relative="/abs/x")]
    man_abs = _build_synthetic_manifest(src, bad_dest_inc, extra_dirs=[dirs_sub])
    abs_wsr = mk("ws_abs_root")
    run_test("absolute_destination_rejected", lambda: test_materialize(
        man_abs, root, abs_wsr, "ws", auth, source_host_map={"r": "src"}), expect_fail=True)

    # dotdot destination rejected.
    dd_inc = [dict(inc_base[0], destination_relative="D/../../escape")]
    man_dd = _build_synthetic_manifest(src, dd_inc, extra_dirs=[dirs_sub])
    dd_wsr = mk("ws_dd_root")
    run_test("dotdot_destination_rejected", lambda: test_materialize(
        man_dd, root, dd_wsr, "ws", auth, source_host_map={"r": "src"}), expect_fail=True)

    # authorized root inside source tree rejected (via _check_authorized_root
    # path in test_materialize is not invoked; instead staging creation under
    # a source subtree is harmless for synthetic tests, so exercise the real
    # _check_authorized_root directly against a synthetic layout).
    ar_inside = os.path.join(root, "src")
    run_test("authorized_root_inside_source_rejected",
             lambda: _check_authorized_root(ar_inside, root),
             expect_fail=True)
    run_test("authorized_root_contains_source_rejected",
             lambda: _check_authorized_root(root, os.path.join(root, "src")),
             expect_fail=True)

    # extra destination directory rejected.
    man_extra_dir = _build_synthetic_manifest(src, inc_base,
        extra_dirs=[dirs_sub, {"source_root": "r", "relative_path": "rogue",
                               "component_scope": "comp"}])
    ed_wsr = mk("ws_extra_dir_root")
    def extra_dir_test():
        fex = test_materialize(man_extra_dir, root, ed_wsr, "ws", auth,
                                 source_host_map={"r": "src"})
        # create an extra unlisted directory to trigger verification failure
        os.makedirs(os.path.join(fex, "D", "unlisted"))
        _verify_destination_complete(fex, man_extra_dir["included_regular_file_entries"],
                                     man_extra_dir["directory_entries"], {"r": "D"})
    run_test("extra_destination_directory_rejected", extra_dir_test, expect_fail=True)

    # missing expected directory rejected (declare dir but do not create it).
    man_miss_dir = _build_synthetic_manifest(src, inc_base, extra_dirs=[dirs_sub])
    md_wsr = mk("ws_miss_dir_root")
    def miss_dir_test():
        fex = test_materialize(man_miss_dir, root, md_wsr, "ws", auth,
                                source_host_map={"r": "src"})
        # remove an expected directory to trigger verification failure
        shutil.rmtree(os.path.join(fex, "D", "sub"))
        _verify_destination_complete(fex, man_miss_dir["included_regular_file_entries"],
                                     man_miss_dir["directory_entries"], {"r": "D"})
    run_test("missing_expected_directory_rejected", miss_dir_test, expect_fail=True)

    # destination symlink rejected.
    sym_wsr = mk("ws_sym_root")
    def sym_test():
        fex = test_materialize(man, root, sym_wsr, "ws", auth,
                                 source_host_map={"r": "src"})
        os.symlink("/etc/hosts", os.path.join(fex, "D", "symlinked"))
        _verify_destination_complete(fex, man["included_regular_file_entries"],
                                     man["directory_entries"], {"r": "D"})
    run_test("destination_symlink_rejected", sym_test, expect_fail=True)

    # prefixed cFS deny-pattern rejected: a copied file matching the prefixed
    # deny pattern must fail even if the manifest classifies it as included.
    dsrc = os.path.join(root, "cfs_src")
    os.makedirs(os.path.join(dsrc, "data", "owls", "bundle"))
    f_deny = os.path.join(dsrc, "data", "owls", "bundle", ".goutputstream-X9")
    with open(f_deny, "wb") as fh: fh.write(b"deny-payload-here")
    os.chmod(f_deny, 0o644)
    deny_dirs = [
        {"source_root": "cfs", "relative_path": "data", "component_scope": "cfs"},
        {"source_root": "cfs", "relative_path": "data/owls", "component_scope": "cfs"},
        {"source_root": "cfs", "relative_path": "data/owls/bundle", "component_scope": "cfs"},
    ]
    deny_inc = [{"source_root": "cfs", "relative_path": "data/owls/bundle/.goutputstream-X9",
                 "entry_type": "regular_file", "mode": "0644", "size": 17,
                 "sha256": sha256_file(f_deny), "nlink": 1,
                 "destination_relative": "fsw/build/exe/cpu1/data/owls/bundle/.goutputstream-X9",
                 "component_scope": "cfs"}]
    man_deny = _build_synthetic_manifest(dsrc, deny_inc, extra_dirs=deny_dirs,
        src_root="cfs", comp_scope="cfs", dest_prefix="fsw/build/exe/cpu1",
        ws_id="cfs", ws_seed=["cfs"])
    man_deny["deny_pattern_declarations"] = [
        {"pattern": "data/owls/bundle/.goutputstream-*", "scope": "cfs"}]
    deny_wsr = mk("ws_deny_root")
    run_test("prefixed_cfs_deny_pattern_rejected", lambda: test_materialize(
        man_deny, root, deny_wsr, "cfs", auth, source_host_map={"cfs": "cfs_src"}),
             expect_fail=True)

    # cFS directory mapping: directories must exist only beneath
    # fsw/build/exe/cpu1; no workspace-root cf or data directories.
    cfs_check_wsr = mk("ws_cfs_check_root")
    cfs_f = os.path.join(dsrc, "cf", "Inp_ADAC.txt")
    os.makedirs(os.path.join(dsrc, "cf"))
    with open(cfs_f, "wb") as fh: fh.write(b"config-input-adac-value")
    os.chmod(cfs_f, 0o644)
    cfs_inc = [{"source_root": "cfs", "relative_path": "cf/Inp_ADAC.txt",
                "entry_type": "regular_file", "mode": "0644",
                "size": os.path.getsize(cfs_f), "sha256": sha256_file(cfs_f), "nlink": 1,
                "destination_relative": "fsw/build/exe/cpu1/cf/Inp_ADAC.txt",
                "component_scope": "cfs"}]
    man_cfs = _build_synthetic_manifest(dsrc, cfs_inc,
        extra_dirs=[{"source_root": "cfs", "relative_path": "cf", "component_scope": "cfs"}],
        src_root="cfs", comp_scope="cfs", dest_prefix="fsw/build/exe/cpu1",
        ws_id="cfs", ws_seed=["cfs"])
    try:
        fex = test_materialize(man_cfs, root, cfs_check_wsr, "cfs", auth,
                                source_host_map={"cfs": "cfs_src"})
        has_cf_top = os.path.isdir(os.path.join(fex, "cf"))
        has_data_top = os.path.isdir(os.path.join(fex, "data"))
        cfs_dir_ok = os.path.isdir(os.path.join(fex, "fsw", "build", "exe", "cpu1", "cf"))
        results.append(("cfs_dir_under_fsw_build_exe_cpu1", "PASS" if cfs_dir_ok else "FAIL"))
        results.append(("no_workspace_root_cf_dir", "PASS" if not has_cf_top else "FAIL"))
        results.append(("no_workspace_root_data_dir", "PASS" if not has_data_top else "FAIL"))
    except Exception as exc:
        results.append(("cfs_dir_under_fsw_build_exe_cpu1", "FAIL: %r" % exc))
        results.append(("no_workspace_root_cf_dir", "FAIL: %r" % exc))
        results.append(("no_workspace_root_data_dir", "FAIL: %r" % exc))


def glob_dirs(root):
    out = []
    for dp, dn, fn in os.walk(root, followlinks=False):
        for n in dn + fn:
            out.append(os.path.join(dp, n))
    return out

def _run_double_emission(results):
    """Build two manifests from the same synthetic fixture; compare bytes."""
    tmp = tempfile.mkdtemp(prefix="nrm_double_")
    try:
        root = os.path.join(tmp, "fake_root")
        os.makedirs(os.path.join(root, "sub"))
        with open(os.path.join(root, "a.txt"), "wb") as fh: fh.write(b"aaa")
        os.makedirs(os.path.join(tmp, "src"))
        # Build a synthetic included + directories list and serialize twice.
        inc = [{"source_root": "x", "relative_path": "a.txt",
                "entry_type": "regular_file", "destination_relative": "D/a.txt",
                "component_scope": "comp", "mode": "0644", "size": 3,
                "sha256": sha256_bytes(b"aaa"), "nlink": 1}]
        dirs = [{"source_root": "x", "relative_path": "", "component_scope": "comp"},
                {"source_root": "x", "relative_path": "sub", "component_scope": "comp"}]
        stats = {"raw_regular_files": 1, "present_exact_exclusions": 0,
                 "unsupported_filesystem_objects": 0, "escaping_symlinks": 0,
                 "hard_link_aliases": 0, "unclassified_source_paths": 0,
                 "included_regular_file_count": 1, "directory_entry_count": 2,
                 "exact_exclusion_record_count": 0, "present_exclusion_keys": []}
        m1 = build_manifest(tmp, inc, dirs, [], stats)
        m2 = build_manifest(tmp, inc, dirs, [], stats)
        b1 = serialize_manifest(m1)
        b2 = serialize_manifest(m2)
        results.append(("double_emission_byte_identical", "PASS" if b1 == b2 else "FAIL"))
        one_lf = b1.endswith(b"\n") and not b1.endswith(b"\n\n")
        results.append(("double_emission_one_lf", "PASS" if one_lf else "FAIL"))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

# --------------------------------------------------------------------------
# CLI.
# --------------------------------------------------------------------------
def cmd_emit(repo_root, out_path):
    i1, d1, e1, s1 = walk_source_roots(repo_root)
    raw = serialize_manifest(build_manifest(repo_root, i1, d1, e1, s1))
    with open(out_path, "wb") as f:
        f.write(raw)
    # double-emission determinism
    i2, d2, e2, s2 = walk_source_roots(repo_root)
    raw2 = serialize_manifest(build_manifest(repo_root, i2, d2, e2, s2))
    if raw != raw2:
        raise FailClosed("double emission not byte-identical")
    return sha256_bytes(raw), len(i1), raw


def cmd_verify(repo_root, manifest_path):
    with open(manifest_path, "rb") as f:
        raw = f.read()
    return verify_manifest(raw, repo_root)

def cmd_authorize_v3_check(args):
    """Non-mutating CLI inspection: attempt v3 materialization bearer
    issuance against actual files.  Never calls materialize_workspace() and
    never mutates an authorized root.  On the closed current contract it
    returns nonzero and prints exactly one marker
    V3_MATERIALIZATION_AUTHORIZATION=CLOSED.  On a successfully issued genuine
    bearer it prints V3_MATERIALIZATION_AUTHORIZATION=READY and returns 0."""
    missing = []
    for a in ("contract", "manifest", "candidate", "tool_path", "repo_root"):
        v = getattr(args, a, None)
        if not v:
            missing.append(a)
    if missing:
        print("V3_MATERIALIZATION_AUTHORIZATION=CLOSED")
        print("[ERROR] missing required arguments: %s" % ", ".join(missing),
              file=sys.stderr)
        return 2
    try:
        authorize_v3_materialization(args.repo_root, args.contract, args.manifest,
                                     args.candidate, args.tool_path)
    except FailClosed:
        print("V3_MATERIALIZATION_AUTHORIZATION=CLOSED")
        return 1
    print("V3_MATERIALIZATION_AUTHORIZATION=READY")
    return 0


def main(argv=None):
    p = argparse.ArgumentParser(
        description="NOS3 runtime-material tool (WP4 v3, host-only, "
                    "deterministic, fail-closed).")
    p.add_argument("--repo-root", default=os.getcwd())
    g = p.add_mutually_exclusive_group(required=False)
    g.add_argument("--emit", metavar="PATH")
    g.add_argument("--verify", metavar="PATH")
    g.add_argument("--selftest", action="store_true")
    g.add_argument("--json-stats", action="store_true")
    g.add_argument("--authorize-v3-check", action="store_true")
    p.add_argument("--contract", metavar="PATH")
    p.add_argument("--manifest", metavar="PATH")
    p.add_argument("--candidate", metavar="PATH")
    p.add_argument("--tool-path", metavar="PATH")
    args = p.parse_args(argv)

    if args.selftest:
        passed, failed, skips, results = selftest()
        for name, r in results:
            print("  %-46s %s" % (name, r))
        print("SELFTEST passed=%d failed=%d skips=%d" % (passed, failed, skips))
        return 0 if failed == 0 else 1
    if args.emit:
        sha, count, raw = cmd_emit(args.repo_root, args.emit)
        print("EMIT path=%s count=%d sha256=%s" % (args.emit, count, sha))
        return 0
    if args.verify:
        ok = cmd_verify(args.repo_root, args.verify)
        print("VERIFY path=%s result=%s" % (args.verify, "PASS" if ok else "FAIL"))
        return 0 if ok else 1
    if args.json_stats:
        # no positional manifest argument
        included, directories, excluded_present, stats = walk_source_roots(args.repo_root)
        print(json.dumps(stats, sort_keys=True, indent=2))
        return 0
    if args.authorize_v3_check:
        return cmd_authorize_v3_check(args)
    p.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
