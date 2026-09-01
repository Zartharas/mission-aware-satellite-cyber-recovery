from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True)
class CampaignAuthorization:
    authorization_id: str
    experiment_id: str
    scope: str
    authorized_repository_commit: str
    protocol_sha256: str
    cell_matrix_sha256: str
    trial_manifest_sha256: str
    runtime_freeze_sha256: str
    container_recipe_sha256: str
    active: bool
    consumed: bool

    def validate(self, *, current_repository_commit: str, expected_bindings: Mapping[str, str]) -> None:
        if not self.authorization_id:
            raise ValueError("authorization_id is required")
        if self.experiment_id != "S2-AEATR-001":
            raise ValueError("authorization experiment identity mismatch")
        if self.scope != "EXACT_FROZEN_STUDY2_CAMPAIGN":
            raise ValueError("authorization scope mismatch")
        if not self.active or self.consumed:
            raise ValueError("campaign authorization is not active and unconsumed")
        if self.authorized_repository_commit != current_repository_commit:
            raise ValueError("runtime repository commit is not authorized")
        actual = {
            "protocol_sha256": self.protocol_sha256,
            "cell_matrix_sha256": self.cell_matrix_sha256,
            "trial_manifest_sha256": self.trial_manifest_sha256,
            "runtime_freeze_sha256": self.runtime_freeze_sha256,
            "container_recipe_sha256": self.container_recipe_sha256,
        }
        if actual != dict(expected_bindings):
            raise ValueError("campaign authorization hash bindings do not match")
