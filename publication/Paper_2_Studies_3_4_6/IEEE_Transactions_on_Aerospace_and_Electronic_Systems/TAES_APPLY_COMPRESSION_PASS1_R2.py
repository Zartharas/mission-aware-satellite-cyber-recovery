#!/usr/bin/env python3
"""Apply TAES Paper 2 editorial compression pass 1, verifier revision 2.

This helper reuses the approved compression text from TAES_APPLY_COMPRESSION_PASS1.py
but fixes the preservation verifier. It edits only the Introduction, Section III,
and Section VII. Untouched manuscript components are verified against the tracked
component SHA-256 manifest before any write occurs.
"""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

import TAES_APPLY_COMPRESSION_PASS1 as p1

ROOT = Path(__file__).resolve().parent
INTRO = ROOT / "TAES_SECTION_I_INTRODUCTION.md"
CORE = ROOT / "TAES_MANUSCRIPT_SOURCE.md"
SYNTH = ROOT / "TAES_SECTION_VII_SYNTHESIS.md"
MANIFEST = ROOT / "TAES_MANUSCRIPT_COMPONENT_SHA256.txt"

UNTOUCHED_COMPONENTS = [
    "TAES_ABSTRACT_KEYWORDS.md",
    "TAES_SECTION_IV_STUDY3.md",
    "TAES_SECTION_V_STUDY4.md",
    "TAES_SECTION_VI_STUDY6.md",
    "TAES_SECTION_VIII_VALIDITY.md",
    "TAES_SECTION_IX_CONCLUSION.md",
]


def read(path: Path) -> str:
    if not path.is_file():
        raise SystemExit(f"ERROR: missing required file: {path}")
    return path.read_text(encoding="utf-8").replace("\r\n", "\n")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_manifest() -> dict[str, str]:
    entries: dict[str, str] = {}
    for line in read(MANIFEST).splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            digest, name = line.split("  ", 1)
        except ValueError as exc:
            raise SystemExit(f"ERROR: malformed component manifest line: {line}") from exc
        entries[name] = digest
    return entries


def verify_untouched_components() -> None:
    entries = parse_manifest()
    for name in UNTOUCHED_COMPONENTS:
        expected = entries.get(name)
        if not expected:
            raise SystemExit(f"ERROR: manifest entry missing for untouched component: {name}")
        actual = sha256(ROOT / name)
        if actual != expected:
            raise SystemExit(
                f"ERROR: untouched component drift before compression: {name}; "
                f"expected={expected}; actual={actual}"
            )


def verify_edited_targets(intro_new: str, core_new: str, synth_new: str) -> None:
    combined = "\n".join([intro_new, core_new, synth_new])

    if "—" in combined:
        raise SystemExit("ERROR: em dash introduced by compression pass")
    if "6,408" in combined:
        raise SystemExit("ERROR: combined Paper-2 population total introduced")
    if re.search(r"\[\d+\]\s*-\s*\[\d+\]", combined):
        raise SystemExit("ERROR: dash-form numeric citation range introduced")

    edited_markers = [
        "**RQ1:**",
        "**RQ2:**",
        "**RQ3:**",
        "1,380",
        "4,608",
        "420",
        "Only Study 3 directly models intermittent contact",
        "No pooled Paper-2 `N`",
        "not a prospectively tested integrated architecture",
        "V5",
        "Q3_D3",
        "G3",
        "G4",
        "APPROVED_BAD_SOURCE",
        "globally best policy",
    ]
    for marker in edited_markers:
        if marker not in combined:
            raise SystemExit(f"ERROR: required edited-target marker missing: {marker}")

    first_use: list[int] = []
    for match in re.finditer(r"\[(\d+)\]", intro_new):
        number = int(match.group(1))
        if number not in first_use:
            first_use.append(number)
    if first_use != list(range(1, 14)):
        raise SystemExit(
            f"ERROR: Introduction citation first-use order changed: {first_use}"
        )


