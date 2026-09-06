#!/usr/bin/env python3
"""Apply the audited IEEE bibliography corrections to TAES Paper 2.

This helper changes citation structure and bibliographic metadata only. It does
not rerun studies, alter frozen results, or modify publisher-facing PDFs.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent

INTRO = ROOT / "TAES_SECTION_I_INTRODUCTION.md"
CORE = ROOT / "TAES_MANUSCRIPT_SOURCE.md"
STUDY6 = ROOT / "TAES_SECTION_VI_STUDY6.md"
LEDGER = ROOT / "TAES_LITERATURE_SOURCE_LEDGER.md"
ASSEMBLER = ROOT / "TAES_ASSEMBLE_MANUSCRIPT.py"


def read(path: Path) -> str:
    if not path.is_file():
        raise SystemExit(f"ERROR: missing required file: {path}")
    return path.read_text(encoding="utf-8").replace("\r\n", "\n")


def write(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count == 1:
        return text.replace(old, new, 1)
    if count == 0 and new in text:
        return text
    raise SystemExit(f"ERROR: expected exactly one old marker for {label}; found {count}")


FINAL_REFERENCES = """## References Used in Sections II and III

[1] R. Thummala, E. Rice, and G. Falco, \"Why is space cybersecurity unique?,\" in Proc. 4th Workshop Security Space Satellite Syst. (SpaceSec), San Diego, CA, USA, Feb. 23, 2026, doi: 10.14722/spacesec.2026.23055.

[2] J. Vanlyssel, G.-C. Roman, K. Cook, S. Rahaman, and A. Anwar, \"Trust without boundaries: An architectural analysis of satellite flight software,\" 2026, arXiv:2608.14532.

[3] J. Curbo and G. Falco, \"Testable cyber requirements for space flight software,\" in Proc. 2025 IEEE Aerosp. Conf., Big Sky, MT, USA, 2025, pp. 1-20, doi: 10.1109/AERO63441.2025.11068629.

[4] The Aerospace Corporation. \"Space Attack Research & Tactic Analysis (SPARTA).\" Accessed: Sep. 6, 2026. [Online]. Available: https://sparta.aerospace.org/

[5] H. Birkholz, D. Thaler, M. Richardson, N. Smith, and W. Pan, \"Remote ATtestation procedureS (RATS) architecture,\" RFC 9334, Jan. 2023, doi: 10.17487/RFC9334.

[6] Y. Deshpande, J. Zhang, H. Labiod, and H. Birkholz, \"Remote attestation with multiple verifiers,\" IETF, Internet-Draft draft-ietf-rats-multi-verifier-00, May 2026, work in progress. [Online]. Available: https://datatracker.ietf.org/doc/draft-ietf-rats-multi-verifier/

[7] D. Malkhi and M. Reiter, \"Byzantine quorum systems,\" Distrib. Comput., vol. 11, no. 4, pp. 203-213, Oct. 1998, doi: 10.1007/s004460050050.

[8] O. Alpos, C. Cachin, B. Tackmann, and L. Zanolini, \"Asymmetric distributed trust,\" Distrib. Comput., vol. 37, no. 3, pp. 247-277, May 2024, doi: 10.1007/s00446-024-00469-1.

[9] F. Rezabek, D. Malkhi, and A. Yahalom, \"Space Fabric: A satellite-enhanced trusted execution architecture,\" 2026, arXiv:2603.23745.

[10] S. Torres-Arias, H. Afzali, T. K. Kuppusamy, R. Curtmola, and J. Cappos, \"in-toto: Providing farm-to-table guarantees for bits and bytes,\" in Proc. 28th USENIX Security Symp. (USENIX Security 19), Santa Clara, CA, USA, Aug. 2019, pp. 1393-1410.

[11] The Update Framework. \"The Update Framework Specification, v1.0.33.\" Accessed: Sep. 6, 2026. [Online]. Available: https://theupdateframework.io/spec/

