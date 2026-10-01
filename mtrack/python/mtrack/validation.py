from __future__ import annotations

from dataclasses import dataclass
from math import sqrt


@dataclass(frozen=True)
class ResidualMetrics:
    samples: int
    mean: float
    rms: float
    p95: float
    maximum: float


@dataclass(frozen=True)
class CandidateDecision:
    accept: bool
    reason: str
    active: ResidualMetrics
    candidate: ResidualMetrics


def residual_metrics(errors: list[float]) -> ResidualMetrics:
    if not errors:
        raise ValueError("errors cannot be empty")
    values = sorted(max(0.0, float(x)) for x in errors)
    n = len(values)
    mean = sum(values) / n
    rms = sqrt(sum(x * x for x in values) / n)
    # Nearest-rank p95, deliberately dependency-free.
    rank = max(1, (95 * n + 99) // 100)
    p95 = values[min(n - 1, rank - 1)]
    return ResidualMetrics(n, mean, rms, p95, values[-1])


def compare_candidate(
    active_errors: list[float],
    candidate_errors: list[float],
    *,
    min_rms_improvement: float = 0.05,
    max_p95_regression: float = 0.05,
    max_worst_regression: float = 0.10,
) -> CandidateDecision:
    """Gate a learned calibration/model using held-out residuals.

    Thresholds are relative fractions. Example: 0.05 = 5%.
    """
    if len(active_errors) != len(candidate_errors):
        raise ValueError("active/candidate must use the same validation samples")

    active = residual_metrics(active_errors)
    candidate = residual_metrics(candidate_errors)

    required_rms = active.rms * (1.0 - min_rms_improvement)
    if candidate.rms > required_rms:
        return CandidateDecision(
            False, "candidate RMS improvement is insufficient", active, candidate
        )

    allowed_p95 = active.p95 * (1.0 + max_p95_regression)
    if candidate.p95 > allowed_p95:
        return CandidateDecision(
            False, "candidate improves RMS but regresses p95 too much", active, candidate
        )

    allowed_worst = active.maximum * (1.0 + max_worst_regression)
    if candidate.maximum > allowed_worst:
        return CandidateDecision(
            False, "candidate improves RMS but regresses worst case too much",
            active, candidate,
        )

    return CandidateDecision(True, "candidate passes validation gates", active, candidate)
