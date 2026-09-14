from __future__ import annotations

import sys
from typing import Mapping

from .contracts import REQUIRED_VARIABLES, load_frozen_contracts


def _selector_module():
    contracts = load_frozen_contracts()
    study2_src = contracts.repo_root / "study2" / "src"
    if str(study2_src) not in sys.path:
        sys.path.insert(0, str(study2_src))
    from study2_security import selectors

    return selectors


def selector_types():
    selectors = _selector_module()
    return selectors.Study2Policy, selectors.Study2Action, selectors.ObservationSummary


def select_action_from_state(policy, state: Mapping[str, bool]):
    if set(state) != set(REQUIRED_VARIABLES):
        missing = set(REQUIRED_VARIABLES) - set(state)
        extra = set(state) - set(REQUIRED_VARIABLES)
        raise ValueError(f"state variables mismatch: missing={sorted(missing)} extra={sorted(extra)}")
    non_bool = [key for key, value in state.items() if type(value) is not bool]
    if non_bool:
        raise ValueError(f"state contains non-boolean values: {sorted(non_bool)}")

    selectors = _selector_module()
    if not isinstance(policy, selectors.Study2Policy):
        policy = selectors.Study2Policy(policy)
    obs = selectors.ObservationSummary(**{name: state[name] for name in REQUIRED_VARIABLES})
    return selectors.select_action(policy, obs)
