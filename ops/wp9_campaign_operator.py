#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Iterable, Mapping

FROZEN_RUNTIME_SHA = "aae2239753119c92e7633db3b6c73aee94c7b6dd"
FROZEN_RUNTIME_TREE = "105bc8a868ab90e0c1cfd2385e4e0b50924312df"
PINNED_NOS3_IMAGE = (
    "ivvitc/nos3-64@sha256:"
    "06aa945988a7770b759022c2e1f6f2531818c087fe41a4739d3a3a7f2a9dcce2"
)

EXPECTED_BLOBS = {
    "scripts/run_wp9_r066_final_campaign_trial.sh": (
        "5713f46cb42c34b12d9224d92033695dc438a693"
    ),
    "src/mission_recovery/wp9_campaign_trial_controller.py": (
        "1ad44ff57d21868d7e79c38d4ea6f8c95fe11d47"
    ),
    "src/mission_recovery/wp9_final_campaign_bridge.py": (
        "4e906e2bdd7ca9a2355553d525e7c034d0252339"
    ),
    "src/mission_recovery/wp9_r064_attempt_history.py": (
        "3af3c5188472f0ad012043e2294071d7f7ef26c6"
    ),
    "src/mission_recovery/wp9_r066_campaign_evidence_freshness.py": (
        "f5b64c2a1eab20795ee71edb8cd7b5f40981ba96"
    ),
    "src/mission_recovery/wp9_r066_campaign_runtime_executor.py": (
        "95236646894350d84675abf4ea06f7b8af37bf6d"
    ),
    "src/mission_recovery/wp9_r066_final_campaign_runtime_binding.py": (
        "1c8ba3809a3a85e35e3b85a26cfcff3a20114e9d"
    ),
}

AUTOMATIC_RETRY_ALLOWED = False
AUTOMATIC_NEXT_ALLOWED = False
MAX_RUNTIME_INVOCATIONS_PER_CALL = 1
RUN_ID_PATTERN = re.compile(r"^[A-Za-z0-9_.-]+$")
CAMPAIGN_ROOT_REL = Path("results/wp9/campaign")
ATTEMPT_HISTORY_REL = CAMPAIGN_ROOT_REL / "attempt-history.json"
RUNTIME_ARTIFACT_ROOT_REL = Path("artifacts/runtime")

_ALLOWED_UNLEDGERED_FILES = {
    Path("immutable-ground/campaign-plan.json"),
    Path("immutable-ground/r066-runtime-request.json"),
}


class OperatorError(RuntimeError):
    pass


@dataclass(frozen=True)
class RepoModules:
    validate_attempt_history: Any
    next_required_trial_from_attempt_history: Any
    build_trial_plan: Any
    build_authorization_request: Any
    authorization_classification: str
    authorization_request_classification: str
    build_campaign_runtime_request: Any
    cell_harness_bindings: Mapping[str, dict[str, Any]]
    preflight_runtime_wrapper_composition: Any
    validate_fresh_campaign_evidence: Any


def _run(
    args: list[str],
    *,
    cwd: Path,
    env: Mapping[str, str] | None = None,
    check: bool = True,
    capture: bool = True,
) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(
        args,
        cwd=cwd,
        env=None if env is None else dict(env),
        check=False,
        text=True,
        capture_output=capture,
    )
    if check and completed.returncode != 0:
        detail = (completed.stderr or completed.stdout or "").strip()
        raise OperatorError(
            f"command failed ({completed.returncode}): {' '.join(args)}"
            + (f"\n{detail}" if detail else "")
        )
    return completed


