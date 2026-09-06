#!/usr/bin/env python3
"""Apply the remaining pre-format compliance corrections for TAES Paper 2.

This helper is deliberately narrow and idempotent. It may update only TUF
bibliographic metadata in the live source, literature ledger, and rerunnable
bibliography helper. The controlled IEEE AI-use acknowledgment is bound directly
by TAES_ASSEMBLE_MANUSCRIPT.py and is only verified here.

It does not rerun or alter Study 3, Study 4, or Study 6 science.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent

MANUSCRIPT = ROOT / "TAES_MANUSCRIPT_FULL_DRAFT.md"
FIG_PDF = ROOT / "TAES_FIGURE1_RESIDUAL_BOUNDARIES.pdf"
FIG_PNG = ROOT / "TAES_FIGURE1_RESIDUAL_BOUNDARIES.png"
CORE = ROOT / "TAES_MANUSCRIPT_SOURCE.md"
LEDGER = ROOT / "TAES_LITERATURE_SOURCE_LEDGER.md"
BIB_HELPER = ROOT / "TAES_APPLY_BIBLIOGRAPHY_FIXES.py"
ASSEMBLER = ROOT / "TAES_ASSEMBLE_MANUSCRIPT.py"
ACK = ROOT / "TAES_ACKNOWLEDGMENT_AI_DISCLOSURE.md"

BASELINE_MANUSCRIPT = "dde7d9c6ab4efb1c6f567937dd1c28c904baeb713dc960b716eae1b15ef5e709"
PARTIAL_TUF_MANUSCRIPT = "c904425c3095ea62642f6d0cf671865a81f36fd629b37050bd35e360f5e0c08e"
EXPECTED_FIG_PDF = "4872707261c8a8b6b747e76b9166b4ad7ae426e43d7bd9ffe272e4c5ea6f4ff8"
EXPECTED_FIG_PNG = "7d22964bdae052b35b4680e1b09f3209f1c99bb1d157a0f995dcd2a6445e6698"

OLD_REF = '[11] The Update Framework. "The Update Framework Specification, v1.0.33." Accessed: Sep. 6, 2026. [Online]. Available: https://theupdateframework.io/spec/'
NEW_REF = '[11] The Update Framework. "The Update Framework Specification, v1.0.36." Aug. 10, 2026. [Online]. Available: https://github.com/theupdateframework/specification/releases/tag/v1.0.36'


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read(path: Path) -> str:
    if not path.is_file():
        raise SystemExit(f"ERROR: missing required file: {path}")
    return path.read_text(encoding="utf-8").replace("\r\n", "\n")


def write(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def replace_old_or_accept_new(text: str, old: str, new: str, label: str) -> str:
    old_count = text.count(old)
    new_count = text.count(new)
    if old_count == 1 and new_count == 0:
        return text.replace(old, new, 1)
    if old_count == 0 and new_count >= 1:
        return text
    raise SystemExit(
        f"ERROR: ambiguous state for {label}: old_count={old_count} new_count={new_count}"
    )


def verify_start_state() -> None:
    for path, expected in [(FIG_PDF, EXPECTED_FIG_PDF), (FIG_PNG, EXPECTED_FIG_PNG)]:
        actual = sha256(path)
        if actual != expected:
            raise SystemExit(
                f"ERROR: figure binding mismatch for {path.name}: expected={expected} actual={actual}"
            )

    manuscript_hash = sha256(MANUSCRIPT)
    manuscript_text = read(MANUSCRIPT)
    already_complete = (
        "## Acknowledgment" in manuscript_text
        and "OpenAI ChatGPT (GPT-5.6 Sol)" in manuscript_text
        and NEW_REF in manuscript_text
        and "v1.0.33" not in manuscript_text
    )
    if manuscript_hash not in {BASELINE_MANUSCRIPT, PARTIAL_TUF_MANUSCRIPT} and not already_complete:
        raise SystemExit(
            "ERROR: manuscript is neither the canonical baseline, the known safe partial-TUF state, "
            f"nor an already-compliant assembled state: {manuscript_hash}"
        )


def patch_core() -> None:
    text = read(CORE)
    text = replace_old_or_accept_new(text, OLD_REF, NEW_REF, "live manuscript TUF reference")
    write(CORE, text)


def patch_ledger() -> None:
    text = read(LEDGER)
    pairs = [
        (
            'The Update Framework, "The Update Framework Specification, v1.0.33," latest stable specification.',
            'The Update Framework, "The Update Framework Specification, v1.0.36," latest stable specification release.',
            "ledger TUF identity",
        ),
        (
            "Official specification page: https://theupdateframework.io/spec/",
            "Official release record: https://github.com/theupdateframework/specification/releases/tag/v1.0.36",
            "ledger TUF URL",
        ),
        (
            "- the official specification page identifies v1.0.33 as the latest stable specification as of 2026-09-06;",
            "- the official specification repository release history identifies v1.0.36 as the latest release as of 2026-09-06;",
            "ledger TUF live verification",
        ),
    ]
    for old, new, label in pairs:
        text = replace_old_or_accept_new(text, old, new, label)
    write(LEDGER, text)


def patch_bibliography_helper() -> None:
    text = read(BIB_HELPER)
    text = text.replace("v1.0.33", "v1.0.36")
    text = text.replace(
        "https://theupdateframework.io/spec/",
        "https://github.com/theupdateframework/specification/releases/tag/v1.0.36",
    )
    text = text.replace(
        "the official specification page identifies v1.0.36 as the latest stable specification as of 2026-09-06;",
        "the official specification repository release history identifies v1.0.36 as the latest release as of 2026-09-06;",
    )
    text = text.replace("Official specification page:", "Official release record:")
    text = text.replace(
        'The Update Framework Specification, v1.0.36.\\" Accessed: Sep. 6, 2026.',
        'The Update Framework Specification, v1.0.36.\\" Aug. 10, 2026.',
    )
    write(BIB_HELPER, text)


def verify_assembler_and_ack() -> None:
    assembler = read(ASSEMBLER)
    ack = read(ACK)
    assembler_markers = [
        '"TAES_ACKNOWLEDGMENT_AI_DISCLOSURE.md"',
        '"## Acknowledgment\\n\\n" + acknowledgment',
        '"## Acknowledgment"',
        'print("ieee_ai_disclosure_binding=PASS")',
    ]
    for marker in assembler_markers:
        if marker not in assembler:
            raise SystemExit(f"ERROR: canonical assembler AI-disclosure binding missing: {marker}")

    ack_markers = [
        "OpenAI ChatGPT (GPT-5.6 Sol)",
        "Abstract and Sections I-IX",
        "substantive drafting and editorial level",
        "It was not used to generate or modify the frozen experimental results.",
        "assumes responsibility for the final manuscript",
    ]
    for marker in ack_markers:
        if marker not in ack:
            raise SystemExit(f"ERROR: required AI-disclosure marker missing: {marker}")


def verify_final_sources() -> None:
    core = read(CORE)
    ledger = read(LEDGER)
    bib_helper = read(BIB_HELPER)
    if OLD_REF in core or "v1.0.33" in core:
        raise SystemExit("ERROR: stale TUF v1.0.33 remains in live manuscript source")
    if NEW_REF not in core:
        raise SystemExit("ERROR: corrected TUF v1.0.36 reference missing from live manuscript source")
    if "v1.0.36" not in ledger or "releases/tag/v1.0.36" not in ledger:
        raise SystemExit("ERROR: literature ledger was not corrected to TUF v1.0.36")
    if "v1.0.33" in bib_helper:
        raise SystemExit("ERROR: rerunnable bibliography helper can still regress TUF to v1.0.33")


if __name__ == "__main__":
    verify_start_state()
    patch_core()
    patch_ledger()
    patch_bibliography_helper()
    verify_assembler_and_ack()
    verify_final_sources()
    print("TAES_PRE_FORMAT_COMPLIANCE_FIXES=PASS")
    print("resume_mode=BASELINE_OR_SAFE_PARTIAL_STATE")
    print("tuf_reference=V1.0.36_OFFICIAL_RELEASE_RECORD")
    print("ieee_ai_disclosure=BOUND_BY_CANONICAL_ASSEMBLER")
    print("science_files_changed=NONE")
    print("NOTE: Re-run TAES_ASSEMBLE_MANUSCRIPT.py and length audit before committing.")
