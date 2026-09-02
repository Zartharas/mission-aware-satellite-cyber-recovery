from __future__ import annotations

from dataclasses import dataclass
from itertools import product

QUALITY_COUNT = 6

POLICIES = (
    "D0_S1_VISIBLE_ONLY",
    "L0_ERM_VISIBLE_ONLY",
    "L1_ERM_WITH_INDEPENDENT_CORROBORATION",
)


@dataclass(frozen=True)
class LinearThresholdModel:
    quality_weight: int
    authorization_weight: int
    corroboration_weight: int
    security_weight: int
    threshold: int
    training_errors: int

    def predict(self, features: tuple[int, ...]) -> int:
        if len(features) not in (8, 9):
            raise ValueError("features must contain 8 or 9 binary values")
        if any(x not in (0, 1) for x in features):
            raise ValueError("features must be binary")
        quality = sum(features[:QUALITY_COUNT])
        security = features[6]
        authorization = features[7]
        corroboration = features[8] if len(features) == 9 else 0
        score = (
            self.quality_weight * quality
            + self.authorization_weight * authorization
            + self.corroboration_weight * corroboration
            + self.security_weight * security
        )
        return int(score >= self.threshold)


def objective_safe_to_proceed(
    base_features: tuple[int, ...], *, hidden_authorization: int | None = None
) -> int:
    if len(base_features) != 8:
        raise ValueError("base_features must contain 8 binary values")
    if any(x not in (0, 1) for x in base_features):
        raise ValueError("base_features must be binary")
    quality_ok = all(base_features[:QUALITY_COUNT])
    security = base_features[6]
    visible_authorization = base_features[7]
    hidden = visible_authorization if hidden_authorization is None else hidden_authorization
    return int(quality_ok and ((not security) or bool(hidden)))


def deterministic_visible_only(base_features: tuple[int, ...]) -> int:
    return objective_safe_to_proceed(base_features)


def _visible_training_examples() -> tuple[tuple[tuple[int, ...], int], ...]:
    rows: list[tuple[tuple[int, ...], int]] = []
    for authorization in (0, 1):
        v = (1, 1, 1, 1, 1, 1, 0, authorization)
        rows.append((v, objective_safe_to_proceed(v)))
    for authorization in (0, 1):
        v = (1, 1, 1, 1, 1, 1, 1, authorization)
        rows.append((v, objective_safe_to_proceed(v)))
    for index in range(QUALITY_COUNT):
        v = [1, 1, 1, 1, 1, 1, 0, 1]
        v[index] = 0
        t = tuple(v)
        rows.append((t, objective_safe_to_proceed(t)))
    return tuple(rows)


def _corroboration_training_examples() -> tuple[tuple[tuple[int, ...], int], ...]:
    rows: list[tuple[tuple[int, ...], int]] = []
    for authorization in (0, 1):
        for corroboration in (0, 1):
            v = (1, 1, 1, 1, 1, 1, 0, authorization, corroboration)
            rows.append((v, objective_safe_to_proceed(v[:8])))
    for authorization in (0, 1):
        corroboration = authorization
        v = (1, 1, 1, 1, 1, 1, 1, authorization, corroboration)
        rows.append((v, objective_safe_to_proceed(v[:8])))
    # V5-like training example: policy-visible authorization remains true,
    # but an independent source does not corroborate it and hidden truth is false.
    v = (1, 1, 1, 1, 1, 1, 1, 1, 0)
    rows.append((v, objective_safe_to_proceed(v[:8], hidden_authorization=0)))
    for index in range(QUALITY_COUNT):
        v = [1, 1, 1, 1, 1, 1, 0, 1, 1]
        v[index] = 0
        t = tuple(v)
        rows.append((t, objective_safe_to_proceed(t[:8])))
    return tuple(rows)


def train_visible_only() -> LinearThresholdModel:
    training = _visible_training_examples()
    best: tuple[int, int, int, int, int, int] | None = None
    for q in range(1, 5):
        for wa in range(0, 5):
            for ws in range(-4, 1):
                for threshold in range(1, 31):
                    errors = 0
                    for features, expected in training:
                        score = q * sum(features[:6]) + wa * features[7] + ws * features[6]
                        errors += int(int(score >= threshold) != expected)
                    candidate = (errors, abs(q) + abs(wa) + abs(ws), threshold, q, wa, ws)
                    if best is None or candidate < best:
                        best = candidate
    assert best is not None
    errors, _, threshold, q, wa, ws = best
    return LinearThresholdModel(q, wa, 0, ws, threshold, errors)