def _git(repo_root: Path, *args: str) -> str:
    return _run(["git", *args], cwd=repo_root).stdout.strip()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _repo_modules(repo_root: Path) -> RepoModules:
    root = str(repo_root.resolve())
    if root not in sys.path:
        sys.path.insert(0, root)

    from src.mission_recovery.wp9_campaign_trial_controller import (  # noqa: PLC0415
        build_trial_plan,
    )
    from src.mission_recovery.wp9_final_campaign_bridge import (  # noqa: PLC0415
        AUTHORIZATION_CLASSIFICATION,
        AUTHORIZATION_REQUEST_CLASSIFICATION,
        build_authorization_request,
    )
    from src.mission_recovery.wp9_r064_attempt_history import (  # noqa: PLC0415
        next_required_trial_from_attempt_history,
        validate_attempt_history,
    )
    from src.mission_recovery.wp9_r066_campaign_evidence_freshness import (  # noqa: PLC0415
        validate_fresh_campaign_evidence,
    )
    from src.mission_recovery.wp9_r066_campaign_runtime_executor import (  # noqa: PLC0415
        _preflight_runtime_wrapper_composition,
    )
    from src.mission_recovery.wp9_r066_final_campaign_runtime_binding import (  # noqa: PLC0415
        CELL_HARNESS_BINDINGS,
        build_campaign_runtime_request,
    )

    return RepoModules(
        validate_attempt_history=validate_attempt_history,
        next_required_trial_from_attempt_history=(
            next_required_trial_from_attempt_history
        ),
        build_trial_plan=build_trial_plan,
        build_authorization_request=build_authorization_request,
        authorization_classification=AUTHORIZATION_CLASSIFICATION,
        authorization_request_classification=(
            AUTHORIZATION_REQUEST_CLASSIFICATION
        ),
        build_campaign_runtime_request=build_campaign_runtime_request,
        cell_harness_bindings=CELL_HARNESS_BINDINGS,
        preflight_runtime_wrapper_composition=(
            _preflight_runtime_wrapper_composition
        ),
        validate_fresh_campaign_evidence=validate_fresh_campaign_evidence,
    )


def verify_frozen_repository(repo_root: Path) -> None:
    root = repo_root.resolve()
    if not (root / ".git").exists():
        raise OperatorError(f"not a Git repository: {root}")

    head = _git(root, "rev-parse", "HEAD")
    tree = _git(root, "rev-parse", "HEAD^{tree}")
    if head != FROZEN_RUNTIME_SHA:
        raise OperatorError(
            "scientific checkout moved: "
            f"expected {FROZEN_RUNTIME_SHA}, observed {head}. "
            "Do not pull live main during the frozen campaign."
        )
    if tree != FROZEN_RUNTIME_TREE:
        raise OperatorError(
            "scientific runtime tree changed: "
            f"expected {FROZEN_RUNTIME_TREE}, observed {tree}"
        )

    status = _git(root, "status", "--short")
    if status:
        raise OperatorError("tracked/untracked worktree is not clean:\n" + status)

    mode = _git(
        root,
        "ls-tree",
        "HEAD",
        "scripts/run_wp9_r066_final_campaign_trial.sh",
    ).split()[0]
    if mode != "100755":
        raise OperatorError("R-066 campaign entry point is not mode 100755")

    for path, expected_blob in EXPECTED_BLOBS.items():
        observed = _git(root, "rev-parse", f"HEAD:{path}")
        if observed != expected_blob:
            raise OperatorError(
                f"frozen blob changed for {path}: "
                f"expected {expected_blob}, observed {observed}"
            )


def validate_static_runtime(repo_root: Path) -> str:
    script = repo_root / "scripts/run_wp9_r066_final_campaign_trial.sh"
    completed = _run(
        [str(script), "validate-static"],
        cwd=repo_root,
    )
    output = completed.stdout
    required = (
        "WP9_R064_FINAL_CAMPAIGN_BRIDGE_STATIC=PASS",
        "WP9_R064_ATTEMPT_HISTORY_GUARD_STATIC=PASS",
        "WP9_R066_FINAL_CAMPAIGN_RUNTIME_BINDING_STATIC=PASS",
        "WP9_R066_CAMPAIGN_RUNTIME_EXECUTOR_STATIC=PASS",
        "production_runtime_executor_bound=true",
        "post_readiness_seed_commit_enforced=true",
        "evidence_freshness_guard_enforced_in_executor=true",
        "runtime_wrapper_composition_preflight_enforced=true",
        "binding_global_restore_enforced=true",
    )
    missing = [item for item in required if item not in output]
    if missing:
        raise OperatorError("missing static runtime invariants: " + ", ".join(missing))
    return output


def _docker_lines(repo_root: Path, args: list[str]) -> list[str]:
    completed = _run(["docker", *args], cwd=repo_root)
    return [line.strip() for line in completed.stdout.splitlines() if line.strip()]


