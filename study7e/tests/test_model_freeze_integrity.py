from __future__ import annotations
import base64, hashlib, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
M = json.loads((ROOT / "study7e/MODEL_FREEZE_MANIFEST_001.json").read_text())
A = json.loads((ROOT / "study7e/configs/model_freeze_authorization_001.json").read_text())
S = json.loads((ROOT / "study7e/PRODUCTION_TRAINING_STATE.json").read_text())
P = ROOT / "study7e/frozen_models/S7E-AERC-MODEL-FREEZE-001"

def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def canonical_json_hash(path: Path) -> str:
    obj = json.loads(path.read_text())
    return sha(json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode())

def decoded(path: Path) -> bytes:
    return base64.b64decode("".join(path.read_text().split()), validate=True)

def test_freeze_identity_and_scope():
    assert M["model_freeze_id"] == "S7E-AERC-MODEL-FREEZE-001"
    assert M["state"] == "ACTIVE_FROZEN_MODELS__HELD_OUT_EVALUATION_NOT_AUTHORIZED"
    assert A["state"] == "AUTHORIZED_MODEL_FREEZE_ONLY"
    assert A["authorized"]["model_freeze_activation"] is True
    assert all(A["not_authorized"].values())

def test_runtime_bytes_match_candidate_of_record():
    assert sha(decoded(P / "L0_BASE.primary.joblib.b64")) == "5b38a0088c4dd0cb2ce3739993cd2d9ee7949eb1a86c188ca1bd95b38cb5f4b1"
    assert sha(decoded(P / "L1_CORROBORATED.primary.joblib.b64")) == "6c4b589766f1df51fad2bde80350000f24c53b215ef345079fd81a8a7b98b960"

def test_semantic_identities_are_exact():
    assert canonical_json_hash(P / "L0_BASE.semantic.json") == "1060d526704f21d4ee72be1ace6916c061b0c254de64246b1f469a576ba42ef1"
    assert canonical_json_hash(P / "L1_CORROBORATED.semantic.json") == "499fc92b714948c9a837861d4810051f51ab014f3f261a13df85646f7832f558"

def test_provenance_hashes_are_exact():
    assert sha((P / "dependency_inventory.json").read_bytes()) == "023a745c1edde1a929030fbc15245811f828365aba11b0485c5b139a402fdd08"
    assert sha((P / "prefit_binding.json").read_bytes()) == "3105d9741cf4bffb7acb23bc91c4dfdc89832cccc17cbe30fee4a79995bce38f"
    assert sha((P / "candidate_payload.json").read_bytes()) == "49dd341bbef9f5ba694c2b127a30246cbe612f1598458b85594a4078503d4dfb"
    assert sha((P / "training_execution_record.json").read_bytes()) == "f98890e34020cabce2e0090bc100a192bb977eda489ef303bb61c886022c5b45"

def test_candidate_remains_historical_and_unmodified():
    candidate = json.loads((P / "candidate_payload.json").read_text())
    assert candidate["state"] == "MODEL_FREEZE_CANDIDATE__NOT_FROZEN__HELD_OUT_EVALUATION_PROHIBITED"
    assert candidate["gates"]["production_models_frozen"] is False
    assert candidate["gates"]["held_out_evaluation_executed"] is False

def test_freeze_state_opens_only_model_freeze_gate():
    assert S["production_models_trained"] is True
    assert S["production_models_frozen"] is True
    assert S["held_out_evaluation_executed"] is False
    assert S["canonical_execution_authorized"] is False
    assert S["canonical_results_generated"] is False
    assert S["pr_merge_authorized"] is False
    assert S["publication_or_result_claims_authorized"] is False

def test_no_held_out_or_canonical_authorization_file_exists():
    assert not (ROOT / "study7e/CANONICAL_EXECUTION_AUTHORIZATION.json").exists()
    assert not (ROOT / "study7e/HELD_OUT_EVALUATION_AUTHORIZATION.json").exists()
    assert not (ROOT / ".github/workflows/study7e-canonical-execution.yml").exists()
