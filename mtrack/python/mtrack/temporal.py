from __future__ import annotations

from dataclasses import dataclass

from .model import Vec3


@dataclass(frozen=True)
class TrackEstimate:
    position: Vec3
    velocity: Vec3
    timestamp_s: float
    confidence: float


class AlphaBetaTracker:
    """Small deterministic motion estimator.

    It smooths noisy XYZ observations and estimates velocity. It is not an
    object detector and does not establish persistent human identity.
    """

    def __init__(self, alpha: float = 0.65, beta: float = 0.20):
        if not 0.0 < alpha <= 1.0:
            raise ValueError("alpha must be in (0,1]")
        if not 0.0 <= beta <= 1.0:
            raise ValueError("beta must be in [0,1]")
        self.alpha = alpha
        self.beta = beta
        self._state: TrackEstimate | None = None

    @property
    def state(self) -> TrackEstimate | None:
        return self._state

    def update(
        self,
        measured: Vec3,
        timestamp_s: float,
        confidence: float,
    ) -> TrackEstimate:
        confidence = max(0.0, min(1.0, confidence))
        if self._state is None:
            self._state = TrackEstimate(
                measured, Vec3(0.0, 0.0, 0.0), timestamp_s, confidence
            )
            return self._state

        dt = timestamp_s - self._state.timestamp_s
        if dt <= 0:
            raise ValueError("timestamps must increase")

        predicted = self._state.position + self._state.velocity.scale(dt)
        error = measured - predicted
        a = self.alpha * confidence
        b = self.beta * confidence

        position = predicted + error.scale(a)
        velocity = self._state.velocity + error.scale(b / dt)
        self._state = TrackEstimate(position, velocity, timestamp_s, confidence)
        return self._state

    def predict(self, timestamp_s: float) -> Vec3:
        if self._state is None:
            raise RuntimeError("tracker has no state")
        dt = timestamp_s - self._state.timestamp_s
        if dt < 0:
            raise ValueError("cannot predict into the past")
        return self._state.position + self._state.velocity.scale(dt)