def verify_clean_runtime_snapshot(repo_root: Path) -> None:
    _run(["docker", "info"], cwd=repo_root)
    _run(["docker", "image", "inspect", PINNED_NOS3_IMAGE], cwd=repo_root)

    containers = [
        name
        for name in _docker_lines(
            repo_root,
            ["ps", "-a", "--format", "{{.Names}}"],
        )
        if name.startswith("mascr-")
    ]
    networks = [
        name
        for name in _docker_lines(
            repo_root,
            ["network", "ls", "--format", "{{.Name}}"],
        )
        if name.startswith("mascr-")
    ]
    if containers or networks:
        raise OperatorError(
            "clean runtime snapshot failed; residual MASCR resources: "
            f"containers={containers}, networks={networks}"
        )


def load_attempt_history(history_path: Path) -> list[dict[str, Any]]:
    if not history_path.exists():
        return []
    if history_path.is_symlink():
        raise OperatorError("attempt-history ledger must not be a symlink")
    value = json.loads(history_path.read_text(encoding="utf-8"))
    if not isinstance(value, list):
        raise OperatorError("attempt-history ledger must be a JSON array")
    return value


def next_required_trial(
    *,
    repo_root: Path,
    history: list[dict[str, Any]],
) -> dict[str, Any] | None:
    api = _repo_modules(repo_root)
    api.validate_attempt_history(history)
    return api.next_required_trial_from_attempt_history(history)


