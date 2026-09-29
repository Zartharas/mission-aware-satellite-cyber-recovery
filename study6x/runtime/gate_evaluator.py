from __future__ import annotations

SIGNALS = (
    "signature_valid",
    "independent_target_digest_match",
    "provenance_valid",
    "independent_reproduced_build_match",
    "source_review_attested",
    "release_approved",
)

GATES = {
    "G0_SIGNATURE_ONLY": ("signature_valid",),
    "G1_SIGNATURE_TARGET_DIGEST": ("signature_valid", "independent_target_digest_match"),
    "G2_SIGNATURE_PROVENANCE": ("signature_valid", "provenance_valid"),
    "G3_PROVENANCE_REPRODUCED_BUILD": (
        "signature_valid", "provenance_valid", "independent_reproduced_build_match"
    ),
    "G4_PROVENANCE_SOURCE_REVIEW": (
        "signature_valid", "provenance_valid", "source_review_attested"
    ),
    "G5_COMPOSITE": SIGNALS,
}

def evaluate_gate(gate: str, evidence: dict[str, bool]) -> bool:
    return all(bool(evidence[name]) for name in GATES[gate])
