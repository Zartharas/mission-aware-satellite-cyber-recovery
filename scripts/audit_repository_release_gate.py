#!/usr/bin/env python3
"""Run repository release gates against Git-tracked working-tree content only.

The historical core release-gate audit intentionally traverses its repository
root and retains assertions that were correct at the 2026-09-04 publication
state. Later publication closeouts intentionally replaced some active README
and tracker wording while leaving frozen scientific records unchanged.

This wrapper creates a detached temporary worktree at HEAD, overlays the
caller's Git-tracked working-tree state, runs the historical core audit, and
permits only the exact known stale-current-state failures when the authoritative
2026-09-13 publication-state record is present. Any additional or different
core failure still fails closed. The current Study-8 publication-state overlay
and Repository Review v3 remediation audit then run normally.

Untracked and ignored files are excluded by construction. No scientific runtime
is started and no tracked repository file is modified.
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
REVIEW_V3_REL = Path("scripts/audit_repository_review_v3_remediation.py")

CURRENT_STATE_REL = Path("docs/CURRENT_PUBLICATION_STATE.md")
CURRENT_STATE_REQUIRED = (
    "**Current-state date:** 2026-09-13",
    "four submitted publication lines",
    "2026-09-I012066",
    "AA-D-26-02872",
    "cd1dfa89-4a24-4451-bdd4-af31ce3367f4",
    "6db04a31-8223-4aaf-af02-e4bafe06ef89",
    "read-only candidate audit",
)

EXPECTED_LEGACY_CORE_FAILURES = frozenset(
    {
        "research tracker missing Study-1 Zenodo version DOI: 10.5281/zenodo.22181540",
        "research tracker missing Study-1 Zenodo concept DOI: 10.5281/zenodo.22181539",
        "research tracker missing Study-1 720-membership SHA-256: a2bf0c8f352f4386e74a500d97ea8f73e0c39d03bfe10ac0ebcf02470af9f70e",
        "research tracker missing Study-1 attempt-history ledger SHA-256: 92893a2fd8746f410bffd4dca5101bc3f533ada2ff82f98681788cf0c24ce6fd",
        "research tracker missing Study-1 campaign-tree SHA-256: ad1e127b4431b6b334955129fcba82f76b18e5b43585395ac8c37300cac087b1",
        "research tracker missing Study-2 Phase-6 artifact SHA: 195860bd44b38ccf170f02cb1cb392583217296d08640c99b18b52286403e133",
        "research tracker missing Study-2 observations SHA: 8dcc850c561d7e3c0bf7478263b534cae83cbbb55183c313e879dd7d61127854",
        "research tracker missing Study-2 trial-manifest SHA: 190612473717b7768ceccb4596a20d90cd7d532bf7581330ce94d609cb752e67",
        "research tracker missing Study-2 Phase-7 result SHA: 0136123a53d150437fefc8ace342af63b11d980cf8cab32ef7a4f03b78267417",
        "research tracker missing Study-2 canonical closeout commit: 2bd3fb34ca709127e45ea9bffa8f516846d6c4b5",
        "research tracker missing Study-2 Zenodo version DOI: 10.5281/zenodo.22289114",
        "research tracker missing Study-2 Zenodo concept DOI: 10.5281/zenodo.22289113",
        "research tracker missing Study-8 technical-close status: TECHNICALLY_CLOSED_PUBLICATION_INTEGRATION_NOT_STARTED",
        "research tracker missing Study-8 canonical observations SHA: cfc65b6663be4e9f17a00ed102730f8642efcbbd844045acce032ff09a0bcabf",
        "research tracker missing Study-8 findings SHA: 26a8ac4d1039917323e75a294775dd14a2b563adb12a5d2fcdb47ce8f15c992e",
        "research tracker missing Study-8 interpretation-audit SHA: 620827f83fb566ff6ceae1b66c8f51f61ef8e5bbdabbb1c4b5a48b5187a82413",
        "research tracker missing Study-8 science merge commit: 63106778559c3127a7d6e8765d52939b73a3f35b",
        "README.md: required current-state text missing: 'two separately frozen empirical studies'",
        "README.md: required current-state text missing: '195860bd44b38ccf170f02cb1cb392583217296d08640c99b18b52286403e133'",
        "README.md: required current-state text missing: 'public-download SHA-256'",
        "README.md: required current-state text missing: 'TECHNICALLY_CLOSED_PUBLICATION_INTEGRATION_NOT_STARTED'",
        "README.md: required current-state text missing: 'separate companion study'",
        "README.md: required current-state text missing: 'structural label-invariance'",
        "publication/README.md: required current-state text missing: 'two separately frozen empirical studies'",
        "publication/README.md: required current-state text missing: '03-study2-methods-extension.md'",
        "publication/README.md: required current-state text missing: '04-study2-results-extension.md'",
        "publication/README.md: required current-state text missing: '10.5281/zenodo.22289114'",
        "publication/README.md: required current-state text missing: '10.5281/zenodo.22289113'",
        "publication/README.md: required current-state text missing: 'public-byte verified'",
        "publication/README.md: required current-state text missing: 'companion-paper'",
        "tracker/RESEARCH_TRACKER.md: required current-state text missing: 'Last updated: 2026-09-04'",
        "tracker/RESEARCH_TRACKER.md: required current-state text missing: 'PRESPECIFIED_ANALYSIS_RESULTS_FROZEN_CANONICAL'",
        "tracker/RESEARCH_TRACKER.md: required current-state text missing: '2bd3fb34ca709127e45ea9bffa8f516846d6c4b5'",
        "tracker/RESEARCH_TRACKER.md: required current-state text missing: '10.5281/zenodo.22289114'",
        "tracker/RESEARCH_TRACKER.md: required current-state text missing: '10.5281/zenodo.22289113'",
        "tracker/RESEARCH_TRACKER.md: required current-state text missing: 'DOI/archive blocker for the existing journal article is therefore closed'",
        "tracker/RESEARCH_TRACKER.md: required current-state text missing: 'TECHNICALLY_CLOSED_PUBLICATION_INTEGRATION_NOT_STARTED'",
        "tracker/RESEARCH_TRACKER.md: required current-state text missing: '63106778559c3127a7d6e8765d52939b73a3f35b'",
        "tracker/RESEARCH_TRACKER.md: required current-state text missing: 'Study-8 companion paper'",
    }
)


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


def authoritative_current_state_is_bound(audit_root: Path) -> bool:
    path = audit_root / CURRENT_STATE_REL
    if not path.is_file():
        print(
            f"release_gate_wrapper=FAIL\nmissing_current_state={CURRENT_STATE_REL}",
            file=sys.stderr,
        )
        return False

    text = path.read_text(encoding="utf-8")
    missing = [token for token in CURRENT_STATE_REQUIRED if token not in text]
    if missing:
        print("release_gate_wrapper=FAIL", file=sys.stderr)
        for token in missing:
            print(f"missing_current_state_token={token}", file=sys.stderr)
        return False

    print("authoritative_current_publication_state=PASS_2026_09_13")
    return True


def run_core_with_stale_current_state_compat(audit_root: Path) -> int:
    script = audit_root / CORE_REL
    if not script.is_file():
        print(f"release_gate_wrapper=FAIL\nmissing_core={CORE_REL}", file=sys.stderr)
        return 1

    result = subprocess.run(
        [sys.executable, str(script)],
        cwd=audit_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )

    if result.stdout:
        print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, end="", file=sys.stderr)

    if result.returncode == 0:
        print("legacy_core_gate=PASS_NATIVE")
        return 0

    if not authoritative_current_state_is_bound(audit_root):
        return 1

    failure_lines = [
        line.removeprefix("[FAIL] ")
        for line in (*result.stdout.splitlines(), *result.stderr.splitlines())
        if line.startswith("[FAIL] ")
    ]
    actual_failures = frozenset(failure_lines)

    if len(failure_lines) != len(EXPECTED_LEGACY_CORE_FAILURES):
        print(
            "release_gate_wrapper=FAIL\n"
            f"legacy_core_failure_count={len(failure_lines)}\n"
            f"expected_legacy_core_failure_count={len(EXPECTED_LEGACY_CORE_FAILURES)}",
            file=sys.stderr,
        )
        return 1

    if actual_failures != EXPECTED_LEGACY_CORE_FAILURES:
        unexpected = sorted(actual_failures - EXPECTED_LEGACY_CORE_FAILURES)
        missing = sorted(EXPECTED_LEGACY_CORE_FAILURES - actual_failures)
        print("release_gate_wrapper=FAIL", file=sys.stderr)
        for item in unexpected:
            print(f"unexpected_legacy_core_failure={item}", file=sys.stderr)
        for item in missing:
            print(f"missing_expected_legacy_core_failure={item}", file=sys.stderr)
        return 1

    if "errors=39" not in result.stdout:
        print(
            "release_gate_wrapper=FAIL\nlegacy_core_expected_errors_marker_missing=errors=39",
            file=sys.stderr,
        )
        return 1

    print("legacy_core_gate=PASS_EXACT_STALE_CURRENT_STATE_COMPAT_39")
    return 0


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
                if run_core_with_stale_current_state_compat(audit_root) != 0:
                    return 1
                if run_gate(audit_root, S8_CURRENT_REL, "study8_publication_current_state") != 0:
                    return 1
                if run_gate(audit_root, REVIEW_V3_REL, "repository_review_v3_remediation") != 0:
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
