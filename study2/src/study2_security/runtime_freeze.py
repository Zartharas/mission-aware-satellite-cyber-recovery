from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from enum import Enum
from typing import Any

from .cell_matrix import matrix_sha256
from .protocol import ContactRegime
from .trial_manifest import trial_manifest_sha256


EXPERIMENT_ID = "S2-AEATR-001"
DECISION_TIME_S = 10.0
EVIDENCE_ISSUED_AT_S = 8.0
EVIDENCE_VALID_FOR_S = 5.0
RECOVERY_PROCESSING_S = 5.0
CENSOR_HORIZON_S = 240.0

DEVELOPMENT_SEED_START = 2_900_001
DEVELOPMENT_SEED_END = 2_900_064
CAMPAIGN_SEED_RANGES = (
    (2_100_001, 2_100_096),
    (2_200_001, 2_200_032),
    (2_300_001, 2_300_032),
    (2_400_001, 2_400_032),
    (2_500_001, 2_500_032),
)

ASSURANCE_DOCKERFILE_SHA256 = "fb12f3194c170953c5643603d94b17e39ebce34faefa781d580a880fc0b3a162"
REQUIREMENTS_SHA256 = "ca5e93a0d998206ccaaa16b2f5a1414bf51d58fd53e7da9da1e2026a6fee8da4"
PROTOCOL_AMENDMENT_SHA256 = "987559dfc1ccc28a50f3299161bfe1ff39e352d5891fb9b488672867fbf44246"
EXPECTED_TRIAL_MANIFEST_SHA256 = "190612473717b7768ceccb4596a20d90cd7d532bf7581330ce94d609cb752e67"


class RuntimeMode(str, Enum):
    DEVELOPMENT = "DEVELOPMENT"
    CAMPAIGN = "CAMPAIGN"


@dataclass(frozen=True)
class ContactCalibration:
    regime: ContactRegime
    windows: tuple[tuple[float, float], ...]

    def __post_init__(self) -> None:
        previous_end = -1.0
        for start, end in self.windows:
            if start < 0 or end <= start:
                raise ValueError("contact windows must be positive ordered intervals")
            if start < previous_end:
                raise ValueError("contact windows must not overlap")
            if end > CENSOR_HORIZON_S:
                raise ValueError("contact window exceeds frozen censor horizon")
            previous_end = end

    def available_at(self, logical_time_s: float) -> bool:
        return any(start <= logical_time_s <= end for start, end in self.windows)

    def next_contact_at_or_after(self, logical_time_s: float) -> float | None:
        for start, end in self.windows:
            if start <= logical_time_s <= end:
                return logical_time_s
            if logical_time_s < start:
                return start
        return None


CONTACT_CALIBRATION = {
    ContactRegime.K0: ContactCalibration(ContactRegime.K0, ((0.0, 240.0),)),
    ContactRegime.K1: ContactCalibration(ContactRegime.K1, ((20.0, 240.0),)),
    ContactRegime.K2: ContactCalibration(ContactRegime.K2, ((60.0, 240.0),)),
    ContactRegime.K3: ContactCalibration(ContactRegime.K3, ((180.0, 240.0),)),
    ContactRegime.K4: ContactCalibration(
        ContactRegime.K4,
        ((25.0, 35.0), (75.0, 90.0), (145.0, 165.0), (220.0, 240.0)),
    ),
}


def is_development_seed(seed: int) -> bool:
    return DEVELOPMENT_SEED_START <= seed <= DEVELOPMENT_SEED_END


def is_campaign_seed(seed: int) -> bool:
    return any(start <= seed <= end for start, end in CAMPAIGN_SEED_RANGES)


def require_seed_mode(seed: int, mode: RuntimeMode) -> None:
    if mode is RuntimeMode.DEVELOPMENT:
        if not is_development_seed(seed) or is_campaign_seed(seed):
            raise ValueError("development runtime requires a disjoint development-only seed")
        return
    if not is_campaign_seed(seed):
        raise ValueError("campaign runtime requires a frozen campaign seed")


def freeze_payload() -> dict[str, Any]:
    return {
        "schema": 1,
        "experiment_id": EXPERIMENT_ID,
        "status": "PHASE5_RUNTIME_FREEZE_CANDIDATE_RUNTIME_NOT_AUTHORIZED",
        "time_basis": "DETERMINISTIC_LOGICAL_SIL_TIME_NOT_WALL_CLOCK",
        "decision_time_s": DECISION_TIME_S,
        "evidence_issued_at_s": EVIDENCE_ISSUED_AT_S,
        "evidence_valid_for_s": EVIDENCE_VALID_FOR_S,
        "recovery_processing_s": RECOVERY_PROCESSING_S,
        "censor_horizon_s": CENSOR_HORIZON_S,
        "contact_windows": {
            regime.value: [list(window) for window in calibration.windows]
            for regime, calibration in CONTACT_CALIBRATION.items()
        },
        "development_seed_range": [DEVELOPMENT_SEED_START, DEVELOPMENT_SEED_END],
        "campaign_seed_ranges": [list(row) for row in CAMPAIGN_SEED_RANGES],
        "cell_matrix_sha256": matrix_sha256(),
        "trial_manifest_sha256": trial_manifest_sha256(),
        "protocol_amendment_sha256": PROTOCOL_AMENDMENT_SHA256,
        "assurance_dockerfile_sha256": ASSURANCE_DOCKERFILE_SHA256,
        "requirements_sha256": REQUIREMENTS_SHA256,
        "campaign_runtime_authorized": False,
        "automatic_retry_allowed": False,
        "automatic_next_trial_allowed": False,
        "post_hoc_seed_substitution_allowed": False,
        "campaign_observations_generated": False,
    }


def canonical_freeze_bytes(payload: dict[str, Any] | None = None) -> bytes:
    return (
        json.dumps(
            payload or freeze_payload(),
            ensure_ascii=True,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
    ).encode("utf-8")


def runtime_freeze_sha256(payload: dict[str, Any] | None = None) -> str:
    return hashlib.sha256(canonical_freeze_bytes(payload)).hexdigest()
