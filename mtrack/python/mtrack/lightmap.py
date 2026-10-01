from __future__ import annotations

from dataclasses import dataclass

from .model import CalibrationPoint, Vec3


@dataclass(frozen=True)
class Aim:
    pan16: int
    tilt16: int
    confidence: float


class LightMap:
    """Sampled fixture response map: stage XYZ -> pan/tilt.

    This deliberately starts with inverse-distance weighting. It is simple,
    explainable and gives us a baseline before introducing learned models.
    """

    def __init__(self, points: list[CalibrationPoint]):
        if not points:
            raise ValueError("LightMap requires calibration points")
        self.points = tuple(points)

    def aim(self, target: Vec3, *, power: float = 2.0, epsilon: float = 1e-9) -> Aim:
        for sample in self.points:
            if sample.stage.distance_to(target) <= epsilon:
                return Aim(sample.pan16, sample.tilt16, sample.confidence)

        weights = []
        for sample in self.points:
            distance = max(epsilon, sample.stage.distance_to(target))
            weight = max(0.0, sample.confidence) / (distance ** power)
            weights.append((sample, weight))

        total = sum(weight for _sample, weight in weights)
        if total <= 0:
            raise ValueError("calibration points have no usable confidence")

        pan = round(sum(sample.pan16 * weight for sample, weight in weights) / total)
        tilt = round(sum(sample.tilt16 * weight for sample, weight in weights) / total)
        confidence = min(
            1.0,
            sum(sample.confidence * weight for sample, weight in weights) / total,
        )
        return Aim(
            pan16=max(0, min(65535, pan)),
            tilt16=max(0, min(65535, tilt)),
            confidence=confidence,
        )
