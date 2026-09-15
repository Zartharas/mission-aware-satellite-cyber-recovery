from __future__ import annotations

from functools import lru_cache
import sys
from typing import Mapping

from .contracts import REQUIRED_VARIABLES, load_frozen_contracts


@lru_cache(maxsize=1)
def _selector_module():
    """Load and validate the frozen Study 2 selector once per Python process."""
    contracts = load_frozen_contracts()
    study2_src = contracts.repo_root / "study2" / "src"
    if str(study2_src) not in sys.path:
        sys.path.insert(0, str(study2_src))
    from study2_security import selectors

    return selectors


@lru_cache(maxsize=None)
def _select_action_cached(policy_value: str, state_values: tuple[bool, ...]):
    """Memoize deterministic selector evaluation for one policy and full Boolean state."""
    if len(state_values) != len(REQUIRED_VARIABLES):
        raise ValueError("cached state does not contain all required variables")
    selectors = _selector_module()
    policy = selectors.Study2Policy(policy_value)
    obs = selectors.ObservationSummary(
        **dict(zip(REQUIRED_VARIABLES, state_values, strict=True))
    )
    return selectors.select_action(policy, obs)


def clear_selector_caches() -> None:
    """Clear canonical selector caches for tests and explicit process-boundary control."""
    _select_action_cached.cache_clear()
    _selector_module.cache_clear()


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
    if isinstance(policy, selectors.Study2Policy):
        policy_value = policy.value
    else:
        policy_value = selectors.Study2Policy(policy).value
    state_values = tuple(state[name] for name in REQUIRED_VARIABLES)
    return _select_action_cached(policy_value, state_values)
