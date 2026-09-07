#!/usr/bin/env python3
"""Apply TAES Paper-2 compression Pass 2 revision 2.

R2 exists because the first Pass-2 candidate removed 3,630 words and was
correctly stopped by its reduction guard. This revision does not weaken that
guard. Instead, it evaluates the candidate reduction contributed by each of the
five proposed section replacements independently and applies only a subset whose
combined reduction falls inside the authorized 1,700-2,200-word window.

The script is self-recovering for the known Pass-2 failure state: it verifies
that the tracked HEAD versions of the five candidate manuscript components are
exactly the canonical pre-pass versions, permits local tracked modifications only
for those five files, and restores only those five files from HEAD before
constructing the R2 candidate. Untracked IEEEtran development artifacts are not
touched.

No frozen study, result, population, protocol, workflow, audit evidence, Figure
1, abstract, Sections I-III or VII, references, or AI disclosure is modified.
The assembled result remains a local review candidate only.
"""

from __future__ import annotations

import hashlib
import itertools
import re
import subprocess
import sys
from pathlib import Path

import TAES_APPLY_COMPRESSION_PASS2 as p1

ROOT = Path(__file__).resolve().parent
REPO = Path(
    subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    ).stdout.strip()
)

FILES = p1.FILES
EXPECTED_PRE_SHA256 = p1.EXPECTED_PRE_SHA256
UNTOUCHED = p1.UNTOUCHED
CANDIDATE = p1.NEW_CONTENT
WORD_RE = re.compile(r"\b[\w'-]+\b")

MIN_REDUCTION = 1700
MAX_REDUCTION = 2200
TARGET_REDUCTION = 1900

# Preference follows the feasibility audit: first remove table-driven and
# validity duplication, then consider Study 6, Study 3, and the Conclusion.
PRIORITY = {"v": 0, "viii": 1, "vi": 2, "iv": 3, "ix": 4}


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_file(path: Path) -> str:
    return sha_bytes(path.read_bytes())


def words(text: str) -> int:
    return len(WORD_RE.findall(text))


def rel(path: Path) -> str:
    return path.resolve().relative_to(REPO.resolve()).as_posix()


def head_bytes(path: Path) -> bytes:
    proc = subprocess.run(
        ["git", "show", f"HEAD:{rel(path)}"],
        cwd=REPO,
        check=True,
        capture_output=True,
    )
    return proc.stdout


def tracked_modified_paths() -> set[str]:
    proc = subprocess.run(
        ["git", "diff", "--name-only"],
        cwd=REPO,
        check=True,
        text=True,
        capture_output=True,
    )
    return {line.strip() for line in proc.stdout.splitlines() if line.strip()}


def verify_head_baseline() -> dict[str, str]:
    baseline: dict[str, str] = {}
    for key, path in FILES.items():
        data = head_bytes(path)
        actual = sha_bytes(data)
        expected = EXPECTED_PRE_SHA256[path.name]
        if actual != expected:
            raise SystemExit(
                "ERROR: tracked HEAD baseline drift for "
                f"{path.name}: expected {expected}, got {actual}"
            )
        baseline[key] = data.decode("utf-8")
    return baseline


def recover_known_partial_state(baseline: dict[str, str]) -> None:
    allowed = {rel(path) for path in FILES.values()}
    modified = tracked_modified_paths()
    outside = sorted(modified - allowed)
    if outside:
        raise SystemExit(
            "ERROR: tracked modifications outside the known Pass-2 component set; "
            "refusing automatic recovery: " + ", ".join(outside)
        )

    for key, path in FILES.items():
        path.write_text(baseline[key], encoding="utf-8")
        actual = sha_file(path)
        expected = EXPECTED_PRE_SHA256[path.name]
        if actual != expected:
            raise SystemExit(
                f"ERROR: failed to recover {path.name} to canonical HEAD baseline"
            )


def choose_sections(baseline: dict[str, str]) -> tuple[tuple[str, ...], dict[str, int]]:
    reductions = {
        key: words(baseline[key]) - words(CANDIDATE[key])
        for key in FILES
    }
    if any(value <= 0 for value in reductions.values()):
        raise SystemExit(f"ERROR: nonpositive section reduction detected: {reductions}")

    feasible: list[tuple[tuple[int, int, int, tuple[int, ...]], tuple[str, ...], int]] = []
    keys = tuple(FILES.keys())
    for size in range(1, len(keys) + 1):
        for combo in itertools.combinations(keys, size):
            total = sum(reductions[key] for key in combo)
            if not (MIN_REDUCTION <= total <= MAX_REDUCTION):
                continue
            contains_v_viii = int(not ("v" in combo and "viii" in combo))
            priority_vector = tuple(sorted(PRIORITY[key] for key in combo))
            score = (
                abs(total - TARGET_REDUCTION),
                contains_v_viii,
                len(combo),
                priority_vector,
            )
            feasible.append((score, combo, total))

    if not feasible:
        detail = ", ".join(f"{k}={v}" for k, v in reductions.items())
        raise SystemExit(
            "ERROR: no whole-section candidate combination falls inside the "
            f"authorized {MIN_REDUCTION}-{MAX_REDUCTION}-word window; {detail}"
        )

    feasible.sort(key=lambda item: item[0])
    _, combo, _ = feasible[0]
    return combo, reductions


