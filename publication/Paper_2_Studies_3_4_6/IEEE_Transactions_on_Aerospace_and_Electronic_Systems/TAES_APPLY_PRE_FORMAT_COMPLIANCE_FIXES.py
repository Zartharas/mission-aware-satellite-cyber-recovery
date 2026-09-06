#!/usr/bin/env python3
"""Apply pre-format compliance corrections for TAES Paper 2.

This helper performs only two controlled manuscript-preparation updates:
1. update TUF reference [11] from stale v1.0.33 metadata to the official
   v1.0.36 release record;
2. bind the controlled IEEE AI-use acknowledgment into deterministic assembly.

The helper is deliberately idempotent and can resume from the safe partial state
created by the first revision, in which the TUF correction was already applied
but acknowledgment registration had not yet occurred.

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
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
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
    allowed = {BASELINE_MANUSCRIPT, PARTIAL_TUF_MANUSCRIPT}
    # A previously completed run is also acceptable if the disclosure is already assembled.
    manuscript_text = read(MANUSCRIPT)
    already_complete = (
        "## Acknowledgment" in manuscript_text
        and "OpenAI ChatGPT (GPT-5.6 Sol)" in manuscript_text
        and NEW_REF in manuscript_text
        and "v1.0.33" not in manuscript_text
    )
    if manuscript_hash not in allowed and not already_complete:
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
    # Accept either the original helper or the already-corrected partial state.
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


def add_ack_to_components(text: str) -> str:
    component = '    "TAES_ACKNOWLEDGMENT_AI_DISCLOSURE.md",\n'
    if component in text:
        return text

    start = text.find("COMPONENTS = [\n")
    if start < 0:
        raise SystemExit("ERROR: COMPONENTS block start missing")
    end = text.find("\n]\n\nFIGURE_FILES", start)
    if end < 0:
        raise SystemExit("ERROR: COMPONENTS block end missing")
    block = text[start:end]
    anchor = '    "TAES_SECTION_IX_CONCLUSION.md",\n'
    if block.count(anchor) != 1:
        raise SystemExit("ERROR: Section IX anchor not unique inside COMPONENTS block")
    block = block.replace(anchor, anchor + component, 1)
    return text[:start] + block + text[end:]


def patch_assembler() -> None:
    text = read(ASSEMBLER)
    text = add_ack_to_components(text)

    extraction_new = '''    later_sections = [normalize_section(read(name)) for name in SECTION_FILES[1:]]\n\n    ack_doc = read("TAES_ACKNOWLEDGMENT_AI_DISCLOSURE.md")\n    ack_lines = []\n    for line in ack_doc.splitlines():\n        stripped = line.strip()\n        if stripped == "# Acknowledgment":\n            continue\n        if stripped.startswith("> Control note:"):\n            continue\n        ack_lines.append(line)\n    acknowledgment = "\\n".join(ack_lines).strip()\n    if not acknowledgment:\n        raise SystemExit("ERROR: AI-use acknowledgment body is empty")\n\n    assembled_parts = ['''
    extraction_old = '    later_sections = [normalize_section(read(name)) for name in SECTION_FILES[1:]]\n\n    assembled_parts = ['
    if extraction_new not in text:
        if text.count(extraction_old) != 1:
            raise SystemExit("ERROR: acknowledgment extraction anchor missing or ambiguous")
        text = text.replace(extraction_old, extraction_new, 1)

    parts_new = '        *later_sections,\n        "## Acknowledgment\\n\\n" + acknowledgment,\n        references,\n    ]'
    parts_old = '        *later_sections,\n        references,\n    ]'
    if parts_new not in text:
        if text.count(parts_old) != 1:
            raise SystemExit("ERROR: acknowledgment assembly-order anchor missing or ambiguous")
        text = text.replace(parts_old, parts_new, 1)

    req_new = '        "## IX. Conclusion",\n        "## Acknowledgment",\n        "## References",'
    req_old = '        "## IX. Conclusion",\n        "## References",'
    if req_new not in text:
        if text.count(req_old) != 1:
            raise SystemExit("ERROR: acknowledgment required-marker anchor missing or ambiguous")
        text = text.replace(req_old, req_new, 1)

    print_new = '    print("retired_table_v_check=PASS")\n    print("ieee_ai_disclosure_binding=PASS")\n'
    print_old = '    print("retired_table_v_check=PASS")\n'
    if print_new not in text:
        if text.count(print_old) != 1:
            raise SystemExit("ERROR: acknowledgment PASS-output anchor missing or ambiguous")
        text = text.replace(print_old, print_new, 1)

    write(ASSEMBLER, text)


def verify() -> None:
    core = read(CORE)
    ledger = read(LEDGER)
    bib_helper = read(BIB_HELPER)
    assembler = read(ASSEMBLER)
    ack = read(ACK)

    if OLD_REF in core or "v1.0.33" in core:
        raise SystemExit("ERROR: stale TUF v1.0.33 remains in live manuscript source")
    if NEW_REF not in core:
        raise SystemExit("ERROR: corrected TUF v1.0.36 reference missing from live manuscript source")
    if "v1.0.36" not in ledger or "releases/tag/v1.0.36" not in ledger:
        raise SystemExit("ERROR: literature ledger was not corrected to TUF v1.0.36")
    if "v1.0.33" in bib_helper:
        raise SystemExit("ERROR: rerunnable bibliography helper can still regress TUF to v1.0.33")
    if '"TAES_ACKNOWLEDGMENT_AI_DISCLOSURE.md"' not in assembler:
        raise SystemExit("ERROR: assembler does not bind AI-use acknowledgment component")
    if '"## Acknowledgment\\n\\n" + acknowledgment' not in assembler:
        raise SystemExit("ERROR: assembler does not insert Acknowledgment before references")
    if '"## Acknowledgment"' not in assembler:
        raise SystemExit("ERROR: assembler does not require Acknowledgment section")
    if 'print("ieee_ai_disclosure_binding=PASS")' not in assembler:
        raise SystemExit("ERROR: assembler does not report AI-disclosure binding")

    required_ack = [
        "OpenAI ChatGPT (GPT-5.6 Sol)",
        "Abstract and Sections I-IX",
        "substantive drafting and editorial level",
        "It was not used to generate or modify the frozen experimental results.",
        "assumes responsibility for the final manuscript",
    ]
    for marker in required_ack:
        if marker not in ack:
            raise SystemExit(f"ERROR: required AI-disclosure marker missing: {marker}")


if __name__ == "__main__":
    verify_start_state()
    patch_core()
    patch_ledger()
    patch_bibliography_helper()
    patch_assembler()
    verify()
    print("TAES_PRE_FORMAT_COMPLIANCE_FIXES=PASS")
    print("resume_mode=BASELINE_OR_SAFE_PARTIAL_STATE")
    print("tuf_reference=V1.0.36_OFFICIAL_RELEASE_RECORD")
    print("ieee_ai_disclosure=BOUND_AS_CONTROLLED_COMPONENT")
    print("science_files_changed=NONE")
    print("NOTE: Re-run TAES_ASSEMBLE_MANUSCRIPT.py and length audit before committing.")