def train_with_corroboration() -> LinearThresholdModel:
    training = _corroboration_training_examples()
    best: tuple[int, int, int, int, int, int, int] | None = None
    for q in range(1, 5):
        for wa in range(0, 5):
            for wc in range(0, 5):
                for ws in range(-5, 1):
                    for threshold in range(1, 35):
                        errors = 0
                        for features, expected in training:
                            score = (
                                q * sum(features[:6])
                                + wa * features[7]
                                + wc * features[8]
                                + ws * features[6]
                            )
                            errors += int(int(score >= threshold) != expected)
                        candidate = (
                            errors,
                            abs(q) + abs(wa) + abs(wc) + abs(ws),
                            threshold,
                            q,
                            wa,
                            wc,
                            ws,
                        )
                        if best is None or candidate < best:
                            best = candidate
    assert best is not None
    errors, _, threshold, q, wa, wc, ws = best
    return LinearThresholdModel(q, wa, wc, ws, threshold, errors)


def evaluation_rows() -> list[dict[str, object]]:
    l0 = train_visible_only()
    l1 = train_with_corroboration()
    rows: list[dict[str, object]] = []

    # Block A: exhaustive 8-feature lattice, hidden truth equals visible authorization.
    for bits in product((0, 1), repeat=8):
        base = tuple(bits)
        objective = objective_safe_to_proceed(base)
        for policy, decision in (
            ("D0_S1_VISIBLE_ONLY", deterministic_visible_only(base)),
            ("L0_ERM_VISIBLE_ONLY", l0.predict(base)),
        ):
            rows.append(
                _row(
                    block="A_VISIBLE_LATTICE",
                    scenario="VISIBLE_STATE",
                    policy=policy,
                    base=base,
                    corroboration=None,
                    hidden_authorization=base[7],
                    objective=objective,
                    decision=decision,
                )
            )

    # Block B: exhaustive 9-feature lattice for the corroboration-aware learner.
    for bits in product((0, 1), repeat=8):
        base = tuple(bits)
        objective = objective_safe_to_proceed(base)
        for corroboration in (0, 1):
            decision = l1.predict(base + (corroboration,))
            rows.append(
                _row(
                    block="B_CORROBORATION_LATTICE",
                    scenario="EXTENDED_VISIBLE_STATE",
                    policy="L1_ERM_WITH_INDEPENDENT_CORROBORATION",
                    base=base,
                    corroboration=corroboration,
                    hidden_authorization=base[7],
                    objective=objective,
                    decision=decision,
                )
            )

    # Block C: same eight visible features, different hidden truth/corroboration.
    base = (1, 1, 1, 1, 1, 1, 1, 1)
    scenarios = (
        ("SAFE_CORROBORATED", 1, 1),
        ("V5_INDEPENDENT_DISAGREEMENT", 0, 0),
        ("V5_CORRELATED_FALSE_CORROBORATION", 0, 1),
    )
    for scenario, hidden_authorization, corroboration in scenarios:
        objective = objective_safe_to_proceed(base, hidden_authorization=hidden_authorization)
        decisions = (
            ("D0_S1_VISIBLE_ONLY", deterministic_visible_only(base)),
            ("L0_ERM_VISIBLE_ONLY", l0.predict(base)),
            ("L1_ERM_WITH_INDEPENDENT_CORROBORATION", l1.predict(base + (corroboration,))),
        )
        for policy, decision in decisions:
            rows.append(
                _row(
                    block="C_HIDDEN_TRUTH_COLLISION",
                    scenario=scenario,
                    policy=policy,
                    base=base,
                    corroboration=corroboration if policy.startswith("L1_") else None,
                    hidden_authorization=hidden_authorization,
                    objective=objective,
                    decision=decision,
                )
            )
    return rows


def _row(
    *,
    block: str,
    scenario: str,
    policy: str,
    base: tuple[int, ...],
    corroboration: int | None,
    hidden_authorization: int,
    objective: int,
    decision: int,
) -> dict[str, object]:
    return {
        "block": block,
        "scenario": scenario,
        "policy": policy,
        "signature_valid": base[0],
        "source_trusted": base[1],
        "fresh": base[2],
        "epoch_valid": base[3],
        "noncontradictory": base[4],
        "minimum_evidence_complete": base[5],
        "security_signal": base[6],
        "authorization_available": base[7],
        "independent_corroboration": "" if corroboration is None else corroboration,
        "hidden_authorization": hidden_authorization,
        "objective_safe_to_proceed": objective,
        "decision_proceed": decision,
        "objective_decision_error": int(decision != objective),
        "unsafe_proceed": int(decision == 1 and objective == 0),
        "false_conservative_hold": int(decision == 0 and objective == 1),
    }
