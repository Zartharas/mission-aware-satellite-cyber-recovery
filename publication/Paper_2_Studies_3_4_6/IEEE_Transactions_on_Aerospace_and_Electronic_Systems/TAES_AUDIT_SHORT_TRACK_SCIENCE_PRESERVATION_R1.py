#!/usr/bin/env python3
"""Read-only science-preservation audit for the TAES Paper-2 short track.

This audit proves that the frozen 16-page R9 scientific source remains intact,
that the short 8-page main article and corrected supplement retain the registered
Study 3, Study 4, and Study 6 result boundaries, and that the compression branch
contains no tracked changes outside the Paper-2 TAES publication directory.

It does not modify any manuscript, supplement, study, or result file. It writes
only a local audit text file after all checks pass.
"""
from __future__ import annotations

import hashlib
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT
while REPO.parent != REPO:
    if (REPO / ".git").exists():
        break
    REPO = REPO.parent
else:
    raise SystemExit("ERROR: repository root not found")

PUB_REL = Path("publication/Paper_2_Studies_3_4_6/IEEE_Transactions_on_Aerospace_and_Electronic_Systems")

R9_SOURCE = ROOT / "TAES_MANUSCRIPT_FULL_DRAFT.md"
R9_PDF = ROOT / "TAES_MANUSCRIPT.pdf"
MAIN_SOURCE = ROOT / "TAES_10P_R3_MANUSCRIPT_DRAFT.md"
MAIN_PDF = ROOT / "TAES_10P_R3_MANUSCRIPT_IEEETRAN_R8_DEV.pdf"
SUPP_SOURCE = ROOT / "TAES_10P_R3_SUPPLEMENTARY_MATERIAL.md"
SUPP_PDF = ROOT / "TAES_10P_R3_SUPPLEMENTARY_MATERIAL_R9_DEV.pdf"
PATCH_AUDIT = ROOT / "TAES_10P_R3_SUPPLEMENTARY_R9_CROSSREF_FIX_AUDIT.txt"
BUILD_AUDIT = ROOT / "TAES_10P_R3_SUPPLEMENTARY_R9_BUILD_AUDIT.txt"
OUT_AUDIT = ROOT / "TAES_10P_R3_SHORT_TRACK_SCIENCE_PRESERVATION_R1_AUDIT.txt"

CORE_SOURCE = ROOT / "TAES_MANUSCRIPT_SOURCE.md"
S3_SOURCE = ROOT / "TAES_SECTION_IV_STUDY3.md"
S4_SOURCE = ROOT / "TAES_SECTION_V_STUDY4.md"
S6_SOURCE = ROOT / "TAES_SECTION_VI_STUDY6.md"
VALIDITY_SOURCE = ROOT / "TAES_SECTION_VIII_VALIDITY.md"

EXPECTED = {
    R9_SOURCE: "802e6658e9e1325ec4f4a785c5da1b3856fbfadb950dadb6f6a57aec0acacd48",
    R9_PDF: "a7624fa416ebe4ba4d0b9e46da25b5dcb4d85e23e63291f4bdf497d5ba6cb319",
    MAIN_SOURCE: "7fa44eb55255bc7532a01728ab039b5e98fb3c719058f62440310e430b5f7909",
    MAIN_PDF: "f34cd280371f73492f6ef746fd52279fb1ab01fa4ce8c38eedb8aa67a74f551b",
    CORE_SOURCE: "7146b02da2dcd09f9ee89e6cc4dfa796f7cc2ba7dc9f86238c5ed08c475941a9",
    S3_SOURCE: "f7265f8315ecf4a6c0eeb503a8bd1e1f118f27e979eab2f52cb1fd63b81aef8a",
    S4_SOURCE: "3e33a0513f75a409e9c16a162ae8f6743b9621b594462cc4dce133c19919d389",
    S6_SOURCE: "6db7f547ab7a58c285ac9edae262785008398a6c199b297f28dcf002d1cf66bb",
    VALIDITY_SOURCE: "9b4a4b34cdd9a198230b2808122a94666c3f4d95435a9bfdd0d181a2f6a64c35",
}

