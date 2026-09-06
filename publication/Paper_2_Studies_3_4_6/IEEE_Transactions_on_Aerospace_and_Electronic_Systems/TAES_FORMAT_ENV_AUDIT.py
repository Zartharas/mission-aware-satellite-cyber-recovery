#!/usr/bin/env python3
"""Read-only local environment audit for the TAES two-column formatting gate.

This script does not modify manuscript files or generate a publisher-facing PDF.
It verifies the exact canonical manuscript/Figure-1 hashes and checks whether the
local tools required for the controlled IEEEtran formatting path are available.
"""

from __future__ import annotations

import hashlib
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent

MANUSCRIPT = ROOT / "TAES_MANUSCRIPT_FULL_DRAFT.md"
FIGURE_PDF = ROOT / "TAES_FIGURE1_RESIDUAL_BOUNDARIES.pdf"
FIGURE_PNG = ROOT / "TAES_FIGURE1_RESIDUAL_BOUNDARIES.png"

EXPECTED = {
    MANUSCRIPT.name: "dde7d9c6ab4efb1c6f567937dd1c28c904baeb713dc960b716eae1b15ef5e709",
    FIGURE_PDF.name: "4872707261c8a8b6b747e76b9166b4ad7ae426e43d7bd9ffe272e4c5ea6f4ff8",
    FIGURE_PNG.name: "7d22964bdae052b35b4680e1b09f3209f1c99bb1d157a0f995dcd2a6445e6698",
}

REQUIRED_COMMANDS = [
    "pandoc",
    "pdflatex",
    "latexmk",
    "kpsewhich",
    "pdfinfo",
    "pdffonts",
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def run_capture(args: list[str]) -> str:
    try:
        completed = subprocess.run(
            args,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=20,
        )
    except Exception as exc:
        return f"ERROR:{type(exc).__name__}:{exc}"
    line = completed.stdout.strip().splitlines()
    return line[0] if line else f"rc={completed.returncode}"


def main() -> None:
    problems: list[str] = []

    print("TAES_FORMAT_ENV_AUDIT=BEGIN")

    for path in (MANUSCRIPT, FIGURE_PDF, FIGURE_PNG):
        if not path.is_file():
            problems.append(f"missing_file:{path.name}")
            print(f"{path.name}_status=MISSING")
            continue
        actual = sha256(path)
        expected = EXPECTED[path.name]
        status = "PASS" if actual == expected else "FAIL"
        print(f"{path.name}_sha256={actual}")
        print(f"{path.name}_hash_status={status}")
        if status != "PASS":
            problems.append(f"hash_mismatch:{path.name}")

    print("TOOLCHAIN_BEGIN")
    for command in REQUIRED_COMMANDS:
        resolved = shutil.which(command)
        if not resolved:
            print(f"{command}=MISSING")
            problems.append(f"missing_command:{command}")
            continue
        print(f"{command}={resolved}")

    if shutil.which("pandoc"):
        print(f"pandoc_version={run_capture(['pandoc', '--version'])}")
    if shutil.which("pdflatex"):
        print(f"pdflatex_version={run_capture(['pdflatex', '--version'])}")
    if shutil.which("latexmk"):
        print(f"latexmk_version={run_capture(['latexmk', '-v'])}")
    if shutil.which("pdfinfo"):
        print(f"pdfinfo_version={run_capture(['pdfinfo', '-v'])}")
    print("TOOLCHAIN_END")

    ieee_cls = ""
    if shutil.which("kpsewhich"):
        try:
            completed = subprocess.run(
                ["kpsewhich", "IEEEtran.cls"],
                check=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=20,
            )
            ieee_cls = completed.stdout.strip()
        except Exception:
            ieee_cls = ""

    if ieee_cls:
        print(f"IEEEtran_cls={ieee_cls}")
        print("IEEEtran_cls_status=PASS")
    else:
        print("IEEEtran_cls_status=FAIL")
        problems.append("IEEEtran_cls_unresolved")

    if problems:
        print("TAES_FORMAT_ENV_AUDIT=FAIL")
        for problem in problems:
            print(f"problem={problem}")
        raise SystemExit(1)

    print("canonical_manuscript_binding=PASS")
    print("canonical_figure1_binding=PASS")
    print("TAES_FORMAT_ENV_AUDIT=PASS")
    print("next_gate=DETERMINISTIC_IEEEtran_TWO_COLUMN_BUILD")
    print("NOTE: This audit is read-only and does not create or modify manuscript artifacts.")


if __name__ == "__main__":
    main()
