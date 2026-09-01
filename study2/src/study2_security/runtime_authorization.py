from __future__ import annotations

import hashlib
import json
import re
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from typing import Mapping

from .cell_matrix import matrix_sha256
from .runtime_freeze import runtime_freeze_sha256
from .trial_manifest import trial_manifest_sha256


ROOT = Path(__file__).resolve().parents[3]
COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
AUTHORIZATION_PATH = ROOT / "study2" / "PHASE6_CAMPAIGN_AUTHORIZATION.json"
RUNTIME_STATIC_PATHS = (
    ".github/workflows/run-study2-phase6-campaign.yml",
    "study2/Dockerfile",
    "study2/requirements.txt",
    "study2/STUDY2_PROTOCOL.json",
    "study2/STUDY2_PROTOCOL_AMENDMENT_1.json",
    "study2/scripts/run_phase6_campaign.py",
)


def _file_sha256(relative_path: str) -> str:
    path = ROOT / relative_path
    if not path.is_file():
        raise ValueError(f"required runtime binding path is missing: {relative_path}")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def runtime_bundle_manifest() -> tuple[tuple[str, str], ...]:
    paths = set(RUNTIME_STATIC_PATHS)
    paths.update(
        str(path.relative_to(ROOT))
        for path in (ROOT / "study2" / "src" / "study2_security").glob("*.py")
    )
    return tuple((path, _file_sha256(path)) for path in sorted(paths))


def runtime_bundle_sha256() -> str:
    digest = hashlib.sha256()
    for path, sha256 in runtime_bundle_manifest():
        digest.update(f"{path}:{sha256}\n".encode("utf-8"))
    return digest.hexdigest()


def current_runtime_bindings() -> dict[str, str]:
    return {
        "protocol_sha256": _file_sha256("study2/STUDY2_PROTOCOL.json"),
        "protocol_amendment_sha256": _file_sha256(
            "study2/STUDY2_PROTOCOL_AMENDMENT_1.json"
        ),
        "cell_matrix_sha256": matrix_sha256(),
        "trial_manifest_sha256": trial_manifest_sha256(),
        "runtime_freeze_sha256": runtime_freeze_sha256(),
        "container_recipe_sha256": _file_sha256("study2/Dockerfile"),
        "runtime_bundle_sha256": runtime_bundle_sha256(),
    }


@dataclass(frozen=True)
class CampaignAuthorization:
    authorization_id: str
    experiment_id: str
    scope: str
    phase5_base_commit: str
    protocol_sha256: str
    protocol_amendment_sha256: str
    cell_matrix_sha256: str
    trial_manifest_sha256: str
    runtime_freeze_sha256: str
    container_recipe_sha256: str
    runtime_bundle_sha256: str
    active: bool
    consumed: bool

    def _binding_fields(self) -> dict[str, str]:
        return {
            "protocol_sha256": self.protocol_sha256,
            "protocol_amendment_sha256": self.protocol_amendment_sha256,
            "cell_matrix_sha256": self.cell_matrix_sha256,
            "trial_manifest_sha256": self.trial_manifest_sha256,
            "runtime_freeze_sha256": self.runtime_freeze_sha256,
            "container_recipe_sha256": self.container_recipe_sha256,
            "runtime_bundle_sha256": self.runtime_bundle_sha256,
        }

    def validate_bindings(self) -> None:
        if not self.authorization_id:
            raise ValueError("authorization_id is required")
        if self.experiment_id != "S2-AEATR-001":
            raise ValueError("authorization experiment identity mismatch")
        if self.scope != "EXACT_FROZEN_STUDY2_CAMPAIGN":
            raise ValueError("authorization scope mismatch")
        if not COMMIT_RE.fullmatch(self.phase5_base_commit):
            raise ValueError("phase5_base_commit must be an exact 40-hex Git commit")
        if not self.active or self.consumed:
            raise ValueError("campaign authorization is not active and unconsumed")
        if self._binding_fields() != current_runtime_bindings():
            raise ValueError("campaign authorization does not match current runtime bindings")

    def validate(
        self,
        *,
        current_repository_commit: str = "",
        expected_bindings: Mapping[str, str] | None = None,
    ) -> None:
        # Caller-supplied bindings cannot weaken authorization. The effective
        # runtime bindings are derived from the checked-out repository itself.
        del expected_bindings
        if current_repository_commit and not COMMIT_RE.fullmatch(current_repository_commit):
            raise ValueError("current_repository_commit must be an exact 40-hex Git commit when supplied")
        self.validate_bindings()
        if not AUTHORIZATION_PATH.exists():
            raise ValueError("no repository-backed Phase-6 campaign authorization exists")
        persisted = json.loads(AUTHORIZATION_PATH.read_text(encoding="utf-8"))
        if persisted != asdict(self):
            raise ValueError("in-memory authorization differs from repository authorization")

    def consumed_copy(self) -> CampaignAuthorization:
        self.validate_bindings()
        return replace(self, active=False, consumed=True)