def append_attempt_history_atomic(
    *,
    repo_root: Path,
    history_path: Path,
    entry: dict[str, Any],
) -> dict[str, Any]:
    api = _repo_modules(repo_root)
    retained = load_attempt_history(history_path)
    candidate = retained + [copy.deepcopy(entry)]
    state = api.validate_attempt_history(candidate)

    history_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = history_path.with_name(
        f".{history_path.name}.{uuid.uuid4().hex}.tmp"
    )
    temporary.write_text(
        json.dumps(candidate, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, history_path)
    return state


def classify_unledgered_evidence(evidence: Path) -> str:
    if evidence.is_symlink():
        raise ValueError(f"unledgered campaign run is a symlink: {evidence}")
    if not evidence.is_dir():
        raise ValueError(f"unledgered campaign run is not a directory: {evidence}")

    files: set[Path] = set()
    for item in evidence.rglob("*"):
        if item.is_symlink():
            raise ValueError(f"unledgered campaign evidence contains symlink: {item}")
        if item.is_file():
            files.add(item.relative_to(evidence))

    scientific_markers = {
        Path("immutable-ground/campaign-seed-consumption.json"),
        Path("campaign-trial-result.json"),
        Path("campaign-trial-invalid.json"),
        Path("source-harness-invalid.json"),
        Path("source-harness.stdout.log"),
        Path("source-harness.stderr.log"),
    }
    if files & scientific_markers:
        raise ValueError(
            "unledgered campaign evidence contains runtime/scientific markers: "
            + ", ".join(str(path) for path in sorted(files & scientific_markers))
        )
    if any(path.parts and path.parts[0] == "runtime-observation" for path in files):
        raise ValueError("unledgered campaign evidence contains runtime observation")
    unexpected = files - _ALLOWED_UNLEDGERED_FILES
    if unexpected:
        raise ValueError(
            "unledgered campaign evidence is not a known pre-runtime abort: "
            + ", ".join(str(path) for path in sorted(unexpected))
        )
    return "PRE_RUNTIME_ABORT_UNCONSUMED"


def _run_evidence_directory(
    repo_root: Path,
    *,
    campaign_seed: int,
    cell_id: str,
    run_id: str,
) -> Path:
    return (
        repo_root
        / CAMPAIGN_ROOT_REL
        / f"seed-{int(campaign_seed)}"
        / str(cell_id)
        / str(run_id)
    )


def _iter_campaign_run_directories(repo_root: Path) -> Iterable[Path]:
    campaign_root = repo_root / CAMPAIGN_ROOT_REL
    if not campaign_root.exists():
        return []
    runs: list[Path] = []
    for seed_dir in sorted(campaign_root.glob("seed-*")):
        if seed_dir.is_symlink() or not seed_dir.is_dir():
            raise OperatorError(f"invalid campaign seed directory: {seed_dir}")
        for cell_dir in sorted(seed_dir.iterdir()):
            if cell_dir.is_symlink() or not cell_dir.is_dir():
                raise OperatorError(f"invalid campaign cell directory: {cell_dir}")
            if re.fullmatch(r"A\d{2}", cell_dir.name) is None:
                raise OperatorError(f"unexpected campaign cell directory: {cell_dir}")
            for run_dir in sorted(cell_dir.iterdir()):
                if run_dir.is_symlink() or not run_dir.is_dir():
                    raise OperatorError(f"invalid campaign run directory: {run_dir}")
                runs.append(run_dir)
    return runs


def audit_campaign_filesystem(
    *,
    repo_root: Path,
    history: list[dict[str, Any]],
) -> dict[str, Any]:
    api = _repo_modules(repo_root)
    state = api.validate_attempt_history(history)
    ledger_by_run: dict[str, dict[str, Any]] = {}

    for row in history:
        run_id = str(row["run_id"])
        if run_id in ledger_by_run:
            raise OperatorError(f"duplicate run_id in ledger: {run_id}")
        ledger_by_run[run_id] = row
        evidence = _run_evidence_directory(
            repo_root,
            campaign_seed=int(row["campaign_seed"]),
            cell_id=str(row["cell_id"]),
            run_id=run_id,
        )
        if not evidence.is_dir() or evidence.is_symlink():
            raise OperatorError(f"ledgered campaign evidence directory missing: {evidence}")

        status = str(row["attempt_status"])
        canonical = evidence / (
            "campaign-trial-result.json" if status == "VALID" else "campaign-trial-invalid.json"
        )
        opposite = evidence / (
            "campaign-trial-invalid.json" if status == "VALID" else "campaign-trial-result.json"
        )
        if not canonical.is_file() or opposite.exists():
            raise OperatorError(
                f"ledger/canonical evidence mismatch for {run_id}: status={status}"
            )
        record = json.loads(canonical.read_text(encoding="utf-8"))
        if (
            record.get("run_id") != run_id
            or int(record.get("campaign_seed")) != int(row["campaign_seed"])
            or record.get("cell_id") != row["cell_id"]
            or record.get("attempt_status") != status
        ):
            raise OperatorError(f"canonical campaign identity mismatch for {run_id}")
        if status == "VALID":
            seed_marker = evidence / "immutable-ground/campaign-seed-consumption.json"
            if not seed_marker.is_file():
                raise OperatorError(f"VALID attempt lacks seed-commit marker: {run_id}")
            runtime_manifest = (
                repo_root
                / RUNTIME_ARTIFACT_ROOT_REL
                / run_id
                / "runtime-manifest.txt"
            )
            if not runtime_manifest.is_file():
                raise OperatorError(f"VALID attempt lacks runtime manifest: {run_id}")

    unledgered: list[dict[str, str]] = []
    seen_run_dirs: set[str] = set()
    for run_dir in _iter_campaign_run_directories(repo_root):
        run_id = run_dir.name
        if run_id in seen_run_dirs:
            raise OperatorError(f"run_id appears in multiple campaign directories: {run_id}")
        seen_run_dirs.add(run_id)
        if run_id in ledger_by_run:
            continue
        classification = classify_unledgered_evidence(run_dir)
        runtime_artifact = repo_root / RUNTIME_ARTIFACT_ROOT_REL / run_id
        if runtime_artifact.exists() or runtime_artifact.is_symlink():
            raise OperatorError(
                "unledgered pre-runtime campaign artifact unexpectedly has "
                f"runtime evidence: {runtime_artifact}"
            )
        unledgered.append(
            {
                "run_id": run_id,
                "classification": classification,
                "relative_path": str(run_dir.relative_to(repo_root)),
            }
        )

    return {
        **state,
        "ledgered_run_count": len(history),
        "unledgered_pre_runtime_count": len(unledgered),
        "unledgered_pre_runtime": unledgered,
    }


def _fresh_run_id(next_trial: Mapping[str, Any]) -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    position = int(next_trial["global_order_index"])
    seed = int(next_trial["campaign_seed"])
    cell = str(next_trial["cell_id"]).lower()
    return (
        f"{stamp}-wp9-r066-p{position:04d}-s{seed}-{cell}-"
        f"{uuid.uuid4().hex}"
    )


def prepare_next_request(
    *,
    repo_root: Path,
    history: list[dict[str, Any]],
    run_id: str | None = None,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    api = _repo_modules(repo_root)
    next_trial = api.next_required_trial_from_attempt_history(history)
    if next_trial is None:
        raise OperatorError("frozen campaign already has 720 valid positions")

    chosen_run_id = _fresh_run_id(next_trial) if run_id is None else run_id
    if RUN_ID_PATTERN.fullmatch(chosen_run_id) is None:
        raise OperatorError("generated/provided run_id is not safe")

    plan = api.build_trial_plan(
        campaign_seed=int(next_trial["campaign_seed"]),
        cell_id=str(next_trial["cell_id"]),
        run_id=chosen_run_id,
        repo_commit=FROZEN_RUNTIME_SHA,
    )
    authorization_request = api.build_authorization_request(plan)
    if (
        authorization_request.get("classification")
        != api.authorization_request_classification
        or authorization_request.get("authorization_scope") != "single_frozen_trial"
        or authorization_request.get("single_trial_runtime_authorized") is not False
        or authorization_request.get("campaign_wide_execution_authorized") is not False
    ):
        raise OperatorError("single-trial authorization request contract changed")

    authorization = copy.deepcopy(authorization_request)
    authorization["classification"] = api.authorization_classification
    authorization["single_trial_runtime_authorized"] = True

    request = api.build_campaign_runtime_request(
        plan=plan,
        authorization=authorization,
        attempt_history=history,
        current_repo_sha=FROZEN_RUNTIME_SHA,
    )

    persisted = json.loads(json.dumps(request, sort_keys=True))
    if persisted != request:
        raise OperatorError("R-066 request is not stable across JSON persistence")
    expected_binding = api.cell_harness_bindings[str(next_trial["cell_id"])]
    if persisted.get("source_harness") != expected_binding:
        raise OperatorError("persisted source-harness binding changed")

    api.preflight_runtime_wrapper_composition(request=persisted)
    api.validate_fresh_campaign_evidence(persisted)

    if (
        int(persisted["global_order_index"]) != int(next_trial["global_order_index"])
        or int(persisted["campaign_seed"]) != int(next_trial["campaign_seed"])
        or int(persisted["cell_order_index"]) != int(next_trial["cell_order_index"])
        or persisted["cell_id"] != next_trial["cell_id"]
    ):
        raise OperatorError("prepared request differs from exact next frozen position")
    if persisted.get("automatic_retry_allowed") is not False:
        raise OperatorError("prepared request unexpectedly allows retry")
    if persisted.get("automatic_next_case_allowed") is not False:
        raise OperatorError("prepared request unexpectedly allows next case")

    return plan, authorization, persisted


def _write_json(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )


def _residual_runtime_resources(repo_root: Path, run_id: str) -> tuple[list[str], list[str]]:
    safe = re.sub(r"[^a-z0-9_.-]+", "-", run_id.lower())
    containers = [
        name
        for name in _docker_lines(
            repo_root,
            ["ps", "-a", "--format", "{{.Names}}"],
        )
        if safe in name
    ]
    networks = [
        name
        for name in _docker_lines(
            repo_root,
            ["network", "ls", "--format", "{{.Name}}"],
        )
        if safe in name
    ]
    return containers, networks


def _print_result_summary(
    *,
    result: dict[str, Any],
    canonical_path: Path,
    global_order_index: int,
) -> None:
    runner = result.get("runner_result", {})
    record = runner.get("run_record", {}) if isinstance(runner, dict) else {}
    outcomes = record.get("outcomes", {}) if isinstance(record, dict) else {}
    timing = record.get("timing", {}) if isinstance(record, dict) else {}
    provenance = runner.get("binding_provenance", {}) if isinstance(runner, dict) else {}
    metadata = provenance.get("execution_metadata", {}) if isinstance(provenance, dict) else {}

    print("CAMPAIGN_SINGLE_POSITION_RESULT=PASS")
    print(f"global_order_index={global_order_index}")
    print(f"attempt_status={result.get('attempt_status')}")
    print(f"run_id={result.get('run_id')}")
    print(f"campaign_seed={result.get('campaign_seed')}")
    print(f"cell_id={result.get('cell_id')}")
    print(f"event_id={runner.get('event_id')}")
    print(f"runtime_family={runner.get('runtime_family')}")
    print(f"runtime_variant={runner.get('runtime_variant')}")
    print(f"requested_policy_id={metadata.get('requested_policy_id')}")
    print(f"effective_policy_id={metadata.get('effective_policy_id')}")
    print(f"selected_action={metadata.get('selected_action')}")
    print(f"treatment_fidelity_valid={str(runner.get('treatment_fidelity_valid')).lower()}")
    print(f"raw_metric_inputs_complete={str(runner.get('raw_metric_inputs_complete')).lower()}")
    print(
        "outcome_matches_predeclared_expectation="
        + str(runner.get("outcome_matches_predeclared_expectation")).lower()
    )
    print(
        "unexpected_scientific_outcome_retained="
        + str(runner.get("unexpected_scientific_outcome_retained")).lower()
    )
    print(f"terminal_state={record.get('terminal_state')}")
    for key in (
        "unauthorized_effect_completed",
        "evidence_completeness_ratio",
        "mission_objective_completion_ratio",
        "legitimate_command_rejection_rate",
        "ground_spacecraft_state_divergence_s",
    ):
        if key in outcomes:
            print(f"{key}={outcomes[key]}")
    if "safety_invariant_violations" in outcomes:
        print(
            "safety_invariant_violations="
            + json.dumps(outcomes["safety_invariant_violations"], separators=(",", ":"))
        )
    for key in ("event_activation_s", "containment_s", "verified_recovery_s"):
        if key in timing:
            print(f"{key}={timing[key]}")
    print(f"canonical_result_sha256={_sha256_file(canonical_path)}")


def run_one_next_position(repo_root: Path) -> int:
    verify_frozen_repository(repo_root)
    validate_static_runtime(repo_root)

    history_path = repo_root / ATTEMPT_HISTORY_REL
    history = load_attempt_history(history_path)
    audit = audit_campaign_filesystem(repo_root=repo_root, history=history)
    next_trial = next_required_trial(repo_root=repo_root, history=history)
    if next_trial is None:
        print("campaign_complete=true")
        print("valid_position_count=720")
        return 0

    verify_clean_runtime_snapshot(repo_root)
    run_id = _fresh_run_id(next_trial)
    plan, authorization, request = prepare_next_request(
        repo_root=repo_root,
        history=history,
        run_id=run_id,
    )

    # Re-audit after all zero-write request/composition/freshness checks. Any
    # campaign namespace mutation before the one execution is a hard block.
    audit_after = audit_campaign_filesystem(repo_root=repo_root, history=history)
    if audit_after != audit:
        raise OperatorError("campaign state changed during zero-write preflight")

    print("WP9_CAMPAIGN_OPERATOR_PREFLIGHT=PASS")
    print(f"prior_attempt_count={len(history)}")
    print(f"prior_valid_position_count={audit['valid_position_count']}")
    print(f"prior_invalid_attempt_count={audit['invalid_attempt_count']}")
    print(f"retained_pre_runtime_abort_count={audit['unledgered_pre_runtime_count']}")
    print(f"global_order_index={next_trial['global_order_index']}")
    print(f"campaign_seed={next_trial['campaign_seed']}")
    print(f"cell_order_index={next_trial['cell_order_index']}")
    print(f"cell_id={next_trial['cell_id']}")
    print(f"run_id={run_id}")
    print(f"frozen_runtime_sha={FROZEN_RUNTIME_SHA}")
    print("automatic_retry_allowed=false")
    print("automatic_next_case_allowed=false")

    evidence_rel = Path(str(request["evidence_directory"]))
    evidence = repo_root / evidence_rel
    script = repo_root / "scripts/run_wp9_r066_final_campaign_trial.sh"

    with tempfile.TemporaryDirectory(prefix="wp9-campaign-operator-") as tmp:
        tmp_path = Path(tmp)
        request_path = tmp_path / "runtime-request.json"
        output_path = tmp_path / "executor-return.json"
        plan_path = tmp_path / "plan.json"
        authorization_path = tmp_path / "authorization.json"
        _write_json(request_path, request)
        _write_json(plan_path, plan)
        _write_json(authorization_path, authorization)

        env = os.environ.copy()
        env.update(
            {
                "WP9_R066_FINAL_CAMPAIGN_RUNTIME_AUTHORIZED": "1",
                "WP9_R066_AUTHORIZED_RUN_ID": run_id,
                "WP9_R066_AUTHORIZED_SEED": str(next_trial["campaign_seed"]),
                "WP9_R066_AUTHORIZED_CELL": str(next_trial["cell_id"]),
                "WP9_R066_AUTHORIZED_REPO_SHA": FROZEN_RUNTIME_SHA,
            }
        )

        completed = _run(
            [
                str(script),
                "execute-request",
                "--request-json",
                str(request_path),
                "--output-json",
                str(output_path),
            ],
            cwd=repo_root,
            env=env,
            check=False,
            capture=False,
        )

        containers, networks = _residual_runtime_resources(repo_root, run_id)
        if containers or networks:
            raise OperatorError(
                "post-runtime residual resources require review: "
                f"containers={containers}, networks={networks}"
            )
        if _git(repo_root, "status", "--short"):
            raise OperatorError("tracked worktree changed during campaign trial")

        if completed.returncode != 0:
            if output_path.exists():
                raise OperatorError(
                    "executor returned nonzero but also wrote structured output; review required"
                )
            if evidence.exists():
                try:
                    classification = classify_unledgered_evidence(evidence)
                except ValueError as exc:
                    raise OperatorError(
                        "executor failed with ambiguous unledgered campaign evidence; "
                        "do not retry: " + str(exc)
                    ) from exc
                print("CAMPAIGN_PRE_RUNTIME_ABORT_RETAINED=PASS")
                print(f"classification={classification}")
                print(f"run_id={run_id}")
                print(f"campaign_seed={next_trial['campaign_seed']}")
                print(f"cell_id={next_trial['cell_id']}")
                print("campaign_seed_consumed=false")
                print("attempt_history_appended=false")
            else:
                print("CAMPAIGN_PRE_RUNTIME_ABORT_RETAINED=PASS")
                print("classification=PRE_RUNTIME_ABORT_UNCONSUMED")
                print(f"run_id={run_id}")
                print("evidence_directory_created=false")
                print("campaign_seed_consumed=false")
                print("attempt_history_appended=false")
            print("automatic_retry_performed=false")
            print("automatic_next_case_performed=false")
            return completed.returncode

        if not output_path.is_file():
            raise OperatorError("successful executor did not write structured return")
        result = json.loads(output_path.read_text(encoding="utf-8"))

    if (
        result.get("run_id") != run_id
        or int(result.get("campaign_seed")) != int(next_trial["campaign_seed"])
        or result.get("cell_id") != next_trial["cell_id"]
        or int(result.get("source_harness_invocation_count")) != 1
        or result.get("automatic_retry_performed") is not False
        or result.get("automatic_next_case_performed") is not False
        or result.get("campaign_wide_execution_authorized") is not False
    ):
        raise OperatorError("executor return violated single-position contract")

    status = result.get("attempt_status")
    if status not in {"VALID", "INVALID"}:
        raise OperatorError(f"unexpected attempt status: {status!r}")
    canonical_path = evidence / (
        "campaign-trial-result.json" if status == "VALID" else "campaign-trial-invalid.json"
    )
    if not canonical_path.is_file():
        raise OperatorError("structured executor return lacks canonical retained evidence")

    entry = {
        "campaign_seed": int(next_trial["campaign_seed"]),
        "cell_order_index": int(next_trial["cell_order_index"]),
        "cell_id": str(next_trial["cell_id"]),
        "run_id": run_id,
        "attempt_status": status,
    }
    state = append_attempt_history_atomic(
        repo_root=repo_root,
        history_path=history_path,
        entry=entry,
    )

    retained_history = load_attempt_history(history_path)
    post_audit = audit_campaign_filesystem(
        repo_root=repo_root,
        history=retained_history,
    )
    if post_audit["attempt_count"] != state["attempt_count"]:
        raise OperatorError("post-append filesystem audit differs from ledger state")

    _print_result_summary(
        result=result,
        canonical_path=canonical_path,
        global_order_index=int(next_trial["global_order_index"]),
    )
    print("attempt_history_append=PASS")
    print(f"attempt_count={state['attempt_count']}")
    print(f"valid_position_count={state['valid_position_count']}")
    print(f"invalid_attempt_count={state['invalid_attempt_count']}")

    following = next_required_trial(
        repo_root=repo_root,
        history=retained_history,
    )
    if following is None:
        print("campaign_complete=true")
        print("next_required_trial=NONE")
    else:
        print("campaign_complete=false")
        print(f"next_required_global_order_index={following['global_order_index']}")
        print(f"next_required_campaign_seed={following['campaign_seed']}")
        print(f"next_required_cell_order_index={following['cell_order_index']}")
        print(f"next_required_cell_id={following['cell_id']}")

    print("automatic_retry_performed=false")
    print("automatic_next_case_performed=false")
    print("CAMPAIGN_OPERATOR_HARD_STOP=PASS")
    return 0


def print_status(repo_root: Path) -> int:
    verify_frozen_repository(repo_root)
    history_path = repo_root / ATTEMPT_HISTORY_REL
    history = load_attempt_history(history_path)
    audit = audit_campaign_filesystem(repo_root=repo_root, history=history)
    next_trial = next_required_trial(repo_root=repo_root, history=history)

    print("WP9_CAMPAIGN_OPERATOR_STATUS=PASS")
    print(f"frozen_runtime_sha={FROZEN_RUNTIME_SHA}")
    print(f"attempt_count={audit['attempt_count']}")
    print(f"valid_position_count={audit['valid_position_count']}")
    print(f"invalid_attempt_count={audit['invalid_attempt_count']}")
    print(f"retained_pre_runtime_abort_count={audit['unledgered_pre_runtime_count']}")
    for row in audit["unledgered_pre_runtime"]:
        print(
            "retained_pre_runtime_abort="
            + row["run_id"]
            + ":"
            + row["classification"]
        )
    if next_trial is None:
        print("campaign_complete=true")
        print("next_required_trial=NONE")
    else:
        print("campaign_complete=false")
        print(f"next_required_global_order_index={next_trial['global_order_index']}")
        print(f"next_required_campaign_seed={next_trial['campaign_seed']}")
        print(f"next_required_cell_order_index={next_trial['cell_order_index']}")
        print(f"next_required_cell_id={next_trial['cell_id']}")
    print("automatic_retry_allowed=false")
    print("automatic_next_case_allowed=false")
    return 0


def preflight_next(repo_root: Path) -> int:
    verify_frozen_repository(repo_root)
    validate_static_runtime(repo_root)
    history_path = repo_root / ATTEMPT_HISTORY_REL
    history = load_attempt_history(history_path)
    audit = audit_campaign_filesystem(repo_root=repo_root, history=history)
    next_trial = next_required_trial(repo_root=repo_root, history=history)
    if next_trial is None:
        print("campaign_complete=true")
        return 0
    verify_clean_runtime_snapshot(repo_root)
    run_id = _fresh_run_id(next_trial)
    _, _, request = prepare_next_request(
        repo_root=repo_root,
        history=history,
        run_id=run_id,
    )
    audit_after = audit_campaign_filesystem(repo_root=repo_root, history=history)
    if audit_after != audit:
        raise OperatorError("campaign state changed during zero-write preflight")
    print("WP9_CAMPAIGN_OPERATOR_ZERO_WRITE_PREFLIGHT=PASS")
    print(f"global_order_index={next_trial['global_order_index']}")
    print(f"campaign_seed={next_trial['campaign_seed']}")
    print(f"cell_order_index={next_trial['cell_order_index']}")
    print(f"cell_id={next_trial['cell_id']}")
    print(f"runtime_family={request['runtime_family']}")
    print(f"runtime_variant={request['runtime_variant']}")
    print("runtime_execution_performed=false")
    print("campaign_seed_consumed=false")
    print("campaign_data_generated=false")
    return 0


def _default_repo() -> Path:
    value = os.environ.get("WP9_REPO_ROOT")
    if value:
        return Path(value).expanduser().resolve()
    return Path.cwd().resolve()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "External one-position operator for the frozen WP9 final campaign. "
            "It never retries and never executes the next position automatically."
        )
    )
    parser.add_argument("--repo", type=Path, default=_default_repo())
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("status")
    sub.add_parser("preflight-next")
    run = sub.add_parser("run-next")
    run.add_argument(
        "--execute-one",
        action="store_true",
        help="required explicit acknowledgement for exactly one runtime invocation",
    )

    args = parser.parse_args(argv)
    repo_root = args.repo.expanduser().resolve()
    try:
        if args.command == "status":
            return print_status(repo_root)
        if args.command == "preflight-next":
            return preflight_next(repo_root)
        if not args.execute_one:
            raise OperatorError(
                "run-next requires --execute-one; automatic campaign execution is prohibited"
            )
        return run_one_next_position(repo_root)
    except (OperatorError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print(f"WP9_CAMPAIGN_OPERATOR_BLOCKED={type(exc).__name__}", file=sys.stderr)
        print(str(exc), file=sys.stderr)
        print("automatic_retry_performed=false", file=sys.stderr)
        print("automatic_next_case_performed=false", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
