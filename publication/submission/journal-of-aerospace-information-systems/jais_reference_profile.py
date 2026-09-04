"""JAIS-only reference cleanup layered over the compact editorial profile.

The target-neutral manuscript and bibliography remain unchanged. This module
removes nonessential web-only citations from the JAIS export and consolidates
SPARTA taxonomy support to an archival Aerospace Corporation fact sheet.
"""

import jais_editorial_profile as source


def _clean(text: str) -> str:
    replacements = {
        "[@chunawala2026satelliteir; @nist800160v2r1]": "[@nist800160v2r1]",
        "[@wanninger2025fdir; @thangavel2024trusted; @sarri2026juice]": "[@wanninger2025fdir; @thangavel2024trusted]",
        "[@thangavel2024trusted; @wanninger2025fdir; @sarri2026juice]": "[@thangavel2024trusted; @wanninger2025fdir]",
        "[@bakirtzis2026missionaware; @wanninger2025fdir; @thangavel2024trusted; @sarri2026juice]": "[@bakirtzis2026missionaware; @wanninger2025fdir; @thangavel2024trusted]",
        "[@nasa_nos3; @nasa_cfs]": "[@geletko2019nos3]",
        "[@sparta_cybersafe]": "[@sparta_fact_sheet_2025]",
        "[@sparta_malicious_valid_gs; @sparta_replay_command_packets; @sparta_onorbit_update; @sparta_compromise_boot_memory; @sparta_telemetry_downlink_modes]": "[@sparta_fact_sheet_2025]",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)

    text = text.replace(
        "Current satellite incident-response guidance likewise recognizes that containment and recovery can depend on contact opportunities and approval gates [@chunawala2026satelliteir]. The present experiments therefore model contact as a controlled factor, not as orbital geometry, antenna availability, radio propagation, or operator latency.",
        "Spacecraft recovery and autonomy literature establishes that operation may continue without immediate ground intervention. The present experiments therefore model contact as a controlled factor, not as orbital geometry, antenna availability, radio propagation, or operator latency.",
    )
    text = text.replace(
        "The frozen event families are related to SPARTA only as behavioral correspondences: unauthorized valid commanding, replayed commands, compromised synthetic updates, and telemetry/evidence degradation map to documented spacecraft-security behaviors without claiming reproduction of complete operational attack chains [@sparta_fact_sheet_2025]. The experiments do not model real ground-station compromise, supply-chain compromise, key theft, or radio-frequency attack mechanisms.",
        "The frozen event families are cross-walked to SPARTA behavioral identifiers in the public traceability record; that crosswalk is taxonomy correspondence rather than reproduction of complete operational attack chains [@sparta_fact_sheet_2025]. The experiments do not model real ground-station compromise, supply-chain compromise, key theft, or radio-frequency attack mechanisms.",
    )
    return text


INTRODUCTION = _clean(source.INTRODUCTION)
BACKGROUND = _clean(source.BACKGROUND)
METHODS = _clean(source.METHODS)
DISCUSSION = _clean(source.DISCUSSION)
CONCLUSION = _clean(source.CONCLUSION)
