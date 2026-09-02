from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
import hashlib
import sys

ROOT = Path(__file__).resolve().parents[2]
STUDY2_SRC = ROOT / "study2" / "src"
if str(STUDY2_SRC) not in sys.path:
    sys.path.insert(0, str(STUDY2_SRC))

from study2_security.selectors import ObservationSummary, Study2Policy, select_action  # noqa: E402

SELECTOR_PATH = ROOT / "study2" / "src" / "study2_security" / "selectors.py"
SELECTOR_SHA256 = "3bd5b607095807acf93a929d6d67c5cc1d2f592e5b0650c14032a7724e5f5505"

LABELS = ((0, "COMMAND_FLOODING"), (1, "DATA_INJECTION"), (2, "DEFENCE_IMPAIRMENT"), (3, "NORMAL"), (4, "STORAGE_EXHAUSTION"))
POLICIES = (Study2Policy.FAIL_CLOSED, Study2Policy.FAIL_OPERATIONAL, Study2Policy.RISK_THRESHOLD, Study2Policy.EVIDENCE_AWARE)
CONTEXTS = {
    "QUALIFIED_AUTH_AVAILABLE": dict(signature_valid=True, source_trusted=True, fresh=True, epoch_valid=True, contradictory=False, minimum_evidence_complete=True, authorization_available=True),
    "QUALIFIED_AUTH_UNAVAILABLE": dict(signature_valid=True, source_trusted=True, fresh=True, epoch_valid=True, contradictory=False, minimum_evidence_complete=True, authorization_available=False),
    "INCOMPLETE_EVIDENCE": dict(signature_valid=True, source_trusted=True, fresh=True, epoch_valid=True, contradictory=False, minimum_evidence_complete=False, authorization_available=True),
    "UNTRUSTED_SOURCE": dict(signature_valid=True, source_trusted=False, fresh=True, epoch_valid=True, contradictory=False, minimum_evidence_complete=True, authorization_available=True),
}
REQUIRED_RECOVERY_INPUTS = ("signature_valid", "source_trusted", "fresh", "epoch_valid", "contradictory", "minimum_evidence_complete", "security_signal", "authorization_available")
TRANSFERABILITY = (
    {"label_code": 0, "label": "COMMAND_FLOODING", "external_sparta": "EX-0013.01", "frozen_event_correspondence": "CONCEPTUAL_ADJACENCY_E1", "study2_correspondence": "NONE_DIRECT", "reason": "Both involve valid commands, but CuCD-ID flooding is volumetric and does not encode the authorization-state semantics of E1."},
    {"label_code": 1, "label": "DATA_INJECTION", "external_sparta": "EX-0014.03", "frozen_event_correspondence": "CONCEPTUAL_ADJACENCY_E4", "study2_correspondence": "CONCEPTUAL_ADJACENCY_V5", "reason": "False sensor/state content is adjacent to evidence-truth degradation, but CuCD-ID does not encode trusted-producer signature or recovery-evidence semantics."},
    {"label_code": 2, "label": "DEFENCE_IMPAIRMENT", "external_sparta": "DE-0001", "frozen_event_correspondence": "NONE_DIRECT", "study2_correspondence": "ASSURANCE_BOUNDARY_ADJACENCY", "reason": "Disabling fault management can affect recovery assurance but is not the frozen E3 update mechanism or a Study-2 evidence treatment."},
    {"label_code": 3, "label": "NORMAL", "external_sparta": "", "frozen_event_correspondence": "CONTROL_ONLY", "study2_correspondence": "CONTROL_ONLY", "reason": "Nominal external scenario used only as the no-alarm control."},
    {"label_code": 4, "label": "STORAGE_EXHAUSTION", "external_sparta": "IMP-0003", "frozen_event_correspondence": "NONE_DIRECT", "study2_correspondence": "AVAILABILITY_ADJACENCY", "reason": "Storage denial can hinder telemetry/recovery but is not represented as a frozen event or evidence-integrity treatment."},
)

def selector_sha256() -> str:
    return hashlib.sha256(SELECTOR_PATH.read_bytes()).hexdigest()

def assert_frozen_selector() -> None:
    actual = selector_sha256()
    if actual != SELECTOR_SHA256:
        raise RuntimeError(f"Study-2 selector drift: {actual} != {SELECTOR_SHA256}")

def sufficiency_rows() -> list[dict[str, object]]:
    return [{"required_input": name, "directly_available_from_cucdid_row": False, "allowed_study5_source": "OFFLINE_LABEL_ORACLE" if name == "security_signal" else "CONTROLLED_CONTEXT_ONLY"} for name in REQUIRED_RECOVERY_INPUTS]

def portability_rows() -> list[dict[str, object]]:
    assert_frozen_selector()
    rows: list[dict[str, object]] = []
    for label_code, label in LABELS:
        security_signal = label != "NORMAL"
        for context_name, context in CONTEXTS.items():
            for policy in POLICIES:
                obs = ObservationSummary(security_signal=security_signal, **context)
                action = select_action(policy, obs)
                row = {"label_code": label_code, "label": label, "security_signal_source": "OFFLINE_LABEL_ORACLE", "context": context_name, "policy": policy.value, "action": action.value}
                row.update(asdict(obs))
                rows.append(row)
    return rows

def transferability_rows() -> list[dict[str, object]]:
    return [dict(row) for row in TRANSFERABILITY]
