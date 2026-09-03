#!/usr/bin/env python3
"""Run repository release gates against Git-tracked working-tree content only.

The core release-gate audit intentionally traverses its repository root. Developer
clones can also contain ignored virtual environments, cached dependency data, and
historical local runtime artifacts that are not part of the repository. Those files
must not influence a publication/release decision.

This wrapper creates a detached temporary worktree at HEAD, overlays the caller's
Git-tracked working-tree state (including tracked modifications, staged additions,
and tracked deletions), runs the historical/canonical core audit, and then runs the
current Study-8 publication-state overlay. Untracked and ignored files are excluded by
construction. No scientific runtime is started and no tracked repository file is
modified.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORE_REL = Path("scripts/audit_repository_release_gate_core.py")
S8_CURRENT_REL = Path("scripts/audit_study8_publication_current_state.py")


def git_paths(*args: str) -> set[Path]:
    result = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0:
        message = result.stderr.decode("utf-8", errors="replace").strip()
        raise RuntimeError(f"git {' '.join(args)} failed: {message}")
    return {
        Path(raw.decode("utf-8"))
        for raw in result.stdout.split(b"\0")
        if raw
    }


def remove_path(path: Path) -> None:
    if path.is_symlink() or path.is_file():
        path.unlink()
    elif path.is_dir():
        shutil.rmtree(path)


def overlay_tracked_worktree(audit_root: Path) -> None:
    index_paths = git_paths("ls-files", "-z")
    head_paths = git_paths("ls-tree", "-r", "--name-only", "-z", "HEAD")

    for rel in sorted(index_paths | head_paths, key=lambda item: item.as_posix()):
        source = ROOT / rel
        destination = audit_root / rel

        # A path absent from the current index is a staged deletion. A path present
        # in the index but absent from the working tree is an unstaged deletion.
        if rel not in index_paths or not os.path.lexists(source):
            if os.path.lexists(destination):
                remove_path(destination)
            continue

        destination.parent.mkdir(parents=True, exist_ok=True)
        if os.path.lexists(destination):
            remove_path(destination)

        if source.is_symlink():
            destination.symlink_to(os.readlink(source))
        elif source.is_file():
            shutil.copy2(source, destination)
        else:
            # Gitlinks/submodules are not release-gate document inputs. Preserve the
            # detached-worktree checkout rather than importing untracked contents.
            continue


def run_gate(audit_root: Path, rel: Path, label: str) -> int:
    script = audit_root / rel
    if not script.is_file():
        print(f"release_gate_wrapper=FAIL\nmissing_{label}={rel}", file=sys.stderr)
        return 1
    result = subprocess.run(
        [sys.executable, str(script)],
        cwd=audit_root,
        check=False,
    )
    if result.returncode != 0:
        print(f"release_gate_wrapper=FAIL\nfailed_gate={label}", file=sys.stderr)
    return result.returncode


def main() -> int:
    try:
        with tempfile.TemporaryDirectory(prefix="repository-release-gate-") as temp_parent:
            audit_root = Path(temp_parent) / "worktree"
            add = subprocess.run(
                ["git", "worktree", "add", "--detach", "--quiet", str(audit_root), "HEAD"],
                cwd=ROOT,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False,
            )
            if add.returncode != 0:
                print(
                    "release_gate_wrapper=FAIL\n"
                    f"git_worktree_add_error={add.stderr.strip()}",
                    file=sys.stderr,
                )
                return 1

            try:
                overlay_tracked_worktree(audit_root)
                if run_gate(audit_root, CORE_REL, "core") != 0:
                    return 1
                if run_gate(audit_root, S8_CURRENT_REL, "study8_publication_current_state") != 0:
                    return 1
                print("release_gate_wrapper=PASS")
                return 0
            finally:
                subprocess.run(
                    ["git", "worktree", "remove", "--force", str(audit_root)],
                    cwd=ROOT,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    check=False,
                )
    except Exception as exc:  # noqa: BLE001
        print(f"release_gate_wrapper=FAIL\nerror={exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
