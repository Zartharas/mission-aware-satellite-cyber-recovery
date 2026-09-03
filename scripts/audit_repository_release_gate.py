#!/usr/bin/env python3
"""Fail-closed repository sanity audit for journal/submission and frozen-study state.

Historical work-package and phase documents may retain stage-local status text because
that text is provenance. Current state is governed by the active tracker, the existing
Study-1/Study-2 manuscript assembly, Study-2 canonical freeze/provenance, the Study-8
technical close/results freeze, and the target submission package checked here.

This audit never starts NOS3/cFS, executes a campaign trial, consumes a campaign seed,
or mutates scientific evidence.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
import subprocess
import sys
import tomllib
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import unquote

import yaml

ROOT = Path(__file__).resolve().parents[1]
ERRORS: list[str] = []
CHECKS: list[str] = []

# Study-1 frozen/public identities.
S1_VERSION_DOI = "10.5281/zenodo.22181540"
S1_CONCEPT_DOI = "10.5281/zenodo.22181539"
S1_MEMBERSHIP_SHA = "a2bf0c8f352f4386e74a500d97ea8f73e0c39d03bfe10ac0ebcf02470af9f70e"
S1_LEDGER_SHA = "92893a2fd8746f410bffd4dca5101bc3f533ada2ff82f98681788cf0c24ce6fd"
S1_CAMPAIGN_TREE_SHA = "ad1e127b4431b6b334955129fcba82f76b18e5b43585395ac8c37300cac087b1"
S1_REPRO_COMMIT = "99892bd9bb0828bdb3d0a28caf40dbc18fcbc4dc"

# Study-2 canonical identities.
S2_EXPERIMENT_ID = "S2-AEATR-001"
S2_STATUS = "PRESPECIFIED_ANALYSIS_RESULTS_FROZEN_CANONICAL"
S2_VALID = 3872
S2_INVALID = 0
S2_CELLS = 85
S2_PRIMARY = 162
S2_SECONDARY = 432
S2_PHASE6_ZIP_SHA = "195860bd44b38ccf170f02cb1cb392583217296d08640c99b18b52286403e133"
S2_OBSERVATIONS_SHA = "8dcc850c561d7e3c0bf7478263b534cae83cbbb55183c313e879dd7d61127854"
S2_TRIAL_MANIFEST_SHA = "190612473717b7768ceccb4596a20d90cd7d532bf7581330ce94d609cb752e67"
S2_ANALYZER_SHA = "351039f0d6d79eb605c7dc027a5427da862b0f544815f862a85bc997df56c8bd"
S2_RESULT_ZIP_SHA = "0136123a53d150437fefc8ace342af63b11d980cf8cab32ef7a4f03b78267417"
S2_AUDITOR_SHA = "3e738e2c27d621073a8c1bba49044df3fc83d099abdd244894537f4c4b22142d"
S2_RESULTS_MERGE = "49c62cbed3fb8fc318e44d696faba1854ed6c21a"
S2_CANONICAL_CLOSEOUT = "2bd3fb34ca709127e45ea9bffa8f516846d6c4b5"
S2_RESULT_ARCHIVE = (
    "study2/evidence/phase7/archive/"
    "study2-phase7-results-60f64327c45efda24cbb5b342f9d0eac908e1934.zip"
)

# Study-8 canonical/technical-close identities.
S8_EXPERIMENT_ID = "S8-PQC-ICR-001"
S8_STATUS = "TECHNICALLY_CLOSED_PUBLICATION_INTEGRATION_NOT_STARTED"
S8_ROWS = 3456
S8_CANONICAL_SHA = "cfc65b6663be4e9f17a00ed102730f8642efcbbd844045acce032ff09a0bcabf"
S8_FINDINGS_SHA = "26a8ac4d1039917323e75a294775dd14a2b563adb12a5d2fcdb47ce8f15c992e"
S8_INTERPRETATION_SHA = "620827f83fb566ff6ceae1b66c8f51f61ef8e5bbdabbb1c4b5a48b5187a82413"
S8_SCIENCE_MERGE = "63106778559c3127a7d6e8765d52939b73a3f35b"
S8_POST_MERGE_CI = 33761681328

PROVENANCE_COMMITS = (
    # Study 1.
    "aae2239753119c92e7633db3b6c73aee94c7b6dd",
    "97074d0cdc4261de02bc6f618e891a88f45f9cfc",
    "7ed85d5cbeca8f903b3468bc6ccc1c56e29c2446",
    "18596ea32c696b65bbdaf5676b1157d633ed59b5",
    S1_REPRO_COMMIT,
    # Study 2.
    "18207460fc5d419ad6a940f00db2df8610a5e5a0",
    S2_RESULTS_MERGE,
    S2_CANONICAL_CLOSEOUT,
    # Study 8.
    S8_SCIENCE_MERGE,
)

ACTIVE_MARKDOWN = (
    "README.md",
    "publication/README.md",
    "scripts/README.md",
    "docs/REPRODUCIBILITY_GUIDE.md",
    "publication/manuscript/MANUSCRIPT-ASSEMBLY.md",
    "publication/manuscript/00-title-abstract.md",
    "publication/manuscript/01-introduction.md",
    "publication/manuscript/02-background-and-related-work.md",
    "publication/manuscript/03-methods.md",
    "publication/manuscript/03-study2-methods-extension.md",
    "publication/manuscript/04-results.md",
    "publication/manuscript/04-study2-results-extension.md",
    "publication/manuscript/05-discussion.md",
    "publication/manuscript/06-conclusion.md",
    "publication/manuscript/07-declarations-and-availability.md",
    "study2/README.md",
    "study2/docs/PHASE7_RESULTS_FREEZE.md",
    "study8/README.md",
    "study8/docs/PHASE8_7_TECHNICAL_CLOSE.md",
    "publication/submission/computers-and-security/README.md",
    "publication/submission/computers-and-security/submission-checklist.md",
    "publication/submission/computers-and-security/title-page.md",
    "publication/submission/computers-and-security/ai-declaration.md",
    "publication/submission/computers-and-security/cover-letter.md",
    "publication/submission/computers-and-security/highlights.md",
    "publication/submission/computers-and-security/concise-abstract-candidate.md",
    "publication/submission/computers-and-security/venue-fit.md",
)

RECOMMENDED_SCRIPTS = (
    "verify_environment.sh",
    "validate_experiment_schema.py",
    "audit_repository_release_gate.py",
    "prepare_nos3_candidate.sh",
    "prepare_42_candidate.sh",
    "build_nominal_nos3.sh",
    "run_nominal_runtime_preflight.sh",
    "cleanup_nominal_runtime.sh",
    "verify_nos3_source_lock.sh",
    "verify_testbed_runtime.sh",
)

DISPLAY_FILES = (
    # Study-1 displays.
    "publication/tables/table-r1-proposition-summary.csv",
    "publication/tables/table-r2-p2-contact-effects.csv",
    "publication/tables/table-r3-p3-p4-evidence-pathways.csv",
    "publication/tables/table-r4-p5-pareto-status.csv",
    "publication/tables/table-r5-cybersecurity-positioning.csv",
    "publication/tables/table-r6-security-property-mapping.csv",
    "publication/tables/table-s1-execution-provenance-sensitivity.csv",
    "publication/figures/figure-r1-p2-contact-effects.svg",
    "publication/figures/figure-r2-p3-trusted-recovery.svg",
    "publication/figures/figure-r3-p4-selection-pathway.svg",
    "publication/figures/figure-r4-p5-pareto-status.svg",
    # Study-2 journal displays.
    "publication/tables/table-r7-study2-prespecified-findings.csv",
    "publication/tables/table-s2-study2-secondary-holm.csv",
    "publication/manuscript/study2-claim-traceability.csv",
)

MANUSCRIPT_COMPONENTS = (
    "publication/manuscript/00-title-abstract.md",
    "publication/manuscript/01-introduction.md",
    "publication/manuscript/02-background-and-related-work.md",
    "publication/manuscript/03-methods.md",
    "publication/manuscript/03-study2-methods-extension.md",
    "publication/manuscript/04-results.md",
    "publication/manuscript/04-study2-results-extension.md",
    "publication/manuscript/05-discussion.md",
    "publication/manuscript/06-conclusion.md",
    "publication/manuscript/07-declarations-and-availability.md",
)


def ok(message: str) -> None:
    CHECKS.append(message)
    print(f"[OK] {message}")


def fail(message: str) -> None:
    ERRORS.append(message)
    print(f"[FAIL] {message}", file=sys.stderr)


def read(rel: str) -> str:
    path = ROOT / rel
    if not path.is_file():
        fail(f"required file missing: {rel}")
        return ""
    return path.read_text(encoding="utf-8")


def require_text(
    rel: str,
    required: tuple[str, ...] = (),
    forbidden: tuple[str, ...] = (),
) -> None:
    text = read(rel)
    if not text:
        return
    before = len(ERRORS)
    for token in required:
        if token not in text:
            fail(f"{rel}: required current-state text missing: {token!r}")
    for token in forbidden:
        if token in text:
            fail(f"{rel}: stale/current-state text still present: {token!r}")
    if len(ERRORS) == before:
        ok(f"current-state wording checked: {rel}")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_json() -> None:
    files = sorted(p for p in ROOT.rglob("*.json") if ".git" not in p.parts)
    before = len(ERRORS)
    for path in files:
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001
            fail(f"invalid JSON syntax: {path.relative_to(ROOT)}: {exc}")
    if len(ERRORS) == before:
        ok(f"JSON syntax parsed for {len(files)} tracked files")


def validate_yaml() -> None:
    candidates: list[Path] = []
    for pattern in ("*.yml", "*.yaml", "*.cff"):
        candidates.extend(ROOT.rglob(pattern))
    files = sorted({p for p in candidates if ".git" not in p.parts})
    before = len(ERRORS)
    for path in files:
        try:
            yaml.safe_load(path.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001
            fail(f"invalid YAML/CFF syntax: {path.relative_to(ROOT)}: {exc}")
    if len(ERRORS) == before:
        ok(f"YAML/CFF syntax parsed for {len(files)} tracked files")


def validate_toml() -> None:
    files = sorted(p for p in ROOT.rglob("*.toml") if ".git" not in p.parts)
    before = len(ERRORS)
    for path in files:
        try:
            tomllib.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001
            fail(f"invalid TOML syntax: {path.relative_to(ROOT)}: {exc}")
    if len(ERRORS) == before:
        ok(f"TOML syntax parsed for {len(files)} tracked files")


def validate_csv() -> None:
    files = sorted(p for p in ROOT.rglob("*.csv") if ".git" not in p.parts)
    before = len(ERRORS)
    for path in files:
        try:
            with path.open("r", encoding="utf-8-sig", newline="") as handle:
                rows = list(csv.reader(handle))
        except Exception as exc:  # noqa: BLE001
            fail(f"CSV parse failure: {path.relative_to(ROOT)}: {exc}")
            continue
        if not rows:
            fail(f"empty CSV: {path.relative_to(ROOT)}")
            continue
        width = len(rows[0])
        if width == 0:
            fail(f"CSV has empty header: {path.relative_to(ROOT)}")
            continue
        for idx, row in enumerate(rows[1:], start=2):
            if len(row) != width:
                fail(
                    f"ragged CSV: {path.relative_to(ROOT)} line {idx}: "
                    f"expected {width} fields, found {len(row)}"
                )
    if len(ERRORS) == before:
        ok(f"CSV structure checked for {len(files)} tracked files")


def validate_xml_svg() -> None:
    candidates = list(ROOT.rglob("*.xml")) + list(ROOT.rglob("*.svg"))
    files = sorted({p for p in candidates if ".git" not in p.parts})
    before = len(ERRORS)
    for path in files:
        try:
            ET.parse(path)
        except Exception as exc:  # noqa: BLE001
            fail(f"invalid XML/SVG syntax: {path.relative_to(ROOT)}: {exc}")
    if len(ERRORS) == before:
        ok(f"XML/SVG syntax parsed for {len(files)} tracked files")


def validate_markdown_links() -> None:
    pattern = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
    checked = 0
    before = len(ERRORS)
    for rel in ACTIVE_MARKDOWN:
        text = read(rel)
        if not text:
            continue
        base = (ROOT / rel).parent
        for raw_target in pattern.findall(text):
            target = raw_target.strip()
            if not target or target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            if target.startswith("<") and target.endswith(">"):
                target = target[1:-1]
            target = re.sub(r"\s+[\"'].*[\"']$", "", target)
            target = unquote(target.split("#", 1)[0])
            if not target:
                continue
            candidate = (base / target).resolve()
            try:
                candidate.relative_to(ROOT.resolve())
            except ValueError:
                fail(f"markdown link escapes repository: {rel}: {raw_target}")
                continue
            checked += 1
            if not candidate.exists():
                fail(f"broken local markdown link: {rel}: {raw_target}")
    if len(ERRORS) == before:
        ok(f"active-document local links checked: {checked}")


def validate_script_guide() -> None:
    before = len(ERRORS)
    for name in RECOMMENDED_SCRIPTS:
        if not (ROOT / "scripts" / name).is_file():
            fail(f"scripts/README.md recommended entry point missing: scripts/{name}")
    if len(ERRORS) == before:
        ok(f"recommended script entry points exist: {len(RECOMMENDED_SCRIPTS)}")


def validate_publication_displays() -> None:
    before = len(ERRORS)
    for rel in DISPLAY_FILES:
        if not (ROOT / rel).is_file():
            fail(f"publication display missing: {rel}")
    if len(ERRORS) == before:
        ok(f"publication display/control files exist: {len(DISPLAY_FILES)}")


def validate_bibliography_and_citations() -> None:
    bib = read("references/references.bib")
    key_pattern = re.compile(r"(?m)^\s*@\w+\s*\{\s*([^,\s]+)\s*,")
    keys = key_pattern.findall(bib)
    if not keys:
        fail("references/references.bib contains no parseable BibTeX keys")
        return
    duplicates = sorted({key for key in keys if keys.count(key) > 1})
    if duplicates:
        fail(f"duplicate BibTeX keys: {duplicates}")
    key_set = set(keys)
    cited: set[str] = set()
    cite_pattern = re.compile(r"@([A-Za-z0-9_:.+\-/]+)")
    for rel in MANUSCRIPT_COMPONENTS:
        cited.update(cite_pattern.findall(read(rel)))
    missing = sorted(cited - key_set)
    if missing:
        fail(f"manuscript citation keys absent from references.bib: {missing}")
    if not duplicates and not missing:
        ok(
            "bibliography/citation keys resolved: "
            f"{len(key_set)} bibliography keys, {len(cited)} cited keys"
        )


def validate_submission_inputs() -> None:
    path = ROOT / "publication/manuscript/submission-inputs.csv"
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = {row["input_id"]: row for row in csv.DictReader(handle)}
    expected = {
        "S05": "RESOLVED",
        "S06": "RESOLVED",
        "S09": "AUTHOR_APPROVED_POLICY_RECHECK_REQUIRED",
        "S13": "RESOLVED",
        "S14": "RESOLVED",
    }
    before = len(ERRORS)
    for key, status in expected.items():
        actual = rows.get(key, {}).get("status")
        if actual != status:
            fail(f"submission-inputs.csv {key}: expected {status}, found {actual}")
    s12 = rows.get("S12", {})
    if s12.get("status") != "USER_OR_INSTITUTION_INPUT_IF_REQUIRED":
        fail("S12 IRB/HRPP field must remain conditional; do not invent an identifier")
    if len(ERRORS) == before:
        ok("author attestations and conditional IRB/HRPP state checked")


def validate_study1_identities() -> None:
    declarations = read("publication/manuscript/07-declarations-and-availability.md")
    tracker = read("tracker/RESEARCH_TRACKER.md")
    before = len(ERRORS)
    for token, label in (
        (S1_VERSION_DOI, "Study-1 Zenodo version DOI"),
        (S1_CONCEPT_DOI, "Study-1 Zenodo concept DOI"),
        (S1_MEMBERSHIP_SHA, "Study-1 720-membership SHA-256"),
        (S1_LEDGER_SHA, "Study-1 attempt-history ledger SHA-256"),
        (S1_CAMPAIGN_TREE_SHA, "Study-1 campaign-tree SHA-256"),
    ):
        if token not in declarations:
            fail(f"declarations missing {label}: {token}")
        if token not in tracker:
            fail(f"research tracker missing {label}: {token}")
    if S1_REPRO_COMMIT not in declarations:
        fail("Code Availability no longer records the frozen Study-1 reproduction snapshot")

    citation = yaml.safe_load(read("CITATION.cff"))
    preferred = citation.get("preferred-citation", {}) if isinstance(citation, dict) else {}
    if preferred.get("doi") != S1_VERSION_DOI:
        fail(f"CITATION.cff Study-1 preferred DOI drift: {preferred.get('doi')!r}")
    if preferred.get("version") != "1.0.0":
        fail(f"CITATION.cff preferred version drift: {preferred.get('version')!r}")
    if len(ERRORS) == before:
        ok("Study-1 DOI/hash/code-snapshot identities cross-checked")


def validate_study2_identities() -> None:
    freeze = json.loads(read("study2/PHASE7_RESULTS_FREEZE.json"))
    provenance = json.loads(read("study2/PHASE7_PROVENANCE.json"))
    declarations = read("publication/manuscript/07-declarations-and-availability.md")
    tracker = read("tracker/RESEARCH_TRACKER.md")
    before = len(ERRORS)

    expected_freeze = {
        "experiment_id": S2_EXPERIMENT_ID,
        "status": S2_STATUS,
        "canonical_merge_commit": S2_RESULTS_MERGE,
        "analysis_entrypoint_sha256": S2_ANALYZER_SHA,
        "phase6_artifact_zip_sha256": S2_PHASE6_ZIP_SHA,
        "phase7_result_artifact_zip_sha256": S2_RESULT_ZIP_SHA,
        "durable_result_archive_sha256": S2_RESULT_ZIP_SHA,
        "valid_observations_analyzed": S2_VALID,
        "invalid_attempts": S2_INVALID,
        "cells_analyzed": S2_CELLS,
        "primary_contrast_rows": S2_PRIMARY,
        "secondary_contrast_rows": S2_SECONDARY,
        "independent_recalculation_mismatches": 0,
        "independent_auditor_sha256": S2_AUDITOR_SHA,
        "new_campaign_execution": False,
        "study1_reanalysis": False,
        "weighted_global_policy_score_computed": False,
        "global_policy_rank_computed": False,
    }
    for key, expected in expected_freeze.items():
        actual = freeze.get(key)
        if actual != expected:
            fail(f"PHASE7_RESULTS_FREEZE.json {key}: expected {expected!r}, found {actual!r}")

    rq3 = freeze.get("rq3_interpretation", {})
    for key, expected in (
        ("classification", "STRUCTURAL_LABEL_INVARIANCE_CONTROL"),
        ("c_family_holm_rejected", 0),
        ("c_family_contrasts", 54),
        ("cause_label_changes_hidden_truth", False),
        ("cause_label_changes_policy_visible_evidence", False),
    ):
        if rq3.get(key) != expected:
            fail(f"Study-2 RQ3 freeze drift: {key}={rq3.get(key)!r}, expected {expected!r}")

    source = provenance.get("source_phase6", {})
    for key, expected in (
        ("artifact_zip_sha256", S2_PHASE6_ZIP_SHA),
        ("observations_sha256", S2_OBSERVATIONS_SHA),
        ("trial_manifest_sha256", S2_TRIAL_MANIFEST_SHA),
        ("valid_observations", S2_VALID),
        ("invalid_attempts", S2_INVALID),
        ("cell_count", S2_CELLS),
    ):
        if source.get(key) != expected:
            fail(f"PHASE7_PROVENANCE.json source_phase6 {key} drift")

    canonical = provenance.get("canonicalization", {})
    if canonical.get("merge_commit") != S2_RESULTS_MERGE or canonical.get("state") != "MERGED_TO_MAIN":
        fail("Study-2 canonicalization identity/state drift")
    independent = provenance.get("independent_reproduction", {})
    if independent.get("mismatches") != 0:
        fail("Study-2 independent reproduction mismatch count is not zero")
    if independent.get("auditor_sha256") != S2_AUDITOR_SHA:
        fail("Study-2 independent auditor SHA drift")

    archive = ROOT / S2_RESULT_ARCHIVE
    if not archive.is_file():
        fail(f"Study-2 durable result ZIP missing: {S2_RESULT_ARCHIVE}")
    elif sha256_file(archive) != S2_RESULT_ZIP_SHA:
        fail("Study-2 durable result ZIP SHA-256 mismatch")

    for token, label in (
        (S2_PHASE6_ZIP_SHA, "Study-2 Phase-6 artifact SHA"),
        (S2_OBSERVATIONS_SHA, "Study-2 observations SHA"),
        (S2_TRIAL_MANIFEST_SHA, "Study-2 trial-manifest SHA"),
        (S2_RESULT_ZIP_SHA, "Study-2 Phase-7 result SHA"),
        (S2_CANONICAL_CLOSEOUT, "Study-2 canonical closeout commit"),
    ):
        if token not in tracker:
            fail(f"research tracker missing {label}: {token}")
    for token, label in (
        (S2_PHASE6_ZIP_SHA, "Study-2 Phase-6 artifact SHA"),
        (S2_OBSERVATIONS_SHA, "Study-2 observations SHA"),
        (S2_TRIAL_MANIFEST_SHA, "Study-2 trial-manifest SHA"),
        (S2_RESULT_ZIP_SHA, "Study-2 Phase-7 result SHA"),
    ):
        if token not in declarations:
            fail(f"declarations missing {label}: {token}")

    if len(ERRORS) == before:
        ok("Study-2 canonical freeze/provenance/archive identities cross-checked")


def validate_study8_identities() -> None:
    close = json.loads(read("study8/STUDY8_TECHNICAL_CLOSE.json"))
    tracker = read("tracker/RESEARCH_TRACKER.md")
    before = len(ERRORS)

    if close.get("study_id") != S8_EXPERIMENT_ID:
        fail("Study-8 technical-close experiment ID drift")
    if close.get("status") != S8_STATUS:
        fail(f"Study-8 technical-close status drift: {close.get('status')!r}")

    science_merge = close.get("science_merge", {})
    if science_merge.get("main_commit") != S8_SCIENCE_MERGE:
        fail("Study-8 science merge commit drift")
    post_ci = science_merge.get("post_merge_ci", {})
    if post_ci.get("run_id") != S8_POST_MERGE_CI or post_ci.get("conclusion") != "success":
        fail("Study-8 post-merge CI identity/conclusion drift")

    population = close.get("canonical_population", {})
    for key in ("expected_rows", "primary_rows", "independent_rows", "exact_row_matches"):
        if population.get(key) != S8_ROWS:
            fail(f"Study-8 {key} drift: {population.get(key)!r}")
    if population.get("mismatch_count") != 0:
        fail("Study-8 row mismatch count is not zero")

    frozen = close.get("frozen_sha256", {})
    for key, expected in (
        ("canonical_observations_csv", S8_CANONICAL_SHA),
        ("primary_findings_json", S8_FINDINGS_SHA),
        ("independent_findings_json", S8_FINDINGS_SHA),
        ("interpretation_audit_json", S8_INTERPRETATION_SHA),
    ):
        if frozen.get(key) != expected:
            fail(f"Study-8 frozen SHA drift: {key}")

    for token, label in (
        (S8_STATUS, "Study-8 technical-close status"),
        (S8_CANONICAL_SHA, "Study-8 canonical observations SHA"),
        (S8_FINDINGS_SHA, "Study-8 findings SHA"),
        (S8_INTERPRETATION_SHA, "Study-8 interpretation-audit SHA"),
        (S8_SCIENCE_MERGE, "Study-8 science merge commit"),
    ):
        if token not in tracker:
            fail(f"research tracker missing {label}: {token}")

    result = subprocess.run(
        [sys.executable, "study8/scripts/check_study8_technical_close.py"],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        fail("Study-8 technical-close integrity checker failed:\n" + result.stdout.rstrip())
    elif "study8_technical_close=PASS" not in result.stdout:
        fail("Study-8 technical-close checker did not emit PASS marker")

    if len(ERRORS) == before:
        ok("Study-8 technical-close/results-freeze identities cross-checked")


def validate_git_provenance() -> None:
    before = len(ERRORS)
    for sha in PROVENANCE_COMMITS:
        result = subprocess.run(
            ["git", "cat-file", "-e", f"{sha}^{{commit}}"],
            cwd=ROOT,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
        if result.returncode != 0:
            fail(f"historical/canonical provenance commit not resolvable: {sha}")
    if len(ERRORS) == before:
        ok(f"historical/canonical provenance commits resolve: {len(PROVENANCE_COMMITS)}")


def validate_no_unresolved_markers() -> None:
    files = [
        p
        for p in ROOT.rglob("*")
        if p.is_file()
        and ".git" not in p.parts
        and p.suffix.lower() in {".py", ".sh"}
    ]
    terms = ("TO" + "DO", "FIX" + "ME", "X" * 3, "HA" + "CK")
    marker = re.compile(r"\b(?:" + "|".join(re.escape(term) for term in terms) + r")\b", re.IGNORECASE)
    before = len(ERRORS)
    for path in files:
        for lineno, line in enumerate(
            path.read_text(encoding="utf-8", errors="replace").splitlines(), start=1
        ):
            if "#" not in line:
                continue
            comment = line.split("#", 1)[1]
            if marker.search(comment):
                fail(f"unresolved source work marker {path.relative_to(ROOT)}:{lineno}: {comment.strip()}")
    if len(ERRORS) == before:
        ok(f"source comments checked across {len(files)} Python/shell files")


def validate_current_state() -> None:
    require_text(
        "README.md",
        required=(
            "two separately frozen empirical studies",
            "3,872 VALID observations",
            "Study 8",
            S8_STATUS,
            "separate companion study",
            "structural label-invariance",
        ),
        forbidden=("the package is at the **final submission-export gate**",),
    )
    require_text(
        "publication/README.md",
        required=(
            "two separately frozen empirical studies",
            "03-study2-methods-extension.md",
            "04-study2-results-extension.md",
            "responsible-release-reviewed DOI archive",
            "Study 8",
            "companion-paper",
        ),
    )
    require_text(
        "publication/manuscript/MANUSCRIPT-ASSEMBLY.md",
        required=(
            "two separately frozen empirical studies",
            "Study 1 = exactly 720 VALID observations",
            "Study 2 = exactly 3,872 VALID observations",
            "structural label-invariance/control result",
        ),
        forbidden=("Study 2/Study 3 proposals kept scientifically separate",),
    )
    require_text(
        "tracker/RESEARCH_TRACKER.md",
        required=(
            "Last updated: 2026-09-03",
            S2_STATUS,
            S2_CANONICAL_CLOSEOUT,
            S8_STATUS,
            S8_SCIENCE_MERGE,
            "Study-8 companion paper",
        ),
        forbidden=("Current action: final submission-export gate",),
    )
    require_text(
        "tracker/work_packages.csv",
        required=(
            "Historical WP10 is closed",
            "Study-2 source-evidence responsible release is a separate current pre-submission gate",
        ),
    )
    require_text(
        "docs/REPRODUCIBILITY_GUIDE.md",
        required=(
            "Study-2 Phase-7 verification",
            S2_RESULT_ZIP_SHA,
            "responsible-release-reviewed DOI-bearing archive",
            "Study-8 technical-close verification",
            S8_CANONICAL_SHA,
        ),
    )
    require_text(
        "study8/README.md",
        required=(S8_STATUS, S8_SCIENCE_MERGE, S8_CANONICAL_SHA, "P3 - P1 = 0/1"),
    )
    require_text(
        "study8/docs/PHASE8_7_TECHNICAL_CLOSE.md",
        required=("Study 8 is technically closed", S8_SCIENCE_MERGE, str(S8_POST_MERGE_CI), S8_FINDINGS_SHA),
    )
    require_text(
        "publication/submission/computers-and-security/submission-checklist.md",
        required=(
            "TWO-STUDY JOURNAL INTEGRATION / STUDY-2 SOURCE-EVIDENCE RESPONSIBLE RELEASE",
            "3,872 VALID observations",
        ),
        forbidden=("Study 2 generalization design is separate from the frozen Study 1 population and remains design-only/not runtime-authorized",),
    )
    require_text(
        "publication/submission/computers-and-security/README.md",
        required=(
            "two separately frozen empirical studies",
            "structural label-invariance/control result",
            "responsible-release-reviewed DOI publication still required",
        ),
    )
    require_text("publication/submission/computers-and-security/highlights.md", required=("720 and 3,872",))
    require_text("publication/submission/computers-and-security/title-page.md", required=("Two Controlled Software-in-the-Loop Studies",))
    require_text("publication/manuscript/03-study2-methods-extension.md", required=("3,872", "85", "logical SIL"))
    require_text("publication/manuscript/04-study2-results-extension.md", required=("structural label-invariance", "54", "0"))
    require_text(
        "publication/manuscript/07-declarations-and-availability.md",
        required=("Study 2 has a separate frozen population", "responsible-release-reviewed, DOI-bearing durable archive", S2_RESULT_ZIP_SHA),
    )
    require_text("release/UPLOAD_CHECKLIST.md", required=("Historical procedural checklist", "Zenodo v1.0.0"))
    require_text("data/README.md", required=("screening/rights register", "not part of the frozen 720-observation statistical population"))


def main() -> int:
    print("=== REPOSITORY RELEASE / FROZEN-STUDY STATE AUDIT ===")
    validate_json()
    validate_yaml()
    validate_toml()
    validate_csv()
    validate_xml_svg()
    validate_markdown_links()
    validate_script_guide()
    validate_publication_displays()
    validate_bibliography_and_citations()
    validate_submission_inputs()
    validate_study1_identities()
    validate_study2_identities()
    validate_study8_identities()
    validate_git_provenance()
    validate_no_unresolved_markers()
    validate_current_state()

    print(f"checks_completed={len(CHECKS)}")
    print(f"errors={len(ERRORS)}")
    if ERRORS:
        print("repository_release_gate=FAIL", file=sys.stderr)
        return 1
    print("repository_release_gate=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
