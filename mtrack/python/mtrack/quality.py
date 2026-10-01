from __future__ import annotations

from dataclasses import dataclass
from math import exp


@dataclass(frozen=True)
class ConfidenceInputs:
    detector: float
    calibration: float
    source_health: float
    age_ms: float
    inside_coverage: bool = True


def effective_confidence(
    inputs: ConfidenceInputs,
    *,
    half_life_ms: float = 250.0,
) -> float:
    """Conservative multiplicative confidence with temporal decay."""
    if half_life_ms <= 0:
        raise ValueError("half_life_ms must be positive")
    if not inputs.inside_coverage:
        return 0.0

    detector = max(0.0, min(1.0, inputs.detector))
    calibration = max(0.0, min(1.0, inputs.calibration))
    health = max(0.0, min(1.0, inputs.source_health))
    age = max(0.0, inputs.age_ms)
    decay = exp(-0.6931471805599453 * age / half_life_ms)
    return detector * calibration * health * decay