[12] SLSA. \"Source: Requirements for producing source,\" SLSA Specification, v1.2. Accessed: Sep. 6, 2026. [Online]. Available: https://slsa.dev/spec/v1.2/source-requirements

[13] SLSA. \"Threats & mitigations,\" SLSA Specification, v1.2. Accessed: Sep. 6, 2026. [Online]. Available: https://slsa.dev/spec/v1.2/threats
"""


def patch_intro() -> None:
    text = read(INTRO)
    old = (
        "Software-supply-chain mechanisms use signatures, hashes, provenance, controlled build processes, "
        "reproducibility, review, and release metadata to establish properties of software artifacts "
        "[10]-[12]. The present work does not introduce these mechanisms."
    )
    new = (
        "Software-supply-chain mechanisms use signatures, hashes, provenance, controlled build processes, "
        "reproducibility, review, and release metadata to establish properties of software artifacts "
        "[10], [11], [12]. SLSA also documents threat boundaries for intentionally malicious producers [13]. "
        "The present work does not introduce these mechanisms."
    )
    text = replace_once(text, old, new, "Introduction SLSA/citation-range sentence")
    write(INTRO, text)


def patch_core() -> None:
    text = read(CORE)
    text = replace_once(
        text,
        "SLSA explicitly states that an intentionally malicious software producer cannot be directly mitigated by SLSA controls alone and that consumers need some independent basis for trusting the producer [12].",
        "SLSA explicitly states that an intentionally malicious software producer cannot be directly mitigated by SLSA controls alone and that consumers need some independent basis for trusting the producer [13].",
        "Related Work malicious-producer citation",
    )
    text = replace_once(
        text,
        "Space cybersecurity already treats communication gaps, autonomy, continuity, trusted baselines, and internal trust boundaries as important concerns [1]-[4].",
        "Space cybersecurity already treats communication gaps, autonomy, continuity, trusted baselines, and internal trust boundaries as important concerns [1], [2], [3], [4].",
        "Related Work space-source range",
    )
    text = replace_once(
        text,
        "Software-supply-chain research already provides provenance, signed update metadata, target binding, reproducible-process concepts, and explicit limits on what those controls can establish about producer intent [10]-[12].",
        "Software-supply-chain research already provides provenance, signed update metadata, target binding, reproducible-process concepts, and explicit limits on what those controls can establish about producer intent [10], [11], [12], [13].",
        "Related Work supply-chain source range",
    )

    marker = "## References Used in Sections II and III\n"
    if marker not in text:
        raise SystemExit("ERROR: references marker missing from TAES_MANUSCRIPT_SOURCE.md")
    prefix = text.split(marker, 1)[0]
    text = prefix + FINAL_REFERENCES
    write(CORE, text)


def patch_study6() -> None:
    text = read(STUDY6)
    text = replace_once(
        text,
        "SLSA v1.2 explicitly recognizes that an intentionally malicious software producer cannot be directly mitigated through SLSA controls and that the consumer must establish a basis for trusting the producer [12].",
        "SLSA v1.2 explicitly recognizes that an intentionally malicious software producer cannot be directly mitigated through SLSA controls and that the consumer must establish a basis for trusting the producer [13].",
        "Study 6 malicious-producer citation",
    )
    text = replace_once(
        text,
        "SLSA defines source and build assurance levels and threat boundaries [12].",
        "SLSA defines source assurance requirements and documents supply-chain threat boundaries [12], [13].",
        "Study 6 source/threat citation split",
    )
    write(STUDY6, text)


def patch_ledger() -> None:
    text = read(LEDGER)

    start = text.find("### [11] The Update Framework")
    end = text.find("## Current-context source not required for the core reference list")
    if start < 0 or end < 0 or end <= start:
        raise SystemExit("ERROR: unable to locate TUF/SLSA ledger section")

    replacement = """### [11] The Update Framework

The Update Framework, \"The Update Framework Specification, v1.0.33,\" latest stable specification.