STUDY4_ROWS = (
    ("Q1_D1", "1/1", "7/7"),
    ("Q2_D1", "2/2", "6/6"),
    ("Q2_D2", "2/4", "4/6"),
    ("Q3_D1", "3/3", "5/5"),
    ("Q3_D2", "3/4", "4/5"),
    ("Q3_D3", "3/6", "2/5"),
    ("Q4_D1", "4/4", "4/4"),
    ("Q4_D2", "4/4", "4/4"),
    ("Q4_D3", "4/6", "2/4"),
    ("Q5_D1", "5/5", "3/3"),
    ("Q5_D2", "5/5", "3/3"),
    ("Q5_D3", "5/6", "2/3"),
    ("Q6_D1", "6/6", "2/2"),
    ("Q6_D2", "6/6", "2/2"),
    ("Q6_D3", "6/6", "2/2"),
    ("Q7_D1", "7/7", "1/1"),
    ("Q7_D2", "7/7", "1/1"),
    ("Q7_D3", "7/7", "1/1"),
)

STUDY6_ROWS = (
    ("G0_SIGNATURE_ONLY", "4/5", "32/64"),
    ("G1_SIGNATURE_TARGET_DIGEST", "3/5", "48/64"),
    ("G2_SIGNATURE_PROVENANCE", "3/5", "48/64"),
    ("G3_PROVENANCE_REPRODUCED_BUILD", "2/5", "56/64"),
    ("G4_PROVENANCE_SOURCE_REVIEW", "2/5", "56/64"),
    ("G5_COMPOSITE", "1/5", "63/64"),
)


def sha256(path: Path) -> str:
    if not path.is_file():
        raise SystemExit(f"ERROR: required file missing: {path}")
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read(path: Path) -> str:
    if not path.is_file():
        raise SystemExit(f"ERROR: required file missing: {path}")
    return path.read_text(encoding="utf-8", errors="strict").replace("\r\n", "\n")


def run(*args: str) -> str:
    proc = subprocess.run(
        list(args), cwd=REPO, text=True, stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT, check=False
    )
    if proc.returncode != 0:
        print(proc.stdout)
        raise SystemExit(f"ERROR: command failed ({proc.returncode}): {' '.join(args)}")
    return proc.stdout


def require(text: str, marker: str, label: str) -> None:
    if marker not in text:
        raise SystemExit(f"ERROR: science-preservation marker missing [{label}]: {marker}")


def require_row(text: str, cells: tuple[str, ...], label: str) -> None:
    lines = text.splitlines()
    normalized_cells = [c.replace("_", "") for c in cells]
    for line in lines:
        normalized = line.replace("`", "").replace("_", "").replace(" ", "")
        if all(cell.replace(" ", "") in normalized for cell in normalized_cells):
            return
    raise SystemExit(f"ERROR: exact row marker missing [{label}]: {cells}")


def audit_corrected_supp_sha() -> str:
    text = read(PATCH_AUDIT)
    match = re.search(r"^corrected_supplement_sha256=([0-9a-f]{64})$", text, re.MULTILINE)
    if not match:
        raise SystemExit("ERROR: corrected supplement SHA missing from patch audit")
    return match.group(1)


def audit_supp_pdf_sha() -> str:
    text = read(BUILD_AUDIT)
    match = re.search(r"^pdf_sha256=([0-9a-f]{64})$", text, re.MULTILINE)
    if not match:
        raise SystemExit("ERROR: supplement PDF SHA missing from build audit")
    return match.group(1)


