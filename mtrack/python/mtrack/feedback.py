from __future__ import annotations

from .model import Observation3D, Residual, Vec3


def residual(predicted: Vec3, observed: Observation3D) -> Residual:
    delta = observed.point - predicted
    return Residual(
        predicted=predicted,
        observed=observed.point,
        delta=delta,
        magnitude=predicted.distance_to(observed.point),
        confidence=max(0.0, min(1.0, observed.confidence)),
    )
