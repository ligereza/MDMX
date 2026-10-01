from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum


class CalibrationState(str, Enum):
    COLLECT = "collect"
    CANDIDATE = "candidate"
    VALIDATED = "validated"
    ACTIVE = "active"
    STALE = "stale"


@dataclass(frozen=True)
class CalibrationRecord:
    calibration_id: str
    source_id: str
    state: CalibrationState
    rms_error_px: float | None = None
    sample_count: int = 0
    resolution: tuple[int, int] | None = None
    lens_signature: str | None = None

    def propose(
        self,
        *,
        rms_error_px: float,
        sample_count: int,
        resolution: tuple[int, int],
        lens_signature: str | None = None,
    ) -> "CalibrationRecord":
        if self.state not in (CalibrationState.COLLECT, CalibrationState.STALE):
            raise ValueError("only COLLECT/STALE calibration may become CANDIDATE")
        if rms_error_px < 0 or sample_count <= 0:
            raise ValueError("invalid candidate metrics")
        return replace(
            self,
            state=CalibrationState.CANDIDATE,
            rms_error_px=rms_error_px,
            sample_count=sample_count,
            resolution=resolution,
            lens_signature=lens_signature,
        )

    def validate(self, *, max_rms_error_px: float) -> "CalibrationRecord":
        if self.state != CalibrationState.CANDIDATE:
            raise ValueError("only CANDIDATE calibration may be validated")
        if self.rms_error_px is None or self.rms_error_px > max_rms_error_px:
            raise ValueError("candidate does not satisfy RMS gate")
        return replace(self, state=CalibrationState.VALIDATED)

    def activate(self) -> "CalibrationRecord":
        if self.state != CalibrationState.VALIDATED:
            raise ValueError("only VALIDATED calibration may become ACTIVE")
        return replace(self, state=CalibrationState.ACTIVE)

    def mark_stale(self) -> "CalibrationRecord":
        if self.state == CalibrationState.COLLECT:
            return self
        return replace(self, state=CalibrationState.STALE)

    def verify_runtime_identity(
        self,
        *,
        resolution: tuple[int, int],
        lens_signature: str | None,
    ) -> "CalibrationRecord":
        if self.state != CalibrationState.ACTIVE:
            return self
        if self.resolution != resolution:
            return self.mark_stale()
        if self.lens_signature is not None and self.lens_signature != lens_signature:
            return self.mark_stale()
        return self
