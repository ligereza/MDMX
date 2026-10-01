from __future__ import annotations

from dataclasses import dataclass

from .model import Observation3D


@dataclass(frozen=True)
class SyncWindow:
    observations: tuple[Observation3D, ...]
    span_ms: float


def synchronize_observations(
    observations: list[Observation3D],
    *,
    max_skew_ms: float = 80.0,
) -> SyncWindow:
    """Select observations close enough in time for geometric fusion.

    This is timestamp gating, not clock synchronization. Camera/system clocks
    still need a common timebase or estimated offsets for strict fusion.
    """
    if not observations:
        raise ValueError("observations cannot be empty")
    if max_skew_ms < 0:
        raise ValueError("max_skew_ms cannot be negative")

    newest = max(o.timestamp_s for o in observations)
    kept = tuple(
        o for o in observations
        if (newest - o.timestamp_s) * 1000.0 <= max_skew_ms
    )
    oldest = min(o.timestamp_s for o in kept)
    return SyncWindow(
        observations=kept,
        span_ms=(newest - oldest) * 1000.0,
    )
