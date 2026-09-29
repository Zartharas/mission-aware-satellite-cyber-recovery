from __future__ import annotations

def evaluate_gate_reference(gate: str, e: dict[str, bool]) -> bool:
    if gate == "G0_SIGNATURE_ONLY":
        return bool(e["signature_valid"])
    if gate == "G1_SIGNATURE_TARGET_DIGEST":
        return bool(e["signature_valid"] and e["independent_target_digest_match"])
    if gate == "G2_SIGNATURE_PROVENANCE":
        return bool(e["signature_valid"] and e["provenance_valid"])
    if gate == "G3_PROVENANCE_REPRODUCED_BUILD":
        return bool(e["signature_valid"] and e["provenance_valid"] and e["independent_reproduced_build_match"])
    if gate == "G4_PROVENANCE_SOURCE_REVIEW":
        return bool(e["signature_valid"] and e["provenance_valid"] and e["source_review_attested"])
    if gate == "G5_COMPOSITE":
        return bool(
            e["signature_valid"]
            and e["independent_target_digest_match"]
            and e["provenance_valid"]
            and e["independent_reproduced_build_match"]
            and e["source_review_attested"]
            and e["release_approved"]
        )
    raise KeyError(gate)