Official specification page: https://theupdateframework.io/spec/

Live-verified status and support:
- the official specification page identifies v1.0.33 as the latest stable specification as of 2026-09-06;
- signed metadata, trusted roles, target hashes, thresholds, versions, and expiration are established update-security mechanisms.

Novelty implication:
- Study 6 does not introduce target-hash binding, threshold-signature concepts, or trusted update roles.

### [12] SLSA v1.2 Source Requirements

SLSA, \"Source: Requirements for producing source,\" approved v1.2 specification.

Official source: https://slsa.dev/spec/v1.2/source-requirements

Live-verified support:
- the page is marked Approved;
- the Source track defines increasing levels of trustworthiness and completeness in how source revisions are created;
- source provenance and controlled review are established assurance mechanisms.

Novelty implication:
- Study 6 does not introduce source provenance or source-process assurance requirements.

### [13] SLSA v1.2 Threats & Mitigations

SLSA, \"Threats & mitigations,\" approved v1.2 specification.

Official source: https://slsa.dev/spec/v1.2/threats

Live-verified support:
- the page is marked Approved;
- the threat model explicitly states that intentionally malicious software produced by the producer cannot be directly mitigated through SLSA controls;
- consumers must establish some independent basis for trusting the producer.

Novelty implication:
- Study 6's `APPROVED_BAD_SOURCE` state must not be presented as the discovery that provenance or process conformance can fail to establish benevolent source intent.

"""

    text = text[:start] + replacement + text[end:]
    write(LEDGER, text)


def patch_assembler() -> None:
    text = read(ASSEMBLER)
    marker = "    # Guard only genuinely affirmative superiority claims. Explicit limitation\n"
    guard = (
        "    # Current IEEE reference style writes numeric citation ranges out individually.\n"
        "    if re.search(r\"\\[\\d+\\]\\s*-\\s*\\[\\d+\\]\", assembled):\n"
        "        raise SystemExit(\"ERROR: dash-form numeric IEEE citation range detected\")\n\n"
    )
    if guard not in text:
        if marker not in text:
            raise SystemExit("ERROR: assembler insertion marker missing")
        text = text.replace(marker, guard + marker, 1)
    write(ASSEMBLER, text)


def verify() -> None:
    intro = read(INTRO)
    core = read(CORE)
    study6 = read(STUDY6)
    ledger = read(LEDGER)
    assembler = read(ASSEMBLER)

    joined = "\n".join([intro, core, study6])
    if re.search(r"\[\d+\]\s*-\s*\[\d+\]", joined):
        raise SystemExit("ERROR: dash-form citation range remains in manuscript components")
    if "[13]" not in intro or "[13]" not in core or "[13]" not in study6:
        raise SystemExit("ERROR: SLSA threat reference [13] was not propagated")
    if core.count("\n[13] ") != 1:
        raise SystemExit("ERROR: final bibliography does not contain exactly one [13] entry")
    if "v1.0.33" not in core or "v1.0.33" not in ledger:
        raise SystemExit("ERROR: verified TUF version was not propagated")
    if "vol. 37, no. 3, pp. 247-277, May 2024" not in core:
        raise SystemExit("ERROR: corrected Alpos et al. issue/month metadata missing")
    if "dash-form numeric IEEE citation range detected" not in assembler:
        raise SystemExit("ERROR: assembler citation-range guard missing")


if __name__ == "__main__":
    patch_intro()
    patch_core()
    patch_study6()
    patch_ledger()
    patch_assembler()
    verify()
    print("TAES_BIBLIOGRAPHY_FIXES=PASS")
    print("reference_count=13")
    print("slsa_source_reference=12")
    print("slsa_threat_reference=13")
    print("tuf_stable_version=v1.0.33")
    print("alpos_issue_month=no.3_May_2024")
    print("NOTE: Re-run TAES_ASSEMBLE_MANUSCRIPT.py after this helper.")
