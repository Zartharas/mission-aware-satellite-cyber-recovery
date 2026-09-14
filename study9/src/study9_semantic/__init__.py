"""Synthetic-only implementation support for Study 9 semantic interoperability.

This package is intentionally unable to authorize canonical Study 9 execution.
Authorization remains governed by study9/STUDY9_PROTOCOL.json.
"""

from .contracts import ContractViolation, FrozenContracts, load_frozen_contracts
from .mapping import MappingRecord, materialize_mapping_matrix

__all__ = [
    "ContractViolation",
    "FrozenContracts",
    "MappingRecord",
    "load_frozen_contracts",
    "materialize_mapping_matrix",
]
