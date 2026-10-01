from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PassiveCalibrationSample:
    """Derived calibration evidence; contains no image or biometric identity."""

    source_id: str
    ephemeral_track_id: str
    pixel_x: float
    pixel_y: float
    timestamp_s: float


@dataclass(frozen=True)
class EvidenceQuality:
    samples: int
    duration_s: float
    span_x_px: float
    span_y_px: float
    ready: bool
    reason: str


class PassiveCalibrationBuffer:
    """Collects ephemeral 2D trajectories for future calibration fitting.

    This class intentionally does NOT estimate camera parameters. It only
    determines whether evidence has enough temporal/spatial diversity to
    justify running a calibration candidate solver later.
    """

    def __init__(self) -> None:
        self._samples: list[PassiveCalibrationSample] = []

    def add(self, sample: PassiveCalibrationSample) -> None:
        self._samples.append(sample)

    def clear(self) -> None:
        self._samples.clear()

    def quality(
        self,
        *,
        min_samples: int = 20,
        min_duration_s: float = 3.0,
        min_span_px: float = 100.0,
    ) -> EvidenceQuality:
        if not self._samples:
            return EvidenceQuality(0, 0.0, 0.0, 0.0, False, "no samples")

        xs = [s.pixel_x for s in self._samples]
        ys = [s.pixel_y for s in self._samples]
        ts = [s.timestamp_s for s in self._samples]
        duration = max(ts) - min(ts)
        span_x = max(xs) - min(xs)
        span_y = max(ys) - min(ys)

        if len(self._samples) < min_samples:
            return EvidenceQuality(
                len(self._samples), duration, span_x, span_y, False,
                "insufficient sample count",
            )
        if duration < min_duration_s:
            return EvidenceQuality(
                len(self._samples), duration, span_x, span_y, False,
                "insufficient temporal diversity",
            )
        if max(span_x, span_y) < min_span_px:
            return EvidenceQuality(
                len(self._samples), duration, span_x, span_y, False,
                "trajectory is spatially degenerate",
            )
        return EvidenceQuality(
            len(self._samples), duration, span_x, span_y, True, "ready"
        )
