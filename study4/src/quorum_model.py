from __future__ import annotations

from dataclasses import dataclass, asdict
from itertools import combinations
from typing import Iterable

EXPERIMENT_ID = "S4-MPQ-001"
PRODUCERS = ("P1", "P2", "P3", "P4", "P5", "P6", "P7")
DOMAIN = {
    "P1": "D1",
    "P2": "D1",
    "P3": "D1",
    "P4": "D2",
    "P5": "D2",
    "P6": "D3",
    "P7": "D3",
}
N = len(PRODUCERS)


@dataclass(frozen=True)
class Rule:
    q_total: int
    q_domains: int

    @property
    def rule_id(self) -> str:
        return f"Q{self.q_total}_D{self.q_domains}"


@dataclass(frozen=True)
class Scenario:
    block: str
    affected: tuple[str, ...]
    affected_count: int


@dataclass(frozen=True)
class Observation:
    experiment_id: str
    block: str
    rule_id: str
    q_total: int
    q_domains: int
    affected_count: int
    affected_fraction: float
    affected_members: str
    true_votes: int
    true_vote_domains: int
    qualified: bool
    unsafe_qualified: bool
    false_conservative: bool


def rules() -> tuple[Rule, ...]:
    output: list[Rule] = []
    for q_total in range(1, N + 1):
        for q_domains in range(1, min(3, q_total) + 1):
            output.append(Rule(q_total, q_domains))
    result = tuple(output)
    if len(result) != 18:
        raise AssertionError("Study-4 rule matrix must contain exactly 18 rules")
    return result


def subsets_of_size(k: int) -> tuple[tuple[str, ...], ...]:
    return tuple(combinations(PRODUCERS, k))


def scenarios(block: str) -> tuple[Scenario, ...]:
    if block not in {"SAFETY", "AVAILABILITY"}:
        raise ValueError(block)
    rows: list[Scenario] = []
    for k in range(N + 1):
        for subset in subsets_of_size(k):
            rows.append(Scenario(block, subset, k))
    output = tuple(rows)
    if len(output) != 2**N:
        raise AssertionError("Study-4 subset population drift")
    return output


def qualify(rule: Rule, true_voters: Iterable[str]) -> tuple[bool, int, int]:
    voters = tuple(true_voters)
    domains = {DOMAIN[producer] for producer in voters}
    return (
        len(voters) >= rule.q_total and len(domains) >= rule.q_domains,
        len(voters),
        len(domains),
    )


def evaluate(rule: Rule, scenario: Scenario) -> Observation:
    affected = set(scenario.affected)
    if scenario.block == "SAFETY":
        true_voters = affected
        qualified, true_votes, true_domains = qualify(rule, true_voters)
        unsafe_qualified = qualified
        false_conservative = False
    else:
        true_voters = [producer for producer in PRODUCERS if producer not in affected]
        qualified, true_votes, true_domains = qualify(rule, true_voters)
        unsafe_qualified = False
        false_conservative = not qualified

    return Observation(
        experiment_id=EXPERIMENT_ID,
        block=scenario.block,
        rule_id=rule.rule_id,
        q_total=rule.q_total,
        q_domains=rule.q_domains,
        affected_count=scenario.affected_count,
        affected_fraction=scenario.affected_count / N,
        affected_members=";".join(scenario.affected),
        true_votes=true_votes,
        true_vote_domains=true_domains,
        qualified=qualified,
        unsafe_qualified=unsafe_qualified,
        false_conservative=false_conservative,
    )


def run_population() -> tuple[Observation, ...]:
    rows: list[Observation] = []
    for rule in rules():
        for block in ("SAFETY", "AVAILABILITY"):
            for scenario in scenarios(block):
                rows.append(evaluate(rule, scenario))
    output = tuple(rows)
    if len(output) != 4608:
        raise AssertionError("Study-4 finite population must contain 4,608 observations")
    return output


def as_rows(values: Iterable[object]) -> list[dict[str, object]]:
    return [asdict(value) for value in values]