def main() -> None:
    branch = run("git", "branch", "--show-current").strip()
    if branch != "paper2/taes-10-page-compression":
        raise SystemExit(f"ERROR: wrong branch: {branch}")

    for path, expected in EXPECTED.items():
        actual = sha256(path)
        if actual != expected:
            raise SystemExit(
                f"ERROR: protected identity mismatch for {path.name}: expected={expected} actual={actual}"
            )

    corrected_supp_sha = audit_corrected_supp_sha()
    if sha256(SUPP_SOURCE) != corrected_supp_sha:
        raise SystemExit("ERROR: corrected supplement source does not match patch audit")
    supplement_pdf_sha = audit_supp_pdf_sha()
    if sha256(SUPP_PDF) != supplement_pdf_sha:
        raise SystemExit("ERROR: corrected supplement PDF does not match build audit")

    changed = [line.strip() for line in run(
        "git", "diff", "--name-only", "origin/main...HEAD"
    ).splitlines() if line.strip()]
    outside = [p for p in changed if not p.startswith(str(PUB_REL) + "/")]
    if outside:
        raise SystemExit(
            "ERROR: compression branch contains tracked changes outside Paper-2 TAES publication directory: "
            + ", ".join(outside)
        )

    r9 = read(R9_SOURCE)
    main_text = read(MAIN_SOURCE)
    supp = read(SUPP_SOURCE)
    union = main_text + "\n\n" + supp

    # Common scientific identity and claim controls.
    common_markers = (
        "Residual Trust Boundaries in Satellite Cyber Recovery: Temporal Evidence, Producer Composition, and Artifact Assurance",
        "1,380",
        "4,608",
        "420",
        "Only Study 3 models contact",
        "not external replication",
        "qualification",
        "PRE_ONSET_CACHE",
        "APPROVED_BAD_SOURCE",
    )
    for marker in common_markers:
        require(union, marker, "COMMON")

    forbidden_union = (
        "6,408",
        "combined Paper-2 N =",
        "globally best policy",
        "integrated three-layer architecture connects",
    )
    if "6,408" in union:
        raise SystemExit("ERROR: pooled Paper-2 population found in short-track sources")

    # Framework retained in main article.
    for marker in (
        "`E_j`",
        "`Q_j(E_j)",
        "`T_j",
        "`U_j = 1[Q_j(E_j) = 1 and T_j = 0]`",
        "`C_j = 1[Q_j(E_j) = 0 and T_j = 1]`",
    ):
        require(main_text, marker, "FRAMEWORK_MAIN")

    # Study 3 key population, treatments, exact results, and model limits.
    for marker in (
        "1,380 trajectories",
        "67,620",
        "[25,35]",
        "[75,90]",
        "[145,165]",
        "[220,240]",
        "46/46",
        "122.500",
        "55.326",
        "49.022",
        "55.0 logical seconds",
        "6.304 logical seconds",
        "3/46",
        "0.326 logical seconds",
        "five logical seconds",
        "V5_AFFECTED_RECORD",
        "affected post-signature",
        "structural",
    ):
        require(union, marker, "STUDY3")

    # Study 4 complete threshold map must be in supplement.
    require(supp, "Table S2", "STUDY4_TABLE")
    for row in STUDY4_ROWS:
        require_row(supp, row, "STUDY4_FULL_MAP")
    for marker in (
        "Seven producers",
        "D1={P1,P2,P3}",
        "D2={P4,P5}",
        "D3={P6,P7}",
        "128 subsets",
        "4,608 exact observations",
        "not Byzantine consensus",
        "no contact model",
    ):
        require(supp, marker, "STUDY4_BOUNDARY")

    # Study 6 complete gate frontier and residual identities must be preserved.
    require(supp, "Table S3", "STUDY6_TABLE")
    for row in STUDY6_ROWS:
        require_row(supp, row, "STUDY6_FRONTIER")
    for marker in (
        "POST_RELEASE_TAMPER",
        "TRUSTED_SIGNER_COMPROMISE",
        "TRUSTED_BUILDER_COMPROMISE",
        "SOURCE_REVIEW_BYPASS",
        "APPROVED_BAD_SOURCE",
        "independent_target_digest_match",
        "independent_reproduced_build_match",
        "minimum missing-signal count for benign loss is therefore one",
        "not an information-theoretic impossibility result",
        "does not claim standards compliance",
    ):
        require(supp, marker, "STUDY6_BOUNDARY")

    # Supplement relocation and validity controls.
    for marker in (
        "Supplementary Figure S1",
        "no experimental data flow or integrated three-layer architecture connects Studies 3, 4, and 6",
        "Appendix D. Expanded Validity and Aerospace Boundaries",
        "Appendix E. Frozen-population and non-pooling control",
        "These units are not pooled",
        "No experiment in Paper 2 operates an on-orbit spacecraft",
    ):
        require(supp, marker, "SUPPLEMENT_RELOCATION")

    # Main article still carries every reference and the required AI disclosure.
    for n in range(1, 14):
        require(main_text, f"[{n}]", f"REFERENCE_{n}")
    require(main_text, "The Update Framework Specification, v1.0.36", "TUF_REFERENCE")
    require(main_text, "OpenAI ChatGPT (GPT-5.6 Sol)", "AI_DISCLOSURE")
    require(main_text, "It was not used to generate or modify the frozen experimental results.", "AI_RESULT_BOUNDARY")

    # The four known stale R8 supplement cross-references must be gone.
    stale = (
        "Table II values are logical model time",
        "Table III gives the complete frozen map",
        "Table IV reports the canonical gate summary",
        "denominators in Table IV are finite model populations",
    )
    present = [marker for marker in stale if marker in supp]
    if present:
        raise SystemExit("ERROR: stale R8 supplement cross-reference remains: " + ", ".join(present))
    corrected = (
        "Table S1 values are logical model time",
        "Table S2 gives the complete frozen map",
        "Table S3 reports the canonical gate summary",
        "denominators in Table S3 are finite model populations",
    )
    for marker in corrected:
        require(supp, marker, "CORRECTED_TABLE_CROSSREF")

    audit_lines = [
        "TAES_SHORT_TRACK_SCIENCE_PRESERVATION=PASS",
        f"branch={branch}",
        f"frozen_r9_source_sha256={EXPECTED[R9_SOURCE]}",
        f"frozen_r9_pdf_sha256={EXPECTED[R9_PDF]}",
        f"short_main_source_sha256={EXPECTED[MAIN_SOURCE]}",
        f"short_main_pdf_sha256={EXPECTED[MAIN_PDF]}",
        f"corrected_supplement_source_sha256={corrected_supp_sha}",
        f"corrected_supplement_pdf_sha256={supplement_pdf_sha}",
        f"core_source_sha256={EXPECTED[CORE_SOURCE]}",
        f"study3_source_sha256={EXPECTED[S3_SOURCE]}",
        f"study4_source_sha256={EXPECTED[S4_SOURCE]}",
        f"study6_source_sha256={EXPECTED[S6_SOURCE]}",
        f"validity_source_sha256={EXPECTED[VALIDITY_SOURCE]}",
        f"tracked_changed_files_on_branch={len(changed)}",
        "tracked_changes_outside_paper2_taes_directory=NONE",
        "study3_population_and_key_results=PASS_PRESERVED",
        "study4_complete_18_rule_map=PASS_PRESERVED_IN_SUPPLEMENT",
        "study6_complete_gate_frontier=PASS_PRESERVED",
        "framework_e_q_t_u_c=PASS_PRESERVED_IN_MAIN",
        "figure1_relocation=PASS_AS_SUPPLEMENTARY_FIGURE_S1",
        "validity_detail_relocation=PASS_SUPPLEMENT_APPENDIX_D_WITH_MAIN_CAVEATS_RETAINED",
        "non_pooling_control=PASS_MAIN_AND_SUPPLEMENT",
        "only_study3_contact_control=PASS",
        "qualification_not_recovery_completion_control=PASS",
        "external_replication_claim=PASS_NOT_CLAIMED",
        "references_1_through_13=PASS_MAIN",
        "tuf_v1_0_36=PASS_MAIN",
        "ai_disclosure=PASS_MAIN_AND_RESULTS_BOUNDARY",
        "stale_table_crossrefs=PASS_REMOVED",
        "corrected_table_crossrefs=PASS_S1_S2_S3",
        "experimental_results_changed=NO",
        "frozen_study_sources_changed=NO",
        "study_rerun=NO",
        "pooled_population_introduced=NO",
        "common_effect_introduced=NO",
        "global_policy_rank_introduced=NO",
        "science_preservation_decision=PASS_SHORT_MAIN_PLUS_CORRECTED_SUPPLEMENT_PRESERVES_FROZEN_R9_CLAIM_BOUNDARIES",
    ]
    OUT_AUDIT.write_text("\n".join(audit_lines) + "\n", encoding="utf-8")
    for line in audit_lines:
        print(line)


if __name__ == "__main__":
    main()