def verify_global_preservation(intro_new: str, core_new: str, synth_new: str) -> None:
    global_text = "\n".join(
        [
            intro_new,
            core_new,
            read(ROOT / "TAES_SECTION_IV_STUDY3.md"),
            read(ROOT / "TAES_SECTION_V_STUDY4.md"),
            read(ROOT / "TAES_SECTION_VI_STUDY6.md"),
            synth_new,
            read(ROOT / "TAES_SECTION_VIII_VALIDITY.md"),
            read(ROOT / "TAES_SECTION_IX_CONCLUSION.md"),
        ]
    )

    global_markers = [
        "PRE_ONSET_CACHE",
        "46/46",
        "122.500",
        "55.326",
        "49.022",
        "3/46",
        "0.326",
        "Q3_D3",
        "Q4_D1",
        "Q4_D2",
        "G0_SIGNATURE_ONLY",
        "G5_COMPOSITE",
        "32/64",
        "48/64",
        "56/64",
        "63/64",
        "APPROVED_BAD_SOURCE",
        "same-repository reproducibility",
        "not a prospectively tested integrated architecture",
    ]
    for marker in global_markers:
        if marker not in global_text:
            raise SystemExit(f"ERROR: required global preservation marker missing: {marker}")


def main() -> None:
    intro_old = read(INTRO)
    core_old = read(CORE)
    synth_old = read(SYNTH)

    # Confirm the files we are intentionally not editing still match the tracked
    # pre-compression component manifest.
    verify_untouched_components()

    baseline_markers = [
        (intro_old, "Several results constrain stronger interpretations and are intentionally retained."),
        (core_old, "#### 1) Study 3: temporal evidence qualification"),
        (core_old, "### F. Cross-Study Interpretation Rule"),
        (synth_old, "## C. Integrity and Authenticity Do Not Exhaust Semantic Trust"),
        (synth_old, "## G. Aerospace Systems Implications"),
    ]
    for text, marker in baseline_markers:
        if marker not in text:
            raise SystemExit(f"ERROR: expected compression baseline marker missing: {marker}")

    intro_new = p1.INTRO_NEW
    core_new = p1.replace_section(
        core_old,
        "## III. Common Trust-Qualification Framework and Study Separation",
        "## References Used in Sections II and III",
        p1.SECTION_III_NEW,
        "Section III",
    )
    synth_new = p1.SYNTH_NEW

    verify_edited_targets(intro_new, core_new, synth_new)
    verify_global_preservation(intro_new, core_new, synth_new)

    before = {
        "I": p1.words(intro_old),
        "III": p1.words(
            core_old[
                core_old.find("## III.") : core_old.find(
                    "## References Used in Sections II and III"
                )
            ]
        ),
        "VII": p1.words(synth_old),
    }
    after = {
        "I": p1.words(intro_new),
        "III": p1.words(p1.SECTION_III_NEW),
        "VII": p1.words(synth_new),
    }

    total_reduction = sum(before.values()) - sum(after.values())
    if total_reduction < 1200:
        raise SystemExit(f"ERROR: compression reduction too small: {total_reduction} words")
    if total_reduction > 2200:
        raise SystemExit(
            f"ERROR: compression reduction exceeds conservative pass bound: {total_reduction} words"
        )

    p1.write(INTRO, intro_new)
    p1.write(CORE, core_new)
    p1.write(SYNTH, synth_new)

    print("TAES_COMPRESSION_PASS1_R2=PASS")
    print(f"section_I_before={before['I']}")
    print(f"section_I_after={after['I']}")
    print(f"section_III_before={before['III']}")
    print(f"section_III_after={after['III']}")
    print(f"section_VII_before={before['VII']}")
    print(f"section_VII_after={after['VII']}")
    print(f"targeted_word_reduction={total_reduction}")
    print("untouched_component_manifest_check=PASS")
    print("science_files_changed=NONE")
    print("section_VIII_changed=NO")
    print(
        "NOTE: Re-run TAES_ASSEMBLE_MANUSCRIPT.py and "
        "TAES_AUDIT_LENGTH_REDUNDANCY.py before committing."
    )


if __name__ == "__main__":
    main()