def verify_untouched() -> None:
    for name, expected in UNTOUCHED.items():
        path = ROOT / name
        if not path.is_file():
            raise SystemExit(f"ERROR: missing untouched component: {name}")
        actual = sha_file(path)
        if actual != expected:
            raise SystemExit(
                f"ERROR: untouched component drift for {name}: expected {expected}, got {actual}"
            )


def main() -> None:
    baseline = verify_head_baseline()
    recover_known_partial_state(baseline)
    verify_untouched()

    combo, reductions = choose_sections(baseline)
    selected = set(combo)
    total_reduction = sum(reductions[key] for key in combo)

    # Preflight selected candidate prose before writing it.
    selected_text = "\n".join(CANDIDATE[key] for key in combo)
    if "—" in selected_text:
        raise SystemExit("ERROR: em dash detected in selected Pass-2 R2 candidate")

    for key, path in FILES.items():
        text = CANDIDATE[key] if key in selected else baseline[key]
        path.write_text(text.strip() + "\n", encoding="utf-8")

    verify_untouched()

    # Unselected sections must remain byte-identical to the canonical baseline.
    for key, path in FILES.items():
        if key in selected:
            continue
        expected = EXPECTED_PRE_SHA256[path.name]
        actual = sha_file(path)
        if actual != expected:
            raise SystemExit(
                f"ERROR: unselected section drift after R2 construction: {path.name}"
            )

    actual_before = sum(words(text) for text in baseline.values())
    actual_after = sum(words(path.read_text(encoding="utf-8")) for path in FILES.values())
    actual_reduction = actual_before - actual_after
    if actual_reduction != total_reduction:
        raise SystemExit(
            f"ERROR: R2 reduction accounting mismatch: expected {total_reduction}, got {actual_reduction}"
        )
    if not (MIN_REDUCTION <= actual_reduction <= MAX_REDUCTION):
        raise SystemExit(
            f"ERROR: R2 reduction outside authorized range: {actual_reduction} words"
        )

    assembler = ROOT / "TAES_ASSEMBLE_MANUSCRIPT.py"
    audit = ROOT / "TAES_AUDIT_LENGTH_REDUNDANCY.py"
    subprocess.run([sys.executable, str(assembler)], cwd=ROOT, check=True)
    subprocess.run([sys.executable, str(audit)], cwd=ROOT, check=True)

    full_path = ROOT / "TAES_MANUSCRIPT_FULL_DRAFT.md"
    full = full_path.read_text(encoding="utf-8")

    # Scientific-preservation sentinels distributed across all three studies and
    # the validity firewall. These are checks, not substitutes for human review.
    required = [
        "1,380",
        "67,620",
        "PRE_ONSET_CACHE",
        "V5_AFFECTED_RECORD",
        "122.5",
        "55.326",
        "49.022",
        "0.326",
        "4,608",
        "Q3_D3",
        "Q4_D3",
        "Q5_D3",
        "420 exact observations",
        "APPROVED_BAD_SOURCE",
        "32/64",
        "48/64",
        "56/64",
        "63/64",
        "Only Study 3 models contact",
        "not external empirical replication",
    ]
    for marker in required:
        if marker not in full:
            raise SystemExit(f"ERROR: assembled R2 protected marker missing: {marker}")

    forbidden = [
        "6,408",
        "mission availability improves",
        "operational attack rate",
    ]
    for marker in forbidden:
        if marker.lower() in full.lower():
            raise SystemExit(f"ERROR: forbidden R2 phrase detected: {marker}")

    print("TAES_COMPRESSION_PASS2_R2=PASS_LOCAL_CANDIDATE_ONLY")
    print("recovery_from_failure1_partial_state=PASS_CANONICAL_HEAD_RESTORED_FIRST")
    print("science_files_changed=NONE")
    print("study_rerun=NO")
    print("abstract_changed=NO")
    print("sections_I_II_III_VII_changed=NO")
    print("references_changed=NO")
    print("figure1_changed=NO")
    print("ai_disclosure_changed=NO")
    print("authorized_reduction_window=1700..2200")
    print(f"target_reduction_words={TARGET_REDUCTION}")
    for key in ("iv", "v", "vi", "viii", "ix"):
        print(f"candidate_section_{key}_standalone_reduction_words={reductions[key]}")
    print("selected_sections=" + ",".join(key.upper() for key in combo))
    print(f"edited_sections_reduction_words={actual_reduction}")
    print(f"assembled_sha256={sha_file(full_path)}")
    print("candidate_status=UNTRACKED_REVIEW_REQUIRED")
    print("publisher_facing=NO")
    print("submission_effective=NO_PENDING_REMAINING_GATES")


if __name__ == "__main__":
    main()
